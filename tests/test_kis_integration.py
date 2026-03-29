"""
KIS 통합 테스트

외부 KIS 서버 없이:
  - 로컬 목 WebSocket 서버로 KisWebSocketManager 연결 흐름 검증
  - SSE event_stream 제너레이터 실제 이벤트 방출 검증
"""

import asyncio
import json
import queue
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
import websockets
from websockets.asyncio.server import serve


# ---------------------------------------------------------------------------
# 공통 헬퍼
# ---------------------------------------------------------------------------

TRADE_BODY = (
    "005930^153000^58300^2^200^0.34^58200"
    "^58000^58500^57800^58310^58290^100^5000000^290000000000"
)


def _orderbook_body() -> str:
    fields = ["005930", "153000", "0"]
    fields += [str(58300 + i * 10) for i in range(10)]
    fields += [str(58290 - i * 10) for i in range(10)]
    fields += [str(1000 + i * 100) for i in range(10)]
    fields += [str(900 + i * 100) for i in range(10)]
    fields += ["55000", "49500"]
    return "^".join(fields)


def _collect_stream(gen, count: int, timeout: float = 3.0) -> list[str]:
    """
    스트리밍 제너레이터에서 최대 count개 이벤트를 수집.

    별도 스레드에서 읽고 timeout 이내에 반환하므로 무한 루프에 안전하다.
    """
    events: list[str] = []
    done = threading.Event()

    def _reader():
        try:
            for chunk in gen:
                text = chunk.decode() if isinstance(chunk, bytes) else chunk
                events.append(text)
                if len(events) >= count:
                    done.set()
                    return
        except Exception:
            done.set()

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    done.wait(timeout=timeout)
    return events


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_kis_singleton():
    """각 테스트마다 KisWebSocketManager 싱글톤 리셋."""
    from kis.services.kis_websocket import KisWebSocketManager
    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None
    yield
    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None


@pytest.fixture
def manager():
    from kis.services.kis_websocket import KisWebSocketManager
    return KisWebSocketManager()


# ---------------------------------------------------------------------------
# 1. SSE event_stream 통합 테스트
# ---------------------------------------------------------------------------

class TestSSEEventStream:
    """
    SSE event_stream() 제너레이터 실제 동작 검증.

    view를 통하지 않고 StreamingHttpResponse.streaming_content 를
    직접 이터레이션하여 실제 이벤트 문자열을 확인한다.
    """

    def _get_stream_response(self, symbol: str, mock_manager):
        """KisWebSocketManager를 목으로 교체한 상태로 SSE 응답 반환."""
        with patch.dict("os.environ", {"KIS_APP_KEY": "test"}):
            with patch("kis.views.KisWebSocketManager", return_value=mock_manager):
                from rest_framework.test import APIClient
                client = APIClient()
                return client.get(f"/api/kis/stream/{symbol}/")

    def test_initial_trade_event_emitted(self, manager):
        """캐시에 체결가가 있으면 SSE 연결 즉시 trade 이벤트를 방출한다."""
        manager._trade_cache["005930"] = {"price": 58300, "symbol": "005930"}

        response = self._get_stream_response("005930", manager)

        assert response.status_code == 200
        assert "text/event-stream" in response["Content-Type"]

        events = _collect_stream(response.streaming_content, count=1, timeout=2.0)

        assert len(events) >= 1
        combined = "".join(events)
        assert "trade" in combined
        assert "58300" in combined

    def test_initial_orderbook_event_emitted(self, manager):
        """캐시에 호가가 있으면 SSE 연결 즉시 orderbook 이벤트를 방출한다."""
        manager._orderbook_cache["005930"] = {"totalAskVolume": 55000, "symbol": "005930"}

        response = self._get_stream_response("005930", manager)
        events = _collect_stream(response.streaming_content, count=1, timeout=2.0)

        combined = "".join(events)
        assert "orderbook" in combined
        assert "55000" in combined

    def test_both_snapshot_events_emitted(self, manager):
        """체결가 + 호가 캐시가 모두 있으면 trade → orderbook 순으로 방출한다."""
        manager._trade_cache["005930"] = {"price": 58300, "symbol": "005930"}
        manager._orderbook_cache["005930"] = {"totalAskVolume": 55000, "symbol": "005930"}

        response = self._get_stream_response("005930", manager)
        events = _collect_stream(response.streaming_content, count=2, timeout=2.0)

        combined = "".join(events)
        assert "trade" in combined
        assert "orderbook" in combined

    def test_listener_event_forwarded(self, manager):
        """
        subscribe로 등록된 리스너에 이벤트가 들어오면
        SSE 스트림으로 즉시 전달된다.
        """
        captured_listener = []
        original_subscribe = manager.subscribe

        def spy_subscribe(symbol, listener):
            captured_listener.append(listener)
            # _ensure_connected 없이 리스너만 등록
            with manager._listener_lock:
                manager._listeners[symbol].append(listener)
                manager._subscriptions[symbol] = manager._subscriptions.get(symbol, 0) + 1

        manager.subscribe = spy_subscribe
        manager.get_snapshot = MagicMock(return_value=None)

        response = self._get_stream_response("005930", manager)

        # 0.3초 후 리스너를 통해 이벤트 주입
        def inject():
            time.sleep(0.3)
            if captured_listener:
                captured_listener[0]("trade", {"price": 99999, "symbol": "005930"})

        threading.Thread(target=inject, daemon=True).start()

        events = _collect_stream(response.streaming_content, count=1, timeout=3.0)
        combined = "".join(events)

        assert "trade" in combined
        assert "99999" in combined

    def test_sse_response_headers(self, manager):
        """SSE 응답에 필수 헤더가 설정되어 있다."""
        manager.get_snapshot = MagicMock(return_value=None)

        response = self._get_stream_response("005930", manager)

        assert response["Cache-Control"] == "no-cache"
        assert response["X-Accel-Buffering"] == "no"


