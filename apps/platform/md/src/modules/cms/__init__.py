"""
CMS Module
SillyMD Content Management Module

Provides tutorials, articles, guides, and category management functionality.

This module enables:
- Creating and managing articles (tutorials, articles, guides)
- Organizing content with categories
- Article search and filtering
- Featured articles
- Article likes and view tracking
- Category hierarchy management

Usage:
    from src.modules.cms import SillyMDModule, article_service, category_service

    # In your FastAPI app:
    cms_module = SillyMDModule()
    cms_module.register(app)

Module Structure:
    - config.yaml: Module configuration
    - schemas.py: Pydantic request/response models
    - services.py: Business logic layer (ArticleService, CategoryService)
    - routes.py: FastAPI route handlers
    - __init__.py: Module entry point

Example:
    ```python
    from src.modules.cms import SillyMDModule

    cms_module = SillyMDModule()
    cms_module.register(app)
    ```

Routes:
    Articles:
        - POST /api/cms/articles - Create article (Auth required)
        - GET /api/cms/articles - List articles (Public)
        - GET /api/cms/articles/featured - Get featured articles (Public)
        - GET /api/cms/articles/search - Search articles (Public)
        - GET /api/cms/articles/{id} - Get article (Public)
        - PUT /api/cms/articles/{id} - Update article (Auth required)
        - DELETE /api/cms/articles/{id} - Delete article (Auth required)
        - POST /api/cms/articles/{id}/like - Like article (Auth required)

    Categories:
        - GET /api/cms/categories - List categories (Public)
        - GET /api/cms/categories/{id} - Get category (Public)
        - GET /api/cms/categories/{id}/articles - Get category with articles (Public)
        - POST /api/cms/categories - Create category (Admin)
        - PUT /api/cms/categories/{id} - Update category (Admin)
        - DELETE /api/cms/categories/{id} - Delete category (Admin)

    Statistics:
        - GET /api/cms/stats/articles - Get article stats (Admin)
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yaml

from fastapi import FastAPI
from pydantic import BaseModel

# Import components
from .schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListItem,
    ArticleList,
    ArticleSearchResult,
    FeaturedArticlesResponse,
    LikeResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryList,
    CategoryWithArticles,
    CMSResponse,
    CMSDeleteResponse,
    ArticleType,
    ArticleStatus,
)

from .services import (
    ArticleService,
    CategoryService,
    article_service,
    category_service,
)

from .routes import router as cms_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information."""
    id: str = "cms"
    name: str = "CMS 内容管理模块"
    version: str = "1.0.0"
    description: str = "提供教程、文章管理功能"
    dependencies: list = ["auth", "storage"]


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration."""
    max_article_length: int = 100000
    allowed_content_types: list = ["markdown", "html"]
    featured_articles_limit: int = 10


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD CMS Module

    Extends BaseModule pattern to integrate content management
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "cms"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CMS Module.

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        # Initialize services
        self.article_service = ArticleService(
            self.config.model_dump() if self.config else {}
        )
        self.category_service = CategoryService(
            self.config.model_dump() if self.config else {}
        )

        logger.info(f"CMS module initialized (v{self.info.version})")

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load module configuration from YAML file.

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
        Register module routes with FastAPI application.

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Include CMS routes
        app.include_router(cms_router)

        logger.info(f"CMS routes registered at {cms_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook.

        Called when the application starts.
        Performs initialization tasks like:
        - Database connection verification
        - Cache initialization
        - Background task registration
        """
        logger.info("CMS module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            cursor = get_db_cursor()
            if cursor:
                with cursor as cur:
                    cur.execute("SELECT 1")
                logger.info("CMS module database connection verified")
        except Exception as e:
            logger.warning(f"CMS module database connection check failed: {e}")

        # TODO: Initialize search index
        # TODO: Start background tasks for statistics aggregation

        logger.info("CMS module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook.

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Canceling background tasks
        """
        logger.info("CMS module shutting down...")

        # TODO: Flush search index
        # TODO: Cancel background tasks
        # TODO: Close database connections

        logger.info("CMS module shutdown complete")

    def get_routes(self) -> list:
        """
        Get list of registered routes.

        Returns:
            List of route dictionaries with method, path, and handler info
        """
        if not self.app:
            return []

        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/cms'):
                routes.append({
                    "method": getattr(route, 'methods', {'GET'}).__iter__().__next__(),
                    "path": route.path,
                    "name": getattr(route, 'name', 'unnamed')
                })

        return routes

    def get_info(self) -> Dict[str, Any]:
        """
        Get module information.

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

__version__ = "1.0.0"

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "ArticleService",
    "CategoryService",
    "article_service",
    "category_service",

    # Schemas - Article
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleResponse",
    "ArticleListItem",
    "ArticleList",
    "ArticleSearchResult",
    "FeaturedArticlesResponse",
    "LikeResponse",
    "ArticleType",
    "ArticleStatus",

    # Schemas - Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryList",
    "CategoryWithArticles",

    # Schemas - Generic
    "CMSResponse",
    "CMSDeleteResponse",

    # Routes
    "router",
]
