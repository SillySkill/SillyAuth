from __future__ import annotations
import logging
from typing import Optional
from pathlib import Path
import yaml
from fastapi import FastAPI

from .routes import router as config_data_router

logger = logging.getLogger(__name__)


class SillyMDModule:
    """通用配置数据模块"""

    module_id: str = "config_data"
    info = {
        "id": "config_data",
        "name": "通用配置数据模块",
        "version": "1.0.0",
        "description": "提供通用配置数据存储功能，支持任意JSON格式数据",
        "dependencies": [],
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = None
        self.app = None
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[str] = None) -> None:
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件未找到: {config_path}")
            self.config = {}

    def register(self, app: FastAPI) -> None:
        """注册模块路由"""
        self.app = app
        app.include_router(config_data_router)
        logger.info("通用配置数据模块已注册")

    def install(self, app: FastAPI) -> None:
        """安装模块 - 与 register 相同"""
        self.register(app)

    def on_startup(self) -> None:
        """启动钩子"""
        logger.info("通用配置数据模块启动")

    def on_shutdown(self) -> None:
        """关闭钩子"""
        logger.info("通用配置数据模块关闭")


__all__ = ["SillyMDModule", "router"]
router = config_data_router
