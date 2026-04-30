"""
Transaction module for SillyMD.

This module provides order management, settlement processing, and refund handling
functionality for the SillyMD platform.

Modules:
    schemas: Pydantic schemas for data validation and serialization.
    services: Business logic services for orders, settlements, and refunds.
    routes: FastAPI routes for the transaction API endpoints.

Example:
    ```python
    from transaction.routes import router

    app.include_router(router)
    ```
"""

from .schemas import (
    OrderCreate,
    OrderResponse,
    OrderStatus,
    OrderUpdate,
    OrderItem,
    SettlementCreate,
    SettlementResponse,
    SettlementStatus,
    SettlementProcess,
    RefundRequest,
    RefundResponse,
    RefundStatus,
    RefundItem,
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
    ShippingAddress,
    AdminOrderItem,
)
from .services import AdminOrderService, SettlementService, RefundService, Order, Settlement, Refund
from .routes import router, admin_router


class BaseModule:
    """Base class for SillyMD modules."""

    def __init__(self, config: dict = None):
        """
        Initialize the module.

        Args:
            config: Module configuration dictionary.
        """
        self.config = config or {}
        self.id = self.config.get("id", "transaction")
        self.name = self.config.get("name", "Transaction Module")
        self.version = self.config.get("version", "1.0.0")
        self.description = self.config.get("description", "")
        self.dependencies = self.config.get("dependencies", [])

        # Initialize services
        self.admin_order_service = AdminOrderService()
        self.settlement_service = SettlementService(self.config.get("config"))
        self.refund_service = RefundService(self.config.get("config"))
        self.refund_service.set_order_service(self.admin_order_service)

        # Expose routers
        self.router = router
        self.admin_router = admin_router

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "transaction"

    @property
    def info(self):
        """Get module info."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }

    def register(self):
        """Register the module with the application."""
        pass

    def install(self, app=None):
        """Install the module (alias for register)."""
        if app is not None and hasattr(app, 'include_router'):
            # Include main router
            app.include_router(self.router)
            # Include admin router
            app.include_router(self.admin_router)
        return self.register()

    def get_routes(self):
        """Get the FastAPI router for this module."""
        return self.router

    def get_admin_routes(self):
        """Get the admin FastAPI router for this module."""
        return self.admin_router

    def get_services(self):
        """Get the services provided by this module."""
        return {
            "order_service": self.order_service,
            "settlement_service": self.settlement_service,
            "refund_service": self.refund_service,
            "admin_order_service": self.admin_order_service,
        }

    def get_config(self):
        """Get the module configuration."""
        return self.config

    def get_dependencies(self):
        """Get the module dependencies."""
        return self.dependencies

    def get_metadata(self):
        """Get module metadata."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
        }

    def initialize(self):
        """Initialize the module (called when the application starts)."""
        pass

    def shutdown(self):
        """Shutdown the module (called when the application stops)."""
        pass


__version__ = "1.0.0"
__all__ = [
    "BaseModule",
    "router",
    "admin_router",
    "schemas",
    "services",
    "OrderService",
    "SettlementService",
    "RefundService",
    "AdminOrderService",
    "Order",
    "Settlement",
    "Refund",
    # Admin schemas
    "AdminOrderResponse",
    "AdminOrderListResponse",
    "AdminOrderFilters",
    "AdminOrderStats",
    "AdminOrderStatus",
    "AdminPaymentMethod",
    "AdminExpressCompany",
    "UpdateOrderStatusRequest",
    "ShipOrderRequest",
    "BatchShipOrderRequest",
    "RefundOrderRequest",
    "ShippingAddress",
    "AdminOrderItem",
]
