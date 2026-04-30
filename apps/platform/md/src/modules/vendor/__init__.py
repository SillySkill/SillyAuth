"""
Vendor Module - SillyMD
开发者入驻模块

提供开发者入驻、认证、等级管理功能

模块结构:
    - config.yaml: 模块配置
    - schemas.py: 数据模型定义
    - services.py: 业务逻辑服务
    - routes.py: API路由
    - __init__.py: 模块入口

使用方法:
    from modules.vendor import VendorModule

    module = VendorModule()
    module.install(app)
"""

from typing import Optional, Any
import os
import sys
import yaml
import logging
from abc import abstractmethod

# Fix import path
_vendor_path = os.path.dirname(os.path.abspath(__file__))
_src_path = os.path.dirname(os.path.dirname(_vendor_path))
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

try:
    from core.module import BaseModule, ModuleInfo, ModuleState
    from core.config_loader import ConfigLoader
except ImportError:
    from src.core.module import BaseModule, ModuleInfo, ModuleState
    from src.core.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class VendorModule(BaseModule):
    """
    开发者入驻模块

    提供开发者入驻申请、认证、等级管理等功能
    """

    def __init__(self):
        """初始化模块"""
        super().__init__()
        self._config = {}
        self._router = None
        self._service = None
        # Initialize module info directly
        self._info = ModuleInfo(
            id="vendor",
            name="开发者入驻模块",
            version="1.0.0",
            description="提供开发者入驻、认证、等级管理功能",
            author="SillyMD Team",
            dependencies=["auth"]
        )

    @property
    def module_id(self) -> str:
        """模块唯一标识"""
        return "vendor"

    def _load_config(self) -> dict:
        """加载模块配置"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "config.yaml"
        )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load vendor config: {e}")
            return {
                "id": "vendor",
                "name": "开发者入驻模块",
                "version": "1.0.0",
                "description": "提供开发者入驻、认证、等级管理功能",
                "config": {
                    "tiers": [
                        {"id": "basic", "name": "基础开发者", "commission_rate": 0.7, "features": ["skills_basic", "skills_publish"]},
                        {"id": "standard", "name": "标准开发者", "commission_rate": 0.8, "features": ["skills_basic", "skills_publish", "analytics", "api_access"]},
                        {"id": "premium", "name": "高级开发者", "commission_rate": 0.85, "features": ["all"]},
                    ]
                }
            }

    def install(self, app: Any = None) -> None:
        """
        安装模块到应用

        Args:
            app: FastAPI应用实例
        """
        self._app = app
        self._state = ModuleState.INSTALLED

        # 加载配置
        self._config = self._load_config()

        # 注册路由
        from .routes import router
        self._router = router

        # 将路由挂载到应用
        if hasattr(app, 'include_router'):
            app.include_router(router)

        logger.info(f"Vendor module installed: {self.info.name} v{self.info.version}")

    def uninstall(self) -> None:
        """卸载模块"""
        self._state = ModuleState.UNINSTALLED
        self._config = {}
        self._router = None
        self._service = None
        logger.info("Vendor module uninstalled")

    def on_startup(self) -> None:
        """应用启动时的初始化"""
        self._state = ModuleState.ACTIVE

        # 初始化数据库表（如果需要）
        # self._init_database()

        logger.info("Vendor module started")

    def on_shutdown(self) -> None:
        """应用关闭时的清理"""
        self._state = ModuleState.INSTALLED
        logger.info("Vendor module stopped")

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，为None时返回全部配置
            default: 默认值

        Returns:
            配置值
        """
        if key is None:
            return self._config

        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_tiers(self) -> list:
        """获取开发者等级配置"""
        return self._config.get("config", {}).get("tiers", [])

    def get_tier(self, tier_id: str) -> Optional[dict]:
        """获取指定等级配置"""
        for tier in self.get_tiers():
            if tier.get("id") == tier_id:
                return tier
        return None


# 模块单例
_module_instance: Optional[VendorModule] = None


def get_module() -> VendorModule:
    """获取模块单例"""
    global _module_instance
    if _module_instance is None:
        _module_instance = VendorModule()
    return _module_instance


def install(app: Any) -> VendorModule:
    """安装并返回模块实例"""
    module = get_module()
    module.install(app)
    return module


__version__ = "1.0.0"
__all__ = [
    "VendorModule",
    "get_module",
    "install",
]
