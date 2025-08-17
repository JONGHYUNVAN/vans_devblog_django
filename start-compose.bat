@echo off
chcp 65001 >nul
echo ====================================
echo  VansDevBlog Docker Compose 시작
echo ====================================
echo.

echo Docker Compose로 Elasticsearch + Cerebro 시작 중...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose 시작 실패!
    echo Docker Compose가 설치되어 있는지 확인해주세요.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] 모든 서비스가 성공적으로 시작되었습니다!
echo.
echo [INFO] 접속 정보:
echo    - Elasticsearch: http://localhost:9200
echo    - Cerebro:       http://localhost:9000
echo.
echo [TIP] Cerebro에서 Elasticsearch 연결 시:
echo    Host: http://elasticsearch:9200
echo.
echo [CMD] 상태 확인: docker-compose ps
echo [CMD] 로그 확인: docker-compose logs
echo.
echo 웹 브라우저에서 http://localhost:9000 을 열어보세요!
echo.
pause
