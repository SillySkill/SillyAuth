"""
PayPal Client
PayPal 支付客户端

提供 PayPal 支付的核心功能：
- 创建订单
- 捕获支付
- 退款
- 验证 Webhook
"""
import os
import json
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


# ============================================
# 异常类定义
# ============================================

class PayPalError(Exception):
    """PayPal 基础异常"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class PayPalAuthError(PayPalError):
    """PayPal 认证异常"""
    pass


class PayPalAPIError(PayPalError):
    """PayPal API 调用异常"""
    pass


class PayPalWebhookError(PayPalError):
    """PayPal Webhook 异常"""
    pass


# ============================================
# PayPal 客户端类
# ============================================

class PayPalClient:
    """
    PayPal API 客户端

    支持沙盒和生产环境
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        mode: str = None,
        webhook_id: str = None
    ):
        """
        初始化 PayPal 客户端

        Args:
            client_id: PayPal 客户端 ID
            client_secret: PayPal 客户端密钥
            mode: 环境模式 (sandbox/live)
            webhook_id: Webhook ID（用于验证 webhook）
        """
        # 从环境变量或参数获取配置
        self.client_id = client_id or os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("PAYPAL_CLIENT_SECRET")
        self.mode = mode or os.getenv("PAYPAL_MODE", "sandbox")
        self.webhook_id = webhook_id or os.getenv("PAYPAL_WEBHOOK_ID")

        # 验证配置
        if not self.client_id or not self.client_secret:
            raise PayPalAuthError("PayPal client_id 和 client_secret 必须提供")

        # 设置 API 基础 URL
        if self.mode == "live":
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"

        # 访问令牌（懒加载）
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

        logger.info(f"PayPal 客户端初始化成功 (mode={self.mode})")

    async def _get_access_token(self) -> str:
        """
        获取访问令牌（自动缓存）

        Returns:
            str: 访问令牌
        """
        # 检查缓存是否有效
        if self._access_token and self._token_expiry:
            if datetime.utcnow() < self._token_expiry:
                logger.debug("使用缓存的访问令牌")
                return self._access_token

        # 获取新令牌
        logger.info("获取新的 PayPal 访问令牌")

        try:
            # 构建 Basic Auth 头
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/oauth2/token",
                    headers={
                        "Authorization": f"Basic {encoded_credentials}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data="grant_type=client_credentials",
                    timeout=30.0
                )

                if response.status_code != 200:
                    error_data = response.json()
                    raise PayPalAuthError(
                        f"获取访问令牌失败: {error_data.get('error', 'Unknown error')}",
                        error_code=error_data.get('error'),
                        details=error_data
                    )

                data = response.json()
                self._access_token = data["access_token"]

                # 计算过期时间（提前5分钟刷新）
                expires_in = data.get("expires_in", 3600)
                self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)

                logger.info("访问令牌获取成功")
                return self._access_token

        except httpx.HTTPError as e:
            logger.error(f"HTTP 请求失败: {e}")
            raise PayPalAuthError(f"网络请求失败: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, PayPalAPIError))
    )
    async def _api_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None,
        headers: Dict = None
    ) -> Dict[str, Any]:
        """
        发送 API 请求（带重试）

        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求体数据
            params: 查询参数
            headers: 额外的请求头

        Returns:
            Dict: 响应数据
        """
        # 获取访问令牌
        access_token = await self._get_access_token()

        # 构建请求头
        request_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        if headers:
            request_headers.update(headers)

        # 构建完整 URL
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    timeout=30.0
                )

                # 处理错误响应
                if response.status_code >= 400:
                    error_data = response.json()
                    error_message = error_data.get("message", "Unknown error")
                    logger.error(f"API 请求失败: {response.status_code} - {error_message}")
                    raise PayPalAPIError(
                        f"API 请求失败: {error_message}",
                        error_code=str(response.status_code),
                        details=error_data
                    )

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HTTP 请求异常: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            raise PayPalAPIError(f"响应解析失败: {str(e)}")

    async def create_order(
        self,
        amount: float,
        currency: str = "USD",
        order_number: str = None,
        description: str = None,
        return_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        """
        创建 PayPal 订单

        Args:
            amount: 订单金额
            currency: 货币代码
            order_number: 订单号（用于自定义）
            description: 订单描述
            return_url: 支付成功后的返回 URL
            cancel_url: 取消支付后的返回 URL

        Returns:
            Dict: 订单信息，包含 approval_url
        """
        logger.info(f"创建 PayPal 订单: amount={amount} {currency}, order_number={order_number}")

        # 构建请求体
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": order_number or "",
                    "description": description or "Order payment",
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}"
                    },
                    "custom_id": order_number or ""
                }
            ]
        }

        # 添加支付跳转 URL
        if return_url or cancel_url:
            order_data["payment_source"] = {
                "paypal": {
                    "experience_context": {
                        "return_url": return_url or "https://example.com/success",
                        "cancel_url": cancel_url or "https://example.com/cancel"
                    }
                }
            }

        try:
            # 调用 API
            response = await self._api_request(
                method="POST",
                endpoint="/v2/checkout/orders",
                data=order_data
            )

            # 提取审批链接
            approval_url = None
            for link in response.get("links", []):
                if link.get("rel") == "approve":
                    approval_url = link["href"]
                    break

            logger.info(f"订单创建成功: PayPal Order ID = {response.get('id')}")

            return {
                "paypal_order_id": response.get("id"),
                "status": response.get("status"),
                "approval_url": approval_url,
                "order_data": response
            }

        except PayPalError as e:
            logger.error(f"创建订单失败: {e}")
            raise

    async def capture_order(
        self,
        paypal_order_id: str
    ) -> Dict[str, Any]:
        """
        捕获支付（完成支付）

        Args:
            paypal_order_id: PayPal 订单 ID

        Returns:
            Dict: 捕获结果
        """
        logger.info(f"捕获 PayPal 支付: order_id={paypal_order_id}")

        try:
            response = await self._api_request(
                method="POST",
                endpoint=f"/v2/checkout/orders/{paypal_order_id}/capture"
            )

            status = response.get("status")
            logger.info(f"支付捕获成功: status={status}")

            # 提取交易详情
            purchase_units = response.get("purchase_units", [])
            captures = purchase_units[0].get("payments", {}).get("captures", []) if purchase_units else []

            transaction_id = None
            if captures:
                transaction_id = captures[0].get("id")

            return {
                "paypal_order_id": response.get("id"),
                "status": status,
                "transaction_id": transaction_id,
                "capture_data": response
            }

        except PayPalError as e:
            logger.error(f"捕获支付失败: {e}")
            raise

    async def get_order_details(self, paypal_order_id: str) -> Dict[str, Any]:
        """
        获取订单详情

        Args:
            paypal_order_id: PayPal 订单 ID

        Returns:
            Dict: 订单详情
        """
        logger.info(f"获取订单详情: order_id={paypal_order_id}")

        try:
            response = await self._api_request(
                method="GET",
                endpoint=f"/v2/checkout/orders/{paypal_order_id}"
            )

            return response

        except PayPalError as e:
            logger.error(f"获取订单详情失败: {e}")
            raise

    async def verify_webhook(
        self,
        headers: Dict[str, str],
        body: str,
        webhook_id: str = None
    ) -> Tuple[bool, Dict]:
        """
        验证 Webhook 签名

        Args:
            headers: HTTP 请求头
            body: 请求体
            webhook_id: Webhook ID（可选，使用配置中的 ID）

        Returns:
            Tuple[bool, Dict]: (是否有效, 解析后的数据)
        """
        webhook_id = webhook_id or self.webhook_id

        if not webhook_id:
            logger.error("Webhook ID 未配置")
            return False, {}

        try:
            # 获取必要的验证头
            transmission_id = headers.get("PAYPAL-TRANSMISSION-ID")
            timestamp = headers.get("PAYPAL-TRANSMISSION-TIME")
            cert_id = headers.get("PAYPAL-CERT-ID")
            sig = headers.get("PAYPAL-TRANSMISSION-SIG")
            auth_algo = headers.get("PAYPAL-AUTH-ALGO")

            if not all([transmission_id, timestamp, cert_id, sig, auth_algo]):
                logger.error("Webhook 缺少必要的验证头")
                return False, {}

            logger.info(f"验证 Webhook: transmission_id={transmission_id}")

            # 构建验证请求
            verification_data = {
                "auth_algo": auth_algo,
                "cert_id": cert_id,
                "transmission_id": transmission_id,
                "transmission_sig": sig,
                "transmission_time": timestamp,
                "webhook_id": webhook_id,
                "webhook_event": json.loads(body)
            }

            # 调用 PayPal Webhook 验证 API
            access_token = await self._get_access_token()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/notifications/verify-webhook-signature",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=verification_data,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Webhook 验证失败: {response.status_code}")
                    return False, {}

                verification_result = response.json()
                is_valid = verification_result.get("verification_status") == "SUCCESS"

                if is_valid:
                    logger.info("Webhook 验证成功")
                    return True, json.loads(body)
                else:
                    logger.warning("Webhook 验证失败")
                    return False, {}

        except Exception as e:
            logger.error(f"Webhook 验证异常: {e}")
            return False, {}

    async def refund(
        self,
        capture_id: str,
        amount: float = None,
        currency: str = None,
        note: str = None
    ) -> Dict[str, Any]:
        """
        退款

        Args:
            capture_id: 捕获 ID
            amount: 退款金额（None 表示全额退款）
            currency: 货币代码
            note: 退款备注

        Returns:
            Dict: 退款结果
        """
        logger.info(f"处理退款: capture_id={capture_id}, amount={amount}")

        refund_data = {}
        if amount is not None:
            refund_data["amount"] = {
                "value": f"{amount:.2f}",
                "currency_code": currency or "USD"
            }
        if note:
            refund_data["note_to_payer"] = note

        try:
            response = await self._api_request(
                method="POST",
                endpoint=f"/v2/payments/captures/{capture_id}/refund",
                data=refund_data if refund_data else None
            )

            logger.info(f"退款成功: refund_id={response.get('id')}")
            return response

        except PayPalError as e:
            logger.error(f"退款失败: {e}")
            raise

    async def get_refund_details(self, refund_id: str) -> Dict[str, Any]:
        """
        获取退款详情

        Args:
            refund_id: 退款 ID

        Returns:
            Dict: 退款详情
        """
        logger.info(f"获取退款详情: refund_id={refund_id}")

        try:
            response = await self._api_request(
                method="GET",
                endpoint=f"/v2/payments/refunds/{refund_id}"
            )

            return response

        except PayPalError as e:
            logger.error(f"获取退款详情失败: {e}")
            raise

    async def disconnect_webhook(self, webhook_id: str) -> bool:
        """
        删除 Webhook

        Args:
            webhook_id: Webhook ID

        Returns:
            bool: 是否成功
        """
        logger.info(f"删除 Webhook: webhook_id={webhook_id}")

        try:
            await self._api_request(
                method="DELETE",
                endpoint=f"/v1/notifications/webhooks/{webhook_id}"
            )
            logger.info("Webhook 删除成功")
            return True

        except PayPalError as e:
            logger.error(f"删除 Webhook 失败: {e}")
            return False


