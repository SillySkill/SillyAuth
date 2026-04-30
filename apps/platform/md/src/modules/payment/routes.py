"""
Payment Module Routes
支付模块路由

提供支付相关的 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks, Header
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging
import json
import xml.etree.ElementTree as ET

from .schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentStatus,
    PaymentStatusEnum,
    PaymentMethod,
    PaymentChannel,
    RefundRequest,
    RefundResult,
    PaymentMethodsResponse,
    PaymentMethodInfo,
    # New schemas
    CreateOrderRequest,
    PaymentCreateRequest,
    SubmissionCreate,
    SubmissionResponse,
    ApproveSubmissionBody,
    RejectSubmissionBody,
    PaymentAccountCreate,
    PaymentAccountUpdate,
    PaymentAccountResponse,
    CreatorSettlementPreference,
    SettlementRequest,
    ALLOWED_ACCOUNT_TYPES,
    ALLOWED_CURRENCIES,
    ALLOWED_SETTLEMENT_METHODS,
    ALLOWED_SETTLEMENT_PERIODS,
)
from .services import PaymentService, get_payment_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payment", tags=["支付"])


# ============================================
# Auth Stubs (Token-based)
# ============================================

def get_current_user_stub(authorization: str = Header(None)) -> dict:
    """
    Stub auth dependency - extracts user info from Bearer token.
    Token format: Bearer <user_id> (for development/stub usage).
    In production, replace with real JWT validation.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "").strip()
    try:
        user_id = int(token)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": user_id, "username": f"user_{user_id}"}


def get_current_admin_stub(authorization: str = Header(None)) -> dict:
    """
    Stub admin auth dependency - extracts user info from Bearer token.
    Token format: Bearer <admin_user_id>.
    In production, replace with real JWT + role validation.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "").strip()
    try:
        user_id = int(token)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": user_id, "username": f"admin_{user_id}"}


# ============================================
# Request/Response Models
# ============================================

class CreatePaymentRequest(BaseModel):
    """创建支付请求（兼容多种格式）"""
    order_id: str = Field(..., description="订单ID")
    amount: float = Field(..., description="支付金额", gt=0)
    currency: str = Field(default="CNY", description="货币代码")
    method: str = Field(..., description="支付方式: wechat|alipay|paypal")
    channel: Optional[str] = Field(default=None, description="支付渠道")
    description: Optional[str] = Field(default=None, description="支付描述")
    notify_url: Optional[str] = Field(default=None, description="异步通知URL")
    return_url: Optional[str] = Field(default=None, description="支付成功跳转URL")
    cancel_url: Optional[str] = Field(default=None, description="支付取消跳转URL")


class RefundRequestModel(BaseModel):
    """退款请求"""
    payment_id: str = Field(..., description="支付记录ID")
    amount: Optional[float] = Field(default=None, description="退款金额", gt=0)
    reason: Optional[str] = Field(default=None, description="退款原因")


# ============================================
# API Endpoints
# ============================================

@router.post("/create", response_model=dict)
async def create_payment(
    request: CreatePaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    创建支付

    创建支付订单，返回支付参数或支付链接
    """
    try:
        # 转换支付方式
        method = PaymentMethod(request.method)

        # 转换支付渠道（如果有）
        channel = None
        if request.channel:
            channel = PaymentChannel(request.channel)

        # 创建支付
        result = await payment_service.create_payment(
            order_id=request.order_id,
            amount=request.amount,
            currency=request.currency,
            method=method,
            description=request.description,
            channel=channel,
            notify_url=request.notify_url,
            return_url=request.return_url,
            cancel_url=request.cancel_url
        )

        return {
            "success": True,
            "data": {
                "payment_id": result.payment_id,
                "order_id": result.order_id,
                "amount": result.amount,
                "currency": result.currency,
                "status": result.status.value,
                "method": result.method.value,
                "channel": result.channel.value if result.channel else None,
                "pay_url": result.pay_url,
                "pay_params": result.pay_params,
                "qr_code": result.qr_code,
                "expires_at": result.expires_at.isoformat() if result.expires_at else None,
                "created_at": result.created_at.isoformat()
            }
        }

    except ValueError as e:
        logger.error(f"创建支付参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建支付失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建支付失败: {str(e)}")


