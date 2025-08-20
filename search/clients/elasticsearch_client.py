"""
VansDevBlog Search Service Elasticsearch Client

Elasticsearch 연결 및 검색 기능을 제공하는 클라이언트 클래스입니다.
"""

from typing import Dict, List, Any, Optional, Union
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError, NotFoundError
from elasticsearch_dsl.connections import connections
import logging

logger = logging.getLogger('search')


class ElasticsearchClient:
    """
    Elasticsearch 연결 및 검색 작업을 관리하는 클라이언트 클래스.
    
    이 클래스는 Elasticsearch 서버와의 연결을 관리하고,
    검색, 인덱싱, 클러스터 상태 확인 등의 작업을 수행합니다.
    
    Attributes:
        client (Elasticsearch): Elasticsearch 클라이언트 인스턴스
        
    Example:
        >>> es_client = ElasticsearchClient()
        >>> health = es_client.get_cluster_health()
        >>> print(health['status'])
        'green'
        
        >>> results = es_client.search_posts("Django")
        >>> print(f"Found {results['total']} posts")
    """
    
    def __init__(self):
        """
        ElasticsearchClient 인스턴스를 초기화합니다.
        
        Django 설정에서 Elasticsearch 연결 정보를 가져와서
        클라이언트 연결을 설정합니다.
        
        Raises:
            ConnectionError: Elasticsearch 서버에 연결할 수 없는 경우
        """
        try:
            self.client = connections.get_connection()
            logger.info("Elasticsearch client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {str(e)}")
            raise ConnectionError(f"Cannot connect to Elasticsearch: {str(e)}")
    
    def check_connection(self) -> bool:
        """
        Elasticsearch 서버 연결 상태를 확인합니다.
        
        Returns:
            bool: 연결 성공 시 True, 실패 시 False
            
        Example:
            >>> es_client = ElasticsearchClient()
            >>> if es_client.check_connection():
            ...     print("Elasticsearch is connected")
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
        
        Returns:
            Dict[str, Any]: 클러스터 상태 정보
                - status (str): 클러스터 상태 (green, yellow, red)
                - number_of_nodes (int): 노드 수
                - number_of_data_nodes (int): 데이터 노드 수
                - active_shards (int): 활성 샤드 수
                
        Raises:
            ConnectionError: Elasticsearch 연결 실패
            
        Example:
            >>> health = es_client.get_cluster_health()
            >>> print(f"Cluster status: {health['status']}")
        """
        try:
            health = self.client.cluster.health()
            logger.debug(f"Cluster health: {health['status']}")
            return health
        except Exception as e:
            logger.error(f"Failed to get cluster health: {str(e)}")
            raise ConnectionError(f"Cannot get cluster health: {str(e)}")
    
    def create_index_if_not_exists(self, index_name: str, mapping: Dict[str, Any]) -> bool:
        """
        인덱스가 존재하지 않으면 생성합니다.
        
        Args:
            index_name (str): 생성할 인덱스 이름
            mapping (Dict[str, Any]): 인덱스 매핑 설정
            
        Returns:
            bool: 인덱스 생성 성공 시 True, 이미 존재하거나 실패 시 False
            
        Example:
            >>> mapping = {
            ...     "mappings": {
            ...         "properties": {
            ...             "title": {"type": "text"}
            ...         }
            ...     }
            ... }
            >>> es_client.create_index_if_not_exists("test_index", mapping)
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
        
        Args:
            index_name (str): 삭제할 인덱스 이름
            
        Returns:
            bool: 삭제 성공 시 True, 실패 시 False
            
        Example:
            >>> es_client.delete_index("old_index")
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
        sort: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        게시물을 검색합니다.
        
        Args:
            query (str): 검색할 키워드
            filters (Optional[Dict[str, Any]]): 검색 필터
                - category (str): 카테고리 필터
                - tags (List[str]): 태그 필터
                - date_range (Dict): 날짜 범위 필터
                - language (str): 언어 필터
            page (int): 페이지 번호 (기본값: 1)
            page_size (int): 페이지 크기 (기본값: 20)
            sort (Optional[List[Dict[str, str]]]): 정렬 옵션
            
        Returns:
            Dict[str, Any]: 검색 결과
                - total (int): 전체 결과 수
                - hits (List[Dict]): 검색 결과 문서들
                - aggregations (Dict): 집계 결과 (카테고리, 태그 등)
                
        Example:
            >>> results = es_client.search_posts(
            ...     query="Django",
            ...     filters={"category": "Backend"},
            ...     page=1,
            ...     page_size=10
            ... )
            >>> print(f"Found {results['total']} posts")
        """
        try:
            # 기본 검색 쿼리 구성
            if query.strip():
                search_query = {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title^3",  # 제목에 가중치 3배
                            "title.english^2",
                            "content",
                            "content.english",
                            "summary^2",
                            "summary.english^2",
                            "tags^2"
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                }
            else:
                search_query = {"match_all": {}}
            
            # 필터 조건 구성
            filter_conditions = []
            
            if filters:
                if filters.get('theme'):
                    filter_conditions.append({
                        "term": {"theme": filters['theme']}
                    })
                
                if filters.get('category'):
                    filter_conditions.append({
                        "term": {"category": filters['category']}
                    })
                
                if filters.get('tags'):
                    filter_conditions.append({
                        "terms": {"tags": filters['tags']}
                    })
                
                if filters.get('language'):
                    filter_conditions.append({
                        "term": {"language": filters['language']}
                    })
                
                if filters.get('date_range'):
                    date_filter = {"range": {"published_date": {}}}
                    if filters['date_range'].get('start'):
                        date_filter["range"]["published_date"]["gte"] = filters['date_range']['start']
                    if filters['date_range'].get('end'):
                        date_filter["range"]["published_date"]["lte"] = filters['date_range']['end']
                    filter_conditions.append(date_filter)
            
            # 전체 쿼리 구성
            body = {
                "query": {
                    "bool": {
                        "must": [search_query],
                        "filter": filter_conditions
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {"fragment_size": 150, "number_of_fragments": 3},
                        "summary": {}
                    }
                },
                "aggs": {
                    "categories": {
                        "terms": {"field": "category", "size": 10}
                    },
                    "tags": {
                        "terms": {"field": "tags", "size": 20}
                    },
                    "languages": {
                        "terms": {"field": "language"}
                    }
                },
                "from": (page - 1) * page_size,
                "size": page_size
            }
            
            # 정렬 옵션 추가
            if sort:
                body["sort"] = sort
            else:
                body["sort"] = [
                    {"_score": {"order": "desc"}},
                    {"published_date": {"order": "desc"}}
                ]
            
            # 검색 실행
            response = self.client.search(
                index="vans_posts",
                body=body
            )
            
            # 결과 포맷팅 (ID와 점수만 반환)
            result = {
                "total": response["hits"]["total"]["value"],
                "hits": [
                    {
                        "post_id": hit["_source"]["post_id"],  # MongoDB ObjectId
                        "score": hit["_score"]
                    }
                    for hit in response["hits"]["hits"]
                ],
                "aggregations": response.get("aggregations", {})
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
        size: int = 10
    ) -> List[str]:
        """
        자동완성 제안을 반환합니다.
        
        Args:
            prefix (str): 자동완성할 접두사
            suggestion_type (Optional[str]): 제안 타입 (query, tag, category)
            language (str): 언어 코드 (기본값: "ko")
            size (int): 반환할 제안 수 (기본값: 10)
            
        Returns:
            List[str]: 자동완성 제안 목록
            
        Example:
            >>> suggestions = es_client.get_autocomplete_suggestions("Djan")
            >>> print(suggestions)
            ['Django', 'Django REST', 'Django Tutorial']
        """
        try:
            # 제목에서 자동완성 검색
            body = {
                "suggest": {
                    "title_suggest": {
                        "prefix": prefix,
                        "completion": {
                            "field": "title.suggest",
                            "size": size,
                            "contexts": {
                                "language": [language]
                            } if suggestion_type else {}
                        }
                    },
                    "tag_suggest": {
                        "prefix": prefix,
                        "completion": {
                            "field": "tags.suggest",
                            "size": size
                        }
                    }
                }
            }
            
            response = self.client.search(
                index="vans_posts",
                body=body
            )
            
            # 제안 추출 및 중복 제거
            suggestions = set()
            
            for suggest_result in response["suggest"]["title_suggest"]:
                for option in suggest_result["options"]:
                    suggestions.add(option["text"])
            
            for suggest_result in response["suggest"]["tag_suggest"]:
                for option in suggest_result["options"]:
                    suggestions.add(option["text"])
            
            result = list(suggestions)[:size]
            logger.debug(f"Autocomplete suggestions for '{prefix}': {len(result)} results")
            return result
            
        except Exception as e:
            logger.error(f"Autocomplete suggestion failed: {str(e)}")
            return []
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        인기 검색어 목록을 반환합니다.
        
        Args:
            limit (int): 반환할 검색어 수 (기본값: 10)
            
        Returns:
            List[Dict[str, Any]]: 인기 검색어 목록
                각 항목은 {'query': str, 'count': int} 형태
                
        Example:
            >>> popular = es_client.get_popular_searches(5)
            >>> for item in popular:
            ...     print(f"{item['query']}: {item['count']} searches")
        """
        try:
            # 실제 구현에서는 검색 로그 데이터를 분석
            # 현재는 더미 데이터 반환
            dummy_popular = [
                {"query": "Django", "count": 150},
                {"query": "Python", "count": 120},
                {"query": "Elasticsearch", "count": 95},
                {"query": "REST API", "count": 80},
                {"query": "웹 개발", "count": 75}
            ]
            
            return dummy_popular[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get popular searches: {str(e)}")
            return []
