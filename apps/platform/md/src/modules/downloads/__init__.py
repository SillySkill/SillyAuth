"""
Downloads Module

A SillyMD module for managing downloadable resources including
SillyFu program downloads.

This module provides:
- Download item management with categories
- Signed URL generation for secure downloads
- Download counting and analytics
- SillyFu-specific download endpoints
- Featured downloads for homepage

Usage:
    from src.modules.downloads import create_module, DownloadService

    # Create module instance
    module = create_module(config)

    # Register routes
    module.register(app)

    # Initialize on startup
    module.on_startup()

Example config.yaml:
    id: downloads
    name: 下载区模块
    version: 1.0.0
    description: 提供 SillyFu 程序下载功能
    dependencies: [storage, sillyfu]

    config:
      download_base_url: https://skills.sillymd.com
      featured_downloads:
        - id: sillyfu
          name: SillyFu 控制面板
          category: application
          latest_version_required: true
      cache_ttl: 3600
"""

from __future__ import annotations

import os
import logging
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template

from .services import DownloadService, set_download_service, get_download_service
from .schemas import (
    DownloadItemResponse,
    DownloadCategory,
    DownloadListResponse,
    FeaturedDownloadResponse,
    SillyClawDownloadResponse,
    LikeResponse,
    RecordDownloadResponse,
    DownloadDetailResponse,
    ErrorResponse
)

__version__ = "1.0.0"
__all__ = [
    "__version__",
    "DownloadsModule",
    "DownloadService",
    "create_module",
    "get_download_service",
    "set_download_service",
    # Schemas
    "DownloadItemResponse",
    "DownloadCategory",
    "DownloadListResponse",
    "FeaturedDownloadResponse",
    "SillyClawDownloadResponse",
    "LikeResponse",
    "RecordDownloadResponse",
    "DownloadDetailResponse",
    "ErrorResponse",
]

logger = logging.getLogger(__name__)


class ModuleInfo:
    """Module metadata"""
    id: str = "downloads"
    name: str = "下载区模块"
    version: str = "1.0.0"
    description: str = "提供 SillyFu 程序下载功能"
    dependencies = ["storage", "sillyfu"]  # type: list