@router.get("/{payment_id}", response_model=dict)
async def get_payment_status(
    payment_id: str,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    查询支付状态

    根据支付记录ID查询支付状态
    """
    # Guard against known static route paths being misinterpreted as payment IDs
    _known_paths = {
        "create", "refund", "methods", "notify",
        "orders", "my-purchases", "submissions",
    }
    if payment_id in _known_paths:
        raise HTTPException(status_code=404, detail="Payment not found")
    # Also guard against paths containing forward slash (multi-segment paths)
    if "/" in payment_id:
        raise HTTPException(status_code=404, detail="Payment not found")

    try:
        result = await payment_service.query_payment(payment_id=payment_id)

        return {
            "success": True,
            "data": {
                "payment_id": result.payment_id,
                "order_id": result.order_id,
                "status": result.status.value,
                "transaction_id": result.transaction_id,
                "amount": result.amount,
                "currency": result.currency,
                "method": result.method.value,
                "paid_at": result.paid_at.isoformat() if result.paid_at else None,
                "updated_at": result.updated_at.isoformat()
            }
        }

    except Exception as e:
        logger.error(f"查询支付失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询支付失败: {str(e)}")


@router.post("/notify/{provider}", response_model=dict)
async def payment_notification(
    provider: str,
    request: Request,
    background_tasks: BackgroundTasks,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    支付通知 Webhook

    接收第三方支付的异步通知
    """
    logger.info(f"收到 {provider} 支付通知")

    try:
        if provider == "wechat":
            # 微信支付使用 XML 格式
            body = await request.body()
            try:
                root = ET.fromstring(body)
                data = {child.tag: child.text for child in root}
            except ET.ParseError:
                raise HTTPException(status_code=400, detail="XML 解析失败")

        elif provider == "alipay":
            # 支付宝使用 form data
            form_data = await request.form()
            data = dict(form_data)

        elif provider == "paypal":
            # PayPal 使用 JSON
            body = await request.body()
            data = json.loads(body)
            # PayPal 需要验证签名
            paypal_client = payment_service._get_paypal_client()
            if paypal_client:
                headers = dict(request.headers)
                is_valid, verified_data = await paypal_client.verify_webhook(
                    headers,
                    body.decode()
                )
                if not is_valid:
                    logger.error("PayPal Webhook 验证失败")
                    raise HTTPException(status_code=401, detail="签名验证失败")

        else:
            raise HTTPException(status_code=400, detail="不支持的支付提供商")

        # 处理通知
        success = await payment_service.handle_notification(provider, data)

        # 返回响应
        if provider == "wechat":
            if success:
                return {"return_code": "SUCCESS", "return_msg": "OK"}
            else:
                return {"return_code": "FAIL", "return_msg": "处理失败"}
        else:
            if success:
                return {"success": True, "message": "处理成功"}
            else:
                return {"success": False, "message": "处理失败"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理支付通知失败: {e}")
        if provider == "wechat":
            return {"return_code": "FAIL", "return_msg": str(e)}
        else:
            return {"success": False, "message": str(e)}


@router.post("/refund", response_model=dict)
async def request_refund(
    request: RefundRequestModel,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    申请退款

    对已支付的订单申请退款
    """
    try:
        result = await payment_service.refund(
            payment_id=request.payment_id,
            amount=request.amount,
            reason=request.reason
        )

        return {
            "success": True,
            "data": {
                "refund_id": result.refund_id,
                "payment_id": result.payment_id,
                "order_id": result.order_id,
                "refund_amount": result.refund_amount,
                "refund_status": result.refund_status,
                "refund_reason": result.refund_reason,
                "transaction_id": result.transaction_id,
                "refund_time": result.refund_time.isoformat() if result.refund_time else None,
                "created_at": result.created_at.isoformat()
            }
        }

    except Exception as e:
        logger.error(f"申请退款失败: {e}")
        raise HTTPException(status_code=500, detail=f"申请退款失败: {str(e)}")


@router.get("/methods", response_model=dict)
async def get_payment_methods(
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    获取可用支付方式

    返回支持的支付方式列表
    """
    try:
        result = payment_service.get_available_payment_methods()

        methods_data = []
        for method in result.methods:
            methods_data.append({
                "method": method.method.value,
                "name": method.name,
                "icon": method.icon,
                "description": method.description,
                "channels": [ch.value for ch in method.channels],
                "currencies": method.currencies,
                "enabled": method.enabled
            })

        return {
            "success": True,
            "data": {
                "methods": methods_data,
                "default_currency": result.default_currency
            }
        }

    except Exception as e:
        logger.error(f"获取支付方式失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取支付方式失败: {str(e)}")


# ============================================
# PayPal Specific Endpoints
# ============================================

@router.post("/paypal/capture/{paypal_order_id}", response_model=dict)
async def capture_paypal_payment(
    paypal_order_id: str,
    payment_id: str,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    捕获 PayPal 支付

    用户在 PayPal 页面批准支付后调用此接口完成支付
    """
    try:
        paypal_client = payment_service._get_paypal_client()

        if not paypal_client:
            raise HTTPException(status_code=500, detail="PayPal 客户端未初始化")

        # 捕获支付
        capture_result = await paypal_client.capture_order(paypal_order_id)

        logger.info(f"PayPal 支付捕获成功: {capture_result}")

        return {
            "success": True,
            "data": {
                "paypal_order_id": capture_result.get("paypal_order_id"),
                "status": capture_result.get("status"),
                "transaction_id": capture_result.get("transaction_id")
            }
        }

    except Exception as e:
        logger.error(f"捕获 PayPal 支付失败: {e}")
        raise HTTPException(status_code=500, detail=f"捕获支付失败: {str(e)}")


# ============================================
# Order Endpoints (from old payment.py)
# ============================================

@router.post("/orders", response_model=dict)
def create_order(
    request: CreateOrderRequest,
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Create a purchase order.

    1. Validate content exists and is paid content
    2. Check if user already purchased
    3. Check order idempotency (prevent duplicate orders)
    4. Create order with pricing (including discounts)
    5. Return order info for payment
    """
    user_id = current_user["id"]
    try:
        from core.db_adapter import get_db_cursor as _get_db

        with _get_db() as cur:
            # Check for existing pending order (idempotency)
            cur.execute(
                """SELECT order_number FROM orders
                   WHERE user_id = %s AND content_type = %s AND content_id = %s
                     AND payment_status = 'pending'
                   ORDER BY created_at DESC LIMIT 1""",
                (user_id, request.content_type, request.content_id)
            )
            existing = cur.fetchone()
            if existing:
                return {
                    "success": True,
                    "data": {
                        "order_number": existing["order_number"],
                        "message": "Order already exists, please proceed with payment",
                    }
                }

            # Get content
            if request.content_type == "tutorial":
                cur.execute(
                    "SELECT id, title_zh_CN, is_paid, price, thumbnail FROM tutorials WHERE id = %s",
                    (request.content_id,)
                )
            elif request.content_type == "download":
                cur.execute(
                    "SELECT id, title_zh_CN, is_paid, price, thumbnail FROM downloads WHERE id = %s",
                    (request.content_id,)
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid content type")

            content = cur.fetchone()
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")

            if not content.get("is_paid") or (content.get("price", 0) or 0) == 0:
                raise HTTPException(status_code=400, detail="This content is free, no purchase needed")

            # Check if already unlocked
            cur.execute(
                """SELECT id FROM content_unlocks
                   WHERE user_id = %s AND content_type = %s AND content_id = %s
                     AND (expires_at IS NULL OR expires_at > NOW())""",
                (user_id, request.content_type, request.content_id)
            )
            if cur.fetchone():
                return {
                    "success": True,
                    "already_purchased": True,
                    "message": "You already own this content",
                }

            # Get paid product info
            cur.execute(
                """SELECT id, product_name, price, currency, is_active, has_discount,
                          discount_type, discount_value, discount_start, discount_end,
                          creator_id, creator_share_percentage, platform_share_percentage
                   FROM paid_products
                   WHERE content_type = %s AND content_id = %s AND is_active = TRUE
                   LIMIT 1""",
                (request.content_type, request.content_id)
            )
            product = cur.fetchone()
            if not product:
                raise HTTPException(status_code=404, detail="Product info not found")

            # Calculate price with discount
            final_price = float(product["price"]) if product["price"] else 0
            discount_amount = 0.0
            now = datetime.now()
            if product.get("has_discount") and product.get("discount_start") and product.get("discount_end"):
                if product["discount_start"] <= now <= product["discount_end"]:
                    if product.get("discount_type") == "percentage":
                        final_price = final_price * (1 - (product.get("discount_value", 0) or 0) / 100)
                    else:
                        final_price = final_price - (product.get("discount_value", 0) or 0)
                    discount_amount = float(product["price"]) - final_price

            # Generate order number
            import hashlib, uuid
            timestamp_str = now.strftime("%Y%m%d%H%M%S")
            random_str = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:6]
            order_number = f"ORD{timestamp_str}{random_str}"

            # Create order
            cur.execute(
                """INSERT INTO orders
                   (order_number, user_id, content_type, content_id, product_id,
                    product_name, original_price, discount_amount, final_price,
                    currency, purchase_type, status, payment_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')
                   RETURNING id, order_number, created_at""",
                (
                    order_number, user_id, request.content_type, request.content_id,
                    product["id"], product.get("product_name"),
                    float(product["price"]) if product["price"] else 0,
                    discount_amount, final_price,
                    product.get("currency", "CNY"), request.purchase_type,
                )
            )
            result_row = cur.fetchone()

        return {
            "success": True,
            "data": {
                "order_id": result_row["id"],
                "order_number": result_row["order_number"],
                "product_name": product.get("product_name"),
                "original_price": float(product["price"]) if product["price"] else 0,
                "discount_amount": discount_amount,
                "final_price": final_price,
                "currency": product.get("currency", "CNY"),
                "created_at": result_row["created_at"].isoformat() if result_row["created_at"] else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create order failed: {e}")
        raise HTTPException(status_code=500, detail=f"Create order failed: {str(e)}")


@router.get("/orders", response_model=dict)
def get_user_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get user orders (paginated, filterable by status).
    """
    try:
        user_id = current_user["id"]
        result = payment_service.get_user_orders(
            user_id=user_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Get user orders failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get user orders failed: {str(e)}")


# ============================================
# Purchase Endpoints
# ============================================

@router.get("/my-purchases", response_model=dict)
def get_my_purchases(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get user's purchased/unlocked content.
    Returns valid unlocks (not expired).
    """
    try:
        user_id = current_user["id"]
        results = payment_service.get_my_purchases(
            user_id=user_id,
            content_type=content_type,
        )
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Get my purchases failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get my purchases failed: {str(e)}")


# ============================================
# Submission Endpoints (from old payment.py)
# ============================================

@router.post("/submissions", response_model=dict)
def create_submission(
    request: SubmissionCreate,
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Create a user submission (tutorial/download/content).
    Automatically enters pending review state.
    """
    try:
        user_id = current_user["id"]
        username = current_user["username"]

        # Validate required fields
        if not all([request.title_zh_CN, request.description_zh_CN, request.content_zh_CN, request.content_type, request.category]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Validate file URL if provided
        if request.file_url:
            if not request.file_url.startswith(("http://", "https://", "/")):
                raise HTTPException(status_code=400, detail="Invalid file URL format")

        data = request.model_dump()
        result = payment_service.create_submission(user_id, username, data)
        return {
            "success": True,
            "data": {
                "submission_id": result["submission_id"],
                "status": "pending",
                "message": "Submission created, pending review",
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Create submission failed: {str(e)}")


@router.get("/submissions", response_model=dict)
def get_my_submissions(
    status: Optional[str] = Query(None, description="Filter by submission status"),
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get user's submissions.
    """
    try:
        user_id = current_user["id"]
        results = payment_service.get_my_submissions(
            user_id=user_id,
            status=status,
        )
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Get my submissions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get my submissions failed: {str(e)}")


# ============================================
# Admin Submission Endpoints
# ============================================

@router.get("/admin/pending-submissions", response_model=dict)
def get_pending_submissions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Get pending submissions for review.
    """
    try:
        result = payment_service.get_pending_submissions(
            page=page,
            page_size=page_size,
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Get pending submissions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get pending submissions failed: {str(e)}")


@router.put("/admin/submissions/{submission_id}/approve", response_model=dict)
def approve_submission(
    submission_id: int,
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Approve a pending submission.
    """
    try:
        result = payment_service.approve_submission(
            submission_id=submission_id,
            admin_id=current_admin["id"],
        )
        return {"success": True, "message": "Submission approved", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Approve submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Approve submission failed: {str(e)}")


@router.put("/admin/submissions/{submission_id}/reject", response_model=dict)
def reject_submission(
    submission_id: int,
    body: RejectSubmissionBody,
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Reject a pending submission with a reason.
    """
    try:
        result = payment_service.reject_submission(
            submission_id=submission_id,
            admin_id=current_admin["id"],
            reason=body.reason,
        )
        return {"success": True, "message": "Submission rejected", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Reject submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reject submission failed: {str(e)}")


# ============================================
# Admin Revenue Endpoints
# ============================================

@router.get("/admin/revenue/stats", response_model=dict)
def get_revenue_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Get revenue statistics for the specified period.
    """
    try:
        result = payment_service.get_revenue_stats(days=days)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Get revenue stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get revenue stats failed: {str(e)}")


# ============================================
# Payment Account Management (Admin)
# ============================================

@router.get("/accounts", response_model=dict)
def list_payment_accounts(
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: List payment accounts.
    """
    try:
        if account_type and account_type not in ALLOWED_ACCOUNT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account_type. Allowed: {', '.join(ALLOWED_ACCOUNT_TYPES)}"
            )
        results = payment_service.list_payment_accounts(
            account_type=account_type,
            is_active=is_active,
        )
        return {"success": True, "data": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List payment accounts failed: {e}")
        raise HTTPException(status_code=500, detail=f"List payment accounts failed: {str(e)}")


@router.post("/accounts", response_model=dict)
def create_payment_account(
    account: PaymentAccountCreate,
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Create a payment account.
    """
    try:
        # Validate account type
        if account.account_type not in ALLOWED_ACCOUNT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account_type. Allowed: {', '.join(ALLOWED_ACCOUNT_TYPES)}"
            )
        if account.currency not in ALLOWED_CURRENCIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid currency. Allowed: {', '.join(ALLOWED_CURRENCIES)}"
            )

        result = payment_service.create_payment_account(
            data=account.model_dump()
        )
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create payment account failed: {e}")
        raise HTTPException(status_code=500, detail=f"Create payment account failed: {str(e)}")


@router.put("/accounts/{account_id}", response_model=dict)
def update_payment_account(
    account_id: int,
    account: PaymentAccountUpdate,
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Update a payment account.
    """
    try:
        if account.currency is not None and account.currency not in ALLOWED_CURRENCIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid currency. Allowed: {', '.join(ALLOWED_CURRENCIES)}"
            )
        # Only send non-None values
        update_data = {k: v for k, v in account.model_dump().items() if v is not None}
        result = payment_service.update_payment_account(
            account_id=account_id,
            data=update_data,
        )
        return {"success": True, "message": result["message"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update payment account failed: {e}")
        raise HTTPException(status_code=500, detail=f"Update payment account failed: {str(e)}")


@router.delete("/accounts/{account_id}", response_model=dict)
def delete_payment_account(
    account_id: int,
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Delete a payment account.
    """
    try:
        result = payment_service.delete_payment_account(account_id=account_id)
        return {"success": True, "message": result["message"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Delete payment account failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete payment account failed: {str(e)}")


# ============================================
# Creator Settlement Preference Endpoints
# ============================================

@router.get("/accounts/creator/preference", response_model=dict)
def get_creator_settlement_preference(
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get creator's settlement preference.
    """
    try:
        result = payment_service.get_creator_settlement_preference(
            user_id=current_user["id"]
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Get creator settlement preference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get creator settlement preference failed: {str(e)}")


@router.put("/accounts/creator/preference", response_model=dict)
def update_creator_settlement_preference(
    preference: CreatorSettlementPreference,
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Update creator's settlement preference.
    """
    try:
        # Validate
        if preference.settlement_method not in ALLOWED_SETTLEMENT_METHODS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid settlement_method. Allowed: {', '.join(ALLOWED_SETTLEMENT_METHODS)}"
            )
        if preference.settlement_period not in ALLOWED_SETTLEMENT_PERIODS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid settlement_period. Allowed: {', '.join(ALLOWED_SETTLEMENT_PERIODS)}"
            )
        if preference.payment_account_type and preference.payment_account_type not in ALLOWED_ACCOUNT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_account_type. Allowed: {', '.join(ALLOWED_ACCOUNT_TYPES)}"
            )

        result = payment_service.update_creator_settlement_preference(
            user_id=current_user["id"],
            data=preference.model_dump(),
        )
        return {"success": True, "message": result["message"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update creator settlement preference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Update creator settlement preference failed: {str(e)}")


# ============================================
# Creator Earnings Endpoints
# ============================================

@router.get("/accounts/creator/earnings", response_model=dict)
def get_creator_earnings(
    status: Optional[str] = Query(None, description="Filter by settlement status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get creator earnings records (paginated).
    """
    try:
        valid_statuses = {"pending", "settled", "points_converted", "failed"}
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {', '.join(valid_statuses)}"
            )

        result = payment_service.get_creator_earnings(
            user_id=current_user["id"],
            status=status,
            page=page,
            page_size=page_size,
        )
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get creator earnings failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get creator earnings failed: {str(e)}")


@router.get("/accounts/creator/earnings/summary", response_model=dict)
def get_creator_earnings_summary(
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get creator earnings summary.
    """
    try:
        result = payment_service.get_creator_earnings_summary(
            user_id=current_user["id"]
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Get creator earnings summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get creator earnings summary failed: {str(e)}")


# ============================================
# Creator Settlement Endpoints
# ============================================

@router.post("/accounts/creator/settle", response_model=dict)
def settle_creator_earnings(
    request: SettlementRequest,
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Settle creator's pending earnings.
    """
    try:
        if request.payment_account_type not in ALLOWED_ACCOUNT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_account_type. Allowed: {', '.join(ALLOWED_ACCOUNT_TYPES)}"
            )

        result = payment_service.settle_creator_earnings(
            user_id=current_user["id"],
            payment_account_type=request.payment_account_type,
            payment_account_id=request.payment_account_id,
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Settle creator earnings failed: {e}")
        raise HTTPException(status_code=500, detail=f"Settle creator earnings failed: {str(e)}")


@router.get("/accounts/creator/settlements", response_model=dict)
def get_creator_settlements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get creator settlement records (paginated).
    """
    try:
        result = payment_service.get_creator_settlements(
            user_id=current_user["id"],
            page=page,
            page_size=page_size,
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Get creator settlements failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get creator settlements failed: {str(e)}")


# ============================================
# Admin Settlement Endpoints
# ============================================

@router.get("/accounts/admin/pending-settlements", response_model=dict)
def get_pending_settlements(
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Get list of creators with pending settlements.
    """
    try:
        results = payment_service.get_pending_settlements()
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Get pending settlements failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get pending settlements failed: {str(e)}")


@router.post("/accounts/admin/settle/{target_user_id}", response_model=dict)
def admin_settle_creator(
    target_user_id: int,
    request: SettlementRequest,
    current_admin: dict = Depends(get_current_admin_stub),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin: Manually settle a creator's pending earnings.
    """
    try:
        if request.payment_account_type not in ALLOWED_ACCOUNT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_account_type. Allowed: {', '.join(ALLOWED_ACCOUNT_TYPES)}"
            )

        result = payment_service.admin_settle_creator(
            target_user_id=target_user_id,
            payment_account_type=request.payment_account_type,
            payment_account_id=request.payment_account_id,
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin settle creator failed: {e}")
        raise HTTPException(status_code=500, detail=f"Admin settle creator failed: {str(e)}")


# ============================================
# 导出
# ============================================

__all__ = ["router"]
