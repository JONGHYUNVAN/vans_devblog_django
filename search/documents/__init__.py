"""
VansDevBlog Search Service Elasticsearch Documents

Elasticsearch 문서 스키마와 인덱스 매핑을 정의합니다.
Post 문서, Suggestion 문서 등이 포함됩니다.
"""

from .analyzers import english_analyzer, korean_analyzer, search_analyzer
from .index_manager import IndexManager
from .post_document import PostDocument
from .suggestion_document import SuggestionDocument

__all__ = [
    "PostDocument",
    "SuggestionDocument",
    "IndexManager",
    "korean_analyzer",
    "english_analyzer",
    "search_analyzer",
]
