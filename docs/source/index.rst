.. doc documentation master file, created by
   sphinx-quickstart on Sun Aug 17 20:13:49 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

VansDevBlog Search Service
==========================

.. image:: https://img.shields.io/badge/Python-3.9+-blue.svg
   :target: https://python.org
   :alt: Python Version

.. image:: https://img.shields.io/badge/Django-5.1+-green.svg
   :target: https://djangoproject.com
   :alt: Django Version

.. image:: https://img.shields.io/badge/Elasticsearch-8.x-orange.svg
   :target: https://elastic.co
   :alt: Elasticsearch Version

고성능 Django-Elasticsearch 기반 검색 마이크로서비스입니다.

Overview
--------

VansDevBlog Search Service는 블로그 플랫폼을 위한 전용 검색 엔진으로, 
Elasticsearch를 활용하여 빠르고 정확한 검색 결과를 제공합니다.

.. note::
   이 서비스는 RESTful API를 통해 독립적으로 운영되며, 
   다양한 프론트엔드 애플리케이션과 쉽게 통합할 수 있습니다.

Key Features
------------

**Advanced Search**
   * 전문 검색 (Full-text search)
   * 다국어 분석기 지원 (한국어/영어)
   * 유사도 기반 랭킹

**Real-time Features**  
   * 실시간 자동완성
   * 검색 제안 시스템
   * 인기 검색어 트래킹

**Smart Filtering**
   * 계층적 카테고리 필터링
   * 태그 기반 검색
   * 날짜 범위 검색

**High Performance**
   * Redis 캐시 시스템
   * 비동기 인덱싱
   * 확장 가능한 아키텍처

Quick Start
-----------

.. code-block:: bash

   # 검색 요청 예시
   GET /api/v1/search/posts/?query=Django&category=Backend

   # 자동완성 요청 예시  
   GET /api/v1/search/autocomplete/?query=Djan&limit=5

Architecture
------------

.. code-block:: text

   Frontend Apps → API Gateway → Search Service → Elasticsearch
                                      ↓
                                   Redis Cache
                                      ↓
                                   MongoDB

API Documentation
-----------------

.. toctree::
   :maxdepth: 3
   :caption: Documentation:
   
   quickstart
   architecture
   deployment
   testing
   api

