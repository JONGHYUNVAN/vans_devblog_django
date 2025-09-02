"""
VansDevBlog Search Service Popular Search Document

인기 검색어 Elasticsearch 문서를 정의하고 관리합니다.
elasticsearch-dsl 대신 elasticsearch-py 클라이언트를 직접 사용하여
연결 방식을 통일합니다.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from django.conf import settings
from elasticsearch import Elasticsearch

from .analyzers import BASE_INDEX_SETTINGS, korean_analyzer

logger = logging.getLogger("search")

# --- Constants ---
INDEX_NAME = "vans_popular_searches"


# --- Helper Function ---
def _get_es_client() -> Elasticsearch:
    """
    설정에서 Elasticsearch 클라이언트 인스턴스를 생성하여 반환합니다.
    """
    try:
        es_config = settings.ELASTICSEARCH_DSL['default'].copy()
        return Elasticsearch(**es_config)
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch client for popular search: {str(e)}")
        raise ConnectionError(f"Cannot connect to Elasticsearch for popular search: {str(e)}")


# --- Main Class ---
class PopularSearchDocument:
    """
    인기 검색어 Elasticsearch 문서를 관리하는 클래스.
    (elasticsearch-dsl.Document를 상속하지 않음)
    """

    @staticmethod
    def update_popular_search(query_text: str) -> None:
        """
        인기 검색어를 업데이트하거나 새로 생성합니다.

        Args:
            query_text: 검색어
        """
        es = _get_es_client()
        now = datetime.now()

        try:
            # 1. 기존 검색어가 있는지 확인
            search_body = {
                "query": {
                    "term": {
                        "query.keyword": query_text
                    }
                }
            }
            response = es.search(index=INDEX_NAME, body=search_body)
            
            if response['hits']['total']['value'] > 0:
                # 2a. 기존 검색어 업데이트 (painless script 사용)
                doc_id = response['hits']['hits'][0]['_id']
                update_body = {
                    "script": {
                        "source": "ctx._source.search_count += 1; ctx._source.last_searched = params.now",
                        "lang": "painless",
                        "params": {
                            "now": now.isoformat()
                        }
                    }
                }
                es.update(index=INDEX_NAME, id=doc_id, body=update_body)
                logger.info(f"Updated popular search: '{query_text}'")
            else:
                # 2b. 새 검색어 생성
                doc_body = {
                    "query": query_text,
                    "search_count": 1,
                    "last_searched": now,
                    "created_at": now,
                }
                es.index(index=INDEX_NAME, body=doc_body, refresh=True)
                logger.info(f"Created popular search: '{query_text}'")

        except Exception as e:
            logger.error(f"Failed to update popular search '{query_text}': {str(e)}")
            # 여기서 에러를 다시 raise하여 호출 측에서 알 수 있도록 함
            raise

    @staticmethod
    def get_top_popular_searches(limit: int = 10) -> List[Dict[str, Any]]:
        """
        상위 인기 검색어 목록을 반환합니다.

        Args:
            limit: 반환할 검색어 수

        Returns:
            List[Dict]: 인기 검색어 목록 [{"query": "검색어", "count": 횟수}]
        """
        es = _get_es_client()
        try:
            search_body = {
                "size": limit,
                "sort": [
                    {"search_count": {"order": "desc"}},
                    {"last_searched": {"order": "desc"}},
                ],
                "_source": ["query", "search_count"]
            }
            response = es.search(index=INDEX_NAME, body=search_body)

            popular_list = [
                {
                    "query": hit['_source']['query'],
                    "count": hit['_source']['search_count'],
                }
                for hit in response['hits']['hits']
            ]

            logger.debug(f"Retrieved {len(popular_list)} popular searches")
            return popular_list

        except Exception as e:
            # 인덱스가 없는 경우 등 에러 발생 시 빈 리스트 반환
            logger.error(f"Failed to get popular searches: {str(e)}")
            return []

    @staticmethod
    def delete_index():
        """
        인덱스를 삭제합니다.
        """
        es = _get_es_client()
        try:
            if es.indices.exists(index=INDEX_NAME):
                es.indices.delete(index=INDEX_NAME)
                logger.info(f"Deleted index: {INDEX_NAME}")
        except Exception as e:
            logger.error(f"Failed to delete index {INDEX_NAME}: {str(e)}")
            raise

    @staticmethod
    def create_index_if_not_exists():
        """
        인덱스가 존재하지 않으면 생성합니다.
        (elasticsearch-dsl.Document.init() 대체)
        """
        es = _get_es_client()
        try:
            if not es.indices.exists(index=INDEX_NAME):
                mapping = {
                    "settings": BASE_INDEX_SETTINGS,
                    "mappings": {
                        "properties": {
                            "query": {
                                "type": "text",
                                "analyzer": "korean_analyzer",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword"
                                    }
                                }
                            },
                            "search_count": {
                                "type": "integer"
                            },
                            "last_searched": {
                                "type": "date"
                            },
                            "created_at": {
                                "type": "date"
                            }
                        }
                    }
                }
                es.indices.create(index=INDEX_NAME, body=mapping)
                logger.info(f"Created index: {INDEX_NAME}")
            else:
                logger.debug(f"Index already exists: {INDEX_NAME}")
        except Exception as e:
            logger.error(f"Failed to create index {INDEX_NAME}: {str(e)}")
            raise