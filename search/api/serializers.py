"""
VansDevBlog Search Service Serializers

Django REST Framework용 시리얼라이저를 정의합니다.
"""



from rest_framework import serializers


class AuthorSerializer(serializers.Serializer):
    """
    작성자 정보 시리얼라이저.

    Attributes:
        user_id (str): 사용자 ID
        username (str): 사용자 이름
        display_name (str): 표시 이름
        profile_image (str): 프로필 이미지 URL

    Example:
        >>> author_data = {
        ...     "user_id": "123",
        ...     "username": "vansdev",
        ...     "display_name": "VansDev",
        ...     "profile_image": "https://example.com/avatar.jpg"
        ... }
        >>> serializer = AuthorSerializer(data=author_data)
        >>> serializer.is_valid()
        True
    """

    user_id = serializers.CharField(max_length=50, help_text="사용자 ID")
    username = serializers.CharField(max_length=100, help_text="사용자 이름")
    display_name = serializers.CharField(
        max_length=100, allow_blank=True, help_text="표시 이름"
    )
    profile_image = serializers.URLField(
        allow_blank=True, required=False, help_text="프로필 이미지 URL"
    )


class PostDocumentSerializer(serializers.Serializer):
    """
    게시물 문서 시리얼라이저.

    Elasticsearch PostDocument를 JSON으로 직렬화/역직렬화합니다.

    Attributes:
        post_id (str): 게시물 ID
        title (str): 제목
        content (str): 내용
        summary (str): 요약
        slug (str): URL 슬러그
        category (str): 카테고리
        tags (List[str]): 태그 목록
        author (Dict): 작성자 정보
        published_date (datetime): 발행일
        updated_date (datetime): 수정일
        view_count (int): 조회수
        like_count (int): 좋아요 수
        comment_count (int): 댓글 수
        is_published (bool): 발행 여부
        language (str): 언어 코드
        reading_time (int): 읽기 시간
        featured_image (str): 대표 이미지
        meta_description (str): 메타 설명
        search_boost (float): 검색 부스트 점수

    Example:
        >>> post_data = {
        ...     "post_id": "507f1f77bcf86cd799439011",
        ...     "title": "Django Tutorial",
        ...     "content": "Django is a web framework...",
        ...     "category": "Backend",
        ...     "tags": ["Django", "Python"]
        ... }
        >>> serializer = PostDocumentSerializer(data=post_data)
        >>> serializer.is_valid()
        True
    """

    # 기본 필드
    post_id = serializers.CharField(
        max_length=100, help_text="게시물 ID (MongoDB ObjectId)"
    )
    title = serializers.CharField(max_length=200, help_text="게시물 제목")
    content = serializers.CharField(help_text="게시물 내용")
    summary = serializers.CharField(
        max_length=500, allow_blank=True, required=False, help_text="게시물 요약"
    )
    slug = serializers.CharField(
        max_length=200, allow_blank=True, required=False, help_text="URL 슬러그"
    )

    # 분류 필드
    category = serializers.CharField(
        max_length=100, allow_blank=True, required=False, help_text="카테고리"
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        help_text="태그 목록",
    )

    # 작성자 정보
    author = AuthorSerializer(required=False, help_text="작성자 정보")

    # 날짜 필드
    published_date = serializers.DateTimeField(required=False, help_text="발행일")
    updated_date = serializers.DateTimeField(required=False, help_text="수정일")

    # 통계 필드
    view_count = serializers.IntegerField(default=0, min_value=0, help_text="조회수")
    like_count = serializers.IntegerField(default=0, min_value=0, help_text="좋아요 수")
    comment_count = serializers.IntegerField(default=0, min_value=0, help_text="댓글 수")

    # 상태 필드
    is_published = serializers.BooleanField(default=False, help_text="발행 여부")
    language = serializers.CharField(
        max_length=10, default="ko", help_text="언어 코드 (ko, en)"
    )

    # 메타데이터
    reading_time = serializers.IntegerField(
        default=1, min_value=1, help_text="예상 읽기 시간 (분)"
    )
    featured_image = serializers.URLField(
        allow_blank=True, required=False, help_text="대표 이미지 URL"
    )
    meta_description = serializers.CharField(
        max_length=300, allow_blank=True, required=False, help_text="SEO 메타 설명"
    )
    search_boost = serializers.FloatField(
        default=1.0, min_value=0.1, max_value=10.0, help_text="검색 결과 부스트 점수"
    )


