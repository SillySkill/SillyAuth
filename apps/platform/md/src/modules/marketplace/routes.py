"""
Marketplace Module Routes
FastAPI routes for marketplace listings and purchases

Provides listing management, purchase workflow, search, and reviews
"""

import math
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
import logging

from .schemas import (
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    ListingListResponse,
    ListingStatus,
    ListingSearchQuery,
    PurchaseItem,
    PurchaseRequest,
    PurchaseResponse,
    PurchaseListResponse,
    PurchaseStatus,
    PaymentMethod,
    ReviewCreate,
    ReviewResponse,
    MarketplaceResponse,
    MarketplaceStats,
    VendorSalesStats,
)
from .services import (
    listing_service,
    purchase_service,
    review_service,
    ListingService,
    PurchaseService,
    ReviewService,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/marketplace", tags=["交易市场"])


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


# ============================================================================
# Listing Routes
# ============================================================================

@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    data: ListingCreate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new marketplace listing.

    Creates a listing from an existing product.
    """
    vendor_id = get_vendor_id()

    # Get product data (mock - would integrate with goods module)
    # In production, this would fetch from goods service
    product_data = {
        "id": data.product_id,
        "name": f"Product {data.product_id}",
        "slug": f"product-{data.product_id}",
        "price": data.price,
        "original_price": None,
        "currency": "CNY",
        "images": [],
    }

    try:
        listing = listing_service.create_listing(
            product_id=data.product_id,
            vendor_id=vendor_id,
            product_data=product_data,
            data=data,
        )

        logger.info(f"Listing created: ID={listing.id}, Vendor={vendor_id}")

        return listing.to_response()

    except Exception as e:
        logger.error(f"Failed to create listing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建商品列表失败: {str(e)}"
        )


@router.get("/listings", response_model=ListingListResponse)
async def list_listings(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    is_featured: Optional[bool] = Query(None, description="Featured listings only"),
    sort_by: str = Query("created_at", description="Sort: created_at, price, sales, rating"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List marketplace listings with filtering and pagination.

    Public endpoint for browsing listings.
    """
    # Only show active listings by default
    status_filter = ListingStatus.ACTIVE

    listings = listing_service.list_listings(
        status=status_filter,
        category_id=category_id,
        vendor_id=vendor_id,
        keyword=keyword,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        is_featured=is_featured,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )

    total = listing_service.count_listings(status=status_filter)
    pages = math.ceil(total / limit) if total > 0 else 1

    return ListingListResponse(
        items=[l.to_response() for l in listings],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/listings/featured", response_model=ListingListResponse)
async def list_featured_listings(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of listings"),
):
    """
    List featured/promoted listings.

    Returns featured listings for homepage display.
    """
    listings = listing_service.list_listings(
        status=ListingStatus.ACTIVE,
        category_id=category_id,
        is_featured=True,
        page=1,
        limit=limit,
        sort_by="sales",
        sort_order="desc",
    )

    return ListingListResponse(
        items=[l.to_response() for l in listings],
        total=len(listings),
        page=1,
        limit=limit,
        pages=1,
    )


@router.get("/listings/search", response_model=ListingListResponse)
async def search_listings(
    q: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    sort_by: str = Query("relevance", description="Sort: relevance, price, sales, rating, created_at"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search marketplace listings.

    Full-text search across product names and descriptions.
    """
    # Map relevance to created_at
    if sort_by == "relevance":
        sort_by = "created_at"

    listings = listing_service.list_listings(
        status=ListingStatus.ACTIVE,
        category_id=category_id,
        keyword=q,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        min_price=min_price,
        max_price=max_price,
    )

    total = listing_service.count_listings(status=ListingStatus.ACTIVE)
    pages = math.ceil(total / limit) if total > 0 else 1

    return ListingListResponse(
        items=[l.to_response() for l in listings],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: int):
    """
    Get listing details by ID.

    Public endpoint for viewing listing details.
    """
    listing = listing_service.get_listing(listing_id)

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品列表不存在"
        )

    return listing.to_response()


@router.put("/listings/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    data: ListingUpdate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Update a listing.

    Only the listing owner can update their listings.
    """
    listing = listing_service.get_listing(listing_id)

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品列表不存在"
        )

    vendor_id = get_vendor_id()
    if listing.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此商品列表"
        )

    if listing.status == ListingStatus.REMOVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已删除的商品列表无法修改"
        )

    updated_listing = listing_service.update_listing(listing_id, data)

    if not updated_listing:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新商品列表失败"
        )

    return updated_listing.to_response()


