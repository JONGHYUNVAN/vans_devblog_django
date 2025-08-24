"""
VansDevBlog Search Service Suggestion Document

검색 자동완성을 위한 제안 문서를 정의합니다.
"""

import logging

from elasticsearch_dsl import Completion, Document, Integer, Keyword

logger = logging.getLogger("search")


class SuggestionDocument(Document):
    """
    검색 자동완성을 위한 제안 문서 클래스.

    검색어, 카테고리, 태그 등의 자동완성 데이터를 저장합니다.

    Attributes:
        suggestion (str): 제안할 텍스트
        type (str): 제안 타입 (query, category, tag, title)
        frequency (int): 사용 빈도
        language (str): 언어 코드

    Example:
        >>> suggestion = SuggestionDocument(
        ...     suggestion="Django",
        ...     type="tag",
        ...     frequency=150,
        ...     language="ko"
        ... )
        >>> suggestion.save()
    """

    suggestion = Completion(
        contexts=[
            {"name": "type", "type": "category"},
            {"name": "language", "type": "category"},
        ]
    )

    type = Keyword()
    frequency = Integer()
    language = Keyword()

    class Index:
        name = "vans_suggestions"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    def save(self, **kwargs) -> "SuggestionDocument":
        """
        제안 문서를 Elasticsearch에 저장합니다.

        Returns:
            SuggestionDocument: 저장된 문서 인스턴스
        """
        try:
            logger.debug(f"Saving suggestion document: {self.suggestion}")
            return super().save(**kwargs)
        except Exception as e:
            logger.error(
                f"Failed to save suggestion document {self.suggestion}: {str(e)}"
            )
            raise

    @classmethod
    def create_suggestion(
        cls,
        suggestion_text: str,
        suggestion_type: str,
        language: str = "ko",
        frequency: int = 1,
    ) -> "SuggestionDocument":
        """
        제안 문서를 생성합니다.

        Args:
            suggestion_text (str): 제안 텍스트
            suggestion_type (str): 제안 타입
            language (str): 언어 코드
            frequency (int): 사용 빈도

        Returns:
            SuggestionDocument: 생성된 제안 문서
        """
        return cls(
            suggestion={
                "input": [suggestion_text],
                "contexts": {"type": [suggestion_type], "language": [language]},
                "weight": frequency,
            },
            type=suggestion_type,
            frequency=frequency,
            language=language,
        )

    def increment_frequency(self) -> None:
        """제안 빈도를 증가시킵니다."""
        self.frequency += 1
        self.suggestion["weight"] = self.frequency
