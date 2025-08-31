#!/usr/bin/env python
"""
CloudType.io 헬스체크 스크립트

이 스크립트는 CloudType 배포 후 시스템의 상태를 확인합니다.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any

# Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings.cloudtype')

import django
django.setup()

from django.core.management import call_command
from django.test import Client
from django.conf import settings


class CloudTypeHealthChecker:
    """CloudType 배포 환경 헬스 체커"""
    
    def __init__(self):
        self.client = Client()
        self.results = {}
        
    def check_django_settings(self) -> Dict[str, Any]:
        """Django 설정 확인"""
        try:
            return {
                "status": "OK",
                "debug": settings.DEBUG,
                "allowed_hosts": settings.ALLOWED_HOSTS,
                "secret_key_set": bool(settings.SECRET_KEY and settings.SECRET_KEY != "django-insecure-change-this-in-production"),
                "time_zone": settings.TIME_ZONE,
                "language_code": settings.LANGUAGE_CODE,
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    def check_database(self) -> Dict[str, Any]:
        """데이터베이스 연결 확인"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            return {
                "status": "OK" if result else "ERROR",
                "engine": settings.DATABASES['default']['ENGINE'],
                "name": settings.DATABASES['default'].get('NAME', 'Not specified'),
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    def check_static_files(self) -> Dict[str, Any]:
        """정적 파일 설정 확인"""
        try:
            static_root = getattr(settings, 'STATIC_ROOT', None)
            static_files_exist = static_root and os.path.exists(static_root)
            
            return {
                "status": "OK" if static_files_exist else "WARNING",
                "static_root": static_root,
                "static_url": settings.STATIC_URL,
                "staticfiles_storage": getattr(settings, 'STATICFILES_STORAGE', 'Default'),
                "files_collected": static_files_exist,
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    def check_cache(self) -> Dict[str, Any]:
        """캐시 설정 확인"""
        try:
            from django.core.cache import cache
            
            # 캐시 테스트
            test_key = "health_check_test"
            test_value = "test_value"
            cache.set(test_key, test_value, 60)
            cached_value = cache.get(test_key)
            
            return {
                "status": "OK" if cached_value == test_value else "ERROR",
                "backend": settings.CACHES['default']['BACKEND'],
                "location": settings.CACHES['default'].get('LOCATION', 'Not specified'),
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    def check_elasticsearch(self) -> Dict[str, Any]:
        """Elasticsearch 연결 확인"""
        try:
            from search.clients.elasticsearch_client import get_elasticsearch_client
            
            client = get_elasticsearch_client()
            if client.ping():
                cluster_info = client.info()
                return {
                    "status": "OK",
                    "host": settings.ELASTICSEARCH_HOST,
                    "port": settings.ELASTICSEARCH_PORT,
                    "cluster_name": cluster_info.get('cluster_name', 'Unknown'),
                    "version": cluster_info.get('version', {}).get('number', 'Unknown'),
                }
            else:
                return {"status": "ERROR", "message": "Cannot ping Elasticsearch"}
                
        except Exception as e:
            return {"status": "WARNING", "message": f"Elasticsearch not available: {str(e)}"}
    
    def check_mongodb(self) -> Dict[str, Any]:
        """MongoDB 연결 확인"""
        try:
            from search.clients.mongodb_client import get_mongodb_client
            
            client = get_mongodb_client()
            # 간단한 연결 테스트
            client.admin.command('ismaster')
            
            return {
                "status": "OK",
                "host": settings.MONGODB_HOST,
                "port": settings.MONGODB_PORT,
                "database": settings.MONGODB_DB,
            }
        except Exception as e:
            return {"status": "WARNING", "message": f"MongoDB not available: {str(e)}"}
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """API 엔드포인트 확인"""
        endpoints = [
            "/api/v1/search/health/",
            "/swagger/",
            "/admin/",
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = self.client.get(endpoint)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "status": "OK" if response.status_code < 500 else "ERROR",
                }
            except Exception as e:
                results[endpoint] = {
                    "status": "ERROR", 
                    "message": str(e)
                }
        
        return results
    
    def check_security_settings(self) -> Dict[str, Any]:
        """보안 설정 확인"""
        try:
            return {
                "status": "OK",
                "debug": settings.DEBUG,
                "secure_ssl_redirect": getattr(settings, 'SECURE_SSL_REDIRECT', False),
                "session_cookie_secure": getattr(settings, 'SESSION_COOKIE_SECURE', False),
                "csrf_cookie_secure": getattr(settings, 'CSRF_COOKIE_SECURE', False),
                "secure_browser_xss_filter": getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
                "secure_content_type_nosniff": getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
                "x_frame_options": getattr(settings, 'X_FRAME_OPTIONS', None),
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    def run_all_checks(self) -> Dict[str, Any]:
        """모든 헬스체크 실행"""
        print("🔍 CloudType.io 헬스체크 시작...")
        
        checks = {
            "django_settings": self.check_django_settings,
            "database": self.check_database,
            "static_files": self.check_static_files,
            "cache": self.check_cache,
            "elasticsearch": self.check_elasticsearch,
            "mongodb": self.check_mongodb,
            "api_endpoints": self.check_api_endpoints,
            "security_settings": self.check_security_settings,
        }
        
        results = {
            "timestamp": time.time(),
            "environment": "cloudtype",
            "checks": {}
        }
        
        for check_name, check_func in checks.items():
            print(f"  ⏳ {check_name} 확인 중...")
            try:
                result = check_func()
                results["checks"][check_name] = result
                
                # 상태에 따른 아이콘 표시
                if isinstance(result, dict) and "status" in result:
                    status = result["status"]
                    if status == "OK":
                        print(f"  ✅ {check_name}: OK")
                    elif status == "WARNING":
                        print(f"  ⚠️  {check_name}: WARNING")
                    else:
                        print(f"  ❌ {check_name}: ERROR")
                else:
                    print(f"  ✅ {check_name}: OK")
                    
            except Exception as e:
                results["checks"][check_name] = {
                    "status": "ERROR",
                    "message": str(e)
                }
                print(f"  ❌ {check_name}: ERROR - {str(e)}")
        
        # 전체 상태 결정
        error_count = sum(1 for check in results["checks"].values() 
                         if isinstance(check, dict) and check.get("status") == "ERROR")
        warning_count = sum(1 for check in results["checks"].values() 
                           if isinstance(check, dict) and check.get("status") == "WARNING")
        
        if error_count > 0:
            results["overall_status"] = "ERROR"
            print(f"\n❌ 전체 상태: ERROR ({error_count}개 오류)")
        elif warning_count > 0:
            results["overall_status"] = "WARNING"
            print(f"\n⚠️  전체 상태: WARNING ({warning_count}개 경고)")
        else:
            results["overall_status"] = "OK"
            print(f"\n✅ 전체 상태: OK")
        
        return results


def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON 형식으로 출력
        checker = CloudTypeHealthChecker()
        results = checker.run_all_checks()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # 사람이 읽기 쉬운 형식으로 출력
        checker = CloudTypeHealthChecker()
        results = checker.run_all_checks()
        
        print("\n" + "="*60)
        print("📊 CloudType.io 헬스체크 요약")
        print("="*60)
        
        for check_name, result in results["checks"].items():
            if isinstance(result, dict):
                status = result.get("status", "UNKNOWN")
                message = result.get("message", "")
                print(f"{check_name:20}: {status:8} {message}")
        
        print("="*60)
        print(f"전체 상태: {results['overall_status']}")
        print("="*60)
        
        # 종료 코드 설정
        if results["overall_status"] == "ERROR":
            sys.exit(1)
        elif results["overall_status"] == "WARNING":
            sys.exit(2)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
