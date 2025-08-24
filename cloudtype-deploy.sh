#!/bin/bash
# =============================================================================
# CloudType.io 배포 스크립트
# =============================================================================

echo "🚀 Starting CloudType.io deployment..."

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=vans_search_service.settings.cloudtype

# 데이터베이스 마이그레이션
echo "📦 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 정적 파일 수집
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Elasticsearch 인덱스 생성 (선택사항)
echo "🔍 Creating search indexes..."
python manage.py create_search_indexes || echo "⚠️  Elasticsearch not available, skipping index creation"

# 슈퍼유저 생성 (환경 변수가 있는 경우)
if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput || echo "⚠️  Superuser already exists"
fi

echo "✅ Deployment preparation completed!"


