# VansDevBlog Django-Elasticsearch 검색 서비스 구현 계획

## 프로젝트 개요

VansDevBlog의 마이크로서비스 아키텍처에 Django-Elasticsearch 기반 검색 서비스를 추가하여 사용자에게 강력하고 직관적인 검색 기능을 제공합니다.

### 프로젝트 목표
- 기존 마이크로서비스 아키텍처와 원활한 통합
- 비용 효율적인 검색 서비스 구축
- 한국어/영어 다국어 검색 지원
- 실시간 검색 및 자동완성 기능 제공

## 아키텍처 설계

### 현재 VansDevBlog 아키텍처
```
Frontend (Next.js)
├── User Service (Spring Boot + MariaDB)
├── Post Service (NestJS + MongoDB)
├── OAuth Service (Next.js)
├── Image Service (Next.js + AWS S3)
└── AI Chat Service (Next.js + OpenAI)
```

### 추가될 검색 서비스 아키텍처
```
Search Service (Django-Elasticsearch)
├── Elasticsearch (단일 노드, 최소 구성)
├── Django REST API
├── 기존 DB 활용:
│   ├── MariaDB (User Service) - 검색 로그, 사용자 검색 기록
│   └── MongoDB (Post Service) - 메인 데이터 소스, 검색 분석 데이터
└── Django 내장 캐싱 (메모리 기반)
```

## 기술 스택

### 핵심 기술
- **Backend**: Django 4.2+ + Django REST Framework
- **검색 엔진**: Elasticsearch 8.11+ (단일 노드)
- **한국어 처리**: Elasticsearch Nori 분석기
- **캐싱**: Django 내장 캐시 프레임워크 (LocMemCache)
- **API 문서화**: Swagger/OpenAPI (`drf-yasg`)
- **코드 문서화**: PyDoc (Google/Numpy 스타일)
- **코드 품질**: Black, Flake8, isort, mypy

### 데이터베이스 활용
- **MariaDB** (기존 User Service DB)
  - 검색 로그 저장
  - 사용자 검색 히스토리
  - 인기 검색어 통계
- **MongoDB** (기존 Post Service DB)
  - 게시물 데이터 (검색 소스)
  - 검색 분석 데이터
  - 자동완성 데이터

### 모니터링 및 분석
- Django Admin 확장 대시보드
- Chart.js 기반 통계 시각화
- 커스텀 성능 모니터링
- **Cerebro**: Elasticsearch GUI 관리 도구 (무료)

## 비용 최적화 전략

### 기존 인프라 최대 활용
- **MariaDB/MongoDB**: 기존 DB 활용으로 추가 비용 없음
- **Django 내장 캐싱**: Redis 대신 메모리 기반 캐시 사용
- **커스텀 대시보드**: Kibana 대신 Django Admin 활용

### 예상 비용 절감 효과
```
기존 계획 (Redis + Kibana + PostgreSQL): $65-115/월
수정된 계획 (기존 DB 활용): $10-20/월
절감 효과: 월 $55-95 (약 85% 절감)
```

## 구현할 검색 기능

### 1. 핵심 검색 기능
- **통합 검색**: 모든 게시물, 카테고리, 태그 통합 검색
- **실시간 검색**: 타이핑 중 즉시 결과 표시
- **자동완성**: 검색어 제안 및 추천
- **다국어 검색**: 한국어/영어 형태소 분석 지원

### 2. 고급 검색 기능
- **카테고리별 필터링**: Frontend, Backend, Database, IT 등
- **날짜 범위 검색**: 특정 기간 게시물 검색
- **태그 기반 검색**: 관련 태그로 정확한 결과 제공
- **관련도 기반 정렬**: 검색 정확도 순 결과 제공

### 3. 검색 분석 기능
- **검색어 통계**: 인기 검색어, 검색 트렌드
- **기본 성능 모니터링**: 응답 시간, 검색 결과 수
- **사용자 검색 패턴**: 개인별 검색 히스토리

## 데이터베이스 스키마 설계

### MariaDB 확장 (User Service DB)

