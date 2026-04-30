"""
Payment Module
支付模块

提供微信、支付宝、PayPal 支付功能

功能：
- 创建支付订单
- 查询支付状态
- 处理支付回调
- 申请退款

依赖模块：
- auth: 认证模块
- transaction: 交易模块

配置项：
- WECHAT_APP_ID: 微信应用ID
- WECHAT_MCH_ID: 微信商户号
- WECHAT_API_KEY: 微信API密钥
- WECHAT_CERT_PATH: 微信退款证书路径
- ALIPAY_APP_ID: 支付宝应用ID
- ALIPAY_PRIVATE_KEY: 支付宝私钥
- ALIPAY_PUBLIC_KEY: 支付宝公钥
- PAYPAL_CLIENT_ID: PayPal 客户端ID
- PAYPAL_CLIENT_SECRET: PayPal 客户端密钥
- PAYPAL_MODE: PayPal 环境模式 (sandbox/live)
- PAYPAL_WEBHOOK_ID: PayPal Webhook ID
"""
from __future__ import annotations

import logging
from typing import Optional, List
from pydantic import BaseModel

# 导入模块组件
from .schemas import (
    PaymentMethod,
    PaymentStatusEnum,
    PaymentChannel,
    PaymentCreate,
    PaymentResponse,
    PaymentStatus,
    RefundRequest,
    RefundResult,
    # New schemas
    CreateOrderRequest,
    OrderResponse,
    OrderListResponse,
    PaymentCreateRequest,
    PurchaseResponse,
    SubmissionCreate,
    SubmissionResponse,
    ApproveSubmissionBody,
    RejectSubmissionBody,
    DailyRevenueStat,
    RevenueStatsResponse,
    PaymentAccountCreate,
    PaymentAccountUpdate,
    PaymentAccountResponse,
    CreatorSettlementPreference,
    CreatorEarningResponse,
    CreatorEarningListResponse,
    CreatorEarningSummary,
    SettlementRequest,
    SettlementResponse,
    SettlementListResponse,
    PendingSettlementResponse,
    ALLOWED_ACCOUNT_TYPES,
    ALLOWED_CURRENCIES,
    ALLOWED_SETTLEMENT_METHODS,
    ALLOWED_SETTLEMENT_PERIODS,
)
from .services import PaymentService, get_payment_service
from .routes import router

logger = logging.getLogger(__name__)


# ============================================
# 模块元数据
# ============================================

MODULE_ID = "payment"
MODULE_NAME = "支付模块"
MODULE_VERSION = "1.0.0"
MODULE_DESCRIPTION = "提供微信、支付宝、PayPal 支付功能"
MODULE_DEPENDENCIES = ["auth", "transaction"]


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "payment"
    name: str = "支付模块"
    version: str = "1.0.0"
    description: str = "提供微信、支付宝、PayPal 支付功能"
    dependencies: List[str] = ["auth", "transaction"]


# ============================================
# 模块配置
# ============================================

class BaseModule:
    """模块基类"""

    def __init__(self):
        self.id = MODULE_ID
        self.name = MODULE_NAME
        self.version = MODULE_VERSION
        self.description = MODULE_DESCRIPTION
        self.dependencies = MODULE_DEPENDENCIES
        self._enabled = True
        self._info = ModuleInfo()

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return MODULE_ID

    @property
    def info(self):
        """Get module info."""
        return self._info

    @property
    def enabled(self) -> bool:
        """模块是否启用"""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """设置模块启用状态"""
        self._enabled = value

    async def on_load(self):
        """模块加载时调用"""
        logger.info(f"{self.name} v{self.version} 加载中...")

    async def on_enable(self):
        """模块启用时调用"""
        logger.info(f"{self.name} 已启用")

    async def on_disable(self):
        """模块禁用时调用"""
        logger.info(f"{self.name} 已禁用")

    async def on_unload(self):
        """模块卸载时调用"""
        logger.info(f"{self.name} 卸载中...")


class PaymentModule(BaseModule):
    """支付模块"""

    def __init__(self):
        super().__init__()
        self.payment_service: Optional[PaymentService] = None

    async def on_load(self):
        """加载支付模块"""
        await super().on_load()

        # 初始化支付服务
        self.payment_service = get_payment_service()

        logger.info(f"{self.name} 加载完成")

    def get_routes(self):
        """获取模块路由"""
        return router

    def get_services(self) -> dict:
        """获取模块服务"""
        return {
            "payment_service": self.payment_service
        }


# ============================================
# 模块实例（延迟初始化）
# ============================================

_payment_module: Optional[PaymentModule] = None


def get_payment_module() -> PaymentModule:
    """
    获取支付模块实例

    Returns:
        PaymentModule: 支付模块实例
    """
    global _payment_module
    if _payment_module is None:
        _payment_module = PaymentModule()
    return _payment_module


def init_payment_module() -> PaymentModule:
    """
    初始化支付模块

    Returns:
        PaymentModule: 支付模块实例
    """
    global _payment_module
    _payment_module = PaymentModule()
    return _payment_module


# ============================================
# 导出
# ============================================

__all__ = [
    # 模块类
    "PaymentModule",
    "BaseModule",
    "get_payment_module",
    "init_payment_module",
    # 模块信息
    "ModuleInfo",
    # 路由
    "router",
    # 服务
    "PaymentService",
    "get_payment_service",
    # Schemas - existing
    "PaymentMethod",
    "PaymentStatusEnum",
    "PaymentChannel",
    "PaymentCreate",
    "PaymentResponse",
    "PaymentStatus",
    "RefundRequest",
    "RefundResult",
    # Schemas - orders
    "CreateOrderRequest",
    "OrderResponse",
    "OrderListResponse",
    "PaymentCreateRequest",
    # Schemas - purchases
    "PurchaseResponse",
    # Schemas - submissions
    "SubmissionCreate",
    "SubmissionResponse",
    "ApproveSubmissionBody",
    "RejectSubmissionBody",
    # Schemas - revenue
    "DailyRevenueStat",
    "RevenueStatsResponse",
    # Schemas - accounts
    "PaymentAccountCreate",
    "PaymentAccountUpdate",
    "PaymentAccountResponse",
    # Schemas - settlements
    "CreatorSettlementPreference",
    "CreatorEarningResponse",
    "CreatorEarningListResponse",
    "CreatorEarningSummary",
    "SettlementRequest",
    "SettlementResponse",
    "SettlementListResponse",
    "PendingSettlementResponse",
    # Constants
    "ALLOWED_ACCOUNT_TYPES",
    "ALLOWED_CURRENCIES",
    "ALLOWED_SETTLEMENT_METHODS",
    "ALLOWED_SETTLEMENT_PERIODS",
    # 常量
    "MODULE_ID",
    "MODULE_NAME",
    "MODULE_VERSION",
    "MODULE_DESCRIPTION",
    "MODULE_DEPENDENCIES",
]
