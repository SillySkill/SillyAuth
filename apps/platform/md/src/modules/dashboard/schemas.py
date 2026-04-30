"""
仪表盘数据模型
定义仪表盘相关的Pydantic v2模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DashboardStats(BaseModel):
    """仪表板统计数据"""
    totalViews: float = 0.0
    totalUsers: float = 0.0
    totalSkills: float = 0.0
    conversionRate: float = 0.0
    revenue: float = 0.0
    viewsChange: float = 0.0
    usersChange: float = 0.0
    conversionChange: float = 0.0
    revenueChange: float = 0.0


class ActivityItem(BaseModel):
    """活动项"""
    id: int
    action: str
    username: Optional[str] = None
    description: str
    timestamp: datetime
    icon: str


class QuickAction(BaseModel):
    """快速操作"""
    name: str
    icon: str
    url: str
    description: str


class UserActivityStats(BaseModel):
    """用户活动统计"""
    totalActions: int = 0
    activeDays: int = 0
    logins: int = 0
    skillsCreated: int = 0
    dailyTrend: List[dict] = Field(default_factory=list)


class DashboardOverview(BaseModel):
    """仪表板概览"""
    stats: DashboardStats
    recentActivity: List[ActivityItem] = Field(default_factory=list)
    quickActions: List[QuickAction] = Field(default_factory=list)
