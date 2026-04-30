-- ============================================
-- Migration 006: PayPal and Creator Settlement
-- 添加 PayPal 支付和创作者结算功能
-- ============================================

-- ============================================
-- 1. 收款账户配置表
-- ============================================
CREATE TABLE IF NOT EXISTS payment_accounts (
    id SERIAL PRIMARY KEY,
    account_type VARCHAR(20) NOT NULL,  -- wechat, alipay, paypal, bank
    account_name VARCHAR(255) NOT NULL,
    account_id VARCHAR(255) NOT NULL,  -- 账户标识
    credentials JSONB NOT NULL,  -- 加密存储的凭证信息
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,  -- 优先级，数字越大优先级越高
    currency VARCHAR(10) DEFAULT 'CNY',  -- 支持的货币
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_primary_account_per_type UNIQUE (account_type, is_primary)
        WHERE is_primary = TRUE
);

CREATE INDEX idx_payment_accounts_type ON payment_accounts(account_type);
CREATE INDEX idx_payment_accounts_active ON payment_accounts(is_active, priority DESC);

-- ============================================
-- 2. 创作者结算偏好表
-- ============================================
CREATE TABLE IF NOT EXISTS creator_settlement_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    settlement_method VARCHAR(20) NOT NULL DEFAULT 'direct',  -- direct（直接分佣）, points（转换为积分）
    payment_account_type VARCHAR(20),  -- 创作者指定的收款方式
    payment_account_id VARCHAR(255),  -- 收款账户标识
    auto_settle BOOLEAN DEFAULT FALSE,  -- 是否自动结算
    min_settlement_amount DECIMAL(10, 2) DEFAULT 100.00,  -- 最低结算金额
    settlement_period VARCHAR(20) DEFAULT 'monthly',  -- weekly, monthly, quarterly
    bank_info JSONB,  -- 银行账户信息（加密）
    paypal_email VARCHAR(255),
    alipay_account VARCHAR(255),
    wechat_openid VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_creator_settlement_user ON creator_settlement_preferences(user_id);
CREATE INDEX idx_creator_settlement_method ON creator_settlement_preferences(settlement_method);

-- ============================================
-- 3. 创作者收益记录表
-- ============================================
CREATE TABLE IF NOT EXISTS creator_earnings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    content_type VARCHAR(20) NOT NULL,
    content_id INTEGER NOT NULL,
    product_id INTEGER REFERENCES paid_products(id) ON DELETE SET NULL,

    -- 收益金额
    gross_amount DECIMAL(10, 2) NOT NULL,  -- 总金额
    platform_commission DECIMAL(10, 2) NOT NULL,  -- 平台佣金
    creator_share DECIMAL(10, 2) NOT NULL,  -- 创作者分成

    -- 结算信息
    settlement_status VARCHAR(20) DEFAULT 'pending',  -- pending, settled, points_converted
    settlement_method VARCHAR(20),  -- direct, points
    settlement_amount DECIMAL(10, 2),  -- 实际结算金额
    settled_at TIMESTAMP WITH TIME ZONE,

    -- 积分转换信息
    points_awarded INTEGER,  -- 转换的积分数
    points_transaction_id INTEGER REFERENCES point_transactions(id) ON DELETE SET NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_settlement_status CHECK (
        settlement_status IN ('pending', 'settled', 'points_converted', 'failed')
    )
);

CREATE INDEX idx_creator_earnings_user ON creator_earnings(user_id, created_at DESC);
CREATE INDEX idx_creator_earnings_status ON creator_earnings(settlement_status);
CREATE INDEX idx_creator_earnings_order ON creator_earnings(order_id);

-- ============================================
-- 4. 结算记录表
-- ============================================
CREATE TABLE IF NOT EXISTS settlement_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    batch_number VARCHAR(50) NOT NULL UNIQUE,  -- 批次号

    -- 汇总信息
    total_orders INTEGER NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    total_commission DECIMAL(10, 2) NOT NULL,
    total_earnings DECIMAL(10, 2) NOT NULL,

    -- 结算信息
    settlement_method VARCHAR(20) NOT NULL,
    payment_account_type VARCHAR(20),
    payment_account_id VARCHAR(255),

    -- 状态
    status VARCHAR(20) DEFAULT 'processing',  -- processing, completed, failed
    transaction_id VARCHAR(255),  -- 支付平台交易号
    failure_reason TEXT,

    -- 时间
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT valid_settlement_status CHECK (
        status IN ('processing', 'completed', 'failed', 'cancelled')
    )
);

CREATE INDEX idx_settlement_user ON settlement_records(user_id, created_at DESC);
CREATE INDEX idx_settlement_status ON settlement_records(status);
CREATE INDEX idx_settlement_batch ON settlement_records(batch_number);

