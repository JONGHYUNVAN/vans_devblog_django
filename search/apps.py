import logging

from django.apps import AppConfig

logger = logging.getLogger("search")


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"

    def ready(self):
        try:
            from .documents.popular_search_document import PopularSearchDocument

            PopularSearchDocument.create_index_if_not_exists()
        except Exception as e:
            logger.warning(f"Could not auto-create popular search index on startup: {e}")
