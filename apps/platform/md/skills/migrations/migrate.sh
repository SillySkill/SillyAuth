#!/bin/bash
# ============================================
# SillyMD 数据库迁移执行脚本
# 版本: 1.0
# 描述: 自动执行所有未应用的数据库迁移
# ============================================

set -e  # 遇到错误立即退出

# ============================================
# 配置变量
# ============================================

# 数据库连接配置（从环境变量读取，如未设置则使用默认值）
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-sillymd}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"

# 迁移脚本目录
MIGRATIONS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 日志文件
LOG_FILE="${MIGRATIONS_DIR}/migration_$(date +%Y%m%d_%H%M%S).log"

# ============================================
# 颜色输出
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# 日志函数
# ============================================

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $*" | tee -a "$LOG_FILE" >&2
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN:${NC} $*" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $*" | tee -a "$LOG_FILE"
}

# ============================================
# 检查函数
# ============================================

check_dependencies() {
    log "检查依赖..."

    if ! command -v psql &> /dev/null; then
        error "psql 未安装，请先安装 PostgreSQL 客户端"
        exit 1
    fi

    info "依赖检查完成"
}

check_connection() {
    log "检查数据库连接..."

    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c '\q' 2>/dev/null || {
        error "无法连接到数据库服务器"
        error "请检查连接配置: host=$DB_HOST port=$DB_PORT user=$DB_USER"
        exit 1
    }

    info "数据库连接成功"
}

check_database() {
    log "检查数据库是否存在..."

    DB_EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -w "$DB_NAME" | wc -l)

    if [ "$DB_EXISTS" -eq 0 ]; then
        warn "数据库 $DB_NAME 不存在，将自动创建"
        info "创建数据库: $DB_NAME"
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME ENCODING 'UTF8';"
        log "数据库创建成功"
    else
        info "数据库 $DB_NAME 已存在"
    fi
}

# ============================================
# 迁移版本检查
# ============================================

get_applied_migrations() {
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT version FROM schema_migrations ORDER BY applied_at;" 2>/dev/null || echo ""
}

is_migration_applied() {
    local version=$1
    local applied
    applied=$(get_applied_migrations | grep -c "^${version}$" || echo "0")
    [ "$applied" -gt 0 ]
}

# ============================================
# 执行迁移
# ============================================

apply_migration() {
    local file=$1
    local filename
    filename=$(basename "$file")
    local version
    version=$(echo "$filename" | cut -d'_' -f1)

    if is_migration_applied "$version"; then
        info "跳过已应用的迁移: $filename"
        return 0
    fi

    log "应用迁移: $filename"

    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file" >> "$LOG_FILE" 2>&1; then
        log "迁移 $filename 应用成功"
        return 0
    else
        error "迁移 $filename 应用失败，请查看日志: $LOG_FILE"
        return 1
    fi
}

# ============================================
# 主流程
# ============================================

main() {
    log "======================================"
    log "SillyMD 数据库迁移开始"
    log "======================================"
    log "数据库: $DB_NAME@$DB_HOST:$DB_PORT"
    log "迁移目录: $MIGRATIONS_DIR"
    log "======================================"

    # 检查依赖
    check_dependencies

    # 检查连接
    check_connection

    # 检查数据库
    check_database

    # 获取所有迁移文件（按版本号排序）
    info "扫描迁移文件..."
    MIGRATION_FILES=($(ls "$MIGRATIONS_DIR"/*.sql 2>/dev/null | sort))

    if [ ${#MIGRATION_FILES[@]} -eq 0 ]; then
        warn "未找到迁移文件"
        exit 0
    fi

    info "找到 ${#MIGRATION_FILES[@]} 个迁移文件"

    # 统计
    local total=${#MIGRATION_FILES[@]}
    local applied=0
    local skipped=0
    local failed=0

    # 执行每个迁移
    for migration in "${MIGRATION_FILES[@]}"; do
        if apply_migration "$migration"; then
            ((applied++))
        else
            ((failed++))
            error "迁移失败，停止执行"
            break
        fi
    done

    # 显示结果
    log "======================================"
    log "迁移执行完成"
    log "总迁移数: $total"
    log "应用成功: $applied"
    log "跳过: $skipped"
    log "失败: $failed"
    log "日志文件: $LOG_FILE"
    log "======================================"

    if [ "$failed" -gt 0 ]; then
        exit 1
    fi
}

# ============================================
# 信号处理
# ============================================

trap 'error "迁移被中断"; exit 130' INT

# ============================================
# 启动
# ============================================

main "$@"
