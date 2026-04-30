"""
数据分析模块 - 服务层
处理分析相关的业务逻辑
"""

import csv
import io
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.core.db_adapter import get_db_cursor

logger = logging.getLogger(__name__)


class AnalyticsService:
    """数据分析服务"""

    # ============================================
    # 概览
    # ============================================

    @staticmethod
    def get_overview(days: int = 7) -> Dict[str, Any]:
        """
        获取分析概览数据，包含环比变化。

        Args:
            days: 统计天数

        Returns:
            概览数据字典
        """
        try:
            with get_db_cursor() as cur:
                current_period_start = datetime.now() - timedelta(days=days)
                previous_period_start = current_period_start - timedelta(days=days)

                # 当前期间统计
                cur.execute("""
                    SELECT
                        COUNT(DISTINCT user_id) as unique_visitors,
                        COUNT(*) as total_views,
                        COUNT(DISTINCT DATE(created_at)) as active_days
                    FROM user_activity_logs
                    WHERE created_at >= %s
                """, (current_period_start,))
                current_stats = cur.fetchone()

                # 上一期间统计（用于计算变化率）
                cur.execute("""
                    SELECT
                        COUNT(DISTINCT user_id) as unique_visitors,
                        COUNT(*) as total_views
                    FROM user_activity_logs
                    WHERE created_at >= %s AND created_at < %s
                """, (previous_period_start, current_period_start))
                previous_stats = cur.fetchone()

                # 模拟平均停留时间和跳出率（实际需要更复杂的计算）
                avg_time_on_page = 272.0  # 4分32秒
                bounce_rate = 42.8

                # 计算变化率
                visitors_change = 0.0
                page_views_change = 0.0

                prev_visitors = previous_stats.get('unique_visitors') if previous_stats else 0
                prev_views = previous_stats.get('total_views') if previous_stats else 0
                curr_visitors = current_stats.get('unique_visitors') if current_stats else 0
                curr_views = current_stats.get('total_views') if current_stats else 0

                if prev_visitors and prev_visitors > 0:
                    visitors_change = ((curr_visitors - prev_visitors) / prev_visitors) * 100

                if prev_views and prev_views > 0:
                    page_views_change = ((curr_views - prev_views) / prev_views) * 100

                return {
                    "totalVisitors": curr_visitors or 0,
                    "pageViews": curr_views or 0,
                    "avgTimeOnPage": avg_time_on_page,
                    "bounceRate": bounce_rate,
                    "visitorsChange": round(visitors_change, 1),
                    "pageViewsChange": round(page_views_change, 1),
                    "timeOnPageChange": 5.1,
                    "bounceRateChange": -2.3,
                }
        except Exception as e:
            logger.error(f"获取分析概览失败: {str(e)}")
            raise

    # ============================================
    # 趋势
    # ============================================

    @staticmethod
    def get_trend(days: int = 30) -> List[Dict[str, Any]]:
        """
        获取访问趋势数据，按日期聚合。

        Args:
            days: 统计天数

        Returns:
            趋势数据列表
        """
        try:
            with get_db_cursor() as cur:
                start_date = datetime.now() - timedelta(days=days)

                cur.execute("""
                    SELECT
                        DATE(created_at) as date,
                        COUNT(DISTINCT user_id) as unique_visitors,
                        COUNT(*) as total_views
                    FROM user_activity_logs
                    WHERE created_at >= %s
                    GROUP BY DATE(created_at)
                    ORDER BY date ASC
                """, (start_date,))

                trend_data = []
                for row in cur.fetchall():
                    trend_data.append({
                        "date": row['date'].isoformat() if row['date'] else None,
                        "visitors": row['unique_visitors'] or 0,
                        "pageViews": row['total_views'] or 0,
                        "uniqueVisitors": row['unique_visitors'] or 0,
                    })

                return trend_data
        except Exception as e:
            logger.error(f"获取访问趋势失败: {str(e)}")
            raise

    # ============================================
    # 热门页面
    # ============================================

    @staticmethod
    def get_top_pages(limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取热门页面排行。

        Args:
            limit: 返回数量
            days: 统计天数

        Returns:
            热门页面列表
        """
        try:
            with get_db_cursor() as cur:
                start_date = datetime.now() - timedelta(days=days)

                cur.execute("""
                    SELECT
                        entity,
                        COUNT(*) as views,
                        COUNT(DISTINCT user_id) as unique_visitors
                    FROM user_activity_logs
                    WHERE created_at >= %s
                      AND entity IS NOT NULL
                    GROUP BY entity
                    ORDER BY views DESC
                    LIMIT %s
                """, (start_date, limit))

                top_pages = []
                for row in cur.fetchall():
                    entity = row['entity']
                    title = entity
                    if 'skill' in entity.lower():
                        title = f"Skill: {entity}"

                    top_pages.append({
                        "url": f"/{entity.lower()}",
                        "title": title,
                        "views": row['views'],
                        "uniqueVisitors": row['unique_visitors'],
                        "avgTimeOnPage": 120.0,  # 模拟数据，实际需要计算
                    })

                return top_pages
        except Exception as e:
            logger.error(f"获取热门页面失败: {str(e)}")
            raise

    # ============================================
    # 用户活动摘要
    # ============================================

    @staticmethod
    def get_user_activity_summary(days: int = 7) -> Dict[str, Any]:
        """
        获取用户活动摘要统计。

        Args:
            days: 统计天数

        Returns:
            用户活动摘要字典
        """
        try:
            with get_db_cursor() as cur:
                start_date = datetime.now() - timedelta(days=days)

                # 总用户数（活跃，排除种子用户）
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM users
                    WHERE is_active = TRUE
                      AND email NOT LIKE '%@seed.local'
                """)
                total_users = cur.fetchone()['count'] or 0

                # 期间活跃用户
                cur.execute("""
                    SELECT COUNT(DISTINCT user_id) as count
                    FROM user_activity_logs
                    WHERE created_at >= %s
                """, (start_date,))
                active_users = cur.fetchone()['count'] or 0

                # 期间新用户
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM users
                    WHERE created_at >= %s
                      AND is_active = TRUE
                      AND email NOT LIKE '%@seed.local'
                """, (start_date,))
                new_users = cur.fetchone()['count'] or 0

                # 回头客（有历史活动记录的用户）
                cur.execute("""
                    SELECT COUNT(DISTINCT al.user_id) as count
                    FROM user_activity_logs al
                    WHERE al.created_at >= %s
                      AND al.user_id IN (
                        SELECT DISTINCT user_id
                        FROM user_activity_logs
                        WHERE created_at < %s
                      )
                """, (start_date, start_date))
                returning_users = cur.fetchone()['count'] or 0

                return {
                    "totalUsers": total_users,
                    "activeUsers": active_users,
                    "newUsers": new_users,
                    "returningUsers": returning_users,
                }
        except Exception as e:
            logger.error(f"获取用户活动摘要失败: {str(e)}")
            raise

    # ============================================
    # 小时分布
    # ============================================

    @staticmethod
    def get_hourly_stats(days: int = 7) -> List[Dict[str, Any]]:
        """
        获取每小时访问分布，填充所有24小时。

        Args:
            days: 统计天数

        Returns:
            完整的24小时统计列表
        """
        try:
            with get_db_cursor() as cur:
                start_date = datetime.now() - timedelta(days=days)

                cur.execute("""
                    SELECT
                        EXTRACT(HOUR FROM created_at) as hour,
                        COUNT(*) as views,
                        COUNT(DISTINCT user_id) as unique_visitors
                    FROM user_activity_logs
                    WHERE created_at >= %s
                    GROUP BY EXTRACT(HOUR FROM created_at)
                    ORDER BY hour
                """, (start_date,))

                # 构建已有的小时映射
                hourly_map = {}
                for row in cur.fetchall():
                    hour_val = int(row['hour'])
                    hourly_map[hour_val] = {
                        "hour": hour_val,
                        "views": row['views'],
                        "uniqueVisitors": row['unique_visitors'],
                    }

                # 填充所有24小时
                complete_data = []
                for hour in range(24):
                    if hour in hourly_map:
                        complete_data.append(hourly_map[hour])
                    else:
                        complete_data.append({
                            "hour": hour,
                            "views": 0,
                            "uniqueVisitors": 0,
                        })

                return complete_data
        except Exception as e:
            logger.error(f"获取小时统计失败: {str(e)}")
            raise

    # ============================================
    # 导出
    # ============================================

    @staticmethod
    def export_data(start_date: str, end_date: str, fmt: str = "json") -> Dict[str, Any]:
        """
        导出分析数据。

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            fmt: 导出格式 (json / csv)

        Returns:
            导出数据和格式信息
        """
        try:
            with get_db_cursor() as cur:
                # 解析日期
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

                cur.execute("""
                    SELECT
                        DATE(al.created_at) as date,
                        EXTRACT(HOUR FROM al.created_at) as hour,
                        al.action,
                        al.entity,
                        u.username,
                        COUNT(*) as count
                    FROM user_activity_logs al
                    LEFT JOIN users u ON al.user_id = u.id
                    WHERE al.created_at >= %s AND al.created_at < %s
                    GROUP BY DATE(al.created_at), EXTRACT(HOUR FROM al.created_at), al.action, al.entity, u.username
                    ORDER BY date, hour
                """, (start_dt, end_dt))

                data = []
                for row in cur.fetchall():
                    data.append({
                        "date": row['date'].isoformat() if row['date'] else None,
                        "hour": int(row['hour']) if row['hour'] is not None else 0,
                        "action": row['action'],
                        "entity": row['entity'],
                        "username": row['username'],
                        "count": row['count'],
                    })

                if fmt == "csv":
                    output = io.StringIO()
                    writer = csv.writer(output)
                    writer.writerow(["date", "hour", "action", "entity", "username", "count"])
                    for item in data:
                        writer.writerow([
                            item["date"],
                            item["hour"],
                            item["action"],
                            item["entity"],
                            item["username"],
                            item["count"],
                        ])
                    csv_data = output.getvalue()
                    output.close()

                    return {
                        "data": csv_data,
                        "format": "csv",
                    }

                return {
                    "data": data,
                    "format": "json",
                }
        except Exception as e:
            logger.error(f"导出分析数据失败: {str(e)}")
            raise
