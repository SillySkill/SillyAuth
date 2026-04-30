#!/bin/bash

# 前端页面HTTP状态码检查脚本
# 测试所有23个核心页面的可访问性

BASE_URL="http://47.96.133.238"
REPORT_FILE="E:/silly/md/docs/verification/http-status-check.txt"

# 创建报告目录
mkdir -p "E:/silly/md/docs/verification"

# 清空报告文件
> "$REPORT_FILE"

echo "========================================" | tee -a "$REPORT_FILE"
echo "前端页面HTTP状态检查报告" | tee -a "$REPORT_FILE"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 定义要测试的页面列表
declare -a PAGES=(
    "examples/index.html"
    "examples/login.html"
    "examples/register.html"
    "examples/forgot-password.html"
    "examples/reset-password.html"
    "examples/skills.html"
    "examples/skill-detail.html"
    "examples/skills-real.html"
    "examples/dashboard.html"
    "examples/settings.html"
    "examples/analytics.html"
    "examples/user-center.html"
    "examples/tutorials.html"
    "examples/downloads.html"
    "examples/creation.html"
    "examples/points-mall.html"
    "examples/tasks.html"
    "examples/messages.html"
    "examples/marketplace.html"
    "examples/projects.html"
    "examples/features.html"
    "examples/vendor-apply.html"
    "examples/index-dynamic.html"
)

SUCCESS_COUNT=0
FAIL_COUNT=0
WARNING_COUNT=0

echo "开始检查页面..." | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

for page in "${PAGES[@]}"; do
    URL="$BASE_URL/$page"
    echo -n "检查 $page ... " | tee -a "$REPORT_FILE"

    # 获取HTTP状态码
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "$URL" 2>/dev/null)

    case $STATUS in
        200)
            echo "✅ 通过 (200)" | tee -a "$REPORT_FILE"
            ((SUCCESS_COUNT++))
            ;;
        301|302|307|308)
            echo "⚠️  重定向 ($STATUS)" | tee -a "$REPORT_FILE"
            ((WARNING_COUNT++))
            ;;
        404)
            echo "❌ 失败 (404 Not Found)" | tee -a "$REPORT_FILE"
            ((FAIL_COUNT++))
            ;;
        502)
            echo "❌ 失败 (502 Bad Gateway)" | tee -a "$REPORT_FILE"
            ((FAIL_COUNT++))
            ;;
        000)
            echo "❌ 失败 (连接超时/无法访问)" | tee -a "$REPORT_FILE"
            ((FAIL_COUNT++))
            ;;
        *)
            echo "⚠️  警告 (状态码: $STATUS)" | tee -a "$REPORT_FILE"
            ((WARNING_COUNT++))
            ;;
    esac
done

echo "" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"
echo "统计结果" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"
echo "总页面数: ${#PAGES[@]}" | tee -a "$REPORT_FILE"
echo "✅ 通过: $SUCCESS_COUNT" | tee -a "$REPORT_FILE"
echo "⚠️  警告: $WARNING_COUNT" | tee -a "$REPORT_FILE"
echo "❌ 失败: $FAIL_COUNT" | tee -a "$REPORT_FILE"
echo "通过率: $(awk "BEGIN {printf \"%.1f\", ($SUCCESS_COUNT/${#PAGES[@]})*100}")%" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"

exit 0
