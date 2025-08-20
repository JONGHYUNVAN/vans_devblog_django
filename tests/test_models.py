"""
Models Test Suite

Django 모델의 기능을 테스트합니다.
"""

import pytest
from django.utils import timezone
from django.db import IntegrityError
from search.models import SearchLog, PopularSearch


@pytest.mark.django_db
class TestSearchLog:
    """SearchLog 모델 테스트"""
    
    def test_create_search_log(self):
        """검색 로그 생성 테스트"""
        log = SearchLog.objects.create(
            query="Django REST",
            results_count=5,
            response_time_ms=120
        )
        
        assert log.query == "Django REST"
        assert log.results_count == 5
        assert log.response_time_ms == 120
        assert log.search_time is not None
        
    def test_record_log_class_method(self):
        """record_log 클래스 메서드 테스트"""
        log = SearchLog.record_log(
            query="Python Testing",
            results_count=3,
            response_time_ms=200
        )
        
        assert isinstance(log, SearchLog)
        assert log.query == "Python Testing"
        assert log.results_count == 3
        
    def test_search_log_str_representation(self):
        """SearchLog __str__ 메서드 테스트"""
        log = SearchLog.objects.create(
            query="Test Query",
            results_count=10
        )
        
        str_repr = str(log)
        assert "Test Query" in str_repr
        assert "10 results" in str_repr


@pytest.mark.django_db
class TestPopularSearch:
    """PopularSearch 모델 테스트"""
    
    def test_create_popular_search(self):
        """인기 검색어 생성 테스트"""
        popular = PopularSearch.objects.create(
            query="React Hooks",
            search_count=15
        )
        
        assert popular.query == "React Hooks"
        assert popular.search_count == 15
        assert popular.last_searched is not None
        
    def test_update_popular_search_new(self):
        """새로운 인기 검색어 업데이트 테스트"""
        popular = PopularSearch.update_popular_search("New Framework")
        
        assert popular.query == "New Framework"
        assert popular.search_count == 1
        
    def test_update_popular_search_existing(self):
        """기존 인기 검색어 업데이트 테스트"""
        # 첫 번째 검색
        PopularSearch.update_popular_search("Vue.js")
        
        # 같은 검색어 재검색
        popular = PopularSearch.update_popular_search("Vue.js")
        
        assert popular.search_count == 2
        
    def test_get_top_popular_searches(self):
        """상위 인기 검색어 조회 테스트"""
        # 테스트 데이터 생성
        PopularSearch.objects.create(query="Django", search_count=10)
        PopularSearch.objects.create(query="Python", search_count=20)
        PopularSearch.objects.create(query="React", search_count=5)
        
        top_searches = PopularSearch.get_top_popular_searches(limit=2)
        
        assert len(top_searches) == 2
        assert top_searches[0]['query'] == "Python"  # 가장 높은 카운트
        assert top_searches[0]['count'] == 20
        assert top_searches[1]['query'] == "Django"
        
    def test_popular_search_unique_constraint(self):
        """인기 검색어 유니크 제약조건 테스트"""
        PopularSearch.objects.create(query="Unique Test", search_count=1)
        
        with pytest.raises(IntegrityError):
            PopularSearch.objects.create(query="Unique Test", search_count=2)
            
    def test_popular_search_str_representation(self):
        """PopularSearch __str__ 메서드 테스트"""
        popular = PopularSearch.objects.create(
            query="Test Framework",
            search_count=25
        )
        
        str_repr = str(popular)
        assert "Test Framework" in str_repr
        assert "Count: 25" in str_repr
