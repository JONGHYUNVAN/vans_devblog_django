#!/usr/bin/env python
"""
테스트 실행 스크립트

다양한 테스트 시나리오를 실행할 수 있는 편의 스크립트입니다.
"""

import os
import sys
import subprocess
import argparse


def setup_django():
    """Django 환경 설정"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings.testing')
    
    import django
    django.setup()


def run_command(command, description):
    """명령어 실행"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='VansDevBlog Search Service 테스트 실행')
    parser.add_argument('--type', choices=['unit', 'integration', 'api', 'models', 'services', 'clients', 'all'], 
                       default='all', help='실행할 테스트 타입')
    parser.add_argument('--coverage', action='store_true', help='커버리지 리포트 생성')
    parser.add_argument('--verbose', action='store_true', help='상세 출력')
    parser.add_argument('--file', help='특정 테스트 파일 실행')
    
    args = parser.parse_args()
    
    # Django 설정
    setup_django()
    
    # 기본 pytest 옵션
    pytest_options = []
    
    if args.verbose:
        pytest_options.append('-v')
    
    if args.coverage:
        pytest_options.extend(['--cov=search', '--cov-report=html', '--cov-report=term-missing'])
    
    # 테스트 타입별 실행
    commands = []
    
    if args.file:
        commands.append((f"pytest {' '.join(pytest_options)} {args.file}", f"파일 테스트: {args.file}"))
    elif args.type == 'unit':
        commands.extend([
            (f"pytest {' '.join(pytest_options)} tests/test_models.py", "모델 유닛 테스트"),
            (f"pytest {' '.join(pytest_options)} tests/test_services.py", "서비스 유닛 테스트"),
            (f"pytest {' '.join(pytest_options)} tests/test_clients.py", "클라이언트 유닛 테스트"),
        ])
    elif args.type == 'integration':
        commands.append((f"pytest {' '.join(pytest_options)} tests/test_integration.py", "통합 테스트"))
    elif args.type == 'api':
        commands.append((f"pytest {' '.join(pytest_options)} tests/test_api.py", "API 테스트"))
    elif args.type == 'models':
        commands.append((f"pytest {' '.join(pytest_options)} tests/test_models.py", "모델 테스트"))
    elif args.type == 'services':
        commands.append((f"pytest {' '.join(pytest_options)} tests/test_services.py", "서비스 테스트"))
    elif args.type == 'clients':
        commands.append((f"pytest {' '.join(pytest_options)} tests/test_clients.py", "클라이언트 테스트"))
    else:  # all
        commands.extend([
            (f"pytest {' '.join(pytest_options)} tests/test_models.py", "모델 테스트"),
            (f"pytest {' '.join(pytest_options)} tests/test_services.py", "서비스 테스트"),
            (f"pytest {' '.join(pytest_options)} tests/test_clients.py", "클라이언트 테스트"),
            (f"pytest {' '.join(pytest_options)} tests/test_api.py", "API 테스트"),
            (f"pytest {' '.join(pytest_options)} tests/test_integration.py", "통합 테스트"),
        ])
    
    # 테스트 실행
    success_count = 0
    total_count = len(commands)
    
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
    
    # 결과 요약
    print(f"\n{'='*60}")
    print(f"🎯 테스트 완료: {success_count}/{total_count} 성공")
    print(f"{'='*60}")
    
    if args.coverage:
        print("\n📊 커버리지 리포트가 htmlcov/ 디렉토리에 생성되었습니다.")
        print("브라우저에서 htmlcov/index.html을 열어보세요.")
    
    return success_count == total_count


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
