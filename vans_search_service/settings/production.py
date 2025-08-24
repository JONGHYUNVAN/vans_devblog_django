"""
VansDevBlog Search Service Production Settings

운영 환경에서 사용되는 Django 설정입니다.
"""

import logging

from .base import (
    BASE_DIR,
    get_env_variable,
    DATABASES,
)

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

DEBUG = False

ALLOWED_HOSTS = get_env_variable("ALLOWED_HOSTS", "localhost").split(",")

# HTTPS 설정
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# CSRF 설정
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}"
    for host in get_env_variable("ALLOWED_HOSTS", "localhost").split(",")
]

# Session 설정
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24시간

# =============================================================================
# CORS SETTINGS (운영용)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    f"https://{host}"
    for host in get_env_variable("FRONTEND_HOSTS", "localhost").split(",")
]

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# DATABASE SETTINGS (운영용)
# =============================================================================

# SQLite 대신 PostgreSQL 사용 권장
if get_env_variable("DATABASE_URL", None):
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(get_env_variable("DATABASE_URL"))

# =============================================================================
# STATIC FILES (운영용)
# =============================================================================

# AWS S3 또는 CDN 사용 권장
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)

# =============================================================================
# LOGGING CONFIGURATION (운영용)
# =============================================================================

LOGS_DIR = BASE_DIR / "logs"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "format": (
                '{"level": "{levelname}", "time": "{asctime}", '
                '"module": "{module}", "message": "{message}"}'
            ),
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "production.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "search": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "elasticsearch": {
            "handlers": ["file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# =============================================================================
# CACHE SETTINGS (운영용)
# =============================================================================

# Redis 캐시 사용 권장 (운영 환경)
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

# =============================================================================
# EMAIL SETTINGS (운영용)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_env_variable("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(get_env_variable("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = get_env_variable(
    "DEFAULT_FROM_EMAIL", "noreply@vansdevblog.online"
)

# =============================================================================
# SENTRY 에러 모니터링 (선택사항)
# =============================================================================

if get_env_variable("SENTRY_DSN", None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    sentry_sdk.init(
        dsn=get_env_variable("SENTRY_DSN"),
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )
