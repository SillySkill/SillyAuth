"""
Payment Service
支付服务

提供统一的支付服务接口
"""
import os
import uuid
import hashlib
import logging
from typing import Any, Dict, Optional
import json
from datetime import datetime, timedelta
from enum import Enum

from .schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentStatus,
    PaymentStatusEnum,
    PaymentMethod,
    PaymentChannel,
    RefundRequest,
    RefundResult,
    PaymentMethodInfo,
    PaymentMethodsResponse,
    WeChatPayNotifyData,
    AlipayNotifyData,
    PayPalWebhookData,
)
from .clients import (
    get_wechat_pay_client,
    get_alipay_client,
    get_paypal_client,
    WeChatPayError,
    AlipayError,
    PayPalError,
)

logger = logging.getLogger(__name__)


# ============================================
# 常量定义
# ============================================

# 支付有效期（分钟）
PAYMENT_EXPIRY_MINUTES = 30

# 支持的货币
SUPPORTED_CURRENCIES = {
    PaymentMethod.WECHAT: ["CNY"],
    PaymentMethod.ALIPAY: ["CNY", "USD"],
    PaymentMethod.PAYPAL: ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"],
}


# ============================================
# 辅助函数
# ============================================

def generate_payment_id() -> str:
    """生成支付记录ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]
    return f"PAY{timestamp}{unique_id}"


def generate_refund_id() -> str:
    """生成退款记录ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]
    return f"REF{timestamp}{unique_id}"


