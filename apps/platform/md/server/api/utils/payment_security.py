"""
支付签名验证模块
Payment Signature Verification

实现微信支付、支付宝和PayPal的签名验证、回调解密等功能
"""
import hashlib
import hmac
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


# ============================================
# 配置
# ============================================

# 微信支付配置
WECHAT_CONFIG = {
    "api_key": "YOUR_WECHAT_API_KEY",
    "mch_id": "YOUR_MCH_ID",
    "key_path": "/path/to/cert/apiclient_key.pem",  # 商户API证书路径
    "serial_no": "YOUR_SERIAL_NO",
    "sign_type": "HMAC-SHA256"
}

# 支付宝配置
ALIPAY_CONFIG = {
    "app_id": "YOUR_ALIPAY_APP_ID",
    "private_key": "YOUR_ALIPAY_PRIVATE_KEY",
    "alipay_public_key": "YOUR_ALIPAY_PUBLIC_KEY",
    "sign_type": "RSA2"
}

# PayPal配置
PAYPAL_CONFIG = {
    "client_id": "YOUR_PAYPAL_CLIENT_ID",
    "client_secret": "YOUR_PAYPAL_CLIENT_SECRET",
    "mode": "sandbox",  # sandbox or live
    "webhook_id": "YOUR_PAYPAL_WEBHOOK_ID"
}


# ============================================
# 工具函数
# ============================================

def build_sign_str(params: Dict[str, Any]) -> str:
    """构建签名字符串"""
    # 过滤空值和 sign 字段
    filtered_params = {k: v for k, v in params.items() if v is not None and k != "sign"}
    # 按字典序排序
    sorted_params = sorted(filtered_params.items())
    # 拼接成 key=value&key=value 格式
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    return sign_str


