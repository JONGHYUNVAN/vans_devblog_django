"""
KIS 앱 테스트 (pytest 스타일)

테스트 대상:
  - kis_parser: parse_trade, parse_orderbook
  - kis_auth: get_approval_key (캐시 & API 호출)
  - KisWebSocketManager: get_snapshot, subscribe/unsubscribe, _on_message
  - views: snapshot / stream 엔드포인트
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests as req
from django.urls import reverse
from rest_framework import status

from kis.services.kis_parser import parse_orderbook, parse_trade


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_kis_singleton():
    """각 테스트마다 KisWebSocketManager 싱글톤을 리셋."""
    from kis.services.kis_websocket import KisWebSocketManager
    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None
    yield
    with KisWebSocketManager._lock:
        KisWebSocketManager._instance = None


@pytest.fixture
def manager():
    """깨끗한 KisWebSocketManager 인스턴스 반환."""
    from kis.services.kis_websocket import KisWebSocketManager
    return KisWebSocketManager()


def _trade_body(overrides: dict | None = None) -> str:
    """테스트용 체결가 데이터 본문 생성 (^ 구분자, 15개 필드)."""
    fields = [
        "005930",        # [0]  종목코드
        "153000",        # [1]  체결시간
        "58300",         # [2]  현재가
        "2",             # [3]  전일대비부호
        "200",           # [4]  전일대비
        "0.34",          # [5]  전일대비율
        "58200",         # [6]  가중평균가
        "58000",         # [7]  시가
        "58500",         # [8]  고가
        "57800",         # [9]  저가
        "58310",         # [10] 매도호가1
        "58290",         # [11] 매수호가1
        "100",           # [12] 체결거래량
        "5000000",       # [13] 누적거래량
        "290000000000",  # [14] 누적거래대금
    ]
    if overrides:
        for idx, val in overrides.items():
            fields[idx] = val
    return "^".join(fields)


def _orderbook_body() -> str:
    """테스트용 호가 데이터 본문 생성 (^ 구분자, 45개 필드)."""
    fields = ["005930", "153000", "0"]
    fields += [str(58300 + i * 10) for i in range(10)]   # 매도호가 10개
    fields += [str(58290 - i * 10) for i in range(10)]   # 매수호가 10개
    fields += [str(1000 + i * 100) for i in range(10)]   # 매도잔량 10개
    fields += [str(900 + i * 100) for i in range(10)]    # 매수잔량 10개
    fields += ["55000", "49500"]                          # 총매도/총매수잔량
    return "^".join(fields)


# ---------------------------------------------------------------------------
# 1. kis_parser
# ---------------------------------------------------------------------------

class TestParseTrade:
    """parse_trade 단위 테스트"""

    def test_valid_body(self):
        result = parse_trade(_trade_body())
        assert result is not None
        assert result["symbol"] == "005930"
        assert result["price"] == 58300
        assert result["change"] == 200
        assert abs(result["changePercent"] - 0.34) < 0.001
        assert result["open"] == 58000
        assert result["high"] == 58500
        assert result["low"] == 57800
        assert result["volume"] == 5000000

    def test_insufficient_fields_returns_none(self):
        assert parse_trade("005930^153000^58300") is None

    def test_non_numeric_price_allows_none(self):
        result = parse_trade(_trade_body({2: "NOT_A_NUMBER"}))
        assert result is not None
        assert result["price"] is None

    def test_empty_body_returns_none(self):
        assert parse_trade("") is None


class TestParseOrderbook:
    """parse_orderbook 단위 테스트"""

    def test_valid_body(self):
        result = parse_orderbook(_orderbook_body())
        assert result is not None
        assert result["symbol"] == "005930"
        assert len(result["askPrices"]) == 10
        assert len(result["bidPrices"]) == 10
        assert len(result["askVolumes"]) == 10
        assert len(result["bidVolumes"]) == 10
        assert result["totalAskVolume"] == 55000
        assert result["totalBidVolume"] == 49500

    def test_insufficient_fields_returns_none(self):
        assert parse_orderbook("005930^153000") is None


# ---------------------------------------------------------------------------
# 2. kis_auth
# ---------------------------------------------------------------------------

class TestGetApprovalKey:
    """get_approval_key 단위 테스트"""

    def test_missing_env_returns_none(self):
        from kis.services.kis_auth import get_approval_key
        with patch.dict("os.environ", {}, clear=True):
            assert get_approval_key() is None

    def test_cache_hit_skips_api(self):
        from kis.services.kis_auth import get_approval_key
        with patch.dict("os.environ", {"KIS_APP_KEY": "k", "KIS_APP_SECRET": "s"}):
            with patch("kis.services.kis_auth.cache") as mock_cache:
                mock_cache.get.return_value = "cached_key"
                result = get_approval_key()
        assert result == "cached_key"

    def test_cache_miss_calls_api_and_caches(self):
        from kis.services.kis_auth import get_approval_key
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"approval_key": "new_key"}
        mock_resp.raise_for_status.return_value = None

        with patch.dict("os.environ", {"KIS_APP_KEY": "k", "KIS_APP_SECRET": "s"}):
            with patch("kis.services.kis_auth.cache") as mock_cache:
                mock_cache.get.return_value = None
                with patch("kis.services.kis_auth.requests.post", return_value=mock_resp):
                    result = get_approval_key()

        assert result == "new_key"
        mock_cache.set.assert_called_once()

    def test_api_failure_returns_none(self):
        from kis.services.kis_auth import get_approval_key
        with patch.dict("os.environ", {"KIS_APP_KEY": "k", "KIS_APP_SECRET": "s"}):
            with patch("kis.services.kis_auth.cache") as mock_cache:
                mock_cache.get.return_value = None
                with patch(
                    "kis.services.kis_auth.requests.post",
                    side_effect=req.RequestException("timeout"),
                ):
                    result = get_approval_key()
        assert result is None


# ---------------------------------------------------------------------------
# 3. KisWebSocketManager
# ---------------------------------------------------------------------------

class TestKisWebSocketManager:
    """KisWebSocketManager 단위 테스트 (실제 WebSocket 연결 없음)"""

    def test_get_snapshot_empty_cache_returns_none(self, manager):
        assert manager.get_snapshot("005930") is None

    def test_get_snapshot_trade_only(self, manager):
        manager._trade_cache["005930"] = {"price": 58300}
        result = manager.get_snapshot("005930")
        assert result is not None
        assert result["trade"]["price"] == 58300
        assert result["orderbook"] is None

    def test_get_snapshot_both_caches(self, manager):
        manager._trade_cache["005930"] = {"price": 58300}
        manager._orderbook_cache["005930"] = {"totalAskVolume": 55000}
        result = manager.get_snapshot("005930")
        assert result["trade"]["price"] == 58300
        assert result["orderbook"]["totalAskVolume"] == 55000
        assert "updatedAt" in result

    def test_subscribe_registers_listener(self, manager):
        listener = MagicMock()
        with patch.object(manager, "_ensure_connected"):
            manager.subscribe("005930", listener)
        with manager._listener_lock:
            assert listener in manager._listeners["005930"]
            assert manager._subscriptions["005930"] == 1

    def test_subscribe_increments_count_for_duplicate(self, manager):
        l1, l2 = MagicMock(), MagicMock()
        with patch.object(manager, "_ensure_connected"):
            manager.subscribe("005930", l1)
            manager.subscribe("005930", l2)
        with manager._listener_lock:
            assert manager._subscriptions["005930"] == 2

    def test_unsubscribe_removes_listener(self, manager):
        listener = MagicMock()
        with patch.object(manager, "_ensure_connected"):
            manager.subscribe("005930", listener)
        manager.unsubscribe("005930", listener)
        with manager._listener_lock:
            assert listener not in manager._listeners.get("005930", [])
            assert manager._subscriptions.get("005930", 0) == 0

    def test_notify_listeners_calls_all(self, manager):
        cb1, cb2 = MagicMock(), MagicMock()
        manager._listeners["005930"] = [cb1, cb2]
        manager._notify_listeners("005930", "trade", {"price": 58300})
        cb1.assert_called_once_with("trade", {"price": 58300})
        cb2.assert_called_once_with("trade", {"price": 58300})

    def test_on_message_pingpong_calls_send_pong(self, manager):
        raw = json.dumps({"header": {"tr_id": "PINGPONG"}, "body": {}})
        with patch.object(manager, "_send_pong") as mock_pong:
            manager._on_message(raw)
        mock_pong.assert_called_once_with(raw)

    def test_on_message_trade_updates_cache(self, manager):
        raw = f"0|H0STCNT0|1|{_trade_body()}"
        listener = MagicMock()
        manager._listeners["005930"] = [listener]
        manager._on_message(raw)
        assert "005930" in manager._trade_cache
        assert manager._trade_cache["005930"]["price"] == 58300
        listener.assert_called_once()
        event_type, data = listener.call_args[0]
        assert event_type == "trade"

    def test_on_message_orderbook_updates_cache(self, manager):
        raw = f"0|H0STASP0|1|{_orderbook_body()}"
        manager._on_message(raw)
        assert "005930" in manager._orderbook_cache
        assert manager._orderbook_cache["005930"]["totalAskVolume"] == 55000

    def test_on_message_malformed_does_not_raise(self, manager):
        manager._on_message("MALFORMED_DATA")  # 예외 없이 통과


# ---------------------------------------------------------------------------
# 4. views - snapshot
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSnapshotView:
    """GET /api/kis/snapshot/<symbol>/ 테스트"""

    def test_invalid_symbol_returns_400(self, api_client):
        response = api_client.get("/api/kis/snapshot/INVALID/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["error"]["code"] == "INVALID_SYMBOL"

    def test_short_symbol_returns_400(self, api_client):
        response = api_client.get("/api/kis/snapshot/12345/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_kis_not_configured_returns_503(self, api_client):
        with patch.dict("os.environ", {}, clear=True):
            response = api_client.get("/api/kis/snapshot/005930/")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()["error"]["code"] == "KIS_NOT_CONFIGURED"

    def test_no_data_returns_200_with_null(self, api_client):
        """장 마감 등 데이터 미수신 시 200 + null 반환."""
        with patch.dict("os.environ", {"KIS_APP_KEY": "test"}):
            with patch("kis.views.KisWebSocketManager") as MockMgr:
                inst = MockMgr.return_value
                inst.get_snapshot.return_value = None
                inst.ensure_connected.return_value = None
                with patch("kis.views.time.sleep"):
                    response = api_client.get("/api/kis/snapshot/005930/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["trade"] is None
        assert data["data"]["orderbook"] is None
        assert data["data"]["symbol"] == "005930"

    def test_success_returns_200(self, api_client):
        fake_snapshot = {
            "trade": {"price": 58300, "change": 200},
            "orderbook": {"totalAskVolume": 55000},
            "updatedAt": "2026-03-28T15:00:00+00:00",
        }
        with patch.dict("os.environ", {"KIS_APP_KEY": "test"}):
            with patch("kis.views.KisWebSocketManager") as MockMgr:
                MockMgr.return_value.get_snapshot.return_value = fake_snapshot
                response = api_client.get("/api/kis/snapshot/005930/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["symbol"] == "005930"
        assert data["data"]["name"] == "삼성전자"
        assert data["data"]["trade"]["price"] == 58300

    def test_name_fallback_to_symbol(self, api_client):
        """KR_STOCK_MAP에 없는 종목코드는 name에 symbol 그대로 반환."""
        fake_snapshot = {
            "trade": {"price": 10000},
            "orderbook": None,
            "updatedAt": "2026-03-28T15:00:00+00:00",
        }
        with patch.dict("os.environ", {"KIS_APP_KEY": "test"}):
            with patch("kis.views.KisWebSocketManager") as MockMgr:
                MockMgr.return_value.get_snapshot.return_value = fake_snapshot
                response = api_client.get("/api/kis/snapshot/999999/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["name"] == "999999"


# ---------------------------------------------------------------------------
# 5. views - stream
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStreamView:
    """GET /api/kis/stream/<symbol>/ 테스트"""

    def test_invalid_symbol_returns_400_sse(self, api_client):
        response = api_client.get("/api/kis/stream/INVALID/")
        assert response.status_code == 400
        assert "text/event-stream" in response["Content-Type"]

    def test_kis_not_configured_returns_degraded_stream(self, api_client):
        with patch.dict("os.environ", {}, clear=True):
            response = api_client.get("/api/kis/stream/005930/")
        assert response.status_code == 200
        assert "text/event-stream" in response["Content-Type"]
