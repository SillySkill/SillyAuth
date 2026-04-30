# PayPal Payment and Creator Settlement System

Complete guide to PayPal payment integration and creator settlement features for the SillyMD platform.

## Table of Contents

1. [Feature Overview](#feature-overview)
2. [Installation](#installation)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Integration Points](#integration-points)
6. [Configuration](#configuration)
7. [Admin Pages](#admin-pages)
8. [Migration Guide](#migration-guide)
9. [Common Errors](#common-errors)

---

## Feature Overview

### PayPal Payment Integration

The platform supports PayPal as a payment method alongside WeChat Pay and Alipay. Key features:

- Multiple payment channels (Web, Mobile App)
- Sandbox and production environments
- Webhook-based payment notifications
- Automatic signature verification

### Creator Settlement System

Creators can earn revenue from their paid content. Two settlement methods:

1. **Direct Commission** - Earnings accumulate and can be withdrawn to payment accounts
2. **Points Conversion** - Earnings automatically convert to platform points (1 CNY = 1 point)

### Key Features

- Automatic earnings calculation on every sale
- Configurable commission rates (global, category, user-specific)
- Settlement preferences per creator
- Batch settlement processing
- Complete transaction history

---

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Existing SillyMD platform installation
- PayPal Developer Account (for API credentials)

### Step 1: Database Migration

Run the migration scripts in order:

```bash
# Navigate to server directory
cd server

# Run migration 004 (if not already done)
psql -U sillymd_user -d sillymd_db -f migrations/004_add_ugc_and_payment.sql

# Run migration 005 (commission and points)
psql -U sillymd_user -d sillymd_db -f migrations/005_add_commission_and_points.sql

# Run migration 006 (PayPal and settlement)
psql -U sillymd_user -d sillymd_db -f migrations/006_add_paypal_and_settlement.sql
```

**Expected Output:**
```
Migration 006: PayPal and Creator Settlement completed successfully
```

### Step 2: Install Python Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary cryptography pyjwt
```

### Step 3: Configure Environment Variables

Create or update `.env` file in the server directory:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://sillymd_user:password@localhost/sillymd_db

# PayPal Configuration
PAYPAL_MODE=sandbox  # sandbox or live
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_WEBHOOK_ID=your_webhook_id

# WeChat Pay (if using)
WECHAT_APP_ID=your_wechat_app_id
WECHAT_MCH_ID=your_merchant_id
WECHAT_API_KEY=your_api_key
WECHAT_CERT_PATH=/path/to/apiclient_key.pem

# Alipay (if using)
ALIPAY_APP_ID=your_alipay_app_id
ALIPAY_PRIVATE_KEY=your_private_key
ALIPAY_PUBLIC_KEY=your_alipay_public_key
```

### Step 4: Update Payment Security Module

Edit `server/api/utils/payment_security.py` with your credentials:

```python
# PayPal Configuration
PAYPAL_CONFIG = {
    "client_id": "your_paypal_client_id",
    "client_secret": "your_paypal_client_secret",
    "mode": "sandbox",
    "webhook_id": "your_webhook_id"
}
```

### Step 5: Start the Server

```bash
cd server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Database Schema

### Core Tables

#### 1. payment_accounts

Platform's receiving account configurations.

```sql
CREATE TABLE payment_accounts (
    id SERIAL PRIMARY KEY,
    account_type VARCHAR(20) NOT NULL,  -- wechat, alipay, paypal, bank
    account_name VARCHAR(255) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    credentials JSONB NOT NULL,  -- Encrypted credentials
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'CNY',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_payment_accounts_type` on `account_type`
- `idx_payment_accounts_active` on `(is_active, priority DESC)`

**Example Record:**
```json
{
  "id": 1,
  "account_type": "paypal",
  "account_name": "PayPal-Sandbox",
  "account_id": "default_paypal_sandbox",
  "credentials": {
    "client_id": "ATxxxxxxxxxx",
    "client_secret": "EJxxxxxxxxxx",
    "mode": "sandbox"
  },
  "is_active": true,
  "is_primary": true,
  "priority": 100,
  "currency": "USD"
}
```

#### 2. creator_settlement_preferences

Creator-specific settlement settings.

```sql
CREATE TABLE creator_settlement_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    settlement_method VARCHAR(20) NOT NULL DEFAULT 'direct',  -- direct, points
    payment_account_type VARCHAR(20),
    payment_account_id VARCHAR(255),
    auto_settle BOOLEAN DEFAULT FALSE,
    min_settlement_amount DECIMAL(10, 2) DEFAULT 100.00,
    settlement_period VARCHAR(20) DEFAULT 'monthly',  -- weekly, monthly, quarterly
    bank_info JSONB,
    paypal_email VARCHAR(255),
    alipay_account VARCHAR(255),
    wechat_openid VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

**Settlement Methods:**
- `direct` - Accumulate earnings for withdrawal
- `points` - Auto-convert to platform points

#### 3. creator_earnings

Individual earning records from each sale.

```sql
CREATE TABLE creator_earnings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    content_type VARCHAR(20) NOT NULL,
    content_id INTEGER NOT NULL,
    product_id INTEGER REFERENCES paid_products(id) ON DELETE SET NULL,

    -- Amounts
    gross_amount DECIMAL(10, 2) NOT NULL,
    platform_commission DECIMAL(10, 2) NOT NULL,
    creator_share DECIMAL(10, 2) NOT NULL,

    -- Settlement Info
    settlement_status VARCHAR(20) DEFAULT 'pending',  -- pending, settled, points_converted
    settlement_method VARCHAR(20),
    settlement_amount DECIMAL(10, 2),
    settled_at TIMESTAMPTZ,

    -- Points Conversion
    points_awarded INTEGER,
    points_transaction_id INTEGER REFERENCES point_transactions(id) ON DELETE SET NULL,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

**Settlement Status Flow:**
```
pending → settled (direct withdrawal)
       → points_converted (automatic conversion)
```

#### 4. settlement_records

Batch settlement records.

```sql
CREATE TABLE settlement_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    batch_number VARCHAR(50) NOT NULL UNIQUE,

    -- Summary
    total_orders INTEGER NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    total_commission DECIMAL(10, 2) NOT NULL,
    total_earnings DECIMAL(10, 2) NOT NULL,

    -- Settlement
    settlement_method VARCHAR(20) NOT NULL,
    payment_account_type VARCHAR(20),
    payment_account_id VARCHAR(255),

    -- Status
    status VARCHAR(20) DEFAULT 'processing',  -- processing, completed, failed
    transaction_id VARCHAR(255),
    failure_reason TEXT,

    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ
);
```

### Trigger Functions

#### handle_creator_earnings()

Automatically processes creator earnings when order payment status changes to `paid`.

```sql
CREATE OR REPLACE FUNCTION handle_creator_earnings()
RETURNS TRIGGER AS $$
DECLARE
    v_product RECORD;
    v_commission_rate DECIMAL(5,2);
    v_creator_share DECIMAL(10,2);
    v_platform_share DECIMAL(10,2);
    v_settlement_pref RECORD;
BEGIN
    -- Only process paid orders
    IF NEW.payment_status != 'paid' OR OLD.payment_status = 'paid' THEN
        RETURN NEW;
    END IF;

    -- Get product and calculate commission
    -- ... (see full SQL in migration file)

    -- Check settlement preference
    IF v_settlement_pref.settlement_method = 'points' THEN
        -- Convert to points automatically
        -- Create point transaction, update user_points
    ELSE
        -- Create pending earning record
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Trigger:**
```sql
CREATE TRIGGER trigger_handle_creator_earnings
    AFTER UPDATE OF payment_status ON orders
    FOR EACH ROW
    EXECUTE FUNCTION handle_creator_earnings();
```

#### batch_settle_creator_earnings()

Batch processes pending earnings into a settlement.

```sql
CREATE OR REPLACE FUNCTION batch_settle_creator_earnings(
    p_user_id INTEGER,
    p_payment_account_type VARCHAR,
    p_payment_account_id VARCHAR
) RETURNS INTEGER AS $$
```

**Usage:**
```sql
SELECT batch_settle_creator_earnings(
    123,  -- user_id
    'alipay',  -- payment_account_type
    'user@example.com'  -- payment_account_id
);
```

### Views

#### v_creator_earnings_summary

Per-creator earnings summary.

```sql
CREATE VIEW v_creator_earnings_summary AS
SELECT
    u.id AS user_id,
    u.username,
    u.email,
    csp.settlement_method,
    csp.auto_settle,
    COUNT(DISTINCT ce.id) AS total_earnings_count,
    COALESCE(SUM(CASE WHEN ce.settlement_status = 'pending'
        THEN ce.creator_share ELSE 0 END), 0) AS pending_earnings,
    COALESCE(SUM(CASE WHEN ce.settlement_status = 'settled'
        THEN ce.settlement_amount ELSE 0 END), 0) AS settled_amount,
    COALESCE(SUM(CASE WHEN ce.settlement_status = 'points_converted'
        THEN ce.points_awarded ELSE 0 END), 0) AS points_earned
FROM users u
LEFT JOIN creator_settlement_preferences csp ON u.id = csp.user_id
LEFT JOIN creator_earnings ce ON u.id = ce.user_id
GROUP BY u.id, u.username, u.email, csp.settlement_method, csp.auto_settle;
```

**Query Example:**
```sql
SELECT * FROM v_creator_earnings_summary WHERE user_id = 123;
```

#### v_pending_settlements

List of creators with pending earnings above minimum threshold.

```sql
SELECT * FROM v_pending_settlements
ORDER BY total_pending_amount DESC;
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Admin Endpoints

#### Get Payment Accounts

```http
GET /api/payment/accounts
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `account_type` (optional) - Filter by type: `wechat`, `alipay`, `paypal`, `bank`
- `is_active` (optional) - Filter by active status: `true`, `false`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "account_type": "paypal",
      "account_name": "PayPal-Sandbox",
      "account_id": "default_paypal_sandbox",
      "credentials": {
        "client_id": "ATxxxxxxxx",
        "client_secret": "***HIDDEN***",
        "mode": "sandbox"
      },
      "is_active": true,
      "is_primary": true,
      "priority": 100,
      "currency": "USD",
      "description": "PayPal Sandbox Environment",
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:00:00Z"
    }
  ]
}
```

#### Create Payment Account

```http
POST /api/payment/accounts
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "account_type": "paypal",
  "account_name": "PayPal-Production",
  "account_id": "prod_paypal_001",
  "credentials": {
    "client_id": "ATxxxxxxxxxx",
    "client_secret": "EJxxxxxxxxxx",
    "mode": "live"
  },
  "currency": "USD",
  "is_active": true,
  "is_primary": false,
  "priority": 50,
  "description": "Production PayPal account"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "message": "收款账户创建成功"
  }
}
```

#### Update Payment Account

```http
PUT /api/payment/accounts/{account_id}
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "account_name": "PayPal-Sandbox-Updated",
  "is_active": true,
  "priority": 100
}
```

#### Delete Payment Account

```http
DELETE /api/payment/accounts/{account_id}
Authorization: Bearer {admin_token}
```

#### Get Pending Settlements (Admin)

```http
GET /api/payment/accounts/admin/pending-settlements
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "user_id": 123,
      "username": "creator_john",
      "email": "john@example.com",
      "settlement_method": "direct",
      "payment_account_type": "alipay",
      "payment_account_id": "john@example.com",
      "min_settlement_amount": 100.0,
      "pending_count": 45,
      "total_pending_amount": 2580.50,
      "oldest_earning_date": "2024-01-15T10:00:00Z",
      "latest_earning_date": "2024-02-01T15:30:00Z"
    }
  ]
}
```

#### Admin Settlement (Force)

```http
POST /api/payment/accounts/admin/settle/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "payment_account_type": "alipay",
  "payment_account_id": "john@example.com"
}
```

### Creator Endpoints

#### Get Settlement Preference

```http
GET /api/payment/accounts/creator/preference
Authorization: Bearer {creator_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "settlement_method": "direct",
    "payment_account_type": "alipay",
    "payment_account_id": "john@example.com",
    "auto_settle": false,
    "min_settlement_amount": 100.0,
    "settlement_period": "monthly",
    "paypal_email": null,
    "alipay_account": "john@example.com",
    "wechat_openid": null
  }
}
```

#### Update Settlement Preference

```http
PUT /api/payment/accounts/creator/preference
Authorization: Bearer {creator_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "settlement_method": "direct",
  "payment_account_type": "paypal",
  "payment_account_id": "john@example.com",
  "auto_settle": false,
  "min_settlement_amount": 100.00,
  "settlement_period": "monthly",
  "paypal_email": "john@example.com"
}
```

#### Get Earnings

```http
GET /api/payment/accounts/creator/earnings
Authorization: Bearer {creator_token}
```

**Query Parameters:**
- `status` (optional) - Filter by status: `pending`, `settled`, `points_converted`
- `page` (default: 1)
- `page_size` (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "order_id": 1001,
        "content_type": "tutorial",
        "content_id": 15,
        "gross_amount": 99.99,
        "platform_commission": 29.997,
        "creator_share": 69.993,
        "settlement_status": "pending",
        "settlement_method": "direct",
        "settlement_amount": 69.993,
        "points_awarded": null,
        "settled_at": null,
        "created_at": "2026-02-04T10:00:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  }
}
```

