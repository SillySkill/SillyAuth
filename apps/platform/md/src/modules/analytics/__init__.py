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

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template

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

    def install(self, app: FastAPI) -> None:
        """安装模块到应用"""
        app.include_router(self.router)
        # Page routes
        @app.get("/analytics", response_class=HTMLResponse, include_in_schema=False)
        async def analytics_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                analytics = {}
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT COUNT(*) as cnt FROM users")
                        analytics["total_users"] = cur.fetchone()["cnt"]
                        cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE is_deleted = FALSE")
                        analytics["total_skills"] = cur.fetchone()["cnt"]
                        cur.execute("SELECT COALESCE(SUM(download_count), 0) as cnt FROM skills")
                        analytics["total_downloads"] = cur.fetchone()["cnt"]
                        cur.execute("SELECT COUNT(*) as cnt FROM vendors")
                        analytics["total_vendors"] = cur.fetchone()["cnt"]
                except Exception:
                    analytics = {}
            except Exception:
                analytics = {}

            # Map to template-expected field names
            overview = {
                "total_visits": analytics.get("total_users", 0),
                "visits_change": "+0%",
                "total_pageviews": analytics.get("total_skills", 0),
                "pageviews_change": "+0%",
                "avg_duration": "0m 0s",
                "duration_change": "+0%",
                "bounce_rate": "0%",
                "bounce_change": "+0%",
            }
            trends = []
            top_pages = []
            return render_template(request, "analytics/index.html", {
                "overview": overview,
                "trends": trends,
                "top_pages": top_pages,
            })

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
