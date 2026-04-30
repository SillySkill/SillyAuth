"""
数据分析模块 - API路由
提供访问统计、页面浏览量、用户行为分析等接口
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from .schemas import (
    AnalyticsOverview,
    HourlyStat,
    TopPage,
    TrendDataPoint,
    UserActivitySummary,
)
from .services import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# ============================================
# 概览
# ============================================

@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(7, description="统计天数", ge=1, le=90),
) -> Dict[str, Any]:
    """
    获取分析概览数据

    返回访问量、页面浏览量、停留时间、跳出率等核心指标及环比变化
    """
    try:
        service = AnalyticsService()
        data = service.get_overview(days=days)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"获取分析概览失败: {str(e)}")
        return {"success": False, "message": f"获取分析概览失败: {str(e)}"}


# ============================================
# 趋势
# ============================================

@router.get("/trend")
async def get_analytics_trend(
    days: int = Query(30, description="统计天数", ge=7, le=365),
) -> Dict[str, Any]:
    """
    获取访问趋势数据

    按日期返回访问量和页面浏览量趋势
    """
    try:
        service = AnalyticsService()
        data = service.get_trend(days=days)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"获取访问趋势失败: {str(e)}")
        return {"success": False, "message": f"获取访问趋势失败: {str(e)}", "data": []}


# ============================================
# 热门页面
# ============================================

@router.get("/top-pages")
async def get_top_pages(
    limit: int = Query(10, description="返回数量", ge=1, le=50),
    days: int = Query(7, description="统计天数", ge=1, le=90),
) -> Dict[str, Any]:
    """
    获取热门页面

    返回访问量最高的页面列表
    """
    try:
        service = AnalyticsService()
        data = service.get_top_pages(limit=limit, days=days)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"获取热门页面失败: {str(e)}")
        return {"success": False, "message": f"获取热门页面失败: {str(e)}", "data": []}


# ============================================
# 用户活动摘要
# ============================================

@router.get("/user-activity")
async def get_user_activity_summary(
    days: int = Query(7, description="统计天数", ge=1, le=90),
) -> Dict[str, Any]:
    """
    获取用户活动摘要

    返回总用户数、活跃用户、新用户、回头客等数据
    """
    try:
        service = AnalyticsService()
        data = service.get_user_activity_summary(days=days)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"获取用户活动摘要失败: {str(e)}")
        return {"success": False, "message": f"获取用户活动摘要失败: {str(e)}"}


# ============================================
# 小时分布
# ============================================

@router.get("/hourly")
async def get_hourly_stats(
    days: int = Query(7, description="统计天数", ge=1, le=30),
) -> Dict[str, Any]:
    """
    获取每小时统计数据

    返回一天24小时的访问分布
    """
    try:
        service = AnalyticsService()
        data = service.get_hourly_stats(days=days)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"获取小时统计失败: {str(e)}")
        return {"success": False, "message": f"获取小时统计失败: {str(e)}", "data": []}


# ============================================
# 导出
# ============================================

@router.get("/export")
async def export_analytics(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    format: str = Query("json", description="导出格式: json, csv"),
) -> Dict[str, Any]:
    """
    导出分析数据

    支持导出为JSON或CSV格式
    """
    try:
        service = AnalyticsService()
        result = service.export_data(start_date=start_date, end_date=end_date, fmt=format)
        return {"success": True, "data": result["data"], "format": result["format"]}
    except Exception as e:
        logger.error(f"导出分析数据失败: {str(e)}")
        return {"success": False, "message": f"导出分析数据失败: {str(e)}"}
