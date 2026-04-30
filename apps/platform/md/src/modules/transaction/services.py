"""
Transaction module services for SillyMD.

This module provides service classes for order management,
settlement processing, and refund handling.
"""

import uuid
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from io import BytesIO

from .schemas import (
    OrderCreate,
    OrderResponse,
    OrderStatus,
    OrderItem,
    SettlementCreate,
    SettlementResponse,
    SettlementStatus,
    RefundRequest,
    RefundResponse,
    RefundStatus,
    RefundItem,
    # Admin schemas
    AdminOrderResponse,
    AdminOrderItem,
    AdminOrderStatus,
    AdminPaymentMethod,
    AdminOrderFilters,
    AdminOrderStats,
    UpdateOrderStatusRequest,
    ShipOrderRequest,
    BatchShipOrderRequest,
    RefundOrderRequest,
    ShippingAddress,
)

logger = logging.getLogger(__name__)


class Order:
    """Order model."""

    def __init__(
        self,
        id: str,
        user_id: str,
        items: List[Dict],
        status: OrderStatus,
        total_amount: Decimal,
        currency: str,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.items = items
        self.status = status
        self.total_amount = total_amount
        self.currency = currency
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_response(self) -> OrderResponse:
        """Convert to OrderResponse schema."""
        return OrderResponse(
            id=self.id,
            user_id=self.user_id,
            items=[OrderItem(**item) for item in self.items],
            status=self.status,
            total_amount=self.total_amount,
            currency=self.currency,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class Settlement:
    """Settlement model."""

    def __init__(
        self,
        id: str,
        vendor_id: str,
        amount: Decimal,
        status: SettlementStatus,
        period: str,
        created_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
    ):
        self.id = id
        self.vendor_id = vendor_id
        self.amount = amount
        self.status = status
        self.period = period
        self.created_at = created_at or datetime.utcnow()
        self.processed_at = processed_at

    def to_response(self) -> SettlementResponse:
        """Convert to SettlementResponse schema."""
        return SettlementResponse(
            id=self.id,
            vendor_id=self.vendor_id,
            amount=self.amount,
            status=self.status,
            period=self.period,
            created_at=self.created_at,
            processed_at=self.processed_at,
        )


class Refund:
    """Refund model."""

    def __init__(
        self,
        id: str,
        order_id: str,
        amount: Decimal,
        status: RefundStatus,
        reason: str,
        items: Optional[List[Dict]] = None,
        created_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
        processed_by: Optional[str] = None,
        rejection_reason: Optional[str] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.status = status
        self.reason = reason
        self.items = items or []
        self.created_at = created_at or datetime.utcnow()
        self.processed_at = processed_at
        self.processed_by = processed_by
        self.rejection_reason = rejection_reason

    def to_response(self) -> RefundResponse:
        """Convert to RefundResponse schema."""
        return RefundResponse(
            id=self.id,
            order_id=self.order_id,
            amount=self.amount,
            status=self.status,
            reason=self.reason,
            items=[RefundItem(**item) for item in self.items] if self.items else None,
            created_at=self.created_at,
            processed_at=self.processed_at,
            processed_by=self.processed_by,
            rejection_reason=self.rejection_reason,
        )


# ============================================
# Admin Order Models and Service
# ============================================

class AdminOrder:
    """Admin order model for backend order management."""

    def __init__(
        self,
        id: str,
        order_no: str,
        user_id: str,
        items: List[Dict[str, Any]],
        total_amount: Decimal,
        discount_amount: Decimal = Decimal("0"),
        shipping_amount: Decimal = Decimal("0"),
        final_amount: Optional[Decimal] = None,
        status: AdminOrderStatus = AdminOrderStatus.PENDING,
        shipping_address: Optional[Dict[str, Any]] = None,
        tracking_number: Optional[str] = None,
        express_company: Optional[str] = None,
        payment_method: Optional[str] = None,
        payment_id: Optional[str] = None,
        paid_at: Optional[datetime] = None,
        shipped_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None,
        remark: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        # Metadata fields
        user_name: Optional[str] = None,
        user_phone: Optional[str] = None,
        vendor_id: Optional[str] = None,
        vendor_name: Optional[str] = None,
    ):
        self.id = id
        self.order_no = order_no
        self.user_id = user_id
        self.user_name = user_name
        self.user_phone = user_phone
        self.vendor_id = vendor_id
        self.vendor_name = vendor_name
        self.items = items
        self.total_amount = total_amount
        self.discount_amount = discount_amount
        self.shipping_amount = shipping_amount
        self.final_amount = final_amount if final_amount is not None else total_amount
        self.status = status
        self.shipping_address = shipping_address
        self.tracking_number = tracking_number
        self.express_company = express_company
        self.payment_method = payment_method
        self.payment_id = payment_id
        self.paid_at = paid_at
        self.shipped_at = shipped_at
        self.delivered_at = delivered_at
        self.remark = remark
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_response(self) -> AdminOrderResponse:
        """Convert to AdminOrderResponse schema."""
        order_items = [
            AdminOrderItem(
                id=str(uuid.uuid4()),
                product_id=item.get("product_id", ""),
                product_name=item.get("product_name", "Unknown Product"),
                product_image=item.get("product_image"),
                sku=item.get("sku"),
                quantity=item.get("quantity", 1),
                unit_price=Decimal(str(item.get("unit_price", "0"))),
                subtotal=Decimal(str(item.get("subtotal", "0"))),
            )
            for item in self.items
        ]

        return AdminOrderResponse(
            id=self.id,
            order_no=self.order_no,
            user_id=self.user_id,
            user_name=self.user_name,
            user_phone=self.user_phone,
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            items=order_items,
            total_amount=self.total_amount,
            discount_amount=self.discount_amount,
            shipping_amount=self.shipping_amount,
            final_amount=self.final_amount,
            status=self.status,
            shipping_address=self.shipping_address,
            tracking_number=self.tracking_number,
            express_company=self.express_company,
            payment_method=self.payment_method,
            payment_id=self.payment_id,
            paid_at=self.paid_at,
            shipped_at=self.shipped_at,
            delivered_at=self.delivered_at,
            remark=self.remark,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class AdminOrderService:
    """Service for admin order management."""

    def __init__(self):
        self._orders: Dict[str, AdminOrder] = {}
        self._order_no_index: Dict[str, str] = {}  # order_no -> order_id
        self._user_index: Dict[str, List[str]] = {}  # user_id -> list of order_ids
        self._status_index: Dict[AdminOrderStatus, List[str]] = {}  # status -> list of order_ids
        self._next_id: int = 1
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize sample data for testing."""
        sample_orders = [
            {
                "order_no": "ORD202401150001",
                "user_id": "user_001",
                "user_name": "Zhang San",
                "user_phone": "13800138001",
                "vendor_id": "vendor_001",
                "vendor_name": "Test Store",
                "status": AdminOrderStatus.PAID,
                "total_amount": Decimal("299.00"),
                "final_amount": Decimal("299.00"),
                "payment_method": "balance",
                "paid_at": datetime.utcnow() - timedelta(hours=2),
            },
            {
                "order_no": "ORD202401150002",
                "user_id": "user_002",
                "user_name": "Li Si",
                "user_phone": "13900139002",
                "vendor_id": "vendor_001",
                "vendor_name": "Test Store",
                "status": AdminOrderStatus.PROCESSING,
                "total_amount": Decimal("599.00"),
                "shipping_amount": Decimal("10.00"),
                "final_amount": Decimal("609.00"),
                "payment_method": "alipay",
                "paid_at": datetime.utcnow() - timedelta(hours=5),
            },
            {
                "order_no": "ORD202401150003",
                "user_id": "user_003",
                "user_name": "Wang Wu",
                "user_phone": "13700137003",
                "vendor_id": "vendor_002",
                "vendor_name": "Smart Shop",
                "status": AdminOrderStatus.SHIPPED,
                "total_amount": Decimal("899.00"),
                "shipping_amount": Decimal("15.00"),
                "final_amount": Decimal("914.00"),
                "payment_method": "wechat",
                "paid_at": datetime.utcnow() - timedelta(days=1),
                "shipped_at": datetime.utcnow() - timedelta(hours=6),
                "tracking_number": "SF1234567890",
                "express_company": "sf",
                "shipping_address": {
                    "receiver_name": "Wang Wu",
                    "phone": "13700137003",
                    "province": "Guangdong",
                    "city": "Shenzhen",
                    "district": "Nanshan",
                    "address": "Tech Park Building A, 123 Software Road",
                    "postal_code": "518000"
                }
            },
            {
                "order_no": "ORD202401150004",
                "user_id": "user_001",
                "user_name": "Zhang San",
                "user_phone": "13800138001",
                "vendor_id": "vendor_001",
                "vendor_name": "Test Store",
                "status": AdminOrderStatus.PENDING,
                "total_amount": Decimal("199.00"),
                "final_amount": Decimal("199.00"),
                "payment_method": "balance",
            },
            {
                "order_no": "ORD202401150005",
                "user_id": "user_004",
                "user_name": "Zhao Liu",
                "user_phone": "13600136004",
                "vendor_id": "vendor_002",
                "vendor_name": "Smart Shop",
                "status": AdminOrderStatus.DELIVERED,
                "total_amount": Decimal("1299.00"),
                "shipping_amount": Decimal("20.00"),
                "final_amount": Decimal("1319.00"),
                "payment_method": "bank",
                "paid_at": datetime.utcnow() - timedelta(days=3),
                "shipped_at": datetime.utcnow() - timedelta(days=2),
                "delivered_at": datetime.utcnow() - timedelta(days=1),
                "tracking_number": "YT9876543210",
                "express_company": "yto",
                "shipping_address": {
                    "receiver_name": "Zhao Liu",
                    "phone": "13600136004",
                    "province": "Guangdong",
                    "city": "Guangzhou",
                    "district": "Tianhe",
                    "address": "Shopping Mall, 888 Sports Road",
                    "postal_code": "510000"
                }
            },
            {
                "order_no": "ORD202401150006",
                "user_id": "user_005",
                "user_name": "Chen Qi",
                "user_phone": "13500135005",
                "vendor_id": "vendor_001",
                "vendor_name": "Test Store",
                "status": AdminOrderStatus.COMPLETED,
                "total_amount": Decimal("459.00"),
                "discount_amount": Decimal("50.00"),
                "shipping_amount": Decimal("10.00"),
                "final_amount": Decimal("419.00"),
                "payment_method": "alipay",
                "paid_at": datetime.utcnow() - timedelta(days=5),
                "shipped_at": datetime.utcnow() - timedelta(days=4),
                "delivered_at": datetime.utcnow() - timedelta(days=2),
                "tracking_number": "ZTO123123123",
                "express_company": "zto",
                "shipping_address": {
                    "receiver_name": "Chen Qi",
                    "phone": "13500135005",
                    "province": "Shanghai",
                    "city": "Shanghai",
                    "district": "Pudong",
                    "address": "Business Center, 999 Century Avenue",
                    "postal_code": "200000"
                }
            },
            {
                "order_no": "ORD202401150007",
                "user_id": "user_006",
                "user_name": "Liu Ba",
                "user_phone": "13400134006",
                "vendor_id": "vendor_003",
                "vendor_name": "Fashion House",
                "status": AdminOrderStatus.CANCELLED,
                "total_amount": Decimal("799.00"),
                "final_amount": Decimal("799.00"),
                "payment_method": "wechat",
                "paid_at": datetime.utcnow() - timedelta(days=1),
                "remark": "Customer requested cancellation",
            },
            {
                "order_no": "ORD202401150008",
                "user_id": "user_007",
                "user_name": "Zhou Jiu",
                "user_phone": "13300133007",
                "vendor_id": "vendor_002",
                "vendor_name": "Smart Shop",
                "status": AdminOrderStatus.REFUNDED,
                "total_amount": Decimal("599.00"),
                "final_amount": Decimal("599.00"),
                "payment_method": "balance",
                "paid_at": datetime.utcnow() - timedelta(days=3),
                "remark": "Product quality issue - full refund",
            },
        ]

        sample_items = [
            {"product_id": "prod_001", "product_name": "Wireless Mouse", "quantity": 1, "unit_price": "99.00", "subtotal": "99.00"},
            {"product_id": "prod_002", "product_name": "Mechanical Keyboard", "quantity": 1, "unit_price": "299.00", "subtotal": "299.00"},
            {"product_id": "prod_003", "product_name": "USB-C Hub", "quantity": 2, "unit_price": "150.00", "subtotal": "300.00"},
            {"product_id": "prod_004", "product_name": "Monitor Stand", "quantity": 1, "unit_price": "199.00", "subtotal": "199.00"},
            {"product_id": "prod_005", "product_name": "Laptop Bag", "quantity": 1, "unit_price": "299.00", "subtotal": "299.00"},
            {"product_id": "prod_006", "product_name": "Wireless Charger", "quantity": 3, "unit_price": "89.00", "subtotal": "267.00"},
        ]

        for i, order_data in enumerate(sample_orders):
            order_id = str(uuid.uuid4())
            order_no = order_data.pop("order_no")

            # Assign different items based on order
            if i % 3 == 0:
                items = [sample_items[0], sample_items[1]]
            elif i % 3 == 1:
                items = [sample_items[2], sample_items[3]]
            else:
                items = [sample_items[4], sample_items[5]]

            order = AdminOrder(
                id=order_id,
                order_no=order_no,
                items=items,
                created_at=datetime.utcnow() - timedelta(days=7-i) + timedelta(hours=i),
                **order_data
            )

            self._orders[order_id] = order
            self._order_no_index[order_no] = order_id

            # Update indexes
            if order.user_id not in self._user_index:
                self._user_index[order.user_id] = []
            self._user_index[order.user_id].append(order_id)

            if order.status not in self._status_index:
                self._status_index[order.status] = []
            self._status_index[order.status].append(order_id)

            self._next_id += 1

        logger.info(f"Initialized {len(self._orders)} sample orders")

    def _generate_order_no(self) -> str:
        """Generate a unique order number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_part = str(uuid.uuid4())[:6].upper()
        return f"ORD{timestamp}{unique_part}"

    def create_order(self, user_id: str, items: List[Dict], **kwargs) -> AdminOrder:
        """Create a new admin order."""
        total_amount = sum(Decimal(str(item.get("subtotal", "0"))) for item in items)
        final_amount = kwargs.get("final_amount", total_amount)

        order = AdminOrder(
            id=str(uuid.uuid4()),
            order_no=self._generate_order_no(),
            user_id=user_id,
            items=items,
            total_amount=total_amount,
            discount_amount=kwargs.get("discount_amount", Decimal("0")),
            shipping_amount=kwargs.get("shipping_amount", Decimal("0")),
            final_amount=final_amount,
            status=AdminOrderStatus.PENDING,
            shipping_address=kwargs.get("shipping_address"),
            payment_method=kwargs.get("payment_method"),
            user_name=kwargs.get("user_name"),
            user_phone=kwargs.get("user_phone"),
            vendor_id=kwargs.get("vendor_id"),
            vendor_name=kwargs.get("vendor_name"),
        )

        self._orders[order.id] = order
        self._order_no_index[order.order_no] = order.id

        # Update indexes
        if order.user_id not in self._user_index:
            self._user_index[order.user_id] = []
        self._user_index[order.user_id].append(order.id)

        if order.status not in self._status_index:
            self._status_index[order.status] = []
        self._status_index[order.status].append(order.id)

        logger.info(f"Order created: {order.order_no}")
        return order

    def get_order(self, order_id: str) -> Optional[AdminOrder]:
        """Get an order by ID."""
        return self._orders.get(order_id)

    def get_order_by_no(self, order_no: str) -> Optional[AdminOrder]:
        """Get an order by order number."""
        order_id = self._order_no_index.get(order_no)
        if order_id:
            return self._orders.get(order_id)
        return None

    def list_admin_orders(
        self,
        filters: Optional[AdminOrderFilters] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[AdminOrder], int]:
        """
        List orders with filters and pagination.

        Args:
            filters: Filter criteria
            page: Page number (1-indexed)
            limit: Items per page
            sort_by: Sort field
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (orders list, total count)
        """
        orders = list(self._orders.values())

        # Apply filters
        if filters:
            if filters.status:
                orders = [o for o in orders if o.status == filters.status]

            if filters.payment_method:
                orders = [o for o in orders if o.payment_method == filters.payment_method]

            if filters.express_company:
                orders = [o for o in orders if o.express_company == filters.express_company]

            if filters.start_date:
                orders = [o for o in orders if o.created_at >= filters.start_date]

            if filters.end_date:
                orders = [o for o in orders if o.created_at <= filters.end_date]

            if filters.keyword:
                keyword = filters.keyword.lower()
                orders = [
                    o for o in orders
                    if keyword in o.order_no.lower() or
                       (o.user_name and keyword in o.user_name.lower()) or
                       (o.user_phone and keyword in o.user_phone)
                ]

            if filters.vendor_id:
                orders = [o for o in orders if o.vendor_id == filters.vendor_id]

        # Sort
        reverse = sort_order.lower() == "desc"
        if sort_by == "created_at":
            orders.sort(key=lambda o: o.created_at, reverse=reverse)
        elif sort_by == "final_amount":
            orders.sort(key=lambda o: float(o.final_amount), reverse=reverse)
        elif sort_by == "order_no":
            orders.sort(key=lambda o: o.order_no, reverse=reverse)
        else:
            orders.sort(key=lambda o: o.created_at, reverse=reverse)

        total = len(orders)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        return orders[start:end], total

    def count_orders(self, filters: Optional[AdminOrderFilters] = None) -> int:
        """Count orders matching filters."""
        orders, total = self.list_orders(filters=filters, page=1, limit=100000)
        return total

    def update_order_status(
        self,
        order_id: str,
        new_status: AdminOrderStatus,
        remark: Optional[str] = None
    ) -> Optional[AdminOrder]:
        """Update order status."""
        order = self._orders.get(order_id)
        if not order:
            return None

        # Update status index
        if order.status in self._status_index:
            if order_id in self._status_index[order.status]:
                self._status_index[order.status].remove(order_id)

        order.status = new_status
        order.updated_at = datetime.utcnow()

        if remark:
            order.remark = remark

        # Update timestamps based on status
        if new_status == AdminOrderStatus.PAID and not order.paid_at:
            order.paid_at = datetime.utcnow()
        elif new_status == AdminOrderStatus.SHIPPED and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif new_status == AdminOrderStatus.DELIVERED and not order.delivered_at:
            order.delivered_at = datetime.utcnow()

        # Add to new status index
        if new_status not in self._status_index:
            self._status_index[new_status] = []
        self._status_index[new_status].append(order_id)

        logger.info(f"Order {order.order_no} status updated to {new_status}")
        return order

    def ship_order(
        self,
        order_id: str,
        tracking_number: str,
        express_company: str,
        remark: Optional[str] = None
    ) -> Optional[AdminOrder]:
        """Ship an order with tracking info."""
        order = self._orders.get(order_id)
        if not order:
            return None

        # Validate order status
        if order.status not in [AdminOrderStatus.PAID, AdminOrderStatus.PROCESSING]:
            logger.warning(f"Cannot ship order {order.order_no} with status {order.status}")
            return None

        # Update status index
        if order.status in self._status_index:
            if order_id in self._status_index[order.status]:
                self._status_index[order.status].remove(order_id)

        order.tracking_number = tracking_number
        order.express_company = express_company
        order.status = AdminOrderStatus.SHIPPED
        order.shipped_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()

        if remark:
            order.remark = remark

        # Add to new status index
        if AdminOrderStatus.SHIPPED not in self._status_index:
            self._status_index[AdminOrderStatus.SHIPPED] = []
        self._status_index[AdminOrderStatus.SHIPPED].append(order_id)

        logger.info(f"Order {order.order_no} shipped with tracking {tracking_number}")
        return order

    def batch_ship_orders(
        self,
        order_ids: List[str],
        tracking_number: str,
        express_company: str,
        remark: Optional[str] = None
    ) -> List[AdminOrder]:
        """Batch ship multiple orders."""
        shipped_orders = []

        for order_id in order_ids:
            order = self.ship_order(order_id, tracking_number, express_company, remark)
            if order:
                shipped_orders.append(order)

        logger.info(f"Batch shipped {len(shipped_orders)} orders")
        return shipped_orders

    def refund_order(
        self,
        order_id: str,
        reason: str,
        refund_amount: Optional[Decimal] = None,
        remark: Optional[str] = None
    ) -> Optional[AdminOrder]:
        """Process refund for an order."""
        order = self._orders.get(order_id)
        if not order:
            return None

        # Validate order status
        if order.status not in [
            AdminOrderStatus.PAID,
            AdminOrderStatus.PROCESSING,
            AdminOrderStatus.SHIPPED,
            AdminOrderStatus.DELIVERED
        ]:
            logger.warning(f"Cannot refund order {order.order_no} with status {order.status}")
            return None

        # Update status index
        if order.status in self._status_index:
            if order_id in self._status_index[order.status]:
                self._status_index[order.status].remove(order_id)

        # Determine refund type (full or partial)
        is_partial = refund_amount is not None and refund_amount < order.final_amount

        if is_partial:
            order.status = AdminOrderStatus.PARTIAL_REFUND
        else:
            order.status = AdminOrderStatus.REFUNDED

        order.updated_at = datetime.utcnow()

        refund_remark = f"Refund reason: {reason}"
        if refund_amount:
            refund_remark += f", Amount: {refund_amount}"
        if remark:
            refund_remark += f". {remark}"
        order.remark = refund_remark

        # Add to new status index
        new_status = AdminOrderStatus.PARTIAL_REFUND if is_partial else AdminOrderStatus.REFUNDED
        if new_status not in self._status_index:
            self._status_index[new_status] = []
        self._status_index[new_status].append(order_id)

        logger.info(f"Order {order.order_no} refunded ({'partial' if is_partial else 'full'})")
        return order

    def get_order_stats(self) -> AdminOrderStats:
        """Get order statistics."""
        orders = list(self._orders.values())

        stats = AdminOrderStats()
        stats.total_orders = len(orders)
        stats.total_amount = sum(o.final_amount for o in orders)

        for order in orders:
            if order.status == AdminOrderStatus.PENDING:
                stats.pending_orders += 1
            elif order.status == AdminOrderStatus.PAID:
                stats.paid_orders += 1
            elif order.status == AdminOrderStatus.SHIPPED:
                stats.shipped_orders += 1
            elif order.status == AdminOrderStatus.DELIVERED:
                stats.delivered_orders += 1
            elif order.status == AdminOrderStatus.COMPLETED:
                stats.completed_orders += 1
            elif order.status == AdminOrderStatus.CANCELLED:
                stats.cancelled_orders += 1
            elif order.status == AdminOrderStatus.REFUNDED:
                stats.refunded_orders += 1
                stats.total_refunds += order.final_amount

            # Calculate revenue from completed/delivered orders
            if order.status in [AdminOrderStatus.COMPLETED, AdminOrderStatus.DELIVERED]:
                stats.total_revenue += order.final_amount

        return stats

    def export_orders(
        self,
        filters: Optional[AdminOrderFilters] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export orders data.

        Args:
            filters: Filter criteria
            format: Export format (json/csv)

        Returns:
            Export data
        """
        orders, total = self.list_orders(filters=filters, page=1, limit=100000)

        if format == "csv":
            # Generate CSV content
            csv_lines = ["Order No,User ID,User Name,Status,Total Amount,Final Amount,Payment Method,Created At,Paid At,Shipped At,Tracking Number,Express Company"]

            for order in orders:
                csv_lines.append(",".join([
                    order.order_no,
                    order.user_id,
                    order.user_name or "",
                    order.status.value,
                    str(order.total_amount),
                    str(order.final_amount),
                    order.payment_method or "",
                    order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    order.paid_at.strftime("%Y-%m-%d %H:%M:%S") if order.paid_at else "",
                    order.shipped_at.strftime("%Y-%m-%d %H:%M:%S") if order.shipped_at else "",
                    order.tracking_number or "",
                    order.express_company or ""
                ]))

            return {
                "format": "csv",
                "content": "\n".join(csv_lines),
                "filename": f"orders_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                "total": total
            }

        # Default to JSON format
        return {
            "format": "json",
            "data": [order.to_response().model_dump() for order in orders],
            "filename": f"orders_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
            "total": total
        }
    """Service for managing orders."""

    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def create_order(self, user_id: str, items: List[OrderItem], metadata: Optional[Dict[str, Any]] = None) -> Order:
        """
        Create a new order.

        Args:
            user_id: The ID of the user creating the order.
            items: List of order items.
            metadata: Optional metadata for the order.

        Returns:
            The created Order instance.
        """
        total_amount = sum((item.subtotal for item in items), Decimal("0"))

        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            items=[item.model_dump() for item in items],
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            currency="CNY",
            metadata=metadata,
        )

        self._orders[order.id] = order
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get an order by ID.

        Args:
            order_id: The ID of the order to retrieve.

        Returns:
            The Order instance if found, None otherwise.
        """
        return self._orders.get(order_id)

    def list_orders(
        self,
        user_id: str,
        status: Optional[OrderStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Order]:
        """
        List orders for a user with optional filtering.

        Args:
            user_id: The ID of the user.
            status: Optional status filter.
            page: Page number (1-indexed).
            limit: Number of items per page.

        Returns:
            List of Order instances.
        """
        orders = [
            order for order in self._orders.values()
            if order.user_id == user_id
            and (status is None or order.status == status)
        ]

        orders.sort(key=lambda x: x.created_at, reverse=True)

        start = (page - 1) * limit
        end = start + limit
        return orders[start:end]

    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        """
        Update the status of an order.

        Args:
            order_id: The ID of the order to update.
            status: The new status.

        Returns:
            The updated Order instance if found, None otherwise.
        """
        order = self._orders.get(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
        return order

    def cancel_order(self, order_id: str) -> Optional[Order]:
        """
        Cancel an order.

        Args:
            order_id: The ID of the order to cancel.

        Returns:
            The cancelled Order instance if found, None otherwise.
        """
        order = self._orders.get(order_id)
        if order and order.status in [OrderStatus.PENDING, OrderStatus.PAID]:
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.utcnow()
            return order
        return None

    def count_orders(
        self,
        user_id: str,
        status: Optional[OrderStatus] = None
    ) -> int:
        """Count orders matching the criteria."""
        return len([
            order for order in self._orders.values()
            if order.user_id == user_id
            and (status is None or order.status == status)
        ])


class SettlementService:
    """Service for managing settlements."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._settlements: Dict[str, Settlement] = {}
        self._config = config or {}
        self._settlement_config = self._config.get("settlement", {})
        self._min_settlement_amount = Decimal(str(self._settlement_config.get("min_settlement_amount", 100)))

    def create_settlement(self, vendor_id: str, period: str) -> Settlement:
        """
        Create a new settlement request.

        Args:
            vendor_id: The ID of the vendor.
            period: The settlement period (e.g., '2024-01').

        Returns:
            The created Settlement instance.
        """
        settlement = Settlement(
            id=str(uuid.uuid4()),
            vendor_id=vendor_id,
            amount=Decimal("0"),
            status=SettlementStatus.PENDING,
            period=period,
        )

        self._settlements[settlement.id] = settlement
        return settlement

    def process_settlement(self, settlement_id: str) -> Optional[Settlement]:
        """
        Process a settlement.

        Args:
            settlement_id: The ID of the settlement to process.

        Returns:
            The processed Settlement instance if found, None otherwise.
        """
        settlement = self._settlements.get(settlement_id)
        if settlement and settlement.status == SettlementStatus.PENDING:
            if settlement.amount >= self._min_settlement_amount:
                settlement.status = SettlementStatus.PROCESSING
                # Simulate processing completion
                settlement.status = SettlementStatus.COMPLETED
                settlement.processed_at = datetime.utcnow()
                return settlement
            else:
                settlement.status = SettlementStatus.FAILED
                return settlement
        return None

    def get_vendor_settlements(self, vendor_id: str) -> List[Settlement]:
        """
        Get all settlements for a vendor.

        Args:
            vendor_id: The ID of the vendor.

        Returns:
            List of Settlement instances for the vendor.
        """
        settlements = [
            settlement for settlement in self._settlements.values()
            if settlement.vendor_id == vendor_id
        ]
        settlements.sort(key=lambda x: x.created_at, reverse=True)
        return settlements

    def get_settlement(self, settlement_id: str) -> Optional[Settlement]:
        """Get a settlement by ID."""
        return self._settlements.get(settlement_id)

    def update_settlement_amount(self, settlement_id: str, amount: Decimal) -> Optional[Settlement]:
        """Update the amount of a settlement."""
        settlement = self._settlements.get(settlement_id)
        if settlement:
            settlement.amount = amount
        return settlement


class RefundService:
    """Service for managing refunds."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._refunds: Dict[str, Refund] = {}
        self._orders: Dict[str, Order] = {}
        self._config = config or {}
        self._refund_config = self._config.get("refund", {})
        self._allow_partial = self._refund_config.get("allow_partial", True)
        self._max_refund_days = self._refund_config.get("max_refund_days", 30)

    def set_order_service(self, order_service: AdminOrderService):
        """Set the order service reference."""
        self._order_service = order_service

    def create_refund(
        self,
        order_id: str,
        amount: Decimal,
        reason: str,
        items: Optional[List[RefundItem]] = None
    ) -> Optional[Refund]:
        """
        Create a new refund request.

        Args:
            order_id: The ID of the order to refund.
            amount: The amount to refund.
            reason: The reason for the refund.
            items: Optional list of specific items to refund.

        Returns:
            The created Refund instance if successful, None otherwise.
        """
        # Check if order exists and is refundable
        order = self._order_service.get_order(order_id) if hasattr(self, "_order_service") else None

        if not order:
            # Try to find in local cache
            order = self._orders.get(order_id)

        if not order:
            return None

        # Check if order is in a refundable status
        if order.status not in [OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.COMPLETED]:
            return None

        # Check refund eligibility (within max days)
        days_since_creation = (datetime.utcnow() - order.created_at).days
        if days_since_creation > self._max_refund_days:
            return None

        # Validate amount
        if amount <= 0 or amount > order.total_amount:
            return None

        # Create refund
        refund = Refund(
            id=str(uuid.uuid4()),
            order_id=order_id,
            amount=amount,
            status=RefundStatus.PENDING,
            reason=reason,
            items=[item.model_dump() for item in items] if items else None,
        )

        self._refunds[refund.id] = refund
        return refund

    def approve_refund(self, refund_id: str, approved_by: Optional[str] = None) -> Optional[Refund]:
        """
        Approve a refund request.

        Args:
            refund_id: The ID of the refund to approve.
            approved_by: The ID of the user approving the refund.

        Returns:
            The approved Refund instance if found, None otherwise.
        """
        refund = self._refunds.get(refund_id)
        if refund and refund.status == RefundStatus.PENDING:
            refund.status = RefundStatus.APPROVED
            refund.processed_at = datetime.utcnow()
            refund.processed_by = approved_by

            # Update order status if using local order cache
            order = self._orders.get(refund.order_id)
            if order:
                order.status = OrderStatus.REFUNDED

            return refund
        return None

    def reject_refund(self, refund_id: str, reason: str, rejected_by: Optional[str] = None) -> Optional[Refund]:
        """
        Reject a refund request.

        Args:
            refund_id: The ID of the refund to reject.
            reason: The reason for rejection.
            rejected_by: The ID of the user rejecting the refund.

        Returns:
            The rejected Refund instance if found, None otherwise.
        """
        refund = self._refunds.get(refund_id)
        if refund and refund.status == RefundStatus.PENDING:
            refund.status = RefundStatus.REJECTED
            refund.processed_at = datetime.utcnow()
            refund.processed_by = rejected_by
            refund.rejection_reason = reason
            return refund
        return None

    def get_refund(self, refund_id: str) -> Optional[Refund]:
        """Get a refund by ID."""
        return self._refunds.get(refund_id)

    def list_refunds(
        self,
        order_id: Optional[str] = None,
        status: Optional[RefundStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Refund]:
        """
        List refunds with optional filtering.

        Args:
            order_id: Optional order ID filter.
            status: Optional status filter.
            page: Page number (1-indexed).
            limit: Number of items per page.

        Returns:
            List of Refund instances.
        """
        refunds = [
            refund for refund in self._refunds.values()
            if (order_id is None or refund.order_id == order_id)
            and (status is None or refund.status == status)
        ]

        refunds.sort(key=lambda x: x.created_at, reverse=True)

        start = (page - 1) * limit
        end = start + limit
        return refunds[start:end]
