"""
VansDevBlog Search Service Development Settings

개발 환경에서 사용되는 Django 설정입니다.
"""

from .base import *
import logging.config

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

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
    '127.0.0.1',
]

# =============================================================================
# LOGGING CONFIGURATION (개발용)
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'colored': {
            'format': '\033[92m[{asctime}]\033[0m \033[94m{name}\033[0m - \033[{color}m{levelname}\033[0m - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'search': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'elasticsearch': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =============================================================================
# EMAIL BACKEND (개발용)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# CACHE SETTINGS (개발용)
# =============================================================================

# 개발 환경에서는 캐시 비활성화 (항상 최신 데이터)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 또는 매우 짧은 캐시 타임아웃
# SEARCH_CACHE_TIMEOUT = 30  # 30초
# AUTOCOMPLETE_CACHE_TIMEOUT = 60  # 1분
# POPULAR_SEARCHES_CACHE_TIMEOUT = 300  # 5분

