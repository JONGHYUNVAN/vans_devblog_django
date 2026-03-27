# Method Inventory Detailed

Full inventory of functions/methods with parameters and returns.

## gunicorn.conf.py :: when_ready
- Purpose: 서버 시작 시 호출되는 콜백
- Parameters: `when_ready(server)`
- Returns: (no Returns in docstring)

## gunicorn.conf.py :: worker_int
- Purpose: 워커 인터럽트 시 호출되는 콜백
- Parameters: `worker_int(worker)`
- Returns: (no Returns in docstring)

## gunicorn.conf.py :: pre_fork
- Purpose: 워커 포크 전 호출되는 콜백
- Parameters: `pre_fork(server, worker)`
- Returns: (no Returns in docstring)

## gunicorn.conf.py :: post_fork
- Purpose: 워커 포크 후 호출되는 콜백
- Parameters: `post_fork(server, worker)`
- Returns: (no Returns in docstring)

## gunicorn.conf.py :: pre_exec
- Purpose: 서버 재시작 전 호출되는 콜백
- Parameters: `pre_exec(server)`
- Returns: (no Returns in docstring)

## gunicorn.conf.py :: worker_abort
- Purpose: 워커 중단 시 호출되는 콜백
- Parameters: `worker_abort(worker)`
- Returns: (no Returns in docstring)

