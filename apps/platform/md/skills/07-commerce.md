# 第七章：商用授权与交易系统

> 本文档描述 SillyMD 平台的商用 Skills 交易和授权机制。
>
> 本章涵盖商用授权与交易系统所需的所有数据库表结构设计。

## 7.0 数据库设计

### 7.0.1 枚举类型定义

```sql
-- ============================================
-- 商用交易系统枚举类型
-- ============================================

CREATE TYPE order_status AS ENUM ('pending', 'paid', 'completed', 'cancelled', 'refunded');
CREATE TYPE payment_method_type AS ENUM ('balance', 'alipay', 'wechat', 'bank');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'success', 'failed', 'cancelled');
CREATE TYPE withdrawal_method AS ENUM ('alipay', 'wechat', 'bank');
CREATE TYPE withdrawal_status AS ENUM ('pending', 'processing', 'completed', 'rejected', 'cancelled');
CREATE TYPE commerce_transaction_type AS ENUM ('recharge', 'consume', 'refund', 'income', 'withdraw', 'reward', 'commission', 'fee');
CREATE TYPE discount_type AS ENUM ('percentage', 'fixed');
CREATE TYPE promo_user_type AS ENUM ('all', 'new', 'vip');
```

### 7.0.2 订单表 (orders)

```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    buyer_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    license_type license_type NOT NULL DEFAULT 'personal',
    quantity INT NOT NULL DEFAULT 1,
    unit_price INT NOT NULL,
    total_amount INT NOT NULL,
    platform_fee INT NOT NULL,
    seller_income INT NOT NULL,
    status order_status NOT NULL DEFAULT 'pending',
    payment_method payment_method_type,
    paid_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    refund_amount INT DEFAULT 0,
    refund_reason TEXT,
    refunded_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (seller_id) REFERENCES users(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- 索引
CREATE INDEX idx_orders_buyer_id ON orders(buyer_id);
CREATE INDEX idx_orders_seller_id ON orders(seller_id);
CREATE INDEX idx_orders_skill_id ON orders(skill_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 表注释
COMMENT ON TABLE orders IS '商用 Skills 订单主表';
COMMENT ON COLUMN orders.id IS '订单 ID';
COMMENT ON COLUMN orders.order_no IS '订单编号（唯一）';
COMMENT ON COLUMN orders.buyer_id IS '购买者 ID';
COMMENT ON COLUMN orders.seller_id IS '供应商 ID';
COMMENT ON COLUMN orders.skill_id IS 'Skill ID';
COMMENT ON COLUMN orders.license_type IS '授权类型：personal/team/enterprise';
COMMENT ON COLUMN orders.quantity IS '购买数量';
COMMENT ON COLUMN orders.unit_price IS '单价（积分）';
COMMENT ON COLUMN orders.total_amount IS '订单总金额（积分）';
COMMENT ON COLUMN orders.platform_fee IS '平台手续费（积分）';
COMMENT ON COLUMN orders.seller_income IS '供应商收入（积分）';
COMMENT ON COLUMN orders.status IS '订单状态：pending/paid/completed/cancelled/refunded';
COMMENT ON COLUMN orders.payment_method IS '支付方式：balance/alipay/wechat/bank';
COMMENT ON COLUMN orders.paid_at IS '支付时间';
COMMENT ON COLUMN orders.completed_at IS '完成时间';
COMMENT ON COLUMN orders.cancelled_at IS '取消时间';
COMMENT ON COLUMN orders.refund_amount IS '退款金额（积分）';
COMMENT ON COLUMN orders.refund_reason IS '退款原因';
COMMENT ON COLUMN orders.refunded_at IS '退款时间';
COMMENT ON COLUMN orders.client_ip IS '客户端 IP';
COMMENT ON COLUMN orders.user_agent IS '用户代理';
```

### 7.0.3 支付记录表 (payments)