def calculate_hmac_sha256(sign_str: str, key: str) -> str:
    """计算 HMAC-SHA256 签名"""
    return hmac.new(key.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest()


def calculate_md5(sign_str: str) -> str:
    """计算 MD5 签名"""
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest()


def calculate_rsa2_sign(sign_str: str, private_key: str) -> str:
    """计算 RSA2 签名"""
    import base64
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    try:
        # 加载私钥
        private_key = serialization.load_pem_private_key(
            private_key.encode(),
            password=None
        )

        # 签名
        signature = private_key.sign(
            sign_str.encode('utf-8'),
            padding.PKCS1v15,
            hashes.SHA256()
        )

        # Base64 编码
        sign_base64 = base64.b64encode(signature)
        return sign_base64.decode('utf-8')

    except Exception as e:
        logger.error(f"RSA2 签名失败: {e}")
        raise


def verify_rsa2_sign(sign_str: str, public_key: str, signature: str) -> bool:
    """验证 RSA2 签名"""
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    try:
        # 加载公钥
        pub_key = serialization.load_pem_public_key(
            public_key.encode(),
            password=None
        )

        # 解码签名
        signature_bytes = base64.b64decode(signature)

        # 验证签名
        pub_key.verify(
            sign_str.encode('utf-8'),
            signature_bytes,
            padding.PKCS1v15,
            hashes.SHA256()
        )

        return True

    except Exception as e:
        logger.error(f"RSA2 签名验证失败: {e}")
        return False


# ============================================
# 微信支付签名验证
# ============================================

class WeChatPaySignature:
    """微信支付签名验证"""

    @staticmethod
    def verify_callback(data: Dict[str, Any]) -> bool:
        """
        验证微信支付回调签名

        Args:
            data: 回调数据

        Returns:
            bool: 签名是否有效
        """
        try:
            # 获取签名
            sign = data.get("sign")
            if not sign:
                logger.error("微信回调缺少签名")
                return False

            # 构建待签名串
            sign_str = build_sign_str(data)

            # 计算签名
            calculated_sign = calculate_hmac_sha256(sign_str, WECHAT_CONFIG["api_key"])

            # 验证签名（忽略大小写）
            return sign.upper() == calculated_sign.upper()

        except Exception as e:
            logger.error(f"微信签名验证失败: {e}")
            return False

    @staticmethod
    def build_wechat_sign_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建微信支付签名参数
        """
        sign_str = build_sign_str(params)
        sign = calculate_hmac_sha256(sign_str, WECHAT_CONFIG["api_key"])

        return {
            **params,
            "sign": sign
        }

    @staticmethod
    def decode_wechat_callback(notify_data: str) -> Dict[str, Any]:
        """
        解密微信支付回调数据

        Args:
            notify_data: 微信回调数据（XML格式）

        Returns:
            解密后的数据
        """
        try:
            # 解析 XML
            root = ET.fromstring(notify_data)

            # 获取加密数据
            req_info = root.find("req_info")
            if req_info is None:
                logger.error("微信回调缺少 req_info")
                return {}

            # 获取密文
            cipher_text = req_info.find("cipher_text")
            if cipher_text is None:
                logger.error("微信回调缺少 cipher_text")
                return {}

            cipher_text = cipher_text.text

            # Base64 解码
            import base64
            cipher_text_bytes = base64.b64decode(cipher_text)

            # 解密
            from cryptography.hazmat.primitives.ciphers import Cipher
            from cryptography.hazmat.primitives.serialization import load_pem
            from cryptography.hazmat.backends.default import default_backend

            # 加载商户私钥
            with open(WECHAT_CONFIG["key_path"], "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )

            # 提取密钥和向量
            key = private_key.private_key().raw_secret()
            iv = cipher_text_bytes[:16]
            ciphertext = cipher_text_bytes[16:]

            # 解密
            cipher = Cipher(
                key,
                modes.CBC(IV(iv)),
                default_backend()
            )

            decrypted = cipher.decrypt(ciphertext)

            # 去除填充
            padding = decrypted[-1]
            if isinstance(padding, bytes):
                decrypted = decrypted[:-padding]

            # 解析 JSON
            decrypted_str = decrypted.decode('utf-8')
            import json
            return json.loads(decrypted_str)

        except Exception as e:
            logger.error(f"微信回调解密失败: {e}")
            return {}


# ============================================
# 支付宝签名验证
# ============================================

class AlipaySignature:
    """支付宝签名验证"""

    @staticmethod
    def verify_callback(params: Dict[str, Any]) -> bool:
        """
        验证支付宝回调签名

        Args:
            params: 回调参数

        Returns:
            bool: 签名是否有效
        """
        try:
            # 获取签名
            sign = params.get("sign")
            if not sign:
                logger.error("支付宝回调缺少签名")
                return False

            # 获取公钥
            public_key = ALIPAY_CONFIG["alipay_public_key"]

            # 构建待签名串
            sign_str = build_sign_str(params)

            # 验证签名
            return verify_rsa2_sign(sign_str, public_key, sign)

        except Exception as e:
            logger.error(f"支付宝签名验证失败: {e}")
            return False

    @staticmethod
    def build_alipay_sign_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建支付宝签名参数
        """
        sign_str = build_sign_str(params)
        sign = calculate_rsa2_sign(sign_str, ALIPAY_CONFIG["private_key"])

        return {
            **params,
            "sign": sign
        }


# ============================================
# PayPal 签名验证
# ============================================

class PayPalSignature:
    """PayPal 签名验证"""

    @staticmethod
    def verify_webhook(
        headers: Dict[str, str],
        body: str,
        webhook_id: str = None
    ) -> bool:
        """
        验证 PayPal Webhook 签名

        使用 PayPal Webhook Verification API 验证 webhook 签名
        文档: https://developer.paypal.com/docs/api/webhooks/v1/#verify-webhook-signature_post

        Args:
            headers: HTTP 请求头
            body: 请求体
            webhook_id: Webhook ID（可选，从配置获取）

        Returns:
            bool: 签名是否有效
        """
        try:
            import httpx
            import json
            from typing import Dict, Any

            # 获取必要的头信息
            paypal_transmission_id = headers.get("paypal-transmission-id", "")
            paypal_cert_id = headers.get("paypal-cert-id", "")
            paypal_transmission_sig = headers.get("paypal-transmission-sig", "")
            paypal_transmission_time = headers.get("paypal-transmission-time", "")
            paypal_auth_version = headers.get("paypal-auth-version", "")

            if not all([paypal_transmission_id, paypal_cert_id, paypal_transmission_sig,
                       paypal_transmission_time, paypal_auth_version]):
                logger.error("PayPal webhook 缺少必要的头信息")
                return False

            # 使用配置的 webhook_id
            webhook_id = webhook_id or PAYPAL_CONFIG.get("webhook_id")
            if not webhook_id:
                logger.error("PayPal webhook_id 未配置")
                return False

            # 构建验证请求
            verify_url = PAYPAL_CONFIG.get("base_url", "https://api-m.sandbox.paypal.com")
            if PAYPAL_CONFIG.get("mode") == "live":
                verify_url = "https://api-m.paypal.com"

            verify_url = f"{verify_url}/v1/notifications/verify-webhook-signature"

            # 准备验证payload
            verification_payload = {
                "transmission_id": paypal_transmission_id,
                "cert_id": paypal_cert_id,
                "transmission_sig": paypal_transmission_sig,
                "transmission_time": paypal_transmission_time,
                "auth_version": paypal_auth_version,
                "webhook_id": webhook_id,
                "webhook_event": json.loads(body) if isinstance(body, str) else body
            }

            # 获取 PayPal 访问令牌
            client_id = PAYPAL_CONFIG.get("client_id")
            client_secret = PAYPAL_CONFIG.get("client_secret")

            if not client_id or not client_secret:
                logger.error("PayPal client_id 或 client_secret 未配置")
                return False

            # 获取访问令牌
            token_url = PAYPAL_CONFIG.get("base_url", "https://api-m.sandbox.paypal.com")
            if PAYPAL_CONFIG.get("mode") == "live":
                token_url = "https://api-m.paypal.com"
            token_url = f"{token_url}/v1/oauth2/token"

            async def verify_with_paypal():
                async with httpx.AsyncClient() as client:
                    # 获取访问令牌
                    auth_response = await client.post(
                        token_url,
                        auth=(client_id, client_secret),
                        data={"grant_type": "client_credentials"},
                        headers={"Accept": "application/json"}
                    )

                    if auth_response.status_code != 200:
                        logger.error(f"PayPal 令牌获取失败: {auth_response.status_code}")
                        return False

                    access_token = auth_response.json().get("access_token")

                    # 验证webhook签名
                    verify_response = await client.post(
                        verify_url,
                        json=verification_payload,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {access_token}"
                        }
                    )

                    if verify_response.status_code != 200:
                        logger.error(f"PayPal webhook 验证失败: {verify_response.status_code}")
                        return False

                    result = verify_response.json()
                    verification_status = result.get("verification_status")

                    logger.info(f"PayPal webhook 验证结果: {verification_status} (ID: {paypal_transmission_id})")

                    return verification_status == "SUCCESS"

            # 执行验证
            import asyncio
            try:
                return asyncio.run(verify_with_paypal())
            except RuntimeError:
                # 如果没有运行的事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(verify_with_paypal())
                finally:
                    loop.close()

        except Exception as e:
            logger.error(f"PayPal webhook 验证异常: {e}", exc_info=True)
            return False

    @staticmethod
    def verify_ipn(notification: Dict[str, str]) -> bool:
        """
        验证 PayPal IPN (Instant Payment Notification)

        通过回传数据给 PayPal 进行验证

        Args:
            notification: IPN 通知数据

        Returns:
            bool: 是否有效
        """
        try:
            import httpx
            from urllib.parse import urlencode

            # 构建验证请求
            verify_url = "https://ipnpb.paypal.com/cgi-bin/webscr"
            if PAYPAL_CONFIG.get("mode") == "sandbox":
                verify_url = "https://ipnpb.sandbox.paypal.com/cgi-bin/webscr"

            # 添加验证命令
            verification_data = {"cmd": "_notify-validate"}
            verification_data.update(notification)

            # 发送验证请求
            async def verify_with_paypal():
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        verify_url,
                        data=verification_data,
                        headers={"User-Agent": "IPN-Verification-Script"}
                    )

                    response_text = response.text.strip()
                    logger.info(f"PayPal IPN 验证响应: {response_text}")

                    # PayPal 返回 "VERIFIED" 表示验证成功
                    return response_text == "VERIFIED"

            import asyncio
            try:
                result = asyncio.run(verify_with_paypal())
                if result:
                    logger.info(f"PayPal IPN 验证成功: {notification.get('txn_id')}")
                else:
                    logger.warning(f"PayPal IPN 验证失败: {notification.get('txn_id')}")
                return result
            except RuntimeError:
                # 如果没有运行的事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(verify_with_paypal())
                finally:
                    loop.close()

        except Exception as e:
            logger.error(f"PayPal IPN 验证异常: {e}", exc_info=True)
            return False