-- ============================================
-- 5. 修改订单表，支持 PayPal 和结算标记
-- ============================================
ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20) DEFAULT 'wechat',
    ADD COLUMN IF NOT EXISTS payment_channel VARCHAR(50),
    ADD COLUMN IF NOT EXISTS payment_account_id INTEGER REFERENCES payment_accounts(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS creator_settled BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS creator_settlement_id INTEGER REFERENCES creator_earnings(id) ON DELETE SET NULL;

CREATE INDEX idx_orders_payment_method ON orders(payment_method);
CREATE INDEX idx_orders_creator_settled ON orders(creator_settled);

-- ============================================
-- 6. 修改积分交易表，支持创作者收益转换
-- ============================================
ALTER TABLE point_transactions
    ADD COLUMN IF NOT EXISTS source_order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS source_earning_id INTEGER REFERENCES creator_earnings(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS conversion_rate DECIMAL(10, 4),  -- 金额转积分的汇率

CREATE INDEX idx_point_transactions_source_order ON point_transactions(source_order_id);
CREATE INDEX idx_point_transactions_source_earning ON point_transactions(source_earning_id);

-- ============================================
-- 7. 触发器：支付成功后自动处理创作者收益
-- ============================================
CREATE OR REPLACE FUNCTION handle_creator_earnings()
RETURNS TRIGGER AS $$
DECLARE
    v_product RECORD;
    v_commission_rate DECIMAL(5, 2);
    v_creator_share DECIMAL(10, 2);
    v_platform_share DECIMAL(10, 2);
    v_settlement_pref RECORD;
    v_points_awarded INTEGER;
BEGIN
    -- 只处理已支付的订单
    IF NEW.payment_status != 'paid' OR OLD.payment_status = 'paid' THEN
        RETURN NEW;
    END IF;

    -- 获取产品信息
    SELECT * INTO v_product
    FROM paid_products
    WHERE id = NEW.product_id;

    IF NOT FOUND OR v_product.creator_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- 计算佣金比例
    SELECT get_commission_rate(
        NEW.content_type,
        NEW.content_id,
        v_product.creator_id
    ) INTO v_commission_rate;

    -- 计算分成
    v_creator_share := NEW.final_price * (1 - v_commission_rate / 100);
    v_platform_share := NEW.final_price * (v_commission_rate / 100);

    -- 获取创作者结算偏好
    SELECT * INTO v_settlement_pref
    FROM creator_settlement_preferences
    WHERE user_id = v_product.creator_id;

    IF NOT FOUND THEN
        -- 默认：直接分佣
        v_settlement_pref.settlement_method := 'direct';
    END IF;

    -- 根据结算偏好处理
    IF v_settlement_pref.settlement_method = 'points' THEN
        -- 转换为积分
        v_points_awarded := ROUND(v_creator_share::NUMERIC);  -- 1元 = 1积分

        -- 创建积分交易记录
        INSERT INTO point_transactions (
            user_id,
            transaction_type,
            transaction_source,
            amount,
            balance_before,
            balance_after,
            description,
            source_order_id,
            conversion_rate
        )
        VALUES (
            v_product.creator_id,
            'earn',
            'creator_revenue',
            v_points_awarded,
            (SELECT balance FROM user_points WHERE user_id = v_product.creator_id),
            (SELECT balance + v_points_awarded FROM user_points WHERE user_id = v_product.creator_id),
            '创作者收益转换: ' || NEW.order_number,
            NEW.id,
            1.0
        )
        RETURNING id INTO v_points_transaction_id;

        -- 更新用户积分
        UPDATE user_points
        SET
            balance = balance + v_points_awarded,
            total_earned = total_earned + v_points_awarded
        WHERE user_id = v_product.creator_id;

        -- 创建创作者收益记录
        INSERT INTO creator_earnings (
            user_id,
            order_id,
            content_type,
            content_id,
            product_id,
            gross_amount,
            platform_commission,
            creator_share,
            settlement_status,
            settlement_method,
            settlement_amount,
            points_awarded,
            points_transaction_id
        )
        VALUES (
            v_product.creator_id,
            NEW.id,
            NEW.content_type,
            NEW.content_id,
            v_product.id,
            NEW.final_price,
            v_platform_share,
            v_creator_share,
            'points_converted',
            'points',
            v_creator_share,
            v_points_awarded,
            v_points_transaction_id
        )
        RETURNING id INTO v_earning_id;

        -- 标记订单已结算
        NEW.creator_settled := TRUE;
        NEW.creator_settlement_id := v_earning_id;

    ELSE
        -- 直接分佣（待结算）
        INSERT INTO creator_earnings (
            user_id,
            order_id,
            content_type,
            content_id,
            product_id,
            gross_amount,
            platform_commission,
            creator_share,
            settlement_status,
            settlement_method,
            settlement_amount
        )
        VALUES (
            v_product.creator_id,
            NEW.id,
            NEW.content_type,
            NEW.content_id,
            v_product.id,
            NEW.final_price,
            v_platform_share,
            v_creator_share,
            'pending',
            'direct',
            v_creator_share
        )
        RETURNING id INTO v_earning_id;

        NEW.creator_settlement_id := v_earning_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_handle_creator_earnings
    AFTER UPDATE OF payment_status ON orders
    FOR EACH ROW
    EXECUTE FUNCTION handle_creator_earnings();

-- ============================================
-- 8. 视图：创作者收益统计
-- ============================================
CREATE OR REPLACE VIEW v_creator_earnings_summary AS
SELECT
    u.id AS user_id,
    u.username,
    u.email,
    csp.settlement_method,
    csp.auto_settle,

    -- 收益统计
    COUNT(DISTINCT ce.id) AS total_earnings_count,
    COALESCE(SUM(CASE WHEN ce.settlement_status = 'pending' THEN ce.creator_share ELSE 0 END), 0) AS pending_earnings,
    COALESCE(SUM(CASE WHEN ce.settlement_status = 'settled' THEN ce.settlement_amount ELSE 0 END), 0) AS settled_amount,
    COALESCE(SUM(CASE WHEN ce.settlement_status = 'points_converted' THEN ce.points_awarded ELSE 0 END), 0) AS points_earned,

    -- 订单统计
    COUNT(DISTINCT ce.order_id) AS total_orders_count,
    COALESCE(SUM(ce.gross_amount), 0) AS total_gross_amount,
    COALESCE(SUM(ce.platform_commission), 0) AS total_platform_commission

FROM users u
LEFT JOIN creator_settlement_preferences csp ON u.id = csp.user_id
LEFT JOIN creator_earnings ce ON u.id = ce.user_id
GROUP BY u.id, u.username, u.email, csp.settlement_method, csp.auto_settle;

-- ============================================
-- 9. 视图：待结算创作者列表
-- ============================================
CREATE OR REPLACE VIEW v_pending_settlements AS
SELECT
    ce.user_id,
    u.username,
    u.email,
    csp.settlement_method,
    csp.payment_account_type,
    csp.payment_account_id,
    csp.min_settlement_amount,

    -- 统计信息
    COUNT(*) AS pending_count,
    SUM(ce.creator_share) AS total_pending_amount,
    MIN(ce.created_at) AS oldest_earning_date,
    MAX(ce.created_at) AS latest_earning_date

FROM creator_earnings ce
JOIN users u ON ce.user_id = u.id
LEFT JOIN creator_settlement_preferences csp ON u.id = csp.user_id
WHERE ce.settlement_status = 'pending'
GROUP BY
    ce.user_id,
    u.username,
    u.email,
    csp.settlement_method,
    csp.payment_account_type,
    csp.payment_account_id,
    csp.min_settlement_amount
HAVING SUM(ce.creator_share) >= COALESCE(csp.min_settlement_amount, 100.00);

-- ============================================
-- 10. 函数：批量结算创作者收益
-- ============================================
CREATE OR REPLACE FUNCTION batch_settle_creator_earnings(
    p_user_id INTEGER,
    p_payment_account_type VARCHAR,
    p_payment_account_id VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    v_batch_number VARCHAR(50);
    v_earning RECORD;
    v_total_orders INTEGER := 0;
    v_total_amount DECIMAL(10, 2) := 0;
    v_total_commission DECIMAL(10, 2) := 0;
    v_total_earnings DECIMAL(10, 2) := 0;
    v_settlement_id INTEGER;
BEGIN
    -- 生成批次号
    v_batch_number := 'STL' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS') || LPAD(p_user_id::TEXT, 6, '0');

    -- 汇总待结算收益
    FOR v_earning IN
        SELECT
            id,
            order_id,
            creator_share,
            platform_commission,
            gross_amount
        FROM creator_earnings
        WHERE user_id = p_user_id
          AND settlement_status = 'pending'
        FOR UPDATE SKIP LOCKED
    LOOP
        v_total_orders := v_total_orders + 1;
        v_total_amount := v_total_amount + v_earning.gross_amount;
        v_total_commission := v_total_commission + v_earning.platform_commission;
        v_total_earnings := v_total_earnings + v_earning.creator_share;

        -- 标记为已结算
        UPDATE creator_earnings
        SET
            settlement_status = 'settled',
            settlement_amount = v_earning.creator_share,
            settled_at = CURRENT_TIMESTAMP
        WHERE id = v_earning.id;
    END LOOP;

    -- 创建结算记录
    IF v_total_orders > 0 THEN
        INSERT INTO settlement_records (
            user_id,
            batch_number,
            total_orders,
            total_amount,
            total_commission,
            total_earnings,
            settlement_method,
            payment_account_type,
            payment_account_id,
            status,
            period_start,
            period_end
        )
        VALUES (
            p_user_id,
            v_batch_number,
            v_total_orders,
            v_total_amount,
            v_total_commission,
            v_total_earnings,
            'direct',
            p_payment_account_type,
            p_payment_account_id,
            'processing',
            (SELECT MIN(created_at)::DATE FROM creator_earnings WHERE user_id = p_user_id),
            CURRENT_DATE
        )
        RETURNING id INTO v_settlement_id;
    END IF;

    RETURN v_settlement_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 11. 初始化默认数据
-- ============================================

-- 添加默认的收款账户配置（需要管理员配置实际信息）
INSERT INTO payment_accounts (account_type, account_name, account_id, credentials, is_primary, priority, description)
VALUES
    ('wechat', '微信支付-主账户', 'default_wechat', '{"mch_id": "", "api_key": "", "cert_path": ""}', TRUE, 100, '需要配置微信商户信息'),
    ('alipay', '支付宝-主账户', 'default_alipay', '{"app_id": "", "private_key": "", "public_key": ""}', TRUE, 100, '需要配置支付宝应用信息'),
    ('paypal', 'PayPal-Sandbox', 'default_paypal_sandbox', '{"client_id": "", "client_secret": "", "mode": "sandbox"}', TRUE, 100, 'PayPal 沙盒环境')
ON CONFLICT DO NOTHING;

-- ============================================
-- 12. 授权
-- ============================================
GRANT SELECT, INSERT, UPDATE ON payment_accounts TO sillymd_user;
GRANT SELECT, INSERT, UPDATE ON creator_settlement_preferences TO sillymd_user;
GRANT SELECT, INSERT, UPDATE ON creator_earnings TO sillymd_user;
GRANT SELECT, INSERT, UPDATE ON settlement_records TO sillymd_user;
GRANT SELECT ON v_creator_earnings_summary TO sillymd_user;
GRANT SELECT ON v_pending_settlements TO sillymd_user;
GRANT EXECUTE ON FUNCTION batch_settle_creator_earnings TO sillymd_user;

-- ============================================
-- 13. 函数：获取佣金比例
-- ============================================
CREATE OR REPLACE FUNCTION get_commission_rate(
    p_content_type VARCHAR,
    p_content_id INTEGER,
    p_creator_id INTEGER
) RETURNS DECIMAL(5, 2) AS $$
DECLARE
    v_commission_rate DECIMAL(5, 2);
BEGIN
    -- 默认平台佣金比例 20%
    v_commission_rate := 20.00;

    -- 检查是否有特定产品的佣金配置
    -- 可以扩展为从配置表读取

    -- 如果是教程，检查是否有特殊佣金率
    IF p_content_type = 'tutorial' THEN
        SELECT
            COALESCE(
                -- 优先使用产品特定的佣金率（如果有的话）
                (SELECT platform_share_percentage
                 FROM paid_products
                 WHERE content_type = p_content_type
                   AND content_id = p_content_id
                   AND creator_id = p_creator_id
                 LIMIT 1),
                20.00
            )
        INTO v_commission_rate;
    END IF;

    -- 如果是下载资源，检查是否有特殊佣金率
    IF p_content_type = 'download' THEN
        SELECT
            COALESCE(
                -- 优先使用产品特定的佣金率
                (SELECT platform_share_percentage
                 FROM paid_products
                 WHERE content_type = p_content_type
                   AND content_id = p_content_id
                   AND creator_id = p_creator_id
                 LIMIT 1),
                20.00
            )
        INTO v_commission_rate;
    END IF;

    -- 确保佣金率在合理范围内
    v_commission_rate := GREATEST(LEAST(v_commission_rate, 50.00), 0.00);

    RETURN v_commission_rate;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 完成
-- ============================================
COMMENT ON TABLE payment_accounts IS '平台收款账户配置';
COMMENT ON TABLE creator_settlement_preferences IS '创作者结算偏好设置';
COMMENT ON TABLE creator_earnings IS '创作者收益记录';
COMMENT ON TABLE settlement_records IS '结算批次记录';
COMMENT ON VIEW v_creator_earnings_summary IS '创作者收益汇总视图';
COMMENT ON VIEW v_pending_settlements IS '待结算创作者列表';
COMMENT ON FUNCTION get_commission_rate IS '根据内容和创作者获取平台佣金比例';

SELECT 'Migration 006: PayPal and Creator Settlement completed successfully' AS status;
