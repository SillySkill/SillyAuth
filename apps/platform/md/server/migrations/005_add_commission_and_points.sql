-- ============================================
-- Migration 005: Add Commission Config and Points Payment
-- Description: Add platform commission configuration and points payment system
-- Author: SillyMD Team
-- Date: 2026-02-04
-- ============================================

-- ============================================
-- Table 1: commission_settings (佣金配置表)
-- Purpose: Store platform commission configuration
-- ============================================
CREATE TABLE IF NOT EXISTS commission_settings (
    id BIGSERIAL PRIMARY KEY,

    -- Configuration Scope
    scope VARCHAR(50) NOT NULL,  -- global, category, user, product
    scope_id BIGINT,  -- NULL for global, user_id for user, etc.

    -- Commission Rates
    commission_rate DECIMAL(5,2) NOT NULL DEFAULT 30.00,  -- 平台佣金比例（%）
    min_commission_rate DECIMAL(5,2) DEFAULT 0.00,  -- 最低佣金比例
    max_commission_rate DECIMAL(5,2) DEFAULT 100.00,  -- 最高佣金比例

    -- Creator Share (calculated as 100 - commission_rate)
    creator_share_rate DECIMAL(5,2) GENERATED ALWAYS AS (100 - commission_rate) STORED,

    -- Special Rules
    is_custom BOOLEAN DEFAULT FALSE,  -- 是否自定义规则
    is_active BOOLEAN DEFAULT TRUE,

    -- Validity Period
    valid_from DATE,
    valid_until DATE,

    -- Metadata
    description TEXT,
    created_by BIGINT,
    updated_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_commission_settings_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_commission_settings_updated_by FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT uq_commission_settings_scope UNIQUE(scope, scope_id)
);

CREATE INDEX idx_commission_settings_scope ON commission_settings(scope);
CREATE INDEX idx_commission_settings_is_active ON commission_settings(is_active);

CREATE TRIGGER update_commission_settings_updated_at
    BEFORE UPDATE ON commission_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE commission_settings IS '平台佣金配置表';
COMMENT ON COLUMN commission_settings.scope IS '配置范围: global=全局, category=分类, user=用户, product=产品';
COMMENT ON COLUMN commission_settings.commission_rate IS '平台佣金比例（%），0-100';
COMMENT ON COLUMN commission_settings.creator_share_rate IS '创作者分成比例（%），自动计算为 100 - 佣金比例';


