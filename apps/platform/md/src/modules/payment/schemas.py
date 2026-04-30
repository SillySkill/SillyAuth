"""
Payment Module Schemas
支付模块数据模型

定义支付相关的请求和响应数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    PAYPAL = "paypal"


class PaymentStatusEnum(str, Enum):
    """支付状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CLOSED = "closed"


class PaymentChannel(str, Enum):
    """支付渠道枚举"""
    # 微信支付渠道
    WECHAT_APP = "wechat_app"
    WECHAT_WEB = "wechat_web"
    WECHAT_H5 = "wechat_h5"
    WECHAT_NATIVE = "wechat_native"
    # 支付宝渠道
    ALIPAY_APP = "alipay_app"
    ALIPAY_WEB = "alipay_web"
    ALIPAY_WAP = "alipay_wap"
    # PayPal渠道
    PAYPAL_WEB = "paypal_web"
    PAYPAL_APP = "paypal_app"


# ============================================
# Request Schemas
# ============================================

class PaymentCreate(BaseModel):
    """创建支付请求"""
    order_id: str = Field(..., description="订单ID", min_length=1, max_length=64)
    amount: float = Field(..., description="支付金额", gt=0)
    currency: str = Field(default="CNY", description="货币代码", max_length=3)
    method: PaymentMethod = Field(..., description="支付方式: wechat|alipay|paypal")
    channel: Optional[PaymentChannel] = Field(default=None, description="支付渠道")
    description: Optional[str] = Field(default=None, description="支付描述", max_length=256)
    notify_url: Optional[str] = Field(default=None, description="异步通知URL")
    return_url: Optional[str] = Field(default=None, description="支付成功跳转URL")
    cancel_url: Optional[str] = Field(default=None, description="支付取消跳转URL")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD20240101000001",
                "amount": 99.99,
                "currency": "CNY",
                "method": "wechat",
                "channel": "wechat_app",
                "description": "购买教程：Python入门",
                "notify_url": "https://example.com/api/payment/notify/wechat",
                "return_url": "https://example.com/payment/success",
                "cancel_url": "https://example.com/payment/cancel"
            }
        }


class RefundRequest(BaseModel):
    """退款请求"""
    payment_id: str = Field(..., description="支付记录ID", min_length=1, max_length=64)
    amount: Optional[float] = Field(default=None, description="退款金额（None表示全额退款）", gt=0)
    reason: Optional[str] = Field(default=None, description="退款原因", max_length=256)

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "PAY20240101000001",
                "amount": 99.99,
                "reason": "用户申请退款"
            }
        }


class PaymentQuery(BaseModel):
    """支付查询请求"""
    payment_id: Optional[str] = Field(default=None, description="支付记录ID")
    order_id: Optional[str] = Field(default=None, description="订单ID")
    transaction_id: Optional[str] = Field(default=None, description="第三方交易ID")


# ============================================
# Response Schemas
# ============================================

class PaymentResponse(BaseModel):
    """支付响应"""
    payment_id: str = Field(..., description="支付记录ID")
    order_id: str = Field(..., description="订单ID")
    amount: float = Field(..., description="支付金额")
    currency: str = Field(..., description="货币代码")
    status: PaymentStatusEnum = Field(..., description="支付状态")
    method: PaymentMethod = Field(..., description="支付方式")
    channel: Optional[PaymentChannel] = Field(default=None, description="支付渠道")
    pay_url: Optional[str] = Field(default=None, description="支付链接/二维码")
    pay_params: Optional[dict] = Field(default=None, description="支付参数（APP支付用）")
    qr_code: Optional[str] = Field(default=None, description="二维码内容（扫码支付用）")
    expires_at: Optional[datetime] = Field(default=None, description="支付过期时间")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "PAY20240101000001",
                "order_id": "ORD20240101000001",
                "amount": 99.99,
                "currency": "CNY",
                "status": "pending",
                "method": "wechat",
                "channel": "wechat_app",
                "pay_url": "weixin://wxpay/bizpayurl?pr=xxxxxx",
                "created_at": "2024-01-01T10:00:00Z"
            }
        }


