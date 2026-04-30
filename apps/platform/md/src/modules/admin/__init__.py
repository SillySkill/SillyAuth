"""
Admin Module
SillyMD Admin Module

Provides admin API endpoints for managing the platform, including:
- User management
- Content moderation
- System statistics
- Audit logging
- Module management

Usage:
    from src.modules.admin import SillyMDModule, admin_services

    # In your FastAPI app:
    admin_module = SillyMDModule()
    admin_module.register(app)

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
    UserStatus,
    ContentType,
    ContentAction,
    UserListResponse,
    UserDetailsResponse,
    UpdateUserStatusResponse,
    ResetPasswordResponse,
    PendingContentResponse,
    ContentModerationResponse,
    SystemStats,
    DashboardData,
    AuditLogResponse,
    ModuleListResponse,
    ModuleActionResponse,
    AdminResponse,
    ErrorResponse,
)
from .services import (
    user_management_service,
    content_moderation_service,
    system_service,
    audit_log_service,
    UserManagementService,
    ContentModerationService,
    SystemService,
    AuditLogService,
)
from .routes import router as admin_router

logger = logging.getLogger(__name__)

# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "admin"
    name: str = "管理后台 API 模块"
    version: str = "1.0.0"
    description: str = "提供管理后台 API 功能"
    dependencies: List[str] = ["auth"]
    author: str = "SillyMD Team"


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    admin_roles: List[str] = [
        "super_admin",
        "content_admin",
        "user_admin",
        "finance_admin"
    ]
    audit_log_enabled: bool = True


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Admin Module

    Extends BaseModule pattern to integrate admin
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "admin"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Admin Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Admin module initialized (v{self.info.version})")

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

                # Update module info if provided
                if config_data:
                    if 'id' in config_data:
                        self.info.id = config_data['id']
                    if 'name' in config_data:
                        self.info.name = config_data['name']
                    if 'version' in config_data:
                        self.info.version = config_data['version']
                    if 'description' in config_data:
                        self.info.description = config_data['description']
                    if 'dependencies' in config_data:
                        self.info.dependencies = config_data['dependencies']

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

        # Include admin routes
        app.include_router(admin_router)

        logger.info(f"Admin routes registered at {admin_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks like:
        - Database connection verification
        - Creating necessary database tables
        - Cache initialization
        """
        logger.info("Admin module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("SELECT 1")

            # Ensure audit_logs table exists
            self._ensure_audit_logs_table()

            logger.info("Admin module database connection verified")
        except Exception as e:
            logger.error(f"Admin module database connection failed: {e}")

        # Initialize audit log service with config
        if self.config:
            audit_log_service.enabled = self.config.audit_log_enabled

        logger.info("Admin module startup complete")

    def _ensure_audit_logs_table(self) -> None:
        """
        Ensure the audit_logs table exists in the database

        Creates the table if it doesn't exist.
        """
        try:
            from .services import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id SERIAL PRIMARY KEY,
                        admin_id INTEGER NOT NULL,
                        action VARCHAR(255) NOT NULL,
                        target_type VARCHAR(100),
                        target_id INTEGER,
                        target VARCHAR(500),
                        details TEXT,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Create index on timestamp for faster queries
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp
                    ON audit_logs (timestamp DESC)
                """)
                # Create index on admin_id
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id
                    ON audit_logs (admin_id)
                """)
        except Exception as e:
            logger.warning(f"Failed to ensure audit_logs table: {e}")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Saving state
        """
        logger.info("Admin module shutting down...")

        # TODO: Flush caches
        # TODO: Save state

        logger.info("Admin module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/admin'):
                routes.append({
                    "method": list(getattr(route, 'methods', {'GET'}))[0],
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
            "author": self.info.author,
            "config": self.config.model_dump() if self.config else None
        }


# ============================================================================
# Module Admin Services (convenience access)
# ============================================================================

class AdminServices:
    """Container for admin module services"""

    @property
    def users(self) -> UserManagementService:
        """User management service"""
        return user_management_service

    @property
    def content(self) -> ContentModerationService:
        """Content moderation service"""
        return content_moderation_service

    @property
    def system(self) -> SystemService:
        """System statistics service"""
        return system_service

    @property
    def audit(self) -> AuditLogService:
        """Audit logging service"""
        return audit_log_service


admin_services = AdminServices()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "UserManagementService",
    "ContentModerationService",
    "SystemService",
    "AuditLogService",
    "admin_services",
    "user_management_service",
    "content_moderation_service",
    "system_service",
    "audit_log_service",

    # Schemas
    "UserStatus",
    "ContentType",
    "ContentAction",
    "UserListResponse",
    "UserDetailsResponse",
    "UpdateUserStatusResponse",
    "ResetPasswordResponse",
    "PendingContentResponse",
    "ContentModerationResponse",
    "SystemStats",
    "DashboardData",
    "AuditLogResponse",
    "ModuleListResponse",
    "ModuleActionResponse",
    "AdminResponse",
    "ErrorResponse",

    # Routes
    "router",
]
