# 第二章：技术架构

> 本文档详细描述 SillyMD 平台的技术选型、系统架构和核心设计。

## 2.1 技术栈选型

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

## 2.2 系统架构图

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

## 2.3 SDK 设计

### 2.3.1 NPM 包

```bash
# 核心 SDK
npm install @sillymd/sdk

# MCP Server (用于 Claude Code)
npm install @sillymd/mcp-server

# CLI 工具
npm install -g @sillymd/cli
```

### 2.3.2 SDK 使用示例

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

## 2.4 数据库设计

### 2.4.1 PostgreSQL 类型定义

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
CREATE TYPE project_status AS ENUM ('planned', 'in_progress', 'on_hold', 'completed', 'cancelled');
CREATE TYPE conversation_type AS ENUM ('direct', 'group');
CREATE TYPE message_type AS ENUM ('text', 'image', 'file', 'system');
CREATE TYPE conversation_participant_role AS ENUM ('owner', 'admin', 'member');
CREATE TYPE verification_type AS ENUM ('register', 'change', 'bind');

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
    preferred_language VARCHAR(10) DEFAULT 'zh-CN',
    theme_preference VARCHAR(20) DEFAULT 'tech-blue',
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 用户表注释
COMMENT ON TABLE users IS '平台用户主表，存储所有用户信息';
COMMENT ON COLUMN users.id IS '用户唯一标识';
COMMENT ON COLUMN users.username IS '用户名（3-50字符，唯一）';
COMMENT ON COLUMN users.email IS '用户邮箱（唯一）';
COMMENT ON COLUMN users.password_hash IS '密码哈希值（bcrypt）';
COMMENT ON COLUMN users.role IS '用户角色：user=普通用户, vendor=供应商, admin=管理员';
COMMENT ON COLUMN users.vendor_level IS '供应商等级：normal=普通, premium=高级, gold=金牌';
COMMENT ON COLUMN users.ai_points IS 'AI 积分余额（用于 AI 审核等付费功能）';
COMMENT ON COLUMN users.avatar_url IS '头像 URL';
COMMENT ON COLUMN users.bio IS '用户简介';
COMMENT ON COLUMN users.preferred_language IS '偏好语言：zh-CN=中文简体, en=English, ja=日语, ko=韩语';
COMMENT ON COLUMN users.theme_preference IS '主题偏好：tech-blue, cyber-purple, forest-green 等';
COMMENT ON COLUMN users.last_login_at IS '最后登录时间';
COMMENT ON COLUMN users.is_active IS '账户是否激活（可禁用但保留数据）';
COMMENT ON COLUMN users.is_verified IS '是否已验证邮箱/手机';
COMMENT ON COLUMN users.created_at IS '账户创建时间';
COMMENT ON COLUMN users.updated_at IS '最后更新时间（自动触发）';

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
-- 管理员表
-- ============================================
-- 注意: admin_users 表已移至 19-admin-backend.md
-- 管理员使用独立的登录系统，不依赖 users 表
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
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Skills 表注释
COMMENT ON TABLE skills IS 'Skills 主表，存储所有 AI Skills 的基础信息';
COMMENT ON COLUMN skills.id IS 'Skills 内部 ID';
COMMENT ON COLUMN skills.skill_id IS 'Skills 外部标识符（人类可读）';
COMMENT ON COLUMN skills.name IS 'Skills 名称（3-200字符）';
COMMENT ON COLUMN skills.description IS 'Skills 详细描述';
COMMENT ON COLUMN skills.author_id IS '作者 ID（关联 users 表）';
COMMENT ON COLUMN skills.category IS 'Skills 分类：tech/product/design/marketing/ops';
COMMENT ON COLUMN skills.type IS 'Skills 类型：free=免费, commercial=商用';
COMMENT ON COLUMN skills.version IS '语义化版本号（SemVer）';
COMMENT ON COLUMN skills.status IS 'Skills 状态：draft/reviewing/approved/rejected';
COMMENT ON COLUMN skills.is_deleted IS '软删除标记（TRUE=已删除）';
COMMENT ON COLUMN skills.is_featured IS '是否精选（首页推荐）';
COMMENT ON COLUMN skills.published_at IS '首次发布时间';
COMMENT ON COLUMN skills.repo_url IS '代码仓库 URL';
COMMENT ON COLUMN skills.dependencies IS '依赖关系（JSONB 格式）';
COMMENT ON COLUMN skills.content_hash IS '内容 SHA256 哈希（数字存证）';
COMMENT ON COLUMN skills.platform_signature IS '平台数字签名';
COMMENT ON COLUMN skills.author_signature IS '作者数字签名';
COMMENT ON COLUMN skills.price IS '当前价格（积分）';
COMMENT ON COLUMN skills.license_types IS '支持的授权类型（JSONB 数组）';
COMMENT ON COLUMN skills.original_price IS '原价（用于促销）';
COMMENT ON COLUMN skills.promo_until IS '促销结束时间';
COMMENT ON COLUMN skills.view_count IS '浏览次数';
COMMENT ON COLUMN skills.download_count IS '下载次数';
COMMENT ON COLUMN skills.favorite_count IS '收藏次数';
COMMENT ON COLUMN skills.rating_avg IS '平均评分（0-5）';
COMMENT ON COLUMN skills.rating_count IS '评分人数';

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
    content TEXT NOT NULL,
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

