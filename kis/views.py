"""
KIS 실시간 주식 데이터 API 뷰

엔드포인트:
  GET /api/kis/snapshot/<symbol>/  - 캐시된 최신 스냅샷 반환 (REST)
  GET /api/kis/stream/<symbol>/    - 실시간 SSE 스트리밍
"""

import json
import logging
import os
import queue
import time

from django.http import StreamingHttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response


class ServerSentEventRenderer(BaseRenderer):
    """SSE(text/event-stream) 응답을 위한 DRF 렌더러."""

    media_type = "text/event-stream"
    format = "event-stream"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

from kis.constants import KR_STOCK_MAP
from kis.services.kis_websocket import KisWebSocketManager

logger = logging.getLogger("kis")

_SYMBOL_WAIT_SECONDS = 5  # 스냅샷 데이터 대기 시간


def _is_valid_symbol(symbol: str) -> bool:
    """6자리 숫자 종목코드 검증."""
    return bool(symbol) and len(symbol) == 6 and symbol.isdigit()


def _kis_configured() -> bool:
    """KIS_APP_KEY 환경변수 설정 여부 확인."""
    return bool(os.environ.get("KIS_APP_KEY"))


# ---------------------------------------------------------------------------
# Snapshot View
# ---------------------------------------------------------------------------

@swagger_auto_schema(
    method="get",
    operation_summary="KIS 종목 스냅샷",
    operation_description="캐시된 최신 체결가 + 호가 데이터를 반환한다. KIS WebSocket 미연결 시 잠시 대기 후 재시도.",
    manual_parameters=[
        openapi.Parameter(
            "symbol",
            openapi.IN_PATH,
            description="KRX 종목코드 6자리 (예: 005930)",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: openapi.Response(
            description="스냅샷 성공",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "symbol": "005930",
                        "name": "삼성전자",
                        "trade": {"price": 58300, "change": -200},
                        "orderbook": {"totalAskVolume": 55550},
                        "updatedAt": "2026-03-28T15:00:00+00:00",
                    },
                }
            },
        ),
        400: "유효하지 않은 종목코드",
        404: "데이터 없음",
        503: "KIS 설정 미비",
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def snapshot(request, symbol: str):
    """종목의 최신 체결가 + 호가 스냅샷 반환."""
    if not _is_valid_symbol(symbol):
        return Response(
            {
                "success": False,
                "error": {
                    "message": "유효하지 않은 종목코드입니다. 6자리 숫자를 입력하세요.",
                    "code": "INVALID_SYMBOL",
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # KIS 미설정 시 graceful degradation
    if not _kis_configured():
        logger.warning("KIS_APP_KEY 미설정 - snapshot 요청 무시 (symbol=%s)", symbol)
        return Response(
            {
                "success": False,
                "error": {
                    "message": "KIS OpenAPI가 설정되지 않았습니다.",
                    "code": "KIS_NOT_CONFIGURED",
                },
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    manager = KisWebSocketManager()
    data = manager.get_snapshot(symbol)

    if data is None:
        # WebSocket 데이터가 없으면 연결을 보장한 뒤 잠시 대기 후 1회 재시도
        manager.ensure_connected()
        logger.info("스냅샷 없음 - %d초 대기 후 재시도 (symbol=%s)", _SYMBOL_WAIT_SECONDS, symbol)
        time.sleep(_SYMBOL_WAIT_SECONDS)
        data = manager.get_snapshot(symbol)

    name = KR_STOCK_MAP.get(symbol, symbol)

    # 장 마감 등으로 데이터 미수신 시 200 + null (연결은 정상)
    if data is None:
        return Response(
            {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "name": name,
                    "trade": None,
                    "orderbook": None,
                    "updatedAt": None,
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "success": True,
            "data": {
                "symbol": symbol,
                "name": name,
                "trade": data.get("trade"),
                "orderbook": data.get("orderbook"),
                "updatedAt": data.get("updatedAt"),
            },
        },
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------------
# SSE Stream View
# ---------------------------------------------------------------------------

def stream(request, symbol):
    """
    SSE 스트리밍 뷰.

    KIS WebSocket 체결가/호가 데이터를 Server-Sent Events로 실시간 중계한다.
    30초마다 ping 이벤트를 전송하여 연결을 유지한다.
    클라이언트 연결 종료 시 구독을 해제한다.

    KIS 미설정 시 ping만 전송하는 degraded 스트림을 반환한다.
    """
    if not _is_valid_symbol(symbol):
        def _error_gen():
            yield 'event: error\ndata: {"message": "invalid symbol", "code": "INVALID_SYMBOL"}\n\n'

        return StreamingHttpResponse(
            _error_gen(),
            content_type="text/event-stream",
            status=400,
        )

    # KIS 미설정: ping만 전송하는 degraded 스트림
    if not _kis_configured():
        logger.warning("KIS_APP_KEY 미설정 - degraded SSE 스트림 반환 (symbol=%s)", symbol)

        def _degraded_gen():
            while True:
                yield "event: ping\ndata: {}\n\n"
                time.sleep(30)

        resp = StreamingHttpResponse(
            _degraded_gen(),
            content_type="text/event-stream",
        )
        resp["Cache-Control"] = "no-cache"
        resp["X-Accel-Buffering"] = "no"
        return resp

    # 정상 SSE 스트림
    q: queue.Queue = queue.Queue(maxsize=100)

    def listener(event_type: str, data: dict) -> None:
        try:
            q.put_nowait((event_type, data))
        except queue.Full:
            pass  # 클라이언트가 느리면 이벤트 드랍

    manager = KisWebSocketManager()
    manager.subscribe(symbol, listener)

    def event_stream():
        try:
            yield f"event: connected\ndata: {json.dumps({'symbol': symbol})}\n\n"

            snap = manager.get_snapshot(symbol)
            if snap:
                if snap.get("trade"):
                    yield f"event: trade\ndata: {json.dumps(snap['trade'])}\n\n"
                if snap.get("orderbook"):
                    yield f"event: orderbook\ndata: {json.dumps(snap['orderbook'])}\n\n"

            last_ping = time.time()

            while True:
                try:
                    event_type, data = q.get(timeout=1.0)
                    yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                except queue.Empty:
                    pass

                if time.time() - last_ping > 15:
                    yield "event: ping\ndata: {}\n\n"
                    last_ping = time.time()

        except GeneratorExit:
            pass
        finally:
            manager.unsubscribe(symbol, listener)
            logger.info("SSE 연결 종료: symbol=%s", symbol)

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # nginx 버퍼링 비활성화
    return response
