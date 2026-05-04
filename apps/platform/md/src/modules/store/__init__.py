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

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template

from .routes import router as store_router
from .routes import admin_router as admin_store_router
from .inventory_routes import external_router as inventory_external_router
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

    def install(self, app: FastAPI) -> None:
        """安装模块到应用"""
        app.include_router(self.router)
        app.include_router(self.admin_router)
        app.include_router(inventory_external_router)
        # Page routes
        @app.get("/store", response_class=HTMLResponse, include_in_schema=False)
        async def store_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                collections = []
                products = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("""
                            SELECT sc.*, COUNT(sp.id) as product_count
                            FROM store_collections sc
                            LEFT JOIN store_products sp ON sp.collection_id = sc.id AND sp.is_active = TRUE
                            WHERE sc.is_active = TRUE
                            GROUP BY sc.id
                            ORDER BY sc.sort_order, sc.id
                        """)
                        rows = cur.fetchall()
                        for r in rows:
                            collections.append({
                                "id": r.get("id"),
                                "name": r.get("name", ""),
                                "collection_key": r.get("collection_key", ""),
                                "description": r.get("description", ""),
                                "image_url": r.get("image_url", ""),
                                "product_count": r.get("product_count", 0),
                            })

                        cur.execute("""
                            SELECT sp.*, sc.name as collection_name, sc.collection_key
                            FROM store_products sp
                            LEFT JOIN store_collections sc ON sp.collection_id = sc.id
                            WHERE sp.is_active = TRUE
                            ORDER BY sp.sort_order, sp.id
                            LIMIT 30
                        """)
                        p_rows = cur.fetchall()
                        for p in p_rows:
                            products.append({
                                "id": p.get("id"),
                                "name": p.get("name", ""),
                                "description": p.get("description", ""),
                                "price": float(p.get("price", 0) or 0),
                                "original_price": float(p.get("original_price", 0) or 0),
                                "image_url": p.get("image_url", ""),
                                "collection_name": p.get("collection_name", ""),
                                "collection_key": p.get("collection_key", ""),
                                "stock": p.get("stock", 0),
                                "sales_count": p.get("sales_count", 0),
                            })
                except Exception:
                    products, collections = [], []

            except Exception:
                products, collections = [], []

            # Merge: set collection = first collection with its products
            collection = None
            if collections:
                first = collections[0]
                ckey = first.get("collection_key", "")
                coll_products = [p for p in products if p.get("collection_key") == ckey]
                collection = {
                    "id": first.get("id"),
                    "name": first.get("name", ""),
                    "name_zh": first.get("name", ""),
                    "collection_key": ckey,
                    "description": first.get("description", ""),
                    "image_url": first.get("image_url", ""),
                    "product_count": first.get("product_count", 0),
                    "products": coll_products,
                }
                # Add name_zh, url to all collections for the switcher
                for c in collections:
                    c["name_zh"] = c.get("name", "")
                    c["url"] = f"/store?collection={c.get('collection_key', '')}"

            # No server-side cart; client JS manages it
            return render_template(request, "store/index.html", {
                "collection": collection,
                "collections": collections,
            })

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
