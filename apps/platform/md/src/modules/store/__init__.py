"""
多产品线商城模块 (Store Module)

提供多产品线商城购物车、订单管理和支付功能

功能:
- 产品集合管理（按产品线分集合）
- 产品管理
- 购物车功能
- 订单创建与管理
- 微信支付 / 支付宝支付
- 支付回调处理
- 商城统计（管理端）
"""
from __future__ import annotations

from typing import List
from pydantic import BaseModel

from .routes import router as store_router
from .routes import admin_router as admin_store_router
from .services import StoreService, AdminStoreService
from .schemas import (
    StoreCollection,
    StoreProduct,
    StoreProductDetail,
    StoreCartItem,
    StoreOrder,
    StoreOrderItem,
    CartAddRequest,
    CartUpdateRequest,
    CreateOrderRequest,
    PaymentRequest,
    StoreCollectionCreate,
    StoreCollectionUpdate,
    StoreProductCreate,
    StoreProductUpdate,
    OrderStatusUpdate,
    StoreProductListResponse,
    StoreCollectionListResponse,
    StoreOrderDetailResponse,
    StoreOrderListResponse,
    StoreStats,
    CollectionStats,
    PaymentResponse,
    PaymentStatusResponse,
    CreateOrderResponse,
)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "store"
    name: str = "多产品线商城模块"
    version: str = "1.0.0"
    description: str = "提供多产品线商城购物车、订单管理和支付功能"
    dependencies: List[str] = ["auth"]


# ============================================
# BaseModule
# ============================================

class BaseModule:
    """模块基类"""

    def __init__(self):
        self.id = "store"
        self.name = "多产品线商城模块"
        self.version = "1.0.0"
        self.description = "提供多产品线商城购物车、订单管理和支付功能"
        self.dependencies = ["auth"]
        self.router = store_router
        self.admin_router = admin_store_router
        self._info = ModuleInfo()

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "store"

    @property
    def info(self):
        """Get module info."""
        return self._info

    def get_router(self):
        """获取公共路由"""
        return self.router

    def get_admin_router(self):
        """获取管理路由"""
        return self.admin_router

    def get_services(self):
        """获取服务实例"""
        return {
            "store": StoreService,
            "admin_store": AdminStoreService
        }

    def get_config(self):
        """获取模块配置"""
        return {
            "payment_enabled": True,
            "wechat_enabled": False,
            "alipay_enabled": False,
            "order_expire_minutes": 30
        }


# 创建模块实例
module = BaseModule()

# 导出公共 router 和管理 router（PluginManager 会根据命名查找）
router = store_router
admin_router = admin_store_router


# 导出
__all__ = [
    # 模块信息
    "ModuleInfo",

    # 路由
    "router",
    "admin_router",

    # 服务
    "StoreService",
    "AdminStoreService",

    # 数据模型
    "StoreCollection",
    "StoreProduct",
    "StoreProductDetail",
    "StoreCartItem",
    "StoreOrder",
    "StoreOrderItem",

    # 请求模型
    "CartAddRequest",
    "CartUpdateRequest",
    "CreateOrderRequest",
    "PaymentRequest",
    "StoreCollectionCreate",
    "StoreCollectionUpdate",
    "StoreProductCreate",
    "StoreProductUpdate",
    "OrderStatusUpdate",

    # 响应模型
    "StoreProductListResponse",
    "StoreCollectionListResponse",
    "StoreOrderDetailResponse",
    "StoreOrderListResponse",
    "StoreStats",
    "CollectionStats",
    "PaymentResponse",
    "PaymentStatusResponse",
    "CreateOrderResponse",

    # 模块
    "BaseModule",
    "module"
]
