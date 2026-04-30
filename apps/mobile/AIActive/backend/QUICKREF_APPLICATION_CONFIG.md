# 应用配置管理 - 快速参考

## 项目结构

```
backend/
├── api/
│   ├── __init__.py                           # API路由注册
│   ├── admin_application_config.py           # 应用配置API (新增)
│   └── ...
├── models_admin.py                           # 数据库模型 (已更新)
├── database_admin.py                         # 数据库连接
├── fastapi_app.py                            # FastAPI应用入口 (新增)
├── utils/
│   └── config_validator.py                   # 配置验证工具 (新增)
└── scripts/
    ├── create_application_config_table.py    # 创建数据库表 (新增)
    └── init_admin.py                         # 初始化管理员 (新增)
```

## 快速开始

### 1. 创建数据库表
```bash
cd backend
python scripts/create_application_config_table.py
```

### 2. 创建管理员账户
```bash
python scripts/init_admin.py
```

### 3. 启动服务
```bash
# 终端1: 启动Flask服务 (5000端口)
python app.py

# 终端2: 启动FastAPI服务 (8000端口)
python fastapi_app.py
```

### 4. 测试API
```bash
# 运行测试脚本
python test_application_config_api.py
```

## API端点速查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/application/config` | 获取配置列表 |
| GET | `/api/admin/application/config/{app_id}` | 获取单个配置 |
| POST | `/api/admin/application/config` | 创建配置 |
| PUT | `/api/admin/application/config/{app_id}` | 完整更新配置 |
| PATCH | `/api/admin/application/config/{app_id}` | 部分更新配置 ⭐ |
| DELETE | `/api/admin/application/config/{app_id}` | 删除配置 |
| GET | `/api/admin/application/config/{app_id}/schema` | 获取配置结构 |
| POST | `/api/admin/application/config/{app_id}/reset` | 重置为默认配置 |
| POST | `/api/admin/application/config/{app_id}/validate` | 验证配置 |
| GET | `/api/admin/application/config/{app_id}/history` | 获取修改历史 |

## 配置结构

```json
{
  "app": {
    "name": "AI活动秀",
    "version": "1.0.0",
    "debug": true
  },
  "features": {
    "ai_show": {
      "enabled": true,
      "invite_code_mode": true,
      "payment_mode": true,
      "employee_mode": true,
      "auto_close_time": 20
    },
    "quiz": {
      "enabled": true,
      "voice_input": false,
      "push_prize": true
    },
    "lottery": {
      "enabled": true,
      "voice_trigger": false,
      "push_winner": true
    },
    "inner_show": {
      "enabled": true,
      "digital_human_announce": true
    }
  }
}
```

## 常用命令

### 登录获取Token
```bash
curl -X POST http://localhost:8000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 获取配置
```bash
curl http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 部分更新配置 (推荐)
```bash
curl -X PATCH \
  http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "features": {
        "quiz": {
          "enabled": false
        }
      }
    }
  }'
```

### 重置配置
```bash
curl -X POST \
  http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity/reset \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 配置验证

### 验证规则
- **类型验证**: string, integer, boolean, object
- **必填验证**: app.name 必填
- **格式验证**: version 必须匹配 x.y.z
- **范围验证**: auto_close_time 必须在 5-300 之间

### 验证示例
```python
from utils.config_validator import validate_config

config = {...}  # 你的配置
is_valid, errors = validate_config(config)

if not is_valid:
    for error in errors:
        print(f"验证错误: {error}")
```

## 错误处理

### 常见错误码
- `400`: 配置验证失败
- `401`: Token无效或过期
- `403`: 权限不足
- `404`: 配置不存在

### 错误响应示例
```json
{
  "detail": {
    "message": "配置验证失败",
    "errors": [
      "字段 'features.quiz.enabled': 期望布尔类型，实际为字符串"
    ]
  }
}
```

## 数据库查询

### 直接查询配置
```python
from sqlalchemy import select
from database_admin import get_db_session
from models_admin import ApplicationConfig

async def query_config():
    db = await get_db_session()
    try:
        result = await db.execute(
            select(ApplicationConfig).where(
                ApplicationConfig.app_id == "com.jcoding.aiactivity"
            )
        )
        config = result.scalar_one_or_none()
        if config:
            print(config.config)
        return config
    finally:
        await db.close()
```

### 更新配置
```python
from sqlalchemy import update
from database_admin import get_db_session
from models_admin import ApplicationConfig

async def update_config():
    db = await get_db_session()
    try:
        await db.execute(
            update(ApplicationConfig)
            .where(ApplicationConfig.app_id == "com.jcoding.aiactivity")
            .values(config={"new": "config"})
        )
        await db.commit()
    finally:
        await db.close()
```

## 环境变量

在 `.env` 文件中配置:

```bash
# 数据库配置
DB_TYPE=mysql
DATABASE_URL_MYSQL=mysql+aiomysql://user:password@localhost:3306/database

# JWT密钥 (生产环境必须修改)
JWT_SECRET=your-secret-key

# Flask配置
FLASK_ENV=development  # or production
```

## 调试技巧

### 查看SQL日志
编辑 `database_admin.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 改为True查看SQL日志
    ...
)
```

### 查看FastAPI自动生成的文档
访问: http://localhost:8000/docs

### 查看操作日志
```python
from sqlalchemy import select, desc
from database_admin import get_db_session
from models_admin import AdminOperationLog

async def get_logs():
    db = await get_db_session()
    try:
        result = await db.execute(
            select(AdminOperationLog)
            .order_by(desc(AdminOperationLog.created_at))
            .limit(10)
        )
        logs = result.scalars().all()
        for log in logs:
            print(f"{log.operation}: {log.operation_desc}")
        return logs
    finally:
        await db.close()
```

## 开发工作流

### 1. 修改配置验证规则
编辑 `utils/config_validator.py` 中的 `CONFIG_SCHEMA`

### 2. 添加新的API端点
编辑 `api/admin_application_config.py`

### 3. 修改数据库模型
编辑 `models_admin.py`，然后运行:
```bash
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 4. 测试修改
```bash
python test_application_config_api.py
```

## 注意事项

⚠️ **重要提示:**
1. 生产环境必须修改JWT_SECRET
2. 使用HTTPS保护API
3. 定期备份数据库
4. 监控日志文件大小
5. PATCH方法比PUT方法更安全，推荐使用
6. 所有配置修改都会记录操作日志

## 文档链接

- [完整API文档](./APPLICATION_CONFIG_API.md)
- [部署指南](./DEPLOY_APPLICATION_CONFIG.md)
- [项目文档](./README_ADMIN.md)