#### 검색 로그 테이블
```sql
CREATE TABLE search_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    query VARCHAR(255) NOT NULL,
    results_count INT DEFAULT 0,
    clicked_result_id VARCHAR(50),
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INT,
    INDEX idx_user_search (user_id, search_time),
    INDEX idx_query (query),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 인기 검색어 통계 테이블
```sql
CREATE TABLE popular_searches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query VARCHAR(255) UNIQUE NOT NULL,
    search_count INT DEFAULT 1,
    last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_count (search_count DESC)
);
```

#### 사용자 검색 설정 테이블
```sql
CREATE TABLE user_search_preferences (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNIQUE,
    preferred_categories JSON,
    search_history_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### MongoDB 확장 (Post Service DB)

#### 검색 분석 컬렉션
```javascript
// search_analytics 컬렉션
{
    _id: ObjectId,
    date: Date,
    query: String,
    total_results: Number,
    avg_response_time: Number,
    click_through_rate: Number,
    popular_results: [String], // 클릭된 게시물 ID 목록
    user_count: Number, // 해당 검색어를 사용한 사용자 수
    created_at: Date
}

// 인덱스
db.search_analytics.createIndex({ "date": 1, "query": 1 });
db.search_analytics.createIndex({ "query": 1, "date": -1 });
```

#### 자동완성 데이터 컬렉션
```javascript
// search_suggestions 컬렉션
{
    _id: ObjectId,
    prefix: String, // 검색어 접두사
    suggestions: [
        {
            text: String,
            score: Number, // 인기도 점수
            category: String
        }
    ],
    updated_at: Date
}

// 인덱스
db.search_suggestions.createIndex({ "prefix": 1, "score": -1 });
```

## 성능 최적화 구성

### Django 캐싱 설정
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'search-cache',
        'TIMEOUT': 300,  # 5분
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# 검색 결과 캐싱 전략
SEARCH_CACHE_TIMEOUT = 300  # 5분
AUTOCOMPLETE_CACHE_TIMEOUT = 600  # 10분
POPULAR_SEARCHES_CACHE_TIMEOUT = 3600  # 1시간
```

### Elasticsearch 최소 구성
```yaml
# docker-compose.yml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    container_name: vans_search_elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
      - cluster.name=vans-search-cluster
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - vans_search_network

  # Elasticsearch GUI 관리 도구
  cerebro:
    image: lmenezes/cerebro:0.9.4
    container_name: vans_search_cerebro
    ports:
      - "9000:9000"
    depends_on:
      - elasticsearch
    networks:
      - vans_search_network

volumes:
  es_data:
    driver: local

networks:
  vans_search_network:
    driver: bridge
```

### Elasticsearch 인덱스 매핑
```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "nori",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "content": {
        "type": "text",
        "analyzer": "nori"
      },
      "tags": {
        "type": "keyword"
      },
      "category": {
        "type": "keyword"
      },
      "created_at": {
        "type": "date"
      },
      "updated_at": {
        "type": "date"
      },
      "author": {
        "type": "keyword"
      },
      "view_count": {
        "type": "integer"
      },
      "like_count": {
        "type": "integer"
      }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "nori": {
          "type": "custom",
          "tokenizer": "nori_tokenizer",
          "decompound_mode": "mixed",
          "filter": [
            "nori_part_of_speech",
            "lowercase"
          ]
        }
      }
    }
  }
}
```

## 단계별 구현 계획

### Phase 1: 기본 인프라 구축 (1주)

#### 1.1 Django 프로젝트 설정
- [ ] Django 4.2+ 프로젝트 생성
- [ ] Django REST Framework 설정
- [ ] `django-elasticsearch-dsl` 설치 및 설정
- [ ] **Swagger 설정**: `drf-yasg` 설치 및 API 문서화 준비
- [ ] **코드 품질 도구**: `black`, `flake8`, `isort` 설정
- [ ] 기본 프로젝트 구조 설정

#### 1.2 Elasticsearch 환경 구성
- [ ] Docker Compose로 Elasticsearch 8.11 설정
- [ ] 한국어 Nori 분석기 설정
- [ ] 기본 인덱스 매핑 정의
- [ ] 연결 테스트 및 기본 동작 확인

#### 1.3 데이터베이스 연결 설정
- [ ] MariaDB 연결 설정 (User Service DB)
- [ ] MongoDB 연결 설정 (Post Service DB)
- [ ] 데이터베이스 연결 테스트

### Phase 2: 기존 DB 통합 (1주)

#### 2.1 MariaDB 스키마 확장
- [ ] 검색 로그 테이블 생성
- [ ] 인기 검색어 테이블 생성
- [ ] 사용자 검색 설정 테이블 생성
- [ ] Django 모델 정의 및 마이그레이션

#### 2.2 MongoDB 컬렉션 설계
- [ ] 검색 분석 컬렉션 설계
- [ ] 자동완성 데이터 컬렉션 설계
- [ ] 인덱스 생성 및 최적화
- [ ] PyMongo 연결 및 테스트

#### 2.3 데이터 동기화 로직 구현
- [ ] MongoDB에서 Elasticsearch로 초기 데이터 이관
- [ ] 실시간 데이터 동기화 파이프라인 구현
- [ ] 데이터 일관성 검증 로직

### Phase 3: 기본 검색 기능 (2주)

#### 3.1 검색 API 개발
- [ ] 기본 키워드 검색 API
- [ ] **PyDoc 작성**: 모든 함수에 상세한 docstring 추가
- [ ] **Swagger 문서화**: API 엔드포인트 자동 문서화
- [ ] 검색 결과 페이지네이션
- [ ] 검색 로그 저장 기능
- [ ] Django 내장 캐시 적용

#### 3.2 Elasticsearch Document 정의
- [ ] Post Document 클래스 구현
- [ ] 인덱스 설정 및 매핑 정의
- [ ] 검색 쿼리 최적화
- [ ] 한국어 분석기 적용

#### 3.3 기본 필터링 및 정렬
- [ ] 카테고리별 필터링
- [ ] 날짜 범위 검색
- [ ] 관련도 기반 정렬
- [ ] 검색 성능 최적화

### Phase 4: 고급 기능 (2주)

#### 4.1 자동완성 기능
- [ ] Elasticsearch Suggest API 활용
- [ ] 자동완성 데이터 생성 로직
- [ ] 실시간 자동완성 API
- [ ] 자동완성 캐싱 전략

#### 4.2 검색 분석 시스템
- [ ] 검색어 통계 수집
- [ ] 인기 검색어 계산 로직
- [ ] 검색 성능 모니터링
- [ ] 사용자 검색 패턴 분석

#### 4.3 검색 대시보드
- [ ] Django Admin 확장
- [ ] Chart.js 통계 시각화
- [ ] 검색 성능 대시보드
- [ ] 관리자 모니터링 도구

### Phase 5: 최적화 및 배포 (1주)

#### 5.1 성능 튜닝
- [ ] Elasticsearch 쿼리 최적화
- [ ] Django 캐시 전략 개선
- [ ] 데이터베이스 쿼리 최적화
- [ ] 응답 시간 개선

#### 5.2 배치 작업 구현
- [ ] 인기 검색어 업데이트 배치
- [ ] 검색 분석 데이터 집계
- [ ] 자동완성 데이터 갱신
- [ ] 시스템 헬스 체크

#### 5.3 배포 및 모니터링
- [ ] Docker 컨테이너 배포
- [ ] 로그 수집 및 모니터링
- [ ] 에러 처리 및 알림
- [ ] 성능 모니터링 설정

## 코드 컨벤션 및 문서화 가이드라인

### 코딩 스타일
- **PEP 8**: Python 코드 스타일 가이드 준수
- **Django 코딩 스타일**: Django 프레임워크 권장사항 적용
- **타입 힌팅**: Python 3.9+ 타입 어노테이션 필수 사용

### 문서화 표준
- **PyDoc**: 모든 함수, 클래스, 모듈에 상세한 docstring 작성
- **Swagger/OpenAPI**: REST API 자동 문서화
- **README**: 각 모듈별 설치 및 사용법 가이드

### PyDoc 작성 규칙
```python
def search_posts(query: str, filters: Dict[str, Any], page: int = 1) -> SearchResponse:
    """
    게시물을 검색하고 결과를 반환합니다.
    
    이 함수는 Elasticsearch를 사용하여 게시물을 검색하며,
    한국어 형태소 분석과 다양한 필터링 옵션을 지원합니다.
    
    Args:
        query (str): 검색할 키워드 또는 구문
            - 빈 문자열일 경우 모든 게시물 반환
            - 한국어, 영어 혼용 검색 지원
        filters (Dict[str, Any]): 검색 필터 옵션
            - category (str): 카테고리 필터 (예: 'frontend', 'backend')
            - tags (List[str]): 태그 필터 목록
            - date_range (Dict): 날짜 범위 {'start': datetime, 'end': datetime}
            - author (str): 작성자 필터
        page (int, optional): 페이지 번호 (기본값: 1)
            - 1부터 시작하는 페이지 번호
            - 페이지당 20개 결과 반환
    
    Returns:
        SearchResponse: 검색 결과 객체
            - total (int): 전체 검색 결과 수
            - results (List[PostDocument]): 검색된 게시물 목록
            - page (int): 현재 페이지 번호
            - has_next (bool): 다음 페이지 존재 여부
            - execution_time (float): 검색 실행 시간 (초)
    
    Raises:
        ValidationError: 잘못된 필터 형식이나 페이지 번호일 때
        ElasticsearchException: Elasticsearch 연결 또는 쿼리 오류
        PermissionError: 접근 권한이 없는 게시물 포함 시
    
    Example:
        >>> filters = {
        ...     'category': 'frontend', 
        ...     'tags': ['react', 'typescript'],
        ...     'date_range': {
        ...         'start': datetime(2024, 1, 1),
        ...         'end': datetime(2024, 12, 31)
        ...     }
        ... }
        >>> result = search_posts("Django Elasticsearch", filters, page=1)
        >>> print(f"총 {result.total}개 결과 중 {len(result.results)}개 표시")
        총 15개 결과 중 15개 표시
    
    Note:
        - 검색 결과는 관련도 순으로 정렬됩니다
        - 캐시된 결과는 5분간 유지됩니다
        - 한국어 검색 시 Nori 분석기를 사용합니다
    
    Version:
        Added in version 1.0.0
        
    See Also:
        autocomplete_suggestions(): 자동완성 제안 함수
        get_popular_searches(): 인기 검색어 조회 함수
    """
    pass
