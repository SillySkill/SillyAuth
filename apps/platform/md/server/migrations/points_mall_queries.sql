-- 积分商城常用SQL查询
-- 用于管理和调试积分商城系统

-- ============================================
-- 1. 查看所有商品
-- ============================================
SELECT
    p.id,
    p.product_key,
    p.name_zh AS "商品名称",
    c.name_zh AS "分类",
    p.points_required AS "所需积分",
    CASE
        WHEN p.stock_count = -1 THEN '无限'
        ELSE p.stock_count::TEXT
    END AS "库存",
    p.sold_count AS "已售",
    p.is_active AS "上架",
    p.is_featured AS "精选",
    p.created_at AS "创建时间"
FROM points_products p
LEFT JOIN points_categories c ON p.category_key = c.category_key
ORDER BY p.created_at DESC;

-- ============================================
-- 2. 查看热门商品（按销量排序）
-- ============================================
SELECT
    p.id,
    p.name_zh AS "商品名称",
    c.name_zh AS "分类",
    p.points_required AS "积分",
    p.sold_count AS "销量",
    p.stock_count AS "库存"
FROM points_products p
LEFT JOIN points_categories c ON p.category_key = c.category_key
WHERE p.is_active = TRUE
ORDER BY p.sold_count DESC
LIMIT 10;

-- ============================================
-- 3. 查看库存紧张的商品
-- ============================================
SELECT
    p.id,
    p.name_zh AS "商品名称",
    p.points_required AS "积分",
    p.stock_count AS "剩余库存",
    p.sold_count AS "已售"
FROM points_products p
WHERE p.is_active = TRUE
  AND p.stock_count != -1
  AND p.stock_count <= 10
ORDER BY p.stock_count ASC;

-- ============================================
-- 4. 查看用户兑换记录
-- ============================================
SELECT
    e.id,
    e.exchange_no AS "兑换号",
    u.username AS "用户",
    p.name_zh AS "商品",
    e.points_used AS "消耗积分",
    e.quantity AS "数量",
    e.status AS "状态",
    e.created_at AS "兑换时间"
FROM points_exchange_records e
LEFT JOIN users u ON e.user_id = u.id
LEFT JOIN points_products p ON e.product_id = p.id
ORDER BY e.created_at DESC
LIMIT 50;

-- ============================================
-- 5. 查看今日兑换统计
-- ============================================
SELECT
    COUNT(*) AS "兑换订单数",
    SUM(points_used) AS "总消耗积分",
    COUNT(DISTINCT user_id) AS "兑换用户数"
FROM points_exchange_records
WHERE DATE(created_at) = CURRENT_DATE
  AND status = 'completed';

-- ============================================
-- 6. 查看商城总体统计
-- ============================================
SELECT
    -- 商品统计
    (SELECT COUNT(*) FROM points_products WHERE is_active = TRUE) AS "总商品数",
    (SELECT COUNT(*) FROM points_products WHERE is_featured = TRUE) AS "精选商品数",

    -- 兑换统计
    (SELECT COUNT(*) FROM points_exchange_records WHERE status = 'completed') AS "总兑换次数",
    (SELECT COALESCE(SUM(points_used), 0) FROM points_exchange_records WHERE status = 'completed') AS "总消耗积分",

    -- 用户统计
    (SELECT COUNT(DISTINCT user_id) FROM points_exchange_records) AS "参与用户数",

    -- 今日统计
    (SELECT COUNT(*) FROM points_exchange_records WHERE DATE(created_at) = CURRENT_DATE AND status = 'completed') AS "今日兑换",
    (SELECT COALESCE(SUM(points_used), 0) FROM points_exchange_records WHERE DATE(created_at) = CURRENT_DATE AND status = 'completed') AS "今日消耗积分";

-- ============================================
-- 7. 查看用户积分排行榜
-- ============================================
SELECT
    u.id,
    u.username AS "用户名",
    u.ai_points AS "当前积分",
    (SELECT COUNT(*) FROM points_exchange_records WHERE user_id = u.id AND status = 'completed') AS "兑换次数",
    (SELECT COALESCE(SUM(points_used), 0) FROM points_exchange_records WHERE user_id = u.id AND status = 'completed') AS "累计消耗"
FROM users u
WHERE u.is_active = TRUE
ORDER BY u.ai_points DESC
LIMIT 20;

-- ============================================
-- 8. 查看分类商品分布
-- ============================================
SELECT
    c.name_zh AS "分类",
    c.icon AS "图标",
    COUNT(p.id) AS "商品数量",
    SUM(p.sold_count) AS "总销量",
    AVG(p.points_required) AS "平均积分"
FROM points_categories c
LEFT JOIN points_products p ON c.category_key = p.category_key AND p.is_active = TRUE
GROUP BY c.id, c.name_zh, c.icon
ORDER BY COUNT(p.id) DESC;

