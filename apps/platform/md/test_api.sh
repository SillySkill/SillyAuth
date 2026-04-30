#!/bin/bash
# API测试脚本
# 测试教程和下载资源API

BASE_URL="http://47.96.133.238:8000"

echo "========================================"
echo "SillyMD 内容API测试"
echo "========================================"

# 1. 检查服务器健康状态
echo ""
echo "1. 健康检查"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/health" | python -m json.tool
echo ""

# 2. 列出所有路由
echo ""
echo "2. 列出所有API路由"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/debug/routes" | python -m json.tool | head -50
echo ""

# 3. 测试教程列表
echo ""
echo "3. 测试教程列表API"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/?limit=5" | python -m json.tool
echo ""

# 4. 测试教程详情 (ID)
echo ""
echo "4. 测试教程详情API (ID=1)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/1" | python -m json.tool
echo ""

# 5. 测试教程详情 (slug)
echo ""
echo "5. 测试教程详情API (slug)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/claude-code-getting-started" | python -m json.tool
echo ""

# 6. 测试教程分类统计
echo ""
echo "6. 测试教程分类统计API"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/categories" | python -m json.tool
echo ""

# 7. 测试教程筛选
echo ""
echo "7. 测试教程筛选API (难度=beginner)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/?difficulty=beginner&limit=5" | python -m json.tool
echo ""

# 8. 测试教程搜索
echo ""
echo "8. 测试教程搜索API (关键词=Claude)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/?search=Claude&limit=5" | python -m json.tool
echo ""

# 9. 测试下载资源列表
echo ""
echo "9. 测试下载资源列表API"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/?limit=5" | python -m json.tool
echo ""

# 10. 测试下载资源详情 (ID)
echo ""
echo "10. 测试下载资源详情API (ID=1)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/1" | python -m json.tool
echo ""

# 11. 测试下载资源详情 (slug)
echo ""
echo "11. 测试下载资源详情API (slug)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/wsl2-windows" | python -m json.tool
echo ""

# 12. 测试下载资源分类统计
echo ""
echo "12. 测试下载资源分类统计API"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/categories" | python -m json.tool
echo ""

# 13. 测试下载资源筛选
echo ""
echo "13. 测试下载资源筛选API (平台=windows)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/?platform=windows&limit=5" | python -m json.tool
echo ""

# 14. 测试下载资源搜索
echo ""
echo "14. 测试下载资源搜索API (关键词=Python)"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/?search=Python&limit=5" | python -m json.tool
echo ""

# 15. 测试精选教程
echo ""
echo "15. 测试精选教程API"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/tutorials/featured?limit=6" | python -m json.tool
echo ""

# 16. 测试精选下载资源
echo ""
echo "16. 测试精选下载资源API"
echo "----------------------------------------"
curl -s "${BASE_URL}/api/content/downloads/featured?limit=6" | python -m json.tool
echo ""

echo "========================================"
echo "测试完成"
echo "========================================"