class PaymentStatus(BaseModel):
    """支付状态响应"""
    payment_id: str = Field(..., description="支付记录ID")
    order_id: str = Field(..., description="订单ID")
    status: PaymentStatusEnum = Field(..., description="支付状态")
    transaction_id: Optional[str] = Field(default=None, description="第三方交易ID")
    amount: float = Field(..., description="支付金额")
    currency: str = Field(..., description="货币代码")
    method: PaymentMethod = Field(..., description="支付方式")
    paid_at: Optional[datetime] = Field(default=None, description="支付成功时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "PAY20240101000001",
                "order_id": "ORD20240101000001",
                "status": "success",
                "transaction_id": "WX20240101000001",
                "amount": 99.99,
                "currency": "CNY",
                "method": "wechat",
                "paid_at": "2024-01-01T10:05:00Z",
                "updated_at": "2024-01-01T10:05:00Z"
            }
        }


class RefundResult(BaseModel):
    """退款结果响应"""
    refund_id: str = Field(..., description="退款记录ID")
    payment_id: str = Field(..., description="原支付记录ID")
    order_id: str = Field(..., description="订单ID")
    refund_amount: float = Field(..., description="退款金额")
    refund_status: Literal["pending", "processing", "success", "failed"] = Field(
        ..., description="退款状态"
    )
    refund_reason: Optional[str] = Field(default=None, description="退款原因")
    transaction_id: Optional[str] = Field(default=None, description="退款交易ID")
    refund_time: Optional[datetime] = Field(default=None, description="退款时间")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "refund_id": "REF20240101000001",
                "payment_id": "PAY20240101000001",
                "order_id": "ORD20240101000001",
                "refund_amount": 99.99,
                "refund_status": "success",
                "refund_reason": "用户申请退款",
                "transaction_id": "WX20240101000002",
                "refund_time": "2024-01-02T10:00:00Z",
                "created_at": "2024-01-02T09:00:00Z"
            }
        }


class PaymentMethodInfo(BaseModel):
    """支付方式信息"""
    method: PaymentMethod = Field(..., description="支付方式")
    name: str = Field(..., description="支付方式名称")
    icon: Optional[str] = Field(default=None, description="图标URL")
    description: Optional[str] = Field(default=None, description="描述")
    channels: List[PaymentChannel] = Field(..., description="支持的渠道列表")
    currencies: List[str] = Field(..., description="支持的货币")
    enabled: bool = Field(default=True, description="是否启用")


class PaymentMethodsResponse(BaseModel):
    """可用支付方式响应"""
    methods: List[PaymentMethodInfo] = Field(..., description="支付方式列表")
    default_currency: str = Field(default="CNY", description="默认货币")


# ============================================
# Webhook Schemas
# ============================================

class WeChatPayNotifyData(BaseModel):
    """微信支付回调数据"""
    return_code: str
    return_msg: Optional[str] = None
    result_code: Optional[str] = None
    mch_id: Optional[str] = None
    appid: Optional[str] = None
    sign_type: Optional[str] = None
    sign: Optional[str] = None
    out_trade_no: Optional[str] = None
    transaction_id: Optional[str] = None
    openid: Optional[str] = None
    trade_type: Optional[str] = None
    trade_state: Optional[str] = None
    bank_type: Optional[str] = None
    total_fee: Optional[int] = None
    cash_fee: Optional[int] = None
    time_end: Optional[str] = None


class AlipayNotifyData(BaseModel):
    """支付宝回调数据"""
    out_trade_no: str = Field(..., description="商户订单号")
    trade_no: Optional[str] = Field(default=None, description="支付宝交易号")
    trade_status: Optional[str] = Field(default=None, description="交易状态")
    total_amount: Optional[str] = Field(default=None, description="订单金额")
    receipt_amount: Optional[str] = Field(default=None, description="实收金额")
    buyer_pay_amount: Optional[str] = Field(default=None, description="买家付款金额")
    gmt_payment: Optional[str] = Field(default=None, description="付款时间")


