"""
分销系统服务层
处理分销相关的业务逻辑
"""

import os
import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Connection pool for database connections
_db_pool = None


def _get_db_pool():
    """Get or create the database connection pool."""
    global _db_pool
    if _db_pool is None:
        config = _get_db_config()
        _db_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **config
        )
    return _db_pool


@contextmanager
def get_db():
    """
    Get a database connection using a connection pool.

    Yields:
        Database connection
    """
    db_pool = _get_db_pool()
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


def _get_db_config() -> Dict[str, Any]:
    """获取数据库配置"""
    from core.db_adapter import get_default_config
    return get_default_config()


# ==================== 数据库初始化 ====================

def init_tables():
    """初始化分销相关数据库表"""
    with get_db() as conn:
        with conn.cursor() as cur:
            # 分销员工表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS affiliate_staffs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE,
                    staff_code VARCHAR(50) UNIQUE NOT NULL,
                    staff_name VARCHAR(100) NOT NULL,
                    total_sales DECIMAL(15, 2) DEFAULT 0,
                    total_orders INTEGER DEFAULT 0,
                    total_commission DECIMAL(15, 2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 分享链接表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS affiliate_links (
                    id SERIAL PRIMARY KEY,
                    staff_id INTEGER NOT NULL,
                    product_id INTEGER,
                    link_code VARCHAR(50) UNIQUE NOT NULL,
                    short_url VARCHAR(255),
                    click_count INTEGER DEFAULT 0,
                    order_count INTEGER DEFAULT 0,
                    conversion_rate DECIMAL(5, 4) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES affiliate_staffs(id) ON DELETE CASCADE
                )
            """)

            # 分销订单表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS affiliate_orders (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    staff_id INTEGER NOT NULL,
                    link_id INTEGER,
                    product_id INTEGER,
                    amount DECIMAL(15, 2) NOT NULL,
                    commission DECIMAL(15, 2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES affiliate_staffs(id) ON DELETE CASCADE,
                    FOREIGN KEY (link_id) REFERENCES affiliate_links(id) ON DELETE SET NULL
                )
            """)

            # 佣金记录表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS affiliate_commissions (
                    id SERIAL PRIMARY KEY,
                    staff_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES affiliate_staffs(id) ON DELETE CASCADE
                )
            """)

            # 访问记录表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS affiliate_visits (
                    id SERIAL PRIMARY KEY,
                    link_id INTEGER NOT NULL,
                    visitor_id VARCHAR(100),
                    source VARCHAR(255),
                    referrer TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (link_id) REFERENCES affiliate_links(id) ON DELETE CASCADE
                )
            """)

            # 创建索引
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_staffs_user_id ON affiliate_staffs(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_staffs_staff_code ON affiliate_staffs(staff_code)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_links_staff_id ON affiliate_links(staff_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_links_link_code ON affiliate_links(link_code)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_orders_staff_id ON affiliate_orders(staff_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_orders_status ON affiliate_orders(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_commissions_staff_id ON affiliate_commissions(staff_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_visits_link_id ON affiliate_visits(link_id)")

            conn.commit()


# ==================== 员工管理服务 ====================

class StaffService:
    """分销员工服务"""

    @staticmethod
    def generate_staff_code() -> str:
        """生成唯一的员工码"""
        while True:
            # 生成8位随机码
            prefix = "AFF"
            chars = string.ascii_uppercase + string.digits
            code = prefix + ''.join(random.choices(chars, k=8))

            # 检查是否已存在
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM affiliate_staffs WHERE staff_code = %s", (code,))
                    if not cur.fetchone():
                        return code

    @staticmethod
    def create_staff(user_id: int, staff_name: str, staff_code: Optional[str] = None) -> Dict[str, Any]:
        """创建分销员工"""
        if staff_code is None:
            staff_code = StaffService.generate_staff_code()

        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 检查用户是否已经是员工
                cur.execute("SELECT id FROM affiliate_staffs WHERE user_id = %s", (user_id,))
                if cur.fetchone():
                    raise ValueError("该用户已经是分销员工")

                # 检查员工码是否已存在
                cur.execute("SELECT id FROM affiliate_staffs WHERE staff_code = %s", (staff_code,))
                if cur.fetchone():
                    staff_code = StaffService.generate_staff_code()

                cur.execute("""
                    INSERT INTO affiliate_staffs (user_id, staff_code, staff_name)
                    VALUES (%s, %s, %s)
                    RETURNING *
                """, (user_id, staff_code, staff_name))

                conn.commit()
                return dict(cur.fetchone())

    @staticmethod
    def get_staff(staff_id: int) -> Optional[Dict[str, Any]]:
        """获取员工信息"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM affiliate_staffs WHERE id = %s", (staff_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    @staticmethod
    def get_staff_by_code(staff_code: str) -> Optional[Dict[str, Any]]:
        """通过员工码获取员工信息"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM affiliate_staffs WHERE staff_code = %s", (staff_code,))
                row = cur.fetchone()
                return dict(row) if row else None

    @staticmethod
    def get_staff_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
        """通过用户ID获取员工信息"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM affiliate_staffs WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    @staticmethod
    def list_staffs(status: Optional[str] = None, page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """获取员工列表"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM affiliate_staffs WHERE 1=1"
                params = []

                if status:
                    query += " AND status = %s"
                    params.append(status)

                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, (page - 1) * limit])

                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def update_staff(staff_id: int, staff_name: Optional[str] = None, status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """更新员工信息"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                updates = []
                params = []

                if staff_name:
                    updates.append("staff_name = %s")
                    params.append(staff_name)

                if status:
                    updates.append("status = %s")
                    params.append(status)

                if not updates:
                    return StaffService.get_staff(staff_id)

                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(staff_id)

                cur.execute(f"""
                    UPDATE affiliate_staffs
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING *
                """, params)

                conn.commit()
                row = cur.fetchone()
                return dict(row) if row else None

    @staticmethod
    def get_staff_stats(staff_id: int, period: str = "all") -> Dict[str, Any]:
        """获取员工统计数据"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 获取员工基本信息
                cur.execute("SELECT * FROM affiliate_staffs WHERE id = %s", (staff_id,))
                staff = cur.fetchone()
                if not staff:
                    raise ValueError("员工不存在")

                # 计算时间范围
                today = datetime.now().date()
                if period == "today":
                    start_date = today
                elif period == "week":
                    start_date = today - timedelta(days=7)
                elif period == "month":
                    start_date = today.replace(day=1)
                else:
                    start_date = None

                # 获取待确认佣金
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as pending
                    FROM affiliate_commissions
                    WHERE staff_id = %s AND status = 'pending'
                """, (staff_id,))
                pending_commission = cur.fetchone()['pending']

                # 获取已支付佣金
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as paid
                    FROM affiliate_commissions
                    WHERE staff_id = %s AND status = 'paid'
                """, (staff_id,))
                paid_commission = cur.fetchone()['paid']

                # 获取链接点击数
                cur.execute("""
                    SELECT COALESCE(SUM(click_count), 0) as clicks
                    FROM affiliate_links
                    WHERE staff_id = %s
                """, (staff_id,))
                click_count = cur.fetchone()['clicks']

                # 获取转化率
                total_orders = staff['total_orders']
                conversion_rate = (total_orders / click_count * 100) if click_count > 0 else 0

                # 获取今日数据
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as today_sales, COUNT(*) as today_orders
                    FROM affiliate_orders
                    WHERE staff_id = %s AND DATE(created_at) = CURRENT_DATE
                """, (staff_id,))
                today_data = cur.fetchone()

                # 获取本周数据
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as week_sales
                    FROM affiliate_orders
                    WHERE staff_id = %s AND created_at >= CURRENT_DATE - INTERVAL '7 days'
                """, (staff_id,))
                week_data = cur.fetchone()

                # 获取本月数据
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as month_sales
                    FROM affiliate_orders
                    WHERE staff_id = %s AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
                """, (staff_id,))
                month_data = cur.fetchone()

                return {
                    "staff_id": staff['id'],
                    "staff_code": staff['staff_code'],
                    "staff_name": staff['staff_name'],
                    "total_sales": float(staff['total_sales']),
                    "total_orders": staff['total_orders'],
                    "total_commission": float(staff['total_commission']),
                    "pending_commission": float(pending_commission),
                    "paid_commission": float(paid_commission),
                    "click_count": click_count,
                    "conversion_rate": round(conversion_rate, 2),
                    "today_sales": float(today_data['today_sales']),
                    "today_orders": today_data['today_orders'],
                    "this_week_sales": float(week_data['week_sales']),
                    "this_month_sales": float(month_data['month_sales'])
                }


# ==================== 分享链接服务 ====================

class LinkService:
    """分享链接服务"""

    @staticmethod
    def generate_link_code() -> str:
        """生成唯一的链接码"""
        while True:
            # 生成12位随机码
            chars = string.ascii_lowercase + string.digits
            code = ''.join(random.choices(chars, k=12))

            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM affiliate_links WHERE link_code = %s", (code,))
                    if not cur.fetchone():
                        return code

    @staticmethod
    def create_affiliate_link(staff_id: int, product_id: Optional[int] = None, expires_in_days: Optional[int] = None) -> Dict[str, Any]:
        """创建分享链接"""
        link_code = LinkService.generate_link_code()

        # 计算过期时间
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        else:
            # 默认365天
            expires_at = datetime.now() + timedelta(days=365)

        # 生成短链接
        short_url = f"/r/{link_code}"

        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO affiliate_links (staff_id, product_id, link_code, short_url, expires_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (staff_id, product_id, link_code, short_url, expires_at))

                conn.commit()
                link = dict(cur.fetchone())

                # 生成完整URL
                if product_id:
                    link['full_url'] = f"/openclaw/product/{product_id}?ref={link['link_code']}"
                else:
                    link['full_url'] = f"/openclaw?ref={link['link_code']}"

                # 获取员工码
                cur.execute("SELECT staff_code FROM affiliate_staffs WHERE id = %s", (staff_id,))
                staff = cur.fetchone()
                if staff:
                    link['staff_code'] = staff['staff_code']

                return link

    @staticmethod
    def get_link_by_code(link_code: str) -> Optional[Dict[str, Any]]:
        """通过链接码获取链接信息"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT l.*, s.staff_code, s.staff_name
                    FROM affiliate_links l
                    LEFT JOIN affiliate_staffs s ON l.staff_id = s.id
                    WHERE l.link_code = %s
                """, (link_code,))
                row = cur.fetchone()
                return dict(row) if row else None

    @staticmethod
    def list_links(staff_id: Optional[int] = None, status: Optional[str] = None, page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """获取链接列表"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT l.*, s.staff_code
                    FROM affiliate_links l
                    LEFT JOIN affiliate_staffs s ON l.staff_id = s.id
                    WHERE 1=1
                """
                params = []

                if staff_id:
                    query += " AND l.staff_id = %s"
                    params.append(staff_id)

                if status:
                    query += " AND l.status = %s"
                    params.append(status)

                query += " ORDER BY l.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, (page - 1) * limit])

                cur.execute(query, params)
                links = []
                for row in cur.fetchall():
                    link = dict(row)
                    # 生成完整URL
                    if link['product_id']:
                        link['full_url'] = f"/openclaw/product/{link['product_id']}?ref={link['link_code']}"
                    else:
                        link['full_url'] = f"/openclaw?ref={link['link_code']}"
                    links.append(link)
                return links

    @staticmethod
    def get_link_stats(link_code: str) -> Dict[str, Any]:
        """获取链接统计数据"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM affiliate_links WHERE link_code = %s", (link_code,))
                link = cur.fetchone()
                if not link:
                    raise ValueError("链接不存在")

                # 获取今日点击
                cur.execute("""
                    SELECT COUNT(*) as today_clicks
                    FROM affiliate_visits
                    WHERE link_id = %s AND DATE(created_at) = CURRENT_DATE
                """, (link['id'],))
                today_clicks = cur.fetchone()['today_clicks']

                # 获取本周点击
                cur.execute("""
                    SELECT COUNT(*) as week_clicks
                    FROM affiliate_visits
                    WHERE link_id = %s AND created_at >= CURRENT_DATE - INTERVAL '7 days'
                """, (link['id'],))
                week_clicks = cur.fetchone()['week_clicks']

                # 获取本月点击
                cur.execute("""
                    SELECT COUNT(*) as month_clicks
                    FROM affiliate_visits
                    WHERE link_id = %s AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
                """, (link['id'],))
                month_clicks = cur.fetchone()['month_clicks']

                # 获取订单和佣金统计
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as sales, COALESCE(SUM(commission), 0) as commissions
                    FROM affiliate_orders
                    WHERE link_id = %s AND status = 'confirmed'
                """, (link['id'],))
                order_stats = cur.fetchone()

                return {
                    "link_id": link['id'],
                    "link_code": link['link_code'],
                    "click_count": link['click_count'],
                    "order_count": link['order_count'],
                    "conversion_rate": float(link['conversion_rate']) * 100,
                    "sales_amount": float(order_stats['sales']),
                    "commission_amount": float(order_stats['commissions']),
                    "today_clicks": today_clicks,
                    "this_week_clicks": week_clicks,
                    "this_month_clicks": month_clicks
                }

    @staticmethod
    def increment_click_count(link_code: str) -> None:
        """增加链接点击数"""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE affiliate_links
                    SET click_count = click_count + 1
                    WHERE link_code = %s
                """, (link_code,))
                conn.commit()