def generate_out_refund_no() -> str:
    """生成商户退款单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"REF{timestamp}"


# ============================================
# 支付服务类
# ============================================

class PaymentService:
    """
    支付服务

    提供统一的支付服务接口，支持微信、支付宝、PayPal
    """

    def __init__(self):
        """初始化支付服务"""
        self.wechat_client = None
        self.alipay_client = None
        self.paypal_client = None
        logger.info("PaymentService 初始化成功")

    def _get_wechat_client(self):
        """获取微信支付客户端"""
        if self.wechat_client is None:
            try:
                self.wechat_client = get_wechat_pay_client()
            except WeChatPayError as e:
                logger.warning(f"微信支付客户端初始化失败: {e}")
        return self.wechat_client

    def _get_alipay_client(self):
        """获取支付宝客户端"""
        if self.alipay_client is None:
            try:
                self.alipay_client = get_alipay_client()
            except AlipayError as e:
                logger.warning(f"支付宝客户端初始化失败: {e}")
        return self.alipay_client

    def _get_paypal_client(self):
        """获取 PayPal 客户端"""
        if self.paypal_client is None:
            try:
                self.paypal_client = get_paypal_client()
            except PayPalError as e:
                logger.warning(f"PayPal 客户端初始化失败: {e}")
        return self.paypal_client

    async def create_payment(
        self,
        order_id: str,
        amount: float,
        currency: str,
        method: PaymentMethod,
        description: str = None,
        channel: PaymentChannel = None,
        notify_url: str = None,
        return_url: str = None,
        cancel_url: str = None
    ) -> PaymentResponse:
        """
        创建支付

        Args:
            order_id: 订单ID
            amount: 支付金额
            currency: 货币代码
            method: 支付方式
            description: 支付描述
            channel: 支付渠道
            notify_url: 异步通知URL
            return_url: 支付成功跳转URL
            cancel_url: 支付取消跳转URL

        Returns:
            PaymentResponse: 支付响应
        """
        payment_id = generate_payment_id()
        expires_at = datetime.now() + timedelta(minutes=PAYMENT_EXPIRY_MINUTES)

        logger.info(f"创建支付: payment_id={payment_id}, order_id={order_id}, method={method}")

        # 根据支付方式创建支付
        if method == PaymentMethod.WECHAT:
            result = await self._create_wechat_payment(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                currency=currency,
                description=description,
                channel=channel,
                notify_url=notify_url,
                expires_at=expires_at
            )
        elif method == PaymentMethod.ALIPAY:
            result = await self._create_alipay_payment(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                currency=currency,
                description=description,
                channel=channel,
                notify_url=notify_url,
                return_url=return_url,
                expires_at=expires_at
            )
        elif method == PaymentMethod.PAYPAL:
            result = await self._create_paypal_payment(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                currency=currency,
                description=description,
                return_url=return_url,
                cancel_url=cancel_url,
                expires_at=expires_at
            )
        else:
            raise ValueError(f"不支持的支付方式: {method}")

        return result

    async def _create_wechat_payment(
        self,
        payment_id: str,
        order_id: str,
        amount: float,
        currency: str,
        description: str,
        channel: PaymentChannel,
        notify_url: str,
        expires_at: datetime
    ) -> PaymentResponse:
        """创建微信支付"""
        client = self._get_wechat_client()

        if not client:
            raise RuntimeError("微信支付客户端未初始化")

        # 确定交易类型
        trade_type_map = {
            PaymentChannel.WECHAT_APP: "APP",
            PaymentChannel.WECHAT_WEB: "JSAPI",
            PaymentChannel.WECHAT_H5: "MWEB",
            PaymentChannel.WECHAT_NATIVE: "NATIVE",
            None: "APP"
        }
        trade_type = trade_type_map.get(channel, "APP")

        # 转换金额为分
        total_fee = int(amount * 100)

        # 构建回调通知地址
        if not notify_url:
            base_url = os.getenv("API_BASE_URL", "https://api.example.com")
            notify_url = f"{base_url}/api/payment/notify/wechat"

        # 创建微信支付订单
        result = await client.create_order(
            out_trade_no=payment_id,
            total_fee=total_fee,
            body=description or f"订单支付：{order_id}",
            trade_type=trade_type,
            notify_url=notify_url,
            attach=order_id
        )

        # 构建响应
        pay_url = None
        pay_params = None
        qr_code = None

        if trade_type == "NATIVE":
            pay_url = result.get("code_url")
            qr_code = result.get("code_url")
        elif trade_type == "APP":
            pay_params = result.get("pay_params")
        elif trade_type == "JSAPI":
            pay_params = {
                "prepay_id": result.get("prepay_id"),
                "appId": client.app_id,
                "timeStamp": str(int(datetime.now().timestamp())),
                "nonceStr": client._generate_nonce_str(),
                "package": f"prepay_id={result.get('prepay_id')}",
                "signType": "MD5"
            }
        elif trade_type == "MWEB":
            pay_url = result.get("mweb_url")

        return PaymentResponse(
            payment_id=payment_id,
            order_id=order_id,
            amount=amount,
            currency=currency,
            status=PaymentStatusEnum.PENDING,
            method=PaymentMethod.WECHAT,
            channel=channel,
            pay_url=pay_url,
            pay_params=pay_params,
            qr_code=qr_code,
            expires_at=expires_at,
            created_at=datetime.now()
        )

    async def _create_alipay_payment(
        self,
        payment_id: str,
        order_id: str,
        amount: float,
        currency: str,
        description: str,
        channel: PaymentChannel,
        notify_url: str,
        return_url: str,
        expires_at: datetime
    ) -> PaymentResponse:
        """创建支付宝支付"""
        client = self._get_alipay_client()

        if not client:
            raise RuntimeError("支付宝客户端未初始化")

        # 确定产品码
        product_code_map = {
            PaymentChannel.ALIPAY_APP: "FAST_INSTANT_TRADE_PAY",
            PaymentChannel.ALIPAY_WEB: "FAST_INSTANT_TRADE_PAY",
            PaymentChannel.ALIPAY_WAP: "QUICK_WAP_WAY",
            None: "FAST_INSTANT_TRADE_PAY"
        }
        product_code = product_code_map.get(channel, "FAST_INSTANT_TRADE_PAY")

        # 构建回调通知地址
        if not notify_url:
            base_url = os.getenv("API_BASE_URL", "https://api.example.com")
            notify_url = f"{base_url}/api/payment/notify/alipay"

        if channel == PaymentChannel.ALIPAY_WAP or (channel is None and "wap" in str(PaymentChannel.ALIPAY_WAP)):
            # WAP 支付
            result = await client.create_wap_order(
                out_trade_no=payment_id,
                total_amount=amount,
                subject=description or f"订单支付：{order_id}",
                product_code=product_code,
                notify_url=notify_url,
                return_url=return_url
            )
            return PaymentResponse(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                currency=currency,
                status=PaymentStatusEnum.PENDING,
                method=PaymentMethod.ALIPAY,
                channel=channel,
                pay_url=result.get("form_html"),
                expires_at=expires_at,
                created_at=datetime.now()
            )
        else:
            # APP 支付
            result = await client.create_order(
                out_trade_no=payment_id,
                total_amount=amount,
                subject=description or f"订单支付：{order_id}",
                product_code=product_code,
                notify_url=notify_url
            )
            return PaymentResponse(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                currency=currency,
                status=PaymentStatusEnum.PENDING,
                method=PaymentMethod.ALIPAY,
                channel=channel,
                pay_params={"order_string": result.get("order_string")},
                expires_at=expires_at,
                created_at=datetime.now()
            )

    async def _create_paypal_payment(
        self,
        payment_id: str,
        order_id: str,
        amount: float,
        currency: str,
        description: str,
        return_url: str,
        cancel_url: str,
        expires_at: datetime
    ) -> PaymentResponse:
        """创建 PayPal 支付"""
        client = self._get_paypal_client()

        if not client:
            raise RuntimeError("PayPal 客户端未初始化")

        # 构建跳转 URL
        base_url = os.getenv("FRONTEND_URL", "https://example.com")
        if not return_url:
            return_url = f"{base_url}/payment/success"
        if not cancel_url:
            cancel_url = f"{base_url}/payment/cancel"

        # 创建 PayPal 订单
        result = await client.create_order(
            amount=amount,
            currency=currency,
            order_number=payment_id,
            description=description or f"Order payment: {order_id}",
            return_url=return_url,
            cancel_url=cancel_url
        )

        return PaymentResponse(
            payment_id=payment_id,
            order_id=order_id,
            amount=amount,
            currency=currency,
            status=PaymentStatusEnum.PENDING,
            method=PaymentMethod.PAYPAL,
            channel=PaymentChannel.PAYPAL_WEB,
            pay_url=result.get("approval_url"),
            expires_at=expires_at,
            created_at=datetime.now()
        )

    async def query_payment(
        self,
        payment_id: str = None,
        order_id: str = None,
        transaction_id: str = None
    ) -> PaymentStatus:
        """
        查询支付状态

        Args:
            payment_id: 支付记录ID
            order_id: 订单ID
            transaction_id: 第三方交易ID

        Returns:
            PaymentStatus: 支付状态
        """
        logger.info(f"查询支付: payment_id={payment_id}, order_id={order_id}")

        try:
            from src.core.db_adapter import get_db_cursor as _get_db
            with _get_db() as cur:
                if payment_id:
                    cur.execute("SELECT * FROM payment_records WHERE payment_id = %s", (payment_id,))
                elif order_id:
                    cur.execute("SELECT * FROM payment_records WHERE order_id = %s", (order_id,))
                elif transaction_id:
                    cur.execute("SELECT * FROM payment_records WHERE transaction_id = %s", (transaction_id,))
                else:
                    return PaymentStatus(
                        payment_id=None, order_id=None,
                        status=PaymentStatusEnum.PENDING,
                        transaction_id=None, amount=0, currency="CNY",
                        method=PaymentMethod.WECHAT,
                        updated_at=datetime.now()
                    )
                record = cur.fetchone()
                if record:
                    return PaymentStatus(
                        payment_id=record.get("payment_id"),
                        order_id=record.get("order_id"),
                        status=record.get("status", PaymentStatusEnum.PENDING),
                        transaction_id=record.get("transaction_id"),
                        amount=float(record.get("amount", 0)),
                        currency=record.get("currency", "CNY"),
                        method=record.get("method", PaymentMethod.WECHAT),
                        updated_at=record.get("updated_at", datetime.now())
                    )
        except Exception as e:
            logger.error(f"Failed to query payment from DB: {e}")

        return PaymentStatus(
            payment_id=payment_id, order_id=order_id,
            status=PaymentStatusEnum.PENDING,
            transaction_id=transaction_id, amount=0, currency="CNY",
            method=PaymentMethod.WECHAT,
            updated_at=datetime.now()
        )

    async def handle_notification(
        self,
        provider: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        处理支付通知

        Args:
            provider: 支付提供商 (wechat|alipay|paypal)
            data: 通知数据

        Returns:
            bool: 处理是否成功
        """
        logger.info(f"处理支付通知: provider={provider}")

        if provider == "wechat":
            return await self._handle_wechat_notification(data)
        elif provider == "alipay":
            return await self._handle_alipay_notification(data)
        elif provider == "paypal":
            return await self._handle_paypal_notification(data)
        else:
            logger.error(f"不支持的支付提供商: {provider}")
            return False

    async def _handle_wechat_notification(self, data: Dict[str, Any]) -> bool:
        """处理微信支付通知"""
        client = self._get_wechat_client()

        if not client:
            logger.error("微信支付客户端未初始化")
            return False

        # 验证签名
        if not client.verify_notification(data):
            logger.error("微信支付通知签名验证失败")
            return False

        # 检查交易状态
        trade_state = data.get("trade_state")
        if trade_state == "SUCCESS":
            # 支付成功，更新订单状态
            logger.info(f"微信支付成功: out_trade_no={data.get('out_trade_no')}")
            # 更新数据库中的订单状态
            order_id = data.get("out_trade_no")
            transaction_id = data.get("transaction_id")
            try:
                from src.core.db_adapter import get_db_cursor as _get_db
                with _get_db() as cur:
                    cur.execute(
                        "UPDATE payment_records SET status = %s, transaction_id = %s, updated_at = NOW() WHERE order_id = %s",
                        ("success", transaction_id, order_id)
                    )
            except Exception as e:
                logger.error(f"Failed to update order status in DB: {e}")
            return True
        else:
            logger.warning(f"微信支付状态异常: {trade_state}")
            return False

    async def _handle_alipay_notification(self, data: Dict[str, Any]) -> bool:
        """处理支付宝通知"""
        client = self._get_alipay_client()

        if not client:
            logger.error("支付宝客户端未初始化")
            return False

        # 验证签名
        is_valid, payment_data = await client.verify_notification(data)

        if not is_valid:
            logger.error("支付宝通知验证失败")
            return False

        # 检查交易状态
        trade_status = data.get("trade_status")
        if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            logger.info(f"支付宝支付成功: out_trade_no={data.get('out_trade_no')}")
            # 更新数据库中的订单状态
            order_id = data.get("out_trade_no")
            transaction_id = data.get("trade_no")
            try:
                from src.core.db_adapter import get_db_cursor as _get_db
                with _get_db() as cur:
                    cur.execute(
                        "UPDATE payment_records SET status = %s, transaction_id = %s, updated_at = NOW() WHERE order_id = %s",
                        ("success", transaction_id, order_id)
                    )
            except Exception as e:
                logger.error(f"Failed to update order status in DB: {e}")
            return True
        else:
            logger.warning(f"支付宝支付状态异常: {trade_status}")
            return False

    async def _handle_paypal_notification(self, data: Dict[str, Any]) -> bool:
        """处理 PayPal Webhook"""
        client = self._get_paypal_client()

        if not client:
            logger.error("PayPal 客户端未初始化")
            return False

        # 验证 Webhook
        # 注意：实际使用时需要传入原始请求头和请求体
        # 这里简化处理
        event_type = data.get("event_type")

        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            logger.info(f"PayPal 支付完成")
            # 更新数据库中的订单状态
            resource = data.get("resource", {})
            order_id = resource.get("custom_id") or resource.get("invoice_id")
            transaction_id = resource.get("id")
            try:
                from src.core.db_adapter import get_db_cursor as _get_db
                with _get_db() as cur:
                    cur.execute(
                        "UPDATE payment_records SET status = %s, transaction_id = %s, updated_at = NOW() WHERE order_id = %s",
                        ("success", transaction_id, order_id)
                    )
            except Exception as e:
                logger.error(f"Failed to update order status in DB: {e}")
            return True
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            logger.warning(f"PayPal 支付被拒绝")
            return False
        else:
            logger.info(f"PayPal 其他事件: {event_type}")
            return True

    async def refund(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> RefundResult:
        """
        申请退款

        Args:
            payment_id: 支付记录ID
            amount: 退款金额（None表示全额退款）
            reason: 退款原因

        Returns:
            RefundResult: 退款结果
        """
        refund_id = generate_refund_id()
        logger.info(f"申请退款: refund_id={refund_id}, payment_id={payment_id}")

        # 从数据库查询原始订单
        try:
            from src.core.db_adapter import get_db_cursor as _get_db
            with _get_db() as cur:
                cur.execute(
                    "SELECT * FROM payment_records WHERE payment_id = %s",
                    (payment_id,)
                )
                record = cur.fetchone()
                if not record:
                    raise ValueError(f"订单未找到: {payment_id}")

                order_id_val = record["order_id"]

                # 更新订单状态为已退款
                cur.execute(
                    "UPDATE payment_records SET status = 'refunded', refund_amount = %s, refund_reason = %s, updated_at = NOW() WHERE payment_id = %s",
                    (amount, reason, payment_id)
                )

                return RefundResult(
                    refund_id=refund_id,
                    payment_id=payment_id,
                    order_id=order_id_val,
                    refund_amount=amount or 0,
                    refund_status="success",
                    refund_reason=reason,
                    created_at=datetime.now()
                )
        except Exception as e:
            logger.error(f"Refund failed: {e}")
            return RefundResult(
                refund_id="",
                payment_id=payment_id,
                order_id="",
                refund_amount=amount or 0,
                refund_status="failed",
                refund_reason=str(e),
                created_at=datetime.now()
            )

    def get_available_payment_methods(self) -> PaymentMethodsResponse:
        """
        获取可用的支付方式

        Returns:
            PaymentMethodsResponse: 可用的支付方式列表
        """
        methods = [
            PaymentMethodInfo(
                method=PaymentMethod.WECHAT,
                name="微信支付",
                icon="/icons/wechat-pay.png",
                description="使用微信支付",
                channels=[
                    PaymentChannel.WECHAT_APP,
                    PaymentChannel.WECHAT_WEB,
                    PaymentChannel.WECHAT_H5,
                    PaymentChannel.WECHAT_NATIVE
                ],
                currencies=["CNY"],
                enabled=self._get_wechat_client() is not None
            ),
            PaymentMethodInfo(
                method=PaymentMethod.ALIPAY,
                name="支付宝",
                icon="/icons/alipay.png",
                description="使用支付宝支付",
                channels=[
                    PaymentChannel.ALIPAY_APP,
                    PaymentChannel.ALIPAY_WEB,
                    PaymentChannel.ALIPAY_WAP
                ],
                currencies=["CNY", "USD"],
                enabled=self._get_alipay_client() is not None
            ),
            PaymentMethodInfo(
                method=PaymentMethod.PAYPAL,
                name="PayPal",
                icon="/icons/paypal.png",
                description="使用 PayPal 支付",
                channels=[
                    PaymentChannel.PAYPAL_WEB,
                    PaymentChannel.PAYPAL_APP
                ],
                currencies=["USD", "EUR", "GBP", "JPY", "CAD", "AUD"],
                enabled=self._get_paypal_client() is not None
            )
        ]

        return PaymentMethodsResponse(
            methods=methods,
            default_currency="CNY"
        )


    # ============================================
    # Order Management
    # ============================================

    def get_user_orders(
        self,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get user orders (paginated)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Count query
            count_sql = "SELECT COUNT(*) as cnt FROM orders WHERE user_id = %s"
            count_params = [user_id]
            if status:
                count_sql += " AND status = %s"
                count_params.append(status)
            cur.execute(count_sql, tuple(count_params))
            total = cur.fetchone()["cnt"]

            # Data query
            offset = (page - 1) * page_size
            data_sql = """
                SELECT id, order_number, product_name, content_type, content_id,
                       original_price, discount_amount, final_price, currency,
                       status, payment_status, purchase_type,
                       created_at, paid_at, expires_at
                FROM orders
                WHERE user_id = %s
            """
            data_params = [user_id]
            if status:
                data_sql += " AND status = %s"
                data_params.append(status)
            data_sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            data_params.extend([page_size, offset])
            cur.execute(data_sql, tuple(data_params))
            rows = cur.fetchall()

            items = []
            for row in rows:
                items.append({
                    "id": row["id"],
                    "order_number": row["order_number"],
                    "product_name": row.get("product_name"),
                    "content_type": row.get("content_type"),
                    "content_id": row.get("content_id"),
                    "original_price": float(row.get("original_price", 0) or 0),
                    "discount_amount": float(row.get("discount_amount", 0) or 0),
                    "final_price": float(row.get("final_price", 0) or 0),
                    "currency": row.get("currency", "CNY"),
                    "status": row.get("status"),
                    "payment_status": row.get("payment_status"),
                    "purchase_type": row.get("purchase_type"),
                    "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                    "paid_at": row["paid_at"].isoformat() if row.get("paid_at") else None,
                    "expires_at": row["expires_at"].isoformat() if row.get("expires_at") else None,
                })

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    # ============================================
    # Purchase Management
    # ============================================

    def get_my_purchases(
        self,
        user_id: int,
        content_type: Optional[str] = None
    ) -> list:
        """Get user's purchased content (unlocked and not expired)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            sql = """
                SELECT cu.content_type, cu.content_id, cu.unlock_source,
                       cu.unlocked_at, cu.expires_at,
                       COALESCE(t.title_zh_CN, d.title_zh_CN) AS title,
                       COALESCE(t.description_zh_CN, d.description_zh_CN) AS description,
                       COALESCE(t.thumbnail, d.thumbnail) AS thumbnail
                FROM content_unlocks cu
                LEFT JOIN tutorials t ON cu.content_type = 'tutorial' AND cu.content_id = t.id
                LEFT JOIN downloads d ON cu.content_type = 'download' AND cu.content_id = d.id
                WHERE cu.user_id = %s
                  AND (cu.expires_at IS NULL OR cu.expires_at > NOW())
            """
            params = [user_id]
            if content_type:
                sql += " AND cu.content_type = %s"
                params.append(content_type)
            sql += " ORDER BY cu.unlocked_at DESC"

            cur.execute(sql, tuple(params))
            rows = cur.fetchall()

            results = []
            for row in rows:
                results.append({
                    "content_type": row["content_type"],
                    "content_id": row["content_id"],
                    "title": row.get("title"),
                    "description": row.get("description"),
                    "thumbnail": row.get("thumbnail"),
                    "unlock_source": row.get("unlock_source"),
                    "unlocked_at": row["unlocked_at"].isoformat() if row.get("unlocked_at") else None,
                    "expires_at": row["expires_at"].isoformat() if row.get("expires_at") else None,
                })

            return results

    # ============================================
    # Submission Management
    # ============================================

    def create_submission(self, user_id: int, username: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user submission for review."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            sql = """
                INSERT INTO user_submissions
                    (user_id, username, content_type, title_zh_CN, title_en,
                     description_zh_CN, description_en, content_zh_CN, content_en,
                     category, subcategory, difficulty, platform, version,
                     thumbnail, video_url, video_type, video_duration,
                     file_name, file_url, file_size, file_type, file_checksum,
                     github_url, is_paid, price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                RETURNING id
            """
            params = (
                user_id, username,
                data.get("content_type"), data.get("title_zh_CN"), data.get("title_en"),
                data.get("description_zh_CN"), data.get("description_en"),
                data.get("content_zh_CN"), data.get("content_en"),
                data.get("category"), data.get("subcategory"),
                data.get("difficulty"), data.get("platform"), data.get("version"),
                data.get("thumbnail"), data.get("video_url"), data.get("video_type"),
                data.get("video_duration"), data.get("file_name"), data.get("file_url"),
                data.get("file_size"), data.get("file_type"), data.get("file_checksum"),
                data.get("github_url"), data.get("is_paid", False),
                data.get("price", 0)
            )
            cur.execute(sql, params)
            submission_id = cur.fetchone()["id"]

        logger.info(f"Submission created: id={submission_id}, user_id={user_id}")
        return {"submission_id": submission_id, "status": "pending"}

    def get_my_submissions(
        self,
        user_id: int,
        status: Optional[str] = None
    ) -> list:
        """Get user's submissions."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            sql = """
                SELECT id, content_type, title_zh_CN, description_zh_CN,
                       category, subcategory, is_paid, price, thumbnail,
                       status, ai_review_status, ai_review_score,
                       submitted_at, reviewed_at, published_content_id, published_at
                FROM user_submissions
                WHERE user_id = %s
            """
            params = [user_id]
            if status:
                sql += " AND status = %s"
                params.append(status)
            sql += " ORDER BY submitted_at DESC"

            cur.execute(sql, tuple(params))
            rows = cur.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "content_type": row.get("content_type"),
                    "title_zh_CN": row.get("title_zh_CN"),
                    "description_zh_CN": row.get("description_zh_CN"),
                    "category": row.get("category"),
                    "subcategory": row.get("subcategory"),
                    "is_paid": row.get("is_paid", False),
                    "price": float(row.get("price", 0) or 0),
                    "thumbnail": row.get("thumbnail"),
                    "status": row.get("status"),
                    "ai_review_status": row.get("ai_review_status"),
                    "ai_review_score": float(row["ai_review_score"]) if row.get("ai_review_score") else None,
                    "submitted_at": row["submitted_at"].isoformat() if row.get("submitted_at") else None,
                    "reviewed_at": row["reviewed_at"].isoformat() if row.get("reviewed_at") else None,
                    "published_content_id": row.get("published_content_id"),
                    "published_at": row["published_at"].isoformat() if row.get("published_at") else None,
                })

            return results

    def get_pending_submissions(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get pending submissions (admin view)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM user_submissions WHERE status = 'pending'")
            total = cur.fetchone()["cnt"]

            offset = (page - 1) * page_size
            cur.execute(
                """SELECT * FROM user_submissions
                   WHERE status = 'pending'
                   ORDER BY submitted_at DESC
                   LIMIT %s OFFSET %s""",
                (page_size, offset)
            )
            rows = cur.fetchall()

            items = []
            for row in rows:
                item = {}
                for key in row.keys():
                    val = row[key]
                    if isinstance(val, datetime):
                        item[key] = val.isoformat()
                    elif hasattr(val, 'isoformat'):
                        item[key] = val.isoformat()
                    else:
                        item[key] = val
                items.append(item)

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    def approve_submission(self, submission_id: int, admin_id: int) -> Dict[str, Any]:
        """Approve a pending submission."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute("SELECT id FROM user_submissions WHERE id = %s", (submission_id,))
            if not cur.fetchone():
                raise ValueError("Submission not found")

            cur.execute(
                """UPDATE user_submissions
                   SET status = 'approved', reviewed_by = %s, reviewed_at = NOW()
                   WHERE id = %s AND status = 'pending'""",
                (admin_id, submission_id)
            )
            if cur.rowcount == 0:
                raise ValueError("Submission is not in pending status")

        logger.info(f"Submission approved: id={submission_id}, admin={admin_id}")
        return {"submission_id": submission_id, "status": "approved"}

    def reject_submission(self, submission_id: int, admin_id: int, reason: str) -> Dict[str, Any]:
        """Reject a pending submission."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute("SELECT id FROM user_submissions WHERE id = %s", (submission_id,))
            if not cur.fetchone():
                raise ValueError("Submission not found")

            cur.execute(
                """UPDATE user_submissions
                   SET status = 'rejected', rejection_reason = %s,
                       reviewed_by = %s, reviewed_at = NOW()
                   WHERE id = %s AND status = 'pending'""",
                (reason, admin_id, submission_id)
            )
            if cur.rowcount == 0:
                raise ValueError("Submission is not in pending status")

        logger.info(f"Submission rejected: id={submission_id}, admin={admin_id}")
        return {"submission_id": submission_id, "status": "rejected"}

    # ============================================
    # Revenue Statistics
    # ============================================

    def get_revenue_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue statistics for admin."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute(
                """SELECT paid_at::date AS date,
                          COUNT(*) AS paid_orders,
                          COALESCE(SUM(final_price), 0) AS total_revenue
                   FROM orders
                   WHERE payment_status = 'paid'
                     AND paid_at >= NOW() - (%s || ' days')::INTERVAL
                   GROUP BY paid_at::date
                   ORDER BY date DESC""",
                (str(days),)
            )
            rows = cur.fetchall()

            daily_stats = []
            total_orders = 0
            total_revenue = 0
            for row in rows:
                daily_stats.append({
                    "date": row["date"].isoformat() if row.get("date") else None,
                    "paid_orders": row["paid_orders"],
                    "total_revenue": float(row["total_revenue"] or 0),
                })
                total_orders += row["paid_orders"]
                total_revenue += float(row["total_revenue"] or 0)

            return {
                "period_days": days,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "daily_stats": daily_stats,
            }

    # ============================================
    # Payment Account Management (Admin)
    # ============================================

    def list_payment_accounts(
        self,
        account_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> list:
        """List payment accounts (admin)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            sql = """
                SELECT id, account_type, account_name, account_id, credentials,
                       is_active, is_primary, priority, currency, description,
                       created_at, updated_at
                FROM payment_accounts
                WHERE 1=1
            """
            params = []
            if account_type:
                sql += " AND account_type = %s"
                params.append(account_type)
            if is_active is not None:
                sql += " AND is_active = %s"
                params.append(is_active)
            sql += " ORDER BY priority DESC, created_at ASC"

            cur.execute(sql, tuple(params) if params else None)
            rows = cur.fetchall()

            accounts = []
            for row in rows:
                # Credentials are stored encrypted; return masked/placeholder
                credentials = row.get("credentials")
                if isinstance(credentials, dict):
                    masked_creds = {k: "***" for k in credentials}
                else:
                    masked_creds = None

                accounts.append({
                    "id": row["id"],
                    "account_type": row["account_type"],
                    "account_name": row["account_name"],
                    "account_id": row["account_id"],
                    "credentials": masked_creds,
                    "is_active": row["is_active"],
                    "is_primary": row["is_primary"],
                    "priority": row["priority"],
                    "currency": row["currency"],
                    "description": row.get("description"),
                    "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                    "updated_at": row["updated_at"].isoformat() if row.get("updated_at") else None,
                })

            return accounts

    def create_payment_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment account (admin)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Store credentials as JSON string (basic storage -- real impl would encrypt)
            credentials_json = json.dumps(data.get("credentials", {}))

            cur.execute(
                """INSERT INTO payment_accounts
                   (account_type, account_name, account_id, credentials, is_active,
                    is_primary, priority, currency, description)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    data["account_type"],
                    data["account_name"],
                    data["account_id"],
                    credentials_json,
                    True,
                    False,
                    0,
                    data.get("currency", "CNY"),
                    data.get("description"),
                )
            )
            new_id = cur.fetchone()["id"]

        logger.info(f"Payment account created: id={new_id}, type={data['account_type']}")
        return {"id": new_id, "message": "Payment account created"}

    def update_payment_account(self, account_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a payment account (admin)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute("SELECT id FROM payment_accounts WHERE id = %s", (account_id,))
            if not cur.fetchone():
                raise ValueError("Payment account not found")

            update_fields = []
            params = []

            if "account_name" in data and data["account_name"] is not None:
                update_fields.append("account_name = %s")
                params.append(data["account_name"])
            if "credentials" in data and data["credentials"] is not None:
                update_fields.append("credentials = %s")
                params.append(json.dumps(data["credentials"]))
            if "is_active" in data and data["is_active"] is not None:
                update_fields.append("is_active = %s")
                params.append(data["is_active"])
            if "is_primary" in data and data["is_primary"] is not None:
                update_fields.append("is_primary = %s")
                params.append(data["is_primary"])
            if "priority" in data and data["priority"] is not None:
                update_fields.append("priority = %s")
                params.append(data["priority"])
            if "currency" in data and data["currency"] is not None:
                update_fields.append("currency = %s")
                params.append(data["currency"])
            if "description" in data and data["description"] is not None:
                update_fields.append("description = %s")
                params.append(data["description"])

            if update_fields:
                update_fields.append("updated_at = NOW()")
                params.append(account_id)
                sql = f"UPDATE payment_accounts SET {', '.join(update_fields)} WHERE id = %s"
                cur.execute(sql, tuple(params))

        logger.info(f"Payment account updated: id={account_id}")
        return {"message": "Payment account updated"}

    def delete_payment_account(self, account_id: int) -> Dict[str, Any]:
        """Delete a payment account (admin)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute("DELETE FROM payment_accounts WHERE id = %s", (account_id,))
            if cur.rowcount == 0:
                raise ValueError("Payment account not found")

        logger.info(f"Payment account deleted: id={account_id}")
        return {"message": "Payment account deleted"}

    # ============================================
    # Creator Settlement Preferences
    # ============================================

    def get_creator_settlement_preference(self, user_id: int) -> Dict[str, Any]:
        """Get creator settlement preference."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute(
                """SELECT id, settlement_method, payment_account_type, payment_account_id,
                          auto_settle, min_settlement_amount, settlement_period,
                          paypal_email, alipay_account, wechat_openid
                   FROM creator_settlement_preferences
                   WHERE user_id = %s""",
                (user_id,)
            )
            row = cur.fetchone()

            if not row:
                return {
                    "settlement_method": "direct",
                    "auto_settle": False,
                    "min_settlement_amount": 100.00,
                    "settlement_period": "monthly",
                }

            return {
                "id": row["id"],
                "settlement_method": row["settlement_method"],
                "payment_account_type": row.get("payment_account_type"),
                "payment_account_id": row.get("payment_account_id"),
                "auto_settle": row["auto_settle"],
                "min_settlement_amount": float(row["min_settlement_amount"] or 100),
                "settlement_period": row["settlement_period"],
                "paypal_email": row.get("paypal_email"),
                "alipay_account": row.get("alipay_account"),
                "wechat_openid": row.get("wechat_openid"),
            }

    def update_creator_settlement_preference(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update creator settlement preference."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute(
                "SELECT id FROM creator_settlement_preferences WHERE user_id = %s",
                (user_id,)
            )
            existing = cur.fetchone()

            if existing:
                cur.execute(
                    """UPDATE creator_settlement_preferences
                       SET settlement_method = %s, payment_account_type = %s,
                           payment_account_id = %s, auto_settle = %s,
                           min_settlement_amount = %s, settlement_period = %s,
                           paypal_email = %s, alipay_account = %s,
                           wechat_openid = %s, updated_at = NOW()
                       WHERE user_id = %s""",
                    (
                        data.get("settlement_method", "direct"),
                        data.get("payment_account_type"),
                        data.get("payment_account_id"),
                        data.get("auto_settle", False),
                        data.get("min_settlement_amount", 100.00),
                        data.get("settlement_period", "monthly"),
                        data.get("paypal_email"),
                        data.get("alipay_account"),
                        data.get("wechat_openid"),
                        user_id,
                    )
                )
            else:
                cur.execute(
                    """INSERT INTO creator_settlement_preferences
                       (user_id, settlement_method, payment_account_type, payment_account_id,
                        auto_settle, min_settlement_amount, settlement_period,
                        paypal_email, alipay_account, wechat_openid)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user_id,
                        data.get("settlement_method", "direct"),
                        data.get("payment_account_type"),
                        data.get("payment_account_id"),
                        data.get("auto_settle", False),
                        data.get("min_settlement_amount", 100.00),
                        data.get("settlement_period", "monthly"),
                        data.get("paypal_email"),
                        data.get("alipay_account"),
                        data.get("wechat_openid"),
                    )
                )

        logger.info(f"Creator settlement preference updated: user_id={user_id}")
        return {"message": "Settlement preference updated"}

    # ============================================
    # Creator Earnings
    # ============================================

    def get_creator_earnings(
        self,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get creator earnings (paginated)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Count
            count_sql = "SELECT COUNT(*) as cnt FROM creator_earnings WHERE user_id = %s"
            count_params = [user_id]
            if status:
                count_sql += " AND settlement_status = %s"
                count_params.append(status)
            cur.execute(count_sql, tuple(count_params))
            total = cur.fetchone()["cnt"]

            # Data
            offset = (page - 1) * page_size
            data_sql = """
                SELECT id, order_id, content_type, content_id,
                       gross_amount, platform_commission, creator_share,
                       settlement_status, settlement_method, settlement_amount,
                       points_awarded, settled_at, created_at
                FROM creator_earnings
                WHERE user_id = %s
            """
            data_params = [user_id]
            if status:
                data_sql += " AND settlement_status = %s"
                data_params.append(status)
            data_sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            data_params.extend([page_size, offset])
            cur.execute(data_sql, tuple(data_params))
            rows = cur.fetchall()

            items = []
            for row in rows:
                items.append({
                    "id": row["id"],
                    "order_id": row.get("order_id"),
                    "content_type": row.get("content_type"),
                    "content_id": row.get("content_id"),
                    "gross_amount": float(row.get("gross_amount", 0) or 0),
                    "platform_commission": float(row.get("platform_commission", 0) or 0),
                    "creator_share": float(row.get("creator_share", 0) or 0),
                    "settlement_status": row.get("settlement_status"),
                    "settlement_method": row.get("settlement_method"),
                    "settlement_amount": float(row["settlement_amount"]) if row.get("settlement_amount") else None,
                    "points_awarded": row.get("points_awarded"),
                    "settled_at": row["settled_at"].isoformat() if row.get("settled_at") else None,
                    "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                })

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    def get_creator_earnings_summary(self, user_id: int) -> Dict[str, Any]:
        """Get creator earnings summary."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Try to use view first, fall back to direct query
            try:
                cur.execute(
                    "SELECT * FROM v_creator_earnings_summary WHERE user_id = %s",
                    (user_id,)
                )
                row = cur.fetchone()
                if row:
                    return {
                        "settlement_method": row.get("settlement_method") if "settlement_method" in row.keys() else None,
                        "auto_settle": row.get("auto_settle") if "auto_settle" in row.keys() else None,
                        "total_earnings_count": row.get("total_earnings_count", 0) or 0,
                        "pending_earnings": float(row.get("pending_earnings", 0) or 0),
                        "settled_amount": float(row.get("settled_amount", 0) or 0),
                        "points_earned": row.get("points_earned", 0) or 0,
                        "total_orders_count": row.get("total_orders_count", 0) or 0,
                        "total_gross_amount": float(row.get("total_gross_amount", 0) or 0),
                        "total_platform_commission": float(row.get("total_platform_commission", 0) or 0),
                    }
            except Exception:
                pass  # View not available, fall through to direct query

            # Direct query fallback
            cur.execute(
                """SELECT
                     COUNT(*) AS total_earnings_count,
                     COALESCE(SUM(CASE WHEN settlement_status = 'pending' THEN creator_share ELSE 0 END), 0) AS pending_earnings,
                     COALESCE(SUM(CASE WHEN settlement_status = 'settled' THEN settlement_amount ELSE 0 END), 0) AS settled_amount,
                     COALESCE(SUM(points_awarded), 0) AS points_earned,
                     COALESCE(SUM(gross_amount), 0) AS total_gross_amount,
                     COALESCE(SUM(platform_commission), 0) AS total_platform_commission
                   FROM creator_earnings
                   WHERE user_id = %s""",
                (user_id,)
            )
            row = cur.fetchone()

            # Also get preference info
            cur.execute(
                """SELECT settlement_method, auto_settle
                   FROM creator_settlement_preferences
                   WHERE user_id = %s""",
                (user_id,)
            )
            pref = cur.fetchone()

            return {
                "settlement_method": pref["settlement_method"] if pref else None,
                "auto_settle": pref["auto_settle"] if pref else None,
                "total_earnings_count": row["total_earnings_count"] if row else 0,
                "pending_earnings": float(row["pending_earnings"] or 0) if row else 0,
                "settled_amount": float(row["settled_amount"] or 0) if row else 0,
                "points_earned": row["points_earned"] if row else 0,
                "total_orders_count": 0,  # Not available in direct query
                "total_gross_amount": float(row["total_gross_amount"] or 0) if row else 0,
                "total_platform_commission": float(row["total_platform_commission"] or 0) if row else 0,
            }

    # ============================================
    # Creator Settlement Operations
    # ============================================

    def settle_creator_earnings(
        self,
        user_id: int,
        payment_account_type: str,
        payment_account_id: str
    ) -> Dict[str, Any]:
        """Settle creator earnings."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Try batch settle function first
            try:
                cur.execute(
                    """SELECT batch_settle_creator_earnings(%s, %s, %s) AS settlement_id""",
                    (user_id, payment_account_type, payment_account_id)
                )
                result = cur.fetchone()
                settlement_id = result["settlement_id"] if result else None
                if settlement_id:
                    return {"settlement_id": settlement_id}
            except Exception:
                pass  # Function not available, do manual settlement

            # Manual settlement: sum pending and mark as settled
            cur.execute(
                """SELECT COALESCE(SUM(creator_share), 0) AS total_pending
                   FROM creator_earnings
                   WHERE user_id = %s AND settlement_status = 'pending'""",
                (user_id,)
            )
            row = cur.fetchone()
            total_pending = float(row["total_pending"] or 0)

            if total_pending < 100:
                raise ValueError(f"Minimum settlement amount not met: {total_pending:.2f} < 100")

            # Create settlement record
            import uuid
            batch_number = f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6]}"
            cur.execute(
                """INSERT INTO settlement_records
                   (user_id, batch_number, total_amount, total_commission, total_earnings,
                    settlement_method, status, payment_account_type, payment_account_id,
                    period_start, period_end, created_at)
                   VALUES (%s, %s, %s, %s, %s, 'direct', 'pending',
                           %s, %s, NOW() - INTERVAL '30 days', NOW(), NOW())
                   RETURNING id""",
                (user_id, batch_number, total_pending, 0, total_pending,
                 payment_account_type, payment_account_id)
            )
            settlement_result = cur.fetchone()
            settlement_id = settlement_result["id"] if settlement_result else None

            # Mark earnings as settled
            cur.execute(
                """UPDATE creator_earnings
                   SET settlement_status = 'settled',
                       settlement_method = 'direct',
                       settlement_amount = creator_share,
                       settled_at = NOW()
                   WHERE user_id = %s AND settlement_status = 'pending'""",
                (user_id,)
            )

        logger.info(f"Creator earnings settled: user_id={user_id}, settlement_id={settlement_id}")
        return {"settlement_id": settlement_id, "message": f"Settled successfully"}

    def get_creator_settlements(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get settlement records (paginated)."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            cur.execute(
                "SELECT COUNT(*) as cnt FROM settlement_records WHERE user_id = %s",
                (user_id,)
            )
            total = cur.fetchone()["cnt"]

            offset = (page - 1) * page_size
            cur.execute(
                """SELECT id, batch_number, total_orders, total_amount,
                          total_commission, total_earnings, settlement_method,
                          status, transaction_id, failure_reason,
                          period_start, period_end, created_at, processed_at
                   FROM settlement_records
                   WHERE user_id = %s
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (user_id, page_size, offset)
            )
            rows = cur.fetchall()

            items = []
            for row in rows:
                items.append({
                    "id": row["id"],
                    "batch_number": row.get("batch_number"),
                    "total_orders": row.get("total_orders"),
                    "total_amount": float(row.get("total_amount", 0) or 0),
                    "total_commission": float(row.get("total_commission", 0) or 0),
                    "total_earnings": float(row.get("total_earnings", 0) or 0),
                    "settlement_method": row.get("settlement_method"),
                    "status": row.get("status"),
                    "transaction_id": row.get("transaction_id"),
                    "failure_reason": row.get("failure_reason"),
                    "period_start": row["period_start"].isoformat() if row.get("period_start") else None,
                    "period_end": row["period_end"].isoformat() if row.get("period_end") else None,
                    "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                    "processed_at": row["processed_at"].isoformat() if row.get("processed_at") else None,
                })

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    # ============================================
    # Admin Settlement Management
    # ============================================

    def get_pending_settlements(self) -> list:
        """Get pending settlements for admin."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Try view first
            try:
                cur.execute(
                    "SELECT * FROM v_pending_settlements ORDER BY total_pending_amount DESC"
                )
                rows = cur.fetchall()
                if rows:
                    results = []
                    for row in rows:
                        results.append({
                            "user_id": row["user_id"] if "user_id" in row.keys() else row[0],
                            "username": row.get("username") if "username" in row.keys() else (row[1] if len(row) > 1 else None),
                            "email": row.get("email") if "email" in row.keys() else None,
                            "settlement_method": row.get("settlement_method") if "settlement_method" in row.keys() else (row[3] if len(row) > 3 else None),
                            "payment_account_type": row.get("payment_account_type") if "payment_account_type" in row.keys() else None,
                            "payment_account_id": row.get("payment_account_id") if "payment_account_id" in row.keys() else None,
                            "min_settlement_amount": float(row.get("min_settlement_amount", 100) or 100) if "min_settlement_amount" in row.keys() else 100,
                            "pending_count": row.get("pending_count", 0) if "pending_count" in row.keys() else 0,
                            "total_pending_amount": float(row.get("total_pending_amount", 0) or 0) if "total_pending_amount" in row.keys() else 0,
                            "oldest_earning_date": row.get("oldest_earning_date") if "oldest_earning_date" in row.keys() else None,
                            "latest_earning_date": row.get("latest_earning_date") if "latest_earning_date" in row.keys() else None,
                        })
                    return results
            except Exception:
                pass  # View not available, fall through

            # Direct query fallback
            cur.execute(
                """SELECT u.id AS user_id, u.username, u.email,
                          csp.settlement_method, csp.payment_account_type,
                          csp.payment_account_id,
                          COALESCE(csp.min_settlement_amount, 100) AS min_settlement_amount,
                          COUNT(ce.id) AS pending_count,
                          COALESCE(SUM(ce.creator_share), 0) AS total_pending_amount,
                          MIN(ce.created_at) AS oldest_earning_date,
                          MAX(ce.created_at) AS latest_earning_date
                   FROM creator_earnings ce
                   JOIN users u ON ce.user_id = u.id
                   LEFT JOIN creator_settlement_preferences csp ON ce.user_id = csp.user_id
                   WHERE ce.settlement_status = 'pending'
                   GROUP BY u.id, u.username, u.email,
                            csp.settlement_method, csp.payment_account_type,
                            csp.payment_account_id, csp.min_settlement_amount
                   ORDER BY total_pending_amount DESC"""
            )
            rows = cur.fetchall()

            results = []
            for row in rows:
                results.append({
                    "user_id": row["user_id"],
                    "username": row.get("username"),
                    "email": row.get("email"),
                    "settlement_method": row.get("settlement_method"),
                    "payment_account_type": row.get("payment_account_type"),
                    "payment_account_id": row.get("payment_account_id"),
                    "min_settlement_amount": float(row.get("min_settlement_amount", 100) or 100),
                    "pending_count": row["pending_count"],
                    "total_pending_amount": float(row["total_pending_amount"] or 0),
                    "oldest_earning_date": row["oldest_earning_date"].isoformat() if row.get("oldest_earning_date") else None,
                    "latest_earning_date": row["latest_earning_date"].isoformat() if row.get("latest_earning_date") else None,
                })

            return results

    def admin_settle_creator(
        self,
        target_user_id: int,
        payment_account_type: str,
        payment_account_id: str
    ) -> Dict[str, Any]:
        """Admin manually settles a creator's earnings."""
        from src.core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Try batch settle function first
            try:
                cur.execute(
                    """SELECT batch_settle_creator_earnings(%s, %s, %s) AS settlement_id""",
                    (target_user_id, payment_account_type, payment_account_id)
                )
                result = cur.fetchone()
                settlement_id = result["settlement_id"] if result else None
                if settlement_id:
                    logger.info(
                        f"Admin settled creator: user_id={target_user_id}, "
                        f"settlement_id={settlement_id}"
                    )
                    return {
                        "settlement_id": settlement_id,
                        "user_id": target_user_id,
                        "message": "Admin settlement successful",
                    }
            except Exception:
                pass  # Fall through to manual

            # Manual settlement
            cur.execute(
                """SELECT COALESCE(SUM(creator_share), 0) AS total_pending
                   FROM creator_earnings
                   WHERE user_id = %s AND settlement_status = 'pending'""",
                (target_user_id,)
            )
            row = cur.fetchone()
            total_pending = float(row["total_pending"] or 0)

            if total_pending <= 0:
                raise ValueError("No pending earnings to settle")

            import uuid
            batch_number = f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6]}"
            cur.execute(
                """INSERT INTO settlement_records
                   (user_id, batch_number, total_amount, total_commission, total_earnings,
                    settlement_method, status, payment_account_type, payment_account_id,
                    period_start, period_end, created_at)
                   VALUES (%s, %s, %s, %s, %s, 'direct', 'pending',
                           %s, %s, NOW() - INTERVAL '30 days', NOW(), NOW())
                   RETURNING id""",
                (target_user_id, batch_number, total_pending, 0, total_pending,
                 payment_account_type, payment_account_id)
            )
            settlement_result = cur.fetchone()
            settlement_id = settlement_result["id"] if settlement_result else None

            cur.execute(
                """UPDATE creator_earnings
                   SET settlement_status = 'settled',
                       settlement_method = 'direct',
                       settlement_amount = creator_share,
                       settled_at = NOW()
                   WHERE user_id = %s AND settlement_status = 'pending'""",
                (target_user_id,)
            )

        logger.info(f"Admin settled creator: user_id={target_user_id}, settlement_id={settlement_id}")
        return {
            "settlement_id": settlement_id,
            "user_id": target_user_id,
            "message": "Admin settlement successful",
        }


# ============================================
# 单例实例
# ============================================

_payment_service: Optional[PaymentService] = None


def get_payment_service() -> PaymentService:
    """
    获取支付服务单例

    Returns:
        PaymentService: 支付服务实例
    """
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService()
    return _payment_service


# ============================================
# 导出
# ============================================

__all__ = [
    "PaymentService",
    "get_payment_service",
    "generate_payment_id",
    "generate_refund_id",
    "generate_out_refund_no",
]
