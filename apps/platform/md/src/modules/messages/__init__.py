"""
Messages Module
SillyMD Messaging Module

Provides messaging system, notifications, and conversation management.

Usage:
    from src.modules.messages import SillyMDModule, message_service, notification_service

    # In your FastAPI app:
    messages_module = SillyMDModule()
    messages_module.register(app)

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
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    MessageThread,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    CreateConversationRequest,
    CreateConversationResponse,
    DeleteConversationResponse,
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    SendMessageRequest,
    MarkReadRequest,
    ApiResponse,
)
from .services import message_service, notification_service, MessageService, NotificationService
from .routes import router as messages_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "messages"
    name: str = "消息系统模块"
    version: str = "1.0.0"
    description: str = "提供系统通知、用户消息功能"
    dependencies: list = ["auth"]


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    max_message_length: int = 5000
    max_attachment_size_mb: int = 10
    retention_days: int = 90


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Messages Module

    Extends BaseModule pattern to integrate messaging
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "messages"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Messages Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Messages module initialized (v{self.info.version})")

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

        # Include messages routes
        app.include_router(messages_router)

        logger.info(f"Messages routes registered at {messages_router.prefix}")

        # Page routes
        @app.get("/messages", response_class=HTMLResponse, include_in_schema=False)
        async def messages_page(request: Request):
            return render_template(request, "user/messages.html")

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
        logger.info("Messages module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("SELECT 1")
            logger.info("Messages module database connection verified")
        except Exception as e:
            logger.error(f"Messages module database connection failed: {e}")

        # TODO: Initialize message cache
        # TODO: Start background cleanup tasks for old notifications

        logger.info("Messages module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Canceling background tasks
        """
        logger.info("Messages module shutting down...")

        # TODO: Flush message cache
        # TODO: Cancel background tasks
        # TODO: Close database connections

        logger.info("Messages module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/messages'):
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
    "MessageService",
    "NotificationService",
    "message_service",
    "notification_service",

    # Message Schemas
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
    "MessageThread",
    "ConversationCreate",
    "ConversationResponse",

    # Conversation Schemas
    "ConversationListResponse",
    "CreateConversationRequest",
    "CreateConversationResponse",
    "DeleteConversationResponse",
    "SendMessageRequest",
    "MarkReadRequest",

    # Notification Schemas
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",

    # Generic Schemas
    "ApiResponse",

    # Routes
    "router",
]
