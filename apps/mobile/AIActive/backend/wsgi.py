"""
WSGI入口文件
用于Gunicorn启动应用
"""
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application

if __name__ == '__main__':
    application.run()
