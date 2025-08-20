"""
VansDevBlog Search Service Post Document

블로그 게시물 Elasticsearch 문서를 정의합니다.
"""

from elasticsearch_dsl import Document, Text, Keyword, Integer, Boolean, Date, Float, Object, Completion
from typing import Dict, Any
import logging

from .analyzers import korean_analyzer, english_analyzer, BASE_INDEX_SETTINGS

logger = logging.getLogger('search')


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
            'english': Text(analyzer=english_analyzer),
            'raw': Keyword(),
            'suggest': Completion()
        }
    )
    
    # 내용 - 다국어 분석
    content = Text(
        analyzer=korean_analyzer,
        fields={
            'english': Text(analyzer=english_analyzer)
        }
    )
    
    # 요약
    summary = Text(
        analyzer=korean_analyzer,
        fields={
            'english': Text(analyzer=english_analyzer)
        }
    )
    
    # URL 슬러그
    slug = Keyword()
    
    # 테마 - 키워드 검색 (카테고리 상위 개념)
    theme = Keyword(
        fields={
            'text': Text(analyzer='keyword')
        }
    )
    
    # 카테고리 - 키워드 검색
    category = Keyword(
        fields={
            'text': Text(analyzer='keyword')
        }
    )
    
    # 태그 - 배열 키워드
    tags = Keyword(
        multi=True,
        fields={
            'suggest': Completion()
        }
    )
    
    # 작성자 정보
    author = Object(
        properties={
            'user_id': Keyword(),
            'username': Keyword(),
            'display_name': Text(analyzer='keyword'),
            'profile_image': Keyword()
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
        """Elasticsearch 인덱스 설정."""
        name = 'vans_posts'
        settings = BASE_INDEX_SETTINGS
    
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
                theme=mongo_post.get('theme', ''),
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
    
    def to_dict_summary(self) -> Dict[str, Any]:
        """
        검색 결과용 요약 데이터를 반환합니다.
        
        Returns:
            Dict[str, Any]: 요약된 게시물 데이터
        """
        return {
            'post_id': self.post_id,
            'title': self.title,
            'summary': self.summary,
            'category': self.category,
            'tags': self.tags,
            'author': {
                'username': self.author.username if self.author else '',
                'display_name': self.author.display_name if self.author else ''
            },
            'published_date': self.published_date,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'reading_time': self.reading_time,
            'featured_image': self.featured_image
        }

