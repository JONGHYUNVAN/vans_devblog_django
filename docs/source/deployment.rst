Deployment
==========

Docker를 이용한 배포
------------------

Docker Compose 사용:

.. code-block:: yaml

    version: '3.8'
    services:
      search-service:
        build: .
        ports:
          - "8000:8000"
        environment:
          - DJANGO_SETTINGS_MODULE=vans_search_service.settings
        depends_on:
          - elasticsearch
          - redis
          - mongodb
      
      elasticsearch:
        image: elasticsearch:8.11.0
        environment:
          - discovery.type=single-node
        ports:
          - "9200:9200"
      
      redis:
        image: redis:7-alpine
        ports:
          - "6379:6379"
      
      mongodb:
        image: mongo:7
        ports:
          - "27017:27017"

실행:

.. code-block:: bash

    docker-compose up -d

Cloudtype.io 배포
------------------

1. **프로젝트 생성**: CloudType.io에서 Django, Python 3.11로 프로젝트 생성
2. **환경 변수 설정**:
   - `DJANGO_SETTINGS_MODULE`: `vans_search_service.settings.cloudtype`
   - `DATABASE_URL`: CloudType에서 제공하는 PostgreSQL URL
   - `SECRET_KEY`, `ALLOWED_HOSTS` 등 설정
3. **빌드 및 시작 명령어 설정**:
   - **빌드**: `pip install -r requirements-cloudtype.txt`
   - **시작 전**: `python manage.py migrate && python manage.py collectstatic --noinput`
   - **시작**: `gunicorn --bind 0.0.0.0:$PORT vans_search_service.wsgi:application`
4. **배포**: "배포" 버튼 클릭

Kubernetes 배포
--------------

Deployment 예시:

.. code-block:: yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: search-service
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: search-service
      template:
        metadata:
          labels:
            app: search-service
        spec:
          containers:
          - name: search-service
            image: vans-search:latest
            ports:
            - containerPort: 8000
            env:
            - name: ELASTICSEARCH_HOST
              value: "elasticsearch-service"
            - name: REDIS_HOST
              value: "redis-service"

프로덕션 고려사항
--------------

보안
~~~~

* HTTPS 설정
* API 키 기반 인증
* Rate limiting
* CORS 정책 설정

모니터링
~~~~~~~

* 로그 수집 (ELK Stack)
* 메트릭 모니터링 (Prometheus)
* 헬스체크 엔드포인트
* 알림 설정

백업
~~~~

* Elasticsearch 스냅샷
* MongoDB 백업
* 설정 파일 버전 관리
