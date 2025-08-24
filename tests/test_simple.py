"""
Simple Test

기본적인 테스트 설정을 검증합니다.
"""

import pytest
from django.conf import settings
from django.test import TestCase


class TestSimple(TestCase):
    """간단한 테스트"""

    def test_django_settings(self):
        """Django 설정 테스트"""
        # 설정 확인 (DEBUG는 base에서 False로 설정됨)
        # self.assertTrue(settings.DEBUG)  # base에서 False로 설정되어 있음
        self.assertIn("testserver", settings.ALLOWED_HOSTS)
        # SQLite 메모리 DB 사용 확인
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3"
        )

    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)


@pytest.mark.django_db
def test_simple_pytest():
    """Pytest 기본 테스트"""
    assert 1 + 1 == 2


@pytest.mark.django_db
def test_django_model_creation():
    """Django 모델 생성 테스트"""
    from search.models import SearchLog

    log = SearchLog.objects.create(query="test query", results_count=5)

    assert log.id is not None
    assert log.query == "test query"
    assert log.results_count == 5
