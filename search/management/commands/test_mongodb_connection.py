"""
MongoDB 연결 테스트 Django 관리 명령어

MongoDB 서버에 연결하고 기본 작업을 테스트합니다.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

from search.clients.mongodb_client import MongoDBClient

logger = logging.getLogger("search")


class Command(BaseCommand):
    help = "MongoDB 연결을 테스트하고 기본 정보를 출력합니다."

    def add_arguments(self, parser):
        parser.add_argument("--show-posts", action="store_true", help="게시물 목록을 출력합니다.")
        parser.add_argument(
            "--all-posts", action="store_true", help="발행 여부에 관계없이 모든 게시물을 출력합니다."
        )
        parser.add_argument("--limit", type=int, default=5, help="출력할 게시물 수 (기본값: 5)")

    def handle(self, *args, **options):
        self.stdout.write("MongoDB 연결 테스트 시작...")
        self.stdout.write("=" * 50)

        try:
            # MongoDB 클라이언트 생성
            mongo_client = MongoDBClient()

            # 연결 테스트
            if mongo_client.check_connection():
                self.stdout.write(self.style.SUCCESS("MongoDB 연결 성공!"))
            else:
                raise CommandError("MongoDB 연결 실패!")

            # 기본 정보 출력
            self._show_database_info(mongo_client)

            # 게시물 정보 출력
            if options["show_posts"] or options["all_posts"]:
                self._show_posts(mongo_client, options["limit"], options["all_posts"])

            mongo_client.close()
            self.stdout.write(self.style.SUCCESS("\n MongoDB 테스트 완료!"))

        except Exception as e:
            logger.error(f"MongoDB test failed: {str(e)}")
            raise CommandError(f"MongoDB 테스트 실패: {str(e)}")

    def _show_database_info(self, mongo_client: MongoDBClient):
        """데이터베이스 기본 정보 출력"""
        self.stdout.write("\n 데이터베이스 정보:")
        self.stdout.write("-" * 30)

        try:
            # 게시물 총 개수
            total_posts = mongo_client.get_posts_count()
            published_posts = mongo_client.get_posts_count({"is_published": True})

            self.stdout.write(f"전체 게시물: {total_posts}개")
            self.stdout.write(f"발행된 게시물: {published_posts}개")

            # 카테고리 목록
            categories = mongo_client.get_categories()
            self.stdout.write(f"카테고리: {len(categories)}개")
            if categories:
                self.stdout.write(f"   → {', '.join(categories[:5])}")
                if len(categories) > 5:
                    self.stdout.write(f"   → ... 외 {len(categories) - 5}개")

            # 태그 목록
            tags = mongo_client.get_all_tags()
            self.stdout.write(f"태그: {len(tags)}개")
            if tags:
                self.stdout.write(f"   → {', '.join(tags[:10])}")
                if len(tags) > 10:
                    self.stdout.write(f"   → ... 외 {len(tags) - 10}개")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"정보 조회 중 오류: {str(e)}"))

    def _show_posts(
        self, mongo_client: MongoDBClient, limit: int, show_all: bool = False
    ):
        """게시물 목록 출력"""
        post_type = "모든 게시물" if show_all else "발행된 게시물"
        self.stdout.write(f"\n최근 {post_type} {limit}개:")
        self.stdout.write("-" * 30)

        try:
            count = 0
            posts_iterator = (
                mongo_client.get_all_posts(batch_size=limit)
                if show_all
                else mongo_client.get_all_published_posts(batch_size=limit)
            )

            for post in posts_iterator:
                count += 1
                title = post.get("title", "No Title")[:50]
                category = post.get("category", "No Category")
                published_date = post.get("published_date", "Unknown")
                is_published = post.get("is_published", False)

                status = "[v]" if is_published else "[x]"

                self.stdout.write(
                    f"{count}. {status} [{category}] {title}" f" - {published_date}"
                )

                if count >= limit:
                    break

            if count == 0:
                self.stdout.write(f"{post_type}이 없습니다.")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"게시물 조회 중 오류: {str(e)}"))