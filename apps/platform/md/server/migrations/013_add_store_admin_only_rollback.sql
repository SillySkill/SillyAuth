-- 013 rollback: Remove test product and is_admin_only column

BEGIN;

-- 删除测试产品
DELETE FROM store_products WHERE product_key = 'sillyfu-test-001';

-- 移除列
ALTER TABLE store_products DROP COLUMN IF EXISTS is_admin_only;

COMMIT;