# ============================================
# 单例实例（延迟初始化）
# ============================================

_paypal_client: Optional[PayPalClient] = None


def get_paypal_client() -> PayPalClient:
    """
    获取 PayPal 客户端单例

    Returns:
        PayPalClient: PayPal 客户端实例
    """
    global _paypal_client
    if _paypal_client is None:
        _paypal_client = PayPalClient()
    return _paypal_client


def init_paypal_client(
    client_id: str = None,
    client_secret: str = None,
    mode: str = None,
    webhook_id: str = None
) -> PayPalClient:
    """
    初始化 PayPal 客户端

    Args:
        client_id: PayPal 客户端 ID
        client_secret: PayPal 客户端密钥
        mode: 环境模式
        webhook_id: Webhook ID

    Returns:
        PayPalClient: PayPal 客户端实例
    """
    global _paypal_client
    _paypal_client = PayPalClient(
        client_id=client_id,
        client_secret=client_secret,
        mode=mode,
        webhook_id=webhook_id
    )
    return _paypal_client


# ============================================
# 导出
# ============================================

__all__ = [
    "PayPalClient",
    "PayPalError",
    "PayPalAuthError",
    "PayPalAPIError",
    "PayPalWebhookError",
    "get_paypal_client",
    "init_paypal_client"
]
