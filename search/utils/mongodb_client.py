import logging
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

import pymongo
from bson import ObjectId
from django.conf import settings
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError

logger = logging.getLogger("search")


class MongoDBClient:
    def __init__(self):
        try:
            mongodb_settings = settings.MONGODB_SETTINGS

            if mongodb_settings.get("username") and mongodb_settings.get("password"):
                connection_url = (
                    f"mongodb://{mongodb_settings['username']}:"
                    f"{mongodb_settings['password']}@"
                    f"{mongodb_settings['host']}:{mongodb_settings['port']}/"
                    f"{mongodb_settings['database']}"
                    f"?authSource={mongodb_settings.get('auth_source', 'admin')}"
                    f"&directConnection={str(mongodb_settings.get('direct_connection', True)).lower()}"
                )
            else:
                connection_url = (
                    f"mongodb://{mongodb_settings['host']}:"
                    f"{mongodb_settings['port']}/{mongodb_settings['database']}"
                )

            self.client = MongoClient(
                connection_url,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
            )

            self.database = self.client[mongodb_settings["database"]]
            self.posts_collection = self.database.posts

            self.client.admin.command("ping")
            logger.info("MongoDB client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            raise ConnectionFailure(f"Cannot connect to MongoDB: {str(e)}")

    def check_connection(self) -> bool:
        try:
            self.client.admin.command("ping")
            logger.debug("MongoDB connection check successful")
            return True
        except Exception as e:
            logger.warning(f"MongoDB connection check failed: {str(e)}")
            return False

    def get_posts_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        try:
            query = self._build_query(filters)
            count = self.posts_collection.count_documents(query)
            logger.debug(f"Posts count: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to get posts count: {str(e)}")
            return 0

    def get_all_posts_for_indexing(
        self, batch_size: int = 100, skip: int = 0
    ) -> Iterator[Dict[str, Any]]:
        try:
            cursor = self.posts_collection.find({}).skip(skip).limit(batch_size)

            for post in cursor:
                yield self._format_post_document(post)

        except Exception as e:
            logger.error(f"Failed to get all posts for indexing: {str(e)}")
            return

    def get_posts_by_ids(self, post_ids: List[str]) -> List[Dict[str, Any]]:
        try:
            object_ids = [
                ObjectId(post_id) for post_id in post_ids if ObjectId.is_valid(post_id)
            ]
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
        self, since_date: datetime, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        try:
            query = {
                "$or": [
                    {"updated_date": {"$gte": since_date}},
                    {"published_date": {"$gte": since_date}},
                ]
            }

            cursor = self.posts_collection.find(query).limit(batch_size)

            for post in cursor:
                yield self._format_post_document(post)

        except Exception as e:
            logger.error(f"Failed to get posts updated since {since_date}: {str(e)}")
            return

    def get_categories(self) -> List[str]:
        try:
            categories = self.posts_collection.distinct("category")
            categories = [cat for cat in categories if cat]
            logger.debug(f"Found {len(categories)} categories")
            return sorted(categories)
        except Exception as e:
            logger.error(f"Failed to get categories: {str(e)}")
            return []

    def get_all_tags(self) -> List[str]:
        try:
            pipeline = [
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags"}},
                {"$sort": {"_id": 1}},
            ]

            tags = [doc["_id"] for doc in self.posts_collection.aggregate(pipeline)]
            tags = [tag for tag in tags if tag]

            logger.debug(f"Found {len(tags)} unique tags")
            return tags

        except Exception as e:
            logger.error(f"Failed to get tags: {str(e)}")
            return []

    def _build_query(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = {}

        if not filters:
            return query

        if filters.get("category"):
            query["category"] = filters["category"]

        if filters.get("tags"):
            query["tags"] = {"$in": filters["tags"]}

        if filters.get("date_range"):
            date_query = {}
            if filters["date_range"].get("start"):
                date_query["$gte"] = filters["date_range"]["start"]
            if filters["date_range"].get("end"):
                date_query["$lte"] = filters["date_range"]["end"]

            if date_query:
                query["published_date"] = date_query

        return query

    def _format_post_document(self, post: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if "_id" in post:
                post["_id"] = str(post["_id"])

            if "author" in post and isinstance(post["author"], dict):
                if "_id" in post["author"]:
                    post["author"]["_id"] = str(post["author"]["_id"])

            current_time = datetime.utcnow()
            if not post.get("published_date"):
                post["published_date"] = current_time
            if not post.get("updated_date"):
                post["updated_date"] = current_time

            post.setdefault("view_count", 0)
            post.setdefault("like_count", 0)
            post.setdefault("comment_count", 0)
            post.setdefault("is_published", False)
            post.setdefault("tags", [])
            post.setdefault("category", "")
            post.setdefault("summary", "")
            post.setdefault("slug", "")
            post.setdefault("featured_image", "")
            post.setdefault("meta_description", "")
            post.setdefault("search_boost", 1.0)

            return post

        except Exception as e:
            logger.error(f"Failed to format post document: {str(e)}")
            return post

    def close(self):
        try:
            if hasattr(self, "client"):
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Failed to close MongoDB connection: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
