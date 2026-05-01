"""
Marketplace Module
SillyMD Marketplace Module

Provides marketplace listings, purchases, and review management
for the SillyMD platform.

Usage:
    from src.modules.marketplace import SillyMDModule, listing_service, purchase_service

    # In your FastAPI app:
    marketplace_module = SillyMDModule()
    marketplace_module.register(app)

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

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template
from pydantic import BaseModel

# Import components
from .schemas import (
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    ListingListResponse,
    ListingStatus,
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
from .routes import router as marketplace_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "marketplace"
    name: str = "交易市场模块"
    version: str = "1.0.0"
    description: str = "提供商品上架、浏览、搜索、购买功能"
    dependencies: List[str] = ["auth", "goods", "transaction"]


# ============================================================================
# Module Config
# ============================================================================

class ListingConfig(BaseModel):
    """Listing configuration"""
    max_per_vendor: int = 100
    featured_limit: int = 20
    search_results_limit: int = 100


class PurchaseConfig(BaseModel):
    """Purchase configuration"""
    allow_oversell: bool = False
    max_quantity_per_order: int = 99


class PaymentConfig(BaseModel):
    """Payment configuration"""
    escrow_enabled: bool = True
    release_on_delivery: bool = True


class ReviewConfig(BaseModel):
    """Review configuration"""
    allow_review: bool = True
    review_window_days: int = 14


class ModuleConfig(BaseModel):
    """Module configuration"""
    listing: ListingConfig = ListingConfig()
    purchase: PurchaseConfig = PurchaseConfig()
    payment: PaymentConfig = PaymentConfig()
    review: ReviewConfig = ReviewConfig()


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Marketplace Module

    Extends BaseModule pattern to integrate marketplace functionality
    into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "marketplace"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Marketplace Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Marketplace module initialized (v{self.info.version})")

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

        # Include marketplace routes
        app.include_router(marketplace_router)

        logger.info(f"Marketplace routes registered at {marketplace_router.prefix}")

        # Page routes
        @app.get("/marketplace", response_class=HTMLResponse, include_in_schema=False)
        async def marketplace_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                # Load market stats from config_data
                stats = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("market_stats", "stats"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _j
                            stats = _j.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    pass

                # Load vendor tiers from config_data
                tiers = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("vendor_tiers", "tiers"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _j2
                            tiers = _j2.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    pass

                # Load vendor listings from DB
                listings = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("""
                            SELECT
                                v.id, v.tier, v.company_name as display_name,
                                u.username, u.avatar_url,
                                COALESCE(skill_counts.cnt, 0) as total_skills,
                                COALESCE(sales.total, 0) as total_sales,
                                COALESCE(rating.avg_rating, 0) as rating_avg
                            FROM vendors v
                            JOIN users u ON v.user_id = u.id
                            LEFT JOIN (
                                SELECT author_id, COUNT(*) as cnt FROM skills WHERE is_deleted = FALSE GROUP BY author_id
                            ) skill_counts ON skill_counts.author_id = v.user_id
                            LEFT JOIN (
                                SELECT sk.author_id, COUNT(*) as total
                                FROM skills sk
                                JOIN orders o ON o.product_id = sk.id AND o.status = 'completed'
                                WHERE sk.is_deleted = FALSE
                                GROUP BY sk.author_id
                            ) sales ON sales.author_id = v.user_id
                            LEFT JOIN (
                                SELECT sk.author_id, ROUND(AVG(sk.rating_avg)::numeric, 1) as avg_rating
                                FROM skills sk
                                WHERE sk.is_deleted = FALSE AND sk.rating_count > 0
                                GROUP BY sk.author_id
                            ) rating ON rating.author_id = v.user_id
                            WHERE v.is_verified = TRUE
                            ORDER BY rating.avg_rating DESC NULLS LAST, skill_counts.cnt DESC
                            LIMIT 20
                        """)
                        rows = cur.fetchall()
                        tier_emoji_map = {t.get("name"): t for t in tiers}
                        for r in rows:
                            tier_name = r.get("tier", "basic")
                            tier_info = tier_emoji_map.get(tier_name, {})
                            listings.append({
                                "username": r.get("username", ""),
                                "avatar_url": r.get("avatar_url") or "/static/img/avatar-default.svg",
                                "display_name": r.get("display_name") or r.get("username", ""),
                                "tier_name": tier_name,
                                "tier_emoji": tier_info.get("emoji", ""),
                                "tier_color": tier_info.get("revenue_color", "#888"),
                                "total_skills": r.get("total_skills", 0),
                                "total_sales": r.get("total_sales", 0),
                                "rating_avg": float(r.get("rating_avg", 0) or 0),
                            })
                except Exception:
                    pass
            except Exception:
                stats, tiers, listings = [], [], []

            return render_template(request, "marketplace/list.html", {
                "market_stats": stats,
                "tiers": tiers,
                "listings": listings,
                "search_query": "",
                "current_sort": "popular",
                "total_pages": 1,
            })

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks.
        """
        logger.info("Marketplace module starting up...")

        # Initialize services with config
        if self.config:
            listing_service._config = self.config.model_dump()
            purchase_service._config = self.config.model_dump()
            logger.info("Marketplace module services initialized with config")

        logger.info("Marketplace module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks.
        """
        logger.info("Marketplace module shutting down...")

        # TODO: Save any cached data
        # TODO: Close connections

        logger.info("Marketplace module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/marketplace'):
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
    "ListingService",
    "PurchaseService",
    "ReviewService",
    "listing_service",
    "purchase_service",
    "review_service",

    # Schemas - Listings
    "ListingCreate",
    "ListingUpdate",
    "ListingResponse",
    "ListingListResponse",
    "ListingStatus",

    # Schemas - Purchases
    "PurchaseItem",
    "PurchaseRequest",
    "PurchaseResponse",
    "PurchaseListResponse",
    "PurchaseStatus",
    "PaymentMethod",

    # Schemas - Reviews
    "ReviewCreate",
    "ReviewResponse",

    # Schemas - Statistics
    "MarketplaceStats",
    "VendorSalesStats",

    # Schemas - Response
    "MarketplaceResponse",

    # Routes
    "router",
]
