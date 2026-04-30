"""
Goods Module
SillyMD Goods/Product Management Module

Provides product CRUD operations, publish/unpublish workflow,
and category management for the marketplace.

Usage:
    from src.modules.goods import SillyMDModule, product_service, category_service

    # In your FastAPI app:
    goods_module = SillyMDModule()
    goods_module.register(app)

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
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductStatus,
    ProductType,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
    GoodsResponse,
)
from .services import (
    product_service,
    category_service,
    ProductService,
    CategoryService,
)
from .routes import router as goods_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "goods"
    name: str = "商品管理模块"
    version: str = "1.0.0"
    description: str = "提供商品发布、编辑、上下架管理功能"
    dependencies: List[str] = ["auth", "vendor", "storage"]


# ============================================================================
# Module Config
# ============================================================================

class PaginationConfig(BaseModel):
    """Pagination configuration"""
    default_page_size: int = 20
    max_page_size: int = 100


class UploadConfig(BaseModel):
    """Upload configuration"""
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]


class ReviewConfig(BaseModel):
    """Review configuration"""
    require_review: bool = False
    auto_approve_vendor_tier: Optional[str] = "premium"


class ModuleConfig(BaseModel):
    """Module configuration"""
    pagination: PaginationConfig = PaginationConfig()
    upload: UploadConfig = UploadConfig()
    review: ReviewConfig = ReviewConfig()


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Goods Module

    Extends BaseModule pattern to integrate goods/product
    management functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "goods"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Goods Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Goods module initialized (v{self.info.version})")

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

        # Include goods routes
        app.include_router(goods_router)

        logger.info(f"Goods routes registered at {goods_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks.
        """
        logger.info("Goods module starting up...")

        # Initialize services with config
        if self.config:
            product_service._config = self.config.model_dump()
            logger.info("Goods module services initialized with config")

        logger.info("Goods module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks.
        """
        logger.info("Goods module shutting down...")

        # TODO: Save any cached data
        # TODO: Close connections

        logger.info("Goods module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/goods'):
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
    "ProductService",
    "CategoryService",
    "product_service",
    "category_service",

    # Schemas - Products
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    "ProductStatus",
    "ProductType",

    # Schemas - Categories
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryTreeResponse",

    # Schemas - Response
    "GoodsResponse",

    # Routes
    "router",
]