#### Get Earnings Summary

```http
GET /api/payment/accounts/creator/earnings/summary
Authorization: Bearer {creator_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "settlement_method": "direct",
    "auto_settle": false,
    "total_earnings_count": 150,
    "pending_earnings": 2580.50,
    "settled_amount": 12450.00,
    "points_earned": 5200,
    "total_orders_count": 150,
    "total_gross_amount": 17800.00,
    "total_platform_commission": 2769.50
  }
}
```

#### Request Settlement

```http
POST /api/payment/accounts/creator/settle
Authorization: Bearer {creator_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "payment_account_type": "alipay",
  "payment_account_id": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "settlement_id": 1,
    "message": "成功结算 2580.50 元"
  }
}
```

**Error Response (insufficient amount):**
```json
{
  "detail": "待结算金额不足 100 元，当前为 58.50 元"
}
```

#### Get Settlement Records

```http
GET /api/payment/accounts/creator/settlements
Authorization: Bearer {creator_token}
```

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "batch_number": "STL20260204123456789001",
        "total_orders": 45,
        "total_amount": 6800.00,
        "total_commission": 2040.00,
        "total_earnings": 4760.00,
        "settlement_method": "direct",
        "status": "completed",
        "transaction_id": "TXN2026020412345",
        "failure_reason": null,
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "created_at": "2024-02-01T10:00:00Z",
        "processed_at": "2024-02-01T14:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

