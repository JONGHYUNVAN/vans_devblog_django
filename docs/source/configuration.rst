Configuration
=============

Django 설정
-----------

주요 설정들을 ``settings.py``에서 구성할 수 있습니다.

Elasticsearch 설정
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Elasticsearch 연결 설정
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': [f'{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}'],
            'timeout': 20,
        },
    }

Redis 캐시 설정
~~~~~~~~~~~~~

.. code-block:: python

    # Redis 캐시 설정
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

로깅 설정
--------

.. code-block:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': 'logs/search.log',
            },
        },
        'loggers': {
            'search': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

검색 인덱스 설정
--------------

인덱스 생성:

.. code-block:: bash

    python manage.py create_search_indexes

데이터 동기화:

.. code-block:: bash

    python manage.py sync_posts_to_elasticsearch
