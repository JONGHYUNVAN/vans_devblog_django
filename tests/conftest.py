"""
Pytest Configuration and Fixtures

전역 테스트 설정과 공통 픽스처를 정의합니다.
"""

import pytest
import os
import django
from django.conf import settings
from django.test import override_settings
from django.core.management import call_command
from rest_framework.test import APIClient
from unittest.mock import Mock, patch


def pytest_configure():
    """Pytest 설정 초기화"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings.testing')
    django.setup()


@pytest.fixture
def api_client():
    """DRF API 클라이언트 픽스처"""
    return APIClient()


@pytest.fixture
def mock_elasticsearch():
    """Elasticsearch 클라이언트 모킹"""
    with patch('search.clients.elasticsearch_client.ElasticsearchClient') as mock_es:
        mock_instance = Mock()
        mock_instance.search_posts.return_value = {
            'total': 0,
            'results': [],
            'aggregations': {
                'categories': {'buckets': []},
                'tags': {'buckets': []},
                'languages': {'buckets': []}
            }
        }
        mock_instance.autocomplete.return_value = {'suggestions': []}
        mock_instance.health_check.return_value = {'status': 'healthy'}
        mock_es.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mongodb():
    """MongoDB 클라이언트 모킹"""
    with patch('search.clients.mongodb_client.MongoDBClient') as mock_mongo:
        mock_instance = Mock()
        mock_instance.get_categories.return_value = ['Frontend', 'Backend', 'Database']
        mock_instance.health_check.return_value = {'status': 'healthy'}
        mock_mongo.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def clean_cache():
    """캐시 초기화 픽스처"""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
@pytest.mark.django_db
def sample_search_log():
    """샘플 검색 로그 데이터"""
    from search.models import SearchLog
    return SearchLog.objects.create(
        query="Django Test",
        results_count=5,
        response_time_ms=150
    )


@pytest.fixture
@pytest.mark.django_db
def sample_popular_search():
    """샘플 인기 검색어 데이터"""
    from search.models import PopularSearch
    return PopularSearch.objects.create(
        query="Python Testing",
        search_count=10
    )


@pytest.fixture
def override_cache_settings():
    """테스트용 캐시 설정 오버라이드"""
    with override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
    ):
        yield