-- ============================================
-- 9. 查看购物车数据
-- ============================================
SELECT
    u.username AS "用户",
    p.name_zh AS "商品",
    c.quantity AS "数量",
    p.points_required AS "单价",
    (p.points_required * c.quantity) AS "总价",
    c.created_at AS "添加时间"
FROM points_shopping_cart c
LEFT JOIN users u ON c.user_id = u.id
LEFT JOIN points_products p ON c.product_id = p.id
ORDER BY c.created_at DESC;

-- ============================================
-- 10. 查看待清理的购物车（商品已下架）
-- ============================================
SELECT
    c.id AS "cart_id",
    c.user_id,
    u.username,
    c.product_id,
    p.name_zh
FROM points_shopping_cart c
LEFT JOIN users u ON c.user_id = u.id
LEFT JOIN points_products p ON c.product_id = p.id
WHERE p.is_active = FALSE OR p.id IS NULL;

-- ============================================
-- 11. 清理无效购物车项
-- ============================================
-- DELETE FROM points_shopping_cart
-- WHERE product_id IN (
--     SELECT id FROM points_products WHERE is_active = FALSE
-- );

-- ============================================
-- 12. 查看用户积分明细
-- ============================================
-- 替换 {user_id} 为实际用户ID
SELECT
    u.username AS "用户",
    u.ai_points AS "当前积分",
    (SELECT COUNT(*) FROM points_exchange_records WHERE user_id = u.id AND status = 'completed') AS "兑换次数",
    (SELECT COALESCE(SUM(points_used), 0) FROM points_exchange_records WHERE user_id = u.id AND status = 'completed') AS "累计消耗",
    (SELECT MAX(created_at) FROM points_exchange_records WHERE user_id = u.id) AS "最后兑换时间"
FROM users u
WHERE u.id = 1; -- 替换为实际用户ID

-- ============================================
-- 13. 添加新商品模板
-- ============================================
-- INSERT INTO points_products (
--     product_key,
--     category_key,
--     name_en,
--     name_zh,
--     description_en,
--     description_zh,
--     points_required,
--     stock_count,
--     is_featured,
--     sort_order,
--     valid_days
-- ) VALUES (
--     'your_product_key',
--     'content', -- content, coupon, vip, custom
--     'Product Name',
--     '商品名称',
--     'Description',
--     '商品描述',
--     100, -- 积分
--     -1, -- -1表示无限库存
--     false,
--     0,
--     NULL -- 有效期天数，NULL表示永久
-- );

-- ============================================
-- 14. 更新商品库存
-- ============================================
-- UPDATE points_products
-- SET stock_count = 100
-- WHERE product_key = 'your_product_key';

-- ============================================
-- 15. 批量上架/下架商品
-- ============================================
-- 上架
-- UPDATE points_products SET is_active = TRUE WHERE category_key = 'content';

-- 下架
-- UPDATE points_products SET is_active = FALSE WHERE category_key = 'coupon';

-- ============================================
-- 16. 重置商品销量（慎用）
-- ============================================
-- UPDATE points_products SET sold_count = 0;

-- ============================================
-- 17. 查看兑换失败的记录
-- ============================================
SELECT
    e.*,
    u.username
FROM points_exchange_records e
LEFT JOIN users u ON e.user_id = u.id
WHERE e.status != 'completed'
ORDER BY e.created_at DESC;

-- ============================================
-- 18. 查看最近7天的兑换趋势
-- ============================================
SELECT
    DATE(created_at) AS "日期",
    COUNT(*) AS "兑换次数",
    SUM(points_used) AS "消耗积分",
    COUNT(DISTINCT user_id) AS "活跃用户"
FROM points_exchange_records
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
  AND status = 'completed'
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;

-- ============================================
-- 19. 查看最受欢迎的商品类型
-- ============================================
SELECT
    c.name_zh AS "分类",
    COUNT(e.id) AS "兑换次数",
    SUM(e.points_used) AS "总积分消耗",
    AVG(p.points_required) AS "平均积分"
FROM points_exchange_records e
LEFT JOIN points_products p ON e.product_id = p.id
LEFT JOIN points_categories c ON p.category_key = c.category_key
WHERE e.status = 'completed'
GROUP BY c.id, c.name_zh
ORDER BY COUNT(e.id) DESC;

-- ============================================
-- 20. 生成兑换报表（按月）
-- ============================================
SELECT
    TO_CHAR(created_at, 'YYYY-MM') AS "月份",
    COUNT(*) AS "订单数",
    SUM(points_used) AS "总积分",
    COUNT(DISTINCT user_id) AS "用户数",
    AVG(points_used) AS "平均订单积分"
FROM points_exchange_records
WHERE status = 'completed'
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY TO_CHAR(created_at, 'YYYY-MM') DESC;
