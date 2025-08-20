"""
Services Test Suite

비즈니스 로직 서비스 레이어를 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from search.services.search_service import SearchService
from search.services.health_service import HealthService
from search.services.cache_service import CacheService


class TestSearchService:
    """SearchService 테스트"""
    
    def test_search_service_initialization(self, mock_elasticsearch, mock_mongodb):
        """SearchService 초기화 테스트"""
        service = SearchService()
        
        assert service.es_client is not None
        assert service.cache_service is not None
        
    @patch('search.services.search_service.SearchLog.record_log')
    @patch('search.services.search_service.PopularSearch.update_popular_search')
    def test_search_posts_with_logging(self, mock_popular_update, mock_log_record, 
                                     mock_elasticsearch, mock_mongodb, clean_cache):
        """검색 로그 기록을 포함한 게시물 검색 테스트"""
        # 모킹 설정
        mock_elasticsearch.search_posts.return_value = {
            'total': 2,
            'results': [
                {'post_id': '123', 'score': 1.5},
                {'post_id': '456', 'score': 1.2}
            ],
            'aggregations': {
                'categories': {'buckets': [{'key': 'Backend', 'doc_count': 2}]},
                'tags': {'buckets': []},
                'languages': {'buckets': []}
            }
        }
        
        service = SearchService()
        result = service.search_posts({
            'query': 'Django Test',
            'page': 1,
            'page_size': 20
        })
        
        # 결과 검증
        assert result['total'] == 2
        assert len(result['results']) == 2
        assert result['page'] == 1
        
        # 로그 기록 검증
        mock_log_record.assert_called_once_with(
            query='Django Test',
            results_count=2
        )
        mock_popular_update.assert_called_once_with('Django Test')
        
    def test_search_posts_empty_query(self, mock_elasticsearch, mock_mongodb):
        """빈 검색어 처리 테스트"""
        mock_elasticsearch.search_posts.return_value = {
            'total': 0,
            'results': [],
            'aggregations': {'categories': {'buckets': []}, 'tags': {'buckets': []}, 'languages': {'buckets': []}}
        }
        
        service = SearchService()
        result = service.search_posts({
            'query': '',
            'page': 1,
            'page_size': 20
        })
        
        assert result['total'] == 0
        assert result['results'] == []
        
    @patch('search.models.PopularSearch.get_top_popular_searches')
    def test_get_popular_searches_from_db(self, mock_get_popular, mock_elasticsearch, 
                                        mock_mongodb, clean_cache):
        """DB에서 인기 검색어 조회 테스트"""
        mock_get_popular.return_value = [
            {'query': 'Django', 'count': 10},
            {'query': 'Python', 'count': 8}
        ]
        
        service = SearchService()
        result = service.get_popular_searches()
        
        assert 'popular_searches' in result
        assert len(result['popular_searches']) == 2
        assert result['popular_searches'][0]['query'] == 'Django'
        
    def test_get_popular_searches_empty_db(self, mock_elasticsearch, mock_mongodb, clean_cache):
        """DB가 비어있을 때 인기 검색어 조회 테스트"""
        with patch('search.models.PopularSearch.get_top_popular_searches', return_value=[]):
            service = SearchService()
            result = service.get_popular_searches()
            
            assert result['popular_searches'] == []
            
    def test_get_categories_from_mongodb(self, mock_elasticsearch, mock_mongodb, clean_cache):
        """MongoDB에서 카테고리 조회 테스트"""
        mock_mongodb.get_categories.return_value = ['Frontend', 'Backend', 'Database']
        
        service = SearchService()
        result = service.get_categories()
        
        assert 'categories' in result
        assert len(result['categories']) == 3
        assert 'Frontend' in result['categories']


class TestHealthService:
    """HealthService 테스트"""
    
    def test_health_check_all_healthy(self, mock_elasticsearch, mock_mongodb):
        """모든 서비스가 정상일 때 헬스체크 테스트"""
        mock_elasticsearch.health_check.return_value = {'status': 'healthy'}
        mock_mongodb.health_check.return_value = {'status': 'healthy'}
        
        service = HealthService()
        result = service.check_health()
        
        assert result['status'] == 'healthy'
        assert 'elasticsearch' in result['services']
        assert 'mongodb' in result['services']
        assert result['services']['elasticsearch']['status'] == 'healthy'
        
    def test_health_check_elasticsearch_unhealthy(self, mock_elasticsearch, mock_mongodb):
        """Elasticsearch가 비정상일 때 헬스체크 테스트"""
        mock_elasticsearch.health_check.side_effect = Exception("Connection failed")
        mock_mongodb.health_check.return_value = {'status': 'healthy'}
        
        service = HealthService()
        result = service.check_health()
        
        assert result['status'] == 'degraded'
        assert result['services']['elasticsearch']['status'] == 'unhealthy'


class TestCacheService:
    """CacheService 테스트"""
    
    def test_cache_search_result(self, clean_cache):
        """검색 결과 캐싱 테스트"""
        cache_service = CacheService()
        
        # 캐시 저장
        test_data = {'total': 5, 'results': []}
        cache_service.set_search_result('test query', {}, 1, 20, test_data)
        
        # 캐시 조회
        cached_data = cache_service.get_search_result('test query', {}, 1, 20)
        
        assert cached_data is not None
        assert cached_data['total'] == 5
        
    def test_cache_popular_searches(self, clean_cache):
        """인기 검색어 캐싱 테스트"""
        cache_service = CacheService()
        
        # 캐시 저장
        popular_data = [{'query': 'Django', 'count': 10}]
        cache_service.set_popular_searches(popular_data)
        
        # 캐시 조회
        cached_data = cache_service.get_popular_searches()
        
        assert cached_data is not None
        assert len(cached_data) == 1
        assert cached_data[0]['query'] == 'Django'
        
    def test_cache_categories(self, clean_cache):
        """카테고리 캐싱 테스트"""
        cache_service = CacheService()
        
        # 캐시 저장
        categories = ['Frontend', 'Backend']
        cache_service.set_categories(categories)
        
        # 캐시 조회
        cached_data = cache_service.get_categories()
        
        assert cached_data is not None
        assert len(cached_data) == 2
        assert 'Frontend' in cached_data