class SearchRequestSerializer(serializers.Serializer):
    """
    검색 요청 시리얼라이저.

    검색 API 요청 파라미터를 검증합니다.

    Attributes:
        query (str): 검색 키워드
        category (str): 카테고리 필터
        tags (List[str]): 태그 필터
        language (str): 언어 필터
        date_from (datetime): 시작 날짜
        date_to (datetime): 종료 날짜
        page (int): 페이지 번호
        page_size (int): 페이지 크기
        sort (str): 정렬 방식

    Example:
        >>> request_data = {
        ...     "query": "Django",
        ...     "category": "Backend",
        ...     "page": 1,
        ...     "page_size": 20
        ... }
        >>> serializer = SearchRequestSerializer(data=request_data)
        >>> serializer.is_valid()
        True
    """

    query = serializers.CharField(
        max_length=200, required=False, allow_blank=True, help_text="검색 키워드"
    )
    theme = serializers.CharField(
        max_length=100, required=False, allow_blank=True, help_text="테마 필터 (카테고리 상위 개념)"
    )
    category = serializers.CharField(
        max_length=100, required=False, allow_blank=True, help_text="카테고리 필터"
    )
    tags = serializers.CharField(
        required=False, allow_blank=True, help_text="태그 필터 (쉼표로 구분)"
    )
    language = serializers.ChoiceField(
        choices=[("ko", "한국어"), ("en", "English"), ("all", "전체")],
        default="all",
        help_text="언어 필터",
    )
    date_from = serializers.DateTimeField(required=False, help_text="검색 시작 날짜")
    date_to = serializers.DateTimeField(required=False, help_text="검색 종료 날짜")
    page = serializers.IntegerField(default=1, min_value=1, help_text="페이지 번호")
    page_size = serializers.IntegerField(
        default=20, min_value=1, max_value=100, help_text="페이지 크기"
    )
    sort = serializers.ChoiceField(
        choices=[
            ("relevance", "관련도"),
            ("date_desc", "최신순"),
            ("date_asc", "오래된순"),
            ("views_desc", "조회수순"),
            ("likes_desc", "좋아요순"),
        ],
        default="relevance",
        help_text="정렬 방식",
    )

    def validate_tags(self, value):
        """
        태그 필터를 검증하고 리스트로 변환합니다.

        Args:
            value (str): 쉼표로 구분된 태그 문자열

        Returns:
            List[str]: 태그 목록
        """
        if not value:
            return []

        tags = [tag.strip() for tag in value.split(",") if tag.strip()]
        return tags[:10]  # 최대 10개 태그로 제한

    def validate(self, attrs):
        """
        전체 데이터를 검증합니다.

        Args:
            attrs (Dict): 검증할 데이터

        Returns:
            Dict: 검증된 데이터

        Raises:
            ValidationError: 검증 실패
        """
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("시작 날짜는 종료 날짜보다 이전이어야 합니다.")

        return attrs


class SearchResultSerializer(serializers.Serializer):
    """
    검색 결과 시리얼라이저.

    검색 API 응답을 직렬화합니다.

    Attributes:
        id (str): 문서 ID
        score (float): 검색 점수
        source (Dict): 문서 소스 데이터
        highlight (Dict): 하이라이트된 부분

    Example:
        >>> result = {
        ...     "id": "507f1f77bcf86cd799439011",
        ...     "score": 1.5,
        ...     "source": {...},
        ...     "highlight": {"title": ["<em>Django</em> Tutorial"]}
        ... }
        >>> serializer = SearchResultSerializer(result)
    """

    post_id = serializers.CharField(help_text="MongoDB 게시물 ID")
    score = serializers.FloatField(help_text="검색 관련도 점수")


