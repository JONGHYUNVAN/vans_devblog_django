"""
VansDevBlog Search Service Elasticsearch Documents

Elasticsearch 문서 스키마와 인덱스 매핑을 정의합니다.
한국어/영어 다국어 검색을 위한 Nori 분석기를 포함합니다.
"""

import logging
from typing import Any, Dict

from django.conf import settings
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
    analyzer,
)
from elasticsearch_dsl.connections import connections

logger = logging.getLogger("search")

# =============================================================================
# Elasticsearch 연결 설정
# =============================================================================


def setup_elasticsearch_connection():
    """Elasticsearch 연결을 설정합니다."""
    try:
        connections.create_connection(
            hosts=settings.ELASTICSEARCH_DSL["default"]["hosts"],
            timeout=settings.ELASTICSEARCH_DSL["default"].get("timeout", 20),
            max_retries=settings.ELASTICSEARCH_DSL["default"].get("max_retries", 3),
            retry_on_timeout=settings.ELASTICSEARCH_DSL["default"].get(
                "retry_on_timeout", True
            ),
        )
        logger.info("Elasticsearch connection established")
    except Exception as e:
        logger.error(f"Failed to establish Elasticsearch connection: {str(e)}")
        raise


# 연결 초기화
setup_elasticsearch_connection()

# =============================================================================
# 분석기 정의
# =============================================================================

# 한국어 분석기 (Nori 토크나이저 사용)
korean_analyzer = analyzer(
    "korean_analyzer",
    tokenizer="nori_tokenizer",
    filter=["lowercase", "nori_part_of_speech", "nori_readingform", "stop"],
)

# 영어 분석기
english_analyzer = analyzer(
    "english_analyzer", tokenizer="standard", filter=["lowercase", "stop", "snowball"]
)

# 검색용 분석기
search_analyzer = analyzer("search_analyzer", tokenizer="keyword", filter=["lowercase"])

