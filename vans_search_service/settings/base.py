"""
VansDevBlog Search Service Base Settings

모든 환경에서 공통으로 사용되는 Django 기본 설정입니다.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from . import get_env_variable

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'django_elasticsearch_dsl',
]

LOCAL_APPS = [
    'search',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vans_search_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vans_search_service.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # MariaDB connection for search logs (기존 User Service DB)
    'search_logs': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_env_variable('MARIADB_DATABASE', 'vans_user_db'),
        'USER': get_env_variable('MARIADB_USER', 'vans_user'),
        'PASSWORD': get_env_variable('MARIADB_PASSWORD', 'password'),
        'HOST': get_env_variable('MARIADB_HOST', 'localhost'),
        'PORT': get_env_variable('MARIADB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# =============================================================================
# DEFAULT FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# REST FRAMEWORK SETTINGS
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# =============================================================================
# SWAGGER SETTINGS
# =============================================================================

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get', 'post', 'put', 'delete', 'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
}

# =============================================================================
# ELASTICSEARCH SETTINGS
# =============================================================================

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': [f"http://{get_env_variable('ELASTICSEARCH_HOST', 'localhost:9200')}"],
        'timeout': 20,
        'max_retries': 3,
        'retry_on_timeout': True,
    },
}

# =============================================================================
# MONGODB SETTINGS
# =============================================================================

MONGODB_SETTINGS = {
    'host': get_env_variable('MONGODB_HOST', 'localhost'),
    'port': int(get_env_variable('MONGODB_PORT', '27017')),
    'database': get_env_variable('MONGODB_DATABASE', 'devblog'),
    'username': get_env_variable('MONGODB_USERNAME', ''),
    'password': get_env_variable('MONGODB_PASSWORD', ''),
    'auth_source': get_env_variable('MONGODB_AUTH_SOURCE', 'admin'),
    'direct_connection': get_env_variable('MONGODB_DIRECT_CONNECTION', 'true').lower() == 'true'
}

# =============================================================================
# CACHING SETTINGS
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'search-cache',
        'TIMEOUT': 300,  # 5분
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Search cache timeouts
SEARCH_CACHE_TIMEOUT = 300  # 5분
AUTOCOMPLETE_CACHE_TIMEOUT = 600  # 10분
POPULAR_SEARCHES_CACHE_TIMEOUT = 3600  # 1시간

