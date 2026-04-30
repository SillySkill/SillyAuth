"""
仪表盘模块 (Dashboard Module)

提供仪表板数据概览、最近活动和用户统计功能

功能:
- 仪表板统计数据（周期对比）
- 最近活动列表
- 快速操作
- 用户活动统计
- 仪表板概览（聚合端点）
"""
from __future__ import annotations

from typing import List
from pydantic import BaseModel

from .routes import router as dashboard_router
from .services import DashboardService
from .schemas import (
    DashboardStats,
    ActivityItem,
    QuickAction,
    UserActivityStats,
    DashboardOverview,
)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "dashboard"
    name: str = "仪表盘模块"
    version: str = "1.0.0"
    description: str = "提供仪表板数据概览、最近活动和用户统计功能"
    dependencies: List[str] = ["auth"]


# ============================================
# BaseModule
# ============================================

class BaseModule:
    """模块基类"""

    def __init__(self):
        self.id = "dashboard"
        self.name = "仪表盘模块"
        self.version = "1.0.0"
        self.description = "提供仪表板数据概览、最近活动和用户统计功能"
        self.dependencies = ["auth"]
        self.router = dashboard_router
        self._info = ModuleInfo()

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "dashboard"

    @property
    def info(self):
        """Get module info."""
        return self._info

    def get_router(self):
        """获取路由"""
        return self.router

    def get_services(self):
        """获取服务实例"""
        return {
            "dashboard": DashboardService,
        }

    def get_config(self):
        """获取模块配置"""
        return {
            "default_days": 7,
            "max_days": 90,
            "default_activity_limit": 10,
        }


# 创建模块实例
module = BaseModule()


# 导出
__all__ = [
    # 模块信息
    "ModuleInfo",

    # 路由
    "dashboard_router",

    # 服务
    "DashboardService",

    # 模型
    "DashboardStats",
    "ActivityItem",
    "QuickAction",
    "UserActivityStats",
    "DashboardOverview",

    # 模块
    "BaseModule",
    "module",
]
