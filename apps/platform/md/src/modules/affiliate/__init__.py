"""
Affiliate Module - 员工分销统计系统

提供分销相关的功能，包括：
- 分销员工管理
- 分享链接生成与追踪
- 订单归属与佣金计算
- 业绩排行榜
- 全局统计数据

模块结构:
    - config.yaml: 模块配置
    - schemas.py: Pydantic 数据模型
    - routes.py: API 路由定义
    - services.py: 业务逻辑服务

使用示例:
    from src.modules.affiliate import SillyMDModule, router

    # 注册模块
    module = SillyMDModule()
    module.register(app)

    # 使用服务
    from src.modules.affiliate.services import StaffService, LinkService

    # 创建员工
    staff = StaffService.create_staff(user_id=1, staff_name="张三")

    # 生成分享链接
    link = LinkService.create_affiliate_link(staff_id=staff['id'], product_id=123)
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

import yaml
from fastapi import FastAPI
from pydantic import BaseModel

from .schemas import (
    # Staff
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffStats,
    # Link
    LinkCreate,
    LinkResponse,
    LinkStats,
    # Order
    OrderAssignRequest,
    OrderResponse,
    OrderListResponse,
    # Visit
    VisitTrackRequest,
    VisitResponse,
    # Commission
    CommissionResponse,
    CommissionListResponse,
    # Leaderboard
    LeaderboardEntry,
    LeaderboardResponse,
    # Stats
    GlobalStats,
)
from .services import (
    StaffService,
    LinkService,
    VisitService,
    OrderService,
    CommissionService,
    LeaderboardService,
    StatsService,
    init_tables,
)
from .routes import router

__version__ = "1.0.0"

logger = logging.getLogger(__name__)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "affiliate"
    name: str = "分销系统模块"
    version: str = "1.0.0"
    description: str = "员工分销统计系统，支持通过分享链接追踪订单和统计员工业绩"
    dependencies: List[str] = ["auth"]
    author: str = "SillyMD Team"


# ============================================
# Module Config
# ============================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    default_commission_rate: float = 0.05
    link_expiry_days: int = 365
    visit_cookie_hours: int = 168
    leaderboard_limit: int = 50
    min_withdrawal: float = 100


# ============================================
# SillyMD Module
# ============================================

class SillyMDModule:
    """
    Affiliate Module - 分销系统模块

    提供分销相关的功能，包括分销员工管理、分享链接追踪、
    订单归属、佣金计算和业绩排行榜。
    """

    # Module identifier for PluginManager registration
    module_id: str = "affiliate"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Affiliate Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        logger.info(f"Affiliate module initialized (v{self.info.version})")

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

        # Include affiliate routes
        app.include_router(router)

        logger.info(f"Affiliate routes registered at {router.prefix}")

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
        logger.info("Affiliate module starting up...")

        # Initialize database tables
        try:
            init_tables()
            logger.info("Affiliate module database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize affiliate tables: {e}")

        logger.info("Affiliate module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks.
        """
        logger.info("Affiliate module shutting down...")
        logger.info("Affiliate module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/affiliate'):
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


# ============================================
# Module Services (convenience access)
# ============================================

class AffiliateServices:
    """Container for affiliate module services"""

    @property
    def staff(self) -> type:
        """Staff management service"""
        return StaffService

    @property
    def link(self) -> type:
        """Link management service"""
        return LinkService

    @property
    def visit(self) -> type:
        """Visit tracking service"""
        return VisitService

    @property
    def order(self) -> type:
        """Order assignment service"""
        return OrderService

    @property
    def commission(self) -> type:
        """Commission management service"""
        return CommissionService

    @property
    def leaderboard(self) -> type:
        """Leaderboard service"""
        return LeaderboardService

    @property
    def stats(self) -> type:
        """Global statistics service"""
        return StatsService


affiliate_services = AffiliateServices()


# ============================================
# Exports
# ============================================

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",
    "ModuleConfig",

    # Services
    "StaffService",
    "LinkService",
    "VisitService",
    "OrderService",
    "CommissionService",
    "LeaderboardService",
    "StatsService",
    "affiliate_services",
    "init_tables",

    # Schemas - Staff
    "StaffCreate",
    "StaffUpdate",
    "StaffResponse",
    "StaffStats",

    # Schemas - Link
    "LinkCreate",
    "LinkResponse",
    "LinkStats",

    # Schemas - Order
    "OrderAssignRequest",
    "OrderResponse",
    "OrderListResponse",

    # Schemas - Visit
    "VisitTrackRequest",
    "VisitResponse",

    # Schemas - Commission
    "CommissionResponse",
    "CommissionListResponse",

    # Schemas - Leaderboard
    "LeaderboardEntry",
    "LeaderboardResponse",

    # Schemas - Stats
    "GlobalStats",

    # Routes
    "router",

    # Version
    "__version__",
]
