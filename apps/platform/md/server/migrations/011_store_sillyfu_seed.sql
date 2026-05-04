-- 011_store_sillyfu_seed.sql
-- SillyFu 商城种子数据 — 产品线集合 + 产品规格
-- 执行此 SQL 前确保 store_collections 和 store_products 表已创建

-- 产品线集合
INSERT INTO store_collections (collection_key, name_zh, name_en, description, is_active, sort_order)
VALUES ('sillyfu', '傻福虾盘', 'SillyFu', 'SillyFu AI USB 智能U盘 - 官方商城', TRUE, 1)
ON CONFLICT (collection_key) DO NOTHING;

-- 产品规格（示例：标准版 / 高速版 / Pro 版）

-- 标准版
INSERT INTO store_products (collection_id, product_key, name_zh, description_zh, image_url, price, stock_count, sort_order, is_active)
SELECT id, 'sillyfu-standard', '傻福虾盘 标准版', 'USB-A + USB-C 双接口 | 128G', '/static/img/sillyclaw/product-front-silver.png', 47900, 500, 1, TRUE
FROM store_collections WHERE collection_key = 'sillyfu'
ON CONFLICT DO NOTHING;

-- 高速版
INSERT INTO store_products (collection_id, product_key, name_zh, description_zh, image_url, price, stock_count, sort_order, is_active)
SELECT id, 'sillyfu-highspeed', '傻福虾盘 高速版', 'USB-A + USB-C 双接口 | 256G | 高速读写', '/static/img/sillyclaw/product-black.png', 84900, 300, 2, TRUE
FROM store_collections WHERE collection_key = 'sillyfu'
ON CONFLICT DO NOTHING;

-- Pro 版
INSERT INTO store_products (collection_id, product_key, name_zh, description_zh, image_url, price, stock_count, sort_order, is_active)
SELECT id, 'sillyfu-pro', '傻福虾盘 Pro', 'USB-A + USB-C 双接口 | 512G | 极速读写', '/static/img/sillyclaw/glowing.jpg', 148900, 200, 3, TRUE
FROM store_collections WHERE collection_key = 'sillyfu'
ON CONFLICT DO NOTHING;

-- 1TB 版
INSERT INTO store_products (collection_id, product_key, name_zh, description_zh, image_url, price, stock_count, sort_order, is_active)
SELECT id, 'sillyfu-1tb', '傻福虾盘 1TB版', 'USB-A + USB-C 双接口 | 1TB | 超大容量', '/static/img/sillyclaw/product-black.png', 208900, 100, 4, TRUE
FROM store_collections WHERE collection_key = 'sillyfu'
ON CONFLICT DO NOTHING;
