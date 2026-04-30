-- 积分商城系统迁移脚本
-- 创建时间: 2025-02-04

-- 商品分类表
CREATE TABLE IF NOT EXISTS points_categories (
    id SERIAL PRIMARY KEY,
    category_key VARCHAR(50) UNIQUE NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    name_zh VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 积分商品表
CREATE TABLE IF NOT EXISTS points_products (
    id SERIAL PRIMARY KEY,
    product_key VARCHAR(100) UNIQUE NOT NULL,
    category_key VARCHAR(50) NOT NULL REFERENCES points_categories(category_key),
    name_en VARCHAR(200) NOT NULL,
    name_zh VARCHAR(200) NOT NULL,
    description_en TEXT,
    description_zh TEXT,
    image_url VARCHAR(500),
    points_required INTEGER NOT NULL CHECK (points_required >= 0),
    stock_count INTEGER DEFAULT -1 CHECK (stock_count >= -1), -- -1表示无限库存
    sold_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    valid_days INTEGER DEFAULT NULL, -- 有效期（天数），NULL表示永久有效
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- 购物车表
CREATE TABLE IF NOT EXISTS points_shopping_cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES points_products(id),
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

-- 兑换记录表
CREATE TABLE IF NOT EXISTS points_exchange_records (
    id SERIAL PRIMARY KEY,
    exchange_no VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES points_products(id),
    product_name VARCHAR(200) NOT NULL,
    points_used INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'completed', -- completed, cancelled, refunded
    exchange_data JSONB DEFAULT '{}'::jsonb, -- 兑换时的商品数据快照
    metadata JSONB DEFAULT '{}'::jsonb, -- 其他元数据（如优惠券码、VIP到期时间等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_points_products_category ON points_products(category_key);
CREATE INDEX IF NOT EXISTS idx_points_products_active ON points_products(is_active);
CREATE INDEX IF NOT EXISTS idx_points_products_featured ON points_products(is_featured);
CREATE INDEX IF NOT EXISTS idx_points_cart_user ON points_shopping_cart(user_id);
CREATE INDEX IF NOT EXISTS idx_points_exchange_user ON points_exchange_records(user_id);
CREATE INDEX IF NOT EXISTS idx_points_exchange_status ON points_exchange_records(status);

-- 插入默认分类数据
INSERT INTO points_categories (category_key, name_en, name_zh, description, icon, sort_order) VALUES
('content', 'Content Exchange', '内容兑换', '兑换AI生成的各种内容和资源', 'fas fa-file-alt', 1),
('coupon', 'Coupons', '优惠券', '平台使用优惠券和折扣券', 'fas fa-ticket-alt', 2),
('vip', 'VIP Membership', 'VIP会员', '升级VIP会员享受更多特权', 'fas fa-crown', 3),
('custom', 'Custom Items', '自定义商品', '管理员自定义的其他商品', 'fas fa-gift', 4)
ON CONFLICT (category_key) DO NOTHING;

-- 插入示例商品数据
INSERT INTO points_products (product_key, category_key, name_en, name_zh, description_en, description_zh, image_url, points_required, stock_count, is_featured, sort_order, valid_days) VALUES
-- 内容兑换类
('content_1000_words', 'content', '1000 AI Words', '1000字AI内容', 'Generate 1000 words of AI content', '生成1000字AI内容', null, 100, -1, TRUE, 1, NULL),
('content_5000_words', 'content', '5000 AI Words', '5000字AI内容', 'Generate 5000 words of AI content', '生成5000字AI内容', null, 400, -1, TRUE, 2, NULL),
('content_image_gen', 'content', 'Image Generation', 'AI图像生成', 'Generate one AI image', '生成一张AI图像', null, 50, 100, FALSE, 3, NULL),

-- 优惠券类
('coupon_10percent', 'coupon', '10% Off Coupon', '10%折扣券', '10% off on next purchase', '下次购买享受10%折扣', null, 200, 50, FALSE, 4, 90),
('coupon_20percent', 'coupon', '20% Off Coupon', '20%折扣券', '20% off on next purchase', '下次购买享受20%折扣', null, 350, 30, TRUE, 5, 90),
('coupon_50points', 'coupon', '50 Points Bonus', '50积分奖励券', 'Get 50 bonus points', '获得50额外积分', null, 500, 20, FALSE, 6, 60),

-- VIP会员类
('vip_7days', 'vip', '7 Days VIP', '7天VIP会员', '7 days of VIP membership', '7天VIP会员权限', null, 300, -1, TRUE, 7, 7),
('vip_30days', 'vip', '30 Days VIP', '30天VIP会员', '30 days of VIP membership', '30天VIP会员权限', null, 1000, -1, TRUE, 8, 30),
('vip_90days', 'vip', '90 Days VIP', '90天VIP会员', '90 days of VIP membership', '90天VIP会员权限', null, 2500, -1, FALSE, 9, 90),
('vip_365days', 'vip', '365 Days VIP', '365天VIP会员', '365 days of VIP membership', '365天VIP会员权限', null, 8000, -1, TRUE, 10, 365),

-- 自定义商品类
('custom_starter_pack', 'custom', 'Starter Pack', '新手礼包', 'New user starter pack with bonus items', '新手专享礼包，包含多种奖励', null, 150, 100, FALSE, 11, NULL),
('custom_premium_theme', 'custom', 'Premium Theme', '高级主题', 'Unlock premium theme', '解锁高级主题', null, 500, -1, FALSE, 12, NULL)
ON CONFLICT (product_key) DO NOTHING;

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_points_categories_updated_at BEFORE UPDATE ON points_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_points_products_updated_at BEFORE UPDATE ON points_products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_points_cart_updated_at BEFORE UPDATE ON points_shopping_cart FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_points_exchange_updated_at BEFORE UPDATE ON points_exchange_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE points_categories IS '积分商品分类表';
COMMENT ON TABLE points_products IS '积分商品表';
COMMENT ON TABLE points_shopping_cart IS '购物车表';
COMMENT ON TABLE points_exchange_records IS '兑换记录表';

COMMENT ON COLUMN points_products.stock_count IS '库存数量，-1表示无限库存';
COMMENT ON COLUMN points_products.valid_days IS '商品有效期（天数），NULL表示永久有效';
COMMENT ON COLUMN points_exchange_records.status IS '状态: completed-已完成, cancelled-已取消, refunded-已退款';
