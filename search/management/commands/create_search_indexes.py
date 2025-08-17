"""
VansDevBlog Search Service Index Management Command

Elasticsearch 인덱스를 생성, 삭제, 재구축하는 Django 관리 명령어입니다.
"""

from django.core.management.base import BaseCommand, CommandError
from search.documents import create_indexes, delete_indexes, rebuild_indexes
from search.utils.elasticsearch_client import ElasticsearchClient
import logging

logger = logging.getLogger('search')


class Command(BaseCommand):
    """
    Elasticsearch 인덱스 관리 명령어.
    
    이 명령어는 VansDevBlog 검색 서비스의 Elasticsearch 인덱스를
    생성, 삭제, 재구축하는 기능을 제공합니다.
    
    사용법:
        python manage.py create_search_indexes --create     # 인덱스 생성
        python manage.py create_search_indexes --delete     # 인덱스 삭제
        python manage.py create_search_indexes --rebuild    # 인덱스 재구축
    
    Example:
        >>> python manage.py create_search_indexes --create
        INFO: Creating Elasticsearch indexes...
        INFO: Created index: vans_posts
        INFO: Created index: vans_suggestions
        SUCCESS: All indexes created successfully!
    """
    
    help = 'VansDevBlog 검색 서비스 Elasticsearch 인덱스를 관리합니다.'
    
    def add_arguments(self, parser):
        """
        명령어 인자를 정의합니다.
        
        Args:
            parser: Django ArgumentParser 인스턴스
        """
        parser.add_argument(
            '--create',
            action='store_true',
            help='Elasticsearch 인덱스를 생성합니다.',
        )
        
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Elasticsearch 인덱스를 삭제합니다.',
        )
        
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Elasticsearch 인덱스를 재구축합니다 (삭제 후 재생성).',
        )
        
        parser.add_argument(
            '--check',
            action='store_true',
            help='Elasticsearch 연결 상태를 확인합니다.',
        )
    
    def handle(self, *args, **options):
        """
        명령어를 실행합니다.
        
        Args:
            *args: 위치 인자들
            **options: 키워드 옵션들
            
        Raises:
            CommandError: 명령어 실행 실패
        """
        try:
            # 옵션 확인
            create = options.get('create', False)
            delete = options.get('delete', False)
            rebuild = options.get('rebuild', False)
            check = options.get('check', False)
            
            # 하나의 옵션만 선택되었는지 확인
            selected_options = sum([create, delete, rebuild, check])
            if selected_options == 0:
                self.stdout.write(
                    self.style.ERROR('옵션을 선택해주세요: --create, --delete, --rebuild, --check 중 하나')
                )
                self.print_help()
                return
            elif selected_options > 1:
                self.stdout.write(
                    self.style.ERROR('하나의 옵션만 선택해주세요.')
                )
                return
            
            # Elasticsearch 연결 확인
            if check:
                self._check_elasticsearch_connection()
                return
            
            self._check_elasticsearch_connection()
            
            # 선택된 작업 실행
            if create:
                self._create_indexes()
            elif delete:
                self._delete_indexes()
            elif rebuild:
                self._rebuild_indexes()
                
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            raise CommandError(f'명령어 실행 실패: {str(e)}')
    
    def _check_elasticsearch_connection(self):
        """
        Elasticsearch 연결 상태를 확인합니다.
        
        Raises:
            CommandError: Elasticsearch 연결 실패
        """
        try:
            self.stdout.write('Elasticsearch 연결 확인 중...')
            
            es_client = ElasticsearchClient()
            if es_client.check_connection():
                health = es_client.get_cluster_health()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Elasticsearch 연결 성공! '
                        f'(상태: {health.get("status", "unknown")})'
                    )
                )
            else:
                raise CommandError('Elasticsearch 연결 실패')
                
        except Exception as e:
            logger.error(f"Elasticsearch connection check failed: {str(e)}")
            raise CommandError(f'Elasticsearch 연결 확인 실패: {str(e)}')
    
    def _create_indexes(self):
        """
        Elasticsearch 인덱스를 생성합니다.
        
        Raises:
            CommandError: 인덱스 생성 실패
        """
        try:
            self.stdout.write('🔧 Elasticsearch 인덱스 생성 중...')
            
            create_indexes()
            
            self.stdout.write(
                self.style.SUCCESS('✅ 모든 인덱스가 성공적으로 생성되었습니다!')
            )
            self.stdout.write('생성된 인덱스:')
            self.stdout.write('  - vans_posts (게시물 검색용)')
            self.stdout.write('  - vans_suggestions (자동완성용)')
            
        except Exception as e:
            logger.error(f"Index creation failed: {str(e)}")
            raise CommandError(f'인덱스 생성 실패: {str(e)}')
    
    def _delete_indexes(self):
        """
        Elasticsearch 인덱스를 삭제합니다.
        
        Raises:
            CommandError: 인덱스 삭제 실패
        """
        try:
            # 사용자 확인
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  모든 검색 인덱스가 삭제됩니다. 계속하시겠습니까? [y/N]: '
                ),
                ending=''
            )
            
            confirm = input().lower().strip()
            if confirm not in ['y', 'yes']:
                self.stdout.write(self.style.SUCCESS('인덱스 삭제가 취소되었습니다.'))
                return
            
            self.stdout.write('🗑️  Elasticsearch 인덱스 삭제 중...')
            
            delete_indexes()
            
            self.stdout.write(
                self.style.SUCCESS('✅ 모든 인덱스가 성공적으로 삭제되었습니다!')
            )
            
        except Exception as e:
            logger.error(f"Index deletion failed: {str(e)}")
            raise CommandError(f'인덱스 삭제 실패: {str(e)}')
    
    def _rebuild_indexes(self):
        """
        Elasticsearch 인덱스를 재구축합니다.
        
        Raises:
            CommandError: 인덱스 재구축 실패
        """
        try:
            # 사용자 확인
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  모든 검색 인덱스가 삭제되고 재생성됩니다. 계속하시겠습니까? [y/N]: '
                ),
                ending=''
            )
            
            confirm = input().lower().strip()
            if confirm not in ['y', 'yes']:
                self.stdout.write(self.style.SUCCESS('인덱스 재구축이 취소되었습니다.'))
                return
            
            self.stdout.write('🔄 Elasticsearch 인덱스 재구축 중...')
            
            rebuild_indexes()
            
            self.stdout.write(
                self.style.SUCCESS('✅ 모든 인덱스가 성공적으로 재구축되었습니다!')
            )
            self.stdout.write('재구축된 인덱스:')
            self.stdout.write('  - vans_posts (게시물 검색용)')
            self.stdout.write('  - vans_suggestions (자동완성용)')
            
        except Exception as e:
            logger.error(f"Index rebuild failed: {str(e)}")
            raise CommandError(f'인덱스 재구축 실패: {str(e)}')
    
    def print_help(self):
        """사용법 도움말을 출력합니다."""
        self.stdout.write('\n📖 사용법:')
        self.stdout.write('  python manage.py create_search_indexes --create   # 인덱스 생성')
        self.stdout.write('  python manage.py create_search_indexes --delete   # 인덱스 삭제')
        self.stdout.write('  python manage.py create_search_indexes --rebuild  # 인덱스 재구축')
        self.stdout.write('  python manage.py create_search_indexes --check    # 연결 확인')
        self.stdout.write('')
