"""
Storage Module - TOS 对象存储模块

提供 TOS (火山引擎对象存储) 集成，为平台提供文件存储服务。

模块配置 (config.yaml):
    - tos: TOS 连接配置
        - endpoint: TOS 端点
        - bucket: 存储桶名称
        - access_key: 访问密钥 (通过环境变量 TOS_ACCESS_KEY)
        - secret_key: 秘密密钥 (通过环境变量 TOS_SECRET_KEY)
        - custom_domain: 自定义域名

    - upload: 上传配置
        - max_file_size_mb: 最大文件大小 (MB)
        - allowed_types: 允许的文件类型

使用示例:
    from src.modules.storage import get_storage_service, router

    # 初始化服务
    storage = get_storage_service(config)

    # 上传文件
    result = storage.upload(content, "images/", "photo.jpg")

    # 获取签名 URL
    url = storage.get_url(key, signed=True, expires_seconds=3600)

    # 列出文件
    files = storage.list("documents/")

    # 删除文件
    storage.delete(key)

环境变量:
    TOS_ACCESS_KEY: TOS 访问密钥
    TOS_SECRET_KEY: TOS 秘密密钥
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from .tos_client import TosClient, get_tos_client
from .services import StorageService, get_storage_service
from .schemas import (
    UploadRequest,
    UploadResponse,
    FileInfo,
    FileListResponse,
    SignedUrlRequest,
    SignedUrlResponse,
    StorageUsageStats,
    StorageConfig
)
from .routes import router

__version__ = "1.0.0"

logger = logging.getLogger(__name__)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "storage"
    name: str = "存储模块"
    version: str = "1.0.0"
    description: str = "提供 TOS 对象存储服务"
    dependencies: List[str] = []


class BaseModule:
    """
    存储模块基类

    提供模块的统一接口
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化模块

        Args:
            config: 模块配置 (可选)
        """
        if config is None:
            config = {}
        self.config = config
        self.id = config.get("id", "storage")
        self.name = config.get("name", "Storage Module")
        self.version = config.get("version", "1.0.0")
        self.description = config.get("description", "")

        # 初始化服务
        self._storage_service: Optional[StorageService] = None
        self._info = ModuleInfo()
        self._state = "INSTALLED"

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "storage"

    @property
    def info(self):
        """Get module info."""
        return self._info

    @property
    def state(self):
        """Get module state."""
        return self._state

    @state.setter
    def state(self, value):
        """Set module state."""
        self._state = value

    def initialize(self):
        """初始化模块服务"""
        try:
            # 使用 core.config 中的 get_tos_config() 来获取 TOS 配置
            from core.config import get_tos_config
            tos_config = get_tos_config()

            # 构建存储服务配置
            storage_config = {
                "tos": {
                    "endpoint": tos_config.endpoint,
                    "region": getattr(tos_config, 'region', 'cn-shanghai'),
                    "bucket": tos_config.bucket,
                    "access_key": tos_config.access_key,
                    "secret_key": tos_config.secret_key,
                    "custom_domain": tos_config.custom_domain,
                },
                "default_folder": tos_config.default_prefix,
                "upload": {
                    "max_file_size_mb": 500,
                    "allowed_types": ["image", "video", "audio", "document", "archive"]
                }
            }

            self._storage_service = get_storage_service(storage_config)
            logger.info(f"Storage module initialized: {self.name} v{self.version}")
        except Exception as e:
            logger.error(f"Failed to initialize storage module: {e}")
            raise

    def install(self, app):
        """安装模块 - 注册路由"""
        from core.module import ModuleState
        import sys
        try:
            # 初始化存储服务
            self.initialize()
            # 注册路由
            logger.info(f"Storage: Before include_router, app routes count: {len(app.routes)}")
            app.include_router(router)
            logger.info(f"Storage: After include_router, app routes count: {len(app.routes)}")
            self._state = ModuleState.ACTIVE
            logger.info(f"Storage module installed, routes registered at {router.prefix}")
        except Exception as e:
            logger.error(f"Failed to install storage module: {e}")
            raise

    def get_service(self) -> StorageService:
        """获取存储服务实例"""
        if self._storage_service is None:
            self.initialize()
        return self._storage_service

    def get_router(self):
        """获取路由"""
        return router

    def get_config(self) -> Dict[str, Any]:
        """获取模块配置"""
        return self.config

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            service = self.get_service()
            service.list(folder="", max_keys=1)
            return {
                "status": "healthy",
                "module": self.id,
                "version": self.version
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "module": self.id,
                "version": self.version,
                "error": str(e)
            }


# 模块实例
_module_instance: Optional[BaseModule] = None


def create_module(config: Dict[str, Any]) -> BaseModule:
    """
    创建存储模块实例

    Args:
        config: 模块配置

    Returns:
        BaseModule: 模块实例
    """
    global _module_instance
    _module_instance = BaseModule(config)
    return _module_instance


def get_module() -> BaseModule:
    """
    获取存储模块实例

    Returns:
        BaseModule: 模块实例
    """
    if _module_instance is None:
        raise RuntimeError("Storage module not created. Call create_module(config) first.")
    return _module_instance


# 导出
__all__ = [
    # 版本
    "__version__",
    # 核心类
    "BaseModule",
    "ModuleInfo",
    "TosClient",
    "StorageService",
    # 工厂函数
    "create_module",
    "get_module",
    "get_tos_client",
    "get_storage_service",
    # 路由
    "router",
    # Schemas
    "UploadRequest",
    "UploadResponse",
    "FileInfo",
    "FileListResponse",
    "SignedUrlRequest",
    "SignedUrlResponse",
    "StorageUsageStats",
    "StorageConfig",
]
