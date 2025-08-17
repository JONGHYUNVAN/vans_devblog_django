Quick Start
===========

시작하기 전에
-----------

필요한 환경:

* Python 3.9+
* Django 5.1+
* Elasticsearch 8.x
* Redis (선택사항)

설치
----

1. 저장소 클론:

.. code-block:: bash

    git clone https://github.com/your-repo/vans-devblog-search.git
    cd vans-devblog-search

2. 의존성 설치:

.. code-block:: bash

    pip install -r requirements.txt

3. 환경 설정:

.. code-block:: bash

    cp .env.example .env
    # .env 파일 편집

4. 서버 실행:

.. code-block:: bash

    python manage.py runserver

기본 사용법
---------

검색 API 사용:

.. code-block:: bash

    # 기본 검색
    curl "http://localhost:8000/api/v1/search/posts/?query=Django"
    
    # 필터링 검색
    curl "http://localhost:8000/api/v1/search/posts/?query=Django&category=Backend"
    
    # 자동완성
    curl "http://localhost:8000/api/v1/search/autocomplete/?query=Djan"