## manage.py :: main
- Purpose: Run administrative tasks.
- Parameters: `main()`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.__init__
- Purpose: No docstring.
- Parameters: `__init__(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_django_settings
- Purpose: Django 설정 확인
- Parameters: `check_django_settings(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_database
- Purpose: 데이터베이스 연결 확인
- Parameters: `check_database(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_static_files
- Purpose: 정적 파일 설정 확인
- Parameters: `check_static_files(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_cache
- Purpose: 캐시 설정 확인
- Parameters: `check_cache(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_elasticsearch
- Purpose: Elasticsearch 연결 확인
- Parameters: `check_elasticsearch(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_mongodb
- Purpose: MongoDB 연결 확인
- Parameters: `check_mongodb(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_api_endpoints
- Purpose: API 엔드포인트 확인
- Parameters: `check_api_endpoints(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.check_security_settings
- Purpose: 보안 설정 확인
- Parameters: `check_security_settings(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: CloudTypeHealthChecker.run_all_checks
- Purpose: 모든 헬스체크 실행
- Parameters: `run_all_checks(self)`
- Returns: (no Returns in docstring)

## scripts/cloudtype_health_check.py :: main
- Purpose: 메인 함수
- Parameters: `main()`
- Returns: (no Returns in docstring)

## scripts/run_tests.py :: setup_django
- Purpose: Django 환경 설정
- Parameters: `setup_django()`
- Returns: (no Returns in docstring)

## scripts/run_tests.py :: run_command
- Purpose: 명령어 실행
- Parameters: `run_command(command, description)`
- Returns: (no Returns in docstring)

## scripts/run_tests.py :: main
- Purpose: No docstring.
- Parameters: `main()`
- Returns: (no Returns in docstring)

## scripts/safe_test_runner.py :: check_environment
- Purpose: 환경 확인
- Parameters: `check_environment()`
- Returns: (no Returns in docstring)

## scripts/safe_test_runner.py :: run_safe_tests
- Purpose: 안전한 테스트 실행
- Parameters: `run_safe_tests(test_type='quick', verbose=False)`
- Returns: (no Returns in docstring)

## scripts/safe_test_runner.py :: main
- Purpose: 메인 함수
- Parameters: `main()`
- Returns: (no Returns in docstring)

## scripts/simple_health.py :: health_check
- Endpoint: /api/v1/search/health/ [GET]
- Purpose: No docstring.
- Parameters: `health_check(request)`
- Returns: (no Returns in docstring)

## search/models.py :: SearchLog.__str__
- Purpose: No docstring.
- Parameters: `__str__(self)`
- Returns: (no Returns in docstring)

## search/models.py :: SearchLog.record_log
- Purpose: No docstring.
- Parameters: `record_log(cls, query, results_count, user_id=None, clicked_result_id=None, response_time_ms=None, ip_address=None, user_agent=None)`
- Returns: (no Returns in docstring)

## search/models.py :: PopularSearch.__str__
- Purpose: No docstring.
- Parameters: `__str__(self)`
- Returns: (no Returns in docstring)

## search/models.py :: PopularSearch.update_popular_search
- Purpose: No docstring.
- Parameters: `update_popular_search(cls, query)`
- Returns: (no Returns in docstring)

## search/models.py :: PopularSearch.get_top_popular_searches
- Purpose: No docstring.
- Parameters: `get_top_popular_searches(cls, limit=10)`
- Returns: (no Returns in docstring)

## tests/conftest.py :: pytest_configure
- Purpose: Pytest 설정 초기화
- Parameters: `pytest_configure()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: api_client
- Purpose: DRF API 클라이언트 픽스처
- Parameters: `api_client()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: mock_elasticsearch
- Purpose: Elasticsearch 클라이언트 모킹
- Parameters: `mock_elasticsearch()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: mock_mongodb
- Purpose: MongoDB 클라이언트 모킹
- Parameters: `mock_mongodb()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: clean_cache
- Purpose: 캐시 초기화 픽스처
- Parameters: `clean_cache()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: sample_search_log
- Purpose: 샘플 검색 로그 데이터
- Parameters: `sample_search_log()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: sample_popular_search
- Purpose: 샘플 인기 검색어 데이터
- Parameters: `sample_popular_search()`
- Returns: (no Returns in docstring)

## tests/conftest.py :: override_cache_settings
- Purpose: 테스트용 캐시 설정 오버라이드
- Parameters: `override_cache_settings()`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestSearchAPI.test_health_check_endpoint
- Purpose: 헬스체크 엔드포인트 테스트
- Parameters: `test_health_check_endpoint(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestSearchAPI.test_search_posts_endpoint
- Purpose: 게시물 검색 엔드포인트 테스트
- Parameters: `test_search_posts_endpoint(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestSearchAPI.test_search_posts_invalid_params
- Purpose: 잘못된 파라미터로 검색 API 테스트
- Parameters: `test_search_posts_invalid_params(self, api_client)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestSearchAPI.test_autocomplete_endpoint
- Purpose: 자동완성 엔드포인트 테스트
- Parameters: `test_autocomplete_endpoint(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestSearchAPI.test_popular_searches_endpoint
- Purpose: 인기 검색어 엔드포인트 테스트
- Parameters: `test_popular_searches_endpoint(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestSearchAPI.test_categories_endpoint
- Purpose: 카테고리 엔드포인트 테스트
- Parameters: `test_categories_endpoint(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestAPIErrorHandling.test_search_service_exception
- Purpose: 검색 서비스 예외 처리 테스트
- Parameters: `test_search_service_exception(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestAPIErrorHandling.test_autocomplete_service_exception
- Purpose: 자동완성 서비스 예외 처리 테스트
- Parameters: `test_autocomplete_service_exception(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestAPIAuthentication.test_public_endpoints_no_auth_required
- Purpose: 공개 엔드포인트는 인증 불필요 테스트
- Parameters: `test_public_endpoints_no_auth_required(self, api_client)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestAPIPerformance.test_search_response_structure
- Purpose: 검색 응답 구조 테스트
- Parameters: `test_search_response_structure(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_api.py :: TestAPIPerformance.test_pagination_parameters
- Purpose: 페이지네이션 파라미터 테스트
- Parameters: `test_pagination_parameters(self, api_client, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestElasticsearchClient.test_client_initialization
- Purpose: 클라이언트 초기화 테스트
- Parameters: `test_client_initialization(self, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestElasticsearchClient.test_search_posts_success
- Purpose: 게시물 검색 성공 테스트
- Parameters: `test_search_posts_success(self, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestElasticsearchClient.test_search_posts_exception
- Purpose: 게시물 검색 예외 처리 테스트
- Parameters: `test_search_posts_exception(self, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestElasticsearchClient.test_autocomplete_success
- Purpose: 자동완성 성공 테스트
- Parameters: `test_autocomplete_success(self, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestElasticsearchClient.test_health_check_success
- Purpose: 헬스체크 성공 테스트
- Parameters: `test_health_check_success(self, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestElasticsearchClient.test_health_check_failure
- Purpose: 헬스체크 실패 테스트
- Parameters: `test_health_check_failure(self, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestMongoDBClient.test_client_initialization
- Purpose: 클라이언트 초기화 테스트
- Parameters: `test_client_initialization(self, mock_mongo_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestMongoDBClient.test_get_categories_success
- Purpose: 카테고리 조회 성공 테스트
- Parameters: `test_get_categories_success(self, mock_mongo_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestMongoDBClient.test_get_categories_exception
- Purpose: 카테고리 조회 예외 처리 테스트
- Parameters: `test_get_categories_exception(self, mock_mongo_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestMongoDBClient.test_health_check_success
- Purpose: 헬스체크 성공 테스트
- Parameters: `test_health_check_success(self, mock_mongo_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestMongoDBClient.test_health_check_failure
- Purpose: 헬스체크 실패 테스트
- Parameters: `test_health_check_failure(self, mock_mongo_class)`
- Returns: (no Returns in docstring)

## tests/test_clients.py :: TestClientIntegration.test_both_clients_healthy
- Purpose: 두 클라이언트 모두 정상일 때 테스트
- Parameters: `test_both_clients_healthy(self, mock_mongo_class, mock_es_class)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestSearchWorkflow.setUpClass
- Purpose: 클래스 레벨 설정 - 메모리 효율성을 위해
- Parameters: `setUpClass(cls)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestSearchWorkflow.setUp
- Purpose: 테스트 설정 - 최소한의 인스턴스만 생성
- Parameters: `setUp(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestSearchWorkflow.tearDown
- Purpose: 테스트 정리 - 메모리 누수 방지
- Parameters: `tearDown(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestSearchWorkflow.test_complete_search_workflow
- Purpose: 완전한 검색 워크플로우 테스트 (메모리 최적화됨)
- Parameters: `test_complete_search_workflow(self, mock_mongodb, mock_elasticsearch)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestSearchWorkflow.test_search_logging_integration
- Purpose: 검색 로그 통합 테스트 (메모리 최적화 버전)
- Parameters: `test_search_logging_integration(self, mock_mongodb, mock_elasticsearch)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestSearchWorkflow.test_error_handling_integration
- Purpose: 에러 처리 통합 테스트 (빠른 버전)
- Parameters: `test_error_handling_integration(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestLightweightIntegration.setUpClass
- Purpose: 클래스 레벨 설정 - 메모리 효율성 극대화
- Parameters: `setUpClass(cls)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestLightweightIntegration.setUp
- Purpose: 테스트 설정 - 최소한의 리소스만 사용
- Parameters: `setUp(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestLightweightIntegration.tearDown
- Purpose: 메모리 정리
- Parameters: `tearDown(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestLightweightIntegration.test_basic_api_endpoints
- Purpose: 기본 API 엔드포인트 연결 테스트 - 메모리 최적화
- Parameters: `test_basic_api_endpoints(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestLightweightIntegration.test_model_operations
- Purpose: 모델 기본 동작 테스트 - 메모리 최적화
- Parameters: `test_model_operations(self)`
- Returns: (no Returns in docstring)

## tests/test_integration.py :: TestFullIntegration.test_complete_model_integration
- Purpose: 완전한 모델 통합 테스트
- Parameters: `test_complete_model_integration(self)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: MemoryEfficientTestCase.setUpClass
- Purpose: 클래스 레벨 설정 - 리소스 최소화
- Parameters: `setUpClass(cls)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: MemoryEfficientTestCase.tearDownClass
- Purpose: 클래스 정리 - 메모리 확인
- Parameters: `tearDownClass(cls)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: MemoryEfficientTestCase.setUp
- Purpose: 테스트별 설정 - 최소화
- Parameters: `setUp(self)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: MemoryEfficientTestCase.tearDown
- Purpose: 테스트별 정리 - 메모리 누수 방지
- Parameters: `tearDown(self)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: TestMemoryEfficient.test_basic_endpoints_memory_safe
- Purpose: 기본 엔드포인트 테스트 - 메모리 안전
- Parameters: `test_basic_endpoints_memory_safe(self)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: TestMemoryEfficient.test_search_with_minimal_mocking
- Purpose: 최소한의 모킹으로 검색 테스트
- Parameters: `test_search_with_minimal_mocking(self, mock_es)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: TestMemoryEfficient.test_model_operations_minimal
- Purpose: 최소한의 모델 테스트
- Parameters: `test_model_operations_minimal(self)`
- Returns: (no Returns in docstring)

## tests/test_memory_efficient.py :: TestMemoryStress.test_multiple_requests_memory_stable
- Purpose: 여러 요청에서 메모리 안정성 테스트
- Parameters: `test_multiple_requests_memory_stable(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestSearchLog.test_create_search_log
- Purpose: 검색 로그 생성 테스트
- Parameters: `test_create_search_log(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestSearchLog.test_record_log_class_method
- Purpose: record_log 클래스 메서드 테스트
- Parameters: `test_record_log_class_method(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestSearchLog.test_search_log_str_representation
- Purpose: SearchLog __str__ 메서드 테스트
- Parameters: `test_search_log_str_representation(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestPopularSearch.test_create_popular_search
- Purpose: 인기 검색어 생성 테스트
- Parameters: `test_create_popular_search(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestPopularSearch.test_update_popular_search_new
- Purpose: 새로운 인기 검색어 업데이트 테스트
- Parameters: `test_update_popular_search_new(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestPopularSearch.test_update_popular_search_existing
- Purpose: 기존 인기 검색어 업데이트 테스트
- Parameters: `test_update_popular_search_existing(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestPopularSearch.test_get_top_popular_searches
- Purpose: 상위 인기 검색어 조회 테스트
- Parameters: `test_get_top_popular_searches(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestPopularSearch.test_popular_search_unique_constraint
- Purpose: 인기 검색어 유니크 제약조건 테스트
- Parameters: `test_popular_search_unique_constraint(self)`
- Returns: (no Returns in docstring)

## tests/test_models.py :: TestPopularSearch.test_popular_search_str_representation
- Purpose: PopularSearch __str__ 메서드 테스트
- Parameters: `test_popular_search_str_representation(self)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestSearchService.test_search_service_initialization
- Purpose: SearchService 초기화 테스트
- Parameters: `test_search_service_initialization(self, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestSearchService.test_search_posts_with_logging
- Purpose: 검색 로그 기록을 포함한 게시물 검색 테스트
- Parameters: `test_search_posts_with_logging(self, mock_popular_update, mock_log_record, mock_elasticsearch, mock_mongodb, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestSearchService.test_search_posts_empty_query
- Purpose: 빈 검색어 처리 테스트
- Parameters: `test_search_posts_empty_query(self, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestSearchService.test_get_popular_searches_from_db
- Purpose: DB에서 인기 검색어 조회 테스트
- Parameters: `test_get_popular_searches_from_db(self, mock_get_popular, mock_elasticsearch, mock_mongodb, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestSearchService.test_get_popular_searches_empty_db
- Purpose: DB가 비어있을 때 인기 검색어 조회 테스트
- Parameters: `test_get_popular_searches_empty_db(self, mock_elasticsearch, mock_mongodb, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestSearchService.test_get_categories_from_mongodb
- Purpose: MongoDB에서 카테고리 조회 테스트
- Parameters: `test_get_categories_from_mongodb(self, mock_elasticsearch, mock_mongodb, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestHealthService.test_health_check_all_healthy
- Purpose: 모든 서비스가 정상일 때 헬스체크 테스트
- Parameters: `test_health_check_all_healthy(self, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestHealthService.test_health_check_elasticsearch_unhealthy
- Purpose: Elasticsearch가 비정상일 때 헬스체크 테스트
- Parameters: `test_health_check_elasticsearch_unhealthy(self, mock_elasticsearch, mock_mongodb)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestCacheService.test_cache_search_result
- Purpose: 검색 결과 캐싱 테스트
- Parameters: `test_cache_search_result(self, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestCacheService.test_cache_popular_searches
- Purpose: 인기 검색어 캐싱 테스트
- Parameters: `test_cache_popular_searches(self, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_services.py :: TestCacheService.test_cache_categories
- Purpose: 카테고리 캐싱 테스트
- Parameters: `test_cache_categories(self, clean_cache)`
- Returns: (no Returns in docstring)

## tests/test_simple.py :: TestSimple.test_django_settings
- Purpose: Django 설정 테스트
- Parameters: `test_django_settings(self)`
- Returns: (no Returns in docstring)

## tests/test_simple.py :: TestSimple.test_database_connection
- Purpose: 데이터베이스 연결 테스트
- Parameters: `test_database_connection(self)`
- Returns: (no Returns in docstring)

## tests/test_simple.py :: test_simple_pytest
- Purpose: Pytest 기본 테스트
- Parameters: `test_simple_pytest()`
- Returns: (no Returns in docstring)

## tests/test_simple.py :: test_django_model_creation
- Purpose: Django 모델 생성 테스트
- Parameters: `test_django_model_creation()`
- Returns: (no Returns in docstring)

## vans_search_service/settings.py :: get_env_variable
- Purpose: 환경변수 값을 가져옵니다.
- Parameters: `get_env_variable(var_name, default_value=None)`
- Returns: (no Returns in docstring)

## vans_search_service/settings/testing.py :: DisableMigrations.__contains__
- Purpose: No docstring.
- Parameters: `__contains__(self, item)`
- Returns: (no Returns in docstring)

## vans_search_service/settings/testing.py :: DisableMigrations.__getitem__
- Purpose: No docstring.
- Parameters: `__getitem__(self, item)`
- Returns: (no Returns in docstring)

## vans_search_service/settings/__init__.py :: get_env_variable
- Purpose: 환경변수를 가져오는 헬퍼 함수입니다.
- Parameters: `get_env_variable(var_name, default=None)`
- Returns:

```
Returns:
str: 환경변수 값
```

## search/api/serializers.py :: SearchRequestSerializer.validate_tags
- Purpose: 태그 필터를 검증하고 리스트로 변환합니다.
- Parameters: `validate_tags(self, value)`
- Returns:

```
Returns:
List[str]: 태그 목록
```

## search/api/serializers.py :: SearchRequestSerializer.validate
- Purpose: 전체 데이터를 검증합니다.
- Parameters: `validate(self, attrs)`
- Returns:

```
Returns:
Dict: 검증된 데이터
```

## search/api/serializers.py :: SearchResultSerializer.get_highlight
- Purpose: highlight 객체에서 하이라이트된 HTML 스니펫을 추출합니다.
- Parameters: `get_highlight(self, obj)`
- Returns: (no Returns in docstring)

## search/api/serializers.py :: SyncRequestSerializer.validate
- Purpose: 전체 데이터를 검증합니다.
- Parameters: `validate(self, attrs)`
- Returns:

```
Returns:
Dict: 검증된 데이터
```

## search/api/views.py :: api_logger
- Purpose: API 호출 로깅 데코레이터
- Parameters: `api_logger(func)`
- Returns: (no Returns in docstring)

## search/api/views.py :: health_logger
- Purpose: 헬스체크 전용 경량 로깅 데코레이터 - 에러 시에만 로깅
- Parameters: `health_logger(func)`
- Returns: (no Returns in docstring)

## search/api/views.py :: health_check
- Endpoint: /api/v1/search/health/ [GET]
- Purpose: 서비스 상태를 확인하는 헬스체크 엔드포인트입니다.
- Parameters: `health_check(request)`
- Returns:

```
Returns:
Response: 서비스 상태 정보
```

## search/api/views.py :: search_posts
- Endpoint: /api/v1/search/posts/ [GET]
- Purpose: 게시물을 검색하는 API 엔드포인트입니다.
- Parameters: `search_posts(request)`
- Returns: (no Returns in docstring)

## search/api/views.py :: autocomplete
- Endpoint: /api/v1/search/autocomplete/ [GET]
- Purpose: 검색어 자동완성 제안을 제공하는 API 엔드포인트입니다.
- Parameters: `autocomplete(request)`
- Returns: (no Returns in docstring)

## search/api/views.py :: popular_searches
- Endpoint: /api/v1/search/popular/ [GET]
- Purpose: 인기 검색어 목록을 제공하는 API 엔드포인트입니다.
- Parameters: `popular_searches(request)`
- Returns: (no Returns in docstring)

## search/api/views.py :: get_categories
- Endpoint: /api/v1/search/categories/ [GET]
- Purpose: 사용 가능한 모든 카테고리 목록을 제공하는 API 엔드포인트입니다.
- Parameters: `get_categories(request)`
- Returns: (no Returns in docstring)

## search/api/views.py :: sync_status
- Endpoint: /api/v1/search/sync/status/ [GET]
- Purpose: 동기화 상태를 조회하는 API 엔드포인트입니다.
- Parameters: `sync_status(request)`
- Returns: (no Returns in docstring)

## search/api/views.py :: sync_data
- Endpoint: /api/v1/search/sync/ [POST]
- Purpose: MongoDB에서 Elasticsearch로 데이터를 동기화하는 API 엔드포인트입니다.
- Parameters: `sync_data(request)`
- Returns: (no Returns in docstring)

## search/api/views.py :: sync_all_data
- Endpoint: /api/v1/search/sync/all/ [POST]
- Purpose: 모든 데이터를 동기화하는 간편한 API 엔드포인트입니다.
- Parameters: `sync_all_data(request)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.__init__
- Purpose: ElasticsearchClient 인스턴스를 초기화합니다.
- Parameters: `__init__(self, timeout=None)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.check_connection
- Purpose: Elasticsearch 서버 연결 상태를 확인합니다.
- Parameters: `check_connection(self)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.get_cluster_health
- Purpose: Elasticsearch 클러스터 상태 정보를 반환합니다.
- Parameters: `get_cluster_health(self)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.create_index_if_not_exists
- Purpose: 인덱스가 존재하지 않으면 생성합니다.
- Parameters: `create_index_if_not_exists(self, index_name, mapping)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.delete_index
- Purpose: 인덱스를 삭제합니다.
- Parameters: `delete_index(self, index_name)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.search_posts
- Endpoint: /api/v1/search/posts/ [GET]
- Purpose: 게시물을 검색하고, Elasticsearch에 저장된 실제 데이터(_source)를 기반으로 응답을 생성합니다.
- Parameters: `search_posts(self, query, filters=None, page=1, page_size=20, sort=None)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.get_autocomplete_suggestions
- Purpose: 자동완성 제안을 반환합니다.
- Parameters: `get_autocomplete_suggestions(self, prefix, suggestion_type=None, language='ko', size=10)`
- Returns: (no Returns in docstring)

## search/clients/elasticsearch_client.py :: ElasticsearchClient.get_popular_searches
- Purpose: 인기 검색어 목록을 반환합니다.
- Parameters: `get_popular_searches(self, limit=10)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.__init__
- Purpose: MongoDBClient 인스턴스를 초기화합니다.
- Parameters: `__init__(self, timeout=None)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.check_connection
- Purpose: MongoDB 서버 연결 상태를 확인합니다.
- Parameters: `check_connection(self)`
- Returns:

```
Returns:
bool: 연결 성공 시 True, 실패 시 False
Example:
>>> mongo_client = MongoDBClient()
>>> if mongo_client.check_connection():
...     print("MongoDB is connected")
```

## search/clients/mongodb_client.py :: MongoDBClient.get_posts_count
- Purpose: 게시물 총 개수를 반환합니다.
- Parameters: `get_posts_count(self, filters=None)`
- Returns:

```
Returns:
int: 게시물 개수
Example:
>>> count = mongo_client.get_posts_count({"is_published": True})
>>> print(f"Published posts: {count}")
```

## search/clients/mongodb_client.py :: MongoDBClient.get_all_published_posts
- Purpose: 발행된 모든 게시물을 배치 단위로 반환합니다.
- Parameters: `get_all_published_posts(self, batch_size=100, skip=0)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.get_all_posts
- Purpose: 모든 게시물을 배치 단위로 반환합니다 (발행 여부 무관).
- Parameters: `get_all_posts(self, batch_size=100, skip=0)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.get_posts_by_ids
- Purpose: ID 목록으로 게시물들을 조회합니다.
- Parameters: `get_posts_by_ids(self, post_ids)`
- Returns:

```
Returns:
List[Dict[str, Any]]: 원본 게시물 문서 목록
Example:
>>> posts = mongo_client.get_posts_by_ids([
...     "507f1f77bcf86cd799439011",
...     "507f1f77bcf86cd799439012"
... ])
```

## search/clients/mongodb_client.py :: MongoDBClient.get_post_by_id
- Purpose: ID로 단일 게시물을 조회합니다.
- Parameters: `get_post_by_id(self, post_id)`
- Returns:

```
Returns:
Optional[Dict[str, Any]]: 원본 게시물 문서 또는 None
Example:
>>> post = mongo_client.get_post_by_id("507f1f77bcf86cd799439011")
>>> if post:
...     print(f"Found post: {post['title']}")
```

## search/clients/mongodb_client.py :: MongoDBClient.get_posts_updated_since
- Purpose: 특정 날짜 이후 업데이트된 게시물들을 반환합니다.
- Parameters: `get_posts_updated_since(self, since_date, batch_size=100)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.get_categories
- Endpoint: /api/v1/search/categories/ [GET]
- Purpose: 모든 카테고리 목록을 반환합니다.
- Parameters: `get_categories(self)`
- Returns:

```
Returns:
List[str]: 카테고리 목록
Example:
>>> categories = mongo_client.get_categories()
>>> print(f"Categories: {categories}")
```

## search/clients/mongodb_client.py :: MongoDBClient.get_all_tags
- Purpose: 모든 태그 목록을 반환합니다.
- Parameters: `get_all_tags(self)`
- Returns:

```
Returns:
List[str]: 태그 목록
Example:
>>> tags = mongo_client.get_all_tags()
>>> print(f"Found {len(tags)} unique tags")
```

## search/clients/mongodb_client.py :: MongoDBClient._build_query
- Purpose: 필터 조건에서 MongoDB 쿼리를 구성합니다.
- Parameters: `_build_query(self, filters=None)`
- Returns:

```
Returns:
Dict[str, Any]: MongoDB 쿼리
```

## search/clients/mongodb_client.py :: MongoDBClient.close
- Purpose: MongoDB 연결을 종료합니다.
- Parameters: `close(self)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.__enter__
- Purpose: 컨텍스트 매니저 진입
- Parameters: `__enter__(self)`
- Returns: (no Returns in docstring)

## search/clients/mongodb_client.py :: MongoDBClient.__exit__
- Purpose: 컨텍스트 매니저 종료
- Parameters: `__exit__(self, exc_type, exc_val, exc_tb)`
- Returns: (no Returns in docstring)

## search/documents/index_manager.py :: IndexManager.__init__
- Purpose: No docstring.
- Parameters: `__init__(self)`
- Returns: (no Returns in docstring)

## search/documents/index_manager.py :: IndexManager._setup_connection
- Purpose: Elasticsearch 연결을 설정합니다.
- Parameters: `_setup_connection(self)`
- Returns: (no Returns in docstring)

## search/documents/index_manager.py :: IndexManager.create_indexes
- Purpose: 모든 Elasticsearch 인덱스를 생성합니다.
- Parameters: `create_indexes(self)`
- Returns: (no Returns in docstring)

## search/documents/index_manager.py :: IndexManager.delete_indexes
- Purpose: 모든 Elasticsearch 인덱스를 삭제합니다.
- Parameters: `delete_indexes(self)`
- Returns: (no Returns in docstring)

## search/documents/index_manager.py :: IndexManager.rebuild_indexes
- Purpose: 모든 Elasticsearch 인덱스를 재구축합니다.
- Parameters: `rebuild_indexes(self)`
- Returns: (no Returns in docstring)

## search/documents/index_manager.py :: IndexManager.check_index_health
- Purpose: 인덱스 상태를 확인합니다.
- Parameters: `check_index_health(self)`
- Returns:

```
Returns:
dict: 인덱스별 상태 정보
```

## search/documents/popular_search_document.py :: _get_es_client
- Purpose: 설정에서 Elasticsearch 클라이언트 인스턴스를 생성하여 반환합니다.
- Parameters: `_get_es_client()`
- Returns: (no Returns in docstring)

## search/documents/popular_search_document.py :: PopularSearchDocument.update_popular_search
- Purpose: 인기 검색어를 업데이트하거나 새로 생성합니다.
- Parameters: `update_popular_search(query_text)`
- Returns: (no Returns in docstring)

## search/documents/popular_search_document.py :: PopularSearchDocument.get_top_popular_searches
- Purpose: 상위 인기 검색어 목록을 반환합니다.
- Parameters: `get_top_popular_searches(limit=10)`
- Returns:

```
Returns:
List[Dict]: 인기 검색어 목록 [{"query": "검색어", "count": 횟수}]
```

## search/documents/popular_search_document.py :: PopularSearchDocument.delete_index
- Purpose: 인덱스를 삭제합니다.
- Parameters: `delete_index()`
- Returns: (no Returns in docstring)

## search/documents/popular_search_document.py :: PopularSearchDocument.create_index_if_not_exists
- Purpose: 인덱스가 존재하지 않으면 생성합니다.
- Parameters: `create_index_if_not_exists()`
- Returns: (no Returns in docstring)

## search/documents/post_document.py :: PostDocument.save
- Purpose: 문서를 Elasticsearch에 저장합니다.
- Parameters: `save(self, **kwargs)`
- Returns:

```
Returns:
PostDocument: 저장된 문서 인스턴스
```

## search/documents/post_document.py :: PostDocument.create_from_mongo_post
- Purpose: MongoDB Post 문서에서 PostDocument 인스턴스를 생성합니다.
- Parameters: `create_from_mongo_post(cls, mongo_post)`
- Returns:

```
Returns:
PostDocument: 생성된 PostDocument 인스턴스
```

## search/documents/post_document.py :: PostDocument.to_dict_summary
- Purpose: 검색 결과용 요약 데이터를 반환합니다.
- Parameters: `to_dict_summary(self)`
- Returns:

```
Returns:
Dict[str, Any]: 요약된 게시물 데이터
```

## search/documents/suggestion_document.py :: SuggestionDocument.save
- Purpose: 제안 문서를 Elasticsearch에 저장합니다.
- Parameters: `save(self, **kwargs)`
- Returns:

```
Returns:
SuggestionDocument: 저장된 문서 인스턴스
```

## search/documents/suggestion_document.py :: SuggestionDocument.create_suggestion
- Purpose: 제안 문서를 생성합니다.
- Parameters: `create_suggestion(cls, suggestion_text, suggestion_type, language='ko', frequency=1)`
- Returns:

```
Returns:
SuggestionDocument: 생성된 제안 문서
```

## search/documents/suggestion_document.py :: SuggestionDocument.increment_frequency
- Purpose: 제안 빈도를 증가시킵니다.
- Parameters: `increment_frequency(self)`
- Returns: (no Returns in docstring)

## search/documents/__init__.py :: create_indexes
- Purpose: 모든 Elasticsearch 인덱스를 생성합니다.
- Parameters: `create_indexes()`
- Returns: (no Returns in docstring)

## search/documents/__init__.py :: delete_indexes
- Purpose: 모든 Elasticsearch 인덱스를 삭제합니다.
- Parameters: `delete_indexes()`
- Returns: (no Returns in docstring)

## search/documents/__init__.py :: rebuild_indexes
- Purpose: 모든 Elasticsearch 인덱스를 재구축합니다.
- Parameters: `rebuild_indexes()`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.__init__
- Purpose: No docstring.
- Parameters: `__init__(self)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService._generate_cache_key
- Purpose: No docstring.
- Parameters: `_generate_cache_key(self, prefix, *args, **kwargs)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.get_search_result
- Purpose: No docstring.
- Parameters: `get_search_result(self, query, filters, page, page_size)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.set_search_result
- Purpose: No docstring.
- Parameters: `set_search_result(self, query, filters, page, page_size, result)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.get_autocomplete_suggestions
- Purpose: No docstring.
- Parameters: `get_autocomplete_suggestions(self, query, language)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.set_autocomplete_suggestions
- Purpose: No docstring.
- Parameters: `set_autocomplete_suggestions(self, query, language, suggestions)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.get_popular_searches
- Purpose: No docstring.
- Parameters: `get_popular_searches(self)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.set_popular_searches
- Purpose: No docstring.
- Parameters: `set_popular_searches(self, popular_list)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.get_categories
- Endpoint: /api/v1/search/categories/ [GET]
- Purpose: No docstring.
- Parameters: `get_categories(self)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.set_categories
- Purpose: No docstring.
- Parameters: `set_categories(self, categories)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.clear_search_cache
- Purpose: No docstring.
- Parameters: `clear_search_cache(self)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: CacheService.invalidate_cache
- Purpose: No docstring.
- Parameters: `invalidate_cache(self, cache_type=None)`
- Returns: (no Returns in docstring)

## search/services/cache_service.py :: cache_result
- Purpose: No docstring.
- Parameters: `cache_result(cache_key_func, timeout=300)`
- Returns: (no Returns in docstring)

## search/services/content_parser.py :: _extract_text_from_nodes
- Purpose: Recursively traverses a list of content nodes and extracts all text.
- Parameters: `_extract_text_from_nodes(nodes)`
- Returns: (no Returns in docstring)

## search/services/content_parser.py :: parse_rich_text_json
- Purpose: Parses a structured JSON object (from a rich text editor) into a plain text string.
- Parameters: `parse_rich_text_json(content)`
- Returns:

```
Returns:
A plain text representation of the content, or the original content
if it's not a recognized format.
```

## search/services/health_service.py :: HealthService.get_health_status
- Purpose: 서비스의 전반적인 상태를 확인합니다.
- Parameters: `get_health_status(self)`
- Returns:

```
Returns:
Dict[str, Any]: 서비스 상태 정보
```

## search/services/health_service.py :: HealthService._check_elasticsearch_connection_fast
- Purpose: Elasticsearch 연결 상태를 빠르게 확인합니다 (2초 타임아웃).
- Parameters: `_check_elasticsearch_connection_fast(self)`
- Returns: (no Returns in docstring)

## search/services/health_service.py :: HealthService._check_mongodb_connection_fast
- Purpose: MongoDB 연결 상태를 빠르게 확인합니다 (2초 타임아웃).
- Parameters: `_check_mongodb_connection_fast(self)`
- Returns: (no Returns in docstring)

## search/services/health_service.py :: HealthService._check_elasticsearch_connection
- Purpose: Elasticsearch 연결 상태를 확인합니다.
- Parameters: `_check_elasticsearch_connection(self)`
- Returns:

```
Returns:
bool: 연결 상태
```

## search/services/health_service.py :: HealthService._check_mongodb_connection
- Purpose: MongoDB 연결 상태를 확인합니다.
- Parameters: `_check_mongodb_connection(self)`
- Returns:

```
Returns:
bool: 연결 상태
```

## search/services/search_service.py :: SearchService.__init__
- Purpose: No docstring.
- Parameters: `__init__(self)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService.search_posts
- Endpoint: /api/v1/search/posts/ [GET]
- Purpose: No docstring.
- Parameters: `search_posts(self, search_params)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService.get_autocomplete_suggestions
- Purpose: No docstring.
- Parameters: `get_autocomplete_suggestions(self, autocomplete_params)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService.get_popular_searches
- Purpose: 인기 검색어 목록을 제공합니다.
- Parameters: `get_popular_searches(self)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService.get_categories
- Endpoint: /api/v1/search/categories/ [GET]
- Purpose: 사용 가능한 카테고리 목록을 제공합니다.
- Parameters: `get_categories(self)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService._build_filters
- Purpose: No docstring.
- Parameters: `_build_filters(self, theme, category, tags, language, date_from, date_to)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService._build_sort_params
- Purpose: No docstring.
- Parameters: `_build_sort_params(self, sort_option)`
- Returns: (no Returns in docstring)

## search/services/search_service.py :: SearchService._build_search_response
- Purpose: No docstring.
- Parameters: `_build_search_response(self, search_result, page, page_size)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService.__init__
- Purpose: SyncService 인스턴스를 초기화합니다.
- Parameters: `__init__(self)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._init_clients
- Purpose: 클라이언트들을 초기화합니다.
- Parameters: `_init_clients(self)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._close_clients
- Purpose: 클라이언트 연결을 종료합니다.
- Parameters: `_close_clients(self)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService.get_sync_status
- Purpose: 현재 동기화 상태를 조회합니다.
- Parameters: `get_sync_status(self)`
- Returns:

```
Returns:
Dict[str, Any]: 동기화 상태 정보
Example:
>>> sync_service = SyncService()
>>> status = sync_service.get_sync_status()
>>> print(f"MongoDB 연결: {status['mongodb_connected']}")
```

## search/services/sync_service.py :: SyncService.sync_data
- Endpoint: /api/v1/search/sync/ [POST]
- Purpose: 데이터 동기화를 실행합니다.
- Parameters: `sync_data(self, options)`
- Returns:

```
Returns:
Dict[str, Any]: 동기화 결과
Example:
>>> options = {"incremental": True, "days": 7}
>>> result = sync_service.sync_data(options)
>>> print(f"동기화 완료: {result['synced']}개")
```

## search/services/sync_service.py :: SyncService._check_connections
- Purpose: 연결 상태를 확인합니다.
- Parameters: `_check_connections(self)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._clear_existing_data
- Purpose: 기존 Elasticsearch 데이터를 삭제합니다.
- Parameters: `_clear_existing_data(self)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._full_sync
- Purpose: 전체 동기화를 실행합니다.
- Parameters: `_full_sync(self, options)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._incremental_sync
- Purpose: 증분 동기화를 실행합니다.
- Parameters: `_incremental_sync(self, options)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._process_batch
- Purpose: 배치 단위로 게시물을 처리합니다.
- Parameters: `_process_batch(self, posts, dry_run)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._validate_post_data
- Purpose: 게시물 데이터의 유효성을 검사합니다.
- Parameters: `_validate_post_data(self, post)`
- Returns: (no Returns in docstring)

## search/services/sync_service.py :: SyncService._update_result
- Purpose: 배치 결과를 전체 결과에 반영합니다.
- Parameters: `_update_result(self, total_result, batch_result)`
- Returns: (no Returns in docstring)

## search/utils/pm_plain.py :: _strip_html
- Purpose: No docstring.
- Parameters: `_strip_html(s)`
- Returns: (no Returns in docstring)

## search/utils/pm_plain.py :: pm_to_text
- Purpose: No docstring.
- Parameters: `pm_to_text(node)`
- Returns: (no Returns in docstring)

## search/utils/pm_plain.py :: tiptap_to_plain
- Purpose: No docstring.
- Parameters: `tiptap_to_plain(doc, max_len=20000)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command.add_arguments
- Purpose: 명령어 인자를 정의합니다.
- Parameters: `add_arguments(self, parser)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command.handle
- Purpose: 명령어를 실행합니다.
- Parameters: `handle(self, *args, **options)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command._check_elasticsearch_connection
- Purpose: Elasticsearch 연결 상태를 확인합니다.
- Parameters: `_check_elasticsearch_connection(self)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command._create_indexes
- Purpose: Elasticsearch 인덱스를 생성합니다.
- Parameters: `_create_indexes(self)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command._delete_indexes
- Purpose: Elasticsearch 인덱스를 삭제합니다.
- Parameters: `_delete_indexes(self)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command._rebuild_indexes
- Purpose: Elasticsearch 인덱스를 재구축합니다.
- Parameters: `_rebuild_indexes(self)`
- Returns: (no Returns in docstring)

## search/management/commands/create_search_indexes.py :: Command.print_help
- Purpose: 사용법 도움말을 출력합니다.
- Parameters: `print_help(self)`
- Returns: (no Returns in docstring)

## search/management/commands/fetch_mongodb_data.py :: Command.add_arguments
- Purpose: No docstring.
- Parameters: `add_arguments(self, parser)`
- Returns: (no Returns in docstring)

## search/management/commands/fetch_mongodb_data.py :: Command.handle
- Purpose: No docstring.
- Parameters: `handle(self, *args, **options)`
- Returns: (no Returns in docstring)

## search/management/commands/fetch_mongodb_data.py :: Command._print_status
- Purpose: 현재 상태를 출력합니다.
- Parameters: `_print_status(self, status_data)`
- Returns: (no Returns in docstring)

## search/management/commands/fetch_mongodb_data.py :: Command._print_result
- Purpose: 동기화 결과를 출력합니다.
- Parameters: `_print_result(self, result)`
- Returns: (no Returns in docstring)

## search/management/commands/setup_popular_searches.py :: Command.add_arguments
- Purpose: No docstring.
- Parameters: `add_arguments(self, parser)`
- Returns: (no Returns in docstring)

## search/management/commands/setup_popular_searches.py :: Command.handle
- Purpose: No docstring.
- Parameters: `handle(self, *args, **options)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command.add_arguments
- Purpose: No docstring.
- Parameters: `add_arguments(self, parser)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command.handle
- Purpose: No docstring.
- Parameters: `handle(self, *args, **options)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._check_connections
- Purpose: MongoDB와 Elasticsearch 연결 상태 확인
- Parameters: `_check_connections(self, mongo_client, es_client)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._clear_existing_data
- Purpose: 기존 Elasticsearch 데이터 삭제
- Parameters: `_clear_existing_data(self, es_client)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._full_sync
- Purpose: 전체 동기화 실행
- Parameters: `_full_sync(self, mongo_client, es_client, options)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._incremental_sync
- Purpose: 증분 동기화 실행
- Parameters: `_incremental_sync(self, mongo_client, es_client, options)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._process_batch
- Purpose: 배치 단위로 게시물 처리
- Parameters: `_process_batch(self, posts, dry_run)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._validate_post_data
- Purpose: 게시물 데이터 유효성 검사
- Parameters: `_validate_post_data(self, post)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._update_result
- Purpose: 배치 결과를 전체 결과에 반영
- Parameters: `_update_result(self, total_result, batch_result)`
- Returns: (no Returns in docstring)

## search/management/commands/sync_posts_to_elasticsearch.py :: Command._print_sync_results
- Purpose: 동기화 결과 출력
- Parameters: `_print_sync_results(self, result)`
- Returns: (no Returns in docstring)

## search/management/commands/test_mongodb_connection.py :: Command.add_arguments
- Purpose: No docstring.
- Parameters: `add_arguments(self, parser)`
- Returns: (no Returns in docstring)

## search/management/commands/test_mongodb_connection.py :: Command.handle
- Purpose: No docstring.
- Parameters: `handle(self, *args, **options)`
- Returns: (no Returns in docstring)

## search/management/commands/test_mongodb_connection.py :: Command._show_database_info
- Purpose: 데이터베이스 기본 정보 출력
- Parameters: `_show_database_info(self, mongo_client)`
- Returns: (no Returns in docstring)

## search/management/commands/test_mongodb_connection.py :: Command._show_posts
- Purpose: 게시물 목록 출력
- Parameters: `_show_posts(self, mongo_client, limit, show_all=False)`
- Returns: (no Returns in docstring)

## docs/source/conf.py :: skip_module_variables
- Purpose: 모듈 레벨 변수들을 문서에서 제외
- Parameters: `skip_module_variables(app, what, name, obj, skip, options)`
- Returns: (no Returns in docstring)

## docs/source/conf.py :: setup
- Purpose: No docstring.
- Parameters: `setup(app)`
- Returns: (no Returns in docstring)
