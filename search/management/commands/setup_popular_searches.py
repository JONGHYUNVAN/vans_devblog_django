"""
Django management command to create popular search index in Elasticsearch.
"""

import logging

from django.core.management.base import BaseCommand

from search.documents.popular_search_document import PopularSearchDocument

logger = logging.getLogger("search")


class Command(BaseCommand):
    help = "Set up the popular searches index in Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--recreate",
            action="store_true",
            help="Delete existing index and recreate it",
        )

    def handle(self, *args, **options):
        try:
            if options["recreate"]:
                self.stdout.write("Deleting existing popular search index...")
                try:
                    PopularSearchDocument.delete_index()
                    self.stdout.write(
                        self.style.SUCCESS("Existing index deleted successfully")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Index deletion failed: {str(e)}")
                    )

            self.stdout.write("Creating popular search index...")
            PopularSearchDocument.create_index_if_not_exists()
            self.stdout.write(
                self.style.SUCCESS("Popular search index created successfully")
            )

            

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to create popular search index: {str(e)}")
            )
            logger.error(f"Popular search index creation failed: {str(e)}", exc_info=True)
