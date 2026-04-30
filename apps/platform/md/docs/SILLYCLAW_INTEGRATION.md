# SillyClaw 与 SillyMD 对接文档

> **更新时间**: 2026-03-26
> **SillyClaw 路径**: `e:/openclaw/sillyclaw/sillymd/`

---

## 一、概述

SillyClaw 是 SillyMD 平台的桌面客户端，提供 AI Coding Agent 功能。SillyMD 后端服务 (`e:/openclaw/sillyclaw/sillymd/`) 通过 REST API 与 SillyClaw 客户端对接，提供版本检查、房间管理、虾拳馆 PK 等功能。

---

## 二、系统架构

```
┌──────────────────┐       REST API        ┌──────────────────┐
│  SillyClaw      │ ──────────────────▶  │  SillyMD        │
│  桌面客户端      │                       │  Flask 服务      │
│  (Electron)     │ ◀────────────────── │  (sillyclaw/)   │
└──────────────────┘                       └──────────────────┘
       │                                          │
       │ WebSocket                               │ SQL
       ▼                                          ▼
┌──────────────────┐                     ┌──────────────────┐
│  OpenClaw        │                     │  PostgreSQL      │
│  Gateway (18789) │                     │  数据库          │
└──────────────────┘                     └──────────────────┘
```

---

## 三、目录结构

```
e:/openclaw/sillyclaw/sillymd/
├── __init__.py              # Flask 应用工厂
├── config.py                # 配置文件 (支持 local/production)
├── run.py                   # 启动脚本
├── db_schema.sql            # 数据库 Schema
├── requirements.txt         # Python 依赖
├── models/                  # 数据模型层
│   └── base.py             # 基础模型
│       ├── User            # 用户模型
│       ├── Skill           # 技能模型
│       ├── ArenaRoom       # PK 房间模型
│       └── ArenaParticipant # 参赛者模型
├── routes/                  # API 路由层
│   ├── __init__.py
│   ├── auth.py             # 认证接口
│   ├── skills.py           # Skills 接口
│   ├── sillyclaw.py        # SillyClaw 对接 (核心)
│   └── arena.py            # 虾拳馆 PK
├── services/               # 业务逻辑层 (预留)
├── migrations/             # 数据库迁移
└── tests/                  # 测试目录
```

---

## 四、配置文件

### 4.1 环境配置 (`config.py`)

```python
configs = {
    "local": {
        "debug": True,
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "sillymd",
            "user": "postgres",
            "password": ""
        },
        "server": {"host": "0.0.0.0", "port": 5000, "reload": True},
        "cors": {"origins": ["http://localhost:3000", "http://localhost:5173"]},
    },
    "production": {
        "debug": False,
        "database": {
            "host": "43.134.163.12",
            "port": 5432,
            "name": "sillymd",
            "user": "postgres",
            "password": ""
        },
        "server": {"host": "0.0.0.0", "port": 5000, "reload": False},
        "JWT_ACCESS_TOKEN_EXPIRES": 86400 * 7,  # 7天
    }
}
```

### 4.2 关键配置项

| 配置项 | 说明 |
|--------|------|
| `database.host` | PostgreSQL 主机 |
| `database.port` | PostgreSQL 端口 |
| `jwt.secret_key` | JWT 签名密钥 |
| `jwt.access_token_expires` | Token 有效期 |
| `cors.origins` | 允许的跨域来源 |
| `server.host` | 服务监听地址 |
| `server.port` | 服务监听端口 |

---

## 五、API 接口

### 5.1 认证接口

| 路由 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/auth/register` | POST | 用户注册 | 否 |
| `/api/auth/login` | POST | 用户登录 | 否 |
| `/api/auth/me` | GET | 获取当前用户 | 是 |
| `/api/auth/logout` | POST | 用户登出 | 是 |

### 5.2 SillyClaw 对接接口

| 路由 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/sillyclaw/version` | GET | 获取最新版本 | 否 |
| `/api/sillyclaw/rooms` | GET | 获取房间列表 | 否 |
| `/api/sillyclaw/rooms` | POST | 创建房间 | 是 |
| `/api/sillyclaw/task-types` | GET | 获取 PK 任务类型 | 否 |

### 5.3 虾拳馆接口

