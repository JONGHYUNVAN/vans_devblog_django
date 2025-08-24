"""
테스트용 URL 설정

admin 없이 최소한의 URL만 포함
"""

from django.urls import path, include

urlpatterns = [
    # API 경로만 포함 (admin 제외)
    path('api/v1/search/', include('search.api.urls')),
]

