"""
Transaction module routes for SillyMD.

This module provides FastAPI routes for order management,
settlement processing, and refund handling.
"""

from typing import Optional
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from fastapi.responses import StreamingResponse

from .schemas import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    OrderStatus,
    SettlementCreate,
    SettlementResponse,
    SettlementStatus,
    RefundRequest,
    RefundResponse,
    RefundStatus,
    RefundReject,
    PaginatedOrdersResponse,
    PaginatedSettlementsResponse,
    PaginatedRefundsResponse,
    # Admin schemas
    AdminOrderResponse,
    AdminOrderListResponse,
    AdminOrderFilters,
    AdminOrderStats,
    AdminOrderStatus,
    AdminPaymentMethod,
    AdminExpressCompany,
    UpdateOrderStatusRequest,
    ShipOrderRequest,
    BatchShipOrderRequest,
    RefundOrderRequest,
)
from .services import AdminOrderService, SettlementService, RefundService


# Initialize services
admin_order_service = AdminOrderService()
settlement_service = SettlementService()
refund_service = RefundService()

# Link services
refund_service.set_order_service(admin_order_service)

# Create router
router = APIRouter(prefix="/api/v1/transaction", tags=["transaction"])

# Create admin router
admin_router = APIRouter(prefix="/api/v1/admin/orders", tags=["Admin Orders"])


# ============ Order Routes ============

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    user_id: str = Query(..., description="User ID")
):
    """
    Create a new order.

    Args:
        order_data: Order creation data.
        user_id: The ID of the user creating the order.

    Returns:
        The created order.
    """
    order = admin_order_service.create_order(
        user_id=user_id,
        items=order_data.items,
        metadata=order_data.metadata
    )
    return order.to_response()


