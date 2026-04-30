"""
Configuration Example for PayPal Integration
PayPal 集成配置示例

复制此文件到 .env 并填入真实的凭证
"""

# ============================================
# PayPal Configuration
# ============================================

# PayPal Client ID (从 Developer Portal 获取)
# 获取地址: https://developer.paypal.com/dashboard/applications/live
PAYPAL_CLIENT_ID=your_paypal_client_id_here

# PayPal Client Secret (从 Developer Portal 获取)
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here

# PayPal Mode: sandbox (测试环境) 或 live (生产环境)
# 开发测试使用 sandbox，正式上线使用 live
PAYPAL_MODE=sandbox

# PayPal Webhook ID (可选，用于验证 webhook 签名)
# 创建 Webhook 后从 Developer Portal 获取
PAYPAL_WEBHOOK_ID=your_webhook_id_here

# Frontend URL (用于构建支付返回链接)
FRONTEND_URL=http://localhost:3000

# ============================================
# PayPal 沙盒测试账号
# ============================================

# 沙盒买家账号（用于测试）
# 创建地址: https://developer.paypal.com/dashboard/accounts
SANDBOX_BUYER_EMAIL=sb-buyer@example.com
SANDBOX_BUYER_PASSWORD=sandbox_password

# 沙盒商家账号（用于测试）
SANDBOX_MERCHANT_EMAIL=sb-merchant@example.com

# ============================================
# Webhook 配置说明
# ============================================

# 1. 登录 PayPal Developer Dashboard
# 2. 导航到 Apps & Credentials -> Webhooks
# 3. 创建 Webhook，URL 格式: https://your-domain.com/api/payment/callback/paypal
# 4. 选择需要监听的事件:
#    - PAYMENT.CAPTURE.COMPLETED (支付完成)
#    - PAYMENT.CAPTURE.DENIED (支付被拒绝)
#    - PAYMENT.CAPTURE.PENDING (支付待处理)
#    - PAYMENT.REFUND.COMPLETED (退款完成)
# 5. 复制 Webhook ID 到 PAYPAL_WEBHOOK_ID

# ============================================
# 测试环境设置
# ============================================

# PayPal 沙盒环境地址
# - 测试登录: https://www.sandbox.paypal.com/signin
# - 测试注册: https://www.sandbox.paypal.com/webapps/mpp/account-selection
# - 开发面板: https://developer.paypal.com/developer/accounts/

# ============================================
# 生产环境切换
# ============================================

# 从测试切换到生产时，需要:
# 1. 将 PAYPAL_MODE 改为 live
# 2. 更新 PAYPAL_CLIENT_ID 和 PAYPAL_CLIENT_SECRET 为生产环境凭证
# 3. 更新 PAYPAL_WEBHOOK_ID 为生产环境 Webhook ID
# 4. 更新 FRONTEND_URL 为生产环境 URL
