"""
테스트용 URL 설정

admin 없이 최소한의 URL만 포함
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/search/", include("search.api.urls")),
    path("api/kis/", include("kis.urls")),
]
