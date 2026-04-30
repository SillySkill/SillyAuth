-- Store Module Database Migration
-- 多产品线商城数据库结构
-- Version: 1.0
-- Date: 2026-04-29

-- ============================================
-- 1. Store Collections Table
-- ============================================
CREATE TABLE IF NOT EXISTS store_collections (
    id SERIAL PRIMARY KEY,
    collection_key VARCHAR(50) UNIQUE NOT NULL,
    name_zh VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    logo_url VARCHAR(500),
    theme_config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE store_collections IS '商城产品集合表';
COMMENT ON COLUMN store_collections.collection_key IS '集合标识键，用于URL，如 sillyclaw, electronics';
COMMENT ON COLUMN store_collections.theme_config IS '主题配置JSON，可包含颜色、Logo等';

-- ============================================
-- 2. Store Products Table
-- ============================================
CREATE TABLE IF NOT EXISTS store_products (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER REFERENCES store_collections(id) ON DELETE CASCADE,
    product_key VARCHAR(50) NOT NULL,
    name_zh VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    description_zh TEXT,
    description_en TEXT,
    image_url VARCHAR(500),
    gallery JSONB DEFAULT '[]',
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    original_price DECIMAL(10, 2),
    stock_count INTEGER DEFAULT -1,
    sold_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    specifications JSONB,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, product_key)
);

COMMENT ON TABLE store_products IS '商城产品表';
COMMENT ON COLUMN store_products.stock_count IS '库存数量，-1表示无限库存';
COMMENT ON COLUMN store_products.gallery IS '产品图片列表JSON数组';
COMMENT ON COLUMN store_products.specifications IS '技术规格JSON对象';

-- ============================================
-- 3. Store Cart Table
-- ============================================
CREATE TABLE IF NOT EXISTS store_cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    collection_id INTEGER REFERENCES store_collections(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES store_products(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0 AND quantity <= 99),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, collection_id, product_id)
);

COMMENT ON TABLE store_cart IS '商城购物车表';
COMMENT ON COLUMN store_cart.user_id IS '用户ID';
COMMENT ON COLUMN store_cart.collection_id IS '集合ID，购物车按集合隔离';

-- ============================================
-- 4. Store Orders Table
-- ============================================
CREATE TABLE IF NOT EXISTS store_orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    collection_id INTEGER REFERENCES store_collections(id),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20),
    payment_no VARCHAR(64),
    shipping_name VARCHAR(100),
    shipping_phone VARCHAR(20),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE store_orders IS '商城订单表';
COMMENT ON COLUMN store_orders.status IS '订单状态: pending, paid, shipped, completed, cancelled';

-- ============================================
-- 5. Store Order Items Table
-- ============================================
CREATE TABLE IF NOT EXISTS store_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES store_orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES store_products(id),
    product_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0)
);

COMMENT ON TABLE store_order_items IS '商城订单项表';

-- ============================================
-- Indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_store_products_collection ON store_products(collection_id);
CREATE INDEX IF NOT EXISTS idx_store_products_key ON store_products(product_key);
CREATE INDEX IF NOT EXISTS idx_store_products_active ON store_products(is_active);
CREATE INDEX IF NOT EXISTS idx_store_cart_user ON store_cart(user_id);
CREATE INDEX IF NOT EXISTS idx_store_cart_collection ON store_cart(collection_id);
CREATE INDEX IF NOT EXISTS idx_store_orders_user ON store_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_store_orders_collection ON store_orders(collection_id);
CREATE INDEX IF NOT EXISTS idx_store_orders_status ON store_orders(status);
CREATE INDEX IF NOT EXISTS idx_store_order_items_order ON store_order_items(order_id);

-- ============================================
-- Initial Seed Data: SillyClaw Collection
-- ============================================
INSERT INTO store_collections (collection_key, name_zh, name_en, description, is_active, sort_order)
VALUES
    ('sillyclaw', '傻福虾盘', 'SillyClaw', '傻福虾U盘官方商城 - 双接口高速USB闪存盘', TRUE, 1)
ON CONFLICT (collection_key) DO NOTHING;

-- Get the SillyClaw collection ID
DO $$
DECLARE
    sillyclaw_id INTEGER;
BEGIN
    SELECT id INTO sillyclaw_id FROM store_collections WHERE collection_key = 'sillyclaw';

    -- Insert SillyClaw USB products
    INSERT INTO store_products (collection_id, product_key, name_zh, name_en, description_zh, price, original_price, stock_count, is_active, sort_order, specifications)
    VALUES
        (sillyclaw_id, 'sillyclaw-128gb-silver', '傻福虾U盘 128GB 银色', 'SillyClaw USB 128GB Silver',
         '双接口高速USB闪存盘，Type-A + Type-C设计，128GB容量',
         69.00, 89.00, 100, TRUE, 1,
         '{"capacity": "128GB", "interface": "USB 3.2 Gen 1", "color": "银色", "material": "金属合金"}'),

        (sillyclaw_id, 'sillyclaw-256gb-silver', '傻福虾U盘 256GB 银色', 'SillyClaw USB 256GB Silver',
         '双接口高速USB闪存盘，Type-A + Type-C设计，256GB容量',
         99.00, 129.00, 80, TRUE, 2,
         '{"capacity": "256GB", "interface": "USB 3.2 Gen 1", "color": "银色", "material": "金属合金"}'),

        (sillyclaw_id, 'sillyclaw-512gb-gunmetal', '傻福虾U盘 512GB 枪灰银', 'SillyClaw USB 512GB Gunmetal',
         '双接口高速USB闪存盘，Type-A + Type-C设计，512GB容量',
         169.00, 199.00, 50, TRUE, 3,
         '{"capacity": "512GB", "interface": "USB 3.2 Gen 1", "color": "枪灰银", "material": "金属合金"}'),

        (sillyclaw_id, 'sillyclaw-1tb-gunmetal', '傻福虾U盘 1TB 枪灰银', 'SillyClaw USB 1TB Gunmetal',
         '双接口高速USB闪存盘，Type-A + Type-C设计，1TB大容量',
         269.00, 329.00, 30, TRUE, 4,
         '{"capacity": "1TB", "interface": "USB 3.2 Gen 1", "color": "枪灰银", "material": "金属合金"}')
    ON CONFLICT (collection_id, product_key) DO NOTHING;
END $$;

-- ============================================
-- Functions
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_store_collections_updated_at ON store_collections;
CREATE TRIGGER update_store_collections_updated_at
    BEFORE UPDATE ON store_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_store_products_updated_at ON store_products;
CREATE TRIGGER update_store_products_updated_at
    BEFORE UPDATE ON store_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_store_cart_updated_at ON store_cart;
CREATE TRIGGER update_store_cart_updated_at
    BEFORE UPDATE ON store_cart
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_store_orders_updated_at ON store_orders;
CREATE TRIGGER update_store_orders_updated_at
    BEFORE UPDATE ON store_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