```

### Swagger 설정
```python
# settings.py
INSTALLED_APPS = [
    # ... 기타 앱들
    'drf_yasg',  # Swagger UI
    'rest_framework',
]

# Swagger 설정
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get', 'post', 'put', 'delete', 'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
}
```

### API 문서화 예시
```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SearchViewSet(viewsets.ViewSet):
    """
    게시물 검색 API
    
    이 ViewSet은 Elasticsearch를 사용한 게시물 검색 기능을 제공합니다.
    실시간 검색, 자동완성, 고급 필터링을 지원합니다.
    """
    
    @swagger_auto_schema(
        operation_summary="게시물 검색",
        operation_description="""
        키워드를 사용하여 게시물을 검색합니다.
        한국어/영어 혼용 검색과 다양한 필터링 옵션을 지원합니다.
        """,
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="검색 키워드",
                type=openapi.TYPE_STRING,
                required=True,
                example="Django Elasticsearch"
            ),
            openapi.Parameter(
                'category', openapi.IN_QUERY,
                description="카테고리 필터",
                type=openapi.TYPE_STRING,
                enum=['frontend', 'backend', 'database', 'it'],
                example="backend"
            ),
            openapi.Parameter(
                'page', openapi.IN_QUERY,
                description="페이지 번호 (1부터 시작)",
                type=openapi.TYPE_INTEGER,
                default=1,
                example=1
            ),
        ],
        responses={
            200: openapi.Response(
                description="검색 성공",
                examples={
                    "application/json": {
                        "total": 15,
                        "results": [
                            {
                                "id": "507f1f77bcf86cd799439011",
                                "title": "Django와 Elasticsearch 연동하기",
                                "content": "Django 프로젝트에 Elasticsearch를...",
                                "category": "backend",
                                "tags": ["django", "elasticsearch"],
                                "created_at": "2024-01-15T10:30:00Z",
                                "score": 1.5
                            }
                        ],
                        "page": 1,
                        "has_next": False,
                        "execution_time": 0.125
                    }
                }
            ),
            400: "잘못된 요청 파라미터",
            500: "서버 내부 오류"
        },
        tags=['검색']
    )
    def search(self, request):
        """게시물 검색 엔드포인트"""
        pass