# =============================================================================
# 게시물 Document 클래스
# =============================================================================


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
        category (str): 카테고리 (키워드 검색)
        tags (List[str]): 태그 목록
        author (Dict): 작성자 정보
        published_date (datetime): 발행일
        updated_date (datetime): 수정일
        view_count (int): 조회수
        like_count (int): 좋아요 수
        comment_count (int): 댓글 수
        is_published (bool): 발행 여부
        language (str): 언어 코드 (ko, en)
        reading_time (int): 예상 읽기 시간 (분)
        featured_image (str): 대표 이미지 URL
        meta_description (str): SEO 메타 설명

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

    # 테마 - 키워드 검색 (카테고리 상위 개념)
    theme = Keyword(fields={"text": Text(analyzer="keyword")})

    # 카테고리 - 키워드 검색
    category = Keyword(fields={"text": Text(analyzer="keyword")})

    # 태그 - 배열 키워드
    tags = Keyword(multi=True, fields={"suggest": Completion()})

    # 작성자 정보
    author = Object(
        properties={
            "user_id": Keyword(),
            "username": Keyword(),
            "display_name": Text(analyzer="keyword"),
            "profile_image": Keyword(),
        }
    )

    # 날짜 필드
    published_date = Date()
    updated_date = Date()

    # 통계 필드
    view_count = Integer()
    like_count = Integer()
    comment_count = Integer()

    # 상태 필드
    is_published = Boolean()

    # 언어 코드
    language = Keyword()

    # 기타 메타데이터
    reading_time = Integer()
    featured_image = Keyword()
    meta_description = Text(analyzer=korean_analyzer)
    search_boost = Float()

    class Index:
        """Elasticsearch 인덱스 설정.

        vans_posts 인덱스의 설정을 정의합니다.

        Attributes:
            name (str): 인덱스 이름 'vans_posts'
            settings (dict): 인덱스 설정

        Index Settings:
            * **Basic Settings**:
                - number_of_shards: 1 (샤드 수)
                - number_of_replicas: 0 (복제본 수)
                - max_result_window: 10000 (최대 검색 결과 수)

            * **Analysis Configuration**:
                - **korean_analyzer**: 한국어 텍스트 분석
                    * tokenizer: nori_tokenizer (한국어 형태소 분석)
                    * filters: lowercase, nori_part_of_speech, nori_readingform, stop

                - **english_analyzer**: 영어 텍스트 분석
                    * tokenizer: standard (표준 토크나이저)
                    * filters: lowercase, stop, snowball

                - **search_analyzer**: 검색용 분석기
                    * tokenizer: keyword (키워드 토크나이저)
                    * filters: lowercase

            * **Custom Tokenizer**:
                - **nori_tokenizer**: 한국어 형태소 분석기
                    * decompound_mode: mixed (복합어 분해 모드)
                    * user_dictionary_rules: 사용자 정의 사전 (Django, React 등)

            * **Custom Filters**:
                - **nori_part_of_speech**: 품사 태그 필터
                    * stoptags: 제외할 품사 태그 목록

                - **nori_readingform**: 한국어 읽기 형태 변환

                - **stop**: 불용어 제거 (한국어, 영어)
        """

        name = "vans_posts"
        settings = {
            # === 기본 인덱스 설정 ===
            "number_of_shards": 1,  # 샤드 수
            "number_of_replicas": 0,  # 복제본 수
            "max_result_window": 10000,  # 최대 검색 결과 수
            # === 텍스트 분석 설정 ===
            "analysis": {
                # --- 분석기 (Analyzers) ---
                "analyzer": {
                    # 한국어 텍스트 분석기
                    "korean_analyzer": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",  # 한국어 형태소 분석
                        "filter": [
                            "lowercase",  # 소문자 변환
                            "nori_part_of_speech",  # 품사 태그 필터
                            "nori_readingform",  # 읽기 형태 변환
                            "stop",  # 불용어 제거
                        ],
                    },
                    # 영어 텍스트 분석기
                    "english_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",  # 표준 토크나이저
                        "filter": [
                            "lowercase",  # 소문자 변환
                            "stop",  # 불용어 제거
                            "snowball",  # 어간 추출
                        ],
                    },
                    # 검색용 분석기
                    "search_analyzer": {
                        "type": "custom",
                        "tokenizer": "keyword",  # 키워드 토크나이저
                        "filter": ["lowercase"],  # 소문자 변환만
                    },
                },
                # --- 토크나이저 (Tokenizers) ---
                "tokenizer": {
                    # 한국어 형태소 분석 토크나이저
                    "nori_tokenizer": {
                        "type": "nori_tokenizer",
                        "decompound_mode": "mixed",  # 복합어 분해 모드
                        "user_dictionary_rules": [  # 사용자 정의 사전
                            "Django",  # 웹 프레임워크
                            "Elasticsearch",  # 검색 엔진
                            "REST API",  # API 방식
                            "Spring Boot",  # Java 프레임워크
                            "React",  # 프론트엔드 라이브러리
                            "Vue.js",  # 프론트엔드 프레임워크
                        ],
                    }
                },
                # --- 필터 (Filters) ---
                "filter": {
                    # 한국어 품사 태그 필터
                    "nori_part_of_speech": {
                        "type": "nori_part_of_speech",
                        "stoptags": [  # 제외할 품사 태그들
                            "E",  # 어미
                            "IC",  # 감탄사
                            "J",  # 관계언(조사)
                            "MAG",  # 일반 부사
                            "MAJ",  # 접속 부사
                            "MM",  # 관형사
                            "SP",  # 공백
                            "SSC",  # 닫는 괄호
                            "SSO",  # 여는 괄호
                            "SC",  # 구분자
                            "SE",  # 생략 기호
                            "XPN",  # 체언 접두사
                            "XSA",  # 형용사 파생 접미사
                            "XSN",  # 명사 파생 접미사
                            "XSV",  # 동사 파생 접미사
                            "UNA",  # 알 수 없는 문자
                            "NA",  # 분석 불가
                            "VSV",  # 동사
                        ],
                    },
                    # 한국어 읽기 형태 변환 필터
                    "nori_readingform": {"type": "nori_readingform"},
                    # 불용어 제거 필터
                    "stop": {
                        "type": "stop",
                        "stopwords": ["_korean_", "_english_"],  # 한국어/영어 기본 불용어
                    },
                },
            },
        }

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

        Example:
            >>> post_doc = PostDocument(title="Test Post")
            >>> saved_doc = post_doc.save()
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

        Example:
            >>> mongo_data = {
            ...     "_id": ObjectId("507f1f77bcf86cd799439011"),
            ...     "title": "Django Tutorial",
            ...     "content": "Django is a web framework...",
            ...     "category": "Backend"
            ... }
            >>> post_doc = PostDocument.create_from_mongo_post(mongo_data)
        """
        try:
            # MongoDB ObjectId를 문자열로 변환
            post_id = str(mongo_post.get("_id", ""))

            # 작성자 정보 추출
            author_data = mongo_post.get("author", {})
            author = {
                "user_id": str(author_data.get("_id", "")),
                "username": author_data.get("username", ""),
                "display_name": author_data.get("display_name", ""),
                "profile_image": author_data.get("profile_image", ""),
            }

            # 언어 감지 (한국어 포함 여부로 판단)
            title = mongo_post.get("title", "")
            content = mongo_post.get("content", "")
            language = (
                "ko"
                if any("\uAC00" <= char <= "\uD7A3" for char in title + content)
                else "en"
            )

            # 읽기 시간 계산 (단어 수 기준)
            word_count = len(content.split())
            reading_time = max(1, word_count // 200)  # 분당 200단어 기준

            return cls(
                meta={"id": post_id},
                post_id=post_id,
                title=title,
                content=content,
                summary=mongo_post.get("summary", ""),
                slug=mongo_post.get("slug", ""),
                category=mongo_post.get("category", ""),
                tags=mongo_post.get("tags", []),
                author=author,
                published_date=mongo_post.get("published_date"),
                updated_date=mongo_post.get("updated_date"),
                view_count=mongo_post.get("view_count", 0),
                like_count=mongo_post.get("like_count", 0),
                comment_count=mongo_post.get("comment_count", 0),
                is_published=mongo_post.get("is_published", False),
                language=language,
                reading_time=reading_time,
                featured_image=mongo_post.get("featured_image", ""),
                meta_description=mongo_post.get("meta_description", ""),
                search_boost=mongo_post.get("search_boost", 1.0),
            )

        except Exception as e:
            logger.error(f"Failed to create PostDocument from mongo data: {str(e)}")
            raise ValueError(f"Invalid MongoDB post data: {str(e)}")


# =============================================================================
# 자동완성용 Suggestion Document
# =============================================================================


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


# =============================================================================
# 인덱스 초기화 함수
# =============================================================================


def create_indexes():
    """
    Elasticsearch 인덱스를 생성합니다.

    Example:
        >>> create_indexes()
        INFO: Created index: vans_posts
        INFO: Created index: vans_suggestions
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


def delete_indexes():
    """
    Elasticsearch 인덱스를 삭제합니다.

    Example:
        >>> delete_indexes()
        INFO: Deleted index: vans_posts
        INFO: Deleted index: vans_suggestions
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


def rebuild_indexes():
    """
    Elasticsearch 인덱스를 재구축합니다.

    Example:
        >>> rebuild_indexes()
        INFO: Deleted index: vans_posts
        INFO: Created index: vans_posts
        INFO: Deleted index: vans_suggestions
        INFO: Created index: vans_suggestions
    """
    try:
        delete_indexes()
        create_indexes()
        logger.info("Rebuilt all indexes successfully")
    except Exception as e:
        logger.error(f"Failed to rebuild indexes: {str(e)}")
        raise
