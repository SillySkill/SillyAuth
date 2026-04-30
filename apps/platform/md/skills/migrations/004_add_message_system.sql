-- ============================================
-- 迁移脚本: 添加消息系统
-- 版本: 004
-- 描述: 创建对话和消息相关表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '004') THEN
        RAISE EXCEPTION 'Migration 004 already applied';
    END IF;
END
$$;

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

CREATE INDEX idx_conversations_created_by ON conversations(created_by);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);

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

CREATE INDEX idx_conversation_participants_conversation ON conversation_participants(conversation_id);
CREATE INDEX idx_conversation_participants_user ON conversation_participants(user_id);

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

CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_messages_sender_created ON messages(sender_id, created_at DESC);

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('004', '添加消息系统', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_messages_sender_created;
DROP INDEX IF EXISTS idx_messages_conversation_created;
DROP INDEX IF EXISTS idx_conversation_participants_user;
DROP INDEX IF EXISTS idx_conversation_participants_conversation;
DROP INDEX IF EXISTS idx_conversations_last_message;
DROP INDEX IF EXISTS idx_conversations_created_by;

-- 删除触发器
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;

-- 删除表
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversation_participants;
DROP TABLE IF EXISTS conversations;

-- 删除枚举类型
DROP TYPE IF EXISTS conversation_participant_role;
DROP TYPE IF EXISTS message_type;
DROP TYPE IF EXISTS conversation_type;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '004';

COMMIT;
*/
