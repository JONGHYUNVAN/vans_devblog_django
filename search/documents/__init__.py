"""
VansDevBlog Search Service Elasticsearch Documents

Elasticsearch 문서 스키마와 인덱스 매핑을 정의합니다.
Post 문서, Suggestion 문서 등이 포함됩니다.
"""

from .post_document import PostDocument
from .suggestion_document import SuggestionDocument
from .index_manager import IndexManager
from .analyzers import korean_analyzer, english_analyzer, search_analyzer

__all__ = [
    'PostDocument', 
    'SuggestionDocument', 
    'IndexManager',
    'korean_analyzer', 
    'english_analyzer', 
    'search_analyzer'
]

