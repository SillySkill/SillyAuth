-- ============================================
-- 迁移版本: 009
-- 描述: 添加外部应用集成 - AI活动秀文件上传记录表
-- 作者: System
-- 日期: 2026-02-05
-- ============================================

-- 开始事务
BEGIN;

-- 检查迁移是否已应用
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'schema_migrations') THEN
        IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '009') THEN
            RAISE NOTICE 'Migration 009 already applied, skipping...';
            RETURN;
        END IF;
    END IF;
END $$;

-- ============================================
-- 创建 upload_records 表
-- ============================================
CREATE TABLE IF NOT EXISTS upload_records (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(36) UNIQUE NOT NULL,
    filename VARCHAR(512) NOT NULL,
    stored_filename VARCHAR(512) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size >= 0),
    mime_type VARCHAR(128) NOT NULL,
    package_name VARCHAR(256) NOT NULL,
    module_name VARCHAR(64) NOT NULL,
    uploader_fingerprint VARCHAR(128),
    uploader_ip VARCHAR(45),
    uploader_user_agent TEXT,
    upload_time BIGINT NOT NULL CHECK (upload_time > 0),
    upload_status VARCHAR(16) NOT NULL CHECK (upload_status IN ('success', 'failed')),
    error_message TEXT,
    oss_url TEXT,
    CONSTRAINT chk_file_size CHECK (file_size >= 0),
    CONSTRAINT chk_upload_time CHECK (upload_time > 0)
);

-- ============================================
-- 创建索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_package_module ON upload_records(package_name, module_name);
CREATE INDEX IF NOT EXISTS idx_upload_time ON upload_records(upload_time DESC);
CREATE INDEX IF NOT EXISTS idx_fingerprint ON upload_records(uploader_fingerprint);
CREATE UNIQUE INDEX IF NOT EXISTS upload_records_file_id_key ON upload_records(file_id);

-- ============================================
-- 添加表注释
-- ============================================
COMMENT ON TABLE upload_records IS 'AI活动秀应用文件上传记录表';
COMMENT ON COLUMN upload_records.id IS '自增主键';
COMMENT ON COLUMN upload_records.file_id IS '文件唯一ID，UUID格式';
COMMENT ON COLUMN upload_records.filename IS '原始文件名';
COMMENT ON COLUMN upload_records.stored_filename IS '存储文件名，时间戳格式';
COMMENT ON COLUMN upload_records.file_path IS 'OSS相对路径';
COMMENT ON COLUMN upload_records.file_size IS '文件大小(字节)';
COMMENT ON COLUMN upload_records.mime_type IS 'MIME类型，如 image/jpeg';
COMMENT ON COLUMN upload_records.package_name IS '应用包名，如 com.jcoding.aiactivity';
COMMENT ON COLUMN upload_records.module_name IS '模块名，如 style/quiz/lottery';
COMMENT ON COLUMN upload_records.uploader_fingerprint IS '设备指纹(MD5前16位)';
COMMENT ON COLUMN upload_records.uploader_ip IS '上传者IP地址';
COMMENT ON COLUMN upload_records.uploader_user_agent IS 'User-Agent字符串';
COMMENT ON COLUMN upload_records.upload_time IS '上传时间(毫秒时间戳)';
COMMENT ON COLUMN upload_records.upload_status IS '状态：success=成功, failed=失败';
COMMENT ON COLUMN upload_records.error_message IS '错误信息(失败时记录)';
COMMENT ON COLUMN upload_records.oss_url IS 'OSS完整URL';

-- ============================================
-- 初始化示例数据（可选）
-- ============================================
-- 插入示例上传记录（用于测试）
INSERT INTO upload_records (
    file_id, filename, stored_filename, file_path, file_size, mime_type,
    package_name, module_name, uploader_fingerprint, uploader_ip, uploader_user_agent,
    upload_time, upload_status, oss_url
) VALUES
(
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test_photo.jpg',
    '1738754321234.jpg',
    'application/com.jcoding.aiactivity/style/1738754321234.jpg',
    1024000,
    'image/jpeg',
    'com.jcoding.aiactivity',
    'style',
    'a1b2c3d4e5f6g7h8',
    '192.168.1.100',
    'AIActivity/1.0.0 (Android 14)',
    1738754321234,
    'success',
    'https://oss.example.com/application/com.jcoding.aiactivity/style/1738754321234.jpg'
)
ON CONFLICT (file_id) DO NOTHING;

-- ============================================
-- 记录迁移历史
-- ============================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(10) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version, description, applied_at)
VALUES ('009', '添加外部应用集成 - AI活动秀文件上传记录表', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

-- 提交事务
COMMIT;

-- ============================================
-- 回滚脚本（如需回滚，请取消注释并执行）
-- ============================================
/*
BEGIN;

-- 删除表
DROP TABLE IF EXISTS upload_records CASCADE;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '009';

COMMIT;
*/
