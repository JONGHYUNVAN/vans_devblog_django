"""
VansDevBlog Search Service API Views

API 엔드포인트를 정의하고 HTTP 요청/응답을 처리합니다.
비즈니스 로직은 서비스 레이어로 위임합니다.
"""

import logging
import time
from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..services.health_service import HealthService
from ..services.search_service import SearchService
from ..services.sync_service import SyncService
from .serializers import (
    AutocompleteRequestSerializer,
    AutocompleteResponseSerializer,
    PopularSearchesResponseSerializer,
    SearchRequestSerializer,
    SearchResponseSerializer,
    SyncRequestSerializer,
    SyncResponseSerializer,
    SyncStatusSerializer,
)

logger = logging.getLogger("search")

# API 로깅 데코레이터
def api_logger(func):
    """API 호출 로깅 데코레이터"""
    def wrapper(*args, **kwargs):
        request = args[0]  # request 객체
        start_time = time.time()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 요청 정보 로깅 (이모지 제거)
        logger.info(f"[API 요청 시작] {func.__name__}")
        logger.info(f"[시간] {timestamp}")
        logger.info(f"[메서드] {request.method}")
        logger.info(f"[경로] {request.path}")
        logger.info(f"[쿼리] {dict(request.GET)}")
        logger.info(f"[데이터] {getattr(request, 'data', {})}")
        logger.info(f"[IP] {request.META.get('REMOTE_ADDR', 'Unknown')}")
        logger.info(f"[User-Agent] {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}")
        
        try:
            # API 함수 실행
            response = func(*args, **kwargs)
            
            # 응답 정보 로깅 (이모지 제거)
            execution_time = time.time() - start_time
            logger.info(f"[API 응답 성공] {func.__name__}")
            logger.info(f"[상태 코드] {response.status_code}")
            logger.info(f"[실행 시간] {execution_time:.3f}초")
            
            if hasattr(response, 'data') and isinstance(response.data, dict):
                if 'count' in response.data:
                    logger.info(f"[결과 수] {response.data['count']}")
                if 'results' in response.data:
                    logger.info(f"[반환 항목] {len(response.data['results'])}개")
            
            return response
            
        except Exception as e:
            # 에러 정보 로깅 (이모지 제거)
            execution_time = time.time() - start_time
            logger.error(f"[API 에러 발생] {func.__name__}")
            logger.error(f"[에러] {str(e)}")
            logger.error(f"[실행 시간] {execution_time:.3f}초")
            logger.error(f"[에러 타입] {type(e).__name__}")
            
            # 에러 응답 반환
            return Response(
                {
                    "error": "search request failed",
                    "message": "An error occurred while processing your search request. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return wrapper


# 헬스체크 전용 경량 로거 (로그 최소화)
def health_logger(func):
    """헬스체크 전용 경량 로깅 데코레이터 - 에러 시에만 로깅"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            # API 함수 실행
            response = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 에러 시에만 로깅 (성공은 완전히 무시)
            if response.status_code != 200:
                logger.warning(f"헬스체크 실패 - 상태코드: {response.status_code}, 실행시간: {execution_time:.3f}초")
            # 성공 시에는 아무 로그도 남기지 않음
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"헬스체크 에러 - {str(e)}, 실행시간: {execution_time:.3f}초")
            
            # 에러 응답 반환
            return Response(
                {
                    "status": "unhealthy",
                    "service": "VansDevBlog Search Service",
                    "version": "1.0.0",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    return wrapper


@swagger_auto_schema(
    method="get",
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
                    "elasticsearch_connected": True,
                }
            },
        )
    },
    tags=["Health Check"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@health_logger  
def health_check(request):
    """
    서비스 상태를 확인하는 헬스체크 엔드포인트입니다.
    결과를 30분간 캐시하여 과도한 체크를 방지합니다.

    Returns:
        Response: 서비스 상태 정보
    """
    from django.core.cache import cache
    from datetime import datetime
    
    # 캐시 키
    cache_key = "health_check_result"
    cache_timeout = 1800  # 30분 (1800초)
    
    # 캐시된 결과 확인
    cached_result = cache.get(cache_key)
    if cached_result:
        # 캐시된 결과에 타임스탬프 추가 (딕셔너리 복사해서 수정)
        response_data = cached_result.copy()
        response_data['cached'] = True
        response_data['last_check'] = cache.get('health_check_timestamp', 'unknown')
        return Response(response_data, status=status.HTTP_200_OK)
    
    try:
        # 실제 헬스체크 수행
        health_service = HealthService()
        health_data = health_service.get_health_status()
        
        # 타임스탬프 추가
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        health_data['cached'] = False
        health_data['last_check'] = current_time
        
        # 결과 캐시에 저장
        cache.set(cache_key, health_data, cache_timeout)
        cache.set('health_check_timestamp', current_time, cache_timeout)
        
        return Response(health_data, status=status.HTTP_200_OK)

    except Exception as e:
        # 에러 로깅은 health_logger 데코레이터에서 처리됨
        error_response = {
            "status": "unhealthy",
            "service": "VansDevBlog Search Service",
            "version": "1.0.0",
            "error": str(e),
            "cached": False,
            "last_check": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    operation_summary="게시물 검색",
    operation_description="키워드, 테마, 카테고리, 태그 등을 기반으로 게시물을 검색합니다.",
    query_serializer=SearchRequestSerializer,
    responses={
        200: SearchResponseSerializer,
        400: openapi.Response(description="잘못된 요청"),
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Search"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@api_logger
def search_posts(request):
    """게시물을 검색하는 API 엔드포인트입니다."""
    try:
        # 요청 데이터 검증
        serializer = SearchRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f"Invalid search request: {serializer.errors}")
            return Response(
                {"error": "Invalid request parameters", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 서비스 레이어로 위임
        search_service = SearchService()
        search_result = search_service.search_posts(serializer.validated_data)

        logger.info(
            f"Search completed: query='{serializer.validated_data.get('query', '')}', total={search_result['total']}"
        )
        return Response(search_result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Search request failed",
                "message": "An error occurred while processing your search request. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="get",
    operation_summary="자동완성 제안",
    operation_description="검색어 입력 중 자동완성 제안을 제공합니다.",
    query_serializer=AutocompleteRequestSerializer,
    responses={
        200: AutocompleteResponseSerializer,
        400: openapi.Response(description="잘못된 요청"),
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Search"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@api_logger
def autocomplete(request):
    """검색어 자동완성 제안을 제공하는 API 엔드포인트입니다."""
    try:
        # 요청 데이터 검증
        serializer = AutocompleteRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.warning(f"Invalid autocomplete request: {serializer.errors}")
            return Response(
                {"error": "Invalid request parameters", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 서비스 레이어로 위임
        search_service = SearchService()
        suggestions = search_service.get_autocomplete_suggestions(
            serializer.validated_data
        )

        logger.debug(
            f"Autocomplete completed: query='{serializer.validated_data.get('query', '')}', suggestions={len(suggestions['suggestions'])}"
        )
        return Response(suggestions, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Autocomplete failed: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Autocomplete request failed",
                "message": "An error occurred while getting suggestions. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="get",
    operation_summary="인기 검색어",
    operation_description="인기 검색어 목록을 제공합니다.",
    responses={
        200: PopularSearchesResponseSerializer,
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Search"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@api_logger
def popular_searches(request):
    """인기 검색어 목록을 제공하는 API 엔드포인트입니다."""
    try:
        search_service = SearchService()
        popular_list = search_service.get_popular_searches()

        logger.debug(
            f"Popular searches completed: {len(popular_list['popular_searches'])} items"
        )
        return Response(popular_list, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Popular searches failed: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Popular searches request failed",
                "message": "An error occurred while getting popular searches. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="get",
    operation_summary="카테고리 목록",
    operation_description="사용 가능한 모든 카테고리 목록을 제공합니다.",
    responses={
        200: openapi.Response(
            description="카테고리 목록",
            examples={
                "application/json": {
                    "categories": ["Frontend", "Backend", "Database", "DevOps"]
                }
            },
        ),
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Search"],
)
@api_view(["GET"])
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
        return Response(
            {
                "error": "Categories request failed",
                "message": "An error occurred while getting categories. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="get",
    operation_summary="동기화 상태 조회",
    operation_description="MongoDB와 Elasticsearch 간의 데이터 동기화 상태를 조회합니다.",
    responses={
        200: SyncStatusSerializer,
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Data Sync"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@api_logger
def sync_status(request):
    """동기화 상태를 조회하는 API 엔드포인트입니다."""
    try:
        sync_service = SyncService()
        status_data = sync_service.get_sync_status()

        logger.info(f"Sync status retrieved: {status_data}")
        return Response(status_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Sync status failed: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Sync status request failed",
                "message": "동기화 상태 조회 중 오류가 발생했습니다. 다시 시도해주세요.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="post",
    operation_summary="데이터 동기화 실행",
    operation_description="MongoDB에서 Elasticsearch로 게시물 데이터를 동기화합니다.",
    request_body=SyncRequestSerializer,
    responses={
        200: SyncResponseSerializer,
        400: openapi.Response(description="잘못된 요청"),
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Data Sync"],
)
@api_view(["POST"])
@permission_classes([AllowAny])  # 실제로는 관리자 권한 필요할 수 있음
@api_logger
def sync_data(request):
    """MongoDB에서 Elasticsearch로 데이터를 동기화하는 API 엔드포인트입니다."""
    try:
        # 요청 데이터 검증
        serializer = SyncRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid sync request: {serializer.errors}")
            return Response(
                {"error": "Invalid request parameters", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 동기화 실행
        sync_service = SyncService()
        sync_result = sync_service.sync_data(serializer.validated_data)

        logger.info(f"Sync completed: {sync_result}")

        # 응답 상태 결정
        if sync_result["status"] == "completed":
            response_status = status.HTTP_200_OK
        elif sync_result["status"] == "partial":
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(sync_result, status=response_status)

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Sync request failed",
                "message": "데이터 동기화 중 오류가 발생했습니다. 다시 시도해주세요.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="post",
    operation_summary="전체 데이터 동기화",
    operation_description="MongoDB의 모든 발행된 게시물을 Elasticsearch로 동기화합니다.",
    responses={
        200: SyncResponseSerializer,
        500: openapi.Response(description="서버 오류"),
    },
    tags=["Data Sync"],
)
@api_view(["POST"])
@permission_classes([AllowAny])  # 실제로는 관리자 권한 필요할 수 있음
@api_logger
def sync_all_data(request):
    """모든 데이터를 동기화하는 간편한 API 엔드포인트입니다."""
    try:
        # 전체 동기화 옵션 (is_published 필드가 없으므로 모든 게시물 동기화)
        sync_options = {
            "batch_size": 50,
            "force_all": True,  # 모든 게시물 동기화
            "incremental": False,
            "days": 7,
            "clear_existing": False,
            "dry_run": False,
        }

        # 동기화 실행
        sync_service = SyncService()
        sync_result = sync_service.sync_data(sync_options)

        logger.info(f"Full sync completed: {sync_result}")

        # 응답 상태 결정
        if sync_result["status"] == "completed":
            response_status = status.HTTP_200_OK
        elif sync_result["status"] == "partial":
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(sync_result, status=response_status)

    except Exception as e:
        logger.error(f"Full sync failed: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Full sync request failed",
                "message": "전체 데이터 동기화 중 오류가 발생했습니다. 다시 시도해주세요.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
