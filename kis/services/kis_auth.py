"""
KIS OpenAPI 인증 토큰 관리

approval_key 발급 및 Django 캐시를 통한 재사용.
"""

import logging
import os

import requests
from django.core.cache import cache

from kis.constants import KIS_REST_URL_MOCK, KIS_REST_URL_REAL

logger = logging.getLogger("kis")

_CACHE_KEY = "kis_approval_key"
_CACHE_TIMEOUT = 82800  # 23시간 (approval_key 유효기간 24시간보다 1시간 일찍 만료)


def get_approval_key() -> str | None:
    """
    KIS WebSocket approval_key 발급.

    Django LocMemCache에 82800초 동안 캐시하여 재발급을 최소화한다.
    KIS_APP_KEY 또는 KIS_APP_SECRET 환경변수가 없으면 None 반환 (graceful degradation).

    Returns:
        str: approval_key 문자열, 또는 None (설정 미비 시)
    """
    app_key = os.environ.get("KIS_APP_KEY")
    app_secret = os.environ.get("KIS_APP_SECRET")

    if not app_key or not app_secret:
        logger.warning("KIS_APP_KEY 또는 KIS_APP_SECRET 환경변수가 설정되지 않았습니다.")
        return None

    # 캐시 히트 확인
    cached = cache.get(_CACHE_KEY)
    if cached:
        logger.debug("캐시에서 approval_key 반환")
        return cached

    # KIS REST API로 approval_key 발급
    is_real = os.environ.get("KIS_IS_REAL", "false").lower() == "true"
    rest_url = KIS_REST_URL_REAL if is_real else KIS_REST_URL_MOCK

    try:
        resp = requests.post(
            f"{rest_url}/oauth2/Approval",
            json={
                "grant_type": "client_credentials",
                "appkey": app_key,
                "secretkey": app_secret,
            },
            timeout=10,
        )
        resp.raise_for_status()
        approval_key = resp.json().get("approval_key")
        if not approval_key:
            logger.error("approval_key 응답에서 키를 찾을 수 없습니다: %s", resp.text)
            return None

        cache.set(_CACHE_KEY, approval_key, timeout=_CACHE_TIMEOUT)
        logger.info("approval_key 발급 및 캐시 완료 (timeout=%ds)", _CACHE_TIMEOUT)
        return approval_key

    except requests.RequestException as exc:
        logger.error("approval_key 발급 실패: %s", exc)
        return None
