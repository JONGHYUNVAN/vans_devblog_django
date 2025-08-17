# VansDevBlog Django-Elasticsearch 검색 서비스 구조

## 📂 현재 프로젝트 파일 구조

```
vans_devblog_django/
├── 문서
│   ├── Django-Elasticsearch-Search-Service-Plan.md  # 구현 계획서
│   └── project_structure.md                         # 이 파일
│
├── Docker 설정
│   ├── docker-compose.yml                          # Elasticsearch + Cerebro
│   ├── start-compose.bat                           # Docker 시작 스크립트
│   └── stop-compose.bat                            # Docker 종료 스크립트
│
├── Python 환경
│   ├── venv/                                       # 가상환경
│   ├── requirements.txt                            # 전체 패키지 목록
│   ├── requirements-minimal.txt                    # 최소 패키지 목록
│   └── manage.py                                   # Django 관리 스크립트
│
├──  Django 프로젝트 (vans_search_service/)
│   ├── __init__.py
│   ├── settings.py                                 # Django 설정
│   ├── urls.py                                     # 메인 URL 라우팅
│   ├── wsgi.py                                     # WSGI 설정
│   └── asgi.py                                     # ASGI 설정
│
├──  검색 앱 (search/)
│   ├── __init__.py
│   ├── apps.py                                     # 앱 설정
│   ├── models.py                                   # Django 모델
│   ├── views.py                                    # API 뷰
│   ├── urls.py                                     # 검색 URL 라우팅
│   ├── admin.py                                    # Django 관리자
│   ├── tests.py                                    # 테스트
│   └── migrations/                                 # 데이터베이스 마이그레이션
│
├── 데이터
│   ├── db.sqlite3                                  # SQLite 데이터베이스
│   └── logs/
│       └── search.log                              # 검색 서비스 로그
│
└──  환경설정 (필요시 생성)
    ├── .env                                        # 환경변수 (gitignore)
    ├── .gitignore                                  # Git 무시 파일
    └── README.md                                   # 프로젝트 설명
```

## 권장 구조 개선

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
