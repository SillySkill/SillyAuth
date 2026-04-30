"""
数据库管理器
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'jc_ai_activity'),
            'user': os.getenv('DB_USER', 'jcode'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset': 'utf8mb4'
        }
        self.connection = None
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(**self.config)
            return self.connection
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
    
    def execute(self, sql, params=None):
        """执行SQL语句"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as e:
            print(f"SQL执行失败: {e}")
            self.connection.rollback()
            return None
    
    def fetch_one(self, sql, params=None):
        """查询单条记录"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"查询失败: {e}")
            return None
