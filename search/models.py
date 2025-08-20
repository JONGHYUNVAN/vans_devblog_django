from django.db import models
from django.utils import timezone
from typing import List, Dict, Any
import logging

logger = logging.getLogger('search')


class SearchLog(models.Model):
    user_id = models.BigIntegerField(
        null=True, 
        blank=True,
        help_text="검색을 수행한 사용자 ID (인증된 사용자)"
    )
    query = models.CharField(
        max_length=255,
        db_index=True,
        help_text="사용자가 검색한 쿼리 문자열"
    )
    results_count = models.IntegerField(
        default=0,
        help_text="해당 검색 쿼리로 반환된 결과 수"
    )
    clicked_result_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="검색 결과 중 사용자가 클릭한 게시물의 ID"
    )
    search_time = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="검색이 수행된 시간"
    )
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="검색 응답 시간 (밀리초)"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="검색을 수행한 사용자의 IP 주소"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="검색을 수행한 사용자의 User-Agent 문자열"
    )
    
    class Meta:
        verbose_name = "검색 로그"
        verbose_name_plural = "검색 로그"
        ordering = ['-search_time']
    
    def __str__(self):
        return f"[{self.search_time.strftime('%Y-%m-%d %H:%M:%S')}] Query: '{self.query}' ({self.results_count} results)"
    
    @classmethod
    def record_log(cls, query: str, results_count: int, user_id: int = None, 
                   clicked_result_id: str = None, response_time_ms: int = None,
                   ip_address: str = None, user_agent: str = None) -> 'SearchLog':
        try:
            log = cls.objects.create(
                user_id=user_id,
                query=query,
                results_count=results_count,
                clicked_result_id=clicked_result_id,
                response_time_ms=response_time_ms,
                ip_address=ip_address,
                user_agent=user_agent
            )
            logger.info(f"Search log recorded: Query='{query}', Results={results_count}")
            return log
        except Exception as e:
            logger.error(f"Failed to record search log for query '{query}': {str(e)}")
            raise


class PopularSearch(models.Model):
    query = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="인기 검색어 문자열"
    )
    search_count = models.IntegerField(
        default=1,
        help_text="해당 검색어의 총 검색 횟수"
    )
    last_searched = models.DateTimeField(
        default=timezone.now,
        help_text="마지막으로 검색된 시간"
    )
    
    class Meta:
        verbose_name = "인기 검색어"
        verbose_name_plural = "인기 검색어"
        ordering = ['-search_count', '-last_searched']
    
    def __str__(self):
        return f"Query: '{self.query}' (Count: {self.search_count})"
    
    @classmethod
    def update_popular_search(cls, query: str) -> 'PopularSearch':
        try:
            popular_search, created = cls.objects.get_or_create(
                query=query,
                defaults={'search_count': 1}
            )
            if not created:
                popular_search.search_count += 1
                popular_search.last_searched = timezone.now()
                popular_search.save()
            
            logger.info(f"Popular search updated/created: Query='{query}', Count={popular_search.search_count}")
            return popular_search
        except Exception as e:
            logger.error(f"Failed to update popular search for query '{query}': {str(e)}")
            raise
    
    @classmethod
    def get_top_popular_searches(cls, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            top_searches = cls.objects.order_by('-search_count', '-last_searched')[:limit]
            return [{'query': ps.query, 'count': ps.search_count} for ps in top_searches]
        except Exception as e:
            logger.error(f"Failed to get top popular searches: {str(e)}")
            return []