"""
VansDevBlog Search Service Index Migration Command

기존 vans_posts 인덱스를 새 스키마(posts_v2)로 무중단 마이그레이션합니다.

절차:
  1. 새 인덱스(posts_v2)를 새 매핑으로 생성
  2. MongoDB에서 전체 문서를 가져와 posts_v2에 벌크 색인
  3. 'posts' 알리아스를 posts_v2로 교체
  4. 구 인덱스(posts_v1 / vans_posts) 삭제

사용법:
    python manage.py migrate_search_index
    python manage.py migrate_search_index --batch-size 100
    python manage.py migrate_search_index --skip-delete-old
    python manage.py migrate_search_index --dry-run
"""

import logging
import sys
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger("search")

# 알리아스 이름 (고정)
ALIAS_NAME = "posts"

# 새 인덱스 이름
NEW_INDEX_NAME = "posts_v2"

# 이전 인덱스 이름 후보 (존재하는 것 삭제)
OLD_INDEX_CANDIDATES = ["posts_v1", "vans_posts"]


class Command(BaseCommand):
    help = "ES 인덱스를 새 스키마로 무중단 마이그레이션합니다 (posts_v2 생성 → 재색인 → 알리아스 교체 → 구 인덱스 삭제)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="MongoDB 문서 배치 처리 크기 (기본값: 50)",
        )
        parser.add_argument(
            "--skip-delete-old",
            action="store_true",
            help="알리아스 교체 후 구 인덱스를 삭제하지 않습니다.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="실제 변경 없이 처리 예정 문서 수만 확인합니다.",
        )

    def handle(self, *args, **options):
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass

        batch_size = options["batch_size"]
        skip_delete = options["skip_delete_old"]
        dry_run = options["dry_run"]

        self.stdout.write("=" * 60)
        self.stdout.write("ES 인덱스 마이그레이션 시작")
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY-RUN 모드] 실제 변경 없이 실행됩니다."))
        self.stdout.write("=" * 60)

        try:
            from elasticsearch import Elasticsearch, helpers
            from django.conf import settings

            from search.clients.mongodb_client import MongoDBClient
            from search.documents.post_document import PostDocument, extract_tiptap_text

            # --- 클라이언트 초기화 ---
            es_config = settings.ELASTICSEARCH_DSL["default"].copy()
            es = Elasticsearch(**es_config)

            if not es.ping():
                raise CommandError("Elasticsearch 연결 실패!")
            self.stdout.write("Elasticsearch 연결 성공")

            mongo_client = MongoDBClient()
            if not mongo_client.check_connection():
                raise CommandError("MongoDB 연결 실패!")
            self.stdout.write("MongoDB 연결 성공")

            # --- STEP 1: 새 인덱스 생성 ---
            self.stdout.write(f"\n[1/4] 새 인덱스 '{NEW_INDEX_NAME}' 생성...")
            self._create_new_index(es, dry_run)

            # --- STEP 2: MongoDB → posts_v2 벌크 색인 ---
            self.stdout.write(f"\n[2/4] MongoDB → '{NEW_INDEX_NAME}' 벌크 색인...")
            total_synced = self._bulk_reindex(
                es, mongo_client, helpers, batch_size, dry_run
            )
            self.stdout.write(
                self.style.SUCCESS(f"  색인 완료: {total_synced}개 문서")
            )

            # --- STEP 3: 알리아스 교체 ---
            self.stdout.write(f"\n[3/4] 알리아스 '{ALIAS_NAME}' → '{NEW_INDEX_NAME}' 교체...")
            if not dry_run:
                self._swap_alias(es)
                self.stdout.write(
                    self.style.SUCCESS(f"  알리아스 '{ALIAS_NAME}' 교체 완료")
                )
            else:
                self.stdout.write(f"  [DRY-RUN] 알리아스 교체 생략")

            # --- STEP 4: 구 인덱스 삭제 ---
            if skip_delete:
                self.stdout.write("\n[4/4] --skip-delete-old 옵션으로 구 인덱스 삭제 생략")
            else:
                self.stdout.write("\n[4/4] 구 인덱스 삭제...")
                if not dry_run:
                    self._delete_old_indexes(es)
                else:
                    self.stdout.write(f"  [DRY-RUN] 구 인덱스 삭제 생략")

            mongo_client.close()

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("ES 인덱스 마이그레이션 완료!"))
            self.stdout.write("=" * 60)

        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            raise CommandError(f"마이그레이션 실패: {str(e)}")

    # -------------------------------------------------------------------------
    # 내부 메서드
    # -------------------------------------------------------------------------

    def _build_new_index_body(self) -> Dict[str, Any]:
        """
        posts_v2 인덱스 매핑 및 설정을 빌드합니다.
        PostDocument의 Index.settings와 동일한 설정을 사용합니다.
        """
        from search.documents.analyzers import BASE_INDEX_SETTINGS

        mappings = {
            "properties": {
                "post_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "english": {"type": "text", "analyzer": "english_analyzer"},
                        "raw": {"type": "keyword"},
                        "suggest": {"type": "completion"},
                    },
                },
                "description": {
                    "type": "text",
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "english": {"type": "text", "analyzer": "english_analyzer"},
                        "suggest": {"type": "completion"},
                    },
                },
                "content_text": {
                    "type": "text",
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "english": {"type": "text", "analyzer": "english_analyzer"},
                    },
                },
                "topic": {
                    "type": "text",
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "english": {"type": "text", "analyzer": "english_analyzer"},
                        "raw": {"type": "keyword"},
                        "suggest": {"type": "completion"},
                    },
                },
                "mainCategory": {
                    "type": "keyword",
                    "fields": {"suggest": {"type": "completion"}},
                },
                "subCategory": {
                    "type": "keyword",
                    "fields": {"suggest": {"type": "completion"}},
                },
                "tags": {
                    "type": "keyword",
                    "fields": {"suggest": {"type": "completion"}},
                },
                "author": {"type": "keyword"},
                "language": {"type": "keyword"},
                "createdAt": {"type": "date"},
                "updatedAt": {"type": "date"},
            }
        }

        return {"settings": BASE_INDEX_SETTINGS, "mappings": mappings}

    def _create_new_index(self, es: Any, dry_run: bool) -> None:
        """posts_v2 인덱스를 생성합니다. 이미 존재하면 삭제 후 재생성합니다."""
        if dry_run:
            self.stdout.write(f"  [DRY-RUN] 인덱스 '{NEW_INDEX_NAME}' 생성 생략")
            return

        if es.indices.exists(index=NEW_INDEX_NAME):
            self.stdout.write(
                self.style.WARNING(
                    f"  '{NEW_INDEX_NAME}' 인덱스가 이미 존재합니다. 삭제 후 재생성합니다."
                )
            )
            es.indices.delete(index=NEW_INDEX_NAME)
            logger.info(f"Deleted existing index: {NEW_INDEX_NAME}")

        body = self._build_new_index_body()
        es.indices.create(index=NEW_INDEX_NAME, body=body)
        logger.info(f"Created new index: {NEW_INDEX_NAME}")
        self.stdout.write(self.style.SUCCESS(f"  인덱스 '{NEW_INDEX_NAME}' 생성 완료"))

    def _build_actions(
        self, posts_iterator: Any, extract_tiptap_text: Any
    ):
        """
        MongoDB 문서 이터레이터에서 Elasticsearch bulk action을 생성합니다.
        """
        for post in posts_iterator:
            try:
                post_id = str(post.get("_id", ""))
                if not post_id or not post.get("title"):
                    continue

                # TipTap JSON → plain text
                content_raw = post.get("content")
                if isinstance(content_raw, dict):
                    content_text = " ".join(extract_tiptap_text(content_raw))
                elif isinstance(content_raw, str):
                    content_text = content_raw
                else:
                    content_text = ""

                yield {
                    "_index": NEW_INDEX_NAME,
                    "_id": post_id,
                    "_source": {
                        "post_id": post_id,
                        "title": str(post.get("title", "")),
                        "description": post.get("description", ""),
                        "content_text": content_text,
                        "topic": post.get("topic", ""),
                        "mainCategory": post.get("mainCategory", ""),
                        "subCategory": post.get("subCategory", ""),
                        "tags": post.get("tags", []),
                        "author": post.get("author", ""),
                        "language": post.get("language", "ko"),
                        "createdAt": post.get("createdAt"),
                        "updatedAt": post.get("updatedAt"),
                    },
                }
            except Exception as e:
                logger.error(
                    f"Failed to build action for post {post.get('_id')}: {str(e)}"
                )
                continue

    def _bulk_reindex(
        self,
        es: Any,
        mongo_client: Any,
        helpers: Any,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        """
        MongoDB 전체 문서를 가져와 posts_v2에 벌크 색인합니다.

        Returns:
            int: 색인 성공한 문서 수
        """
        from search.documents.post_document import extract_tiptap_text

        posts_iterator = mongo_client.get_all_posts(batch_size=batch_size)

        if dry_run:
            count = 0
            for post in posts_iterator:
                if post.get("_id") and post.get("title"):
                    count += 1
            self.stdout.write(
                f"  [DRY-RUN] 색인 예정 문서 수: {count}개"
            )
            return count

        success_count = 0
        error_count = 0

        actions = self._build_actions(posts_iterator, extract_tiptap_text)

        for ok, info in helpers.streaming_bulk(
            es,
            actions,
            chunk_size=batch_size,
            raise_on_error=False,
        ):
            if ok:
                success_count += 1
            else:
                error_count += 1
                logger.error(f"Bulk index error: {info}")

            if (success_count + error_count) % 100 == 0:
                self.stdout.write(
                    f"  진행: 성공 {success_count}개 / 오류 {error_count}개"
                )

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f"  경고: {error_count}개 문서 색인 실패")
            )

        return success_count

    def _swap_alias(self, es: Any) -> None:
        """
        'posts' 알리아스를 원자적으로 posts_v2로 교체합니다.

        기존에 알리아스가 가리키던 인덱스에서 알리아스를 제거하고
        동시에 posts_v2에 알리아스를 추가합니다.
        """
        actions = []

        # 기존 알리아스가 가리키는 인덱스에서 제거
        try:
            existing = es.indices.get_alias(name=ALIAS_NAME)
            for old_index in existing.keys():
                if old_index != NEW_INDEX_NAME:
                    actions.append(
                        {"remove": {"index": old_index, "alias": ALIAS_NAME}}
                    )
                    logger.info(f"Removing alias '{ALIAS_NAME}' from '{old_index}'")
        except Exception:
            # 알리아스가 아직 없으면 무시
            pass

        # 새 인덱스에 알리아스 추가
        actions.append({"add": {"index": NEW_INDEX_NAME, "alias": ALIAS_NAME}})

        if actions:
            es.indices.update_aliases(body={"actions": actions})
            logger.info(f"Alias '{ALIAS_NAME}' now points to '{NEW_INDEX_NAME}'")

    def _delete_old_indexes(self, es: Any) -> None:
        """구 인덱스 후보를 삭제합니다."""
        for index_name in OLD_INDEX_CANDIDATES:
            try:
                if es.indices.exists(index=index_name):
                    es.indices.delete(index=index_name)
                    logger.info(f"Deleted old index: {index_name}")
                    self.stdout.write(
                        self.style.SUCCESS(f"  구 인덱스 '{index_name}' 삭제 완료")
                    )
                else:
                    self.stdout.write(
                        f"  구 인덱스 '{index_name}' 없음 (생략)"
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  구 인덱스 '{index_name}' 삭제 실패: {str(e)}"
                    )
                )
                logger.warning(f"Failed to delete old index '{index_name}': {str(e)}")
