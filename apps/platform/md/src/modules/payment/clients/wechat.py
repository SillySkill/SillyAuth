"""
WeChat Pay Client
微信支付客户端

提供微信支付的核心功能：
- 创建支付订单
- 查询订单状态
- 申请退款
- 验证回调签名
"""
import os
import time
import random
import string
import hashlib
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)


# ============================================
# 异常类定义
# ============================================

class WeChatPayError(Exception):
    """微信支付基础异常"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class WeChatPaySignError(WeChatPayError):
    """微信支付签名异常"""
    pass


class WeChatPayAPIError(WeChatPayError):
    """微信支付 API 调用异常"""
    pass


# ============================================
# 微信支付客户端类
# ============================================

class WeChatPayClient:
    """
    微信支付 API 客户端

    支持 V2 和 V3 API
    """

    def __init__(
        self,
        app_id: str = None,
        mch_id: str = None,
        api_key: str = None,
        cert_path: str = None,
        mode: str = "sandbox"
    ):
        """
        初始化微信支付客户端

        Args:
            app_id: 微信应用ID
            mch_id: 商户号
            api_key: API密钥
            cert_path: 证书路径（用于退款等敏感操作）
            mode: 环境模式 (sandbox/live)
        """
        self.app_id = app_id or os.getenv("WECHAT_APP_ID")
        self.mch_id = mch_id or os.getenv("WECHAT_MCH_ID")
        self.api_key = api_key or os.getenv("WECHAT_API_KEY")
        self.cert_path = cert_path or os.getenv("WECHAT_CERT_PATH")

        if not all([self.app_id, self.mch_id, self.api_key]):
            raise WeChatPayError("微信支付配置不完整: app_id, mch_id, api_key 必须提供")

        # 设置 API 基础 URL
        if mode == "sandbox":
            self.base_url = "https://api.mch.weixin.qq.com/sandboxnew"
        else:
            self.base_url = "https://api.mch.weixin.qq.com"

        self.mode = mode
        logger.info(f"WeChat Pay 客户端初始化成功 (mode={self.mode}, mch_id={self.mch_id})")

    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _sign_v2(self, params: Dict[str, Any]) -> str:
        """
        生成签名 (V2)

        Args:
            params: 参数字典

        Returns:
            str: 签名字符串
        """
        # 按字典序排序参数
        sorted_params = sorted([(k, v) for k, v in params.items() if k != "sign" and v])
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])

        # 拼接密钥
        sign_string = f"{param_string}&key={self.api_key}"

        # MD5 签名
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

    def _verify_sign_v2(self, params: Dict[str, Any]) -> bool:
        """
        验证签名 (V2)

        Args:
            params: 参数字典

        Returns:
            bool: 签名是否有效
        """
        if "sign" not in params:
            return False

        received_sign = params["sign"]
        calculated_sign = self._sign_v2(params)

        return received_sign == calculated_sign

    def _to_xml(self, data: Dict[str, Any]) -> str:
        """将字典转换为 XML"""
        root = ET.Element("xml")
        for key, value in data.items():
            child = ET.SubElement(root, key)
            if isinstance(value, str):
                child.text = value
            else:
                child.text = str(value)
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    def _from_xml(self, xml_string: str) -> Dict[str, Any]:
        """从 XML 解析为字典"""
        root = ET.fromstring(xml_string)
        return {child.tag: child.text for child in root}

    async def _request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        use_cert: bool = False
    ) -> Dict[str, Any]:
        """
        发送 API 请求

        Args:
            endpoint: API 端点
            data: 请求数据
            use_cert: 是否使用证书

        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        xml_data = self._to_xml(data)

        headers = {
            "Content-Type": "application/xml"
        }

        try:
            async with httpx.AsyncClient() as client:
                if use_cert and self.cert_path:
                    with open(self.cert_path, 'rb') as f:
                        cert_content = f.read()
                    with open(self.cert_path, 'rb') as f:
                        key_content = f.read()
                    response = await client.post(
                        url,
                        content=xml_data,
                        headers=headers,
                        cert=(cert_content, key_content),
                        timeout=30.0
                    )
                else:
                    response = await client.post(
                        url,
                        content=xml_data,
                        headers=headers,
                        timeout=30.0
                    )

            result = self._from_xml(response.text)

            # 检查返回状态码
            if result.get("return_code") != "SUCCESS":
                raise WeChatPayAPIError(
                    f"API 请求失败: {result.get('return_msg', 'Unknown error')}",
                    error_code=result.get("return_code"),
                    details=result
                )

            # 检查业务结果
            if result.get("result_code") != "SUCCESS":
                raise WeChatPayAPIError(
                    f"业务处理失败: {result.get('err_code_des', result.get('err_code', 'Unknown'))}",
                    error_code=result.get("err_code"),
                    details=result
                )

            return result

        except httpx.HTTPError as e:
            logger.error(f"HTTP 请求失败: {e}")
            raise WeChatPayAPIError(f"网络请求失败: {str(e)}")

    async def create_order(
        self,
        out_trade_no: str,
        total_fee: int,
        body: str,
        trade_type: str = "APP",
        notify_url: str = None,
        openid: str = None,
        attach: str = None,
        time_start: str = None,
        time_expire: str = None
    ) -> Dict[str, Any]:
        """
        创建支付订单

        Args:
            out_trade_no: 商户订单号
            total_fee: 订单金额（分）
            body: 商品描述
            trade_type: 交易类型 (APP, JSAPI, NATIVE, MWEB)
            notify_url: 通知回调地址
            openid: 用户openid（JSAPI必填）
            attach: 附加数据
            time_start: 订单起始时间
            time_expire: 订单过期时间

        Returns:
            Dict: 支付参数
        """
        logger.info(f"创建微信支付订单: out_trade_no={out_trade_no}, total_fee={total_fee}")

        # 构建请求参数
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": body,
            "out_trade_no": out_trade_no,
            "total_fee": total_fee,
            "spbill_create_ip": os.getenv("SERVER_IP", "127.0.0.1"),
            "trade_type": trade_type,
        }

        if notify_url:
            params["notify_url"] = notify_url
        if openid:
            params["openid"] = openid
        if attach:
            params["attach"] = attach
        if time_start:
            params["time_start"] = time_start
        if time_expire:
            params["time_expire"] = time_expire

        # 添加签名
        params["sign"] = self._sign_v2(params)

        try:
            result = await self._request("/pay/unifiedorder", params)

            # 根据交易类型返回不同格式
            if trade_type == "NATIVE":
                # 扫码支付
                return {
                    "code_url": result.get("code_url"),
                    "prepay_id": result.get("prepay_id"),
                    "out_trade_no": out_trade_no
                }
            elif trade_type == "JSAPI":
                # JSAPI 支付
                prepay_id = result.get("prepay_id")
                return {
                    "prepay_id": prepay_id,
                    "out_trade_no": out_trade_no
                }
            elif trade_type == "APP":
                # APP 支付
                prepay_id = result.get("prepay_id")
                timestamp = str(int(time.time()))

                # 构建 APP 调起支付的签名
                pay_params = {
                    "appid": self.app_id,
                    "partnerid": self.mch_id,
                    "prepayid": prepay_id,
                    "package": "Sign=WXPay",
                    "noncestr": self._generate_nonce_str(),
                    "timestamp": timestamp
                }
                pay_params["sign"] = self._sign_v2(pay_params)

                return {
                    "out_trade_no": out_trade_no,
                    "pay_params": pay_params
                }
            elif trade_type == "MWEB":
                # H5 支付
                return {
                    "mweb_url": result.get("mweb_url"),
                    "prepay_id": result.get("prepay_id"),
                    "out_trade_no": out_trade_no
                }
            else:
                return result

        except WeChatPayError as e:
            logger.error(f"创建订单失败: {e}")
            raise

    async def query_order(
        self,
        out_trade_no: str = None,
        transaction_id: str = None
    ) -> Dict[str, Any]:
        """
        查询订单

        Args:
            out_trade_no: 商户订单号
            transaction_id: 微信订单号

        Returns:
            Dict: 订单信息
        """
        if not out_trade_no and not transaction_id:
            raise WeChatPayError("out_trade_no 和 transaction_id 至少需要一个")

        logger.info(f"查询微信支付订单: out_trade_no={out_trade_no}, transaction_id={transaction_id}")

        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
        }

        if out_trade_no:
            params["out_trade_no"] = out_trade_no
        if transaction_id:
            params["transaction_id"] = transaction_id

        params["sign"] = self._sign_v2(params)

        try:
            result = await self._request("/pay/orderquery", params)
            return result

        except WeChatPayError as e:
            logger.error(f"查询订单失败: {e}")
            raise

    async def refund(
        self,
        out_refund_no: str,
        total_fee: int,
        refund_fee: int,
        out_trade_no: str = None,
        transaction_id: str = None,
        refund_desc: str = None,
        refund_account: str = None
    ) -> Dict[str, Any]:
        """
        申请退款

        Args:
            out_refund_no: 商户退款单号
            total_fee: 订单金额（分）
            refund_fee: 退款金额（分）
            out_trade_no: 商户订单号
            transaction_id: 微信订单号
            refund_desc: 退款原因
            refund_account: 退款资金来源 (REFUND_SOURCE_UNSETTLED_FUNDS, REFUND_SOURCE_RECHARGE_FUNDS)

        Returns:
            Dict: 退款结果
        """
        if not out_trade_no and not transaction_id:
            raise WeChatPayError("out_trade_no 和 transaction_id 至少需要一个")

        logger.info(f"申请微信支付退款: out_refund_no={out_refund_no}, refund_fee={refund_fee}")

        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "out_refund_no": out_refund_no,
            "total_fee": total_fee,
            "refund_fee": refund_fee,
        }

        if out_trade_no:
            params["out_trade_no"] = out_trade_no
        if transaction_id:
            params["transaction_id"] = transaction_id
        if refund_desc:
            params["refund_desc"] = refund_desc
        if refund_account:
            params["refund_account"] = refund_account

        params["sign"] = self._sign_v2(params)

        try:
            result = await self._request("/secapi/pay/refund", params, use_cert=True)
            return result

        except WeChatPayError as e:
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
        logger.info(f"关闭微信支付订单: out_trade_no={out_trade_no}")

        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "out_trade_no": out_trade_no,
        }

        params["sign"] = self._sign_v2(params)

        try:
            result = await self._request("/pay/closeorder", params)
            return result

        except WeChatPayError as e:
            logger.error(f"关闭订单失败: {e}")
            raise

    def verify_notification(self, data: Dict[str, Any]) -> bool:
        """
        验证回调通知签名

        Args:
            data: 回调数据

        Returns:
            bool: 签名是否有效
        """
        if not data:
            return False

        is_valid = self._verify_sign_v2(data)
        if not is_valid:
            logger.warning("微信支付回调签名验证失败")

        return is_valid

    def verify_jsapi_signature(
        self,
        prepay_id: str,
        timeStamp: str,
        nonceStr: str,
        package: str,
        signType: str,
        paySign: str
    ) -> bool:
        """
        验证 JSAPI 支付签名

        Args:
            prepay_id: 预支付交易会话ID
            timeStamp: 时间戳
            nonceStr: 随机字符串
            package: 扩展包
            signType: 签名类型
            paySign: 签名

        Returns:
            bool: 签名是否有效
        """
        sign_params = {
            "appId": self.app_id,
            "timeStamp": timeStamp,
            "nonceStr": nonceStr,
            "package": package,
            "signType": signType
        }

        # JSAPI 使用 appId, timeStamp, nonceStr, package 计算签名
        sorted_params = sorted([(k, v) for k, v in sign_params.items()])
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_string = f"{param_string}&key={self.api_key}"

        calculated_sign = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().upper()

        return calculated_sign == paySign


