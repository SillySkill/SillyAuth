"""
Auth Module
SillyMD Authentication Module

Provides user registration, login, authentication, token management,
password reset, and email verification functionality.

Usage:
    from src.modules.auth import SillyMDModule, auth_service

    # In your FastAPI app:
    auth_module = SillyMDModule()
    auth_module.register(app)

Module Structure:
    - config.yaml: Module configuration
    - schemas.py: Pydantic request/response models
    - services.py: Business logic layer
    - routes.py: FastAPI route handlers
    - __init__.py: Module entry point
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yaml

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template
from pydantic import BaseModel

# Import components
from .schemas import (
    LoginRequest,
    RegisterRequest,
    Token,
    UserResponse,
    AuthResponse,
    RefreshTokenRequest,
)
from .services import auth_service, AuthService
from .routes import router as auth_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "auth"
    name: str = "用户认证模块"
    version: str = "1.0.0"
    description: str = "提供用户注册、登录、认证功能"
    dependencies: list = []


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    jwt_expiry_days: int = 7
    max_login_attempts: int = 5
    password_min_length: int = 8


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Auth Module

    Extends BaseModule pattern to integrate authentication
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "auth"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Auth Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Auth module initialized (v{self.info.version})")

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

        # Include auth routes
        app.include_router(auth_router)

        logger.info(f"Auth routes registered at {auth_router.prefix}")

        # Page routes
        @app.get("/login", response_class=HTMLResponse, include_in_schema=False)
        async def login_page(request: Request):
            return render_template(request, "auth/login.html")

        @app.get("/register", response_class=HTMLResponse, include_in_schema=False)
        async def register_page(request: Request):
            return render_template(request, "auth/register.html")

        @app.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
        async def forgot_password_page(request: Request):
            return render_template(request, "auth/forgot-password.html")

        @app.get("/reset-password", response_class=HTMLResponse, include_in_schema=False)
        async def reset_password_page(request: Request):
            return render_template(request, "auth/reset-password.html")

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
        logger.info("Auth module starting up...")

        # Verify database connection
        try:
            with auth_service.get_db_cursor() as cur:
                cur.execute("SELECT 1")
            logger.info("Auth module database connection verified")
        except Exception as e:
            logger.error(f"Auth module database connection failed: {e}")

        # TODO: Initialize token blacklist cache
        # TODO: Start background cleanup tasks

        logger.info("Auth module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Canceling background tasks
        """
        logger.info("Auth module shutting down...")

        # TODO: Flush token blacklist cache
        # TODO: Cancel background tasks
        # TODO: Close database connections

        logger.info("Auth module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/auth'):
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

    # Service
    "AuthService",
    "auth_service",

    # Schemas
    "LoginRequest",
    "RegisterRequest",
    "Token",
    "UserResponse",
    "AuthResponse",
    "RefreshTokenRequest",

    # Routes
    "router",
]