class PayPalWebhookData(BaseModel):
    """PayPal Webhook 数据"""
    id: Optional[str] = None
    event_type: str = Field(..., description="事件类型")
    resource: Optional[dict] = Field(default=None, description="资源数据")
    create_time: Optional[str] = None
    resource_type: Optional[str] = None


# ============================================
# Error Schemas
# ============================================

class PaymentError(BaseModel):
    """支付错误响应"""
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[dict] = Field(default=None, description="错误详情")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "PAYMENT_FAILED",
                "error_message": "支付创建失败",
                "details": {"reason": "余额不足"}
            }
        }


# ============================================
# Order Schemas (from old payment.py)
# ============================================

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    content_type: str = Field(..., description="内容类型: tutorial, download")
    content_id: int = Field(..., description="内容ID")
    purchase_type: str = Field(default="one_time", description="购买类型: one_time, subscription")

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """订单响应"""
    id: int = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单号")
    product_name: Optional[str] = Field(default=None, description="产品名称")
    content_type: Optional[str] = Field(default=None, description="内容类型")
    content_id: Optional[int] = Field(default=None, description="内容ID")
    original_price: float = Field(default=0, description="原价")
    discount_amount: float = Field(default=0, description="折扣金额")
    final_price: float = Field(default=0, description="最终价格")
    currency: str = Field(default="CNY", description="货币")
    status: Optional[str] = Field(default=None, description="订单状态")
    payment_status: Optional[str] = Field(default=None, description="支付状态")
    purchase_type: Optional[str] = Field(default=None, description="购买类型")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    paid_at: Optional[datetime] = Field(default=None, description="支付时间")
    expires_at: Optional[datetime] = Field(default=None, description="过期时间")

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    """订单列表响应"""
    items: List[OrderResponse] = Field(default_factory=list, description="订单列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页大小")
    total_pages: int = Field(default=0, description="总页数")

    model_config = {"from_attributes": True}


class PaymentCreateRequest(BaseModel):
    """创建支付请求（订单支付）"""
    order_number: str = Field(..., description="订单号")
    payment_method: str = Field(..., description="支付方式: wechat, alipay, paypal")
    payment_channel: str = Field(..., description="支付渠道")

    model_config = {"from_attributes": True}


# ============================================
# Purchase Schemas
# ============================================

class PurchaseResponse(BaseModel):
    """已购买内容响应"""
    content_type: str = Field(..., description="内容类型")
    content_id: int = Field(..., description="内容ID")
    title: Optional[str] = Field(default=None, description="标题")
    description: Optional[str] = Field(default=None, description="描述")
    thumbnail: Optional[str] = Field(default=None, description="缩略图")
    unlock_source: Optional[str] = Field(default=None, description="解锁来源")
    unlocked_at: Optional[datetime] = Field(default=None, description="解锁时间")
    expires_at: Optional[datetime] = Field(default=None, description="过期时间")

    model_config = {"from_attributes": True}


# ============================================
# Submission Schemas (from old payment.py)
# ============================================

class SubmissionCreate(BaseModel):
    """创建提交请求"""
    title_zh_CN: str = Field(..., description="中文标题")
    description_zh_CN: str = Field(..., description="中文描述")
    content_zh_CN: str = Field(..., description="中文内容")
    content_type: str = Field(..., description="内容类型")
    category: str = Field(..., description="分类")
    subcategory: Optional[str] = Field(default=None, description="子分类")
    is_paid: bool = Field(default=False, description="是否付费")
    price: Optional[float] = Field(default=0, description="价格")

    title_en: Optional[str] = Field(default=None, description="英文标题")
    description_en: Optional[str] = Field(default=None, description="英文描述")
    content_en: Optional[str] = Field(default=None, description="英文内容")
    difficulty: Optional[str] = Field(default=None, description="难度")
    platform: Optional[str] = Field(default=None, description="平台")
    version: Optional[str] = Field(default=None, description="版本")
    thumbnail: Optional[str] = Field(default=None, description="缩略图URL")
    video_url: Optional[str] = Field(default=None, description="视频URL")
    video_type: Optional[str] = Field(default=None, description="视频类型")
    video_duration: Optional[int] = Field(default=None, description="视频时长(秒)")
    file_name: Optional[str] = Field(default=None, description="文件名")
    file_url: Optional[str] = Field(default=None, description="文件URL")
    file_size: Optional[int] = Field(default=None, description="文件大小(字节)")
    file_type: Optional[str] = Field(default=None, description="文件类型")
    file_checksum: Optional[str] = Field(default=None, description="文件校验和")
    github_url: Optional[str] = Field(default=None, description="GitHub URL")

    model_config = {"from_attributes": True}


