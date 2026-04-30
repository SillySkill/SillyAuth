"""
后台管理 - 应用管理API
提供应用的CRUD操作和统计功能
"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import App, AdminUser, AppModule, AppAsset, AppDevice, ConfigPushTask

# 创建蓝图
apps_bp = Blueprint('admin_apps', __name__)


@apps_bp.route('/api/admin/apps', methods=['GET'])
@token_required
async def get_apps_list():
    """
    获取应用列表（分页、搜索、筛选）

    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        keyword: 搜索关键词（应用名称/应用Key）
        status: 状态筛选（0=禁用, 1=启用）
        created_by: 创建人筛选

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
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keyword = request.args.get('keyword', '').strip()
        status = request.args.get('status')
        created_by = request.args.get('created_by')

        async for db in get_db():
            # 构建查询
            query = select(App)

            # 搜索条件
            if keyword:
                query = query.where(
                    (App.app_name.like(f'%{keyword}%')) |
                    (App.app_key.like(f'%{keyword}%')) |
                    (App.package_name.like(f'%{keyword}%'))
                )

            # 状态筛选
            if status is not None:
                query = query.where(App.status == int(status))

            # 创建人筛选
            if created_by:
                query = query.where(App.created_by == int(created_by))

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(App.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            apps = result.scalars().all()

            # 序列化结果
            apps_list = []
            for app in apps:
                apps_list.append({
                    'id': app.id,
                    'app_key': app.app_key,
                    'app_name': app.app_name,
                    'app_name_en': app.app_name_en,
                    'app_description': app.app_description,
                    'app_icon': app.app_icon,
                    'package_name': app.package_name,
                    'version': app.version,
                    'status': app.status,
                    'created_by': app.created_by,
                    'created_at': app.created_at.isoformat() if app.created_at else None,
                    'updated_at': app.updated_at.isoformat() if app.updated_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': apps_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取应用列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取应用列表失败: {str(e)}'
        }), 500


@apps_bp.route('/api/admin/apps', methods=['POST'])
@token_required
@admin_role_required(1)  # 仅超级管理员可创建
async def create_app():
    """
    创建应用

    Request Body:
        {
            "app_name": "AI活动秀",
            "app_name_en": "AI Activity Show",
            "app_description": "应用描述",
            "app_icon": "https://...",
            "package_name": "com.jcoding.aiactivity",
            "version": "1.0.0",
            "status": 1
        }

    Returns:
        创建的应用信息
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['app_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400

        async for db in get_db():
            # 生成唯一的app_key
            app_key = data.get('app_key') or f'app_{uuid.uuid4().hex[:16]}'

            # 检查app_key是否已存在
            existing = await db.execute(
                select(App).where(App.app_key == app_key)
            )
            if existing.scalar_one_or_none():
                return jsonify({
                    'code': 400,
                    'message': '应用标识已存在'
                }), 400

            # 创建应用
            app = App(
                app_key=app_key,
                app_name=data['app_name'],
                app_name_en=data.get('app_name_en'),
                app_description=data.get('app_description'),
                app_icon=data.get('app_icon'),
                package_name=data.get('package_name'),
                version=data.get('version', '1.0.0'),
                status=data.get('status', 1),
                created_by=g.current_admin_id
            )

            db.add(app)
            await db.commit()
            await db.refresh(app)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='create_app',
                resource_type='app',
                resource_id=app.id,
                operation_desc=f'创建应用: {app.app_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '创建成功',
                'data': {
                    'id': app.id,
                    'app_key': app.app_key,
                    'app_name': app.app_name,
                    'version': app.version,
                    'status': app.status
                }
            })

    except Exception as e:
        current_app.logger.error(f'创建应用失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'创建应用失败: {str(e)}'
        }), 500


@apps_bp.route('/api/admin/apps/<int:app_id>', methods=['GET'])
@token_required
async def get_app_detail(app_id):
    """
    获取应用详情

    Path Parameters:
        app_id: 应用ID

    Returns:
        应用详细信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 获取创建人信息
            creator = None
            if app.created_by:
                creator_result = await db.execute(
                    select(AdminUser).where(AdminUser.id == app.created_by)
                )
                creator_user = creator_result.scalar_one_or_none()
                if creator_user:
                    creator = {
                        'id': creator_user.id,
                        'username': creator_user.username,
                        'real_name': creator_user.real_name
                    }

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': app.id,
                    'app_key': app.app_key,
                    'app_name': app.app_name,
                    'app_name_en': app.app_name_en,
                    'app_description': app.app_description,
                    'app_icon': app.app_icon,
                    'package_name': app.package_name,
                    'version': app.version,
                    'status': app.status,
                    'created_by': app.created_by,
                    'creator': creator,
                    'created_at': app.created_at.isoformat() if app.created_at else None,
                    'updated_at': app.updated_at.isoformat() if app.updated_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取应用详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取应用详情失败: {str(e)}'
        }), 500


