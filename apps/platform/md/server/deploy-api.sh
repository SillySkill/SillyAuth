#!/bin/bash
# ============================================
# SillyMD API 服务部署脚本
# ============================================

set -e

SERVER="47.96.133.238"
SSH_KEY=".ignore/silly.pem"
REMOTE_USER="root"
REMOTE_DIR="/opt/sillymd-api"
API_PORT=8000

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

error() {
    echo "[ERROR] $*" >&2
    exit 1
}

main() {
    log "======================================"
    log "SillyMD API 服务部署"
    log "======================================"

    # 1. 创建远程目录
    log "创建远程目录..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" "mkdir -p $REMOTE_DIR/api"

    # 2. 上传 API 文件
    log "上传 API 文件..."
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no api/* "$REMOTE_USER@$SERVER:$REMOTE_DIR/api/"

    # 3. 安装 Python 依赖
    log "安装 Python 依赖..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" << 'ENDSSH'
cd /opt/sillymd-api

# 安装 Python 包
pip3 install -q fastapi uvicorn psycopg2-binary pydantic 2>/dev/null || true

# 创建 requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
pydantic==2.5.0
python-dotenv==1.0.0
EOF
ENDSSH

    # 4. 创建环境变量文件
    log "配置环境变量..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" << 'ENDSSH'
cd /opt/sillymd-api

cat > .env << EOF
DB_HOST=47.96.133.238
DB_PORT=5432
DB_NAME=sillymd
DB_USER=sillyAdmin
DB_PASSWORD=Jcoding2026
EOF
ENDSSH

    # 5. 创建 systemd 服务
    log "创建 systemd 服务..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" << 'ENDSSH'
cat > /etc/systemd/system/sillymd-api.service << 'SERVICE'
[Unit]
Description=SillyMD API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sillymd-api
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# 重载 systemd
systemctl daemon-reload
ENDSSH

    # 6. 停止旧服务（如果有）
    log "停止旧服务..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" "systemctl stop sillymd-api 2>/dev/null || true"

    # 7. 启动服务
    log "启动 API 服务..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" << 'ENDSSH'
cd /opt/sillymd-api

# 测试启动
echo "测试 API 服务..."
/usr/local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 3

# 检查是否启动成功
if curl -s http://localhost:8000/ > /dev/null; then
    echo "API 服务测试成功，启动后台服务..."
    kill $API_PID 2>/dev/null || true
    systemctl start sillymd-api
    systemctl enable sillymd-api
else
    echo "API 服务测试失败，保持前台运行..."
    wait $API_PID
fi
ENDSSH

    # 8. 配置防火墙
    log "配置防火墙..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$SERVER" << 'ENDSSH'
if command -v ufw >/dev/null 2>&1; then
    ufw allow 8000/tcp 2>/dev/null || true
    ufw reload 2>/dev/null || true
fi

# 检查端口监听
echo "检查端口监听..."
sleep 2
netstat -tlnp | grep :8000 || echo "警告: 端口 8000 未监听"
ENDSSH

    log "======================================"
    log "API 服务部署完成！"
    log "======================================"
    cat << INFO
API 访问地址:
  http://47.96.133.238:8000

API 文档:
  http://47.96.133.238:8000/docs

健康检查:
  http://47.96.133.238:8000/api/health

常用命令:
  查看日志: ssh -i .ignore/silly.pem root@47.96.133.238 'journalctl -u sillymd-api -f'
  重启服务: ssh -i .ignore/silly.pem root@47.96.133.238 'systemctl restart sillymd-api'
  停止服务: ssh -i .ignore/silly.pem root@47.96.133.238 'systemctl stop sillymd-api'
  查看状态: ssh -i .ignore/silly.pem root@47.96.133.238 'systemctl status sillymd-api'
INFO
    log "======================================"
}

main "$@"
