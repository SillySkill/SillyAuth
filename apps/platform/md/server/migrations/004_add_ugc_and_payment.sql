-- ============================================
-- Migration 004: Add UGC and Payment System
-- Description: Add user submissions, AI moderation, and payment system
-- Author: SillyMD Team
-- Date: 2026-02-04
-- ============================================

-- ============================================
-- Table 1: user_submissions (用户提交内容表)
-- Purpose: Store user-submitted tutorials and resources awaiting review
-- ============================================
CREATE TABLE IF NOT EXISTS user_submissions (
    id BIGSERIAL PRIMARY KEY,

    -- User Info
    user_id BIGINT NOT NULL,
    username VARCHAR(100),

    -- Content Type
    content_type VARCHAR(20) NOT NULL,  -- tutorial, download

    -- Basic Info (for tutorials)
    title_zh_CN VARCHAR(200) NOT NULL,
    title_en VARCHAR(200),
    description_zh_CN TEXT,
    description_en TEXT,
    content_zh_CN TEXT,  -- Full content in Markdown/HTML
    content_en TEXT,

    -- Categorization
    category VARCHAR(50),
    subcategory VARCHAR(50),
    difficulty VARCHAR(20),  -- For tutorials
    platform VARCHAR(50),  -- For downloads
    version VARCHAR(50),  -- For downloads

    -- Media (for tutorials)
    thumbnail VARCHAR(500),
    video_url VARCHAR(500),
    video_type VARCHAR(20),
    video_duration INT,

    -- Files (for downloads)
    file_name VARCHAR(255),
    file_url VARCHAR(500),
    file_size BIGINT,
    file_type VARCHAR(50),
    file_checksum VARCHAR(100),
    github_url VARCHAR(500),

    -- Pricing
    is_paid BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) DEFAULT 0,  -- 价格（元）
    currency VARCHAR(10) DEFAULT 'CNY',
    discount_price DECIMAL(10,2),  -- 折扣价
    discount_until TIMESTAMPTZ,  -- 折扣截止时间

    -- Submit Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reviewing, approved, rejected
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Review Info
    reviewed_by BIGINT,
    reviewed_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- AI Moderation
    ai_review_status VARCHAR(20),  -- pending, passed, failed
    ai_review_score DECIMAL(5,2),  -- 0-100
    ai_review_feedback TEXT,

    -- Published Reference
    published_content_id BIGINT,  -- 转换为 tutorials 或 downloads 的 ID
    published_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_submissions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_submissions_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_user_submissions_published_id FOREIGN KEY (published_content_id) REFERENCES tutorials(id) ON DELETE SET NULL
);

CREATE INDEX idx_user_submissions_user_id ON user_submissions(user_id);
CREATE INDEX idx_user_submissions_content_type ON user_submissions(content_type);
CREATE INDEX idx_user_submissions_status ON user_submissions(status);
CREATE INDEX idx_user_submissions_ai_review_status ON user_submissions(ai_review_status);
CREATE INDEX idx_user_submissions_submitted_at ON user_submissions(submitted_at);
CREATE INDEX idx_user_submissions_is_paid ON user_submissions(is_paid);

CREATE TRIGGER update_user_submissions_updated_at
    BEFORE UPDATE ON user_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_submissions IS '用户提交内容表（待审核）';
COMMENT ON COLUMN user_submissions.content_type IS '内容类型: tutorial, download';
COMMENT ON COLUMN user_submissions.status IS '审核状态: pending, reviewing, approved, rejected';
COMMENT ON COLUMN user_submissions.is_paid IS '是否付费内容';
COMMENT ON COLUMN user_submissions.price IS '价格（元）';
COMMENT ON COLUMN user_submissions.ai_review_status IS 'AI审核状态: pending, passed, failed';
COMMENT ON COLUMN user_submissions.ai_review_score IS 'AI审核分数 (0-100)';


