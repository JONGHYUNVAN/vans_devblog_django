"""KIS OpenAPI 관련 상수 및 종목 매핑"""

# 대시보드에서 추적하는 국내 종목
KR_STOCK_MAP = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005380": "현대차",
}

# KIS WebSocket URL
KIS_WS_URL_REAL = "ws://ops.koreainvestment.com:21000"
KIS_WS_URL_MOCK = "ws://ops.koreainvestment.com:31000"

# KIS REST API URL
KIS_REST_URL_REAL = "https://openapi.koreainvestment.com:9443"
KIS_REST_URL_MOCK = "https://openapivts.koreainvestment.com:29443"

# 구독 TR ID
TR_ID_TRADE = "H0STCNT0"       # 실시간 체결가
TR_ID_ORDERBOOK = "H0STASP0"   # 실시간 호가
