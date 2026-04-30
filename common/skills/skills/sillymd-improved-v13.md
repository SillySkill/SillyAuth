# SillyMD Skills 在线平台 - 改进设计文档 v13.0

> **平台愿景**：打造专业的 AI Skills 托管与协作平台，支持 Skills 资产化管理、多领域团队协作、商用授权交易。

> **v13.0 改进要点**：
> - 优化数据库设计，消除冗余
> - 添加完整的 API 设计规范
> - 增强缓存策略
> - 完善监控与可观测性
> - 强化授权验证机制

---

## 目录

1. [平台概述](#一平台概述)
2. [技术架构](#二技术架构)
3. [API 设计规范](#三api-设计规范)
4. [数据库设计（已优化）](#四数据库设计已优化)
5. [缓存架构](#五缓存架构)
6. [核心功能模块](#六核心功能模块)
7. [授权验证系统](#七授权验证系统)
8. [监控与可观测性](#八监控与可观测性)
9. [安全设计](#九安全设计)
10. [部署与运维](#十部署与运维)
11. [开发路线图](#十一开发路线图)

---

## 一、平台概述

### 1.1 基本信息

| 项目 | 内容 |
|------|------|
| 网站域名 | sillymd.com（已完成备案） |
| 团队协作域名 | sillymd.com/组织名 |
| 服务器地址 | 47.96.133.238 |
| 平台定位 | AI Skills 托管中心 + 多领域协作网络 + 商用授权市场 |

### 1.2 核心定义

**Skills 是什么？**

> Skills 是智能体与大模型交互的标准化说明文档，按需加载，降低 AI 管理成本。

### 1.3 Skills 分类体系

```
按收费分类:
├── 免费 Skills (Free) - 开源共享
└── 商用 Skills (Commercial) - 付费授权

按领域分类:
├── 技术 Skills (Tech) - 代码、架构、工具
├── 产品 Skills (Product) - 需求、规划、研究
├── 设计 Skills (Design) - UI/UX、视觉、品牌
├── 市场 Skills (Marketing) - 推广、策略、分析
└── 运营 Skills (Ops) - 流程、增长、数据
```

---

## 二、技术架构

### 2.1 技术栈（已优化）

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | React 18 + TypeScript + Zustand + Vite 5.x | 单页应用，轻量状态管理 |
| UI | TailwindCSS + shadcn/ui | 可定制组件库 |
| 后端 | Python 3.11+ + FastAPI | 异步 RESTful API |
| 数据库 | PostgreSQL 15+ | 关系型数据 + JSON 支持 |
| 缓存 | Redis 7.0 (集群模式) | 会话、队列、热点数据 |
| 消息队列 | Celery + Redis | 异步任务处理 |
| 搜索 | Meilisearch | 全文搜索引擎 |
| 存储 | 阿里云 OSS (版本控制) | Skills 文件存储 |
| CDN | 阿里云 CDN / CloudFlare | 静态资源加速 |
| 监控 | Prometheus + Grafana + Sentry | 指标、日志、错误追踪 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                  │
│   Web端 │ 管理后台 │ API文档 │ SDK工具 │ MCP Server             │
├─────────────────────────────────────────────────────────────────┤
│                         接入层                                  │
│          CDN + 负载均衡 + API Gateway (Kong/APISIX)             │
│                  (认证 + 限流 + 日志 + 签名验证)                 │
├─────────────────────────────────────────────────────────────────┤
│                       业务逻辑层 (FastAPI)                       │
│  用户服务 │ Skills服务 │ 审核服务 │ 交易服务 │ 团队服务           │
│  积分服务 │ 授权服务 │ 钱包服务 │ 推荐服务 │ 消息服务             │
├─────────────────────────────────────────────────────────────────┤
│                    基础设施层                                   │
│  PostgreSQL │ Redis │ Meilisearch │ OSS │ Celery                │
├─────────────────────────────────────────────────────────────────┤
│                    监控与运维层                                 │
│  Prometheus │ Grafana │ Sentry │ ELK │ OpenTelemetry            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、API 设计规范

### 3.1 RESTful 规范

#### 3.1.1 URL 设计

```
# 资源命名（复数形式）
GET    /api/v1/skills           # 获取 Skills 列表
GET    /api/v1/skills/{id}      # 获取单个 Skill
POST   /api/v1/skills           # 创建 Skill
PUT    /api/v1/skills/{id}      # 更新 Skill
DELETE /api/v1/skills/{id}      # 删除 Skill

# 子资源
GET    /api/v1/skills/{id}/versions      # 获取版本列表
GET    /api/v1/skills/{id}/comments      # 获取评论
POST   /api/v1/skills/{id}/favorite      # 收藏

# 过滤和搜索
GET    /api/v1/skills?category=tech&type=free&sort=hot
GET    /api/v1/skills/search?q=python&page=1&page_size=20
```

#### 3.1.2 统一分页规范

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 3.1.3 统一响应格式

```json
// 成功响应
{
  "code": 0,
  "message": "success",
  "data": {...},
  "request_id": "req_abc123"
}

// 错误响应
{
  "code": 10001,
  "message": "Skill not found",
  "errors": [
    {"field": "skill_id", "message": "Invalid skill_id format"}
  ],
  "request_id": "req_abc123"
}
```

#### 3.1.4 错误码规范

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 0 | 成功 | 200 |
| 10001 | 资源不存在 | 404 |
| 10002 | 参数错误 | 400 |
| 10003 | 未授权 | 401 |
| 10004 | 权限不足 | 403 |
| 10005 | 资源冲突 | 409 |
| 10006 | 请求过于频繁 | 429 |
| 10007 | 服务器错误 | 500 |
| 20001 | 积分不足 | 400 |
| 20002 | 授权无效 | 403 |
| 20003 | 授权已过期 | 403 |

### 3.2 API 限流策略

| 用户类型 | 限制 | 时间窗口 |
|----------|------|----------|
| 访客 | 60 次 | 1 分钟 |
| 普通用户 | 120 次 | 1 分钟 |
| 付费用户 | 300 次 | 1 分钟 |
| 企业用户 | 1000 次 | 1 分钟 |

---

## 四、数据库设计（已优化）

### 4.1 核心表结构（优化版）

#### 4.1.1 优化要点
- 移除 `skill_id` 冗余字段，统一使用自增 `id`
- 添加 `version` 字段支持乐观锁
- 添加复合索引优化查询
- 添加 `created_at` 和 `updated_at` 索引

```sql
-- ============================================
-- 用户表（优化版）
-- ============================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'vendor', 'admin')),
    vendor_level VARCHAR(20) DEFAULT 'normal' CHECK (vendor_level IN ('normal', 'premium', 'gold')),
    ai_points INT DEFAULT 0,
    avatar_url VARCHAR(500),
    bio TEXT,
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引优化
    CONSTRAINT chk_ai_points CHECK (ai_points >= 0)
);

CREATE INDEX idx_users_role ON users(role) WHERE is_active = TRUE;
CREATE INDEX idx_users_vendor_level ON users(vendor_level) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- ============================================
-- Skills 表（优化版 - 移除冗余 skill_id）
-- ============================================
CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,

    -- 基础信息
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,  -- URL 友好标识
    description TEXT,
    author_id BIGINT NOT NULL,

    -- 分类
    category VARCHAR(20) NOT NULL CHECK (category IN ('tech', 'product', 'design', 'marketing', 'ops')),
    type VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (type IN ('free', 'commercial')),
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'reviewing', 'approved', 'rejected')),

    -- 乐观锁版本
    lock_version INT DEFAULT 0,

    -- 标志位
    is_deleted BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,

    -- 关联
    repo_url VARCHAR(500),
    dependencies JSONB,

    -- 商用字段
    price INT DEFAULT 0,
    license_types JSONB,
    original_price INT DEFAULT 0,
    promo_until TIMESTAMP WITH TIME ZONE,

    -- 统计字段（定期更新，避免频繁写入）
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    favorite_count INT DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_price CHECK (price >= 0),
    CONSTRAINT chk_rating_avg CHECK (rating_avg >= 0 AND rating_avg <= 5)
);

-- 复合索引优化
CREATE INDEX idx_skills_category_type ON skills(category, type) WHERE is_deleted = FALSE AND status = 'approved';
CREATE INDEX idx_skills_author_status ON skills(author_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_skills_featured ON skills(is_featured, published_at DESC) WHERE is_featured = TRUE AND is_deleted = FALSE;
CREATE INDEX idx_skills_search ON skills USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, ''))) WHERE is_deleted = FALSE;
CREATE INDEX idx_skills_created_at ON skills(created_at DESC) WHERE is_deleted = FALSE;

-- ============================================
-- Skills 版本表（新增乐观锁）
-- ============================================
CREATE TABLE skill_versions (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    version VARCHAR(20) NOT NULL,
    content LONGTEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    commit_message VARCHAR(500),
    author_id BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id),
    UNIQUE (skill_id, version)
);

CREATE INDEX idx_skill_versions_skill_id ON skill_versions(skill_id, created_at DESC);

-- ============================================
-- 团队表
-- ============================================
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id BIGINT NOT NULL,
    description TEXT,
    avatar_url VARCHAR(500),
    member_count INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- ============================================
-- 授权记录表（优化版）
-- ============================================
CREATE TABLE licenses (
    id BIGSERIAL PRIMARY KEY,
    license_key VARCHAR(100) UNIQUE NOT NULL,
    skill_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    license_type VARCHAR(20) NOT NULL CHECK (license_type IN ('personal', 'team', 'enterprise')),
    price INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_verified_at TIMESTAMP WITH TIME ZONE,  -- 心跳验证时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE RESTRICT,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (vendor_id) REFERENCES users(id)
);

CREATE INDEX idx_licenses_license_key ON licenses(license_key) WHERE is_active = TRUE;
CREATE INDEX idx_licenses_buyer_skill ON licenses(buyer_id, skill_id) WHERE is_active = TRUE;
CREATE INDEX idx_licenses_expires_at ON licenses(expires_at) WHERE is_active = TRUE;

-- ============================================
-- 操作日志表（审计）
-- ============================================
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id, created_at DESC);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- 分区策略（按月分区）
CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

---

## 五、缓存架构

### 5.1 缓存层级

```
┌─────────────────────────────────────────────────────────────┐
│                     缓存架构                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  L1 - 浏览器缓存                                             │
│  └── 静态资源、Skills 内容（Cache-Control: max-age=3600）   │
│                                                             │
│  L2 - CDN 缓存                                               │
│  └── 静态文件、Skills 下载（CDN 缓存）                       │
│                                                             │
│  L3 - 应用缓存 (Redis)                                       │
│  ├── 热点数据（用户信息、热门 Skills）                       │
│  ├── 会话缓存（JWT Token 黑名单）                            │
│  ├── 搜索结果缓存（5 分钟）                                  │
│  └── 计数器（浏览量、下载量）                                │
│                                                             │
│  L4 - 数据库查询缓存                                         │
│  └── PostgreSQL 查询计划缓存                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Redis 缓存策略

| 数据类型 | Key 格式 | TTL | 淘汰策略 |
|----------|----------|-----|----------|
| 用户信息 | `user:{id}` | 1h | LRU |
| 用户会话 | `session:{token}` | 24h | LRU |
| Skill 详情 | `skill:{id}` | 30m | LRU |
| Skills 列表 | `skills:list:{hash}` | 5m | LRU |
| 搜索结果 | `search:{hash}` | 5m | LRU |
| 排行榜 | `ranking:{type}:{date}` | 1h | 过期删除 |
| 计数器 | `counter:{type}:{id}` | - | 持久化 |

### 5.3 缓存更新策略

```python
# Cache-Aside 模式
async def get_skill(skill_id: int):
    # 1. 先查缓存
    cache_key = f"skill:{skill_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 缓存未命中，查数据库
    skill = await db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        return None

    # 3. 写入缓存
    await redis.setex(cache_key, 1800, json.dumps(skill))
    return skill

async def update_skill(skill_id: int, data: dict):
    # 1. 更新数据库
    await db.query(Skill).filter(Skill.id == skill_id).update(data)

    # 2. 删除缓存（避免脏数据）
    await redis.delete(f"skill:{skill_id}")
    await redis.delete("skills:list:*")  # 删除列表缓存
```

---

## 六、核心功能模块

### 6.1 Skills 托管

#### 6.1.1 免费 Skills
| 特性 | 说明 |
|------|------|
| 内容类型 | AI 使用技巧、最佳实践、开源工具 |
| 访问权限 | 公开，所有用户可查看下载 |
| 许可证 | MIT / Apache 2.0 / CC BY |

#### 6.1.2 商用 Skills
| 特性 | 说明 |
|------|------|
| 内容类型 | 行业解决方案、企业级应用 |
| 访问权限 | 需购买授权 |
| 授权类型 | 个人 (1x) / 团队 (3x) / 企业 (10x) |

### 6.2 版本管理

```yaml
# SemVer 版本约束
dependencies:
  - skill_id: "tech-database-base"
    version: ">=1.2.0"   # 最低版本
    type: "required"
  - skill_id: "tech-cache"
    version: "^2.0.0"    # 兼容版本
    type: "optional"
```

---

## 七、授权验证系统

### 7.1 多层验证机制

```
┌─────────────────────────────────────────────────────────────┐
│                  授权验证流程                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. SDK 验证（本地）                                         │
│     ├── 验证 licenseKey 格式                                │
│     ├── 验证签名（本地公钥）                                 │
│     └── 检查过期时间                                         │
│                                                             │
│  2. API 验证（在线）                                         │
│     ├── 验证 licenseKey 有效性                              │
│     ├── 检查授权类型与使用场景                               │
│     └── 验证使用次数限制                                     │
│                                                             │
│  3. 心跳验证（定期）                                         │
│     ├── 每 24h 上报一次心跳                                  │
│     ├── 7 天未心跳视为离线                                   │
│     └── 超期需重新验证                                       │
│                                                             │
│  4. 离线验证（离线证书）                                     │
│     ├── 证书包含 license + 签名                              │
│     ├── 本地验证签名有效性                                   │
│     └── 适用于无网络环境                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 授权验证 API

```python
# 验证授权
POST /api/v1/licenses/verify
{
  "license_key": "lic_xxx",
  "skill_id": 123,
  "verification_type": "online"  # online | offline | heartbeat
}

# 响应
{
  "code": 0,
  "data": {
    "valid": true,
    "license_type": "team",
    "expires_at": "2025-12-31T23:59:59Z",
    "usage_limits": {
      "max_users": 10,
      "current_users": 3
    }
  }
}
```

---

## 八、监控与可观测性

### 8.1 监控指标

| 层级 | 指标 | 工具 |
|------|------|------|
| **应用层** | QPS、响应时间、错误率 | Prometheus |
| **业务层** | 注册量、发布量、交易量 | Prometheus + Grafana |
| **基础设施** | CPU、内存、磁盘、网络 | Node Exporter |
| **数据库** | 连接数、慢查询、锁等待 | pg_exporter |
| **缓存** | 命中率、内存使用、连接数 | redis_exporter |

### 8.2 链路追踪（OpenTelemetry）

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# 初始化链路追踪
FastAPIInstrumentor.instrument_app(app)

# 自定义 Span
@app.get("/api/v1/skills/{skill_id}")
async def get_skill(skill_id: int):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("get_skill_from_db"):
        skill = await db.query(Skill).filter(Skill.id == skill_id).first()
    return skill
```

### 8.3 日志规范

```json
{
  "timestamp": "2024-02-01T12:00:00Z",
  "level": "INFO",
  "service": "api",
  "request_id": "req_abc123",
  "user_id": 12345,
  "action": "get_skill",
  "resource": "skill",
  "resource_id": 678,
  "duration_ms": 45,
  "status_code": 200,
  "ip_address": "1.2.3.4",
  "user_agent": "Mozilla/5.0...",
  "metadata": {
    "source": "web",
    "cached": false
  }
}
```

---

## 九、安全设计

### 9.1 数据安全

| 措施 | 实现 |
|------|------|
| 传输加密 | HTTPS/TLS 1.3 |
| 存储加密 | 敏感数据 AES-256 |
| 密码安全 | bcrypt + salt |
| SQL 防护 | 参数化查询 |

### 9.2 访问控制

| 措施 | 说明 |
|------|------|
| 会话管理 | JWT + Redis 黑名单 |
| 限流保护 | Redis Token Bucket |
| 签名验证 | HMAC-SHA256 |

---

## 十、部署与运维

### 10.1 环境管理

```
开发环境 (dev)        → 开发人员本地开发
测试环境 (staging)    → 预发布验证
生产环境 (production) → 正式服务
```

### 10.2 Docker Compose 部署

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on: [db, redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  db:
    image: postgres:15-alpine
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=sillymd

  redis:
    image: redis:7-alpine
    volumes: [redis_data:/data]

  meilisearch:
    image: getmeili/meilisearch:v1.5
    volumes: [meili_data:/meili_data]

volumes:
  postgres_data:
  redis_data:
  meili_data:
```

---

## 十一、开发路线图

### Phase 1: MVP (0-3个月)
- ✅ 用户注册/登录
- ✅ Skills CRUD
- ✅ 基础版本控制
- ✅ 搜索与浏览

### Phase 2: 协作 (3-6个月)
- [ ] 团队管理
- [ ] Skills 依赖
- [ ] 权限细分

### Phase 3: 审核 (6-9个月)
- [ ] AI 自动审核
- [ ] 审核工作流

### Phase 4: 商用 (9-12个月)
- [ ] 商用 Skills
- [ ] 积分交易
- [ ] 授权验证

---

**文档版本**: v13.0
**最后更新**: 2026-02-01
**维护团队**: SillyMD Team
