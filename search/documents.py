"""
VansDevBlog Search Service Elasticsearch Documents

Elasticsearch 문서 스키마와 인덱스 매핑을 정의합니다.
한국어/영어 다국어 검색을 위한 Nori 분석기를 포함합니다.
"""

from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger('search')

# =============================================================================
# Elasticsearch 인덱스 설정
# =============================================================================

# 게시물 인덱스 설정
posts_index = Index('vans_posts')
posts_index.settings(
    number_of_shards=1,
    number_of_replicas=0,  # 개발 환경에서는 복제본 없음
    max_result_window=10000,  # 최대 검색 결과 수
    # 한국어 분석기 설정
    analysis={
        'analyzer': {
            'korean_analyzer': {
                'type': 'custom',
                'tokenizer': 'nori_tokenizer',
                'filter': [
                    'lowercase',
                    'nori_part_of_speech',
                    'nori_readingform',
                    'stop'
                ]
            },
            'english_analyzer': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'stop',
                    'snowball'
                ]
            },
            'search_analyzer': {
                'type': 'custom',
                'tokenizer': 'keyword',
                'filter': ['lowercase']
            }
        },
        'tokenizer': {
            'nori_tokenizer': {
                'type': 'nori_tokenizer',
                'decompound_mode': 'mixed'
            }
        },
        'filter': {
            'nori_part_of_speech': {
                'type': 'nori_part_of_speech',
                'stoptags': ['E', 'IC', 'J', 'MAG', 'MAJ', 'MM', 'SP', 'SSC', 'SSO', 'SC', 'SE', 'XPN', 'XSA', 'XSN', 'XSV', 'UNA', 'NA', 'VSV']
            },
            'stop': {
                'type': 'stop',
                'stopwords': ['_korean_', '_english_']
            }
        }
    }
)


