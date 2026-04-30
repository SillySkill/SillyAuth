"""
Logistics Module Schemas
Pydantic models for logistics management

Provides express companies, shipping templates, tracking info, and shipping calculation
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================

class ExpressCompanyStatus(str, Enum):
    """Express company status."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ShippingTemplateType(str, Enum):
    """Shipping template type."""
    BY_WEIGHT = "by_weight"    # 按重量计费
    BY_PIECE = "by_piece"      # 按件数计费


class LogisticsStatus(str, Enum):
    """Logistics tracking status."""
    PENDING = "pending"           # 待发货
    IN_TRANSIT = "in_transit"    # 运输中
    DELIVERED = "delivered"      # 已签收
    EXCEPTION = "exception"       # 异常
    RETURNED = "returned"        # 退件
    UNKNOWN = "unknown"          # 未知状态


class ShippingCalculateType(str, Enum):
    """Shipping calculation type."""
    EXPRESS = "express"           # 快递
    ECONOMIC = "economic"         # 经济快递


# ============================================
# Express Company Schemas
# ============================================

class ExpressCompanyResponse(BaseModel):
    """Schema for express company response."""
    id: int
    code: str
    name: str
    logo_url: Optional[str] = None
    tracking_url: Optional[str] = None
    status: ExpressCompanyStatus
    sort_order: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Shipping Template Schemas
# ============================================

class ShippingTemplateRule(BaseModel):
    """Schema for shipping template rule."""
    id: int
    template_id: int
    region_ids: List[int] = Field(default_factory=list)
    region_names: List[str] = Field(default_factory=list, description="地区名称列表")
    first_unit: float = Field(1.0, description="首重/首件")
    first_fee: Decimal = Field(..., description="首重/首件费用")
    continue_unit: float = Field(1.0, description="续重/续件")
    continue_fee: Decimal = Field(..., description="续重/续件费用")


class ShippingTemplateCreate(BaseModel):
    """Schema for creating shipping template."""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    template_type: ShippingTemplateType = Field(..., description="模板类型")
    is_free_shipping: bool = Field(False, description="是否包邮")
    default_fee: Optional[Decimal] = Field(None, description="默认运费(包邮时使用)")


class ShippingTemplateUpdate(BaseModel):
    """Schema for updating shipping template."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    template_type: Optional[ShippingTemplateType] = None
    is_free_shipping: Optional[bool] = None
    default_fee: Optional[Decimal] = None


class ShippingTemplateResponse(BaseModel):
    """Schema for shipping template response."""
    id: int
    name: str
    template_type: ShippingTemplateType
    is_free_shipping: bool
    default_fee: Optional[Decimal] = None
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShippingTemplateDetailResponse(ShippingTemplateResponse):
    """Schema for shipping template detail with rules."""
    rules: List[ShippingTemplateRule] = Field(default_factory=list)


# ============================================
# Shipping Calculation Schemas
# ============================================

class OrderItem(BaseModel):
    """Schema for order item in shipping calculation."""
    product_id: int
    product_name: str
    quantity: int = Field(..., ge=1)
    weight: float = Field(..., ge=0, description="重量(kg)")
    price: Optional[Decimal] = None


class ShippingAddress(BaseModel):
    """Schema for shipping address."""
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: Optional[str] = Field(None, description="区县")
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    postal_code: Optional[str] = None


class ShippingCalculateRequest(BaseModel):
    """Schema for shipping calculation request."""
    items: List[OrderItem] = Field(..., min_length=1, description="订单商品列表")
    address: ShippingAddress = Field(..., description="收货地址")
    express_company: Optional[str] = Field(None, description="指定快递公司代码")
    calculate_type: ShippingCalculateType = Field(ShippingCalculateType.EXPRESS, description="计算类型")


class ShippingOption(BaseModel):
    """Schema for a single shipping option."""
    express_company_code: str
    express_company_name: str
    express_company_logo: Optional[str] = None
    fee: Decimal = Field(..., description="运费")
    estimated_days: Optional[str] = Field(None, description="预计送达天数")
    is_free: bool = Field(False, description="是否包邮")
    is_recommend: bool = Field(False, description="是否推荐")


class ShippingCalculateResponse(BaseModel):
    """Schema for shipping calculation response."""
    total_weight: float = Field(..., description="总重量(kg)")
    free_shipping_threshold: Decimal = Field(..., description="包邮门槛")
    is_free_shipping: bool = Field(False, description="是否满足包邮条件")
    options: List[ShippingOption] = Field(default_factory=list, description="可选快递方案")


# ============================================
# Tracking Schemas
# ============================================

class TrackingTrace(BaseModel):
    """Schema for tracking trace record."""
    time: str = Field(..., description="时间")
    status: str = Field(..., description="状态")
    location: Optional[str] = Field(None, description="地点")
    description: Optional[str] = None


class TrackingInfo(BaseModel):
    """Schema for tracking information."""
    express_company: str
    express_company_name: str
    tracking_number: str
    status: LogisticsStatus
    status_text: str
    traces: List[TrackingTrace] = Field(default_factory=list)
    last_update: Optional[datetime] = None
    estimated_delivery: Optional[str] = None


class TrackingResponse(BaseModel):
    """Schema for tracking response."""
    success: bool = True
    message: str = "查询成功"
    data: Optional[TrackingInfo] = None


# ============================================
# Express Label Schemas
# ============================================

class ExpressLabelRequest(BaseModel):
    """Schema for express label request."""
    order_id: int = Field(..., description="订单ID")
    express_company: str = Field(..., description="快递公司代码")
    sender_name: str = Field(..., description="发件人姓名")
    sender_phone: str = Field(..., description="发件人电话")
    sender_address: str = Field(..., description="发件人地址")
    receiver_name: str = Field(..., description="收件人姓名")
    receiver_phone: str = Field(..., description="收件人电话")
    receiver_address: str = Field(..., description="收件人地址")
    goods_name: Optional[str] = Field(None, description="物品名称")
    goods_weight: Optional[float] = Field(None, description="物品重量(kg)")


class ExpressLabelData(BaseModel):
    """Schema for express label data."""
    order_id: int
    express_company: str
    express_company_name: str
    tracking_number: str
    sender: Dict[str, str]
    receiver: Dict[str, str]
    goods_name: Optional[str] = None
    goods_weight: Optional[float] = None
    created_at: datetime
    label_url: Optional[str] = None  # 电子面单URL


class ExpressLabelResponse(BaseModel):
    """Schema for express label response."""
    success: bool = True
    message: str = "面单生成成功"
    data: Optional[ExpressLabelData] = None


# ============================================
# Region Schemas
# ============================================

class RegionResponse(BaseModel):
    """Schema for region response."""
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int = Field(..., description="层级: 1-省, 2-市, 3-区")
    code: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# Generic Response
# ============================================

class LogisticsResponse(BaseModel):
    """Generic response wrapper for logistics module."""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
