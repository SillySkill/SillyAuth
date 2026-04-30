# PayPal 集成文档

## 目录
- [概述](#概述)
- [配置步骤](#配置步骤)
- [功能说明](#功能说明)
- [API 使用](#api-使用)
- [测试指南](#测试指南)
- [常见问题](#常见问题)

---

## 概述

本项目已集成 PayPal 官方 SDK，支持以下功能：

- ✅ 创建支付订单
- ✅ 捕获支付
- ✅ Webhook 验证
- ✅ 支付退款
- ✅ 自动重试和错误处理
- ✅ 订单状态管理

**关键文件：**
- `server/api/services/paypal_client.py` - PayPal 客户端实现
- `server/api/routes/payment.py` - 支付路由
- `tests/test_paypal_client.py` - 测试用例

---

## 配置步骤

### 1. 获取 PayPal 凭证

1. 登录 [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/)
2. 导航到 **Apps & Credentials**
3. 创建新应用或使用默认应用
4. 复制 **Client ID** 和 **Client Secret**

### 2. 配置环境变量

在 `server/api/.env` 文件中添加以下配置：

```bash
# PayPal 配置
PAYPAL_CLIENT_ID=你的_Client_ID
PAYPAL_CLIENT_SECRET=你的_Client_Secret
PAYPAL_MODE=sandbox  # 开发用 sandbox，生产用 live
PAYPAL_WEBHOOK_ID=你的_Webhook_ID
FRONTEND_URL=http://localhost:3000
```

### 3. 创建 Webhook（可选但推荐）

1. 在 PayPal Developer Dashboard 中，导航到 **Webhooks**
2. 点击 **Create Webhook**
3. 输入 Webhook URL: `https://your-domain.com/api/payment/callback/paypal`
4. 选择以下事件：
   - `PAYMENT.CAPTURE.COMPLETED` - 支付成功
   - `PAYMENT.CAPTURE.DENIED` - 支付被拒绝
   - `PAYMENT.CAPTURE.PENDING` - 支付待处理
   - `PAYMENT.REFUND.COMPLETED` - 退款完成
5. 复制生成的 Webhook ID 到 `.env` 文件

### 4. 安装依赖

```bash
cd server/api
pip install -r requirements.txt
```

### 5. 测试配置

```bash
# 运行单元测试
pytest tests/test_paypal_client.py -v

# 运行集成测试（需要真实凭证）
pytest tests/test_paypal_client.py -m integration
```

---

## 功能说明

### PayPal 客户端类

```python
from server.api.services.paypal_client import PayPalClient, get_paypal_client

# 初始化客户端
client = PayPalClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    mode="sandbox",  # 或 "live"
    webhook_id="your_webhook_id"
)

# 或使用单例
client = get_paypal_client()
```

### 主要方法

#### 1. 创建订单

```python
result = await client.create_order(
    amount=10.00,
    currency="USD",
    order_number="ORDER_123",
    description="Product purchase",
    return_url="https://example.com/success",
    cancel_url="https://example.com/cancel"
)

# 返回:
{
    "paypal_order_id": "PAYPAL_ORDER_ID",
    "status": "CREATED",
    "approval_url": "https://www.sandbox.paypal.com/checkoutnow?token=...",
    "order_data": {...}
}
```

#### 2. 捕获支付

```python
result = await client.capture_payment("PAYPAL_ORDER_ID")

# 返回:
{
    "paypal_order_id": "PAYPAL_ORDER_ID",
    "status": "COMPLETED",
    "transaction_id": "CAPTURE_ID",
    "capture_data": {...}
}
```

#### 3. 获取订单详情

```python
details = await client.get_order_details("PAYPAL_ORDER_ID")
```

#### 4. 验证 Webhook

```python
is_valid, data = await client.verify_webhook(
    headers=request.headers,
    body=await request.body()
)
```

#### 5. 退款

```python
# 全额退款
await client.refund_payment("CAPTURE_ID")

# 部分退款
await client.refund_payment(
    capture_id="CAPTURE_ID",
    amount=5.00,
    currency="USD",
    note="Partial refund"
)
```

---

## API 使用

### 前端支付流程

#### 1. 创建订单

```javascript
// POST /api/payment/orders
const response = await fetch('/api/payment/orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    content_type: 'tutorial',
    content_id: 123,
    purchase_type: 'one_time'
  })
});

const { data } = await response.json();
// { order_number: 'ORD...', product_name: '...', final_price: 10.00 }
```

#### 2. 创建支付

```javascript
// POST /api/payment/pay
const paymentResponse = await fetch('/api/payment/pay', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    order_number: 'ORD20240201...',
    payment_method: 'paypal',
    payment_channel: 'paypal_web'  // 或 'paypal_app'
  })
});

const { data } = await paymentResponse.json();
// {
//   payment_method: 'paypal_web',
//   paypal_order_id: 'PAYPAL_ORDER_ID',
//   approval_url: 'https://www.sandbox.paypal.com/...'
// }
```

#### 3. 跳转到 PayPal

```javascript
// 网页支付：跳转到审批页面
window.location.href = data.approval_url;

// APP 支付：使用 PayPal SDK
// 参考: https://developer.paypal.com/sdk/js/reference/
```

#### 4. 捕获支付（用户批准后）

```javascript
// 用户批准后，PayPal 会重定向到 return_url
// 并附带 PayerID 和 token

// POST /api/payment/paypal/capture/{paypal_order_id}
const captureResponse = await fetch(`/api/payment/paypal/capture/${paypalOrderId}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    order_number: 'ORD20240201...'
  }
});

const result = await captureResponse.json();
// { success: true, transaction_id: '...' }
```

### Webhook 处理

PayPal 会自动发送 webhook 到配置的 URL，服务器会：

1. 验证 webhook 签名
2. 解析事件类型
3. 更新订单状态
4. 解锁内容
5. 发送通知

**无需额外操作**，webhook 会自动处理。

---

## 测试指南

### 单元测试

```bash
# 运行所有测试
pytest tests/test_paypal_client.py -v

# 运行特定测试类
pytest tests/test_paypal_client.py::TestCreateOrder -v

# 查看覆盖率
pytest tests/test_paypal_client.py --cov=server.api.services.paypal_client
```

### 集成测试

集成测试需要真实的 PayPal 沙盒凭证：

```bash
# 设置环境变量
export PAYPAL_SANDBOX_CLIENT_ID=your_sandbox_client_id
export PAYPAL_SANDBOX_CLIENT_SECRET=your_sandbox_client_secret

# 运行集成测试
pytest tests/test_paypal_client.py -m integration -v
```

### 手动测试

#### 1. 获取沙盒测试账号

1. 访问 [PayPal Developer Accounts](https://developer.paypal.com/developer/accounts/)
2. 创建或使用现有的沙盒账号
3. 使用沙盒买家账号进行测试支付

#### 2. 测试流程

1. 创建订单
2. 创建支付
3. 在沙盒 PayPal 页面完成支付
4. 验证订单状态更新
5. 检查内容解锁

---

## 常见问题

### 1. 如何从沙盒切换到生产环境？

修改 `.env` 文件：

```bash
# 从
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=sandbox_client_id
PAYPAL_CLIENT_SECRET=sandbox_client_secret

# 改为
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=live_client_id
PAYPAL_CLIENT_SECRET=live_client_secret
```

**注意：** 生产环境的凭证与沙盒环境不同。

### 2. Webhook 验证失败？

检查：
- Webhook ID 是否正确配置
- PayPal Developer Dashboard 中的 Webhook URL 是否正确
- 服务器是否可以访问 PayPal API

### 3. 订单创建失败？

常见原因：
- Client ID 或 Secret 不正确
- 账号余额不足
- 网络连接问题
- 请求参数格式错误

查看日志：`server/api/logs/`

### 4. 如何处理货币？

PayPal 支持多种货币，常用：

- USD - 美元
- EUR - 欧元
- GBP - 英镑
- JPY - 日元
- CNY - 人民币（有限支持）

确保订单货币与 PayPal 账号支持的货币一致。

### 5. 退款限制？

- PayPal 允许在 180 天内全额或部分退款
- 部分退款可以多次进行，直到全额退款
- 退款不可撤销

---

## 错误处理

PayPal 客户端使用自定义异常：

```python
try:
    result = await client.create_order(amount=10.00, currency="USD")
except PayPalAuthError as e:
    # 认证错误（凭证无效）
    print(f"认证失败: {e}")
except PayPalAPIError as e:
    # API 调用错误
    print(f"API 错误: {e.error_code} - {e.message}")
except PayPalWebhookError as e:
    # Webhook 验证错误
    print(f"Webhook 错误: {e}")
except PayPalError as e:
    # 其他 PayPal 错误
    print(f"PayPal 错误: {e}")
```

### 重试机制

客户端自动重试失败的请求（最多 3 次）：

- 初始延迟：2 秒
- 最大延迟：10 秒
- 指数退避策略

---

## 参考资源

- [PayPal REST API 文档](https://developer.paypal.com/api/rest/)
- [PayPal Checkout SDK](https://developer.paypal.com/sdk/checkout/)
- [PayPal Webhooks 文档](https://developer.paypal.com/docs/api/webhooks/)
- [PayPal 沙盒测试](https://developer.paypal.com/tools/sandbox/)

---

## 支持

如有问题，请：

1. 查看 [PayPal API 状态页](https://www.paypal-status.com/)
2. 检查项目日志文件
3. 运行测试诊断问题
4. 提交 Issue 到项目仓库
