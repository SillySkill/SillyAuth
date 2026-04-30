# 应用配置管理系统部署指南

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (反向代理)                     │
│  /api/* → Flask (5000)                                  │
│  /admin/api/* → FastAPI (8000)                          │
└─────────────────────────────────────────────────────────┘
           │                      │
           ▼                      ▼
    ┌─────────────┐        ┌─────────────┐
    │  Flask App  │        │  FastAPI    │
    │  Port 5000  │        │  Port 8000  │
    └─────────────┘        └─────────────┘
           │                      │
           └──────────┬───────────┘
                      ▼
              ┌─────────────┐
              │   MySQL DB  │
              │ Port 3306   │
              └─────────────┘
```

## 部署步骤

### 1. 准备环境

#### 系统要求
- Python 3.8+
- MySQL 8.0+
- 2GB RAM minimum
- 20GB disk space

#### 安装系统依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv mysql-server nginx

# CentOS/RHEL
sudo yum install python3-pip python3-venv mysql-server nginx
```

### 2. 配置数据库

#### 创建数据库
```sql
CREATE DATABASE jc_ai_activity CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aiactivity'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON jc_ai_activity.* TO 'aiactivity'@'localhost';
FLUSH PRIVILEGES;
```

#### 创建数据表
```bash
cd /path/to/backend
python scripts/create_application_config_table.py
```

### 3. 配置Python环境

#### 创建虚拟环境
```bash
cd /path/to/backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

#### 创建 .env 文件
```bash
cp .env.example .env
```

#### 编辑 .env 文件
```bash
# 数据库配置
DB_TYPE=mysql
DATABASE_URL_MYSQL=mysql+aiomysql://aiactivity:your-strong-password@localhost:3306/jc_ai_activity

# JWT密钥（生产环境必须修改）
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Flask配置
FLASK_ENV=production

# 其他配置...
```

### 5. 初始化管理员账户

```bash
python scripts/init_admin.py
```

按照提示输入管理员信息。

### 6. 启动服务

#### 方式一：手动启动（开发/测试）

**启动Flask服务:**
```bash
source venv/bin/activate
python app.py
```

**启动FastAPI服务:**
```bash
source venv/bin/activate
python fastapi_app.py
```

#### 方式二：使用systemd（生产环境推荐）

**创建Flask服务文件** `/etc/systemd/system/aiactivity-flask.service`:
```ini
[Unit]
Description=AI活动秀 Flask服务
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/aiactivity/backend
Environment="PATH=/var/www/aiactivity/backend/venv/bin"
ExecStart=/var/www/aiactivity/backend/venv/bin/gunicorn app:app \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/aiactivity/flask-access.log \
    --error-logfile /var/log/aiactivity/flask-error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**创建FastAPI服务文件** `/etc/systemd/system/aiactivity-fastapi.service`:
```ini
[Unit]
Description=AI活动秀 FastAPI服务
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/aiactivity/backend
Environment="PATH=/var/www/aiactivity/backend/venv/bin"
ExecStart=/var/www/aiactivity/backend/venv/bin/uvicorn fastapi_app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-config /var/www/aiactivity/backend/logging.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**创建日志目录:**
```bash
sudo mkdir -p /var/log/aiactivity
sudo chown www-data:www-data /var/log/aiactivity
```

**启动服务:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable aiactivity-flask
sudo systemctl enable aiactivity-fastapi
sudo systemctl start aiactivity-flask
sudo systemctl start aiactivity-fastapi
```

**查看状态:**
```bash
sudo systemctl status aiactivity-flask
sudo systemctl status aiactivity-fastapi
```

### 7. 配置Nginx反向代理

#### 创建Nginx配置文件 `/etc/nginx/sites-available/aiactivity`:

```nginx
upstream flask_backend {
    server 127.0.0.1:5000;
}

upstream fastapi_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 日志
    access_log /var/log/nginx/aiactivity-access.log;
    error_log /var/log/nginx/aiactivity-error.log;

    # Flask API路由
    location /api/ {
        proxy_pass http://flask_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # FastAPI后台管理路由
    location /admin/api/ {
        rewrite ^/admin/api/(.*)$ /api/$1 break;
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持（如果需要）
    location /ws {
        proxy_pass http://flask_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 前端静态文件（如果需要）
    location / {
        root /var/www/aiactivity/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 启用配置
```bash
sudo ln -s /etc/nginx/sites-available/aiactivity /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

### 8. 配置SSL（HTTPS，推荐）

#### 使用Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Certbot会自动配置SSL并更新Nginx配置。

### 9. 验证部署

#### 检查服务状态
```bash
# 检查服务是否运行
sudo systemctl status aiactivity-flask
sudo systemctl status aiactivity-fastapi
sudo systemctl status nginx
sudo systemctl status mysql

# 检查端口监听
sudo netstat -tlnp | grep -E '5000|8000|3306|80|443'
```

#### 测试API
```bash
# 测试Flask服务
curl http://localhost:5000/health

# 测试FastAPI服务
curl http://localhost:8000/health

# 测试Nginx反向代理
curl http://your-domain.com/health
```

#### 运行测试脚本
```bash
cd /path/to/backend
source venv/bin/activate
python test_application_config_api.py
```

## 监控和维护

### 查看日志

**Flask服务日志:**
```bash
sudo journalctl -u aiactivity-flask -f
# 或
tail -f /var/log/aiactivity/flask-error.log
```

**FastAPI服务日志:**
```bash
sudo journalctl -u aiactivity-fastapi -f
```

**Nginx日志:**
```bash
tail -f /var/log/nginx/aiactivity-access.log
tail -f /var/log/nginx/aiactivity-error.log
```

### 数据库备份

**创建备份脚本** `/usr/local/bin/backup_aiactivity.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/aiactivity"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 数据库备份
mysqldump -u aiactivity -p'your-password' jc_ai_activity | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 保留最近7天的备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
```

**添加到crontab:**
```bash
sudo crontab -e
# 每天凌晨2点备份
0 2 * * * /usr/local/bin/backup_aiactivity.sh
```

### 性能优化

#### MySQL优化
编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
[mysqld]
# 连接数
max_connections = 200

# 缓冲池大小（根据可用内存调整）
innodb_buffer_pool_size = 1G

# 日志文件大小
innodb_log_file_size = 256M

# 查询缓存
query_cache_size = 64M
query_cache_type = 1
```

#### Nginx优化
编辑 `/etc/nginx/nginx.conf`:
```nginx
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
gzip on;
gzip_types text/plain application/json application/javascript;
```

### 故障排查

#### 服务无法启动
```bash
# 查看详细错误
sudo journalctl -u aiactivity-flask -n 50 --no-pager
sudo journalctl -u aiactivity-fastapi -n 50 --no-pager

# 检查端口占用
sudo lsof -i :5000
sudo lsof -i :8000
```

#### 数据库连接失败
```bash
# 检查MySQL状态
sudo systemctl status mysql

# 测试连接
mysql -u aiactivity -p jc_ai_activity

# 检查防火墙
sudo ufw status
sudo ufw allow 3306  # 如果需要远程访问
```

#### API请求失败
```bash
# 检查Nginx错误日志
sudo tail -f /var/log/nginx/aiactivity-error.log

# 测试后端直接访问
curl http://localhost:5000/health
curl http://localhost:8000/health

# 检查JWT token是否有效
```

## 安全建议

1. **修改默认密码**: 更改数据库密码、JWT密钥、管理员密码
2. **限制访问**: 配置防火墙，只开放必要的端口
3. **使用HTTPS**: 在生产环境启用SSL
4. **定期更新**: 及时更新系统和依赖包
5. **日志监控**: 定期检查日志，发现异常行为
6. **备份策略**: 建立定期备份机制
7. **权限分离**: 使用不同的数据库用户，遵循最小权限原则

## 升级指南

### 更新代码
```bash
cd /var/www/aiactivity/backend
git pull  # 或使用其他部署方式

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl restart aiactivity-flask
sudo systemctl restart aiactivity-fastapi
```

### 数据库迁移
如果有数据库结构变更：
```bash
# 使用alembic进行迁移
alembic upgrade head
```

## 联系支持

如有问题，请参考：
- 项目文档: `/backend/README_ADMIN.md`
- API文档: `/backend/APPLICATION_CONFIG_API.md`
- 故障排查日志