class SearchResponseSerializer(serializers.Serializer):
    """
    검색 응답 시리얼라이저.

    전체 검색 응답을 직렬화합니다.

    Attributes:
        total (int): 전체 결과 수
        page (int): 현재 페이지
        page_size (int): 페이지 크기
        results (List): 검색 결과 목록
        aggregations (Dict): 집계 정보

    Example:
        >>> response = {
        ...     "total": 100,
        ...     "page": 1,
        ...     "page_size": 20,
        ...     "results": [...],
        ...     "aggregations": {...}
        ... }
        >>> serializer = SearchResponseSerializer(response)
    """

    total = serializers.IntegerField(help_text="전체 검색 결과 수")
    page = serializers.IntegerField(help_text="현재 페이지 번호")
    page_size = serializers.IntegerField(help_text="페이지 크기")
    total_pages = serializers.IntegerField(help_text="전체 페이지 수")
    results = SearchResultSerializer(many=True, help_text="검색 결과 목록")
    aggregations = serializers.DictField(required=False, help_text="카테고리, 태그 등 집계 정보")


class AutocompleteRequestSerializer(serializers.Serializer):
    """
    자동완성 요청 시리얼라이저.

    Attributes:
        query (str): 자동완성할 검색어
        language (str): 언어 필터
        limit (int): 결과 개수 제한

    Example:
        >>> request = {
        ...     "query": "Djan",
        ...     "language": "ko",
        ...     "limit": 10
        ... }
        >>> serializer = AutocompleteRequestSerializer(data=request)
    """

    query = serializers.CharField(max_length=100, min_length=1, help_text="자동완성할 검색어")
    language = serializers.ChoiceField(
        choices=[("ko", "한국어"), ("en", "English"), ("all", "전체")],
        default="all",
        help_text="언어 필터",
    )
    limit = serializers.IntegerField(
        default=10, min_value=1, max_value=20, help_text="반환할 제안 수"
    )


class AutocompleteResponseSerializer(serializers.Serializer):
    """
    자동완성 응답 시리얼라이저.

    Attributes:
        suggestions (List[str]): 자동완성 제안 목록
        query (str): 원본 검색어

    Example:
        >>> response = {
        ...     "suggestions": ["Django", "Django REST", "Django Tutorial"],
        ...     "query": "Djan"
        ... }
        >>> serializer = AutocompleteResponseSerializer(response)
    """

    suggestions = serializers.ListField(
        child=serializers.CharField(), help_text="자동완성 제안 목록"
    )
    query = serializers.CharField(help_text="원본 검색어")


class PopularSearchesResponseSerializer(serializers.Serializer):
    """
    인기 검색어 응답 시리얼라이저.

    Attributes:
        popular_searches (List[Dict]): 인기 검색어 목록

    Example:
        >>> response = {
        ...     "popular_searches": [
        ...         {"query": "Django", "count": 150},
        ...         {"query": "Python", "count": 120}
        ...     ]
        ... }
        >>> serializer = PopularSearchesResponseSerializer(response)
    """

    popular_searches = serializers.ListField(
        child=serializers.DictField(), help_text="인기 검색어 목록 (query, count 포함)"
    )


class SyncRequestSerializer(serializers.Serializer):
    """
    데이터 동기화 요청 시리얼라이저.

    MongoDB에서 Elasticsearch로 데이터를 동기화하는 요청을 검증합니다.

    Attributes:
        batch_size (int): 배치 처리 크기
        force_all (bool): 발행 여부 무관 전체 동기화
        incremental (bool): 증분 동기화 여부
        days (int): 증분 동기화 시 확인할 일수
        clear_existing (bool): 기존 데이터 삭제 여부
        dry_run (bool): 실제 동기화 없이 확인만

    Example:
        >>> request_data = {
        ...     "batch_size": 50,
        ...     "force_all": False,
        ...     "incremental": True,
        ...     "days": 7
        ... }
        >>> serializer = SyncRequestSerializer(data=request_data)
        >>> serializer.is_valid()
        True
    """

    batch_size = serializers.IntegerField(
        default=50, min_value=1, max_value=500, help_text="배치 처리 크기 (기본값: 50)"
    )
    force_all = serializers.BooleanField(
        default=False, help_text="발행 여부와 관계없이 모든 게시물을 동기화합니다."
    )
    incremental = serializers.BooleanField(
        default=False, help_text="증분 동기화: 최근 업데이트된 게시물만 동기화합니다."
    )
    days = serializers.IntegerField(
        default=7, min_value=1, max_value=365, help_text="증분 동기화 시 확인할 일수 (기본값: 7일)"
    )
    clear_existing = serializers.BooleanField(
        default=False, help_text="기존 Elasticsearch 데이터를 모두 삭제하고 새로 동기화합니다."
    )
    dry_run = serializers.BooleanField(
        default=False, help_text="실제 동기화 없이 처리할 데이터만 확인합니다."
    )

    def validate(self, attrs):
        """
        전체 데이터를 검증합니다.

        Args:
            attrs (Dict): 검증할 데이터

        Returns:
            Dict: 검증된 데이터

        Raises:
            ValidationError: 검증 실패
        """
        if attrs.get("incremental") and attrs.get("force_all"):
            raise serializers.ValidationError(
                "incremental과 force_all 옵션은 동시에 사용할 수 없습니다."
            )

        return attrs


