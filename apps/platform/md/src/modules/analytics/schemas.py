"""
数据分析模块 - 数据模型
定义分析相关的Pydantic v2模型
"""

from typing import Optional

from pydantic import BaseModel, Field


class AnalyticsOverview(BaseModel):
    """分析概览数据"""
    totalVisitors: int
    pageViews: int
    avgTimeOnPage: float = 272.0
    bounceRate: float = 42.8
    visitorsChange: float = 0.0
    pageViewsChange: float = 0.0
    timeOnPageChange: float = 5.1
    bounceRateChange: float = -2.3


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str
    visitors: int
    pageViews: int
    uniqueVisitors: int


class TopPage(BaseModel):
    """热门页面"""
    url: str
    title: str
    views: int
    uniqueVisitors: int
    avgTimeOnPage: float = 120.0


class UserActivitySummary(BaseModel):
    """用户活动摘要"""
    totalUsers: int
    activeUsers: int
    newUsers: int
    returningUsers: int


class HourlyStat(BaseModel):
    """每小时统计"""
    hour: int
    views: int
    uniqueVisitors: int


class ExportDataPoint(BaseModel):
    """导出数据点"""
    date: Optional[str] = None
    hour: int = 0
    action: Optional[str] = None
    entity: Optional[str] = None
    username: Optional[str] = None
    count: int = 0
