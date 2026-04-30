#!/bin/bash
# 配置同步后端部署脚本
# 使用方法: bash deploy_config_sync.sh

set -e

echo "=== AI活动秀 - 配置同步后端部署 ==="

# 配置变量
SERVER_USER="root"
SERVER_HOST="your_server_ip"  # 请修改为实际服务器IP
SSH_KEY="e:/silly/md/.ignore/silly.pem"  # SSH密钥路径
REMOTE_PATH="/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity"
CONFIG_STORAGE_PATH="/var/www/config_storage"
VENV_PATH="/var/www/venv"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查本地文件
check_local_files() {
    log_info "检查本地文件..."

    if [ ! -f "api/config.py" ]; then
        log_error "api/config.py 不存在"
        exit 1
    fi

    if [ ! -f "app.py" ]; then
        log_error "app.py 不存在"
        exit 1
    fi

    log_info "本地文件检查完成"
}

# 上传文件到服务器
upload_files() {
    log_info "上传文件到服务器..."

    ssh -i "$SSH_KEY" ${SERVER_USER}@${SERVER_HOST} "mkdir -p $REMOTE_PATH/{api,utils}"

    scp -i "$SSH_KEY" api/config.py ${SERVER_USER}@${SERVER_HOST}:${REMOTE_PATH}/api/
    scp -i "$SSH_KEY" app.py ${SERVER_USER}@${SERVER_HOST}:${REMOTE_PATH}/
    scp -i "$SSH_KEY" requirements.txt ${SERVER_USER}@${SERVER_HOST}:${REMOTE_PATH}/

    log_info "文件上传完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."

    ssh -i "$SSH_KEY" ${SERVER_USER}@${SERVER_HOST} << EOF
        # 创建虚拟环境
        if [ ! -d "$VENV_PATH" ]; then
            python3 -m venv $VENV_PATH
        fi

        # 激活虚拟环境并安装依赖
        source $VENV_PATH/bin/activate
        cd $REMOTE_PATH
        pip install -r requirements.txt

        # 创建配置存储目录
        mkdir -p $CONFIG_STORAGE_PATH
EOF

    log_info "依赖安装完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."

    cat > /tmp/aiactivity_config.conf << EOF
location /application/com.jcoding.aiactivity/api/config/ {
    proxy_pass http://127.0.0.1:5000/api/config/;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;

    # 支持大文件上传
    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
}
EOF

    log_warn "请手动添加以下Nginx配置："
    cat /tmp/aiactivity_config.conf
    echo ""
    log_warn "Nginx配置文件位置: /etc/nginx/sites-available/default"
    log_warn "添加后执行: sudo nginx -t && sudo systemctl reload nginx"
}

# 配置Systemd服务
configure_service() {
    log_info "配置Systemd服务..."

    ssh -i "$SSH_KEY" ${SERVER_USER}@${SERVER_HOST} << 'EOF'
        cat > /etc/systemd/system/aiactivity-config.service << 'SERVICE'
[Unit]
Description=AI Activity Show Config Sync Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
Environment="PATH=/var/www/venv/bin"
Environment="FLASK_ENV=production"
Environment="CONFIG_STORAGE_PATH=/var/www/config_storage"
ExecStart=/var/www/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

        systemctl daemon-reload
        systemctl enable aiactivity-config
        systemctl restart aiactivity-config
        systemctl status aiactivity-config
EOF

    log_info "服务配置完成"
}

# 创建初始配置版本
create_initial_version() {
    log_info "创建初始配置版本..."

    ssh -i "$SSH_KEY" ${SERVER_USER}@${SERVER_HOST} << EOF
        # 创建版本目录
        mkdir -p $CONFIG_STORAGE_PATH/v1.0.0/{style,question,lottery,aibeing}

        # 从Android assets复制配置文件（需要先上传）
        # TODO: 请手动上传配置文件到相应目录

        # 创建初始版本清单
        cat > $CONFIG_STORAGE_PATH/versions.json << 'VERSIONS'
{
  "versions": {
    "v1.0.0": {
      "version": "v1.0.0",
      "version_code": 100,
      "released_at": "2025-01-01T00:00:00Z",
      "force_update": false,
      "min_compatible_version": "v1.0.0",
      "release_notes": "初始版本",
      "files": []
    }
  },
  "current": "v1.0.0"
}
VERSIONS
EOF

    log_info "初始版本创建完成"
}

# 测试API
test_api() {
    log_info "测试API..."

    sleep 3

    curl -s "https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version" | python3 -m json.tool || log_warn "API测试失败，请检查配置"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "=== 部署完成 ==="
    echo ""
    echo "后续步骤:"
    echo "1. 修改脚本中的 SERVER_HOST 为实际服务器IP"
    echo "2. 上传配置文件到服务器: $CONFIG_STORAGE_PATH/v1.0.0/"
    echo "3. 配置Nginx (见上面输出)"
    echo "4. 测试API: curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version"
    echo ""
    echo "发布新配置:"
    echo "curl -X POST https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/publish \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"version\": \"v1.0.1\", \"source_dir\": \"/path/to/config\"}'"
    echo ""
}

# 主流程
main() {
    log_info "开始部署配置同步后端..."

    check_local_files
    # upload_files  # 需要先配置SERVER_HOST
    # install_dependencies
    configure_nginx
    # configure_service  # 需要先配置SERVER_HOST
    # create_initial_version
    # test_api

    show_usage
}

main
