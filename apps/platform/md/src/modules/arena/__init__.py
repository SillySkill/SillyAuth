"""
Arena Module (虾拳馆 PK)

A SillyMD module for managing arena PK battles.
Provides room management, battle orchestration, and ranking systems.

Features:
- Create and join arena rooms for PK battles
- Start battles with multiple participants
- Submit answers and track scores
- ELO rating system with rankings
- Battle history tracking
"""

import os
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI

logger = logging.getLogger(__name__)


class ModuleInfo:
    """Module metadata"""
    id: str = "arena"
    name: str = "虾拳馆 PK 模块"
    version: str = "1.0.0"
    description: str = "提供虾拳馆 PK 竞技功能"
    dependencies: list = ["auth"]


class ArenaModule:
    """
    Arena PK Battle Module for SillyMD.

    This module provides:
    - Arena room creation and management
    - PK battle orchestration with questions
    - ELO-based ranking system
    - Battle history tracking
    """

    module_id: str = "arena"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Arena module.

        Args:
            config: Optional configuration dictionary
        """
        self.info = ModuleInfo()
        self.config = config or {}
        self.app: Optional[FastAPI] = None

        # Service instances (set during startup)
        self.arena_service = None
        self.battle_service = None
        self.ranking_service = None

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
            'max_room_participants': 4,
            'battle_timeout_seconds': 300,
            'ranking_update_interval': 3600,
            'elo_k_factor': 32,
            'initial_elo_rating': 1000
        }

    def _get_db_config(self) -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        from core.db_adapter import get_default_config
        return get_default_config()

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
        from .routes import router

        # Register router
        app.include_router(router)

        logger.info(f"Registered Arena module v{self.info.version}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup handler.

        Initializes services, database tables, and sets up the arena services.
        Called when the application starts.
        """
        logger.info("Starting Arena module...")

        # Load configuration
        module_config = self._load_config()

        # Get database config
        db_config = self._get_db_config()

        # Create services
        from .services import ArenaService, BattleService, RankingService

        self.arena_service = ArenaService(
            db_config=db_config,
            config=module_config
        )

        self.battle_service = BattleService(
            db_config=db_config,
            config=module_config
        )

        self.ranking_service = RankingService(
            db_config=db_config,
            config=module_config
        )

        # Store services in module for route access
        global _arena_service, _battle_service, _ranking_service
        _arena_service = self.arena_service
        _battle_service = self.battle_service
        _ranking_service = self.ranking_service

        # Initialize database tables
        try:
            self.arena_service.initialize_database()
            logger.info("Arena database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise

        logger.info("Arena module started successfully")

    def on_shutdown(self) -> None:
        """
        Module shutdown handler.

        Called when the application shuts down.
        Cleans up resources and connections.
        """
        logger.info("Shutting down Arena module...")

        # Clear service references
        self.arena_service = None
        self.battle_service = None
        self.ranking_service = None

        # Clear global service references
        global _arena_service, _battle_service, _ranking_service
        _arena_service = None
        _battle_service = None
        _ranking_service = None

        logger.info("Arena module shut down successfully")

    def get_routes(self) -> list:
        """
        Get list of routes registered by this module.

        Returns:
            List of route dictionaries with path, methods, and handler info
        """
        return [
            # Room routes
            {
                "path": "/arena/rooms",
                "methods": ["POST"],
                "summary": "Create room"
            },
            {
                "path": "/arena/rooms",
                "methods": ["GET"],
                "summary": "List rooms"
            },
            {
                "path": "/arena/rooms/{room_id}",
                "methods": ["GET"],
                "summary": "Get room"
            },
            {
                "path": "/arena/rooms/{room_id}/join",
                "methods": ["POST"],
                "summary": "Join room"
            },
            {
                "path": "/arena/rooms/{room_id}/leave",
                "methods": ["POST"],
                "summary": "Leave room"
            },
            # Battle routes
            {
                "path": "/arena/battles/{room_id}/start",
                "methods": ["POST"],
                "summary": "Start battle"
            },
            {
                "path": "/arena/battles/{battle_id}/answer",
                "methods": ["POST"],
                "summary": "Submit answer"
            },
            {
                "path": "/arena/battles/{battle_id}/result",
                "methods": ["GET"],
                "summary": "Get battle result"
            },
            {
                "path": "/arena/battles/history",
                "methods": ["GET"],
                "summary": "Battle history"
            },
            # Ranking routes
            {
                "path": "/arena/rankings",
                "methods": ["GET"],
                "summary": "Get rankings"
            },
            {
                "path": "/arena/rankings/me",
                "methods": ["GET"],
                "summary": "My rank"
            }
        ]


# Global service instances for route access
_arena_service: Optional['ArenaService'] = None
_battle_service: Optional['BattleService'] = None
_ranking_service: Optional['RankingService'] = None


def create_module(config: Optional[Dict[str, Any]] = None) -> ArenaModule:
    """
    Factory function to create an Arena module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured ArenaModule instance
    """
    return ArenaModule(config=config)


# For backwards compatibility with direct imports
ArenaService = None
BattleService = None
RankingService = None


def _lazy_import_services():
    """Lazy import to avoid circular imports."""
    global ArenaService, BattleService, RankingService
    if ArenaService is None:
        from .services import ArenaService as AS, BattleService as BS, RankingService as RS
        ArenaService = AS
        BattleService = BS
        RankingService = RS
    return ArenaService, BattleService, RankingService
