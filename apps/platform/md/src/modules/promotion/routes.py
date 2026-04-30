"""
Promotion Module Routes
FastAPI routes for promotion/coupon/flash sale management endpoints

Provides CRUD operations, validation, and redemption for promotions
"""

import math
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
import logging

from .schemas import (
    PromotionCreate,
    PromotionUpdate,
    PromotionResponse,
    PromotionListResponse,
    PromotionStatus,
    PromotionType,
    PromotionResponseModel,
    CouponCreate,
    CouponResponse,
    CouponValidateRequest,
    CouponValidateResponse,
    FlashSaleCreate,
    FlashSaleResponse,
    FlashSaleListResponse,
    CouponUsageResponse,
    CouponUsageListResponse,
    DiscountCalculationRequest,
    DiscountCalculationResponse,
    OrderItemForDiscount,
)

from .services import (
    promotion_service,
    coupon_service,
    flash_sale_service,
    PromotionService,
    CouponService,
    FlashSaleService,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/promotions", tags=["促销管理"])


# ============================================================================
# Helper Functions
# ============================================================================

def get_current_user_id(request: Request) -> int:
    """
    Get current authenticated user ID from JWT token.

    Args:
        request: FastAPI request object with Authorization header

    Returns:
        User ID of the authenticated user.

    Raises:
        HTTPException: If token is missing or invalid
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.replace("Bearer ", "")
    try:
        from modules.auth.services import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id", 0)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_admin_user_id(request: Request) -> int:
    """
    Get admin user ID from JWT token.

    Args:
        request: FastAPI request object with Authorization header

    Returns:
        Admin user ID.

    Raises:
        HTTPException: If token is missing or not admin
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.replace("Bearer ", "")
    try:
        from modules.auth.services import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role", "user")
        if role not in ("super_admin", "admin", "content_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload.get("user_id", 0)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================================
# Promotion Routes
# ============================================================================

@router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    data: PromotionCreate,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Create a new promotion.

    Admin endpoint for creating promotions.
    """
    try:
        promotion = promotion_service.create_promotion(data)
        logger.info(f"Promotion created: ID={promotion.id}, Admin={user_id}")
        return promotion.to_response()
    except Exception as e:
        logger.error(f"Failed to create promotion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建促销活动失败: {str(e)}"
        )


@router.get("/active", response_model=List[PromotionResponse])
async def get_active_promotions():
    """
    Get all currently active promotions.

    Public endpoint for browsing active promotions.
    """
    promotions = promotion_service.get_active_promotions()
    return [p.to_response() for p in promotions]


@router.get("/", response_model=PromotionListResponse)
async def list_promotions(
    status: Optional[PromotionStatus] = Query(None, description="Filter by status"),
    promotion_type: Optional[PromotionType] = Query(None, description="Filter by type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List promotions with filtering and pagination.

    Admin endpoint for managing promotions.
    """
    promotions = promotion_service.list_promotions(
        status=status,
        promotion_type=promotion_type,
        is_active=is_active,
        page=page,
        limit=limit,
    )

    total = len(promotions)  # Simplified for in-memory storage
    pages = math.ceil(total / limit) if total > 0 else 1

    return PromotionListResponse(
        items=[p.to_response() for p in promotions],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


# ============================================================================
# Stats Routes
# ============================================================================

@router.get("/stats")
async def get_promotion_stats(
    user_id: int = Depends(get_admin_user_id)
):
    """
    Get promotion statistics.

    Admin endpoint for viewing promotion stats.
    """
    # Count active promotions
    active_promotions = promotion_service.get_active_promotions()

    # Count active coupons
    active_coupons = [
        c for c in coupon_service._coupons.values()
        if c.status == "active" and c.remaining_count > 0
    ]

    # Count ongoing flash sales
    ongoing_flash_sales = flash_sale_service.get_ongoing_flash_sales()

    return PromotionResponseModel(
        success=True,
        data={
            "active_promotions": len(active_promotions),
            "active_coupons": len(active_coupons),
            "ongoing_flash_sales": len(ongoing_flash_sales),
            "total_coupons_created": len(coupon_service._coupons),
            "total_flash_sales_created": len(flash_sale_service._flash_sales),
        }
    )


@router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_promotion(promotion_id: int):
    """
    Get promotion details by ID.
    """
    promotion = promotion_service.get_promotion(promotion_id)

    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="促销活动不存在"
        )

    return promotion.to_response()


@router.put("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: int,
    data: PromotionUpdate,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Update a promotion.

    Admin endpoint for updating promotions.
    """
    promotion = promotion_service.update_promotion(promotion_id, data)

    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="促销活动不存在"
        )

    logger.info(f"Promotion updated: ID={promotion_id}, Admin={user_id}")
    return promotion.to_response()


@router.delete("/{promotion_id}", response_model=PromotionResponseModel)
async def delete_promotion(
    promotion_id: int,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Delete a promotion.

    Admin endpoint for deleting promotions.
    """
    success = promotion_service.delete_promotion(promotion_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="促销活动不存在"
        )

    logger.info(f"Promotion deleted: ID={promotion_id}, Admin={user_id}")
    return PromotionResponseModel(
        success=True,
        message="促销活动已删除"
    )


@router.post("/{promotion_id}/activate", response_model=PromotionResponse)
async def activate_promotion(
    promotion_id: int,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Activate a promotion.

    Admin endpoint for activating promotions.
    """
    promotion = promotion_service.activate_promotion(promotion_id)

    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="促销活动不存在"
        )

    logger.info(f"Promotion activated: ID={promotion_id}, Admin={user_id}")
    return promotion.to_response()


@router.post("/{promotion_id}/deactivate", response_model=PromotionResponse)
async def deactivate_promotion(
    promotion_id: int,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Deactivate a promotion.

    Admin endpoint for deactivating promotions.
    """
    promotion = promotion_service.deactivate_promotion(promotion_id)

    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="促销活动不存在"
        )

    logger.info(f"Promotion deactivated: ID={promotion_id}, Admin={user_id}")
    return promotion.to_response()


# ============================================================================
# Coupon Routes
# ============================================================================

@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    data: CouponCreate,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Create a new coupon.

    Admin endpoint for creating coupons.
    """
    try:
        coupon = coupon_service.create_coupon(data)
        logger.info(f"Coupon created: ID={coupon.id}, Code={coupon.code}, Admin={user_id}")
        return coupon.to_response()
    except Exception as e:
        logger.error(f"Failed to create coupon: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建优惠券失败: {str(e)}"
        )


@router.get("/coupons", response_model=List[CouponResponse])
async def list_coupons(
    user_id: int = Depends(get_current_user_id),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List coupons for the current user.

    Returns coupons that the user has redeemed.
    """
    from .schemas import CouponStatus as CouponStatusEnum
    coupon_status = CouponStatusEnum(status) if status else None

    coupons = coupon_service.list_user_coupons(
        user_id=user_id,
        status=coupon_status,
        page=page,
        limit=limit,
    )

    return [c.to_response() for c in coupons]


@router.get("/coupons/{code}", response_model=CouponValidateResponse)
async def get_coupon(code: str):
    """
    Get coupon details by code and validate it.

    Returns coupon information and validation status.
    """
    response = coupon_service.validate_coupon(code)
    return response


@router.post("/coupons/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    data: CouponValidateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Validate a coupon for use.

    Checks if the coupon is valid for the user and order amount.
    """
    response = coupon_service.validate_coupon(
        code=data.code,
        order_amount=data.order_amount,
        user_id=data.user_id or user_id
    )
    return response


@router.post("/coupons/{code}/redeem", response_model=CouponResponse)
async def redeem_coupon(
    code: str,
    user_id: int = Depends(get_current_user_id)
):
    """
    Redeem/claim a coupon.

    User endpoint for claiming a coupon to their account.
    """
    coupon, message = coupon_service.redeem_coupon(code, user_id)

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    logger.info(f"Coupon redeemed: Code={code}, User={user_id}")
    return coupon.to_response()


@router.post("/coupons/{code}/apply", response_model=PromotionResponseModel)
async def apply_coupon(
    code: str,
    order_id: str = Query(..., description="Order ID"),
    order_amount: Decimal = Query(..., ge=0, description="Order amount"),
    user_id: int = Depends(get_current_user_id)
):
    """
    Apply a coupon to an order.

    Calculates and returns the discount amount.
    """
    discount, message = coupon_service.apply_coupon(code, user_id, order_id, order_amount)

    if discount is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return PromotionResponseModel(
        success=True,
        message=f"优惠券已应用，减免 {discount} 元",
        data={
            "coupon_code": code,
            "discount_amount": discount,
            "original_amount": order_amount,
            "final_amount": order_amount - discount
        }
    )


# ============================================================================
# Discount Calculation Routes
# ============================================================================

@router.post("/calculate-discount", response_model=DiscountCalculationResponse)
async def calculate_discount(
    data: DiscountCalculationRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Calculate discount for a coupon.

    Returns the discount amount without applying the coupon.
    """
    coupon = coupon_service.get_coupon_by_code(data.coupon_code)

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="优惠券不存在"
        )

    is_valid, message = coupon.is_valid(data.user_id or user_id)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Calculate total order amount
    order_items = data.order_items
    original_amount = sum(item.subtotal for item in order_items)

    # Calculate discount
    discount_amount = coupon.calculate_discount(original_amount)
    final_amount = original_amount - discount_amount

    return DiscountCalculationResponse(
        original_amount=original_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        coupon_code=coupon.code,
        coupon_type=coupon.coupon_type,
        coupon_value=coupon.value,
        savings=discount_amount
    )


# ============================================================================
# Flash Sale Routes
# ============================================================================

@router.post("/flash-sales", response_model=FlashSaleResponse, status_code=status.HTTP_201_CREATED)
async def create_flash_sale(
    data: FlashSaleCreate,
    user_id: int = Depends(get_admin_user_id)
):
    """
    Create a new flash sale.

    Admin endpoint for creating flash sales.
    """
    try:
        flash_sale = flash_sale_service.create_flash_sale(data)
        logger.info(f"Flash sale created: ID={flash_sale.id}, Admin={user_id}")
        return flash_sale.to_response()
    except Exception as e:
        logger.error(f"Failed to create flash sale: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建限时抢购失败: {str(e)}"
        )


@router.get("/flash-sales", response_model=FlashSaleListResponse)
async def list_flash_sales(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_ongoing: Optional[bool] = Query(None, description="Filter ongoing only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List flash sales with filtering and pagination.

    Public endpoint for browsing flash sales.
    """
    flash_sales, total = flash_sale_service.get_flash_sales(
        is_active=is_active,
        is_ongoing=is_ongoing,
        page=page,
        limit=limit,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return FlashSaleListResponse(
        items=[fs.to_response() for fs in flash_sales],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/flash-sales/ongoing", response_model=List[FlashSaleResponse])
async def get_ongoing_flash_sales():
    """
    Get all currently ongoing flash sales.

    Public endpoint for displaying active flash sales.
    """
    flash_sales = flash_sale_service.get_ongoing_flash_sales()
    return [fs.to_response() for fs in flash_sales]


@router.get("/flash-sales/{flash_sale_id}", response_model=FlashSaleResponse)
async def get_flash_sale(flash_sale_id: int):
    """
    Get flash sale details by ID.
    """
    flash_sale = flash_sale_service.get_flash_sale(flash_sale_id)

    if not flash_sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="限时抢购不存在"
        )

    return flash_sale.to_response()


@router.get("/flash-sales/product/{product_id}", response_model=FlashSaleResponse)
async def get_product_flash_sale(product_id: int):
    """
    Get current active flash sale for a product.
    """
    flash_sale = flash_sale_service.get_flash_sale_by_product(product_id)

    if not flash_sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该商品当前没有进行中的限时抢购"
        )

    return flash_sale.to_response()


@router.post("/flash-sales/{flash_sale_id}/purchase", response_model=PromotionResponseModel)
async def purchase_flash_sale(
    flash_sale_id: int,
    quantity: int = Query(1, ge=1, description="Quantity to purchase"),
    user_id: int = Depends(get_current_user_id)
):
    """
    Purchase from a flash sale.

    User endpoint for buying flash sale items.
    """
    success, message = flash_sale_service.purchase(flash_sale_id, user_id, quantity)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    flash_sale = flash_sale_service.get_flash_sale(flash_sale_id)

    return PromotionResponseModel(
        success=True,
        message=f"购买成功！您已购买 {quantity} 件",
        data={
            "flash_sale_id": flash_sale_id,
            "product_name": flash_sale.product_name if flash_sale else None,
            "quantity": quantity,
            "flash_price": flash_sale.flash_price if flash_sale else None,
            "total_amount": (flash_sale.flash_price * quantity) if flash_sale else None,
        }
    )


# ============================================================================
# Usage History Routes
# ============================================================================

@router.get("/usage/history", response_model=CouponUsageListResponse)
async def get_usage_history(
    user_id: int = Depends(get_current_user_id),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Get coupon usage history for the current user.

    Returns a list of coupons that the user has used.
    """
    usages, total = coupon_service.get_usage_history(user_id=user_id, page=page, limit=limit)
    pages = math.ceil(total / limit) if total > 0 else 1

    return CouponUsageListResponse(
        items=[u.to_response() for u in usages],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/usage/history/all", response_model=CouponUsageListResponse)
async def get_all_usage_history(
    coupon_id: Optional[int] = Query(None, description="Filter by coupon ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: int = Depends(get_admin_user_id)
):
    """
    Get all coupon usage history (admin endpoint).

    Admin endpoint for viewing all coupon usage.
    """
    usages, total = coupon_service.get_usage_history(coupon_id=coupon_id, page=page, limit=limit)
    pages = math.ceil(total / limit) if total > 0 else 1

    return CouponUsageListResponse(
        items=[u.to_response() for u in usages],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


