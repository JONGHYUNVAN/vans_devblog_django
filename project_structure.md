# VansDevBlog Django-Elasticsearch 검색 서비스 구조

## 📂 현재 프로젝트 구조

```
vans_devblog_django/
├── 📋 문서
│   ├── Django-Elasticsearch-Search-Service-Plan.md  # 구현 계획서
│   └── project_structure.md                         # 이 파일
│
├── 🐳 Docker 설정
│   ├── docker-compose.yml                          # Elasticsearch + Cerebro
│   ├── start-compose.bat                           # Docker 시작 스크립트
│   └── stop-compose.bat                            # Docker 종료 스크립트
│
├── 🐍 Python 환경
│   ├── venv/                                       # 가상환경
│   ├── requirements.txt                            # 전체 패키지 목록
│   ├── requirements-minimal.txt                    # 최소 패키지 목록
│   └── manage.py                                   # Django 관리 스크립트
│
├── 🔧 Django 프로젝트 (vans_search_service/)
│   ├── __init__.py
│   ├── settings.py                                 # Django 설정
│   ├── urls.py                                     # 메인 URL 라우팅
│   ├── wsgi.py                                     # WSGI 설정
│   └── asgi.py                                     # ASGI 설정
│
├── 🔍 검색 앱 (search/)
│   ├── __init__.py
│   ├── apps.py                                     # 앱 설정
│   ├── models.py                                   # Django 모델
│   ├── views.py                                    # API 뷰
│   ├── urls.py                                     # 검색 URL 라우팅
│   ├── admin.py                                    # Django 관리자
│   ├── tests.py                                    # 테스트
│   └── migrations/                                 # 데이터베이스 마이그레이션
│
├── 📊 데이터
│   ├── db.sqlite3                                  # SQLite 데이터베이스
│   └── logs/
│       └── search.log                              # 검색 서비스 로그
│
└── ⚙️ 환경설정 (필요시 생성)
    ├── .env                                        # 환경변수 (gitignore)
    ├── .gitignore                                  # Git 무시 파일
    └── README.md                                   # 프로젝트 설명
```

## 🎯 권장 구조 개선

### 1. 생성 필요한 파일들
- `.gitignore` - Git 버전 관리 설정
- `.env` - 환경 변수 (개발용)
- `README.md` - 프로젝트 설명서
- `pyproject.toml` - 현대적인 Python 패키지 설정

### 2. search/ 앱 확장 구조
```
search/
├── __init__.py
├── apps.py
├── admin.py
├── tests/                                          # 테스트 디렉토리
│   ├── __init__.py
│   ├── test_views.py
│   ├── test_models.py
│   └── test_documents.py
├── documents.py                                    # Elasticsearch Documents
├── serializers.py                                 # DRF Serializers
├── filters.py                                     # 검색 필터
├── utils/                                         # 유틸리티
│   ├── __init__.py
│   ├── elasticsearch_client.py
│   ├── mongodb_client.py
│   └── cache_utils.py
├── management/                                     # Django 관리 명령어
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── sync_posts.py                          # MongoDB -> ES 동기화
│       └── rebuild_index.py                       # 인덱스 재구축
├── models.py                                       # Django 모델 (검색 로그 등)
├── views.py                                        # API 뷰
├── urls.py                                         # URL 라우팅
└── migrations/                                     # DB 마이그레이션
```

### 3. 설정 파일 분리 (향후 확장용)
```
vans_search_service/
├── settings/
│   ├── __init__.py
│   ├── base.py                                     # 공통 설정
│   ├── development.py                              # 개발 환경
│   ├── production.py                               # 운영 환경
│   └── testing.py                                  # 테스트 환경
├── urls.py
├── wsgi.py
└── asgi.py
```

## 🔧 현재 상태 점검

### ✅ 완료된 것들
- Django 5.1.5 프로젝트 생성
- Elasticsearch Docker 환경 구성
- 기본 search 앱 생성
- Swagger 문서화 설정
- 기본 URL 라우팅 설정

### ⚠️ 정리 필요한 것들
1. **가상환경 활성화 문제** - 터미널 세션마다 재활성화 필요
2. **환경 변수 파일** - .env 파일 생성 필요
3. **Django 서버 실행 확인** - 포트 8001에서 정상 작동 확인
4. **Git 설정** - .gitignore 및 초기 커밋 설정

### 🚀 다음 단계 우선순위
1. **즉시 해결**: 가상환경 문제 및 Django 서버 실행 확인
2. **Elasticsearch Documents 생성**: Post 모델에 대한 ES 문서 정의
3. **MongoDB 연동**: Post Service 데이터 동기화
4. **기본 검색 API 구현**: 키워드 검색 기능

## 💡 권장사항

현재 기본 구조는 잘 설정되어 있으니, 다음 순서로 정리를 진행하는 것을 추천합니다:

1. **즉시**: Django 서버 실행 문제 해결
2. **단기**: 필수 설정 파일들 생성 (.gitignore, .env)
3. **중기**: search 앱 내부 구조 확장
4. **장기**: 설정 파일 분리 및 테스트 환경 구축
