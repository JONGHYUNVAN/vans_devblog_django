# Method Inventory

??? ????????????? ????????

## docs/source/conf.py
### Functions
- skip_module_variables, setup

## gunicorn.conf.py
### Functions
- when_ready, worker_int, pre_fork, post_fork, pre_exec, worker_abort

## manage.py
### Functions
- main

## scripts/cloudtype_health_check.py
### Classes
- CloudTypeHealthChecker: __init__, check_django_settings, check_database, check_static_files, check_cache, check_elasticsearch, check_mongodb, check_api_endpoints, check_security_settings, run_all_checks
### Functions
- main

## scripts/run_tests.py
### Functions
- setup_django, run_command, main

## scripts/safe_test_runner.py
### Functions
- check_environment, run_safe_tests, main

## scripts/simple_health.py
### Functions
- health_check

## scripts/temp_check_server.py
- (no classes or functions)

## search/__init__.py
- (no classes or functions)

## search/admin.py
- (no classes or functions)

## search/api/__init__.py
- (no classes or functions)

## search/api/serializers.py
### Classes
- AuthorSerializer: (no methods)
- PostDocumentSerializer: (no methods)
- SearchRequestSerializer: validate_tags, validate
- SearchResultSerializer: get_highlight
- SearchResponseSerializer: (no methods)
- AutocompleteRequestSerializer: (no methods)
- AutocompleteResponseSerializer: (no methods)
- PopularSearchesResponseSerializer: (no methods)
- SyncRequestSerializer: validate
- SyncResponseSerializer: (no methods)
- SyncStatusSerializer: (no methods)

## search/api/urls.py
- (no classes or functions)

## search/api/views.py
### Functions
- api_logger, health_logger, health_check, search_posts, autocomplete, popular_searches, get_categories, sync_status, sync_data, sync_all_data

## search/apps.py
### Classes
- SearchConfig: (no methods)

## search/clients/__init__.py
- (no classes or functions)

## search/clients/elasticsearch_client.py
### Classes
- ElasticsearchClient: __init__, check_connection, get_cluster_health, create_index_if_not_exists, delete_index, search_posts, get_autocomplete_suggestions, get_popular_searches

## search/clients/mongodb_client.py
### Classes
- MongoDBClient: __init__, check_connection, get_posts_count, get_all_published_posts, get_all_posts, get_posts_by_ids, get_post_by_id, get_posts_updated_since, get_categories, get_all_tags, _build_query, close, __enter__, __exit__

## search/documents.py
### Classes
- PostDocument: save, create_from_mongo_post
- SuggestionDocument: (no methods)
### Functions
- setup_elasticsearch_connection, create_indexes, delete_indexes, rebuild_indexes

## search/documents/__init__.py
### Functions
- create_indexes, delete_indexes, rebuild_indexes

## search/documents/analyzers.py
- (no classes or functions)

## search/documents/index_manager.py
### Classes
- IndexManager: __init__, _setup_connection, create_indexes, delete_indexes, rebuild_indexes, check_index_health

## search/documents/popular_search_document.py
### Classes
- PopularSearchDocument: update_popular_search, get_top_popular_searches, delete_index, create_index_if_not_exists
### Functions
- _get_es_client

## search/documents/post_document.py
### Classes
- PostDocument: save, create_from_mongo_post, to_dict_summary

## search/documents/suggestion_document.py
### Classes
- SuggestionDocument: save, create_suggestion, increment_frequency

## search/management/__init__.py
- (no classes or functions)

## search/management/commands/__init__.py
- (no classes or functions)

## search/management/commands/create_search_indexes.py
### Classes
- Command: add_arguments, handle, _check_elasticsearch_connection, _create_indexes, _delete_indexes, _rebuild_indexes, print_help

## search/management/commands/fetch_mongodb_data.py
### Classes
- Command: add_arguments, handle, _print_status, _print_result

## search/management/commands/setup_popular_searches.py
### Classes
- Command: add_arguments, handle

## search/management/commands/sync_posts_to_elasticsearch.py
### Classes
- Command: add_arguments, handle, _check_connections, _clear_existing_data, _full_sync, _incremental_sync, _process_batch, _validate_post_data, _update_result, _print_sync_results

## search/management/commands/test_mongodb_connection.py
### Classes
- Command: add_arguments, handle, _show_database_info, _show_posts

## search/migrations/0001_initial.py
### Classes
- Migration: (no methods)

## search/migrations/__init__.py
- (no classes or functions)

## search/models.py
### Classes
- SearchLog: __str__, record_log
- PopularSearch: __str__, update_popular_search, get_top_popular_searches

## search/serializers.py
### Classes
- AuthorSerializer: (no methods)
- PostDocumentSerializer: (no methods)
- SearchRequestSerializer: validate_tags, validate
- SearchResultSerializer: (no methods)
- SearchResponseSerializer: (no methods)
- AutocompleteRequestSerializer: (no methods)
- AutocompleteResponseSerializer: (no methods)
- PopularSearchesResponseSerializer: (no methods)

