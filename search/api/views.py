"""
VansDevBlog Search Service API Views

API 엔드포인트를 정의하고 HTTP 요청/응답을 처리합니다.
비즈니스 로직은 서비스 레이어로 위임합니다.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .serializers import (
    SearchRequestSerializer, SearchResponseSerializer,
    AutocompleteRequestSerializer, AutocompleteResponseSerializer,
    PopularSearchesResponseSerializer
)
from ..services.search_service import SearchService
from ..services.health_service import HealthService

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
        Response: 서비스 상태 정보
    """
    try:
        health_service = HealthService()
        health_data = health_service.get_health_status()
        
        return Response(health_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'status': 'unhealthy',
            'service': 'VansDevBlog Search Service',
            'version': '1.0.0',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_summary="게시물 검색",
    operation_description="키워드, 테마, 카테고리, 태그 등을 기반으로 게시물을 검색합니다.",
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
    """게시물을 검색하는 API 엔드포인트입니다."""
    try:
        # 요청 데이터 검증
        serializer = SearchRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f"Invalid search request: {serializer.errors}")
            return Response({
                'error': 'Invalid request parameters',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 서비스 레이어로 위임
        search_service = SearchService()
        search_result = search_service.search_posts(serializer.validated_data)
        
        logger.info(f"Search completed: query='{serializer.validated_data.get('query', '')}', total={search_result['total']}")
        return Response(search_result, status=status.HTTP_200_OK)
        
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
    """검색어 자동완성 제안을 제공하는 API 엔드포인트입니다."""
    try:
        # 요청 데이터 검증
        serializer = AutocompleteRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f"Invalid autocomplete request: {serializer.errors}")
            return Response({
                'error': 'Invalid request parameters',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 서비스 레이어로 위임
        search_service = SearchService()
        suggestions = search_service.get_autocomplete_suggestions(serializer.validated_data)
        
        logger.debug(f"Autocomplete completed: query='{serializer.validated_data.get('query', '')}', suggestions={len(suggestions['suggestions'])}")
        return Response(suggestions, status=status.HTTP_200_OK)
        
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
    """인기 검색어 목록을 제공하는 API 엔드포인트입니다."""
    try:
        search_service = SearchService()
        popular_list = search_service.get_popular_searches()
        
        logger.debug(f"Popular searches completed: {len(popular_list['popular_searches'])} items")
        return Response(popular_list, status=status.HTTP_200_OK)
        
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
    """사용 가능한 모든 카테고리 목록을 제공하는 API 엔드포인트입니다."""
    try:
        search_service = SearchService()
        categories = search_service.get_categories()
        
        logger.debug(f"Categories completed: {len(categories['categories'])} items")
        return Response(categories, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get categories failed: {str(e)}", exc_info=True)
        return Response({
            'error': 'Categories request failed',
            'message': 'An error occurred while getting categories. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

