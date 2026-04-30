# SillyMD 模块化架构

> 可插拔式 MVC 模块化架构

## 项目结构

```
src/
├── core/                      # 核心框架
│   ├── module.py             # 模块基类
│   ├── registry.py           # 模块注册器
│   ├── plugin_manager.py     # 插件管理器
│   ├── config_loader.py      # 配置加载器
│   ├── database.py           # 数据库连接
│   └── events.py             # 事件总线
│
├── modules/                   # 可插拔模块
│   ├── auth/                 # 认证模块
│   ├── skills/               # Skills 平台
│   ├── sillyclaw/            # SillyClaw 版本管理
│   ├── payment/              # 支付模块
│   ├── transaction/          # 交易系统
│   ├── vendor/              # 开发者入驻
│   ├── points/              # 积分商城
│   ├── tasks/               # 任务系统
│   ├── messages/            # 消息系统
│   ├── cms/                 # CMS 内容管理
│   ├── downloads/           # 下载区
│   ├── arena/              # 虾拳馆 PK
│   ├── goods/               # 商品系统
│   ├── marketplace/         # 傻福虾盘
│   ├── storage/             # TOS 对象存储
│   └── admin/               # 管理后台
│
├── config.yaml              # 全局配置
├── main.py                  # 应用入口
└── requirements.txt         # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export DB_HOST=43.134.163.12
export DB_PORT=5432
export DB_NAME=sillymd
export DB_USER=sillyAdmin
export DB_PASSWORD=silly2026@

export TOS_ACCESS_KEY=your_access_key
export TOS_SECRET_KEY=your_secret_key

export JWT_SECRET=your-jwt-secret-key
```

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 模块开发

### 创建新模块

1. 在 `modules/` 下创建模块目录
2. 创建 `__init__.py` - 模块入口
3. 创建 `routes.py` - 路由定义
4. 创建 `services.py` - 业务逻辑
5. 创建 `schemas.py` - Pydantic 模型
6. 创建 `config.yaml` - 模块配置

### 模块结构

```python
# __init__.py
from core import BaseModule, ModuleInfo

class MyModule(BaseModule):
    info = ModuleInfo(
        id="mymodule",
        name="我的模块",
        version="1.0.0",
        description="模块描述",
        author="SillyMD",
        dependencies=[],
    )

    def install(self, app: FastAPI):
        # 注册路由
        app.include_router(self.router)

    def on_startup(self):
        # 启动时初始化
        pass

    def on_shutdown(self):
        # 关闭时清理
        pass
```

## API 文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 模块管理 API

```bash
# 列出所有模块
GET /api/modules

# 启用模块
POST /api/modules/{module_id}/enable

# 禁用模块
POST /api/modules/{module_id}/disable

# 健康检查
GET /api/health
```

## 许可证

MIT License