@router.get("/orders", response_model=PaginatedOrdersResponse)
async def list_orders(
    user_id: str = Query(..., description="User ID"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List orders for a user.

    Args:
        user_id: The ID of the user.
        status: Optional status filter.
        page: Page number (1-indexed).
        limit: Number of items per page.

    Returns:
        Paginated list of orders.
    """
    orders = admin_order_service.list_orders(
        user_id=user_id,
        status=status,
        page=page,
        limit=limit
    )
    total = admin_order_service.count_orders(user_id=user_id, status=status)
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedOrdersResponse(
        items=[order.to_response() for order in orders],
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """
    Get order details.

    Args:
        order_id: The ID of the order.

    Returns:
        The order details.
    """
    order = admin_order_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    return order.to_response()


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    update_data: OrderUpdate
):
    """
    Update order status.

    Args:
        order_id: The ID of the order.
        update_data: The status update data.

    Returns:
        The updated order.
    """
    order = admin_order_service.update_order_status(order_id, update_data.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    return order.to_response()


@router.delete("/orders/{order_id}", response_model=OrderResponse)
async def cancel_order(order_id: str):
    """
    Cancel an order.

    Args:
        order_id: The ID of the order to cancel.

    Returns:
        The cancelled order.
    """
    order = admin_order_service.cancel_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} cannot be cancelled (not in cancellable state)"
        )
    return order.to_response()


# ============ Settlement Routes ============

@router.post("/settlements", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_settlement(settlement_data: SettlementCreate):
    """
    Create a new settlement request.

    Args:
        settlement_data: Settlement creation data.

    Returns:
        The created settlement.
    """
    settlement = settlement_service.create_settlement(
        vendor_id=settlement_data.vendor_id,
        period=settlement_data.period
    )
    # Set amount if provided
    if settlement_data.amount > 0:
        settlement = settlement_service.update_settlement_amount(
            settlement.id,
            settlement_data.amount
        )
    return settlement.to_response()


@router.get("/settlements", response_model=PaginatedSettlementsResponse)
async def list_settlements(
    vendor_id: str = Query(..., description="Vendor ID"),
    status: Optional[SettlementStatus] = Query(None, description="Filter by settlement status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List settlements for a vendor.

    Args:
        vendor_id: The ID of the vendor.
        status: Optional status filter.
        page: Page number (1-indexed).
        limit: Number of items per page.

    Returns:
        Paginated list of settlements.
    """
    all_settlements = settlement_service.get_vendor_settlements(vendor_id)

    # Filter by status if provided
    if status:
        settlements = [s for s in all_settlements if s.status == status]
    else:
        settlements = all_settlements

    total = len(settlements)
    pages = math.ceil(total / limit) if total > 0 else 1

    start = (page - 1) * limit
    end = start + limit
    page_settlements = settlements[start:end]

    return PaginatedSettlementsResponse(
        items=[settlement.to_response() for settlement in page_settlements],
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.post("/settlements/{settlement_id}/process", response_model=SettlementResponse)
async def process_settlement(settlement_id: str):
    """
    Process a settlement.

    Args:
        settlement_id: The ID of the settlement to process.

    Returns:
        The processed settlement.
    """
    settlement = settlement_service.process_settlement(settlement_id)
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found or not in processable state"
        )
    return settlement.to_response()


# ============ Refund Routes ============

@router.post("/refunds", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(refund_data: RefundRequest):
    """
    Create a new refund request.

    Args:
        refund_data: Refund request data.

    Returns:
        The created refund.
    """
    refund = refund_service.create_refund(
        order_id=refund_data.order_id,
        amount=refund_data.amount,
        reason=refund_data.reason,
        items=refund_data.items
    )
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create refund. Order may not exist or is not refundable."
        )
    return refund.to_response()


@router.get("/refunds", response_model=PaginatedRefundsResponse)
async def list_refunds(
    order_id: Optional[str] = Query(None, description="Filter by order ID"),
    status: Optional[RefundStatus] = Query(None, description="Filter by refund status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List refunds with optional filtering.

    Args:
        order_id: Optional order ID filter.
        status: Optional status filter.
        page: Page number (1-indexed).
        limit: Number of items per page.

    Returns:
        Paginated list of refunds.
    """
    refunds = refund_service.list_refunds(
        order_id=order_id,
        status=status,
        page=page,
        limit=limit
    )

    # Count total (simplified - in production would be a separate query)
    all_refunds = refund_service.list_refunds(
        order_id=order_id,
        status=status,
        page=1,
        limit=10000
    )
    total = len(all_refunds)
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedRefundsResponse(
        items=[refund.to_response() for refund in refunds],
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/refunds/{refund_id}", response_model=RefundResponse)
async def get_refund(refund_id: str):
    """
    Get refund details.

    Args:
        refund_id: The ID of the refund.

    Returns:
        The refund details.
    """
    refund = refund_service.get_refund(refund_id)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund {refund_id} not found"
        )
    return refund.to_response()


@router.put("/refunds/{refund_id}/approve", response_model=RefundResponse)
async def approve_refund(
    refund_id: str,
    approved_by: str = Query(..., description="User approving the refund")
):
    """
    Approve a refund request.

    Args:
        refund_id: The ID of the refund to approve.
        approved_by: The ID of the user approving.

    Returns:
        The approved refund.
    """
    refund = refund_service.approve_refund(refund_id, approved_by)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund {refund_id} not found or not in pending state"
        )
    return refund.to_response()


@router.put("/refunds/{refund_id}/reject", response_model=RefundResponse)
async def reject_refund(
    refund_id: str,
    reject_data: RefundReject,
    rejected_by: str = Query(..., description="User rejecting the refund")
):
    """
    Reject a refund request.

    Args:
        refund_id: The ID of the refund to reject.
        reject_data: Rejection data including reason.
        rejected_by: The ID of the user rejecting.

    Returns:
        The rejected refund.
    """
    refund = refund_service.reject_refund(refund_id, reject_data.reason, rejected_by)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund {refund_id} not found or not in pending state"
        )
    return refund.to_response()


# ============================================
# Admin Order Routes
# ============================================

@admin_router.get("", response_model=AdminOrderListResponse)
async def list_admin_orders(
    status: Optional[AdminOrderStatus] = Query(None, description="Filter by order status"),
    payment_method: Optional[AdminPaymentMethod] = Query(None, description="Filter by payment method"),
    express_company: Optional[AdminExpressCompany] = Query(None, description="Filter by express company"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    keyword: Optional[str] = Query(None, description="Search keyword (order_no, receiver_name, phone)"),
    vendor_id: Optional[str] = Query(None, description="Filter by vendor ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field: created_at, final_amount, order_no"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
):
    """
    List all orders with filtering and pagination.

    Admin endpoint for order management.
    """
    from datetime import datetime

    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    filters = AdminOrderFilters(
        status=status,
        payment_method=payment_method,
        express_company=express_company,
        start_date=start_dt,
        end_date=end_dt,
        keyword=keyword,
        vendor_id=vendor_id,
    )

    orders, total = admin_order_service.list_admin_orders(
        filters=filters,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return AdminOrderListResponse(
        items=[order.to_response() for order in orders],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@admin_router.get("/stats", response_model=AdminOrderStats)
async def get_order_stats():
    """
    Get order statistics.

    Returns overview statistics for all orders.
    """
    return admin_order_service.get_order_stats()


@admin_router.get("/{order_id}", response_model=AdminOrderResponse)
async def get_admin_order(order_id: str):
    """
    Get order details by ID.

    Args:
        order_id: The order ID.

    Returns:
        Order details.
    """
    order = admin_order_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    return order.to_response()


@admin_router.get("/no/{order_no}", response_model=AdminOrderResponse)
async def get_admin_order_by_no(order_no: str):
    """
    Get order details by order number.

    Args:
        order_no: The order number.

    Returns:
        Order details.
    """
    order = admin_order_service.get_order_by_no(order_no)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_no} not found"
        )
    return order.to_response()


@admin_router.put("/{order_id}/status", response_model=AdminOrderResponse)
async def update_order_status(
    order_id: str,
    request: UpdateOrderStatusRequest,
):
    """
    Update order status.

    Args:
        order_id: The order ID.
        request: Status update request.

    Returns:
        Updated order.
    """
    order = admin_order_service.update_order_status(
        order_id,
        request.status,
        request.remark,
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    return order.to_response()


@admin_router.post("/{order_id}/ship", response_model=AdminOrderResponse)
async def ship_order(
    order_id: str,
    request: ShipOrderRequest,
):
    """
    Ship an order with tracking information.

    Args:
        order_id: The order ID.
        request: Shipping information.

    Returns:
        Updated order with shipping info.
    """
    order = admin_order_service.ship_order(
        order_id,
        request.tracking_number,
        request.express_company,
        request.remark,
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} cannot be shipped (invalid status)"
        )
    return order.to_response()


@admin_router.post("/{order_id}/refund", response_model=AdminOrderResponse)
async def refund_order(
    order_id: str,
    request: RefundOrderRequest,
):
    """
    Process refund for an order.

    Args:
        order_id: The order ID.
        request: Refund information.

    Returns:
        Updated order after refund.
    """
    from decimal import Decimal

    order = admin_order_service.refund_order(
        order_id,
        request.reason,
        request.refund_amount,
        request.remark,
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} cannot be refunded (invalid status)"
        )
    return order.to_response()


@admin_router.post("/batch-ship", response_model=AdminOrderListResponse)
async def batch_ship_orders(
    request: BatchShipOrderRequest,
):
    """
    Batch ship multiple orders with the same tracking information.

    Args:
        request: Batch shipping request.

    Returns:
        List of shipped orders.
    """
    shipped_orders = admin_order_service.batch_ship_orders(
        request.order_ids,
        request.tracking_number,
        request.express_company,
        request.remark,
    )

    return AdminOrderListResponse(
        items=[order.to_response() for order in shipped_orders],
        total=len(shipped_orders),
        page=1,
        limit=len(shipped_orders),
        pages=1,
    )


@admin_router.get("/export/download")
async def export_orders(
    status: Optional[AdminOrderStatus] = Query(None, description="Filter by order status"),
    payment_method: Optional[AdminPaymentMethod] = Query(None, description="Filter by payment method"),
    express_company: Optional[AdminExpressCompany] = Query(None, description="Filter by express company"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    vendor_id: Optional[str] = Query(None, description="Filter by vendor ID"),
    format: str = Query("json", description="Export format: json, csv"),
):
    """
    Export orders data.

    Args:
        format: Export format (json or csv).

    Returns:
        Exported orders data as file download.
    """
    from datetime import datetime

    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    filters = AdminOrderFilters(
        status=status,
        payment_method=payment_method,
        express_company=express_company,
        start_date=start_dt,
        end_date=end_dt,
        keyword=keyword,
        vendor_id=vendor_id,
    )

    export_data = admin_order_service.export_orders(filters=filters, format=format)

    if format == "csv":
        return Response(
            content=export_data["content"],
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={export_data['filename']}"
            }
        )

    # JSON format
    return {
        "success": True,
        "data": export_data["data"],
        "total": export_data["total"],
        "filename": export_data["filename"],
    }


# Import timedelta at module level
from datetime import timedelta
