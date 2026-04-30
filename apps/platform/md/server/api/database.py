"""
数据库连接模块
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Dict, Any


def get_db(config: Dict[str, Any]):
    """
    获取数据库连接

    配置项:
        host: 数据库主机
        port: 数据库端口
        database: 数据库名
        user: 用户名
        password: 密码
    """
    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        database=config["database"],
        user=config["user"],
        password=config["password"],
        cursor_factory=RealDictCursor
    )
    return conn


@contextmanager
def get_db_cursor(config: Dict[str, Any]):
    """
    获取数据库游标上下文管理器

    用法:
        with get_db_cursor(DB_CONFIG) as cur:
            cur.execute("SELECT * FROM users")
            results = cur.fetchall()
    """
    conn = get_db(config)
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
