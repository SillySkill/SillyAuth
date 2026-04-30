"""
Alipay Client
支付宝支付客户端

提供支付宝支付的核心功能：
- 创建支付订单
- 验证回调签名
- 申请退款
"""
import os
import base64
import hashlib
import json
import rsa
import time
import random
import string
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)


# ============================================
# 异常类定义
# ============================================

class AlipayError(Exception):
    """支付宝基础异常"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AlipaySignError(AlipayError):
    """支付宝签名异常"""
    pass


class AlipayAPIError(AlipayError):
    """支付宝 API 调用异常"""
    pass


# ============================================
# 支付宝客户端类
# ============================================

class AlipayClient:
    """
    支付宝 API 客户端

    支持当面付、手机网站支付、电脑网站支付
    """

    def __init__(
        self,
        app_id: str = None,
        private_key: str = None,
        alipay_public_key: str = None,
        mode: str = "sandbox"
    ):
        """
        初始化支付宝客户端

        Args:
            app_id: 支付宝应用ID
            private_key: 应用私钥
            alipay_public_key: 支付宝公钥
            mode: 环境模式 (sandbox/live)
        """
        self.app_id = app_id or os.getenv("ALIPAY_APP_ID")
        self.private_key = private_key or os.getenv("ALIPAY_PRIVATE_KEY")
        self.alipay_public_key = alipay_public_key or os.getenv("ALIPAY_PUBLIC_KEY")
        self.mode = mode

        if not all([self.app_id, self.private_key, self.alipay_public_key]):
            raise AlipayError("支付宝配置不完整: app_id, private_key, alipay_public_key 必须提供")

        # 设置 API 基础 URL
        if mode == "sandbox":
            self.gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.gateway = "https://openapi.alipay.com/gateway.do"

        # 加载 RSA 密钥
        self._load_keys()

        logger.info(f"Alipay 客户端初始化成功 (mode={self.mode}, app_id={self.app_id})")

    def _load_keys(self):
        """加载 RSA 密钥"""
        try:
            # 尝试解析私钥
            if "-----BEGIN RSA PRIVATE KEY-----" in self.private_key:
                self._private_key = rsa.PrivateKey.load_pkcs1(
                    self.private_key.encode('utf-8')
                )
            elif "-----BEGIN PRIVATE KEY-----" in self.private_key:
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.backends import default_backend
                private_key_obj = serialization.load_pem_private_key(
                    self.private_key.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
                self._private_key = private_key_obj
            else:
                # 使用 PKCS8 格式加载
                self._private_key = rsa.PrivateKey.load_pkcs1(
                    self.private_key.encode('utf-8')
                )

            # 加载公钥
            if "-----BEGIN PUBLIC KEY-----" in self.alipay_public_key:
                self._alipay_public_key = rsa.PublicKey.load_pkcs1_openssl_pem(
                    self.alipay_public_key.encode('utf-8')
                )
            else:
                # 尝试作为 base64 编码的 DER 格式
                key_data = base64.b64decode(self.alipay_public_key)
                self._alipay_public_key = rsa.PublicKey.load_pkcs1_openssl_pem(
                    self.alipay_public_key.encode('utf-8')
                )

        except Exception as e:
            raise AlipaySignError(f"密钥加载失败: {str(e)}")

    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _sign(self, sign_string: str) -> str:
        """
        对字符串进行签名

        Args:
            sign_string: 待签名字符串

        Returns:
            str: 签名字符串 (base64)
        """
        try:
            signature = rsa.sign(
                sign_string.encode('utf-8'),
                self._private_key,
                hashlib.SHA256
            )
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise AlipaySignError(f"签名失败: {str(e)}")

    def _verify_sign(self, sign_string: str, sign: str) -> bool:
        """
        验证签名

        Args:
            sign_string: 签名字符串
            sign: 签名 (base64)

        Returns:
            bool: 签名是否有效
        """
        try:
            signature = base64.b64decode(sign)
            return rsa.verify(
                sign_string.encode('utf-8'),
                signature,
                self._alipay_public_key
            ) == hashlib.sHA256
        except rsa.VerificationError:
            return False
        except Exception as e:
            logger.error(f"签名验证异常: {e}")
            return False

    def _build_sign_string(self, params: Dict[str, Any]) -> str:
        """
        构建签名字符串

        Args:
            params: 参数字典

        Returns:
            str: 待签名字符串
        """
        # 按字典序排序并拼接
        sorted_params = sorted([(k, v) for k, v in params.items() if v])
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        return param_string

    def _generate_signed_params(
        self,
        biz_content: Dict[str, Any],
        method: str,
        notify_url: str = None
    ) -> Dict[str, str]:
        """
        生成带签名的请求参数

        Args:
            biz_content: 业务参数
            method: API 方法
            notify_url: 回调通知地址

        Returns:
            Dict: 带签名的完整参数
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        params = {
            "app_id": self.app_id,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": timestamp,
            "version": "1.0",
            "biz_content": json.dumps(biz_content, ensure_ascii=False),
            "nonce_str": self._generate_nonce_str(),
        }

        if notify_url:
            params["notify_url"] = notify_url

        # 计算签名
        sign_string = self._build_sign_string(params)
        params["sign"] = self._sign(sign_string)

        return params

    async def _request(
        self,
        method: str,
        biz_content: Dict[str, Any],
        notify_url: str = None
    ) -> Dict[str, Any]:
        """
        发送 API 请求

        Args:
            method: API 方法
            biz_content: 业务参数
            notify_url: 回调通知地址

        Returns:
            Dict: 响应数据
        """
        params = self._generate_signed_params(biz_content, method, notify_url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.gateway,
                    data=params,
                    timeout=30.0
                )

            # 解析响应
            response_data = response.json()
            response_key = f"{method.replace('.', '_')}_response"

            if response_key not in response_data:
                raise AlipayAPIError("响应格式错误")

            result = response_data[response_key]

            # 检查错误
            if result.get("code") != "10000":
                raise AlipayAPIError(
                    f"API 调用失败: {result.get('msg', 'Unknown error')}",
                    error_code=result.get("code"),
                    details=result
                )

            # 验证签名（如果有 sign 字段）
            if "sign" in response_data:
                sign = response_data["sign"]
                sign_string = self._build_sign_string(result)
                if not self._verify_sign(sign_string, sign):
                    logger.warning("支付宝响应签名验证失败")

            return result

        except httpx.HTTPError as e:
            logger.error(f"HTTP 请求失败: {e}")
            raise AlipayAPIError(f"网络请求失败: {str(e)}")

    async def create_order(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        product_code: str = "FAST_INSTANT_TRADE_PAY",
        body: str = None,
        goods_detail: list = None,
        passback_params: str = None,
        extend_params: dict = None,
        timeout_express: str = "30m",
        notify_url: str = None,
        return_url: str = None
    ) -> Dict[str, Any]:
        """
        创建支付订单

        Args:
            out_trade_no: 商户订单号
            total_amount: 订单金额
            subject: 订单标题
            product_code: 产品码
            body: 订单描述
            goods_detail: 商品详情
            passback_params: 回传参数
            extend_params: 扩展参数
            timeout_express: 支付超时时间
            notify_url: 异步通知地址
            return_url: 同步跳转地址

        Returns:
            Dict: 支付参数
        """
        logger.info(f"创建支付宝订单: out_trade_no={out_trade_no}, total_amount={total_amount}")

        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": f"{total_amount:.2f}",
            "subject": subject,
            "product_code": product_code,
            "timeout_express": timeout_express,
        }

        if body:
            biz_content["body"] = body
        if goods_detail:
            biz_content["goods_detail"] = goods_detail
        if passback_params:
            biz_content["passback_params"] = passback_params
        if extend_params:
            biz_content["extend_params"] = extend_params

        method = "alipay.trade.app.pay"

        try:
            # 生成带签名的参数
            params = self._generate_signed_params(biz_content, method, notify_url)

            # 返回 form 表单（用于手机网站支付）或签名参数
            result = {
                "out_trade_no": out_trade_no,
                "order_string": "&".join([f"{k}={httpx.utils.is_query_param(v)}" for k, v in params.items()]),
                "sign": params["sign"]
            }

            if return_url:
                result["return_url"] = return_url

            return result

        except AlipayError as e:
            logger.error(f"创建订单失败: {e}")
            raise

    async def create_wap_order(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        product_code: str = "QUICK_WAP_WAY",
        body: str = None,
        notify_url: str = None,
        return_url: str = None,
        timeout_express: str = "30m"
    ) -> Dict[str, Any]:
        """
        创建 WAP 支付订单

        Args:
            out_trade_no: 商户订单号
            total_amount: 订单金额
            subject: 订单标题
            product_code: 产品码
            body: 订单描述
            notify_url: 异步通知地址
            return_url: 同步跳转地址
            timeout_express: 支付超时时间

        Returns:
            Dict: 支付表单 HTML
        """
        logger.info(f"创建支付宝 WAP 订单: out_trade_no={out_trade_no}")

        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": f"{total_amount:.2f}",
            "subject": subject,
            "product_code": product_code,
            "timeout_express": timeout_express,
        }

        if body:
            biz_content["body"] = body

        method = "alipay.trade.wap.pay"

        try:
            params = self._generate_signed_params(biz_content, method, notify_url)

            # 构建表单
            form_html = f'<form id="alipay_form" action="{self.gateway}" method="POST">'
            for key, value in params.items():
                form_html += f'<input type="hidden" name="{key}" value="{value}"/>'
            form_html += '<input type="submit" value="正在跳转..." style="display:none"/></form>'

            return {
                "out_trade_no": out_trade_no,
                "form_html": form_html,
                "return_url": return_url
            }

        except AlipayError as e:
            logger.error(f"创建 WAP 订单失败: {e}")
            raise

    async def verify_notification(
        self,
        params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        验证回调通知

        Args:
            params: 回调参数

        Returns:
            Tuple[bool, Dict]: (是否有效, 解析后的数据)
        """
        if not params:
            return False, {}

        try:
            # 提取签名
            sign = params.get("sign")
            sign_type = params.get("sign_type", "RSA2")

            if not sign:
                logger.warning("支付宝回调缺少签名")
                return False, {}

            # 构建签名字符串
            exclude_keys = {"sign", "sign_type"}
            sign_string = self._build_sign_string(
                {k: v for k, v in params.items() if k not in exclude_keys and v}
            )

            # 验证签名
            if not self._verify_sign(sign_string, sign):
                logger.warning("支付宝回调签名验证失败")
                return False, {}

            # 解析数据
            trade_status = params.get("trade_status")

            data = {
                "out_trade_no": params.get("out_trade_no"),
                "trade_no": params.get("trade_no"),
                "trade_status": trade_status,
                "total_amount": float(params.get("total_amount", 0)),
                "receipt_amount": float(params.get("receipt_amount", 0)),
                "buyer_pay_amount": float(params.get("buyer_pay_amount", 0)),
                "gmt_payment": params.get("gmt_payment"),
                "buyer_logon_id": params.get("buyer_logon_id"),
                "passback_params": params.get("passback_params"),
            }

            is_success = trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED")

            return is_success, data

        except Exception as e:
            logger.error(f"验证回调异常: {e}")
            return False, {}

    async def query_order(
        self,
        out_trade_no: str = None,
        trade_no: str = None
    ) -> Dict[str, Any]:
        """
        查询订单

        Args:
            out_trade_no: 商户订单号
            trade_no: 支付宝交易号

        Returns:
            Dict: 订单信息
        """
        if not out_trade_no and not trade_no:
            raise AlipayError("out_trade_no 和 trade_no 至少需要一个")

        logger.info(f"查询支付宝订单: out_trade_no={out_trade_no}, trade_no={trade_no}")

        biz_content = {}
        if out_trade_no:
            biz_content["out_trade_no"] = out_trade_no
        if trade_no:
            biz_content["trade_no"] = trade_no

        method = "alipay.trade.query"

        try:
            result = await self._request(method, biz_content)
            return result

        except AlipayError as e:
            logger.error(f"查询订单失败: {e}")
            raise

    async def refund(
        self,
        out_trade_no: str = None,
        trade_no: str = None,
        refund_amount: float = None,
        refund_reason: str = None,
        out_request_no: str = None
    ) -> Dict[str, Any]:
        """
        申请退款

        Args:
            out_trade_no: 商户订单号
            trade_no: 支付宝交易号
            refund_amount: 退款金额
            refund_reason: 退款原因
            out_request_no: 商户退款单号

        Returns:
            Dict: 退款结果
        """
        if not out_trade_no and not trade_no:
            raise AlipayError("out_trade_no 和 trade_no 至少需要一个")

        logger.info(f"申请支付宝退款: out_trade_no={out_trade_no}")

        biz_content = {}

        if out_trade_no:
            biz_content["out_trade_no"] = out_trade_no
        if trade_no:
            biz_content["trade_no"] = trade_no
        if refund_amount:
            biz_content["refund_amount"] = f"{refund_amount:.2f}"
        if refund_reason:
            biz_content["refund_reason"] = refund_reason
        if out_request_no:
            biz_content["out_request_no"] = out_request_no
        else:
            # 如果没有提供退款单号，使用时间戳作为单号
            biz_content["out_request_no"] = f"{int(time.time() * 1000)}"

        method = "alipay.trade.refund"

        try:
            result = await self._request(method, biz_content)
            return result

        except AlipayError as e:
            logger.error(f"申请退款失败: {e}")
            raise

    async def close_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        关闭订单

        Args:
            out_trade_no: 商户订单号

        Returns:
            Dict: 关闭结果
        """
        logger.info(f"关闭支付宝订单: out_trade_no={out_trade_no}")

        biz_content = {
            "out_trade_no": out_trade_no
        }

        method = "alipay.trade.close"

        try:
            result = await self._request(method, biz_content)
            return result

        except AlipayError as e:
            logger.error(f"关闭订单失败: {e}")
            raise

    async def download_bill(
        self,
        bill_type: str,
        bill_date: str
    ) -> Dict[str, Any]:
        """
        下载对账单

        Args:
            bill_type: 账单类型 (trade, signcustomer)
            bill_date: 账单日期 (格式: yyyy-MM-dd)

        Returns:
            Dict: 对账单数据
        """
        logger.info(f"下载支付宝对账单: bill_type={bill_type}, bill_date={bill_date}")

        biz_content = {
            "bill_type": bill_type,
            "bill_date": bill_date
        }

        method = "alipay.data.dataservice.bill.downloadurl.query"

        try:
            result = await self._request(method, biz_content)
            return result

        except AlipayError as e:
            logger.error(f"下载对账单失败: {e}")
            raise


# ============================================
# 单例实例（延迟初始化）
# ============================================

_alipay_client: Optional[AlipayClient] = None


def get_alipay_client() -> AlipayClient:
    """
    获取支付宝客户端单例

    Returns:
        AlipayClient: 支付宝客户端实例
    """
    global _alipay_client
    if _alipay_client is None:
        _alipay_client = AlipayClient()
    return _alipay_client


def init_alipay_client(
    app_id: str = None,
    private_key: str = None,
    alipay_public_key: str = None,
    mode: str = "sandbox"
) -> AlipayClient:
    """
    初始化支付宝客户端

    Args:
        app_id: 支付宝应用ID
        private_key: 应用私钥
        alipay_public_key: 支付宝公钥
        mode: 环境模式

    Returns:
        AlipayClient: 支付宝客户端实例
    """
    global _alipay_client
    _alipay_client = AlipayClient(
        app_id=app_id,
        private_key=private_key,
        alipay_public_key=alipay_public_key,
        mode=mode
    )
    return _alipay_client


# ============================================
# 导出
# ============================================

__all__ = [
    "AlipayClient",
    "AlipayError",
    "AlipaySignError",
    "AlipayAPIError",
    "get_alipay_client",
    "init_alipay_client"
]
