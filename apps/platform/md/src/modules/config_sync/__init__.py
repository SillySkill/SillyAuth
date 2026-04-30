"""
Config Sync Module
SillyMD Configuration Sync Module

Provides client configuration version management, file distribution,
and update log tracking functionality.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yaml

from fastapi import FastAPI
from pydantic import BaseModel

from .routes import router as config_sync_router

logger = logging.getLogger(__name__)

class ModuleInfo(BaseModel):
    id: str = "config_sync"
    name: str = "配置同步模块"
    version: str = "1.0.0"
    description: str = "客户端配置文件版本管理和同步"
    dependencies: list = []

class ModuleConfig(BaseModel):
    storage_path: str = "/data/config"
    max_versions: int = 10

class SillyMDModule:
    module_id: str = "config_sync"
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self._load_config(config_path)
        logger.info(f"ConfigSync module initialized (v{self.info.version})")

    def _load_config(self, config_path: Optional[str] = None) -> None:
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
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                self.config = ModuleConfig()
        else:
            self.config = ModuleConfig()

    def register(self, app: FastAPI) -> None:
        app.include_router(config_sync_router)
        self.app = app
        logger.info(f"ConfigSync routes registered")

    def install(self, app: FastAPI) -> None:
        self.register(app)

    def on_startup(self) -> None:
        logger.info("ConfigSync module starting up...")
        logger.info("ConfigSync module startup complete")

    def on_shutdown(self) -> None:
        logger.info("ConfigSync module shutting down...")
        logger.info("ConfigSync module shutdown complete")

    def get_routes(self) -> list:
        if not self.app: return []
        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/v1/config'):
                routes.append({
                    "method": next(iter(getattr(route, 'methods', {'GET'}))),
                    "path": route.path,
                    "name": getattr(route, 'name', 'unnamed')
                })
        return routes

    def get_info(self) -> Dict[str, Any]:
        return {
            "id": self.info.id, "name": self.info.name,
            "version": self.info.version, "description": self.info.description,
            "dependencies": self.info.dependencies,
            "config": self.config.model_dump() if self.config else None
        }

__all__ = ["SillyMDModule", "ModuleInfo", "ModuleConfig", "config_sync_router"]
