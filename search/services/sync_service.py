"""
VansDevBlog Search Service Sync Service

MongoDB와 Elasticsearch 간의 데이터 동기화를 관리하는 서비스입니다.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.utils import timezone

from ..clients.elasticsearch_client import ElasticsearchClient
from ..clients.mongodb_client import MongoDBClient
from ..documents import PostDocument

logger = logging.getLogger("search")


class SyncService:
    """
    MongoDB와 Elasticsearch 간의 데이터 동기화 서비스.

    데이터 동기화, 상태 확인, 통계 조회 등의 기능을 제공합니다.

    Attributes:
        mongo_client (MongoDBClient): MongoDB 클라이언트
        es_client (ElasticsearchClient): Elasticsearch 클라이언트

    Example:
        >>> sync_service = SyncService()
        >>> status = sync_service.get_sync_status()
        >>> result = sync_service.sync_data({"incremental": True})
    """

    def __init__(self):
        """
        SyncService 인스턴스를 초기화합니다.
        """
        self.mongo_client = None
        self.es_client = None

    def _init_clients(self):
        """클라이언트들을 초기화합니다."""
        if not self.mongo_client:
            self.mongo_client = MongoDBClient()
        if not self.es_client:
            self.es_client = ElasticsearchClient()

    def _close_clients(self):
        """클라이언트 연결을 종료합니다."""
        if self.mongo_client:
            self.mongo_client.close()
            self.mongo_client = None
        if self.es_client:
            self.es_client = None

    def get_sync_status(self) -> Dict[str, Any]:
        """
        현재 동기화 상태를 조회합니다.

        Returns:
            Dict[str, Any]: 동기화 상태 정보

        Example:
            >>> sync_service = SyncService()
            >>> status = sync_service.get_sync_status()
            >>> print(f"MongoDB 연결: {status['mongodb_connected']}")
        """
        try:
            self._init_clients()

            # 연결 상태 확인
            mongodb_connected = self.mongo_client.check_connection()
            elasticsearch_connected = self.es_client.check_connection()

            # MongoDB 통계 (is_published 필드가 없으므로 전체 게시물만 조회)
            total_posts_in_mongodb = 0
            published_posts_in_mongodb = 0
            if mongodb_connected:
                total_posts_in_mongodb = self.mongo_client.get_posts_count()
                published_posts_in_mongodb = total_posts_in_mongodb  # 모든 게시물이 발행된 것으로 간주

            # Elasticsearch 통계
            total_docs_in_elasticsearch = 0
            if elasticsearch_connected:
                try:
                    from elasticsearch_dsl import Search

                    s = Search().using(self.es_client.client)
                    response = s.count()
                    total_docs_in_elasticsearch = response
                except Exception as e:
                    logger.warning(f"Failed to count Elasticsearch documents: {str(e)}")

            # 마지막 동기화 시간 (캐시에서 조회)
            last_sync_time = cache.get("last_sync_time")

            # 동기화 필요 여부 판단
            sync_needed = (
                published_posts_in_mongodb != total_docs_in_elasticsearch
                or not last_sync_time
                or (timezone.now() - last_sync_time).days > 1
            )

            return {
                "mongodb_connected": mongodb_connected,
                "elasticsearch_connected": elasticsearch_connected,
                "total_posts_in_mongodb": total_posts_in_mongodb,
                "published_posts_in_mongodb": published_posts_in_mongodb,
                "total_docs_in_elasticsearch": total_docs_in_elasticsearch,
                "last_sync_time": last_sync_time,
                "sync_needed": sync_needed,
            }

        except Exception as e:
            logger.error(f"Failed to get sync status: {str(e)}")
            return {
                "mongodb_connected": False,
                "elasticsearch_connected": False,
                "total_posts_in_mongodb": 0,
                "published_posts_in_mongodb": 0,
                "total_docs_in_elasticsearch": 0,
                "last_sync_time": None,
                "sync_needed": True,
            }
        finally:
            self._close_clients()

    def sync_data(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 동기화를 실행합니다.

        Args:
            options (Dict[str, Any]): 동기화 옵션
                - batch_size (int): 배치 크기
                - force_all (bool): 전체 동기화 여부
                - incremental (bool): 증분 동기화 여부
                - days (int): 증분 동기화 기간
                - clear_existing (bool): 기존 데이터 삭제 여부
                - dry_run (bool): 테스트 실행 여부

        Returns:
            Dict[str, Any]: 동기화 결과

        Example:
            >>> options = {"incremental": True, "days": 7}
            >>> result = sync_service.sync_data(options)
            >>> print(f"동기화 완료: {result['synced']}개")
        """
        start_time = time.time()
        result = {
            "status": "started",
            "type": "incremental" if options.get("incremental") else "full",
            "processed": 0,
            "synced": 0,
            "skipped": 0,
            "errors": 0,
            "success_rate": 0.0,
            "execution_time": 0.0,
            "message": "",
        }

        try:
            self._init_clients()

            # 연결 상태 확인
            if not self._check_connections():
                result.update(
                    {
                        "status": "failed",
                        "message": "MongoDB 또는 Elasticsearch 연결에 실패했습니다.",
                    }
                )
                return result

            # 기존 데이터 삭제 (옵션)
            if options.get("clear_existing") and not options.get("dry_run"):
                self._clear_existing_data()

            # 동기화 실행
            if options.get("incremental"):
                sync_result = self._incremental_sync(options)
            else:
                sync_result = self._full_sync(options)

            # 결과 업데이트
            result.update(sync_result)

            # 성공률 계산
            if result["processed"] > 0:
                result["success_rate"] = (result["synced"] / result["processed"]) * 100

            # 상태 결정
            if result["errors"] == 0:
                result["status"] = "completed"
                result["message"] = "동기화가 성공적으로 완료되었습니다."
            elif result["synced"] > 0:
                result["status"] = "partial"
                result["message"] = f"동기화가 부분적으로 완료되었습니다. ({result['errors']}개 오류)"
            else:
                result["status"] = "failed"
                result["message"] = "동기화에 실패했습니다."

            # 마지막 동기화 시간 저장
            if not options.get("dry_run") and result["synced"] > 0:
                cache.set("last_sync_time", timezone.now(), 60 * 60 * 24 * 30)  # 30일

            logger.info(f"Sync completed: {result}")

        except Exception as e:
            logger.error(f"Sync failed: {str(e)}", exc_info=True)
            result.update(
                {
                    "status": "failed",
                    "message": f"동기화 중 오류가 발생했습니다: {str(e)}",
                }
            )

        finally:
            result["execution_time"] = time.time() - start_time
            self._close_clients()

        return result

    def _check_connections(self) -> bool:
        """연결 상태를 확인합니다."""
        mongodb_ok = self.mongo_client.check_connection()
        elasticsearch_ok = self.es_client.check_connection()

        if not mongodb_ok:
            logger.error("MongoDB connection failed")
        if not elasticsearch_ok:
            logger.error("Elasticsearch connection failed")

        return mongodb_ok and elasticsearch_ok

    def _clear_existing_data(self):
        """기존 Elasticsearch 데이터를 삭제합니다."""
        try:
            from elasticsearch_dsl import Search

            s = Search().using(self.es_client.client)
            response = s.delete()
            logger.info(f"Deleted {response.get('deleted', 0)} existing documents")
        except Exception as e:
            logger.warning(f"Failed to clear existing data: {str(e)}")

    def _full_sync(self, options: Dict[str, Any]) -> Dict[str, int]:
        """전체 동기화를 실행합니다."""
        batch_size = options.get("batch_size", 50)
        force_all = options.get("force_all", False)
        dry_run = options.get("dry_run", False)

        result = {"processed": 0, "synced": 0, "skipped": 0, "errors": 0}

        # 게시물 가져오기 (is_published 필드가 없으므로 모든 게시물 조회)
        posts_iterator = self.mongo_client.get_all_posts(batch_size=batch_size)

        batch_posts = []

        for post in posts_iterator:
            result["processed"] += 1
            batch_posts.append(post)

            if len(batch_posts) >= batch_size:
                batch_result = self._process_batch(batch_posts, dry_run)
                self._update_result(result, batch_result)
                batch_posts = []

        # 남은 배치 처리
        if batch_posts:
            batch_result = self._process_batch(batch_posts, dry_run)
            self._update_result(result, batch_result)

        return result

    def _incremental_sync(self, options: Dict[str, Any]) -> Dict[str, int]:
        """증분 동기화를 실행합니다."""
        days = options.get("days", 7)
        since_date = timezone.now() - timedelta(days=days)
        batch_size = options.get("batch_size", 50)
        dry_run = options.get("dry_run", False)

        result = {"processed": 0, "synced": 0, "skipped": 0, "errors": 0}

        batch_posts = []

        for post in self.mongo_client.get_posts_updated_since(
            since_date, batch_size=batch_size
        ):
            result["processed"] += 1
            batch_posts.append(post)

            if len(batch_posts) >= batch_size:
                batch_result = self._process_batch(batch_posts, dry_run)
                self._update_result(result, batch_result)
                batch_posts = []

        # 남은 배치 처리
        if batch_posts:
            batch_result = self._process_batch(batch_posts, dry_run)
            self._update_result(result, batch_result)

        return result

    def _process_batch(
        self, posts: List[Dict[str, Any]], dry_run: bool
    ) -> Dict[str, int]:
        """배치 단위로 게시물을 처리합니다."""
        batch_result = {"synced": 0, "skipped": 0, "errors": 0}

        for post in posts:
            try:
                # 데이터 유효성 검사
                if not self._validate_post_data(post):
                    batch_result["skipped"] += 1
                    continue

                if dry_run:
                    logger.debug(
                        f"[DRY-RUN] Would sync: {post.get('title', 'No Title')[:30]}..."
                    )
                    batch_result["synced"] += 1
                    continue

                # Elasticsearch 문서 생성 및 저장
                es_doc = PostDocument.create_from_mongo_post(post)
                es_doc.save()

                batch_result["synced"] += 1
                logger.debug(f"Synced post: {post.get('_id')}")

            except Exception as e:
                batch_result["errors"] += 1
                logger.error(f"Failed to sync post {post.get('_id')}: {str(e)}")

        return batch_result

    def _validate_post_data(self, post: Dict[str, Any]) -> bool:
        """게시물 데이터의 유효성을 검사합니다."""
        required_fields = ["_id", "title"]

        for field in required_fields:
            if not post.get(field):
                logger.warning(
                    f"Missing required field '{field}' in post: {post.get('_id')}"
                )
                return False

        return True

    def _update_result(
        self, total_result: Dict[str, int], batch_result: Dict[str, int]
    ):
        """배치 결과를 전체 결과에 반영합니다."""
        for key in batch_result:
            if key in total_result:
                total_result[key] += batch_result[key]
