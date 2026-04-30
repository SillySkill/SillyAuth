"""
JWT认证中间件
用于后台管理系统的API身份验证
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# JWT配置
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def generate_token(admin_id: int, username: str, role: int) -> str:
    """
    生成JWT Token

    Args:
        admin_id: 管理员ID
        username: 用户名
        role: 角色

    Returns:
        JWT Token字符串
    """
    payload = {
        'admin_id': admin_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    解码JWT Token

    Args:
        token: JWT Token字符串

    Returns:
        解码后的payload字典
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    Token验证装饰器

    使用示例:
        @app.route('/api/test')
        @token_required
        def test():
            return jsonify({'admin_id': g.current_admin_id})
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        from sqlalchemy.ext.asyncio import AsyncSession

        # 从Authorization header获取token
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'code': 401,
                'message': '缺少认证令牌'
            }), 401

        # Token格式: "Bearer <token>"
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'code': 401,
                'message': '无效的令牌格式'
            }), 401

        # 解码token
        payload = decode_token(token)

        if not payload:
            return jsonify({
                'code': 401,
                'message': '令牌无效或已过期'
            }), 401

        # 将用户信息存储到g对象中
        g.current_admin_id = payload.get('admin_id')
        g.current_username = payload.get('username')
        g.current_role = payload.get('role')

        return await f(*args, **kwargs)

    return decorated_function


def admin_role_required(role: int):
    """
    角色权限验证装饰器

    Args:
        role: 所需的最低角色等级 (1=超级管理员, 2=应用管理员)

    使用示例:
        @app.route('/api/admin-only')
        @token_required
        @admin_role_required(1)
        def admin_only():
            return jsonify({'message': 'Only super admin'})
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_role'):
                return jsonify({
                    'code': 401,
                    'message': '未认证'
                }), 401

            # 检查角色权限
            # role=1是超级管理员，拥有所有权限
            # role=2是应用管理员
            if g.current_role > role:
                return jsonify({
                    'code': 403,
                    'message': '权限不足'
                }), 403

            return await f(*args, **kwargs)

        return decorated_function
    return decorator