-- ============================================
-- Table 2: paid_products (付费产品表)
-- Purpose: Store pricing information for premium content
-- ============================================
CREATE TABLE IF NOT EXISTS paid_products (
    id BIGSERIAL PRIMARY KEY,

    -- Content Reference
    content_type VARCHAR(20) NOT NULL,  -- tutorial, download
    content_id BIGINT NOT NULL,  -- tutorials.id or downloads.id

    -- Product Info
    product_name VARCHAR(200) NOT NULL,
    product_description TEXT,

    -- Pricing
    is_free BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'CNY',

    -- Discount
    has_discount BOOLEAN DEFAULT FALSE,
    discount_type VARCHAR(20),  -- percentage, fixed
    discount_value DECIMAL(10,2),
    discount_price DECIMAL(10,2),
    discount_start TIMESTAMPTZ,
    discount_end TIMESTAMPTZ,

    -- Purchase Options
    one_time_purchase BOOLEAN DEFAULT TRUE,
    subscription_enabled BOOLEAN DEFAULT FALSE,
    subscription_price DECIMAL(10,2),  -- 月付价格
    subscription_period VARCHAR(20),  -- month, year

    -- Free Preview
    free_preview_enabled BOOLEAN DEFAULT FALSE,
    free_chapters INT DEFAULT 0,  -- 免费章节数
    free_percentage INT DEFAULT 10,  -- 免费内容百分比

    -- Revenue Sharing (for user-generated content)
    creator_id BIGINT,
    creator_share_percentage DECIMAL(5,2) DEFAULT 70.00,  -- 创作者分成比例
    platform_share_percentage DECIMAL(5,2) DEFAULT 30.00,  -- 平台分成比例

    -- Stats
    total_purchases INT DEFAULT 0,
    total_revenue DECIMAL(15,2) DEFAULT 0,
    net_revenue DECIMAL(15,2) DEFAULT 0,  -- 扣除平台分成后的收入

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_paid_products_creator_id FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_paid_products_content UNIQUE(content_type, content_id)
);

CREATE INDEX idx_paid_products_content_type ON paid_products(content_type, content_id);
CREATE INDEX idx_paid_products_creator_id ON paid_products(creator_id);
CREATE INDEX idx_paid_products_is_active ON paid_products(is_active);
CREATE INDEX idx_paid_products_is_free ON paid_products(is_free);
CREATE INDEX idx_paid_products_price ON paid_products(price);

CREATE TRIGGER update_paid_products_updated_at
    BEFORE UPDATE ON paid_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE paid_products IS '付费产品表';
COMMENT ON COLUMN paid_products.content_type IS '内容类型: tutorial, download';
COMMENT ON COLUMN paid_products.price IS '价格（元）';
COMMENT ON COLUMN paid_products.creator_share_percentage IS '创作者分成比例（%）';


-- ============================================
-- Table 3: orders (订单表)
-- Purpose: Store purchase orders
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,

    -- Order Info
    order_number VARCHAR(50) UNIQUE NOT NULL,  -- 订单号
    user_id BIGINT NOT NULL,

    -- Product Info
    content_type VARCHAR(20) NOT NULL,
    content_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(200) NOT NULL,

    -- Pricing
    original_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',

    -- Purchase Type
    purchase_type VARCHAR(20) DEFAULT 'one_time',  -- one_time, subscription
    subscription_period VARCHAR(20),  -- month, year

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, cancelled, refunded, expired
    payment_status VARCHAR(20) DEFAULT 'unpaid',  -- unpaid, processing, paid, failed, refunded

    -- Payment
    payment_method VARCHAR(50),  -- wechat, alipay, balance
    payment_transaction_id VARCHAR(200),

    -- Time
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,  -- 订单过期时间（订阅）

    CONSTRAINT fk_orders_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_orders_product_id FOREIGN KEY (product_id) REFERENCES paid_products(id) ON DELETE CASCADE
);

CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_content ON orders(content_type, content_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

COMMENT ON TABLE orders IS '订单表';
COMMENT ON COLUMN orders.order_number IS '订单号（唯一）';
COMMENT ON COLUMN orders.status IS '订单状态: pending, paid, cancelled, refunded, expired';
COMMENT ON COLUMN orders.payment_status IS '支付状态: unpaid, processing, paid, failed, refunded';


-- ============================================
-- Table 4: payment_records (支付记录表)
-- Purpose: Store payment transaction details
-- ============================================
CREATE TABLE IF NOT EXISTS payment_records (
    id BIGSERIAL PRIMARY KEY,

    -- References
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    order_number VARCHAR(50) NOT NULL,

    -- Payment Info
    payment_method VARCHAR(50) NOT NULL,  -- wechat, alipay, balance
    payment_channel VARCHAR(50),  -- wechat_app, wechat_web, alipay_app, alipay_web
    transaction_id VARCHAR(200) UNIQUE,  -- 第三方交易ID
    prepay_id VARCHAR(200),  -- 预支付ID（微信）

    -- Amount
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, success, failed, cancelled

    -- Callback
    notified_at TIMESTAMPTZ,  -- 支付回调时间
    callback_data JSONB,  -- 支付回调原始数据

    -- Refund
    refund_amount DECIMAL(10,2),
    refund_reason TEXT,
    refund_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payment_records_order_id FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_payment_records_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_payment_records_order_id ON payment_records(order_id);
CREATE INDEX idx_payment_records_user_id ON payment_records(user_id);
CREATE INDEX idx_payment_records_transaction_id ON payment_records(transaction_id);
CREATE INDEX idx_payment_records_status ON payment_records(status);
CREATE INDEX idx_payment_records_created_at ON payment_records(created_at);

CREATE TRIGGER update_payment_records_updated_at
    BEFORE UPDATE ON payment_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE payment_records IS '支付记录表';
COMMENT ON COLUMN payment_records.transaction_id IS '第三方交易ID（唯一）';


-- ============================================
-- Table 5: content_unlocks (内容解锁记录表)
-- Purpose: Track which users have unlocked which content
-- ============================================
CREATE TABLE IF NOT EXISTS content_unlocks (
    id BIGSERIAL PRIMARY KEY,

    -- User & Content
    user_id BIGINT NOT NULL,
    content_type VARCHAR(20) NOT NULL,  -- tutorial, download
    content_id BIGINT NOT NULL,

    -- Unlock Source
    unlock_source VARCHAR(50) NOT NULL,  -- purchase, subscription, free, admin_grant

    -- Order Reference
    order_id BIGINT,
    order_number VARCHAR(50),

    -- Access Period
    unlocked_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ,  -- 订阅到期时间（永久为NULL）

    CONSTRAINT fk_content_unlocks_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_content_unlocks_order_id FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    CONSTRAINT uq_content_unlocks_user_content UNIQUE(user_id, content_type, content_id)
);

CREATE INDEX idx_content_unlocks_user_id ON content_unlocks(user_id);
CREATE INDEX idx_content_unlocks_content ON content_unlocks(content_type, content_id);
CREATE INDEX idx_content_unlocks_expires_at ON content_unlocks(expires_at);

COMMENT ON TABLE content_unlocks IS '内容解锁记录表';
COMMENT ON COLUMN content_unlocks.unlock_source IS '解锁来源: purchase=购买, subscription=订阅, free=免费, admin_grant=管理员赠送';


-- ============================================
-- Alter existing tables: add paid content support
-- ============================================

-- Add paid content fields to tutorials
ALTER TABLE tutorials
    ADD COLUMN IF NOT EXISTS is_paid BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS price DECIMAL(10,2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'CNY',
    ADD COLUMN IF NOT EXISTS free_preview_enabled BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS free_chapters INT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_tutorials_is_paid ON tutorials(is_paid);
CREATE INDEX idx_tutorials_creator_id ON tutorials(creator_id);
CREATE INDEX idx_tutorials_price ON tutorials(price);

-- Add paid content fields to downloads
ALTER TABLE downloads
    ADD COLUMN IF NOT EXISTS is_paid BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS price DECIMAL(10,2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'CNY',
    ADD COLUMN IF NOT EXISTS free_preview_enabled BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_downloads_is_paid ON downloads(is_paid);
CREATE INDEX idx_downloads_creator_id ON downloads(creator_id);
CREATE INDEX idx_downloads_price ON downloads(price);


-- ============================================
-- Insert sample paid products
-- ============================================

INSERT INTO paid_products (content_type, content_id, product_name, is_free, price, creator_share_percentage) VALUES
('tutorial', 1, 'Claude Code 入门教程', FALSE, 29.99, 70.00),
('tutorial', 2, 'OpenClaw 高级指南', FALSE, 49.99, 70.00),
('download', 1, 'WSL2 安装包', TRUE, 0, NULL)
ON CONFLICT (content_type, content_id) DO NOTHING;


-- ============================================
-- Create helper functions
-- ============================================

-- Function: Generate order number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    order_num VARCHAR(50);
BEGIN
    -- Format: T + date + random (e.g., T20260204123456abc)
    SELECT 'T' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS') || substring(md5(random()::text), 1, 3)
    INTO order_num;

    RETURN order_num;
END;
$$ LANGUAGE plpgsql;


-- Function: Check if user has access to content
CREATE OR REPLACE FUNCTION check_content_access(
    p_user_id BIGINT,
    p_content_type VARCHAR,
    p_content_id BIGINT
) RETURNS BOOLEAN AS $$
DECLARE
    has_unlock BOOLEAN;
    is_free BOOLEAN;
BEGIN
    -- Check if user has unlocked this content
    SELECT EXISTS(
        SELECT 1 FROM content_unlocks
        WHERE user_id = p_user_id
          AND content_type = p_content_type
          AND content_id = p_content_id
          AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
    ) INTO has_unlock;

    IF has_unlock THEN
        RETURN TRUE;
    END IF;

    -- Check if content is free
    IF p_content_type = 'tutorial' THEN
        SELECT is_free INTO is_free FROM tutorials WHERE id = p_content_id;
    ELSIF p_content_type = 'download' THEN
        SELECT is_free INTO is_free FROM downloads WHERE id = p_content_id;
    END IF;

    RETURN COALESCE(is_free, FALSE);
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- Create views for admin dashboard
-- ============================================

-- View: Pending submissions queue
CREATE OR REPLACE VIEW v_pending_submissions AS
SELECT
    s.id,
    s.user_id,
    s.username,
    s.content_type,
    s.title_zh_CN,
    s.category,
    s.is_paid,
    s.price,
    s.status,
    s.ai_review_status,
    s.ai_review_score,
    s.submitted_at,
    u.email,
    u.avatar_url
FROM user_submissions s
LEFT JOIN users u ON s.user_id = u.id
WHERE s.status = 'pending'
ORDER BY s.submitted_at DESC;

COMMENT ON VIEW v_pending_submissions IS '待审核提交队列';


-- View: Revenue statistics
CREATE OR REPLACE VIEW v_revenue_stats AS
SELECT
    DATE_TRUNC('day', o.created_at) AS date,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status = 'paid' THEN 1 ELSE 0 END) AS paid_orders,
    COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.final_price ELSE 0 END), 0) AS total_revenue
FROM orders o
WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', o.created_at)
ORDER BY date DESC;

COMMENT ON VIEW v_revenue_stats IS '收入统计（最近30天）';


-- View: Creator earnings
CREATE OR REPLACE VIEW v_creator_earnings AS
SELECT
    p.creator_id,
    u.username,
    u.email,
    COUNT(DISTINCT p.id) AS total_products,
    SUM(p.total_purchases) AS total_sales,
    SUM(p.net_revenue) AS total_earnings,
    SUM(CASE WHEN p.created_at >= CURRENT_DATE - INTERVAL '7 days' THEN p.net_revenue ELSE 0 END) AS weekly_earnings
FROM paid_products p
LEFT JOIN users u ON p.creator_id = u.id
WHERE p.creator_id IS NOT NULL
GROUP BY p.creator_id, u.username, u.email
ORDER BY total_earnings DESC;

COMMENT ON VIEW v_creator_earnings IS '创作者收益统计';


-- ============================================
-- Migration complete
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 004 completed successfully';
    RAISE NOTICE 'Added tables: user_submissions, paid_products, orders, payment_records, content_unlocks';
    RAISE NOTICE 'Added functions: generate_order_number(), check_content_access()';
    RAISE NOTICE 'Added views: v_pending_submissions, v_revenue_stats, v_creator_earnings';
    RAISE NOTICE 'Altered tables: tutorials (added paid support), downloads (added paid support)';
END $$;
