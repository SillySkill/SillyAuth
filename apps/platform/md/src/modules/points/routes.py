"""
积分商城API路由
提供积分获取、兑换、积分商城、购物车、分类管理等功能
"""

import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .schemas import (
    PointsBalance,
    PointsHistoryResponse,
    PointsRecord,
    SignInResponse,
    MallItemCreate,
    MallItemResponse,
    MallItemUpdate,
    ExchangeRequest,
    ExchangeResponse,
    ExchangeRecordResponse,
    MallStats,
    PointsCategorySchema,
    CategoryCreate,
    CategoryUpdate,
    ShoppingCartItemSchema,
    CartRequest,
    CartItemUpdate,
    CartResponse,
    UserPointsStats,
    PointsTransactionListResponse,
    PointsTransactionResponse,
)
from .services import PointsService, MallService, CategoryService, CartService


router = APIRouter(prefix="/api/v1/points", tags=["积分商城"])

# 配置
POINTS_NAME = "傻福币"
SIGN_IN_POINTS = 10


# ==================== 积分余额与历史 ====================

@router.get("/balance", response_model=PointsBalance)
async def get_points_balance(user_id: int = Query(..., description="用户ID")):
    """
    获取用户积分余额

    - user_id: 用户ID
    """
    try:
        balance = PointsService.get_balance(user_id)
        return PointsBalance(**balance)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=PointsHistoryResponse)
