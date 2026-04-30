# 后台管理系统部署和使用说明

## 目录结构

```
backend/
├── api/
│   ├── admin_auth.py         # 认证API
│   ├── admin_apps.py         # 应用管理API
│   ├── admin_modules.py      # 模块配置API
│   ├── admin_assets.py       # 素材管理API
│   ├── admin_devices.py      # 设备管理API
│   ├── admin_push.py         # 推送管理API
│   └── ...
├── middleware/
│   └── auth.py               # JWT认证中间件
├── models_admin.py           # ORM模型定义
├── database_admin.py         # 异步数据库连接
├── app.py                    # Flask应用入口
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量配置示例
└── API_DOCUMENTATION.md      # API文档
```

## 安装步骤

### 1. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

主要依赖:
- Flask 2.3.0
- SQLAlchemy 2.0.23
- PyJWT 2.8.0
- bcrypt 4.0.1
- asyncpg 0.29.0 (PostgreSQL异步驱动)
- oss2 2.17.0 (阿里云OSS)

### 2. 配置环境变量

复制`.env.example`为`.env`并填入实际配置:

```bash
cp .env.example .env
```

编辑`.env`文件，填入以下配置:

```bash
# 数据库配置
DB_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://sillyAdmin:Jcoding2026@47.96.133.238:5432/sillymd

# JWT配置
JWT_SECRET=your-production-secret-key-change-this
JWT_EXPIRATION_HOURS=24

# 阿里云OSS配置
OSS_ACCESS_KEY_ID=REDACTED_ALIYUN_ACCESS_KEY
OSS_ACCESS_KEY_SECRET=REDACTED_ALIYUN_SECRET_KEY
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
OSS_BUCKET_NAME=jc-st
```

### 3. 初始化数据库

确保PostgreSQL数据库已创建，并运行初始化SQL:

```bash
psql -h 47.96.133.238 -U sillyAdmin -d sillymd -f database/admin_tables_pg.sql
```

这将创建:
- 7张数据表
- 1个默认管理员账号 (admin / admin123)
- 1个默认应用 (AI活动秀)
- 4个默认模块配置

### 4. 验证安装

启动Flask应用:

```bash
python app.py
```

或使用gunicorn (生产环境):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

测试健康检查端点:

```bash
curl http://localhost:5000/health
```

应返回:
```json
{"status": "healthy"}
```

## 测试API

### 1. 测试登录

```bash
curl -X POST https://www.jcoding.chat/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

成功响应:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "admin": {
      "id": 1,
      "username": "admin",
      "role": 1
    }
  }
}
```

### 2. 测试获取应用列表

保存从登录接口获取的token，然后:

```bash
TOKEN="your_token_here"

curl -X GET https://www.jcoding.chat/api/admin/apps \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 测试上传素材

```bash
TOKEN="your_token_here"

curl -X POST https://www.jcoding.chat/api/admin/apps/1/assets/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "asset_type=image" \
  -F "module_key=ai_show"
```

## API使用示例

### Python示例

```python
import requests

BASE_URL = "https://www.jcoding.chat/api/admin"

# 1. 登录获取token
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
data = response.json()
token = data['data']['token']

# 设置认证头
headers = {
    "Authorization": f"Bearer {token}"
}

# 2. 获取应用列表
response = requests.get(f"{BASE_URL}/apps", headers=headers)
apps = response.json()

# 3. 创建应用
response = requests.post(f"{BASE_URL}/apps", headers=headers, json={
    "app_name": "新应用",
    "package_name": "com.example.newapp",
    "version": "1.0.0"
})
app = response.json()

# 4. 上传素材
files = {
    'file': open('/path/to/image.jpg', 'rb')
}
data = {
    'asset_type': 'image',
    'module_key': 'ai_show'
}
response = requests.post(
    f"{BASE_URL}/apps/1/assets/upload",
    headers=headers,
    files=files,
    data=data
)
```

### JavaScript/Node.js示例

```javascript
const axios = require('axios');

const BASE_URL = 'https://www.jcoding.chat/api/admin';

