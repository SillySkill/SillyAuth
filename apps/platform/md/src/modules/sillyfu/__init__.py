"""
SillyFu Version Management Module

A SillyMD module for managing SillyFu desktop application versions.
Provides version checking, downloading, and publishing functionality.
"""

import os
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse, RedirectResponse
from core.template_helpers import render_template

logger = logging.getLogger(__name__)


class ModuleInfo:
    """Module metadata"""
    id: str = "sillyfu"
    name: str = "SillyFu 版本管理模块"
    version: str = "1.0.0"
    description: str = "提供 SillyFu 版本检查、下载、发布功能"
    dependencies: list = ["storage"]


class SillyMDModule:
    """
    SillyFu Version Management Module for SillyMD.

    This module provides:
    - Version checking API for SillyFu control panel
    - Version download redirects
    - Admin interface for publishing new versions
    - Version comparison and update detection
    """

    module_id: str = "sillyfu"

    @property
    def info(self):
        """Get module info."""
        return ModuleInfo()

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SillyFu module.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.app: Optional[FastAPI] = None
        self.state = None

        # Service instance (set during startup)
        self.version_service = None

    def _load_config(self) -> Dict[str, Any]:
        """Load module configuration from file or use defaults."""
        import yaml

        # Try to load from config.yaml
        config_path = os.path.join(
            os.path.dirname(__file__),
            "config.yaml"
        )

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                return file_config.get('config', {})

        # Return default configuration
        return {
            'tos': {
                'endpoint': 'tos-cn-shanghai.volces.com',
                'bucket': 'sillymd-skills',
                'custom_domain': 'skills.sillymd.com'
            },
            'release_path': 'sillyfu/releases/',
            'version_check_cache_ttl': 3600
        }

    def _get_db_config(self) -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        from core.db_adapter import get_default_config
        return get_default_config()

    def _get_tos_credentials(self) -> Dict[str, str]:
        """Get TOS credentials from environment variables."""
        access_key = os.getenv("TOS_ACCESS_KEY")
        secret_key = os.getenv("TOS_SECRET_KEY")

        if not access_key or not secret_key:
            raise RuntimeError(
                "Missing TOS credentials. Please set TOS_ACCESS_KEY and "
                "TOS_SECRET_KEY environment variables."
            )

        return {
            "access_key": access_key,
            "secret_key": secret_key
        }

    def register(self, app: FastAPI) -> None:
        """
        Register the module with the FastAPI application.

        This method is called during application startup to register
        the module's routes and dependencies.

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Import routes here to avoid circular imports
        from .routes import router, check_update_router

        # Register routers
        app.include_router(router)
        app.include_router(check_update_router)

        logger.info(f"Registered SillyFu module v{ModuleInfo.version}")

        # Page routes
        @app.get("/sillyfu", response_class=HTMLResponse, include_in_schema=False)
        async def sillyfu_page(request: Request):
            """Render the sillyfu page with full OpenClaw content + Store integration."""
            try:
                from core.db_adapter import get_db_cursor
                product = {}
                variants = []
                openclaw_data = {}
                store_products = []
                collection_id = 0
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("sillyfu", "product"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _js
                            product = _js.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    product = {}

                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("sillyfu", "variants"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _jv
                            variants = _jv.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    variants = []

                # Fallback: if no independent variants record exists, read from product.data.variants
                if not variants and product.get("variants"):
                    variants = product["variants"]

                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("sillyfu", "openclaw"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _jo
                            openclaw_data = _jo.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    openclaw_data = {}

                # Query store_products for sillyfu collection (commerce data)
                try:
                    with get_db_cursor() as cur:
                        cur.execute("""
                            SELECT sp.*, sc.id as collection_id
                            FROM store_products sp
                            JOIN store_collections sc ON sp.collection_id = sc.id
                            WHERE sc.collection_key = 'sillyfu' AND sp.is_active = TRUE
                            ORDER BY sp.sort_order, sp.id
                        """)
                        rows = cur.fetchall()
                        for r in rows:
                            store_products.append({
                                "id": r.get("id"),
                                "collection_id": r.get("collection_id"),
                                "product_key": r.get("product_key", ""),
                                "name_zh": r.get("name_zh", r.get("name", "")),
                                "name_en": r.get("name_en", ""),
                                "description_zh": r.get("description_zh", r.get("description", "")),
                                "description_en": r.get("description_en", ""),
                                "image_url": r.get("image_url", ""),
                                "price": int(r.get("price", 0) or 0),
                                "original_price": r.get("original_price"),
                                "stock_count": r.get("stock_count", r.get("stock", 0)),
                                "sold_count": r.get("sold_count", 0),
                                "is_active": r.get("is_active", True),
                                "sort_order": r.get("sort_order", 0),
                            })
                        if rows:
                            collection_id = rows[0].get("collection_id", 0)

                    if collection_id == 0:
                        with get_db_cursor() as cur:
                            cur.execute("SELECT id FROM store_collections WHERE collection_key='sillyfu'")
                            crow = cur.fetchone()
                            if crow:
                                collection_id = crow.get("id", 0)
                except Exception:
                    store_products = []
                    collection_id = 0
            except Exception:
                product, variants, openclaw_data, store_products = {}, [], {}, []
                collection_id = 0

            # Compute starting price from active store products
            starting_price = 0
            if store_products:
                active_prices = [p["price"] for p in store_products if p.get("is_active")]
                if active_prices:
                    starting_price = min(active_prices)

            return render_template(request, "sillyfu/openclaw.html", {
                "product": product,
                "variants": variants,
                "openclaw": openclaw_data,
                "store_products": store_products,
                "collection_id": collection_id,
                "starting_price": starting_price,
            })

        @app.get("/openclaw", include_in_schema=False)
        async def openclaw_redirect():
            """Redirect /openclaw to /sillyfu."""
            return RedirectResponse(url="/sillyfu", status_code=301)

        @app.get("/sillyclaw", include_in_schema=False)
        async def sillyclaw_redirect():
            """Redirect /sillyclaw to /sillyfu."""
            return RedirectResponse(url="/sillyfu", status_code=301)

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        logger.info(f"SillyFu install called with app: {app}")
        self.register(app)
        logger.info(f"SillyFu install complete. Routes count: {len(app.routes)}")

    def on_startup(self) -> None:
        """
        Module startup handler.

        Initializes services, database tables, and sets up the version service.
        Called when the application starts.
        """
        logger.info("Starting SillyFu module...")

        # Load configuration
        module_config = self._load_config()

        # Get database config
        db_config = self._get_db_config()

        # Get TOS credentials
        tos_creds = self._get_tos_credentials()

        # Create TOS client
        from .tos_client import TosClient
        tos_client = TosClient(
            endpoint=module_config['tos']['endpoint'],
            bucket=module_config['tos']['bucket'],
            access_key=tos_creds['access_key'],
            secret_key=tos_creds['secret_key'],
            custom_domain=module_config['tos'].get('custom_domain'),
            release_path=module_config['release_path']
        )

        # Create version service
        from .services import SillyFuVersionService
        self.version_service = SillyFuVersionService(
            db_config=db_config,
            tos_client=tos_client,
            cache_ttl=module_config.get('version_check_cache_ttl', 3600)
        )

        # Store service in module for route access
        global _version_service
        _version_service = self.version_service

        # Initialize database tables
        try:
            self.version_service.initialize_database()
            logger.info("SillyFu database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise

        # Store TOS client reference
        self.tos_client = tos_client

        logger.info("SillyFu module started successfully")

    def on_shutdown(self) -> None:
        """
        Module shutdown handler.

        Called when the application shuts down.
        Cleans up resources and connections.
        """
        logger.info("Shutting down SillyFu module...")

        # Clear service references
        self.version_service = None
        self.tos_client = None

        # Clear global service reference
        global _version_service
        _version_service = None

        logger.info("SillyFu module shut down successfully")

    def get_routes(self) -> list:
        """
        Get list of routes registered by this module.

        Returns:
            List of route dictionaries with path, methods, and handler info
        """
        return [
            {
                "path": "/sillyfu/version",
                "methods": ["GET"],
                "summary": "Get latest version"
            },
            {
                "path": "/sillyfu/version/{version}",
                "methods": ["GET"],
                "summary": "Get specific version"
            },
            {
                "path": "/sillyfu/version/{version}/download",
                "methods": ["GET"],
                "summary": "Download version file"
            },
            {
                "path": "/sillyfu/version/all",
                "methods": ["GET"],
                "summary": "List all versions"
            },
            {
                "path": "/sillyfu/version",
                "methods": ["POST"],
                "summary": "Publish new version (Admin)"
            },
            {
                "path": "/sillyfu/check-update",
                "methods": ["GET"],
                "summary": "Check for updates"
            },
            {
                "path": "/sillyfu/version/{version}",
                "methods": ["DELETE"],
                "summary": "Delete version (Admin)"
            }
        ]


# Global service instance for route access
_version_service: Optional['SillyFuVersionService'] = None


def create_module(config: Optional[Dict[str, Any]] = None) -> SillyMDModule:
    """
    Factory function to create a SillyFu module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured SillyMDModule instance
    """
    return SillyMDModule(config=config)


# For backwards compatibility with direct imports
SillyFuVersionService = None


def _lazy_import_services():
    """Lazy import to avoid circular imports."""
    global SillyFuVersionService
    if SillyFuVersionService is None:
        from .services import SillyFuVersionService as SVS
        SillyFuVersionService = SVS
    return SillyFuVersionService
