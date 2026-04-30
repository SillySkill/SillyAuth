"""
Tasks Module Services
Business logic for task system operations

Provides task management, check-in handling, and achievement tracking
"""

import os
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from contextlib import contextmanager

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Connection pool for database connections
_db_pool = None

def _get_db_pool():
    """Get or create the database connection pool."""
    global _db_pool
    if _db_pool is None:
        config = get_db_config()
        _db_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **config
        )
    return _db_pool

@contextmanager
def get_db(config: Optional[Dict[str, Any]] = None):
    """
    Get a database connection using a connection pool.

    Args:
        config: Database configuration (uses get_db_config() if not provided)

    Yields:
        Database connection
    """
    if config is None:
        config = get_db_config()

    db_pool = _get_db_pool()
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Database configuration
def get_db_config() -> Dict[str, Any]:
    """Get database configuration"""
    return {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }


# Default task configurations
DEFAULT_SIGN_IN_CONFIG = {
    "enabled": True,
    "base_points": 10,
    "streak_bonus": 2,
    "max_streak_days": 30
}

# Default daily tasks
DEFAULT_DAILY_TASKS = [
    {
        "id": "daily_login",
        "name": "每日登录",
        "description": "每天登录应用",
        "type": "daily",
        "reward_type": "points",
        "reward_amount": 5,
        "conditions": {"action": "login"},
        "target": 1
    },
    {
        "id": "daily_checkin",
        "name": "每日签到",
        "description": "完成每日签到",
        "type": "daily",
        "reward_type": "points",
        "reward_amount": 10,
        "conditions": {"action": "check_in"},
        "target": 1
    },
    {
        "id": "daily_share",
        "name": "每日分享",
        "description": "分享任意内容一次",
        "type": "daily",
        "reward_type": "points",
        "reward_amount": 8,
        "conditions": {"action": "share"},
        "target": 1
    },
    {
        "id": "daily_upload",
        "name": "每日上传",
        "description": "上传一个文件",
        "type": "daily",
        "reward_type": "points",
        "reward_amount": 15,
        "conditions": {"action": "upload"},
        "target": 1
    }
]

# Default achievements
DEFAULT_ACHIEVEMENTS = [
    {
        "id": "first_checkin",
        "name": "初次签到",
        "description": "完成第一次签到",
        "icon": "badge_first",
        "condition_type": "check_in_count",
        "condition_value": 1,
        "reward_type": "points",
        "reward_amount": 20,
        "rarity": "common"
    },
    {
        "id": "week_streak",
        "name": "连续一周",
        "description": "连续签到7天",
        "icon": "badge_week",
        "condition_type": "streak_days",
        "condition_value": 7,
        "reward_type": "points",
        "reward_amount": 50,
        "rarity": "rare"
    },
    {
        "id": "month_streak",
        "name": "连续一月",
        "description": "连续签到30天",
        "icon": "badge_month",
        "condition_type": "streak_days",
        "condition_value": 30,
        "reward_type": "points",
        "reward_amount": 200,
        "rarity": "epic"
    },
    {
        "id": "century_streak",
        "name": "百日坚持",
        "description": "连续签到100天",
        "icon": "badge_century",
        "condition_type": "streak_days",
        "condition_value": 100,
        "reward_type": "points",
        "reward_amount": 500,
        "rarity": "legendary"
    },
    {
        "id": "tasks_10",
        "name": "任务达人",
        "description": "累计完成10个任务",
        "icon": "badge_tasks_10",
        "condition_type": "tasks_completed",
        "condition_value": 10,
        "reward_type": "points",
        "reward_amount": 30,
        "rarity": "common"
    },
    {
        "id": "tasks_100",
        "name": "任务狂人",
        "description": "累计完成100个任务",
        "icon": "badge_tasks_100",
        "condition_type": "tasks_completed",
        "condition_value": 100,
        "reward_type": "points",
        "reward_amount": 150,
        "rarity": "rare"
    }
]


# ============================================================================
# Database Initialization
# ============================================================================

