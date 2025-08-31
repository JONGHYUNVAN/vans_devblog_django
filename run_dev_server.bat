@echo off
REM =============================================================================
REM Django 개발 서버 실행 스크립트 (Windows)
REM =============================================================================

echo 🚀 VansDevBlog Search Service 개발 서버 시작...

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 환경변수 설정
set DJANGO_SETTINGS_MODULE=vans_search_service.settings.development
set PYTHONPATH=%cd%
set PYTHONUNBUFFERED=1

REM 데이터베이스 마이그레이션 확인
echo 📦 데이터베이스 마이그레이션 확인 중...
python manage.py showmigrations --verbosity=0
if errorlevel 1 (
    echo ❌ 마이그레이션 확인 실패
    pause
    exit /b 1
)

REM 개발 서버 시작
echo 🌟 Django 개발 서버 시작 (http://localhost:8000)
echo 📖 API 문서: http://localhost:8000/swagger/
echo 🔧 관리자: http://localhost:8000/admin/
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요
echo.

python manage.py runserver 8000

pause
