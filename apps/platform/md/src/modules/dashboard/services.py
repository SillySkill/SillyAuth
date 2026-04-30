"""
仪表盘服务层
处理仪表盘相关的业务逻辑
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from core.db_adapter import get_db_cursor


class DashboardService:
    """仪表盘服务"""

    # FontAwesome 图标映射
    ACTION_ICON_MAP = {
        'LOGIN': 'fa-sign-in-alt',
        'LOGOUT': 'fa-sign-out-alt',
        'CREATE_SKILL': 'fa-file-alt',
        'UPDATE_SKILL': 'fa-edit',
        'DELETE_SKILL': 'fa-trash',
        'REGISTER': 'fa-user-plus',
        'COMMENT': 'fa-comment',
        'DOWNLOAD': 'fa-download',
        'FAVORITE': 'fa-heart',
    }

    # 模拟数据（后续由真实支付/订单数据替换）
    MOCK_CONVERSION_RATE = 68.2
    MOCK_REVENUE = 12345.0
    MOCK_CONVERSION_CHANGE = 5.1
    MOCK_REVENUE_CHANGE = -2.3

    # 静态快速操作列表
    QUICK_ACTIONS = [
        {
            "name": "新建项目",
            "icon": "fa-plus-circle",
            "url": "projects.html",
            "description": "创建新的项目"
        },
        {
            "name": "发送消息",
            "icon": "fa-envelope",
            "url": "messages.html",
            "description": "给其他用户发送消息"
        },
        {
            "name": "查看分析",
            "icon": "fa-chart-line",
            "url": "analytics.html",
            "description": "查看数据分析"
        },
        {
            "name": "设置",
            "icon": "fa-cog",
            "url": "settings.html",
            "description": "管理账户和偏好设置"
        }
    ]

    @classmethod
    def get_stats(cls, days: int = 7) -> Dict[str, Any]:
        """
        获取仪表板统计数据，包含周期对比。

        Args:
            days: 统计天数，默认7天

        Returns:
            包含 views, users, skills, conversion, revenue 及变化率的字典
        """
        current_period_start = datetime.now() - timedelta(days=days)
        previous_period_start = current_period_start - timedelta(days=days)

        with get_db_cursor() as cur:
            # 当前期间统计：去重用户数和总操作数
            cur.execute("""
                SELECT
                    COUNT(DISTINCT user_id) as total_users,
                    COUNT(*) as total_views
                FROM user_activity_logs
                WHERE created_at >= %s
            """, (current_period_start,))
            current_stats = cur.fetchone()

            # 上一期间统计
            cur.execute("""
                SELECT
                    COUNT(DISTINCT user_id) as total_users,
                    COUNT(*) as total_views
                FROM user_activity_logs
                WHERE created_at >= %s AND created_at < %s
            """, (previous_period_start, current_period_start))
            previous_stats = cur.fetchone()

            # 总 Skills 数（排除种子数据）
            cur.execute("""
                SELECT COUNT(*) as count
                FROM skills
                WHERE is_deleted = FALSE
                  AND skill_id NOT LIKE 'seed_%%'
            """)
            total_skills = cur.fetchone()['count']

        # 计算变化率
        views_change = 0.0
        users_change = 0.0

        prev_views = previous_stats['total_views'] or 0
        prev_users = previous_stats['total_users'] or 0
        curr_views = current_stats['total_views'] or 0
        curr_users = current_stats['total_users'] or 0

        if prev_views > 0:
            views_change = ((curr_views - prev_views) / prev_views) * 100

        if prev_users > 0:
            users_change = ((curr_users - prev_users) / prev_users) * 100

        return {
            "totalViews": float(curr_views),
            "totalUsers": float(curr_users),
            "totalSkills": float(total_skills),
            "conversionRate": cls.MOCK_CONVERSION_RATE,
            "revenue": cls.MOCK_REVENUE,
            "viewsChange": round(views_change, 1),
            "usersChange": round(users_change, 1),
            "conversionChange": cls.MOCK_CONVERSION_CHANGE,
            "revenueChange": cls.MOCK_REVENUE_CHANGE,
        }

    @classmethod
    def get_recent_activity(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近活动列表。

        Args:
            limit: 返回数量，默认10

        Returns:
            格式化后的活动列表
        """
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    al.id,
                    al.action,
                    al.entity,
                    al.entity_id,
                    al.details,
                    al.created_at,
                    u.username,
                    u.avatar_url
                FROM user_activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.created_at DESC
                LIMIT %s
            """, (limit,))
            activities = cur.fetchall()

        formatted = []
        for activity in activities:
            icon = cls.ACTION_ICON_MAP.get(activity['action'], 'fa-circle')
            username = activity.get('username')
            description = f"{username or '未知用户'} 执行了 {activity['action']} 操作"

            formatted.append({
                "id": activity['id'],
                "action": activity['action'],
                "username": username,
                "description": description,
                "timestamp": activity['created_at'],
                "icon": icon,
            })

        return formatted

    @classmethod
    def get_quick_actions(cls) -> List[Dict[str, Any]]:
        """
        获取快速操作列表。

        Returns:
            静态的快速操作列表
        """
        return cls.QUICK_ACTIONS

    @classmethod
    def get_user_activity(cls, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        获取指定用户的活动统计。

        Args:
            user_id: 用户ID
            days: 统计天数，默认30

        Returns:
            包含总操作数、活跃天数、登录数、创建技能数和每日趋势的字典
        """
        start_date = datetime.now() - timedelta(days=days)

        with get_db_cursor() as cur:
            # 用户活动汇总统计
            cur.execute("""
                SELECT
                    COUNT(*) as total_actions,
                    COUNT(DISTINCT DATE(created_at)) as active_days,
                    COUNT(CASE WHEN action = 'LOGIN' THEN 1 END) as logins,
                    COUNT(CASE WHEN action = 'CREATE_SKILL' THEN 1 END) as skills_created
                FROM user_activity_logs
                WHERE user_id = %s
                  AND created_at >= %s
            """, (user_id, start_date))
            stats = cur.fetchone()

            # 每日活动趋势（最近7天）
            cur.execute("""
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as actions
                FROM user_activity_logs
                WHERE user_id = %s
                  AND created_at >= %s
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            """, (user_id, datetime.now() - timedelta(days=7)))

            daily_trend = []
            for row in cur.fetchall():
                daily_trend.append({
                    "date": row['date'].isoformat() if row['date'] else None,
                    "actions": row['actions'],
                })

        return {
            "totalActions": stats['total_actions'] or 0,
            "activeDays": stats['active_days'] or 0,
            "logins": stats['logins'] or 0,
            "skillsCreated": stats['skills_created'] or 0,
            "dailyTrend": list(reversed(daily_trend)),
        }

    @classmethod
    def get_overview(cls) -> Dict[str, Any]:
        """
        获取仪表板概览数据，合并 stats、recent-activity 和 quick-actions。

        Returns:
            包含 stats、recentActivity、quickActions 的聚合字典
        """
        stats = cls.get_stats()
        recent_activity = cls.get_recent_activity(limit=5)
        quick_actions = cls.get_quick_actions()

        return {
            "stats": stats,
            "recentActivity": recent_activity,
            "quickActions": quick_actions,
        }