-- ============================================
-- Table 2: user_points (用户积分表)
-- Purpose: Store user points balance and transactions
-- ============================================
CREATE TABLE IF NOT EXISTS user_points (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,

    -- Balance
    balance BIGINT NOT NULL DEFAULT 0,  -- 当前积分余额
    total_earned BIGINT NOT NULL DEFAULT 0,  -- 累计获得
    total_spent BIGINT NOT NULL DEFAULT 0,  -- 累计消费

    -- Level
    level INT DEFAULT 1,  -- 等级
    experience BIGINT DEFAULT 0,  -- 经验值

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_points_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_points_balance ON user_points(balance);
CREATE INDEX idx_user_points_level ON user_points(level);

CREATE TRIGGER update_user_points_updated_at
    BEFORE UPDATE ON user_points
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_points IS '用户积分表';
COMMENT ON COLUMN user_points.balance IS '积分余额';
COMMENT ON COLUMN user_points.level IS '用户等级';


-- ============================================
-- Table 3: point_transactions (积分交易记录表)
-- Purpose: Store all point transactions
-- ============================================
CREATE TABLE IF NOT EXISTS point_transactions (
    id BIGSERIAL PRIMARY KEY,

    -- User Info
    user_id BIGINT NOT NULL,

    -- Transaction Info
    transaction_type VARCHAR(50) NOT NULL,  -- earn, spend, refund, admin_grant, admin_deduct
    transaction_source VARCHAR(50) NOT NULL,  -- purchase, sign_in, task, event, admin
    amount INT NOT NULL,  -- 积分数量（正数为获得，负数为消费）

    -- Balance Snapshot
    balance_before INT NOT NULL,  -- 交易前余额
    balance_after INT NOT NULL,  -- 交易后余额

    -- Related Info
    related_order_id BIGINT,  -- 关联的订单ID
    related_content_id BIGINT,  -- 关联的内容ID
    description TEXT,

    -- Metadata
    metadata JSONB,  -- 额外的元数据
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_point_transactions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_point_transactions_order_id FOREIGN KEY (related_order_id) REFERENCES orders(id) ON DELETE SET NULL
);

CREATE INDEX idx_point_transactions_user_id ON point_transactions(user_id);
CREATE INDEX idx_point_transactions_type ON point_transactions(transaction_type);
CREATE INDEX idx_point_transactions_source ON point_transactions(transaction_source);
CREATE INDEX idx_point_transactions_created_at ON point_transactions(created_at);

COMMENT ON TABLE point_transactions IS '积分交易记录表';
COMMENT ON COLUMN point_transactions.transaction_type IS '交易类型: earn=获得, spend=消费, refund=退款, admin_grant=管理员赠送, admin_deduct=管理员扣除';


-- ============================================
-- Table 3: point_products (积分商品表)
-- Purpose: Define products that can be purchased with points
-- ============================================
CREATE TABLE IF NOT EXISTS point_products (
    id BIGSERIAL PRIMARY KEY,

    -- Product Info
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL,  -- content, coupon, vip, custom
    description TEXT,

    -- Pricing
    points_price INT NOT NULL,  -- 积分价格
    original_price INT,  -- 原价（用于显示折扣）

    -- Content Reference (if product_type is content)
    content_type VARCHAR(20),  -- tutorial, download
    content_id BIGINT,

    -- Validity
    stock INT DEFAULT -1,  -- 库存，-1 表示无限制
    sold_count INT DEFAULT 0,  -- 已售数量

    -- Display
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Sort Order
    position INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_point_products_content FOREIGN KEY(content_type, content_id)
        REFERENCES paid_products ON UPDATE CASCADE
);

CREATE INDEX idx_point_products_type ON point_products(product_type);
CREATE INDEX idx_point_products_is_active ON point_products(is_active);
CREATE INDEX idx_point_products_is_featured ON point_products(is_featured);
CREATE INDEX idx_point_products_position ON point_products(position);

CREATE TRIGGER update_point_products_updated_at
    BEFORE UPDATE ON point_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE point_products IS '积分商品表';
COMMENT ON COLUMN point_products.points_price IS '积分价格';
COMMENT ON COLUMN point_products.stock IS '库存，-1 表示无限制';


-- ============================================
-- Update paid_products table: add custom commission support
-- ============================================

ALTER TABLE paid_products
    ADD COLUMN IF NOT EXISTS use_custom_commission BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS custom_commission_rate DECIMAL(5,2);  -- 自定义佣金比例

CREATE INDEX idx_paid_products_use_custom_commission ON paid_products(use_custom_commission);


-- ============================================
-- Update orders table: add points payment support
-- ============================================

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50) DEFAULT 'money',
    ADD CONSTRAINT chk_payment_method CHECK (payment_method IN ('wechat', 'alipay', 'points', 'balance'));

-- Update existing orders to default payment method
UPDATE orders SET payment_method = 'wechat' WHERE payment_method IS NULL;


-- ============================================
-- Update orders table: add points_paid field
-- ============================================

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS points_used INT DEFAULT 0,  -- 使用的积分数量
    ADD COLUMN IF NOT EXISTS points_value DECIMAL(10,2) DEFAULT 0;  -- 积分抵扣的金额（元）


-- ============================================
-- Insert default commission settings
-- ============================================

-- Global commission rate (default 30%)
INSERT INTO commission_settings (scope, commission_rate, min_commission_rate, max_commission_rate, description) VALUES
('global', 30.00, 0.00, 100.00, '默认平台佣金比例 30%')
ON CONFLICT (scope, scope_id) DO UPDATE SET commission_rate = 30.00;

-- Tutorial category: 25% commission (encourage tutorials)
INSERT INTO commission_settings (scope, scope_id, commission_rate, description) VALUES
('category', 'tutorial', 25.00, '教程分类佣金比例 25%')
ON CONFLICT (scope, scope_id) DO NOTHING;

-- Download category: 30% commission
INSERT INTO commission_settings (scope, scope_id, commission_rate, description) VALUES
('category', 'download', 30.00, '下载分类佣金比例 30%')
ON CONFLICT (scope, scope_id) DO NOTHING;

-- Top creators: 20% commission (reward high-quality creators)
INSERT INTO commission_settings (scope, commission_rate, description) VALUES
('top_creators', 20.00, '优质创作者佣金比例 20%（月销售超过1000元的创作者）')
ON CONFLICT (scope) DO NOTHING;


-- ============================================
-- Insert sample point products
-- ============================================

INSERT INTO point_products (product_name, product_type, description, points_price, is_featured) VALUES
('免费体验券', 'coupon', '可用于购买任意付费内容的优惠券', 100, TRUE),
('7天VIP会员', 'vip', '7天VIP会员，免费阅读所有付费内容', 500, TRUE),
('30天VIP会员', 'vip', '30天VIP会员，免费阅读所有付费内容', 1500, FALSE),
('积分礼包', 'custom', '1000积分礼包，超值优惠', 80, FALSE)
ON CONFLICT DO NOTHING;


