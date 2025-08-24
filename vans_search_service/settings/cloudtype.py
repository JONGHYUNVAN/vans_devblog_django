"""
VansDevBlog Search Service CloudType.io Settings

CloudType.io 플랫폼에 최적화된 Django 설정입니다.
"""

from .base import *
import os

# =============================================================================
# CLOUDTYPE.IO SPECIFIC SETTINGS
# =============================================================================

DEBUG = False

# CloudType.io 도메인 허용
ALLOWED_HOSTS = [
    '*.cloudtype.app',
    'localhost',
    '127.0.0.1',
] + get_env_variable('ALLOWED_HOSTS', '').split(',') if get_env_variable('ALLOWED_HOSTS') else []

# CSRF 설정 (CloudType.io 도메인 포함)
CSRF_TRUSTED_ORIGINS = [
    'https://*.cloudtype.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://*.cloudtype.app',
]
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# DATABASE SETTINGS (CloudType.io)
# =============================================================================

# CloudType.io에서 제공하는 PostgreSQL 사용
if get_env_variable('DATABASE_URL', None):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(get_env_variable('DATABASE_URL'))
else:
    # 기본값으로 SQLite 사용 (개발/테스트용)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# STATIC FILES (CloudType.io)
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise 설정 (정적 파일 서빙)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise 미들웨어 추가
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# =============================================================================
# CACHE SETTINGS (CloudType.io)
# =============================================================================

# Redis가 있으면 Redis 사용, 없으면 로컬 메모리 캐시 사용
if get_env_variable('REDIS_URL', None):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': get_env_variable('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# =============================================================================
# LOGGING CONFIGURATION (CloudType.io)
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'search': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# ELASTICSEARCH SETTINGS (CloudType.io)
# =============================================================================

# CloudType.io에서 Elasticsearch 서비스 사용하는 경우
ELASTICSEARCH_HOST = get_env_variable('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = get_env_variable('ELASTICSEARCH_PORT', '9200')
ELASTICSEARCH_USERNAME = get_env_variable('ELASTICSEARCH_USERNAME', '')
ELASTICSEARCH_PASSWORD = get_env_variable('ELASTICSEARCH_PASSWORD', '')

# Elasticsearch DSL 설정
es_config = {
    'hosts': [f'{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}'],
    'timeout': 20,
}

# 인증이 필요한 경우
if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
    es_config['http_auth'] = (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)

ELASTICSEARCH_DSL = {
    'default': es_config,
}

# =============================================================================
# MONGODB SETTINGS (CloudType.io)
# =============================================================================

MONGODB_HOST = get_env_variable('MONGODB_HOST', 'localhost')
MONGODB_PORT = int(get_env_variable('MONGODB_PORT', '27017'))
MONGODB_DB = get_env_variable('MONGODB_DB', 'vans_search')
MONGODB_USERNAME = get_env_variable('MONGODB_USERNAME', '')
MONGODB_PASSWORD = get_env_variable('MONGODB_PASSWORD', '')

# =============================================================================
# SECURITY SETTINGS (CloudType.io)
# =============================================================================

# HTTPS 설정 (CloudType.io는 자동으로 HTTPS 제공)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # CloudType.io에서 자동 처리
USE_TLS = True

# Session 보안
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24시간

# CSRF 보안
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

# 파일 업로드 크기 제한
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 연결 풀 설정
CONN_MAX_AGE = 60
