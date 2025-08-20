"""
Integration Test Suite

전체 시스템의 통합 테스트를 수행합니다.
"""

import pytest
from django.test import TransactionTestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from unittest.mock import patch, Mock


@pytest.mark.integration
class TestSearchWorkflow(TransactionTestCase):
    """검색 워크플로우 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.client = APIClient()
        
    @patch('search.clients.elasticsearch_client.ElasticsearchClient')
    @patch('search.clients.mongodb_client.MongoDBClient')
    def test_complete_search_workflow(self, mock_mongodb, mock_elasticsearch):
        """완전한 검색 워크플로우 테스트"""
        # 모킹 설정
        mock_es_instance = Mock()
        mock_elasticsearch.return_value = mock_es_instance
        mock_es_instance.search_posts.return_value = {
            'total': 1,
            'results': [{'post_id': '123', 'score': 1.5}],
            'aggregations': {
                'categories': {'buckets': []},
                'tags': {'buckets': []},
                'languages': {'buckets': []}
            }
        }
        
        mock_mongo_instance = Mock()
        mock_mongodb.return_value = mock_mongo_instance
        mock_mongo_instance.get_categories.return_value = ['Frontend', 'Backend']
        
        # 1. 헬스체크
        response = self.client.get('/api/v1/search/health/')
        assert response.status_code == 200
        
        # 2. 카테고리 조회
        response = self.client.get('/api/v1/search/categories/')
        assert response.status_code == 200
        
        # 3. 검색 실행
        response = self.client.get('/api/v1/search/posts/', {'query': 'Django'})
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 1
        
        # 4. 인기 검색어 확인 (검색 후)
        response = self.client.get('/api/v1/search/popular/')
        assert response.status_code == 200
        
    @patch('search.clients.elasticsearch_client.ElasticsearchClient')
    @patch('search.clients.mongodb_client.MongoDBClient') 
    def test_search_logging_integration(self, mock_mongodb, mock_elasticsearch):
        """검색 로그 통합 테스트"""
        # 모킹 설정
        mock_es_instance = Mock()
        mock_elasticsearch.return_value = mock_es_instance
        mock_es_instance.search_posts.return_value = {
            'total': 2,
            'results': [],
            'aggregations': {'categories': {'buckets': []}, 'tags': {'buckets': []}, 'languages': {'buckets': []}}
        }
        
        mock_mongo_instance = Mock()
        mock_mongodb.return_value = mock_mongo_instance
        
        from search.models import SearchLog, PopularSearch
        
        # 초기 상태 확인
        initial_log_count = SearchLog.objects.count()
        initial_popular_count = PopularSearch.objects.count()
        
        # 검색 실행
        response = self.client.get('/api/v1/search/posts/', {'query': 'Integration Test'})
        assert response.status_code == 200
        
        # 로그 확인
        assert SearchLog.objects.count() == initial_log_count + 1
        latest_log = SearchLog.objects.latest('search_time')
        assert latest_log.query == 'Integration Test'
        assert latest_log.results_count == 2
        
        # 인기 검색어 확인
        assert PopularSearch.objects.count() >= initial_popular_count
        
    def test_error_handling_integration(self):
        """에러 처리 통합 테스트"""
        # 잘못된 파라미터로 검색
        response = self.client.get('/api/v1/search/posts/', {'page_size': 'invalid'})
        assert response.status_code == 400
        
        # 존재하지 않는 엔드포인트
        response = self.client.get('/api/v1/search/nonexistent/')
        assert response.status_code == 404


@pytest.mark.integration
class TestCacheIntegration:
    """캐시 통합 테스트"""
    
    @patch('search.clients.elasticsearch_client.ElasticsearchClient')
    @patch('search.clients.mongodb_client.MongoDBClient')
    def test_cache_behavior(self, mock_mongodb, mock_elasticsearch, clean_cache):
        """캐시 동작 통합 테스트"""
        from search.services.search_service import SearchService
        
        # 모킹 설정
        mock_es_instance = Mock()
        mock_elasticsearch.return_value = mock_es_instance
        mock_es_instance.search_posts.return_value = {
            'total': 1,
            'results': [],
            'aggregations': {'categories': {'buckets': []}, 'tags': {'buckets': []}, 'languages': {'buckets': []}}
        }
        
        mock_mongo_instance = Mock()
        mock_mongodb.return_value = mock_mongo_instance
        
        service = SearchService()
        
        # 첫 번째 호출 - 캐시 미스
        result1 = service.search_posts({
            'query': 'cache test',
            'page': 1,
            'page_size': 20
        })
        
        # 두 번째 호출 - 캐시 히트 (같은 파라미터)
        result2 = service.search_posts({
            'query': 'cache test',
            'page': 1,
            'page_size': 20
        })
        
        # 결과가 동일해야 함
        assert result1 == result2
        
        # Elasticsearch는 한 번만 호출되어야 함 (캐시 때문에)
        assert mock_es_instance.search_posts.call_count == 1


@pytest.mark.integration
class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""
    
    @pytest.mark.django_db
    def test_model_integration(self):
        """모델 통합 테스트"""
        from search.models import SearchLog, PopularSearch
        
        # 검색 로그 생성
        log = SearchLog.record_log(
            query="Model Integration Test",
            results_count=5
        )
        
        assert log.id is not None
        assert log.query == "Model Integration Test"
        
        # 인기 검색어 생성/업데이트
        popular1 = PopularSearch.update_popular_search("Model Integration Test")
        assert popular1.search_count == 1
        
        popular2 = PopularSearch.update_popular_search("Model Integration Test")
        assert popular2.search_count == 2
        assert popular1.id == popular2.id  # 같은 객체
        
        # 상위 인기 검색어 조회
        top_searches = PopularSearch.get_top_popular_searches(limit=5)
        assert len(top_searches) >= 1
        assert any(search['query'] == "Model Integration Test" for search in top_searches)