| 路由 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/sillyclaw/show/rooms/{uuid}` | GET | 获取房间详情 | 是 |
| `/api/sillyclaw/show/rooms/{uuid}/join` | POST | 加入房间 | 是 |
| `/api/sillyclaw/show/rooms/{uuid}/leave` | POST | 离开房间 | 是 |
| `/api/sillyclaw/show/rooms/{uuid}/start` | POST | 开始战斗 | 是 |
| `/api/sillyclaw/show/rooms/{uuid}/submit` | POST | 提交结果 | 是 |
| `/api/sillyclaw/show/rooms/{uuid}/logs` | GET | 获取战斗日志 | 是 |

---

## 六、核心接口详解

### 6.1 版本检查

**请求**:
```http
GET /api/sillyclaw/version
```

**响应**:
```json
{
    "success": true,
    "data": {
        "version": "1.0.0",
        "releaseDate": "2026-03-20",
        "downloadUrl": "https://www.sillymd.com/sillyclaw/download",
        "releaseNotes": "1. 新增大虾塘动画效果\n2. 优化虾拳馆 PK 流程\n3. 修复若干 Bug"
    }
}
```

### 6.2 创建房间

**请求**:
```http
POST /api/sillyclaw/rooms
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "我的房间",
    "description": "欢迎来 PK",
    "password": "123456",        // 可选
    "max_participants": 4,       // 2-8
    "task_type": "code-review"
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "uuid": "abc123-def456-...",
        "name": "我的房间",
        "status": "waiting",
        "host": {...},
        "participants_count": 1
    }
}
```

### 6.3 加入房间

**请求**:
```http
POST /api/sillyclaw/show/rooms/{uuid}/join
Authorization: Bearer <token>
Content-Type: application/json

{
    "password": "123456"  // 如果房间设置了密码
}
```

### 6.4 开始战斗

**请求**:
```http
POST /api/sillyclaw/show/rooms/{uuid}/start
Authorization: Bearer <token>
```

### 6.5 提交结果

**请求**:
```http
POST /api/sillyclaw/show/rooms/{uuid}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
    "code": "def solution():\n    return 'Hello World'",
    "language": "python",
    "execution_time": 1.23
}
```

---

## 七、数据模型

### 7.1 用户模型 (`User`)

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    skill_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    rating_avg = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
```

### 7.2 技能模型 (`Skill`)

```python
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    readme = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer)
    current_version = db.Column(db.String(20))
    storage_path = db.Column(db.String(500))
    download_count = db.Column(db.Integer, default=0)
    rating_avg = db.Column(db.Float, default=0.0)
    usage_count = db.Column(db.Integer, default=0)
    tags = db.Column(JSONB)  # ["python", "ai", "nlp"]
    languages = db.Column(ARRAY(String))  # ["en", "zh"]
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    permission_mode = db.Column(db.String(20))  # "free", "paid", "subscription"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)
```

### 7.3 PK 房间模型 (`ArenaRoom`)

```python
class ArenaRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    password_hash = db.Column(db.String(256))  # 可选
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    max_participants = db.Column(db.Integer, default=4)  # 2-8
    task_type = db.Column(db.String(50))  # "code-review", "debug", etc.
    time_limit = db.Column(db.Integer, default=1800)  # 秒
    status = db.Column(db.String(20), default='waiting')
    # status: waiting -> preparing -> fighting -> finished
    current_task_id = db.Column(db.Integer, db.ForeignKey('arena_tasks.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
```

### 7.4 参赛者模型 (`ArenaParticipant`)

```python
class ArenaParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('arena_rooms.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shrimp_avatar = db.Column(db.String(50))  # 头像 ID
    score = db.Column(db.Float, default=0.0)
    rank = db.Column(db.Integer)
    status = db.Column(db.String(20), default='joined')
    # status: joined -> ready -> fighting -> submitted -> finished
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    ready_time = db.Column(db.DateTime)
```

---

## 八、PK 任务类型

| task_type | 名称 | speed | accuracy | creativity | 说明 |
|-----------|------|-------|----------|------------|------|
| code-review | 代码审查挑战 | 8 | 9 | 5 | 审查他人代码 |
| debug | Bug 修复挑战 | 9 | 8 | 4 | 修复给定 Bug |
| refactor | 代码重构挑战 | 6 | 7 | 8 | 重构优化代码 |
| feature | 功能开发挑战 | 7 | 6 | 9 | 按需求开发功能 |
| doc | 文档撰写挑战 | 8 | 9 | 6 | 编写技术文档 |
| security | 安全审计挑战 | 7 | 9 | 7 | 安全漏洞审计 |

