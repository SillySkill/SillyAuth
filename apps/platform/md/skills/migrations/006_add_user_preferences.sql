-- ============================================
-- 迁移脚本: 添加用户偏好和认证
-- 版本: 006
-- 描述: 创建用户偏好设置和认证相关表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '006') THEN
        RAISE EXCEPTION 'Migration 006 already applied';
    END IF;
END
$$;

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

CREATE INDEX idx_email_verifications_user_id ON email_verifications(user_id);
CREATE INDEX idx_email_verifications_email ON email_verifications(email);
CREATE INDEX idx_email_verifications_token ON email_verifications(token);
CREATE INDEX idx_email_verifications_expires_at ON email_verifications(expires_at);

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('006', '添加用户偏好和认证', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_email_verifications_expires_at;
DROP INDEX IF EXISTS idx_email_verifications_token;
DROP INDEX IF EXISTS idx_email_verifications_email;
DROP INDEX IF EXISTS idx_email_verifications_user_id;
DROP INDEX IF EXISTS idx_password_reset_tokens_expires_at;
DROP INDEX IF EXISTS idx_password_reset_tokens_token;
DROP INDEX IF EXISTS idx_password_reset_tokens_user_id;

-- 删除触发器
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;

-- 删除表
DROP TABLE IF EXISTS email_verifications;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS user_preferences;

-- 删除枚举类型
DROP TYPE IF EXISTS verification_type;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '006';

COMMIT;
*/
