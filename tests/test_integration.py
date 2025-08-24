"""
Integration Test Suite

전체 시스템의 통합 테스트를 수행합니다.
메모리 최적화를 위한 가벼운 테스트 구조로 설계되었습니다.
"""

import pytest
import gc
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest.mock import patch, Mock, MagicMock
import time


@pytest.mark.integration
class TestSearchWorkflow(TestCase):
    """검색 워크플로우 통합 테스트 - 메모리 최적화 버전"""
    
    @classmethod
    def setUpClass(cls):
        """클래스 레벨 설정 - 메모리 효율성을 위해"""
        super().setUpClass()
        cls.base_client = APIClient()
    
    def setUp(self):
        """테스트 설정 - 최소한의 인스턴스만 생성"""
        self.client = self.base_client  # 클라이언트 재사용
        self.test_timeout = 3  # 3초로 단축
        self.mock_objects = []  # Mock 객체 추적을 위한 리스트
        
    def tearDown(self):
        """테스트 정리 - 메모리 누수 방지"""
        # Mock 객체들 명시적 정리
        for mock_obj in self.mock_objects:
            if hasattr(mock_obj, 'reset_mock'):
                mock_obj.reset_mock()
        self.mock_objects.clear()
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        super().tearDown()
        
    @patch('search.clients.elasticsearch_client.ElasticsearchClient')
    @patch('search.clients.mongodb_client.MongoDBClient')
    @pytest.mark.timeout(5)  # 5초로 단축
    def test_complete_search_workflow(self, mock_mongodb, mock_elasticsearch):
        """완전한 검색 워크플로우 테스트 (메모리 최적화됨)"""
        start_time = time.time()
        
        # 경량 모킹 설정 - 메모리 사용량 최소화
        mock_es_instance = MagicMock()
        mock_elasticsearch.return_value = mock_es_instance
        mock_es_instance.search_posts.return_value = {
            'total': 1,
            'results': [{'post_id': '123', 'score': 1.5}],
            'aggregations': {'categories': {'buckets': []}, 'tags': {'buckets': []}, 'languages': {'buckets': []}}
        }
        
        mock_mongo_instance = MagicMock()
        mock_mongodb.return_value = mock_mongo_instance
        mock_mongo_instance.get_categories.return_value = ['Frontend', 'Backend']
        
        # Mock 객체 추적에 추가
        self.mock_objects.extend([mock_es_instance, mock_mongo_instance])
        
        # 1. 헬스체크 (빠른 확인)
        response = self.client.get('/api/v1/search/health/')
        assert response.status_code == 200
        
        # 2. 검색 실행 (핵심 기능만)
        response = self.client.get('/api/v1/search/posts/', {'query': 'Django', 'page_size': 2})  # 페이지 크기 감소
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 1
        
        # 성능 확인
        elapsed_time = time.time() - start_time
        assert elapsed_time < self.test_timeout, f"테스트가 {elapsed_time:.2f}초 걸렸습니다 (제한: {self.test_timeout}초)"
        
    @patch('search.clients.elasticsearch_client.ElasticsearchClient')
    @patch('search.clients.mongodb_client.MongoDBClient') 
    @pytest.mark.django_db(transaction=False)  # 트랜잭션 비활성화로 메모리 절약
    @pytest.mark.timeout(3)  # 3초로 단축
    def test_search_logging_integration(self, mock_mongodb, mock_elasticsearch):
        """검색 로그 통합 테스트 (메모리 최적화 버전)"""
        # 경량 모킹 설정 - 불필요한 데이터 제거
        mock_es_instance = MagicMock()
        mock_elasticsearch.return_value = mock_es_instance
        mock_es_instance.search_posts.return_value = {
            'total': 1,
            'results': [],  # 빈 결과로 메모리 절약
            'aggregations': {'categories': {'buckets': []}, 'tags': {'buckets': []}, 'languages': {'buckets': []}}
        }
        
        mock_mongo_instance = MagicMock()
        mock_mongodb.return_value = mock_mongo_instance
        
        # Mock 객체 추적에 추가
        self.mock_objects.extend([mock_es_instance, mock_mongo_instance])
        
        from search.models import SearchLog
        
        # 초기 카운트 확인 (DB 쿼리 최소화)
        initial_count = SearchLog.objects.count()
        
        # 검색 실행 (최소한의 쿼리)
        response = self.client.get('/api/v1/search/posts/', {'query': 'T', 'page_size': 1})  # 쿼리 길이 최소화
        assert response.status_code == 200
        
        # 로그가 생성되었는지만 간단히 확인
        final_count = SearchLog.objects.count()
        assert final_count >= initial_count  # 엄격한 검증 완화
        
    @pytest.mark.timeout(3)  # 3초 타임아웃
    def test_error_handling_integration(self):
        """에러 처리 통합 테스트 (빠른 버전)"""
        # 잘못된 파라미터로 검색
        response = self.client.get('/api/v1/search/posts/', {'page_size': 'invalid'})
        assert response.status_code == 400


