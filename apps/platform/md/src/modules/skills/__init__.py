"""
Skills Module
SillyMD Skills Platform Module

Provides skills hosting, publishing, and management functionality.
This module handles CRUD operations, version control, and publishing workflows
for AI Skills on the SillyMD platform.

Features:
- Skill creation, editing, and deletion
- Version management
- Category and tag organization
- Publishing workflow (draft -> reviewing -> approved)
- Statistics tracking
- Admin approval system

Usage:
    from src.modules.skills import SillyMDModule

    # In your FastAPI app:
    skills_module = SillyMDModule()
    skills_module.register(app)

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

# Import routes at module level
from .routes import router as skills_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "skills"
    name: str = "Skills 平台模块"
    version: str = "1.0.0"
    description: str = "提供 Skills 托管、发布、管理功能"
    dependencies: list = ["auth", "storage"]


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    max_skill_size_mb: int = 100
    allowed_extensions: List[str] = ["py", "js", "json", "yaml"]
    approval_required: bool = True


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Skills Module

    Extends BaseModule pattern to integrate skills
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "skills"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Skills Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Skills module initialized (v{self.info.version})")

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

        # Include skills routes
        app.include_router(skills_router)

        logger.info(f"Skills routes registered at {skills_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks like:
        - Database connection verification
        - Cache initialization
        - Background task registration
        """
        logger.info("Skills module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("SELECT 1")
            logger.info("Skills module database connection verified")
        except Exception as e:
            logger.error(f"Skills module database connection failed: {e}")

        logger.info("Skills module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Canceling background tasks
        """
        logger.info("Skills module shutting down...")

        logger.info("Skills module shutdown complete")

    def get_routes(self) -> list:
        """
        Get list of registered routes

        Returns:
            List of route dictionaries with method, path, and handler info
        """
        if not self.app:
            return []

        from .routes import router as skills_router
        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith(skills_router.prefix):
                methods = getattr(route, 'methods', {'GET'})
                routes.append({
                    "method": list(methods)[0] if methods else "GET",
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
    "SkillService",
    "skill_service",

    # Routes
    "router",

    # Schemas
    "schemas",
]

# Also export skills_router for plugin_manager
router = skills_router
