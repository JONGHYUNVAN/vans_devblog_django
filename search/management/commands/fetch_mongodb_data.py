"""
MongoDB에서 모든 데이터를 간편하게 가져와서 Elasticsearch로 동기화하는 명령어

간단한 데이터 동기화를 위한 관리 명령어입니다.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from search.services.sync_service import SyncService

logger = logging.getLogger("search")


class Command(BaseCommand):
    help = "MongoDB에서 모든 데이터를 가져와서 Elasticsearch로 동기화합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size", type=int, default=50, help="배치 처리 크기 (기본값: 50)"
        )
        parser.add_argument(
            "--clear", action="store_true", help="기존 Elasticsearch 데이터 삭제 후 동기화"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="실제 동기화 없이 확인만"
        )

    def handle(self, *args, **options):
        self.stdout.write("MongoDB → Elasticsearch 데이터 동기화 시작")
        self.stdout.write("=" * 60)

        try:
            # 동기화 서비스 초기화
            sync_service = SyncService()

            # 동기화 상태 확인
            self.stdout.write("📊 현재 상태 확인 중...")
            status_data = sync_service.get_sync_status()
            self._print_status(status_data)

            # 동기화 옵션 구성
            sync_options = {
                "batch_size": options["batch_size"],
                "force_all": True,  # is_published 필드가 없으므로 항상 모든 게시물 동기화
                "incremental": False,  # 전체 동기화
                "clear_existing": options["clear"],
                "dry_run": options["dry_run"],
            }

            # 확인 메시지
            if options["clear"] and not options["dry_run"]:
                self.stdout.write(
                    self.style.WARNING("⚠️  기존 Elasticsearch 데이터가 모두 삭제됩니다!")
                )
                confirm = input("계속하시겠습니까? (y/N): ")
                if confirm.lower() != "y":
                    self.stdout.write("동기화가 취소되었습니다.")
                    return

            if options["dry_run"]:
                self.stdout.write(self.style.NOTICE("🔍 DRY-RUN 모드: 실제 동기화는 수행되지 않습니다."))

            # 동기화 실행
            self.stdout.write("\n🚀 데이터 동기화 시작...")
            result = sync_service.sync_data(sync_options)

            # 결과 출력
            self._print_result(result)

        except Exception as e:
            logger.error(f"Command failed: {str(e)}")
            raise CommandError(f"데이터 동기화 실패: {str(e)}")

    def _print_status(self, status_data):
        """현재 상태를 출력합니다."""
        self.stdout.write("현재 상태:")
        self.stdout.write("-" * 30)

        # 연결 상태
        mongodb_status = "✅ 연결됨" if status_data["mongodb_connected"] else "❌ 연결 실패"
        es_status = "✅ 연결됨" if status_data["elasticsearch_connected"] else "❌ 연결 실패"

        self.stdout.write(f"MongoDB: {mongodb_status}")
        self.stdout.write(f"Elasticsearch: {es_status}")

        # 데이터 통계
        self.stdout.write(f"MongoDB 총 게시물: {status_data['total_posts_in_mongodb']}개")
        self.stdout.write(f"MongoDB 발행된 게시물: {status_data['published_posts_in_mongodb']}개")
        self.stdout.write(f"Elasticsearch 문서: {status_data['total_docs_in_elasticsearch']}개")

        # 동기화 필요 여부
        if status_data["sync_needed"]:
            self.stdout.write(self.style.WARNING("📝 동기화가 필요합니다."))
        else:
            self.stdout.write(self.style.SUCCESS("✅ 데이터가 동기화되어 있습니다."))

        # 마지막 동기화 시간
        if status_data["last_sync_time"]:
            self.stdout.write(f"마지막 동기화: {status_data['last_sync_time']}")
        else:
            self.stdout.write("마지막 동기화: 없음")

        self.stdout.write()

    def _print_result(self, result):
        """동기화 결과를 출력합니다."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("동기화 결과:")
        self.stdout.write("-" * 30)

        # 상태에 따른 아이콘
        if result["status"] == "completed":
            status_icon = "✅"
            status_style = self.style.SUCCESS
        elif result["status"] == "partial":
            status_icon = "⚠️"
            status_style = self.style.WARNING
        elif result["status"] == "failed":
            status_icon = "❌"
            status_style = self.style.ERROR
        else:
            status_icon = "ℹ️"
            status_style = self.style.NOTICE

        self.stdout.write(status_style(f"{status_icon} 상태: {result['status']}"))
        self.stdout.write(f"타입: {result['type']}")
        self.stdout.write(f"처리된 게시물: {result['processed']}개")
        self.stdout.write(f"동기화 성공: {result['synced']}개")
        self.stdout.write(f"건너뜀: {result['skipped']}개")
        self.stdout.write(f"오류: {result['errors']}개")

        if result["processed"] > 0:
            self.stdout.write(f"성공률: {result['success_rate']:.1f}%")

        self.stdout.write(f"실행 시간: {result['execution_time']:.2f}초")
        self.stdout.write(f"메시지: {result['message']}")

        self.stdout.write("=" * 60)

        # 최종 상태 메시지
        if result["status"] == "completed":
            self.stdout.write(self.style.SUCCESS("\n🎉 데이터 동기화가 성공적으로 완료되었습니다!"))
        elif result["status"] == "partial":
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  데이터 동기화가 부분적으로 완료되었습니다. "
                    f"({result['errors']}개 오류 발생)"
                )
            )
        else:
            self.stdout.write(self.style.ERROR(f"\n❌ 데이터 동기화에 실패했습니다: {result['message']}"))
