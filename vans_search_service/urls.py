"""
URL configuration for vans_search_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Swagger 스키마 설정
schema_view = get_schema_view(
    openapi.Info(
        title="VansDevBlog Search Service API",
        default_version="v1.0.0",
        description="""
        VansDevBlog Django-Elasticsearch 검색 서비스 API
        
        ## 주요 기능
        - **고성능 검색**: Elasticsearch + Nori 한국어 분석기
        - **계층적 필터링**: Theme → Category → Tags
        - **다국어 지원**: 한국어/영어 동시 검색
        - **실시간 자동완성**: 검색어 제안
        - **인기 검색어**: 통계 기반 추천
        
        ## 필터 계층구조
        ```
        Theme (상위) → Category (하위) → Tags (세부)
        ├── algorithm → introduction → [Java, Algorithm]
        ├── web → frontend/backend → [React, Django] 
        └── database → nosql/sql → [MongoDB, MySQL]
        ```
        
        ## 사용 예시
        - 기본 검색: `/posts/?query=Django`
        - 테마 필터: `/posts/?theme=algorithm&query=정렬`
        - 복합 필터: `/posts/?theme=web&category=frontend&tags=React`
        """,
        terms_of_service="https://vansdevblog.online/terms/",
        contact=openapi.Contact(
            name="VansDevBlog Support",
            email="contact@vansdevblog.online",
            url="https://vansdevblog.online",
        ),
        license=openapi.License(
            name="MIT License", url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API 엔드포인트
    path("api/v1/search/", include("search.urls")),
    # Swagger 문서화
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # API 루트
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="api-root"),
]