```

## 주요 구현 고려사항

### 1. 마이크로서비스 통신
- **API Gateway**: 검색 요청 라우팅 및 인증
- **Service Discovery**: 서비스 간 자동 검색 및 연결
- **Circuit Breaker**: 장애 격리 및 자동 복구

### 2. 데이터 일관성
- **Event-Driven Architecture**: 게시물 변경 시 실시간 인덱스 업데이트
- **Eventual Consistency**: 최종 일관성 보장
- **Retry 메커니즘**: 동기화 실패 시 재시도 로직

### 3. 보안 및 권한
- **JWT 인증**: User Service와 연동한 인증 시스템
- **접근 권한 제어**: 공개/비공개 게시물 처리
- **검색 로그 보안**: 개인정보 보호 및 데이터 암호화

### 4. 확장성 고려사항
- **수평 확장**: 트래픽 증가 시 서버 확장 방안
- **Elasticsearch 클러스터**: 향후 멀티 노드 구성
- **캐시 계층**: Redis 도입 시점 및 전략

## 성공 지표

### 기술적 성과
- **응답 시간**: 평균 200ms 이하 검색 응답
- **검색 정확도**: 관련도 85% 이상
- **시스템 가용성**: 99.9% 이상 uptime
- **동시 사용자**: 100명 이상 동시 검색 지원

### 사용자 경험
- **검색 성공률**: 원하는 결과 찾기 90% 이상
- **자동완성 사용률**: 전체 검색의 50% 이상
- **검색 만족도**: 사용자 피드백 4.5/5.0 이상

### 비즈니스 가치
- **비용 효율성**: 기존 대비 85% 비용 절감
- **사용자 체류 시간**: 평균 20% 증가
- **컨텐츠 발견율**: 검색을 통한 과거 게시물 조회 30% 증가

## 다음 단계

1. **Phase 1 시작**: Django 프로젝트 초기화 및 Elasticsearch 환경 구성
2. **MVP 개발**: 기본 검색 기능부터 단계별 구현
3. **점진적 확장**: 사용량 증가에 따른 기능 확장
4. **성능 모니터링**: 각 단계별 성능 측정 및 최적화

## 주요 의존성 패키지

### requirements.txt
```txt
# Django 기본
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1

