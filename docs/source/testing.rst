Testing
=======

테스트 실행
-----------

.. code-block:: bash

   # 모든 테스트 실행
   pytest

   # 특정 마킹 테스트만 실행 (unit, integration, api)
   pytest -m unit

   # 느린 테스트 제외
   pytest -m "not slow"

   # 커버리지 리포트 생성
   pytest --cov=search --cov-report=html

테스트 종류
-----------

Unit Tests
~~~~~~~~~~

* **목적**: 개별 함수, 클래스의 기능 검증
* **특징**: 외부 의존성 없음, 빠른 속도

Integration Tests
~~~~~~~~~~~~~~~~~

* **목적**: 여러 컴포넌트의 상호작용 검증
* **특징**: 외부 서비스(ES, Mongo)는 모킹, 전체 워크플로우 테스트

API Tests
~~~~~~~~~

* **목적**: REST API 엔드포인트 검증
* **특징**: HTTP 요청/응답, 에러 처리 검증

Performance Tests
~~~~~~~~~~~~~~~~~

* **목적**: 메모리 사용량, 응답 시간 등 성능 검증
* **특징**: `@pytest.mark.timeout`, `@pytest.mark.memory_test` 사용

테스트 구성
-----------

* **설정**: `vans_search_service/settings/testing.py`
* **전역 픽스처**: `tests/conftest.py`
* **DB**: In-memory SQLite 사용으로 빠른 테스트
* **캐시**: `DummyCache` 사용으로 캐시 비활성화

베스트 프랙티스
--------------

* **AAA 패턴**: Arrange(준비), Act(실행), Assert(검증) 패턴 사용
* **명확한 테스트 이름**: `test_search_with_empty_query_returns_empty_results` 처럼 명확하게 작성
* **외부 의존성 모킹**: `unittest.mock.patch`를 사용하여 외부 서비스(ES, DB)를 철저히 모킹
