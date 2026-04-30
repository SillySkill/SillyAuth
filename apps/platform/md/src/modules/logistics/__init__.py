"""
Logistics Module - 物流管理模块

SillyMD 物流管理模块，提供快递公司管理、运费计算、物流跟踪和面单生成功能。

模块结构:
    - config.yaml: 模块配置
    - schemas.py: Pydantic 数据模型
    - services.py: 业务逻辑层
    - routes.py: FastAPI 路由
    - clients/: 快递公司 API 客户端
        - base.py: 基础接口
        - shunfeng.py: 顺丰速运
        - yuantong.py: 圆通速递
        - zhongtong.py: 中通快递
        - kd100.py: 快递100

数据库表:
    - express_companies: 快递公司表
    - shipping_templates: 运费模板表
    - shipping_template_rules: 运费规则表
    - logistics_tracking: 物流跟踪表

API 路由:
    GET  /api/logistics/companies - 获取快递公司列表
    GET  /api/logistics/companies/{code} - 获取快递公司详情
    GET  /api/logistics/templates - 获取运费模板
    GET  /api/logistics/templates/{id} - 获取运费模板详情
    POST /api/logistics/templates - 创建运费模板
    PUT  /api/logistics/templates/{id} - 更新运费模板
    POST /api/logistics/calculate - 计算运费
    GET  /api/logistics/track/{tracking_number} - 物流跟踪
    POST /api/logistics/print - 生成面单数据
    GET  /api/logistics/health - 健康检查

使用示例:
    from src.modules.logistics import SillyMDModule, logistics_service

    # 创建模块实例
    module = SillyMDModule()
    module.register(app)

    # 使用服务
    result = logistics_service.calculate_shipping(request)

    # 查询物流
    info = await logistics_service.get_tracking_info("SF1234567890")
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
    ExpressCompanyResponse,
    ShippingTemplateResponse,
    ShippingCalculateRequest,
    ShippingCalculateResponse,
    TrackingInfo,
    TrackingResponse,
    ExpressLabelRequest,
    ExpressLabelResponse,
    LogisticsResponse,
)
from .services import (
    LogisticsService,
    ExpressCompanyService,
    ShippingTemplateService,
    get_logistics_service,
    logistics_service,
)
from .routes import router as logistics_router

logger = logging.getLogger(__name__)

__version__ = "1.0.0"


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "logistics"
    name: str = "物流管理模块"
    version: str = "1.0.0"
    description: str = "提供快递公司管理、运费计算、物流跟踪和面单生成功能"
    dependencies: List[str] = []


# ============================================================================
# Module Config
# ============================================================================

class PaginationConfig(BaseModel):
    """Pagination configuration"""
    default_page_size: int = 20
    max_page_size: int = 100


class ShippingConfig(BaseModel):
    """Shipping configuration"""
    default_first_weight: float = 1.0
    default_continue_weight: float = 1.0
    default_first_fee: float = 10.0
    default_continue_fee: float = 5.0
    free_shipping_threshold: float = 99.0


class Kd100Config(BaseModel):
    """Kuaidi100 API configuration"""
    api_url: str = "https://api.kuaidi100.com/api"
    app_key: str = ""


class ModuleConfig(BaseModel):
    """Module configuration"""
    pagination: PaginationConfig = PaginationConfig()
    shipping: ShippingConfig = ShippingConfig()
    kd100: Kd100Config = Kd100Config()


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Logistics Module

    Provides logistics management functionality including:
    - Express company management
    - Shipping template management
    - Shipping fee calculation
    - Logistics tracking
    - Express label generation
    """

    # Module identifier
    module_id: str = "logistics"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Logistics Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._service: Optional[LogisticsService] = None
        self._load_config(config_path)

        logger.info(f"Logistics module initialized (v{self.info.version})")

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load module configuration from YAML file

        Args:
            config_path: Optional path to config file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)

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

    @property
    def service(self) -> LogisticsService:
        """Get logistics service instance."""
        if self._service is None:
            config_dict = self.config.model_dump() if self.config else None
            self._service = get_logistics_service(config_dict)
        return self._service

    def register(self, app: FastAPI) -> None:
        """
        Register module routes with FastAPI application

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Include logistics routes
        app.include_router(logistics_router)

        logger.info(f"Logistics routes registered at {logistics_router.prefix}")

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks.
        """
        logger.info("Logistics module starting up...")

        # Initialize service with config
        if self.config:
            config_dict = self.config.model_dump()
            get_logistics_service(config_dict)
            logger.info("Logistics module service initialized with config")

        logger.info("Logistics module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks.
        """
        logger.info("Logistics module shutting down...")

        # TODO: Save any cached data
        # TODO: Close connections

        logger.info("Logistics module shutdown complete")

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
            if hasattr(route, 'path') and route.path.startswith('/api/logistics'):
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

    def health_check(self) -> Dict[str, Any]:
        """
        Health check for logistics module.

        Returns:
            Dict with health status
        """
        try:
            # Check services
            companies = self.service.express_company_service.list_companies()
            templates = self.service.shipping_template_service.list_templates()

            return {
                "status": "healthy",
                "module": self.info.id,
                "version": self.info.version,
                "express_companies": len(companies),
                "shipping_templates": len(templates)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "module": self.info.id,
                "error": str(e)
            }


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",
    "ModuleConfig",

    # Services
    "LogisticsService",
    "ExpressCompanyService",
    "ShippingTemplateService",
    "get_logistics_service",
    "logistics_service",

    # Schemas
    "ExpressCompanyResponse",
    "ShippingTemplateResponse",
    "ShippingCalculateRequest",
    "ShippingCalculateResponse",
    "TrackingInfo",
    "TrackingResponse",
    "ExpressLabelRequest",
    "ExpressLabelResponse",
    "LogisticsResponse",

    # Routes
    "router",
]
