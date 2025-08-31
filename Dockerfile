# CloudType.io Django Dockerfile
FROM cloudtype/python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# Node.js 버전 확인 (필요시)
RUN node -v && npm -v

# Gunicorn 설치
RUN pip install gunicorn

# requirements 파일 복사
COPY requirements-cloudtype.txt ./
COPY requirements/ ./requirements/

# 패키지 설치
RUN pip install -r requirements-cloudtype.txt

# 프로젝트 파일 복사
COPY . .

# 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["gunicorn", "vans_search_service.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