```sql
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    payment_no VARCHAR(32) UNIQUE NOT NULL,
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    payment_method payment_method_type NOT NULL,
    payment_channel VARCHAR(50),
    transaction_id VARCHAR(100),
    status payment_status NOT NULL DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    failure_reason TEXT,
    callback_data JSONB,
    client_ip VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_payments_payment_no ON payments(payment_no);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 7.0.4 提现记录表 (withdrawal_requests)

```sql
-- 注意: 提现申请表使用 19-admin-backend.md 中定义的 withdrawal_requests
-- 本文档保留以下扩展字段的说明
-- withdrawal_requests 表包含以下字段:
--   - id, user_id, amount, fee, actual_amount (基础字段)
--   - method, account_info, status (提现相关)
--   - transaction_id, rejection_reason, processed_by, processed_at (处理相关)

-- 商用扩展字段 (需要在 19-admin-backend.md 中添加):
--   - withdrawal_no VARCHAR(32) UNIQUE: 提现单号
--   - exchange_rate NUMERIC(10,4): 汇率 (积分转人民币)
--   - cny_amount NUMERIC(10,2): 人民币金额
--   - account_name VARCHAR(100): 账户名称
--   - admin_note TEXT: 管理员备注

-- 外键引用:
--   FOREIGN KEY (user_id) REFERENCES users(id)
--   FOREIGN KEY (processed_by) REFERENCES admin_users(id) ON DELETE SET NULL
```

### 7.0.5 供应商等级表 (vendor_tiers)

```sql
CREATE TABLE vendor_tiers (
    id BIGSERIAL PRIMARY KEY,
    tier_name VARCHAR(50) UNIQUE NOT NULL,
    tier_level INT NOT NULL,
    min_sales INT NOT NULL DEFAULT 0,
    min_products INT NOT NULL DEFAULT 0,
    min_rating NUMERIC(3,2) NOT NULL DEFAULT 0.00,
    commission_rate NUMERIC(4,3) NOT NULL,
    benefits JSONB,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_vendor_tiers_tier_level ON vendor_tiers(tier_level);
CREATE INDEX idx_vendor_tiers_is_active ON vendor_tiers(is_active);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_vendor_tiers_updated_at BEFORE UPDATE ON vendor_tiers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化等级数据
INSERT INTO vendor_tiers (tier_name, tier_level, min_sales, min_products, min_rating, commission_rate, benefits, description) VALUES
('青铜供应商', 1, 0, 1, 0.00, 0.150, '{"badge": "bronze", "support": "basic"}', '入门级供应商'),
('白银供应商', 2, 5000, 5, 4.00, 0.140, '{"badge": "silver", "support": "priority"}', '进阶级供应商'),
('黄金供应商', 3, 20000, 10, 4.50, 0.130, '{"badge": "gold", "support": "dedicated"}', '优质供应商'),
('铂金供应商', 4, 100000, 20, 4.80, 0.120, '{"badge": "platinum", "support": "vip"}', '顶级供应商'),
('钻石供应商', 5, 500000, 50, 4.90, 0.100, '{"badge": "diamond", "support": "exclusive"}', '旗舰供应商');
```

### 7.0.6 佣金记录表 (commission_records)

```sql
CREATE TABLE commission_records (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    amount INT NOT NULL,
    rate NUMERIC(4,3) NOT NULL,
    tier_id BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    available_at TIMESTAMPTZ,
    withdrawn_at TIMESTAMPTZ,
    withdrawal_id BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (seller_id) REFERENCES users(id),
    FOREIGN KEY (tier_id) REFERENCES vendor_tiers(id),
    FOREIGN KEY (withdrawal_id) REFERENCES withdrawals(id)
);

-- 索引
CREATE INDEX idx_commission_records_seller_id ON commission_records(seller_id);
CREATE INDEX idx_commission_records_status ON commission_records(status);
CREATE INDEX idx_commission_records_created_at ON commission_records(created_at);
```

### 7.0.7 优惠码表 (promo_codes)

```sql
CREATE TABLE promo_codes (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    discount_type discount_type NOT NULL,
    discount_value INT NOT NULL,
    min_order_amount INT DEFAULT 0,
    max_discount_amount INT DEFAULT NULL,
    usage_limit INT DEFAULT NULL,
    used_count INT DEFAULT 0,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    applicable_skills JSONB,
    user_type promo_user_type NOT NULL DEFAULT 'all',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admin_users(id)
);

-- 索引
CREATE INDEX idx_promo_codes_code ON promo_codes(code);
CREATE INDEX idx_promo_codes_is_active ON promo_codes(is_active);
CREATE INDEX idx_promo_codes_valid_period ON promo_codes(valid_from, valid_until);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_promo_codes_updated_at BEFORE UPDATE ON promo_codes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 7.0.8 交易流水表 (commerce_transactions)

```sql
CREATE TABLE commerce_transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_no VARCHAR(32) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    transaction_type commerce_transaction_type NOT NULL,
    amount INT NOT NULL,
    balance_before INT NOT NULL,
    balance_after INT NOT NULL,
    related_id BIGINT,
    related_type VARCHAR(50),
    description VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_commerce_transactions_transaction_no ON commerce_transactions(transaction_no);
CREATE INDEX idx_commerce_transactions_user_id ON commerce_transactions(user_id);
CREATE INDEX idx_commerce_transactions_transaction_type ON commerce_transactions(transaction_type);
CREATE INDEX idx_commerce_transactions_created_at ON commerce_transactions(created_at);
```

### 7.0.9 充值记录表 (recharge_records)

```sql
CREATE TABLE recharge_records (
    id BIGSERIAL PRIMARY KEY,
    recharge_no VARCHAR(32) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    cny_amount NUMERIC(10,2) NOT NULL,
    bonus_amount INT DEFAULT 0,
    payment_method payment_method_type NOT NULL,
    payment_no VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    failure_reason TEXT,
    promo_code_id BIGINT,
    client_ip VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (promo_code_id) REFERENCES promo_codes(id)
);

-- 索引
CREATE INDEX idx_recharge_records_recharge_no ON recharge_records(recharge_no);
CREATE INDEX idx_recharge_records_user_id ON recharge_records(user_id);
CREATE INDEX idx_recharge_records_status ON recharge_records(status);
CREATE INDEX idx_recharge_records_created_at ON recharge_records(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_recharge_records_updated_at BEFORE UPDATE ON recharge_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 7.0.10 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    商用授权与交易系统数据库关系图                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐                              │
│  │    users     │         │    orders    │                              │
│  │              │────────>│              │                              │
│  │ - id         │ (buyer) │ - id         │                              │
│  │ - balance    │         │ - order_no   │                              │
│  └──────────────┘         │ - buyer_id   │                              │
│            │              │ - seller_id  │                              │
│            │              └──────┬───────┘                              │
│            v                     │                                       │
│  ┌──────────────────┐           │                     ┌──────────────┐ │
│  │commerce_transactions│<────────┴────────────────────>│  payments    │ │
│  │                  │                                │              │ │
│  │ - user_id        │                                │ - order_id   │ │
│  │ - amount         │                                └──────────────┘ │
│  │ - balance_after  │                                                 │
│  └──────────────────┘                                                 │
│            ↑                                                            │
│            │                                                            │
│  ┌─────────┴────────┐         ┌──────────────┐                         │
│  │recharge_records  │         │ withdrawals  │                         │
│  │                  │         │              │                         │
│  │ - user_id        │         │ - user_id    │                         │
│  │ - amount         │         │ - amount     │                         │
│  └──────────────────┘         │ - processed_by│                         │
│                                └──────┬───────┘                         │
│  ┌──────────────┐                     │                                 │
│  │promo_codes   │                     v                                 │
│  │              │            ┌──────────────────┐                      │
│  │ - code        │            │ commission_records│                     │
│  │ - discount    │            │                  │                      │
│  └──────────────┘            │ - seller_id      │                      │
│                              │ - order_id       │                      │
│  ┌──────────────┐            │ - tier_id        │                      │
│  │vendor_tiers  │            └──────────────────┘                      │
│  │              │                                                       │
│  │ - tier_level  │                                                       │
│  │ - commission  │                                                       │
│  └──────────────┘                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 7.1 AI 积分体系

**AI Points (AI 积分)** 是平台内的虚拟积分单位。

| 获取方式 | 说明 |
|----------|------|
| 充值购买 | 支持支付宝、微信、银行卡 |
| 销售收益 | 出售商用 Skills 获得 |
| 活动奖励 | 平台活动、推广奖励 |
| 贡献奖励 | 贡献优质免费 Skills |
| 邀请奖励 | 邀请新用户注册 |
| 成就奖励 | 解锁成就获得 |

## 7.2 商用 Skills 定价策略

| Skills 类型 | 建议价格区间 | 说明 |
|-------------|--------------|------|
| 基础工具类 | 100-500 AI Points | 通用脚本、模板 |
| 专业应用类 | 500-2000 AI Points | 行业解决方案 |
| 企业级方案 | 2000-10000 AI Points | 完整系统、复杂集成 |
| 独家定制类 | 10000+ AI Points | 高度定制化 |

## 7.3 授权类型与价格

| 授权类型 | 价格倍数 | 使用范围 | 说明 |
|----------|----------|----------|------|
| **个人授权** | 1x | 单用户使用 | 仅供个人使用 |
| **团队授权** | 3x | 团队内共享 (最多 10 人) | 同一团队内使用 |
| **企业授权** | 10x | 企业内使用 (无人数限制) | 整个企业使用 |

## 7.4 授权验证机制

### SDK 验证

```javascript
// SDK 自动验证授权
const client = new SillyClient({
  apiKey: process.env.SILLY_API_KEY,
  licenseKey: process.env.SILLY_LICENSE_KEY
});

const skill = await client.skills.get('commercial-skill-id');
// SDK 自动：
// 1. 验证 licenseKey 有效性
// 2. 检查授权类型
// 3. 检查是否过期
// 4. 记录访问日志
```

### 离线验证

```javascript
// 授权证书（可离线使用）
const licenseCertificate = {
  license_id: "lic_abc123",
  skill_id: "com-payment-gateway",
  user_id: 12345,
  license_type: "team",
  expires_at: 1737657600,
  signature: "0xabc123...",
  public_key: "0xdef456..."
};

// 本地验证签名
function verifyLicense(certificate) {
  const data = `${certificate.license_id}:${certificate.skill_id}:${certificate.user_id}:${certificate.license_type}:${certificate.expires_at}`;
  return verifySignature(data, certificate.signature, certificate.public_key);
}
```

## 7.5 交易流程

```
┌─────────────────────────────────────────────────────────────┐
│                    交易流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  买家                                                      │
│    ├── 浏览商用 Skills                                     │
│    ├── 查看授权类型和价格                                  │
│    ├── 选择授权类型 (个人/团队/企业)                        │
│    ├── 确认订单，扣除 AI Points                            │
│    └── 获得授权许可 + 授权密钥                             │
│                                                             │
│  平台                                                      │
│    ├── 记录交易                                            │
│    ├── 生成授权密钥                                        │
│    ├── 平台抽成 (15-20%)                                   │
│    └── 供应商到账 (80-85%)                                 │
│                                                             │
│  供应商                                                    │
│    ├── 查看销售数据                                        │
│    ├── AI Points 余额增加                                  │
│    ├── 销售通知推送                                        │
│    └── 可申请提现                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 7.6 平台抽成规则

| 供应商等级 | 累计销售额 | 平台抽成 | 供应商收益 | 特权 |
|------------|--------|----------|------------|------|
| 普通供应商 | - | 20% | 80% | 基础功能 |
| 优质供应商 | ≥ 5,000 Points | 15% | 85% | 更多审核额度 |
| 金牌供应商 | ≥ 50,000 Points | 10% | 90% | 优先推荐、专属客服 |

## 7.7 提现规则

| 规则项 | 说明 |
|--------|------|
| 最低提现 | 500 AI Points |
| 提现周期 | 每周一处理 |
| 提现方式 | 支付宝、银行转账 |
| 汇率 | 100 AI Points = 10 元人民币 |
| 手续费 | 免费（平台承担） |
