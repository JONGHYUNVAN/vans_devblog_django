# 테스트 문서화 가이드

## 목차
- [테스트 구조 개요](#테스트-구조-개요)
- [테스트 종류별 가이드](#테스트-종류별-가이드)
- [테스트 실행 방법](#테스트-실행-방법)
- [테스트 설정 및 구성](#테스트-설정-및-구성)
- [베스트 프랙티스](#베스트-프랙티스)
- [트러블슈팅](#트러블슈팅)

---

## 테스트 구조 개요

### 디렉토리 구조
```
tests/
├── __init__.py                 # 테스트 패키지 초기화
├── conftest.py                 # Pytest 전역 설정 및 픽스처
├── test_urls.py               # 테스트용 최소 URL 구성
├── test_simple.py             # 기본 설정 검증 테스트
├── test_integration.py        # 통합 테스트 (메모리 최적화됨)
├── test_memory_efficient.py   # 메모리 효율성 테스트
├── test_api.py               # REST API 엔드포인트 테스트
├── test_services.py          # 비즈니스 로직 서비스 테스트
├── test_clients.py           # 외부 서비스 클라이언트 테스트
└── test_models.py            # 데이터베이스 모델 테스트
```

### 테스트 설정 파일
- **`pytest.ini`**: Pytest 전체 설정
- **`conftest.py`**: 전역 픽스처 및 Django 설정
- **`vans_search_service/settings/testing.py`**: 테스트 전용 Django 설정

---

## 테스트 종류별 가이드

### 1. 단위 테스트 (Unit Tests)

#### 목적
- 개별 함수, 메서드, 클래스의 단독 기능 검증
- 외부 의존성 없이 빠른 실행

#### 파일
- `test_models.py` - 데이터베이스 모델 테스트
- `test_services.py` - 비즈니스 로직 테스트
- `test_clients.py` - 클라이언트 로직 테스트

#### 예시
```python
# test_models.py
@pytest.mark.django_db
def test_search_log_creation():
    """검색 로그 생성 테스트"""
    log = SearchLog.record_log(
        query="Django Test",
        results_count=5
    )
    
    assert log.id is not None
    assert log.query == "Django Test"
    assert log.results_count == 5
```

#### 특징
- **마킹**: `@pytest.mark.unit`
- **실행 속도**: 매우 빠름 (< 1초)
- **모킹**: 외부 의존성 완전 모킹
- **DB**: 최소한의 DB 사용 (`@pytest.mark.django_db`)

---

### 2. 통합 테스트 (Integration Tests)

#### 목적
- 여러 컴포넌트 간의 상호작용 검증
- 전체 워크플로우 동작 확인

#### 파일
- `test_integration.py` - 전체 시스템 통합 테스트
- `test_memory_efficient.py` - 메모리 최적화된 통합 테스트

#### 예시
```python
# test_integration.py
@pytest.mark.integration
@pytest.mark.timeout(5)
def test_complete_search_workflow(self, mock_mongodb, mock_elasticsearch):
    """완전한 검색 워크플로우 테스트"""
    # 1. 헬스체크
    response = self.client.get('/api/v1/search/health/')
    assert response.status_code == 200
    
    # 2. 검색 실행
    response = self.client.get('/api/v1/search/posts/', {'query': 'Django'})
    assert response.status_code == 200
    
    # 3. 로그 기록 확인
    assert SearchLog.objects.count() > 0
```

#### 특징
- **마킹**: `@pytest.mark.integration`
- **실행 속도**: 보통 (1-5초)
- **모킹**: 외부 서비스만 모킹 (ES, MongoDB)
- **DB**: 트랜잭션 테스트 포함

---

### 3. API 테스트 (API Tests)

#### 목적
- REST API 엔드포인트 기능 검증
- HTTP 요청/응답 검증
- 에러 처리 검증

#### 파일
- `test_api.py` - REST API 엔드포인트 테스트

#### 예시
```python
# test_api.py
@pytest.mark.api
def test_search_posts_endpoint(self, api_client, mock_elasticsearch, mock_mongodb):
    """게시물 검색 엔드포인트 테스트"""
    url = reverse('search_api:search-posts')
    response = api_client.get(url, {'query': 'Django'})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'total' in data
    assert 'results' in data
```

#### 특징
- **마킹**: `@pytest.mark.api`
- **클라이언트**: DRF `APIClient` 사용
- **검증**: HTTP 상태코드, JSON 응답 구조
- **에러 처리**: 400, 500 에러 케이스 포함

---

### 4. 성능 테스트 (Performance Tests)

#### 목적
- 메모리 사용량 최적화
- 응답 시간 검증
- 리소스 누수 방지

#### 파일
- `test_memory_efficient.py` - 메모리 최적화 테스트
- `test_integration.py` - 타임아웃 테스트

#### 예시
```python
# test_memory_efficient.py
@pytest.mark.memory_test
@pytest.mark.timeout(3)
def test_lightweight_search(self):
    """가벼운 검색 테스트"""
    start_memory = self._get_memory_usage()
    
    # 테스트 실행
    response = self.client.get('/api/v1/search/posts/', {'query': 'Q'})
    
    end_memory = self._get_memory_usage()
    memory_diff = end_memory - start_memory
    
    assert memory_diff < 50  # 50MB 이하
    assert response.status_code == 200
```

#### 특징
- **마킹**: `@pytest.mark.memory_test`, `@pytest.mark.timeout`
- **메모리**: 메모리 사용량 모니터링
- **타임아웃**: 개별 테스트 시간 제한
- **최적화**: Mock 객체 재사용, 가비지 컬렉션

---

### 5. 슬로우 테스트 (Slow Tests)

#### 목적
- 완전한 기능 테스트
- 복잡한 시나리오 검증
- 선택적 실행

#### 파일
- `test_integration.py` - `TestFullIntegration` 클래스

#### 예시
```python
# test_integration.py
@pytest.mark.slow
@pytest.mark.timeout(10)
def test_complete_model_integration(self):
    """완전한 모델 통합 테스트"""
    # 복잡한 모델 상호작용 테스트
    # 여러 DB 쿼리 포함
    # 상세한 검증 로직
```

#### 특징
- **마킹**: `@pytest.mark.slow`
- **실행**: 선택적 실행 (`-m "not slow"`)
- **시간**: 5-10초 소요
- **완전성**: 전체 기능 검증

---

## 테스트 실행 방법

### 기본 실행 명령어

```bash
# 가상환경 활성화
.\venv\Scripts\activate

# 모든 테스트 실행
pytest

# 특정 마킹 테스트만 실행
pytest -m unit              # 단위 테스트만
pytest -m integration       # 통합 테스트만
pytest -m api              # API 테스트만
pytest -m "not slow"       # 슬로우 테스트 제외

# 특정 파일 테스트
pytest tests/test_api.py
pytest tests/test_models.py

# 상세 출력
pytest -v                  # 상세 모드
pytest -s                  # print 출력 표시
pytest --tb=short          # 간단한 traceback

# 병렬 실행 (pytest-xdist 설치 필요)
pytest -n auto             # CPU 코어 수만큼 병렬 실행
```

### 메모리 최적화 실행

```bash
# 가벼운 테스트만 실행
pytest -m "memory_test or unit"

# 느린 테스트 제외하고 실행
pytest -m "not slow"

# 최대 실패 수 제한
pytest --maxfail=3

# 타임아웃 설정
pytest --timeout=30
```

### 커버리지 테스트

```bash
# 커버리지 포함 실행
pytest --cov=search

# HTML 리포트 생성
pytest --cov=search --cov-report=html

# 커버리지 제외 (빠른 실행)
pytest --no-cov
```

---

## 테스트 설정 및 구성

### 1. pytest.ini 설정

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = vans_search_service.settings.testing
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --timeout=30
    --timeout-method=thread
    --maxfail=3
    --no-migrations
    --reuse-db
    --no-cov
testpaths = tests
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
    models: marks tests as model tests
    services: marks tests as service tests
    clients: marks tests as client tests
    timeout: timeout decorator for individual tests
    memory_test: marks tests as memory-efficient tests
    memory_stress: marks tests as memory stress tests
```

### 2. Django 테스트 설정

#### `vans_search_service/settings/testing.py`
```python
from .base import *

# 테스트 데이터베이스 - 메모리 SQLite 사용
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        },
    },
    'search_logs': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# 테스트용 최소 앱 구성
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'search',
]

# 테스트용 URL 구성
ROOT_URLCONF = 'tests.test_urls'

# 캐시 비활성화
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 로깅 최소화
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}
```

### 3. 테스트 픽스처 (conftest.py)

#### 주요 픽스처들
```python
@pytest.fixture
def api_client():
    """DRF API 클라이언트"""
    return APIClient()

@pytest.fixture
def mock_elasticsearch():
    """Elasticsearch 모킹"""
    with patch('search.clients.elasticsearch_client.ElasticsearchClient') as mock_es:
        # 모킹 설정
        yield mock_instance

@pytest.fixture
def mock_mongodb():
    """MongoDB 모킹"""
    with patch('search.clients.mongodb_client.MongoDBClient') as mock_mongo:
        # 모킹 설정
        yield mock_instance

@pytest.fixture
def clean_cache():
    """캐시 초기화"""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
```

---

## 베스트 프랙티스

### 1. 테스트 작성 원칙

#### AAA 패턴 사용
```python
def test_search_log_creation():
    # Arrange (준비)
    query = "Django Test"
    results_count = 5
    
    # Act (실행)
    log = SearchLog.record_log(query=query, results_count=results_count)
    
    # Assert (검증)
    assert log.query == query
    assert log.results_count == results_count
```

#### 명확한 테스트 이름
```python
# 나쁜 예
def test_search():
    pass

# 좋은 예
def test_search_posts_returns_correct_total_count():
    pass

def test_search_posts_with_empty_query_returns_empty_results():
    pass
```

#### 하나의 테스트는 하나의 기능만
```python
# 나쁜 예 - 여러 기능 테스트
def test_search_functionality():
    # 검색 + 로그 + 캐시 모두 테스트
    pass

# 좋은 예 - 기능별 분리
def test_search_posts_returns_results():
    pass

def test_search_logs_are_recorded():
    pass

def test_search_results_are_cached():
    pass
```

### 2. 모킹 전략

#### 외부 의존성만 모킹
```python
# 좋은 예: 외부 서비스 모킹
@patch('search.clients.elasticsearch_client.ElasticsearchClient')
@patch('search.clients.mongodb_client.MongoDBClient')
def test_search_service(mock_mongo, mock_es):
    # 테스트 로직
    pass

# 나쁜 예: 내부 로직까지 과도한 모킹
@patch('search.services.search_service.SearchService._build_response')
def test_search_service(mock_build):
    # 내부 메서드까지 모킹하면 테스트 의미 퇴색
    pass
```

#### 모킹 범위 최소화
```python
# 좋은 예: 필요한 부분만 모킹
def test_elasticsearch_search(self):
    with patch.object(self.es_client.client, 'search') as mock_search:
        mock_search.return_value = {'hits': {'total': {'value': 0}}}
        result = self.es_client.search_posts("test", {}, 1, 20)
        assert result['total'] == 0

# 나쁜 예: 과도한 모킹
def test_elasticsearch_search(self):
    with patch('search.clients.elasticsearch_client.Elasticsearch') as mock_es:
        # 전체 클래스를 모킹하면 실제 로직 테스트 불가
        pass
```

### 3. 성능 최적화

#### 메모리 효율적인 테스트
```python
class TestMemoryEfficient(TestCase):
    @classmethod
    def setUpClass(cls):
        """클래스 레벨에서 공통 객체 생성"""
        super().setUpClass()
        cls.shared_client = APIClient()
    
    def setUp(self):
        """인스턴스마다 필요한 최소한의 설정"""
        self.client = self.shared_client  # 재사용
        
    def tearDown(self):
        """메모리 정리"""
        gc.collect()
```

#### 타임아웃 설정
```python
@pytest.mark.timeout(5)  # 5초 제한
def test_quick_response():
    response = self.client.get('/api/v1/search/health/')
    assert response.status_code == 200
```

#### 데이터베이스 최적화
```python
# 트랜잭션 비활성화로 속도 향상
@pytest.mark.django_db(transaction=False)
def test_model_creation():
    pass

# 최소한의 데이터만 생성
def test_search_log():
    log = SearchLog.record_log(query="Q", results_count=1)  # 최소 데이터
    assert log.id is not None
```

### 4. 테스트 마킹 전략

#### 마킹 규칙
```python
@pytest.mark.unit          # 단위 테스트
@pytest.mark.integration   # 통합 테스트
@pytest.mark.api          # API 테스트
@pytest.mark.slow         # 느린 테스트 (5초 이상)
@pytest.mark.memory_test  # 메모리 최적화 테스트
@pytest.mark.timeout(5)   # 타임아웃 설정
```

#### 선택적 실행
```bash
# 빠른 테스트만 실행
pytest -m "unit or memory_test"

# 느린 테스트 제외
pytest -m "not slow"

# 통합 테스트만 실행
pytest -m integration
```

### 5. 픽스처 활용

#### 재사용 가능한 픽스처
```python
@pytest.fixture
def sample_search_data():
    """재사용 가능한 검색 데이터"""
    return {
        'query': 'Django',
        'total': 10,
        'results': [{'post_id': '123', 'score': 1.5}]
    }

def test_search_response(sample_search_data):
    # 픽스처 재사용
    assert sample_search_data['total'] == 10
```

#### 스코프 설정
```python
@pytest.fixture(scope='class')  # 클래스당 한 번만 실행
def expensive_setup():
    # 비용이 큰 설정
    return setup_data

@pytest.fixture(scope='function')  # 함수당 한 번 실행 (기본값)
def clean_state():
    # 매번 새로운 상태
    return fresh_data
```

---

## 트러블슈팅

### 1. 메모리 부족 문제

#### 증상
```
MemoryError: Unable to allocate array
```

#### 해결책
```python
# 1. 가비지 컬렉션 강제 실행
import gc

def tearDown(self):
    gc.collect()

# 2. Mock 객체 명시적 정리
def tearDown(self):
    for mock_obj in self.mock_objects:
        if hasattr(mock_obj, 'reset_mock'):
            mock_obj.reset_mock()
    self.mock_objects.clear()

# 3. 메모리 효율적인 테스트 작성
@pytest.mark.memory_test
def test_lightweight():
    # 최소한의 데이터만 사용
    pass
```

### 2. 테스트 속도 저하

#### 증상
```
테스트가 10초 이상 소요
```

#### 해결책
```bash
# 1. 느린 테스트 제외
pytest -m "not slow"

# 2. 타임아웃 설정
pytest --timeout=5

# 3. 병렬 실행
pytest -n auto

# 4. 마이그레이션 건너뛰기
pytest --no-migrations

# 5. DB 재사용
pytest --reuse-db
```

### 3. Django 설정 오류

#### 증상
```
CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False
```

#### 해결책
```python
# testing.py에서 설정 수정
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# 또는 DEBUG 활성화
DEBUG = True
```

### 4. 데이터베이스 연결 오류

#### 증상
```
ModuleNotFoundError: No module named 'MySQLdb'
```

#### 해결책
```python
# testing.py에서 SQLite로 변경
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

### 5. Mock 객체 오류

#### 증상
```
AttributeError: 'Mock' object has no attribute 'some_method'
```

#### 해결책
```python
# 1. Mock 메서드 명시적 정의
mock_obj.some_method.return_value = "expected_value"

# 2. MagicMock 사용
from unittest.mock import MagicMock
mock_obj = MagicMock()

# 3. spec 사용으로 실제 클래스 구조 유지
mock_obj = Mock(spec=RealClass)
```

---

## 테스트 커버리지

### 커버리지 측정
```bash
# 커버리지 측정
pytest --cov=search

# HTML 리포트 생성
pytest --cov=search --cov-report=html

# 터미널에서 상세 리포트
pytest --cov=search --cov-report=term-missing
```

### 목표 커버리지
- **전체**: 80% 이상
- **모델**: 90% 이상
- **API**: 85% 이상
- **서비스**: 90% 이상
- **클라이언트**: 75% 이상

---

## CI/CD 통합

### GitHub Actions 예시
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
        
    - name: Install dependencies
      run: |
        pip install -r requirements/testing.txt
        
    - name: Run tests
      run: |
        pytest -m "not slow" --cov=search
        
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

---

이 문서를 통해 프로젝트의 테스트를 체계적으로 관리하고 실행할 수 있습니다. 테스트 작성 시 이 가이드를 참고하여 일관성 있고 효율적인 테스트를 작성하세요!