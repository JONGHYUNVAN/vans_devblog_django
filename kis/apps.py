from django.apps import AppConfig


class KisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kis"
    verbose_name = "KIS 실시간 주식 데이터"

    def ready(self):
        # 앱 시작 시 WebSocket 매니저 초기화는 하지 않음
        # 첫 요청 시 lazy 초기화
        pass