class SubmissionResponse(BaseModel):
    """提交响应"""
    id: int = Field(..., description="提交ID")
    content_type: Optional[str] = Field(default=None, description="内容类型")
    title_zh_CN: Optional[str] = Field(default=None, description="中文标题")
    description_zh_CN: Optional[str] = Field(default=None, description="中文描述")
    category: Optional[str] = Field(default=None, description="分类")
    subcategory: Optional[str] = Field(default=None, description="子分类")
    is_paid: bool = Field(default=False, description="是否付费")
    price: float = Field(default=0, description="价格")
    thumbnail: Optional[str] = Field(default=None, description="缩略图")
    status: Optional[str] = Field(default=None, description="状态")
    ai_review_status: Optional[str] = Field(default=None, description="AI审核状态")
    ai_review_score: Optional[float] = Field(default=None, description="AI审核分数")
    submitted_at: Optional[datetime] = Field(default=None, description="提交时间")
    reviewed_at: Optional[datetime] = Field(default=None, description="审核时间")
    published_content_id: Optional[int] = Field(default=None, description="发布内容ID")
    published_at: Optional[datetime] = Field(default=None, description="发布时间")

    model_config = {"from_attributes": True}


class ApproveSubmissionBody(BaseModel):
    """审核通过请求体"""
    pass

    model_config = {"from_attributes": True}


class RejectSubmissionBody(BaseModel):
    """审核拒绝请求体"""
    reason: str = Field(..., description="拒绝原因")

    model_config = {"from_attributes": True}


# ============================================
# Revenue Schemas
# ============================================

class DailyRevenueStat(BaseModel):
    """每日收入统计"""
    date: Optional[str] = Field(default=None, description="日期")
    paid_orders: int = Field(default=0, description="已支付订单数")
    total_revenue: float = Field(default=0, description="总收入")

    model_config = {"from_attributes": True}


class RevenueStatsResponse(BaseModel):
    """收入统计响应"""
    period_days: int = Field(..., description="统计周期(天)")
    total_orders: int = Field(default=0, description="总订单数")
    total_revenue: float = Field(default=0, description="总收入")
    daily_stats: List[DailyRevenueStat] = Field(default_factory=list, description="每日统计")

    model_config = {"from_attributes": True}


# ============================================
# Payment Account Schemas (from payment_accounts.py)
# ============================================

ALLOWED_ACCOUNT_TYPES: set = {"wechat", "alipay", "paypal", "bank"}
ALLOWED_CURRENCIES: set = {"CNY", "USD", "EUR", "GBP", "JPY", "HKD"}
ALLOWED_SETTLEMENT_METHODS: set = {"direct", "points"}
ALLOWED_SETTLEMENT_PERIODS: set = {"weekly", "monthly", "quarterly"}


class PaymentAccountCreate(BaseModel):
    """创建收款账户请求"""
    account_type: str = Field(..., description="账户类型: wechat, alipay, paypal, bank")
    account_name: str = Field(..., description="账户名称", min_length=1, max_length=255)
    account_id: str = Field(..., description="账户标识", min_length=1, max_length=255)
    credentials: dict = Field(..., description="凭证信息（加密存储）")
    currency: str = Field(default="CNY", description="支持的货币")
    description: Optional[str] = Field(default=None, description="描述", max_length=1000)

    model_config = {"from_attributes": True}


