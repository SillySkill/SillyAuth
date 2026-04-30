# SillyMD - AI Skills 内容管理与交易平台

> 基于 FastAPI + PostgreSQL + TOS 的模块化 API 平台，支持 AI Skills 内容管理、支付交易、创作者生态和用户社区。

## 技术架构

- **后端**: Python 3.10+ / FastAPI / psycopg2 / PluginManager 模块化架构
- **数据库**: PostgreSQL 16 (RealDictCursor, `%s` 参数化)
- **存储**: 火山引擎 TOS (Volcengine Object Storage)
- **管理后台**: React 18 + TypeScript + Ant Design 5 + Vite (admin-v2/)
- **认证**: JWT HS256

## 项目结构

```
md/
├── src/
│   ├── main.py                    # 应用入口 (uvicorn src.main:app)
│   ├── core/
│   │   ├── db_adapter.py          # 统一数据库适配层
│   │   └── plugin_manager.py      # 模块管理器
│   └── modules/                   # 31 功能模块
│       ├── auth/                  # 认证授权
│       ├── admin/                 # 管理后台 API
│       ├── cms/                   # 内容管理
│       ├── payment/               # 支付系统
│       ├── points/                # 积分商城
│       ├── tasks/                 # 任务与签到
│       ├── downloads/             # 下载资源
│       ├── messages/              # 消息通知
│       ├── tutorials/             # 教程管理
│       ├── dashboard/             # 仪表盘
│       ├── analytics/             # 数据分析
│       ├── config_sync/           # 配置同步
│       ├── config_data/           # 配置数据 CRUD
│       ├── store/                 # 电商商城
│       ├── goods/                 # 商品管理
│       ├── marketplace/           # 交易市场
│       ├── transaction/           # 交易订单
│       ├── promotion/             # 促销管理
│       ├── logistics/             # 物流追踪
│       ├── storage/               # TOS 文件存储
│       ├── skills/                # Skills 管理
│       ├── vendor/                # 供应商管理
│       ├── affiliate/             # 联属营销
│       ├── staff/                 # 员工 RBAC 管理
│       ├── arena/                 # 竞技场 PK
│       ├── recommendations/       # Skills 推荐
│       ├── notifications/         # 通知推送
│       ├── i18n/                  # 国际化
│       ├── sillyclaw/             # SillyClaw 版本管理
│       ├── search/                # 搜索服务
│       └── scheduler/             # 定时任务
├── admin-v2/                      # 管理后台前端
├── server/
│   ├── api/                       # 旧 API (已弃用，保留 .backup)
│   ├── migrations/                # 数据库迁移
│   └── scripts/                   # 数据脚本
├── seeds/                         # 种子数据
└── docs/                          # 项目文档
```

## 快速开始

### 1. 环境准备
```bash
# 设置环境变量
export DB_HOST=your_host
export DB_PORT=5432
export DB_NAME=sillymd
export DB_USER=your_user
export DB_PASSWORD=your_password
export JWT_SECRET=your_secret

# TOS 存储 (可选)
export TOS_ACCESS_KEY=your_key
export TOS_SECRET_KEY=your_secret
export TOS_ENDPOINT=tos-cn-shanghai.volces.com
export TOS_BUCKET=your_bucket
export TOS_CUSTOM_DOMAIN=your_domain
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动 API 服务
```bash
cd src
python main.py
# 或: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 启动管理后台 (开发模式)
```bash
cd admin-v2
npm install
npm run dev
# 访问 http://localhost:5173
```

### 5. 健康检查
```bash
curl http://localhost:8000/api/health
# {"status": "healthy", "database": "connected", "version": "2.0.0"}
```

## API 概览

| 模块 | 前缀 | 主要功能 |
|------|------|---------|
| auth | `/api/v1/auth` | 登录、注册、Token 刷新 |
| admin | `/api/v1/admin` | 用户管理、模块管理、审计日志 |
| cms | `/api/v1/cms` | 文章、分类、导航、SEO |
| payment | `/api/v1/payment` | 支付、订单、创作者收益结算 |
| points | `/api/v1/points` | 积分、商城、购物车、兑换 |
| tasks | `/api/v1/tasks` | 每日任务、签到、成就系统 |
| downloads | `/api/v1/downloads` | 下载资源管理 |
| messages | `/api/v1/messages` | 消息、会话、通知 |
| tutorials | `/api/v1/tutorials` | 教程内容管理 |
| dashboard | `/api/v1/dashboard` | 数据仪表盘 |
| analytics | `/api/v1/analytics` | 用户行为分析 |
| config_sync | `/api/v1/config` | 配置版本管理与同步 |
| store | `/api/v1/store` | 电商商城 |
| storage | `/api/v1/storage` | TOS 文件上传下载 |
| i18n | `/api/v1/i18n` | 多语言翻译管理 |
| skills | `/api/v1/skills` | Skills 管理 |
| vendor | `/api/v1/vendor` | 供应商管理 |
| affiliate | `/api/v1/affiliate` | 联属营销 |
| sillyclaw | `/api/v1/sillyclaw` | SillyClaw 升级管理 |
| arena | `/api/v1/arena` | 竞技场 PK 房间、对战、排行榜 |
| recommendations | (挂载决定) | Skills 推荐、热门、最新、下载 |
| goods | `/api/v1/goods` | 商品 CRUD、分类管理 |
| marketplace | `/api/v1/marketplace` | 交易市场挂牌、购买、评价 |
| promotion | `/api/v1/promotions` | 促销活动、优惠券、闪购 |
| staff | `/api/v1/staff` | 员工 RBAC 管理 (用户/角色/权限) |
| transaction | `/api/v1/transaction` + `/api/v1/admin/orders` | 订单、结算、退款 |
| logistics | `/api/v1/logistics` | 快递公司、运费模板、物流追踪 |
| config_data | `/api/v1/config-data` | 结构化配置数据 CRUD |

### 文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| 完整 API 文档 | [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | 所有端点详细说明和请求/响应示例 |
| API 端点清单 | [docs/API_ENDPOINT_CHECKLIST.md](docs/API_ENDPOINT_CHECKLIST.md) | 每个接口的功能、参数、认证、用法一览 |
| v1→v2 迁移指南 | [docs/API_MIGRATION_GUIDE.md](docs/API_MIGRATION_GUIDE.md) | 旧 API 路径 → 新 API 路径对照，供客户端迁移参考 |
| 快速开始 | [QUICKSTART.md](QUICKSTART.md) | 5 分钟快速启动指南 |
| 部署指南 | [QUICK_DEPLOY.md](QUICK_DEPLOY.md) | 生产环境部署 (PM2/Nginx/Docker) |

## 开发指南

### 添加新模块
每个模块遵循统一结构:

```
src/modules/new_module/
├── config.yaml        # 模块元数据
├── __init__.py         # BaseModule 类定义
├── schemas.py          # Pydantic v2 数据模型
├── services.py         # 业务逻辑 (使用 get_db_cursor)
└── routes.py           # API 路由 (prefix=/api/v1/new_module)
```

模块通过 PluginManager 自动发现和加载，无需手动注册。

### 代码规范
- 数据库: `from src.core.db_adapter import get_db_cursor`，使用 `%s` 占位符
- Pydantic: `model_config = {"from_attributes": True}`
- 路由: 统一前缀 `/api/v1/{module}`

## 部署
详见 [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

## 许可证
MIT License