COMMENT ON TABLE skill_favorites IS 'Skills 收藏关系表';
COMMENT ON COLUMN skill_favorites.user_id IS '收藏者 ID';
COMMENT ON COLUMN skill_favorites.skill_id IS '被收藏的 Skill ID';
COMMENT ON COLUMN skill_favorites.created_at IS '收藏时间';

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

COMMENT ON TABLE skill_comments IS 'Skills 评论表（支持嵌套回复）';
COMMENT ON COLUMN skill_comments.id IS '评论 ID';
COMMENT ON COLUMN skill_comments.skill_id IS '被评论的 Skill ID';
COMMENT ON COLUMN skill_comments.user_id IS '评论者 ID';
COMMENT ON COLUMN skill_comments.parent_id IS '父评论 ID（NULL=顶层评论）';
COMMENT ON COLUMN skill_comments.content IS '评论内容';
COMMENT ON COLUMN skill_comments.is_deleted IS '软删除标记';
COMMENT ON COLUMN skill_comments.created_at IS '评论时间';
COMMENT ON COLUMN skill_comments.updated_at IS '最后编辑时间';

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

COMMENT ON TABLE teams IS '团队主表，用于多领域协作';
COMMENT ON COLUMN teams.id IS '团队 ID';
COMMENT ON COLUMN teams.team_name IS '团队名称（3-100字符，唯一）';
COMMENT ON COLUMN teams.team_slug IS '团队 URL 标识符（唯一）';
COMMENT ON COLUMN teams.owner_id IS '团队所有者 ID';
COMMENT ON COLUMN teams.description IS '团队简介';
COMMENT ON COLUMN teams.avatar_url IS '团队头像 URL';
COMMENT ON COLUMN teams.member_count IS '成员数量（冗余字段）';
COMMENT ON COLUMN teams.is_active IS '团队是否激活';
COMMENT ON COLUMN teams.created_at IS '团队创建时间';
COMMENT ON COLUMN teams.updated_at IS '最后更新时间';

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

COMMENT ON TABLE team_members IS '团队成员关系表';
COMMENT ON COLUMN team_members.team_id IS '团队 ID';
COMMENT ON COLUMN team_members.user_id IS '成员用户 ID';
COMMENT ON COLUMN team_members.role IS '角色：owner=admin, member=普通成员, viewer=访客';
COMMENT ON COLUMN team_members.joined_at IS '加入时间';

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
    project_status VARCHAR(20) DEFAULT 'planned',
    progress INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    UNIQUE (team_id, project_slug)
);

-- 项目状态枚举
CREATE TYPE project_status AS ENUM ('planned', 'in_progress', 'on_hold', 'completed', 'cancelled');
ALTER TABLE team_projects
    ALTER COLUMN project_status TYPE project_status USING project_status::project_status;

COMMENT ON TABLE team_projects IS '团队项目表';
COMMENT ON COLUMN team_projects.id IS '项目 ID';
COMMENT ON COLUMN team_projects.team_id IS '所属团队 ID';
COMMENT ON COLUMN team_projects.project_name IS '项目名称';
COMMENT ON COLUMN team_projects.project_slug IS '项目 URL 标识符';
COMMENT ON COLUMN team_projects.description IS '项目描述';
COMMENT ON COLUMN team_projects.owner_id IS '项目负责人 ID';
COMMENT ON COLUMN team_projects.project_status IS '项目状态：planned=计划中, in_progress=进行中, on_hold=暂停, completed=已完成, cancelled=已取消';
COMMENT ON COLUMN team_projects.progress IS '项目进度百分比（0-100）';
COMMENT ON COLUMN team_projects.is_active IS '是否激活';
COMMENT ON COLUMN team_projects.created_at IS '创建时间';
COMMENT ON COLUMN team_projects.updated_at IS '最后更新时间';

