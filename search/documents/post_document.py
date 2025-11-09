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
        topic (str): 게시물 주제
        description (str): 게시물 설명
        mainCategory (str): 메인 카테고리 (기존 테마)
        subCategory (str): 서브 카테고리 (기존 카테고리)
        tags (List[str]): 태그 목록
        authorEmail (str): 작성자 이메일
        viewCount (int): 조회수
        likeCount (int): 좋아요 수
        thumbnail (str): 썸네일 이미지 URL
        language (str): 언어 코드 (ko, en)
        updated_date (datetime): 수정일
        slug (str): URL 슬러그 (옵션)
        reading_time (int): 예상 읽기 시간 (분)
        search_boost (float): 검색 가중치

    Example:
        >>> # 문서 생성
        >>> post_doc = PostDocument(
        ...     post_id="507f1f77bcf86cd799439011",
        ...     title="Django와 Elasticsearch 연동하기",
        ...     content="Django 프로젝트에서 Elasticsearch를...",
        ...     mainCategory="Backend",
        ...     subCategory="Framework",
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

    # === 검색 핵심 필드 ===
    # 주제 - 키워드 검색 (높은 가중치)
    topic = Text(
        analyzer=korean_analyzer, 
        fields={
            "english": Text(analyzer=english_analyzer),
            "keyword": Keyword(),  # 정확한 매칭용
            "suggest": Completion()  # 자동완성용
        }
    )

    # 설명 - 다국어 분석 (중간 가중치)
    description = Text(
        analyzer=korean_analyzer, 
        fields={
            "english": Text(analyzer=english_analyzer),
            "suggest": Completion()
        }
    )

    # === 분류 필드 (필터링용) ===
    # 메인 카테고리 (기존 테마) - 정확한 필터링
    mainCategory = Keyword(fields={"suggest": Completion()})

    # 서브 카테고리 (기존 카테고리) - 정확한 필터링  
    subCategory = Keyword(fields={"suggest": Completion()})

    # 태그 - 배열 키워드 (검색 + 필터링)
    tags = Keyword(multi=True, fields={"suggest": Completion()})

    # === 메타데이터 (필터링/정렬용만) ===
    # 작성자 이메일 (필터링용)
    authorEmail = Keyword()

    # 언어 코드 (필터링용)
    language = Keyword()

    # 날짜 필드 (정렬용)
    updated_date = Date()

    # 통계 필드 (정렬용만 - 검색에는 불필요)
    viewCount = Integer(index=False)  # 검색 불가, 정렬만 가능
    likeCount = Integer(index=False)  # 검색 불가, 정렬만 가능

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
                mainCategory=mongo_post.get("mainCategory", ""),
                subCategory=mongo_post.get("subCategory", ""),
                tags=mongo_post.get("tags", []),
                authorEmail=mongo_post.get("authorEmail", ""),
                updated_date=mongo_post.get("updatedAt", mongo_post.get("updated_date")),
                viewCount=mongo_post.get("viewCount", 0),
                likeCount=mongo_post.get("likeCount", 0),
                language=mongo_post.get("language", "ko"),
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
            "authorEmail": self.authorEmail,
            "viewCount": self.viewCount,
            "likeCount": self.likeCount,
            "language": self.language,
        }