-- ============================================
-- Create functions and triggers
-- ============================================

-- Function: Get commission rate for a product
CREATE OR REPLACE FUNCTION get_commission_rate(
    p_content_type VARCHAR,
    p_content_id BIGINT,
    p_creator_id BIGINT
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_commission_rate DECIMAL(5,2);
    v_creator_sales NUMERIC;
BEGIN
    -- Check if product has custom commission
    SELECT custom_commission_rate INTO v_commission_rate
    FROM paid_products
    WHERE content_type = p_content_type
      AND content_id = p_content_id
      AND use_custom_commission = TRUE;

    -- If custom commission exists, return it
    IF v_commission_rate IS NOT NULL THEN
        RETURN v_commission_rate;
    END IF;

    -- Check if creator has custom rate (top creator)
    SELECT COALESCE(SUM(final_price), 0) INTO v_creator_sales
    FROM orders
    WHERE paid_at >= DATE_TRUNC('month', CURRENT_DATE)
      AND paid_at < DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')
      AND status = 'paid';

    IF v_creator_sales >= 1000 THEN
        -- Top creator rate
        SELECT commission_rate INTO v_commission_rate
        FROM commission_settings
        WHERE scope = 'top_creators'
          AND is_active = TRUE
        LIMIT 1;

        IF v_commission_rate IS NOT NULL THEN
            RETURN v_commission_rate;
        END IF;
    END IF;

    -- Get category-specific rate
    SELECT commission_rate INTO v_commission_rate
    FROM commission_settings
    WHERE scope = 'category'
      AND scope_id = p_content_type
      AND is_active = TRUE
      AND (valid_from IS NULL OR valid_from <= CURRENT_DATE)
      AND (valid_until IS NULL OR valid_until >= CURRENT_DATE)
    LIMIT 1;

    -- If category rate exists, return it
    IF v_commission_rate IS NOT NULL THEN
        RETURN v_commission_rate;
    END IF;

    -- Default to global rate
    SELECT commission_rate INTO v_commission_rate
    FROM commission_settings
    WHERE scope = 'global'
      AND is_active = TRUE
    LIMIT 1;

    RETURN COALESCE(v_commission_rate, 30.00);
END;
$$ LANGUAGE plpgsql;


-- Function: Award points for purchase
CREATE OR REPLACE FUNCTION award_purchase_points(
    p_user_id BIGINT,
    p_order_id BIGINT
) RETURNS VOID AS $$
DECLARE
    v_points INT;
    v_current_balance INT;
BEGIN
    -- Calculate points (1 point per 1 yuan)
    SELECT CEIL(final_price)::INT INTO v_points
    FROM orders
    WHERE id = p_order_id;

    IF v_points IS NULL OR v_points = 0 THEN
        RETURN;
    END IF;

    -- Get current balance
    SELECT balance INTO v_current_balance
    FROM user_points
    WHERE user_id = p_user_id;

    -- If no record exists, create one
    IF v_current_balance IS NULL THEN
        INSERT INTO user_points (user_id, balance, total_earned)
        VALUES (p_user_id, v_points, v_points);
        v_current_balance := 0;
    END IF;

    -- Update balance
    UPDATE user_points
    SET balance = balance + v_points,
        total_earned = total_earned + v_points
    WHERE user_id = p_user_id;

    -- Record transaction
    INSERT INTO point_transactions (
        user_id,
        transaction_type,
        transaction_source,
        amount,
        balance_before,
        balance_after,
        related_order_id,
        description
    )
    VALUES (
        p_user_id,
        'earn',
        'purchase',
        v_points,
        v_current_balance,
        v_current_balance + v_points,
        p_order_id,
        '购物获得积分：' || v_points || ' 分'
    );
END;
$$ LANGUAGE plpgsql;


-- Trigger: Auto award points after payment
CREATE OR REPLACE FUNCTION trigger_award_points()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'paid' AND OLD.status != 'paid' THEN
        PERFORM award_purchase_points(NEW.user_id, NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_award_points_on_payment ON orders;
CREATE TRIGGER trigger_award_points_on_payment
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION trigger_award_points();


-- ============================================
-- Migration complete
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 005 completed successfully';
    RAISE NOTICE 'Added tables: commission_settings, user_points, point_transactions, point_products';
    RAISE NOTICE 'Added functions: get_commission_rate(), award_purchase_points()';
    RAISE NOTICE 'Added trigger: trigger_award_points_on_payment';
    RAISE NOTICE 'Updated tables: paid_products, orders';
    RAISE NOTICE 'Inserted sample data: commission settings, point products';
END $$;
