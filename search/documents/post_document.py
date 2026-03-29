"""
VansDevBlog Search Service Post Document

블로그 게시물 Elasticsearch 문서를 정의합니다.
"""

import logging
from typing import Any, Dict, List

from elasticsearch_dsl import (
    Completion,
    Date,
    Document,
    Keyword,
    Text,
)

from .analyzers import BASE_INDEX_SETTINGS, english_analyzer, korean_analyzer

logger = logging.getLogger("search")


def extract_tiptap_text(node: Any) -> List[str]:
    """
    TipTap JSON 노드 트리에서 텍스트 리프 노드를 재귀적으로 수집합니다.

    Args:
        node: TipTap JSON 노드 (dict) 또는 임의의 값

    Returns:
        List[str]: 수집된 텍스트 값 목록
    """
    if not isinstance(node, dict):
        return []

    texts = []

    # 현재 노드가 텍스트 타입인 경우 text 값을 수집
    if node.get("type") == "text" and isinstance(node.get("text"), str):
        texts.append(node["text"])

    # content 배열이 있으면 재귀 탐색
    for child in node.get("content", []):
        texts.extend(extract_tiptap_text(child))

    return texts


class PostDocument(Document):
    """
    블로그 게시물 Elasticsearch 문서 클래스.

    MongoDB의 Post 컬렉션 데이터를 Elasticsearch에 매핑하여
    한국어/영어 다국어 검색과 고급 필터링을 지원합니다.

    Attributes:
        post_id (str): MongoDB ObjectId 문자열
        title (str): 게시물 제목 (한국어/영어 분석)
        description (str): 게시물 설명
        content_text (str): TipTap JSON에서 추출한 순수 텍스트 (한국어/영어 분석)
        topic (str): 게시물 주제
        mainCategory (str): 메인 카테고리 (기존 테마)
        subCategory (str): 서브 카테고리 (기존 카테고리)
        tags (List[str]): 태그 목록
        author (str): 작성자 닉네임 (표시용)
        language (str): 언어 코드 (ko, en)
        createdAt (datetime): 생성일 (정렬용)
        updatedAt (datetime): 수정일 (정렬용)
    """

    # 기본 식별자
    post_id = Keyword()

    # 제목 - 다국어 분석 + 자동완성
    title = Text(
        analyzer=korean_analyzer,
        fields={
            "english": Text(analyzer=english_analyzer),
            "raw": Keyword(),
            "suggest": Completion(),
        },
    )

    # 설명 - 다국어 분석 + 자동완성
    description = Text(
        analyzer=korean_analyzer,
        fields={
            "english": Text(analyzer=english_analyzer),
            "suggest": Completion(),
        },
    )

    # 본문 순수 텍스트 - TipTap JSON에서 추출 (색인용, 응답 제외)
    content_text = Text(
        analyzer=korean_analyzer,
        fields={
            "english": Text(analyzer=english_analyzer),
        },
    )

    # 주제 - 다국어 분석 + 자동완성
    topic = Text(
        analyzer=korean_analyzer,
        fields={
            "english": Text(analyzer=english_analyzer),
            "raw": Keyword(),
            "suggest": Completion(),
        },
    )

    # === 분류 필드 (필터링용) ===
    mainCategory = Keyword(fields={"suggest": Completion()})
    subCategory = Keyword(fields={"suggest": Completion()})

    # 태그 - 배열 키워드 (검색 + 필터링)
    tags = Keyword(multi=True, fields={"suggest": Completion()})

    # === 메타데이터 ===
    # 작성자 닉네임 (표시용, PII 없음)
    author = Keyword()

    # 언어 코드 (필터링용)
    language = Keyword()

    # 날짜 필드 (정렬용)
    createdAt = Date()
    updatedAt = Date()

    class Index:
        """Elasticsearch 인덱스 설정."""

        name = "vans_posts"
        settings = BASE_INDEX_SETTINGS

    def save(self, **kwargs) -> "PostDocument":
        """
        문서를 Elasticsearch에 저장합니다.

        Args:
            **kwargs: 추가 저장 옵션

        Returns:
            PostDocument: 저장된 문서 인스턴스

        Raises:
            ConnectionError: Elasticsearch 연결 실패
            RequestError: 잘못된 문서 구조
        """
        try:
            logger.info(f"Saving post document: {self.post_id}")
            return super().save(**kwargs)
        except Exception as e:
            logger.error(f"Failed to save post document {self.post_id}: {str(e)}")
            raise

    @classmethod
    def create_from_mongo_post(cls, mongo_post: Dict[str, Any]) -> "PostDocument":
        """
        MongoDB Post 문서에서 PostDocument 인스턴스를 생성합니다.

        TipTap JSON content 필드에서 plain text를 추출하여 content_text에 저장합니다.
        authorEmail 대신 author(닉네임)만 색인합니다.

        Args:
            mongo_post (Dict[str, Any]): MongoDB Post 문서 데이터

        Returns:
            PostDocument: 생성된 PostDocument 인스턴스
        """
        try:
            post_id = str(mongo_post.get("_id", ""))
            title = str(mongo_post.get("title", ""))

            # TipTap JSON → 순수 텍스트 추출
            content_raw = mongo_post.get("content")
            if isinstance(content_raw, dict):
                texts = extract_tiptap_text(content_raw)
                content_text = " ".join(texts)
            elif isinstance(content_raw, str):
                # 이미 문자열인 경우 그대로 사용 (레거시 데이터 대비)
                content_text = content_raw
            else:
                content_text = ""

            return cls(
                meta={"id": post_id},
                post_id=post_id,
                title=title,
                description=mongo_post.get("description", ""),
                content_text=content_text,
                topic=mongo_post.get("topic", ""),
                mainCategory=mongo_post.get("mainCategory", ""),
                subCategory=mongo_post.get("subCategory", ""),
                tags=mongo_post.get("tags", []),
                author=mongo_post.get("author", ""),
                language=mongo_post.get("language", "ko"),
                createdAt=mongo_post.get("createdAt"),
                updatedAt=mongo_post.get("updatedAt"),
            )

        except Exception as e:
            logger.error(f"Failed to create PostDocument from mongo data: {str(e)}")
            raise ValueError(f"Invalid MongoDB post data: {str(e)}")

    def to_dict_summary(self) -> Dict[str, Any]:
        """
        검색 결과용 요약 데이터를 반환합니다.

        Returns:
            Dict[str, Any]: 요약된 게시물 데이터
        """
        return {
            "post_id": self.post_id,
            "title": self.title,
            "description": self.description,
            "topic": self.topic,
            "mainCategory": self.mainCategory,
            "subCategory": self.subCategory,
            "tags": self.tags,
            "author": self.author,
            "language": self.language,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
