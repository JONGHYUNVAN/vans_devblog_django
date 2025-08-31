"""
VansDevBlog Search Service Development Settings

개발 환경에서 사용되는 Django 설정입니다.
"""

import logging.config

import socket
from .base import *  # 모든 기본 설정 import

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

DEBUG = True

ALLOWED_HOSTS = [
    "*.cloudtype.app",
    "*.sel4.cloudtype.app",
]

# Add internal IP for health checks in cloud environments
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip for ip in ips if not ip.startswith('127.')]
    ALLOWED_HOSTS.extend(INTERNAL_IPS)
except socket.gaierror:
    # Handle the case where hostname might not be resolvable
    pass

# For development, allow localhost and 127.0.0.1 if DEBUG is True
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '[::1]', '0.0.0.0'])

# =============================================================================
# CORS SETTINGS (개발용)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True  # Development only
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js frontend
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vue.js frontend
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================

# Django Debug Toolbar (개발 시 추가 가능)
INTERNAL_IPS = [
    "127.0.0.1",
]

# =============================================================================
# LOGGING CONFIGURATION (개발용)
# =============================================================================

# Elasticsearch 개발 환경 설정 (CloudType 전용)
ELASTICSEARCH_HOST = get_env_variable("ELASTICSEARCH_HOST", "web-elasticsearch-m7fb3ua7b5f728d5.sel4.cloudtype.app:9200")
ELASTICSEARCH_USERNAME = get_env_variable("ELASTICSEARCH_USERNAME", "elastic")
ELASTICSEARCH_PASSWORD = get_env_variable("ELASTICSEARCH_PASSWORD", "VANSDEVBLOG")

# CloudType Elasticsearch 전용 설정
es_config = {
    "hosts": [f"https://{ELASTICSEARCH_HOST}"],
    "timeout": 30,
    "verify_certs": False,  # 개발환경에서는 SSL 인증서 검증 비활성화
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
        "colored": {
            "format": "\033[92m[{asctime}]\033[0m \033[94m{name}\033[0m - \033[{color}m{levelname}\033[0m - {message}",
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
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "development.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends.schema": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.utils.autoreload": {
            "handlers": [],
            "level": "WARNING",
            "propagate": False,
        },
        "search": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "elasticsearch": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "elastic_transport": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "search.clients": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# =============================================================================
# EMAIL BACKEND (개발용)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# CACHE SETTINGS (개발용)
# =============================================================================

# 개발 환경에서는 캐시 비활성화 (항상 최신 데이터)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# 또는 매우 짧은 캐시 타임아웃
# SEARCH_CACHE_TIMEOUT = 30  # 30초
# AUTOCOMPLETE_CACHE_TIMEOUT = 60  # 1분
# POPULAR_SEARCHES_CACHE_TIMEOUT = 300  # 5분