class SyncResponseSerializer(serializers.Serializer):
    """
    데이터 동기화 응답 시리얼라이저.

    동기화 결과를 직렬화합니다.

    Attributes:
        status (str): 동기화 상태
        type (str): 동기화 타입 (full/incremental)
        processed (int): 처리된 게시물 수
        synced (int): 동기화 성공한 게시물 수
        skipped (int): 건너뛴 게시물 수
        errors (int): 오류 발생한 게시물 수
        success_rate (float): 성공률
        execution_time (float): 실행 시간 (초)
        message (str): 결과 메시지

    Example:
        >>> response = {
        ...     "status": "completed",
        ...     "type": "incremental",
        ...     "processed": 100,
        ...     "synced": 95,
        ...     "skipped": 3,
        ...     "errors": 2,
        ...     "success_rate": 95.0,
        ...     "execution_time": 15.5,
        ...     "message": "동기화가 성공적으로 완료되었습니다."
        ... }
        >>> serializer = SyncResponseSerializer(response)
    """

    status = serializers.ChoiceField(
        choices=[
            ("started", "시작됨"),
            ("completed", "완료됨"),
            ("failed", "실패"),
            ("partial", "부분 완료"),
        ],
        help_text="동기화 상태",
    )
    type = serializers.ChoiceField(
        choices=[("full", "전체 동기화"), ("incremental", "증분 동기화")],
        help_text="동기화 타입",
    )
    processed = serializers.IntegerField(help_text="처리된 게시물 수")
    synced = serializers.IntegerField(help_text="동기화 성공한 게시물 수")
    skipped = serializers.IntegerField(help_text="건너뛴 게시물 수")
    errors = serializers.IntegerField(help_text="오류 발생한 게시물 수")
    success_rate = serializers.FloatField(help_text="성공률 (%)")
    execution_time = serializers.FloatField(help_text="실행 시간 (초)")
    message = serializers.CharField(help_text="결과 메시지")


class SyncStatusSerializer(serializers.Serializer):
    """
    동기화 상태 조회 응답 시리얼라이저.

    현재 동기화 상태 정보를 직렬화합니다.

    Attributes:
        mongodb_connected (bool): MongoDB 연결 상태
        elasticsearch_connected (bool): Elasticsearch 연결 상태
        total_posts_in_mongodb (int): MongoDB 총 게시물 수
        published_posts_in_mongodb (int): MongoDB 발행된 게시물 수
        total_docs_in_elasticsearch (int): Elasticsearch 총 문서 수
        last_sync_time (datetime): 마지막 동기화 시간
        sync_needed (bool): 동기화 필요 여부

    Example:
        >>> status = {
        ...     "mongodb_connected": True,
        ...     "elasticsearch_connected": True,
        ...     "total_posts_in_mongodb": 500,
        ...     "published_posts_in_mongodb": 450,
        ...     "total_docs_in_elasticsearch": 440,
        ...     "sync_needed": True
        ... }
        >>> serializer = SyncStatusSerializer(status)
    """

    mongodb_connected = serializers.BooleanField(help_text="MongoDB 연결 상태")
    elasticsearch_connected = serializers.BooleanField(help_text="Elasticsearch 연결 상태")
    total_posts_in_mongodb = serializers.IntegerField(help_text="MongoDB 총 게시물 수")
    published_posts_in_mongodb = serializers.IntegerField(help_text="MongoDB 발행된 게시물 수")
    total_docs_in_elasticsearch = serializers.IntegerField(help_text="Elasticsearch 총 문서 수")
    last_sync_time = serializers.DateTimeField(
        required=False, allow_null=True, help_text="마지막 동기화 시간"
    )
    sync_needed = serializers.BooleanField(help_text="동기화 필요 여부")