### Payment Endpoints

#### Create Order

```http
POST /api/payment/orders
Authorization: Bearer {user_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "content_type": "tutorial",
  "content_id": 15,
  "purchase_type": "one_time"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order_number": "ORD20260204123456abc",
    "product_name": "Claude Code 入门教程",
    "original_price": 99.99,
    "discount_amount": 0.0,
    "final_price": 99.99,
    "currency": "CNY",
    "created_at": "2026-02-04T10:00:00Z"
  }
}
```

#### Create Payment (PayPal)

```http
POST /api/payment/pay
Authorization: Bearer {user_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "order_number": "ORD20260204123456abc",
  "payment_method": "paypal",
  "payment_channel": "paypal_web"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "payment_method": "paypal_web",
    "approval_url": "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=EC-XXXXXXXX",
    "order_id": "ORD20260204123456abc"
  }
}
```

#### PayPal Webhook Callback

```http
POST /api/payment/callback/paypal
```

**Headers:**
```
PAYPAL-TRANSMISSION-ID: xxxxx
PAYPAL-TRANSMISSION-TIME: 2026-02-04T10:00:00Z
PAYPAL-CERT-ID: xxxxx
PAYPAL-TRANSMISSION-SIG: xxxxx
```

**Event Types:**
- `PAYMENT.CAPTURE.COMPLETED` - Payment successful
- `PAYMENT.CAPTURE.DENIED` - Payment denied
- `PAYMENT.CAPTURE.PENDING` - Payment pending

