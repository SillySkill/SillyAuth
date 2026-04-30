"""
分销系统数据模型
定义分销相关的Pydantic模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, date
from enum import Enum


class StaffStatus(str, Enum):
    """员工状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class LinkStatus(str, Enum):
    """链接状态枚举"""
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待确认
    CONFIRMED = "confirmed"  # 已确认
    CANCELLED = "cancelled"  # 已取消


class CommissionStatus(str, Enum):
    """佣金状态枚举"""
    PENDING = "pending"      # 待结算
    CONFIRMED = "confirmed"  # 已确认
    PAID = "paid"           # 已支付
    CANCELLED = "cancelled"  # 已取消


# ==================== 员工相关模型 ====================

class StaffCreate(BaseModel):
    """创建分销员工"""
    user_id: int = Field(..., description="关联的用户ID")
    staff_name: str = Field(..., min_length=1, max_length=100, description="员工姓名")
    staff_code: Optional[str] = Field(None, max_length=50, description="员工编码（自动生成）")


class StaffUpdate(BaseModel):
    """更新分销员工"""
    staff_name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[StaffStatus] = None


class StaffResponse(BaseModel):
    """分销员工响应"""
    id: int
    user_id: int
    staff_code: str
    staff_name: str
    total_sales: float = 0
    total_orders: int = 0
    total_commission: float = 0
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StaffStats(BaseModel):
    """员工统计数据"""
    staff_id: int
    staff_code: str
    staff_name: str
    total_sales: float
    total_orders: int
    total_commission: float
    pending_commission: float
    paid_commission: float
    click_count: int
    conversion_rate: float
    today_sales: float
    today_orders: int
    this_week_sales: float
    this_month_sales: float


# ==================== 分享链接相关模型 ====================

class LinkCreate(BaseModel):
    """创建分享链接"""
    staff_id: int = Field(..., description="员工ID")
    product_id: Optional[int] = Field(None, description="商品ID（可选）")
    expires_in_days: Optional[int] = Field(None, description="有效期天数")


class LinkResponse(BaseModel):
    """分享链接响应"""
    id: int
    staff_id: int
    staff_code: Optional[str] = None
    product_id: Optional[int] = None
    link_code: str
    short_url: str
    full_url: str
    click_count: int
    order_count: int
    conversion_rate: float
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    """链接统计数据"""
    link_id: int
    link_code: str
    click_count: int
    order_count: int
    conversion_rate: float
    sales_amount: float
    commission_amount: float
    today_clicks: int
    this_week_clicks: int
    this_month_clicks: int


# ==================== 订单相关模型 ====================

class OrderAssignRequest(BaseModel):
    """订单归属请求"""
    order_id: int = Field(..., description="订单ID")
    link_code: str = Field(..., description="分享链接码")
    product_id: Optional[int] = Field(None, description="商品ID")
    amount: float = Field(..., gt=0, description="订单金额")


class OrderResponse(BaseModel):
    """分销订单响应"""
    id: int
    order_id: int
    staff_id: int
    staff_name: Optional[str] = None
    link_id: int
    product_id: Optional[int] = None
    amount: float
    commission: float
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: List[OrderResponse]
    total: int
    page: int
    limit: int


# ==================== 访问追踪相关模型 ====================

class VisitTrackRequest(BaseModel):
    """访问追踪请求"""
    link_code: str = Field(..., description="分享链接码")
    visitor_id: Optional[str] = Field(None, description="访客ID（可选，用于识别用户）")
    source: Optional[str] = Field(None, description="来源")
    referrer: Optional[str] = Field(None, description="来源页面")


class VisitResponse(BaseModel):
    """访问追踪响应"""
    success: bool
    short_url: str
    redirect_url: str
    message: str


# ==================== 佣金相关模型 ====================

class CommissionResponse(BaseModel):
    """佣金记录响应"""
    id: int
    staff_id: int
    staff_name: Optional[str] = None
    order_id: int
    amount: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommissionListResponse(BaseModel):
    """佣金列表响应"""
    commissions: List[CommissionResponse]
    total: float
    pending: float
    confirmed: float
    paid: float


# ==================== 排行榜相关模型 ====================

class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int
    staff_id: int
    staff_code: str
    staff_name: str
    total_sales: float
    total_orders: int
    total_commission: float
    click_count: int


class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    entries: List[LeaderboardEntry]
    period: str
    total_staffs: int


# ==================== 统计相关模型 ====================

class GlobalStats(BaseModel):
    """全局统计数据"""
    total_staffs: int
    active_staffs: int
    total_links: int
    total_visits: int
    total_orders: int
    total_sales: float
    total_commission: float
    paid_commission: float
    pending_commission: float
    average_conversion_rate: float
    top_performer: Optional[StaffResponse] = None


# ==================== 短链接相关模型 ====================

class ShortLinkRedirect(BaseModel):
    """短链接重定向响应"""
    redirect_url: str
    staff_code: str
