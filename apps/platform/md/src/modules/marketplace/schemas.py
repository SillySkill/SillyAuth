"""
Marketplace Module Schemas
Pydantic models for marketplace listings and purchases

Provides listing creation, purchase request/response schemas
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ListingStatus(str, Enum):
    """Listing status enumeration."""
    ACTIVE = "active"           # Active and available for purchase
    SOLD_OUT = "sold_out"       # Stock depleted
    INACTIVE = "inactive"       # Manually deactivated by vendor
    EXPIRED = "expired"         # Listing expired
    REMOVED = "removed"         # Removed by admin


class PurchaseStatus(str, Enum):
    """Purchase status enumeration."""
    PENDING = "pending"         # Awaiting payment
    PAID = "paid"               # Payment received
    PROCESSING = "processing"   # Being processed/fulfilled
    SHIPPED = "shipped"         # Shipped/delivered
    COMPLETED = "completed"     # Transaction completed
    CANCELLED = "cancelled"     # Cancelled
    REFUNDED = "refunded"       # Refunded


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    BALANCE = "balance"         # Platform balance
    ALIPAY = "alipay"           # Alipay
    WECHAT = "wechat"           # WeChat Pay
    CARD = "card"              # Credit/Debit Card
    BANK = "bank"              # Bank Transfer


# ============================================
# Listing Schemas
# ============================================

class ListingCreate(BaseModel):
    """Schema for creating a marketplace listing."""
    product_id: int = Field(..., description="Product ID to list")
    price: Decimal = Field(..., ge=0, description="Listing price")
    quantity: int = Field(..., ge=0, description="Available quantity")
    min_quantity: int = Field(1, ge=1, description="Minimum purchase quantity")
    max_quantity: Optional[int] = Field(None, ge=1, description="Maximum purchase quantity per order")
    description: Optional[str] = Field(None, max_length=2000, description="Additional listing description")
    start_time: Optional[datetime] = Field(None, description="Listing start time")
    end_time: Optional[datetime] = Field(None, description="Listing end time (auto-expire)")
    is_featured: bool = Field(False, description="Feature this listing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ListingUpdate(BaseModel):
    """Schema for updating a listing."""
    price: Optional[Decimal] = Field(None, ge=0, description="Listing price")
    quantity: Optional[int] = Field(None, ge=0, description="Available quantity")
    min_quantity: Optional[int] = Field(None, ge=1, description="Minimum purchase quantity")
    max_quantity: Optional[int] = Field(None, ge=1, description="Maximum purchase quantity")
    description: Optional[str] = Field(None, max_length=2000, description="Additional description")
    start_time: Optional[datetime] = Field(None, description="Listing start time")
    end_time: Optional[datetime] = Field(None, description="Listing end time")
    is_featured: Optional[bool] = Field(None, description="Feature this listing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ListingResponse(BaseModel):
    """Schema for listing response."""
    id: int
    product_id: int
    vendor_id: int
    vendor_name: Optional[str] = None
    product_name: str
    product_slug: str
    product_images: List[Dict[str, Any]] = Field(default_factory=list)
    price: Decimal
    original_price: Optional[Decimal] = None
    currency: str
    quantity: int
    sold_quantity: int = 0
    available_quantity: int = 0
    min_quantity: int = 1
    max_quantity: Optional[int] = None
    description: Optional[str] = None
    status: ListingStatus
    is_featured: bool = False
    rating: float = 0.0
    review_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ListingListResponse(BaseModel):
    """Schema for paginated listing response."""
    items: List[ListingResponse]
    total: int
    page: int
    limit: int
    pages: int


class ListingSearchQuery(BaseModel):
    """Schema for listing search query."""
    keyword: Optional[str] = Field(None, description="Search keyword")
    category_id: Optional[int] = Field(None, description="Filter by category")
    vendor_id: Optional[int] = Field(None, description="Filter by vendor")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    sort_by: str = Field("created_at", description="Sort: created_at, price, sales, rating")
    sort_order: str = Field("desc", description="Sort order: asc, desc")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


# ============================================
# Purchase Schemas
# ============================================

class PurchaseItem(BaseModel):
    """Schema for purchase item."""
    listing_id: int = Field(..., description="Listing ID")
    quantity: int = Field(..., ge=1, description="Purchase quantity")
    price: Decimal = Field(..., description="Price at time of purchase")


class PurchaseRequest(BaseModel):
    """Schema for creating a purchase."""
    items: List[PurchaseItem] = Field(..., min_length=1, description="Purchase items")
    payment_method: PaymentMethod = Field(PaymentMethod.BALANCE, description="Payment method")
    coupon_code: Optional[str] = Field(None, description="Coupon code to apply")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    shipping_address: Optional[Dict[str, Any]] = Field(None, description="Shipping address for physical goods")

    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[PurchaseItem]) -> List[PurchaseItem]:
        """Validate purchase items."""
        if not v:
            raise ValueError('At least one item is required')
        return v


class PurchaseResponse(BaseModel):
    """Schema for purchase response."""
    id: int
    order_id: str
    buyer_id: int
    items: List[PurchaseItem]
    subtotal: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    shipping_amount: Decimal = Decimal("0")
    total_amount: Decimal
    currency: str
    payment_method: PaymentMethod
    payment_status: str
    purchase_status: PurchaseStatus
    coupon_code: Optional[str] = None
    notes: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseListResponse(BaseModel):
    """Schema for paginated purchase list response."""
    items: List[PurchaseResponse]
    total: int
    page: int
    limit: int
    pages: int


class PurchaseStatusUpdate(BaseModel):
    """Schema for updating purchase status."""
    status: PurchaseStatus


# ============================================
# Review Schemas
# ============================================

class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    listing_id: int = Field(..., description="Listing ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    title: Optional[str] = Field(None, max_length=100, description="Review title")
    content: Optional[str] = Field(None, max_length=2000, description="Review content")
    images: List[str] = Field(default_factory=list, description="Review image URLs")
    attributes: Optional[Dict[str, str]] = Field(None, description="Attribute ratings")


class ReviewResponse(BaseModel):
    """Schema for review response."""
    id: int
    purchase_id: int
    listing_id: int
    buyer_id: int
    buyer_name: Optional[str] = None
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    images: List[str] = []
    attributes: Optional[Dict[str, str]] = None
    is_verified: bool = False
    helpful_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Statistics Schemas
# ============================================

class MarketplaceStats(BaseModel):
    """Schema for marketplace statistics."""
    total_listings: int = 0
    active_listings: int = 0
    total_products: int = 0
    total_vendors: int = 0
    total_purchases: int = 0
    total_revenue: Decimal = Decimal("0")
    total_orders: int = 0
    average_rating: float = 0.0


class VendorSalesStats(BaseModel):
    """Schema for vendor sales statistics."""
    vendor_id: int
    total_sales: int = 0
    total_revenue: Decimal = Decimal("0")
    total_orders: int = 0
    average_order_value: Decimal = Decimal("0")
    best_selling_listing_id: Optional[int] = None
    top_category_id: Optional[int] = None


# ============================================
# Response Wrappers
# ============================================

class MarketplaceResponse(BaseModel):
    """Generic response wrapper for marketplace module."""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
