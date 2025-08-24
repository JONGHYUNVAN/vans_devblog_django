"""
Clients Test Suite

외부 서비스 클라이언트를 테스트합니다.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from search.clients.elasticsearch_client import ElasticsearchClient
from search.clients.mongodb_client import MongoDBClient


class TestElasticsearchClient:
    """ElasticsearchClient 테스트"""

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    def test_client_initialization(self, mock_es_class):
        """클라이언트 초기화 테스트"""
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance

        client = ElasticsearchClient()

        assert client.client == mock_es_instance
        mock_es_class.assert_called_once()

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    def test_search_posts_success(self, mock_es_class):
        """게시물 검색 성공 테스트"""
        # 모킹 설정
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance

        mock_response = {
            "hits": {
                "total": {"value": 2},
                "hits": [{"_id": "123", "_score": 1.5}, {"_id": "456", "_score": 1.2}],
            },
            "aggregations": {
                "categories": {"buckets": []},
                "tags": {"buckets": []},
                "languages": {"buckets": []},
            },
        }
        mock_es_instance.search.return_value = mock_response

        client = ElasticsearchClient()
        result = client.search_posts(query="Django", filters={}, page=1, page_size=20)

        assert result["total"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["post_id"] == "123"

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    def test_search_posts_exception(self, mock_es_class):
        """게시물 검색 예외 처리 테스트"""
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance
        mock_es_instance.search.side_effect = Exception("Search failed")

        client = ElasticsearchClient()

        with pytest.raises(Exception) as exc_info:
            client.search_posts("test", {}, 1, 20)

        assert "Search request failed" in str(exc_info.value)

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    def test_autocomplete_success(self, mock_es_class):
        """자동완성 성공 테스트"""
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance

        mock_response = {
            "suggest": {
                "title_suggest": [
                    {"options": [{"text": "Django"}, {"text": "Django REST"}]}
                ]
            }
        }
        mock_es_instance.search.return_value = mock_response

        client = ElasticsearchClient()
        result = client.autocomplete("Dja")

        assert "suggestions" in result
        assert len(result["suggestions"]) == 2
        assert "Django" in result["suggestions"]

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    def test_health_check_success(self, mock_es_class):
        """헬스체크 성공 테스트"""
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance
        mock_es_instance.ping.return_value = True
        mock_es_instance.cluster.health.return_value = {
            "status": "green",
            "number_of_nodes": 1,
        }

        client = ElasticsearchClient()
        result = client.health_check()

        assert result["status"] == "healthy"
        assert result["cluster_status"] == "green"

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    def test_health_check_failure(self, mock_es_class):
        """헬스체크 실패 테스트"""
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance
        mock_es_instance.ping.return_value = False

        client = ElasticsearchClient()
        result = client.health_check()

        assert result["status"] == "unhealthy"


class TestMongoDBClient:
    """MongoDBClient 테스트"""

    @patch("search.clients.mongodb_client.MongoClient")
    def test_client_initialization(self, mock_mongo_class):
        """클라이언트 초기화 테스트"""
        mock_mongo_instance = Mock()
        mock_mongo_class.return_value = mock_mongo_instance

        client = MongoDBClient()

        assert client.client == mock_mongo_instance
        mock_mongo_class.assert_called_once()

    @patch("search.clients.mongodb_client.MongoClient")
    def test_get_categories_success(self, mock_mongo_class):
        """카테고리 조회 성공 테스트"""
        mock_mongo_instance = Mock()
        mock_mongo_class.return_value = mock_mongo_instance

        mock_db = Mock()
        mock_collection = Mock()
        mock_mongo_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.distinct.return_value = ["Frontend", "Backend", "Database"]

        client = MongoDBClient()
        categories = client.get_categories()

        assert len(categories) == 3
        assert "Frontend" in categories
        assert "Backend" in categories

    @patch("search.clients.mongodb_client.MongoClient")
    def test_get_categories_exception(self, mock_mongo_class):
        """카테고리 조회 예외 처리 테스트"""
        mock_mongo_instance = Mock()
        mock_mongo_class.return_value = mock_mongo_instance

        mock_db = Mock()
        mock_collection = Mock()
        mock_mongo_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.distinct.side_effect = Exception("Connection failed")

        client = MongoDBClient()
        categories = client.get_categories()

        # 예외 발생 시 빈 리스트 반환
        assert categories == []

    @patch("search.clients.mongodb_client.MongoClient")
    def test_health_check_success(self, mock_mongo_class):
        """헬스체크 성공 테스트"""
        mock_mongo_instance = Mock()
        mock_mongo_class.return_value = mock_mongo_instance

        mock_admin_db = Mock()
        mock_mongo_instance.admin = mock_admin_db
        mock_admin_db.command.return_value = {"ok": 1}

        client = MongoDBClient()
        result = client.health_check()

        assert result["status"] == "healthy"

    @patch("search.clients.mongodb_client.MongoClient")
    def test_health_check_failure(self, mock_mongo_class):
        """헬스체크 실패 테스트"""
        mock_mongo_instance = Mock()
        mock_mongo_class.return_value = mock_mongo_instance

        mock_admin_db = Mock()
        mock_mongo_instance.admin = mock_admin_db
        mock_admin_db.command.side_effect = Exception("Connection failed")

        client = MongoDBClient()
        result = client.health_check()

        assert result["status"] == "unhealthy"


class TestClientIntegration:
    """클라이언트 통합 테스트"""

    @patch("search.clients.elasticsearch_client.Elasticsearch")
    @patch("search.clients.mongodb_client.MongoClient")
    def test_both_clients_healthy(self, mock_mongo_class, mock_es_class):
        """두 클라이언트 모두 정상일 때 테스트"""
        # Elasticsearch 모킹
        mock_es_instance = Mock()
        mock_es_class.return_value = mock_es_instance
        mock_es_instance.ping.return_value = True
        mock_es_instance.cluster.health.return_value = {"status": "green"}

        # MongoDB 모킹
        mock_mongo_instance = Mock()
        mock_mongo_class.return_value = mock_mongo_instance
        mock_admin_db = Mock()
        mock_mongo_instance.admin = mock_admin_db
        mock_admin_db.command.return_value = {"ok": 1}

        es_client = ElasticsearchClient()
        mongo_client = MongoDBClient()

        es_health = es_client.health_check()
        mongo_health = mongo_client.health_check()

        assert es_health["status"] == "healthy"
        assert mongo_health["status"] == "healthy"
