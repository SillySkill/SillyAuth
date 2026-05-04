-- 010_store_inventory_logs.sql
-- 库存变动流水表 - 进销存审计日志，支持外部ERP对接
--
-- 功能:
--   - 完整的入库/出库/盘点/订单扣减/订单取消流水记录
--   - 外部ERP系统对接字段 (external_ref, source, sync_status)
--   - 对账追溯支持 (stock_before → stock_after)
--   - 多条件索引加速查询

CREATE TABLE IF NOT EXISTS store_inventory_logs (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES store_products(id) ON DELETE CASCADE,
    change_type VARCHAR(20) NOT NULL
        CHECK (change_type IN ('in','out','adjust','order_deduct','order_cancel')),
    change_quantity INT NOT NULL,
    stock_before INT NOT NULL,
    stock_after INT NOT NULL,
    reference_no VARCHAR(100),              -- 内部关联单号（订单号/入库单号/出库单号）
    external_ref VARCHAR(100),              -- 外部ERP系统单据号（用于对接追溯）
    source VARCHAR(30) NOT NULL DEFAULT 'admin'
        CHECK (source IN ('admin', 'order', 'external_api', 'system')),
    note TEXT,
    operator_id BIGINT,                     -- 操作人 user_id
    operator_name VARCHAR(100),             -- 操作人姓名（方便外部系统记录）
    sync_status VARCHAR(20) DEFAULT 'local'
        CHECK (sync_status IN ('local', 'syncing', 'synced', 'sync_failed')),
    synced_at TIMESTAMPTZ,                  -- 同步到外部系统的时间
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_inventory_logs_product     ON store_inventory_logs(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_type        ON store_inventory_logs(change_type);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_date        ON store_inventory_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_source      ON store_inventory_logs(source);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_ref         ON store_inventory_logs(reference_no);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_ext_ref     ON store_inventory_logs(external_ref);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_sync        ON store_inventory_logs(sync_status);

COMMENT ON TABLE store_inventory_logs IS '库存变动流水表 - 进销存审计日志，支持外部ERP对接';
