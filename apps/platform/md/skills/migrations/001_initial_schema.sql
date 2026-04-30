-- ============================================
-- 迁移脚本: 初始化数据库架构
-- 版本: 001
-- 描述: 创建核心枚举类型和核心表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'schema_migrations') THEN
        IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '001') THEN
            RAISE EXCEPTION 'Migration 001 already applied';
        END IF;
    END IF;
END
$$;

-- 创建迁移版本表（如果不存在）
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rollback_available BOOLEAN DEFAULT TRUE,
    checksum VARCHAR(64)
);

-- ============================================
-- 枚举类型定义
-- ============================================

-- 用户相关
CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');
CREATE TYPE vendor_level AS ENUM ('normal', 'premium', 'gold');

-- Skills 相关
CREATE TYPE skill_category AS ENUM ('tech', 'product', 'design', 'marketing', 'ops');
CREATE TYPE skill_type AS ENUM ('free', 'commercial');
CREATE TYPE skill_status AS ENUM ('draft', 'reviewing', 'approved', 'rejected');

-- 团队相关
CREATE TYPE team_role AS ENUM ('owner', 'admin', 'member', 'viewer');
CREATE TYPE project_status AS ENUM ('planned', 'in_progress', 'on_hold', 'completed', 'cancelled');

-- 授权相关
CREATE TYPE license_type AS ENUM ('personal', 'team', 'enterprise');

-- 交易相关
CREATE TYPE transaction_type AS ENUM ('recharge', 'purchase', 'earning', 'refund', 'withdraw');

-- 通知相关
CREATE TYPE notification_type AS ENUM ('system', 'skill_update', 'comment', 'license', 'achievement', 'team');

-- 消息系统
CREATE TYPE conversation_type AS ENUM ('direct', 'group');
CREATE TYPE message_type AS ENUM ('text', 'image', 'file', 'system');
CREATE TYPE conversation_participant_role AS ENUM ('owner', 'admin', 'member');

-- 认证相关
CREATE TYPE verification_type AS ENUM ('register', 'change', 'bind');

