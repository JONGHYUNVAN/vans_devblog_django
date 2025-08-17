"""
VansDevBlog Search Service Views

Django-Elasticsearch 기반 검색 서비스의 뷰를 정의합니다.
"""

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Dict, Any, List
import logging
import math

from .serializers import (
    SearchRequestSerializer, SearchResponseSerializer,
    AutocompleteRequestSerializer, AutocompleteResponseSerializer,
    PopularSearchesResponseSerializer
)
from .utils.elasticsearch_client import ElasticsearchClient
from .utils.cache_utils import CacheManager

logger = logging.getLogger('search')


@swagger_auto_schema(
    method='get',
    operation_summary="서비스 상태 확인",
    operation_description="검색 서비스가 정상적으로 작동하는지 확인합니다.",
    responses={
        200: openapi.Response(
            description="서비스 정상",
            examples={
                "application/json": {
                    "status": "healthy",
                    "service": "VansDevBlog Search Service",
                    "version": "1.0.0",
                    "elasticsearch_connected": True
                }
            }
        )
    },
    tags=['Health Check']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    서비스 상태를 확인하는 헬스체크 엔드포인트입니다.
    
    Returns:
        JsonResponse: 서비스 상태 정보
            - status (str): 서비스 상태 ("healthy" 또는 "unhealthy")
            - service (str): 서비스 이름
            - version (str): 서비스 버전
            - elasticsearch_connected (bool): Elasticsearch 연결 상태
    
    Example:
        >>> response = health_check(request)
        >>> print(response.content)
        {"status": "healthy", "service": "VansDevBlog Search Service", ...}
    """
    try:
        # TODO: Elasticsearch 연결 상태 확인
        elasticsearch_connected = True
        
        logger.info("Health check requested - Service is healthy")
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'VansDevBlog Search Service',
            'version': '1.0.0',
            'elasticsearch_connected': elasticsearch_connected,
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'service': 'VansDevBlog Search Service',
            'version': '1.0.0',
            'elasticsearch_connected': False,
            'error': str(e)
        }, status=500)


@swagger_auto_schema(
    method='get',
    operation_summary="게시물 검색",
    operation_description="키워드, 카테고리, 태그 등을 기반으로 게시물을 검색합니다.",
    query_serializer=SearchRequestSerializer,
    responses={
        200: SearchResponseSerializer,
        400: openapi.Response(description="잘못된 요청"),
        500: openapi.Response(description="서버 오류")
    },
    tags=['Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_posts(request):
    """
    게시물을 검색하는 API 엔드포인트입니다.
    
    이 API는 Elasticsearch를 사용하여 게시물을 검색하며,
    키워드, 카테고리, 태그, 날짜 등 다양한 필터를 지원합니다.
    
    Query Parameters:
        query (str): 검색할 키워드
        category (str): 카테고리 필터
        tags (str): 태그 필터 (쉼표로 구분)
        language (str): 언어 필터 (ko, en, all)
        date_from (datetime): 검색 시작 날짜
        date_to (datetime): 검색 종료 날짜
        page (int): 페이지 번호 (기본값: 1)
        page_size (int): 페이지 크기 (기본값: 20)
        sort (str): 정렬 방식 (relevance, date_desc, date_asc, views_desc, likes_desc)
        
    Returns:
        Response: 검색 결과
            - total (int): 전체 결과 수
            - page (int): 현재 페이지
            - page_size (int): 페이지 크기
            - total_pages (int): 전체 페이지 수
            - results (List[Dict]): 검색 결과 목록
            - aggregations (Dict): 집계 정보
            
    Example:
        >>> GET /api/v1/search/posts/?query=Django&category=Backend&page=1
        {
            "total": 25,
            "page": 1,
            "page_size": 20,
            "total_pages": 2,
            "results": [
                {
                    "id": "507f1f77bcf86cd799439011",
                    "score": 1.5,
                    "source": {
                        "title": "Django REST Framework Tutorial",
                        "content": "...",
                        "category": "Backend",
                        "tags": ["Django", "REST", "API"]
                    },
                    "highlight": {
                        "title": ["<em>Django</em> REST Framework Tutorial"]
                    }
                }
            ],
            "aggregations": {
                "categories": {...},
                "tags": {...}
            }
        }
    """
    try:
        # 요청 데이터 검증
        serializer = SearchRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f"Invalid search request: {serializer.errors}")
            return Response({
                'error': 'Invalid request parameters',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # 검색 파라미터 추출
        query = validated_data.get('query', '')
        category = validated_data.get('category', '')
        tags = validated_data.get('tags', [])
        language = validated_data.get('language', 'all')
        date_from = validated_data.get('date_from')
        date_to = validated_data.get('date_to')
        page = validated_data.get('page', 1)
        page_size = validated_data.get('page_size', 20)
        sort_option = validated_data.get('sort', 'relevance')
        
        # 캐시 확인
        cache_manager = CacheManager()
        filters = {
            'category': category,
            'tags': tags,
            'language': language if language != 'all' else None,
            'date_range': {}
        }
        
        if date_from:
            filters['date_range']['start'] = date_from
        if date_to:
            filters['date_range']['end'] = date_to
        
        # 빈 날짜 범위 제거
        if not filters['date_range']:
            filters.pop('date_range')
        
        cached_result = cache_manager.get_search_result(query, filters, page, page_size)
        if cached_result:
            logger.debug(f"Cache hit for search: '{query}'")
            return Response(cached_result)
        
        # Elasticsearch 검색 수행
        es_client = ElasticsearchClient()
        
        # 정렬 옵션 변환
        sort_mapping = {
            'relevance': [{"_score": {"order": "desc"}}, {"published_date": {"order": "desc"}}],
            'date_desc': [{"published_date": {"order": "desc"}}],
            'date_asc': [{"published_date": {"order": "asc"}}],
            'views_desc': [{"view_count": {"order": "desc"}}],
            'likes_desc': [{"like_count": {"order": "desc"}}]
        }
        sort_params = sort_mapping.get(sort_option, sort_mapping['relevance'])
        
        # 검색 실행
        search_result = es_client.search_posts(
            query=query,
            filters=filters,
            page=page,
            page_size=page_size,
            sort=sort_params
        )
        
        # 응답 데이터 구성
        total = search_result['total']
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        response_data = {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': search_result['hits'],
            'aggregations': search_result.get('aggregations', {})
        }
        
        # 결과 캐시 저장
        cache_manager.set_search_result(query, filters, page, page_size, response_data)
        
        logger.info(f"Search completed: query='{query}', total={total}, page={page}")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        return Response({
            'error': 'Search request failed',
            'message': 'An error occurred while processing your search request. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_summary="자동완성 제안",
    operation_description="검색어 입력 중 자동완성 제안을 제공합니다.",
    query_serializer=AutocompleteRequestSerializer,
    responses={
        200: AutocompleteResponseSerializer,
        400: openapi.Response(description="잘못된 요청"),
        500: openapi.Response(description="서버 오류")
    },
    tags=['Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def autocomplete(request):
    """
    검색어 자동완성 제안을 제공하는 API 엔드포인트입니다.
    
    사용자가 검색어를 입력하는 동안 실시간으로 관련 제안을 제공합니다.
    
    Query Parameters:
        query (str): 자동완성할 검색어 (1글자 이상)
        language (str): 언어 필터 (ko, en, all) - 기본값: all
        limit (int): 반환할 제안 수 (1-20) - 기본값: 10
        
    Returns:
        Response: 자동완성 제안 목록
            - suggestions (List[str]): 제안 목록
            - query (str): 원본 검색어
            
    Example:
        >>> GET /api/v1/search/autocomplete/?query=Djan&limit=5
        {
            "suggestions": [
                "Django",
                "Django REST Framework",
                "Django Tutorial",
                "Django ORM",
                "Django Authentication"
            ],
            "query": "Djan"
        }
    """
    try:
        # 요청 데이터 검증
        serializer = AutocompleteRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f"Invalid autocomplete request: {serializer.errors}")
            return Response({
                'error': 'Invalid request parameters',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        query = validated_data.get('query', '')
        language = validated_data.get('language', 'all')
        limit = validated_data.get('limit', 10)
        
        # 캐시 확인
        cache_manager = CacheManager()
        cached_suggestions = cache_manager.get_autocomplete_suggestions(query, language)
        if cached_suggestions:
            logger.debug(f"Autocomplete cache hit for: '{query}'")
            return Response({
                'suggestions': cached_suggestions[:limit],
                'query': query
            })
        
        # Elasticsearch 자동완성 검색
        es_client = ElasticsearchClient()
        suggestions = es_client.get_autocomplete_suggestions(
            prefix=query,
            language=language if language != 'all' else 'ko',
            size=limit
        )
        
        # 캐시 저장
        cache_manager.set_autocomplete_suggestions(query, language, suggestions)
        
        response_data = {
            'suggestions': suggestions,
            'query': query
        }
        
        logger.debug(f"Autocomplete completed: query='{query}', suggestions={len(suggestions)}")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Autocomplete failed: {str(e)}", exc_info=True)
        return Response({
            'error': 'Autocomplete request failed',
            'message': 'An error occurred while getting suggestions. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_summary="인기 검색어",
    operation_description="인기 검색어 목록을 제공합니다.",
    responses={
        200: PopularSearchesResponseSerializer,
        500: openapi.Response(description="서버 오류")
    },
    tags=['Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_searches(request):
    """
    인기 검색어 목록을 제공하는 API 엔드포인트입니다.
    
    최근 검색 빈도가 높은 검색어들을 제공합니다.
    
    Returns:
        Response: 인기 검색어 목록
            - popular_searches (List[Dict]): 인기 검색어 목록
                각 항목은 query(검색어)와 count(검색 횟수)를 포함
                
    Example:
        >>> GET /api/v1/search/popular/
        {
            "popular_searches": [
                {"query": "Django", "count": 150},
                {"query": "Python", "count": 120},
                {"query": "REST API", "count": 95},
                {"query": "Elasticsearch", "count": 80}
            ]
        }
    """
    try:
        # 캐시 확인
        cache_manager = CacheManager()
        cached_popular = cache_manager.get_popular_searches()
        if cached_popular:
            logger.debug("Popular searches cache hit")
            return Response({'popular_searches': cached_popular})
        
        # Elasticsearch에서 인기 검색어 조회
        es_client = ElasticsearchClient()
        popular_list = es_client.get_popular_searches(limit=10)
        
        # 캐시 저장
        cache_manager.set_popular_searches(popular_list)
        
        response_data = {'popular_searches': popular_list}
        
        logger.debug(f"Popular searches completed: {len(popular_list)} items")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Popular searches failed: {str(e)}", exc_info=True)
        return Response({
            'error': 'Popular searches request failed',
            'message': 'An error occurred while getting popular searches. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_summary="카테고리 목록",
    operation_description="사용 가능한 모든 카테고리 목록을 제공합니다.",
    responses={
        200: openapi.Response(
            description="카테고리 목록",
            examples={
                "application/json": {
                    "categories": ["Frontend", "Backend", "Database", "DevOps"]
                }
            }
        ),
        500: openapi.Response(description="서버 오류")
    },
    tags=['Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """
    사용 가능한 모든 카테고리 목록을 제공하는 API 엔드포인트입니다.
    
    Returns:
        Response: 카테고리 목록
            - categories (List[str]): 카테고리 이름 목록
            
    Example:
        >>> GET /api/v1/search/categories/
        {
            "categories": [
                "Frontend",
                "Backend", 
                "Database",
                "DevOps",
                "AI/ML"
            ]
        }
    """
    try:
        # 캐시 확인
        cache_manager = CacheManager()
        cached_categories = cache_manager.get_categories()
        if cached_categories:
            logger.debug("Categories cache hit")
            return Response({'categories': cached_categories})
        
        # TODO: MongoDB에서 카테고리 조회 (현재는 더미 데이터)
        categories = [
            "Frontend",
            "Backend", 
            "Database",
            "DevOps",
            "AI/ML",
            "Mobile",
            "Security",
            "Testing"
        ]
        
        # 캐시 저장
        cache_manager.set_categories(categories)
        
        response_data = {'categories': categories}
        
        logger.debug(f"Categories completed: {len(categories)} items")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Get categories failed: {str(e)}", exc_info=True)
        return Response({
            'error': 'Categories request failed',
            'message': 'An error occurred while getting categories. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
