#!/usr/bin/env python
"""
안전한 테스트 러너

성능 문제를 방지하면서 테스트를 실행하는 스크립트입니다.
"""

import argparse
import os
import subprocess
import sys
import time



def check_environment():
    """환경 확인"""
    print("🔍 환경 확인 중...")

    # 가상환경 확인
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  경고: 가상환경이 활성화되지 않은 것 같습니다.")
        return False

    # Django 설정 확인
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "vans_search_service.settings.testing"
    )

    print("✅ 환경 확인 완료")
    return True


def run_safe_tests(test_type="quick", verbose=False):
    """안전한 테스트 실행"""

    if not check_environment():
        print("❌ 환경 확인 실패")
        return False

    base_cmd = ["python", "-m", "pytest"]

    if test_type == "quick":
        print("🚀 빠른 테스트 실행 중...")
        cmd = base_cmd + [
            "tests/test_simple.py",
            "tests/test_models.py",
            "tests/test_integration.py::TestLightweightIntegration",
            "--ds=vans_search_service.settings.testing",
            "-v" if verbose else "-q",
            "--timeout=30",
            "--maxfail=3",
        ]

    elif test_type == "basic":
        print("🧪 기본 테스트 실행 중...")
        cmd = base_cmd + [
            "tests/test_simple.py",
            "tests/test_models.py",
            "--ds=vans_search_service.settings.testing",
            "-v" if verbose else "",
            "--timeout=20",
        ]

    elif test_type == "integration":
        print("🔄 통합 테스트 실행 중...")
        cmd = base_cmd + [
            "tests/test_integration.py::TestLightweightIntegration",
            "--ds=vans_search_service.settings.testing",
            "-v",
            "--timeout=45",
            "--maxfail=2",
        ]

    elif test_type == "full":
        print("🎯 전체 테스트 실행 중 (느림 제외)...")
        cmd = base_cmd + [
            "tests/",
            "-m",
            "not slow",
            "--ds=vans_search_service.settings.testing",
            "-v" if verbose else "",
            "--timeout=60",
            "--maxfail=5",
        ]

    elif test_type == "all":
        print("🔥 전체 테스트 실행 중 (모든 테스트 포함)...")
        print("⚠️  주의: 이 모드는 시간이 오래 걸릴 수 있습니다!")
        response = input("계속하시겠습니까? (y/N): ")
        if response.lower() != "y":
            print("❌ 테스트 실행 취소")
            return False

        cmd = base_cmd + [
            "tests/",
            "--ds=vans_search_service.settings.testing",
            "-v",
            "--timeout=120",
            "--maxfail=10",
        ]

    else:
        print(f"❌ 알 수 없는 테스트 타입: {test_type}")
        return False

    # 명령어 출력
    print(f"📝 실행 명령어: {' '.join(cmd)}")
    print("⏱️  시작 시간:", time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        start_time = time.time()
        result = subprocess.run(cmd, check=False, capture_output=False)
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"\n⏱️  실행 시간: {elapsed:.2f}초")

        if result.returncode == 0:
            print("✅ 모든 테스트 통과!")
            return True
        else:
            print(f"❌ 테스트 실패 (종료 코드: {result.returncode})")
            return False

    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 테스트가 중단되었습니다.")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="안전한 테스트 러너")
    parser.add_argument(
        "--type",
        "-t",
        choices=["quick", "basic", "integration", "full", "all"],
        default="quick",
        help="테스트 타입 선택 (기본값: quick)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 출력")

    args = parser.parse_args()

    print("🧪 안전한 테스트 러너")
    print("=" * 50)

    success = run_safe_tests(args.type, args.verbose)

    if success:
        print("\n🎉 테스트 완료!")
        sys.exit(0)
    else:
        print("\n💥 테스트 실패!")
        sys.exit(1)


if __name__ == "__main__":
    main()
