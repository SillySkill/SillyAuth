# SillyMD Skills 在线平台 - 优化架构设计 v13.0

> **平台愿景**：打造专业的 AI Skills 托管与协作平台，支持 Skills 资产化管理、多领域团队协作、商用授权交易。

---

## 目录

1. [架构评审与改进建议](#一架构评审与改进建议)
2. [平台概述](#二平台概述)
3. [技术架构](#三技术架构)
4. [核心功能模块](#四核心功能模块)
5. [Skills 分类体系](#五skills-分类体系)
6. [AI 审核系统](#六ai-审核系统)
7. [多领域协作系统](#七多领域协作系统)
8. [商用授权与交易系统](#八商用授权与交易系统)
9. [数字存证架构](#九数字存证架构)
10. [用户与权限系统](#十用户与权限系统)
11. [运营与增长系统](#十一运营与增长系统)
12. [开发路线图](#十二开发路线图)
13. [安全设计](#十三安全设计)
14. [基础设施与部署](#十四基础设施与部署)

---

## 一、架构评审与改进建议

### 1.1 原架构评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 技术栈选型 | ⭐⭐⭐⭐☆ | 现代化技术栈，但需补充细节 |
| 数据库设计 | ⭐⭐⭐☆☆ | 表结构完整，但存在语法问题和性能隐患 |
| 系统架构 | ⭐⭐⭐☆☆ | 分层清晰，但缺少服务治理方案 |
| 安全设计 | ⭐⭐⭐☆☆ | 覆盖基本安全需求，需加强 RBAC |
| 可扩展性 | ⭐⭐⭐☆☆ | 有考虑扩展，但缺少具体方案 |
| 可维护性 | ⭐⭐⭐⭐☆ | 模块化设计良好 |

### 1.2 关键问题与改进

#### 问题 1: 数据库语法混乱

**问题**: 混用 MySQL 和 PostgreSQL 语法

```sql
-- ❌ 问题代码 (MySQL + PostgreSQL 混用)
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- MySQL 语法
    -- ...
);
```

**改进方案**:

```sql
-- ✅ PostgreSQL 标准语法
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    -- 使用 CHECK 约束替代 ENUM
    role TEXT NOT NULL CHECK (role IN ('user', 'vendor', 'admin')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ✅ 创建枚举类型（PostgreSQL 原生方式）
CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');
CREATE TYPE skill_category AS ENUM ('tech', 'product', 'design', 'marketing', 'ops');
CREATE TYPE skill_type AS ENUM ('free', 'commercial');
```

#### 问题 2: 缺少索引优化策略

**改进方案**:

```sql
-- ✅ 复合索引优化
CREATE INDEX idx_skills_category_type_status ON skills(category, type, status);
CREATE INDEX idx_skills_published_featured ON skills(published_at DESC) WHERE is_featured = TRUE;
CREATE INDEX idx_licenses_buyer_skill ON licenses(buyer_id, skill_id);
CREATE INDEX idx_reviews_skill_created ON reviews(skill_id, created_at DESC);

-- ✅ 部分索引（PostgreSQL 特性）
CREATE INDEX idx_active_commercial_skills ON skills(id, name)
WHERE type = 'commercial' AND status = 'approved' AND is_deleted = FALSE;

-- ✅ 全文搜索索引
CREATE INDEX idx_skills_fulltext ON skills
USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

#### 问题 3: 缺少服务间通信机制

**改进方案**:

```python
# ✅ 使用消息队列解耦服务
from faststream import FastStream, KafkaBroker
import json

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)

# 技能发布事件
@broker.publisher("skill.published")
async def publish_skill_event(skill_data: dict):
    await broker.publish(
        {
            "event_type": "skill.published",
            "skill_id": skill_data["id"],
            "author_id": skill_data["author_id"],
            "timestamp": datetime.utcnow().isoformat()
        },
        topic="skill.published"
    )

# 审核服务消费事件
@broker.subscriber("skill.published")
async def handle_skill_publish(msg: dict):
    # 触发审核流程
    await initiate_review(msg["skill_id"])

# 统计服务消费事件
@broker.subscriber("skill.published")
async def update_skill_stats(msg: dict):
    # 更新统计数据
    await increment_author_skill_count(msg["author_id"])
```

#### 问题 4: 缺少 RBAC 详细设计

**改进方案**:

```python
# ✅ 基于 Casbin 的 RBAC 实现
from casbin import Enforcer
from fastapi import Depends

# 模型定义 (model.conf)
"""
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
"""

# 权限检查中间件
async def check_permission(
    user: User = Depends(get_current_user),
    obj: str = None,
    act: str = None
):
    enforcer = Enforcer("model.conf", "policy.csv")
    if not enforcer.enforce(user.role, obj, act):
        raise HTTPException(status_code=403, detail="Permission denied")
    return True

# 策略示例 (policy.csv)
"""
p, admin, skills, *
p, vendor, skills, create
p, vendor, skills, update
p, vendor, skills, delete_own
p, user, skills, read
g, alice, admin
g, bob, vendor
"""
```

#### 问题 5: 缺少 API 版本控制

**改进方案**:

```python
# ✅ API 版本控制
from fastapi import APIRouter

# 版本化路由
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/skills/{skill_id}")
async def get_skill_v1(skill_id: str):
    # v1 实现
    pass

@v2_router.get("/skills/{skill_id}")
async def get_skill_v2(skill_id: str, include_details: bool = False):
    # v2 实现（向后兼容）
    pass

# 版本弃用策略
@app.get("/api/v1/skills/{skill_id}", deprecated=True)
async def deprecated_endpoint(skill_id: str):
    # 返回警告头
    return {
        "skill": skill_data,
        "_warning": "This API is deprecated. Please use /api/v2/skills/{id}"
    }
```

#### 问题 6: 缺少分布式追踪

**改进方案**:

```python
# ✅ OpenTelemetry 集成
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 配置追踪
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# 自动追踪 FastAPI
FastAPIInstrumentor.instrument_app(app)
```

### 1.3 新增改进项

| 改进项 | 优先级 | 说明 |
|--------|--------|------|
| 读写分离 | P1 | 主从复制，读写分离提升性能 |
| 缓存策略 | P0 | Redis 多层缓存架构 |
| 搜索引擎 | P1 | Meilisearch 替代 PG 全文搜索 |
| 限流降级 | P1 | 令牌桶 + 熔断器 |
| 数据归档 | P2 | 冷热数据分离 |
| WebSocket | P1 | 实时通知推送 |
| 任务调度 | P1 | Celery Beat 定时任务 |

---

## 二、平台概述

### 2.1 基本信息

| 项目 | 内容 |
|------|------|
| 网站域名 | sillymd.com（已完成备案） |
| 团队协作域名 | sillymd.com/组织名 |
| 服务器地址 | 47.96.133.238 |
| 平台定位 | AI Skills 托管中心 + 多领域协作网络 + 商用授权市场 |

### 2.2 名字内涵

- **"挺傻的"**：代表对 AI 现状的诚实认知，有时候 "AI，挺傻的"
- **人生态度**：容纳自身不足，持续迭代进化
- **技术理念**：承认 AI 局限，通过 Skills 补全能力边界

### 2.3 核心定义

**Skills 是什么？**

> Skills 是智能体与大模型交互的标准化说明文档，按需加载，降低 AI 管理成本。

**Skills 标准化的扩展：**

Skills 不仅限于编程代码，还可以是：
- 产品需求文档 (PRD)
- 设计规范文档 (Design Specs)
- 市场推广方案 (Marketing Plans)
- 运营流程手册 (Operations Guides)
- 用户研究报告 (User Research)

**所有项目协作都可以按照 Skills 文件标准进行管理。**

### 2.4 核心价值

| 价值 | 说明 |
|------|------|
| **资产化** | 将 Skills 从"文档"升级为"数字资产" |
| **可授权** | 商用 Skills 支持授权交易，资产可流转 |
| **可验证** | 商用 Skills 具有数字签名指纹，确保内容真实 |
| **标准化** | 统一 Skills 格式，跨团队、跨领域协作无障碍 |
| **安全可靠** | 多层安全机制，数据加密存储 |

---

## 三、技术架构

### 3.1 技术栈选型（已优化）

| 层级 | 技术选型 | 说明 | 理由 |
|------|----------|------|------|
| 前端 | React 18 + TypeScript + Zustand | 单页应用，轻量状态管理 | Zustand 比 Redux 更简洁 |
| 前端构建 | Vite 5.x | 快速开发构建 | 比 Webpack 快 10x |
| UI 框架 | TailwindCSS + shadcn/ui | 组件库 | 可定制性强 |
| 后端 | Python 3.11+ + FastAPI | RESTful API，异步支持 | 性能优于 Flask，自动生成文档 |
| 数据库 | PostgreSQL 16+ | 关系型数据存储 | JSON支持更好，适合复杂数据 |
| 缓存 | Redis 7.2 Cluster | 会话、队列、热点数据 | 集群模式高可用 |
| 消息队列 | Kafka | 异步事件、服务解耦 | 高吞吐量，持久化 |
| 异步任务 | Celery + Redis | 后台任务处理 | 成熟方案 |
| AI 审核 | DeepSeek / 智谱 /KIMI | 内容合规性审核 | 多模型备选 |
| 搜索 | Meilisearch | 全文搜索引擎 | 毫秒级响应，中文友好 |
| 存储 | 阿里云 OSS | Skills 文件存储 | - |
| CDN | 阿里云 CDN / CloudFlare | 静态资源加速 | - |
| 追踪 | OpenTelemetry + Jaeger | 分布式追踪 | 排查问题 |
| 监控 | Prometheus + Grafana | 监控告警 | - |

### 3.2 系统架构图（已优化）

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│   │  Web端   │  │  管理后台 │  │  API文档  │  │  SDK工具  │      │
│   └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘      │
├─────────┼──────────────┼──────────────┼──────────────┼──────────┤
│         │              │              │              │          │
│   ┌─────▼──────────────▼──────────────▼──────────────▼──────┐   │
│   │                    CDN + WAF                             │   │
│   └─────────────────────────────┬───────────────────────────┘   │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│   ┌─────────────────────────────▼───────────────────────────┐   │
│   │                    API Gateway                           │   │
│   │   (认证 + 限流 + 日志 + 版本控制 + 签名验证)              │   │
│   └─────────────────────────────┬───────────────────────────┘   │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│   ┌─────────────────────────────▼───────────────────────────┐   │
│   │                    业务逻辑层 (FastAPI)                   │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │ 用户服务 │ │ Skills服务│ │ 审核服务 │ │ 交易服务 │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │ 团队服务 │ │ 积分服务 │ │ 授权服务 │ │ 钱包服务 │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │ 推荐服务 │ │ 消息服务 │ │ 统计服务 │ │ 运营服务 │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   └─────────────────────────────┬───────────────────────────┘   │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│   ┌─────────────────────────────▼───────────────────────────┐   │
│   │                      消息队列层                           │   │
│   │                    Kafka Cluster                        │   │
│   └─────────────────────────────┬───────────────────────────┘   │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│   ┌─────────────────────────────▼───────────────────────────┐   │
│   │                        数据存储层                        │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │PostgreSQL│ │  Redis   │ │   OSS    │ │Meilisearch││   │
│   │  │ 主从集群 │ │  Cluster  │ │          │ │           │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 数据库设计（已优化）

#### 3.3.1 PostgreSQL 类型定义

```sql
-- ============================================
-- 枚举类型定义
-- ============================================

-- 用户角色
CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');

-- 供应商等级
CREATE TYPE vendor_level AS ENUM ('normal', 'premium', 'gold');

-- Skills 分类
CREATE TYPE skill_category AS ENUM ('tech', 'product', 'design', 'marketing', 'ops');

-- Skills 类型
CREATE TYPE skill_type AS ENUM ('free', 'commercial');

-- Skills 状态
CREATE TYPE skill_status AS ENUM ('draft', 'reviewing', 'approved', 'rejected');

-- 团队角色
CREATE TYPE team_role AS ENUM ('owner', 'admin', 'member', 'viewer');

-- 项目角色
CREATE TYPE project_role AS ENUM ('prd', 'design', 'tech', 'marketing', 'ops', 'other');

-- 授权类型
CREATE TYPE license_type AS ENUM ('personal', 'team', 'enterprise');

-- 交易类型
CREATE TYPE transaction_type AS ENUM ('recharge', 'purchase', 'earning', 'refund', 'withdraw');

-- 交易状态
CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed');

-- 通知类型
CREATE TYPE notification_type AS ENUM ('system', 'skill_update', 'comment', 'license', 'achievement', 'team');

-- 邀请状态
CREATE TYPE invitation_status AS ENUM ('pending', 'accepted', 'expired');

-- 成就类别
CREATE TYPE achievement_category AS ENUM ('creation', 'contribution', 'social', 'commercial');

-- 审核阶段
CREATE TYPE review_stage AS ENUM ('L1', 'L2', 'L3');

-- 审核结果
CREATE TYPE review_result AS ENUM ('approved', 'rejected', 'revision_required');

-- ============================================
-- 核心表结构
-- ============================================

-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    vendor_level vendor_level DEFAULT 'normal',
    ai_points INT DEFAULT 0,
    avatar_url VARCHAR(500),
    bio TEXT,
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 自动更新 updated_at 触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Skills 表
CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,
    skill_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    author_id BIGINT NOT NULL,
    category skill_category NOT NULL,
    type skill_type DEFAULT 'free',
    version VARCHAR(20) DEFAULT '1.0.0',
    status skill_status DEFAULT 'draft',

    -- 软删除和精选
    is_deleted BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    repo_url VARCHAR(500),
    dependencies JSONB,

    -- 数字存证字段
    content_hash CHAR(64),
    platform_signature VARCHAR(255),
    author_signature VARCHAR(255),

    -- 商用字段
    price INT DEFAULT 0,
    license_types JSONB,
    original_price INT DEFAULT 0,
    promo_until TIMESTAMPTZ,

    -- 统计字段（考虑异步更新）
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    favorite_count INT DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Skills 版本表
CREATE TABLE skill_versions (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    version VARCHAR(20) NOT NULL,
    content LONGTEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    commit_message VARCHAR(500),
    author_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id),
    UNIQUE (skill_id, version)
);

-- Skills 依赖关系表
CREATE TABLE skill_dependencies (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    depends_on_skill_id BIGINT NOT NULL,
    version_constraint VARCHAR(50),
    dependency_type TEXT DEFAULT 'required',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (skill_id, depends_on_skill_id)
);

-- 标签表
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Skills 标签关联表
CREATE TABLE skill_tags (
    skill_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (skill_id, tag_id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Skills 收藏表
CREATE TABLE skill_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (user_id, skill_id)
);

-- Skills 评论表
CREATE TABLE skill_comments (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_id BIGINT,
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES skill_comments(id) ON DELETE CASCADE
);

CREATE TRIGGER update_skill_comments_updated_at BEFORE UPDATE ON skill_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 团队表
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id BIGINT NOT NULL,
    description TEXT,
    avatar_url VARCHAR(500),
    member_count INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 团队成员表
CREATE TABLE team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role team_role DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (team_id, user_id)
);

-- 团队项目表
CREATE TABLE team_projects (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    project_slug VARCHAR(200) NOT NULL,
    description TEXT,
    owner_id BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    UNIQUE (team_id, project_slug)
);

CREATE TRIGGER update_team_projects_updated_at BEFORE UPDATE ON team_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 项目 Skills 关联表
CREATE TABLE project_skills (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    role project_role DEFAULT 'other',
    order_index INT DEFAULT 0,
    added_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (project_id, skill_id)
);

-- 授权记录表
CREATE TABLE licenses (
    id BIGSERIAL PRIMARY KEY,
    license_id VARCHAR(50) UNIQUE NOT NULL,
    license_key VARCHAR(100) UNIQUE NOT NULL,
    skill_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    license_type license_type NOT NULL,
    price INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (vendor_id) REFERENCES users(id)
);

-- 积分交易表
CREATE TABLE point_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    type transaction_type NOT NULL,
    balance_after INT NOT NULL,
    related_id BIGINT,
    description VARCHAR(500),
    status transaction_status DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 审核记录表
CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    reviewer_id BIGINT NOT NULL,
    stage review_stage NOT NULL,
    result review_result NOT NULL,
    comments TEXT,
    ai_model VARCHAR(50),
    ai_confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 成就表
CREATE TABLE achievements (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    category achievement_category NOT NULL,
    xp_reward INT DEFAULT 0,
    points_reward INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 用户成就关联表
CREATE TABLE user_achievements (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    achievement_id BIGINT NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE (user_id, achievement_id)
);

-- 操作日志表
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 用户活跃度表
CREATE TABLE user_activity_stats (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    skills_viewed INT DEFAULT 0,
    skills_downloaded INT DEFAULT 0,
    skills_created INT DEFAULT 0,
    comments_posted INT DEFAULT 0,
    login_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, date)
);

-- 价格历史表
CREATE TABLE skill_price_history (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    old_price INT NOT NULL,
    new_price INT NOT NULL,
    change_reason VARCHAR(200),
    changed_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- 消息通知表
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    link_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 邀请记录表
CREATE TABLE invitations (
    id BIGSERIAL PRIMARY KEY,
    inviter_id BIGINT NOT NULL,
    invitee_email VARCHAR(100) NOT NULL,
    invite_code VARCHAR(20) UNIQUE NOT NULL,
    status invitation_status DEFAULT 'pending',
    team_id BIGINT,
    reward_points INT DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (inviter_id) REFERENCES users(id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
);

-- ============================================
-- 索引优化
-- ============================================

-- 复合索引
CREATE INDEX idx_users_role ON users(role) WHERE is_active = TRUE;
CREATE INDEX idx_skills_category_type_status ON skills(category, type, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_skills_author_status ON skills(author_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_skills_published_featured ON skills(published_at DESC) WHERE is_featured = TRUE AND status = 'approved';
CREATE INDEX idx_licenses_buyer_skill ON licenses(buyer_id, skill_id) WHERE is_active = TRUE;
CREATE INDEX idx_licenses_vendor ON licenses(vendor_id, created_at DESC) WHERE is_active = TRUE;
CREATE INDEX idx_reviews_skill_created ON reviews(skill_id, created_at DESC);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read, created_at DESC);
CREATE INDEX idx_point_transactions_user_created ON point_transactions(user_id, created_at DESC);

-- 全文搜索索引
CREATE INDEX idx_skills_fulltext ON skills
USING gin(to_tsvector('simple', name || ' ' || COALESCE(description, '')))
WHERE is_deleted = FALSE AND status = 'approved';

-- 部分索引（PostgreSQL 特性）
CREATE INDEX idx_active_commercial_skills ON skills(id, name)
WHERE type = 'commercial' AND status = 'approved' AND is_deleted = FALSE;

-- ============================================
-- 分区表（大数据量表）
-- ============================================

-- 审计日志按月分区
CREATE TABLE audit_logs_partitioned (
    id BIGSERIAL,
    user_id BIGINT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- 用户活跃度按年分区
CREATE TABLE user_activity_stats_partitioned (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    skills_viewed INT DEFAULT 0,
    skills_downloaded INT DEFAULT 0,
    skills_created INT DEFAULT 0,
    comments_posted INT DEFAULT 0,
    login_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (date);

-- 创建分区
CREATE TABLE user_activity_stats_2026 PARTITION OF user_activity_stats_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

#### 3.3.2 缓存策略设计

```python
# ============================================
# Redis 缓存策略
# ============================================

from redis import Redis
from redis.cluster import RedisCluster
from typing import Optional, Any
import json
import hashlib

class CacheManager:
    """多层级缓存管理器"""

    def __init__(self):
        # Redis 集群配置
        self.redis_cluster = RedisCluster(
            startup_nodes=[
                {"host": "redis-node-1", "port": 7000},
                {"host": "redis-node-2", "port": 7001},
                {"host": "redis-node-3", "port": 7002},
            ],
            decode_responses=True
        )

    # L1 缓存：热点数据（内存，1分钟）
    async def get_l1(self, key: str) -> Optional[Any]:
        """本地缓存（可以使用 functools.lru_cache）"""
        pass

    # L2 缓存：Redis（5分钟）
    async def get_l2(self, key: str) -> Optional[Any]:
        """Redis 缓存"""
        data = await self.redis_cluster.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_l2(self, key: str, value: Any, ttl: int = 300):
        """设置 Redis 缓存"""
        await self.redis_cluster.setex(
            key,
            ttl,
            json.dumps(value)
        )

    # 缓存键生成策略
    @staticmethod
    def make_key(prefix: str, *args, **kwargs) -> str:
        """生成标准化缓存键"""
        key_parts = [prefix]
        key_parts.extend(str(a) for a in args)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend(f"{k}={v}" for k, v in sorted_kwargs)
        return ":".join(key_parts)

# ============================================
# FastAPI 缓存装饰器
# ============================================

from functools import wraps
from fastapi import Request

def cache_response(prefix: str, ttl: int = 300):
    """响应缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试从缓存获取
            cache_key = CacheManager.make_key(prefix, *args, **kwargs)
            cached = await cache_manager.get_l2(cache_key)
            if cached:
                return cached

            # 执行原函数
            result = await func(*args, **kwargs)

            # 存入缓存
            await cache_manager.set_l2(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# 使用示例
@cache_response("skill:detail", ttl=600)
async def get_skill_detail(skill_id: str):
    """获取 Skill 详情（缓存 10 分钟）"""
    return await db.query(Skill).filter(Skill.id == skill_id).first()

# ============================================
# 缓存失效策略
# ============================================

class CacheInvalidation:
    """缓存失效管理"""

    @staticmethod
    async def invalidate_skill(skill_id: str):
        """Skill 相关缓存失效"""
        patterns = [
            f"skill:detail:{skill_id}",
            f"skill:list:*",
            f"skill:author:*",
            f"search:skill:*"
        ]
        for pattern in patterns:
            keys = await redis_cluster.keys(pattern)
            if keys:
                await redis_cluster.delete(*keys)

    @staticmethod
    async def invalidate_user(user_id: int):
        """用户相关缓存失效"""
        patterns = [
            f"user:profile:{user_id}",
            f"user:skills:{user_id}",
            f"user:stats:{user_id}"
        ]
        for pattern in patterns:
            keys = await redis_cluster.keys(pattern)
            if keys:
                await redis_cluster.delete(*keys)
```

### 3.4 Meilisearch 集成

```python
# ============================================
# Meilisearch 搜索引擎集成
# ============================================

from meilisearch import Client
from typing import List, Dict

class SearchService:
    """Meilisearch 搜索服务"""

    def __init__(self):
        self.client = Client('http://127.0.0.1:7700', 'masterKey')

    async def index_skill(self, skill: Dict):
        """索引单个 Skill"""
        self.client.index('skills').add_documents([{
            'id': skill['id'],
            'skill_id': skill['skill_id'],
            'name': skill['name'],
            'description': skill['description'],
            'category': skill['category'],
            'type': skill['type'],
            'tags': skill.get('tags', []),
            'author_name': skill.get('author_name'),
            'rating_avg': skill.get('rating_avg', 0),
            'download_count': skill.get('download_count', 0),
        }])

    async def search_skills(
        self,
        query: str,
        category: str = None,
        type: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """搜索 Skills"""
        search_params = {
            'limit': limit,
            'attributesToCrop': ['description'],
            'cropLength': 50
        }

        # 添加过滤器
        filters = []
        if category:
            filters.append(f'category = {category}')
        if type:
            filters.append(f'type = {type}')
        if filters:
            search_params['filter'] = ' AND '.join(filters)

        results = self.client.index('skills').search(query, search_params)
        return results['hits']

# ============================================
# 搜索索引配置
# ============================================

# Skills 索引配置
index_config = {
    'primaryKey': 'id',
    'searchableAttributes': [
        'name',
        'description',
        'tags',
        'author_name'
    ],
    'filterableAttributes': [
        'category',
        'type',
        'rating_avg'
    ],
    'sortableAttributes': [
        'rating_avg',
        'download_count',
        'created_at'
    ],
    'rankingRules': [
        'words',
        'typo',
        'proximity',
        'attribute',
        'sort',
        'exactness',
        'download_count:desc',
        'rating_avg:desc'
    ],
    'stopWords': [
        'the', 'a', 'an', 'and', 'or', 'but',
        '的', '了', '是', '在', '和', '与'
    ],
    'synonyms': {
        'ai': ['artificial intelligence', '人工智能'],
        'api': ['interface', '接口'],
        'sdk': ['development kit', '开发工具包']
    }
}
```

### 3.5 WebSocket 实时通知

```python
# ============================================
# WebSocket 实时通知系统
# ============================================

from fastapi import WebSocket
from typing import Dict, Set
import json

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """建立连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """断开连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_notification(self, user_id: int, notification: Dict):
        """发送通知给特定用户"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(notification)
            except Exception:
                # 连接已断开，清理
                self.disconnect(user_id)

    async def broadcast(self, notification: Dict, exclude: int = None):
        """广播通知"""
        for user_id, websocket in self.active_connections.items():
            if exclude and user_id == exclude:
                continue
            try:
                await websocket.send_json(notification)
            except Exception:
                self.disconnect(user_id)

manager = ConnectionManager()

# ============================================
# FastAPI WebSocket 路由
# ============================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

ws_router = APIRouter()

@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    current_user: User = Depends(get_current_user_ws)
):
    """WebSocket 连接端点"""
    await manager.connect(current_user.id, websocket)

    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()

            # 处理心跳
            if data == "ping":
                await websocket.send_text("pong")

            # 处理其他消息
            else:
                message = json.loads(data)
                # 处理客户端请求...

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)

# ============================================
# 通知推送
# ============================================

async def push_notification(
    user_id: int,
    notification_type: str,
    title: str,
    content: str = None,
    link_url: str = None
):
    """推送通知（WebSocket + 数据库）"""

    # 1. 保存到数据库
    notification = await create_notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        content=content,
        link_url=link_url
    )

    # 2. 实时推送
    await manager.send_notification(user_id, {
        "type": "notification",
        "data": {
            "id": notification.id,
            "type": notification_type,
            "title": title,
            "content": content,
            "link_url": link_url,
            "created_at": notification.created_at.isoformat()
        }
    })

    # 3. 离线用户标记（未读计数）
    await redis_cluster.incr(f"notifications:unread:{user_id}")

# ============================================
# 通知类型定义
# ============================================

# Skill 相关
async def notify_skill_published(user_id: int, skill_name: str):
    """Skill 发布成功通知"""
    await push_notification(
        user_id=user_id,
        notification_type="skill_update",
        title=f"您的 Skill 《{skill_name}》已成功发布！",
        content="恭喜！您的 Skill 已通过审核并上线。",
        link_url=f"/skills/{skill_name}"
    )

async def notify_skill_comment(user_id: int, skill_name: str, commenter: str):
    """收到新评论通知"""
    await push_notification(
        user_id=user_id,
        notification_type="comment",
        title=f"{commenter} 评论了您的 Skill",
        content=f"您的 Skill 《{skill_name}》收到了新评论。",
        link_url=f"/skills/{skill_name}#comments"
    )

# 授权相关
async def notify_license_purchased(vendor_id: int, skill_name: str, buyer: str, amount: int):
    """售出授权通知"""
    await push_notification(
        user_id=vendor_id,
        notification_type="license",
        title=f"售出授权！+{amount} AI Points",
        content=f"{buyer} 购买了您的 Skill 《{skill_name}》的授权。",
        link_url=f"/dashboard/sales"
    )

# 成就相关
async def notify_achievement_unlocked(user_id: int, achievement_name: str, reward: int):
    """解锁成就通知"""
    await push_notification(
        user_id=user_id,
        notification_type="achievement",
        title=f"解锁成就：{achievement_name}",
        content=f"恭喜！您获得了 {reward} AI Points 奖励。",
        link_url=f"/achievements"
    )
```

### 3.6 限流与降级策略

```python
# ============================================
# 限流策略（令牌桶算法）
# ============================================

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

# 限流规则
@app.get("/api/v1/skills")
@limiter.limit("60/minute")  # 每分钟 60 次
async def list_skills(request: Request):
    pass

@app.post("/api/v1/skills")
@limiter.limit("10/minute")  # 每分钟 10 次
async def create_skill(request: Request):
    pass

@app.get("/api/v1/search")
@limiter.limit("30/minute")  # 每分钟 30 次
async def search_skills(request: Request):
    pass

# ============================================
# 熔断器（Circuit Breaker）
# ============================================

from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def call_external_ai_api(text: str):
    """调用外部 AI API（带熔断）"""
    try:
        response = await http_client.post(
            "https://api.example.com/analyze",
            json={"text": text}
        )
        return response.json()
    except Exception as e:
        # 记录失败
        logger.error(f"AI API call failed: {e}")
        raise

# ============================================
# 降级策略
# ============================================

class DegradationStrategy:
    """服务降级策略"""

    @staticmethod
    async def search_skills_fallback(query: str):
        """搜索降级：返回基础结果"""
        # Meilisearch 不可用时，降级到 PostgreSQL 全文搜索
        return await db.query(Skill).filter(
            Skill.name.ilike(f"%{query}%")
        ).limit(10).all()

    @staticmethod
    async def recommendation_fallback(user_id: int):
        """推荐降级：返回热门 Skills"""
        # 推荐服务不可用时，返回热门列表
        return await db.query(Skill).order_by(
            Skill.view_count.desc()
        ).limit(10).all()

    @staticmethod
    async def ai_review_fallback(skill_data: dict):
        """AI 审核降级：标记为人工审核"""
        # AI 审核不可用时，直接进入人工审核队列
        return await create_review_ticket(
            skill_id=skill_data['id'],
            stage='L2',
            auto_assigned=True
        )
```

---

## 四、核心功能模块

### 4.1 Skills 托管中心

#### 4.1.1 免费 Skills 区域

| 特性 | 说明 |
|------|------|
| 内容类型 | AI 使用技巧、最佳实践、开源工具 |
| 访问权限 | 公开，所有用户可查看下载 |
| 编辑权限 | 作者可编辑，他人可 Fork |
| 许可证 | MIT / Apache 2.0 / CC BY |
| 社区功能 | 收藏、评论、评分 |

#### 4.1.2 商用 Skills 区域

| 特性 | 说明 |
|------|------|
| 内容类型 | 行业解决方案、企业级应用、专业工具 |
| 访问权限 | 需购买授权或订阅 |
| 存储方式 | OSS 存储 + 数字签名存证 |
| 授权类型 | 个人授权 / 团队授权 / 企业授权 |
| 授权验证 | SDK 验证 + 在线验证 + 证书验证 |

### 4.2 版本管理

| 功能 | 说明 |
|------|------|
| Git 风格版本控制 | 版本历史、分支、回滚 |
| 版本对比 | 可视化展示版本间差异 |
| 版本标签 | 支持为重要版本打标签 |
| 自动备份 | 每次修改自动备份 |
| 语义化版本 | 支持 SemVer 依赖约束 |

### 4.3 搜索与发现（已优化）

| 搜索维度 | 说明 | 优先级 |
|----------|------|--------|
| 关键词搜索 | Meilisearch 全文检索 | P0 |
| 分类筛选 | 按领域/类型筛选 | P0 |
| 标签筛选 | 按自定义标签筛选 | P0 |
| 智能推荐 | AI 个性化推荐 | P1 |
| 排序方式 | 热度/评分/最新/价格 | P0 |
| 相似 Skills | 基于标签和内容相似度 | P1 |
| 搜索建议 | 自动补全 + 热门搜索 | P1 |

### 4.4 Skills 依赖管理

```yaml
# 支持 SemVer 版本约束
skill:
  id: "tech-auth-api"
  name: "用户认证 API"
  dependencies:
    - skill_id: "tech-database-base"
      version: ">=1.2.0"  # 最低版本
      type: "required"
    - skill_id: "tech-logger"
      version: "^2.0.0"   # 兼容版本
      type: "optional"
    - skill_id: "tech-cache"
      version: "~1.5.0"   # 补丁版本更新
      type: "required"

# 依赖解析策略
resolution_strategy:
  - highest_compatible  # 选择最高兼容版本
  - lowest_compatible   # 选择最低兼容版本（默认）
```

---

## 五、Skills 分类体系

### 5.1 按领域分类

#### 5.1.1 技术 Skills (Tech Skills)

| 子类 | 示例 |
|------|------|
| 开发工具 | 代码生成器、调试工具、性能分析 |
| 架构设计 | 系统架构、微服务、API 设计 |
| 自动化 | CI/CD、脚本、工作流自动化 |
| 数据处理 | ETL、数据清洗、数据可视化 |

#### 5.1.2 产品 Skills (Product Skills)

| 子类 | 示例 |
|------|------|
| 需求管理 | PRD 模板、需求分析框架 |
| 用户研究 | 用户画像、调研方法 |
| 产品规划 | 路线图、OKR、优先级管理 |
| 数据分析 | 埋点方案、漏斗分析 |

#### 5.1.3 设计 Skills (Design Skills)

| 子类 | 示例 |
|------|------|
| UI 设计 | 组件库、设计规范、配色方案 |
| UX 设计 | 交互模式、用户旅程、可用性测试 |
| 品牌设计 | Logo 规范、品牌指南、VI 系统 |

#### 5.1.4 市场 Skills (Marketing Skills)

| 子类 | 示例 |
|------|------|
| 内容营销 | 文案模板、内容规划 |
| 社交媒体 | 运营策略、涨粉技巧 |
| 广告投放 | 投放策略、素材模板 |
| 数据分析 | 获客分析、转化优化 |

#### 5.1.5 运营 Skills (Operations Skills)

| 子类 | 示例 |
|------|------|
| 用户运营 | 用户分层、留存策略 |
| 活动运营 | 活动策划、执行流程 |
| 内容运营 | 内容规划、发布策略 |

### 5.2 按授权类型分类

```
┌─────────────────────────────────────────────────────────────┐
│                    授权类型                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  免费 (Free)                                                │
│  ├── 开源许可 - MIT、Apache、GPL                            │
│  └── CC 许可 - CC BY、CC BY-SA                              │
│                                                             │
│  商用 (Commercial)                                          │
│  ├── 个人授权 - 单用户使用 (1x)                             │
│  ├── 团队授权 - 团队内共享，最多 10 人 (3x)                 │
│  └── 企业授权 - 企业内使用，无人数限制 (10x)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、AI 审核系统

### 6.1 审核目的

所有上架的 Skills 必须通过 AI 审核，确保：
- **合规性**：符合法律法规，无违法违规内容
- **安全性**：无恶意代码、无病毒木马
- **准确性**：内容真实有效，无虚假宣传
- **格式规范**：符合 Skills 格式标准

### 6.2 审核流程

```
┌─────────────────────────────────────────────────────────────┐
│                      AI 审核流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户提交 Skills                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L1 初审   │  AI 自动审核                               │
│  │  (AI 自动)  │  - 格式检查                                │
│  └──────┬──────┘  - 基础合规检查                            │
│         │          - 重复检测                                │
│         │          - 消耗额度：1 次/天 免费                  │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L2 复审   │  AI 深度审核                               │
│  │ (AI + 人工) │  - 专业准确性                              │
│  └──────┬──────┘  - 商业价值评估                            │
│         │          - 定价合理性                              │
│         │          - 市场需求分析                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L3 终审   │  平台管理员                                │
│  │  (管理员)   │  - 最终质量把关                            │
│  └──────┬──────┘  - 上架决定                                │
│         │                                                   │
│         ▼                                                   │
│   上架 / 驳回                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 审核维度

| 维度 | 技术 Skills | 产品 Skills | 设计 Skills | 市场/运营 Skills |
|------|-------------|-------------|-------------|------------------|
| 法律合规 | ✅ | ✅ | ✅ | ✅ |
| 内容安全 | ✅ | ✅ | ✅ | ✅ |
| 格式规范 | ✅ | ✅ | ✅ | ✅ |
| 专业准确 | ✅ | ✅ | ✅ | ✅ |
| 商业价值 | ✅ | ✅ | ✅ | ✅ |
| 原创性检测 | ✅ | ✅ | ✅ | ✅ |

### 6.4 审核配额与定价

| 用户类型 | 免费审核额度 | 超额费用 |
|---------|-------------|---------|
| 普通用户 | 3 次/月 | 10 AI Points/次 |
| 供应商 | 20 次/月 | 5 AI Points/次 |
| 金牌供应商 | 100 次/月 | 免费 |

### 6.5 审核结果处理

| 结果 | 说明 | 处理方式 |
|------|------|----------|
| **通过** | 符合所有标准 | 自动上架 |
| **需修正** | 存在小问题，可修正 | 返回用户修正后重新提交 |
| **驳回** | 存在重大问题 | 拒绝上架，说明原因，保留修改建议 |

---

## 七、多领域协作系统

### 7.1 协作理念

**核心理念**：将 Skills 标准化扩展到所有工作领域。

传统的项目协作各自为政：
- 技术团队用 Git
- 产品团队用文档系统
- 设计团队用设计工具
- 市场团队用营销系统

**SillyMD 的解决方案**：所有团队都用 Skills 标准来管理和协作。

### 7.2 团队组织结构

```
团队域名结构：sillymd.com/{team_slug}

示例：
├── sillymd.com/acme-tech          → ACME 科技公司
│   └── sillymd.com/acme-tech/payment-system  → 项目：支付系统
├── sillymd.com/design-studio      → 某设计工作室
├── sillymd.com/marketing-agency   → 某营销公司
└── sillymd.com/startup-abc        → 某创业团队
```

### 7.3 团队角色

| 角色 | 权限 | 说明 |
|------|------|------|
| **Owner** | 完全控制 | 团队创建者，可解散团队 |
| **Admin** | 管理 | 管理成员、设置、项目 |
| **Member** | 编辑 | 创建/编辑 Skills，参与项目 |
| **Viewer** | 查看 | 只读访问团队内容 |

### 7.4 项目协作模式

```
┌─────────────────────────────────────────────────────────────┐
│                    项目协作模式                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  项目启动                                                   │
│    ├── 产品经理创建 "产品需求 Skill"                        │
│    │   └── 依赖：设计、技术                                 │
│    ├── 设计师基于需求创建 "设计规范 Skill"                  │
│    │   └── 依赖：产品需求                                   │
│    ├── 开发者基于规范创建 "技术实现 Skill"                  │
│    │   └── 依赖：设计规范、数据库 Base Skill                │
│    └── 运营创建 "推广方案 Skill"                            │
│        └── 依赖：产品需求                                   │
│                                                             │
│  项目迭代                                                   │
│    ├── 每个 Skill 独立版本控制                              │
│    ├── Skill 之间通过依赖关系自动关联                       │
│    ├── 上游 Skill 变更通知下游维护者                        │
│    ├── 形成完整的知识沉淀                                   │
│    └── 项目可导出为完整文档包                               │
│                                                             │
│  项目交付                                                   │
│    ├── 所有 Skills 形成项目资产                             │
│    ├── 可导出为完整项目文档                                 │
│    ├── 可打包发布为商用 Skill                               │
│    └── 可复用至新项目                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.5 Skills 引用系统

Skills 可以相互引用，形成知识网络：

```yaml
# 产品需求 Skill
skill:
  id: "prd-user-auth"
  name: "用户认证需求"
  version: "1.0.0"
  dependencies:
    - skill_id: "design-auth-ui"
      type: "design"
      version: ">=1.0.0"
    - skill_id: "impl-auth-api"
      type: "tech"
      version: ">=1.2.0"

# 技能依赖图自动生成
dependency_graph:
  prd-user-auth:
    ├── design-auth-ui
    │   └── design-color-palette (底层依赖)
    └── impl-auth-api
        ├── tech-database-base (底层依赖)
        └── tech-cache (可选依赖)
```

---

## 八、商用授权与交易系统

### 8.1 AI 积分体系

**AI Points (AI 积分)** 是平台内的虚拟积分单位。

| 获取方式 | 说明 |
|----------|------|
| 充值购买 | 支持支付宝、微信、银行卡 |
| 销售收益 | 出售商用 Skills 获得 |
| 活动奖励 | 平台活动、推广奖励 |
| 贡献奖励 | 贡献优质免费 Skills |
| 邀请奖励 | 邀请新用户注册 |
| 成就奖励 | 解锁成就获得 |

### 8.2 商用 Skills 定价策略

| Skills 类型 | 建议价格区间 | 说明 |
|-------------|--------------|------|
| 基础工具类 | 100-500 AI Points | 通用脚本、模板 |
| 专业应用类 | 500-2000 AI Points | 行业解决方案 |
| 企业级方案 | 2000-10000 AI Points | 完整系统、复杂集成 |
| 独家定制类 | 10000+ AI Points | 高度定制化 |

### 8.3 授权类型与价格

| 授权类型 | 价格倍数 | 使用范围 | 说明 |
|----------|----------|----------|------|
| **个人授权** | 1x | 单用户使用 | 仅供个人使用 |
| **团队授权** | 3x | 团队内共享 (最多 10 人) | 同一团队内使用 |
| **企业授权** | 10x | 企业内使用 (无人数限制) | 整个企业使用 |

### 8.4 授权验证机制

#### SDK 验证

```javascript
// SDK 自动验证授权
const client = new SillyClient({
  apiKey: process.env.SILLY_API_KEY,
  licenseKey: process.env.SILLY_LICENSE_KEY  // 商用授权密钥
});

// 访问商用 Skill 时自动验证
const skill = await client.skills.get('commercial-skill-id');
// SDK 自动：
// 1. 验证 licenseKey 有效性
// 2. 检查授权类型
// 3. 检查是否过期
// 4. 记录访问日志
```

#### 离线验证

```javascript
// 授权证书（可离线使用）
const licenseCertificate = {
  license_id: "lic_abc123",
  skill_id: "com-payment-gateway",
  user_id: 12345,
  license_type: "team",
  expires_at: 1737657600,
  signature: "0xabc123...",  // 平台私钥签名
  public_key: "0xdef456..."   // 平台公钥（用于验证）
};

// 本地验证签名
function verifyLicense(certificate) {
  const data = `${certificate.license_id}:${certificate.skill_id}:${certificate.user_id}:${certificate.license_type}:${certificate.expires_at}`;
  return verifySignature(data, certificate.signature, certificate.public_key);
}
```

### 8.5 交易流程

```
┌─────────────────────────────────────────────────────────────┐
│                    交易流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  买家                                                      │
│    │                                                       │
│    ├── 浏览商用 Skills                                     │
│    ├── 查看授权类型和价格                                  │
│    ├── 选择授权类型 (个人/团队/企业)                        │
│    ├── 确认订单，扣除 AI Points                            │
│    └── 获得授权许可 + 授权密钥                             │
│                                                             │
│  平台                                                      │
│    │                                                       │
│    ├── 记录交易                                            │
│    ├── 生成授权密钥                                        │
│    ├── 平台抽成 (15-20%)                                   │
│    └── 供应商到账 (80-85%)                                 │
│                                                             │
│  供应商                                                    │
│    │                                                       │
│    ├── 查看销售数据                                        │
│    ├── AI Points 余额增加                                  │
│    ├── 销售通知推送                                        │
│    └── 可申请提现                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.6 平台抽成规则

| 供应商等级 | 累计销售额 | 平台抽成 | 供应商收益 | 特权 |
|------------|--------|----------|------------|------|
| 普通供应商 | - | 20% | 80% | 基础功能 |
| 优质供应商 | ≥ 5,000 Points | 15% | 85% | 更多审核额度 |
| 金牌供应商 | ≥ 50,000 Points | 10% | 90% | 优先推荐、专属客服 |

### 8.7 提现规则

| 规则项 | 说明 |
|--------|------|
| 最低提现 | 500 AI Points |
| 提现周期 | 每周一处理 |
| 提现方式 | 支付宝、银行转账 |
| 汇率 | 100 AI Points = 10 元人民币 |
| 手续费 | 免费（平台承担） |

---

## 九、数字存证架构

### 9.1 为什么商用 Skills 需要数字存证

| 需求 | 传统存储 | 数字签名存证 |
|------|----------|-------------|
| 数据完整性 | 中心化可篡改 | 签名不可伪造 |
| 版权证明 | 需第三方公证 | 双签名即证明 |
| 授权记录 | 可被伪造 | 签名可追溯 |
| 实施成本 | 低 | 低 |
| 维护成本 | 中 | 中 |

### 9.2 存证架构

```
┌─────────────────────────────────────────────────────────────┐
│              商用 Skills 数字存证架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  存证数据                                                   │
│  ├── Skill ID (唯一标识)                                   │
│  ├── Content Hash (SHA-256 内容哈希)                       │
│  ├── Author (创作者)                                       │
│  ├── Creation Time (创建时间戳)                            │
│  ├── Platform Signature (平台数字签名)                     │
│  └── Author Signature (作者数字签名)                       │
│                                                             │
│  存储方式                                                   │
│  └── Skills 完整内容存储于 OSS，签名存储于数据库            │
│                                                             │
│  验证流程                                                   │
│  1. 下载 Skills 内容                                       │
│  2. 计算本地 SHA-256 哈希                                  │
│  3. 验证平台签名（使用平台公钥）                            │
│  4. 验证作者签名（使用作者公钥）                            │
│  5. 一致则内容真实未被篡改                                 │
│                                                             │
│  分阶段实施                                                 │
│  ├── MVP: 中心化哈希存储                                   │
│  ├── 商用期: 数字签名存证                                   │
│  └── 企业期: 可选上链（以太坊 Layer 2）                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 存证数据结构

```json
{
  "skill_id": "skill_com_abc123",
  "content_hash": "sha256:3a7b8c9d1e2f...4b5m6n",
  "author": {
    "id": 12345,
    "username": "ACME_Technologies",
    "public_key": "0xabc123..."
  },
  "name": "Enterprise Payment Gateway Solution",
  "version": "2.1.0",
  "category": "tech",
  "created_at": 1737657600,
  "platform_signature": "0x9f8e7d6c5b4a...3210",
  "author_signature": "0x123456789abc...def0"
}
```

### 9.4 上链策略（分阶段）

| 阶段 | 存证方式 | 原因 |
|-------------|----------|------|
| **MVP 阶段** | 数据库哈希存储 | 验证需求低，成本低 |
| **商用验证期** | 数字签名存证 | 需要版权证明，成本可控 |
| **企业定制期** | 可选上链（以太坊 Layer 2） | 大客户需求，安全性最高 |

---

## 十、用户与权限系统

### 10.1 用户类型

| 用户类型 | 权限 | 升级条件 |
|----------|------|----------|
| **访客** | 浏览公开 Skills | - |
| **普通用户** | 下载免费 Skills、创建 Skills | 注册 + 邮箱验证 |
| **供应商** | 创建商用 Skills、设置价格 | 实名认证 + 审核 |
| **团队管理员** | 创建团队、管理成员 | 创建团队 |
| **平台管理员** | 全局管理权限 | 平台任命 |

### 10.2 登录方式

| 方式 | 说明 | 优先级 |
|------|------|--------|
| 邮箱注册 | 基础方式 | P0 |
| 手机号 | 国内用户 | P0 |
| GitHub OAuth | 开发者友好 | P1 |
| 企业微信 | 企业用户 | P2 |

### 10.3 权限矩阵

| 操作 | 访客 | 普通用户 | 供应商 | 管理员 |
|------|------|----------|--------|--------|
| 浏览免费 Skills | ✅ | ✅ | ✅ | ✅ |
| 下载免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建商用 Skills | ❌ | ❌ | ✅ | ✅ |
| 审核 Skills | ❌ | ❌ | ❌ | ✅ |
| 管理用户 | ❌ | ❌ | ❌ | ✅ |

### 10.4 API 密钥管理

| 密钥类型 | 用途 | 权限 |
|---------|------|------|
| `pk_live_xxx` | 生产环境 | 完整权限 |
| `pk_test_xxx` | 测试环境 | 测试权限 |
| `sk_live_xxx` | 服务端密钥 | 隐私操作权限 |

---

## 十一、运营与增长系统

### 11.1 成就系统

| 成就 | 条件 | 奖励 |
|------|------|------|
| **初出茅庐** | 创建第一个 Skill | 10 XP |
| **创作新星** | 创建 10 个 Skills | 100 XP + 50 Points |
| **优质创作者** | Skills 平均评分 > 4.5 | 200 XP + 100 Points |
| **开源先锋** | 免费 Skills 下载 > 1000 | 500 XP + 200 Points |
| **商业精英** | 商用销售额 > 10000 Points | 1000 XP + 500 Points |
| **社区领袖** | 获赞 > 1000 | 300 XP + 100 Points |
| **评论达人** | 发表评论 > 100 | 100 XP |
| **团队玩家** | 创建团队 > 5 个 | 200 XP |

### 11.2 排行榜

```
┌─────────────────────────────────────────────────────────────┐
│                        排行榜                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  热门 Skills 排行                                           │
│  ├── 今日热门                                               │
│  ├── 本周热门                                               │
│  ├── 本月热门                                               │
│  └── 历史热门                                               │
│                                                             │
│  优秀创作者排行                                             │
│  ├── 按作品数量                                             │
│  ├── 按下载量                                               │
│  └── 按销售额                                               │
│                                                             │
│  团队排行                                                   │
│  ├── 按成员数量                                             │
│  ├── 按项目数量                                             │
│  └── 按活跃度                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 11.3 邀请返利系统

| 行为 | 奖励 |
|------|------|
| 邀请新用户注册 | 50 AI Points |
| 被邀请人首次充值 | 额外 20% 奖励 |
| 被邀请人成为供应商 | 100 AI Points |

### 11.4 用户召回机制

```
┌─────────────────────────────────────────────────────────────┐
│                    用户召回策略                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  流失用户定义                                               │
│  └── 7 天未登录为轻度流失                                   │
│  └── 30 天未登录为重度流失                                  │
│                                                             │
│  召回策略                                                   │
│  ├── 邮件通知                                               │
│  │   ├── 新 Skills 推荐                                     │
│  │   ├── 专属优惠码                                         │
│  │   └── 社区动态                                           │
│  ├── 站内消息                                               │
│  └── 积分回归奖励                                           │
│      └── 回归即送 100 Points                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十二、开发路线图

### Phase 1: MVP 基础版 (0-3个月)

**目标：验证核心价值**

- [ ] 用户注册/登录
- [ ] Skills CRUD 基础功能
- [ ] 简单版本控制
- [ ] 基础权限管理
- [ ] AI 积分系统
- [ ] Skills 浏览与搜索
- [ ] 基础社区功能（收藏、评论）
- [ ] 成就系统

### Phase 2: 协作功能 (3-6个月)

**目标：支持团队协作**

- [ ] 团队创建与管理
- [ ] 团队成员管理
- [ ] Skills 共享与协作
- [ ] 权限细分控制
- [ ] 项目管理功能
- [ ] Skills 依赖管理

### Phase 3: AI 审核 (6-9个月)

**目标：自动化审核流程**

- [ ] L1 AI 自动审核
- [ ] L2 AI+人工复审
- [ ] L3 管理员终审
- [ ] 审核工作流引擎
- [ ] 审核配额管理
- [ ] 审核反馈机制

### Phase 4: 商用交易 (9-12个月)

**目标：商业化功能**

- [ ] 商用 Skills 创建
- [ ] AI Points 充值系统
- [ ] 订单与支付
- [ ] 授权管理系统
- [ ] 供应商工作台
- [ ] 数字签名存证

### Phase 5: 运营增长 (12-15个月)

**目标：用户增长与留存**

- [ ] 推荐系统
- [ ] 排行榜
- [ ] 邀请返利
- [ ] 用户召回
- [ ] 数据分析看板
- [ ] 运营活动系统

### Phase 6: 多领域扩展 (15-18个月)

**目标：支持全领域协作**

- [ ] 产品 Skills 模板
- [ ] 设计 Skills 模板
- [ ] 市场 Skills 模板
- [ ] 运营 Skills 模板
- [ ] 跨领域引用系统

### Phase 7: 生态完善 (18个月+)

**目标：构建生态**

- [ ] SDK 与 API 完善
- [ ] 开发者社区
- [ ] 移动端 APP
- [ ] 国际化支持
- [ ] 可选区块链上链

---

## 十三、安全设计

### 13.1 数据安全

| 措施 | 说明 |
|------|------|
| 传输加密 | HTTPS/TLS 1.3 |
| 存储加密 | 敏感数据 AES-256 加密 |
| 密码安全 | bcrypt 哈希 + 盐值 |
| SQL 防护 | 参数化查询，防止注入 |
| 密钥管理 | 分离 publishable_key 和 secret_key |

### 13.2 访问控制

| 措施 | 说明 |
|------|------|
| 会话管理 | JWT Token，自动续期 |
| 请求签名 | 敏感操作需要 HMAC-SHA256 签名 |
| 限流保护 | API 限流，防止滥用 |
| IP 白名单 | 企业用户可选 |
| 操作审计 | 关键操作日志记录 |

### 13.3 内容安全

| 措施 | 说明 |
|------|------|
| AI 审核 | 上架前审核 |
| 人工复核 | 争议内容人工审核 |
| 用户举报 | 违规内容举报机制 |
| 定期巡查 | 定期检查存量内容 |
| 内容过滤 | 敏感词过滤 |

### 13.4 交易安全

| 措施 | 说明 |
|------|------|
| 积分锁 | 交易中锁定积分 |
| 交易记录 | 完整交易日志 |
| 退款机制 | 争议可退款 |
| 数字签名 | 商用授权签名存证 |
| Webhook 验证 | 回调签名验证 |

---

## 十四、基础设施与部署

### 14.1 监控与告警

```python
# ============================================
# Prometheus 指标定义
# ============================================

from prometheus_client import Counter, Histogram, Gauge

# 请求计数
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 请求延迟
request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# 在线用户
online_users = Gauge(
    'online_users',
    'Number of online users'
)

# Skills 统计
skills_published = Gauge(
    'skills_published_total',
    'Total published skills',
    ['category', 'type']
)

# 商用交易
transactions_total = Counter(
    'transactions_total',
    'Total transactions',
    ['type']
)

revenue_total = Gauge(
    'revenue_total',
    'Total revenue in AI Points'
)

# ============================================
# Grafana 看板配置示例
# ============================================

dashboard = {
    "title": "SillyMD Platform Metrics",
    "panels": [
        {
            "title": "Request Rate",
            "targets": [{
                "expr": "rate(http_requests_total[5m])"
            }]
        },
        {
            "title": "P95 Latency",
            "targets": [{
                "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
            }]
        },
        {
            "title": "Online Users",
            "targets": [{
                "expr": "online_users"
            }]
        },
        {
            "title": "Revenue (24h)",
            "targets": [{
                "expr": "increase(revenue_total[24h])"
            }]
        }
    ]
}
```

### 14.2 日志聚合（ELK Stack）

```yaml
# ============================================
# Filebeat 配置
# ============================================

filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata:

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "filebeat-sillymd-%{+yyyy.MM.dd"

setup.kibana:
  host: "kibana:5601"

# ============================================
# 日志格式规范（JSON）
# ============================================

import json
from datetime import datetime

class StructuredLogger:
    """结构化日志"""

    @staticmethod
    def log(level: str, message: str, **context):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "context": context
        }
        print(json.dumps(log_entry))

# 使用示例
StructuredLogger.log(
    level="INFO",
    message="Skill published",
    skill_id="skill_123",
    user_id=456,
    category="tech"
)
```

### 14.3 备份与恢复

```bash
# ============================================
# PostgreSQL 备份脚本
# ============================================

#!/bin/bash

# 全量备份（每天凌晨 2 点）
0 2 * * * pg_dump -U postgres -d sillymd | gzip > /backup/sillymd-full-$(date +\%Y\%m\%d).sql.gz

# 增量备份（WAL 归档）
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
restore_command = 'cp /backup/wal/%f %p'

# ============================================
# OSS 备份策略
# ============================================

# 使用 rclone 同步到 OSS
rclone sync /var/data sillymd-oss:backup \
    --backup-dir sillymd-oss:backup-archive/$(date +%Y%m%d) \
    --max-age 30d

# ============================================
# 恢复演练
# ============================================

# 每月演练一次
0 0 1 * * /scripts/restore_drill.sh
```

---

**文档版本**: v13.0
**最后更新**: 2026-02-01
**维护团队**: SillyMD Team

---

*"承认自己有时候挺傻的，这是智慧的开始。"*