# ---------------------------------------------------------------------------
# 2. WebSocket 통합 테스트
# ---------------------------------------------------------------------------

class TestWebSocketIntegration:
    """
    로컬 목 WebSocket 서버를 띄워 KisWebSocketManager의
    실제 연결 → 메시지 수신 → 캐시 갱신 흐름을 검증한다.
    """

    @staticmethod
    def _start_mock_server(handler_coro, port_holder: list) -> None:
        """비동기 WebSocket 서버를 백그라운드 스레드에서 실행."""
        async def _run():
            async with serve(handler_coro, "localhost", 0) as server:
                port = server.sockets[0].getsockname()[1]
                port_holder.append(port)
                await asyncio.sleep(15)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_run())
        finally:
            loop.close()

    def _launch_server(self, handler_coro) -> int:
        """서버를 스레드로 시작하고 포트 번호를 반환한다."""
        port_holder: list = []
        t = threading.Thread(
            target=self._start_mock_server,
            args=(handler_coro, port_holder),
            daemon=True,
        )
        t.start()
        for _ in range(30):
            if port_holder:
                return port_holder[0]
            time.sleep(0.1)
        raise RuntimeError("목 WebSocket 서버가 시작되지 않았습니다")

    def test_manager_connects_and_processes_trade(self, manager):
        """
        KisWebSocketManager가 WS 서버에 연결하고
        체결가 메시지를 수신하여 _trade_cache를 갱신한다.
        """
        trade_sent = threading.Event()

        async def mock_server(websocket):
            # 구독 메시지 수신 시도 (없어도 무방)
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.0)
            except (asyncio.TimeoutError, Exception):
                pass

            await websocket.send(f"0|H0STCNT0|1|{TRADE_BODY}")
            trade_sent.set()
            await asyncio.sleep(10)

        port = self._launch_server(mock_server)

        with patch("kis.services.kis_auth.get_approval_key", return_value="fake_key"):
            with patch("kis.services.kis_websocket.KIS_WS_URL_MOCK", f"ws://localhost:{port}"):
                manager._ensure_connected()
                trade_sent.wait(timeout=5.0)
                time.sleep(0.3)  # _on_message 처리 완료 대기

        assert "005930" in manager._trade_cache
        assert manager._trade_cache["005930"]["price"] == 58300

    def test_manager_processes_orderbook(self, manager):
        """
        KisWebSocketManager가 호가 메시지를 수신하여
        _orderbook_cache를 갱신한다.
        """
        ob_sent = threading.Event()
        body = _orderbook_body()

        async def mock_server(websocket):
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.0)
            except (asyncio.TimeoutError, Exception):
                pass

            await websocket.send(f"0|H0STASP0|1|{body}")
            ob_sent.set()
            await asyncio.sleep(10)

        port = self._launch_server(mock_server)

        with patch("kis.services.kis_auth.get_approval_key", return_value="fake_key"):
            with patch("kis.services.kis_websocket.KIS_WS_URL_MOCK", f"ws://localhost:{port}"):
                manager._ensure_connected()
                ob_sent.wait(timeout=5.0)
                time.sleep(0.3)

        assert "005930" in manager._orderbook_cache
        assert manager._orderbook_cache["005930"]["totalAskVolume"] == 55000

    def test_manager_sends_subscription_on_connect(self, manager):
        """
        연결 후 구독 중인 종목에 대해 WS 서버로 구독 메시지를 전송한다.
        """
        received_messages = []
        all_received = threading.Event()

        async def mock_server(websocket):
            try:
                for _ in range(2):  # TRADE + ORDERBOOK 두 종목 구독
                    msg = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    received_messages.append(json.loads(msg))
                all_received.set()
            except (asyncio.TimeoutError, Exception):
                all_received.set()
            await asyncio.sleep(10)

        port = self._launch_server(mock_server)

        # 연결 전에 구독 등록
        with manager._listener_lock:
            manager._subscriptions["005930"] = 1

        with patch("kis.services.kis_auth.get_approval_key", return_value="fake_key"):
            with patch("kis.services.kis_websocket.KIS_WS_URL_MOCK", f"ws://localhost:{port}"):
                manager._ensure_connected()
                all_received.wait(timeout=5.0)

        assert len(received_messages) >= 1
        tr_ids = [m.get("body", {}).get("input", {}).get("tr_id") for m in received_messages]
        assert "H0STCNT0" in tr_ids  # 체결가 구독

    def test_manager_notifies_listeners_on_trade(self, manager):
        """
        WS에서 체결가 메시지를 수신하면 등록된 SSE 리스너가 호출된다.
        """
        listener_called = threading.Event()
        received_data = {}

        def listener(event_type, data):
            received_data["type"] = event_type
            received_data["data"] = data
            listener_called.set()

        trade_sent = threading.Event()

        async def mock_server(websocket):
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.0)
            except (asyncio.TimeoutError, Exception):
                pass
            await websocket.send(f"0|H0STCNT0|1|{TRADE_BODY}")
            trade_sent.set()
            await asyncio.sleep(10)

        port = self._launch_server(mock_server)

        with manager._listener_lock:
            manager._listeners["005930"].append(listener)
            manager._subscriptions["005930"] = 1

        with patch("kis.services.kis_auth.get_approval_key", return_value="fake_key"):
            with patch("kis.services.kis_websocket.KIS_WS_URL_MOCK", f"ws://localhost:{port}"):
                manager._ensure_connected()
                listener_called.wait(timeout=5.0)

        assert listener_called.is_set(), "리스너가 호출되지 않았습니다"
        assert received_data["type"] == "trade"
        assert received_data["data"]["price"] == 58300

    def test_manager_reconnects_after_disconnect(self, manager):
        """
        WS 서버가 연결을 끊으면 매니저가 재연결을 시도한다.
        """
        connect_count = [0]
        second_connected = threading.Event()

        async def mock_server(websocket):
            connect_count[0] += 1
            if connect_count[0] == 1:
                # 첫 번째 연결은 즉시 끊는다
                await websocket.close()
            else:
                second_connected.set()
                await asyncio.sleep(10)

        port = self._launch_server(mock_server)

        with patch("kis.services.kis_auth.get_approval_key", return_value="fake_key"):
            with patch("kis.services.kis_websocket.KIS_WS_URL_MOCK", f"ws://localhost:{port}"):
                with patch("kis.services.kis_websocket.KIS_WS_URL_REAL", f"ws://localhost:{port}"):
                    manager._ensure_connected()
                    second_connected.wait(timeout=10.0)

        assert second_connected.is_set(), "재연결이 발생하지 않았습니다"
        assert connect_count[0] >= 2
