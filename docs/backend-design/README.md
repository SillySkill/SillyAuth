# SillyMD Backend

AI Skills 托管中心后端服务

## 技术栈

- **Python 3.11+**
- **FastAPI** - 异步 Web 框架
- **PostgreSQL 16** - 主数据库
- **Redis** - 缓存和消息队列
- **Meilisearch** - 全文搜索
- **Celery** - 异步任务
- **Kafka** - 事件流（可选）

## 快速开始

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env

# 启动数据库（使用 Docker）
docker-compose up -d postgres redis meilisearch

# 运行数据库迁移
# alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## API 文档

启动服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── api/           # API 路由
│   ├── core/          # 核心配置
│   ├── db/            # 数据库
│   ├── middleware/    # 中间件
│   ├── models/        # 数据模型
│   ├── schemas/       # Pydantic 模型
│   ├── services/      # 业务服务
│   └── tasks/         # Celery 任务
├── db/                # 数据库初始化
├── tests/             # 测试
├── requirements.txt   # 依赖
├── Dockerfile
└── docker-compose.yml
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/schemas/` 创建 Schema
2. 在 `app/services/` 创建 Service
3. 在 `app/api/v1/` 添加路由
4. 在 `app/api/v1/__init__.py` 注册路由

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 部署

### 自动部署

```bash
chmod +x deploy.sh
./deploy.sh
```

### 手动部署

1. SSH 登录服务器
2. 克隆代码仓库
3. 配置 `.env` 文件
4. 运行 `docker-compose up -d`

## 许可证

MIT