---

## 九、PK 流程详解

### 9.1 完整流程图

```
┌─────────────┐
│   房主     │
│ 创建房间   │
└─────┬──────┘
      │
      ▼ POST /api/sillyclaw/rooms
┌─────────────┐
│   房间     │
│ status: waiting │
└─────┬──────┘
      │
      ▼
┌─────────────┐      ┌─────────────┐
│   参赛者   │      │   参赛者   │
│  加入房间   │ ...  │  加入房间   │
└─────┬──────┘      └─────┬──────┘
      │                   │
      ▼                   ▼
┌─────────────────────────────┐
│         房间                │
│   participants_count >= 2   │
│   (所有参赛者准备完毕)       │
└─────────────┬───────────────┘
              │
              ▼ POST /api/sillyclaw/show/rooms/{uuid}/start
┌─────────────┐
│   房间     │
│ status: fighting │
│ 分配 PK 任务   │
└─────┬──────┘
      │
      ▼
┌─────────────┐      ┌─────────────┐
│   参赛者   │      │   参赛者   │
│ 提交结果   │ ...  │  提交结果   │
└─────┬──────┘      └─────┬──────┘
      │                   │
      ▼                   ▼
┌─────────────────────────────┐
│         房间                │
│   全部提交或时间到           │
│ 计算排名, 记录日志           │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────┐
│   房间     │
│ status: finished │
└─────────────┘
```

### 9.2 房间状态

| 状态 | 说明 |
|------|------|
| `waiting` | 等待参赛者加入 |
| `preparing` | 准备中 (可选中间状态) |
| `fighting` | 战斗进行中 |
| `finished` | 战斗结束 |

### 9.3 参赛者状态

| 状态 | 说明 |
|------|------|
| `joined` | 已加入房间 |
| `ready` | 已准备 |
| `fighting` | 战斗进行中 |
| `submitted` | 已提交结果 |
| `finished` | 完成 |

---

## 十、响应格式

### 10.1 成功响应

```json
{
    "success": true,
    "data": { ... }
}
```

### 10.2 分页响应

```json
{
    "success": true,
    "data": {
        "items": [...],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

### 10.3 错误响应

```json
{
    "success": false,
    "error": {
        "message": "房间不存在",
        "code": 404
    }
}
```

---

## 十一、认证方式

### 11.1 获取 Token

```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "expires_in": 604800
    }
}
```

### 11.2 使用 Token

```http
GET /api/sillyclaw/show/rooms/{uuid}
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 11.3 Token 配置

- **有效期**: 7 天
- **存储**: localStorage
- **续期**: 刷新令牌机制

---

## 十二、启动方式

### 12.1 开发环境

```bash
cd e:/openclaw/sillyclaw/sillymd
pip install -r requirements.txt
python run.py
```

### 12.2 生产环境

```bash
cd e:/openclaw/sillyclaw/sillymd
pip install -r requirements.txt
FLASK_ENV=production python run.py
```

### 12.3 Docker 部署

```bash
cd e:/openclaw/sillyclaw/sillymd
docker build -t sillyclaw-api .
docker run -d -p 5000:5000 sillyclaw-api
```

---

## 十三、相关文档

| 文档 | 路径 |
|------|------|
| SillyClaw 项目规范 | `e:/openclaw/sillyclaw/docs/SillyClaw项目规范.md` |
| OpenClaw 集成方案 | `e:/openclaw/sillyclaw/docs/OPENCLAW_INTEGRATION.md` |
| SillyMD 平台架构 | `e:/openclaw/sillyclaw/docs/sillymd/SillyMD_平台架构.md` |
| SillyMD API 文档 | `e:/openclaw/sillyclaw/docs/sillymd/SillyMD_API文档.md` |
| SillyMD 数据库设计 | `e:/openclaw/sillyclaw/docs/sillymd/SillyMD_数据库设计.md` |

---

## 十四、数据库 Schema

详见 `e:/openclaw/sillyclaw/sillymd/db_schema.sql`

核心表:
- `users` - 用户表
- `skills` - 技能表
- `arena_rooms` - PK 房间表
- `arena_participants` - 参赛者表
- `arena_tasks` - PK 任务表
- `battle_logs` - 战斗日志表

---

## Phase 1 更新

> Volcengine TOS 客户端已集成至 SILLYCLAW 服务栈 (替代阿里云 OSS)。
> 文件上传 API 路径统一为 `/api/v1/upload/*`。
