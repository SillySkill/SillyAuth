-- ============================================
-- 迁移脚本: 添加运营统计表
-- 版本: 007
-- 描述: 创建页面访问统计和用户活动日志表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '007') THEN
        RAISE EXCEPTION 'Migration 007 already applied';
    END IF;
END
$$;

-- ============================================
-- 页面访问统计表
-- ============================================
CREATE TABLE page_views (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    page_path VARCHAR(500) NOT NULL,
    session_id VARCHAR(255),
    view_duration INT,
    referrer VARCHAR(500),
    user_agent VARCHAR(500),
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE page_views IS '页面访问统计表';
COMMENT ON COLUMN page_views.id IS '访问 ID';
COMMENT ON COLUMN page_views.user_id IS '用户 ID（NULL=匿名用户）';
COMMENT ON COLUMN page_views.page_path IS '页面路径';
COMMENT ON COLUMN page_views.session_id IS '会话 ID';
COMMENT ON COLUMN page_views.view_duration IS '浏览时长（秒）';
COMMENT ON COLUMN page_views.referrer IS '来源页面';
COMMENT ON COLUMN page_views.user_agent IS '用户代理';
COMMENT ON COLUMN page_views.ip_address IS 'IP 地址';
COMMENT ON COLUMN page_views.created_at IS '访问时间';

CREATE INDEX idx_page_views_user_created ON page_views(user_id, created_at DESC);
CREATE INDEX idx_page_views_path_created ON page_views(page_path, created_at DESC);
CREATE INDEX idx_page_views_session_id ON page_views(session_id);
CREATE INDEX idx_page_views_created_at ON page_views(created_at DESC);

-- ============================================
-- 用户活动日志表
-- ============================================
CREATE TABLE user_activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    activity_title VARCHAR(255) NOT NULL,
    activity_detail TEXT,
    metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE user_activity_logs IS '用户活动日志表';
COMMENT ON COLUMN user_activity_logs.id IS '日志 ID';
COMMENT ON COLUMN user_activity_logs.user_id IS '用户 ID';
COMMENT ON COLUMN user_activity_logs.activity_type IS '活动类型：login, logout, view, create, update, delete, download';
COMMENT ON COLUMN user_activity_logs.resource_type IS '资源类型：skill, team, project, user';
COMMENT ON COLUMN user_activity_logs.resource_id IS '资源 ID';
COMMENT ON COLUMN user_activity_logs.activity_title IS '活动标题';
COMMENT ON COLUMN user_activity_logs.activity_detail IS '活动详情';
COMMENT ON COLUMN user_activity_logs.metadata IS '额外元数据（JSONB 格式）';
COMMENT ON COLUMN user_activity_logs.ip_address IS 'IP 地址';
COMMENT ON COLUMN user_activity_logs.created_at IS '活动时间';

CREATE INDEX idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX idx_user_activity_logs_type ON user_activity_logs(activity_type);
CREATE INDEX idx_user_activity_logs_resource ON user_activity_logs(resource_type, resource_id);
CREATE INDEX idx_user_activity_logs_created_at ON user_activity_logs(created_at DESC);

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('007', '添加运营统计表', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_user_activity_logs_created_at;
DROP INDEX IF EXISTS idx_user_activity_logs_resource;
DROP INDEX IF EXISTS idx_user_activity_logs_type;
DROP INDEX IF EXISTS idx_user_activity_logs_user_id;
DROP INDEX IF EXISTS idx_page_views_created_at;
DROP INDEX IF EXISTS idx_page_views_session_id;
DROP INDEX IF EXISTS idx_page_views_path_created;
DROP INDEX IF EXISTS idx_page_views_user_created;

-- 删除表
DROP TABLE IF EXISTS user_activity_logs;
DROP TABLE IF EXISTS page_views;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '007';

COMMIT;
*/