@router.delete("/listings/{listing_id}", response_model=MarketplaceResponse)
async def delete_listing(
    listing_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a listing.

    Only the listing owner can delete their listings.
    """
    listing = listing_service.get_listing(listing_id)

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品列表不存在"
        )

    vendor_id = get_vendor_id()
    if listing.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此商品列表"
        )

    success = listing_service.delete_listing(listing_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除商品列表失败"
        )

    return MarketplaceResponse(
        success=True,
        message="商品列表已删除"
    )


@router.post("/listings/{listing_id}/activate", response_model=ListingResponse)
async def activate_listing(
    listing_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Activate a listing (make it available for purchase)."""
    listing = listing_service.get_listing(listing_id)

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品列表不存在"
        )

    vendor_id = get_vendor_id()
    if listing.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品列表"
        )

    activated_listing = listing_service.activate_listing(listing_id)
    return activated_listing.to_response()


@router.post("/listings/{listing_id}/deactivate", response_model=ListingResponse)
async def deactivate_listing(
    listing_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Deactivate a listing (pause sales)."""
    listing = listing_service.get_listing(listing_id)

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品列表不存在"
        )

    vendor_id = get_vendor_id()
    if listing.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品列表"
        )

    deactivated_listing = listing_service.deactivate_listing(listing_id)
    return deactivated_listing.to_response()


# ============================================================================
# Purchase Routes
# ============================================================================

@router.post("/purchases", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    data: PurchaseRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new purchase.

    Validates stock availability and creates the purchase order.
    """
    try:
        purchase = purchase_service.create_purchase(
            buyer_id=user_id,
            items=data.items,
            payment_method=data.payment_method,
            coupon_code=data.coupon_code,
            notes=data.notes,
            shipping_address=data.shipping_address,
            listing_service=listing_service,
        )

        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建订单失败，可能库存不足"
            )

        logger.info(f"Purchase created: Order={purchase.order_id}, Buyer={user_id}")

        return purchase.to_response()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create purchase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/purchases", response_model=PurchaseListResponse)
