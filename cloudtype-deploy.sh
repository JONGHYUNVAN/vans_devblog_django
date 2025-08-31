#!/bin/bash
# =============================================================================
# CloudType.io 배포 스크립트
# =============================================================================

set -e  # 오류 발생시 스크립트 중단

echo "🚀 Starting CloudType.io deployment..."

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=vans_search_service.settings.cloudtype
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Python 환경 확인
echo "🐍 Python version:"
python --version

# 의존성 설치 확인
echo "📦 Checking dependencies..."
pip list | grep -E "(Django|gunicorn|whitenoise)" || pip install -r requirements-cloudtype.txt

# 데이터베이스 연결 테스트
echo "🗄️  Testing database connection..."
python manage.py check --database default || echo "⚠️  Database connection issue"

# 데이터베이스 마이그레이션
echo "📦 Running database migrations..."
python manage.py makemigrations --dry-run
python manage.py makemigrations
python manage.py migrate --run-syncdb

# 정적 파일 수집
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Elasticsearch 연결 테스트 및 인덱스 생성
echo "🔍 Testing Elasticsearch connection..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings.cloudtype')
import django
django.setup()
try:
    from search.clients.elasticsearch_client import get_elasticsearch_client
    client = get_elasticsearch_client()
    if client.ping():
        print('✅ Elasticsearch connected successfully')
    else:
        print('❌ Elasticsearch connection failed')
except Exception as e:
    print(f'⚠️  Elasticsearch not available: {e}')
"

echo "🔍 Creating search indexes..."
python manage.py create_search_indexes || echo "⚠️  Elasticsearch not available, skipping index creation"

# MongoDB 연결 테스트
echo "🍃 Testing MongoDB connection..."
python manage.py test_mongodb_connection || echo "⚠️  MongoDB not available"

# 슈퍼유저 생성 (환경 변수가 있는 경우)
if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput || echo "⚠️  Superuser already exists"
fi

# 시스템 체크
echo "🔍 Running system checks..."
python manage.py check --deploy

# 헬스체크 테스트
echo "💓 Testing health endpoint..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings.cloudtype')
import django
django.setup()
from django.test import Client
client = Client()
try:
    response = client.get('/api/v1/search/health/')
    if response.status_code == 200:
        print('✅ Health check passed')
    else:
        print(f'❌ Health check failed: {response.status_code}')
except Exception as e:
    print(f'⚠️  Health check error: {e}')
"

echo "✅ Deployment preparation completed!"
echo "🌟 Ready to start with: gunicorn --bind 0.0.0.0:\$PORT vans_search_service.wsgi:application"


