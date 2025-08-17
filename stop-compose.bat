@echo off
chcp 65001 >nul
echo ====================================
echo  VansDevBlog Docker Compose 정지
echo ====================================
echo.

echo Docker Compose 서비스 정지 중...
docker-compose down

echo.
echo [SUCCESS] 모든 서비스가 정지되었습니다!
echo.
pause
