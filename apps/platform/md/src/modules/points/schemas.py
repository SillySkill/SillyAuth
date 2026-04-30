"""
积分商城数据模型
定义积分系统相关的Pydantic模型 (Pydantic v2)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PointsType(str, Enum):
    """积分类型枚举"""
    SIGN_IN = "sign_in"           # 签到获得
    PURCHASE = "purchase"          # 购买获得
    REFERRAL = "referral"          # 推荐获得
    REWARD = "reward"              # 奖励获得
    EXCHANGE = "exchange"          # 兑换消耗
    GIFT = "gift"                  # 礼物消耗
    DEDUCTION = "deduction"        # 扣减


# ==================== 积分余额与记录 ====================

class PointsRecord(BaseModel):
    """积分记录"""
    id: int
    user_id: int
    amount: int
    type: str  # PointsType
    description: str
    balance_after: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PointsBalance(BaseModel):
    """积分余额"""
    user_id: int
    username: Optional[str] = None
    balance: int
    total_earned: int = 0
    total_spent: int = 0
    level: Optional[int] = 1
    experience: Optional[int] = 0

    model_config = {"from_attributes": True}


class PointsExchange(BaseModel):
    """积分兑换配置"""
    item_id: int
    points_cost: int
    quantity: int = Field(default=1, ge=1)


class PointsHistoryResponse(BaseModel):
    """积分历史响应"""
    records: List[PointsRecord]
    total: int
    page: int
    limit: int


# ==================== 积分交易记录 ====================

class PointsTransactionResponse(BaseModel):
    """积分交易记录响应（带来源）"""
    id: int
    user_id: int
    transaction_type: Optional[str] = None
    transaction_source: Optional[str] = None
    amount: int
    balance_before: Optional[int] = None
    balance_after: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PointsTransactionListResponse(BaseModel):
    """积分交易记录列表响应"""
    items: List[PointsTransactionResponse]
    total: int
    page: int
    page_size: int


# ==================== 商城商品 ====================

class MallItemCreate(BaseModel):
    """创建商城商品"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    points_cost: int = Field(..., ge=0)
    stock: int = Field(default=-1, ge=-1, description="-1表示无限库存")
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_featured: bool = False
    sort_order: int = 0
    valid_days: Optional[int] = None


class MallItemUpdate(BaseModel):
    """更新商城商品"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    points_cost: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=-1)
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class MallItemResponse(BaseModel):
    """商城商品响应"""
    id: int
    name: str
    description: Optional[str] = None
    points_cost: int
    stock: int
    stock_available: bool = True
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_featured: bool = False
    is_active: bool = True
    sort_order: int = 0
    valid_days: Optional[int] = None
    sold_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ==================== 兑换 ====================

class ExchangeRecordResponse(BaseModel):
    """兑换记录响应"""
    id: int
    exchange_no: str
    user_id: int
    item_id: int
    item_name: str
    points_used: int
    quantity: int
    status: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class SignInResponse(BaseModel):
    """签到响应"""
    success: bool
    points_earned: int
    current_balance: int
    sign_in_count: int
    message: str


class ExchangeRequest(BaseModel):
    """兑换请求"""
    item_id: int
    quantity: int = Field(default=1, ge=1, le=10)


class ExchangeResponse(BaseModel):
    """兑换响应"""
    success: bool
    exchange_no: str
    points_used: int
    remaining_balance: int
    message: str


# ==================== 商品分类 ====================

class PointsCategorySchema(BaseModel):
    """积分商品分类"""
    id: int
    category_key: str
    name_en: str
    name_zh: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    """创建分类请求"""
    category_key: str = Field(..., min_length=1, max_length=50)
    name_en: str = Field(..., min_length=1, max_length=200)
    name_zh: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ==================== 购物车 ====================

class ShoppingCartItemSchema(BaseModel):
    """购物车项"""
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    points_required: int = 0
    total_points: int = 0
    stock_available: bool = True

    model_config = {"from_attributes": True}


class CartRequest(BaseModel):
    """购物车请求"""
    product_id: int
    user_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemUpdate(BaseModel):
    """购物车项更新"""
    quantity: int = Field(..., ge=1, le=99)


class CartResponse(BaseModel):
    """购物车响应消息"""
    message: str
    cart_id: Optional[int] = None


# ==================== 用户积分统计 ====================

class UserPointsStats(BaseModel):
    """用户积分统计"""
    user_id: int
    balance: int = 0
    total_earned: int = 0
    total_spent: int = 0
    level: int = 1
    experience: int = 0
    total_exchanges: int = 0
    total_points_used: int = 0

    model_config = {"from_attributes": True}


# ==================== 商城统计 ====================

class MallStats(BaseModel):
    """商城统计"""
    total_items: int
    active_items: int
    total_exchanges: int
    total_points_spent: int
    today_exchanges: int
