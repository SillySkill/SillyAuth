-- 013: Add is_admin_only column to store_products + insert test product
-- 仅 admin 用户可见的测试商品（0.01元）

BEGIN;

-- 添加 is_admin_only 列
ALTER TABLE store_products
ADD COLUMN IF NOT EXISTS is_admin_only BOOLEAN NOT NULL DEFAULT FALSE;

-- 插入测试产品（仅 admin 可见，0.01 元）
INSERT INTO store_products (collection_id, product_key, name_zh, name_en,
    description_zh, description_en, image_url, price, stock_count, is_active,
    is_admin_only, sort_order)
SELECT
    sc.id, 'sillyfu-test-001', '测试商品 (0.01元)', 'Test Product (¥0.01)',
    '仅用于测试支付流程，仅管理员可见', 'For testing payment flow, admin only',
    '/static/img/sillyclaw/product-front-silver.png',
    1,  -- 1分 = ¥0.01
    9999,  -- 充足库存
    TRUE, TRUE, 0
FROM store_collections sc
WHERE sc.collection_key = 'sillyfu'
AND NOT EXISTS (
    SELECT 1 FROM store_products sp WHERE sp.product_key = 'sillyfu-test-001'
);

COMMIT;
