# CloudType.io 배포 가이드

## 개요

이 문서는 VansDevBlog Search Service를 CloudType.io 플랫폼에 배포하는 방법을 설명합니다.

## 사전 준비

### 1. CloudType.io 계정 준비
- [CloudType.io](https://cloudtype.io/) 회원가입
- GitHub 계정 연동

### 2. 프로젝트 준비
```bash
# 배포용 requirements 파일 확인
cat requirements-cloudtype.txt

# 배포 스크립트 실행 권한 부여
chmod +x cloudtype-deploy.sh
```

## 배포 단계

### 1단계: CloudType.io 프로젝트 생성

1. CloudType.io 대시보드 접속
2. "새 프로젝트" 클릭
3. GitHub 저장소 연결
4. 프레임워크: **Python Django** 선택
5. Python 버전: **3.11** 선택

### 2단계: 환경 변수 설정

CloudType.io 대시보드에서 다음 환경 변수를 설정하세요:

#### 필수 환경 변수
```bash
# Django 설정
DJANGO_SETTINGS_MODULE=vans_search_service.settings.cloudtype
SECRET_KEY=시크릿 키키
DEBUG=False

# 허용 호스트 (CloudType.io 도메인 자동 추가됨)
ALLOWED_HOSTS=허용 호스트트

# 데이터베이스 (CloudType.io에서 제공)
DATABASE_URL=postgresql://user:password@host:port/dbname
```

#### 선택적 환경 변수
```bash
# Elasticsearch (외부 서비스 사용시)
ELASTICSEARCH_HOST=your-es-host
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password

# Redis (캐싱용, 외부 서비스 사용시)
REDIS_URL=redis://user:password@host:port

# MongoDB (메타데이터용, 외부 서비스 사용시)
MONGODB_HOST=your-mongo-host
MONGODB_PORT=27017
MONGODB_DB=vans_search
MONGODB_USERNAME=your-username
MONGODB_PASSWORD=your-password

# 슈퍼유저 자동 생성 (선택사항)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your-admin-password

# 이메일 설정 (선택사항)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yoursite.com
```

### 3단계: 빌드 설정

CloudType.io 프로젝트 설정에서:

1. **빌드 명령어**:
   ```bash
   pip install -r requirements-cloudtype.txt
   ```

2. **시작 전 명령어**:
   ```bash
   python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput
   ```

3. **시작 명령어**:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT vans_search_service.wsgi:application
   ```

### 4단계: 배포 실행

1. "배포" 버튼 클릭
2. 빌드 로그 확인
3. 배포 완료 후 URL 확인

## 외부 서비스 연동

### Elasticsearch 연동

CloudType.io는 Elasticsearch를 직접 제공하지 않으므로 외부 서비스를 사용해야 합니다:

1. **Elastic Cloud** (권장)
   - [Elastic Cloud](https://cloud.elastic.co/) 무료 플랜 사용
   - 클러스터 생성 후 엔드포인트 정보를 환경 변수에 설정

2. **AWS OpenSearch**
   - AWS OpenSearch Service 사용
   - VPC 설정 및 보안 그룹 구성 필요

3. **자체 호스팅**
   - 별도 서버에 Elasticsearch 설치
   - 네트워크 접근 권한 설정

### MongoDB 연동

1. **MongoDB Atlas** (권장)
   - [MongoDB Atlas](https://www.mongodb.com/atlas) 무료 플랜 사용
   - 클러스터 생성 후 연결 문자열을 환경 변수에 설정

2. **자체 호스팅**
   - 별도 서버에 MongoDB 설치

### Redis 연동 (선택사항)

1. **Upstash Redis** (권장)
   - [Upstash](https://upstash.com/) 무료 플랜 사용
   - Redis 인스턴스 생성 후 URL을 환경 변수에 설정

2. **Redis Labs**
   - [Redis Labs](https://redis.com/) 무료 플랜 사용

## 배포 후 확인사항

### 1. 기본 기능 테스트
```bash
# 헬스체크
curl https://your-app.cloudtype.app/api/v1/search/health/

# API 문서 확인
curl https://your-app.cloudtype.app/swagger/
```

### 2. 관리자 페이지 접속
```
https://your-app.cloudtype.app/admin/
```

### 3. 로그 확인
CloudType.io 대시보드에서 애플리케이션 로그를 확인할 수 있습니다.

## 트러블슈팅

### 자주 발생하는 문제

#### 1. ALLOWED_HOSTS 오류
```
DisallowedHost at /
```
**해결방법**: 환경 변수에 `ALLOWED_HOSTS` 설정 또는 CloudType.io 도메인 확인

#### 2. 정적 파일 404 오류
```
Static files not found
```
**해결방법**: `python manage.py collectstatic --noinput` 명령어가 시작 전 명령어에 포함되었는지 확인

#### 3. 데이터베이스 연결 오류
```
FATAL: database does not exist
```
**해결방법**: CloudType.io에서 PostgreSQL 애드온 추가 및 `DATABASE_URL` 환경 변수 설정

#### 4. Elasticsearch 연결 오류
```
ConnectionError: Elasticsearch unreachable
```
**해결방법**: 
- Elasticsearch 서비스가 실행 중인지 확인
- 환경 변수 `ELASTICSEARCH_HOST`, `ELASTICSEARCH_PORT` 확인
- 네트워크 접근 권한 확인

#### 5. 환경 변수 오류
```
KeyError: 'SECRET_KEY'
```
**해결방법**: CloudType.io 대시보드에서 필수 환경 변수 설정

### 로그 확인 방법

1. CloudType.io 대시보드 → 프로젝트 선택 → "로그" 탭
2. 실시간 로그 모니터링 가능
3. 오류 발생시 상세 스택 트레이스 확인

## 성능 최적화

### 1. 정적 파일 최적화
```python
# cloudtype.py에 이미 설정됨
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 2. 데이터베이스 최적화
```python
# 연결 풀 설정 (cloudtype.py에 포함됨)
CONN_MAX_AGE = 60
```

### 3. 캐싱 설정
Redis가 있는 경우 자동으로 사용되며, 없는 경우 로컬 메모리 캐시 사용

## 도메인 연결

CloudType.io에서 커스텀 도메인을 연결하려면:

1. CloudType.io 대시보드 → 프로젝트 → "도메인" 탭
2. 커스텀 도메인 추가
3. DNS 설정에서 CNAME 레코드 추가
4. 환경 변수 `ALLOWED_HOSTS`에 새 도메인 추가

## 백업 및 복원

### 데이터베이스 백업
```bash
# PostgreSQL 백업
pg_dump $DATABASE_URL > backup.sql

# 복원
psql $DATABASE_URL < backup.sql
```

### Elasticsearch 백업
```bash
# 스냅샷 생성 (Elasticsearch API 사용)
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_1"
```

## 모니터링

### 1. 애플리케이션 모니터링
- CloudType.io 대시보드에서 CPU, 메모리 사용량 확인
- 로그 모니터링으로 오류 추적

### 2. 외부 서비스 모니터링
- Elasticsearch 클러스터 상태 확인
- MongoDB Atlas 메트릭 확인
- Redis 연결 상태 확인

## 비용 최적화

### 1. CloudType.io
- 무료 플랜: 512MB RAM, 0.5 vCPU
- 유료 플랜: 필요에 따라 스케일링

### 2. 외부 서비스
- Elastic Cloud: 14일 무료 체험 → $16/월부터
- MongoDB Atlas: 512MB 무료 → $9/월부터  
- Upstash Redis: 10K 명령어 무료 → $0.2/100K 명령어

## 보안 고려사항

### 1. 환경 변수 보안
- SECRET_KEY는 강력한 랜덤 문자열 사용
- 데이터베이스 비밀번호는 복잡하게 설정
- API 키는 정기적으로 로테이션

### 2. HTTPS 설정
CloudType.io는 자동으로 SSL/TLS 인증서를 제공하므로 별도 설정 불필요

### 3. 접근 제어
- Django 관리자 페이지 접근 제한
- API 엔드포인트 인증 설정 (필요시)

## 참고 자료

- [CloudType.io 공식 문서](https://docs.cloudtype.io/)
- [Django 배포 가이드](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [WhiteNoise 문서](http://whitenoise.evans.io/)
- [Gunicorn 문서](https://gunicorn.org/)


