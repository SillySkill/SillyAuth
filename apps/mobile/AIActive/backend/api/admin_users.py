"""
后台管理 - 管理员用户管理API
提供管理员用户的CRUD操作、角色管理、密码重置等功能
"""
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AdminUser

# 导入密码处理函数
from api.admin_auth import hash_password

# 创建蓝图
users_bp = Blueprint('admin_users', __name__)


@users_bp.route('/api/admin/users', methods=['GET'])
@token_required
@admin_role_required(1)  # 仅超级管理员可查看
async def get_users_list():
    """
    获取管理员列表（分页、搜索、筛选）

    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        keyword: 搜索关键词（用户名/真实姓名/邮箱）
        role: 角色筛选（1=超级管理员, 2=应用管理员）
        status: 状态筛选（1=启用, 0=禁用）

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "list": [...],
                "total": 100,
                "page": 1,
                "page_size": 20
            }
        }
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keyword = request.args.get('keyword', '').strip()
        role = request.args.get('role')
        status = request.args.get('status')

        async for db in get_db():
            query = select(AdminUser)

            # 搜索条件
            if keyword:
                query = query.where(
                    (AdminUser.username.like(f'%{keyword}%')) |
                    (AdminUser.real_name.like(f'%{keyword}%')) |
                    (AdminUser.email.like(f'%{keyword}%'))
                )

            # 角色筛选
            if role is not None:
                query = query.where(AdminUser.role == int(role))

            # 状态筛选
            if status is not None:
                query = query.where(AdminUser.status == int(status))

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(AdminUser.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            users = result.scalars().all()

            users_list = []
            for user in users:
                users_list.append({
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role,
                    'role_name': '超级管理员' if user.role == 1 else '应用管理员',
                    'status': user.status,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                    'last_login_ip': user.last_login_ip,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': users_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取管理员列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取管理员列表失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users', methods=['POST'])
@token_required
@admin_role_required(1)  # 仅超级管理员可创建
async def create_user():
    """
    创建管理员

    Request Body:
        {
            "username": "admin001",
            "password": "123456",
            "real_name": "张三",
            "email": "admin@example.com",
            "phone": "13800138000",
            "role": 2,
            "status": 1
        }

    Returns:
        创建的管理员信息
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['username', 'password', 'real_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400

        # 验证密码长度
        if len(data['password']) < 6:
            return jsonify({
                'code': 400,
                'message': '密码长度不能少于6位'
            }), 400

        async for db in get_db():
            # 检查用户名是否已存在
            existing = await db.execute(
                select(AdminUser).where(AdminUser.username == data['username'])
            )
            if existing.scalar_one_or_none():
                return jsonify({
                    'code': 400,
                    'message': '用户名已存在'
                }), 400

            # 创建管理员
            user = AdminUser(
                username=data['username'],
                password_hash=hash_password(data['password']),
                real_name=data['real_name'],
                email=data.get('email'),
                phone=data.get('phone'),
                role=data.get('role', 2),  # 默认为应用管理员
                status=data.get('status', 1)
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='create_user',
                resource_type='admin_user',
                resource_id=user.id,
                operation_desc=f'创建管理员: {user.username}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '创建成功',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'role': user.role
                }
            })

    except Exception as e:
        current_app.logger.error(f'创建管理员失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'创建管理员失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>', methods=['GET'])
@token_required
@admin_role_required(1)
async def get_user_detail(user_id):
    """
    获取管理员详情

    Path Parameters:
        user_id: 管理员ID

    Returns:
        管理员详细信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role,
                    'role_name': '超级管理员' if user.role == 1 else '应用管理员',
                    'status': user.status,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                    'last_login_ip': user.last_login_ip,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取管理员详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取管理员详情失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_role_required(1)
async def update_user(user_id):
    """
    更新管理员信息

    Path Parameters:
        user_id: 管理员ID

    Request Body:
        {
            "real_name": "新名称",
            "email": "new@example.com",
            "phone": "13900139000",
            "role": 1,
            "status": 1
        }

    Returns:
        更新结果
    """
    try:
        data = request.get_json()

        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 不允许修改自己的角色和状态
            if user.id == g.current_admin_id:
                if 'role' in data:
                    return jsonify({
                        'code': 400,
                        'message': '不能修改自己的角色'
                    }), 400
                if 'status' in data and data['status'] == 0:
                    return jsonify({
                        'code': 400,
                        'message': '不能禁用自己的账号'
                    }), 400

            # 构建更新数据
            update_data = {}
            allowed_fields = ['real_name', 'email', 'phone', 'role', 'status']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            if not update_data:
                return jsonify({
                    'code': 400,
                    'message': '没有可更新的字段'
                }), 400

            # 执行更新
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == user_id)
                .values(**update_data)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='update_user',
                resource_type='admin_user',
                resource_id=user_id,
                operation_desc=f'更新管理员信息: {user.username}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '更新成功'
            })

    except Exception as e:
        current_app.logger.error(f'更新管理员失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新管理员失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_role_required(1)
async def delete_user(user_id):
    """
    删除管理员

    Path Parameters:
        user_id: 管理员ID

    注意：不能删除自己
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 不允许删除自己
            if user.id == g.current_admin_id:
                return jsonify({
                    'code': 400,
                    'message': '不能删除自己的账号'
                }), 400

            username = user.username

            # 删除管理员
            await db.execute(
                delete(AdminUser).where(AdminUser.id == user_id)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='delete_user',
                resource_type='admin_user',
                resource_id=user_id,
                operation_desc=f'删除管理员: {username}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '删除成功'
            })

    except Exception as e:
        current_app.logger.error(f'删除管理员失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除管理员失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@token_required
@admin_role_required(1)
async def reset_user_password(user_id):
    """
    重置管理员密码

    Path Parameters:
        user_id: 管理员ID

    Request Body:
        {
            "new_password": "123456"
        }

    Returns:
        重置结果
    """
    try:
        data = request.get_json()
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({
                'code': 400,
                'message': '新密码不能为空'
            }), 400

        if len(new_password) < 6:
            return jsonify({
                'code': 400,
                'message': '新密码长度不能少于6位'
            }), 400

        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 更新密码
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == user_id)
                .values(password_hash=hash_password(new_password))
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='reset_password',
                resource_type='admin_user',
                resource_id=user_id,
                operation_desc=f'重置管理员密码: {user.username}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '密码重置成功'
            })

    except Exception as e:
        current_app.logger.error(f'重置密码失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'重置密码失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@token_required
@admin_role_required(1)
async def toggle_user_status(user_id):
    """
    快速切换管理员启用状态

    Path Parameters:
        user_id: 管理员ID

    Request Body:
        {
            "status": 1  // 1=启用, 0=禁用
        }

    Returns:
        切换结果
    """
    try:
        data = request.get_json()
        status = data.get('status')

        if status is None:
            return jsonify({
                'code': 400,
                'message': '缺少status参数'
            }), 400

        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 不允许禁用自己
            if user.id == g.current_admin_id and status == 0:
                return jsonify({
                    'code': 400,
                    'message': '不能禁用自己的账号'
                }), 400

            # 更新状态
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == user_id)
                .values(status=int(status))
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='toggle_user_status',
                resource_type='admin_user',
                resource_id=user_id,
                operation_desc=f'{"启用" if status else "禁用"}管理员: {user.username}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '操作成功',
                'data': {
                    'status': int(status)
                }
            })

    except Exception as e:
        current_app.logger.error(f'切换管理员状态失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'切换管理员状态失败: {str(e)}'
        }), 500


# ==================== 辅助函数 ====================

async def log_operation(db: AsyncSession, admin_id: int, operation: str,
                        operation_desc: str = None, resource_type: str = None,
                        resource_id: int = None, request_ip: str = None,
                        user_agent: str = None, status: int = 1):
    """记录管理员操作日志"""
    from models_admin import AdminOperationLog

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