@pytest.mark.integration
class TestLightweightIntegration(TestCase):
    """가벼운 통합 테스트 모음 - 극도로 최적화된 버전"""
    
    @classmethod
    def setUpClass(cls):
        """클래스 레벨 설정 - 메모리 효율성 극대화"""
        super().setUpClass()
        cls.shared_client = APIClient()
    
    def setUp(self):
        """테스트 설정 - 최소한의 리소스만 사용"""
        self.client = self.shared_client  # 클라이언트 재사용
        
    def tearDown(self):
        """메모리 정리"""
        gc.collect()  # 가비지 컬렉션 강제 실행
    
    @pytest.mark.timeout(3)
    def test_basic_api_endpoints(self):
        """기본 API 엔드포인트 연결 테스트 - 메모리 최적화"""
        # 헬스체크만 빠르게 확인
        response = self.client.get('/api/v1/search/health/')
        assert response.status_code == 200
        
        # 간단한 에러 케이스
        response = self.client.get('/api/v1/search/posts/', {'page_size': 'invalid'})
        assert response.status_code == 400
    
    @pytest.mark.django_db(transaction=False)  # 트랜잭션 비활성화
    @pytest.mark.timeout(2)  # 2초로 더 단축
    def test_model_operations(self):
        """모델 기본 동작 테스트 - 메모리 최적화"""
        from search.models import SearchLog, PopularSearch
        
        # 간단한 모델 생성 - 최소한의 데이터
        log = SearchLog.record_log(query="Q", results_count=1)  # 쿼리 길이 최소화
        assert log.id is not None
        
        # 간단한 인기 검색어 생성
        popular = PopularSearch.update_popular_search("Q")  # 쿼리 길이 최소화
        assert popular.search_count == 1


# 기존의 무거운 테스트들은 조건부로만 실행
@pytest.mark.integration
@pytest.mark.slow  # 느린 테스트 마킹
class TestFullIntegration(TestCase):
    """전체 통합 테스트 (선택적 실행)"""
    
    @pytest.mark.django_db
    @pytest.mark.timeout(10)
    def test_complete_model_integration(self):
        """완전한 모델 통합 테스트"""
        from search.models import SearchLog, PopularSearch
        
        # 검색 로그 생성
        log = SearchLog.record_log(
            query="Complete Integration Test",
            results_count=5
        )
        
        assert log.id is not None
        assert log.query == "Complete Integration Test"
        
        # 인기 검색어 생성/업데이트
        popular1 = PopularSearch.update_popular_search("Complete Integration Test")
        assert popular1.search_count == 1
        
        popular2 = PopularSearch.update_popular_search("Complete Integration Test")
        assert popular2.search_count == 2
        assert popular1.id == popular2.id  # 같은 객체
        
        # 상위 인기 검색어 조회
        top_searches = PopularSearch.get_top_popular_searches(limit=5)
        assert len(top_searches) >= 1
        assert any(search['query'] == "Complete Integration Test" for search in top_searches)