async function main() {
  // 1. 登录
  const loginRes = await axios.post(`${BASE_URL}/auth/login`, {
    username: 'admin',
    password: 'admin123'
  });
  const token = loginRes.data.data.token;

  // 设置认证头
  const headers = {
    'Authorization': `Bearer ${token}`
  };

  // 2. 获取应用列表
  const appsRes = await axios.get(`${BASE_URL}/apps`, { headers });
  console.log(appsRes.data);

  // 3. 获取模块配置
  const modulesRes = await axios.get(`${BASE_URL}/apps/1/modules`, { headers });
  console.log(modulesRes.data);

  // 4. 上传素材
  const FormData = require('form-data');
  const fs = require('fs');
  const form = new FormData();
  form.append('file', fs.createReadStream('/path/to/image.jpg'));
  form.append('asset_type', 'image');
  form.append('module_key', 'ai_show');

  const uploadRes = await axios.post(
    `${BASE_URL}/apps/1/assets/upload`,
    form,
    {
      headers: {
        ...headers,
        ...form.getHeaders()
      }
    }
  );
  console.log(uploadRes.data);
}

main();
```

## 权限说明

系统支持两种角色:

1. **超级管理员 (role=1)**
   - 所有权限
   - 可以创建/删除应用
   - 可以管理所有管理员账号

2. **应用管理员 (role=2)**
   - 可以查看被授权的应用
   - 可以修改应用配置
   - 不能创建/删除应用

## 常见问题

### 1. Token过期怎么办?

JWT Token默认24小时过期。过期后需要重新登录获取新Token。

### 2. 如何修改管理员密码?

```bash
curl -X PUT https://www.jcoding.chat/api/admin/auth/password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin123",
    "new_password": "newpassword123"
  }'
```

### 3. 文件上传失败?

检查:
- 文件大小是否超过50MB限制
- OSS配置是否正确
- 网络连接是否正常

### 4. 数据库连接失败?

检查:
- DATABASE_URL是否正确
- 数据库是否启动
- 网络是否可达
- 用户权限是否足够

## 生产环境部署

### 使用Gunicorn

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务 (4个worker进程)
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### 使用Systemd管理服务

创建`/etc/systemd/system/sillymd-api.service`:

```ini
[Unit]
Description=AI Activity Show Admin API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/sillymd/server/api
Environment="PATH=/opt/sillymd/server/api/venv/bin"
ExecStart=/opt/sillymd/server/api/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl start sillymd-api
sudo systemctl enable sillymd-api
sudo systemctl status sillymd-api
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name api.jcoding.chat;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 文件上传大小限制
        client_max_body_size 50M;
    }
}
```

## 日志和监控

### 查看日志

```bash
# Systemd服务日志
sudo journalctl -u sillymd-api -f

# Gunicorn日志
tail -f /opt/sillymd/server/api/logs/app.log
```

### 监控指标

可以集成以下监控工具:
- Prometheus + Grafana
- Sentry (错误追踪)
- DataDog (APM)

## 安全建议

1. **修改默认密码**: 首次登录后立即修改admin密码
2. **使用HTTPS**: 生产环境必须使用HTTPS
3. **限制IP**: 在Nginx层限制管理后台的访问IP
4. **定期更新**: 及时更新依赖包修复安全漏洞
5. **备份**: 定期备份数据库和OSS文件
6. **审计**: 定期查看操作日志

## 维护命令

### 重启服务

```bash
sudo systemctl restart sillymd-api
```

### 查看服务状态

```bash
sudo systemctl status sillymd-api
```

### 查看错误日志

```bash
sudo journalctl -u sillymd-api --since today --priority err
```

### 数据库备份

```bash
pg_dump -h 47.96.133.238 -U sillyAdmin sillymd > backup_$(date +%Y%m%d).sql
```

### 数据库恢复

```bash
psql -h 47.96.133.238 -U sillyAdmin sillymd < backup_20260207.sql
```

## 联系支持

如遇到问题，请联系:
- Email: support@jcoding.tech
- GitHub Issues: https://github.com/your-repo/issues
