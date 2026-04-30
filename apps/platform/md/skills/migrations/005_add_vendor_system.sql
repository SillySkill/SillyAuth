-- ============================================
-- 迁移脚本: 添加供应商系统
-- 版本: 005
-- 描述: 创建供应商申请和认证相关表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '005') THEN
        RAISE EXCEPTION 'Migration 005 already applied';
    END IF;
END
$$;

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
    FOREIGN KEY (user_id) REFERENCES users(id)
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

CREATE INDEX idx_vendor_applications_user_id ON vendor_applications(user_id);
CREATE INDEX idx_vendor_applications_status ON vendor_applications(application_status);

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

CREATE INDEX idx_vendor_verifications_user_id ON vendor_verifications(user_id);
CREATE INDEX idx_vendor_verifications_status ON vendor_verifications(verification_status);

-- ============================================
-- 供应商等级表
-- ============================================
CREATE TABLE vendor_tiers (
    id BIGSERIAL PRIMARY KEY,
    tier_name VARCHAR(50) UNIQUE NOT NULL,
    tier_level INT NOT NULL,
    min_sales INT NOT NULL DEFAULT 0,
    min_products INT NOT NULL DEFAULT 0,
    min_rating NUMERIC(3,2) NOT NULL DEFAULT 0.00,
    commission_rate NUMERIC(4,3) NOT NULL,
    benefits JSONB,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE vendor_tiers IS '供应商等级配置表';
COMMENT ON COLUMN vendor_tiers.id IS '等级 ID';
COMMENT ON COLUMN vendor_tiers.tier_name IS '等级名称';
COMMENT ON COLUMN vendor_tiers.tier_level IS '等级级别（1-5）';
COMMENT ON COLUMN vendor_tiers.min_sales IS '最低销售额要求';
COMMENT ON COLUMN vendor_tiers.min_products IS '最低产品数量要求';
COMMENT ON COLUMN vendor_tiers.min_rating IS '最低评分要求';
COMMENT ON COLUMN vendor_tiers.commission_rate IS '平台抽成比例';
COMMENT ON COLUMN vendor_tiers.benefits IS '等级权益（JSONB 格式）';
COMMENT ON COLUMN vendor_tiers.description IS '等级描述';
COMMENT ON COLUMN vendor_tiers.is_active IS '是否启用';
COMMENT ON COLUMN vendor_tiers.created_at IS '创建时间';
COMMENT ON COLUMN vendor_tiers.updated_at IS '更新时间';

CREATE TRIGGER update_vendor_tiers_updated_at BEFORE UPDATE ON vendor_tiers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_vendor_tiers_tier_level ON vendor_tiers(tier_level);
CREATE INDEX idx_vendor_tiers_is_active ON vendor_tiers(is_active);

-- 初始化等级数据
INSERT INTO vendor_tiers (tier_name, tier_level, min_sales, min_products, min_rating, commission_rate, benefits, description) VALUES
('青铜供应商', 1, 0, 1, 0.00, 0.150, '{"badge": "bronze", "support": "basic"}', '入门级供应商'),
('白银供应商', 2, 5000, 5, 4.00, 0.140, '{"badge": "silver", "support": "priority"}', '进阶级供应商'),
('黄金供应商', 3, 20000, 10, 4.50, 0.130, '{"badge": "gold", "support": "dedicated"}', '优质供应商'),
('铂金供应商', 4, 100000, 20, 4.80, 0.120, '{"badge": "platinum", "support": "vip"}', '顶级供应商'),
('钻石供应商', 5, 500000, 50, 4.90, 0.100, '{"badge": "diamond", "support": "exclusive"}', '旗舰供应商');

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('005', '添加供应商系统', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除初始化数据
DELETE FROM vendor_tiers WHERE tier_level IN (1, 2, 3, 4, 5);

-- 删除索引
DROP INDEX IF EXISTS idx_vendor_tiers_is_active;
DROP INDEX IF EXISTS idx_vendor_tiers_tier_level;
DROP INDEX IF EXISTS idx_vendor_verifications_status;
DROP INDEX IF EXISTS idx_vendor_verifications_user_id;
DROP INDEX IF EXISTS idx_vendor_applications_status;
DROP INDEX IF EXISTS idx_vendor_applications_user_id;

-- 删除触发器
DROP TRIGGER IF EXISTS update_vendor_tiers_updated_at ON vendor_tiers;
DROP TRIGGER IF EXISTS update_vendor_verifications_updated_at ON vendor_verifications;
DROP TRIGGER IF EXISTS update_vendor_applications_updated_at ON vendor_applications;

-- 删除表
DROP TABLE IF EXISTS vendor_tiers;
DROP TABLE IF EXISTS vendor_verifications;
DROP TABLE IF EXISTS vendor_applications;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '005';

COMMIT;
*/
