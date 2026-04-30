"""
后台管理认证API
提供管理员登录、登出、个人信息管理等功能
"""

import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import generate_token, token_required
from database import get_db

# 创建蓝图
auth_bp = Blueprint('admin_auth', __name__)


@auth_bp.route('/api/admin/auth/login', methods=['POST'])
async def login():
    """
    管理员登录

    Request Body:
        username: 用户名
        password: 密码

    Returns:
        JWT Token和管理员信息
    """
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空'
            }), 400

        async for db in get_db():
            # 查询管理员
            result = await db.execute(
                select(AdminUser).where(
                    AdminUser.username == username,
                    AdminUser.status == 1
                )
            )
            admin = result.scalar_one_or_none()

            if not admin:
                return jsonify({
                    'code': 401,
                    'message': '用户名或密码错误'
                }), 401

            # 验证密码 (使用bcrypt)
            if not verify_password(password, admin.password_hash):
                return jsonify({
                    'code': 401,
                    'message': '用户名或密码错误'
                }), 401

            # 生成token
            token = generate_token(admin.id, admin.username, admin.role)

            # 更新最后登录信息
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == admin.id)
                .values(
                    last_login_at=datetime.utcnow(),
                    last_login_ip=request.remote_addr
                )
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=admin.id,
                operation='login',
                operation_desc='管理员登录',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'token': token,
                    'admin': {
                        'id': admin.id,
                        'username': admin.username,
                        'real_name': admin.real_name,
                        'email': admin.email,
                        'role': admin.role,
                        'role_name': '超级管理员' if admin.role == 1 else '应用管理员'
                    }
                }
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}'
        }), 500


@auth_bp.route('/api/admin/auth/logout', methods=['POST'])
@token_required
async def logout():
    """
    管理员登出

    注意: JWT是无状态的，客户端删除token即可
    此接口主要用于记录登出日志
    """
    try:
        async for db in get_db():
            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='logout',
                operation_desc='管理员登出',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '登出成功'
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'登出失败: {str(e)}'
        }), 500


@auth_bp.route('/api/admin/auth/profile', methods=['GET'])
@token_required
async def get_profile():
    """
    获取当前管理员个人信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == g.current_admin_id)
            )
            admin = result.scalar_one_or_none()

            if not admin:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': admin.id,
                    'username': admin.username,
                    'real_name': admin.real_name,
                    'email': admin.email,
                    'phone': admin.phone,
                    'role': admin.role,
                    'role_name': '超级管理员' if admin.role == 1 else '应用管理员',
                    'status': admin.status,
                    'last_login_at': admin.last_login_at.isoformat() if admin.last_login_at else None,
                    'last_login_ip': admin.last_login_ip,
                    'created_at': admin.created_at.isoformat() if admin.created_at else None
                }
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取信息失败: {str(e)}'
        }), 500


@auth_bp.route('/api/admin/auth/password', methods=['PUT'])
@token_required
async def change_password():
    """
    修改密码

    Request Body:
        old_password: 旧密码
        new_password: 新密码
    """
    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({
                'code': 400,
                'message': '旧密码和新密码不能为空'
            }), 400

        if len(new_password) < 6:
            return jsonify({
                'code': 400,
                'message': '新密码长度不能少于6位'
            }), 400

        async for db in get_db():
            # 查询管理员
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == g.current_admin_id)
            )
            admin = result.scalar_one_or_none()

            if not admin:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 验证旧密码
            if not verify_password(old_password, admin.password_hash):
                return jsonify({
                    'code': 401,
                    'message': '旧密码错误'
                }), 401

            # 更新密码
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == admin.id)
                .values(password_hash=hash_password(new_password))
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='change_password',
                operation_desc='修改密码',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '密码修改成功'
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'修改密码失败: {str(e)}'
        }), 500


# ==================== 辅助函数 ====================

def hash_password(password: str) -> str:
    """
    对密码进行哈希 (使用bcrypt)

    注意: 实际实现需要安装bcrypt库
    pip install bcrypt
    """
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码

    Args:
        password: 明文密码
        password_hash: 密码哈希

    Returns:
        是否匹配
    """
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


async def log_operation(db: AsyncSession, admin_id: int, operation: str,
                        operation_desc: str = None, resource_type: str = None,
                        resource_id: int = None, request_ip: str = None,
                        user_agent: str = None, status: int = 1):
    """
    记录管理员操作日志
    """
    from models import AdminOperationLog

    log = AdminOperationLog(
        admin_id=admin_id,
        operation=operation,
        resource_type=resource_type,
        resource_id=resource_id,
        operation_desc=operation_desc,
        request_ip=request_ip,
        user_agent=user_agent,
        status=status
    )

    db.add(log)
    await db.commit()
