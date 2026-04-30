"""
Promotion Module
SillyMD 促销管理模块

提供优惠券、限时抢购、折扣活动等促销功能。

Usage:
    from src.modules.promotion import SillyMDModule, promotion_service, coupon_service

    # In your FastAPI app:
    promotion_module = SillyMDModule()
    promotion_module.register(app)

Module Structure:
    - config.yaml: Module configuration
    - schemas.py: Pydantic request/response models
    - services.py: Business logic layer
    - routes.py: FastAPI route handlers
    - __init__.py: Module entry point
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml

from fastapi import FastAPI
from pydantic import BaseModel

# Import components
from .schemas import (
    PromotionCreate,
    PromotionUpdate,
    PromotionResponse,
    PromotionListResponse,
    PromotionStatus,
    PromotionType,
    CouponCreate,
    CouponResponse,
    CouponValidateRequest,
    CouponValidateResponse,
    FlashSaleCreate,
    FlashSaleResponse,
    FlashSaleListResponse,
    CouponUsageResponse,
    PromotionResponseModel,
)
from .services import (
    promotion_service,
    coupon_service,
    flash_sale_service,
    PromotionService,
    CouponService,
    FlashSaleService,
)
from .routes import router as promotion_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "promotion"
    name: str = "促销管理模块"
    version: str = "1.0.0"
    description: str = "提供优惠券、限时抢购、折扣活动等促销功能"
    dependencies: List[str] = ["auth", "goods", "transaction"]


# ============================================================================
# Module Config
# ============================================================================

class CouponConfig(BaseModel):
    """Coupon configuration"""
    default_valid_days: int = 30
    max_coupons_per_user: int = 10
    allow_stacking: bool = False


class FlashSaleConfig(BaseModel):
    """Flash sale configuration"""
    max_items_per_user: int = 1
    require_identity_verification: bool = False
    auto_end_when_sold_out: bool = True


class ModuleConfig(BaseModel):
    """Module configuration"""
    coupon: CouponConfig = CouponConfig()
    flash_sale: FlashSaleConfig = FlashSaleConfig()


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Promotion Module

    Extends BaseModule pattern to integrate promotion/coupon
    management functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "promotion"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Promotion Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Promotion module initialized (v{self.info.version})")

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load module configuration from YAML file

        Args:
            config_path: Optional path to config file
        """
        if config_path is None:
            # Default to module's config.yaml
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)

                # Load module-level config
                if config_data and 'config' in config_data:
                    self.config = ModuleConfig(**config_data['config'])
                else:
                    self.config = ModuleConfig()

                logger.info(f"Loaded config from {config_path}")

            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                self.config = ModuleConfig()
        else:
            logger.warning(f"Config file not found: {config_path}")
            self.config = ModuleConfig()

    def register(self, app: FastAPI) -> None:
        """
        Register module routes with FastAPI application

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Include promotion routes
        app.include_router(promotion_router)

        logger.info(f"Promotion routes registered at {promotion_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks.
        """
        logger.info("Promotion module starting up...")

        # Initialize services with config
        if self.config:
            coupon_service._config = self.config.model_dump()
            flash_sale_service._config = self.config.model_dump()
            logger.info("Promotion module services initialized with config")

        logger.info("Promotion module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks.
        """
        logger.info("Promotion module shutting down...")

        # TODO: Save any cached data
        # TODO: Close connections

        logger.info("Promotion module shutdown complete")

    def get_routes(self) -> list:
        """
        Get list of registered routes

        Returns:
            List of route dictionaries with method, path, and handler info
        """
        if not self.app:
            return []

        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/promotions'):
                routes.append({
                    "method": getattr(route, 'methods', {'GET'}).__iter__().__next__(),
                    "path": route.path,
                    "name": getattr(route, 'name', 'unnamed')
                })

        return routes

    def get_info(self) -> Dict[str, Any]:
        """
        Get module information

        Returns:
            Dict containing module info
        """
        return {
            "id": self.info.id,
            "name": self.info.name,
            "version": self.info.version,
            "description": self.info.description,
            "dependencies": self.info.dependencies,
            "config": self.config.model_dump() if self.config else None
        }


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "PromotionService",
    "CouponService",
    "FlashSaleService",
    "promotion_service",
    "coupon_service",
    "flash_sale_service",

    # Schemas - Promotion
    "PromotionCreate",
    "PromotionUpdate",
    "PromotionResponse",
    "PromotionListResponse",
    "PromotionStatus",
    "PromotionType",

    # Schemas - Coupon
    "CouponCreate",
    "CouponResponse",
    "CouponValidateRequest",
    "CouponValidateResponse",

    # Schemas - Flash Sale
    "FlashSaleCreate",
    "FlashSaleResponse",
    "FlashSaleListResponse",

    # Schemas - Usage
    "CouponUsageResponse",

    # Schemas - Response
    "PromotionResponseModel",

    # Routes
    "router",
]