**Webhook Payload (PAYMENT.CAPTURE.COMPLETED):**
```json
{
  "event_type": "PAYMENT.CAPTURE.COMPLETED",
  "resource": {
    "id": "3C1234567890",
    "status": "COMPLETED",
    "amount": {
      "currency_code": "USD",
      "value": "99.99"
    },
    "custom_id": "ORD20260204123456abc",
    "purchase_units": [
      {
        "custom_id": "ORD20260204123456abc",
        "payments": {
          "captures": [
            {
              "id": "3C1234567890"
            }
          ]
        }
      }
    ]
  }
}
```

---

## Integration Points

### Order Creation Flow

```
User Request → API → Create Order → Check Access → Calculate Price → Return Order Info
```

**Code Location:** `server/api/routes/payment.py`

```python
@router.post("/orders", response_model=dict)
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Check order idempotency
    # 2. Get content (tutorial/download)
    # 3. Verify it's paid content
    # 4. Check user already owns it
    # 5. Get product pricing
    # 6. Calculate final price with discounts
    # 7. Create order record
    # 8. Return order info
```

### Payment Processing Flow

```
Create Payment → Call Payment Gateway → User Pays → Callback → Verify → Update Order
```

**Key Integration Points:**

1. **Payment Creation** - `POST /api/payment/pay`
   - Generates payment parameters for PayPal/WeChat/Alipay
   - Creates `payment_records` entry

2. **Payment Callback** - `POST /api/payment/callback/{method}`
   - Verifies signature (security)
   - Validates amount
   - Updates order status
   - Triggers creator earnings (via database trigger)
   - Unlocks content
   - Updates product statistics
   - Awards points to buyer

3. **Creator Earnings** - Automatic via `handle_creator_earnings()` trigger
   - Executes when `orders.payment_status` changes to `paid`
   - Calculates commission based on rate
   - Creates `creator_earnings` record
   - Converts to points if preferred

### Commission Rate Calculation

**Function:** `get_commission_rate(content_type, content_id, creator_id)`

**Priority Order:**
1. Product-specific custom commission
2. Creator-specific rate (top creators: monthly sales > 1000 CNY)
3. Category-specific rate
4. Global default rate (30%)

**Example:**
```sql
-- Get commission for a tutorial by user 123
SELECT get_commission_rate('tutorial', 15, 123);
-- Returns: 25.00 (tutorial category rate)
```

### Content Unlocking

**Function:** `check_content_access(user_id, content_type, content_id)`

**Unlock Sources:**
- `purchase` - User purchased the content
- `subscription` - Active subscription
- `free` - Content is free
- `admin_grant` - Granted by admin

**Auto-unlock on Payment:**
```python
async def _unlock_content(order: Order, db: AsyncSession):
    unlock = ContentUnlock(
        user_id=order.user_id,
        content_type=order.content_type,
        content_id=order.content_id,
        unlock_source="purchase",
        order_id=order.id,
        order_number=order.order_number,
        unlocked_at=datetime.utcnow(),
        expires_at=order.expires_at  # NULL for one-time purchase
    )
    db.add(unlock)
    await db.commit()
```

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# PayPal
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=ATxxxxxxxxxx
PAYPAL_CLIENT_SECRET=EJxxxxxxxxxx
PAYPAL_WEBHOOK_ID=WEBHOOK_ID

# WeChat Pay
WECHAT_APP_ID=wx1234567890
WECHAT_MCH_ID=1234567890
WECHAT_API_KEY=your_api_key
WECHAT_CERT_PATH=/path/to/cert.pem

