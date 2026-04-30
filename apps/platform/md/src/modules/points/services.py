"""
积分商城服务层
处理积分相关的业务逻辑

使用 src.core.db_adapter 统一数据库连接 (psycopg2 + RealDictCursor)。
所有 SQL 参数使用 %s 占位符。
"""

import os
import sys
from datetime import datetime, date
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.db_adapter import get_db_cursor, get_db

# 配置
def get_db_config() -> Dict[str, Any]:
    """获取数据库配置（从环境变量）"""
    from core.db_adapter import get_default_config
    return get_default_config()


class PointsService:
    """积分服务"""

    @staticmethod
    def get_balance(user_id: int) -> Dict[str, Any]:
        """
        获取用户积分余额

        Args:
            user_id: 用户ID

        Returns:
            PointsBalance字典
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                SELECT
                    u.id as user_id,
                    u.username,
                    u.ai_points as balance,
                    COALESCE(SUM(CASE WHEN p.amount > 0 THEN p.amount ELSE 0 END), 0) as total_earned,
                    COALESCE(SUM(CASE WHEN p.amount < 0 THEN ABS(p.amount) ELSE 0 END), 0) as total_spent
                FROM users u
                LEFT JOIN point_transactions p ON u.id = p.user_id
                WHERE u.id = %s
                GROUP BY u.id, u.username, u.ai_points
            """, (user_id,))

            row = cur.fetchone()
            if not row:
                return {
                    "user_id": user_id,
                    "username": None,
                    "balance": 0,
                    "total_earned": 0,
                    "total_spent": 0
                }
            return dict(row)

    @staticmethod
    def add_points(user_id: int, amount: int, transaction_type: str, description: str) -> Dict[str, Any]:
        """
        添加积分

        Args:
            user_id: 用户ID
            amount: 积分数量
            transaction_type: 交易类型
            description: 描述

        Returns:
            PointsRecord字典
        """
        with get_db_cursor(get_db_config()) as cur:
            # 获取当前余额
            cur.execute("SELECT ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
            user = cur.fetchone()
            if not user:
                raise ValueError("用户不存在")

            balance_before = user['ai_points']
            balance_after = balance_before + amount

            # 更新用户积分
            cur.execute("""
                UPDATE users SET ai_points = ai_points + %s WHERE id = %s
            """, (amount, user_id))

            # 记录交易
            cur.execute("""
                INSERT INTO point_transactions (
                    user_id, transaction_type, amount, balance_before, balance_after, description
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (user_id, transaction_type, amount, balance_before, balance_after, description))

            record = cur.fetchone()
            return dict(record)

    @staticmethod
    def deduct_points(user_id: int, amount: int, transaction_type: str, description: str) -> bool:
        """
        扣除积分

        Args:
            user_id: 用户ID
            amount: 积分数量
            transaction_type: 交易类型
            description: 描述

        Returns:
            是否成功
        """
        with get_db_cursor(get_db_config()) as cur:
            # 获取当前余额
            cur.execute("SELECT ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
            user = cur.fetchone()
            if not user:
                raise ValueError("用户不存在")

            if user['ai_points'] < amount:
                return False

            balance_before = user['ai_points']
            balance_after = balance_before - amount

            # 更新用户积分
            cur.execute("""
                UPDATE users SET ai_points = ai_points - %s WHERE id = %s
            """, (amount, user_id))

            # 记录交易（使用负数表示支出）
            cur.execute("""
                INSERT INTO point_transactions (
                    user_id, transaction_type, amount, balance_before, balance_after, description
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, transaction_type, -amount, balance_before, balance_after, description))

            return True

    @staticmethod
    def get_history(user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取积分历史记录

        Args:
            user_id: 用户ID
            page: 页码
            limit: 每页数量

        Returns:
            包含记录列表和分页信息的字典
        """
        with get_db_cursor(get_db_config()) as cur:
            offset = (page - 1) * limit

            # 获取记录
            cur.execute("""
                SELECT
                    id,
                    user_id,
                    transaction_type as type,
                    amount,
                    balance_after,
                    description,
                    created_at
                FROM point_transactions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))

            records = [dict(row) for row in cur.fetchall()]

            # 获取总数
            cur.execute("""
                SELECT COUNT(*) as total FROM point_transactions WHERE user_id = %s
            """, (user_id,))
            total = cur.fetchone()['total']

            return {
                "records": records,
                "total": total,
                "page": page,
                "limit": limit
            }

    @staticmethod
    def get_transactions(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        transaction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取用户积分交易记录（增强版，含交易来源和类型筛选）

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            transaction_type: 交易类型筛选

        Returns:
            包含交易记录列表和分页信息的字典
        """
        with get_db_cursor(get_db_config()) as cur:
            # 构建查询
            query = """
                SELECT
                    id, user_id, transaction_type, transaction_source,
                    amount, balance_before, balance_after, description, created_at
                FROM point_transactions
                WHERE user_id = %s
            """
            params: List[Any] = [user_id]

            if transaction_type:
                query += " AND transaction_type = %s"
                params.append(transaction_type)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cur.execute(query, params)
            rows = [dict(row) for row in cur.fetchall()]

            # 获取总数
            count_query = "SELECT COUNT(*) as total FROM point_transactions WHERE user_id = %s"
            count_params: List[Any] = [user_id]
            if transaction_type:
                count_query += " AND transaction_type = %s"
                count_params.append(transaction_type)

            cur.execute(count_query, count_params)
            total = cur.fetchone()['total']

            return {
                "items": rows,
                "total": total,
                "page": page,
                "page_size": page_size
            }

    @staticmethod
    def sign_in(user_id: int, sign_in_points: int = 10) -> Dict[str, Any]:
        """
        用户签到

        Args:
            user_id: 用户ID
            sign_in_points: 签到积分

        Returns:
            签到结果
        """
        with get_db_cursor(get_db_config()) as cur:
            # 检查今天是否已签到
            cur.execute("""
                SELECT id, sign_in_count FROM user_sign_ins
                WHERE user_id = %s AND sign_in_date = CURRENT_DATE
            """, (user_id,))

            if cur.fetchone():
                raise ValueError("今日已签到")

            # 获取用户信息
            cur.execute("SELECT ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
            user = cur.fetchone()
            if not user:
                raise ValueError("用户不存在")

            balance_before = user['ai_points']
            balance_after = balance_before + sign_in_points

            # 更新用户积分
            cur.execute("""
                UPDATE users SET ai_points = ai_points + %s WHERE id = %s
            """, (sign_in_points, user_id))

            # 记录交易
            cur.execute("""
                INSERT INTO point_transactions (
                    user_id, transaction_type, amount, balance_before, balance_after, description
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, "sign_in", sign_in_points, balance_before, balance_after, "每日签到"))

            # 更新签到记录
            cur.execute("""
                INSERT INTO user_sign_ins (user_id, sign_in_date, points_earned)
                VALUES (%s, CURRENT_DATE, %s)
                ON CONFLICT (user_id, sign_in_date)
                DO NOTHING
            """, (user_id, sign_in_points))

            # 获取连续签到天数
            cur.execute("""
                SELECT COUNT(*) as sign_in_count
                FROM user_sign_ins
                WHERE user_id = %s
                AND sign_in_date >= CURRENT_DATE - INTERVAL '7 days'
            """, (user_id,))
            sign_in_count = cur.fetchone()['sign_in_count']

            return {
                "success": True,
                "points_earned": sign_in_points,
                "current_balance": balance_after,
                "sign_in_count": sign_in_count,
                "message": f"签到成功，获得 {sign_in_points} 积分"
            }

    @staticmethod
    def get_user_points_stats(user_id: int) -> Dict[str, Any]:
        """
        获取用户积分统计信息

        优先从 user_points 表获取，回退到聚合计算。

        Args:
            user_id: 用户ID

        Returns:
            用户积分统计字典
        """
        with get_db_cursor(get_db_config()) as cur:
            # 尝试从 user_points 表获取
            cur.execute("""
                SELECT
                    user_id,
                    balance,
                    total_earned,
                    total_spent,
                    level,
                    experience
                FROM user_points
                WHERE user_id = %s
            """, (user_id,))

            row = cur.fetchone()

            if not row:
                # 回退：从 users 和 point_transactions 聚合
                cur.execute("""
                    SELECT
                        u.id as user_id,
                        u.ai_points as balance,
                        COALESCE(SUM(CASE WHEN pt.amount > 0 THEN pt.amount ELSE 0 END), 0) as total_earned,
                        COALESCE(SUM(CASE WHEN pt.amount < 0 THEN ABS(pt.amount) ELSE 0 END), 0) as total_spent,
                        COALESCE(COUNT(er.id), 0) as total_exchanges,
                        COALESCE(SUM(er.points_used), 0) as total_points_used
                    FROM users u
                    LEFT JOIN point_transactions pt ON u.id = pt.user_id
                    LEFT JOIN exchange_records er ON u.id = er.user_id AND er.status = 'completed'
                    WHERE u.id = %s
                    GROUP BY u.id, u.ai_points
                """, (user_id,))

                row = cur.fetchone()
                if not row:
                    return {
                        "user_id": user_id,
                        "balance": 0,
                        "total_earned": 0,
                        "total_spent": 0,
                        "level": 1,
                        "experience": 0,
                        "total_exchanges": 0,
                        "total_points_used": 0
                    }
                result = dict(row)
                result.setdefault("level", 1)
                result.setdefault("experience", 0)
                result.setdefault("total_exchanges", 0)
                result.setdefault("total_points_used", 0)
                return result

            result = dict(row)
            # 补充兑换统计
            cur.execute("""
                SELECT
                    COALESCE(COUNT(*), 0) as total_exchanges,
                    COALESCE(SUM(points_used), 0) as total_points_used
                FROM exchange_records
                WHERE user_id = %s AND status = 'completed'
            """, (user_id,))
            exchange_stats = cur.fetchone()
            if exchange_stats:
                result['total_exchanges'] = exchange_stats.get('total_exchanges', 0) or 0
                result['total_points_used'] = exchange_stats.get('total_points_used', 0) or 0
            else:
                result.setdefault("total_exchanges", 0)
                result.setdefault("total_points_used", 0)
            return result


