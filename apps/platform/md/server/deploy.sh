#!/bin/bash
# ============================================
# SillyMD 数据库部署脚本
# 版本: 1.0
# ============================================

set -e

# 配置
SERVER="47.96.133.238"
SSH_KEY=".ignore/silly.pem"
REMOTE_USER="root"
REMOTE_DIR="/opt/sillymd"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

# ============================================
# 部署流程
# ============================================

main() {
    log "======================================"
    log "SillyMD 数据库部署开始"
    log "======================================"

    # 1. 检查本地文件
    log "检查本地文件..."
    if [ ! -f "$SSH_KEY" ]; then
        error "私钥文件不存在: $SSH_KEY"
        exit 1
    fi

    # 2. 创建远程目录
    log "创建远程目录..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" "mkdir -p $REMOTE_DIR/{scripts,migrations,seeds}"

    # 3. 上传文件
    log "上传配置文件..."
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no docker-compose.yml "$REMOTE_USER@$SERVER:$REMOTE_DIR/"

    log "上传迁移脚本..."
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -r migrations/*.sql "$REMOTE_USER@$SERVER:$REMOTE_DIR/migrations/"

    log "上传执行脚本..."
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no scripts/*.sh "$REMOTE_USER@$SERVER:$REMOTE_DIR/scripts/"

    log "上传种子数据..."
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -r ../seeds/output/*.json "$REMOTE_USER@$SERVER:$REMOTE_DIR/seeds/"

    # 4. 启动数据库
    log "启动 PostgreSQL 数据库..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" << 'ENDSSH'
cd /opt/sillymd
docker-compose down 2>/dev/null || true
docker-compose up -d

# 等待数据库启动
echo "等待数据库启动..."
for i in {1..30}; do
    if docker exec sillymd-postgres pg_isready -U sillyAdmin -d sillymd >/dev/null 2>&1; then
        echo "数据库已就绪！"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 2
done

# 显示容器状态
docker-compose ps
ENDSSH

    # 5. 执行迁移
    log "执行数据库迁移..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" "bash $REMOTE_DIR/scripts/run-migrations.sh"

    # 6. 导入种子数据
    log "导入种子数据..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" "bash $REMOTE_DIR/scripts/import-seeds.sh"

    log "======================================"
    log "部署完成！"
    log "======================================"
    log "数据库连接信息："
    log "  主机: $SERVER"
    log "  端口: 5432"
    log "  数据库: sillymd"
    log "  用户: sillyAdmin"
    log "  密码: Jcoding2026"
    log ""
    log "pgAdmin 访问地址："
    log "  http://$SERVER:5050"
    log "  邮箱: admin@sillymd.com"
    log "  密码: Jcoding2026"
    log "======================================"
}

main "$@"