# Alipay
ALIPAY_APP_ID=2021001234567890
ALIPAY_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
ALIPAY_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
```

### Payment Account Setup

**Admin Panel Navigation:**
1. Login as admin
2. Go to "收款与结算管理" (Payment & Settlement Management)
3. Click "收款账户" (Payment Accounts) tab
4. Click "新增收款账户" (Add Account)

**Required Fields:**
- Account Type: `paypal`, `wechat`, `alipay`, `bank`
- Account Name: Display name
- Account ID: Unique identifier
- Credentials: JSON configuration

**Example PayPal Configuration:**
```json
{
  "client_id": "ATxxxxxxxxxx",
  "client_secret": "EJxxxxxxxxxx",
  "mode": "sandbox"
}
```

### Creator Settlement Preferences

**Creator Panel Navigation:**
1. Login as creator
2. Go to "创作者收益" (Creator Earnings)
3. Click "结算设置" (Settlement Settings) tab

**Configuration Options:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `settlement_method` | string | `direct` | `direct` or `points` |
| `payment_account_type` | string | null | `alipay`, `wechat`, `paypal`, `bank` |
| `payment_account_id` | string | null | Account identifier (email, account #) |
| `auto_settle` | boolean | `false` | Auto-settle on threshold |
| `min_settlement_amount` | decimal | `100.00` | Minimum for withdrawal (CNY) |
| `settlement_period` | string | `monthly` | `weekly`, `monthly`, `quarterly` |

**Direct Commission Example:**
```json
{
  "settlement_method": "direct",
  "payment_account_type": "paypal",
  "payment_account_id": "creator@example.com",
  "auto_settle": false,
  "min_settlement_amount": 100.00,
  "settlement_period": "monthly"
}
```

**Points Conversion Example:**
```json
{
  "settlement_method": "points",
  "auto_settle": true,
  "min_settlement_amount": 0.00
}
```

### Commission Settings

**Database Table:** `commission_settings`

**Default Values:**
```sql
-- Global default: 30% commission
INSERT INTO commission_settings (scope, commission_rate) VALUES
('global', 30.00);

-- Tutorial category: 25% commission
INSERT INTO commission_settings (scope, scope_id, commission_rate) VALUES
('category', 'tutorial', 25.00);

-- Top creators: 20% commission
INSERT INTO commission_settings (scope, commission_rate) VALUES
('top_creators', 20.00);
```

**Query Current Rates:**
```sql
SELECT * FROM commission_settings WHERE is_active = TRUE;
```

---

## Admin Pages

### PaymentAccountsManagement

**Location:** `admin/src/pages/PaymentAccountsManagement/index.tsx`

**Features:**

#### Tabs

1. **收款账户** (Payment Accounts)
   - List all payment accounts
   - Add/edit/delete accounts
   - Toggle active/primary status
   - Filter by account type

2. **待结算列表** (Pending Settlements)
   - View creators with pending earnings
   - See pending amounts and counts
   - Manual settlement trigger
   - Filterable by status

**Key Operations:**

**Add Payment Account:**
```typescript
const handleAddAccount = () => {
  setEditingAccount(null);
  setAccountModalVisible(true);
};
```

**Edit Account:**
```typescript
const handleEditAccount = (account: PaymentAccount) => {
  setEditingAccount(account);
  setAccountModalVisible(true);
};
```

**Delete Account:**
```typescript
const handleDeleteAccount = async (id: number) => {
  await paymentAccountsApi.delete(id);
  message.success('删除成功');
  loadAccounts();
};
```

**Manual Settlement:**
```typescript
const handleSettleCreator = async (userId: number, username: string) => {
  Modal.confirm({
    title: '结算创作者收益',
    content: `确认为创作者 "${username}" 结算所有待结算收益吗？`,
    onOk: async () => {
      await paymentAccountsApi.adminSettle(userId, { ... });
      message.success('结算成功');
      loadPendingSettlements();
    }
  });
};
```

**Table Columns:**

| Column | Description |
|--------|-------------|
| Type | Account type with icon |
| Account Name | Display name |
| Account ID | Unique identifier |
| Credentials | JSON config (hidden by default) |
| Currency | CNY, USD, EUR |
| Priority | Sort order |
| Status | Active/Primary tags |
| Actions | Edit/Delete buttons |

### CreatorEarnings

**Location:** `admin/src/pages/CreatorEarnings/index.tsx`

**Features:**

#### Tabs

1. **收益概览** (Overview)
   - Summary statistics
   - Pending/settled/points earned
   - Settlement method display
   - Settlement action button

2. **收益明细** (Earnings Details)
   - Paginated earnings list
   - Filter by status
   - Order information
   - Settlement status

3. **结算记录** (Settlement Records)
   - Batch settlement history
   - Transaction IDs
   - Processing status
   - Period ranges

4. **结算设置** (Settlement Settings)
   - Settlement method selection
   - Payment account configuration
   - Auto-settle toggle
   - Minimum amount setting

**Key Statistics Cards:**

```typescript
<Row gutter={16}>
  <Col span={6}>
    <Statistic
      title="待结算金额"
      value={summary.pending_earnings}
      precision={2}
      prefix="¥"
      valueStyle={{ color: '#faad14' }}
    />
  </Col>
  <Col span={6}>
    <Statistic
      title="已结算金额"
      value={summary.settled_amount}
      precision={2}
      prefix="¥"
      valueStyle={{ color: '#52c41a' }}
    />
  </Col>
  <Col span={6}>
    <Statistic
      title="积分收益"
      value={summary.points_earned}
      prefix={<GiftOutlined />}
      valueStyle={{ color: '#1890ff' }}
    />
  </Col>
  <Col span={6}>
    <Statistic
      title="总订单数"
      value={summary.total_orders_count}
      suffix="笔"
    />
  </Col>