def init_tables():
    """Initialize task-related database tables"""
    with get_db(get_db_config()) as conn:
        with conn.cursor() as cur:
            # Task definitions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS task_definitions (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    type VARCHAR(20) NOT NULL DEFAULT 'daily',
                    reward_type VARCHAR(20) NOT NULL DEFAULT 'points',
                    reward_amount INTEGER NOT NULL DEFAULT 0,
                    conditions JSONB DEFAULT '{}',
                    icon VARCHAR(255),
                    target INTEGER DEFAULT 1,
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User task progress table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_task_progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    task_id VARCHAR(50) NOT NULL,
                    progress INTEGER DEFAULT 0,
                    target INTEGER DEFAULT 1,
                    completed BOOLEAN DEFAULT FALSE,
                    claimed BOOLEAN DEFAULT FALSE,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    claimed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, task_id),
                    FOREIGN KEY (task_id) REFERENCES task_definitions(id)
                )
            """)

            # Check-in records table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS check_in_records (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    check_in_date DATE NOT NULL,
                    points_earned INTEGER NOT NULL,
                    streak_days INTEGER DEFAULT 0,
                    bonus_points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, check_in_date)
                )
            """)

            # Achievements table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS achievement_definitions (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    icon VARCHAR(255),
                    condition_type VARCHAR(50) NOT NULL,
                    condition_value INTEGER NOT NULL,
                    reward_type VARCHAR(20) NOT NULL DEFAULT 'points',
                    reward_amount INTEGER NOT NULL DEFAULT 0,
                    rarity VARCHAR(20) DEFAULT 'common',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User achievements table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    achievement_id VARCHAR(50) NOT NULL,
                    unlocked_at TIMESTAMP,
                    claimed BOOLEAN DEFAULT FALSE,
                    claimed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, achievement_id),
                    FOREIGN KEY (achievement_id) REFERENCES achievement_definitions(id)
                )
            """)

            conn.commit()

            # Initialize default data
            _init_default_data(cur, conn)


def _init_default_data(cur, conn):
    """Initialize default tasks and achievements"""
    # Insert default daily tasks
    for task in DEFAULT_DAILY_TASKS:
        cur.execute("""
            INSERT INTO task_definitions (id, name, description, type, reward_type, reward_amount, conditions, target)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                reward_amount = EXCLUDED.reward_amount
        """, (
            task['id'], task['name'], task['description'], task['type'],
            task['reward_type'], task['reward_amount'],
            __import__('json').dumps(task['conditions']), task['target']
        ))

    # Insert default achievements
    for achievement in DEFAULT_ACHIEVEMENTS:
        cur.execute("""
            INSERT INTO achievement_definitions (id, name, description, icon, condition_type, condition_value, reward_type, reward_amount, rarity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                condition_value = EXCLUDED.condition_value,
                reward_amount = EXCLUDED.reward_amount
        """, (
            achievement['id'], achievement['name'], achievement['description'],
            achievement['icon'], achievement['condition_type'], achievement['condition_value'],
            achievement['reward_type'], achievement['reward_amount'], achievement['rarity']
        ))

    conn.commit()


# ============================================================================
# Task Service
# ============================================================================

class TaskService:
    """Task management service"""

    @staticmethod
    def get_daily_tasks(user_id: int) -> List[Dict[str, Any]]:
        """
        Get daily tasks for a user

        Args:
            user_id: User ID

        Returns:
            List of daily tasks with progress
        """
        init_tables()

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()

                # Get active daily tasks
                cur.execute("""
                    SELECT * FROM task_definitions
                    WHERE type = 'daily' AND is_active = TRUE
                    ORDER BY sort_order ASC
                """)
                tasks = [dict(row) for row in cur.fetchall()]

                # Get user's progress for these tasks
                cur.execute("""
                    SELECT * FROM user_task_progress
                    WHERE user_id = %s AND task_id IN (
                        SELECT id FROM task_definitions WHERE type = 'daily' AND is_active = TRUE
                    )
                """, (user_id,))
                progress_map = {row['task_id']: dict(row) for row in cur.fetchall()}

                # Build result
                result = []
                for task in tasks:
                    progress = progress_map.get(task['id'], {})
                    task_progress = progress.get('progress', 0) if progress else 0
                    target = task.get('target', 1)

                    # Check if task was completed today (or is still valid)
                    completed_at = progress.get('completed_at') if progress else None
                    is_today_completed = (
                        completed_at and
                        isinstance(completed_at, (datetime, date)) and
                        (completed_at.date() == today if hasattr(completed_at, 'date') else completed_at == today)
                    ) if completed_at else False

                    # Reset progress for new day if task was completed before today
                    if progress and completed_at:
                        completed_date = completed_at.date() if hasattr(completed_at, 'date') else completed_at
                        if completed_date < today:
                            # Reset for new day - but don't delete record
                            task_progress = 0

                    result.append({
                        "task_id": task['id'],
                        "name": task['name'],
                        "description": task['description'],
                        "type": task['type'],
                        "icon": task['icon'],
                        "reward_type": task['reward_type'],
                        "reward_amount": task['reward_amount'],
                        "progress": task_progress,
                        "target": target,
                        "completed": task_progress >= target,
                        "claimed": progress.get('claimed', False) if progress else False,
                        "available": True
                    })

                return result

    @staticmethod
    def update_progress(user_id: int, task_id: str, progress_delta: int = 1, conditions: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update task progress for a user

        Args:
            user_id: User ID
            task_id: Task ID
            progress_delta: Progress to add
            conditions: Optional additional conditions

        Returns:
            True if task was completed
        """
        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # Get task definition
                    cur.execute("SELECT * FROM task_definitions WHERE id = %s AND is_active = TRUE", (task_id,))
                    task = cur.fetchone()
                    if not task:
                        return False

                    target = task['target']

                    # Get or create progress record
                    cur.execute("""
                        SELECT * FROM user_task_progress
                        WHERE user_id = %s AND task_id = %s
                    """, (user_id, task_id))
                    progress = cur.fetchone()

                    if not progress:
                        # Create new progress record
                        cur.execute("""
                            INSERT INTO user_task_progress (user_id, task_id, progress, target, started_at)
                            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                            RETURNING *
                        """, (user_id, task_id, progress_delta, target))
                        progress = cur.fetchone()
                    else:
                        # Check if needs reset for new day
                        today = date.today()
                        completed_at = progress.get('completed_at')
                        if completed_at:
                            completed_date = completed_at.date() if hasattr(completed_at, 'date') else completed_at
                            if completed_date < today:
                                # Reset progress for new day
                                progress['progress'] = 0
                                progress['completed'] = False
                                progress['claimed'] = False

                        # Update progress
                        new_progress = min(progress['progress'] + progress_delta, target)
                        completed = new_progress >= target
                        completed_at_value = datetime.now() if completed and not progress['completed'] else None

                        cur.execute("""
                            UPDATE user_task_progress
                            SET progress = %s,
                                completed = %s,
                                completed_at = COALESCE(%s, completed_at),
                                updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = %s AND task_id = %s
                            RETURNING *
                        """, (new_progress, completed, completed_at_value, user_id, task_id))
                        progress = cur.fetchone()

                    conn.commit()

                    # If task completed, check achievements
                    if progress['completed'] and not progress.get('claimed'):
                        TaskService._check_task_achievements(user_id, task_id)

                    return progress['completed']

                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error updating task progress: {e}")
                    return False

    @staticmethod
    def claim_task_reward(user_id: int, task_id: str) -> Dict[str, Any]:
        """
        Claim task reward

        Args:
            user_id: User ID
            task_id: Task ID

        Returns:
            Claim result
        """
        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # Get task definition
                    cur.execute("SELECT * FROM task_definitions WHERE id = %s", (task_id,))
                    task = cur.fetchone()
                    if not task:
                        raise ValueError("任务不存在")

                    # Get progress
                    cur.execute("""
                        SELECT * FROM user_task_progress
                        WHERE user_id = %s AND task_id = %s
                    """, (user_id, task_id))
                    progress = cur.fetchone()

                    if not progress:
                        raise ValueError("任务进度不存在")

                    if not progress['completed']:
                        raise ValueError("任务未完成")

                    if progress['claimed']:
                        raise ValueError("奖励已领取")

                    # Get current points
                    cur.execute("SELECT ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
                    user = cur.fetchone()
                    if not user:
                        raise ValueError("用户不存在")

                    balance_before = user['ai_points']
                    reward_amount = task['reward_amount']
                    balance_after = balance_before + reward_amount

                    # Update user points
                    cur.execute("""
                        UPDATE users SET ai_points = ai_points + %s WHERE id = %s
                    """, (reward_amount, user_id))

                    # Record transaction
                    cur.execute("""
                        INSERT INTO point_transactions (
                            user_id, transaction_type, amount, balance_before, balance_after, description
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, "task_reward", reward_amount, balance_before, balance_after, f"任务奖励: {task['name']}"))

                    # Mark as claimed
                    cur.execute("""
                        UPDATE user_task_progress
                        SET claimed = TRUE, claimed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s AND task_id = %s
                    """, (user_id, task_id))

                    conn.commit()

                    return {
                        "success": True,
                        "message": "奖励领取成功",
                        "reward_type": task['reward_type'],
                        "reward_amount": reward_amount,
                        "total_points": balance_after
                    }

                except ValueError as e:
                    conn.rollback()
                    raise e
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error claiming task reward: {e}")
                    raise e

    @staticmethod
    def check_task_completion(user_id: int, task_id: str) -> bool:
        """
        Check if task is completed

        Args:
            user_id: User ID
            task_id: Task ID

        Returns:
            True if completed
        """
        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT completed FROM user_task_progress
                    WHERE user_id = %s AND task_id = %s
                """, (user_id, task_id))
                result = cur.fetchone()
                return result['completed'] if result else False

    @staticmethod
    def _check_task_achievements(user_id: int, task_id: str):
        """Check and unlock task-related achievements"""
        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Count completed tasks
                cur.execute("""
                    SELECT COUNT(*) as count FROM user_task_progress
                    WHERE user_id = %s AND completed = TRUE
                """, (user_id,))
                tasks_count = cur.fetchone()['count']

                # Check task-related achievements
                cur.execute("""
                    SELECT * FROM achievement_definitions
                    WHERE condition_type = 'tasks_completed' AND is_active = TRUE
                """)
                achievements = cur.fetchall()

                for achievement in achievements:
                    if tasks_count >= achievement['condition_value']:
                        AchievementService.check_achievement_unlock(user_id, achievement['id'])


# ============================================================================
# Check-In Service
# ============================================================================

class CheckInService:
    """Check-in management service"""

    @staticmethod
    def check_in(user_id: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform daily check-in

        Args:
            user_id: User ID
            config: Optional check-in configuration

        Returns:
            Check-in record
        """
        init_tables()

        if config is None:
            config = DEFAULT_SIGN_IN_CONFIG

        if not config.get('enabled', True):
            raise ValueError("签到功能已禁用")

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    today = date.today()

                    # Check if already checked in today
                    cur.execute("""
                        SELECT id FROM check_in_records
                        WHERE user_id = %s AND check_in_date = %s
                    """, (user_id, today))
                    if cur.fetchone():
                        raise ValueError("今日已签到")

                    # Calculate streak
                    yesterday = today - timedelta(days=1)
                    cur.execute("""
                        SELECT streak_days FROM check_in_records
                        WHERE user_id = %s AND check_in_date = %s
                    """, (user_id, yesterday))
                    yesterday_record = cur.fetchone()

                    if yesterday_record:
                        current_streak = yesterday_record['streak_days'] + 1
                    else:
                        current_streak = 1

                    # Cap streak at max
                    max_streak = config.get('max_streak_days', 30)
                    current_streak = min(current_streak, max_streak)

                    # Calculate points
                    base_points = config.get('base_points', 10)
                    streak_bonus = config.get('streak_bonus', 2)
                    bonus_points = min((current_streak - 1) * streak_bonus, max_streak * streak_bonus)
                    total_points = base_points + bonus_points

                    # Get user balance
                    cur.execute("SELECT ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
                    user = cur.fetchone()
                    if not user:
                        raise ValueError("用户不存在")

                    balance_before = user['ai_points']
                    balance_after = balance_before + total_points

                    # Update user points
                    cur.execute("""
                        UPDATE users SET ai_points = ai_points + %s WHERE id = %s
                    """, (total_points, user_id))

                    # Record transaction
                    cur.execute("""
                        INSERT INTO point_transactions (
                            user_id, transaction_type, amount, balance_before, balance_after, description
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, "check_in", total_points, balance_before, balance_after, f"每日签到 (连续{total_points}天)"))

                    # Create check-in record
                    cur.execute("""
                        INSERT INTO check_in_records (user_id, check_in_date, points_earned, streak_days, bonus_points)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                    """, (user_id, today, base_points, current_streak, bonus_points))

                    record = dict(cur.fetchone())

                    # Update task progress if task system available
                    try:
                        TaskService.update_progress(user_id, "daily_checkin", progress_delta=1)
                    except Exception as e:
                        logger.warning(f"Failed to update daily_checkin task: {e}")

                    conn.commit()

                    return {
                        "id": record['id'],
                        "user_id": user_id,
                        "check_in_date": record['check_in_date'],
                        "points_earned": total_points,
                        "streak_days": current_streak,
                        "bonus_points": bonus_points,
                        "created_at": record['created_at']
                    }

                except ValueError:
                    conn.rollback()
                    raise
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error during check-in: {e}")
                    raise e

    @staticmethod
    def get_check_in_status(user_id: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get check-in status for a user

        Args:
            user_id: User ID
            config: Optional check-in configuration

        Returns:
            Check-in status
        """
        init_tables()

        if config is None:
            config = DEFAULT_SIGN_IN_CONFIG

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()

                # Check today's status
                cur.execute("""
                    SELECT * FROM check_in_records
                    WHERE user_id = %s AND check_in_date = %s
                """, (user_id, today))
                today_record = cur.fetchone()

                # Get current streak from most recent record
                cur.execute("""
                    SELECT streak_days, check_in_date FROM check_in_records
                    WHERE user_id = %s
                    ORDER BY check_in_date DESC
                    LIMIT 1
                """, (user_id,))
                last_record = cur.fetchone()
                current_streak = last_record['streak_days'] if last_record else 0

                # Verify streak is still valid (last check-in must be yesterday or today)
                if current_streak > 0 and last_record:
                    last_date = last_record['check_in_date']
                    if isinstance(last_date, datetime):
                        last_date = last_date.date()
                    if last_date < today - timedelta(days=1):
                        current_streak = 0

                # Get longest streak
                cur.execute("""
                    SELECT MAX(streak_days) as max_streak FROM check_in_records
                    WHERE user_id = %s
                """, (user_id,))
                longest_streak = cur.fetchone()['max_streak'] or 0

                # Get total check-ins
                cur.execute("""
                    SELECT COUNT(*) as count FROM check_in_records
                    WHERE user_id = %s
                """, (user_id,))
                total_check_ins = cur.fetchone()['count']

                # Calculate next bonus
                base_points = config.get('base_points', 10)
                streak_bonus = config.get('streak_bonus', 2)
                next_bonus_in = None
                if current_streak > 0:
                    next_bonus_in = max(0, (current_streak + 1) - current_streak)

                return {
                    "user_id": user_id,
                    "checked_in_today": today_record is not None,
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "total_check_ins": total_check_ins,
                    "next_bonus_in": next_bonus_in,
                    "base_points": base_points,
                    "streak_bonus": streak_bonus
                }

    @staticmethod
    def get_streak(user_id: int) -> int:
        """
        Get current check-in streak for a user

        Args:
            user_id: User ID

        Returns:
            Current streak days
        """
        status = CheckInService.get_check_in_status(user_id)
        return status['current_streak']

    @staticmethod
    def get_calendar(user_id: int, year: int, month: int) -> Dict[str, Any]:
        """
        Get monthly sign-in calendar for a user.

        Args:
            user_id: User ID
            year: Calendar year
            month: Calendar month (1-12)

        Returns:
            Calendar data with daily check-in records for the specified month
        """
        init_tables()

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get check-in records for the specified month
                cur.execute("""
                    SELECT
                        check_in_date,
                        streak_days,
                        points_earned,
                        bonus_points
                    FROM check_in_records
                    WHERE user_id = %s
                      AND EXTRACT(YEAR FROM check_in_date) = %s
                      AND EXTRACT(MONTH FROM check_in_date) = %s
                    ORDER BY check_in_date ASC
                """, (user_id, year, month))

                rows = cur.fetchall()

                records = []
                for row in rows:
                    check_date = row['check_in_date']
                    if isinstance(check_date, datetime):
                        check_date = check_date.date()

                    records.append({
                        "date": check_date.isoformat(),
                        "consecutive_days": row['streak_days'],
                        "points_earned": row['points_earned'],
                        "bonus_points": row['bonus_points'] or 0,
                    })

                # Count total check-ins (all time)
                cur.execute("""
                    SELECT COUNT(*) as count FROM check_in_records
                    WHERE user_id = %s
                """, (user_id,))
                total_days = cur.fetchone()['count']

                return {
                    "year": year,
                    "month": month,
                    "records": records,
                    "checked_days": len(records),
                    "total_days": total_days,
                }


# ============================================================================
# Achievement Service
# ============================================================================

class AchievementService:
    """Achievement management service"""

    @staticmethod
    def get_achievements(user_id: int) -> List[Dict[str, Any]]:
        """
        Get all achievements with user's unlock status

        Args:
            user_id: User ID

        Returns:
            List of achievements with status
        """
        init_tables()

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all active achievements
                cur.execute("""
                    SELECT * FROM achievement_definitions
                    WHERE is_active = TRUE
                    ORDER BY condition_value ASC
                """)
                achievements = [dict(row) for row in cur.fetchall()]

                # Get user's unlocked achievements
                cur.execute("""
                    SELECT * FROM user_achievements
                    WHERE user_id = %s
                """, (user_id,))
                user_achievements = {row['achievement_id']: dict(row) for row in cur.fetchall()}

                # Build result
                result = []
                for achievement in achievements:
                    user_ach = user_achievements.get(achievement['id'])
                    result.append({
                        "achievement_id": achievement['id'],
                        "user_id": user_id,
                        "unlocked_at": user_ach['unlocked_at'] if user_ach else None,
                        "claimed": user_ach['claimed'] if user_ach else False,
                        "claimed_at": user_ach['claimed_at'] if user_ach else None,
                        "achievement": achievement
                    })

                return result

    @staticmethod
    def check_achievement_unlock(user_id: int, achievement_id: str) -> bool:
        """
        Check and unlock achievement if conditions are met

        Args:
            user_id: User ID
            achievement_id: Achievement ID to check

        Returns:
            True if unlocked
        """
        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # Get achievement definition
                    cur.execute("""
                        SELECT * FROM achievement_definitions
                        WHERE id = %s AND is_active = TRUE
                    """, (achievement_id,))
                    achievement = cur.fetchone()
                    if not achievement:
                        return False

                    # Check if already unlocked
                    cur.execute("""
                        SELECT id FROM user_achievements
                        WHERE user_id = %s AND achievement_id = %s
                    """, (user_id, achievement_id))
                    if cur.fetchone():
                        return False

                    # Check condition
                    condition_type = achievement['condition_type']
                    condition_value = achievement['condition_value']
                    should_unlock = False

                    if condition_type == 'check_in_count':
                        cur.execute("""
                            SELECT COUNT(*) as count FROM check_in_records
                            WHERE user_id = %s
                        """, (user_id,))
                        count = cur.fetchone()['count']
                        should_unlock = count >= condition_value

                    elif condition_type == 'streak_days':
                        streak = CheckInService.get_streak(user_id)
                        should_unlock = streak >= condition_value

                    elif condition_type == 'tasks_completed':
                        cur.execute("""
                            SELECT COUNT(*) as count FROM user_task_progress
                            WHERE user_id = %s AND completed = TRUE AND claimed = TRUE
                        """, (user_id,))
                        count = cur.fetchone()['count']
                        should_unlock = count >= condition_value

                    elif condition_type == 'total_points':
                        cur.execute("""
                            SELECT ai_points FROM users WHERE id = %s
                        """, (user_id,))
                        user = cur.fetchone()
                        points = user['ai_points'] if user else 0
                        should_unlock = points >= condition_value

                    if should_unlock:
                        # Unlock achievement
                        cur.execute("""
                            INSERT INTO user_achievements (user_id, achievement_id, unlocked_at)
                            VALUES (%s, %s, CURRENT_TIMESTAMP)
                            ON CONFLICT (user_id, achievement_id) DO NOTHING
                        """, (user_id, achievement_id))
                        conn.commit()
                        logger.info(f"Achievement unlocked: {achievement_id} for user {user_id}")
                        return True

                    return False

                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error checking achievement unlock: {e}")
                    return False

    @staticmethod
    def claim_achievement_reward(user_id: int, achievement_id: str) -> Dict[str, Any]:
        """
        Claim achievement reward

        Args:
            user_id: User ID
            achievement_id: Achievement ID

        Returns:
            Claim result
        """
        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conn.autocommit = False

                try:
                    # Get achievement
                    cur.execute("""
                        SELECT * FROM achievement_definitions WHERE id = %s
                    """, (achievement_id,))
                    achievement = cur.fetchone()
                    if not achievement:
                        raise ValueError("成就不存在")

                    # Check if unlocked
                    cur.execute("""
                        SELECT * FROM user_achievements
                        WHERE user_id = %s AND achievement_id = %s
                    """, (user_id, achievement_id))
                    user_achievement = cur.fetchone()

                    if not user_achievement:
                        raise ValueError("成就未解锁")

                    if user_achievement['claimed']:
                        raise ValueError("奖励已领取")

                    # Get user balance
                    cur.execute("SELECT ai_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
                    user = cur.fetchone()
                    if not user:
                        raise ValueError("用户不存在")

                    balance_before = user['ai_points']
                    reward_amount = achievement['reward_amount']
                    balance_after = balance_before + reward_amount

                    # Update user points
                    cur.execute("""
                        UPDATE users SET ai_points = ai_points + %s WHERE id = %s
                    """, (reward_amount, user_id))

                    # Record transaction
                    cur.execute("""
                        INSERT INTO point_transactions (
                            user_id, transaction_type, amount, balance_before, balance_after, description
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, "achievement_reward", reward_amount, balance_before, balance_after, f"成就奖励: {achievement['name']}"))

                    # Mark as claimed
                    cur.execute("""
                        UPDATE user_achievements
                        SET claimed = TRUE, claimed_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s AND achievement_id = %s
                    """, (user_id, achievement_id))

                    conn.commit()

                    return {
                        "success": True,
                        "message": "奖励领取成功",
                        "reward_type": achievement['reward_type'],
                        "reward_amount": reward_amount,
                        "total_points": balance_after
                    }

                except ValueError:
                    conn.rollback()
                    raise
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error claiming achievement reward: {e}")
                    raise e


# ============================================================================
# Task Statistics Service
# ============================================================================

class TaskStatsService:
    """Task statistics service"""

    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive task statistics for a user

        Args:
            user_id: User ID

        Returns:
            Task statistics
        """
        init_tables()

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Total tasks completed
                cur.execute("""
                    SELECT COUNT(*) as count FROM user_task_progress
                    WHERE user_id = %s AND completed = TRUE
                """, (user_id,))
                total_tasks_completed = cur.fetchone()['count']

                # Daily tasks completed
                cur.execute("""
                    SELECT COUNT(*) as count FROM user_task_progress utp
                    JOIN task_definitions td ON utp.task_id = td.id
                    WHERE utp.user_id = %s AND utp.completed = TRUE AND td.type = 'daily'
                """, (user_id,))
                daily_tasks_completed = cur.fetchone()['count']

                # Weekly tasks completed
                cur.execute("""
                    SELECT COUNT(*) as count FROM user_task_progress utp
                    JOIN task_definitions td ON utp.task_id = td.id
                    WHERE utp.user_id = %s AND utp.completed = TRUE AND td.type = 'weekly'
                """, (user_id,))
                weekly_tasks_completed = cur.fetchone()['count']

                # Achievements unlocked
                cur.execute("""
                    SELECT COUNT(*) as count FROM user_achievements
                    WHERE user_id = %s
                """, (user_id,))
                achievements_unlocked = cur.fetchone()['count']

                # Total achievements
                cur.execute("""
                    SELECT COUNT(*) as count FROM achievement_definitions
                    WHERE is_active = TRUE
                """, (user_id,))
                achievements_total = cur.fetchone()['count']

                # Total points earned from tasks
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as total FROM point_transactions
                    WHERE user_id = %s AND transaction_type IN ('task_reward', 'achievement_reward')
                """, (user_id,))
                total_points_earned = cur.fetchone()['total']

                return {
                    "user_id": user_id,
                    "total_tasks_completed": total_tasks_completed,
                    "daily_tasks_completed": daily_tasks_completed,
                    "weekly_tasks_completed": weekly_tasks_completed,
                    "achievements_unlocked": achievements_unlocked,
                    "achievements_total": achievements_total,
                    "total_points_earned": total_points_earned
                }


# Initialize tables on module load
try:
    init_tables()
except Exception as e:
    logger.warning(f"Failed to initialize task tables: {e}")
