"""
VansDevBlog Search Service Health Check Service

서비스 상태 확인 관련 비즈니스 로직을 담당합니다.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("search")


class HealthService:
    """
    서비스 상태 확인을 담당하는 서비스 클래스입니다.
    """

    def get_health_status(self) -> Dict[str, Any]:
        """
        서비스의 전반적인 상태를 확인합니다.

        Returns:
            Dict[str, Any]: 서비스 상태 정보
        """
        try:
            # Elasticsearch 연결 상태 확인
            elasticsearch_connected = self._check_elasticsearch_connection()

            # MongoDB 연결 상태 확인
            mongodb_connected = self._check_mongodb_connection()

            # 전체 상태 결정
            overall_status = (
                "healthy"
                if elasticsearch_connected and mongodb_connected
                else "degraded"
            )

            return {
                "status": overall_status,
                "service": "VansDevBlog Search Service",
                "version": "1.0.0",
                "components": {
                    "elasticsearch": {
                        "status": "up" if elasticsearch_connected else "down",
                        "connected": elasticsearch_connected,
                    },
                    "mongodb": {
                        "status": "up" if mongodb_connected else "down",
                        "connected": mongodb_connected,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "VansDevBlog Search Service",
                "version": "1.0.0",
                "error": str(e),
            }

    def _check_elasticsearch_connection(self) -> bool:
        """
        Elasticsearch 연결 상태를 확인합니다.

        Returns:
            bool: 연결 상태
        """
        try:
            from ..clients.elasticsearch_client import ElasticsearchClient

            es_client = ElasticsearchClient()
            return es_client.check_connection()
        except Exception as e:
            logger.warning(f"Elasticsearch connection check failed: {str(e)}")
            return False

    def _check_mongodb_connection(self) -> bool:
        """
        MongoDB 연결 상태를 확인합니다.

        Returns:
            bool: 연결 상태
        """
        try:
            from ..clients.mongodb_client import MongoDBClient

            mongo_client = MongoDBClient()
            return mongo_client.check_connection()
        except Exception as e:
            logger.warning(f"MongoDB connection check failed: {str(e)}")
            return False