CREATE TRIGGER update_team_projects_updated_at BEFORE UPDATE ON team_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 项目状态索引
CREATE INDEX idx_team_projects_status ON team_projects(project_status);
CREATE INDEX idx_team_projects_team_id ON team_projects(team_id);

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

COMMENT ON TABLE licenses IS '商用 Skills 授权许可证表';
COMMENT ON COLUMN licenses.id IS '授权 ID';
COMMENT ON COLUMN licenses.license_id IS '授权许可证编号（人类可读）';
COMMENT ON COLUMN licenses.license_key IS '授权密钥（用于 SDK 验证）';
COMMENT ON COLUMN licenses.skill_id IS '被授权的 Skill ID';
COMMENT ON COLUMN licenses.buyer_id IS '购买者 ID';
COMMENT ON COLUMN licenses.vendor_id IS '供应商 ID';
COMMENT ON COLUMN licenses.license_type IS '授权类型：personal=个人, team=团队, enterprise=企业';
COMMENT ON COLUMN licenses.price IS '授权价格（积分）';
COMMENT ON COLUMN licenses.is_active IS '授权是否有效';
COMMENT ON COLUMN licenses.expires_at IS '授权过期时间（NULL=永久）';
COMMENT ON COLUMN licenses.created_at IS '授权购买时间';

-- ============================================
-- 积分交易表
-- ============================================
CREATE TABLE point_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    transaction_type transaction_type NOT NULL,
    amount INT NOT NULL,
    balance_after INT NOT NULL,
    description TEXT,
    related_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE point_transactions IS '用户积分交易流水表';
COMMENT ON COLUMN point_transactions.id IS '交易 ID';
COMMENT ON COLUMN point_transactions.user_id IS '用户 ID';
COMMENT ON COLUMN point_transactions.transaction_type IS '交易类型：recharge=充值, purchase=消费, earning=收入, refund=退款, withdraw=提现';
COMMENT ON COLUMN point_transactions.amount IS '变动金额（正数=增加，负数=减少）';
COMMENT ON COLUMN point_transactions.balance_after IS '交易后余额';
COMMENT ON COLUMN point_transactions.description IS '交易说明';
COMMENT ON COLUMN point_transactions.related_id IS '关联业务 ID（如订单 ID、授权 ID 等）';
COMMENT ON COLUMN point_transactions.created_at IS '交易时间';
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
-- 对话表 (消息系统)
-- ============================================
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    conversation_type conversation_type NOT NULL,
    title VARCHAR(200),
    created_by BIGINT NOT NULL,
    is_group BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

COMMENT ON TABLE conversations IS '对话表（单聊和群聊）';
COMMENT ON COLUMN conversations.id IS '对话 ID';
COMMENT ON COLUMN conversations.conversation_type IS '对话类型：direct=单聊, group=群聊';
COMMENT ON COLUMN conversations.title IS '对话标题（群聊时使用）';
COMMENT ON COLUMN conversations.created_by IS '创建者 ID';
COMMENT ON COLUMN conversations.is_group IS '是否为群聊';
COMMENT ON COLUMN conversations.is_active IS '对话是否激活';
COMMENT ON COLUMN conversations.last_message_at IS '最后消息时间';
COMMENT ON COLUMN conversations.created_at IS '创建时间';
COMMENT ON COLUMN conversations.updated_at IS '最后更新时间';

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 对话参与者表
-- ============================================
CREATE TABLE conversation_participants (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role conversation_participant_role DEFAULT 'member',
    has_unread BOOLEAN DEFAULT FALSE,
    last_read_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (conversation_id, user_id)
);

COMMENT ON TABLE conversation_participants IS '对话参与者关系表';
COMMENT ON COLUMN conversation_participants.id IS '参与者 ID';
COMMENT ON COLUMN conversation_participants.conversation_id IS '对话 ID';
COMMENT ON COLUMN conversation_participants.user_id IS '用户 ID';
COMMENT ON COLUMN conversation_participants.role IS '角色：owner=所有者, admin=管理员, member=成员';
COMMENT ON COLUMN conversation_participants.has_unread IS '是否有未读消息';
COMMENT ON COLUMN conversation_participants.last_read_at IS '最后阅读时间';
COMMENT ON COLUMN conversation_participants.joined_at IS '加入时间';

