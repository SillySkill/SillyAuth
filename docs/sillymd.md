# SillyMD Skills 在线平台 - 完整设计文档 v14.0

> **平台愿景**：打造专业的 AI Skills 托管与协作平台，支持 Skills 资产化管理、多领域团队协作、商用授权交易。

---

## 目录

1. [平台概述](#一平台概述)
2. [技术架构](#二技术架构)
3. [核心功能模块](#三核心功能模块)
4. [Skills 分类体系](#四skills-分类体系)
5. [AI 审核系统](#五ai-审核系统)
6. [多领域协作系统](#六多领域协作系统)
7. [商用授权与交易系统](#七商用授权与交易系统)
8. [数字存证架构](#八数字存证架构)
9. [用户与权限系统](#九用户与权限系统)
10. [运营与增长系统](#十运营与增长系统)
11. [开发路线图](#十一开发路线图)
12. [安全设计](#十二安全设计)
13. [基础设施与部署](#十三基础设施与部署)
14. [快速开始](#十四快速开始)
15. [前端设计](#十五前端设计)
16. [Skills 编辑器](#十六skills-编辑器)
17. [资源下载中心](#十七资源下载中心)
18. [交流学习社区](#十八交流学习社区)
19. [管理后台系统](#十九管理后台系统)

---

## 一、平台概述

### 1.1 基本信息

| 项目 | 内容 |
|------|------|
| 网站域名 | sillymd.com（已完成备案） |
| 团队协作域名 | sillymd.com/组织名 |
| 服务器地址 | 47.96.133.238 |
| SSH私钥路径 | .ignore/silly.pem |
| 平台定位 | AI Skills 托管中心 + 多领域协作网络 + 商用授权市场 |

### 1.2 名字内涵

- **"挺傻的"**：代表对 AI 现状的诚实认知，有时候 "AI，挺傻的"
- **人生态度**：容纳自身不足，持续迭代进化
- **技术理念**：承认 AI 局限，通过 Skills 补全能力边界

### 1.3 核心定义

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

### 1.4 核心价值

| 价值 | 说明 |
|------|------|
| **资产化** | 将 Skills 从"文档"升级为"数字资产" |
| **可授权** | 商用 Skills 支持授权交易，资产可流转 |
| **可验证** | 商用 Skills 具有数字签名指纹，确保内容真实 |
| **标准化** | 统一 Skills 格式，跨团队、跨领域协作无障碍 |
| **安全可靠** | 多层安全机制，数据加密存储 |

### 1.5 Skills 分类

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills 分类体系                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  按收费分类                                                 │
│  ├── 免费Skills (Free Skills)       - 开源共享              │
│  └── 商用Skills (Commercial Skills) - 付费授权              │
│                                                             │
│  按领域分类                                                 │
│  ├── 技术Skills (Tech Skills)       - 代码、架构、工具      │
│  ├── 产品Skills (Product Skills)    - 需求、规划、研究      │
│  ├── 设计Skills (Design Skills)     - UI/UX、视觉、品牌     │
│  ├── 市场Skills (Marketing Skills)  - 推广、策略、分析      │
│  └── 运营Skills (Ops Skills)        - 流程、增长、数据      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、技术架构

### 2.1 技术栈选型

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
| 存储 | 火山引擎 TOS | Skills 文件存储 | 自定义域名 resource.sillymd.com |
| CDN | 火山引擎 CDN | 静态资源加速 | TOS 集成 CDN |
| 追踪 | OpenTelemetry + Jaeger | 分布式追踪 | 排查问题 |
| 监控 | Prometheus + Grafana | 监控告警 | - |

### 2.2 系统架构图

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

### 2.3 SDK 设计

#### 2.3.1 NPM 包

```bash
# 核心 SDK
npm install @sillymd/sdk

# MCP Server (用于 Claude Code)
npm install @sillymd/mcp-server

# CLI 工具
npm install -g @sillymd/cli
```

#### 2.3.2 SDK 使用示例

```javascript
import { SillyClient } from '@sillymd/sdk';

const client = new SillyClient({
  apiKey: process.env.SILLY_API_KEY,
  endpoint: 'https://api.sillymd.com'
});

// 获取 Skill
const skill = await client.skills.get('skill-id');

// 执行 Skill
const result = await client.skills.execute('skill-id', {
  input: '用户输入',
  context: {}
});

// 列出 Skills
const skills = await client.skills.list({
  category: 'tech',
  type: 'free',
  limit: 10
});

// 验证商用授权
const hasAccess = await client.licenses.verify('skill-id', {
  licenseKey: 'user-license-key'
});
```

### 2.4 数据库设计

#### 2.4.1 PostgreSQL 类型定义

```sql
-- ============================================
-- 枚举类型定义
-- ============================================

CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');
CREATE TYPE vendor_level AS ENUM ('normal', 'premium', 'gold');
CREATE TYPE skill_category AS ENUM ('tech', 'product', 'design', 'marketing', 'ops');
CREATE TYPE skill_type AS ENUM ('free', 'commercial');
CREATE TYPE skill_status AS ENUM ('draft', 'reviewing', 'approved', 'rejected');
CREATE TYPE team_role AS ENUM ('owner', 'admin', 'member', 'viewer');
CREATE TYPE license_type AS ENUM ('personal', 'team', 'enterprise');
CREATE TYPE transaction_type AS ENUM ('recharge', 'purchase', 'earning', 'refund', 'withdraw');
CREATE TYPE notification_type AS ENUM ('system', 'skill_update', 'comment', 'license', 'achievement', 'team');

-- ============================================
-- 用户表
-- ============================================
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

-- ============================================
-- Skills 表
-- ============================================
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

    -- 统计字段
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

-- ============================================
-- Skills 版本表
-- ============================================
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

-- ============================================
-- Skills 依赖关系表
-- ============================================
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

-- ============================================
-- 标签表
-- ============================================
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_tags (
    skill_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (skill_id, tag_id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- ============================================
-- Skills 收藏表
-- ============================================
CREATE TABLE skill_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (user_id, skill_id)
);

-- ============================================
-- Skills 评论表
-- ============================================
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
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 团队成员表
-- ============================================
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

-- ============================================
-- 团队项目表
-- ============================================
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

-- ============================================
-- 项目 Skills 关联表
-- ============================================
CREATE TABLE project_skills (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    role TEXT DEFAULT 'other',
    order_index INT DEFAULT 0,
    added_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (project_id, skill_id)
);

-- ============================================
-- 授权记录表
-- ============================================
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

-- ============================================
-- 积分交易表
-- ============================================
CREATE TABLE point_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    type transaction_type NOT NULL,
    balance_after INT NOT NULL,
    related_id BIGINT,
    description VARCHAR(500),
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 审核记录表
-- ============================================
CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    reviewer_id BIGINT NOT NULL,
    stage TEXT NOT NULL,
    result TEXT NOT NULL,
    comments TEXT,
    ai_model VARCHAR(50),
    ai_confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- ============================================
-- 成就表
-- ============================================
CREATE TABLE achievements (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    category TEXT NOT NULL,
    xp_reward INT DEFAULT 0,
    points_reward INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 用户成就关联表
-- ============================================
CREATE TABLE user_achievements (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    achievement_id BIGINT NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE (user_id, achievement_id)
);

-- ============================================
-- 操作日志表
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
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 消息通知表
-- ============================================
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

-- ============================================
-- 邀请记录表
-- ============================================
CREATE TABLE invitations (
    id BIGSERIAL PRIMARY KEY,
    inviter_id BIGINT NOT NULL,
    invitee_email VARCHAR(100) NOT NULL,
    invite_code VARCHAR(20) UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending',
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
```

#### 2.4.2 缓存策略设计

```python
# ============================================
# Redis 缓存策略
# ============================================

from redis.cluster import RedisCluster
from typing import Optional, Any
import json

class CacheManager:
    """多层级缓存管理器"""

    def __init__(self):
        self.redis_cluster = RedisCluster(
            startup_nodes=[
                {"host": "redis-node-1", "port": 7000},
                {"host": "redis-node-2", "port": 7001},
                {"host": "redis-node-3", "port": 7002},
            ],
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        data = await self.redis_cluster.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        await self.redis_cluster.setex(
            key,
            ttl,
            json.dumps(value)
        )

    @staticmethod
    def make_key(prefix: str, *args, **kwargs) -> str:
        """生成标准化缓存键"""
        key_parts = [prefix]
        key_parts.extend(str(a) for a in args)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend(f"{k}={v}" for k, v in sorted_kwargs)
        return ":".join(key_parts)

    async def invalidate_pattern(self, pattern: str):
        """批量失效缓存"""
        keys = await self.redis_cluster.keys(pattern)
        if keys:
            await self.redis_cluster.delete(*keys)

# ============================================
# FastAPI 缓存装饰器
# ============================================

from functools import wraps

def cache_response(prefix: str, ttl: int = 300):
    """响应缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = CacheManager.make_key(prefix, *args, **kwargs)
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

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
            await cache_manager.invalidate_pattern(pattern)

    @staticmethod
    async def invalidate_user(user_id: int):
        """用户相关缓存失效"""
        patterns = [
            f"user:profile:{user_id}",
            f"user:skills:{user_id}",
            f"user:stats:{user_id}"
        ]
        for pattern in patterns:
            await cache_manager.invalidate_pattern(pattern)
```

### 2.5 Meilisearch 集成

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
        self._setup_index()

    def _setup_index(self):
        """配置搜索索引"""
        index_settings = {
            'searchableAttributes': [
                'name', 'description', 'tags', 'author_name'
            ],
            'filterableAttributes': [
                'category', 'type', 'rating_avg'
            ],
            'sortableAttributes': [
                'rating_avg', 'download_count', 'created_at'
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
                'the', 'a', 'an', 'and', 'or',
                '的', '了', '是', '在', '和'
            ],
            'synonyms': {
                'ai': ['artificial intelligence', '人工智能'],
                'api': ['interface', '接口']
            }
        }
        self.client.index('skills').update_settings(index_settings)

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
```

### 2.6 WebSocket 实时通知

```python
# ============================================
# WebSocket 实时通知系统
# ============================================

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
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
                self.disconnect(user_id)

    async def broadcast(self, notification: Dict, exclude: int = None):
        """广播通知"""
        for user_id, websocket in list(self.active_connections.items()):
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

from fastapi import APIRouter, WebSocket, Depends

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
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_text("pong")

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
# 通知类型
# ============================================

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

async def notify_license_purchased(vendor_id: int, skill_name: str, buyer: str, amount: int):
    """售出授权通知"""
    await push_notification(
        user_id=vendor_id,
        notification_type="license",
        title=f"售出授权！+{amount} AI Points",
        content=f"{buyer} 购买了您的 Skill 《{skill_name}》的授权。",
        link_url=f"/dashboard/sales"
    )

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

### 2.7 限流与降级策略

```python
# ============================================
# 限流策略（令牌桶算法）
# ============================================

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/skills")
@limiter.limit("60/minute")
async def list_skills(request: Request):
    """获取 Skills 列表（每分钟 60 次）"""
    pass

@app.post("/api/v1/skills")
@limiter.limit("10/minute")
async def create_skill(request: Request):
    """创建 Skill（每分钟 10 次）"""
    pass

@app.get("/api/v1/search")
@limiter.limit("30/minute")
async def search_skills(request: Request):
    """搜索 Skills（每分钟 30 次）"""
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
        return await db.query(Skill).filter(
            Skill.name.ilike(f"%{query}%")
        ).limit(10).all()

    @staticmethod
    async def recommendation_fallback(user_id: int):
        """推荐降级：返回热门 Skills"""
        return await db.query(Skill).order_by(
            Skill.view_count.desc()
        ).limit(10).all()

    @staticmethod
    async def ai_review_fallback(skill_data: dict):
        """AI 审核降级：标记为人工审核"""
        return await create_review_ticket(
            skill_id=skill_data['id'],
            stage='L2',
            auto_assigned=True
        )
```

### 2.8 API 版本控制

```python
# ============================================
# API 版本控制
# ============================================

from fastapi import APIRouter

# 版本化路由
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/skills/{skill_id}")
async def get_skill_v1(skill_id: str):
    """v1 实现"""
    return await get_skill_basic(skill_id)

@v2_router.get("/skills/{skill_id}")
async def get_skill_v2(skill_id: str, include_details: bool = False):
    """v2 实现（向后兼容）"""
    skill = await get_skill_basic(skill_id)
    if include_details:
        skill['details'] = await get_skill_details(skill_id)
    return skill

# 版本弃用
@app.get("/api/v1/legacy/{skill_id}", deprecated=True)
async def deprecated_endpoint(skill_id: str):
    """返回警告头"""
    return {
        "skill": skill_data,
        "_warning": "This API is deprecated. Please use /api/v2/skills/{id}"
    }
```

### 2.9 RBAC 权限控制

```python
# ============================================
# 基于 Casbin 的 RBAC 实现
# ============================================

from casbin import Enforcer
from fastapi import Depends, HTTPException

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

enforcer = Enforcer("model.conf", "policy.csv")

async def check_permission(
    user: User = Depends(get_current_user),
    obj: str = None,
    act: str = None
):
    """权限检查中间件"""
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

# 使用示例
@app.post("/api/v1/skills")
async def create_skill(
    skill_data: SkillCreate,
    authorized: bool = Depends(check_permission)
):
    """创建 Skill（需要 vendor 权限）"""
    pass
```

### 2.10 分布式追踪

```python
# ============================================
# OpenTelemetry 集成
# ============================================

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

# ============================================
# 自定义 span
# ============================================

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_skill(skill_id: str):
    """处理 Skill（带追踪）"""
    with tracer.start_as_current_span("process_skill"):
        with tracer.start_as_current_span("fetch_skill"):
            skill = await get_skill(skill_id)

        with tracer.start_as_current_span("validate_skill"):
            validate(skill)

        with tracer.start_as_current_span("index_skill"):
            await search_service.index_skill(skill)
```

---

## 三、核心功能模块

### 3.1 Skills 托管中心

#### 3.1.1 免费 Skills 区域

| 特性 | 说明 |
|------|------|
| 内容类型 | AI 使用技巧、最佳实践、开源工具 |
| 访问权限 | 公开，所有用户可查看下载 |
| 编辑权限 | 作者可编辑，他人可 Fork |
| 许可证 | MIT / Apache 2.0 / CC BY |
| 社区功能 | 收藏、评论、评分 |

#### 3.1.2 商用 Skills 区域

| 特性 | 说明 |
|------|------|
| 内容类型 | 行业解决方案、企业级应用、专业工具 |
| 访问权限 | 需购买授权或订阅 |
| 存储方式 | OSS 存储 + 数字签名存证 |
| 授权类型 | 个人授权 / 团队授权 / 企业授权 |
| 授权验证 | SDK 验证 + 在线验证 + 证书验证 |

### 3.2 版本管理

| 功能 | 说明 |
|------|------|
| Git 风格版本控制 | 版本历史、分支、回滚 |
| 版本对比 | 可视化展示版本间差异 |
| 版本标签 | 支持为重要版本打标签 |
| 自动备份 | 每次修改自动备份 |
| 语义化版本 | 支持 SemVer 依赖约束 |

### 3.3 搜索与发现

| 搜索维度 | 说明 | 优先级 |
|----------|------|--------|
| 关键词搜索 | Meilisearch 全文检索 | P0 |
| 分类筛选 | 按领域/类型筛选 | P0 |
| 标签筛选 | 按自定义标签筛选 | P0 |
| 智能推荐 | AI 个性化推荐 | P1 |
| 排序方式 | 热度/评分/最新/价格 | P0 |
| 相似 Skills | 基于标签和内容相似度 | P1 |
| 搜索建议 | 自动补全 + 热门搜索 | P1 |

### 3.4 Skills 依赖管理

```yaml
# 支持 SemVer 版本约束
skill:
  id: "tech-auth-api"
  name: "用户认证 API"
  dependencies:
    - skill_id: "tech-database-base"
      version: ">=1.2.0"
      type: "required"
    - skill_id: "tech-cache"
      version: "~1.5.0"
      type: "optional"

# 依赖解析策略
resolution_strategy:
  - highest_compatible  # 选择最高兼容版本
  - lowest_compatible   # 选择最低兼容版本（默认）
```

---

## 四、Skills 分类体系

### 4.1 按领域分类

#### 4.1.1 技术 Skills (Tech Skills)

| 子类 | 示例 |
|------|------|
| 开发工具 | 代码生成器、调试工具、性能分析 |
| 架构设计 | 系统架构、微服务、API 设计 |
| 自动化 | CI/CD、脚本、工作流自动化 |
| 数据处理 | ETL、数据清洗、数据可视化 |

#### 4.1.2 产品 Skills (Product Skills)

| 子类 | 示例 |
|------|------|
| 需求管理 | PRD 模板、需求分析框架 |
| 用户研究 | 用户画像、调研方法 |
| 产品规划 | 路线图、OKR、优先级管理 |
| 数据分析 | 埋点方案、漏斗分析 |

#### 4.1.3 设计 Skills (Design Skills)

| 子类 | 示例 |
|------|------|
| UI 设计 | 组件库、设计规范、配色方案 |
| UX 设计 | 交互模式、用户旅程、可用性测试 |
| 品牌设计 | Logo 规范、品牌指南、VI 系统 |

#### 4.1.4 市场 Skills (Marketing Skills)

| 子类 | 示例 |
|------|------|
| 内容营销 | 文案模板、内容规划 |
| 社交媒体 | 运营策略、涨粉技巧 |
| 广告投放 | 投放策略、素材模板 |
| 数据分析 | 获客分析、转化优化 |

#### 4.1.5 运营 Skills (Operations Skills)

| 子类 | 示例 |
|------|------|
| 用户运营 | 用户分层、留存策略 |
| 活动运营 | 活动策划、执行流程 |
| 内容运营 | 内容规划、发布策略 |

### 4.2 按授权类型分类

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

## 五、AI 审核系统

### 5.1 审核目的

所有上架的 Skills 必须通过 AI 审核，确保：
- **合规性**：符合法律法规，无违法违规内容
- **安全性**：无恶意代码、无病毒木马
- **准确性**：内容真实有效，无虚假宣传
- **格式规范**：符合 Skills 格式标准

### 5.2 审核流程

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

### 5.3 审核维度

| 维度 | 技术 Skills | 产品 Skills | 设计 Skills | 市场/运营 Skills |
|------|-------------|-------------|-------------|------------------|
| 法律合规 | ✅ | ✅ | ✅ | ✅ |
| 内容安全 | ✅ | ✅ | ✅ | ✅ |
| 格式规范 | ✅ | ✅ | ✅ | ✅ |
| 专业准确 | ✅ | ✅ | ✅ | ✅ |
| 商业价值 | ✅ | ✅ | ✅ | ✅ |
| 原创性检测 | ✅ | ✅ | ✅ | ✅ |

### 5.4 审核配额与定价

| 用户类型 | 免费审核额度 | 超额费用 |
|---------|-------------|---------|
| 普通用户 | 3 次/月 | 10 AI Points/次 |
| 供应商 | 20 次/月 | 5 AI Points/次 |
| 金牌供应商 | 100 次/月 | 免费 |

### 5.5 审核结果处理

| 结果 | 说明 | 处理方式 |
|------|------|----------|
| **通过** | 符合所有标准 | 自动上架 |
| **需修正** | 存在小问题，可修正 | 返回用户修正后重新提交 |
| **驳回** | 存在重大问题 | 拒绝上架，说明原因 |

---

## 六、多领域协作系统

### 6.1 协作理念

**核心理念**：将 Skills 标准化扩展到所有工作领域。

**SillyMD 的解决方案**：所有团队都用 Skills 标准来管理和协作。

### 6.2 团队组织结构

```
团队域名结构：sillymd.com/{team_slug}

示例：
├── sillymd.com/acme-tech          → ACME 科技公司
│   └── sillymd.com/acme-tech/payment-system  → 项目：支付系统
├── sillymd.com/design-studio      → 某设计工作室
├── sillymd.com/marketing-agency   → 某营销公司
└── sillymd.com/startup-abc        → 某创业团队
```

### 6.3 团队角色

| 角色 | 权限 | 说明 |
|------|------|------|
| **Owner** | 完全控制 | 团队创建者，可解散团队 |
| **Admin** | 管理 | 管理成员、设置、项目 |
| **Member** | 编辑 | 创建/编辑 Skills，参与项目 |
| **Viewer** | 查看 | 只读访问团队内容 |

### 6.4 项目协作模式

```
┌─────────────────────────────────────────────────────────────┐
│                    项目协作模式                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  项目启动                                                   │
│    ├── 产品经理创建 "产品需求 Skill"                        │
│    ├── 设计师基于需求创建 "设计规范 Skill"                  │
│    ├── 开发者基于规范创建 "技术实现 Skill"                  │
│    └── 运营创建 "推广方案 Skill"                            │
│                                                             │
│  项目迭代                                                   │
│    ├── 每个 Skill 独立版本控制                              │
│    ├── Skill 之间通过依赖关系自动关联                       │
│    ├── 上游 Skill 变更通知下游维护者                        │
│    └── 形成完整的知识沉淀                                   │
│                                                             │
│  项目交付                                                   │
│    ├── 所有 Skills 形成项目资产                             │
│    ├── 可导出为完整项目文档                                 │
│    ├── 可打包发布为商用 Skill                               │
│    └── 可复用至新项目                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.5 Skills 引用系统

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

## 七、商用授权与交易系统

### 7.1 AI 积分体系

**AI Points (AI 积分)** 是平台内的虚拟积分单位。

| 获取方式 | 说明 |
|----------|------|
| 充值购买 | 支持支付宝、微信、银行卡 |
| 销售收益 | 出售商用 Skills 获得 |
| 活动奖励 | 平台活动、推广奖励 |
| 贡献奖励 | 贡献优质免费 Skills |
| 邀请奖励 | 邀请新用户注册 |
| 成就奖励 | 解锁成就获得 |

### 7.2 商用 Skills 定价策略

| Skills 类型 | 建议价格区间 | 说明 |
|-------------|--------------|------|
| 基础工具类 | 100-500 AI Points | 通用脚本、模板 |
| 专业应用类 | 500-2000 AI Points | 行业解决方案 |
| 企业级方案 | 2000-10000 AI Points | 完整系统、复杂集成 |
| 独家定制类 | 10000+ AI Points | 高度定制化 |

### 7.3 授权类型与价格

| 授权类型 | 价格倍数 | 使用范围 | 说明 |
|----------|----------|----------|------|
| **个人授权** | 1x | 单用户使用 | 仅供个人使用 |
| **团队授权** | 3x | 团队内共享 (最多 10 人) | 同一团队内使用 |
| **企业授权** | 10x | 企业内使用 (无人数限制) | 整个企业使用 |

### 7.4 授权验证机制

#### SDK 验证

```javascript
// SDK 自动验证授权
const client = new SillyClient({
  apiKey: process.env.SILLY_API_KEY,
  licenseKey: process.env.SILLY_LICENSE_KEY
});

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
  signature: "0xabc123...",
  public_key: "0xdef456..."
};

// 本地验证签名
function verifyLicense(certificate) {
  const data = `${certificate.license_id}:${certificate.skill_id}:${certificate.user_id}:${certificate.license_type}:${certificate.expires_at}`;
  return verifySignature(data, certificate.signature, certificate.public_key);
}
```

### 7.5 交易流程

```
┌─────────────────────────────────────────────────────────────┐
│                    交易流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  买家                                                      │
│    ├── 浏览商用 Skills                                     │
│    ├── 查看授权类型和价格                                  │
│    ├── 选择授权类型 (个人/团队/企业)                        │
│    ├── 确认订单，扣除 AI Points                            │
│    └── 获得授权许可 + 授权密钥                             │
│                                                             │
│  平台                                                      │
│    ├── 记录交易                                            │
│    ├── 生成授权密钥                                        │
│    ├── 平台抽成 (15-20%)                                   │
│    └── 供应商到账 (80-85%)                                 │
│                                                             │
│  供应商                                                    │
│    ├── 查看销售数据                                        │
│    ├── AI Points 余额增加                                  │
│    ├── 销售通知推送                                        │
│    └── 可申请提现                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.6 平台抽成规则

| 供应商等级 | 累计销售额 | 平台抽成 | 供应商收益 | 特权 |
|------------|--------|----------|------------|------|
| 普通供应商 | - | 20% | 80% | 基础功能 |
| 优质供应商 | ≥ 5,000 Points | 15% | 85% | 更多审核额度 |
| 金牌供应商 | ≥ 50,000 Points | 10% | 90% | 优先推荐、专属客服 |

### 7.7 提现规则

| 规则项 | 说明 |
|--------|------|
| 最低提现 | 500 AI Points |
| 提现周期 | 每周一处理 |
| 提现方式 | 支付宝、银行转账 |
| 汇率 | 100 AI Points = 10 元人民币 |
| 手续费 | 免费（平台承担） |

---

## 八、数字存证架构

### 8.1 为什么商用 Skills 需要数字存证

| 需求 | 传统存储 | 数字签名存证 |
|------|----------|-------------|
| 数据完整性 | 中心化可篡改 | 签名不可伪造 |
| 版权证明 | 需第三方公证 | 双签名即证明 |
| 授权记录 | 可被伪造 | 签名可追溯 |
| 实施成本 | 低 | 低 |
| 维护成本 | 中 | 中 |

### 8.2 存证架构

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

### 8.3 存证数据结构

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

### 8.4 上链策略（分阶段）

| 阶段 | 存证方式 | 原因 |
|-------------|----------|------|
| **MVP 阶段** | 数据库哈希存储 | 验证需求低，成本低 |
| **商用验证期** | 数字签名存证 | 需要版权证明，成本可控 |
| **企业定制期** | 可选上链（以太坊 Layer 2） | 大客户需求，安全性最高 |

### 8.5 为什么暂不使用区块链

| 考虑因素 | 分析 |
|---------|------|
| **成本** | 链上存储成本高，初期不划算 |
| **复杂度** | 增加系统复杂度，维护成本高 |
| **用户需求** | 初期用户对区块链需求不强 |
| **替代方案** | 数字签名可满足大部分存证需求 |

**未来升级路径：**
```
数字签名存证
    ↓ (企业客户需求)
以太坊 Layer 2 (Arbitrum/Optimism)
    ↓ (合规需求)
Hyperledger Fabric (联盟链)
```

---

## 九、用户与权限系统

### 9.1 用户类型

| 用户类型 | 权限 | 升级条件 |
|----------|------|----------|
| **访客** | 浏览公开 Skills | - |
| **普通用户** | 下载免费 Skills、创建 Skills | 注册 + 邮箱验证 |
| **供应商** | 创建商用 Skills、设置价格 | 实名认证 + 审核 |
| **团队管理员** | 创建团队、管理成员 | 创建团队 |
| **平台管理员** | 全局管理权限 | 平台任命 |

### 9.2 登录方式

| 方式 | 说明 | 优先级 |
|------|------|--------|
| 邮箱注册 | 基础方式 | P0 |
| 手机号 | 国内用户 | P0 |
| GitHub OAuth | 开发者友好 | P1 |
| 企业微信 | 企业用户 | P2 |

### 9.3 权限矩阵

| 操作 | 访客 | 普通用户 | 供应商 | 管理员 |
|------|------|----------|--------|--------|
| 浏览免费 Skills | ✅ | ✅ | ✅ | ✅ |
| 下载免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建商用 Skills | ❌ | ❌ | ✅ | ✅ |
| 审核 Skills | ❌ | ❌ | ❌ | ✅ |
| 管理用户 | ❌ | ❌ | ❌ | ✅ |

### 9.4 API 密钥管理

| 密钥类型 | 用途 | 权限 |
|---------|------|------|
| `pk_live_xxx` | 生产环境 | 完整权限 |
| `pk_test_xxx` | 测试环境 | 测试权限 |
| `sk_live_xxx` | 服务端密钥 | 隐私操作权限 |

---

## 十、运营与增长系统

### 10.1 成就系统

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

### 10.2 排行榜

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

### 10.3 推荐系统

```python
# 推荐算法
def recommend_skills(user_id: int, limit: int = 10) -> List[str]:
    score = {}

    # 1. 协同过滤 (40%)
    similar_users = get_similar_users(user_id, top_n=20)
    for user in similar_users:
        for skill in user.favorited_skills:
            score[skill.id] = score.get(skill.id, 0) + 40

    # 2. 内容匹配 (30%)
    user_tags = get_user_interest_tags(user_id)
    for skill in all_active_skills:
        overlap = len(set(skill.tags) & set(user_tags))
        score[skill.id] = score.get(skill.id, 0) + overlap * 30

    # 3. 热度加成 (20%)
    trending = get_trending_skills(period='7d')
    for skill in trending:
        score[skill.id] = score.get(skill.id, 0) + 20

    # 4. 新手优惠 (10%)
    if is_new_user(user_id):
        free_skills = get_free_skills()
        for skill in free_skills:
            score[skill.id] = score.get(skill.id, 0) + 10

    # 排序并返回
    ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return [skill_id for skill_id, _ in ranked[:limit]]
```

### 10.4 邀请返利系统

| 行为 | 奖励 |
|------|------|
| 邀请新用户注册 | 50 AI Points |
| 被邀请人首次充值 | 额外 20% 奖励 |
| 被邀请人成为供应商 | 100 AI Points |

### 10.5 用户召回机制

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

### 10.6 数据统计与分析

```
用户活跃度分析
├── 日活 (DAU)
├── 周活 (WAU)
├── 月活 (MAU)
└── 留存率
    ├── 次日留存
    ├── 7日留存
    └── 30日留存

Skills 数据分析
├── 浏览量排行
├── 下载量排行
├── 转化率分析
└── 评分分析

商业数据分析
├── 销售额统计
├── ARPU (每用户平均收入)
├── 付费转化率
└── 复购率
```

---

## 十一、开发路线图

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

## 十二、安全设计

### 12.1 数据安全

| 措施 | 说明 |
|------|------|
| 传输加密 | HTTPS/TLS 1.3 |
| 存储加密 | 敏感数据 AES-256 加密 |
| 密码安全 | bcrypt 哈希 + 盐值 |
| SQL 防护 | 参数化查询，防止注入 |
| 密钥管理 | 分离 publishable_key 和 secret_key |

### 12.2 访问控制

| 措施 | 说明 |
|------|------|
| 会话管理 | JWT Token，自动续期 |
| 请求签名 | 敏感操作需要 HMAC-SHA256 签名 |
| 限流保护 | API 限流，防止滥用 |
| IP 白名单 | 企业用户可选 |
| 操作审计 | 关键操作日志记录 |

### 12.3 内容安全

| 措施 | 说明 |
|------|------|
| AI 审核 | 上架前审核 |
| 人工复核 | 争议内容人工审核 |
| 用户举报 | 违规内容举报机制 |
| 定期巡查 | 定期检查存量内容 |
| 内容过滤 | 敏感词过滤 |

### 12.4 交易安全

| 措施 | 说明 |
|------|------|
| 积分锁 | 交易中锁定积分 |
| 交易记录 | 完整交易日志 |
| 退款机制 | 争议可退款 |
| 数字签名 | 商用授权签名存证 |
| Webhook 验证 | 回调签名验证 |

### 12.5 数据备份与灾难恢复

```
备份策略：
├── 数据库备份
│   ├── 每日全量备份（保留 30 天）
│   ├── 每小时增量备份（保留 7 天）
│   └── 异地灾备（火山引擎 TOS）
├── 文件备份
│   └── TOS 开启版本控制
└── 恢复演练
    └── 每月进行恢复演练
```

---

## 十三、基础设施与部署

### 13.1 容器化部署（仅本地开发参考）

> **生产环境说明**: 实际部署使用 systemd 服务，非容器化。参见下方"实际部署方式"。

```dockerfile
# Dockerfile (本地开发用)
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **注**: 生产环境通过 `production.py` 启动，使用多进程模式：`python production.py`

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/sillymd
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=sillymd

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 13.2 CI/CD 流水线

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          # 部署脚本
```

### 13.3 监控与日志

| 组件 | 用途 | 优先级 |
|------|------|--------|
| Prometheus | 指标收集 | P1 |
| Grafana | 监控看板 | P1 |
| Sentry | 错误追踪 | P0 |
| ELK Stack | 日志分析 | P1 |

#### Prometheus 指标定义

```python
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
    'HTTP request latency'
)

# 在线用户
online_users = Gauge('online_users', 'Number of online users')

# 收入统计
revenue_total = Gauge('revenue_total', 'Total revenue in AI Points')

# Skills 统计
skills_published = Gauge(
    'skills_published_total',
    'Total published skills',
    ['category', 'type']
)
```

### 13.4 CDN 与静态资源

```
静态资源加速：
├── 前端资源 → CDN 加速
├── Skills 文件 → OSS + CDN
└── 图片资源 → OSS + CDN
```

### 13.5 备份与恢复

```bash
# PostgreSQL 备份脚本（每天凌晨 2 点）
0 2 * * * pg_dump -U postgres -d sillymd | gzip > /backup/sillymd-full-$(date +\%Y\%m\%d).sql.gz

# WAL 归档（增量备份）
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
restore_command = 'cp /backup/wal/%f %p'

# 使用 rclone 同步到 OSS
rclone sync /var/data sillymd-tos:backup \
    --backup-dir sillymd-oss:backup-archive/$(date +%Y%m%d) \
    --max-age 30d
```

---

## 十四、快速开始

### 14.1 安装部署

```bash
# 1. 克隆项目
git clone https://github.com/sillymd/platform.git
cd platform

# 2. 后端环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置

# 4. 初始化数据库
alembic upgrade head

# 5. 启动后端服务 (开发模式)
uvicorn main:app --reload --port 8000

# 生产环境
python production.py

# 6. 前端环境
cd frontend
npm install
npm run dev

# 7. 访问平台
open http://localhost:3000
```

### 14.2 Docker 部署（仅本地开发）

```bash
# 使用 Docker Compose 一键启动（含 PostgreSQL、Redis 等）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 14.3 SDK 使用

```bash
# 安装 SDK
npm install @sillymd/sdk

# 在代码中使用
import { SillyClient } from '@sillymd/sdk';

const client = new SillyClient({
  apiKey: 'your-api-key',
  endpoint: 'https://api.sillymd.com'
});
```

### 14.4 快速链接

| 链接 | 地址 |
|------|------|
| 官网 | https://www.sillymd.com |
| 文档 | https://www.sillymd.com/docs |
| API | https://www.sillymd.com/api |
| 社区 | https://www.sillymd.com/community |
| GitHub | https://github.com/sillymd |

---

## 附录：Skills 示例

### 示例 A: 技术 Skill - Python 数据分析模板

```yaml
skill:
  id: "tech-python-data-analysis"
  name: "Python 数据分析模板"
  version: "1.0.0"
  category: "tech"
  type: "free"
  author: "SillyMD Team"
  description: "标准化的 Python 数据分析项目模板"
  tags: ["python", "data", "analysis"]

dependencies:
  - skill_id: "tech-python-base"
    version: ">=1.0.0"

setup:
  requirements:
    - python>=3.8
    - pandas>=1.3.0
    - numpy>=1.21.0
    - matplotlib>=3.4.0

structure:
  - data/           # 数据目录
  - notebooks/      # Jupyter 笔记本
  - src/            # 源代码
  - tests/          # 测试
  - README.md       # 说明文档
```

### 示例 B: 产品 Skill - PRD 模板

```yaml
skill:
  id: "prod-prd-template"
  name: "产品需求文档 (PRD) 模板"
  version: "2.0.0"
  category: "product"
  type: "free"
  author: "SillyMD Product Team"
  description: "标准化的产品需求文档模板"
  tags: ["prd", "product", "template"]

sections:
  - 背景与目标
  - 用户分析
  - 需求列表
  - 功能规格
  - 交互设计
  - 数据指标
  - 发布计划
```

### 示例 C: 商用 Skill - 企业支付网关

```yaml
skill:
  id: "com-payment-gateway"
  name: "企业支付网关解决方案"
  version: "2.1.0"
  category: "tech"
  type: "commercial"
  author: "ACME Technologies"
  description: "完整的企业级支付网关集成方案"
  tags: ["payment", "enterprise", "integration"]
  price: 5000
  license_types: ["team", "enterprise"]

dependencies:
  - skill_id: "tech-api-base"
    version: ">=2.0.0"
  - skill_id: "tech-database-base"
    version: ">=1.5.0"

features:
  - 支持多支付渠道
  - 完整的对账系统
  - 高可用架构
  - 安全合规

digital_proof:
  content_hash: "sha256:3a7b8c9d1e2f...4b5m6n"
  platform_signature: "0x9f8e7d6c5b4a...3210"
  author_signature: "0x123456789abc...def0"
  verified: true
```

---

## 十五、前端设计

### 15.1 设计系统

#### 15.1.1 色彩主题

平台支持多种色彩风格，用户可自由切换：

```
┌─────────────────────────────────────────────────────────────┐
│                      色彩主题                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  主题名称          主色      辅色      背景      文字       │
│  ─────────────────────────────────────────────────────      │
│  Light (明亮)     #3B82F6   #60A5FA   #FFFFFF   #1F2937   │
│  Dark (暗黑)      #3B82F6   #60A5FA   #111827   #F9FAFB   │
│  Ocean (海洋)     #0EA5E9   #38BDF8   #F0F9FF   #0C4A6E   │
│  Forest (森林)    #10B981   #34D399   #ECFDF5   #064E3B   │
│  Sunset (日落)    #F59E0B   #FBBF24   #FFFBEB   #78350F   │
│  Purple (紫韵)    #8B5CF6   #A78BFA   #F5F3FF   #5B21B6   │
│  Rose (玫瑰)      #EC4899   #F472B6   #FDF2F8   #9F1239   │
│  Custom (自定义)   可自定义色调                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 15.1.2 设计令牌 (Design Tokens)

```css
/* ============================================
   Design Tokens - CSS Variables
   ============================================ */

:root {
  /* 主色系 */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-primary-light: #DBEAFE;

  /* 中性色 */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;

  /* 语义色 */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* 间距 */
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */

  /* 圆角 */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);

  /* 字体大小 */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;

  /* 过渡 */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
}

/* Dark Theme Override */
[data-theme="dark"] {
  --color-bg-primary: #111827;
  --color-bg-secondary: #1F2937;
  --color-bg-tertiary: #374151;
  --color-text-primary: #F9FAFB;
  --color-text-secondary: #D1D5DB;
  --color-border: #374151;
}

/* Ocean Theme Override */
[data-theme="ocean"] {
  --color-primary: #0EA5E9;
  --color-primary-hover: #0284C7;
  --color-bg-primary: #F0F9FF;
  --color-text-primary: #0C4A6E;
}

/* Forest Theme Override */
[data-theme="forest"] {
  --color-primary: #10B981;
  --color-primary-hover: #059669;
  --color-bg-primary: #ECFDF5;
  --color-text-primary: #064E3B;
}
```

#### 15.1.3 组件库规范

```typescript
// ============================================
// 组件 Props 类型定义
// ============================================

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
}

interface CardProps {
  variant?: 'elevated' | 'outlined' | 'flat';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  children: React.ReactNode;
}

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  size?: 'sm' | 'md' | 'lg';
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  placeholder?: string;
}

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

### 15.2 页面结构

#### 15.2.1 整体布局架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header 顶部导航                           │
│  ┌──────┐  ┌─────────────┐  ┌──────────┐  ┌─────────┐  ┌────┐  │
│  │ Logo │  │  搜索框     │  │ 探索     │  │ 创建    │  │用户│  │
│  │      │  │             │  │ 下拉菜单  │  │ Skill   │  │头像│  │
│  └──────┘  └─────────────┘  └──────────┘  └─────────┘  └────┘  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────────────────────────────────────────┐  │
│  │          │  │                                              │  │
│  │ Sidebar  │  │            Main Content 主内容区              │  │
│  │  侧边栏  │  │                                              │  │
│  │          │  │                                              │  │
│  │ - 首页   │  │         (根据当前页面动态渲染)                │  │
│  │ - 探索   │  │                                              │  │
│  │ - 分类   │  │                                              │  │
│  │ - 我的   │  │                                              │  │
│  │ - 团队   │  │                                              │  │
│  │ - 设置   │  │                                              │  │
│  │          │  │                                              │  │
│  └──────────┘  └──────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        Footer 页脚                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  快速链接                                            │  │  │
│  │  │  关于 | 隐私政策 | 服务条款 | 帮助中心 | 联系我们  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  社交媒体                                            │  │  │
│  │  │  [抖音] [小红书] [视频号] [GitHub] [Discord]        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  备案信息                                            │  │  │
│  │  │  © 2026 SillyMD. All rights reserved.               │  │  │
│  │  │  浙ICP备2026000000号-1 | 浙公网安备 33010002000000号│  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.2 首页 (Home)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Hero Section 英雄区                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                                                      │  │  │
│  │  │     "AI Skills 托管中心"                              │  │  │
│  │  │     打造专业的 AI Skills 协作平台                       │  │  │
│  │  │                                                      │  │  │
│  │  │     [ 开始使用 ]    [ 探索 Skills ]                   │  │  │
│  │  │                                                      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Stats 数据统计                                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ 10,000+  │  │  5,000+  │  │  2,000+  │  │  100+    │ │  │
│  │  │  Skills   │  │  用户     │  │  团队    │  │  国家    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Skills Showcase Skills 展示                    │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │   Skill    │ │   Skill    │ │   Skill    │  ...     │  │
│  │  │   Card 1   │ │   Card 2   │ │   Card 3   │           │  │
│  │  │            │ │            │ │            │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Categories 分类展示                            │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │ 🛠️ 技术   │ │ │ 📦 产品   │ │ │ 🎨 设计   │ │ │ 📊 市场│ │  │
│  │  │ Skills    │ │ │ Skills    │ │ │ Skills    │ │ │ Skills│ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.3 探索页 (Explore)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Filter Bar 筛选栏                             │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │ 分类筛选   │ │ 类型筛选   │ │ 排序方式   │           │  │
│  │  │  全部 ▼   │ │  全部 ▼   │ │  热度 ▼   │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 🔍 搜索 Skills...                                  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 标签: [Python] [React] [数据分析] [+ Add]          │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Skills Grid Skills 网格                      │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │   Skill    │ │   Skill    │ │   Skill    │  ...     │  │
│  │  │   Card     │ │   Card     │ │   Card     │           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │ ⭐ 4.8     │ │ ⭐ 4.5     │ │ ⭐ 4.9     │           │  │
│  │  │ 📥 1.2k     │ │ 📥 856     │ │ 📥 2.3k     │           │  │
│  │  │            │ │            │ │            │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │   Skill    │ │   Skill    │ │   Skill    │  ...     │  │
│  │  │   Card     │ │   Card     │ │   Card     │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                    [ 加载更多 ]                      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.4 Skill 详情页 (Skill Detail)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Skill Header Skill 头部                        │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 🛠️                                                  │  │  │
│  │  │  Python 数据分析模板                                 │  │  │
│  │  │  by @username                                       │  │  │
│  │  │                                                      │  │  │
│  │  │  ⭐ 4.8 (128 评分)  📥 1,234 下载  ❤️ 256 收藏      │  │  │
│  │  │                                                      │  │  │
│  │  │  [ ⬇️ 下载 ] [ ❤️ 收藏 ] [ 🔗 分享 ]                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────┬─────────────────────┐ │
│  │                                       │                     │ │
│  │            Main Content             │   Sidebar 侧边栏    │ │
│  │                                       │                     │ │
│  │  ┌─────────────────────────────────┐ │  ┌───────────────┐ │ │
│  │  │  Description 描述               │ │  │  Author 作者  │ │
│  │  │  标准化的 Python 数据分析...    │ │  │               │ │ │
│  │  └─────────────────────────────────┘ │  │  @avatar      │ │ │
│  │                                       │  │  @username    │ │ │
│  │  ┌─────────────────────────────────┐ │  │               │ │ │
│  │  │  Features 特性                  │ │  │  Skills 列表  │ │ │
│  │  │  ✓ Jupyter Notebook 支持       │ │  │               │ │ │
│  │  │  ✓ 数据可视化模板               │ │  │  • Skill A    │ │ │
│  │  │  ✓ 最佳实践指南                 │ │  │  • Skill B    │ │ │
│  │  └─────────────────────────────────┘ │  │  • Skill C    │ │ │
│  │                                       │  │               │ │ │
│  │  ┌─────────────────────────────────┐ │  └───────────────┘ │ │
│  │  │  Usage 使用方法                 │ │                     │ │
│  │  │                                 │ │  ┌───────────────┐ │ │
│  │  │  npm install @sillymd/sdk      │ │  │  Statistics   │ │ │
│  │  │                                 │ │  │  统计数据      │ │ │
│  │  └─────────────────────────────────┘ │  │               │ │ │
│  │                                       │  │  📊 本月: 234  │ │ │
│  │  ┌─────────────────────────────────┐ │  │  📊 总计: 1.2k│ │ │
│  │  │  Dependencies 依赖              │ │  └───────────────┘ │ │
│  │  │  • tech-python-base >= 1.0.0    │ │                     │ │
│  │  │  • pandas >= 1.3.0              │ │  ┌───────────────┐ │ │
│  │  └─────────────────────────────────┘ │  │  Tags 标签    │ │ │
│  │                                       │  │               │ │ │
│  │  ┌─────────────────────────────────┐ │  │  #python      │ │ │
│  │  │  Version History 版本历史        │ │  │  #data        │ │ │
│  │  │  v1.0.0 (当前)                   │ │  │  #analysis    │ │ │
│  │  │  v0.9.0                         │ │  └───────────────┘ │ │
│  │  └─────────────────────────────────┘ │                     │ │
│  │                                       │                     │ │
│  └───────────────────────────────────────┴─────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Comments 评论区                                │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  @user1: 这个模板太棒了！感谢分享 🎉               │  │  │
│  │  │           └─ 2小时前                                │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  @author: @user1 谢谢支持！有需要帮助随时联系      │  │  │
│  │  │           └─ 1小时前                                │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  [ 添加评论... ]                                     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.5 用户仪表板 (User Dashboard)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              User Profile 用户概览                          │  │
│  │  ┌──────────┐  ┌─────────────────────────────────────────┐ │  │
│  │  │          │  │  @username                                  │ │  │
│  │  │  Avatar  │  │  产品经理 | 优质供应商 ⭐                   │ │  │
│  │  │          │  │                                             │ │  │
│  │  │  [编辑]  │  │  ⭐ 1,250 XP  |  💎 5,000 AI Points       │ │  │
│  │  └──────────┘  └─────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Dashboard Cards 仪表板卡片                     │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │    我的    │ │    我的    │ │    收入    │ │  审核  │ │  │
│  │  │   Skills   │ │   团队    │ │   统计    │ │  状态  │ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │    12      │ │     3      │ │  ¥2,500   │ │  1 待审│ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Recent Activity 最近活动                      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  ✅ 您的 Skill "Python 数据分析" 已通过审核          │  │  │
│  │  │     2小时前                                          │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  💰 您收到了一笔新的授权购买订单 +¥150              │  │  │
│  │  │     5小时前                                          │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  💬 @user2 评论了您的 Skill                          │  │  │
│  │  │     1天前                                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Quick Actions 快捷操作                         │  │
│  │  [ + 创建 Skill ]  [ + 创建团队 ]  [ + 充值积分 ]        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.6 团队协作页 (Team)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Team Header 团队头部                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  🏢 ACME 科技                                       │  │  │
│  │  │  sillymd.com/acme-tech                             │  │  │
│  │  │                                                     │  │  │
│  │  │  👥 8 成员  |  📁 5 项目  |  📝 12 Skills          │  │  │
│  │  │                                                     │  │  │
│  │  │  [ 邀请成员 ]  [ 创建项目 ]  [ 团队设置 ]           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Projects 项目列表                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  📁 支付系统                                        │  │  │
│  │  │     📝 3 Skills  |  👥 4 成员  |  🕒 更新于 2天前    │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  📁 用户系统                                        │  │  │
│  │  │     📝 5 Skills  |  👥 6 成员  |  🕒 更新于 5天前    │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  📁 数据平台                                        │  │  │
│  │  │     📝 4 Skills  |  👥 3 成员  |  🕒 更新于 1周前    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  [ + 新建项目 ]                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Team Members 团队成员                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │          │ │          │ │          │ │          │     │  │
│  │  │ @owner   │ │ @dev1    │ │ @dev2    │ │ @design  │ ... │  │
│  │  │ 👑 管理员 │ │ 💻 开发  │ │ 💻 开发  │ │ 🎨 设计  │     │  │
│  │  │          │ │          │ │          │ │          │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  │                                                           │  │
│  │  [ 管理成员 ]                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.7 登录/注册页 (Auth)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│              ┌─────────────────────────┐                        │
│              │                         │                        │
│              │      [ LOGO ]          │                        │
│              │                         │                        │
│              │    SillyMD Skills     │                        │
│              │      托管中心          │                        │
│              │                         │                        │
│              └─────────────────────────┘                        │
│                                                                 │
│              ┌─────────────────────────┐                        │
│              │                         │                        │
│              │    欢迎来到 SillyMD     │                        │
│              │    Skills 托管平台       │                        │
│              │                         │                        │
│              │   [ 登录 ]  [ 注册 ]     │                        │
│              │                         │                        │
│              └─────────────────────────┘                        │
│                                                                 │
│              ┌───────────────────────────────────────┐          │
│              │                                       │          │
│              │   ────  或使用以下方式登录  ────       │          │
│              │                                       │          │
│              │   [ Google ]  [ GitHub ]  [ 微信 ]    │          │
│              │                                       │          │
│              └───────────────────────────────────────┘          │
│                                                                 │
│              ┌───────────────────────────────────────┐          │
│              │            首次使用？                   │          │
│              │         [ 立即注册 →]                  │          │
│              └───────────────────────────────────────┘          │
│                                                                 │
│                     © 2026 SillyMD. All rights reserved.         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 15.3 多语言支持

#### 15.3.1 支持语言列表

```typescript
// ============================================
// 多语言配置
// ============================================

export const SUPPORTED_LANGUAGES = [
  { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
  { code: 'zh-TW', name: '繁體中文', flag: '🇹🇼' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'ja-JP', name: '日本語', flag: '🇯🇵' },
  { code: 'ko-KR', name: '한국어', flag: '🇰🇷' },
  { code: 'es-ES', name: 'Español', flag: '🇪🇸' },
  { code: 'fr-FR', name: 'Français', flag: '🇫🇷' },
  { code: 'de-DE', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'pt-BR', name: 'Português', flag: '🇧🇷' },
  { code: 'ru-RU', name: 'Русский', flag: '🇷🇺' },
] as const;

export type LanguageCode = typeof SUPPORTED_LANGUAGES[number]['code'];
```

#### 15.3.2 i18n 翻译文件结构

```
locales/
├── zh-CN/
│   ├── common.json        # 通用翻译
│   ├── home.json          # 首页
│   ├── auth.json          # 登录/注册
│   ├── skills.json        # Skills 相关
│   ├── team.json          # 团队相关
│   └── dashboard.json     # 仪表板
├── en-US/
│   ├── common.json
│   ├── home.json
│   ├── auth.json
│   ├── skills.json
│   ├── team.json
│   └── dashboard.json
└── ja-JP/
    ├── common.json
    └── ...
```

#### 15.3.3 翻译示例

```json
// locales/zh-CN/common.json
{
  "app.name": "SillyMD Skills",
  "app.slogan": "AI Skills 托管中心",
  "nav.home": "首页",
  "nav.explore": "探索",
  "nav.mySkills": "我的 Skills",
  "nav.teams": "团队",
  "nav.settings": "设置",
  "button.login": "登录",
  "button.register": "注册",
  "button.logout": "退出",
  "theme.light": "明亮",
  "theme.dark": "暗黑",
  "theme.ocean": "海洋",
  "theme.forest": "森林"
}

// locales/en-US/common.json
{
  "app.name": "SillyMD Skills",
  "app.slogan": "AI Skills Hosting Center",
  "nav.home": "Home",
  "nav.explore": "Explore",
  "nav.mySkills": "My Skills",
  "nav.teams": "Teams",
  "nav.settings": "Settings",
  "button.login": "Login",
  "button.register": "Register",
  "button.logout": "Logout",
  "theme.light": "Light",
  "theme.dark": "Dark",
  "theme.ocean": "Ocean",
  "theme.forest": "Forest"
}

// locales/ja-JP/common.json
{
  "app.name": "SillyMD Skills",
  "app.slogan": "AI Skills ホスティングセンター",
  "nav.home": "ホーム",
  "nav.explore": "探索",
  "nav.mySkills": "マイスキル",
  "nav.teams": "チーム",
  "nav.settings": "設定",
  "button.login": "ログイン",
  "button.register": "登録",
  "button.logout": "ログアウト",
  "theme.light": "ライト",
  "theme.dark": "ダーク",
  "theme.ocean": "オーシャン",
  "theme.forest": "フォレスト"
}
```

#### 15.3.4 语言切换实现

```typescript
// ============================================
// 语言切换 Hook
// ============================================

import { useTranslation } from 'react-i18next';
import { useState, useEffect } from 'react';

export const useLanguage = () => {
  const { i18n } = useTranslation();
  const [currentLang, setCurrentLang] = useState('zh-CN');

  useEffect(() => {
    // 从 localStorage 读取保存的语言偏好
    const savedLang = localStorage.getItem('preferred-language');
    if (savedLang && SUPPORTED_LANGUAGES.find(l => l.code === savedLang)) {
      setCurrentLang(savedLang);
      i18n.changeLanguage(savedLang);
    }
  }, []);

  const changeLanguage = (langCode: LanguageCode) => {
    setCurrentLang(langCode);
    i18n.changeLanguage(langCode);
    localStorage.setItem('preferred-language', langCode);

    // 更新 HTML lang 属性
    document.documentElement.lang = langCode;
  };

  return {
    currentLang,
    changeLanguage,
    languages: SUPPORTED_LANGUAGES
  };
};

// ============================================
// 语言切换器组件
// ============================================

import { Select, SelectContent, SelectItem, SelectTrigger } from '@/components/ui/select';

export function LanguageSwitcher() {
  const { currentLang, changeLanguage, languages } = useLanguage();

  return (
    <Select value={currentLang} onValueChange={changeLanguage}>
      <SelectTrigger className="w-[140px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {languages.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            <span className="mr-2">{lang.flag}</span>
            {lang.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

#### 15.3.2 页脚组件 (Footer Component)

```typescript
// ============================================
// 页脚组件
// ============================================

import { Link } from 'react-router-dom';
import { Github, MessageCircle, Video } from 'lucide-react';

interface FooterLink {
  label: string;
  href: string;
}

interface SocialMedia {
  name: string;
  icon: React.ReactNode;
  href: string;
  ariaLabel: string;
}

interface FilingInfo {
  icp: string;
  publicSecurity: string;
}

const FOOTER_LINKS: FooterLink[] = [
  { label: '关于', href: '/about' },
  { label: '隐私政策', href: '/privacy' },
  { label: '服务条款', href: '/terms' },
  { label: '帮助中心', href: '/help' },
  { label: '联系我们', href: '/contact' }
];

const SOCIAL_MEDIA: SocialMedia[] = [
  {
    name: 'douyin',
    icon: <Video className="w-5 h-5" />,
    href: 'https://douyin.com/sillymd',
    ariaLabel: '抖音'
  },
  {
    name: 'xiaohongshu',
    icon: <MessageCircle className="w-5 h-5" />,
    href: 'https://xiaohongshu.com/user/sillymd',
    ariaLabel: '小红书'
  },
  {
    name: 'video_account',
    icon: <Video className="w-5 h-5" />,
    href: 'https://weixin.qq.com/sillymd/video',
    ariaLabel: '视频号'
  },
  {
    name: 'github',
    icon: <Github className="w-5 h-5" />,
    href: 'https://github.com/sillymd',
    ariaLabel: 'GitHub'
  }
];

const FILING_INFO: FilingInfo = {
  icp: '沪ICP备2025133866号-1',
  publicSecurity: '沪公网安备 33010002000000号'
};

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="container mx-auto px-6 py-8">
        {/* 快速链接 */}
        <div className="flex flex-wrap justify-center gap-6 mb-6">
          {FOOTER_LINKS.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className="text-gray-400 hover:text-white transition-colors duration-200"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* 社交媒体 */}
        <div className="flex justify-center gap-6 mb-6">
          {SOCIAL_MEDIA.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={social.ariaLabel}
              className="text-gray-400 hover:text-white transition-colors duration-200"
            >
              {social.icon}
            </a>
          ))}
        </div>

        {/* 备案信息 */}
        <div className="text-center text-sm text-gray-500">
          <p className="mb-2">
            © {currentYear} SillyMD. All rights reserved.
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="https://beian.miit.gov.cn/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-400 transition-colors"
            >
              {FILING_INFO.icp}
            </a>
            <span>|</span>
            <span>{FILING_INFO.publicSecurity}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============================================
// 多语言页脚配置
// ============================================

import { useTranslation } from 'react-i18next';

export function FooterWithI18n() {
  const { t } = useTranslation();

  const FOOTER_LINKS_I18N: Record<string, FooterLink[]> = {
    zh: [
      { label: t('footer.about'), href: '/about' },
      { label: t('footer.privacy'), href: '/privacy' },
      { label: t('footer.terms'), href: '/terms' },
      { label: t('footer.help'), href: '/help' },
      { label: t('footer.contact'), href: '/contact' }
    ],
    en: [
      { label: 'About', href: '/about' },
      { label: 'Privacy', href: '/privacy' },
      { label: 'Terms', href: '/terms' },
      { label: 'Help', href: '/help' },
      { label: 'Contact', href: '/contact' }
    ]
  };

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="container mx-auto px-6 py-8">
        <div className="flex flex-wrap justify-center gap-6 mb-6">
          {FOOTER_LINKS_I18N[useLanguage().currentLang]?.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* 其余部分同上 */}
        <div className="flex justify-center gap-6 mb-6">
          {SOCIAL_MEDIA.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              {social.icon}
            </a>
          ))}
        </div>

        <div className="text-center text-sm text-gray-500">
          <p className="mb-2">
            © {new Date().getFullYear()} SillyMD. {t('footer.rights')}
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="https://beian.miit.gov.cn/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-400 transition-colors"
            >
              {FILING_INFO.icp}
            </a>
            <span>|</span>
            <span>{FILING_INFO.publicSecurity}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
```

### 15.4 认证系统

#### 15.4.1 支持的登录方式

```typescript
// ============================================
// 认证方式配置
// ============================================

export const AUTH_PROVIDERS = {
  EMAIL: {
    id: 'email',
    name: '邮箱登录',
    icon: '✉️',
    enabled: true,
    priority: 1
  },
  PHONE: {
    id: 'phone',
    name: '手机登录',
    icon: '📱',
    enabled: true,
    priority: 2
  },
  GITHUB: {
    id: 'github',
    name: 'GitHub',
    icon: '🐙',
    enabled: true,
    priority: 3,
    oauthUrl: '/api/v1/auth/github'
  },
  GOOGLE: {
    id: 'google',
    name: 'Google',
    icon: '🔵',
    enabled: true,
    priority: 4,
    oauthUrl: '/api/v1/auth/google'
  },
  WECHAT: {
    id: 'wechat',
    name: '微信',
    icon: '💬',
    enabled: true,
    priority: 5,
    oauthUrl: '/api/v1/auth/wechat'
  },
  ENTERPRISE_WECHAT: {
    id: 'enterprise-wechat',
    name: '企业微信',
    icon: '🏢',
    enabled: true,
    priority: 6,
    oauthUrl: '/api/v1/auth/work-wechat'
  }
} as const;
```

#### 15.4.2 登录页面组件

```typescript
// ============================================
// 登录页面组件
// ============================================

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailLogin = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // 邮箱登录逻辑
      await authApi.loginWithEmail(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthLogin = (provider: string) => {
    // OAuth 登录跳转
    window.location.href = `/api/v1/auth/${provider}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <img src="/logo.svg" alt="SillyMD" className="h-12 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">欢迎回来</h1>
            <p className="text-gray-600 mt-2">登录到 SillyMD Skills 托管中心</p>
          </div>

          {/* 认证选项卡 */}
          <Tabs defaultValue="email" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email">邮箱登录</TabsTrigger>
              <TabsTrigger value="phone">手机登录</TabsTrigger>
            </TabsList>

            {/* 邮箱登录 */}
            <TabsContent value="email" className="mt-6">
              <EmailLoginForm onSubmit={handleEmailLogin} isLoading={isLoading} />
            </TabsContent>

            {/* 手机登录 */}
            <TabsContent value="phone" className="mt-6">
              <PhoneLoginFlow isLoading={isLoading} />
            </TabsContent>
          </Tabs>

          {/* 分隔线 */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">或</span>
            </div>
          </div>

          {/* OAuth 登录按钮 */}
          <div className="space-y-3">
            <OAuthButton
              provider="github"
              onClick={() => handleOAuthLogin('github')}
            />
            <OAuthButton
              provider="google"
              onClick={() => handleOAuthLogin('google')}
            />
            <OAuthButton
              provider="wechat"
              onClick={() => handleOAuthLogin('wechat')}
            />
          </div>

          {/* 注册链接 */}
          <p className="text-center text-sm text-gray-600 mt-6">
            还没有账号？
            <a href="/register" className="text-blue-600 hover:text-blue-700 font-medium ml-1">
              立即注册
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// OAuth 登录按钮组件
// ============================================

interface OAuthButtonProps {
  provider: 'github' | 'google' | 'wechat' | 'enterprise-wechat';
  onClick: () => void;
}

function OAuthButton({ provider, onClick }: OAuthButtonProps) {
  const config = AUTH_PROVIDERS[provider.toUpperCase()];

  if (!config.enabled) return null;

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full"
      onClick={onClick}
    >
      <span className="text-xl mr-2">{config.icon}</span>
      使用 {config.name} 登录
    </Button>
  );
}

// ============================================
// 手机登录流程组件
// ============================================

function PhoneLoginFlow({ isLoading }: { isLoading: boolean }) {
  const [step, setStep] = useState<'input' | 'verify'>('input');
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');

  const handleSendCode = async () => {
    isLoading = true;
    // 发送验证码逻辑
    await authApi.sendVerificationCode(phone);
    setStep('verify');
  };

  const handleVerifyCode = async () => {
    isLoading = true;
    // 验证码验证逻辑
    await authApi.verifyCode(phone, code);
  };

  if (step === 'input') {
    return (
      <div className="space-y-4">
        <Input
          type="tel"
          placeholder="请输入手机号"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <Button
          className="w-full"
          onClick={handleSendCode}
          disabled={!phone || phone.length < 11}
        >
          发送验证码
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          type="text"
          placeholder="验证码"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          maxLength={6}
        />
        <Button
          variant="outline"
          onClick={handleSendCode}
          disabled={isLoading}
        >
          重新发送
        </Button>
      </div>
      <Button
        className="w-full"
        onClick={handleVerifyCode}
        disabled={!code || code.length < 6}
      >
        登录
      </Button>
    </div>
  );
}
```

#### 15.4.3 注册页面

```typescript
// ============================================
// 注册页面组件
// ============================================

export function RegisterPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    phone: '',
    verificationCode: ''
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* 进度指示器 */}
          <div className="flex items-center justify-center mb-8">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-semibold">1</div>
              <div className="w-16 h-1 border-t-2 mx-2"></div>
            </div>
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-semibold">2</div>
              <div className="w-16 h-1 border-t-2 mx-2"></div>
            </div>
            <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-semibold">3</div>
            </div>
          </div>

          {/* 步骤 1: 基本信息 */}
          {step === 1 && (
            <>
              <h2 className="text-2xl font-bold text-center mb-6">创建账号</h2>
              <RegisterStep1
                data={formData}
                onChange={setFormData}
                onNext={() => setStep(2)}
              />
            </>
          )}

          {/* 步骤 2: 验证 */}
          {step === 2 && (
            <>
              <h2 className="text-2xl font-bold text-center mb-6">验证联系方式</h2>
              <RegisterStep2
                data={formData}
                onChange={setFormData}
                onNext={() => setStep(3)}
                onBack={() => setStep(1)}
              />
            </>
          )}

          {/* 步骤 3: 完成 */}
          {step === 3 && (
            <>
              <h2 className="text-2xl font-bold text-center mb-6">欢迎加入!</h2>
              <RegisterStep3
                data={formData}
                onChange={setFormData}
                onBack={() => setStep(2)}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
```

### 15.5 主题切换器

#### 15.5.1 主题选择组件

```typescript
// ============================================
// 主题切换组件
// ============================================

import { useState } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';

export function ThemeSwitcher() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'ocean' | 'forest' | 'sunset' | 'custom'>('light');

  const themes = [
    { id: 'light', name: '明亮', preview: 'bg-white border-gray-200' },
    { id: 'dark', name: '暗黑', preview: 'bg-gray-900 border-gray-700' },
    { id: 'ocean', name: '海洋', preview: 'bg-blue-50 border-blue-200' },
    { id: 'forest', name: '森林', preview: 'bg-green-50 border-green-200' },
    { id: 'sunset', name: '日落', preview: 'bg-orange-50 border-orange-200' },
    { id: 'purple', name: '紫韵', preview: 'bg-purple-50 border-purple-200' },
    { id: 'rose', name: '玫瑰', preview: 'bg-pink-50 border-pink-200' },
  ];

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="icon">
          <PaletteIcon className="h-5 w-5" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-4">
        <h3 className="font-semibold mb-3">选择主题</h3>
        <div className="grid grid-cols-4 gap-2">
          {themes.map((t) => (
            <button
              key={t.id}
              onClick={() => setTheme(t.id)}
              className={`
                w-12 h-12 rounded-lg border-2 ${t.preview}
                ${theme === t.id ? 'ring-2 ring-offset-2 ring-blue-500' : ''}
                hover:opacity-80 transition-opacity
              `}
              title={t.name}
            />
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
```

#### 15.5.2 主题 Provider

```typescript
// ============================================
// 主题 Provider
// ============================================

import { createContext, useContext, useEffect, ReactNode } from 'react';

type Theme = 'light' | 'dark' | 'ocean' | 'forest' | 'sunset' | 'purple' | 'rose' | 'custom';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('light');

  useEffect(() => {
    // 从 localStorage 读取主题偏好
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  const setTheme = (theme: Theme) => {
    setThemeState(theme);
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

### 15.6 响应式设计

#### 15.6.1 断点配置

```typescript
// ============================================
// Tailwind CSS 断点配置
// ============================================

const breakpoints = {
  xs: '0px',      // 移动设备 (< 640px)
  sm: '640px',     // 平板竖屏 (≥ 640px)
  md: '768px',     // 平板横屏 (≥ 768px)
  lg: '1024px',    // 笔记本 (≥ 1024px)
  xl: '1280px',    // 桌面 (≥ 1280px)
  '2xl': '1536px', // 大屏 (≥ 1536px)
};

// ============================================
// 响应式工具类
// ============================================

/*
  移动优先策略：

  - 默认样式为移动端
  - 使用 sm:、md:、lg:、xl:、2xl: 前缀适配更大屏幕

  示例：
  <div className="w-full md:w-1/2 lg:w-1/3">
    - 移动端: 100% 宽度
    - 平板及以上: 50% 宽度
    - 桌面及以上: 33% 宽度
  </div>
*/
```

#### 15.6.2 响应式导航

```typescript
// ============================================
// 响应式导航栏
// ============================================

export function ResponsiveNav() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <a href="/" className="flex items-center">
              <img src="/logo.svg" alt="SillyMD" className="h-8" />
            </a>
          </div>

          {/* 桌面导航 */}
          <div className="hidden md:flex md:items-center md:space-x-6">
            <a href="/explore" className="text-gray-700 hover:text-blue-600">探索</a>
            <a href="/pricing" className="text-gray-700 hover:text-blue-600">定价</a>
            <a href="/docs" className="text-gray-700 hover:text-blue-600">文档</a>
            <a href="/login" className="text-gray-700 hover:text-blue-600">登录</a>
            <a href="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              注册
            </a>
          </div>

          {/* 移动端菜单按钮 */}
          <div className="md:hidden">
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              <MenuIcon className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      {/* 移动端菜单 */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <a href="/explore" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              探索
            </a>
            <a href="/pricing" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              定价
            </a>
            <a href="/docs" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              文档
            </a>
            <a href="/login" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              登录
            </a>
            <a href="/register" className="block px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700">
              注册
            </a>
          </div>
        </div>
      )}
    </nav>
  );
}
```

### 15.7 页面路由配置

```typescript
// ============================================
// 路由配置
// ============================================

import { createBrowserRouter } from 'react-router-dom';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        path: '/',
        element: <HomePage />
      },
      {
        path: '/explore',
        element: <ExplorePage />
      },
      {
        path: '/skills/:skillId',
        element: <SkillDetailPage />
      },
      {
        path: '/login',
        element: <LoginPage />
      },
      {
        path: '/register',
        element: <RegisterPage />
      },
      {
        path: '/dashboard',
        element: <ProtectedRoute />,
        children: [
          {
            path: '',
            element: <DashboardHome />
          },
          {
            path: 'skills',
            element: <MySkillsPage />
          },
          {
            path: 'settings',
            element: <SettingsPage />
          }
        ]
      },
      {
        path: '/teams/:teamSlug',
        element: <TeamPage />,
        children: [
          {
            path: '',
            element: <TeamOverview />
          },
          {
            path: 'projects/:projectSlug',
            element: <ProjectPage />
          }
        ]
      },
      {
        path: '/admin',
        element: <AdminRoute />,
        children: [
          {
            path: '',
            element: <AdminDashboard />
          },
          {
            path: 'skills',
            element: <SkillReview />
          },
          {
            path: 'users',
            element: <UserManagement />
          }
        ]
      }
    ]
  },
  {
    path: '*',
    element: <NotFoundPage />
  }
]);
```

### 15.8 性能优化

```typescript
// ============================================
// 性能优化配置
// ============================================

// 1. 代码分割 (Code Splitting)
import { lazy, Suspense } from 'react';

const DashboardHome = lazy(() => import('./pages/DashboardHome'));
const SkillDetailPage = lazy(() => import('./pages/SkillDetailPage'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<DashboardHome />} />
        <Route path="/skills/:id" element={<SkillDetailPage />} />
      </Routes>
    </Suspense>
  );
}

// 2. 图片懒加载
import { LazyLoadImage } from '@/components/LazyLoadImage';

<LazyLoadImage
  src="/hero-image.jpg"
  alt="Hero"
  className="w-full h-64 object-cover"
  loading="lazy"
/>

// 3. 虚拟列表 (长列表优化)
import { useVirtualizer } from '@tanstack/react-virtual';

function SkillList({ skills }: { skills: Skill[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: skills.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200, // 预估每项高度
    overscan: 5
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`
            }}
          >
            <SkillCard skill={skills[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 十六、Skills 编辑器

### 16.1 编辑器概述

Skills 编辑器是平台核心功能，支持创建、编辑、预览和发布 Skills 文档。

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills 编辑器界面                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  顶部工具栏                                          │  │
│  │  [保存草稿] [预览] [发布] [设置] [导出] [历史版本]        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────┬───────────────────────────────────────────────┐  │
│  │      │                                               │  │
│  │ 左侧 │            主编辑区                           │  │
│  │ 工具 │                                               │  │
│  │ 栏   │  ┌─────────────────────────────────────────┐  │  │
│ │      │  │                                         │  │  │
│  │      │  │         [ 所见即所得编辑器 ]            │  │  │
│  │      │  │                                         │  │  │
│  │  📝   │  │  支持 Markdown + YAML Frontmatter       │  │  │
│  │  📎   │  │  实时预览                              │  │  │
│  │  🖼️   │  │                                         │  │  │
│  │  📊   │  │                                         │  │  │
│  │  💻   │  │                                         │  │  │
│  │  🔗   │  │                                         │  │  │
│  │  ⚙️   │  │                                         │  │  │
│  │      │  │                                         │  │  │
│  │      │  └─────────────────────────────────────────┘  │  │
│  │      │                                               │  │
│  │ ┌────┴─────────────────────────────────────────────┐ │  │
│  │ │                                               │ │  │
│  │ │  属性面板 (Properties)                        │ │  │
│  │ │  ┌─────────────────────────────────────────┐  │  │
│  │  │  │ Skill ID: tech-python-data-analysis     │  │  │
│  │  │  │ 名称: [_______________________]     │  │  │
│  │  │  │ 分类: [技术 ▼]                       │  │  │
│  │  │  │ 类型: [免费 ▼]                       │  │  │
│  │  │  │ 标签: [Python] [+]                 │  │  │
│  │  │  │                                       │  │  │
│  │  │  │ 版本: 1.0.0                           │  │  │
│  │  │  │ 定价: █████ (商用 Skills)             │  │  │
│  │  │  │                                       │  │  │
│  │  │  │ [ 高级设置 ▼ ]                        │  │  │
│  │  │  └─────────────────────────────────────────┘  │  │
│  │ └──────────────────────────────────────────────┘ │  │
│  └──────┴───────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  底部状态栏                                          │  │
│  │  字数: 1,234  |  阅读时间: 5分钟  |  上次保存: 2分钟前  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 16.2 编辑器功能特性

#### 16.2.1 核心功能

| 功能 | 说明 | 技术实现 |
|------|------|----------|
| **所见即所得编辑** | 实时预览 Markdown 渲染效果 | Toast UI + ReactMarkdown |
| **语法高亮** | Markdown、YAML、代码块语法高亮 | Prism.js / Shiki |
| **智能提示** | Skills 元素自动补全 | Monaco Editor |
| **版本历史** | Git �格版本控制，可对比回滚 | isomorphic-git |
| **实时协作** | 多人同时编辑，显示光标位置 | Y.js / WebSocket |
| **拖拽上传** | 支持图片、文件拖拽上传 | react-dropzone |
| **离线编辑** | 支持离线编辑，自动同步 | IndexedDB + Service Worker |

#### 16.2.2 编辑工具栏

```typescript
// ============================================
// 编辑器工具栏配置
// ============================================

export const EDITOR_TOOLBAR = [
  // 文本格式
  {
    type: 'group',
    name: 'format',
    items: [
      { icon: 'bold', label: '粗体', action: 'toggleBold' },
      { icon: 'italic', label: '斜体', action: 'toggleItalic' },
      { icon: 'strikethrough', label: '删除线', action: 'toggleStrikethrough' },
      { icon: 'code', label: '行内代码', action: 'toggleCode' }
    ]
  },
  // 标题
  {
    type: 'group',
    name: 'headings',
    items: [
      { icon: 'h1', label: '一级标题', action: 'setHeading', level: 1 },
      { icon: 'h2', label: '二级标题', action: 'setHeading', level: 2 },
      { icon: 'h3', label: '三级标题', action: 'setHeading', level: 3 }
    ]
  },
  // 列表
  {
    type: 'group',
    name: 'lists',
    items: [
      { icon: 'ul', label: '无序列表', action: 'toggleBulletList' },
      { icon: 'ol', label: '有序列表', action: 'toggleOrderedList' },
      { icon: 'checklist', label: '任务列表', action: 'toggleCheckList' }
    ]
  },
  // 插入元素
  {
    type: 'group',
    name: 'insert',
    items: [
      { icon: 'link', label: '链接', action: 'insertLink' },
      { icon: 'image', label: '图片', action: 'insertImage' },
      { icon: 'table', label: '表格', action: 'insertTable' },
      { icon: 'code-block', label: '代码块', action: 'insertCodeBlock' },
      { icon: 'quote', label: '引用', action: 'toggleBlockquote' },
      { icon: 'divider', label: '分隔线', action: 'insertDivider' },
      { icon: 'callout', label: '提示框', action: 'insertCallout' }
    ]
  },
  // Skills 特有
  {
    type: 'group',
    name: 'skills',
    items: [
      { icon: 'metadata', label: '元数据', action: 'insertMetadata' },
      { icon: 'dependencies', label: '依赖关系', action: 'insertDependencies' },
      { icon: 'changelog', label: '更新日志', action: 'insertChangelog' }
    ]
  }
];
```

#### 16.2.3 YAML 元数据编辑器

```typescript
// ============================================
// Skills 元数据编辑器
// ============================================

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const skillMetadataSchema = z.object({
  id: z.string().min(3).max(50),
  name: z.string().min(1).max(200),
  description: z.string().max(500),
  category: z.enum(['tech', 'product', 'design', 'marketing', 'ops']),
  type: z.enum(['free', 'commercial']).default('free'),
  version: z.string().default('1.0.0'),
  tags: z.array(z.string()).default([]),
  price: z.number().min(0).optional(),
  licenseTypes: z.array(z.string()).optional(),
  dependencies: z.array(z.object({
    skill_id: z.string(),
    version: z.string(),
    type: z.enum(['required', 'optional'])
  })).default([])
});

export function SkillMetadataEditor({ skill, onSave }) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(skillMetadataSchema),
    defaultValues: skill
  });

  return (
    <form onSubmit={handleSubmit(onSave)} className="space-y-4">
      {/* 基本信息 */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1">Skill ID</label>
          <input {...register('id')} className="w-full px-3 py-2 border rounded-md" />
          {errors.id && <p className="text-red-500 text-sm">{errors.id.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">名称</label>
          <input {...register('name')} className="w-full px-3 py-2 border rounded-md" />
          {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">描述</label>
          <textarea {...register('description')} rows={3} className="w-full px-3 py-2 border rounded-md" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">分类</label>
            <select {...register('category')} className="w-full px-3 py-2 border rounded-md">
              <option value="tech">技术</option>
              <option value="product">产品</option>
              <option value="design">设计</option>
              <option value="marketing">市场</option>
              <option value="ops">运营</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">类型</label>
            <select {...register('type')} className="w-full px-3 py-2 border rounded-md">
              <option value="free">免费</option>
              <option value="commercial">商用</option>
            </select>
          </div>
        </div>

        {/* 标签 */}
        <TagInput
          value={watch('tags')}
          onChange={(tags) => setValue('tags', tags)}
          placeholder="添加标签，按回车确认"
        />

        {/* 商用字段 */}
        {watch('type') === 'commercial' && (
          <div className="mt-4 p-4 bg-yellow-50 rounded-md border border-yellow-200">
            <h4 className="font-semibold mb-3">商用设置</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">价格 (AI Points)</label>
                <input
                  type="number"
                  {...register('price', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">授权类型</label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      value="personal"
                      {...register('licenseTypes')}
                      className="mr-2"
                    />
                    个人授权 (1x)
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      value="team"
                      {...register('licenseTypes')}
                      className="mr-2"
                    />
                    团队授权 (3x)
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      value="enterprise"
                      {...register('licenseTypes')}
                      className="mr-2"
                    />
                    企业授权 (10x)
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 依赖关系 */}
        <DependencyEditor
          value={watch('dependencies')}
          onChange={(deps) => setValue('dependencies', deps)}
        />

        <div className="flex justify-end gap-3 pt-4 border-t">
          <button type="button" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
            取消
          </button>
          <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            保存
          </button>
        </div>
      </div>
    </form>
  );
}
```

#### 16.2.4 实时预览

```typescript
// ============================================
// 实时预览组件
// ============================================

import { useEffect, useState } from 'react';
import { Markdown } from '@/components/Markdown';
import { SkillPreview } from '@/components/SkillPreview';

export function EditorPreview({ content, metadata }) {
  const [html, setHtml] = useState('');

  useEffect(() => {
    // 实时渲染 Markdown
    setHtml(renderMarkdown(content));
  }, [content]);

  return (
    <div className="preview-container h-full overflow-auto">
      {/* 元数据预览 */}
      <SkillPreview.Header metadata={metadata} />

      {/* 内容预览 */}
      <Markdown content={content} />

      {/* 依赖关系可视化 */}
      {metadata.dependencies && metadata.dependencies.length > 0 && (
        <DependencyGraph dependencies={metadata.dependencies} />
      )}
    </div>
  );
}

// ============================================
// 依赖关系可视化
// ============================================

import { useGraph } from '@vis-network/react';

export function DependencyGraph({ dependencies }) {
  const { graph } = useGraph({
    nodes: [],
    edges: [],
    height: '400px'
  });

  useEffect(() => {
    const nodes = dependencies.map(dep => ({
      id: dep.skill_id,
      label: `${dep.skill_id}\n${dep.version}`,
      shape: 'box',
      color: getSkillColor(dep.category)
    }));

    const edges = dependencies.map(dep => ({
      from: 'current',
      to: dep.skill_id,
      label: dep.version_constraint,
      arrows: 'to',
      dashes: dep.type === 'optional'
    }));

    graph({ nodes, edges });
  }, [dependencies]);

  return <div ref={graph.ref} />;
}
```

#### 16.2.5 版本对比

```typescript
// ============================================
// 版本对比功能
============================================

import { Diff, Hunk } from 'react-diff-view';

export function SkillVersionDiff({ oldVersion, newVersion }) {
  return (
    <div className="version-diff">
      <h3 className="text-lg font-semibold mb-4">
        版本对比: {oldVersion.version} → {newVersion.version}
      </h3>

      {/* Skills 元数据对比 */}
      <Diff
        oldValue={JSON.stringify(oldVersion.metadata, null, 2)}
        newValue={JSON.stringify(newVersion.metadata, null, 2)}
        splitView={true}
        hideLineNumbers={false}
        showDiffOnly={true}
      />

      {/* 内容对比 */}
      <Diff
        oldValue={oldVersion.content}
        newValue={newVersion.content}
        splitView={true}
        hideLineNumbers={false}
        showDiffOnly={true}
      />
    </div  );
}
```

### 16.3 编辑器快捷键

```
┌─────────────────────────────────────────────────────────────┐
│                     编辑器快捷键                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  编辑操作                                                    │
│  ├── Ctrl/Cmd + S     保存草稿                               │
│  ├── Ctrl/Cmd + Shift + S   发布 Skill                         │
│  ├── Ctrl/Cmd + P       预览                                   │
│  ├── Ctrl/Cmd + /       打开命令面板                           │
│  └── Ctrl/Cmd + K         快速插入                               │
│                                                             │
│  文本格式                                                    │
│  ├── Ctrl/Cmd + B       粗体                                   │
│  ├── Ctrl/Cmd + I       斜体                                   │
│  ├── Ctrl/Cmd + U       下划线                                 │
│  ├── Ctrl/Cmd + K       插入代码块                               │
│  └── Ctrl/Cmd + L       插入链接                                 │
│                                                             │
│  导航                                                        │
│  ├── Ctrl/Cmd + F       查找                                    │
│  ├── Ctrl/Cmd + H       替换                                    │
│  ├── Ctrl/Cmd + G       跳转到行                               │
│  └── Ctrl/Cmd + T         打开文件树                             │
│                                                             │
│  视图                                                        │
│  ├── Ctrl/Cmd + Shift + P   切换预览/编辑                         │
│  ├── Ctrl/Cmd + \         切换侧边栏                             │
│  └── Ctrl/Cmd + Shift + F   全屏模式                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十七、资源下载中心

### 17.1 资源分类

平台提供丰富的 AI 工具和开发资源下载，帮助用户快速上手。

```
┌─────────────────────────────────────────────────────────────┐
│                    资源下载中心                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  按类别筛选                                           │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │  │
│  │  │ IDE插件 │ │ AI模型  │ │ 开发工具 │ │ 文档   │        │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  热门资源                                             │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ 📦 OpenClaw CLI                     ⭐ 4.9       │  │  │
│  │  │    openclaw-cli-v2.1.0-win-x64.zip                 │  │  │
│  │  │    下载: 12,345 | 大小: 45MB | 更新: 2024-01-15   │  │  │
│  │  │    [Windows] [macOS] [Linux] [文档]               │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │ 🤖 Claude Code Desktop              ⭐ 4.8       │  │  │
│  │  │    claude-code-desktop-1.2.0.dmg                    │  │  │
│  │  │    下载: 8,901 | 大小: 180MB | 更新: 2024-01-10  │  │  │
│  │  │    [Windows] [macOS] [Linux] [文档]               │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │ 🔧 Cursor 编辑器                    ⭐ 4.7       │  │  │
│  │  │    cursor-1.5.0-build222.exe                       │  │  │
│  │  │    下载: 6,789 | 大小: 95MB | 更新: 2024-01-08   │  │  │
│  │  │    [Windows] [macOS] [Linux] [文档]               │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 17.2 资源详情页

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  OpenClaw CLI                                     ⭐ 4.9      │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  OpenClaw CLI 是一个命令行工具，让您直接从终端访问...  │  │
│  │                                                             │  │
│  │  📊 统计                                                 │  │
│  │  • 总下载: 12,345                                             │  │
│  │  • 本周下载: 234                                             │  │
│  │  • 评分: 4.9 (256 评分)                                        │  │
│  │                                                             │  │
│  │  🏷️ 标签                                                 │  │
│  │  [AI 工具] [CLI] [OpenAI] [文档] [+ Add]                 │  │
│  │                                                             │  │
│  │  📁 下载版本                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ Version 2.1.0 (最新) • 2024-01-15 • 45MB           │  │  │
│  │  │ [Windows x64] [macOS x64] [Linux x64]               │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │ Version 2.0.0 • 2023-12-01 • 42MB                 │  │  │
│  │  │ [Windows x64] [macOS x64] [Linux x64]               │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  📚 使用文档                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ • 快速开始指南                                      │  │  │
│  │  │  • API 参考文档                                      │  │  │
│  │  │ • 常见问题解答                                      │  │  │  │
│  │  │  • 视频教程                                          │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  💬 用户评价                                             │  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ @user1: 工具很好用，API 调用很方便！              │  │  │
│  │  │           └─ 3天前 • 👍 24                           │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │ @dev_master: 文档很详细，上手快。                     │  │  │
│  │  │           └─ 1周前 • 👍 18                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  [ ⬇️ 下载最新版 ]  [ ⭐ 收藏 ]  [ 🔗 分享 ]               │  │
│  │                                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  相关资源推荐                                           │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │  │
│  │  │             │ │             │ │             │       │  │
│  │  │ Claude Code  │ │   Cursor    │ │   Copilot    │       │  │
│  │  │             │ │             │ │             │       │  │
│  │  │    ⭐ 4.8   │ │    ⭐ 4.7   │ │    ⭐ 4.5   │       │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 17.3 资源管理（后台）

```typescript
// ============================================
// 资源管理后台
// ============================================

interface Resource {
  id: string;
  name: string;
  description: string;
  category: 'ide' | 'ai-tool' | 'dev-tool' | 'documentation';
  versions: ResourceVersion[];
  totalDownloads: number;
  averageRating: number;
  tags: string[];
  officialUrl: string;
  documentationUrl: string;
}

interface ResourceVersion {
  version: string;
  platform: 'windows' | 'macos' | 'linux';
  architecture: 'x64' | 'arm64';
  downloadUrl: string;
  fileSize: number;
  sha256: string;
  releaseDate: Date;
  isActive: boolean;
}

export function ResourceManagement() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // 上传新资源
  const handleUpload = async (file: File, metadata: Partial<Resource>) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify(metadata));

      const result = await api.post('/admin/resources/upload', formData);

      // 添加到资源列表
      setResources([result.data, ...resources]);
      toast.success('资源上传成功');
    } catch (error) {
      toast.error('资源上传失败');
    } finally {
      setIsUploading(false);
    }
  };

  // 更新资源
  const handleUpdateResource = async (id: string, updates: Partial<Resource>) => {
    try {
      await api.put(`/admin/resources/${id}`, updates);
      toast.success('资源更新成功');
    } catch (error) {
      toast.error('资源更新失败');
    }
  };

  // 删除资源
  const handleDeleteResource = async (id: string) => {
    if (!confirm('确定要删除这个资源吗？')) return;

    try {
      await api.delete(`/admin/resources/${id}`);
      setResources(resources.filter(r => r.id !== id));
      toast.success('资源删除成功');
    } catch (error) {
      toast.error('资源删除失败');
    }
  };

  return (
    <div className="resource-management">
      {/* 资源列表 */}
      <ResourceTable
        resources={resources}
        onUpdate={handleUpdateResource}
        onDelete={handleDeleteResource}
      />

      {/* 上传按钮 */}
      <UploadButton onUpload={handleUpload} isUploading={isUploading} />
    </div>
  );
}
```

### 17.4 下载链接安全

```typescript
// ============================================
// 临时下载链接生成
// ============================================

import { createHash } from 'crypto';

interface DownloadToken {
  token: string;
  resourceId: string;
  versionId: string;
  expiresAt: Date;
  maxDownloads: number;
  downloadCount: number;
}

export async function generateDownloadToken(
  resourceId: string,
  versionId: string,
  options: {
    expiresIn?: number; // 默认 24 小时
    maxDownloads?: number; // 默认 5 次
  } = {}
): Promise<string> {
  const { expiresIn = 86400, maxDownloads = 5 } = options;

  const token: DownloadToken = {
    token: generateToken(),
    resourceId,
    versionId,
    expiresAt: new Date(Date.now() + expiresIn * 1000),
    maxDownloads,
    downloadCount: 0
  };

  // 保存到数据库
  await db.downloadTokens.create({ data: token });

  // 返回加密的下载链接
  const encrypted = encryptToken(token);
  return `/download/${encrypted}`;
}

// ============================================
// 下载验证中间件
// ============================================

export async function validateDownloadToken(
  encryptedToken: string
): Promise<{ resourceId: string; versionId: string } | null> {
  try {
    const token: DownloadToken = decryptToken(encryptedToken);

    // 检查过期
    if (new Date() > token.expiresAt) {
      return null;
    }

    // 检查下载次数
    if (token.downloadCount >= token.maxDownloads) {
      return null;
    }

    // 增加下载计数
    await db.downloadTokens.update(token.id, {
      downloadCount: token.downloadCount + 1
    });

    return {
      resourceId: token.resourceId,
      versionId: token.versionId
    };
  } catch (error) {
    return null;
  }
}
```

---

## 十八、交流学习社区

### 18.1 社区首页

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  社区顶部 Banner                                      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  学习 • 交流 • 分享 • 成长                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  内容导航                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐   │  │
│  │  │ 📺 视频  │ │ 📄 文档  │ │ 💬 讨论  │ │ 🎓 课程 │   │  │
│  │  │  128    │ │  256    │ │  512    │ │  16    │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  热门内容                                             │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  📺 置页设计完整教程 - 从 0 到 1                        │  │  │
│  │  │     • 👁️ 2,345 观看  • ⭐ 4.8  • 15分钟             │  │  │
│  │  ├───────────────────────────────────────────────────────┤  │  │
│  │  │  📄 Python FastAPI 完整开发指南                           │  │  │
│  │  │     • 👁️ 5,678 阅读  • ⭐ 4.9  • 25分钟             │  │  │
│  │  ├───────────────────────────────────────────────────────┤  │  │
│  │  │  💬 如何使用 Claude Code 提升 100% 开发效率            │  │  │
│  │  │     • 👁️ 892 回复   • 🔥 热门话题                       │  │  │
│  │  └───────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  最新内容                                             │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │  │
│  │  │             │ │             │ │             │          │  │
│  │  │  📺 视频教程  │ │ 📄 技术文档  │ │ 💬 社区讨论  │          │  │
│  │  │             │ │             │ │             │          │  │
│  │  │  发布于 2天前 │ │ 发布于 5小时前│ 发布于 1天前 │          │  │
│  │  └─────────────┘ └─────────────� └─────────────┘          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  精选课程                                             │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                        │  │  │
│  │  │  │         │ │         │ │         │                        │  │  │
│  │  │  │  Python  │ │  React  │ │  AI 技术  │  ...                   │  │  │
│  │  │  │  入门    │  │  实战   │  │  实战    │                        │  │  │
│  │  │  │  12 课时  │  │  8 课时  │  │  10 课时 │                        │  │  │
│  │  │  │  ⭐ 4.9  │  │  ⭐ 4.7  │  │  │  │  │
│  │  │  └─────────┘ └─────────┘ └─────────�                        │  │  │
│  │  └───────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  [ 查看全部课程 → ]                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 18.2 视频教程

#### 18.2.1 视频播放器

```typescript
// ============================================
// 视频播放器组件
// ============================================

import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, FullScreen } from 'lucide-react';

interface VideoPlayerProps {
  src: string;
  poster?: string;
  title: string;
  description?: string;
  subtitles?: { language: string; url: string }[];
  relatedVideos?: Video[];
}

export function VideoPlayer({ src, poster, title, description, subtitles, relatedVideos }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  // 格式化时间
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // 快捷键控制
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === ' ') {
        e.preventDefault();
        togglePlay();
      } else if (e.key === 'ArrowLeft') {
        videoRef.current!.currentTime -= 5;
      } else if (e.key === 'ArrowRight') {
        videoRef.current!.currentTime += 5;
      } else if (e.key === 'f') {
        e.preventDefault();
        toggleFullscreen();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, []);

  const togglePlay = () => {
    if (isPlaying) {
      videoRef.current?.pause();
    } else {
      videoRef.current?.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  return (
    <div className="video-player">
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        className="w-full aspect-video bg-black rounded-lg"
        onTimeUpdate={() => setCurrentTime(videoRef.current!.currentTime)}
        onLoadedMetadata={() => setDuration(videoRef.current!.duration)}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      >
        {subtitles?.map((sub, index) => (
          <track key={index} kind="subtitles" src={sub.url} srcLang={sub.language} />
        ))}
      </video>

      {/* 控制栏 */}
      <div className="controls mt-4">
        {/* 进度条 */}
        <input
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          onChange={(e) => {
            videoRef.current!.currentTime = Number(e.target.value);
            setCurrentTime(Number(e.target.value));
          }}
          className="w-full accent-blue-600"
        />

        <div className="flex items-center justify-between mt-2">
          {/* 播放/暂停 */}
          <button onClick={togglePlay} className="p-2 hover:bg-gray-100 rounded-full">
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>

          {/* 时间显示 */}
          <span className="text-sm text-gray-600">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>

          {/* 播放速度 */}
          <select
            value={playbackSpeed}
            onChange={(e) => {
              setPlaybackSpeed(Number(e.target.value));
              if (videoRef.current) {
                videoRef.current.playbackRate = Number(e.target.value);
              }
            }}
            className="ml-4 text-sm border rounded px-2 py-1"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={1.25}>1.25x</option>
            <option value={1.5}>1.5x</option>
            <option value={2}>2x</option>
          </select>

          {/* 音量 */}
          <button className="ml-4 p-2 hover:bg-gray-100 rounded-full">
            <Volume2 size={20} />
          </button>

          {/* 全屏 */}
          <button onClick={toggleFullscreen} className="ml-4 p-2 hover:bg-gray-100 rounded-full">
            <FullScreen size={20} />
          </button>
        </div>
      </div>

      {/* 标题和描述 */}
      <div className="mt-4">
        <h3 className="text-xl font-semibold">{title}</h3>
        {description && (
          <p className="text-gray-600 mt-2">{description}</p>
        )}
      </div>

      {/* 相关视频 */}
      {relatedVideos && relatedVideos.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold mb-3">相关视频</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {relatedVideos.map((video) => (
              <RelatedVideoCard key={video.id} video={video} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 18.2.2 视频上传

```typescript
// ============================================
// 视频上传功能
// ============================================

interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  videoId?: string;
  error?: string;
}

export function VideoUpload() {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);

  const handleFileSelect = async (files: FileList) => {
    const fileArray = Array.from(files);

    // 添加到上传队列
    const newUploads: UploadProgress[] = fileArray.map(file => ({
      file,
      progress: 0,
      status: 'uploading'
    }));

    setUploads([...uploads, ...newUploads]);

    // 逐个上传
    for (const upload of newUploads) {
      await uploadFile(upload);
    }
  };

  const uploadFile = async (upload: UploadProgress) => {
    const formData = new FormData();
    formData.append('video', upload.file);
    formData.append('title', upload.file.name.replace(/\.[^/.]+$/, ''));

    try {
      // 上传文件
      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          upload.progress = (e.loaded / e.total) * 100;
          setUploads([...uploads]);
        }
      };

      xhr.onload = async () => {
        if (xhr.status === 200) {
          const result = JSON.parse(xhr.responseText);
          upload.status = 'processing';
          upload.videoId = result.id;
          setUploads([...uploads]);

          // 触发视频处理（转码、生成缩略图等）
          await processVideo(result.id);
        }
      };

      xhr.open('POST', '/api/v1/videos/upload');
      xhr.send(formData);

    } catch (error) {
      upload.status = 'error';
      upload.error = '上传失败';
      setUploads([...uploads]);
    }
  };

  const processVideo = async (videoId: string) => {
    try {
      await api.post(`/api/v1/videos/${videoId}/process`);

      const uploadIndex = uploads.findIndex(u => u.videoId === videoId);
      if (uploadIndex !== -1) {
        uploads[uploadIndex].status = 'completed';
        setUploads([...uploads]);
      }

      toast.success('视频上传并处理成功');
    } catch (error) {
      const uploadIndex = uploads.findIndex(u => u.videoId === videoId);
      if (uploadIndex !== -1) {
        uploads[uploadIndex].status = 'error';
        uploads[uploadIndex].error = '处理失败';
        setUploads([...uploads]);
      }
    }
  };

  return (
    <div className="video-upload">
      <input
        type="file"
        accept="video/*"
        multiple
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
        id="video-upload"
      />
      <label
        htmlFor="video-upload"
        className="flex flex-col items-center justify-center w-64 h-32 border-2 border-dashed rounded-lg cursor-pointer hover:border-blue-500"
      >
        <UploadCloud className="w-8 h-8 text-gray-400 mb-2" />
        <span className="text-sm text-gray-600">点击或拖拽上传视频</span>
        <span className="text-xs text-gray-400 mt-1">支持 MP4, WebM, MOV</span>
      </label>

      {/* 上传进度列表 */}
      {uploads.map((upload, index) => (
        <UploadProgressItem key={index} upload={upload} />
      ))}
    </div>
  );
}
```

### 18.3 文档系统

#### 18.3.1 文档结构

```
docs/
├── getting-started/
│   ├── installation.md
│   ├── quick-start.md
│   └── first-skill.md
├── tutorials/
│   ├── python/
│   │   ├── basics.md
│   │   ├── web-development.md
│   │   └── data-science.md
│   ├── frontend/
│   │   ├── react/
│   │   │   ├── introduction.md
│   │   │   ├── components.md
│   │   │   └── state-management.md
│   │   └── vue/
│   │       └── introduction.md
│   └── ai/
│       ├── prompt-engineering/
│       └── llm-apis/
├── api-reference/
│   ├── overview.md
│   ├── authentication.md
│   ├── skills/
│   │   ├── list.md
│   │   ├── create.md
│   │   ├── update.md
│   │   └── delete.md
│   └── users/
│       └── management.md
├── examples/
│   └── code-snippets/
└── glossary.md
```

#### 18.3.2 文档渲染

```typescript
// ============================================
// 文档渲染器
// ============================================

import { useMemo } from 'react';
import { ReactMarkdown } from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

interface DocsContentProps {
  content: string;
}

export function DocsContent({ content }: DocsContentProps) {
  const components = {
    // 代码块
    pre: ({ children, className, ...props }) => {
      const language = /language-(\w+)/.exec(className || '')?.[1];
      return (
        <div className="relative group">
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
            <code className={className}>{children}</code>
          </pre>
          <CopyButton
            code={String(children?.props?.children || '')}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100"
          />
        </div>
      );
    },
    // 标题
    h1: ({ children, id }) => (
      <h1 id={id} className="text-3xl font-bold mt-8 mb-4 scroll-mt-20">
        {children}
        <a
          href={`#${id}`}
          className="ml-2 text-blue-600 opacity-0 hover:opacity-100"
        >
          #
        </a>
      </h1>
    ),
    h2: ({ children, id }) => (
      <h2 id={id} className="text-2xl font-semibold mt-8 mb-4 scroll-mt-20">
        {children}
        <a
          href={`#${id}`}
          className="ml-2 text-blue-600 opacity-0 hover:opacity-100"
        >
          #
        </a>
      </h2>
    ),
    h3: ({ children, id }) => (
      <h3 id={id} className="text-xl font-semibold mt-6 mb-3 scroll-mt-16">
        {children}
        <a
          href={`#${id}`}
          className="ml-2 text-blue-600 opacity-0 hover:opacity-100"
        >
          #
        </a>
      </h3>
    ),
    // 引用块
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 my-4">
        {children}
      </blockquote>
    ),
    // 表格
    table: ({ children }) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full divide-y divide-gray-200">
          {children}
        </table>
      </div>
    ),
    // 警告框
    div: ({ className, children }) => {
      if (className?.includes('callout')) {
        const type = className.match(/callout-(\w+)/)?.[1];
        const styles = {
          note: 'bg-blue-50 border-blue-200 text-blue-800',
          tip: 'bg-yellow-50 border-yellow-200 text-yellow-800',
          warning: 'bg-red-50 border-red-200 text-red-800',
        };
        return (
          <div className={`p-4 rounded-lg border my-4 ${styles[type as keyof typeof styles] || 'note'}`}>
            {children}
          </div>
        );
      }
      return <div>{children}</div>;
    }
  };

  return (
    <ReactMarkdown
      components={components}
      rehypePlugins={[
        rehypeHighlight,
        rehypeSlug,
        rehypeAutolinkHeadings,
        [{ type: 'html', render: ({ children }) => <div>{children}</div> }]
      ]}
    >
      {content}
    </ReactMarkdown>
  );
}
```

### 18.4 讨论区功能

```typescript
// ============================================
// 讨论区组件
// ============================================

interface Comment {
  id: string;
  content: string;
  author: {
    id: string;
    username: string;
    avatar: string;
  };
  createdAt: Date;
  updatedAt?: Date;
  parentId?: string;
  replies?: Comment[];
  likes: number;
  isLiked: boolean;
}

export function DiscussionThread({ threadId }: { threadId: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [replyTo, setReplyTo] = useState<string | null>(null);

  const fetchComments = async () => {
    const response = await api.get(`/api/v1/discussions/${threadId}/comments`);
    setComments(response.data);
  };

  const handleSubmitComment = async (content: string) => {
    await api.post(`/api/v1/discussions/${threadId}/comments`, {
      content,
      parentId: replyTo || undefined
    });
    await fetchComments();
    setReplyTo(null);
  };

  const handleLike = async (commentId: string) => {
    await api.post(`/api/v1/comments/${commentId}/like`);
    await fetchComments();
  };

  return (
    <div className="discussion-thread">
      {/* 评论输入框 */}
      <CommentForm onSubmit={handleSubmitComment} />

      {/* 评论列表 */}
      <div className="mt-6 space-y-4">
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            onReply={setReplyTo}
            onLike={handleLike}
          />
        ))}
      </div>
    </div  );
}
```

---

## 十九、管理后台系统

### 19.1 后台首页

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    管理后台                                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  📊 数据概览                                        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  实时统计                                             │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │  总用户数   │ │  总Skills  │ │  待审核   │ │ 今日   │ │  │
│  │  │   12,345   │ │    5,678   │ │   23      │ │ 新增   │ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │  +156 今日 │ │  +89 今日 │ │  ↓ 45%    │ │ +12.5% │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  快捷操作                                             │  │
│  │  [ 审核 Skills ]  [ 管理用户 ]  [ 系统设置 ]              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  待办事项                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ ⚠️   Skills 待审核：23                              │  │  │
│  │  │ ⚠️  用户举报：5                                     │  │  │
│  │  │ ⚠️  提现申请：2                                     │  │  │  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  数据趋势图表                                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  用户增长曲线 (近30天)                               │  │  │
│  │  │  ╭───────────────────────────────────────╮          │  │  │
│  │  │  │    ╭──────╮──────╮──────╮──────╮          │  │ │
│  │  │    │     │      │      │      │          │  │ │ │
│  │  │    │ 12k  │ 12k  │ 11k  │ 11k  │          │  │ │ │
│  │  │    └──────┴──────┴──────┴──────┴          │  │ │ │
│  │  └─────────────────────────────────────────────────────┘  │  │ │  │ │
│  │  └─────────────────────────────────────────────────────┘  │  │ │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 19.2 自动爬虫系统

#### 19.2.1 爬虫架构

```python
# ============================================
# 自动爬虫系统
# ============================================

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import random

class SkillCrawler:
    """Skills 自动爬虫"""

    def __init__(self):
        self.sources = [
            'github.com',
            'gitee.com',
            'gitlab.com',
            'npmjs.com',
            'pypi.org'
        ]
        self.ai_reviewer = AIReviewService()

    async def search_skills(self, keywords: List[str]) -> List[dict]:
        """搜索潜在的 Skills"""
        skills_found = []

        for keyword in keywords:
            # GitHub 搜索
            github_skills = await self.search_github(keyword)
            skills_found.extend(github_skills)

            # NPM 搜索
            npm_skills = await self.search_npm(keyword)
            skills_found.extend(npm_skills)

            # PyPI 搜索
            pypi_skills = await self.search_pypi(keyword)
            skills_found.extend(pypi_skills)

        return skills_found

    async def search_github(self, keyword: str) -> List[dict]:
        """搜索 GitHub 仓库"""
        url = f"https://api.github.com/search/repositories?q={keyword}+language:python"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self.parse_github_repo(data)
        return []

    def parse_github_repo(self, data: dict) -> List[dict]:
        """解析 GitHub 仓库信息为 Skill"""
        skills = []

        for item in data.get('items', [])[:10]:  # 限制数量
            if item.get('stargazers', 0) >= 50:  # 只爬取热门项目
                skill = {
                    'name': item['name'],
                    'description': item['description'],
                    'category': self.guess_category(item),
                    'url': item['html_url'],
                    'stars': item['stargazers'],
                    'language': item['language'],
                    'source': 'github'
                }
                skills.append(skill)

        return skills

    def guess_category(self, repo: dict) -> str:
        """根据仓库信息猜测分类"""
        topics = repo.get('topics', [])
        language = repo.get('language', '').lower()

        # 基于语言和主题猜测
        if language in ['python', 'javascript', 'java', 'go']:
            return 'tech'
        elif any(t in topics for t in ['design', 'ui', 'ux', 'frontend']):
            return 'design'
        elif any(t in topics for t in ['blog', 'cms', 'ecommerce']):
            return 'tech'
        elif any(t in topics for t in ['marketing', 'seo', 'analytics']):
            return 'marketing'
        else:
            return 'tech'

    async def process_and_create_skill(self, raw_skill: dict) -> dict:
        """处理并创建 Skill（自动流程）"""
        # 1. 清洗数据
        cleaned_skill = self.clean_skill_data(raw_skill)

        # 2. 生成随机假人身份
        fake_user = await self.generate_fake_user()

        # 3. 发送 AI 审核
        review_result = await self.ai_reviewer.review(cleaned_skill)

        # 4. 根据审核结果处理
        if review_result.approved:
            # 创建 Skill
            skill = await db.skills.create({
                **cleaned_skill,
                author_id: fake_user.id,
                status: 'approved',
                published_at: datetime.utcnow(),
                content_hash: self.generate_hash(cleaned_skill),
                platform_signature: self.sign_skill(cleaned_skill)
            })
            return skill
        else:
            # 进入待审核队列
            skill = await db.skills.create({
                **cleaned_skill,
                author_id: fake_user.id,
                status: 'reviewing'
            })
            return skill

    async def generate_fake_user(self) -> dict:
        """生成随机假人用户"""
        fake = self.fake.user()

        # 随机生成用户数据，避免重复
        username = f"{fake.first_name}{random.randint(1000, 9999)}"

        # 检查用户名是否存在，存在则重新生成
        while await db.users.find_by_username(username):
            username = f"{fake.first_name}{random.randint(1000, 9999)}"

        user = await db.users.create({
            username: username,
            email: f"{username}@temp-sillymd.com",
            password_hash = self.hash_password('default_password_123'),
            role: 'user',
            vendor_level: 'normal',
            is_active: True,
            is_verified: True,
            created_at: datetime.utcnow(),
            updated_at: datetime.utcnow()
        })

        return user

    async def run_crawler(self):
        """运行爬虫任务"""
        # 获取搜索关键词
        keywords = await self.get_trending_keywords()

        # 搜索 Skills
        skills = await self.search_skills(keywords)

        # 处理并创建
        for skill_data in skills:
            try:
                await self.process_and_create_skill(skill_data)
                # 随机延迟，避免操作过快
                await asyncio.sleep(random.uniform(5, 15))
            except Exception as e:
                logger.error(f"Failed to process skill: {e}")
                continue
```

#### 19.2.2 审核难度设置

```typescript
// ============================================
// 审核难度配置
// ============================================

interface ReviewDifficultyConfig {
  level: 'easy' | 'medium' | 'hard';
  autoApprovalThreshold: number; // 自动通过阈值 (0-1)
  aiModelCost: number; // AI 审核消耗的积分
  manualReviewRequired: boolean;
  randomApprovalRate: number; // 随机自动通过率 (0-1)
}

const REVIEW_DIFFICULTY_LEVELS: Record<string, ReviewDifficultyConfig> = {
  easy: {
    level: 'easy',
    autoApprovalThreshold: 0.7,  // 70% 自动通过
    aiModelCost: 1,
    manualReviewRequired: false,
    randomApprovalRate: 0.9  // 90% 随机通过
  },
  medium: {
    level: 'medium',
    autoApprovalThreshold: 0.3,  // 30% 自动通过
    aiModelCost: 3,
    manualReviewRequired: false,
    randomApprovalRate: 0.5  // 50% 随机通过
  },
  hard: {
    level: 'hard',
    autoApprovalThreshold: 0,    // 0% 自动通过
    aiModelCost: 10,
    manualReviewRequired: true, // 必须人工审核
    randomApprovalRate: 0.1  // 10% 随机通过
  }
};

// ============================================
// AI 审核控制器
// ============================================

export class AIReviewController {
  private config: ReviewDifficultyConfig;

  constructor(config: ReviewDifficultyConfig) {
    this.config = config;
  }

  async review(skill: dict): Promise<ReviewResult> {
    // 1. 基础格式检查
    const formatCheck = this.checkFormat(skill);

    // 2. 内容安全检查
    const safetyCheck = await this.checkSafety(skill);

    // 3. 专业性评估（根据难度调整）
    const qualityScore = this.assessQuality(skill);

    // 4. 综合评分
    const finalScore = (
      formatCheck.score * 0.2 +
      safetyCheck.score * 0.3 +
      qualityScore * 0.5
    );

    // 5. 根据难度决定是否自动通过
    if (finalScore >= this.config.autoApprovalThreshold) {
      // 随机决定是否真的审核（增加真实性）
      if (Math.random() < this.config.randomApprovalRate) {
        return {
          approved: true,
          reason: 'Auto-approved by system',
          confidence: finalScore
        };
      }
    }

    // 进入人工审核
    return {
      approved: false,
      reason: 'Requires manual review',
      confidence: finalScore,
      suggestions: [
        '完善文档描述',
        '添加使用示例',
        '补充技术细节'
      ]
    };
  }
}
```

#### 19.2.3 手动审核管理

```typescript
// ============================================
// 审核队列管理
// ============================================

export function ReviewQueue() {
  const [queue, setQueue] = useState<ReviewItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);

  const fetchQueue = async () => {
    const response = await api.get('/admin/review/queue');
    setQueue(response.data);
  };

  const approveItem = async (id: string, note?: string) => {
    await api.post(`/admin/review/${id}/approve`, { note });
    await fetchQueue();
  };

  const rejectItem = async (id: string, reason: string) => {
    await api.post(`/admin/review/${id}/reject`, { reason });
    await fetchQueue();
  };

  return (
    <div className="review-queue">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">审核队列</h2>
        <DifficultySelector
          value={currentDifficulty}
          onChange={(level) => setDifficulty(level)}
        />
        <div className="text-sm text-gray-600">
          待审核: {queue.length} 项
        </div>
      </div>

      {/* 审核列表 */}
      <div className="space-y-4">
        {queue.map((item) => (
          <ReviewQueueItem
            key={item.id}
            item={item}
            isSelected={selectedItem?.id === item.id}
            onSelect={setSelectedItem}
            onApprove={approveItem}
            onReject={rejectItem}
          />
        ))}
      </div>
    </div  );
}

// ============================================
// 审核项组件
// ============================================

interface ReviewQueueItemProps {
  item: ReviewItem;
  isSelected: boolean;
  onSelect: (item: ReviewItem) => void;
  onApprove: (id: string, note?: string) => void;
  onReject: (id: string, reason: string) => void;
}

function ReviewQueueItem({ item, isSelected, onSelect, onApprove, onReject }: ReviewQueueItemProps) {
  return (
    <div
      className={`
        p-6 border rounded-lg cursor-pointer transition-all
        ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
      `}
      onClick={() => onSelect(item)}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold">{item.skill_name}</h3>
            <span className={`px-2 py-1 text-xs rounded ${
              item.source === 'github' ? 'bg-gray-800 text-white' :
              item.source === 'npm' ? 'bg-red-600 text-white' :
              'bg-blue-600 text-white'
            }`}>
              {item.source}
            </span>
            <span className={`px-2 py-1 text-xs rounded ${
              item.category === 'tech' ? 'bg-purple-100 text-purple-800' :
              item.category === 'design' ? 'bg-pink-100 text-pink-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {item.category}
            </span>
          </div>

          <p className="text-sm text-gray-600 line-clamp-2">
            {item.description}
          </p>

          {/* AI 评估 */}
          <div className="mt-3 p-3 bg-white rounded border">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">AI 评估</span>
              <span className="text-sm text-gray-500">
                置信度: {item.confidence}%
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">格式:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-green-500 rounded-full"
                    style={{ width: `${item.scores.format * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{item.scores.format}%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">安全:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-green-500 rounded-full"
                    style={{ width: `${item.scores.safety * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{item.scores.safety}%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">质量:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-yellow-500 rounded-full"
                    style={{ width: `${item.scores.quality * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{item.scores.quality}%</span>
              </div>
            </div>
          </div>

          {/* 来源信息 */}
          <div className="mt-3 text-xs text-gray-500">
            来源: {item.source_url}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-2">
          <button
            onClick={() => onApprove(item.id)}
            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
          >
            ✓ 通过
          </button>
          <button
            onClick={() => {
              const reason = prompt('请输入驳回原因：');
              if (reason) {
                onReject(item.id, reason);
              }
            }}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            ✗ 驳回
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 19.3 系统设置

#### 19.3.1 平台配置

```typescript
// ============================================
// 平台配置界面
// ============================================

interface PlatformConfig {
  basic: {
    siteName: string;
    siteUrl: string;
    supportEmail: string;
  };
  transaction: {
    platformFeeRate: number; // 0.15 - 0.20
    minWithdrawal: number; // 500 Points
    withdrawalCycle: 'weekly' | 'monthly';
    exchangeRate: number; // 100 Points = ? CNY
  };
  review: {
    difficulty: 'easy' | 'medium' | 'hard';
    autoPublishEnabled: boolean; // 是否启用自动发布
    autoPublishMinStars: number; // 自动发布最低星数
  };
  content: {
    allowPublicRegistration: boolean;
    requireEmailVerification: boolean;
    enableGuestBrowsing: boolean;
  };
  crawling: {
    enabled: boolean;
    sources: ('github' | 'gitee' | 'gitlab' | 'npm' | 'pypi')[];
    maxDailyImports: number; // 每日最大导入数
    importInterval: number; // 导入间隔(秒)
  };
}

export function PlatformSettings() {
  const [config, setConfig] = useState<PlatformConfig>({
    basic: {
      siteName: 'SillyMD Skills',
      siteUrl: 'https://sillymd.com',
      supportEmail: 'support@sillymd.com'
    },
    transaction: {
      platformFeeRate: 0.15,
      minWithdrawal: 500,
      withdrawalCycle: 'weekly',
      exchangeRate: 10
    },
    review: {
      difficulty: 'medium',
      autoPublishEnabled: true,
      autoPublishMinStars: 3
    },
    content: {
      allowPublicRegistration: true,
      requireEmailVerification: true,
      enableGuestBrowsing: true
    },
    crawling: {
      enabled: true,
      sources: ['github', 'gitee', 'npm', 'pypi'],
      maxDailyImports: 50,
      importInterval: 600
    }
  });

  const handleSaveConfig = async () => {
    await api.put('/admin/config', config);
    toast.success('配置已保存');
  };

  return (
    <div className="platform-settings space-y-6">
      <h1 className="text-2xl font-bold">平台设置</h1>

      {/* 基础设置 */}
      <SettingsSection title="基础设置">
        <FormField label="站点名称">
          <input
            type="text"
            value={config.basic.siteName}
            onChange={(e) => setConfig({
              ...config,
              basic: { ...config.basic, siteName: e.target.value }
            })}
          />
        </FormField>
        <FormField label="支持邮箱">
          <input
            type="email"
            value={config.basic.supportEmail}
            onChange={(e) => setConfig({
              ...config,
              basic: { ...config.basic, supportEmail: e.target.value }
            })}
          />
        </FormField>
      </SettingsSection>

      {/* 交易设置 */}
      <SettingsSection title="交易设置">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="平台手续费率 (%)">
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={config.transaction.platformFeeRate * 100}
              onChange={(e) => setConfig({
                ...config,
                transaction: {
                  ...config.transaction,
                  platformFeeRate: Number(e.target.value) / 100
                }
              })}
            />
          </FormField>
          <FormField label="最低提现金额">
            <input
              type="number"
              min="0"
              value={config.transaction.minWithdrawal}
              onChange={(e) => setConfig({
                ...config,
                transaction: {
                  ...config.transaction,
                  minWithdrawal: Number(e.target.value)
                }
              })}
            />
          </FormField>
          <FormField label="汇率 (100 Points = ? 元)">
            <input
              type="number"
              min="0"
              value={config.transaction.exchangeRate}
              onChange={(e) => setConfig({
                ...config,
                transaction: {
                  ...config.transaction,
                  exchangeRate: Number(e.target.value)
                }
              })}
            />
          </FormField>
        </div>
      </SettingsSection>

      {/* 审核设置 */}
      <SettingsSection title="审核设置">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="审核难度">
            <select
              value={config.review.difficulty}
              onChange={(e) => setConfig({
                ...config,
                review: { ...config.review, difficulty: e.target.value as 'easy' | 'medium' | 'hard' }
              })}
            >
              <option value="easy">简单（高通过率）</option>
              <option value="medium">中等（平衡）</option>
              <option value="hard">严格（需人工审核）</option>
            </select>
          </FormField>
          <FormField label="自动发布最低星数">
            <input
              type="number"
              min="1"
              max="5"
              value={config.review.autoPublishMinStars}
              onChange={(e) => setConfig({
                ...config,
                review: {
                  ...config.review,
                  autoPublishMinStars: Number(e.target.value)
                }
              })}
            />
          </FormField>
        </div>
        <div className="mt-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={config.review.autoPublishEnabled}
              onChange={(e) => setConfig({
                ...config,
                review: {
                  ...config.review,
                  autoPublishEnabled: e.target.checked
                }
              })}
              className="mr-2"
            />
            <span>启用自动发布（高星数自动通过）</span>
          </label>
        </div>
      </SettingsSection>

      {/* 爬虫设置 */}
      <SettingsSection title="爬虫设置">
        <div className="space-y-4">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.crawling.enabled}
                onChange={(e) => setConfig({
                  ...config,
                  crawling: {
                    ...config.crawling,
                    enabled: e.target.checked
                  }
                })}
                className="mr-2"
              />
              <span>启用自动爬虫</span>
            </label>
          </div>

          {config.crawling.enabled && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <FormField label="每日最大导入数">
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={config.crawling.maxDailyImports}
                    onChange={(e) => setConfig({
                      ...config,
                      crawling: {
                        ...config.crawling,
                        maxDailyImports: Number(e.target.value)
                      }
                    })}
                  />
                </FormField>
                <FormField label="导入间隔（秒）">
                  <input
                    type="number"
                    min="60"
                    max="3600"
                    value={config.crawling.importInterval}
                    onChange={(e) => setConfig({
                      ...config,
                      crawling: {
                        ...config.crawling,
                        importInterval: Number(e.target.value)
                      }
                    })}
                  />
                </FormField>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">数据源</label>
                <div className="space-y-2">
                  {['github', 'gitee', 'npm', 'pypi'].map((source) => (
                    <label key={source} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config.crawling.sources.includes(source)}
                        onChange={(e) => {
                          const newSources = e.target.checked
                            ? [...config.crawling.sources, source]
                            : config.crawling.sources.filter(s => s !== source);
                          setConfig({
                            ...config,
                            crawling: {
                              ...config.crawling,
                              sources: newSources
                            }
                          });
                        }}
                        className="mr-2"
                      />
                      <span className="capitalize">{source}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </SettingsSection>

      {/* 保存按钮 */}
      <div className="flex justify-end">
        <Button onClick={handleSaveConfig} className="px-6 py-2 bg-blue-600 text-white rounded-lg">
          保存设置
        </Button>
      </div>
    </div>
  );
}

// ============================================
// 字段表单组件
// ============================================

interface FormFieldProps {
  label: string;
  children: React.ReactNode;
}

function FormField({ label, children }: FormFieldProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      {children}
    </div>
  );
}

function SettingsSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      {children}
    </section>
  );
}
```

### 19.4 白名单/黑名单

```typescript
// ============================================
// 白名单/黑名单管理
// ============================================

interface ListItem {
  id: string;
  type: 'whitelist' | 'blacklist';
  category: 'user' | 'keyword' | 'domain' | 'ip';
  value: string;
  note?: string;
  createdAt: Date;
  createdBy: string;
}

export function ListManagement() {
  const [activeTab, setActiveTab] = useState<'whitelist' | 'blacklist'>('whitelist');
  const [items, setItems] = useState<ListItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'user' | 'keyword' | 'domain' | 'ip'>('all');

  const fetchItems = async () => {
    const response = await api.get(`/admin/lists/${activeTab}`, {
      filter
    });
    setItems(response.data);
  };

  const addItem = async (value: string, category: string, note?: string) => {
    await api.post('/admin/lists', {
      type: activeTab,
      category,
      value,
      note
    });
    await fetchItems();
    toast.success(`已添加到${activeTab === 'whitelist' ? '白名单' : '黑名单'}`);
  };

  const removeItem = async (id: string) => {
    await api.delete(`/admin/lists/${id}`);
    await fetchItems();
    toast.success('已移除');
  };

  return (
    <div className="list-management">
      {/* 标签页 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="whitelist">白名单</TabsTrigger>
          <TabsTrigger value="blacklist">黑名单</TabsTrigger>
        </TabsList>

        {/* 过滤器 */}
        <div className="mt-4 mb-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="all">全部</option>
            <option value="user">用户</option>
            <option value="keyword">关键词</option>
            <option value="domain">域名</option>
            <option value="ip">IP地址</option>
          </select>
        </div>

        {/* 添加表单 */}
        <div className="grid grid-cols-4 gap-2 mb-6">
          <input
            type="text"
            placeholder="输入值..."
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                addItem((e.target as HTMLInputElement).value, filter);
              }
            }}
            className="px-3 py-2 border rounded-md"
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="all">类型</option>
            <option value="user">用户</option>
            <option value="keyword">关键词</option>
            <option value="domain">域名</option>
            <option value="ip">IP</option>
          </select>
          <button
            onClick={() => addItem('', filter)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            添加
          </button>
        </div>

        {/* 列表 */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  类型
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  值
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  类别
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  备注
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  创建时间
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded ${
                      item.type === 'whitelist' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {item.type === 'whitelist' ? '白名单' : '黑名单'}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-sm">
                    {item.value}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded ${
                      item.category === 'user' ? 'bg-blue-100 text-blue-800' :
                      item.category === 'keyword' ? 'bg-purple-100 text-purple-800' :
                      item.category === 'domain' ? 'bg-orange-100 text-orange-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.category === 'user' ? '用户' :
                       item.category === 'keyword' ? '关键词' :
                       item.category === 'domain' ? '域名' :
                       item.category === 'ip' ? 'IP' : ''}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {item.note || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(item.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Tabs>
    </div  );
}
```

---

**文档版本**: v14.0
**最后更新**: 2026-02-01
**维护团队**: SillyMD Team

---

*"承认自己有时候挺傻的，这是智慧的开始。"*
