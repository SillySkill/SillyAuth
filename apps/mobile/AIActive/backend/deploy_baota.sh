#!/bin/bash
# 宝塔面板一键部署脚本 - 配置同步API

set -e

echo "======================================"
echo "  AI活动秀 - 配置同步API部署脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
PROJECT_PATH="/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity"
VENV_PATH="$PROJECT_PATH/venv"
SERVICE_NAME="aiactivity-config"
API_PORT="5000"
CONFIG_STORAGE_PATH="/var/www/config_storage"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用root用户执行此脚本"
    exit 1
fi

# 1. 创建必要的目录
log_info "创建目录结构..."
mkdir -p "$PROJECT_PATH/api"
mkdir -p "$CONFIG_STORAGE_PATH"
mkdir -p /var/log/aiactivity-config
chown -R www-data:www-data $CONFIG_STORAGE_PATH
chown -R www-data:www-data /var/log/aiactivity-config

# 2. 安装Python依赖
log_info "安装Python依赖..."
cd $PROJECT_PATH

if [ ! -d "$VENV_PATH" ]; then
    log_info "创建Python虚拟环境..."
    python3 -m venv $VENV_PATH
fi

log_info "激活虚拟环境并安装依赖..."
source $VENV_PATH/bin/activate
pip install --upgrade pip
pip install flask==2.3.0
pip install flask-cors==4.0.0
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0

# 3. 创建Gunicorn配置
log_info "创建Gunicorn配置..."
cat > $PROJECT_PATH/gunicorn_config.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:5000"
workers = max(2, multiprocessing.cpu_count())
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "/var/log/aiactivity-config/access.log"
errorlog = "/var/log/aiactivity-config/error.log"
loglevel = "info"
proc_name = "aiactivity-config"
daemon = False
EOF

# 4. 创建Systemd服务
log_info "创建Systemd服务..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=AI Activity Show Config Sync Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_PATH
Environment="PATH=$VENV_PATH/bin:/usr/bin"
ExecStart=$VENV_PATH/bin/gunicorn -c $PROJECT_PATH/gunicorn_config.py app:app
Restart=always
RestartSec=5
StandardOutput=append:/var/log/aiactivity-config/systemd.log
StandardError=append:/var/log/aiactivity-config/systemd.log

[Install]
WantedBy=multi-user.target
EOF

# 5. 配置Nginx
log_info "配置Nginx..."
NGINX_CONF="/www/server/panel/vhost/nginx/jcoding.chat.conf"

if [ -f "$NGINX_CONF" ]; then
    # 检查是否已配置
    if grep -q "application/com.jcoding.aiactivity/api/config/" "$NGINX_CONF"; then
        log_warn "Nginx配置已存在，跳过"
    else
        # 在server块中添加配置
        log_info "添加Nginx配置..."

        # 备份原配置
        cp $NGINX_CONF ${NGINX_CONF}.bak.$(date +%Y%m%d%H%M%S)

        # 添加配置（在最后一个 } 之前）
        sed -i '/^\s*}$/i \    # AI活动秀配置同步API\n    location /application/com.jcoding.aiactivity/api/config/ {\n        proxy_pass http://127.0.0.1:5000/api/config/;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n\n        client_max_body_size 100M;\n        proxy_read_timeout 300s;\n        proxy_connect_timeout 300s;\n        proxy_send_timeout 300s;\n    }\n' $NGINX_CONF

        log_info "Nginx配置已添加"
    fi
else
    log_warn "未找到Nginx配置文件: $NGINX_CONF"
    log_warn "请手动添加Nginx配置（见README）"
fi

# 6. 测试并重启Nginx
log_info "测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    log_info "重载Nginx..."
    nginx -s reload
else
    log_error "Nginx配置测试失败，请检查配置"
    exit 1
fi

# 7. 启动服务
log_info "启动配置同步服务..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 等待服务启动
sleep 3

# 8. 检查服务状态
if systemctl is-active --quiet $SERVICE_NAME; then
    log_info "服务启动成功！"
else
    log_error "服务启动失败，请查看日志："
    log_error "journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

# 9. 测试API
log_info "测试API..."
sleep 2

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:5000/api/config/version" || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "000" ]; then
    log_info "API本地测试通过"
else
    log_warn "API本地测试返回: $HTTP_CODE"
fi

# 10. 显示服务信息
echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "服务信息:"
echo "  服务名称: $SERVICE_NAME"
echo "  项目路径: $PROJECT_PATH"
echo "  配置存储: $CONFIG_STORAGE_PATH"
echo "  内部端口: $API_PORT"
echo ""
echo "管理命令:"
echo "  查看状态: systemctl status $SERVICE_NAME"
echo "  启动服务: systemctl start $SERVICE_NAME"
echo "  停止服务: systemctl stop $SERVICE_NAME"
echo "  重启服务: systemctl restart $SERVICE_NAME"
echo "  查看日志: journalctl -u $SERVICE_NAME -f"
echo ""
echo "API测试:"
echo "  curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version"
echo ""
echo "日志文件:"
echo "  应用日志: tail -f /var/log/aiactivity-config/error.log"
echo "  系统日志: journalctl -u $SERVICE_NAME -f"
echo ""
echo "下一步:"
echo "  1. 上传配置文件到 $CONFIG_STORAGE_PATH/v1.0.0/"
echo "  2. 发布版本: POST /api/config/publish"
echo ""
