-- ============================================
-- 迁移脚本: 添加商用交易表
-- 版本: 008
-- 描述: 创建订单、支付、提现等交易相关表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '008') THEN
        RAISE EXCEPTION 'Migration 008 already applied';
    END IF;
END
$$;

-- ============================================
-- 商用交易枚举类型
-- ============================================
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'completed', 'cancelled', 'refunded');
CREATE TYPE payment_method_type AS ENUM ('balance', 'alipay', 'wechat', 'bank');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'success', 'failed', 'cancelled');
CREATE TYPE withdrawal_method AS ENUM ('alipay', 'wechat', 'bank');
CREATE TYPE withdrawal_status AS ENUM ('pending', 'processing', 'completed', 'rejected', 'cancelled');

-- ============================================
-- 订单表
-- ============================================
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    buyer_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    license_type license_type NOT NULL DEFAULT 'personal',
    quantity INT NOT NULL DEFAULT 1,
    unit_price INT NOT NULL,
    total_amount INT NOT NULL,
    platform_fee INT NOT NULL,
    seller_income INT NOT NULL,
    status order_status NOT NULL DEFAULT 'pending',
    payment_method payment_method_type,
    paid_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    refund_amount INT DEFAULT 0,
    refund_reason TEXT,
    refunded_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (seller_id) REFERENCES users(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

COMMENT ON TABLE orders IS '商用 Skills 订单主表';
COMMENT ON COLUMN orders.id IS '订单 ID';
COMMENT ON COLUMN orders.order_no IS '订单编号（唯一）';
COMMENT ON COLUMN orders.buyer_id IS '购买者 ID';
COMMENT ON COLUMN orders.seller_id IS '供应商 ID';
COMMENT ON COLUMN orders.skill_id IS 'Skill ID';
COMMENT ON COLUMN orders.license_type IS '授权类型：personal/team/enterprise';
COMMENT ON COLUMN orders.quantity IS '购买数量';
COMMENT ON COLUMN orders.unit_price IS '单价（积分）';
COMMENT ON COLUMN orders.total_amount IS '订单总金额（积分）';
COMMENT ON COLUMN orders.platform_fee IS '平台手续费（积分）';
COMMENT ON COLUMN orders.seller_income IS '供应商收入（积分）';
COMMENT ON COLUMN orders.status IS '订单状态：pending/paid/completed/cancelled/refunded';
COMMENT ON COLUMN orders.payment_method IS '支付方式：balance/alipay/wechat/bank';
COMMENT ON COLUMN orders.paid_at IS '支付时间';
COMMENT ON COLUMN orders.completed_at IS '完成时间';
COMMENT ON COLUMN orders.cancelled_at IS '取消时间';
COMMENT ON COLUMN orders.refund_amount IS '退款金额（积分）';
COMMENT ON COLUMN orders.refund_reason IS '退款原因';
COMMENT ON COLUMN orders.refunded_at IS '退款时间';
COMMENT ON COLUMN orders.client_ip IS '客户端 IP';
COMMENT ON COLUMN orders.user_agent IS '用户代理';

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_orders_buyer_id ON orders(buyer_id);
CREATE INDEX idx_orders_seller_id ON orders(seller_id);
CREATE INDEX idx_orders_skill_id ON orders(skill_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ============================================
-- 支付记录表
-- ============================================
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    payment_no VARCHAR(32) UNIQUE NOT NULL,
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    payment_method payment_method_type NOT NULL,
    payment_channel VARCHAR(50),
    transaction_id VARCHAR(100),
    status payment_status NOT NULL DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    failure_reason TEXT,
    callback_data JSONB,
    client_ip VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

COMMENT ON TABLE payments IS '支付记录表';

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_payments_payment_no ON payments(payment_no);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- ============================================
-- 提现申请表
-- ============================================
CREATE TABLE withdrawal_requests (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    fee INT DEFAULT 0,
    actual_amount INT NOT NULL,
    method withdrawal_method NOT NULL,
    account_info JSONB NOT NULL,
    withdrawal_no VARCHAR(32) UNIQUE,
    exchange_rate NUMERIC(10,4) NOT NULL DEFAULT 1.0,
    cny_amount NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    account_name VARCHAR(100) NOT NULL DEFAULT '',
    status withdrawal_status NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(100),
    rejection_reason TEXT,
    processed_by BIGINT,
    processed_at TIMESTAMPTZ,
    admin_note TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

COMMENT ON TABLE withdrawal_requests IS '提现申请表';

CREATE TRIGGER update_withdrawal_requests_updated_at BEFORE UPDATE ON withdrawal_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_withdrawal_requests_withdrawal_no ON withdrawal_requests(withdrawal_no);
CREATE INDEX idx_withdrawal_requests_user_id ON withdrawal_requests(user_id);
CREATE INDEX idx_withdrawal_requests_status ON withdrawal_requests(status);

-- ============================================
-- 佣金记录表
-- ============================================
CREATE TABLE commission_records (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    amount INT NOT NULL,
    rate NUMERIC(4,3) NOT NULL,
    tier_id BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    available_at TIMESTAMPTZ,
    withdrawn_at TIMESTAMPTZ,
    withdrawal_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (seller_id) REFERENCES users(id),
    FOREIGN KEY (tier_id) REFERENCES vendor_tiers(id)
);

CREATE INDEX idx_commission_records_seller_id ON commission_records(seller_id);
CREATE INDEX idx_commission_records_status ON commission_records(status);
CREATE INDEX idx_commission_records_created_at ON commission_records(created_at);

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('008', '添加商用交易表', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_commission_records_created_at;
DROP INDEX IF EXISTS idx_commission_records_status;
DROP INDEX IF EXISTS idx_commission_records_seller_id;
DROP INDEX IF EXISTS idx_withdrawal_requests_status;
DROP INDEX IF EXISTS idx_withdrawal_requests_user_id;
DROP INDEX IF EXISTS idx_withdrawal_requests_withdrawal_no;
DROP INDEX IF EXISTS idx_payments_created_at;
DROP INDEX IF EXISTS idx_payments_status;
DROP INDEX IF EXISTS idx_payments_user_id;
DROP INDEX IF EXISTS idx_payments_order_id;
DROP INDEX IF EXISTS idx_payments_payment_no;
DROP INDEX IF EXISTS idx_orders_created_at;
DROP INDEX IF EXISTS idx_orders_order_no;
DROP INDEX IF EXISTS idx_orders_status;
DROP INDEX IF EXISTS idx_orders_skill_id;
DROP INDEX IF EXISTS idx_orders_seller_id;
DROP INDEX IF EXISTS idx_orders_buyer_id;

-- 删除触发器
DROP TRIGGER IF EXISTS update_withdrawal_requests_updated_at ON withdrawal_requests;
DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;

-- 删除表
DROP TABLE IF EXISTS commission_records;
DROP TABLE IF EXISTS withdrawal_requests;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;

-- 删除枚举类型
DROP TYPE IF EXISTS withdrawal_status;
DROP TYPE IF EXISTS withdrawal_method;
DROP TYPE IF EXISTS payment_status;
DROP TYPE IF EXISTS payment_method_type;
DROP TYPE IF EXISTS order_status;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '008';

COMMIT;
*/
