"""
Recommendations Module
从外部来源（ClawHub、GitHub）抓取技能数据并推荐给用户
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "recommendations"
    name: str = "推荐系统模块"
    version: str = "1.0.0"
    description: str = "从 ClawHub、GitHub 等来源抓取技能数据并推荐给用户"
    dependencies: list = []


# ============================================================================
# SillyMD Module
# ============================================================================

class RecommendationsModule:
    """
    SillyMD Recommendations Module

    从外部来源抓取技能数据并推荐给用户
    """

    info = ModuleInfo()

    def __init__(self):
        self._service = None
        self._state = "uninstalled"

    @property
    def module_id(self) -> str:
        return self.info.id

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def install(self, app: FastAPI) -> None:
        """安装模块 - 注册路由和服务"""
        from .routes import router
        from .services import RecommendationsService

        # 初始化服务
        self._service = RecommendationsService()

        # 注册路由
        app.include_router(router, prefix="/api/recommendations", tags=["Recommendations"])

        self._state = "installed"
        logger.info(f"Recommendations module installed: {self.info.name} v{self.info.version}")

    def uninstall(self) -> None:
        """卸载模块"""
        self._service = None
        self._state = "uninstalled"
        logger.info(f"Recommendations module uninstalled: {self.info.id}")

    def on_startup(self) -> None:
        """启动时执行初始化"""
        if self._service:
            self._state = "active"
            logger.info("Recommendations module started")

    def on_shutdown(self) -> None:
        """关闭时清理资源"""
        if self._service:
            self._service.cleanup()
            self._state = "installed"
            logger.info("Recommendations module stopped")


# 创建模块实例
module = RecommendationsModule()
