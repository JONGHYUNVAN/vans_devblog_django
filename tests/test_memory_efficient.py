"""
Memory-Efficient Test Suite

메모리 사용량을 최소화한 통합 테스트입니다.
1기가 메모리 누수 문제를 해결하기 위해 설계되었습니다.
"""

import gc
import os
from unittest.mock import MagicMock, patch

import psutil
import pytest
from django.db import connection, connections
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    },
    LOGGING_CONFIG=None,  # 로깅 비활성화로 메모리 절약
)
class MemoryEfficientTestCase(TestCase):
    """메모리 효율적인 기본 테스트 클래스"""

    @classmethod
    def setUpClass(cls):
        """클래스 레벨 설정 - 리소스 최소화"""
        super().setUpClass()
        cls.process = psutil.Process(os.getpid())
        cls.initial_memory = cls.process.memory_info().rss / 1024 / 1024  # MB
        print(f"🔍 초기 메모리 사용량: {cls.initial_memory:.2f} MB")

        # 공유 클라이언트 - 메모리 절약
        cls.api_client = APIClient()

    @classmethod
    def tearDownClass(cls):
        """클래스 정리 - 메모리 확인"""
        # DB 연결 정리
        for conn in connections.all():
            conn.close()

        # 강제 가비지 컬렉션
        collected = gc.collect()

        # 최종 메모리 확인
        final_memory = cls.process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = final_memory - cls.initial_memory

        print(f"🔍 최종 메모리 사용량: {final_memory:.2f} MB")
        print(f"🔍 메모리 차이: {memory_diff:.2f} MB")
        print(f"🗑️  가비지 컬렉션 정리: {collected}개 객체")

        # 메모리 사용량이 500MB를 초과하면 경고
        if memory_diff > 500:
            print(f"⚠️  경고: 메모리 사용량이 {memory_diff:.2f}MB 증가했습니다!")
        else:
            print(f"✅ 메모리 사용량 정상: {memory_diff:.2f}MB 증가")

        super().tearDownClass()

    def setUp(self):
        """테스트별 설정 - 최소화"""
        self.client = self.api_client  # 클라이언트 재사용
        self.mocks = []  # Mock 추적

    def tearDown(self):
        """테스트별 정리 - 메모리 누수 방지"""
        # Mock 객체 정리
        for mock in self.mocks:
            if hasattr(mock, "reset_mock"):
                mock.reset_mock()
        self.mocks.clear()

        # DB 쿼리 캐시 정리
        if hasattr(connection, "queries"):
            connection.queries.clear()

        # 가비지 컬렉션
        gc.collect()


@pytest.mark.memory_test
class TestMemoryEfficient(MemoryEfficientTestCase):
    """메모리 효율적인 통합 테스트"""

    @pytest.mark.timeout(3)
    def test_basic_endpoints_memory_safe(self):
        """기본 엔드포인트 테스트 - 메모리 안전"""
        # 메모리 사용량 모니터링
        start_memory = self.process.memory_info().rss / 1024 / 1024

        # 최소한의 API 호출
        response = self.client.get("/api/v1/search/health/")
        assert response.status_code == 200

        # 에러 케이스 (간단)
        response = self.client.get("/api/v1/search/posts/", {"page_size": "x"})
        assert response.status_code == 400

        # 메모리 사용량 확인
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory

        # 테스트 하나에 50MB 이상 사용하면 경고
        assert memory_used < 50, f"테스트에서 {memory_used:.2f}MB 사용 (제한: 50MB)"

    @patch("search.clients.elasticsearch_client.ElasticsearchClient")
    @pytest.mark.timeout(2)
    def test_search_with_minimal_mocking(self, mock_es):
        """최소한의 모킹으로 검색 테스트"""
        start_memory = self.process.memory_info().rss / 1024 / 1024

        # 극도로 간단한 모킹
        mock_instance = MagicMock()
        mock_es.return_value = mock_instance
        mock_instance.search_posts.return_value = {
            "total": 0,
            "results": [],
            "aggregations": {
                "categories": {"buckets": []},
                "tags": {"buckets": []},
                "languages": {"buckets": []},
            },
        }

        # Mock 추적
        self.mocks.append(mock_instance)

        # 최소한의 검색
        response = self.client.get(
            "/api/v1/search/posts/", {"query": "x", "page_size": 1}
        )
        assert response.status_code == 200

        # 메모리 확인
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory
        assert memory_used < 30, f"검색 테스트에서 {memory_used:.2f}MB 사용 (제한: 30MB)"

    @pytest.mark.django_db(transaction=False)
    @pytest.mark.timeout(2)
    def test_model_operations_minimal(self):
        """최소한의 모델 테스트"""
        start_memory = self.process.memory_info().rss / 1024 / 1024

        from search.models import SearchLog

        # 아주 간단한 로그 하나만 생성
        log = SearchLog.record_log(query="x", results_count=0)
        assert log.id is not None

        # 즉시 정리
        log.delete()

        # 메모리 확인
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory
        assert memory_used < 20, f"모델 테스트에서 {memory_used:.2f}MB 사용 (제한: 20MB)"


@pytest.mark.memory_stress
class TestMemoryStress(MemoryEfficientTestCase):
    """메모리 스트레스 테스트 - 선택적 실행"""

    @pytest.mark.timeout(10)
    def test_multiple_requests_memory_stable(self):
        """여러 요청에서 메모리 안정성 테스트"""
        start_memory = self.process.memory_info().rss / 1024 / 1024

        # 10번의 요청 (기존에는 이것만으로도 메모리 폭발)
        for i in range(10):
            response = self.client.get("/api/v1/search/health/")
            assert response.status_code == 200

            # 중간에 가비지 컬렉션
            if i % 3 == 0:
                gc.collect()

        # 최종 메모리 확인
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory

        # 10번 요청에 100MB 이상 사용하면 문제
        assert memory_used < 100, f"10번 요청에서 {memory_used:.2f}MB 사용 (제한: 100MB)"
        print(f"✅ 10번 요청 메모리 사용량: {memory_used:.2f}MB (정상)")


if __name__ == "__main__":
    # 메모리 효율 테스트만 실행
    pytest.main([__file__, "-v", "--tb=short", "-m", "memory_test"])
