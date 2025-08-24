import logging
import math
from typing import Any, Dict, List

from ..clients.elasticsearch_client import ElasticsearchClient
from ..clients.mongodb_client import MongoDBClient
from ..models import PopularSearch
from .cache_service import CacheService

logger = logging.getLogger("search")


class SearchService:
    def __init__(self):
        self.es_client = ElasticsearchClient()
        try:
            self.mongo_client = MongoDBClient()
        except Exception as e:
            logger.warning(f"MongoDB client initialization failed: {str(e)}")
            self.mongo_client = None
        self.cache_service = CacheService()

    def search_posts(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query = search_params.get("query", "")
            theme = search_params.get("theme", "")
            category = search_params.get("category", "")
            tags = search_params.get("tags", [])
            language = search_params.get("language", "all")
            date_from = search_params.get("date_from")
            date_to = search_params.get("date_to")
            page = search_params.get("page", 1)
            page_size = search_params.get("page_size", 20)
            sort_option = search_params.get("sort", "relevance")

            filters = self._build_filters(
                theme, category, tags, language, date_from, date_to
            )

            cached_result = self.cache_service.get_search_result(
                query, filters, page, page_size
            )
            if cached_result:
                logger.debug(f"Cache hit for search: '{query}'")
                return cached_result

            sort_params = self._build_sort_params(sort_option)

            search_result = self.es_client.search_posts(
                query=query,
                filters=filters,
                page=page,
                page_size=page_size,
                sort=sort_params,
            )

            response_data = self._build_search_response(search_result, page, page_size)

            # 검색 로그 기록 및 인기 검색어 업데이트
            try:
                from ..models import PopularSearch, SearchLog

                # 검색 로그 기록
                SearchLog.record_log(query=query, results_count=response_data["total"])

                # 인기 검색어 업데이트 (빈 검색어가 아닌 경우만)
                if query and query.strip():
                    PopularSearch.update_popular_search(query.strip())

                logger.debug(
                    f"Search log recorded: query='{query}', results={response_data['total']}"
                )

            except Exception as log_error:
                logger.warning(f"Failed to record search log: {str(log_error)}")

            self.cache_service.set_search_result(
                query, filters, page, page_size, response_data
            )

            logger.info(
                f"Search completed: query='{query}', total={response_data['total']}, page={page}"
            )
            return response_data

        except Exception as e:
            logger.error(f"Search service failed: {str(e)}", exc_info=True)
            raise

    def get_autocomplete_suggestions(
        self, autocomplete_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            query = autocomplete_params.get("query", "")
            language = autocomplete_params.get("language", "all")
            limit = autocomplete_params.get("limit", 10)

            cached_suggestions = self.cache_service.get_autocomplete_suggestions(
                query, language
            )
            if cached_suggestions:
                logger.debug(f"Autocomplete cache hit for: '{query}'")
                return {"suggestions": cached_suggestions[:limit], "query": query}

            suggestions = self.es_client.get_autocomplete_suggestions(
                prefix=query,
                language=language if language != "all" else "ko",
                size=limit,
            )

            self.cache_service.set_autocomplete_suggestions(
                query, language, suggestions
            )

            return {"suggestions": suggestions, "query": query}

        except Exception as e:
            logger.error(f"Autocomplete service failed: {str(e)}", exc_info=True)
            raise

    def get_popular_searches(self) -> Dict[str, Any]:
        """
        인기 검색어 목록을 제공합니다.
        """
        try:
            # 캐시 확인
            cached_popular = self.cache_service.get_popular_searches()
            if cached_popular:
                logger.debug("Popular searches cache hit")
                return {"popular_searches": cached_popular}

            # Django 모델에서 실제 인기 검색어 가져오기
            try:
                popular_list = PopularSearch.get_top_popular_searches(limit=10)
                if popular_list:
                    # 캐시 저장
                    self.cache_service.set_popular_searches(popular_list)
                    logger.debug(f"Popular searches from DB: {len(popular_list)} items")
                    return {"popular_searches": popular_list}
            except Exception as db_error:
                logger.warning(
                    f"Failed to get popular searches from DB: {str(db_error)}"
                )

            # DB에 데이터가 없으면 빈 배열 반환
            logger.info("No popular searches found in DB - returning empty list")
            return {"popular_searches": []}

        except Exception as e:
            logger.error(f"Get popular searches failed: {str(e)}")
            # 에러 시에도 빈 배열 반환
            return {"popular_searches": []}

    def get_categories(self) -> Dict[str, Any]:
        """
        사용 가능한 카테고리 목록을 제공합니다.
        """
        try:
            # 캐시 확인
            cached_categories = self.cache_service.get_categories()
            if cached_categories:
                logger.debug("Categories cache hit")
                return {"categories": cached_categories}

            # MongoDB에서 실제 카테고리 가져오기
            if self.mongo_client:
                categories = self.mongo_client.get_categories()
                if categories:
                    # 캐시 저장
                    self.cache_service.set_categories(categories)
                    logger.debug(f"Categories from MongoDB: {len(categories)} items")
                    return {"categories": categories}

            # MongoDB 실패 시 더미 데이터
            fallback_categories = [
                "Frontend",
                "Backend",
                "Database",
                "DevOps",
                "AI/ML",
                "Mobile",
                "Security",
                "Testing",
            ]

            logger.warning("Using fallback categories (MongoDB not available)")
            return {"categories": fallback_categories}

        except Exception as e:
            logger.error(f"Get categories failed: {str(e)}")
            # 에러 시 기본 카테고리 반환
            return {"categories": ["Frontend", "Backend", "Database"]}

    def _build_filters(
        self,
        theme: str,
        category: str,
        tags: List[str],
        language: str,
        date_from: Any,
        date_to: Any,
    ) -> Dict[str, Any]:
        filters = {
            "theme": theme,
            "category": category,
            "tags": tags,
            "language": language if language != "all" else None,
            "date_range": {},
        }

        if date_from:
            filters["date_range"]["start"] = date_from
        if date_to:
            filters["date_range"]["end"] = date_to

        if not filters["date_range"]:
            filters.pop("date_range")

        return filters

    def _build_sort_params(self, sort_option: str) -> List[Dict[str, Any]]:
        sort_mapping = {
            "relevance": [
                {"_score": {"order": "desc"}},
                {"published_date": {"order": "desc"}},
            ],
            "date_desc": [{"published_date": {"order": "desc"}}],
            "date_asc": [{"published_date": {"order": "asc"}}],
            "views_desc": [{"view_count": {"order": "desc"}}],
            "likes_desc": [{"like_count": {"order": "desc"}}],
        }
        return sort_mapping.get(sort_option, sort_mapping["relevance"])

    def _build_search_response(
        self, search_result: Dict[str, Any], page: int, page_size: int
    ) -> Dict[str, Any]:
        total = search_result["total"]
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "post_ids": [hit["post_id"] for hit in search_result["hits"]],
            "results": search_result["hits"],
            "aggregations": search_result.get("aggregations", {}),
        }