class MallService:
    """商城服务"""

    @staticmethod
    def create_item(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建商城商品

        Args:
            data: 商品数据

        Returns:
            创建的商品
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                INSERT INTO mall_items (
                    name, description, points_cost, stock, image_url,
                    category, is_featured, sort_order, valid_days
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                data.get('name'),
                data.get('description'),
                data.get('points_cost'),
                data.get('stock', -1),
                data.get('image_url'),
                data.get('category'),
                data.get('is_featured', False),
                data.get('sort_order', 0),
                data.get('valid_days')
            ))

            return dict(cur.fetchone())

    @staticmethod
    def list_items(
        category: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_active: bool = True,
        page: int = 1,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取商城商品列表

        Args:
            category: 分类筛选
            is_featured: 是否精选
            is_active: 是否上架
            page: 页码
            limit: 每页数量

        Returns:
            商品列表
        """
        with get_db_cursor(get_db_config()) as cur:
            query = """
                SELECT
                    *,
                    CASE
                        WHEN stock = -1 THEN TRUE
                        WHEN stock > 0 THEN TRUE
                        ELSE FALSE
                    END as stock_available
                FROM mall_items
                WHERE 1=1
            """
            params: List[Any] = []

            if category:
                query += " AND category = %s"
                params.append(category)

            if is_featured is not None:
                query += " AND is_featured = %s"
                params.append(is_featured)

            if is_active:
                query += " AND is_active = TRUE"

            query += " ORDER BY sort_order ASC, created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, (page - 1) * limit])

            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def get_item(item_id: int) -> Optional[Dict[str, Any]]:
        """
        获取商品详情

        Args:
            item_id: 商品ID

        Returns:
            商品信息
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                SELECT
                    *,
                    CASE
                        WHEN stock = -1 THEN TRUE
                        WHEN stock > 0 THEN TRUE
                        ELSE FALSE
                    END as stock_available
                FROM mall_items
                WHERE id = %s
            """, (item_id,))

            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_item(item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新商城商品

        Args:
            item_id: 商品ID
            data: 要更新的字段字典

        Returns:
            更新后的商品信息
        """
        with get_db_cursor(get_db_config()) as cur:
            # 检查商品是否存在
            cur.execute("SELECT id FROM mall_items WHERE id = %s", (item_id,))
            if not cur.fetchone():
                raise ValueError("商品不存在")

            # 构建更新字段
            update_fields = []
            params: List[Any] = []

            for field, value in data.items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)

            if not update_fields:
                raise ValueError("没有要更新的字段")

            params.append(item_id)
            query = f"UPDATE mall_items SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *"

            cur.execute(query, params)
            return dict(cur.fetchone())

    @staticmethod
    def delete_item(item_id: int) -> bool:
        """
        删除商城商品

        Args:
            item_id: 商品ID

        Returns:
            是否删除成功
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("DELETE FROM mall_items WHERE id = %s", (item_id,))
            if cur.rowcount == 0:
                return False
            return True

    @staticmethod
    def exchange_item(user_id: int, item_id: int, quantity: int = 1) -> Dict[str, Any]:
        """
        兑换商品

        Args:
            user_id: 用户ID
            item_id: 商品ID
            quantity: 数量

        Returns:
            兑换结果
        """
        with get_db_cursor(get_db_config()) as cur:
            # 检查用户积分
            cur.execute("SELECT id, username, ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
            user = cur.fetchone()
            if not user:
                raise ValueError("用户不存在")

            # 检查商品
            cur.execute("""
                SELECT id, name, points_cost, stock, is_active
                FROM mall_items
                WHERE id = %s FOR UPDATE
            """, (item_id,))

            item = cur.fetchone()
            if not item:
                raise ValueError("商品不存在")

            if not item['is_active']:
                raise ValueError("商品已下架")

            if item['stock'] != -1 and item['stock'] < quantity:
                raise ValueError("库存不足")

            total_points = item['points_cost'] * quantity

            if user['ai_points'] < total_points:
                raise ValueError(f"积分不足，需要 {total_points} 积分")

            # 扣除积分
            cur.execute("""
                UPDATE users SET ai_points = ai_points - %s WHERE id = %s
            """, (total_points, user_id))

            # 更新库存
            if item['stock'] != -1:
                cur.execute("""
                    UPDATE mall_items
                    SET stock = stock - %s, sold_count = sold_count + %s
                    WHERE id = %s
                """, (quantity, quantity, item_id))
            else:
                cur.execute("""
                    UPDATE mall_items SET sold_count = sold_count + %s WHERE id = %s
                """, (quantity, item_id))

            # 生成兑换号
            exchange_no = f"EX{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"

            # 记录交易
            balance_before = user['ai_points']
            balance_after = balance_before - total_points
            cur.execute("""
                INSERT INTO point_transactions (
                    user_id, transaction_type, amount, balance_before, balance_after, description
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, "exchange", -total_points, balance_before, balance_after, f"兑换商品: {item['name']}"))

            # 创建兑换记录
            cur.execute("""
                INSERT INTO exchange_records (
                    exchange_no, user_id, item_id, item_name, points_used, quantity, status
                ) VALUES (%s, %s, %s, %s, %s, %s, 'completed')
            """, (exchange_no, user_id, item_id, item['name'], total_points, quantity))

            return {
                "success": True,
                "exchange_no": exchange_no,
                "points_used": total_points,
                "remaining_balance": balance_after,
                "message": "兑换成功"
            }

    @staticmethod
    def get_my_exchanges(user_id: int, status: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取用户的兑换记录

        Args:
            user_id: 用户ID
            status: 状态筛选
            page: 页码
            limit: 每页数量

        Returns:
            兑换记录列表
        """
        with get_db_cursor(get_db_config()) as cur:
            query = """
                SELECT * FROM exchange_records WHERE user_id = %s
            """
            params: List[Any] = [user_id]

            if status:
                query += " AND status = %s"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, (page - 1) * limit])

            cur.execute(query, params)
            records = [dict(row) for row in cur.fetchall()]

            # 获取总数
            count_query = "SELECT COUNT(*) as total FROM exchange_records WHERE user_id = %s"
            count_params: List[Any] = [user_id]
            if status:
                count_query += " AND status = %s"
                count_params.append(status)

            cur.execute(count_query, count_params)
            total = cur.fetchone()['total']

            return {
                "records": records,
                "total": total,
                "page": page,
                "limit": limit
            }

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        获取商城统计

        Returns:
            统计数据
        """
        with get_db_cursor(get_db_config()) as cur:
            # 总商品数
            cur.execute("SELECT COUNT(*) as count FROM mall_items")
            total_items = cur.fetchone()['count']

            # 活跃商品数
            cur.execute("SELECT COUNT(*) as count FROM mall_items WHERE is_active = TRUE")
            active_items = cur.fetchone()['count']

            # 总兑换数
            cur.execute("SELECT COUNT(*) as count FROM exchange_records WHERE status = 'completed'")
            total_exchanges = cur.fetchone()['count']

            # 总积分消耗
            cur.execute("SELECT COALESCE(SUM(points_used), 0) as total FROM exchange_records WHERE status = 'completed'")
            total_points_spent = cur.fetchone()['total'] or 0

            # 今日兑换数
            cur.execute("""
                SELECT COUNT(*) as count FROM exchange_records
                WHERE status = 'completed' AND DATE(created_at) = CURRENT_DATE
            """)
            today_exchanges = cur.fetchone()['count']

            return {
                "total_items": total_items,
                "active_items": active_items,
                "total_exchanges": total_exchanges,
                "total_points_spent": total_points_spent,
                "today_exchanges": today_exchanges
            }

    @staticmethod
    def list_all_exchanges(
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取所有兑换记录（管理员）

        Args:
            status: 状态筛选
            user_id: 用户ID筛选
            page: 页码
            limit: 每页数量

        Returns:
            兑换记录列表和分页信息
        """
        with get_db_cursor(get_db_config()) as cur:
            query = """
                SELECT er.*, u.username
                FROM exchange_records er
                LEFT JOIN users u ON er.user_id = u.id
                WHERE 1=1
            """
            params: List[Any] = []

            if status:
                query += " AND er.status = %s"
                params.append(status)
            if user_id:
                query += " AND er.user_id = %s"
                params.append(user_id)

            # Count
            count_query = query.replace(
                "SELECT er.*, u.username",
                "SELECT COUNT(*) as total"
            )
            count_query_simple = count_query.rsplit("ORDER BY", 1)[0].rstrip()
            cur.execute(count_query_simple.replace("WHERE 1=1", "WHERE 1=1") if "WHERE 1=1" in count_query_simple else count_query_simple, params)
            total = cur.fetchone()['total']

            query += " ORDER BY er.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, (page - 1) * limit])

            cur.execute(query, params)
            records = [dict(row) for row in cur.fetchall()]

            return {
                "records": records,
                "total": total,
                "page": page,
                "limit": limit
            }

    @staticmethod
    def update_exchange_status(exchange_id: int, status: str) -> Dict[str, Any]:
        """
        更新兑换记录状态

        Args:
            exchange_id: 兑换记录ID
            status: 新状态

        Returns:
            更新后的兑换记录
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                UPDATE exchange_records SET status = %s WHERE id = %s
                RETURNING *
            """, (status, exchange_id))

            row = cur.fetchone()
            if not row:
                raise ValueError("兑换记录不存在")
            return dict(row)


# ==================== 分类服务 ====================

class CategoryService:
    """商品分类服务"""

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """
        获取所有活跃分类

        Returns:
            分类列表
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                SELECT id, category_key, name_en, name_zh, description, icon, sort_order, is_active
                FROM points_categories
                WHERE is_active = TRUE
                ORDER BY sort_order ASC
            """)
            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def get_all_categories(include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        获取所有分类（管理员，含非活跃）

        Args:
            include_inactive: 是否包含非活跃分类

        Returns:
            分类列表
        """
        with get_db_cursor(get_db_config()) as cur:
            if include_inactive:
                cur.execute("""
                    SELECT id, category_key, name_en, name_zh, description, icon, sort_order, is_active
                    FROM points_categories
                    ORDER BY sort_order ASC
                """)
            else:
                cur.execute("""
                    SELECT id, category_key, name_en, name_zh, description, icon, sort_order, is_active
                    FROM points_categories
                    WHERE is_active = TRUE
                    ORDER BY sort_order ASC
                """)
            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def create_category(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建分类

        Args:
            data: 分类数据

        Returns:
            创建的分类
        """
        with get_db_cursor(get_db_config()) as cur:
            # 检查 category_key 是否已存在
            cur.execute("SELECT id FROM points_categories WHERE category_key = %s", (data['category_key'],))
            if cur.fetchone():
                raise ValueError(f"分类标识 '{data['category_key']}' 已存在")

            cur.execute("""
                INSERT INTO points_categories (category_key, name_en, name_zh, description, icon, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                data['category_key'],
                data['name_en'],
                data['name_zh'],
                data.get('description'),
                data.get('icon'),
                data.get('sort_order', 0)
            ))
            return dict(cur.fetchone())

    @staticmethod
    def update_category(category_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新分类

        Args:
            category_id: 分类ID
            data: 要更新的字段

        Returns:
            更新后的分类
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("SELECT id FROM points_categories WHERE id = %s", (category_id,))
            if not cur.fetchone():
                raise ValueError("分类不存在")

            # 构建更新字段
            update_fields = []
            params: List[Any] = []

            for field, value in data.items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)

            if not update_fields:
                raise ValueError("没有要更新的字段")

            params.append(category_id)
            query = f"UPDATE points_categories SET {', '.join(update_fields)} WHERE id = %s RETURNING *"

            cur.execute(query, params)
            return dict(cur.fetchone())

    @staticmethod
    def delete_category(category_id: int) -> bool:
        """
        删除分类

        Args:
            category_id: 分类ID

        Returns:
            是否删除成功
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("DELETE FROM points_categories WHERE id = %s", (category_id,))
            return cur.rowcount > 0

    @staticmethod
    def get_mall_item_categories() -> List[Dict[str, Any]]:
        """
        从 mall_items 表中获取去重后的分类（简单的分类提取）

        Returns:
            分类列表（category名 + 数量）
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                SELECT DISTINCT category, COUNT(*) as count
                FROM mall_items
                WHERE is_active = TRUE AND category IS NOT NULL AND category != ''
                GROUP BY category
                ORDER BY category
            """)
            return [dict(row) for row in cur.fetchall()]


# ==================== 购物车服务 ====================

class CartService:
    """积分商城购物车服务"""

    @staticmethod
    def get_cart(user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户购物车

        Args:
            user_id: 用户ID

        Returns:
            购物车项列表
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                SELECT
                    c.id, c.user_id, c.product_id, c.quantity,
                    m.name as product_name, m.image_url as product_image,
                    m.points_cost as points_required,
                    m.points_cost * c.quantity as total_points,
                    CASE
                        WHEN m.stock = -1 THEN TRUE
                        WHEN m.stock >= c.quantity THEN TRUE
                        ELSE FALSE
                    END as stock_available
                FROM points_shopping_cart c
                JOIN mall_items m ON c.product_id = m.id
                WHERE c.user_id = %s AND m.is_active = TRUE
                ORDER BY c.created_at DESC
            """, (user_id,))

            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """
        添加到购物车

        Args:
            user_id: 用户ID
            product_id: 商品ID
            quantity: 数量

        Returns:
            操作结果
        """
        with get_db_cursor(get_db_config()) as cur:
            # 检查商品是否存在且可用
            cur.execute("""
                SELECT id, name, is_active, stock
                FROM mall_items WHERE id = %s
            """, (product_id,))

            product = cur.fetchone()
            if not product:
                raise ValueError("商品不存在")
            if not product['is_active']:
                raise ValueError("商品已下架")
            if product['stock'] != -1 and product['stock'] < quantity:
                raise ValueError("库存不足")

            # 添加或更新购物车
            cur.execute("""
                INSERT INTO points_shopping_cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, product_id)
                DO UPDATE SET quantity = points_shopping_cart.quantity + %s,
                              updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (user_id, product_id, quantity, quantity))

            return {
                "message": "已添加到购物车",
                "cart_id": cur.fetchone()['id']
            }

    @staticmethod
    def update_cart_item(cart_id: int, quantity: int) -> bool:
        """
        更新购物车项数量

        Args:
            cart_id: 购物车项ID
            quantity: 新数量

        Returns:
            是否更新成功
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("""
                UPDATE points_shopping_cart
                SET quantity = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (quantity, cart_id))

            return cur.rowcount > 0

    @staticmethod
    def remove_from_cart(cart_id: int) -> bool:
        """
        从购物车移除

        Args:
            cart_id: 购物车项ID

        Returns:
            是否移除成功
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("DELETE FROM points_shopping_cart WHERE id = %s", (cart_id,))
            return cur.rowcount > 0

    @staticmethod
    def clear_cart(user_id: int) -> int:
        """
        清空用户购物车

        Args:
            user_id: 用户ID

        Returns:
            移除的项数
        """
        with get_db_cursor(get_db_config()) as cur:
            cur.execute("DELETE FROM points_shopping_cart WHERE user_id = %s", (user_id,))
            return cur.rowcount

    @staticmethod
    def checkout_cart(user_id: int) -> Dict[str, Any]:
        """
        从购物车一键结算（批量兑换购物车中所有商品）

        Args:
            user_id: 用户ID

        Returns:
            兑换结果列表
        """
        with get_db_cursor(get_db_config()) as cur:
            # 获取购物车内容
            cur.execute("""
                SELECT c.*, m.name, m.points_cost, m.stock, m.is_active
                FROM points_shopping_cart c
                JOIN mall_items m ON c.product_id = m.id
                WHERE c.user_id = %s AND m.is_active = TRUE
            """, (user_id,))

            cart_items = cur.fetchall()
            if not cart_items:
                raise ValueError("购物车为空")

            # 获取用户积分
            cur.execute("SELECT id, ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
            user = cur.fetchone()
            if not user:
                raise ValueError("用户不存在")

            # 计算总积分
            total_points = 0
            for item in cart_items:
                # 库存检查
                if item['stock'] != -1 and item['stock'] < item['quantity']:
                    raise ValueError(f"商品 '{item['name']}' 库存不足")
                total_points += item['points_cost'] * item['quantity']

            if user['ai_points'] < total_points:
                raise ValueError(f"积分不足，需要 {total_points} 积分")

            results = []
            for item in cart_items:
                item_total = item['points_cost'] * item['quantity']

                # 扣除积分
                cur.execute("""
                    UPDATE users SET ai_points = ai_points - %s WHERE id = %s
                """, (item_total, user_id))

                # 更新库存
                if item['stock'] != -1:
                    cur.execute("""
                        UPDATE mall_items
                        SET stock = stock - %s, sold_count = sold_count + %s
                        WHERE id = %s
                    """, (item['quantity'], item['quantity'], item['product_id']))
                else:
                    cur.execute("""
                        UPDATE mall_items SET sold_count = sold_count + %s WHERE id = %s
                    """, (item['quantity'], item['product_id']))

                # 生成兑换号
                exchange_no = f"EX{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}{item['product_id']}"

                # 记录交易
                cur.execute("""
                    INSERT INTO point_transactions (
                        user_id, transaction_type, amount, balance_before, balance_after, description
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, "exchange", -item_total, user['ai_points'],
                      user['ai_points'] - item_total, f"兑换商品: {item['name']}"))

                # 创建兑换记录
                cur.execute("""
                    INSERT INTO exchange_records (
                        exchange_no, user_id, item_id, item_name, points_used, quantity, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'completed')
                """, (exchange_no, user_id, item['product_id'], item['name'], item_total, item['quantity']))

                results.append({
                    "exchange_no": exchange_no,
                    "item_name": item['name'],
                    "points_used": item_total,
                    "quantity": item['quantity']
                })

            # 清空购物车
            cur.execute("DELETE FROM points_shopping_cart WHERE user_id = %s", (user_id,))

            return {
                "success": True,
                "total_points_used": total_points,
                "items_count": len(results),
                "exchanges": results,
                "message": f"成功兑换 {len(results)} 件商品，共使用 {total_points} 积分"
            }
