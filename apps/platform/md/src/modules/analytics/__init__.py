"""
数据分析模块 (Analytics Module)

提供访问统计、页面浏览量、用户行为分析等功能

功能:
- 概览统计（含环比变化）
- 访问趋势分析
- 热门页面排行
- 用户活动摘要
- 小时流量分布
- 数据导出（JSON/CSV）
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .routes import router as analytics_router
from .services import AnalyticsService
from .schemas import (
    AnalyticsOverview,
    TrendDataPoint,
    TopPage,
    UserActivitySummary,
    HourlyStat,
    ExportDataPoint,
)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "analytics"
    name: str = "数据分析模块"
    version: str = "1.0.0"
    description: str = "提供访问统计、页面浏览量、用户行为分析等功能"
    dependencies: List[str] = []


# ============================================
# BaseModule
# ============================================

class BaseModule:
    """模块基类"""

    def __init__(self):
        self.id = "analytics"
        self.name = "数据分析模块"
        self.version = "1.0.0"
        self.description = "提供访问统计、页面浏览量、用户行为分析等功能"
        self.dependencies: List[str] = []
        self.router = analytics_router
        self._info = ModuleInfo()

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "analytics"

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
            "analytics": AnalyticsService,
        }

    def get_config(self):
        """获取模块配置"""
        return {
            "default_days": 7,
            "max_trend_days": 365,
            "default_top_pages_limit": 10,
        }


# 创建模块实例
module = BaseModule()


# 导出
__all__ = [
    # 模块信息
    "ModuleInfo",

    # 路由
    "analytics_router",

    # 服务
    "AnalyticsService",

    # 模型
    "AnalyticsOverview",
    "TrendDataPoint",
    "TopPage",
    "UserActivitySummary",
    "HourlyStat",
    "ExportDataPoint",

    # 模块
    "BaseModule",
    "module",
]
