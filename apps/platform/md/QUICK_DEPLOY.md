# SillyMD 后端部署指南

> **更新时间**: 2026-04-30
> **预计部署时间**: 15-20分钟

---

## 部署前检查清单

### 服务器环境

- [ ] 服务器可达
- [ ] 数据库运行中：PostgreSQL 16 @ 5432
- [ ] Python 3.10+ 已安装
- [ ] Git 已安装
- [ ] Node.js 16+ 已安装 (构建前端)

### 数据库准备

- [ ] 数据库 sillymd 已创建
- [ ] 用户已授权
- [ ] 表结构已迁移

### 凭证准备

- [ ] 数据库密码
- [ ] JWT 密钥 (自行生成强随机字符串)
- [ ] 火山引擎 TOS 凭证 (可选，用于文件上传)

---

## 快速部署步骤

### 步骤1: 连接到服务器

```bash
ssh user@your-server-ip
```

### 步骤2: 进入项目目录

```bash
cd /opt/sillymd
```

### 步骤3: 检查代码更新

```bash
# 拉取最新代码（如果使用Git）
git pull origin main

# 确认新入口存在
ls -la src/main.py
```

### 步骤4: 安装 Python 依赖

```bash
cd src
pip install -r requirements.txt
```

### 步骤5: 配置环境变量

```bash
# 创建环境变量文件
cat > .env << 'EOF'
# 数据库配置
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=sillymd
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# JWT 密钥 (请修改为随机字符串)
JWT_SECRET=replace-with-a-random-string

# TOS 存储配置
TOS_ACCESS_KEY=your_tos_access_key
TOS_SECRET_KEY=your_tos_secret_key
TOS_ENDPOINT=tos-cn-shanghai.volces.com
TOS_BUCKET=your_bucket
TOS_CUSTOM_DOMAIN=your_custom_domain

# 应用配置
APP_ENV=production
APP_DEBUG=false
APP_URL=http://your-server-ip
EOF

# 保护环境变量文件
chmod 600 .env
```

### 步骤6: 测试数据库连接

```bash
python3 << 'EOF'
import psycopg2
try:
    conn = psycopg2.connect(
        host="your_db_host",
        port=5432,
        database="sillymd",
        user="your_db_user",
        password="your_db_password"
    )
    print("数据库连接成功")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    print(f"用户数: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM skills")
    print(f"Skills数: {cur.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"错误: {e}")
EOF
```

### 步骤7: 启动 API 服务

```bash
cd /opt/sillymd/src

# 方式1: 直接启动 (开发测试)
python main.py

# 方式2: uvicorn 启动 (推荐生产使用)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# 方式3: PM2 进程管理 (推荐)
pm2 start "uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4" --name sillymd-api
pm2 save
pm2 startup
```

### 步骤8: 构建管理后台

```bash
cd /opt/sillymd/admin-v2
npm install
npm run build
# 构建产物在 admin-v2/dist/
```

### 步骤9: 验证 API 服务

```bash
# 测试健康检查
curl http://localhost:8000/api/health
# {"status": "healthy", "database": "connected", "version": "2.0.0"}

# 测试 API 文档
curl http://localhost:8000/docs

# 测试模块列表
curl http://localhost:8000/api/v1/debug/routes

# 测试 Skills API
curl "http://localhost:8000/api/v1/skills?limit=5"
```

### 步骤10: 配置 Nginx

```bash
cat > /etc/nginx/sites-available/sillymd << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;

    # 管理后台静态文件 (admin-v2)
    location /admin {
        alias /opt/sillymd/admin-v2/dist;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    # 示例页面 (可选)
    location /examples {
        alias /opt/sillymd/examples;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # API 代理 - 统一前缀
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 文件上传大小限制
        client_max_body_size 50m;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/sillymd /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

### 步骤11: PM2 完整配置

创建 PM2 ecosystem 配置文件:

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'sillymd-api',
      script: 'uvicorn',
      args: 'src.main:app --host 0.0.0.0 --port 8000 --workers 4',
      cwd: '/opt/sillymd',
      interpreter: 'python3',
      env: {
        APP_ENV: 'production',
      },
      max_memory_restart: '500M',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/opt/sillymd/logs/api-error.log',
      out_file: '/opt/sillymd/logs/api-out.log',
    },
  ],
};
```

