"""
VansDevBlog Search Service URL Configuration

검색 서비스 관련 URL 패턴을 정의합니다.
새로운 구조에서는 API 레이어로 라우팅을 위임합니다.
"""

from django.urls import path, include

app_name = 'search'

urlpatterns = [
    # API 레이어로 모든 요청 위임
    path('', include('search.api.urls')),
]
