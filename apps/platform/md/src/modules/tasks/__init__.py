"""
Tasks Module
SillyMD Task System Module

Provides daily tasks, check-ins, achievements, and task statistics functionality.

Features:
- Daily task management with progress tracking
- Daily check-in with streak bonuses
- Achievement system with unlock conditions
- Task and achievement reward claiming
- Comprehensive statistics tracking

Usage:
    from src.modules.tasks import SillyMDModule, router

    # In your FastAPI app:
    tasks_module = SillyMDModule()
    tasks_module.register(app)

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
    DailyTask,
    DailyTaskListResponse,
    CheckInRecord,
    CheckInStatus,
    ClaimResponse,
    UserAchievement,
    AchievementListResponse,
    TaskStats,
    TaskType,
    RewardType,
    SignInCalendarDay,
    SignInCalendarResponse,
)
from .services import (
    TaskService,
    CheckInService,
    AchievementService,
    TaskStatsService,
    init_tables,
    DEFAULT_SIGN_IN_CONFIG,
    DEFAULT_DAILY_TASKS,
    DEFAULT_ACHIEVEMENTS
)
from .routes import router as tasks_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "tasks"
    name: str = "任务系统模块"
    version: str = "1.0.0"
    description: str = "提供签到、成就、日常任务功能"
    dependencies: List[str] = ["auth", "points"]


# ============================================================================
# Module Config
# ============================================================================

class SignInConfig(BaseModel):
    """Check-in configuration"""
    enabled: bool = True
    base_points: int = 10
    streak_bonus: int = 2
    max_streak_days: int = 30


class ModuleConfig(BaseModel):
    """Module configuration"""
    sign_in: SignInConfig = SignInConfig()
    daily_reset_hour: int = 0  # UTC


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Tasks Module

    Extends BaseModule pattern to integrate task system
    functionality into the SillyMD application.

    Features:
    - Daily task management
    - Check-in system with streak bonuses
    - Achievement tracking and rewards
    - Task statistics
    """

    # Module identifier for PluginManager registration
    module_id: str = "tasks"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Tasks Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Tasks module initialized (v{self.info.version})")

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
                    sign_in_config = config_data['config'].get('sign_in', {})
                    self.config = ModuleConfig(
                        sign_in=SignInConfig(**sign_in_config) if sign_in_config else SignInConfig(),
                        daily_reset_hour=config_data['config'].get('daily_reset_hour', 0)
                    )
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

        # Include tasks routes
        app.include_router(tasks_router)

        logger.info(f"Tasks routes registered at {tasks_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks like:
        - Database table initialization
        - Default data setup
        """
        logger.info("Tasks module starting up...")

        # Initialize database tables
        try:
            init_tables()
            logger.info("Tasks module database tables initialized")
        except Exception as e:
            logger.error(f"Tasks module database initialization failed: {e}")

        logger.info("Tasks module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks.
        """
        logger.info("Tasks module shutting down...")
        logger.info("Tasks module shutdown complete")

    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Get list of registered routes

        Returns:
            List of route dictionaries with method, path, and handler info
        """
        if not self.app:
            return []

        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/tasks'):
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

    # Convenience methods
    def get_sign_in_config(self) -> Dict[str, Any]:
        """Get check-in configuration as dict"""
        if self.config and self.config.sign_in:
            return self.config.sign_in.model_dump()
        return DEFAULT_SIGN_IN_CONFIG

    def get_default_tasks(self) -> List[Dict[str, Any]]:
        """Get default task definitions"""
        return DEFAULT_DAILY_TASKS

    def get_default_achievements(self) -> List[Dict[str, Any]]:
        """Get default achievement definitions"""
        return DEFAULT_ACHIEVEMENTS


# ============================================================================
# Service Aliases for External Use
# ============================================================================

# These provide convenient access to module services
task_service = TaskService
check_in_service = CheckInService
achievement_service = AchievementService
task_stats_service = TaskStatsService


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "TaskService",
    "CheckInService",
    "AchievementService",
    "TaskStatsService",
    "task_service",
    "check_in_service",
    "achievement_service",
    "task_stats_service",

    # Schemas
    "DailyTask",
    "DailyTaskListResponse",
    "CheckInRecord",
    "CheckInStatus",
    "ClaimResponse",
    "UserAchievement",
    "AchievementListResponse",
    "TaskStats",
    "TaskType",
    "RewardType",
    "SignInCalendarDay",
    "SignInCalendarResponse",

    # Routes
    "router",

    # Constants
    "DEFAULT_SIGN_IN_CONFIG",
    "DEFAULT_DAILY_TASKS",
    "DEFAULT_ACHIEVEMENTS",
]
