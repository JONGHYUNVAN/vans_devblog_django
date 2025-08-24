"""
VansDevBlog Search Service Testing Settings

테스트 환경에서 사용되는 Django 설정입니다.
"""

from .base import get_env_variable

# =============================================================================
# TEST SETTINGS
# =============================================================================

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# 테스트용 최소한의 앱만 사용
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "search",
]

# 테스트용 간단한 URL 설정 (admin 제외)
ROOT_URLCONF = "tests.test_urls"

# =============================================================================
# DATABASE SETTINGS (테스트용)
# =============================================================================

# 메모리 내 SQLite 사용으로 빠른 테스트
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    # 테스트에서는 search_logs도 SQLite 사용
    "search_logs": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# =============================================================================
# PASSWORD VALIDATION (테스트용)
# =============================================================================

# 테스트에서는 비밀번호 검증 비활성화
AUTH_PASSWORD_VALIDATORS = []

# =============================================================================
# CACHE SETTINGS (테스트용)
# =============================================================================

# 테스트에서는 더미 캐시 사용
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# =============================================================================
# EMAIL BACKEND (테스트용)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# =============================================================================
# LOGGING CONFIGURATION (테스트용)
# =============================================================================

# 테스트 중에는 로깅 최소화
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "CRITICAL",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "CRITICAL",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "search": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}

# =============================================================================
# ELASTICSEARCH SETTINGS (테스트용)
# =============================================================================

# 테스트용 Elasticsearch 설정 (별도 인덱스 사용)
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": [
            f"http://{get_env_variable('TEST_ELASTICSEARCH_HOST', 'localhost:9200')}"
        ],
        "timeout": 10,
        "max_retries": 1,
        "retry_on_timeout": False,
    },
}

# =============================================================================
# MONGODB SETTINGS (테스트용)
# =============================================================================

# 테스트용 MongoDB 설정
MONGODB_SETTINGS = {
    "host": get_env_variable("TEST_MONGODB_HOST", "localhost"),
    "port": int(get_env_variable("TEST_MONGODB_PORT", "27017")),
    "database": get_env_variable("TEST_MONGODB_DATABASE", "test_devblog"),
    "username": get_env_variable("TEST_MONGODB_USERNAME", ""),
    "password": get_env_variable("TEST_MONGODB_PASSWORD", ""),
    "auth_source": get_env_variable("TEST_MONGODB_AUTH_SOURCE", "admin"),
    "direct_connection": True,
}

# =============================================================================
# TEST RUNNER SETTINGS
# =============================================================================

# 테스트 속도 향상을 위한 설정
TEST_RUNNER = "django.test.runner.DiscoverRunner"


# 테스트 중 마이그레이션 건너뛰기 (선택사항)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# MIGRATION_MODULES = DisableMigrations()

# =============================================================================
# CORS SETTINGS (테스트용)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True
