"""
统一数据库适配层 - psycopg2 同步连接

提供给所有 src/modules/* 模块使用的统一数据库游标。
替代原有的 server.api.database 和 SimpleDBCursor/MockCursor。

安全要求: 所有数据库凭证必须通过环境变量设置，缺少时程序拒绝启动。
"""

import os
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 必需的环境变量
_REQUIRED_ENV_VARS = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]

# 在模块加载时校验环境变量
_MISSING_VARS = [v for v in _REQUIRED_ENV_VARS if not os.getenv(v)]


def get_default_config() -> Dict[str, Any]:
    """
    从环境变量构建默认数据库配置。
    缺少必需变量时直接抛出 RuntimeError。
    """
    if _MISSING_VARS:
        raise RuntimeError(
            f"缺少必要的数据库环境变量: {', '.join(_MISSING_VARS)}。"
            f"请设置 {', '.join(_REQUIRED_ENV_VARS)}"
        )
    return {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def get_db(config: Optional[Dict[str, Any]] = None) -> psycopg2.extensions.connection:
    """
    获取数据库连接。

    Args:
        config: 数据库配置，不传则从环境变量读取
    """
    cfg = config or get_default_config()
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        cursor_factory=RealDictCursor
    )
    return conn


@contextmanager
def get_db_cursor(config: Optional[Dict[str, Any]] = None):
    """
    获取数据库游标上下文管理器。

    用法:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            result = cur.fetchone()

    所有 SQL 参数使用 %s 占位符（psycopg2 标准）。
    """
    cfg = config or get_default_config()
    conn = get_db(cfg)
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conn.close()
