# AI活动秀 - 后台管理系统API

完整的后台管理系统后端API，支持应用管理、模块配置、素材管理、设备管理和配置推送。

## 🎯 功能特性

- ✅ **应用管理** - 应用的完整生命周期管理
- ✅ **模块配置** - 动态配置应用模块（AI百变秀、知识问答、幸运抽奖、内场秀）
- ✅ **素材管理** - 支持单文件和批量上传到阿里云OSS
- ✅ **设备管理** - 设备注册、状态监控、配置推送
- ✅ **推送管理** - 创建和管理配置推送任务
- ✅ **权限控制** - JWT认证 + 角色权限管理
- ✅ **操作日志** - 完整的操作审计追踪

## 📊 项目统计

- **API端点**: 36个
- **代码行数**: 3,045行
- **数据库模型**: 7个
- **功能模块**: 6个

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑.env文件，填入数据库和OSS配置
```

### 3. 初始化数据库

```bash
psql -h YOUR_HOST -U YOUR_USER -d YOUR_DB -f database/admin_tables_pg.sql
```

### 4. 启动服务

```bash
python app.py
```

### 5. 测试API

```bash
# 自动化测试
python test_admin_api.py

# 或手动测试
curl -X POST http://localhost:5000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📚 文档

- **[API文档](API_DOCUMENTATION.md)** - 完整的API接口文档
- **[部署指南](ADMIN_SYSTEM_SETUP.md)** - 详细的部署和配置说明
- **[快速开始](QUICKSTART.md)** - 5分钟快速上手
- **[完成清单](COMPLETION_CHECKLIST.md)** - 项目完成情况
- **[项目总结](ADMIN_API_SUMMARY.md)** - 技术总结报告

## 🔑 默认账号

```
用户名: admin
密码: admin123
```

⚠️ **生产环境请立即修改密码！**

## 📁 项目结构

```
backend/
├── api/
│   ├── admin_auth.py         # 认证API (4个端点)
│   ├── admin_apps.py         # 应用管理API (6个端点)
│   ├── admin_modules.py      # 模块配置API (6个端点)
│   ├── admin_assets.py       # 素材管理API (6个端点)
│   ├── admin_devices.py      # 设备管理API (7个端点)
│   ├── admin_push.py         # 推送管理API (7个端点)
│   └── __init__.py           # API模块导出
├── middleware/
│   └── auth.py               # JWT认证中间件
├── models_admin.py           # 数据库ORM模型
├── database_admin.py         # 异步数据库连接
├── app.py                    # Flask应用入口
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量配置模板
├── test_admin_api.py         # API测试脚本
├── API_DOCUMENTATION.md      # API文档
├── ADMIN_SYSTEM_SETUP.md     # 部署指南
├── QUICKSTART.md             # 快速开始
├── ADMIN_API_SUMMARY.md      # 项目总结
└── COMPLETION_CHECKLIST.md   # 完成清单
```

## 🛠️ 技术栈

- **框架**: Flask 2.3.0
- **ORM**: SQLAlchemy 2.0.23 (异步)
- **数据库**: PostgreSQL 12+ / MySQL 8.0+
- **认证**: JWT (PyJWT)
- **密码**: bcrypt
- **存储**: 阿里云OSS
- **异步**: async/await + asyncpg

## 📋 API端点一览

### 认证 (4个)
```
POST   /api/admin/auth/login
POST   /api/admin/auth/logout
GET    /api/admin/auth/profile
PUT    /api/admin/auth/password
```

### 应用管理 (6个)
```
GET    /api/admin/apps
POST   /api/admin/apps
GET    /api/admin/apps/:id
PUT    /api/admin/apps/:id
DELETE /api/admin/apps/:id
GET    /api/admin/apps/:id/stats
```

### 模块配置 (6个)
```
GET    /api/admin/apps/:appId/modules
POST   /api/admin/apps/:appId/modules
GET    /api/admin/apps/:appId/modules/:key
PUT    /api/admin/apps/:appId/modules/:key
DELETE /api/admin/apps/:appId/modules/:key
POST   /api/admin/apps/:appId/modules/:key/toggle
```

### 素材管理 (6个)
```
POST   /api/admin/apps/:appId/assets/upload
POST   /api/admin/apps/:appId/assets/batch-upload
GET    /api/admin/apps/:appId/assets
GET    /api/admin/apps/:appId/assets/:id
PUT    /api/admin/apps/:appId/assets/:id
DELETE /api/admin/apps/:appId/assets/:id
```

### 设备管理 (7个)
```
GET    /api/admin/apps/:appId/devices
GET    /api/admin/apps/:appId/devices/online
GET    /api/admin/apps/:appId/devices/:deviceId
DELETE /api/admin/apps/:appId/devices/:deviceId
GET    /api/admin/apps/:appId/devices/stats
POST   /api/admin/apps/:appId/devices/:deviceId/push
POST   /api/admin/apps/:appId/devices/batch-unbind
```

### 推送管理 (7个)
```
POST   /api/admin/apps/:appId/push/tasks
GET    /api/admin/apps/:appId/push/tasks
GET    /api/admin/apps/:appId/push/tasks/:id
POST   /api/admin/apps/:appId/push/tasks/:id/cancel
POST   /api/admin/apps/:appId/push/tasks/:id/retry
POST   /api/admin/apps/:appId/push/broadcast
DELETE /api/admin/apps/:appId/push/tasks/:id
```

## 🔐 安全特性

- ✅ JWT Token认证（24小时有效期）
- ✅ 密码bcrypt加密
- ✅ 角色权限控制（超级管理员/应用管理员）
- ✅ 操作日志记录
- ✅ SQL注入防护（ORM）
- ✅ XSS防护

## 📈 性能特性

- ✅ 异步数据库连接
- ✅ 连接池管理
- ✅ 分页查询
- ✅ 批量操作
- ✅ 文件流式上传

## 🧪 测试

### 运行自动化测试

```bash
python test_admin_api.py
```

### 手动API测试

```bash
# 1. 登录
TOKEN=$(curl -s -X POST http://localhost:5000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.data.token')

# 2. 获取应用列表
curl -X GET http://localhost:5000/api/admin/apps \
  -H "Authorization: Bearer $TOKEN"

# 3. 获取模块配置
curl -X GET http://localhost:5000/api/admin/apps/1/modules \
  -H "Authorization: Bearer $TOKEN"
```

## 🚀 生产部署

### 使用Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### 使用Systemd

详见 [ADMIN_SYSTEM_SETUP.md](ADMIN_SYSTEM_SETUP.md)

### Nginx配置

详见 [ADMIN_SYSTEM_SETUP.md](ADMIN_SYSTEM_SETUP.md)

## 📝 响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "错误描述"
}
```

## 🐛 常见问题

### Q: Token过期怎么办？
A: 重新登录获取新Token

### Q: 如何修改密码？
A: 使用 `PUT /api/admin/auth/password` 接口

### Q: 文件上传失败？
A: 检查文件大小（最大50MB）和OSS配置

### Q: 数据库连接失败？
A: 检查DATABASE_URL配置和数据库服务状态

更多问题请查看 [FAQ](QUICKSTART.md#常见问题)

## 📞 技术支持

- 📧 Email: support@jcoding.tech
- 📖 文档: 查看本目录下的Markdown文档
- 🐛 Issues: 在项目仓库提交Issue

## 📄 许可证

Copyright © 2026 AI活动秀项目组

---

**开发完成时间**: 2026-02-07
**版本**: v1.0.0
**状态**: ✅ 已完成，可投入使用