-- ============================================
-- 消息表
-- ============================================
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    sender_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    message_type message_type DEFAULT 'text',
    reply_to_id BIGINT,
    attachments JSONB,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (reply_to_id) REFERENCES messages(id) ON DELETE SET NULL
);

COMMENT ON TABLE messages IS '消息表';
COMMENT ON COLUMN messages.id IS '消息 ID';
COMMENT ON COLUMN messages.conversation_id IS '对话 ID';
COMMENT ON COLUMN messages.sender_id IS '发送者 ID';
COMMENT ON COLUMN messages.content IS '消息内容';
COMMENT ON COLUMN messages.message_type IS '消息类型：text=文本, image=图片, file=文件, system=系统消息';
COMMENT ON COLUMN messages.reply_to_id IS '回复的消息 ID';
COMMENT ON COLUMN messages.attachments IS '附件信息（JSONB 格式）';
COMMENT ON COLUMN messages.is_deleted IS '是否已删除';
COMMENT ON COLUMN messages.is_system IS '是否为系统消息';
COMMENT ON COLUMN messages.created_at IS '发送时间';

-- 消息系统索引
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_messages_sender_created ON messages(sender_id, created_at DESC);
CREATE INDEX idx_conversation_participants_conversation ON conversation_participants(conversation_id);
CREATE INDEX idx_conversation_participants_user ON conversation_participants(user_id);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);
CREATE INDEX idx_conversations_created_by ON conversations(created_by);

-- ============================================
-- 供应商申请表
-- ============================================
CREATE TABLE vendor_applications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    id_card_number VARCHAR(200) NOT NULL,
    professional_field VARCHAR(50),
    years_of_experience INT,
    bio TEXT,
    portfolio_urls JSONB,
    application_status VARCHAR(20) DEFAULT 'pending',
    reviewed_by BIGINT,
    reviewed_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewed_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

COMMENT ON TABLE vendor_applications IS '供应商申请表';
COMMENT ON COLUMN vendor_applications.id IS '申请 ID';
COMMENT ON COLUMN vendor_applications.user_id IS '申请用户 ID';
COMMENT ON COLUMN vendor_applications.real_name IS '真实姓名';
COMMENT ON COLUMN vendor_applications.id_card_number IS '身份证号（加密存储）';
COMMENT ON COLUMN vendor_applications.professional_field IS '专业领域';
COMMENT ON COLUMN vendor_applications.years_of_experience IS '从业年限';
COMMENT ON COLUMN vendor_applications.bio IS '个人简介';
COMMENT ON COLUMN vendor_applications.portfolio_urls IS '作品集 URL 列表（JSONB 数组）';
COMMENT ON COLUMN vendor_applications.application_status IS '申请状态：pending=待审核, reviewing=审核中, approved=已通过, rejected=已拒绝';
COMMENT ON COLUMN vendor_applications.reviewed_by IS '审核人 ID（管理员）';
COMMENT ON COLUMN vendor_applications.reviewed_at IS '审核时间';
COMMENT ON COLUMN vendor_applications.rejection_reason IS '拒绝原因';
COMMENT ON COLUMN vendor_applications.created_at IS '申请时间';
COMMENT ON COLUMN vendor_applications.updated_at IS '最后更新时间';

CREATE TRIGGER update_vendor_applications_updated_at BEFORE UPDATE ON vendor_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 供应商申请索引
CREATE INDEX idx_vendor_applications_user_id ON vendor_applications(user_id);
CREATE INDEX idx_vendor_applications_status ON vendor_applications(application_status);
CREATE INDEX idx_vendor_applications_reviewed_by ON vendor_applications(reviewed_by);

-- ============================================
-- 供应商实名认证表
-- ============================================
CREATE TABLE vendor_verifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    id_card_name VARCHAR(100) NOT NULL,
    id_card_number VARCHAR(200) NOT NULL,
    id_card_front_url VARCHAR(500),
    id_card_back_url VARCHAR(500),
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_at TIMESTAMPTZ,
    verification_note TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE vendor_verifications IS '供应商实名认证表';
