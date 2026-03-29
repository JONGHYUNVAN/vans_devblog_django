"""
KIS WebSocket 수신 데이터 파싱

H0STCNT0 (체결가), H0STASP0 (호가) 메시지를 파이썬 딕셔너리로 변환한다.
"""

import logging

logger = logging.getLogger("kis")


def _safe_int(value: str) -> int | None:
    """문자열을 int로 변환. 실패 시 None."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_float(value: str) -> float | None:
    """문자열을 float로 변환. 실패 시 None."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_trade(body: str) -> dict | None:
    """
    체결가(H0STCNT0) 데이터 파싱.

    body는 ^ 구분자로 분리된 필드열이다.
    KIS WebSocket 수신 메시지에서 '|'로 분리한 뒤 parts[3] 이후를 넘겨받는다.

    필드 인덱스 (0-based):
      [0]  유가증권단축종목코드
      [1]  주식체결시간 (HHMMSS)
      [2]  주식현재가
      [3]  전일대비부호 (1:상한 2:상승 3:보합 4:하한 5:하락)
      [4]  전일대비
      [5]  전일대비율
      [6]  가중평균주식가격
      [7]  주식시가
      [8]  주식최고가
      [9]  주식최저가
      [10] 매도호가1
      [11] 매수호가1
      [12] 체결거래량
      [13] 누적거래량
      [14] 누적거래대금

    Returns:
        dict 또는 None (파싱 실패 시)
    """
    try:
        fields = body.split("^")
        if len(fields) < 15:
            logger.warning("체결가 데이터 필드 수 부족: %d개 (기대 >=15)", len(fields))
            return None

        return {
            "symbol": fields[0].strip(),
            "time": fields[1].strip(),
            "price": _safe_int(fields[2]),
            "changeSign": fields[3].strip(),
            "change": _safe_int(fields[4]),
            "changePercent": _safe_float(fields[5]),
            "open": _safe_int(fields[7]),
            "high": _safe_int(fields[8]),
            "low": _safe_int(fields[9]),
            "prevClose": None,  # 체결 데이터에 직접 포함되지 않음
            "volume": _safe_int(fields[13]),
            "amount": _safe_int(fields[14]),
        }
    except Exception as exc:
        logger.error("체결가 파싱 오류: %s | body=%s", exc, body[:200])
        return None


def parse_orderbook(body: str) -> dict | None:
    """
    호가(H0STASP0) 데이터 파싱.

    body는 ^ 구분자로 분리된 필드열이다.

    필드 인덱스 (0-based):
      [0]       종목코드
      [1]       영업시간
      [2]       시간구분코드
      [3]~[12]  매도호가1~10
      [13]~[22] 매수호가1~10
      [23]~[32] 매도잔량1~10
      [33]~[42] 매수잔량1~10
      [43]      총매도호가잔량
      [44]      총매수호가잔량

    Returns:
        dict 또는 None (파싱 실패 시)
    """
    try:
        fields = body.split("^")
        if len(fields) < 45:
            logger.warning("호가 데이터 필드 수 부족: %d개 (기대 >=45)", len(fields))
            return None

        ask_prices = [_safe_int(fields[i]) for i in range(3, 13)]
        bid_prices = [_safe_int(fields[i]) for i in range(13, 23)]
        ask_volumes = [_safe_int(fields[i]) for i in range(23, 33)]
        bid_volumes = [_safe_int(fields[i]) for i in range(33, 43)]

        return {
            "symbol": fields[0].strip(),
            "time": fields[1].strip(),
            "askPrices": ask_prices,
            "askVolumes": ask_volumes,
            "bidPrices": bid_prices,
            "bidVolumes": bid_volumes,
            "totalAskVolume": _safe_int(fields[43]),
            "totalBidVolume": _safe_int(fields[44]),
        }
    except Exception as exc:
        logger.error("호가 파싱 오류: %s | body=%s", exc, body[:200])
        return None
