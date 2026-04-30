"""
Store 数据模型定义
多产品线商城模块的数据模型

提供产品集合、产品、购物车、订单、支付等数据模型
"""
from __future__ import annotations

from typing import Optional, List, Any
from datetime import datetime

from pydantic import BaseModel, Field


# ==================== Core Data Models ====================

class StoreCollection(BaseModel):
    """商城产品集合"""
    id: Optional[int] = None
    collection_key: str
    name_zh: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    theme_config: Optional[dict] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StoreProduct(BaseModel):
    """商城产品"""
    id: Optional[int] = None
    collection_id: int
    product_key: str
    name_zh: str
    name_en: Optional[str] = None
    description_zh: Optional[str] = None
    description_en: Optional[str] = None
    image_url: Optional[str] = None
    gallery: Optional[List[str]] = []
    price: float
    original_price: Optional[float] = None
    stock_count: int = -1
    sold_count: int = 0
    specifications: Optional[dict] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StoreProductDetail(StoreProduct):
    """产品详情（含集合名称与库存可用状态）"""
    collection_name: Optional[str] = None
    available: Optional[bool] = None


class StoreCartItem(BaseModel):
    """购物车项"""
    id: Optional[int] = None
    user_id: int
    collection_id: int
    product_id: int
    quantity: int = 1
    product_key: Optional[str] = None
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    price: Optional[float] = None
    total_price: Optional[float] = None
    stock_available: bool = True

    model_config = {"from_attributes": True}


class StoreOrder(BaseModel):
    """商城订单"""
    id: Optional[int] = None
    order_no: str
    user_id: int
    collection_id: int
    total_amount: float
    status: str = "pending"
    payment_method: Optional[str] = None
    payment_no: Optional[str] = None
    shipping_name: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StoreOrderItem(BaseModel):
    """订单项"""
    id: Optional[int] = None
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


# ==================== Request Models ====================

class CartAddRequest(BaseModel):
    """添加到购物车请求"""
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class CartUpdateRequest(BaseModel):
    """更新购物车请求"""
    quantity: int = Field(..., ge=1, le=99)


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    shipping_name: str = Field(..., min_length=1, max_length=100)
    shipping_phone: str = Field(..., min_length=1, max_length=20)
    shipping_address: str = Field(..., min_length=1, max_length=500)


class PaymentRequest(BaseModel):
    """支付请求"""
    payment_method: str = Field(..., description="支付方式: wechat, alipay")


# ==================== Admin Request Models ====================

class StoreCollectionCreate(BaseModel):
    """创建商城集合请求"""
    collection_key: Optional[str] = Field(None, max_length=50, description="集合标识键，不提供则自动生成")
    name_zh: str = Field(..., min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    theme_config: Optional[dict] = None
    is_active: bool = True
    sort_order: int = 0


class StoreCollectionUpdate(BaseModel):
    """更新商城集合请求"""
    collection_key: Optional[str] = Field(None, max_length=50)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    theme_config: Optional[dict] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class StoreProductCreate(BaseModel):
    """创建商城产品请求"""
    collection_id: int = Field(..., description="所属集合ID")
    product_key: Optional[str] = Field(None, max_length=50, description="产品标识键，不提供则自动生成")
    name_zh: str = Field(..., min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description_zh: Optional[str] = Field(None, max_length=2000)
    description_en: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=500)
    gallery: Optional[List[str]] = Field(default_factory=list)
    price: float = Field(..., ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    stock_count: int = Field(-1, ge=-1, description="库存，-1表示无限")
    specifications: Optional[dict] = None
    is_active: bool = True
    sort_order: int = 0


class StoreProductUpdate(BaseModel):
    """更新商城产品请求"""
    collection_id: Optional[int] = None
    product_key: Optional[str] = Field(None, max_length=50)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description_zh: Optional[str] = Field(None, max_length=2000)
    description_en: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=500)
    gallery: Optional[List[str]] = None
    price: Optional[float] = Field(None, ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    stock_count: Optional[int] = Field(None, ge=-1)
    specifications: Optional[dict] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class OrderStatusUpdate(BaseModel):
    """更新订单状态请求"""
    status: str = Field(..., description="新状态: pending, paid, shipped, completed, cancelled")
    reason: Optional[str] = Field(None, max_length=500)


# ==================== Response/List Models ====================

class StoreProductListResponse(BaseModel):
    """产品列表响应（含分页）"""
    items: List[StoreProductDetail]
    total: int
    page: int
    page_size: int
    total_pages: int


class StoreCollectionListResponse(BaseModel):
    """集合列表响应（含分页）"""
    items: List[StoreCollection]
    total: int
    page: int
    page_size: int
    total_pages: int


class StoreOrderDetailResponse(BaseModel):
    """订单详情响应（含订单项）"""
    order: StoreOrder
    items: List[StoreOrderItem]


class StoreOrderListResponse(BaseModel):
    """订单列表响应（含分页）"""
    items: List[StoreOrder]
    total: int
    page: int
    page_size: int
    total_pages: int


class StoreStats(BaseModel):
    """商城统计信息"""
    total_collections: int
    active_collections: int
    total_products: int
    active_products: int
    total_orders: int
    pending_orders: int
    total_revenue: float


class CollectionStats(BaseModel):
    """集合统计信息"""
    product_count: int
    order_count: int
    total_sales: float


# ==================== Payment/Callback Models ====================

class PaymentResponse(BaseModel):
    """支付响应"""
    success: bool
    order_no: str
    payment_method: str
    amount: float
    code_url: Optional[str] = None
    prepay_id: Optional[str] = None
    qr_code: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    """支付状态响应"""
    order_no: str
    status: str
    payment_no: Optional[str] = None
    payment_method: Optional[str] = None
    paid: bool


class CreateOrderResponse(BaseModel):
    """创建订单响应"""
    message: str
    order_no: str
    total_amount: float
    order_id: int
