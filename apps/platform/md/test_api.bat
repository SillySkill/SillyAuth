@echo off
REM API测试脚本 - Windows版本
REM 测试教程和下载资源API

set BASE_URL=http://47.96.133.238:8000

echo ========================================
echo SillyMD 内容API测试
echo ========================================
echo.

echo 1. 健康检查
echo ----------------------------------------
curl -s "%BASE_URL%/api/health"
echo.
echo.

echo 2. 测试教程列表API
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/?limit=5"
echo.
echo.

echo 3. 测试教程详情API (ID=1)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/1"
echo.
echo.

echo 4. 测试教程详情API (slug)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/claude-code-getting-started"
echo.
echo.

echo 5. 测试教程分类统计API
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/categories"
echo.
echo.

echo 6. 测试教程筛选API (难度=beginner)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/?difficulty=beginmer^&limit=5"
echo.
echo.

echo 7. 测试教程搜索API (关键词=Claude)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/?search=Claude^&limit=5"
echo.
echo.

echo 8. 测试下载资源列表API
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/?limit=5"
echo.
echo.

echo 9. 测试下载资源详情API (ID=1)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/1"
echo.
echo.

echo 10. 测试下载资源详情API (slug)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/wsl2-windows"
echo.
echo.

echo 11. 测试下载资源分类统计API
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/categories"
echo.
echo.

echo 12. 测试下载资源筛选API (平台=windows)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/?platform=windows^&limit=5"
echo.
echo.

echo 13. 测试下载资源搜索API (关键词=Python)
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/?search=Python^&limit=5"
echo.
echo.

echo 14. 测试精选教程API
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/tutorials/featured?limit=6"
echo.
echo.

echo 15. 测试精选下载资源API
echo ----------------------------------------
curl -s "%BASE_URL%/api/content/downloads/featured?limit=6"
echo.
echo.

echo ========================================
echo 测试完成
echo ========================================
pause
