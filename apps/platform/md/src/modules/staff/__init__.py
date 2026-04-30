"""
Staff Module
SillyMD Staff Management Module

Provides staff authentication, user management, role management,
and permission-based access control.

Usage:
    from src.modules.staff import SillyMDModule, staff_services

    # In your FastAPI app:
    staff_module = SillyMDModule()
    staff_module.register(app)

Module Structure:
    - config.yaml: Module configuration
    - schemas.py: Pydantic request/response models
    - services.py: Business logic layer
    - middleware.py: Permission checking middleware
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
    # Auth schemas
    LoginRequest,
    LoginResponse,
    ChangePasswordRequest,
    ResetPasswordRequest,

    # Staff user schemas
    StaffUserCreate,
    StaffUserUpdate,
    StaffUserResponse,
    StaffUserListResponse,
    StaffUserStatusUpdate,
    StaffPasswordUpdate,
    StaffUserResponseWrapper,
    StaffOperationResponse,

    # Role schemas
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    RoleOperationResponse,

    # Permission schemas
    PermissionResponse,
    PermissionListResponse,
    PermissionTreeResponse,
    PermissionTreeNode,

    # Audit log schemas
    AuditLogEntry,
    AuditLogFilter,
    AuditLogResponse,

    # Enums
    StaffStatus,
    AuditAction,
)

from .services import (
    AuthService,
    StaffUserService,
    RoleService,
    PermissionService,
    StaffAuditLogService,
    auth_service,
    staff_user_service,
    role_service,
    permission_service,
    audit_service,
    init_staff_tables,
    init_system_roles,
    init_permissions,
    ALL_PERMISSIONS,
    SYSTEM_ROLES,
    expand_permissions,
    check_permission,
    hash_password,
    verify_password,
)

from .middleware import (
    get_current_staff_user,
    get_optional_staff_user,
    require_permissions,
    require_any_permission,
    require_roles,
    require_super_admin,
    get_client_ip,
    get_user_agent,
    security,
)

from .routes import router as staff_router

logger = logging.getLogger(__name__)

# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "staff"
    name: str = "员工权限管理模块"
    version: str = "1.0.0"
    description: str = "提供员工管理、角色管理和权限控制系统"
    dependencies: List[str] = ["auth"]
    author: str = "SillyMD Team"


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    system_roles: List[Dict[str, Any]] = []
    audit_log_enabled: bool = True
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 43200


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Staff Module

    Extends BaseModule pattern to integrate staff management
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "staff"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Staff Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Staff module initialized (v{self.info.version})")

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

        # Include staff routes
        app.include_router(staff_router)

        logger.info(f"Staff routes registered at {staff_router.prefix}")

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
        - Initializing system roles
        - Cache initialization
        """
        logger.info("Staff module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("SELECT 1")

            # Initialize database tables
            init_staff_tables()

            # Initialize system roles
            init_system_roles()

            # Initialize permissions
            init_permissions()

            logger.info("Staff module database connection verified")

        except Exception as e:
            logger.error(f"Staff module database connection failed: {e}")

        # Initialize audit log service with config
        if self.config:
            audit_service.enabled = self.config.audit_log_enabled

        logger.info("Staff module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Saving state
        """
        logger.info("Staff module shutting down...")

        # TODO: Flush caches
        # TODO: Save state

        logger.info("Staff module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/staff'):
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
# Module Staff Services (convenience access)
# ============================================================================

class StaffServices:
    """Container for staff module services"""

    @property
    def auth(self) -> AuthService:
        """Authentication service"""
        return auth_service

    @property
    def users(self) -> StaffUserService:
        """Staff user management service"""
        return staff_user_service

    @property
    def roles(self) -> RoleService:
        """Role management service"""
        return role_service

    @property
    def permissions(self) -> PermissionService:
        """Permission management service"""
        return permission_service

    @property
    def audit(self) -> StaffAuditLogService:
        """Audit logging service"""
        return audit_service


staff_services = StaffServices()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "AuthService",
    "StaffUserService",
    "RoleService",
    "PermissionService",
    "StaffAuditLogService",
    "staff_services",
    "auth_service",
    "staff_user_service",
    "role_service",
    "permission_service",
    "audit_service",

    # Database initialization
    "init_staff_tables",
    "init_system_roles",
    "init_permissions",

    # Permission utilities
    "ALL_PERMISSIONS",
    "SYSTEM_ROLES",
    "expand_permissions",
    "check_permission",
    "hash_password",
    "verify_password",

    # Middleware
    "get_current_staff_user",
    "get_optional_staff_user",
    "require_permissions",
    "require_any_permission",
    "require_roles",
    "require_super_admin",
    "get_client_ip",
    "get_user_agent",
    "security",

    # Schemas - Auth
    "LoginRequest",
    "LoginResponse",
    "ChangePasswordRequest",
    "ResetPasswordRequest",

    # Schemas - Staff User
    "StaffUserCreate",
    "StaffUserUpdate",
    "StaffUserResponse",
    "StaffUserListResponse",
    "StaffUserStatusUpdate",
    "StaffPasswordUpdate",
    "StaffUserResponseWrapper",
    "StaffOperationResponse",

    # Schemas - Role
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleListResponse",
    "RoleOperationResponse",

    # Schemas - Permission
    "PermissionResponse",
    "PermissionListResponse",
    "PermissionTreeResponse",
    "PermissionTreeNode",

    # Schemas - Audit Log
    "AuditLogEntry",
    "AuditLogFilter",
    "AuditLogResponse",

    # Enums
    "StaffStatus",
    "AuditAction",

    # Routes
    "router",
]
