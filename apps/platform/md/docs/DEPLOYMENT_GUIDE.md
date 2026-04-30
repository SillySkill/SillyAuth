# 平台部署指南 (Phase 1)

> **版本**: v2.0.0
> **发布日期**: 2026-04-29
> **状态**: Phase 1 模块化架构已激活
> **入口点**: `src/main.py` (替代旧 `server/api/main.py`)
> **注意**: 旧 `server/api/` 文件已废弃, 即将移除

---

## 目录

- [系统概述](#系统概述)
- [技术栈 (Phase 1)](#技术栈-phase-1)
- [系统架构 (Phase 1)](#系统架构-phase-1)
- [部署前准备](#部署前准备)
- [数据库部署](#数据库部署)
- [后端部署 (Phase 1 - 新入口)](#后端部署-phase-1---新入口)
- [前端部署 (admin-v2)](#前端部署-admin-v2)
- [系统测试](#系统测试)
- [监控和维护](#监控和维护)
- [故障排查](#故障排查)

---

## 系统概述 (Phase 1)

SillyMD 模块化平台, 用于管理内容、用户、支付、分析和配置同步。

### 核心模块

1. **CMS 内容管理** - 教程、资源、用户生成内容管理
2. **认证模块** - JWT 认证 + RBAC 权限控制 (已修复: 真实 DB)
3. **管理模块** - 模块化系统管理 (已修复: `%s` 参数化)
4. **支付模块** - 订单、PayPal、创作者结算 (已修复: 4个TODO)
5. **tutorials** - 教程管理 (新增模块)
6. **dashboard** - 仪表盘 (新增模块)
7. **analytics** - 数据分析 (新增模块)
8. **config_sync** - 配置同步 (新增模块)
9. **store** - 商店 (新增模块)

---

## 技术栈 (Phase 1)

### 后端 (新模块化架构)
```
Python 3.9+
FastAPI
PluginManager (模块自动加载)
psycopg2 (通过 db_adapter)
PostgreSQL 16+
```

### 管理前端
```
React 18
Ant Design 5
Vite 5
```

### 存储 (迁移中)
```
Volcengine TOS (迁移中, 替代阿里云 OSS)
```

---

## 系统架构 (Phase 1)

```
┌─────────────────────────────────────────────────────────────┐
│              管理前端 (React 18 + Ant Design 5)              │
│  admin-v2: Dashboard | CMS | Payment | Analytics | Admin   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (/api/v1/{module}/*)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              SillyMD 模块化后端 (src/main.py)                 │
│                                                             │
│  PluginManager.load_all_modules()                            │
│  ├─ core/ → db_adapter, config, auth                        │
│  └─ modules/ → cms, auth, admin, payment, tutorials,        │
│                 dashboard, analytics, config_sync, store     │
└────────────────────────┬────────────────────────────────────┘
                         │ psycopg2 via db_adapter
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL 数据库 (27+ 表)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 部署前准备

### 1. 服务器要求

**最低配置**:
- CPU: 2 核
- 内存: 4 GB
- 磁盘: 20 GB SSD
- 操作系统: Ubuntu 20.04 / CentOS 8 / Windows Server 2019

**推荐配置**:
- CPU: 4 核
- 内存: 8 GB
- 磁盘: 50 GB SSD
- 操作系统: Ubuntu 22.04 LTS

### 2. 软件要求

```bash
# Python 3.9+
python --version

# PostgreSQL 14+
psql --version

# Node.js 18+
node --version

# Git
git --version
```
### 3. 网络要求

- 开放端口: 80 (HTTP), 443 (HTTPS), 5000 (FastAPI API)
- 数据库端口: 5432 (仅内网)
- 防火墙规则允许外部访问

---

## 数据库部署 (Phase 1 - PostgreSQL)

### 步骤 1: 创建数据库

```bash
# 登录 PostgreSQL
psql -U postgres -h localhost

# 创建数据库
CREATE DATABASE sillymd;

# 创建用户
CREATE USER sillyAdmin WITH PASSWORD 'your_secure_password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE sillymd TO sillyAdmin;
GRANT ALL PRIVILEGES ON SCHEMA public TO sillyAdmin;
```

### 步骤 2: 导入数据库架构

```bash
# 进入迁移脚本目录
cd E:\silly\apps\platform\md\src\migrations

# 按顺序导入
psql -U sillyAdmin -d sillymd -f 001_init_database.sql
psql -U sillyAdmin -d sillymd -f 002_add_users.sql
psql -U sillyAdmin -d sillymd -f 003_add_tutorials_and_downloads.sql
psql -U sillyAdmin -d sillymd -f 004_add_ugc_and_payment.sql
psql -U sillyAdmin -d sillymd -f 005_add_commission_and_points.sql
psql -U sillyAdmin -d sillymd -f 006_add_paypal_and_settlement.sql
psql -U sillyAdmin -d sillymd -f 007_add_points_mall.sql
psql -U sillyAdmin -d sillymd -f 008_add_task_system.sql
```

### 步骤 3: 验证表结构

```bash
psql -U sillyAdmin -d sillymd -c "\dt"
```

预期输出: 27+ 表 (users, skills, tutorials, downloads, orders, payment_records, 等)

---

## 后端部署

### 步骤 1: 安装 Python 依赖

```bash
# 进入项目目录
cd "D:\AIProgram\Claude Code\jcoden"

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 配置应用

创建 `config.py` 文件:

```python
# config.py
import os

class Config:
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_NAME = os.environ.get('DB_NAME', 'jc_ai')
    DB_USER = os.environ.get('DB_USER', 'jc_admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS 配置
    CORS_ORIGINS = ['http://localhost:3000', 'https://admin.jcoding.tech']

    # WebSocket 配置
    WEBSOCKET_HOST = '0.0.0.0'
    WEBSOCKET_PORT = 5100

    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### 步骤 3: 初始化 WebSocket

编辑 `www.py` (或 `app.py`):

```python
from flask import Flask
from flask_cors import CORS
from websocket import init_push_system

# 创建应用
app = Flask(__name__)
app.config.from_object('config')

# 启用 CORS
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

# 初始化数据库
from common.db import db
db.init_app(app)

# 初始化 WebSocket 推送系统
socketio = init_push_system(app, db)

# 注册蓝图
from web.controllers.admin.app_management.AppManagement import app_management_bp
app.register_blueprint(app_management_bp, url_prefix='/api/admin')

from web.controllers.api.ConfigPush import config_push_bp
app.register_blueprint(config_push_bp, url_prefix='/api/push')

if __name__ == '__main__':
    # 使用 socketio.run 而不是 app.run
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
```

### 步骤 4: 创建启动脚本

**Windows (`start.bat`)**:
```batch
@echo off
call venv\Scripts\activate
python www.py
pause
```

**Linux/Mac (`start.sh`)**:
```bash
#!/bin/bash
source venv/bin/activate
python www.py
```

### 步骤 5: 使用 Supervisor 管理进程

创建 `/etc/supervisor/conf.d/jc_ai.conf`:

```ini
[program:jc_ai]
command=/path/to/jcoden/venv/bin/python /path/to/jcoden/www.py
directory=/path/to/jcoden
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/jc_ai.err.log
stdout_logfile=/var/log/jc_ai.out.log
environment=SECRET_KEY="your-secret-key"
```

启动服务:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start jc_ai
```

---

## 前端部署

### 步骤 1: 安装依赖

```bash
cd "D:\AIProgram\Claude Code\jcoden\frontend"
npm install
```

### 步骤 2: 配置环境变量

创建 `.env.production`:

```env
# API 地址
VITE_API_BASE_URL=https://api.jcoding.tech/api
VITE_WS_BASE_URL=wss://api.jcoding.tech/ws

# 应用配置
VITE_APP_TITLE=AI 活动秀管理后台
VITE_APP_VERSION=1.0.0
```

### 步骤 3: 构建生产版本

```bash
npm run build
```

输出目录: `dist/`

### 步骤 4: 部署到 Nginx

创建 Nginx 配置 `/etc/nginx/sites-available/jc_ai_admin`:

```nginx
server {
    listen 80;
    server_name admin.jcoding.tech;

    # 前端静态文件
    location / {
        root /path/to/jcoden/frontend/dist;
        try_files $uri $uri/ /index.html;

        # 缓存配置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://localhost:5100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # 文件上传大小限制
    client_max_body_size 16M;
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/jc_ai_admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤 5: 配置 SSL (推荐)

使用 Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d admin.jcoding.tech
```

---

## WebSocket 服务部署

WebSocket 已集成到主应用中，无需单独部署。

### 验证 WebSocket 服务

使用测试客户端:

```bash
cd "D:\AIProgram\Claude Code\jcoden"
pip install websockets
python test_push_client.py
```

或使用 wscat:

```bash
npm install -g wscat
wscat -c "ws://localhost:5100/?device_id=test&token=test"
```

---

## Android 客户端集成

### 步骤 1: 添加 OkHttp 依赖

已存在于 `android/app/build.gradle`:

```gradle
dependencies {
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
}
```

### 步骤 2: 配置服务器地址

编辑 `ConfigPushClient.java`:

```java
private static final String WS_URL = "wss://api.jcoding.tech/ws";
private static final String API_BASE_URL = "https://api.jcoding.tech/api";
```

### 步骤 3: 在 Application 中启动

编辑 `MyApplication.java`:

```java
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();

        // 启动推送管理器
        ConfigPushManager.getInstance(this).start();
    }
}
```

### 步骤 4: 添加权限

编辑 `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### 步骤 5: 构建和测试

```bash
cd android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## 系统测试

### 1. 后端 API 测试

```bash
cd "D:\AIProgram\Claude Code\jcoden"
python test_api.py
```

### 2. WebSocket 测试

```bash
python test_push_client.py
```

### 3. 前端测试

访问: `https://admin.jcoding.tech`

检查:
- ✅ 页面正常加载
- ✅ 登录功能
- ✅ API 调用正常
- ✅ WebSocket 连接成功

### 4. Android 客户端测试

```bash
adb logcat | grep -E "ConfigPush|ConfigManager"
```

预期输出:
```
I/ConfigPushClient: WebSocket connected
I/ConfigPushManager: Device registered successfully
I/ConfigManager: Config updated via push
```

### 5. 端到端测试流程

1. **登录后台** → https://admin.jcoding.tech
2. **创建应用** → 应用管理 → 新建应用
3. **查看设备** → 设备管理 → 应该看到注册的设备
4. **编辑配置** → 配置管理 → 创建新配置
5. **推送配置** → 推送中心 → 批量推送
6. **Android 端** → 应用接收推送并自动更新

---

## 监控和维护

### 日志位置

```
后端日志: /var/log/jc_ai.out.log
错误日志: /var/log/jc_ai.err.log
Nginx 日志: /var/log/nginx/
```

### 数据库备份

```bash
# 每日备份
0 2 * * * mysqldump -u jc_admin -p jc_ai > /backup/jc_ai_$(date +\%Y\%m\%d).sql

# 保留最近 30 天
find /backup -name "jc_ai_*.sql" -mtime +30 -delete
```

### 监控指标

使用 Prometheus + Grafana:

```python
from prometheus_flask_exporter import PrometheusMetrics

# 在 www.py 中
PrometheusMetrics(app)
```

访问: `http://localhost:5000/metrics`

---

## 故障排查

### 问题 1: WebSocket 连接失败

**症状**: 客户端无法连接到 WebSocket 服务器

**解决方案**:
```bash
# 检查端口监听
netstat -tlnp | grep 5100

# 检查防火墙
sudo ufw allow 5100

# 检查 Nginx 配置
sudo nginx -t
```

### 问题 2: 配置推送失败

**症状**: 推送任务卡住或失败

**解决方案**:
```bash
# 查看推送任务状态
mysql -u jc_admin -p jc_ai -e "SELECT * FROM push_tasks WHERE status = 'failed';"

# 检查设备在线状态
mysql -u jc_admin -p jc_ai -e "SELECT * FROM device_online_status WHERE is_online = 0;"
```

### 问题 3: Android 客户端不接收推送

**症状**: 推送成功但客户端未更新

**解决方案**:
```bash
# 查看客户端日志
adb logcat | grep ConfigPush

# 检查网络连接
adb shell ping -c 3 api.jcoding.tech

# 验证设备注册
mysql -u jc_admin -p jc_ai -e "SELECT * FROM devices WHERE device_id = 'your_device_id';"
```

### 问题 4: 前端无法加载配置

**症状**: API 调用返回 404 或 500

**解决方案**:
```bash
# 检查后端服务状态
sudo supervisorctl status jc_ai

# 检查 Nginx 代理配置
curl http://localhost:5000/api/admin/apps

# 查看后端日志
tail -f /var/log/jc_ai.out.log
```

---

## 性能优化建议

### 1. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_devices_app_id ON devices(app_id);
CREATE INDEX idx_push_tasks_status ON push_tasks(status);

-- 分区大表
ALTER TABLE config_push_history PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

### 2. Redis 缓存

```python
import redis

# 添加到 www.py
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 缓存设备状态
@app.before_request
def cache_device_status():
    key = f'device:{device_id}:status'
    cached = redis_client.get(key)
    if cached:
        return jsonify(json.loads(cached))
```

### 3. 异步任务

```python
from celery import Celery

# 创建 celery_app.py
celery = Celery('jc_ai', broker='redis://localhost:6379/0')

# 异步推送
@celery.task
def async_push_config(device_id, config_id):
    # 推送逻辑
    pass
```

---

## 安全加固

### 1. 启用 HTTPS

```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d api.jcoding.tech -d admin.jcoding.tech
```

### 2. API 认证

```python
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    # 验证 JWT token
    return User.verify_auth_token(token)

@app.route('/api/admin/apps')
@auth.login_required
def get_apps():
    pass
```

### 3. 速率限制

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/admin/push/batch')
@limiter.limit("10 per hour")
def batch_push():
    pass
```

---

## 支持和联系

- **文档**: 查看项目根目录下的各 README 文件
- **问题反馈**: GitHub Issues
- **技术支持**: tech@jcoding.tech

---

**最后更新**: 2026-02-06
**文档版本**: 1.0.0