@registry.register_document
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
    post_id = fields.KeywordField(
        attr='post_id',
        help_text="MongoDB ObjectId 문자열"
    )
    
    # 제목 - 다국어 분석
    title = fields.TextField(
        analyzer='korean_analyzer',
        search_analyzer='korean_analyzer',
        fields={
            'english': fields.TextField(
                analyzer='english_analyzer',
                search_analyzer='english_analyzer'
            ),
            'raw': fields.KeywordField(),  # 정확한 매칭용
            'suggest': fields.CompletionField()  # 자동완성용
        },
        help_text="게시물 제목 (한국어/영어 분석 지원)"
    )
    
    # 내용 - 다국어 분석
    content = fields.TextField(
        analyzer='korean_analyzer',
        search_analyzer='korean_analyzer',
        fields={
            'english': fields.TextField(
                analyzer='english_analyzer',
                search_analyzer='english_analyzer'
            )
        },
        help_text="게시물 본문 내용"
    )
    
    # 요약
    summary = fields.TextField(
        analyzer='korean_analyzer',
        search_analyzer='korean_analyzer',
        fields={
            'english': fields.TextField(
                analyzer='english_analyzer'
            )
        },
        help_text="게시물 요약"
    )
    
    # URL 슬러그
    slug = fields.KeywordField(
        help_text="URL 슬러그"
    )
    
    # 카테고리 - 키워드 검색
    category = fields.KeywordField(
        fields={
            'text': fields.TextField(analyzer='keyword')
        },
        help_text="게시물 카테고리"
    )
    
    # 태그 - 배열 키워드
    tags = fields.KeywordField(
        multi=True,
        fields={
            'suggest': fields.CompletionField()  # 태그 자동완성
        },
        help_text="게시물 태그 목록"
    )
    
    # 작성자 정보
    author = fields.ObjectField(
        properties={
            'user_id': fields.KeywordField(),
            'username': fields.KeywordField(),
            'display_name': fields.TextField(analyzer='keyword'),
            'profile_image': fields.KeywordField()
        },
        help_text="작성자 정보"
    )
    
    # 날짜 필드
    published_date = fields.DateField(
        help_text="게시물 발행일"
    )
    
    updated_date = fields.DateField(
        help_text="게시물 수정일"
    )
    
    # 통계 필드
    view_count = fields.IntegerField(
        help_text="조회수"
    )
    
    like_count = fields.IntegerField(
        help_text="좋아요 수"
    )
    
    comment_count = fields.IntegerField(
        help_text="댓글 수"
    )
    
    # 상태 필드
    is_published = fields.BooleanField(
        help_text="발행 여부"
    )
    
    # 언어 코드
    language = fields.KeywordField(
        help_text="언어 코드 (ko, en)"
    )
    
    # 기타 메타데이터
    reading_time = fields.IntegerField(
        help_text="예상 읽기 시간 (분)"
    )
    
    featured_image = fields.KeywordField(
        help_text="대표 이미지 URL"
    )
    
    meta_description = fields.TextField(
        analyzer='korean_analyzer',
        help_text="SEO 메타 설명"
    )
    
    # 검색 점수 부스팅용 필드
    search_boost = fields.FloatField(
        help_text="검색 결과 부스팅 점수"
    )
    
    class Index:
        """Elasticsearch 인덱스 설정"""
        name = 'vans_posts'
        settings = posts_index._settings
    
    class Django:
        """Django 모델 연결 설정 (현재는 MongoDB 사용하므로 비활성화)"""
        # model = Post  # Django ORM 모델이 있다면 연결
        pass
    
    def save(self, **kwargs) -> 'PostDocument':
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
    def create_from_mongo_post(cls, mongo_post: Dict[str, Any]) -> 'PostDocument':
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
            post_id = str(mongo_post.get('_id', ''))
            
            # 작성자 정보 추출
            author_data = mongo_post.get('author', {})
            author = {
                'user_id': str(author_data.get('_id', '')),
                'username': author_data.get('username', ''),
                'display_name': author_data.get('display_name', ''),
                'profile_image': author_data.get('profile_image', '')
            }
            
            # 언어 감지 (한국어 포함 여부로 판단)
            title = mongo_post.get('title', '')
            content = mongo_post.get('content', '')
            language = 'ko' if any('\uAC00' <= char <= '\uD7A3' for char in title + content) else 'en'
            
            # 읽기 시간 계산 (단어 수 기준)
            word_count = len(content.split())
            reading_time = max(1, word_count // 200)  # 분당 200단어 기준
            
            return cls(
                meta={'id': post_id},
                post_id=post_id,
                title=title,
                content=content,
                summary=mongo_post.get('summary', ''),
                slug=mongo_post.get('slug', ''),
                category=mongo_post.get('category', ''),
                tags=mongo_post.get('tags', []),
                author=author,
                published_date=mongo_post.get('published_date'),
                updated_date=mongo_post.get('updated_date'),
                view_count=mongo_post.get('view_count', 0),
                like_count=mongo_post.get('like_count', 0),
                comment_count=mongo_post.get('comment_count', 0),
                is_published=mongo_post.get('is_published', False),
                language=language,
                reading_time=reading_time,
                featured_image=mongo_post.get('featured_image', ''),
                meta_description=mongo_post.get('meta_description', ''),
                search_boost=mongo_post.get('search_boost', 1.0)
            )
            
        except Exception as e:
            logger.error(f"Failed to create PostDocument from mongo data: {str(e)}")
            raise ValueError(f"Invalid MongoDB post data: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        문서를 딕셔너리로 변환합니다.
        
        Returns:
            Dict[str, Any]: 문서 데이터 딕셔너리
        """
        return self.to_dict()


# =============================================================================
# 자동완성용 Suggestion Document
# =============================================================================

suggestions_index = Index('vans_suggestions')
suggestions_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@registry.register_document
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
    
    suggestion = fields.CompletionField(
        contexts=[
            {
                'name': 'type',
                'type': 'category'
            },
            {
                'name': 'language',
                'type': 'category'
            }
        ]
    )
    
    type = fields.KeywordField(
        help_text="제안 타입: query, category, tag, title"
    )
    
    frequency = fields.IntegerField(
        help_text="사용 빈도"
    )
    
    language = fields.KeywordField(
        help_text="언어 코드"
    )
    
    class Index:
        name = 'vans_suggestions'
        settings = suggestions_index._settings
