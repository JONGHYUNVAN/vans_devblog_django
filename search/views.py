"""
VansDevBlog Search Service Views

Django-Elasticsearch 기반 검색 서비스의 뷰를 정의합니다.
"""

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

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