</Row>
```

**Settlement Request:**
```typescript
const handleSettle = async () => {
  if (!summary || summary.pending_earnings < 100) {
    message.warning('待结算金额不足 100 元');
    return;
  }

  Modal.confirm({
    title: '申请结算',
    content: `确认结算待结算金额 ¥${summary.pending_earnings.toFixed(2)} 吗？`,
    onOk: async () => {
      await paymentAccountsApi.settle({ ... });
      message.success('结算申请已提交');
      loadData();
    }
  });
};
```

**Settings Form:**
```typescript
<Form
  layout="vertical"
  onFinish={handleSaveSettings}
  initialValues={{
    settlement_method: 'direct',
    auto_settle: false,
    min_settlement_amount: 100,
    settlement_period: 'monthly'
  }}
>
  <Form.Item label="结算方式" name="settlement_method">
    <Select>
      <Select.Option value="direct">直接分佣</Select.Option>
      <Select.Option value="points">积分转换</Select.Option>
    </Select>
  </Form.Item>

  <Form.Item label="收款方式" name="payment_account_type">
    <Select>
      <Select.Option value="alipay">支付宝</Select.Option>
      <Select.Option value="wechat">微信支付</Select.Option>
      <Select.Option value="paypal">PayPal</Select.Option>
      <Select.Option value="bank">银行账户</Select.Option>
    </Select>
  </Form.Item>

  <Form.Item label="收款账号" name="payment_account_id">
    <Input placeholder="输入您的收款账号" />
  </Form.Item>

  <Form.Item label="自动结算" name="auto_settle" valuePropName="checked">
    <Switch checkedChildren="开启" unCheckedChildren="关闭" />
  </Form.Item>

  <Form.Item label="最低结算金额" name="min_settlement_amount">
    <InputNumber
      style={{ width: '100%' }}
      min={10}
      max={100000}
      addonAfter="元"
    />
  </Form.Item>

  <Form.Item label="结算周期" name="settlement_period">
    <Select>
      <Select.Option value="weekly">每周结算</Select.Option>
      <Select.Option value="monthly">每月结算</Select.Option>
      <Select.Option value="quarterly">每季度结算</Select.Option>
    </Select>
  </Form.Item>
</Form>
```

---

## Migration Guide

### Step 1: Backup Database

```bash
pg_dump -U sillymd_user -d sillymd_db > backup_$(date +%Y%m%d).sql
```

### Step 2: Check Prerequisites

```sql
-- Check if migration 004 exists
SELECT * FROM information_schema.tables
WHERE table_name = 'paid_products';

-- Expected: paid_products table exists
```

### Step 3: Run Migrations in Order

```bash
# Migration 004 (if not already applied)
psql -U sillymd_user -d sillymd_db -f migrations/004_add_ugc_and_payment.sql

# Verify 004 success
psql -U sillymd_user -d sillymd_db -c "SELECT COUNT(*) FROM paid_products;"

# Migration 005 (commission and points)
psql -U sillymd_user -d sillymd_db -f migrations/005_add_commission_and_points.sql

# Verify 005 success
psql -U sillymd_user -d sillymd_db -c "SELECT * FROM commission_settings;"

# Migration 006 (PayPal and settlement)
psql -U sillymd_user -d sillymd_db -f migrations/006_add_paypal_and_settlement.sql

# Verify 006 success
psql -U sillymd_user -d sillymd_db -c "SELECT * FROM payment_accounts;"
```

### Step 4: Verify Database Schema

```sql
-- Check new tables
\dt payment_accounts
\dt creator_settlement_preferences
\dt creator_earnings
\dt settlement_records

-- Check views
\d+ v_creator_earnings_summary
\d+ v_pending_settlements

-- Check functions
\df get_commission_rate
\df handle_creator_earnings
\df batch_settle_creator_earnings

-- Check triggers
SELECT tgname, tgrelid::regclass
FROM pg_trigger
WHERE tgname LIKE '%creator%';
```

### Step 5: Configure Payment Accounts

```sql
-- Check default accounts
SELECT * FROM payment_accounts;

-- Update PayPal credentials
UPDATE payment_accounts
SET credentials = '{
  "client_id": "ATxxxxxxxxxx",
  "client_secret": "EJxxxxxxxxxx",
  "mode": "sandbox"
}'
WHERE account_type = 'paypal' AND account_id = 'default_paypal_sandbox';
```

### Step 6: Test Creator Earnings Flow

```sql
-- Create test product (if not exists)
INSERT INTO paid_products (content_type, content_id, product_name, price, creator_id, creator_share_percentage)
VALUES ('tutorial', 1, 'Test Tutorial', 99.99, 1, 70.00)
ON CONFLICT (content_type, content_id) DO NOTHING;

-- Create test order
INSERT INTO orders (order_number, user_id, content_type, content_id, product_id, product_name, original_price, final_price, payment_status)
VALUES ('TEST001', 2, 'tutorial', 1, 1, 'Test Tutorial', 99.99, 99.99, 'paid');

