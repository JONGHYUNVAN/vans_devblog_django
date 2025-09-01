"""
VansDevBlog Search Service Elasticsearch Client

Elasticsearch 연결 및 검색 기능을 제공하는 클라이언트 클래스입니다.
"""

import logging
from typing import Any, Dict, List, Optional

from elasticsearch_dsl.connections import connections

from ..services.content_parser import parse_rich_text_json

logger = logging.getLogger("search")


class ElasticsearchClient:
    """
    Elasticsearch 연결 및 검색 작업을 관리하는 클라이언트 클래스.
    """

    def __init__(self, timeout: Optional[int] = None):
        """
        ElasticsearchClient 인스턴스를 초기화합니다.
        """
        try:
            from django.conf import settings
            from elasticsearch import Elasticsearch

            es_config = settings.ELASTICSEARCH_DSL['default'].copy()
            if timeout:
                es_config['timeout'] = timeout
            
            self.client = Elasticsearch(**es_config)
            logger.info("Elasticsearch client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {str(e)}")
            raise ConnectionError(f"Cannot connect to Elasticsearch: {str(e)}")

    def check_connection(self) -> bool:
        """
        Elasticsearch 서버 연결 상태를 확인합니다.
        """
        try:
            self.client.ping()
            logger.debug("Elasticsearch connection check successful")
            return True
        except Exception as e:
            logger.warning(f"Elasticsearch connection check failed: {str(e)}")
            return False

    def get_cluster_health(self) -> Dict[str, Any]:
        """
        Elasticsearch 클러스터 상태 정보를 반환합니다.
        """
        try:
            health = self.client.cluster.health()
            logger.debug(f"Cluster health: {health['status']}")
            return health
        except Exception as e:
            logger.error(f"Failed to get cluster health: {str(e)}")
            raise ConnectionError(f"Cannot get cluster health: {str(e)}")

    def create_index_if_not_exists(
        self, index_name: str, mapping: Dict[str, Any]
    ) -> bool:
        """
        인덱스가 존재하지 않으면 생성합니다.
        """
        try:
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"Created index: {index_name}")
                return True
            else:
                logger.debug(f"Index already exists: {index_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {str(e)}")
            return False

    def delete_index(self, index_name: str) -> bool:
        """
        인덱스를 삭제합니다.
        """
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"Deleted index: {index_name}")
                return True
            else:
                logger.warning(f"Index does not exist: {index_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete index {index_name}: {str(e)}")
            return False

    def search_posts(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        sort: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        게시물을 검색하고, Elasticsearch에 저장된 실제 데이터(_source)를 기반으로 응답을 생성합니다.
        'content' 필드를 반드시 포함하여 반환합니다.
        """
        try:
            # 검색 쿼리: description과 topic을 대상으로 함
            if query.strip():
                search_query = {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description", "topic^2", "tags^2"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            else:
                search_query = {"match_all": {}}

            # 필터 조건 구성
            filter_conditions = []
            if filters:
                for field in ["theme", "category", "language"]:
                    if filters.get(field):
                        filter_conditions.append({"term": {field: filters[field]}})
                if filters.get("tags"):
                    filter_conditions.append({"terms": {"tags": filters["tags"]}})

            # Elasticsearch 쿼리 본문
            body = {
                "query": {"bool": {"must": [search_query], "filter": filter_conditions}},
                "highlight": {
                    "fields": {
                        "title": {},
                        "description": {"fragment_size": 150, "number_of_fragments": 1},
                        "topic": {"fragment_size": 150, "number_of_fragments": 1},
                    }
                },
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": sort or [{"_score": {"order": "desc"}}],
            }

            # 검색 실행
            response = self.client.search(index="vans_posts", body=body)

            # 결과 포맷팅
            hits = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                highlight = hit.get("highlight", {})

                # content 필드 생성 (본문 스니펫)
                content_snippet = ""
                if "description" in highlight:
                    content_snippet = highlight["description"][0]
                elif source.get("description"):
                    content_snippet = (source["description"][:150] + '...') if len(source["description"]) > 150 else source["description"]

                # summary 필드 생성 (주제)
                summary_text = source.get("topic", "")

                # author 객체 생성
                author_email = source.get("author_email")
                author = {
                    "user_id": author_email,
                    "username": author_email.split('@')[0] if author_email else None,
                    "display_name": author_email.split('@')[0] if author_email else None,
                    "profile_image": None,
                } if author_email else None

                # 최종 API 응답 객체 생성
                formatted_hit = {
                    "post_id": source.get("post_id"),
                    "title": source.get("title"),
                    "summary": summary_text,
                    "content": content_snippet, # content 필드 추가
                    "theme": source.get("theme"),
                    "category": source.get("category"),
                    "tags": source.get("tags"),
                    "author": author,
                    "updated_date": source.get("updated_date"),
                    "view_count": source.get("view_count"),
                    "like_count": source.get("like_count"),
                    "language": source.get("language"),
                    "reading_time": source.get("reading_time"),
                    "featured_image": source.get("thumbnail"),
                    "score": hit["_score"],
                    "highlight": highlight,
                }
                hits.append(formatted_hit)

            result = {
                "total": response["hits"]["total"]["value"],
                "hits": hits,
                "aggregations": response.get("aggregations", {}),
            }

            logger.info(f"Search completed: query='{query}', total={result['total']}")
            return result

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise Exception(f"Search request failed: {str(e)}")

    def get_autocomplete_suggestions(
        self,
        prefix: str,
        suggestion_type: Optional[str] = None,
        language: str = "ko",
        size: int = 10,
    ) -> List[str]:
        """
        자동완성 제안을 반환합니다.
        """
        try:
            body = {
                "query": {
                    "bool": {
                        "should": [
                            {"prefix": {"title": prefix}},
                            {"prefix": {"title.raw": prefix}},
                            {"prefix": {"tags": prefix}},
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "size": size,
                "_source": ["title", "tags"],
            }

            response = self.client.search(index="vans_posts", body=body)

            suggestions = set()
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                title = source.get("title", "")
                tags = source.get("tags", [])
                
                if title.lower().startswith(prefix.lower()):
                    suggestions.add(title)
                
                for tag in tags:
                    if tag.lower().startswith(prefix.lower()):
                        suggestions.add(tag)

            result = list(suggestions)[:size]
            logger.debug(
                f"Autocomplete suggestions for '{prefix}': {len(result)} results"
            )
            return result

        except Exception as e:
            logger.error(f"Autocomplete suggestion failed: {str(e)}")
            return []

    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        인기 검색어 목록을 반환합니다.
        """
        try:
            # This is a dummy implementation
            dummy_popular = [
                {"query": "Django", "count": 150},
                {"query": "Python", "count": 120},
                {"query": "Elasticsearch", "count": 95},
                {"query": "REST API", "count": 80},
                {"query": "웹 개발", "count": 75},
            ]
            return dummy_popular[:limit]
        except Exception as e:
            logger.error(f"Failed to get popular searches: {str(e)}")
            return []