class PaymentAccountUpdate(BaseModel):
    """更新收款账户请求"""
    account_name: Optional[str] = Field(default=None, description="账户名称")
    credentials: Optional[dict] = Field(default=None, description="凭证信息")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    is_primary: Optional[bool] = Field(default=None, description="是否首选")
    priority: Optional[int] = Field(default=None, description="优先级")
    currency: Optional[str] = Field(default=None, description="货币")
    description: Optional[str] = Field(default=None, description="描述")

    model_config = {"from_attributes": True}


class PaymentAccountResponse(BaseModel):
    """收款账户响应"""
    id: int = Field(..., description="账户ID")
    account_type: str = Field(..., description="账户类型")
    account_name: str = Field(..., description="账户名称")
    account_id: str = Field(..., description="账户标识")
    credentials: Optional[dict] = Field(default=None, description="凭证（已脱敏）")
    is_active: bool = Field(default=True, description="是否启用")
    is_primary: bool = Field(default=False, description="是否首选")
    priority: int = Field(default=0, description="优先级")
    currency: str = Field(default="CNY", description="货币")
    description: Optional[str] = Field(default=None, description="描述")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")

    model_config = {"from_attributes": True}


# ============================================
# Creator Settlement Schemas
# ============================================

class CreatorSettlementPreference(BaseModel):
    """创作者结算偏好"""
    settlement_method: str = Field(default="direct", description="结算方式: direct, points")
    payment_account_type: Optional[str] = Field(default=None, description="收款账户类型")
    payment_account_id: Optional[str] = Field(default=None, description="收款账户标识")
    auto_settle: bool = Field(default=False, description="是否自动结算")
    min_settlement_amount: float = Field(default=100.00, description="最低结算金额", ge=0)
    settlement_period: str = Field(default="monthly", description="结算周期: weekly, monthly, quarterly")
    paypal_email: Optional[str] = Field(default=None, description="PayPal 邮箱")
    alipay_account: Optional[str] = Field(default=None, description="支付宝账号")
    wechat_openid: Optional[str] = Field(default=None, description="微信 OpenID")

    model_config = {"from_attributes": True}


class CreatorEarningResponse(BaseModel):
    """创作者收益记录"""
    id: int = Field(..., description="记录ID")
    order_id: Optional[int] = Field(default=None, description="订单ID")
    content_type: Optional[str] = Field(default=None, description="内容类型")
    content_id: Optional[int] = Field(default=None, description="内容ID")
    gross_amount: float = Field(default=0, description="总金额")
    platform_commission: float = Field(default=0, description="平台佣金")
    creator_share: float = Field(default=0, description="创作者分成")
    settlement_status: Optional[str] = Field(default=None, description="结算状态")
    settlement_method: Optional[str] = Field(default=None, description="结算方式")
    settlement_amount: Optional[float] = Field(default=None, description="结算金额")
    points_awarded: Optional[int] = Field(default=None, description="奖励积分")
    settled_at: Optional[datetime] = Field(default=None, description="结算时间")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")

    model_config = {"from_attributes": True}


class CreatorEarningListResponse(BaseModel):
    """创作者收益列表响应"""
    items: List[CreatorEarningResponse] = Field(default_factory=list, description="收益列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页大小")
    total_pages: int = Field(default=0, description="总页数")

    model_config = {"from_attributes": True}


class CreatorEarningSummary(BaseModel):
    """创作者收益汇总"""
    settlement_method: Optional[str] = Field(default=None, description="结算方式")
    auto_settle: Optional[bool] = Field(default=None, description="自动结算")
    total_earnings_count: int = Field(default=0, description="收益笔数")
    pending_earnings: float = Field(default=0, description="待结算收益")
    settled_amount: float = Field(default=0, description="已结算金额")
    points_earned: int = Field(default=0, description="获得积分")
    total_orders_count: int = Field(default=0, description="总订单数")
    total_gross_amount: float = Field(default=0, description="总金额")
    total_platform_commission: float = Field(default=0, description="平台佣金合计")

    model_config = {"from_attributes": True}


