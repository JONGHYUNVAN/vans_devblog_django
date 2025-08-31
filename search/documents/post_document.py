"""
VansDevBlog Search Service Post Document

블로그 게시물 Elasticsearch 문서를 정의합니다.
"""

import logging
from typing import Any, Dict

from elasticsearch_dsl import (
    Boolean,
    Completion,
    Date,
    Document,
    Float,
    Integer,
    Keyword,
    Object,
    Text,
)

from .analyzers import BASE_INDEX_SETTINGS, english_analyzer, korean_analyzer

logger = logging.getLogger("search")


class PostDocument(Document):
    """
    블로그 게시물 Elasticsearch 문서 클래스.

    MongoDB의 Post 컬렉션 데이터를 Elasticsearch에 매핑하여
    한국어/영어 다국어 검색과 고급 필터링을 지원합니다.

    Attributes:
        post_id (str): MongoDB ObjectId 문자열
        title (str): 게시물 제목 (한국어/영어 분석)
        content (str): 게시물 내용 (한국어/영어 분석)
        summary (str): 게시물 요약
        slug (str): URL 슬러그
        theme (str): 테마 (카테고리 상위 개념)
        category (str): 카테고리 (키워드 검색)
        tags (List[str]): 태그 목록
        author (Dict): 작성자 정보
        updated_date (datetime): 수정일
        view_count (int): 조회수
        comment_count (int): 댓글 수
        language (str): 언어 코드 (ko, en)
        reading_time (int): 예상 읽기 시간 (분)
        featured_image (str): 대표 이미지 URL
        meta_description (str): SEO 메타 설명
        search_boost (float): 검색 가중치

    Example:
        >>> # 문서 생성
        >>> post_doc = PostDocument(
        ...     post_id="507f1f77bcf86cd799439011",
        ...     title="Django와 Elasticsearch 연동하기",
        ...     content="Django 프로젝트에서 Elasticsearch를...",
        ...     category="Backend",
        ...     tags=["Django", "Elasticsearch", "Python"]
        ... )
        >>> post_doc.save()

        >>> # 검색 수행
        >>> results = PostDocument.search().query("match", title="Django")
    """

    # 기본 식별자
    post_id = Keyword()

    # 제목 - 다국어 분석
    title = Text(
        analyzer=korean_analyzer,
        fields={
            "english": Text(analyzer=english_analyzer),
            "raw": Keyword(),
            "suggest": Completion(),
        },
    )

    # 내용 - 다국어 분석
    content = Text(
        analyzer=korean_analyzer, fields={"english": Text(analyzer=english_analyzer)}
    )

    # 요약
    summary = Text(
        analyzer=korean_analyzer, fields={"english": Text(analyzer=english_analyzer)}
    )

    # URL 슬러그
    slug = Keyword()

    # 주제 - 키워드 검색 (카테고리 상위 개념)
    topic = Keyword(fields={"text": Text(analyzer="keyword")})

    # 카테고리 - 키워드 검색
    category = Keyword(fields={"text": Text(analyzer="keyword")})

    # 설명
    description = Text(
        analyzer=korean_analyzer, fields={"english": Text(analyzer=english_analyzer)}
    )

    # 태그 - 배열 키워드
    tags = Keyword(multi=True, fields={"suggest": Completion()})

    # 작성자 이메일
    author_email = Keyword()

    # 날짜 필드
    updated_date = Date()

    # 통계 필드
    view_count = Integer()
    like_count = Integer()

    # 테마
    theme = Keyword(fields={"text": Text(analyzer="keyword")})

    # 언어 코드
    language = Keyword()

    # 썸네일 이미지
    thumbnail = Keyword()

    # 기타 메타데이터
    reading_time = Integer()
    search_boost = Float()

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

        Args:
            mongo_post (Dict[str, Any]): MongoDB Post 문서 데이터

        Returns:
            PostDocument: 생성된 PostDocument 인스턴스
        """
        try:
            # MongoDB ObjectId를 문자열로 변환
            post_id = str(mongo_post.get("_id", ""))

            # 제목과 내용 추출 및 문자열 변환
            title = str(mongo_post.get("title", ""))
            content_raw = mongo_post.get("content", "")
            
            # content가 dict/object인 경우 문자열로 변환
            if isinstance(content_raw, dict):
                content = str(content_raw)
            elif isinstance(content_raw, str):
                content = content_raw
            else:
                content = str(content_raw)
            
            # 언어 감지 (한국어 포함 여부로 판단)
            language = (
                "ko"
                if any("\uAC00" <= char <= "\uD7A3" for char in title + content)
                else "en"
            )

            # 읽기 시간 계산 (단어 수 기준) - 문자열만 처리
            try:
                word_count = len(content.split()) if content else 0
                reading_time = max(1, word_count // 200)  # 분당 200단어 기준
            except:
                reading_time = 1

            return cls(
                meta={"id": post_id},
                post_id=post_id,
                title=title,
                content=content,
                description=mongo_post.get("description", ""),
                topic=mongo_post.get("topic", ""),
                category=mongo_post.get("category", ""),
                tags=mongo_post.get("tags", []),
                author_email=mongo_post.get("authorEmail", ""),
                updated_date=mongo_post.get("updatedAt", mongo_post.get("updated_date")),
                view_count=mongo_post.get("viewCount", 0),
                like_count=mongo_post.get("likeCount", 0),
                theme=mongo_post.get("theme", ""),
                language=mongo_post.get("language", "ko"),
                thumbnail=mongo_post.get("thumbnail", ""),
                reading_time=reading_time,
                search_boost=1.0,
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
            "category": self.category,
            "tags": self.tags,
            "author_email": self.author_email,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "reading_time": self.reading_time,
            "thumbnail": self.thumbnail,
        }
