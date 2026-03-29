"""
KIS E2E 테스트 (실제 KIS 서버 연결)

KIS_APP_KEY / KIS_APP_SECRET 환경변수가 설정되어 있어야 실행된다.
미설정 시 전체 건너뜀(skip).

실행:
    pytest tests/test_kis_e2e.py -v -s

주의:
    - 모의투자 서버(KIS_IS_REAL=false) 기준
    - 체결가/호가 데이터는 장 운영 시간(09:00~15:30)에만 수신된다
    - 장 외 시간에도 WebSocket 연결·인증·구독 응답 자체는 검증 가능
"""

import os
import time
import threading

import pytest
from dotenv import load_dotenv

# .env 파일 명시적 로드 (테스트 환경에서 누락될 수 있으므로)
load_dotenv(override=True)


def _kis_available() -> bool:
    return bool(os.environ.get("KIS_APP_KEY")) and bool(os.environ.get("KIS_APP_SECRET"))


kis_required = pytest.mark.skipif(
    not _kis_available(),
    reason="KIS_APP_KEY / KIS_APP_SECRET 환경변수 미설정 — E2E 테스트 건너뜀",
)


# ---------------------------------------------------------------------------
# 1. 인증 (approval_key 발급)
# ---------------------------------------------------------------------------

@kis_required
def test_get_approval_key_from_real_server():
    """
    실제 KIS REST API에서 approval_key를 발급받는다.
    응답이 있고 비어 있지 않으면 성공.
    """
    from django.core.cache import cache
    cache.clear()  # 캐시 초기화 후 실제 API 호출 강제

    from kis.services.kis_auth import get_approval_key
    key = get_approval_key()

    assert key is not None, "approval_key 발급 실패 (None 반환)"
    assert len(key) > 10, f"approval_key가 너무 짧습니다: {key!r}"
    print(f"\n[OK] approval_key 발급 성공 (앞 10자): {key[:10]}...")


# ---------------------------------------------------------------------------
# 2. WebSocket 연결 및 구독 응답
# ---------------------------------------------------------------------------

@kis_required
def test_websocket_connection_and_subscription_response():
    """
    실제 KIS WebSocket 서버에 연결하고 종목 구독 응답을 수신한다.

    구독 응답(JSON)이 수신되면 성공.
    장 외 시간에도 구독 응답 자체는 온다.
    """
    from kis.services.kis_websocket import KisWebSocketManager

    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None

    manager = KisWebSocketManager()

    subscription_ack = threading.Event()
    original_on_message = manager._on_message

    def spy_on_message(raw: str):
        original_on_message(raw)
        # KIS는 구독 요청에 JSON 응답을 보낸다
        if raw.startswith("{"):
            subscription_ack.set()

    manager._on_message = spy_on_message

    # 구독 등록 후 연결
    dummy_listener = lambda event_type, data: None
    manager.subscribe("005930", dummy_listener)

    # 구독 응답 대기 (최대 15초)
    received = subscription_ack.wait(timeout=15.0)

    manager.unsubscribe("005930", dummy_listener)

    reconnect_count = manager._reconnect_count
    connected = manager._connected
    print(
        f"\n[DEBUG] connected={connected} "
        f"reconnect_count={reconnect_count} "
        f"subscription_ack={received}"
    )

    if not received and not connected:
        pytest.skip(
            f"KIS WebSocket 연결 불가 (reconnect_count={reconnect_count}) — "
            "포트 31000(모의)/21000(실전) 아웃바운드가 방화벽에서 차단되어 있습니다. "
            "공유기 또는 Windows 방화벽에서 ops.koreainvestment.com:31000 TCP 허용 후 재시도하세요."
        )

    assert received, (
        f"WS 연결은 됐으나 15초 내 구독 응답 없음 "
        f"(connected={connected}) — 인증 키를 확인하세요"
    )
    print("[OK] KIS WebSocket 연결 및 구독 응답 확인")

    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None


# ---------------------------------------------------------------------------
# 3. 실시간 체결가 수신 (장 중 한정)
# ---------------------------------------------------------------------------

@kis_required
@pytest.mark.slow
def test_trade_data_received_during_market_hours():
    """
    실제 체결가(H0STCNT0) 데이터를 수신한다.

    장 운영 시간(평일 09:00~15:30)에만 데이터가 들어온다.
    장 외 시간에는 timeout으로 skip 처리된다.
    """
    from kis.services.kis_websocket import KisWebSocketManager

    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None

    manager = KisWebSocketManager()
    trade_received = threading.Event()

    def listener(event_type, data):
        if event_type == "trade":
            trade_received.set()

    manager.subscribe("005930", listener)

    # 체결가 데이터 대기 (최대 30초)
    received = trade_received.wait(timeout=30.0)

    manager.unsubscribe("005930", listener)

    if not received:
        pytest.skip("30초 내 체결가 데이터 없음 — 장 외 시간이거나 모의서버 미지원")

    snapshot = manager.get_snapshot("005930")
    assert snapshot is not None
    assert snapshot["trade"] is not None
    assert isinstance(snapshot["trade"]["price"], int)
    assert snapshot["trade"]["price"] > 0

    print(f"\n✓ 삼성전자(005930) 체결가: {snapshot['trade']['price']:,}원")

    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None


# ---------------------------------------------------------------------------
# 4. 실시간 호가 수신 (장 중 한정)
# ---------------------------------------------------------------------------

@kis_required
@pytest.mark.slow
def test_orderbook_data_received_during_market_hours():
    """
    실제 호가(H0STASP0) 데이터를 수신한다.
    """
    from kis.services.kis_websocket import KisWebSocketManager

    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None

    manager = KisWebSocketManager()
    ob_received = threading.Event()

    def listener(event_type, data):
        if event_type == "orderbook":
            ob_received.set()

    manager.subscribe("005930", listener)

    received = ob_received.wait(timeout=30.0)

    manager.unsubscribe("005930", listener)

    if not received:
        pytest.skip("30초 내 호가 데이터 없음 — 장 외 시간이거나 모의서버 미지원")

    snapshot = manager.get_snapshot("005930")
    assert snapshot["orderbook"] is not None
    assert len(snapshot["orderbook"]["askPrices"]) == 10
    assert snapshot["orderbook"]["totalAskVolume"] > 0

    print(f"\n✓ 삼성전자(005930) 매도호가1: {snapshot['orderbook']['askPrices'][0]:,}원")

    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None


# ---------------------------------------------------------------------------
# 5. Snapshot REST 엔드포인트 E2E
# ---------------------------------------------------------------------------

@kis_required
@pytest.mark.slow
@pytest.mark.django_db
def test_snapshot_endpoint_with_real_kis(api_client):
    """
    /api/kis/snapshot/005930/ 엔드포인트가 실제 KIS 데이터를 반환한다.

    장 중: 200 + 실제 가격 데이터
    장 외: 404 (데이터 없음) 또는 200
    """
    response = api_client.get("/api/kis/snapshot/005930/")

    assert response.status_code in (200, 404, 503), (
        f"예상치 못한 상태코드: {response.status_code}"
    )

    data = response.json()

    if response.status_code == 200:
        assert data["success"] is True
        assert data["data"]["symbol"] == "005930"
        assert data["data"]["name"] == "삼성전자"
        print(f"\n✓ 스냅샷 응답: {data['data']}")
    elif response.status_code == 404:
        pytest.skip("스냅샷 데이터 없음 — 장 외 시간")
    elif response.status_code == 503:
        pytest.fail("KIS_APP_KEY 설정 문제")