```bash
# 使用 ecosystem 配置启动
pm2 start ecosystem.config.js
pm2 save
```

### 步骤12: 访问测试

```bash
# 测试前端
curl http://your-domain.com/admin/

# 测试 API
curl http://your-domain.com/api/health

# 测试认证 API
curl -X POST http://your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sillymd.com","password":"admin123456"}'

# 测试 Skills API
curl "http://your-domain.com/api/v1/skills?limit=5"
```

---

## 文件上传配置 (TOS)

SillyMD v2.0 使用**火山引擎 TOS (Volcengine Object Storage)** 作为文件存储后端。

### 配置 TOS

```bash
export TOS_ACCESS_KEY='your_tos_access_key'
export TOS_SECRET_KEY='your_tos_secret_key'
export TOS_ENDPOINT='tos-cn-shanghai.volces.com'
export TOS_BUCKET='sillymd-uploads'
export TOS_CUSTOM_DOMAIN='https://cdn.your-domain.com'
```

> 注意: 旧 OSS 存储已废弃，请迁移至 TOS。

---

## 功能测试清单

### 认证功能

```bash
# 1. 注册用户
curl -X POST http://your-domain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"testuser",
    "email":"test@example.com",
    "password":"Test123456"
  }'

# 2. 登录
curl -X POST http://your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"Test123456"
  }'

# 保存返回的 access_token
export TOKEN="返回的token"

# 3. 获取当前用户
curl http://your-domain.com/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Skills 功能

```bash
# 1. 获取 Skills 列表
curl "http://your-domain.com/api/v1/skills?limit=10"

# 2. 获取 Skill 详情
curl "http://your-domain.com/api/v1/skills/seed_ai_trading_bot"

# 3. 搜索 Skills
curl "http://your-domain.com/api/v1/skills?search=AI&limit=5"
```

### 仪表板功能

```bash
# 1. 获取仪表板概览 (需要 Token)
curl http://your-domain.com/api/v1/dashboard/overview \
  -H "Authorization: Bearer $TOKEN"

# 2. 获取统计数据
curl http://your-domain.com/api/v1/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"
```

### 消息功能

```bash
# 1. 获取对话列表
curl http://your-domain.com/api/v1/messages/conversations \
  -H "Authorization: Bearer $TOKEN"

# 2. 创建对话
curl -X POST http://your-domain.com/api/v1/messages/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "direct",
    "participant_ids": [2]
  }'

# 3. 发送消息
curl -X POST http://your-domain.com/api/v1/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "content": "你好！"
  }'
```

### 文件上传测试

```bash
# 上传文件
curl -X POST http://your-domain.com/api/v1/storage/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.png" \
  -F "folder=test"

# 获取签名 URL
curl "http://your-domain.com/api/v1/storage/signed-url/uploads/test/test.png" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 常见问题排查

### 问题1: 数据库连接失败

```bash
could not connect to server: Connection refused
```

**解决**:
```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres

# 启动 PostgreSQL
docker start sillymd-postgres

# 检查端口监听
netstat -tlnp | grep 5432
```

### 问题2: API 服务无法启动 - 旧入口路径

```bash
# 确认启动了正确的新入口
cd /opt/sillymd/src
python main.py
# 或
uvicorn src.main:app --host 0.0.0.0 --port 8000

# 不要使用 server/api/main.py (已废弃)
```

### 问题3: 模块加载失败

```bash
# 检查模块列表
curl http://localhost:8000/api/v1/debug/routes

# 检查日志中是否有模块加载错误
pm2 logs sillymd-api --lines 50
```

### 问题4: JWT 认证失败

```bash
Could not validate credentials
```

**解决**:
```bash
# 检查 JWT_SECRET 是否设置
echo $JWT_SECRET

# 确保 Token 格式正确
Authorization: Bearer <token>

# 检查 Token 是否过期
```

### 问题5: TOS 上传失败

```bash
# 检查 TOS 配置
echo $TOS_ACCESS_KEY
echo $TOS_ENDPOINT
echo $TOS_BUCKET

# 确认 AccessKey 正确且有桶权限
```

### 问题6: Nginx 代理不工作

