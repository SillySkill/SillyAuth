"""
Promotion Module Schemas
Pydantic models for promotion/coupon/flash sale management

Provides request/response schemas for promotions, coupons, and flash sales
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================
# Enums
# ============================================

class PromotionStatus(str, Enum):
    """Promotion status enumeration."""
    DRAFT = "draft"           # Draft/Not active
    ACTIVE = "active"         # Active and running
    PAUSED = "paused"         # Paused temporarily
    ENDED = "ended"           # Ended naturally
    CANCELLED = "cancelled"   # Cancelled by admin


class PromotionType(str, Enum):
    """Promotion type enumeration."""
    COUPON = "coupon"         # Coupon-based promotion
    DISCOUNT = "discount"     # Direct discount
    FLASH_SALE = "flash_sale" # Flash sale/limited time offer
    BUNDLE = "bundle"         # Bundle deal
    VIP_EXCLUSIVE = "vip_exclusive"  # VIP member exclusive


class CouponType(str, Enum):
    """Coupon type enumeration."""
    FIXED = "fixed"           # Fixed amount discount
    PERCENTAGE = "percentage"  # Percentage discount


class CouponStatus(str, Enum):
    """Coupon status enumeration."""
    ACTIVE = "active"         # Available for use
    USED = "used"             # Already used
    EXPIRED = "expired"       # Expired
    CANCELLED = "cancelled"   # Cancelled


# ============================================
# Promotion Schemas
# ============================================

class PromotionRule(BaseModel):
    """Schema for promotion rule/condition."""
    rule_type: str = Field(..., description="Rule type: min_amount, first_order, category, product")
    rule_value: Any = Field(..., description="Rule value based on rule_type")
    description: Optional[str] = Field(None, description="Human-readable rule description")


class PromotionCreate(BaseModel):
    """Schema for creating a promotion."""
    name: str = Field(..., min_length=1, max_length=200, description="Promotion name")
    description: Optional[str] = Field(None, max_length=500, description="Promotion description")
    promotion_type: PromotionType = Field(..., description="Type of promotion")
    start_time: datetime = Field(..., description="Promotion start time")
    end_time: datetime = Field(..., description="Promotion end time")
    rules: List[PromotionRule] = Field(default_factory=list, description="Promotion rules")
    max_usage: Optional[int] = Field(None, ge=1, description="Maximum total usage count")
    max_usage_per_user: Optional[int] = Field(None, ge=1, description="Maximum usage per user")
    min_order_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum order amount")
    is_active: bool = Field(True, description="Whether promotion is active")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PromotionUpdate(BaseModel):
    """Schema for updating a promotion."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    rules: Optional[List[PromotionRule]] = None
    max_usage: Optional[int] = Field(None, ge=1)
    max_usage_per_user: Optional[int] = Field(None, ge=1)
    min_order_amount: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    status: Optional[PromotionStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class PromotionResponse(BaseModel):
    """Schema for promotion response."""
    id: int
    name: str
    description: Optional[str] = None
    promotion_type: PromotionType
    start_time: datetime
    end_time: datetime
    status: PromotionStatus
    rules: List[PromotionRule] = []
    rules_json: Optional[str] = None
    max_usage: Optional[int] = None
    max_usage_per_user: Optional[int] = None
    min_order_amount: Optional[Decimal] = None
    current_usage: int = 0
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PromotionListResponse(BaseModel):
    """Schema for paginated promotion list response."""
    items: List[PromotionResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============================================
# Coupon Schemas
# ============================================

class CouponCreate(BaseModel):
    """Schema for creating a coupon."""
    promotion_id: Optional[int] = Field(None, description="Associated promotion ID")
    code: Optional[str] = Field(None, min_length=4, max_length=50, description="Coupon code (auto-generated if not provided)")
    coupon_type: CouponType = Field(..., description="Type of coupon: fixed or percentage")
    value: Decimal = Field(..., gt=0, description="Discount value (amount or percentage)")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum order amount to apply coupon")
    max_discount: Optional[Decimal] = Field(None, ge=0, description="Maximum discount cap for percentage coupons")
    total_count: int = Field(..., ge=1, description="Total number of coupons available")
    valid_start: datetime = Field(..., description="Coupon validity start time")
    valid_end: datetime = Field(..., description="Coupon validity end time")
    user_id: Optional[int] = Field(None, description="Specific user ID (NULL for universal coupons)")
    is_transferable: bool = Field(False, description="Whether coupon can be transferred")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator('valid_end')
    @classmethod
    def valid_end_after_start(cls, v: datetime, info) -> datetime:
        """Validate end time is after start time."""
        if 'valid_start' in info.data and v <= info.data['valid_start']:
            raise ValueError('Valid end time must be after start time')
        return v


class CouponResponse(BaseModel):
    """Schema for coupon response."""
    id: int
    promotion_id: Optional[int] = None
    code: str
    coupon_type: CouponType
    value: Decimal
    min_amount: Optional[Decimal] = None
    max_discount: Optional[Decimal] = None
    total_count: int
    used_count: int = 0
    user_id: Optional[int] = None
    valid_start: datetime
    valid_end: datetime
    status: CouponStatus
    is_transferable: bool = False
    remaining_count: int = 0
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponValidateRequest(BaseModel):
    """Schema for coupon validation request."""
    code: str = Field(..., min_length=1, description="Coupon code")
    order_amount: Optional[Decimal] = Field(None, ge=0, description="Order amount for validation")
    user_id: Optional[int] = Field(None, description="User ID for user-specific validation")


class CouponValidateResponse(BaseModel):
    """Schema for coupon validation response."""
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: Optional[Decimal] = None
    message: str


# ============================================
# Flash Sale Schemas
# ============================================

class FlashSaleCreate(BaseModel):
    """Schema for creating a flash sale item."""
    promotion_id: Optional[int] = Field(None, description="Associated promotion ID")
    product_id: int = Field(..., description="Product ID for flash sale")
    product_name: Optional[str] = Field(None, description="Product name (for display)")
    flash_price: Decimal = Field(..., gt=0, description="Flash sale price")
    original_price: Optional[Decimal] = Field(None, description="Original price for comparison")
    stock: int = Field(..., ge=0, description="Stock quantity")
    sold_count: int = Field(0, description="Already sold count")
    max_per_user: int = Field(1, ge=1, description="Maximum quantity per user")
    start_time: datetime = Field(..., description="Flash sale start time")
    end_time: datetime = Field(..., description="Flash sale end time")
    is_active: bool = Field(True, description="Whether flash sale is active")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator('flash_price')
    @classmethod
    def flash_price_less_than_original(cls, v: Decimal, info) -> Decimal:
        """Validate flash price is less than original price."""
        if 'original_price' in info.data and info.data['original_price'] is not None:
            if v >= info.data['original_price']:
                raise ValueError('Flash sale price must be less than original price')
        return v

    @field_validator('end_time')
    @classmethod
    def end_time_after_start(cls, v: datetime, info) -> datetime:
        """Validate end time is after start time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v


class FlashSaleResponse(BaseModel):
    """Schema for flash sale response."""
    id: int
    promotion_id: Optional[int] = None
    product_id: int
    product_name: Optional[str] = None
    flash_price: Decimal
    original_price: Optional[Decimal] = None
    discount_rate: Optional[float] = None
    stock: int
    sold_count: int = 0
    remaining_stock: int = 0
    max_per_user: int = 1
    start_time: datetime
    end_time: datetime
    is_active: bool = True
    is_ongoing: bool = False
    is_sold_out: bool = False
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlashSaleListResponse(BaseModel):
    """Schema for paginated flash sale list response."""
    items: List[FlashSaleResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============================================
# Coupon Usage Schemas
# ============================================

class CouponUsageResponse(BaseModel):
    """Schema for coupon usage history response."""
    id: int
    coupon_id: int
    coupon_code: Optional[str] = None
    user_id: int
    order_id: Optional[str] = None
    discount_amount: Optional[Decimal] = None
    used_at: datetime

    class Config:
        from_attributes = True


class CouponUsageListResponse(BaseModel):
    """Schema for paginated coupon usage list response."""
    items: List[CouponUsageResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============================================
# Order Item Schemas
# ============================================

class OrderItemForDiscount(BaseModel):
    """Schema for order item when calculating discount."""
    product_id: int
    quantity: int = 1
    price: Decimal
    subtotal: Decimal


class DiscountCalculationRequest(BaseModel):
    """Schema for discount calculation request."""
    coupon_code: str = Field(..., description="Coupon code")
    order_items: List[OrderItemForDiscount] = Field(..., description="Order items")
    user_id: Optional[int] = Field(None, description="User ID")


class DiscountCalculationResponse(BaseModel):
    """Schema for discount calculation response."""
    original_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    coupon_code: str
    coupon_type: CouponType
    coupon_value: Decimal
    savings: Decimal


# ============================================
# Response Wrappers
# ============================================

class PromotionResponseModel(BaseModel):
    """Generic response wrapper for promotion module."""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