-- Check if earnings were created
SELECT * FROM creator_earnings WHERE order_id IN (SELECT id FROM orders WHERE order_number = 'TEST001');

-- Expected: One earning record with:
-- - gross_amount: 99.99
-- - platform_commission: ~30.00
-- - creator_share: ~70.00
```

### Step 7: Update API Routes

**File:** `server/api/main.py`

```python
# Add payment accounts router
from api.routes import payment_accounts

app.include_router(payment_accounts.router, prefix="/api/payment/accounts", tags=["收款账户管理"])

# Ensure payment router is included
from api.routes import payment

app.include_router(payment.router, prefix="/api/payment", tags=["支付和订阅"])
```

### Step 8: Update Admin Routes

**File:** `admin/src/router/index.tsx`

```typescript
import PaymentAccountsManagement from '../pages/PaymentAccountsManagement';
import CreatorEarnings from '../pages/CreatorEarnings';

const routes = [
  // ... existing routes
  {
    path: '/admin/payment-accounts',
    component: PaymentAccountsManagement,
    meta: { title: '收款账户管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/creator/earnings',
    component: CreatorEarnings,
    meta: { title: '创作者收益', requiresAuth: true }
  }
];
```

### Step 9: Test Payment Flow

1. **Create Order:**
```bash
curl -X POST http://localhost:8000/api/payment/orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "tutorial",
    "content_id": 1,
    "purchase_type": "one_time"
  }'
```

2. **Create Payment:**
```bash
curl -X POST http://localhost:8000/api/payment/pay \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD20260204123456abc",
    "payment_method": "paypal",
    "payment_channel": "paypal_web"
  }'
```

3. **Simulate PayPal Callback:**
```bash
# Use PayPal webhook simulator or manual test
# Verify earnings created in database
```

### Step 10: Monitoring and Verification

```sql
-- View pending settlements
SELECT * FROM v_pending_settlements;

-- View creator summary
SELECT * FROM v_creator_earnings_summary WHERE user_id = 1;

-- Check recent earnings
SELECT
    ce.*,
    o.order_number,
    u.username as creator_name
FROM creator_earnings ce
JOIN orders o ON ce.order_id = o.id
JOIN users u ON ce.user_id = u.id
ORDER BY ce.created_at DESC
LIMIT 10;
```

---

## Common Errors

### Database Errors

#### Error: Function get_commission_rate does not exist

**Cause:** Migration 005 not applied or failed.

**Solution:**
```bash
psql -U sillymd_user -d sillymd_db -f migrations/005_add_commission_and_points.sql
```

#### Error: Table creator_earnings does not exist

**Cause:** Migration 006 not applied.

**Solution:**
```bash
psql -U sillymd_user -d sillymd_db -f migrations/006_add_paypal_and_settlement.sql
```

### API Errors

#### Error: 401 Unauthorized

**Cause:** Invalid or missing authentication token.

**Solution:**
```bash
# Get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in Authorization header
Authorization: Bearer YOUR_TOKEN
```

#### Error: 403 Forbidden - "无权操作此订单"

**Cause:** User trying to access another user's order.

**Solution:** Ensure `order.user_id` matches `current_user.id`.

#### Error: 400 - "待结算金额不足 100 元"

**Cause:** Pending amount below minimum threshold.

**Solution:**
```sql
-- Check pending amount
SELECT SUM(creator_share)
FROM creator_earnings
WHERE user_id = YOUR_USER_ID AND settlement_status = 'pending';

-- Or update threshold
UPDATE creator_settlement_preferences
SET min_settlement_amount = 50.00
WHERE user_id = YOUR_USER_ID;
```

#### Error: "订单已存在，请继续支付"

**Cause:** Idempotency check found existing pending order.

**Solution:** This is expected behavior. Use existing order:
```bash
GET /api/payment/orders?status=pending
```

### Payment Errors

#### Error: PayPal Signature Verification Failed

**Cause:** Webhook ID mismatch or invalid headers.

**Solution:**
```python
# Check configuration
PAYPAL_CONFIG = {
    "webhook_id": "YOUR_ACTUAL_WEBHOOK_ID"  # Verify this matches PayPal dashboard
}

# Verify webhook headers
PAYPAL-TRANSMISSION-ID: present
PAYPAL-TRANSMISSION-TIME: present
PAYPAL-CERT-ID: present
PAYPAL-TRANSMISSION-SIG: present
```

#### Error: Amount Mismatch in Callback

**Cause:** Order amount doesn't match callback amount (possible tampering).

**Solution:**
```sql
-- Check order amount
SELECT final_price FROM orders WHERE order_number = 'ORDER_NUMBER';

-- Check callback amount in payment_records
SELECT amount, callback_data FROM payment_records WHERE order_number = 'ORDER_NUMBER';

-- If legitimate difference (e.g., currency conversion), update tolerance:
-- In payment_security.py
def validate_payment_amount(order_amount, callback_amount, tolerance=0.01):
    diff = abs(order_amount - callback_amount)
    return diff <= tolerance
