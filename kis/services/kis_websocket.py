"""
KIS WebSocket 싱글톤 매니저

Django 프로세스 전체에서 단일 KIS WebSocket 연결을 유지하고,
SSE 리스너에게 실시간 체결가/호가 데이터를 중계한다.

설계 원칙:
- 싱글톤: threading.Lock으로 보호
- 백그라운드 스레드에서 asyncio 이벤트 루프 실행
- Django 동기 뷰에서 thread-safe하게 구독/해제
- 자동 재연결 (최대 10회, 5초 간격)
"""

import asyncio
import base64
import json
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import websockets

from kis.constants import (
    KIS_WS_URL_MOCK,
    KIS_WS_URL_REAL,
    TR_ID_ORDERBOOK,
    TR_ID_TRADE,
)
from kis.services.kis_auth import get_approval_key
from kis.services.kis_parser import parse_orderbook, parse_trade

logger = logging.getLogger("kis")


class KisWebSocketManager:
    """KIS WebSocket 싱글톤 매니저"""

    _instance: Optional["KisWebSocketManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "KisWebSocketManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:  # type: ignore[has-type]
            return
        self._initialized = True

        # WebSocket 및 루프
        self._ws = None
        self._connected = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        # 재연결
        self._reconnect_count = 0
        self._max_reconnect = 10

        # 종목별 구독 카운트 (symbol -> 구독자 수)
        self._subscriptions: Dict[str, int] = {}

        # 종목별 최신 데이터 캐시
        self._trade_cache: Dict[str, dict] = {}
        self._orderbook_cache: Dict[str, dict] = {}

        # TR_ID별 AES 암호화 키 (tr_id -> (iv, key))
        self._aes_keys: Dict[str, Tuple[str, str]] = {}

        # SSE 리스너: symbol -> list of (event_type, data) 콜백
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._listener_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API (Django 동기 뷰에서 호출)
    # ------------------------------------------------------------------

    def subscribe(self, symbol: str, listener: Callable) -> None:
        """
        종목 구독 및 SSE 리스너 등록.

        1. listener를 _listeners[symbol]에 추가
        2. _subscriptions[symbol] 증가
        3. WebSocket 연결 보장
        4. KIS에 구독 요청 전송 (새 구독인 경우)
        """
        with self._listener_lock:
            self._listeners[symbol].append(listener)
            prev_count = self._subscriptions.get(symbol, 0)
            self._subscriptions[symbol] = prev_count + 1
            is_new = prev_count == 0

        self._ensure_connected()

        if is_new and self._loop and self._loop.is_running():
            # 새 종목이면 KIS에 구독 메시지 전송
            asyncio.run_coroutine_threadsafe(
                self._request_subscribe(symbol), self._loop
            )
            logger.info("종목 구독 요청: %s", symbol)

    def unsubscribe(self, symbol: str, listener: Callable) -> None:
        """
        SSE 리스너 해제.

        구독자가 0이 되면 KIS에 구독 해제 요청도 전송한다.
        """
        with self._listener_lock:
            listeners = self._listeners.get(symbol, [])
            if listener in listeners:
                listeners.remove(listener)

            count = self._subscriptions.get(symbol, 0)
            if count > 0:
                self._subscriptions[symbol] = count - 1
            should_unsubscribe = self._subscriptions.get(symbol, 0) == 0

        if should_unsubscribe and self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._request_unsubscribe(symbol), self._loop
            )
            logger.info("종목 구독 해제 요청: %s", symbol)

    def get_snapshot(self, symbol: str) -> Optional[dict]:
        """
        캐시된 최신 trade + orderbook 스냅샷 반환.

        데이터가 전혀 없으면 None 반환.
        """
        trade = self._trade_cache.get(symbol)
        orderbook = self._orderbook_cache.get(symbol)

        if trade is None and orderbook is None:
            return None

        return {
            "trade": trade,
            "orderbook": orderbook,
            "updatedAt": datetime.now(tz=timezone.utc).isoformat(),
        }

    def ensure_connected(self) -> None:
        """외부에서 연결 보장을 요청할 때 사용 (views.py용 public alias)."""
        self._ensure_connected()

    # ------------------------------------------------------------------
    # Internal: Connection management
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        """스레드가 없거나 종료되었으면 새 백그라운드 스레드를 시작한다."""
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(
                    target=self._ws_loop,
                    daemon=True,
                    name="KisWebSocketThread",
                )
                self._thread.start()
                logger.info("KIS WebSocket 백그라운드 스레드 시작")

    def _ws_loop(self) -> None:
        """백그라운드 스레드에서 실행되는 asyncio 이벤트 루프."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        try:
            loop.run_until_complete(self._connect_and_listen())
        finally:
            loop.close()
            self._loop = None
            self._connected = False
            logger.info("KIS WebSocket 이벤트 루프 종료")

    # ------------------------------------------------------------------
    # Internal: Async WebSocket logic
    # ------------------------------------------------------------------

    async def _connect_and_listen(self) -> None:
        """WebSocket 연결 + 메시지 수신 루프 (재연결 포함)."""
        import os

        is_real = os.environ.get("KIS_IS_REAL", "false").lower() == "true"
        ws_url = KIS_WS_URL_REAL if is_real else KIS_WS_URL_MOCK

        while self._reconnect_count <= self._max_reconnect:
            try:
                logger.info(
                    "KIS WebSocket 연결 시도 (%d/%d): %s",
                    self._reconnect_count,
                    self._max_reconnect,
                    ws_url,
                )
                async with websockets.connect(
                    ws_url,
                    ping_interval=None,   # KIS 자체 PINGPONG 사용
                    ping_timeout=None,
                    open_timeout=30,
                    close_timeout=10,
                ) as ws:
                    self._ws = ws
                    self._connected = True
                    self._reconnect_count = 0
                    logger.info("KIS WebSocket 연결 성공")

                    # 현재 구독 중인 종목 재구독
                    with self._listener_lock:
                        symbols = [
                            s for s, c in self._subscriptions.items() if c > 0
                        ]
                    for symbol in symbols:
                        await self._send_subscribe(ws, TR_ID_TRADE, symbol)
                        await self._send_subscribe(ws, TR_ID_ORDERBOOK, symbol)

                    # 메시지 수신 루프
                    async for raw in ws:
                        self._on_message(raw)

            except websockets.exceptions.ConnectionClosedOK:
                logger.info("KIS WebSocket 정상 종료")
                break
            except Exception as exc:
                self._connected = False
                self._ws = None
                self._reconnect_count += 1
                if self._reconnect_count > self._max_reconnect:
                    logger.error(
                        "KIS WebSocket 최대 재연결 횟수(%d) 초과. 종료.",
                        self._max_reconnect,
                    )
                    break
                logger.warning(
                    "KIS WebSocket 연결 끊김 (시도 %d/%d): %s. 5초 후 재연결.",
                    self._reconnect_count,
                    self._max_reconnect,
                    exc,
                )
                await asyncio.sleep(5)

        self._connected = False
        self._ws = None

    async def _send_subscribe(self, ws, tr_id: str, symbol: str) -> None:
        """KIS WebSocket에 구독 요청 메시지를 전송한다."""
        approval_key = get_approval_key()
        if not approval_key:
            logger.warning("approval_key 없음 - 구독 요청 불가: %s %s", tr_id, symbol)
            return

        msg = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": "1",
                "content-type": "utf-8",
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": symbol,
                }
            },
        }
        try:
            await ws.send(json.dumps(msg))
            logger.debug("구독 전송: tr_id=%s symbol=%s", tr_id, symbol)
        except Exception as exc:
            logger.error("구독 전송 실패: %s", exc)

    async def _send_unsubscribe(self, ws, tr_id: str, symbol: str) -> None:
        """KIS WebSocket에 구독 해제 메시지를 전송한다."""
        approval_key = get_approval_key()
        if not approval_key:
            return

        msg = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": "2",   # 2 = 구독 해제
                "content-type": "utf-8",
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": symbol,
                }
            },
        }
        try:
            await ws.send(json.dumps(msg))
            logger.debug("구독 해제 전송: tr_id=%s symbol=%s", tr_id, symbol)
        except Exception as exc:
            logger.error("구독 해제 전송 실패: %s", exc)

    async def _request_subscribe(self, symbol: str) -> None:
        """현재 연결된 ws에 체결가 + 호가 구독 요청."""
        if self._ws is None or not self._connected:
            return
        await self._send_subscribe(self._ws, TR_ID_TRADE, symbol)
        await self._send_subscribe(self._ws, TR_ID_ORDERBOOK, symbol)

    async def _request_unsubscribe(self, symbol: str) -> None:
        """현재 연결된 ws에 체결가 + 호가 구독 해제 요청."""
        if self._ws is None or not self._connected:
            return
        await self._send_unsubscribe(self._ws, TR_ID_TRADE, symbol)
        await self._send_unsubscribe(self._ws, TR_ID_ORDERBOOK, symbol)

    def _send_pong(self, raw: str) -> None:
        """PINGPONG 응답을 비동기로 전송 (동기 컨텍스트에서 호출)."""
        if self._loop and self._loop.is_running() and self._ws:
            asyncio.run_coroutine_threadsafe(
                self._ws.send(raw), self._loop
            )

    # ------------------------------------------------------------------
    # Internal: Message handling
    # ------------------------------------------------------------------

    @staticmethod
    def _decrypt_aes(key: str, iv: str, ciphertext_b64: str) -> str:
        """
        KIS WebSocket AES-256-CBC 복호화.

        KIS는 구독 응답에서 받은 key(32바이트)와 iv(16바이트)로
        실시간 데이터를 AES-256-CBC + PKCS7 패딩으로 암호화해서 전송한다.
        """
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad

        key_bytes = key.encode("utf-8")   # 32 bytes → AES-256
        iv_bytes = iv.encode("utf-8")     # 16 bytes
        ciphertext = base64.b64decode(ciphertext_b64)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode("utf-8")

    def _on_message(self, raw: str) -> None:
        """
        수신 메시지 분기 처리.

        JSON 제어 메시지 (구독 응답, PINGPONG)와
        파이프('|') 구분 데이터 메시지를 구분하여 처리한다.

        데이터 메시지 형식: "암호화여부|tr_id|건수|데이터본문"
          - 암호화여부 == "0": 평문
          - 암호화여부 == "1": AES-256-CBC (구독 응답의 iv/key로 복호화)
        """
        try:
            # 1. JSON 제어 메시지 (구독 응답 또는 PINGPONG)
            if raw.startswith("{"):
                msg = json.loads(raw)
                header = msg.get("header", {})

                if header.get("tr_id") == "PINGPONG":
                    self._send_pong(raw)
                    logger.debug("PINGPONG 수신 및 응답")
                    return

                # 구독 성공/실패 응답 — iv/key 수신 시 저장
                body = msg.get("body", {})
                output = body.get("output", {})
                tr_id = header.get("tr_id", "")
                iv = output.get("iv", "")
                key = output.get("key", "")
                if iv and key:
                    self._aes_keys[tr_id] = (iv, key)
                    logger.info("AES 키 저장: tr_id=%s", tr_id)
                else:
                    logger.info("구독 응답: tr_id=%s msg=%s", tr_id, output)
                return

            # 2. 데이터 메시지: "암호화여부|tr_id|건수|데이터본문"
            parts = raw.split("|")
            if len(parts) < 4:
                logger.debug("파이프 분리 필드 부족: %s", raw[:100])
                return

            encrypted_flag = parts[0]
            tr_id = parts[1]
            body = parts[3]

            # 암호화된 경우 복호화
            if encrypted_flag == "1":
                aes = self._aes_keys.get(tr_id)
                if aes is None:
                    logger.warning("암호화 데이터 수신했으나 AES 키 없음: tr_id=%s", tr_id)
                    return
                try:
                    body = self._decrypt_aes(aes[1], aes[0], body)
                except Exception as exc:
                    logger.error("AES 복호화 실패: tr_id=%s err=%s", tr_id, exc)
                    return

            if tr_id == TR_ID_TRADE:
                trade = parse_trade(body)
                if trade:
                    symbol = trade["symbol"]
                    self._trade_cache[symbol] = trade
                    self._notify_listeners(symbol, "trade", trade)

            elif tr_id == TR_ID_ORDERBOOK:
                orderbook = parse_orderbook(body)
                if orderbook:
                    symbol = orderbook["symbol"]
                    self._orderbook_cache[symbol] = orderbook
                    self._notify_listeners(symbol, "orderbook", orderbook)

            else:
                logger.debug("미처리 tr_id: %s", tr_id)

        except Exception as exc:
            logger.error("메시지 처리 오류: %s | raw=%s", exc, raw[:200])

    def _notify_listeners(self, symbol: str, event_type: str, data: dict) -> None:
        """등록된 모든 SSE 리스너에게 이벤트를 전달한다."""
        with self._listener_lock:
            listeners = list(self._listeners.get(symbol, []))

        for listener in listeners:
            try:
                listener(event_type, data)
            except Exception as exc:
                logger.warning("리스너 호출 오류 (symbol=%s): %s", symbol, exc)