async def get_points_history(
    user_id: int = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取积分历史记录

    - user_id: 用户ID
    - page: 页码
    - limit: 每页数量
    """
    try:
        result = PointsService.get_history(user_id, page, limit)
        return PointsHistoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 签到 ====================

@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(user_id: int = Query(..., description="用户ID")):
    """
    每日签到

    - user_id: 用户ID
    - 返回签到结果和获得的积分
    """
    try:
        result = PointsService.sign_in(user_id, SIGN_IN_POINTS)
        return SignInResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 积分商城 ====================

@router.get("/mall", response_model=List[MallItemResponse])
async def list_mall_items(
    category: Optional[str] = Query(None, description="分类筛选"),
    is_featured: Optional[bool] = Query(None, description="是否精选"),
    is_active: bool = Query(True, description="是否上架"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """
    获取商城商品列表

    - category: 分类筛选
    - is_featured: 是否精选
    - is_active: 是否上架
    - page: 页码
    - limit: 每页数量
    """
    try:
        items = MallService.list_items(category, is_featured, is_active, page, limit)
        return [MallItemResponse(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mall/items/{item_id}", response_model=MallItemResponse)
async def get_mall_item(item_id: int):
    """
    获取商品详情

    - item_id: 商品ID
    """
    try:
        item = MallService.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="商品不存在")
        return MallItemResponse(**item)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mall/items", response_model=MallItemResponse)
async def create_mall_item(item: MallItemCreate):
    """
    创建商城商品（管理员功能）

    - name: 商品名称
    - description: 商品描述
    - points_cost: 所需积分
    - stock: 库存（-1表示无限）
    - image_url: 图片URL
    - category: 分类
    - is_featured: 是否精选
    - sort_order: 排序
    - valid_days: 有效期天数
    """
    try:
        item_data = item.model_dump()
        created_item = MallService.create_item(item_data)
        return MallItemResponse(**created_item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mall/items/{item_id}", response_model=MallItemResponse)
async def update_mall_item(item_id: int, item: MallItemUpdate):
    """
    更新商城商品（管理员功能）

    - item_id: 商品ID
    """
    try:
        update_data = item.model_dump(exclude_unset=True)
        updated_item = MallService.update_item(item_id, update_data)
        return MallItemResponse(**updated_item)
    except ValueError as e:
        raise HTTPException(status_code=404 if "不存在" in str(e) else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/mall/items/{item_id}")
async def delete_mall_item(item_id: int):
    """
    删除商城商品（管理员功能）

    - item_id: 商品ID
    """
    try:
        if not MallService.delete_item(item_id):
            raise HTTPException(status_code=404, detail="商品不存在")
        return {"message": "商品删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 兑换 ====================

@router.post("/mall/exchange", response_model=ExchangeResponse)
async def exchange_item(exchange: ExchangeRequest, user_id: int = Query(..., description="用户ID")):
    """
    兑换商品

    - user_id: 用户ID
    - item_id: 商品ID
    - quantity: 数量
    """
    try:
        result = MallService.exchange_item(user_id, exchange.item_id, exchange.quantity)
        return ExchangeResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mall/my-exchanges", response_model=List[ExchangeRecordResponse])
async def get_my_exchanges(
    user_id: int = Query(..., description="用户ID"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取我的兑换记录

    - user_id: 用户ID
    - status: 状态筛选
    - page: 页码
    - limit: 每页数量
    """
    try:
        result = MallService.get_my_exchanges(user_id, status, page, limit)
        return [ExchangeRecordResponse(**record) for record in result['records']]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 统计 ====================

@router.get("/mall/stats", response_model=MallStats)
async def get_mall_stats():
    """
    获取商城统计数据
    """
    try:
        stats = MallService.get_stats()
        return MallStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 商品分类 ====================

@router.get("/categories", response_model=List[PointsCategorySchema])
async def get_categories():
    """
    获取所有商品分类

    支持两种分类来源：
    1. points_categories 表（结构化分类管理）
    2. mall_items 表的 category 字段（简单分类提取）

    优先使用结构化分类。
    """
    try:
        categories = CategoryService.get_categories()
        if not categories:
            # 回退：从 mall_items 提取分类
            simple_categories = CategoryService.get_mall_item_categories()
            return [
                PointsCategorySchema(
                    id=idx + 1,
                    category_key=cat.get('category', ''),
                    name_en=cat.get('category', ''),
                    name_zh=cat.get('category', ''),
                    sort_order=idx
                )
                for idx, cat in enumerate(simple_categories)
            ]
        return [PointsCategorySchema(**cat) for cat in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/all", response_model=List[PointsCategorySchema])
async def get_all_categories():
    """
    获取所有分类（管理员，含非活跃）
    """
    try:
        categories = CategoryService.get_all_categories(include_inactive=True)
        return [PointsCategorySchema(**cat) for cat in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categories", response_model=PointsCategorySchema)
async def create_category(category: CategoryCreate):
    """
    创建商品分类（管理员功能）

    - category_key: 分类标识（英文，用于关联 mall_items.category）
    - name_en: 英文名称
    - name_zh: 中文名称
    - description: 描述
    - icon: 图标
    - sort_order: 排序
    """
    try:
        data = category.model_dump()
        result = CategoryService.create_category(data)
        return PointsCategorySchema(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/categories/{category_id}", response_model=PointsCategorySchema)
async def update_category(category_id: int, category: CategoryUpdate):
    """
    更新商品分类（管理员功能）

    - category_id: 分类ID
    """
    try:
        data = category.model_dump(exclude_unset=True)
        result = CategoryService.update_category(category_id, data)
        return PointsCategorySchema(**result)
    except ValueError as e:
        raise HTTPException(status_code=404 if "不存在" in str(e) else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int):
    """
    删除商品分类（管理员功能）

    - category_id: 分类ID
    """
    try:
        if not CategoryService.delete_category(category_id):
            raise HTTPException(status_code=404, detail="分类不存在")
        return {"message": "分类删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 购物车 ====================

@router.get("/cart", response_model=List[ShoppingCartItemSchema])
async def get_cart(user_id: int = Query(..., description="用户ID")):
    """
    获取用户购物车

    - user_id: 用户ID
    - 返回购物车中的商品列表，包含库存状态和积分明细
    """
    try:
        items = CartService.get_cart(user_id)
        return [ShoppingCartItemSchema(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cart", response_model=CartResponse)
async def add_to_cart(cart: CartRequest):
    """
    添加到购物车

    - product_id: 商品ID (对应 mall_items.id)
    - user_id: 用户ID
    - quantity: 数量（默认1，最大99）
    - 若商品已在购物车中，则累加数量
    """
    try:
        result = CartService.add_to_cart(cart.user_id, cart.product_id, cart.quantity)
        return CartResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cart/{cart_id}", response_model=CartResponse)
async def update_cart_item(cart_id: int, update: CartItemUpdate):
    """
    更新购物车项数量

    - cart_id: 购物车项ID
    - quantity: 新数量
    """
    try:
        if not CartService.update_cart_item(cart_id, update.quantity):
            raise HTTPException(status_code=404, detail="购物车项不存在")
        return CartResponse(message="购物车已更新")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart/{cart_id}", response_model=CartResponse)
async def remove_from_cart(cart_id: int):
    """
    从购物车移除单项

    - cart_id: 购物车项ID
    """
    try:
        if not CartService.remove_from_cart(cart_id):
            raise HTTPException(status_code=404, detail="购物车项不存在")
        return CartResponse(message="已从购物车移除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart", response_model=CartResponse)
async def clear_cart(user_id: int = Query(..., description="用户ID")):
    """
    清空用户购物车

    - user_id: 用户ID
    """
    try:
        removed = CartService.clear_cart(user_id)
        return CartResponse(message=f"购物车已清空，移除 {removed} 项")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cart/checkout")
async def checkout_cart(user_id: int = Query(..., description="用户ID")):
    """
    购物车一键结算

    批量兑换购物车中所有可兑换商品。

    - user_id: 用户ID
    """
    try:
        result = CartService.checkout_cart(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 积分交易记录 ====================

@router.get("/transactions", response_model=PointsTransactionListResponse)
async def get_point_transactions(
    user_id: int = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    transaction_type: Optional[str] = Query(None, description="交易类型筛选 (sign_in, exchange, purchase, reward, deduction 等)")
):
    """
    获取用户积分交易记录（增强版）

    与 /history 的区别：
    - 包含 transaction_source（交易来源）字段
    - 包含 balance_before（交易前余额）
    - 支持 transaction_type 筛选

    - user_id: 用户ID
    - page: 页码
    - page_size: 每页数量
    - transaction_type: 交易类型筛选
    """
    try:
        result = PointsService.get_transactions(user_id, page, page_size, transaction_type)
        return PointsTransactionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 用户积分统计 ====================

@router.get("/stats/user", response_model=UserPointsStats)
async def get_user_points_stats(
    user_id: int = Query(..., description="用户ID")
):
    """
    获取用户积分统计信息

    包含 余额、总赚取、总支出、等级、经验值、总兑换次数 等。

    - 优先从 user_points 表获取
    - 若 user_points 表无记录则从 users + point_transactions 聚合

    - user_id: 用户ID
    """
    try:
        stats = PointsService.get_user_points_stats(user_id)
        return UserPointsStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 管理员兑换管理 ====================

@router.get("/mall/all-exchanges", response_model=List[ExchangeRecordResponse])
async def get_all_exchanges(
    status: Optional[str] = Query(None, description="状态筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """
    获取所有兑换记录（管理员功能）

    - status: 兑换状态筛选
    - user_id: 用户ID筛选
    - page: 页码
    - limit: 每页数量
    """
    try:
        result = MallService.list_all_exchanges(status, user_id, page, limit)
        return [ExchangeRecordResponse(**record) for record in result['records']]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mall/exchanges/{exchange_id}/status", response_model=ExchangeRecordResponse)
async def update_exchange_status(exchange_id: int, status: str = Query(..., description="新状态 (completed/cancelled/refunded)")):
    """
    更新兑换记录状态（管理员功能）

    - exchange_id: 兑换记录ID
    - status: 新状态
    """
    try:
        result = MallService.update_exchange_status(exchange_id, status)
        return ExchangeRecordResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404 if "不存在" in str(e) else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