# ==================== 访问追踪服务 ====================

class VisitService:
    """访问追踪服务"""

    @staticmethod
    def track_visit(
        link_code: str,
        visitor_id: Optional[str] = None,
        source: Optional[str] = None,
        referrer: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """记录访问"""
        link = LinkService.get_link_by_code(link_code)
        if not link:
            raise ValueError("链接不存在")

        if link['status'] != 'active':
            raise ValueError("链接已失效")

        if link['expires_at'] and link['expires_at'] < datetime.now():
            raise ValueError("链接已过期")

        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 记录访问
                cur.execute("""
                    INSERT INTO affiliate_visits (link_id, visitor_id, source, referrer, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (link['id'], visitor_id, source, referrer, ip_address, user_agent))

                # 增加点击数
                cur.execute("""
                    UPDATE affiliate_links
                    SET click_count = click_count + 1
                    WHERE id = %s
                """, (link['id'],))

                conn.commit()

                # 生成重定向URL
                if link['product_id']:
                    redirect_url = f"/openclaw/product/{link['product_id']}?ref={link_code}"
                else:
                    redirect_url = f"/openclaw?ref={link_code}"

                return {
                    "success": True,
                    "short_url": link['short_url'],
                    "redirect_url": redirect_url,
                    "message": "访问已记录"
                }


# ==================== 订单归属服务 ====================

class OrderService:
    """订单归属服务"""

    @staticmethod
    def assign_order_to_staff(
        order_id: int,
        link_code: str,
        product_id: Optional[int] = None,
        amount: float = 0
    ) -> Dict[str, Any]:
        """将订单归属给员工"""
        link = LinkService.get_link_by_code(link_code)
        if not link:
            raise ValueError("链接不存在")

        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # 检查订单是否已归属
                    cur.execute("""
                        SELECT id FROM affiliate_orders WHERE order_id = %s
                    """, (order_id,))

                    if cur.fetchone():
                        raise ValueError("订单已被归属")

                    # 计算佣金 (默认5%)
                    commission_rate = 0.05
                    commission = amount * commission_rate

                    # 创建订单归属记录
                    cur.execute("""
                        INSERT INTO affiliate_orders (order_id, staff_id, link_id, product_id, amount, commission)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """, (order_id, link['staff_id'], link['id'], product_id, amount, commission))

                    order = dict(cur.fetchone())

                    # 更新链接统计
                    cur.execute("""
                        UPDATE affiliate_links
                        SET order_count = order_count + 1,
                            conversion_rate = CASE
                                WHEN click_count > 0 THEN order_count::decimal / click_count
                                ELSE 0
                            END
                        WHERE id = %s
                    """, (link['id'],))

                    conn.commit()
                    return order
                except Exception as e:
                    conn.rollback()
                    raise e

    @staticmethod
    def confirm_order(order_id: int) -> Dict[str, Any]:
        """确认订单并发放佣金"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # 获取订单
                    cur.execute("SELECT * FROM affiliate_orders WHERE order_id = %s", (order_id,))
                    order = cur.fetchone()

                    if not order:
                        raise ValueError("订单不存在")

                    if order['status'] != 'pending':
                        raise ValueError("订单状态不是待确认")

                    # 更新订单状态
                    cur.execute("""
                        UPDATE affiliate_orders
                        SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
                        WHERE order_id = %s
                        RETURNING *
                    """, (order_id,))
                    order = dict(cur.fetchone())

                    # 创建佣金记录
                    cur.execute("""
                        INSERT INTO affiliate_commissions (staff_id, order_id, amount, status)
                        VALUES (%s, %s, %s, 'confirmed')
                    """, (order['staff_id'], order_id, order['commission']))

                    # 更新员工统计
                    cur.execute("""
                        UPDATE affiliate_staffs
                        SET total_sales = total_sales + %s,
                            total_orders = total_orders + 1,
                            total_commission = total_commission + %s
                        WHERE id = %s
                    """, (order['amount'], order['commission'], order['staff_id']))

                    conn.commit()
                    return order
                except Exception as e:
                    conn.rollback()
                    raise e

    @staticmethod
    def cancel_order(order_id: int) -> bool:
        """取消订单"""
        with get_db() as conn:
            with conn.cursor() as cur:
                conn.autocommit = False

                try:
                    # 获取订单
                    cur.execute("SELECT * FROM affiliate_orders WHERE order_id = %s", (order_id,))
                    order = cur.fetchone()

                    if not order:
                        raise ValueError("订单不存在")

                    if order['status'] == 'cancelled':
                        return True

                    # 更新订单状态
                    cur.execute("""
                        UPDATE affiliate_orders
                        SET status = 'cancelled'
                        WHERE order_id = %s
                    """, (order_id,))

                    # 如果订单已确认，需要回退佣金
                    if order['status'] == 'confirmed':
                        # 删除佣金记录
                        cur.execute("""
                            DELETE FROM affiliate_commissions
                            WHERE order_id = %s AND status != 'paid'
                        """, (order_id,))

                        # 回退员工统计
                        cur.execute("""
                            UPDATE affiliate_staffs
                            SET total_sales = total_sales - %s,
                                total_orders = total_orders - 1,
                                total_commission = total_commission - %s
                            WHERE id = %s
                        """, (order['amount'], order['commission'], order['staff_id']))

                    conn.commit()
                    return True
                except Exception as e:
                    conn.rollback()
                    raise e

    @staticmethod
    def list_orders(
        staff_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取订单列表"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT o.*, s.staff_name
                    FROM affiliate_orders o
                    LEFT JOIN affiliate_staffs s ON o.staff_id = s.id
                    WHERE 1=1
                """
                params = []

                if staff_id:
                    query += " AND o.staff_id = %s"
                    params.append(staff_id)

                if status:
                    query += " AND o.status = %s"
                    params.append(status)

                # 获取总数
                count_query = query.replace("SELECT o.*, s.staff_name", "SELECT COUNT(*) as total")
                cur.execute(count_query, params)
                total = cur.fetchone()['total']

                # 获取分页数据
                query += " ORDER BY o.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, (page - 1) * limit])

                cur.execute(query, params)
                orders = [dict(row) for row in cur.fetchall()]

                return {
                    "orders": orders,
                    "total": total,
                    "page": page,
                    "limit": limit
                }


# ==================== 佣金服务 ====================

class CommissionService:
    """佣金服务"""

    @staticmethod
    def list_commissions(
        staff_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取佣金列表"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT c.*, s.staff_name
                    FROM affiliate_commissions c
                    LEFT JOIN affiliate_staffs s ON c.staff_id = s.id
                    WHERE 1=1
                """
                params = []

                if staff_id:
                    query += " AND c.staff_id = %s"
                    params.append(staff_id)

                if status:
                    query += " AND c.status = %s"
                    params.append(status)

                # 获取汇总
                count_query = query.replace("SELECT c.*, s.staff_name", """
                    SELECT
                        COALESCE(SUM(c.amount), 0) as total,
                        COALESCE(SUM(CASE WHEN c.status = 'pending' THEN c.amount ELSE 0 END), 0) as pending,
                        COALESCE(SUM(CASE WHEN c.status = 'confirmed' THEN c.amount ELSE 0 END), 0) as confirmed,
                        COALESCE(SUM(CASE WHEN c.status = 'paid' THEN c.amount ELSE 0 END), 0) as paid
                """)
                cur.execute(count_query, params)
                summary = cur.fetchone()

                # 获取分页数据
                query += " ORDER BY c.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, (page - 1) * limit])

                cur.execute(query, params)
                commissions = [dict(row) for row in cur.fetchall()]

                return {
                    "commissions": commissions,
                    "total": float(summary['total']),
                    "pending": float(summary['pending']),
                    "confirmed": float(summary['confirmed']),
                    "paid": float(summary['paid'])
                }

    @staticmethod
    def pay_commission(commission_id: int) -> Dict[str, Any]:
        """支付佣金"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # 获取佣金记录
                    cur.execute("""
                        SELECT * FROM affiliate_commissions WHERE id = %s
                    """, (commission_id,))
                    commission = cur.fetchone()

                    if not commission:
                        raise ValueError("佣金记录不存在")

                    if commission['status'] == 'paid':
                        raise ValueError("佣金已支付")

                    # 更新佣金状态
                    cur.execute("""
                        UPDATE affiliate_commissions
                        SET status = 'paid', paid_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING *
                    """, (commission_id,))

                    conn.commit()
                    return dict(cur.fetchone())
                except Exception as e:
                    conn.rollback()
                    raise e


# ==================== 排行榜服务 ====================

class LeaderboardService:
    """排行榜服务"""

    @staticmethod
    def get_leaderboard(limit: int = 50, period: str = "all") -> Dict[str, Any]:
        """获取业绩排行榜"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 构建时间过滤条件
                date_filter = ""
                if period == "today":
                    date_filter = "AND DATE(o.created_at) = CURRENT_DATE"
                elif period == "week":
                    date_filter = "AND o.created_at >= CURRENT_DATE - INTERVAL '7 days'"
                elif period == "month":
                    date_filter = "AND o.created_at >= DATE_TRUNC('month', CURRENT_DATE)"

                query = f"""
                    SELECT
                        s.id as staff_id,
                        s.staff_code,
                        s.staff_name,
                        COALESCE(SUM(o.amount), 0) as total_sales,
                        COUNT(o.id) as total_orders,
                        COALESCE(SUM(o.commission), 0) as total_commission,
                        COALESCE(l.total_clicks, 0) as click_count
                    FROM affiliate_staffs s
                    LEFT JOIN affiliate_orders o ON s.id = o.staff_id AND o.status = 'confirmed' {date_filter}
                    LEFT JOIN (
                        SELECT staff_id, SUM(click_count) as total_clicks
                        FROM affiliate_links
                        GROUP BY staff_id
                    ) l ON s.id = l.staff_id
                    WHERE s.status = 'active'
                    GROUP BY s.id, s.staff_code, s.staff_name, l.total_clicks
                    ORDER BY total_sales DESC
                    LIMIT %s
                """

                cur.execute(query, (limit,))
                rows = cur.fetchall()

                # 获取总员工数
                cur.execute("SELECT COUNT(*) as total FROM affiliate_staffs WHERE status = 'active'")
                total_staffs = cur.fetchone()['total']

                # 构建排行榜
                entries = []
                for rank, row in enumerate(rows, 1):
                    entries.append({
                        "rank": rank,
                        "staff_id": row['staff_id'],
                        "staff_code": row['staff_code'],
                        "staff_name": row['staff_name'],
                        "total_sales": float(row['total_sales']),
                        "total_orders": row['total_orders'],
                        "total_commission": float(row['total_commission']),
                        "click_count": row['click_count'] or 0
                    })

                return {
                    "entries": entries,
                    "period": period,
                    "total_staffs": total_staffs
                }


# ==================== 全局统计服务 ====================

class StatsService:
    """全局统计服务"""

    @staticmethod
    def get_global_stats() -> Dict[str, Any]:
        """获取全局统计数据"""
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 员工统计
                cur.execute("""
                    SELECT
                        COUNT(*) as total_staffs,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_staffs
                    FROM affiliate_staffs
                """)
                staff_stats = cur.fetchone()

                # 链接统计
                cur.execute("SELECT COUNT(*) as total_links FROM affiliate_links")
                total_links = cur.fetchone()['total_links']

                # 访问统计
                cur.execute("SELECT COUNT(*) as total_visits FROM affiliate_visits")
                total_visits = cur.fetchone()['total_visits']

                # 订单统计
                cur.execute("""
                    SELECT
                        COUNT(*) as total_orders,
                        COALESCE(SUM(amount), 0) as total_sales
                    FROM affiliate_orders
                """)
                order_stats = cur.fetchone()

                # 佣金统计
                cur.execute("""
                    SELECT
                        COALESCE(SUM(commission), 0) as total_commission,
                        COALESCE(SUM(CASE WHEN status = 'paid' THEN commission ELSE 0 END), 0) as paid_commission,
                        COALESCE(SUM(CASE WHEN status IN ('pending', 'confirmed') THEN commission ELSE 0 END), 0) as pending_commission
                    FROM affiliate_orders
                """)
                commission_stats = cur.fetchone()

                # 获取平均转化率
                cur.execute("""
                    SELECT
                        COALESCE(SUM(click_count), 0) as total_clicks,
                        COALESCE(SUM(order_count), 0) as total_orders
                    FROM affiliate_links
                """)
                conversion_stats = cur.fetchone()

                avg_conversion = 0
                if conversion_stats['total_clicks'] > 0:
                    avg_conversion = (conversion_stats['total_orders'] / conversion_stats['total_clicks']) * 100

                # 获取最佳员工
                cur.execute("""
                    SELECT * FROM affiliate_staffs
                    ORDER BY total_sales DESC
                    LIMIT 1
                """)
                top_performer = cur.fetchone()

                return {
                    "total_staffs": staff_stats['total_staffs'],
                    "active_staffs": staff_stats['active_staffs'],
                    "total_links": total_links,
                    "total_visits": total_visits,
                    "total_orders": order_stats['total_orders'],
                    "total_sales": float(order_stats['total_sales']),
                    "total_commission": float(commission_stats['total_commission']),
                    "paid_commission": float(commission_stats['paid_commission']),
                    "pending_commission": float(commission_stats['pending_commission']),
                    "average_conversion_rate": round(avg_conversion, 2),
                    "top_performer": dict(top_performer) if top_performer else None
                }
