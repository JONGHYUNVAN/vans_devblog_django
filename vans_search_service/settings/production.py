"""
VansDevBlog Search Service Production Settings

운영 환경에서 사용되는 Django 설정입니다.
"""

import logging.config
import os
import socket
from pathlib import Path

from .base import *  # 모든 기본 설정 import

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

DEBUG = False

ALLOWED_HOSTS = [
    ".cloudtype.app",
    ".sel4.cloudtype.app",
]

# Add internal IP for health checks in cloud environments
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip for ip in ips if not ip.startswith('127.')]
    ALLOWED_HOSTS.extend(INTERNAL_IPS)
except socket.gaierror:
    # Handle the case where hostname might not be resolvable
    pass

# 환경변수에서 추가 호스트 설정
additional_hosts = get_env_variable("ALLOWED_HOSTS", "").split(",")
if additional_hosts and additional_hosts[0]:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts if host.strip()])

# =============================================================================
# SECURITY SETTINGS (운영용)
# =============================================================================

# HTTPS 설정 (CloudType에서는 비활성화)
SECURE_SSL_REDIRECT = False  # CloudType에서는 자동으로 HTTPS 처리됨
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # (신규 Django에선 의미 거의 없음)
X_FRAME_OPTIONS = "DENY"

# CSRF 설정 (Django 4.1+에서 와일드카드 지원)
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    "https://*.cloudtype.app",
    "https://*.sel4.cloudtype.app",
]

# Session 설정
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24시간

# =============================================================================
# CORS SETTINGS (운영용)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
# 와일드카드는 CORS_ALLOWED_ORIGINS에서 동작하지 않으므로 정규식으로 처리
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://[a-z0-9.-]+\.cloudtype\.app$",
    r"^https://[a-z0-9.-]+\.sel4\.cloudtype\.app$",
]

# 환경변수에서 추가 프론트엔드 호스트 설정
frontend_hosts = get_env_variable("FRONTEND_HOSTS", "").split(",")
if frontend_hosts and frontend_hosts[0]:
    # 명시적 호스트는 정확 문자열로 추가
    CORS_ALLOWED_ORIGINS.extend(
        [f"https://{host.strip()}" for host in frontend_hosts if host.strip()]
    )

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# DATABASE SETTINGS (운영용)
# =============================================================================

# MongoDB와 Elasticsearch만 사용하므로 SQLite로 간단히 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# STATIC FILES (운영용)
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# 디렉터리 보장 (경고/오류 방지)
Path(STATIC_ROOT).mkdir(parents=True, exist_ok=True)

# WhiteNoise 설정 (정적 파일 서빙)
# - Manifest 기반(권장). 반드시 collectstatic을 릴리즈 단계에서 실행하세요.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# 만약 manifest 누락 시 ValueError로 죽지 않게 임시 안전망 (장기적으론 collectstatic 필수)
WHITENOISE_MANIFEST_STRICT = False

# WhiteNoise 미들웨어를 SecurityMiddleware 바로 뒤에 안전하게 배치
_mw = list(MIDDLEWARE)
if "whitenoise.middleware.WhiteNoiseMiddleware" not in _mw:
    try:
        sec_idx = _mw.index("django.middleware.security.SecurityMiddleware")
    except ValueError:
        # base에서 빠졌다면 최상단에 Security/WhiteNoise를 보강
        _mw.insert(0, "django.middleware.security.SecurityMiddleware")
        _mw.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    else:
        _mw.insert(sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")
MIDDLEWARE = tuple(_mw)

# =============================================================================
# LOGGING CONFIGURATION (운영용)
# =============================================================================

# 로그 디렉터리 보장
LOG_DIR = Path(BASE_DIR) / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Elasticsearch 운영 환경 설정
ELASTICSEARCH_HOST = get_env_variable("ELASTICSEARCH_HOST", "localhost:9200")
ELASTICSEARCH_USERNAME = get_env_variable("ELASTICSEARCH_USERNAME", "elastic")
ELASTICSEARCH_PASSWORD = get_env_variable("ELASTICSEARCH_PASSWORD", "")

# 운영 환경 Elasticsearch 설정
# (현재 연결 정상 동작 중이므로 기존 http_auth 유지)
es_config = {
    "hosts": [f"https://{ELASTICSEARCH_HOST}"],
    "timeout": 30,
    "verify_certs": True,  # 운영환경에서는 SSL 인증서 검증 활성화
    "http_auth": (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
}

ELASTICSEARCH_DSL = {
    "default": es_config,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "production.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "search": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "elasticsearch": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# =============================================================================
# EMAIL BACKEND (운영용)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# CACHE SETTINGS (운영용)
# =============================================================================

# Redis가 있으면 Redis 사용, 없으면 로컬 메모리 캐시 사용
if get_env_variable("REDIS_URL", None):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": get_env_variable("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 20,
                    "retry_on_timeout": True,
                },
            },
            "KEY_PREFIX": "vans_search",
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