class DownloadsModule:
    """
    Downloads Module for SillyMD.

    Provides download management functionality including:
    - Download item listing with categories
    - Signed URL generation for secure downloads
    - Download counting
    - SillyFu-specific download endpoints
    - Featured downloads
    """

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "downloads"

    @property
    def info(self):
        """Get module info."""
        return ModuleInfo

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Downloads module.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.app: Optional[FastAPI] = None
        self._download_service: Optional[DownloadService] = None
        self._module_config: Dict[str, Any] = {}

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
            'download_base_url': 'https://skills.sillymd.com',
            'featured_downloads': [
                {
                    'id': 'sillyfu',
                    'name': 'SillyFu 控制面板',
                    'category': 'application',
                    'latest_version_required': True
                }
            ],
            'cache_ttl': 3600
        }

    def _get_db_config(self) -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        from core.db_adapter import get_default_config
        return get_default_config()

    def _get_storage_service(self):
        """
        Get the storage service from the storage module.

        Returns:
            Storage service instance or None if not available
        """
        try:
            from src.modules.storage import get_module as get_storage_module
            storage_module = get_storage_module()
            return storage_module.get_service()
        except Exception as e:
            logger.warning(f"Storage module not available: {e}")
            return None

    def register(self, app: FastAPI) -> None:
        """
        Register the module with the FastAPI application.

        This method is called during application startup to register
        the module's routes.

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Import routes here to avoid circular imports
        from .routes import router

        # Register router
        app.include_router(router)

        # Page routes
        @app.get("/downloads", response_class=HTMLResponse, include_in_schema=False)
        async def downloads_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                # Load download items from DB
                downloads = []
                categories = []
                stats = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("""
                            SELECT d.*, d.category as category_name
                            FROM download_items d
                            WHERE d.is_published = TRUE
                            ORDER BY d.downloads_count DESC, d.position ASC, d.created_at DESC
                            LIMIT 20
                        """)
                        rows = cur.fetchall()
                        for r in rows:
                            downloads.append({
                                "name": r.get("name", ""),
                                "version": r.get("version", ""),
                                "is_official": True,
                                "platform_name": r.get("category", ""),
                                "file_type": r.get("category", ""),
                                "description": r.get("description", ""),
                                "file_url": r.get("file_key", ""),
                                "file_size": str(r.get("size", "")) if r.get("size") else "",
                                "mirror_url": r.get("file_key", ""),
                                "mirror_name": r.get("name", ""),
                                "github_url": "",
                                "download_count": r.get("downloads_count", 0),
                                "view_count": r.get("downloads_count", 0),
                                "category_icon": "",
                            })
                except Exception:
                    downloads = []

                # Load categories from DB (grouped from download_items since download_categories table does not exist)
                try:
                    with get_db_cursor() as cur:
                        cur.execute("""
                            SELECT category as slug, category as name, COUNT(id) as count
                            FROM download_items
                            WHERE is_published = TRUE
                            GROUP BY category
                            ORDER BY count DESC
                        """)
                        cat_rows = cur.fetchall()
                        for c in cat_rows:
                            categories.append({
                                "slug": c.get("slug", ""),
                                "icon": "fa-download",
                                "name": c.get("name", c.get("slug", "")),
                                "count": c.get("count", 0),
                            })
                except Exception:
                    categories = []

                # Stats from config_data
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("downloads_stats", "stats"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _j
                            stats = _j.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    stats = [
                        {"value": str(len(downloads)), "label": "开发工具"},
                        {"value": "0", "label": "资源文件"},
                        {"value": "0", "label": "总下载量"},
                        {"value": "99.9%", "label": "可用性"},
                    ]
            except Exception:
                downloads, categories, stats = [], [], []

            return render_template(request, "downloads/list.html", {
                "downloads": downloads,
                "categories": categories,
                "stats": stats,
                "search_query": "",
                "current_category": "",
                "platforms": [],
                "current_platform": "",
                "total_pages": 1,
            })

        logger.info(f"Registered Downloads module v{ModuleInfo.version}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup handler.

        Initializes services, database tables, and sets up the download service.
        Called when the application starts.
        """
        logger.info("Starting Downloads module...")

        # Load configuration
        module_config = self._load_config()
        self._module_config = module_config

        # Get database config
        db_config = self._get_db_config()

        # Get storage service
        storage_service = self._get_storage_service()

        # Create download service
        self._download_service = DownloadService(
            db_config=db_config,
            storage_service=storage_service,
            config=module_config
        )

        # Set global service instance
        set_download_service(self._download_service)

        # Initialize database tables
        try:
            self._download_service.initialize_database()
            logger.info("Downloads database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise

        logger.info("Downloads module started successfully")

    def on_shutdown(self) -> None:
        """
        Module shutdown handler.

        Called when the application shuts down.
        Cleans up resources and connections.
        """
        logger.info("Shutting down Downloads module...")

        # Clear service references
        self._download_service = None

        # Clear global service reference
        set_download_service(None)

        logger.info("Downloads module shut down successfully")

    def get_routes(self):  # type: () -> list
        """
        Get list of routes registered by this module.

        Returns:
            List of route dictionaries with path, methods, and handler info
        """
        return [
            {
                "path": "/downloads",
                "methods": ["GET"],
                "summary": "List downloads"
            },
            {
                "path": "/downloads/categories",
                "methods": ["GET"],
                "summary": "List categories"
            },
            {
                "path": "/downloads/featured",
                "methods": ["GET"],
                "summary": "Get featured downloads"
            },
            {
                "path": "/downloads/{item_id}",
                "methods": ["GET"],
                "summary": "Get download item by ID"
            },
            {
                "path": "/downloads/slug/{slug}",
                "methods": ["GET"],
                "summary": "Get download item by slug"
            },
            {
                "path": "/downloads/{item_id}/file",
                "methods": ["GET"],
                "summary": "Download file"
            },
            {
                "path": "/downloads/{item_id}/like",
                "methods": ["POST"],
                "summary": "Like a download item"
            },
            {
                "path": "/downloads/{item_id}/record-download",
                "methods": ["POST"],
                "summary": "Record download event"
            },
            {
                "path": "/downloads/sillyfu",
                "methods": ["GET"],
                "summary": "Get SillyFu latest"
            },
            {
                "path": "/downloads/sillyfu/{version}",
                "methods": ["GET"],
                "summary": "Get SillyFu specific version"
            }
        ]

    def get_service(self) -> Optional[DownloadService]:
        """Get the download service instance."""
        return self._download_service


# Global module instance
_module_instance: Optional[DownloadsModule] = None


def create_module(config: Optional[Dict[str, Any]] = None) -> DownloadsModule:
    """
    Factory function to create a Downloads module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured DownloadsModule instance
    """
    global _module_instance
    _module_instance = DownloadsModule(config=config)
    return _module_instance


def get_module() -> DownloadsModule:
    """
    Get the global Downloads module instance.

    Returns:
        DownloadsModule instance

    Raises:
        RuntimeError: If module not created
    """
    global _module_instance
    if _module_instance is None:
        raise RuntimeError("Downloads module not created. Call create_module(config) first.")
    return _module_instance


# Backwards compatibility alias
BaseModule = DownloadsModule