```bash
# 检查 Nginx 配置语法
nginx -t

# 检查 Nginx 错误日志
tail -f /var/log/nginx/error.log

# 确认 API 服务在运行
curl http://127.0.0.1:8000/api/health
```

---

## 性能优化建议

### 1. 启用 Gzip 压缩

已在 Nginx 配置中包含。

### 2. 配置缓存

```nginx
# 静态文件缓存 (已在 Nginx 配置中)
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 数据库优化

```sql
-- 创建关键索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_downloads_slug ON downloads(slug);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);

-- 定期维护
VACUUM ANALYZE;
```

### 4. uvicorn 工作进程

根据 CPU 核心数调整:
```bash
# 4 核服务器
uvicorn src.main:app --workers 4

# 8 核服务器
uvicorn src.main:app --workers 8
```

---

## 监控和日志

### 查看 API 日志

```bash
# PM2 日志
pm2 logs sillymd-api

# 实时日志
pm2 logs sillymd-api --lines 100

# 错误日志
pm2 logs sillymd-api --err
```

### 查看 Nginx 日志

```bash
# 访问日志
tail -f /var/log/nginx/access.log

# 错误日志
tail -f /var/log/nginx/error.log
```

---

## 部署验证脚本

```bash
#!/bin/bash
# deploy-test.sh

echo "开始部署验证测试..."

# 测试1: API 健康检查
echo "[1/6] 测试 API 健康检查..."
curl -s http://localhost:8000/api/health | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "  PASS: API 健康检查"
else
    echo "  FAIL: API 健康检查"
    exit 1
fi

# 测试2: 模块列表
echo "[2/6] 测试模块列表..."
curl -s http://localhost:8000/api/v1/debug/routes | grep -q "modules"
if [ $? -eq 0 ]; then
    echo "  PASS: 模块列表 API"
else
    echo "  FAIL: 模块列表 API"
    exit 1
fi

# 测试3: Skills 列表
echo "[3/6] 测试 Skills 列表..."
curl -s "http://localhost:8000/api/v1/skills?limit=1" | grep -q "code"
if [ $? -eq 0 ]; then
    echo "  PASS: Skills 列表 API"
else
    echo "  FAIL: Skills 列表 API"
    exit 1
fi

# 测试4: 用户注册
echo "[4/6] 测试用户注册..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"deploytest","email":"deploytest@example.com","password":"Test123456"}')

if echo $RESPONSE | grep -q "success\|already_exists"; then
    echo "  PASS: 用户注册 API"
else
    echo "  FAIL: 用户注册 API: $RESPONSE"
    exit 1
fi

# 测试5: Nginx 代理
echo "[5/6] 测试 Nginx 代理..."
curl -s http://localhost/api/health | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "  PASS: Nginx 代理"
else
    echo "  FAIL: Nginx 代理"
fi

# 测试6: 管理后台页面
echo "[6/6] 测试管理后台..."
curl -s http://localhost/admin/ | grep -q "<!DOCTYPE html>"
if [ $? -eq 0 ]; then
    echo "  PASS: 管理后台"
else
    echo "  FAIL: 管理后台"
fi

echo ""
echo "部署验证完成！"
```

---

## 部署完成

### 访问地址

- **管理后台**: http://your-domain.com/admin/
- **API 文档 (Swagger)**: http://your-domain.com:8000/docs
- **健康检查**: http://your-domain.com:8000/api/health
- **示例页面**: http://your-domain.com/examples/index.html

### 下一步

1. **配置域名和 HTTPS**
   ```bash
   # 使用 Let's Encrypt 获取免费 SSL 证书
   certbot --nginx -d your-domain.com
   ```

2. **配置 TOS 存储**
   ```bash
   export TOS_ACCESS_KEY='your_tos_access_key'
   export TOS_SECRET_KEY='your_tos_secret_key'
   export TOS_ENDPOINT='tos-cn-shanghai.volces.com'
   export TOS_BUCKET='sillymd-uploads'
   ```

3. **监控服务状态**
   ```bash
   pm2 status
   pm2 monit
   ```

4. **查看日志**
   ```bash
   pm2 logs sillymd-api
   ```

5. **设置自动备份**
   - 配置 PostgreSQL 自动备份
   - 配置 TOS 存储桶生命周期策略
   - 设置日志轮转

---

**最后更新**: 2026-04-30