# ============================================
# 单例实例（延迟初始化）
# ============================================

_wechat_pay_client: Optional[WeChatPayClient] = None


def get_wechat_pay_client() -> WeChatPayClient:
    """
    获取微信支付客户端单例

    Returns:
        WeChatPayClient: 微信支付客户端实例
    """
    global _wechat_pay_client
    if _wechat_pay_client is None:
        _wechat_pay_client = WeChatPayClient()
    return _wechat_pay_client


def init_wechat_pay_client(
    app_id: str = None,
    mch_id: str = None,
    api_key: str = None,
    cert_path: str = None,
    mode: str = "sandbox"
) -> WeChatPayClient:
    """
    初始化微信支付客户端

    Args:
        app_id: 微信应用ID
        mch_id: 商户号
        api_key: API密钥
        cert_path: 证书路径
        mode: 环境模式

    Returns:
        WeChatPayClient: 微信支付客户端实例
    """
    global _wechat_pay_client
    _wechat_pay_client = WeChatPayClient(
        app_id=app_id,
        mch_id=mch_id,
        api_key=api_key,
        cert_path=cert_path,
        mode=mode
    )
    return _wechat_pay_client


# ============================================
# 导出
# ============================================

__all__ = [
    "WeChatPayClient",
    "WeChatPayError",
    "WeChatPaySignError",
    "WeChatPayAPIError",
    "get_wechat_pay_client",
    "init_wechat_pay_client"
]
