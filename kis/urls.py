from django.urls import path

from . import views

app_name = "kis"

urlpatterns = [
    path("snapshot/<str:symbol>/", views.snapshot, name="snapshot"),
    path("stream/<str:symbol>/", views.stream, name="stream"),
]
