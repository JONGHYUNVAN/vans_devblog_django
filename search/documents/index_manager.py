"""
VansDevBlog Search Service Index Manager

Elasticsearch 인덱스 관리 유틸리티입니다.
"""

import logging
from elasticsearch_dsl.connections import connections
from django.conf import settings

from .post_document import PostDocument
from .suggestion_document import SuggestionDocument

logger = logging.getLogger('search')


class IndexManager:
    """
    Elasticsearch 인덱스 생성, 삭제, 관리를 담당하는 클래스입니다.
    """
    
    def __init__(self):
        self._setup_connection()
    
    def _setup_connection(self):
        """Elasticsearch 연결을 설정합니다."""
        try:
            connections.create_connection(
                hosts=settings.ELASTICSEARCH_DSL['default']['hosts'],
                timeout=settings.ELASTICSEARCH_DSL['default'].get('timeout', 20),
                max_retries=settings.ELASTICSEARCH_DSL['default'].get('max_retries', 3),
                retry_on_timeout=settings.ELASTICSEARCH_DSL['default'].get('retry_on_timeout', True)
            )
            logger.info("Elasticsearch connection established")
        except Exception as e:
            logger.error(f"Failed to establish Elasticsearch connection: {str(e)}")
            raise
    
    def create_indexes(self):
        """
        모든 Elasticsearch 인덱스를 생성합니다.
        
        Example:
            >>> manager = IndexManager()
            >>> manager.create_indexes()
        """
        try:
            # PostDocument 인덱스 생성
            post_index = PostDocument._index
            if not post_index.exists():
                post_index.create()
                logger.info("Created index: vans_posts")
            else:
                logger.info("Index already exists: vans_posts")
            
            # SuggestionDocument 인덱스 생성
            suggestion_index = SuggestionDocument._index
            if not suggestion_index.exists():
                suggestion_index.create()
                logger.info("Created index: vans_suggestions")
            else:
                logger.info("Index already exists: vans_suggestions")
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
            raise
    
    def delete_indexes(self):
        """
        모든 Elasticsearch 인덱스를 삭제합니다.
        
        Example:
            >>> manager = IndexManager()
            >>> manager.delete_indexes()
        """
        try:
            # PostDocument 인덱스 삭제
            post_index = PostDocument._index
            if post_index.exists():
                post_index.delete()
                logger.info("Deleted index: vans_posts")
            
            # SuggestionDocument 인덱스 삭제
            suggestion_index = SuggestionDocument._index
            if suggestion_index.exists():
                suggestion_index.delete()
                logger.info("Deleted index: vans_suggestions")
                
        except Exception as e:
            logger.error(f"Failed to delete indexes: {str(e)}")
            raise
    
    def rebuild_indexes(self):
        """
        모든 Elasticsearch 인덱스를 재구축합니다.
        
        Example:
            >>> manager = IndexManager()
            >>> manager.rebuild_indexes()
        """
        try:
            self.delete_indexes()
            self.create_indexes()
            logger.info("Rebuilt all indexes successfully")
        except Exception as e:
            logger.error(f"Failed to rebuild indexes: {str(e)}")
            raise
    
    def check_index_health(self) -> dict:
        """
        인덱스 상태를 확인합니다.
        
        Returns:
            dict: 인덱스별 상태 정보
        """
        try:
            es = connections.get_connection()
            
            status = {
                'vans_posts': {
                    'exists': PostDocument._index.exists(),
                    'doc_count': 0
                },
                'vans_suggestions': {
                    'exists': SuggestionDocument._index.exists(),
                    'doc_count': 0
                }
            }
            
            # 문서 수 조회
            if status['vans_posts']['exists']:
                post_count = es.count(index='vans_posts')
                status['vans_posts']['doc_count'] = post_count['count']
            
            if status['vans_suggestions']['exists']:
                suggestion_count = es.count(index='vans_suggestions')
                status['vans_suggestions']['doc_count'] = suggestion_count['count']
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to check index health: {str(e)}")
            return {}

