"""
Transaction module schemas for SillyMD.

This module provides Pydantic schemas for order management,
settlement processing, and refund handling.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "PENDING"       # Pending payment
    PAID = "PAID"           # Payment received
    PROCESSING = "PROCESSING"  # Being processed
    SHIPPED = "SHIPPED"     # Shipped
    DELIVERED = "DELIVERED" # Delivered
    COMPLETED = "COMPLETED"  # Transaction completed
    CANCELLED = "CANCELLED"  # Cancelled
    REFUNDED = "REFUNDED"    # Refunded
    PARTIAL_REFUND = "PARTIAL_REFUND"  # Partially refunded


class SettlementStatus(str, Enum):
    """Settlement status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RefundStatus(str, Enum):
    """Refund status enumeration."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSED = "PROCESSED"


class OrderItem(BaseModel):
    """Order item schema."""
    product_id: str
    name: str
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    subtotal: Decimal = Field(..., ge=0)


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    items: List[OrderItem] = Field(..., min_length=1)
    total_amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="CNY", max_length=3)
    metadata: Optional[Dict[str, Any]] = None


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: str
    user_id: str
    items: List[OrderItem]
    status: OrderStatus
    total_amount: Decimal
    currency: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class SettlementCreate(BaseModel):
    """Schema for creating a settlement request."""
    vendor_id: str
    amount: Decimal = Field(..., ge=0)
    period: str = Field(..., description="Settlement period, e.g., '2024-01'")


class SettlementResponse(BaseModel):
    """Schema for settlement response."""
    id: str
    vendor_id: str
    amount: Decimal
    status: SettlementStatus
    period: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SettlementProcess(BaseModel):
    """Schema for processing a settlement."""
    settlement_id: str


class RefundItem(BaseModel):
    """Schema for refund item."""
    product_id: str
    quantity: int = Field(..., gt=0)


class RefundRequest(BaseModel):
    """Schema for creating a refund request."""
    order_id: str
    amount: Decimal = Field(..., ge=0)
    reason: str = Field(..., min_length=1)
    items: Optional[List[RefundItem]] = None


class RefundResponse(BaseModel):
    """Schema for refund response."""
    id: str
    order_id: str
    amount: Decimal
    status: RefundStatus
    reason: str
    items: Optional[List[RefundItem]] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True


class RefundReject(BaseModel):
    """Schema for rejecting a refund."""
    refund_id: str
    reason: str = Field(..., min_length=1)


class PaginatedOrdersResponse(BaseModel):
    """Paginated orders response."""
    items: List[OrderResponse]
    total: int
    page: int
    limit: int
    pages: int


class PaginatedSettlementsResponse(BaseModel):
    """Paginated settlements response."""
    items: List[SettlementResponse]
    total: int
    page: int
    limit: int
    pages: int


class PaginatedRefundsResponse(BaseModel):
    """Paginated refunds response."""
    items: List[RefundResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============================================
# Admin Order Schemas
# ============================================

class AdminOrderStatus(str, Enum):
    """Admin order status enumeration."""
    PENDING = "pending"           # Pending payment
    PAID = "paid"               # Payment received
    PROCESSING = "processing"    # Being processed
    SHIPPED = "shipped"         # Shipped
    DELIVERED = "delivered"      # Delivered
    COMPLETED = "completed"      # Completed
    CANCELLED = "cancelled"      # Cancelled
    REFUNDED = "refunded"        # Refunded
    PARTIAL_REFUND = "partial_refund"  # Partially refunded


class AdminPaymentMethod(str, Enum):
    """Admin payment method enumeration."""
    BALANCE = "balance"         # Platform balance
    ALIPAY = "alipay"           # Alipay
    WECHAT = "wechat"           # WeChat Pay
    CARD = "card"              # Credit/Debit Card
    BANK = "bank"              # Bank Transfer


class AdminExpressCompany(str, Enum):
    """Express company enumeration."""
    SF = "sf"                  # SF Express
    YTO = "yto"                # YTO Express
    ZTO = "zto"                # ZTO Express
    ZJS = "zjs"                # ZJS Express
    EMS = "ems"                # EMS
    JD = "jd"                  # JD Logistics
    YT = "yt"                  # YTO
    OTHER = "other"            # Other


class ShippingAddress(BaseModel):
    """Shipping address schema."""
    receiver_name: str = Field(..., description="Receiver name")
    phone: str = Field(..., description="Receiver phone")
    province: str = Field(..., description="Province")
    city: str = Field(..., description="City")
    district: str = Field(..., description="District")
    address: str = Field(..., description="Detailed address")
    postal_code: Optional[str] = Field(None, description="Postal code")


class AdminOrderItem(BaseModel):
    """Admin order item schema."""
    id: str
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    sku: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class AdminOrderResponse(BaseModel):
    """Admin order response schema."""
    id: str
    order_no: str
    user_id: str
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    items: List[AdminOrderItem]
    total_amount: Decimal
    discount_amount: Decimal = Decimal("0")
    shipping_amount: Decimal = Decimal("0")
    final_amount: Decimal
    status: AdminOrderStatus
    shipping_address: Optional[Dict[str, Any]] = None
    tracking_number: Optional[str] = None
    express_company: Optional[str] = None
    payment_method: Optional[AdminPaymentMethod] = None
    payment_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminOrderListResponse(BaseModel):
    """Admin order list response schema."""
    items: List[AdminOrderResponse]
    total: int
    page: int
    limit: int
    pages: int


class AdminOrderFilters(BaseModel):
    """Admin order filters schema."""
    status: Optional[AdminOrderStatus] = None
    payment_method: Optional[AdminPaymentMethod] = None
    express_company: Optional[AdminExpressCompany] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None  # Search: order_no, receiver_name, phone
    vendor_id: Optional[str] = None


class UpdateOrderStatusRequest(BaseModel):
    """Update order status request schema."""
    status: AdminOrderStatus
    remark: Optional[str] = None


class ShipOrderRequest(BaseModel):
    """Ship order request schema."""
    tracking_number: str = Field(..., description="Tracking number")
    express_company: str = Field(..., description="Express company code")
    remark: Optional[str] = None


class BatchShipOrderRequest(BaseModel):
    """Batch ship order request schema."""
    order_ids: List[str] = Field(..., min_length=1, description="Order IDs to ship")
    tracking_number: str = Field(..., description="Tracking number")
    express_company: str = Field(..., description="Express company code")
    remark: Optional[str] = None


class RefundOrderRequest(BaseModel):
    """Refund order request schema."""
    reason: str = Field(..., description="Refund reason")
    refund_amount: Optional[Decimal] = Field(None, description="Refund amount (full if not specified)")
    remark: Optional[str] = None


class AdminOrderStats(BaseModel):
    """Admin order statistics schema."""
    total_orders: int = 0
    pending_orders: int = 0
    paid_orders: int = 0
    shipped_orders: int = 0
    delivered_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    refunded_orders: int = 0
    total_amount: Decimal = Decimal("0")
    total_revenue: Decimal = Decimal("0")
    total_refunds: Decimal = Decimal("0")