# ============================================
# 公开函数
# ============================================

def verify_payment_callback(
    payment_method: str,
    data: Dict[str, Any],
    headers: Dict[str, str] = None
) -> bool:
    """
    验证支付回调签名

    Args:
        payment_method: 支付方式 (wechat, alipay, paypal)
        data: 回调数据
        headers: HTTP 头（PayPal webhook 需要）

    Returns:
        bool: 签名是否有效
    """
    if payment_method == "wechat":
        return WeChatPaySignature.verify_callback(data)
    elif payment_method == "alipay":
        return AlipaySignature.verify_callback(data)
    elif payment_method == "paypal":
        if headers:
            return PayPalSignature.verify_webhook(headers, str(data))
        else:
            return PayPalSignature.verify_ipn(data)
    else:
        logger.error(f"不支持的支付方式: {payment_method}")
        return False


def validate_payment_amount(
    order_amount: float,
    callback_amount: float,
    tolerance: float = 0.01
) -> bool:
    """
    验证支付金额是否匹配

    Args:
        order_amount: 订单金额
        callback_amount: 回调金额
        tolerance: 允许的误差范围

    Returns:
        bool: 金额是否匹配
    """
    diff = abs(order_amount - callback_amount)
    return diff <= tolerance


def check_order_idempotency(
    order_number: str,
    user_id: int,
    db: AsyncSession
) -> bool:
    """
    检查订单幂等性

    防止重复创建订单

    Args:
        order_number: 订单号
        user_id: 用户ID
        db: 数据库会话

    Returns:
        bool: True 表示订单已存在（重复），False 表示可以创建
    """
    from ..models.orders import Order

    existing = await db.execute(
        select(Order).where(
            and_(
                Order.order_number == order_number,
                Order.user_id == user_id
            )
        ).order_by(Order.created_at.desc()).first()

    return existing is not None


def verify_content_ownership(
    user_id: int,
    content_type: str,
    content_id: int,
    db: AsyncSession
) -> bool:
    """
    验证用户是否拥有内容的创作者权限

    Args:
        user_id: 当前用户ID
        content_type: 内容类型
        content_id: 内容ID
        db: 数据库会话

    Returns:
        bool: 是否拥有权限
    """
    # 获取内容
    if content_type == "tutorial":
        from ..models.tutorials import Tutorial
        content = await db.get(Tutorial, content_id)
    elif content_type == "download":
        from ..models.downloads import Download
        content = await db.get(Download, content_id)
    else:
        return False

    if not content:
        return False

    # 如果内容没有创作者或者是官方内容，任何人都不能直接管理
    if not content.creator_id:
        return False

    # 只有创作者本人可以管理自己的内容
    return content.creator_id == user_id


# ============================================
# 导出
# ============================================

__all__ = [
    "WeChatPaySignature",
    "AlipaySignature",
    "PayPalSignature",
    "verify_payment_callback",
    "validate_payment_amount",
    "check_order_idempotency",
    "verify_content_ownership"
]
