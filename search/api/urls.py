"""
VansDevBlog Search Service API URL Configuration

검색 서비스 관련 API 엔드포인트의 URL 패턴을 정의합니다.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# DRF Router 설정
router = DefaultRouter()
# router.register(r'posts', views.PostSearchViewSet, basename='post-search')

app_name = "search_api"

urlpatterns = [
    # DRF Router URLs
    path("", include(router.urls)),
    # 서비스 상태 확인
    path("health/", views.health_check, name="health-check"),
    # 검색 API
    path("posts/", views.search_posts, name="search-posts"),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
    path("popular/", views.popular_searches, name="popular-searches"),
    path("categories/", views.get_categories, name="get-categories"),
    # 데이터 동기화 API
    path("sync/status/", views.sync_status, name="sync-status"),
    path("sync/", views.sync_data, name="sync-data"),
    path("sync/all/", views.sync_all_data, name="sync-all-data"),
]