# Elasticsearch 연동
django-elasticsearch-dsl==7.3.0
elasticsearch==8.11.0

# API 문서화
drf-yasg==1.21.7

# 데이터베이스
mysqlclient==2.2.0  # MariaDB 연결
pymongo==4.6.0      # MongoDB 연결

# 코드 품질 및 문서화
black==23.10.1
flake8==6.1.0
isort==5.12.0
mypy==1.7.0

# 개발 도구
python-dotenv==1.0.0
pydantic==2.5.0

# 테스트
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
```

### 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 코드 포맷팅 설정
black --line-length=88 .
isort --profile=black .
flake8 --max-line-length=88 --extend-ignore=E203,W503 .
```

## 참고 자료

- [Django-Elasticsearch-DSL 공식 문서](https://django-elasticsearch-dsl.readthedocs.io/)
- [Elasticsearch 한국어 분석기 가이드](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-nori.html)
- [Django REST Framework 문서](https://www.django-rest-framework.org/)
- [Elasticsearch 8.x 공식 문서](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/index.html)
- [drf-yasg Swagger 문서](https://drf-yasg.readthedocs.io/)
- [Google Python 스타일 가이드](https://google.github.io/styleguide/pyguide.html)

---

**문서 버전**: 1.0  
**작성일**: 2025년  
**최종 수정일**: 2025년  
**작성자**: VansDevBlog Team
