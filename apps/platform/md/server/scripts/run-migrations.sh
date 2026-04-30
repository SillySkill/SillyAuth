#!/bin/bash
# ============================================
# 数据库迁移执行脚本（服务器端）
# 版本: 1.0
# ============================================

set -e

DB_NAME="sillymd"
DB_USER="sillyAdmin"
MIGRATIONS_DIR="/opt/sillymd/migrations"

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

error() {
    echo "[ERROR] $*" >&2
    exit 1
}

main() {
    log "开始执行数据库迁移..."

    # 等待数据库就绪
    log "等待数据库就绪..."
    for i in {1..30}; do
        if docker exec sillymd-postgres pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
            log "数据库已就绪！"
            break
        fi
        sleep 1
    done

    # 按顺序执行迁移
    log "扫描迁移文件..."
    cd "$MIGRATIONS_DIR"

    for migration in 0*.sql; do
        log "执行迁移: $migration"
        docker exec -i sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" < "$migration"

        if [ $? -eq 0 ]; then
            log "✓ $migration 执行成功"
        else
            error "✗ $migration 执行失败"
        fi
    done

    log "======================================"
    log "所有迁移执行完成！"
    log "======================================"

    # 显示表统计
    docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT
        schemaname,
        COUNT(*) as table_count
    FROM pg_tables
    WHERE schemaname = 'public'
    GROUP BY schemaname;
    "

    # 显示迁移版本
    docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT version, description, applied_at
    FROM schema_migrations
    ORDER BY applied_at;
    "
}

main "$@"
