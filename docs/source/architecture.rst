Architecture
============

시스템 구조
----------

VansDevBlog Search Service는 마이크로서비스 아키텍처를 따릅니다:

.. code-block:: text

    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   Frontend      │    │   API Gateway   │    │ Search Service  │
    │   Applications  │───▶│                 │───▶│                 │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                           │
                                                           ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   MongoDB       │    │   Redis Cache   │    │ Elasticsearch   │
    │   (Metadata)    │◀───┤                 │◀───┤   (Search)      │
    └─────────────────┘    └─────────────────┘    └─────────────────┘

주요 컴포넌트
-----------

API Layer
~~~~~~~~~

* **Django REST Framework**: RESTful API 제공
* **DRF-YASG**: 자동 API 문서 생성
* **CORS Headers**: 크로스 오리진 요청 처리

Search Engine
~~~~~~~~~~~~~

* **Elasticsearch**: 전문 검색 엔진
* **Django-Elasticsearch-DSL**: Django와 Elasticsearch 통합
* **다국어 분석기**: 한국어/영어 텍스트 분석

Caching Layer
~~~~~~~~~~~~~

* **Redis**: 검색 결과 캐시
* **Django Cache Framework**: 캐시 추상화
* **TTL 기반**: 시간 기반 캐시 만료

Data Storage
~~~~~~~~~~~~

* **MongoDB**: 메타데이터 및 통계 저장
* **PyMongo**: MongoDB 클라이언트
* **Collection 기반**: 문서형 데이터 저장

데이터 플로우
-----------

1. **검색 요청**: 클라이언트가 API 요청
2. **캐시 확인**: Redis에서 캐시된 결과 확인
3. **Elasticsearch 쿼리**: 캐시 미스 시 검색 실행
4. **결과 집계**: 검색 결과와 메타데이터 결합
5. **캐시 저장**: 결과를 Redis에 저장
6. **응답 반환**: JSON 형태로 결과 반환

확장성
------

**수평 확장**

* Elasticsearch 클러스터링
* Redis 클러스터 모드
* 로드 밸런서를 통한 API 인스턴스 분산

**성능 최적화**

* 인덱스 샤딩
* 검색 결과 페이지네이션
* 비동기 인덱싱
