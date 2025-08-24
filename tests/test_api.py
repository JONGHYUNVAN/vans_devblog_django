"""
API Test Suite

REST API 엔드포인트를 테스트합니다.
"""

import json
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSearchAPI:
    """검색 API 테스트"""

    def test_health_check_endpoint(self, api_client, mock_elasticsearch, mock_mongodb):
        """헬스체크 엔드포인트 테스트"""
        mock_elasticsearch.health_check.return_value = {"status": "healthy"}
        mock_mongodb.health_check.return_value = {"status": "healthy"}

        url = reverse("search_api:health-check")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "services" in data

    def test_search_posts_endpoint(self, api_client, mock_elasticsearch, mock_mongodb):
        """게시물 검색 엔드포인트 테스트"""
        # 모킹 설정
        mock_search_result = {
            "total": 1,
            "results": [{"post_id": "123", "score": 1.5}],
            "aggregations": {
                "categories": {"buckets": []},
                "tags": {"buckets": []},
                "languages": {"buckets": []},
            },
        }

        with patch(
            "search.services.search_service.SearchService.search_posts",
            return_value=mock_search_result,
        ):
            url = reverse("search_api:search-posts")
            response = api_client.get(url, {"query": "Django"})

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 1
            assert len(data["results"]) == 1

    def test_search_posts_invalid_params(self, api_client):
        """잘못된 파라미터로 검색 API 테스트"""
        url = reverse("search_api:search-posts")
        response = api_client.get(url, {"page_size": "invalid"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data

    def test_autocomplete_endpoint(self, api_client, mock_elasticsearch, mock_mongodb):
        """자동완성 엔드포인트 테스트"""
        mock_suggestions = {"suggestions": ["Django", "Django REST", "Django Testing"]}

        with patch(
            "search.services.search_service.SearchService.autocomplete",
            return_value=mock_suggestions,
        ):
            url = reverse("search_api:autocomplete")
            response = api_client.get(url, {"query": "Dja"})

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "suggestions" in data
            assert len(data["suggestions"]) == 3

    def test_popular_searches_endpoint(
        self, api_client, mock_elasticsearch, mock_mongodb
    ):
        """인기 검색어 엔드포인트 테스트"""
        mock_popular = {
            "popular_searches": [
                {"query": "Django", "count": 10},
                {"query": "Python", "count": 8},
            ]
        }

        with patch(
            "search.services.search_service.SearchService.get_popular_searches",
            return_value=mock_popular,
        ):
            url = reverse("search_api:popular-searches")
            response = api_client.get(url)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "popular_searches" in data
            assert len(data["popular_searches"]) == 2

    def test_categories_endpoint(self, api_client, mock_elasticsearch, mock_mongodb):
        """카테고리 엔드포인트 테스트"""
        mock_categories = {"categories": ["Frontend", "Backend", "Database"]}

        with patch(
            "search.services.search_service.SearchService.get_categories",
            return_value=mock_categories,
        ):
            url = reverse("search_api:get-categories")
            response = api_client.get(url)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "categories" in data
            assert len(data["categories"]) == 3


@pytest.mark.django_db
class TestAPIErrorHandling:
    """API 에러 처리 테스트"""

    def test_search_service_exception(
        self, api_client, mock_elasticsearch, mock_mongodb
    ):
        """검색 서비스 예외 처리 테스트"""
        with patch(
            "search.services.search_service.SearchService.search_posts",
            side_effect=Exception("Service error"),
        ):
            url = reverse("search_api:search-posts")
            response = api_client.get(url, {"query": "test"})

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "error" in data

    def test_autocomplete_service_exception(
        self, api_client, mock_elasticsearch, mock_mongodb
    ):
        """자동완성 서비스 예외 처리 테스트"""
        with patch(
            "search.services.search_service.SearchService.autocomplete",
            side_effect=Exception("Autocomplete error"),
        ):
            url = reverse("search_api:autocomplete")
            response = api_client.get(url, {"query": "test"})

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "error" in data


@pytest.mark.django_db
class TestAPIAuthentication:
    """API 인증 테스트"""

    def test_public_endpoints_no_auth_required(self, api_client):
        """공개 엔드포인트는 인증 불필요 테스트"""
        endpoints = [
            reverse("search_api:health-check"),
            reverse("search_api:search-posts"),
            reverse("search_api:autocomplete"),
            reverse("search_api:popular-searches"),
            reverse("search_api:get-categories"),
        ]

        for endpoint in endpoints:
            response = api_client.get(endpoint)
            # 401 Unauthorized가 아니어야 함 (400, 500 등은 허용)
            assert response.status_code != status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAPIPerformance:
    """API 성능 테스트"""

    def test_search_response_structure(
        self, api_client, mock_elasticsearch, mock_mongodb
    ):
        """검색 응답 구조 테스트"""
        mock_result = {
            "total": 10,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
            "results": [],
            "aggregations": {
                "categories": {"buckets": []},
                "tags": {"buckets": []},
                "languages": {"buckets": []},
            },
        }

        with patch(
            "search.services.search_service.SearchService.search_posts",
            return_value=mock_result,
        ):
            url = reverse("search_api:search-posts")
            response = api_client.get(url, {"query": "test"})

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # 필수 필드 검증
            required_fields = ["total", "page", "page_size", "total_pages", "results"]
            for field in required_fields:
                assert field in data

    def test_pagination_parameters(self, api_client, mock_elasticsearch, mock_mongodb):
        """페이지네이션 파라미터 테스트"""
        mock_result = {
            "total": 100,
            "page": 2,
            "page_size": 10,
            "total_pages": 10,
            "results": [],
            "aggregations": {
                "categories": {"buckets": []},
                "tags": {"buckets": []},
                "languages": {"buckets": []},
            },
        }

        with patch(
            "search.services.search_service.SearchService.search_posts",
            return_value=mock_result,
        ):
            url = reverse("search_api:search-posts")
            response = api_client.get(
                url, {"query": "test", "page": "2", "page_size": "10"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["page"] == 2
            assert data["page_size"] == 10