```

### Settlement Errors

#### Error: Creator Earnings Not Created After Payment

**Cause:** Trigger not firing or product has no creator.

**Solution:**
```sql
-- Check product has creator_id
SELECT id, creator_id FROM paid_products WHERE id = PRODUCT_ID;

-- Check trigger exists
SELECT tgname, tgrelid::regclass
FROM pg_trigger
WHERE tgname = 'trigger_handle_creator_earnings';

-- Manually trigger if needed
SELECT handle_creator_earnings();
```

#### Error: Points Not Converted

**Cause:** Settlement preference not set to 'points'.

**Solution:**
```sql
-- Check preference
SELECT * FROM creator_settlement_preferences WHERE user_id = USER_ID;

-- Update to points method
UPDATE creator_settlement_preferences
SET settlement_method = 'points'
WHERE user_id = USER_ID;
```

#### Error: Settlement Batch Failed

**Cause:** Payment account details invalid or insufficient funds.

**Solution:**
```sql
-- Check settlement record for failure reason
SELECT * FROM settlement_records
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Common failure_reason values:
-- - "Invalid PayPal email"
-- - "Alipay account not found"
-- - "Bank account verification failed"
```

### Configuration Errors

#### Error: PayPal Client ID Invalid

**Cause:** Incorrect credentials or mode mismatch.

**Solution:**
```bash
# Check .env file
PAYPAL_MODE=sandbox  # Should match credential type
PAYPAL_CLIENT_ID=ATxxxxxxxxxx  # Should start with AT for PayPal

# Verify in PayPal Developer Dashboard
# https://developer.paypal.com/dashboard/
```

#### Error: Database Connection Failed

**Cause:** DATABASE_URL incorrect or database not running.

**Solution:**
```bash
# Check PostgreSQL is running
psql -U sillymd_user -d sillymd_db

# Test connection string
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://sillymd_user:password@localhost/sillymd_db'); print(engine.connect())"

# Update .env with correct format
DATABASE_URL=postgresql+asyncpg://sillymd_user:password@localhost/sillymd_db
```

### Debugging Tips

#### Enable SQL Logging

```python
# In server/api/database.py
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

#### Check Trigger Execution

```sql
-- Create test table to log trigger calls
CREATE TABLE trigger_log (
    id SERIAL PRIMARY KEY,
    trigger_name VARCHAR(100),
    order_id INTEGER,
    executed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Add logging to trigger
CREATE OR REPLACE FUNCTION handle_creator_earnings()
RETURNS TRIGGER AS $$
BEGIN
    -- Log execution
    INSERT INTO trigger_log (trigger_name, order_id)
    VALUES ('handle_creator_earnings', NEW.id);

    -- ... rest of function

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Check logs
SELECT * FROM trigger_log ORDER BY executed_at DESC;
```

#### View Earnings Calculation

```sql
-- Trace earnings for specific order
SELECT
    o.id as order_id,
    o.order_number,
    o.final_price,
    o.payment_status,
    pp.creator_id,
    pp.creator_share_percentage,
    ce.id as earning_id,
    ce.gross_amount,
    ce.platform_commission,
    ce.creator_share,
    ce.settlement_status,
    ce.settlement_method,
    ce.points_awarded
FROM orders o
JOIN paid_products pp ON o.product_id = pp.id
LEFT JOIN creator_earnings ce ON o.id = ce.order_id
WHERE o.order_number = 'YOUR_ORDER_NUMBER';
```

---

## Phase 1 Update

> **Status**: Payment module migrated from `server/api/routes/payment.py` to `src/modules/payment/`.
> All 4 pending TODOs completed with database integration via `src/core/db_adapter.py`.

### Architecture Changes

| Item | Before | After |
|------|--------|-------|
| Location | `server/api/routes/payment.py` | `src/modules/payment/` |
| DB Access | SQLAlchemy + AsyncSession | `src/core/db_adapter.py` (psycopg2) |
| API Base | `/api/payment/*` | `/api/v1/payment/*` |
| Entry Point | `server/api/main.py` | `src/main.py` |

---

## Additional Resources

### Related Documentation

- [Migration 004: UGC and Payment System](../server/migrations/004_add_ugc_and_payment.sql)
- [Migration 005: Commission and Points](../server/migrations/005_add_commission_and_points.sql)
- [Migration 006: PayPal and Settlement](../server/migrations/006_add_paypal_and_settlement.sql)
- [Payment Security Module](../server/api/utils/payment_security.py)

### API References

- [Payment API Routes](../server/api/routes/payment.py)
- [Payment Accounts API Routes](../server/api/routes/payment_accounts.py)

### Admin Pages

- [Payment Accounts Management](../admin/src/pages/PaymentAccountsManagement/index.tsx)
- [Creator Earnings](../admin/src/pages/CreatorEarnings/index.tsx)

### External Links

- [PayPal Developer Documentation](https://developer.paypal.com/docs/)
- [PayPal Webhooks Verification](https://developer.paypal.com/docs/api-basics/notifications/webhooks/rest/#verify-the-webhook-message)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/sql-createtrigger.html)
