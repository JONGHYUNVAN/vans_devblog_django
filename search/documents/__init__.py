"""
VansDevBlog Search Service Elasticsearch Documents

Elasticsearch 문서 스키마와 인덱스 매핑을 정의합니다.
Post 문서, Suggestion 문서 등이 포함됩니다.
"""

from .analyzers import english_analyzer, korean_analyzer, search_analyzer
from .index_manager import IndexManager
from .post_document import PostDocument
from .suggestion_document import SuggestionDocument

# 인덱스 관리 함수들을 IndexManager로부터 import
def create_indexes():
    """모든 Elasticsearch 인덱스를 생성합니다."""
    manager = IndexManager()
    return manager.create_indexes()

def delete_indexes():
    """모든 Elasticsearch 인덱스를 삭제합니다."""
    manager = IndexManager()
    return manager.delete_indexes()

def rebuild_indexes():
    """모든 Elasticsearch 인덱스를 재구축합니다."""
    manager = IndexManager()
    return manager.rebuild_indexes()

__all__ = [
    "PostDocument",
    "SuggestionDocument", 
    "IndexManager",
    "korean_analyzer",
    "english_analyzer",
    "search_analyzer",
    "create_indexes",
    "delete_indexes", 
    "rebuild_indexes",
]
