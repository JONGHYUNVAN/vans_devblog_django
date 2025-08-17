"""
MongoDB에서 Elasticsearch로 게시물 데이터 동기화

VansDevBlog의 MongoDB Post 데이터를 Elasticsearch로 동기화하여
검색 기능을 활성화합니다.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from search.utils.mongodb_client import MongoDBClient
from search.documents import PostDocument
from search.utils.elasticsearch_client import ElasticsearchClient

logger = logging.getLogger('search')


class Command(BaseCommand):
    help = 'MongoDB의 게시물을 Elasticsearch로 동기화합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='배치 처리 크기 (기본값: 50)'
        )
        parser.add_argument(
            '--force-all',
            action='store_true',
            help='발행 여부와 관계없이 모든 게시물을 동기화합니다.'
        )
        parser.add_argument(
            '--incremental',
            action='store_true',
            help='증분 동기화: 최근 업데이트된 게시물만 동기화합니다.'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='증분 동기화 시 확인할 일수 (기본값: 7일)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 동기화 없이 처리할 데이터만 확인합니다.'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='기존 Elasticsearch 데이터를 모두 삭제하고 새로 동기화합니다.'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 MongoDB → Elasticsearch 데이터 동기화 시작")
        self.stdout.write("=" * 60)
        
        try:
            # 클라이언트 초기화
            mongo_client = MongoDBClient()
            es_client = ElasticsearchClient()
            
            # 연결 상태 확인
            self._check_connections(mongo_client, es_client)
            
            # 기존 데이터 삭제 (옵션)
            if options['clear_existing'] and not options['dry_run']:
                self._clear_existing_data(es_client)
            
            # 동기화 실행
            if options['incremental']:
                result = self._incremental_sync(
                    mongo_client, es_client, options
                )
            else:
                result = self._full_sync(
                    mongo_client, es_client, options
                )
            
            # 결과 출력
            self._print_sync_results(result)
            
            mongo_client.close()
            self.stdout.write(self.style.SUCCESS("\n🎉 데이터 동기화 완료!"))
            
        except Exception as e:
            logger.error(f"Data sync failed: {str(e)}")
            raise CommandError(f"데이터 동기화 실패: {str(e)}")

    def _check_connections(self, mongo_client: MongoDBClient, es_client: ElasticsearchClient):
        """MongoDB와 Elasticsearch 연결 상태 확인"""
        self.stdout.write("🔗 연결 상태 확인...")
        
        if not mongo_client.check_connection():
            raise CommandError("❌ MongoDB 연결 실패!")
        self.stdout.write("✅ MongoDB 연결 성공")
        
        if not es_client.check_connection():
            raise CommandError("❌ Elasticsearch 연결 실패!")
        self.stdout.write("✅ Elasticsearch 연결 성공")

    def _clear_existing_data(self, es_client: ElasticsearchClient):
        """기존 Elasticsearch 데이터 삭제"""
        self.stdout.write("🗑️  기존 Elasticsearch 데이터 삭제 중...")
        
        try:
            # 모든 문서 삭제
            from elasticsearch_dsl import Search
            s = Search().using(es_client.client)
            response = s.delete()
            self.stdout.write(f"삭제된 문서 수: {response.get('deleted', 0)}개")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  데이터 삭제 중 오류: {str(e)}"))

    def _full_sync(
        self, 
        mongo_client: MongoDBClient, 
        es_client: ElasticsearchClient, 
        options: Dict[str, Any]
    ) -> Dict[str, int]:
        """전체 동기화 실행"""
        self.stdout.write("📚 전체 동기화 시작...")
        
        batch_size = options['batch_size']
        force_all = options['force_all']
        dry_run = options['dry_run']
        
        result = {
            'processed': 0,
            'synced': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # 게시물 가져오기
        posts_iterator = (
            mongo_client.get_all_posts(batch_size=batch_size) 
            if force_all 
            else mongo_client.get_all_published_posts(batch_size=batch_size)
        )
        
        batch_posts = []
        
        for post in posts_iterator:
            result['processed'] += 1
            
            # 배치 처리
            batch_posts.append(post)
            
            if len(batch_posts) >= batch_size:
                batch_result = self._process_batch(batch_posts, dry_run)
                self._update_result(result, batch_result)
                batch_posts = []
                
                # 진행 상황 출력
                self.stdout.write(
                    f"처리 중... {result['processed']}개 | "
                    f"동기화: {result['synced']}개 | "
                    f"건너뜀: {result['skipped']}개"
                )
        
        # 남은 배치 처리
        if batch_posts:
            batch_result = self._process_batch(batch_posts, dry_run)
            self._update_result(result, batch_result)
        
        return result

    def _incremental_sync(
        self, 
        mongo_client: MongoDBClient, 
        es_client: ElasticsearchClient, 
        options: Dict[str, Any]
    ) -> Dict[str, int]:
        """증분 동기화 실행"""
        days = options['days']
        since_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"📅 증분 동기화: {since_date.strftime('%Y-%m-%d')} 이후 업데이트")
        
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        result = {
            'processed': 0,
            'synced': 0,
            'skipped': 0,
            'errors': 0
        }
        
        batch_posts = []
        
        for post in mongo_client.get_posts_updated_since(since_date, batch_size=batch_size):
            result['processed'] += 1
            
            batch_posts.append(post)
            
            if len(batch_posts) >= batch_size:
                batch_result = self._process_batch(batch_posts, dry_run)
                self._update_result(result, batch_result)
                batch_posts = []
                
                self.stdout.write(
                    f"처리 중... {result['processed']}개 | "
                    f"동기화: {result['synced']}개"
                )
        
        # 남은 배치 처리
        if batch_posts:
            batch_result = self._process_batch(batch_posts, dry_run)
            self._update_result(result, batch_result)
        
        return result

    def _process_batch(self, posts: List[Dict[str, Any]], dry_run: bool) -> Dict[str, int]:
        """배치 단위로 게시물 처리"""
        batch_result = {
            'synced': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for post in posts:
            try:
                # 데이터 유효성 검사
                if not self._validate_post_data(post):
                    batch_result['skipped'] += 1
                    continue
                
                if dry_run:
                    self.stdout.write(f"[DRY-RUN] 동기화 예정: {post.get('title', 'No Title')[:30]}...")
                    batch_result['synced'] += 1
                    continue
                
                # Elasticsearch 문서 생성 및 저장
                es_doc = self._convert_to_elasticsearch_document(post)
                es_doc.save()
                
                batch_result['synced'] += 1
                logger.debug(f"Synced post: {post.get('_id')}")
                
            except Exception as e:
                batch_result['errors'] += 1
                logger.error(f"Failed to sync post {post.get('_id')}: {str(e)}")
                self.stdout.write(
                    self.style.WARNING(f"⚠️  동기화 실패: {post.get('title', 'Unknown')[:30]}...")
                )
        
        return batch_result

    def _validate_post_data(self, post: Dict[str, Any]) -> bool:
        """게시물 데이터 유효성 검사"""
        required_fields = ['_id', 'title']
        
        for field in required_fields:
            if not post.get(field):
                logger.warning(f"Missing required field '{field}' in post: {post.get('_id')}")
                return False
        
        return True

    def _convert_to_elasticsearch_document(self, post: Dict[str, Any]) -> PostDocument:
        """MongoDB 문서를 Elasticsearch PostDocument로 변환"""
        
        # 언어 감지 (한국어/영어)
        title = str(post.get('title', ''))
        content = str(post.get('content', ''))
        text_for_detection = f"{title} {content}"
        language = self._detect_language(text_for_detection)
        
        # 작성자 정보 처리
        author_info = post.get('author', {})
        if isinstance(author_info, dict):
            author = {
                'user_id': str(author_info.get('_id', '')),
                'username': author_info.get('username', ''),
                'display_name': author_info.get('display_name', ''),
                'profile_image': author_info.get('profile_image', '')
            }
        else:
            author = {
                'user_id': '',
                'username': '',
                'display_name': '',
                'profile_image': ''
            }
        
        # 태그 처리
        tags = post.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        elif not isinstance(tags, list):
            tags = []
        
        # 요약문 생성
        summary = post.get('summary', '')
        if not summary and content:
            summary = content[:200] + "..." if len(content) > 200 else content
        
        # PostDocument 생성
        es_doc = PostDocument(
            meta={'id': str(post['_id'])},
            post_id=str(post['_id']),
            title=title,
            content=content,
            summary=summary,
            slug=post.get('slug', ''),
            theme=post.get('theme', ''),
            category=post.get('category', ''),
            tags=tags,
            author=author,
            published_date=post.get('published_date'),
            updated_date=post.get('updated_date'),
            view_count=post.get('view_count', 0),
            like_count=post.get('like_count', 0),
            comment_count=post.get('comment_count', 0),
            is_published=post.get('is_published', False),
            language=language,
            reading_time=self._calculate_reading_time(content),
            featured_image=post.get('featured_image', ''),
            meta_description=post.get('meta_description', summary[:150]),
            search_boost=1.0
        )
        
        return es_doc

    def _detect_language(self, text: str) -> str:
        """텍스트 언어 감지 (간단한 휴리스틱)"""
        if not text or not isinstance(text, str):
            return 'ko'
        
        # 한글 문자 개수 계산
        korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7af')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return 'ko'
        
        korean_ratio = korean_chars / total_chars
        return 'ko' if korean_ratio > 0.3 else 'en'

    def _calculate_reading_time(self, content: str) -> int:
        """읽기 시간 계산 (분 단위)"""
        if not content:
            return 1
        
        word_count = len(content.split())
        # 평균 읽기 속도: 분당 200단어
        reading_time = max(1, word_count // 200)
        return reading_time

    def _update_result(self, total_result: Dict[str, int], batch_result: Dict[str, int]):
        """배치 결과를 전체 결과에 반영"""
        for key in batch_result:
            if key in total_result:
                total_result[key] += batch_result[key]

    def _print_sync_results(self, result: Dict[str, int]):
        """동기화 결과 출력"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 동기화 결과:")
        self.stdout.write("-" * 30)
        self.stdout.write(f"📝 처리된 게시물: {result['processed']}개")
        self.stdout.write(f"✅ 동기화 성공: {result['synced']}개")
        self.stdout.write(f"⏭️  건너뜀: {result['skipped']}개")
        self.stdout.write(f"❌ 오류: {result['errors']}개")
        
        if result['processed'] > 0:
            success_rate = (result['synced'] / result['processed']) * 100
            self.stdout.write(f"🎯 성공률: {success_rate:.1f}%")
        
        self.stdout.write("=" * 60)
