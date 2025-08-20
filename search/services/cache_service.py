import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from django.core.cache import cache
from django.conf import settings
from functools import wraps

logger = logging.getLogger('search')


class CacheService:
    def __init__(self):
        self.search_cache_timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 300)
        self.autocomplete_cache_timeout = getattr(settings, 'AUTOCOMPLETE_CACHE_TIMEOUT', 600)
        self.popular_searches_cache_timeout = getattr(settings, 'POPULAR_SEARCHES_CACHE_TIMEOUT', 3600)
        self.category_cache_timeout = getattr(settings, 'POPULAR_SEARCHES_CACHE_TIMEOUT', 3600) # Using popular searches timeout for categories

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        try:
            key_parts = [prefix]
            
            for arg in args:
                if isinstance(arg, (dict, list)):
                    key_parts.append(json.dumps(arg, sort_keys=True, default=str))
                else:
                    key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (dict, list)):
                    key_parts.append(f"{k}_{json.dumps(v, sort_keys=True, default=str)}")
                else:
                    key_parts.append(f"{k}_{v}")
            
            key = ":".join(key_parts)
            if len(key) > 200:
                key_hash = hashlib.md5(key.encode()).hexdigest()
                key = f"{prefix}hash_{key_hash}"
            
            return key
            
        except Exception as e:
            logger.warning(f"Failed to generate cache key: {str(e)}")
            return f"{prefix}fallback_{hashlib.md5(str(args).encode()).hexdigest()}"

    def get_search_result(self, query: str, filters: Dict[str, Any], 
                         page: int, page_size: int) -> Optional[Dict[str, Any]]:
        try:
            cache_key = self._generate_cache_key("search_result:", query, filters, page=page, page_size=page_size)
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.debug(f"Cache hit for search key: {cache_key}")
                return cached_result
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get search cache: {str(e)}")
            return None
    
    def set_search_result(self, query: str, filters: Dict[str, Any], 
                         page: int, page_size: int, result: Dict[str, Any]) -> None:
        try:
            cache_key = self._generate_cache_key("search_result:", query, filters, page=page, page_size=page_size)
            cache.set(cache_key, result, self.search_cache_timeout)
            logger.debug(f"Cached search result with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Failed to set search cache: {str(e)}")
    
    def get_autocomplete_suggestions(self, query: str, language: str) -> Optional[List[str]]:
        try:
            cache_key = self._generate_cache_key("autocomplete:", query, language=language)
            cached_suggestions = cache.get(cache_key)
            
            if cached_suggestions:
                logger.debug(f"Cache hit for autocomplete key: {cache_key}")
                return cached_suggestions
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get autocomplete cache: {str(e)}")
            return None
    
    def set_autocomplete_suggestions(self, query: str, language: str, suggestions: List[str]) -> None:
        try:
            cache_key = self._generate_cache_key("autocomplete:", query, language=language)
            cache.set(cache_key, suggestions, self.autocomplete_cache_timeout)
            logger.debug(f"Cached autocomplete suggestions with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Failed to set autocomplete cache: {str(e)}")
    
    def get_popular_searches(self) -> Optional[List[Dict[str, Any]]]:
        try:
            cache_key = self._generate_cache_key("popular_searches:", "list")
            cached_popular = cache.get(cache_key)
            
            if cached_popular:
                logger.debug(f"Cache hit for popular searches")
                return cached_popular
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get popular searches cache: {str(e)}")
            return None
    
    def set_popular_searches(self, popular_list: List[Dict[str, Any]]) -> None:
        try:
            cache_key = self._generate_cache_key("popular_searches:", "list")
            cache.set(cache_key, popular_list, self.popular_searches_cache_timeout)
            logger.debug(f"Cached popular searches")
            
        except Exception as e:
            logger.warning(f"Failed to set popular searches cache: {str(e)}")
    
    def get_categories(self) -> Optional[List[str]]:
        try:
            cache_key = self._generate_cache_key("categories:", "list")
            cached_categories = cache.get(cache_key)
            
            if cached_categories:
                logger.debug(f"Cache hit for categories")
                return cached_categories
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get categories cache: {str(e)}")
            return None
    
    def set_categories(self, categories: List[str]) -> None:
        try:
            cache_key = self._generate_cache_key("categories:", "list")
            cache.set(cache_key, categories, self.category_cache_timeout)
            logger.debug(f"Cached categories")
            
        except Exception as e:
            logger.warning(f"Failed to set categories cache: {str(e)}")
    
    def clear_search_cache(self) -> None:
        try:
            logger.info("Search cache clear requested")
            
        except Exception as e:
            logger.warning(f"Failed to clear search cache: {str(e)}")
    
    def invalidate_cache(self, cache_type: str = None) -> None:
        try:
            if cache_type == 'popular':
                cache.delete(self._generate_cache_key("popular_searches:", "list"))
            elif cache_type == 'categories':
                cache.delete(self._generate_cache_key("categories:", "list"))
            elif cache_type is None:
                cache.clear()
                
            logger.info(f"Cache invalidated: {cache_type or 'all'}")
            
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {str(e)}")


def cache_result(cache_key_func, timeout=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cache_key = cache_key_func(*args, **kwargs)
                
                result = cache.get(cache_key)
                if result is not None:
                    logger.debug(f"Cache hit for function {func.__name__}: {cache_key}")
                    return result
                
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                
                logger.debug(f"Cached result for function {func.__name__}: {cache_key}")
                return result
                
            except Exception as e:
                logger.error(f"Cache decorator error for {func.__name__}: {str(e)}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator