"""
VansDevBlog Search Service CloudType.io Settings

CloudType.io 플랫폼에 최적화된 Django 설정입니다.
"""

import os
import socket

from .base import (
    BASE_DIR,
    get_env_variable,
    MIDDLEWARE,
    DATABASES,
)

# =============================================================================
# CLOUDTYPE.IO SPECIFIC SETTINGS
# =============================================================================

DEBUG = False

allowed_hosts_env = get_env_variable("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    "*.cloudtype.app",
]

# 환경변수에서 추가 호스트 설정
if allowed_hosts_env:
    additional_hosts = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
    ALLOWED_HOSTS.extend(additional_hosts)

# Add internal IP for health checks in cloud environments
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    print(f"DEBUG: Hostname: {hostname}")
    print(f"DEBUG: IPs from gethostbyname_ex: {ips}")
    INTERNAL_IPS = [ip for ip in ips if not ip.startswith('127.')]
    print(f"DEBUG: INTERNAL_IPS: {INTERNAL_IPS}")
    ALLOWED_HOSTS.extend(INTERNAL_IPS)
except socket.gaierror:
    # Handle the case where hostname might not be resolvable
    print("DEBUG: socket.gaierror occurred during hostname resolution.")
    pass

# For development, allow localhost and 127.0.0.1 if DEBUG is True
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '[::1]'])

print(f"DEBUG: Final ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# CSRF 설정 (CloudType.io 도메인 포함)
CSRF_TRUSTED_ORIGINS = [
    "https://*.cloudtype.app",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://*.cloudtype.app",
    "http://localhost:3000",  # React 개발 서버
    "http://localhost:8080",  # Vue 개발 서버
]

# 환경변수에서 추가 CORS 도메인 설정
cors_origins_env = get_env_variable("CORS_ALLOWED_ORIGINS", "")
if cors_origins_env:
    additional_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    CORS_ALLOWED_ORIGINS.extend(additional_origins)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =============================================================================
# DATABASE SETTINGS (CloudType.io)
# =============================================================================

# CloudType.io에서 제공하는 PostgreSQL 사용
if get_env_variable("DATABASE_URL", None):
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(get_env_variable("DATABASE_URL"))
else:
    # 기본값으로 SQLite 사용 (개발/테스트용)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =============================================================================
# STATIC FILES (CloudType.io)
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# WhiteNoise 설정 (정적 파일 서빙)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# WhiteNoise 미들웨어 추가
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# =============================================================================
# CACHE SETTINGS (CloudType.io)
# =============================================================================

# Redis가 있으면 Redis 사용, 없으면 로컬 메모리 캐시 사용
if get_env_variable("REDIS_URL", None):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": get_env_variable("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

# =============================================================================
# LOGGING CONFIGURATION (CloudType.io)
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "search": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# =============================================================================
# ELASTICSEARCH SETTINGS (CloudType.io)
# =============================================================================

# CloudType.io에서 Elasticsearch 서비스 사용하는 경우
ELASTICSEARCH_HOST = get_env_variable("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = get_env_variable("ELASTICSEARCH_PORT", "9200")
ELASTICSEARCH_USERNAME = get_env_variable("ELASTICSEARCH_USERNAME", "")
ELASTICSEARCH_PASSWORD = get_env_variable("ELASTICSEARCH_PASSWORD", "")

# Elasticsearch DSL 설정 (Nori 플러그인 포함)
es_config = {
    "hosts": [f"{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"],
    "timeout": 20,
    "verify_certs": False,  # CloudType.io SSL 설정에 따라 조정
    "ssl_show_warn": False,
}

# 인증이 필요한 경우
if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
    es_config["http_auth"] = (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)

ELASTICSEARCH_DSL = {
    "default": es_config,
}

# 한국어 검색을 위한 Nori 분석기 설정
ELASTICSEARCH_INDEX_SETTINGS = {
    "analysis": {
        "analyzer": {
            "korean_analyzer": {
                "type": "custom",
                "tokenizer": "nori_tokenizer",
                "decompound_mode": "mixed",
                "filter": [
                    "lowercase",
                    "nori_part_of_speech",
                    "nori_readingform",
                    "cjk_width"
                ]
            },
            "korean_search_analyzer": {
                "type": "custom", 
                "tokenizer": "nori_tokenizer",
                "decompound_mode": "none",
                "filter": [
                    "lowercase",
                    "nori_part_of_speech", 
                    "nori_readingform",
                    "cjk_width"
                ]
            }
        },
        "tokenizer": {
            "nori_tokenizer": {
                "type": "nori_tokenizer",
                "decompound_mode": "mixed",
                "discard_punctuation": True,
                "user_dictionary_rules": [
                    "Django => Django",
                    "ElasticSearch => ElasticSearch", 
                    "CloudType => CloudType"
                ]
            }
        },
        "filter": {
            "nori_part_of_speech": {
                "type": "nori_part_of_speech",
                "stoptags": [
                    "E", "IC", "J", "MAG", "MAJ", "MM", "SP", 
                    "SSC", "SSO", "SC", "SE", "XPN", "XSA", 
                    "XSN", "XSV", "UNA", "NA", "VSV"
                ]
            }
        }
    }
}

# =============================================================================
# MONGODB SETTINGS (CloudType.io)
# =============================================================================

MONGODB_HOST = get_env_variable("MONGODB_HOST", "localhost")
MONGODB_PORT = int(get_env_variable("MONGODB_PORT", "27017"))
MONGODB_DB = get_env_variable("MONGODB_DB", "vans_search")
MONGODB_USERNAME = get_env_variable("MONGODB_USERNAME", "")
MONGODB_PASSWORD = get_env_variable("MONGODB_PASSWORD", "")

# =============================================================================
# SECURITY SETTINGS (CloudType.io)
# =============================================================================

# HTTPS 설정 (CloudType.io는 자동으로 HTTPS 제공)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # CloudType.io에서 자동 처리
USE_TLS = True

# 보안 헤더 설정
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session 보안
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24시간
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF 보안
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

# 파일 업로드 크기 제한
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 연결 풀 설정
CONN_MAX_AGE = 60