## search/services/__init__.py
- (no classes or functions)

## search/services/cache_service.py
### Classes
- CacheService: __init__, _generate_cache_key, get_search_result, set_search_result, get_autocomplete_suggestions, set_autocomplete_suggestions, get_popular_searches, set_popular_searches, get_categories, set_categories, clear_search_cache, invalidate_cache
### Functions
- cache_result

## search/services/content_parser.py
### Functions
- _extract_text_from_nodes, parse_rich_text_json

## search/services/health_service.py
### Classes
- HealthService: get_health_status, _check_elasticsearch_connection_fast, _check_mongodb_connection_fast, _check_elasticsearch_connection, _check_mongodb_connection

## search/services/search_service.py
### Classes
- SearchService: __init__, search_posts, get_autocomplete_suggestions, get_popular_searches, get_categories, _build_filters, _build_sort_params, _build_search_response

## search/services/sync_service.py
### Classes
- SyncService: __init__, _init_clients, _close_clients, get_sync_status, sync_data, _check_connections, _clear_existing_data, _full_sync, _incremental_sync, _process_batch, _validate_post_data, _update_result

## search/tests.py
- (no classes or functions)

## search/urls.py
- (no classes or functions)

## search/utils/pm_plain.py
### Functions
- _strip_html, pm_to_text, tiptap_to_plain

## tests/__init__.py
- (no classes or functions)

## tests/conftest.py
### Functions
- pytest_configure, api_client, mock_elasticsearch, mock_mongodb, clean_cache, sample_search_log, sample_popular_search, override_cache_settings

## tests/test_api.py
### Classes
- TestSearchAPI: test_health_check_endpoint, test_search_posts_endpoint, test_search_posts_invalid_params, test_autocomplete_endpoint, test_popular_searches_endpoint, test_categories_endpoint
- TestAPIErrorHandling: test_search_service_exception, test_autocomplete_service_exception
- TestAPIAuthentication: test_public_endpoints_no_auth_required
- TestAPIPerformance: test_search_response_structure, test_pagination_parameters

## tests/test_clients.py
### Classes
- TestElasticsearchClient: test_client_initialization, test_search_posts_success, test_search_posts_exception, test_autocomplete_success, test_health_check_success, test_health_check_failure
- TestMongoDBClient: test_client_initialization, test_get_categories_success, test_get_categories_exception, test_health_check_success, test_health_check_failure
- TestClientIntegration: test_both_clients_healthy

## tests/test_integration.py
### Classes
- TestSearchWorkflow: setUpClass, setUp, tearDown, test_complete_search_workflow, test_search_logging_integration, test_error_handling_integration
- TestLightweightIntegration: setUpClass, setUp, tearDown, test_basic_api_endpoints, test_model_operations
- TestFullIntegration: test_complete_model_integration

## tests/test_memory_efficient.py
### Classes
- MemoryEfficientTestCase: setUpClass, tearDownClass, setUp, tearDown
- TestMemoryEfficient: test_basic_endpoints_memory_safe, test_search_with_minimal_mocking, test_model_operations_minimal
- TestMemoryStress: test_multiple_requests_memory_stable

## tests/test_models.py
### Classes
- TestSearchLog: test_create_search_log, test_record_log_class_method, test_search_log_str_representation
- TestPopularSearch: test_create_popular_search, test_update_popular_search_new, test_update_popular_search_existing, test_get_top_popular_searches, test_popular_search_unique_constraint, test_popular_search_str_representation

## tests/test_services.py
### Classes
- TestSearchService: test_search_service_initialization, test_search_posts_with_logging, test_search_posts_empty_query, test_get_popular_searches_from_db, test_get_popular_searches_empty_db, test_get_categories_from_mongodb
- TestHealthService: test_health_check_all_healthy, test_health_check_elasticsearch_unhealthy
- TestCacheService: test_cache_search_result, test_cache_popular_searches, test_cache_categories

## tests/test_simple.py
### Classes
- TestSimple: test_django_settings, test_database_connection
### Functions
- test_simple_pytest, test_django_model_creation

## tests/test_urls.py
- (no classes or functions)

## vans_search_service/__init__.py
- (no classes or functions)

## vans_search_service/asgi.py
- (no classes or functions)

## vans_search_service/settings.py
### Functions
- get_env_variable

## vans_search_service/settings/__init__.py
### Functions
- get_env_variable

## vans_search_service/settings/base.py
- (no classes or functions)

## vans_search_service/settings/development.py
- (no classes or functions)

## vans_search_service/settings/production.py
- (no classes or functions)

## vans_search_service/settings/testing.py
### Classes
- DisableMigrations: __contains__, __getitem__

## vans_search_service/urls.py
- (no classes or functions)

## vans_search_service/wsgi.py
- (no classes or functions)
