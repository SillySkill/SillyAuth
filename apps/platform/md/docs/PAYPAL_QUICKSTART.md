# PayPal 集成快速开始

## 🚀 5 分钟快速配置

### 步骤 1: 获取 PayPal 凭证

1. 访问 https://developer.paypal.com/dashboard/
2. 登录并创建应用
3. 复制 **Client ID** 和 **Client Secret**

### 步骤 2: 配置环境变量

在 `server/api/.env` 文件中添加：

```bash
PAYPAL_CLIENT_ID=你的Client_ID
PAYPAL_CLIENT_SECRET=你的Client_Secret
PAYPAL_MODE=sandbox
```

### 步骤 3: 测试配置

```bash
# 运行快速测试
python tests/test_paypal_quickstart.py
```

### 步骤 4: 开始使用 ✅

```python
from server.api.services.paypal_client import get_paypal_client

# 获取客户端
client = get_paypal_client()

# 创建订单
order = await client.create_order(
    amount=10.00,
    currency="USD",
    order_number="ORDER_123"
)

# 捕获支付
result = await client.capture_payment(order["paypal_order_id"])
```

---

## 📚 完整文档

- [完整集成指南](docs/PAYPAL_INTEGRATION.md)
- [功能总结](docs/PAYPAL_INTEGRATION_SUMMARY.md)
- [验证报告](docs/PAYPAL_INTEGRATION_VERIFICATION.md)

---

## ✨ 主要功能

- ✅ 创建支付订单
- ✅ 捕获支付
- ✅ Webhook 验证
- ✅ 支付退款
- ✅ 自动重试
- ✅ 完善的错误处理

---

## 🧪 测试

```bash
# 单元测试
pytest tests/test_paypal_client.py -v

# 集成测试（需要凭证）
pytest tests/test_paypal_client.py -m integration
```

---

## 🔑 关键文件

| 文件 | 说明 |
|------|------|
| `server/api/services/paypal_client.py` | PayPal 客户端 |
| `server/api/routes/payment.py` | 支付路由 |
| `tests/test_paypal_client.py` | 测试用例 |
| `tests/test_paypal_quickstart.py` | 快速测试 |

---

## 💡 提示

- 沙盒环境不需要真实资金
- 测试账号：https://developer.paypal.com/developer/accounts/
- 生产环境只需更改 `PAYPAL_MODE=live`

---

**🎉 集成完成！**