@apps_bp.route('/api/admin/apps/<int:app_id>', methods=['PUT'])
@token_required
async def update_app(app_id):
    """
    更新应用信息

    Path Parameters:
        app_id: 应用ID

    Request Body:
        {
            "app_name": "新名称",
            "app_description": "新描述",
            "status": 1
        }

    Returns:
        更新后的应用信息
    """
    try:
        data = request.get_json()

        async for db in get_db():
            # 检查应用是否存在
            result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 权限检查：只有超级管理员或应用创建者可以修改
            if g.current_role != 1 and app.created_by != g.current_admin_id:
                return jsonify({
                    'code': 403,
                    'message': '权限不足'
                }), 403

            # 构建更新数据
            update_data = {}
            allowed_fields = ['app_name', 'app_name_en', 'app_description',
                            'app_icon', 'package_name', 'version', 'status']
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
                update(App)
                .where(App.id == app_id)
                .values(**update_data)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='update_app',
                resource_type='app',
                resource_id=app_id,
                operation_desc=f'更新应用: {app.app_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '更新成功'
            })

    except Exception as e:
        current_app.logger.error(f'更新应用失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新应用失败: {str(e)}'
        }), 500


@apps_bp.route('/api/admin/apps/<int:app_id>', methods=['DELETE'])
@token_required
@admin_role_required(1)  # 仅超级管理员可删除
async def delete_app(app_id):
    """
    删除应用

    Path Parameters:
        app_id: 应用ID

    注意：会级联删除所有关联数据（模块、素材、设备、推送任务）
    """
    try:
        async for db in get_db():
            # 检查应用是否存在
            result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            app_name = app.app_name

            # 删除应用（级联删除关联数据）
            await db.execute(
                delete(App).where(App.id == app_id)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='delete_app',
                resource_type='app',
                resource_id=app_id,
                operation_desc=f'删除应用: {app_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '删除成功'
            })

    except Exception as e:
        current_app.logger.error(f'删除应用失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除应用失败: {str(e)}'
        }), 500


@apps_bp.route('/api/admin/apps/<int:app_id>/stats', methods=['GET'])
@token_required
async def get_app_stats(app_id):
    """
    获取应用统计信息

    Path Parameters:
        app_id: 应用ID

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "modules_count": 4,
                "assets_count": 150,
                "devices_count": 50,
                "online_devices_count": 30,
                "push_tasks_count": 10
            }
        }
    """
    try:
        async for db in get_db():
            # 检查应用是否存在
            result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 统计模块数量
            modules_count = await db.scalar(
                select(func.count())
                .select_from(AppModule)
                .where(AppModule.app_id == app_id)
            )

            # 统计素材数量
            assets_count = await db.scalar(
                select(func.count())
                .select_from(AppAsset)
                .where(AppAsset.app_id == app_id)
            )

            # 统计设备总数
            devices_count = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.app_id == app_id)
            )

            # 统计在线设备数
            online_devices_count = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.app_id == app_id, AppDevice.status == 1)
            )

            # 统计推送任务数
            push_tasks_count = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.app_id == app_id)
            )

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'modules_count': modules_count or 0,
                    'assets_count': assets_count or 0,
                    'devices_count': devices_count or 0,
                    'online_devices_count': online_devices_count or 0,
                    'push_tasks_count': push_tasks_count or 0
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取应用统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取应用统计失败: {str(e)}'
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
