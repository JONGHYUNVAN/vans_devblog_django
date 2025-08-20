"""
VansDevBlog Search Service Django Settings

환경별 설정을 로드하는 패키지입니다.
DJANGO_SETTINGS_MODULE 환경변수에 따라 적절한 설정을 로드합니다.

사용법:
    export DJANGO_SETTINGS_MODULE=vans_search_service.settings.development
    export DJANGO_SETTINGS_MODULE=vans_search_service.settings.production
    export DJANGO_SETTINGS_MODULE=vans_search_service.settings.testing
"""

import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name: str, default: str = None) -> str:
    """
    환경변수를 가져오는 헬퍼 함수입니다.
    
    Args:
        var_name (str): 환경변수 이름
        default (str, optional): 기본값
        
    Returns:
        str: 환경변수 값
        
    Raises:
        ImproperlyConfigured: 필수 환경변수가 설정되지 않은 경우
    """
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