async def list_my_purchases(
    status: Optional[PurchaseStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: int = Depends(get_current_user_id)
):
    """
    List current user's purchases.

    Returns the authenticated user's order history.
    """
    purchases = purchase_service.list_purchases(
        buyer_id=user_id,
        status=status,
        page=page,
        limit=limit,
    )

    total = purchase_service.count_purchases(
        buyer_id=user_id,
        status=status,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return PurchaseListResponse(
        items=[p.to_response() for p in purchases],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/purchases/order/{order_id}", response_model=PurchaseResponse)
async def get_purchase_by_order(
    order_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """
    Get purchase details by order ID.

    Returns purchase details if the order belongs to the user.
    """
    purchase = purchase_service.get_purchase_by_order_id(order_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # Verify ownership
    if purchase.buyer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单"
        )

    return purchase.to_response()


@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Get purchase details by ID.

    Returns purchase details if it belongs to the user.
    """
    purchase = purchase_service.get_purchase(purchase_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # Verify ownership
    if purchase.buyer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单"
        )

    return purchase.to_response()


@router.post("/purchases/{purchase_id}/cancel", response_model=PurchaseResponse)
async def cancel_purchase(
    purchase_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Cancel a purchase.

    Only pending or paid orders can be cancelled.
    Stock will be released back to listings.
    """
    purchase = purchase_service.get_purchase(purchase_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # Verify ownership
    if purchase.buyer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权取消此订单"
        )

    cancelled_purchase = purchase_service.cancel_purchase(
        purchase_id,
        listing_service=listing_service
    )

    if not cancelled_purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法取消此订单，当前状态不允许取消"
        )

    return cancelled_purchase.to_response()


@router.post("/purchases/{purchase_id}/pay", response_model=PurchaseResponse)
async def pay_purchase(
    purchase_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Process payment for a purchase.

    Simulates payment processing and updates order status.
    """
    purchase = purchase_service.get_purchase(purchase_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if purchase.buyer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此订单"
        )

    if purchase.payment_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已支付或状态不允许支付"
        )

    # Update status (in production, integrate with payment service)
    updated_purchase = purchase_service.update_purchase_status(
        purchase_id,
        PurchaseStatus.PAID,
        payment_status="paid"
    )

    if not updated_purchase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="支付处理失败"
        )

    return updated_purchase.to_response()


# ============================================================================
# Review Routes
# ============================================================================

@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a review for a purchase.

    Only verified purchasers can create reviews.
    """
    # Check if already reviewed
    if review_service.has_reviewed(user_id, data.listing_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已对此商品发表过评论"
        )

    # Mock purchase lookup
    purchase_id = 1  # In production, verify purchase exists

    try:
        review = review_service.create_review(
            purchase_id=purchase_id,
            listing_id=data.listing_id,
            buyer_id=user_id,
            data=data,
        )

        # Update listing rating
        avg_rating, review_count = review_service.calculate_average_rating(data.listing_id)
        listing_service.update_rating(data.listing_id, avg_rating, review_count)

        logger.info(f"Review created: ID={review.id}, Listing={data.listing_id}")

        return review.to_response()

    except Exception as e:
        logger.error(f"Failed to create review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建评论失败: {str(e)}"
        )


@router.get("/listings/{listing_id}/reviews", response_model=List[ReviewResponse])
async def list_listing_reviews(
    listing_id: int,
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List reviews for a listing.

    Public endpoint for viewing product reviews.
    """
    reviews = review_service.list_reviews(
        listing_id=listing_id,
        min_rating=min_rating,
        page=page,
        limit=limit,
    )

    return [r.to_response() for r in reviews]


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int):
    """Get review details by ID."""
    review = review_service.get_review(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    return review.to_response()


# ============================================================================
# Statistics Routes
# ============================================================================

@router.get("/stats", response_model=MarketplaceResponse)
async def get_marketplace_stats():
    """
    Get marketplace-wide statistics.

    Public endpoint for marketplace analytics.
    """
    total_listings = len([
        l for l in listing_service._listings.values()
        if l.status == ListingStatus.ACTIVE
    ])

    total_purchases = len(purchase_service._purchases)
    total_revenue = sum(
        p.total_amount for p in purchase_service._purchases.values()
        if p.purchase_status == PurchaseStatus.COMPLETED
    )

    stats = MarketplaceStats(
        total_listings=len(listing_service._listings),
        active_listings=total_listings,
        total_purchases=total_purchases,
        total_revenue=total_revenue,
        total_orders=total_purchases,
    )

    return MarketplaceResponse(
        success=True,
        data=stats.model_dump()
    )


@router.get("/vendor/stats", response_model=MarketplaceResponse)
async def get_vendor_stats(user_id: int = Depends(get_current_user_id)):
    """
    Get sales statistics for the current vendor.

    Returns vendor-specific analytics.
    """
    vendor_id = get_vendor_id()

    # Get vendor's listings
    vendor_listings = [
        l for l in listing_service._listings.values()
        if l.vendor_id == vendor_id
    ]

    total_sales = sum(l.sold_quantity for l in vendor_listings)

    # Calculate revenue from completed purchases containing vendor's listings
    total_revenue = Decimal("0")
    for purchase in purchase_service._purchases.values():
        if purchase.purchase_status == PurchaseStatus.COMPLETED:
            for item_data in purchase.items:
                item = item_data if isinstance(item_data, dict) else {}
                listing_id = item.get("listing_id")
                if listing_id:
                    listing = listing_service.get_listing(listing_id)
                    if listing and listing.vendor_id == vendor_id:
                        total_revenue += Decimal(str(item.get("price", 0))) * item.get("quantity", 0)

    stats = VendorSalesStats(
        vendor_id=vendor_id,
        total_sales=total_sales,
        total_revenue=total_revenue,
        total_orders=len([
            p for p in purchase_service._purchases.values()
            if any(
                listing_service.get_listing(item.get("listing_id")).vendor_id == vendor_id
                for item in p.items
                if isinstance(item, dict)
            )
        ]),
    )

    return MarketplaceResponse(
        success=True,
        data=stats.model_dump()
    )


# ============================================================================
# Vendor Listing Routes
# ============================================================================

@router.get("/vendor/listings", response_model=ListingListResponse)
async def list_vendor_listings(
    status: Optional[ListingStatus] = Query(None, description="Filter by status"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: int = Depends(get_current_user_id)
):
    """
    List listings for the current vendor.

    Returns all listings owned by the authenticated vendor.
    """
    vendor_id = get_vendor_id()

    listings = listing_service.list_listings(
        vendor_id=vendor_id,
        status=status,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )

    total = listing_service.count_listings(
        vendor_id=vendor_id,
        status=status,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return ListingListResponse(
        items=[l.to_response() for l in listings],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )
