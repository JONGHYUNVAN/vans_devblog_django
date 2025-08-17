"""
VansDevBlog Search Service Cache Utilities

검색 결과 캐싱을 위한 유틸리티 클래스입니다.
"""

from typing import Any, Optional, Dict, List
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging
from functools import wraps

logger = logging.getLogger('search')


class CacheManager:
    """
    검색 서비스 캐시 관리 클래스.
    
    Django 내장 캐시를 사용하여 검색 결과, 자동완성, 인기 검색어 등을
    효율적으로 캐싱합니다.
    
    Example:
        >>> cache_manager = CacheManager()
        >>> cache_manager.set_search_result("django", search_data)
        >>> result = cache_manager.get_search_result("django")
    """
    
    # 캐시 키 접두사
    SEARCH_PREFIX = "search_result:"
    AUTOCOMPLETE_PREFIX = "autocomplete:"
    POPULAR_PREFIX = "popular_searches:"
    POST_PREFIX = "post:"
    CATEGORY_PREFIX = "categories:"
    TAG_PREFIX = "tags:"
    
    def __init__(self):
        """CacheManager 인스턴스를 초기화합니다."""
        self.search_timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 300)
        self.autocomplete_timeout = getattr(settings, 'AUTOCOMPLETE_CACHE_TIMEOUT', 600)
        self.popular_timeout = getattr(settings, 'POPULAR_SEARCHES_CACHE_TIMEOUT', 3600)
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        캐시 키를 생성합니다.
        
        Args:
            prefix (str): 캐시 키 접두사
            *args: 키 생성에 사용할 위치 인자들
            **kwargs: 키 생성에 사용할 키워드 인자들
            
        Returns:
            str: 생성된 캐시 키
            
        Example:
            >>> key = cache_manager._generate_cache_key("search:", "django", page=1)
            >>> print(key)
            'search:django:page_1:hash_abc123'
        """
        try:
            # 인자들을 문자열로 변환
            key_parts = [prefix]
            
            for arg in args:
                if isinstance(arg, (dict, list)):
                    key_parts.append(json.dumps(arg, sort_keys=True))
                else:
                    key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (dict, list)):
                    key_parts.append(f"{k}_{json.dumps(v, sort_keys=True)}")
                else:
                    key_parts.append(f"{k}_{v}")
            
            # 키가 너무 길면 해시 생성
            key = ":".join(key_parts)
            if len(key) > 200:
                key_hash = hashlib.md5(key.encode()).hexdigest()
                key = f"{prefix}hash_{key_hash}"
            
            return key
            
        except Exception as e:
            logger.warning(f"Failed to generate cache key: {str(e)}")
            return f"{prefix}fallback_{hashlib.md5(str(args).encode()).hexdigest()}"
    
    def set_search_result(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        page: int,
        page_size: int,
        result: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> bool:
        """
        검색 결과를 캐시에 저장합니다.
        
        Args:
            query (str): 검색 쿼리
            filters (Optional[Dict[str, Any]]): 필터 조건
            page (int): 페이지 번호
            page_size (int): 페이지 크기
            result (Dict[str, Any]): 검색 결과
            timeout (Optional[int]): 캐시 만료 시간 (초)
            
        Returns:
            bool: 캐시 저장 성공 여부
            
        Example:
            >>> success = cache_manager.set_search_result(
            ...     "django", {"category": "backend"}, 1, 20, search_results
            ... )
        """
        try:
            cache_key = self._generate_cache_key(
                self.SEARCH_PREFIX,
                query,
                filters or {},
                page=page,
                page_size=page_size
            )
            
            timeout = timeout or self.search_timeout
            cache.set(cache_key, result, timeout)
            
            logger.debug(f"Cached search result: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache search result: {str(e)}")
            return False
    
    def get_search_result(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        page: int,
        page_size: int
    ) -> Optional[Dict[str, Any]]:
        """
        캐시된 검색 결과를 반환합니다.
        
        Args:
            query (str): 검색 쿼리
            filters (Optional[Dict[str, Any]]): 필터 조건
            page (int): 페이지 번호
            page_size (int): 페이지 크기
            
        Returns:
            Optional[Dict[str, Any]]: 캐시된 검색 결과 또는 None
            
        Example:
            >>> result = cache_manager.get_search_result(
            ...     "django", {"category": "backend"}, 1, 20
            ... )
            >>> if result:
            ...     print(f"Cache hit! Found {result['total']} results")
        """
        try:
            cache_key = self._generate_cache_key(
                self.SEARCH_PREFIX,
                query,
                filters or {},
                page=page,
                page_size=page_size
            )
            
            result = cache.get(cache_key)
            if result:
                logger.debug(f"Cache hit: {cache_key}")
            else:
                logger.debug(f"Cache miss: {cache_key}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get cached search result: {str(e)}")
            return None
    
    def set_autocomplete_suggestions(
        self,
        prefix: str,
        language: str,
        suggestions: List[str],
        timeout: Optional[int] = None
    ) -> bool:
        """
        자동완성 제안을 캐시에 저장합니다.
        
        Args:
            prefix (str): 검색 접두사
            language (str): 언어 코드
            suggestions (List[str]): 제안 목록
            timeout (Optional[int]): 캐시 만료 시간
            
        Returns:
            bool: 캐시 저장 성공 여부
        """
        try:
            cache_key = self._generate_cache_key(
                self.AUTOCOMPLETE_PREFIX,
                prefix,
                language=language
            )
            
            timeout = timeout or self.autocomplete_timeout
            cache.set(cache_key, suggestions, timeout)
            
            logger.debug(f"Cached autocomplete suggestions: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache autocomplete suggestions: {str(e)}")
            return False
    
    def get_autocomplete_suggestions(
        self,
        prefix: str,
        language: str
    ) -> Optional[List[str]]:
        """
        캐시된 자동완성 제안을 반환합니다.
        
        Args:
            prefix (str): 검색 접두사
            language (str): 언어 코드
            
        Returns:
            Optional[List[str]]: 캐시된 제안 목록 또는 None
        """
        try:
            cache_key = self._generate_cache_key(
                self.AUTOCOMPLETE_PREFIX,
                prefix,
                language=language
            )
            
            suggestions = cache.get(cache_key)
            if suggestions:
                logger.debug(f"Autocomplete cache hit: {cache_key}")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get cached autocomplete suggestions: {str(e)}")
            return None
    
    def set_popular_searches(
        self,
        searches: List[Dict[str, Any]],
        timeout: Optional[int] = None
    ) -> bool:
        """
        인기 검색어를 캐시에 저장합니다.
        
        Args:
            searches (List[Dict[str, Any]]): 인기 검색어 목록
            timeout (Optional[int]): 캐시 만료 시간
            
        Returns:
            bool: 캐시 저장 성공 여부
        """
        try:
            cache_key = f"{self.POPULAR_PREFIX}list"
            timeout = timeout or self.popular_timeout
            cache.set(cache_key, searches, timeout)
            
            logger.debug("Cached popular searches")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache popular searches: {str(e)}")
            return False
    
    def get_popular_searches(self) -> Optional[List[Dict[str, Any]]]:
        """
        캐시된 인기 검색어를 반환합니다.
        
        Returns:
            Optional[List[Dict[str, Any]]]: 캐시된 인기 검색어 목록 또는 None
        """
        try:
            cache_key = f"{self.POPULAR_PREFIX}list"
            searches = cache.get(cache_key)
            
            if searches:
                logger.debug("Popular searches cache hit")
            
            return searches
            
        except Exception as e:
            logger.error(f"Failed to get cached popular searches: {str(e)}")
            return None
    
    def set_categories(self, categories: List[str], timeout: Optional[int] = None) -> bool:
        """
        카테고리 목록을 캐시에 저장합니다.
        
        Args:
            categories (List[str]): 카테고리 목록
            timeout (Optional[int]): 캐시 만료 시간
            
        Returns:
            bool: 캐시 저장 성공 여부
        """
        try:
            cache_key = f"{self.CATEGORY_PREFIX}list"
            timeout = timeout or self.popular_timeout
            cache.set(cache_key, categories, timeout)
            
            logger.debug("Cached categories")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache categories: {str(e)}")
            return False
    
    def get_categories(self) -> Optional[List[str]]:
        """
        캐시된 카테고리 목록을 반환합니다.
        
        Returns:
            Optional[List[str]]: 캐시된 카테고리 목록 또는 None
        """
        try:
            cache_key = f"{self.CATEGORY_PREFIX}list"
            categories = cache.get(cache_key)
            
            if categories:
                logger.debug("Categories cache hit")
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to get cached categories: {str(e)}")
            return None
    
    def invalidate_search_cache(self, pattern: Optional[str] = None) -> bool:
        """
        검색 관련 캐시를 무효화합니다.
        
        Args:
            pattern (Optional[str]): 특정 패턴의 캐시만 삭제 (None이면 모든 검색 캐시)
            
        Returns:
            bool: 캐시 무효화 성공 여부
            
        Example:
            >>> # 모든 검색 캐시 삭제
            >>> cache_manager.invalidate_search_cache()
            
            >>> # 특정 쿼리 관련 캐시만 삭제
            >>> cache_manager.invalidate_search_cache("django")
        """
        try:
            if pattern:
                # 특정 패턴 캐시 삭제 (Django 기본 캐시는 패턴 삭제 미지원)
                logger.warning("Pattern-based cache invalidation not supported with default cache backend")
                return False
            else:
                # 전체 캐시 삭제
                cache.clear()
                logger.info("All search cache invalidated")
                return True
                
        except Exception as e:
            logger.error(f"Failed to invalidate search cache: {str(e)}")
            return False


def cache_result(cache_key_func, timeout=300):
    """
    함수 결과를 캐시하는 데코레이터.
    
    Args:
        cache_key_func: 캐시 키를 생성하는 함수
        timeout (int): 캐시 만료 시간 (초)
        
    Example:
        >>> @cache_result(lambda x: f"user_posts:{x}", timeout=600)
        ... def get_user_posts(user_id):
        ...     return expensive_database_query(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 캐시 키 생성
                cache_key = cache_key_func(*args, **kwargs)
                
                # 캐시에서 결과 확인
                result = cache.get(cache_key)
                if result is not None:
                    logger.debug(f"Cache hit for function {func.__name__}: {cache_key}")
                    return result
                
                # 함수 실행 및 결과 캐시
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                
                logger.debug(f"Cached result for function {func.__name__}: {cache_key}")
                return result
                
            except Exception as e:
                logger.error(f"Cache decorator error for {func.__name__}: {str(e)}")
                # 캐시 오류 시 원본 함수 실행
                return func(*args, **kwargs)
        
        return wrapper
    return decorator
