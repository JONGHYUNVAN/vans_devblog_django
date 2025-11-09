"""
VansDevBlog Search Service Elasticsearch Documents

Elasticsearch 문서 스키마와 인덱스 매핑을 정의합니다.
한국어/영어 다국어 검색을 위한 Nori 분석기를 포함합니다.
"""

import logging
from .utils.pm_plain import tiptap_to_plain

logger = logging.getLogger("search")

# =============================================================================
# Elasticsearch 연결 설정
# =============================================================================


def setup_elasticsearch_connection():
    """Elasticsearch 연결을 설정합니다."""
    try:
        es_config = settings.ELASTICSEARCH_DSL["default"]
        connections.create_connection(
            hosts=es_config["hosts"],
            timeout=es_config.get("timeout", 20),
            max_retries=es_config.get("max_retries", 3),
            retry_on_timeout=es_config.get("retry_on_timeout", True),
            verify_certs=es_config.get("verify_certs", True),
            http_auth=es_config.get("http_auth"),
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
        content (str): 게시물 내용 (JSON)
        content_text (str): 게시물 내용 (Plain Text for search)
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

    Example:
        >>> # 문서 생성
        >>> post_doc = PostDocument(
        ...     post_id="507f1f77bcf86cd799439011",
        ...     title="Django와 Elasticsearch 연동하기",
        ...     content_text="Django 프로젝트에서 Elasticsearch를...",
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

    # === 검색 핵심 필드 ===
    # 원본 JSON 컨텐츠 (검색에는 사용하지 않음, 저장만)
    content = Object(enabled=False)

    # 검색 및 하이라이팅을 위한 Plain Text 필드 (가장 중요)
    content_text = Text(
        analyzer=korean_analyzer, 
        fields={
            "english": Text(analyzer=english_analyzer),
            "raw": Keyword()  # 정확한 구문 검색용
        }
    )

    # 주제 - 높은 가중치 검색 필드
    topic = Text(
        analyzer=korean_analyzer,
        fields={
            "english": Text(analyzer=english_analyzer),
            "keyword": Keyword(),  # 정확한 매칭용
            "suggest": Completion()  # 자동완성용
        }
    )

    # 설명 - 중간 가중치 검색 필드
    description = Text(
        analyzer=korean_analyzer, 
        fields={
            "english": Text(analyzer=english_analyzer),
            "suggest": Completion()
        }
    )

    # === 분류 필드 (필터링용) ===
    # 메인 카테고리 - 정확한 필터링
    mainCategory = Keyword(fields={"suggest": Completion()})

    # 서브 카테고리 - 정확한 필터링
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
            # === 성능 최적화된 인덱스 설정 ===
            "number_of_shards": 1,  # 샤드 수
            "number_of_replicas": 0,  # 복제본 수
            "max_result_window": 1000,  # 최대 검색 결과 수 (성능 향상)
            "refresh_interval": "5s",  # 리프레시 간격 증가 (성능 향상)
            "index.mapping.total_fields.limit": 50,  # 필드 수 제한
            "index.max_ngram_diff": 2,  # N-gram 차이 제한
            # === 텍스트 분석 설정 ===
            "analysis": {
                # --- 분석기 (Analyzers) ---
                "analyzer": {
                    # 성능 최적화된 한국어 분석기
                    "korean_analyzer": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",
                        "filter": [
                            "lowercase",
                            "nori_part_of_speech",
                            "nori_readingform",
                            "trim"  # 공백 제거로 성능 향상
                        ],
                    },
                    # 빠른 검색용 분석기 추가
                    "korean_search_analyzer": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",
                        "filter": [
                            "lowercase",
                            "nori_part_of_speech",
                            "trim"
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
                    # 성능 최적화된 토크나이저
                    "nori_tokenizer": {
                        "type": "nori_tokenizer",
                        "decompound_mode": "discard",  # 빠른 처리를 위해 discard 사용
                        "discard_punctuation": True,  # 구두점 제거로 성능 향상
                        "user_dictionary_rules": [  # 필수 용어만 유지
                            "Django",
                            "Elasticsearch", 
                            "React",
                            "Vue.js",
                            "Spring Boot"
                        ],
                    }
                },
                # --- 필터 (Filters) ---
                "filter": {
                    # 성능 최적화된 품사 태그 필터
                    "nori_part_of_speech": {
                        "type": "nori_part_of_speech",
                        "stoptags": [  # 필수 태그만 제외 (성능 향상)
                            "E", "IC", "J", "MAG", "MAJ", "MM", "SP", 
                            "SSC", "SSO", "SC", "SE", "UNA", "NA"
                        ],
                    },
                    # 한국어 읽기 형태 변환 필터
                    "nori_readingform": {"type": "nori_readingform"},
                    # 최소한의 불용어 (성능 향상)
                    "minimal_stop": {
                        "type": "stop",
                        "stopwords": ["이", "그", "저", "이것", "그것", "저것"],  # 최소한의 한국어 불용어
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
        DB에 저장된 실제 snake_case 필드명을 기준으로 정확히 매핑합니다.
        """
        try:
            post_id = str(mongo_post.get("_id", ""))
            title = mongo_post.get("title", "")

            # be_post 구조에 맞춰 데이터를 읽어옵니다.
            content_json = mongo_post.get("content", {})
            topic = mongo_post.get("topic", "")
            description = mongo_post.get("description", "")
            author_email = mongo_post.get("authorEmail", "")
            view_count = mongo_post.get("viewCount", 0)
            like_count = mongo_post.get("likeCount", 0)
            thumbnail = mongo_post.get("thumbnail", "")
            main_category = mongo_post.get("mainCategory", "")
            sub_category = mongo_post.get("subCategory", "")
            updated_at = mongo_post.get("updatedAt", mongo_post.get("updated_date"))

            # 'content' JSON을 일반 텍스트로 파싱합니다.
            content_text = tiptap_to_plain(content_json)

            language = (
                "ko"
                if any("\uAC00" <= char <= "\uD7A3" for char in title + content_text)
                else "en"
            )
            word_count = len(content_text.split())
            reading_time = max(1, word_count // 200)

            # Elasticsearch 문서 스키마에 맞춰 데이터를 채웁니다.
            return cls(
                meta={"id": post_id},
                post_id=post_id,
                title=title,
                content=content_json,
                content_text=content_text,
                topic=topic,
                description=description,
                mainCategory=main_category,
                subCategory=sub_category,
                tags=mongo_post.get("tags", []),
                authorEmail=author_email,
                updated_date=updated_at,
                viewCount=view_count,
                likeCount=like_count,
                language=language,
            )

        except Exception as e:
            logger.error(f"Failed to create PostDocument from mongo data for post_id {post_id}: {str(e)}")
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
