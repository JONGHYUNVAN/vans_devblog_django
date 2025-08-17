"""
VansDevBlog Search Service MongoDB Client

MongoDB 연결 및 Post 데이터 조회를 위한 클라이언트 클래스입니다.
"""

from typing import Dict, List, Any, Optional, Iterator
from django.conf import settings
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger('search')


class MongoDBClient:
    """
    MongoDB 연결 및 Post 컬렉션 데이터 조회를 관리하는 클라이언트 클래스.
    
    기존 Post Service의 MongoDB에서 게시물 데이터를 가져와서
    Elasticsearch로 동기화하는 기능을 제공합니다.
    
    Attributes:
        client (MongoClient): MongoDB 클라이언트 인스턴스
        database: MongoDB 데이터베이스 인스턴스
        posts_collection (Collection): 게시물 컬렉션
        
    Example:
        >>> mongo_client = MongoDBClient()
        >>> posts = mongo_client.get_all_published_posts()
        >>> print(f"Found {len(posts)} published posts")
    """
    
    def __init__(self):
        """
        MongoDBClient 인스턴스를 초기화합니다.
        
        Django 설정에서 MongoDB 연결 정보를 가져와서
        클라이언트 연결을 설정합니다.
        
        Raises:
            ConnectionFailure: MongoDB 서버에 연결할 수 없는 경우
        """
        try:
            mongodb_settings = settings.MONGODB_SETTINGS
            
            # MongoDB 연결 URL 구성
            if mongodb_settings.get('username') and mongodb_settings.get('password'):
                connection_url = (
                    f"mongodb://{mongodb_settings['username']}:"
                    f"{mongodb_settings['password']}@"
                    f"{mongodb_settings['host']}:{mongodb_settings['port']}/"
                    f"{mongodb_settings['database']}"
                )
            else:
                connection_url = (
                    f"mongodb://{mongodb_settings['host']}:"
                    f"{mongodb_settings['port']}/{mongodb_settings['database']}"
                )
            
            self.client = MongoClient(
                connection_url,
                serverSelectionTimeoutMS=5000  # 5초 타임아웃
            )
            
            # 데이터베이스 및 컬렉션 설정
            self.database = self.client[mongodb_settings['database']]
            self.posts_collection = self.database.posts
            
            # 연결 테스트
            self.client.admin.command('ping')
            logger.info("MongoDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            raise ConnectionFailure(f"Cannot connect to MongoDB: {str(e)}")
    
    def check_connection(self) -> bool:
        """
        MongoDB 서버 연결 상태를 확인합니다.
        
        Returns:
            bool: 연결 성공 시 True, 실패 시 False
            
        Example:
            >>> mongo_client = MongoDBClient()
            >>> if mongo_client.check_connection():
            ...     print("MongoDB is connected")
        """
        try:
            self.client.admin.command('ping')
            logger.debug("MongoDB connection check successful")
            return True
        except Exception as e:
            logger.warning(f"MongoDB connection check failed: {str(e)}")
            return False
    
    def get_posts_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        게시물 총 개수를 반환합니다.
        
        Args:
            filters (Optional[Dict[str, Any]]): 필터 조건
                - is_published (bool): 발행 여부
                - category (str): 카테고리
                - date_range (Dict): 날짜 범위
                
        Returns:
            int: 게시물 개수
            
        Example:
            >>> count = mongo_client.get_posts_count({"is_published": True})
            >>> print(f"Published posts: {count}")
        """
        try:
            query = self._build_query(filters)
            count = self.posts_collection.count_documents(query)
            logger.debug(f"Posts count: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to get posts count: {str(e)}")
            return 0
    
    def get_all_published_posts(
        self,
        batch_size: int = 100,
        skip: int = 0
    ) -> Iterator[Dict[str, Any]]:
        """
        발행된 모든 게시물을 배치 단위로 반환합니다.
        
        Args:
            batch_size (int): 배치 크기 (기본값: 100)
            skip (int): 건너뛸 문서 수 (기본값: 0)
            
        Yields:
            Dict[str, Any]: 게시물 문서
            
        Example:
            >>> for post in mongo_client.get_all_published_posts():
            ...     print(f"Post: {post['title']}")
        """
        try:
            query = {"is_published": True}
            cursor = self.posts_collection.find(query).skip(skip).limit(batch_size)
            
            for post in cursor:
                yield self._format_post_document(post)
                
        except Exception as e:
            logger.error(f"Failed to get published posts: {str(e)}")
            return
    
    def get_posts_by_ids(self, post_ids: List[str]) -> List[Dict[str, Any]]:
        """
        ID 목록으로 게시물들을 조회합니다.
        
        Args:
            post_ids (List[str]): 게시물 ID 목록
            
        Returns:
            List[Dict[str, Any]]: 게시물 문서 목록
            
        Example:
            >>> posts = mongo_client.get_posts_by_ids([
            ...     "507f1f77bcf86cd799439011",
            ...     "507f1f77bcf86cd799439012"
            ... ])
        """
        try:
            object_ids = [ObjectId(post_id) for post_id in post_ids if ObjectId.is_valid(post_id)]
            query = {"_id": {"$in": object_ids}}
            
            posts = []
            for post in self.posts_collection.find(query):
                posts.append(self._format_post_document(post))
            
            logger.debug(f"Retrieved {len(posts)} posts by IDs")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get posts by IDs: {str(e)}")
            return []
    
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 단일 게시물을 조회합니다.
        
        Args:
            post_id (str): 게시물 ID
            
        Returns:
            Optional[Dict[str, Any]]: 게시물 문서 또는 None
            
        Example:
            >>> post = mongo_client.get_post_by_id("507f1f77bcf86cd799439011")
            >>> if post:
            ...     print(f"Found post: {post['title']}")
        """
        try:
            if not ObjectId.is_valid(post_id):
                logger.warning(f"Invalid ObjectId: {post_id}")
                return None
            
            post = self.posts_collection.find_one({"_id": ObjectId(post_id)})
            if post:
                return self._format_post_document(post)
            
            logger.debug(f"Post not found: {post_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get post by ID {post_id}: {str(e)}")
            return None
    
    def get_posts_updated_since(
        self,
        since_date: datetime,
        batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """
        특정 날짜 이후 업데이트된 게시물들을 반환합니다.
        
        Args:
            since_date (datetime): 기준 날짜
            batch_size (int): 배치 크기
            
        Yields:
            Dict[str, Any]: 게시물 문서
            
        Example:
            >>> from datetime import datetime, timedelta
            >>> since = datetime.now() - timedelta(days=7)
            >>> for post in mongo_client.get_posts_updated_since(since):
            ...     print(f"Updated post: {post['title']}")
        """
        try:
            query = {
                "$or": [
                    {"updated_date": {"$gte": since_date}},
                    {"published_date": {"$gte": since_date}}
                ]
            }
            
            cursor = self.posts_collection.find(query).limit(batch_size)
            
            for post in cursor:
                yield self._format_post_document(post)
                
        except Exception as e:
            logger.error(f"Failed to get posts updated since {since_date}: {str(e)}")
            return
    
    def get_categories(self) -> List[str]:
        """
        모든 카테고리 목록을 반환합니다.
        
        Returns:
            List[str]: 카테고리 목록
            
        Example:
            >>> categories = mongo_client.get_categories()
            >>> print(f"Categories: {categories}")
        """
        try:
            categories = self.posts_collection.distinct("category", {"is_published": True})
            categories = [cat for cat in categories if cat]  # None 값 제거
            logger.debug(f"Found {len(categories)} categories")
            return sorted(categories)
        except Exception as e:
            logger.error(f"Failed to get categories: {str(e)}")
            return []
    
    def get_all_tags(self) -> List[str]:
        """
        모든 태그 목록을 반환합니다.
        
        Returns:
            List[str]: 태그 목록
            
        Example:
            >>> tags = mongo_client.get_all_tags()
            >>> print(f"Found {len(tags)} unique tags")
        """
        try:
            # MongoDB aggregation을 사용하여 모든 태그 수집
            pipeline = [
                {"$match": {"is_published": True}},
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags"}},
                {"$sort": {"_id": 1}}
            ]
            
            tags = [doc["_id"] for doc in self.posts_collection.aggregate(pipeline)]
            tags = [tag for tag in tags if tag]  # 빈 값 제거
            
            logger.debug(f"Found {len(tags)} unique tags")
            return tags
            
        except Exception as e:
            logger.error(f"Failed to get tags: {str(e)}")
            return []
    
    def _build_query(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        필터 조건에서 MongoDB 쿼리를 구성합니다.
        
        Args:
            filters (Optional[Dict[str, Any]]): 필터 조건
            
        Returns:
            Dict[str, Any]: MongoDB 쿼리
        """
        query = {}
        
        if not filters:
            return query
        
        if filters.get('is_published') is not None:
            query['is_published'] = filters['is_published']
        
        if filters.get('category'):
            query['category'] = filters['category']
        
        if filters.get('tags'):
            query['tags'] = {"$in": filters['tags']}
        
        if filters.get('date_range'):
            date_query = {}
            if filters['date_range'].get('start'):
                date_query['$gte'] = filters['date_range']['start']
            if filters['date_range'].get('end'):
                date_query['$lte'] = filters['date_range']['end']
            
            if date_query:
                query['published_date'] = date_query
        
        return query
    
    def _format_post_document(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        MongoDB 문서를 Elasticsearch 형식으로 변환합니다.
        
        Args:
            post (Dict[str, Any]): MongoDB 게시물 문서
            
        Returns:
            Dict[str, Any]: 포맷된 게시물 문서
        """
        try:
            # ObjectId를 문자열로 변환
            if '_id' in post:
                post['_id'] = str(post['_id'])
            
            # 작성자 정보 포맷팅
            if 'author' in post and isinstance(post['author'], dict):
                if '_id' in post['author']:
                    post['author']['_id'] = str(post['author']['_id'])
            
            # 날짜 필드 확인 및 기본값 설정
            current_time = datetime.utcnow()
            if not post.get('published_date'):
                post['published_date'] = current_time
            if not post.get('updated_date'):
                post['updated_date'] = current_time
            
            # 기본값 설정
            post.setdefault('view_count', 0)
            post.setdefault('like_count', 0)
            post.setdefault('comment_count', 0)
            post.setdefault('is_published', False)
            post.setdefault('tags', [])
            post.setdefault('category', '')
            post.setdefault('summary', '')
            post.setdefault('slug', '')
            post.setdefault('featured_image', '')
            post.setdefault('meta_description', '')
            post.setdefault('search_boost', 1.0)
            
            return post
            
        except Exception as e:
            logger.error(f"Failed to format post document: {str(e)}")
            return post
    
    def close(self):
        """
        MongoDB 연결을 종료합니다.
        
        Example:
            >>> mongo_client = MongoDBClient()
            >>> # ... 작업 수행 ...
            >>> mongo_client.close()
        """
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Failed to close MongoDB connection: {str(e)}")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
