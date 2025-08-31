"""
CloudType.io 테스트용 간단한 헬스체크
"""

from django.http import JsonResponse
from django.urls import path


def health_check(request):
    return JsonResponse({"status": "ok", "message": "CloudType.io deployment test"})


urlpatterns = [
    path("health/", health_check, name="health"),
]




