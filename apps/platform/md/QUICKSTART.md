# 快速开始指南

## 前置要求

在开始之前，请确保已安装以下软件：

- **Python** >= 3.10
- **Node.js** >= 18.0.0 ([下载地址](https://nodejs.org/))
- **PostgreSQL** >= 14
- **Git** (可选)

## 第一步：配置数据库

### 1. 创建环境变量文件

在 `src/` 目录下创建 `.env` 文件：

```env
# 数据库配置
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=sillymd
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# JWT 密钥
JWT_SECRET=your-super-secret-key

# 应用配置
APP_ENV=development
DEBUG=true

# TOS 存储 (可选，用于文件上传)
TOS_ACCESS_KEY=your_tos_access_key
TOS_SECRET_KEY=your_tos_secret_key
TOS_ENDPOINT=tos-cn-shanghai.volces.com
TOS_BUCKET=your_bucket
TOS_CUSTOM_DOMAIN=your_custom_domain
```

### 2. 测试数据库连接

```bash
psql -h your_db_host -U your_db_user -d sillymd
```

## 第二步：安装依赖

### 后端依赖

```bash
cd src
pip install -r requirements.txt
```

### 前端依赖 (管理后台 v2)

```bash
cd admin-v2
npm install
```

## 第三步：启动服务

### 后端 API 服务

```bash
cd src
python main.py
# 或: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

> **注意**: 使用 `src/main.py` 作为入口，不再使用 `server/api/main.py`。
> 系统通过 `PluginManager.load_all_modules()` 自动发现和加载所有 22+ 模块。
> 所有 API 使用统一前缀 `/api/v1/{module}`。

### 管理后台前端 (开发模式)

```bash
cd admin-v2
npm run dev
# 访问 http://localhost:5173
```

## 第四步：访问系统

打开浏览器访问：

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health
- **管理后台 (Admin-v2)**: http://localhost:5173

## 默认账号

### 管理员账号
- **邮箱**: admin@sillymd.com
- **密码**: admin123456
- **权限**: 所有权限

### 编辑账号
- **邮箱**: editor@sillymd.com
- **密码**: editor123456
- **权限**: 内容管理权限

## API 测试

### 健康检查
```bash
curl http://localhost:8000/api/health
# {"status": "healthy", "database": "connected", "version": "2.0.0"}
```

### 获取模块列表
```bash
curl http://localhost:8000/api/v1/debug/routes
```

### 认证测试
```bash
# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sillymd.com","password":"admin123456"}'

# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"new@example.com","password":"Test123456"}'
```

### Skills 列表
```bash
curl "http://localhost:8000/api/v1/skills?limit=10"
```

## 常见问题

### Q1: 启动后提示 `ModuleNotFoundError`？
**A**: 确保已安装所有依赖：`cd src && pip install -r requirements.txt`

### Q2: 数据库连接失败？
**A**:
1. 检查 `src/.env` 中的数据库配置是否正确
2. 确认 PostgreSQL 服务是否在运行
3. 测试连接：`psql -h <host> -U <user> -d <database>`

### Q3: 误启动了旧入口 `server/api/main.py`？
**A**: 停止服务，改用 `src/main.py` 启动。`server/api/` 已废弃。

### Q4: 前端无法连接后端？
**A**:
1. 确认后端服务已从 `src/main.py` 正常启动
2. 检查端口是否正确（默认 8000）
3. 查看 `admin-v2/` 中的 Vite 代理配置

### Q5: 端口被占用？
**A**: 使用 `--port` 参数修改端口：
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Q6: 文件上传失败？
**A**: 检查 TOS 存储环境变量是否配置正确：
```bash
echo $TOS_ACCESS_KEY
echo $TOS_ENDPOINT
```

## 开发模式 vs 生产模式

### 开发模式
```bash
cd src
python main.py
# 或
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
- 支持热重载 (`--reload`)
- 详细错误日志
- 开发环境配置

### 生产模式
```bash
cd src
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# 使用 PM2
pm2 start "uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4" --name sillymd-api
```

## 下一步

- 阅读 [API 文档](./docs/API_DOCUMENTATION.md) 了解完整 API 接口
- 查看 [部署指南](./QUICK_DEPLOY.md) 了解生产部署
- 浏览 [README](./README.md) 了解项目架构

## 获取帮助

如遇到问题：
1. 查看控制台错误信息
2. 检查 `src/.env` 配置
3. 查阅相关文档
4. 提交 Issue

---

**最后更新**: 2026-04-30
