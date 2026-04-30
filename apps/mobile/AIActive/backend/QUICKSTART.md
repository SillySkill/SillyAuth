# 后台管理系统API - 快速开始指南

## 5分钟快速测试

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件，填入实际配置
# 最少需要配置:
# DATABASE_URL - 数据库连接
# JWT_SECRET - JWT密钥
# OSS_ACCESS_KEY_ID - OSS访问密钥
# OSS_ACCESS_KEY_SECRET - OSS密钥
```

### 3. 初始化数据库

确保数据库已创建并运行初始化SQL:

```bash
psql -h YOUR_HOST -U YOUR_USER -d YOUR_DB -f database/admin_tables_pg.sql
```

### 4. 启动服务

```bash
# 开发环境
python app.py

# 或使用gunicorn (生产环境)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 5. 测试API

#### 方法1: 使用自动化测试脚本

```bash
python test_admin_api.py
```

#### 方法2: 手动测试

```bash
# 1. 登录获取Token
curl -X POST http://localhost:5000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 保存返回的token，然后使用它访问其他接口
TOKEN="从上一步获取的token"

# 2. 获取应用列表
curl -X GET http://localhost:5000/api/admin/apps \
  -H "Authorization: Bearer $TOKEN"

# 3. 获取模块配置
curl -X GET http://localhost:5000/api/admin/apps/1/modules \
  -H "Authorization: Bearer $TOKEN"
```

## 核心API速查

### 认证
```bash
# 登录
POST /api/admin/auth/login
Body: {"username":"admin","password":"admin123"}

# 获取个人信息
GET /api/admin/auth/profile
Headers: Authorization: Bearer {token}
```

### 应用管理
```bash
# 获取应用列表
GET /api/admin/apps

# 创建应用
POST /api/admin/apps
Body: {"app_name":"新应用","package_name":"com.example.app"}

# 获取应用统计
GET /api/admin/apps/1/stats
```

### 模块配置
```bash
# 获取所有模块
GET /api/admin/apps/1/modules

# 更新模块配置
PUT /api/admin/apps/1/modules/ai_show
Body: {"enabled":true,"config":{...}}
```

### 素材上传
```bash
# 上传单个文件
POST /api/admin/apps/1/assets/upload
Form: file=@image.jpg, asset_type=image

# 批量上传
POST /api/admin/apps/1/assets/batch-upload
Form: files=@file1.jpg&files=@file2.jpg
```

### 设备管理
```bash
# 获取设备列表
GET /api/admin/apps/1/devices

# 获取在线设备
GET /api/admin/apps/1/devices/online

# 获取设备统计
GET /api/admin/apps/1/devices/stats
```

### 推送管理
```bash
# 创建推送任务
POST /api/admin/apps/1/push/tasks
Body: {"task_name":"配置更新","push_type":1}

# 获取任务列表
GET /api/admin/apps/1/push/tasks
```

## 默认账号

```
用户名: admin
密码: admin123
```

⚠️ **重要**: 生产环境请立即修改默认密码！

## 常见问题

### Q: Token过期怎么办?
A: Token有效期24小时，过期后重新登录即可

### Q: 如何修改密码?
A: 使用 `PUT /api/admin/auth/password` 接口

### Q: 文件上传失败?
A: 检查文件大小（最大50MB）和OSS配置

### Q: 数据库连接失败?
A: 检查DATABASE_URL配置和数据库服务状态

## 下一步

1. 查看 `API_DOCUMENTATION.md` 了解完整API文档
2. 查看 `ADMIN_SYSTEM_SETUP.md` 了解部署详情
3. 开始开发前端管理界面

## 技术支持

- 完整文档: `backend/API_DOCUMENTATION.md`
- 部署指南: `backend/ADMIN_SYSTEM_SETUP.md`
- 测试脚本: `backend/test_admin_api.py`