-- ============================================
-- 自动更新 updated_at 函数
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 用户表索引
CREATE INDEX idx_users_role ON users(role) WHERE is_active = TRUE;
CREATE INDEX idx_users_email ON users(email);

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
    rating_avg NUMERIC(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

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

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Skills 表索引
CREATE INDEX idx_skills_category_type_status ON skills(category, type, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_skills_author_status ON skills(author_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_skills_published_featured ON skills(published_at DESC) WHERE is_featured = TRUE AND status = 'approved';
CREATE INDEX idx_skills_skill_id ON skills(skill_id);

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

COMMENT ON TABLE skill_versions IS 'Skills 版本历史表';
COMMENT ON COLUMN skill_versions.id IS '版本 ID';
COMMENT ON COLUMN skill_versions.skill_id IS 'Skills ID';
COMMENT ON COLUMN skill_versions.version IS '版本号';
COMMENT ON COLUMN skill_versions.content IS '版本内容（压缩存储）';
COMMENT ON COLUMN skill_versions.content_hash IS '内容 SHA256 哈希';
COMMENT ON COLUMN skill_versions.commit_message IS '提交说明';
COMMENT ON COLUMN skill_versions.author_id IS '提交作者 ID';
COMMENT ON COLUMN skill_versions.created_at IS '创建时间';

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

COMMENT ON TABLE skill_dependencies IS 'Skills 依赖关系表';
COMMENT ON COLUMN skill_dependencies.skill_id IS 'Skills ID';
COMMENT ON COLUMN skill_dependencies.depends_on_skill_id IS '依赖的 Skills ID';
COMMENT ON COLUMN skill_dependencies.version_constraint IS '版本约束（如 >=1.0.0）';
COMMENT ON COLUMN skill_dependencies.dependency_type IS '依赖类型：required=必需, optional=可选';
COMMENT ON COLUMN skill_dependencies.created_at IS '创建时间';

CREATE INDEX idx_skill_dependencies_skill_id ON skill_dependencies(skill_id);

-- ============================================
-- 标签表
-- ============================================
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tags IS '标签主表';
COMMENT ON COLUMN tags.id IS '标签 ID';
COMMENT ON COLUMN tags.name IS '标签名称（唯一）';
COMMENT ON COLUMN tags.usage_count IS '使用次数（冗余字段）';
COMMENT ON COLUMN tags.created_at IS '创建时间';

CREATE TABLE skill_tags (
    skill_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (skill_id, tag_id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

COMMENT ON TABLE skill_tags IS 'Skills-标签关联表';
COMMENT ON COLUMN skill_tags.skill_id IS 'Skills ID';
COMMENT ON COLUMN skill_tags.tag_id IS '标签 ID';
COMMENT ON COLUMN skill_tags.created_at IS '关联时间';

CREATE INDEX idx_skill_tags_tag_id ON skill_tags(tag_id);

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

CREATE INDEX idx_skill_favorites_user_id ON skill_favorites(user_id);
CREATE INDEX idx_skill_favorites_skill_id ON skill_favorites(skill_id);

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

CREATE INDEX idx_skill_comments_skill_id ON skill_comments(skill_id);
CREATE INDEX idx_skill_comments_user_id ON skill_comments(user_id);

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
    ai_confidence NUMERIC(3,2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

COMMENT ON TABLE reviews IS 'Skills 审核记录表';
COMMENT ON COLUMN reviews.id IS '审核 ID';
COMMENT ON COLUMN reviews.skill_id IS '被审核的 Skill ID';
COMMENT ON COLUMN reviews.reviewer_id IS '审核人 ID';
COMMENT ON COLUMN reviews.stage IS '审核阶段：l1_auto, l2_ai, l3_manual';
COMMENT ON COLUMN reviews.result IS '审核结果：approved, rejected';
COMMENT ON COLUMN reviews.comments IS '审核意见';
COMMENT ON COLUMN reviews.ai_model IS 'AI 模型名称（如 deepseek-v3）';
COMMENT ON COLUMN reviews.ai_confidence IS 'AI 置信度（0-1）';
COMMENT ON COLUMN reviews.created_at IS '审核时间';

CREATE INDEX idx_reviews_skill_id ON reviews(skill_id);
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);

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

COMMENT ON TABLE achievements IS '成就定义表';
COMMENT ON COLUMN achievements.id IS '成就 ID';
COMMENT ON COLUMN achievements.code IS '成就代码（唯一标识符）';
COMMENT ON COLUMN achievements.name IS '成就名称';
COMMENT ON COLUMN achievements.description IS '成就描述';
COMMENT ON COLUMN achievements.icon_url IS '成就图标 URL';
COMMENT ON COLUMN achievements.category IS '成就分类：skill, social, commerce';
COMMENT ON COLUMN achievements.xp_reward IS '经验值奖励';
COMMENT ON COLUMN achievements.points_reward IS '积分奖励';
COMMENT ON COLUMN achievements.created_at IS '创建时间';

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

COMMENT ON TABLE user_achievements IS '用户成就关联表';
COMMENT ON COLUMN user_achievements.id IS '关联 ID';
COMMENT ON COLUMN user_achievements.user_id IS '用户 ID';
COMMENT ON COLUMN user_achievements.achievement_id IS '成就 ID';
COMMENT ON COLUMN user_achievements.earned_at IS '获得时间';

CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);

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

CREATE INDEX idx_licenses_buyer_skill ON licenses(buyer_id, skill_id) WHERE is_active = TRUE;
CREATE INDEX idx_licenses_vendor ON licenses(vendor_id, created_at DESC) WHERE is_active = TRUE;
CREATE INDEX idx_licenses_license_key ON licenses(license_key);

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

CREATE INDEX idx_point_transactions_user_created ON point_transactions(user_id, created_at DESC);

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

COMMENT ON TABLE audit_logs IS '操作日志表';
COMMENT ON COLUMN audit_logs.id IS '日志 ID';
COMMENT ON COLUMN audit_logs.user_id IS '操作用户 ID';
COMMENT ON COLUMN audit_logs.action IS '操作类型：create, update, delete, login, logout';
COMMENT ON COLUMN audit_logs.resource_type IS '资源类型：skill, team, user';
COMMENT ON COLUMN audit_logs.resource_id IS '资源 ID';
COMMENT ON COLUMN audit_logs.ip_address IS '操作者 IP';
COMMENT ON COLUMN audit_logs.user_agent IS '用户代理';
COMMENT ON COLUMN audit_logs.metadata IS '额外元数据';
COMMENT ON COLUMN audit_logs.created_at IS '操作时间';

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

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

COMMENT ON TABLE notifications IS '消息通知表';
COMMENT ON COLUMN notifications.id IS '通知 ID';
COMMENT ON COLUMN notifications.user_id IS '接收用户 ID';
COMMENT ON COLUMN notifications.type IS '通知类型：system, skill_update, comment, license, achievement, team';
COMMENT ON COLUMN notifications.title IS '通知标题';
COMMENT ON COLUMN notifications.content IS '通知内容';
COMMENT ON COLUMN notifications.link_url IS '跳转链接';
COMMENT ON COLUMN notifications.is_read IS '是否已读';
COMMENT ON COLUMN notifications.created_at IS '创建时间';

CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read, created_at DESC);

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
    FOREIGN KEY (inviter_id) REFERENCES users(id)
);

COMMENT ON TABLE invitations IS '邀请记录表';
COMMENT ON COLUMN invitations.id IS '邀请 ID';
COMMENT ON COLUMN invitations.inviter_id IS '邀请人 ID';
COMMENT ON COLUMN invitations.invitee_email IS '被邀请人邮箱';
COMMENT ON COLUMN invitations.invite_code IS '邀请码（唯一）';
COMMENT ON COLUMN invitations.status IS '状态：pending=待接受, accepted=已接受, expired=已过期';
COMMENT ON COLUMN invitations.team_id IS '关联团队 ID';
COMMENT ON COLUMN invitations.reward_points IS '奖励积分';
COMMENT ON COLUMN invitations.expires_at IS '过期时间';
COMMENT ON COLUMN invitations.accepted_at IS '接受时间';
COMMENT ON COLUMN invitations.created_at IS '创建时间';

CREATE INDEX idx_invitations_invite_code ON invitations(invite_code);
CREATE INDEX idx_invitations_inviter_id ON invitations(inviter_id);

-- ============================================
-- 全文搜索索引
-- ============================================
CREATE INDEX idx_skills_fulltext ON skills
USING gin(to_tsvector('simple', name || ' ' || COALESCE(description, '')))
WHERE is_deleted = FALSE AND status = 'approved';

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('001', '初始化数据库架构（枚举类型和核心表）', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_skills_fulltext;
DROP INDEX IF EXISTS idx_invitations_inviter_id;
DROP INDEX IF EXISTS idx_invitations_invite_code;
DROP INDEX IF EXISTS idx_notifications_user_read;
DROP INDEX IF EXISTS idx_audit_logs_created_at;
DROP INDEX IF EXISTS idx_audit_logs_resource;
DROP INDEX IF EXISTS idx_audit_logs_user_id;
DROP INDEX IF EXISTS idx_point_transactions_user_created;
DROP INDEX IF EXISTS idx_licenses_license_key;
DROP INDEX IF EXISTS idx_licenses_vendor;
DROP INDEX IF EXISTS idx_licenses_buyer_skill;
DROP INDEX IF EXISTS idx_user_achievements_user_id;
DROP INDEX IF EXISTS idx_reviews_created_at;
DROP INDEX IF EXISTS idx_reviews_skill_id;
DROP INDEX IF EXISTS idx_skill_comments_user_id;
DROP INDEX IF EXISTS idx_skill_comments_skill_id;
DROP INDEX IF EXISTS idx_skill_favorites_skill_id;
DROP INDEX IF EXISTS idx_skill_favorites_user_id;
DROP INDEX IF EXISTS idx_skill_tags_tag_id;
DROP INDEX IF EXISTS idx_skill_dependencies_skill_id;
DROP INDEX IF EXISTS idx_skills_skill_id;
DROP INDEX IF EXISTS idx_skills_published_featured;
DROP INDEX IF EXISTS idx_skills_author_status;
DROP INDEX IF EXISTS idx_skills_category_type_status;
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_role;

-- 删除触发器
DROP TRIGGER IF EXISTS update_skill_comments_updated_at ON skill_comments;
DROP TRIGGER IF EXISTS update_skills_updated_at ON skills;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- 删除函数
DROP FUNCTION IF EXISTS update_updated_at_column();

-- 删除表（按依赖关系倒序）
DROP TABLE IF EXISTS invitations;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS point_transactions;
DROP TABLE IF EXISTS licenses;
DROP TABLE IF EXISTS user_achievements;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS skill_comments;
DROP TABLE IF EXISTS skill_favorites;
DROP TABLE IF EXISTS skill_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS skill_dependencies;
DROP TABLE IF EXISTS skill_versions;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS users;

-- 删除枚举类型（按依赖关系）
DROP TYPE IF EXISTS verification_type;
DROP TYPE IF EXISTS conversation_participant_role;
DROP TYPE IF EXISTS message_type;
DROP TYPE IF EXISTS conversation_type;
DROP TYPE IF EXISTS notification_type;
DROP TYPE IF EXISTS transaction_type;
DROP TYPE IF EXISTS license_type;
DROP TYPE IF EXISTS project_status;
DROP TYPE IF EXISTS team_role;
DROP TYPE IF EXISTS skill_status;
DROP TYPE IF EXISTS skill_type;
DROP TYPE IF EXISTS skill_category;
DROP TYPE IF EXISTS vendor_level;
DROP TYPE IF EXISTS user_role;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '001';

COMMIT;
*/