COMMENT ON COLUMN vendor_verifications.id IS '认证 ID';
COMMENT ON COLUMN vendor_verifications.user_id IS '用户 ID';
COMMENT ON COLUMN vendor_verifications.id_card_name IS '身份证姓名';
COMMENT ON COLUMN vendor_verifications.id_card_number IS '身份证号（加密存储）';
COMMENT ON COLUMN vendor_verifications.id_card_front_url IS '身份证正面照片 URL';
COMMENT ON COLUMN vendor_verifications.id_card_back_url IS '身份证背面照片 URL';
COMMENT ON COLUMN vendor_verifications.verification_status IS '认证状态：pending=待审核, approved=已通过, rejected=已拒绝';
COMMENT ON COLUMN vendor_verifications.verified_at IS '认证通过时间';
COMMENT ON COLUMN vendor_verifications.verification_note IS '认证备注';
COMMENT ON COLUMN vendor_verifications.created_at IS '创建时间';
COMMENT ON COLUMN vendor_verifications.updated_at IS '最后更新时间';

CREATE TRIGGER update_vendor_verifications_updated_at BEFORE UPDATE ON vendor_verifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 用户偏好设置表
-- ============================================
CREATE TABLE user_preferences (
    user_id BIGINT PRIMARY KEY,
    theme VARCHAR(20) DEFAULT 'tech-blue',
    language VARCHAR(10) DEFAULT 'zh-CN',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT FALSE,
    auto_play_videos BOOLEAN DEFAULT FALSE,
    data_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE user_preferences IS '用户偏好设置表';
COMMENT ON COLUMN user_preferences.user_id IS '用户 ID';
COMMENT ON COLUMN user_preferences.theme IS '主题：tech-blue, cyber-purple, forest-green, dark-mode 等';
COMMENT ON COLUMN user_preferences.language IS '语言：zh-CN=中文简体, en=English, ja=日语, ko=韩语';
COMMENT ON COLUMN user_preferences.notifications_enabled IS '是否启用通知';
COMMENT ON COLUMN user_preferences.email_notifications IS '是否启用邮件通知';
COMMENT ON COLUMN user_preferences.push_notifications IS '是否启用推送通知';
COMMENT ON COLUMN user_preferences.auto_play_videos IS '是否自动播放视频';
COMMENT ON COLUMN user_preferences.data_consent IS '是否同意数据收集';
COMMENT ON COLUMN user_preferences.created_at IS '创建时间';
COMMENT ON COLUMN user_preferences.updated_at IS '最后更新时间';

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 密码重置令牌表
-- ============================================
CREATE TABLE password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE password_reset_tokens IS '密码重置令牌表';
COMMENT ON COLUMN password_reset_tokens.id IS '令牌 ID';
COMMENT ON COLUMN password_reset_tokens.user_id IS '用户 ID';
COMMENT ON COLUMN password_reset_tokens.token IS '重置令牌（唯一）';
COMMENT ON COLUMN password_reset_tokens.expires_at IS '过期时间';
COMMENT ON COLUMN password_reset_tokens.used_at IS '使用时间';
COMMENT ON COLUMN password_reset_tokens.client_ip IS '客户端 IP';
COMMENT ON COLUMN password_reset_tokens.user_agent IS '用户代理';
COMMENT ON COLUMN password_reset_tokens.created_at IS '创建时间';

-- 密码重置令牌索引
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- ============================================
-- 邮箱验证表
-- ============================================
CREATE TABLE email_verifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    email VARCHAR(255) NOT NULL,
    verification_type verification_type NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE email_verifications IS '邮箱验证表';
COMMENT ON COLUMN email_verifications.id IS '验证 ID';
COMMENT ON COLUMN email_verifications.user_id IS '用户 ID';
COMMENT ON COLUMN email_verifications.email IS '待验证邮箱';
COMMENT ON COLUMN email_verifications.verification_type IS '验证类型：register=注册, change=更改邮箱, bind=绑定邮箱';
COMMENT ON COLUMN email_verifications.token IS '验证令牌（唯一）';
COMMENT ON COLUMN email_verifications.expires_at IS '过期时间';
COMMENT ON COLUMN email_verifications.verified_at IS '验证时间';
COMMENT ON COLUMN email_verifications.client_ip IS '客户端 IP';
COMMENT ON COLUMN email_verifications.created_at IS '创建时间';

-- 邮箱验证索引
CREATE INDEX idx_email_verifications_user_id ON email_verifications(user_id);
CREATE INDEX idx_email_verifications_email ON email_verifications(email);
CREATE INDEX idx_email_verifications_token ON email_verifications(token);
CREATE INDEX idx_email_verifications_expires_at ON email_verifications(expires_at);

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

### 2.4.2 缓存策略设计

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

## 2.5 Meilisearch 集成

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

## 2.6 WebSocket 实时通知

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

## 2.7 限流与降级策略

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

## 2.8 API 版本控制

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

## 2.9 RBAC 权限控制

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

## 2.10 分布式追踪

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
