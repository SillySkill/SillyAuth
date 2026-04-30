# 平台运维与部署指南 (Phase 1)

> 本文档提供 SillyMD 平台的完整部署、运维和监控指南。
> 架构: 模块化系统 src/ (旧 server/api/ 已废弃)

## 目录

- [1. 系统架构说明](#1-系统架构说明)
- [2. 部署流程](#2-部署流程)
- [3. 运维操作](#3-运维操作)
- [4. 性能优化](#4-性能优化)
- [5. 安全加固](#5-安全加固)

---

## 1. 系统架构说明

### 1.1 整体架构

SillyMD 采用前后端分离的微服务架构，主要包含以下组件：

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  前端页面   │  │  管理后台    │  │  API 文档    │      │
│  │  (Vite)    │  │   (React)    │  │  (Swagger)   │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      应用服务层                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌──────────────────────┐        │
│  │   CMS 后端服务      │  │   API 服务           │        │
│  │   (Node.js/Express) │  │   (FastAPI/Python)   │        │
│  │   - 内容管理        │  │   - Skills API       │        │
│  │   - 用户认证        │  │   - 用户 API         │        │
│  │   - 权限控制        │  │   - 支付 API         │        │
│  └─────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       数据层                                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │    Redis     │  │  OSS 存储    │    │
│  │  (主数据库)  │  │  (缓存层)    │  │  (文件存储)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 模块关系

#### CMS 后端服务 (Node.js)

**端口**: 3001

**核心模块**:
- 认证授权: JWT + bcrypt
- 内容管理: Prisma ORM
- 文件上传: Multer
- 日志管理: Winston

**数据库表**:
- `users` - 用户表
- `contents` - 内容表
- `content_versions` - 内容版本表
- `navigations` - 导航表
- `carousels` - 轮播图表
- `skills` - 技能表
- `vendors` - 供应商表
- `seo_settings` - SEO 配置表
- `translations` - 翻译表
- `activity_logs` - 操作日志表
- `system_configs` - 系统配置表
- `media` - 媒体文件表

#### API 服务 (FastAPI)

**端口**: 8000

**核心模块**:
- Skills API: 技能市场数据
- 用户 API: 用户信息管理
- 支付 API: 支付宝/贝宝集成
- 结算 API: 创作者收益结算

**数据库表**:
- `skills` - 技能市场表
- `users` - 用户扩展表
- `teams` - 团队表
- `team_members` - 团队成员表
- `payment_accounts` - 支付账户表
- `settlement_records` - 结算记录表
- `commissions` - 佣金记录表
- `ai_points_transactions` - AI 积分交易表

### 1.3 数据流向

```
1. 用户访问流程:
   浏览器 → Nginx (反向代理) → 静态资源/API网关 → 后端服务

2. 内容发布流程:
   管理后台 → CMS API → PostgreSQL → 内容版本记录

3. 技能交易流程:
   前端页面 → FastAPI → PostgreSQL → 支付网关 → 通知回调

4. 文件上传流程:
   前端上传 → Multer 中间件 → 本地存储/OSS → 返回 URL
```

### 1.4 技术栈

| 组件 | 技术选型 | 版本 |
|------|---------|------|
| 前端框架 | React 18 | ^18.2.0 |
| UI 组件 | Ant Design | ^5.12.8 |
| 后端框架 | FastAPI + PluginManager | - |
| 数据库 | PostgreSQL | 16 |
| DB驱动 | psycopg2 via db_adapter | - |
| 文件存储 | Volcengine TOS (迁移中) | - |
| 进程管理 | PM2 | 最新版 |

---

## 2. 部署流程

### 2.1 环境准备

#### 系统要求

- **操作系统**: Linux (Ubuntu 22.04 LTS 推荐) / CentOS 8+
- **CPU**: 2核及以上
- **内存**: 4GB 及以上 (推荐 8GB)
- **存储**: 40GB 及以上 (推荐 SSD)
- **网络**: 公网 IP，开放端口 80/443/3000/3001/8000

#### 软件依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim nginx

# 安装 Node.js (18.x)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Python (3.11)
sudo apt install -y python3.11 python3.11-venv python3-pip

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装 PM2
sudo npm install -g pm2

# 验证安装
node --version   # v18.x.x
python3 --version  # 3.11.x
docker --version  # 20.x.x
docker-compose --version  # 2.x.x
pm2 --version
```

### 2.2 依赖安装

#### 克隆代码

```bash
# 克隆仓库
git clone https://github.com/your-org/sillymd.git
cd sillymd

# 创建必要的目录
mkdir -p logs uploads backups
```

#### 安装后端依赖

```bash
# CMS 后端 (Node.js)
cd server
npm install

# API 服务 (Python)
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 安装前端依赖

```bash
# 管理后台
cd ../admin
npm install
```

### 2.3 数据库初始化

#### 方式一: Docker Compose 部署 PostgreSQL

```bash
cd /opt/sillymd

# 启动数据库
docker-compose up -d postgres

# 等待数据库就绪
docker-compose logs -f postgres

# 验证连接
docker exec -it sillymd-postgres psql -U sillyAdmin -d sillymd
```

#### 方式二: 云数据库 (推荐生产环境)

```bash
# 使用阿里云 RDS / 腾讯云 PostgreSQL
# 配置白名单、创建数据库、设置强密码
```

#### 执行数据库迁移

```bash
# 1. 创建迁移表
docker exec -i sillymd-postgres psql -U sillyAdmin -d sillymd << 'EOF'
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(14) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
EOF

# 2. 按顺序执行迁移文件
cd migrations

for migration in 0*.sql; do
    echo "执行迁移: $migration"
    docker exec -i sillymd-postgres psql -U sillyAdmin -d sillymd < "$migration"
done

# 3. 验证迁移
docker exec sillymd-postgres psql -U sillyAdmin -d sillymd -c "
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
"
```

### 2.4 配置说明

#### CMS 后端配置 (`server/.env`)

```bash
# 环境设置
NODE_ENV=production
PORT=3001
API_PREFIX=/api/v1

# 数据库连接
DATABASE_URL="postgresql://sillyAdmin:Jcoding2026@localhost:5432/sillymd"

# JWT 密钥 (必须修改为随机字符串)
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRES_IN=7d

# 文件上传
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# CORS 配置
CORS_ORIGIN=https://your-domain.com

# 日志级别
LOG_LEVEL=info
```

#### Phase 1 环境变量 (src/main.py)

```bash
# 数据库连接 (必须设置, 无默认值)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sillymd
DB_USER=sillyAdmin
DB_PASSWORD=your_secure_password

# JWT 密钥
JWT_SECRET=your-super-secret-jwt-key-change-this

# 支付配置
ALIPAY_APP_ID=your-alipay-app-id
ALIPAY_PRIVATE_KEY=your-alipay-private-key
ALIPAY_PUBLIC_KEY=your-alipay-public-key
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret

# 文件存储 (Volcengine TOS - 迁移中)
TOS_ACCESS_KEY=your-tos-access-key
TOS_SECRET_KEY=your-tos-secret-key
TOS_BUCKET=sillymd-resources
TOS_ENDPOINT=tos-cn-beijing.volces.com
```

#### 前端配置 (`admin-v2/.env.production`)

```bash
# API 基础地址 (统一 /api/v1/ 前缀)
VITE_API_BASE_URL=https://api.sillymd.com/api/v1

# WebSocket 地址
VITE_WS_BASE_URL=wss://api.sillymd.com/ws
```

### 2.5 启动服务

#### 构建前端

```bash
cd admin
npm run build

# 输出目录: admin/dist
```

#### 构建后端

```bash
cd server
npm run build

# 输出目录: server/dist
```

#### 使用 PM2 启动 (Phase 1 - 单入口)

```bash
# 创建 PM2 配置文件
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'sillymd',
      script: 'src/main.py',
      cwd: '/opt/sillymd',
      interpreter: 'venv/bin/python',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        PYTHONUNBUFFERED: 1
      },
      error_file: './logs/sillymd-error.log',
      out_file: './logs/sillymd-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      max_memory_restart: '1G'
    }
  ]
};
EOF

# 启动服务
pm2 start ecosystem.config.js

# 保存 PM2 配置
pm2 save
pm2 startup
```

#### 配置 Nginx 反向代理

```bash
# 创建 Nginx 配置
cat > /etc/nginx/sites-available/sillymd << 'EOF'
# CMS API 服务
server {
    listen 80;
    server_name api.your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件
    location /uploads {
        alias /opt/sillymd/server/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

# SillyMD API (Phase 1 - 单入口, 统一 /api/v1/)
server {
    listen 80;
    server_name api.sillymd.com;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# 管理后台 (admin-v2)
server {
    listen 80;
    server_name admin.sillymd.com;

    root /opt/sillymd/admin-v2/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/sillymd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 配置 SSL (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.your-domain.com \
                     -d api-public.your-domain.com \
                     -d admin.your-domain.com

# 自动续期
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 3. 运维操作

### 3.1 日常维护

#### 服务状态检查

```bash
# 检查 PM2 服务状态 (Phase 1 - 单服务)
pm2 status
pm2 logs sillymd --lines 50

# 检查 Nginx 状态
sudo systemctl status nginx

# 检查磁盘空间
df -h
du -sh /opt/sillymd/*
```

#### 日志管理

```bash
# 查看实时日志
pm2 logs sillymd-cms
pm2 logs sillymd-api

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# 日志轮转配置
cat > /etc/logrotate.d/sillymd << 'EOF'
/opt/sillymd/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
EOF
```

#### 服务重启 (Phase 1)

```bash
# 重启单个服务
pm2 restart sillymd

# 平滑重载 (零停机)
pm2 reload sillymd

# 重启 Nginx
sudo systemctl reload nginx
```

#### 数据库维护

```bash
# 连接数据库
docker exec -it sillymd-postgres psql -U sillyAdmin -d sillymd

# 查看连接数
SELECT count(*) FROM pg_stat_activity;

# 查看慢查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

# 真空清理
VACUUM ANALYZE;

# 重建索引
REINDEX DATABASE sillymd;

# 查看表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3.2 备份恢复

#### 数据库备份

```bash
# 创建备份脚本
cat > /opt/sillymd/scripts/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sillymd"
DB_USER="sillyAdmin"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 全量备份
docker exec sillymd-postgres pg_dump -U "$DB_USER" -d "$DB_NAME" \
    --format=custom --compress=9 \
    > "$BACKUP_DIR/sillymd_full_$DATE.dump"

# 备份元数据
docker exec sillymd-postgres pg_dump -U "$DB_USER" -d "$DB_NAME" \
    --schema-only --format=plain \
    > "$BACKUP_DIR/sillymd_schema_$DATE.sql"

# 删除 30 天前的备份
find "$BACKUP_DIR" -name "sillymd_*.dump" -mtime +30 -delete
find "$BACKUP_DIR" -name "sillymd_*.sql" -mtime +30 -delete

echo "备份完成: sillymd_full_$DATE.dump"
EOF

chmod +x /opt/sillymd/scripts/backup-db.sh

# 添加到 crontab (每天凌晨 2 点)
crontab -e
# 添加以下行:
0 2 * * * /opt/sillymd/scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

#### 文件备份

```bash
# 备份上传文件
cat > /opt/sillymd/scripts/backup-files.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/files"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/opt/sillymd/server/uploads"

mkdir -p "$BACKUP_DIR"

# 使用 rsync 增量备份
rsync -avz --delete \
    "$SOURCE_DIR/" \
    "$BACKUP_DIR/uploads/"

# 打包归档
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$BACKUP_DIR" uploads

# 上传到 OSS (可选)
# rclone copy "$BACKUP_DIR/uploads_$DATE.tar.gz" oss:sillymd-backups/

# 删除 7 天前的备份
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +7 -delete

echo "文件备份完成: uploads_$DATE.tar.gz"
EOF

chmod +x /opt/sillymd/scripts/backup-files.sh
```

#### 数据库恢复

```bash
# 恢复数据库
cat > /opt/sillymd/scripts/restore-db.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "用法: $0 <备份文件路径>"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="sillymd"
DB_USER="sillyAdmin"

# 停止应用服务
pm2 stop sillymd-cms sillymd-api

# 删除现有数据库
docker exec sillymd-postgres psql -U "$DB_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS $DB_NAME;"

# 创建新数据库
docker exec sillymd-postgres psql -U "$DB_USER" -d postgres \
    -c "CREATE DATABASE $DB_NAME;"

# 恢复备份
docker exec -i sillymd-postgres pg_restore -U "$DB_USER" -d "$DB_NAME" \
    --format=custom --verbose < "$BACKUP_FILE"

# 重启服务
pm2 start sillymd-cms sillymd-api

echo "数据库恢复完成"
EOF

chmod +x /opt/sillymd/scripts/restore-db.sh

# 使用示例
./restore-db.sh /opt/backups/postgresql/sillymd_full_20240204_020000.dump
```

### 3.3 监控告警

#### 系统监控

```bash
# 安装监控工具
sudo apt install -y htop iotop nethogs

# 实时监控
htop              # CPU/内存
iotop             # 磁盘 I/O
nethogs           # 网络流量
```

#### 应用监控

```bash
# PM2 监控
pm2 monit

# 查看服务详情
pm2 show sillymd-cms
pm2 show sillymd-api

# 查看内存使用
pm2 prettylist
```

#### 数据库监控

```bash
# PostgreSQL 监控脚本
cat > /opt/sillymd/scripts/check-db.sh << 'EOF'
#!/bin/bash

docker exec sillymd-postgres psql -U sillyAdmin -d sillymd << 'SQL'
-- 连接数
SELECT 'active_connections' as metric, count(*) as value
FROM pg_stat_activity WHERE state = 'active';

-- 数据库大小
SELECT 'database_size_gb' as metric,
    pg_database_size('sillymd')::numeric / 1024 / 1024 / 1024 as value;

-- 缓存命中率
SELECT 'cache_hit_ratio' as metric,
    round(sum(blks_hit)::numeric / (sum(blks_hit) + sum(blks_read)) * 100, 2) as value
FROM pg_stat_database WHERE datname = 'sillymd';

-- 慢查询数量
SELECT 'slow_queries' as metric, count(*) as value
FROM pg_stat_statements
WHERE mean_time > 1000;
SQL
EOF

chmod +x /opt/sillymd/scripts/check-db.sh
```

#### 告警配置

```bash
# 安装报警工具 (简单邮件通知)
sudo apt install -y mailutils

# 创建告警脚本
cat > /opt/sillymd/scripts/alert.sh << 'EOF'
#!/bin/bash
THRESHOLD_CPU=80
THRESHOLD_MEM=80
THRESHOLD_DISK=90

EMAIL="admin@your-domain.com"

# 检查 CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
if (( $(echo "$CPU_USAGE > $THRESHOLD_CPU" | bc -l) )); then
    echo "CPU 警告: 使用率 ${CPU_USAGE}%" | mail -s "SillyMD CPU 告警" $EMAIL
fi

# 检查内存
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
if (( $(echo "$MEM_USAGE > $THRESHOLD_MEM" | bc -l) )); then
    echo "内存警告: 使用率 ${MEM_USAGE}%" | mail -s "SillyMD 内存告警" $EMAIL
fi

# 检查磁盘
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt $THRESHOLD_DISK ]; then
    echo "磁盘警告: 使用率 ${DISK_USAGE}%" | mail -s "SillyMD 磁盘告警" $EMAIL
fi
EOF

chmod +x /opt/sillymd/scripts/alert.sh

# 添加到 crontab (每 10 分钟检查)
crontab -e
# 添加: */10 * * * * /opt/sillymd/scripts/alert.sh
```

### 3.4 故障排查

#### 常见问题

**1. 数据库连接失败**

```bash
# 检查数据库状态
docker ps | grep postgres
docker logs sillymd-postgres --tail 50

# 检查连接数
docker exec sillymd-postgres psql -U sillyAdmin -d sillymd -c "
    SELECT count(*) FROM pg_stat_activity;
"

# 检查最大连接数
docker exec sillymd-postgres psql -U sillyAdmin -d sillymd -c "
    SHOW max_connections;
"

# 增加最大连接数 (修改 docker-compose.yml)
max_connections: 200
```

**2. 服务无法启动**

```bash
# 查看详细错误
pm2 logs sillymd-cms --err
pm2 logs sillymd-api --err

# 检查端口占用
sudo lsof -i :3001
sudo lsof -i :8000

# 检查配置文件
cat /opt/sillymd/server/.env
cat /opt/sillymd/server/api/.env

# 测试数据库连接
docker exec sillymd-postgres pg_isready -U sillyAdmin -d sillymd
```

**3. 磁盘空间不足**

```bash
# 查找大文件
du -ah /opt/sillymd | sort -rh | head -20

# 清理 PM2 日志
pm2 flush

# 清理 Docker 镜像
docker system prune -a

# 清理旧备份
find /opt/backups -mtime +30 -delete
```

**4. API 响应慢**

```bash
# 查看慢查询
docker exec sillymd-postgres psql -U sillyAdmin -d sillymd -c "
    SELECT query, calls, total_time, mean_time
    FROM pg_stat_statements
    ORDER BY mean_time DESC
    LIMIT 10;
"

# 检查索引
docker exec sillymd-postgres psql -U sillyAdmin -d sillymd -c "
    SELECT schemaname, tablename, indexname, idx_scan
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0
    AND indexname NOT LIKE '%_pkey';
"

# 重启服务
pm2 restart all
```

**5. 文件上传失败**

```bash
# 检查上传目录权限
ls -la /opt/sillymd/server/uploads

# 修改权限
sudo chown -R $USER:$USER /opt/sillymd/server/uploads
sudo chmod -R 755 /opt/sillymd/server/uploads

# 检查 Nginx 上传限制
sudo vim /etc/nginx/sites-available/sillymd
# 修改: client_max_body_size 100M;

# 重启 Nginx
sudo systemctl reload nginx
```

---

## 4. 性能优化

### 4.1 数据库优化

#### 索引优化

```sql
-- 常用索引示例
CREATE INDEX CONCURRENTLY idx_contents_status_language ON contents(status, language);
CREATE INDEX CONCURRENTLY idx_contents_type_status ON contents(type, status);
CREATE INDEX CONCURRENTLY idx_skills_category_status ON skills(category, status);
CREATE INDEX CONCURRENTLY idx_skills_author_status ON skills(author_id, status);
CREATE INDEX CONCURRENTLY idx_activity_logs_user_created ON activity_logs(user_id, created_at);

-- 复合索引 (根据查询模式)
CREATE INDEX CONCURRENTLY idx_contents_search
ON contents USING GIN(to_tsvector('chinese', title || ' ' || content));

-- 分析查询计划
EXPLAIN ANALYZE SELECT * FROM contents WHERE status = 'PUBLISHED' AND language = 'zh';
```

#### 查询优化

```sql
-- 使用连接池 (PgBouncer)
-- 安装配置
sudo apt install -y pgbouncer

-- 配置文件 /etc/pgbouncer/pgbouncer.ini
[databases]
sillymd = host=localhost port=5432 dbname=sillymd

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 50
server_lifetime = 3600
server_idle_timeout = 600
```

#### 配置优化

```bash
# PostgreSQL 配置调优 (docker-compose.yml)
environment:
  - shared_buffers=256MB          # 总内存的 25%
  - effective_cache_size=1GB      # 总内存的 50-75%
  - maintenance_work_mem=64MB
  - checkpoint_completion_target=0.9
  - wal_buffers=16MB
  - default_statistics_target=100
  - random_page_cost=1.1          # SSD 使用
  - effective_io_concurrency=200  # SSD 使用
  - work_mem=1310kB
  - min_wal_size=1GB
  - max_wal_size=4GB
```

### 4.2 缓存策略

#### Redis 配置

```yaml
# docker-compose.yml 添加 Redis
redis:
  image: redis:7-alpine
  container_name: sillymd-redis
  restart: unless-stopped
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes --requirepass your-redis-password
  networks:
    - sillymd-network

volumes:
  redis_data:
```

#### 应用层缓存

```javascript
// CMS 后端缓存示例 (使用 Node-Cache)
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600, checkperiod: 120 });

// 获取内容 (带缓存)
async function getContent(key) {
  const cacheKey = `content:${key}`;
  let content = cache.get(cacheKey);

  if (!content) {
    content = await prisma.content.findUnique({ where: { key } });
    if (content) {
      cache.set(cacheKey, content);
    }
  }

  return content;
}

// 清除缓存
function clearContentCache(key) {
  cache.del(`content:${key}`);
}
```

#### HTTP 缓存

```nginx
# Nginx 缓存配置
http {
    # 静态资源缓存
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

    server {
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /api/ {
            proxy_cache api_cache;
            proxy_cache_valid 200 10m;
            proxy_cache_bypass $http_cache_control;
            add_header X-Cache-Status $upstream_cache_status;
        }
    }
}
```

### 4.3 负载均衡

#### Nginx 负载均衡

```nginx
# /etc/nginx/nginx.conf
http {
    # 后端服务器池
    upstream cms_backend {
        least_conn;
        server 127.0.0.1:3001;
        server 127.0.0.1:3002;  # 第二个实例
        server 127.0.0.1:3003;  # 第三个实例
        keepalive 32;
    }

    upstream api_backend {
        least_conn;
        server 127.0.0.1:8000;
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
        keepalive 32;
    }

    server {
        location /api/v1/ {
            proxy_pass http://cms_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }

        location /api/ {
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }
    }
}
```

#### PM2 集群模式

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'sillymd-cms',
      script: './dist/index.js',
      instances: 'max',      // 使用所有 CPU 核心
      exec_mode: 'cluster',  // 集群模式
      max_memory_restart: '1G'
    }
  ]
};
```

---

## 5. 安全加固

### 5.1 安全配置清单

#### 系统安全

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 配置防火墙
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 3. 禁用 root 登录
sudo vim /etc/ssh/sshd_config
# 修改: PermitRootLogin no
# 修改: PasswordAuthentication no
sudo systemctl restart sshd

# 4. 安装 fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 应用安全

```bash
# 1. 配置强密码策略
cat > /opt/sillymd/server/.env << 'EOF'
# 密码强度要求
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBER=true
PASSWORD_REQUIRE_SPECIAL=true
EOF

# 2. JWT 密钥安全 (使用随机字符串)
NODE_ENV=production
JWT_SECRET=$(openssl rand -base64 32)
JWT_EXPIRES_IN=24h

# 3. 数据库凭证安全
# 使用环境变量，不硬编码
DB_PASSWORD=$(openssl rand -base64 16)

# 4. 限制文件上传类型
# server/.env
ALLOWED_FILE_TYPES=.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx
MAX_FILE_SIZE=10485760
```

#### Nginx 安全配置

```nginx
# /etc/nginx/nginx.conf
http {
    # 隐藏版本号
    server_tokens off;

    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # 限速配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    server {
        # 请求限制
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;

        # 超时配置
        client_body_timeout 12s;
        client_header_timeout 12s;
        send_timeout 10s;
    }
}
```

#### 数据库安全

```sql
-- 1. 创建专用数据库用户 (不要使用 postgres)
CREATE USER sillyAdmin WITH PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE sillymd TO sillyAdmin;

-- 2. 限制远程连接 (pg_hba.conf)
host    sillymd    sillyAdmin    127.0.0.1/32    scram-sha-256
host    sillymd    sillyAdmin    ::1/128         scram-sha-256

-- 3. 启用 SSL 连接
-- 修改 postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

-- 4. 定期备份
-- 设置自动备份任务 (见 3.2 节)
```

### 5.2 定期检查项

#### 每日检查

- [ ] 检查服务运行状态 (`pm2 status`)
- [ ] 查看错误日志 (`pm2 logs --err`)
- [ ] 检查磁盘空间 (`df -h`)
- [ ] 检查数据库连接数
- [ ] 检查备份任务执行

#### 每周检查

- [ ] 检查系统更新 (`sudo apt list --upgradable`)
- [ ] 审查安全日志 (`sudo tail -100 /var/log/auth.log`)
- [ ] 检查慢查询
- [ ] 审查用户权限变更
- [ ] 测试备份恢复流程

#### 每月检查

- [ ] 执行系统安全更新
- [ ] 审查访问日志异常
- [ ] 检查证书有效期
- [ ] 审查 API 密钥轮换
- [ ] 性能基准测试
- [ ] 灾难恢复演练

#### 安全检查脚本

```bash
# 创建安全检查脚本
cat > /opt/sillymd/scripts/security-check.sh << 'EOF'
#!/bin/bash

echo "=== SillyMD 安全检查 ==="
echo ""

# 1. 检查过期的软件包
echo "1. 检查系统更新..."
apt list --upgradable 2>/dev/null | grep -c "upgradable"

# 2. 检查开放端口
echo "2. 检查开放端口..."
ss -tuln | grep LISTEN

# 3. 检查失败登录
echo "3. 检查失败登录次数..."
sudo grep "Failed password" /var/log/auth.log | wc -l

# 4. 检查 SSL 证书
echo "4. 检查 SSL 证书有效期..."
for cert in /etc/letsencrypt/live/*/cert.pem; do
    openssl x509 -enddate -noout -in "$cert"
done

# 5. 检查文件权限
echo "5. 检查敏感文件权限..."
ls -la /opt/sillymd/server/.env
ls -la /opt/sillymd/server/api/.env

# 6. 检查数据库连接
echo "6. 检查数据库连接..."
docker exec sillymd-postgres psql -U sillyAdmin -d sillymd -c "
    SELECT count(*) as active_connections
    FROM pg_stat_activity
    WHERE state = 'active';
"

echo ""
echo "=== 检查完成 ==="
EOF

chmod +x /opt/sillymd/scripts/security-check.sh

# 添加到 crontab (每周执行)
crontab -e
# 添加: 0 9 * * 1 /opt/sillymd/scripts/security-check.sh | mail -s "SillyMD 安全检查报告" admin@your-domain.com
```

---

## 附录

### A. 快速命令参考

```bash
# 服务管理
pm2 start ecosystem.config.js
pm2 stop all
pm2 restart all
pm2 delete all
pm2 save

# 日志查看
pm2 logs sillymd-cms
pm2 logs sillymd-api
pm2 flush

# 数据库操作
docker exec -it sillymd-postgres psql -U sillyAdmin -d sillymd
docker exec sillymd-postgres pg_dump -U sillyAdmin sillymd > backup.sql
docker exec -i sillymd-postgres psql -U sillyAdmin sillymd < backup.sql

# Nginx 操作
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx

# 备份恢复
/opt/sillymd/scripts/backup-db.sh
/opt/sillymd/scripts/restore-db.sh /path/to/backup.dump
```

### B. 端口映射表

| 服务 | 内部端口 | 外部端口 | 协议 |
|------|---------|---------|------|
| CMS 后端 | 3001 | 3001 | HTTP |
| FastAPI | 8000 | 8000 | HTTP |
| PostgreSQL | 5432 | 5432 | TCP |
| Redis | 6379 | 6379 | TCP |
| pgAdmin | 80 | 5050 | HTTP |
| Nginx | 80/443 | 80/443 | HTTP/HTTPS |

### C. 默认账号

| 系统 | 用户名 | 密码 | 说明 |
|------|-------|------|------|
| CMS 管理后台 | admin@sillymd.com | admin123456 | 需立即修改 |
| PostgreSQL | sillyAdmin | Jcoding2026 | 需立即修改 |
| pgAdmin | admin@sillymd.com | Jcoding2026 | 需立即修改 |

### D. 常用目录

```
/opt/sillymd/              # 项目根目录
├── server/                # CMS 后端
│   ├── dist/             # 编译输出
│   ├── uploads/          # 上传文件
│   └── logs/             # 日志文件
├── admin/                # 管理后台
│   └── dist/             # 构建输出
├── api/                  # FastAPI 服务
│   ├── venv/             # Python 虚拟环境
│   └── logs/             # 日志文件
├── scripts/              # 运维脚本
├── backups/              # 备份目录
└── logs/                 # 全局日志
```

### E. 联系方式

- 技术支持: support@sillymd.com
- 文档更新: 2024-02-04
- 版本: v1.0.0
