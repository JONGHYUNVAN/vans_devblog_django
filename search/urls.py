"""
VansDevBlog Search Service URL Configuration

검색 서비스 관련 URL 패턴을 정의합니다.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router 설정
router = DefaultRouter()
# router.register(r'posts', views.PostSearchViewSet, basename='post-search')

app_name = 'search'

urlpatterns = [
    # DRF Router URLs
    path('', include(router.urls)),
    
    # 직접 정의된 URL 패턴들
    path('health/', views.health_check, name='health-check'),
    # path('posts/', views.PostSearchView.as_view(), name='post-search'),
    # path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    # path('popular/', views.PopularSearchesView.as_view(), name='popular-searches'),
]