class SettlementRequest(BaseModel):
    """结算请求"""
    payment_account_type: str = Field(..., description="收款账户类型")
    payment_account_id: str = Field(..., description="收款账户标识")

    model_config = {"from_attributes": True}


class SettlementResponse(BaseModel):
    """结算记录响应"""
    id: int = Field(..., description="记录ID")
    batch_number: Optional[str] = Field(default=None, description="批次号")
    total_orders: Optional[int] = Field(default=None, description="订单数")
    total_amount: float = Field(default=0, description="总金额")
    total_commission: float = Field(default=0, description="总佣金")
    total_earnings: float = Field(default=0, description="总收益")
    settlement_method: Optional[str] = Field(default=None, description="结算方式")
    status: Optional[str] = Field(default=None, description="状态")
    transaction_id: Optional[str] = Field(default=None, description="交易ID")
    failure_reason: Optional[str] = Field(default=None, description="失败原因")
    period_start: Optional[datetime] = Field(default=None, description="周期开始")
    period_end: Optional[datetime] = Field(default=None, description="周期结束")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    processed_at: Optional[datetime] = Field(default=None, description="处理时间")

    model_config = {"from_attributes": True}


class SettlementListResponse(BaseModel):
    """结算记录列表响应"""
    items: List[SettlementResponse] = Field(default_factory=list, description="结算列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页大小")
    total_pages: int = Field(default=0, description="总页数")

    model_config = {"from_attributes": True}


class PendingSettlementResponse(BaseModel):
    """待结算创作者响应"""
    user_id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(default=None, description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱")
    settlement_method: Optional[str] = Field(default=None, description="结算方式")
    payment_account_type: Optional[str] = Field(default=None, description="收款账户类型")
    payment_account_id: Optional[str] = Field(default=None, description="收款账户标识")
    min_settlement_amount: float = Field(default=100, description="最低结算金额")
    pending_count: int = Field(default=0, description="待结算笔数")
    total_pending_amount: float = Field(default=0, description="待结算总额")
    oldest_earning_date: Optional[datetime] = Field(default=None, description="最早收益日期")
    latest_earning_date: Optional[datetime] = Field(default=None, description="最新收益日期")

    model_config = {"from_attributes": True}


__all__ = [
    # Existing schemas
    "PaymentMethod",
    "PaymentStatusEnum",
    "PaymentChannel",
    "PaymentCreate",
    "RefundRequest",
    "PaymentQuery",
    "PaymentResponse",
    "PaymentStatus",
    "RefundResult",
    "PaymentMethodInfo",
    "PaymentMethodsResponse",
    "WeChatPayNotifyData",
    "AlipayNotifyData",
    "PayPalWebhookData",
    "PaymentError",
    # Order schemas
    "CreateOrderRequest",
    "OrderResponse",
    "OrderListResponse",
    "PaymentCreateRequest",
    # Purchase schemas
    "PurchaseResponse",
    # Submission schemas
    "SubmissionCreate",
    "SubmissionResponse",
    "ApproveSubmissionBody",
    "RejectSubmissionBody",
    # Revenue schemas
    "DailyRevenueStat",
    "RevenueStatsResponse",
    # Payment account schemas
    "PaymentAccountCreate",
    "PaymentAccountUpdate",
    "PaymentAccountResponse",
    "ALLOWED_ACCOUNT_TYPES",
    "ALLOWED_CURRENCIES",
    "ALLOWED_SETTLEMENT_METHODS",
    "ALLOWED_SETTLEMENT_PERIODS",
    # Creator settlement schemas
    "CreatorSettlementPreference",
    "CreatorEarningResponse",
    "CreatorEarningListResponse",
    "CreatorEarningSummary",
    "SettlementRequest",
    "SettlementResponse",
    "SettlementListResponse",
    "PendingSettlementResponse",
]
