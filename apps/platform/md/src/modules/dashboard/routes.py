"""
仪表盘API路由
提供仪表板数据概览、最近活动和用户统计功能
"""

from typing import Dict, Any

from fastapi import APIRouter, Query

from .services import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


# ============================================
# Dashboard API Endpoints
# ============================================

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    days: int = Query(7, description="统计天数", ge=1, le=90),
):
    """
    获取仪表板统计数据

    返回访问量、用户数、技能数、转化率和收入等核心指标，
    以及各指标相对于上一周期的变化率。
    """
    try:
        stats = DashboardService.get_stats(days=days)
        return {"success": True, "data": stats}
    except Exception as e:
        return {
            "success": False,
            "message": f"获取仪表板统计失败: {str(e)}",
        }


@router.get("/recent-activity", response_model=Dict[str, Any])
async def get_recent_activity(
    limit: int = Query(10, description="返回数量", ge=1, le=50),
):
    """
    获取最近活动列表

    返回用户登录、内容创建等最近活动，
    包含对应的 FontAwesome 图标和描述。
    """
    try:
        activities = DashboardService.get_recent_activity(limit=limit)
        return {"success": True, "data": activities}
    except Exception as e:
        return {
            "success": False,
            "message": f"获取最近活动失败: {str(e)}",
            "data": [],
        }


@router.get("/quick-actions", response_model=Dict[str, Any])
async def get_quick_actions():
    """
    获取快速操作列表

    返回用户常用的快捷操作。
    """
    actions = DashboardService.get_quick_actions()
    return {"success": True, "data": actions}


@router.get("/user-activity", response_model=Dict[str, Any])
async def get_user_activity(
    user_id: int = Query(..., description="用户ID"),
    days: int = Query(30, description="统计天数", ge=1, le=365),
):
    """
    获取用户活动统计

    返回指定用户的活动数据和每日趋势。
    """
    try:
        stats = DashboardService.get_user_activity(user_id=user_id, days=days)
        return {"success": True, "data": stats}
    except Exception as e:
        return {
            "success": False,
            "message": f"获取用户活动失败: {str(e)}",
        }


@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview():
    """
    获取仪表板概览数据

    一次性返回所有仪表板需要的数据，包括统计数据、最近活动和快速操作。
    """
    try:
        overview = DashboardService.get_overview()
        return {"success": True, "data": overview}
    except Exception as e:
        return {
            "success": False,
            "message": f"获取仪表板概览失败: {str(e)}",
        }
