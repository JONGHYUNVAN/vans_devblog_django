@echo off
echo ================================
echo VansDevBlog Search Service API 테스트
echo ================================
echo.

echo 1. 헬스체크 API 테스트
echo URL: http://localhost:8001/api/v1/search/health/
curl -s http://localhost:8001/api/v1/search/health/ | python -m json.tool
echo.
echo.

echo 2. 카테고리 목록 API 테스트  
echo URL: http://localhost:8001/api/v1/search/categories/
curl -s http://localhost:8001/api/v1/search/categories/ | python -m json.tool
echo.
echo.

echo 3. 인기 검색어 API 테스트
echo URL: http://localhost:8001/api/v1/search/popular/
curl -s http://localhost:8001/api/v1/search/popular/ | python -m json.tool
echo.
echo.

echo 4. 자동완성 API 테스트
echo URL: http://localhost:8001/api/v1/search/autocomplete/?query=Django
curl -s "http://localhost:8001/api/v1/search/autocomplete/?query=Django" | python -m json.tool
echo.
echo.

echo 5. 검색 API 테스트
echo URL: http://localhost:8001/api/v1/search/posts/?query=Python&page_size=5
curl -s "http://localhost:8001/api/v1/search/posts/?query=Python&page_size=5" | python -m json.tool
echo.
echo.

echo ================================
echo 테스트 완료!
echo 위 결과를 확인하여 API 정상 작동 여부를 판단하세요.
echo ================================
pause
