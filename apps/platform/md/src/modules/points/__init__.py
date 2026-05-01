"""
积分商城模块 (Points Mall Module)

提供积分获取、兑换、积分商城、购物车、分类管理功能

功能:
- 用户积分余额查询
- 积分历史记录与交易记录
- 每日签到
- 积分商品浏览（含分类筛选）
- 商品分类管理
- 购物车（添加/更新/移除/清空/结算）
- 商品兑换
- 兑换记录查询
- 用户积分统计
- 商城管理（管理员）
"""
from __future__ import annotations

from typing import List
from pydantic import BaseModel

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template

from .routes import router as points_router
from .services import PointsService, MallService, CategoryService, CartService
from .schemas import (
    # 积分余额与记录
    PointsBalance,
    PointsRecord,
    PointsHistoryResponse,
    PointsType,
    PointsTransactionResponse,
    PointsTransactionListResponse,
    # 积分兑换
    PointsExchange,
    # 商城商品
    MallItemCreate,
    MallItemResponse,
    MallItemUpdate,
    # 兑换
    ExchangeRequest,
    ExchangeResponse,
    ExchangeRecordResponse,
    SignInResponse,
    # 商品分类
    PointsCategorySchema,
    CategoryCreate,
    CategoryUpdate,
    # 购物车
    ShoppingCartItemSchema,
    CartRequest,
    CartItemUpdate,
    CartResponse,
    # 用户统计
    UserPointsStats,
    # 商城统计
    MallStats,
)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "points"
    name: str = "积分商城模块"
    version: str = "1.1.0"
    description: str = "提供积分获取、兑换、积分商城、购物车、分类管理功能"
    dependencies: List[str] = ["auth"]


# ============================================
# BaseModule
# ============================================

class BaseModule:
    """模块基类"""

    def __init__(self):
        self.id = "points"
        self.name = "积分商城模块"
        self.version = "1.1.0"
        self.description = "提供积分获取、兑换、积分商城、购物车、分类管理功能"
        self.dependencies = ["auth"]
        self.router = points_router
        self._info = ModuleInfo()

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "points"

    @property
    def info(self):
        """Get module info."""
        return self._info

    def get_router(self):
        """获取路由"""
        return self.router

    def install(self, app: FastAPI) -> None:
        """安装模块到应用"""
        app.include_router(self.router)
        # Page routes
        @app.get("/points-mall", response_class=HTMLResponse, include_in_schema=False)
        async def points_mall_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                items = []
                categories = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("""
                            SELECT mi.*, COALESCE(pc.name, '未分类') as category_name
                            FROM mall_items mi
                            LEFT JOIN points_categories pc ON mi.category_id = pc.id
                            WHERE mi.is_active = TRUE
                            ORDER BY mi.sort_order, mi.created_at DESC
                            LIMIT 30
                        """)
                        rows = cur.fetchall()
                        for r in rows:
                            items.append({
                                "id": r.get("id"),
                                "name": r.get("name", ""),
                                "description": r.get("description", ""),
                                "image_url": r.get("image_url", ""),
                                "points": r.get("points", 0),
                                "stock": r.get("stock", 0),
                                "exchange_count": r.get("exchange_count", 0),
                                "category_name": r.get("category_name", "未分类"),
                            })
                except Exception:
                    items = []

                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT id, name, icon FROM points_categories ORDER BY sort_order")
                        cat_rows = cur.fetchall()
                        for c in cat_rows:
                            categories.append({
                                "id": c.get("id"),
                                "name": c.get("name", ""),
                                "icon": c.get("icon", "fa-gift"),
                            })
                except Exception:
                    categories = []
            except Exception:
                items, categories = [], []

            return render_template(request, "points/mall.html", {
                "items": items,
                "categories": categories,
            })

    def get_services(self):
        """获取服务实例"""
        return {
            "points": PointsService,
            "mall": MallService,
            "category": CategoryService,
            "cart": CartService
        }

    def get_config(self):
        """获取模块配置"""
        return {
            "points_name": "傻福币",
            "exchange_rate": 100,
            "sign_in_points": 10,
            "daily_limit": 1000
        }


# 创建模块实例
module = BaseModule()


# 导出
__all__ = [
    # 模块信息
    "ModuleInfo",

    # 路由
    "points_router",

    # 服务
    "PointsService",
    "MallService",
    "CategoryService",
    "CartService",

    # 模型 - 积分
    "PointsBalance",
    "PointsRecord",
    "PointsHistoryResponse",
    "PointsType",
    "PointsTransactionResponse",
    "PointsTransactionListResponse",
    "PointsExchange",

    # 模型 - 商城
    "MallItemCreate",
    "MallItemResponse",
    "MallItemUpdate",

    # 模型 - 兑换
    "ExchangeRequest",
    "ExchangeResponse",
    "ExchangeRecordResponse",
    "SignInResponse",

    # 模型 - 分类
    "PointsCategorySchema",
    "CategoryCreate",
    "CategoryUpdate",

    # 模型 - 购物车
    "ShoppingCartItemSchema",
    "CartRequest",
    "CartItemUpdate",
    "CartResponse",

    # 模型 - 统计
    "UserPointsStats",
    "MallStats",

    # 模块
    "BaseModule",
    "module"
]
