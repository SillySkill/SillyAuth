"""
后台管理 - 模块配置API
管理应用的模块配置（AI百变秀、知识问答、幸运抽奖、内场秀等）
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AppModule, App

# 创建蓝图
modules_bp = Blueprint('admin_modules', __name__)


@modules_bp.route('/api/admin/apps/<int:app_id>/modules', methods=['GET'])
@token_required
async def get_modules_list(app_id):
    """
    获取应用的所有模块配置

    Path Parameters:
        app_id: 应用ID

    Query Parameters:
        enabled: 是否只返回启用的模块（true/false）

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "modules": [
                    {
                        "id": 1,
                        "module_key": "ai_show",
                        "module_name": "AI百变秀",
                        "enabled": true,
                        "config": {...},
                        "sort_order": 1
                    },
                    ...
                ]
            }
        }
    """
    try:
        enabled_only = request.args.get('enabled', '').lower() == 'true'

        async for db in get_db():
            # 检查应用是否存在
            app_result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = app_result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 构建查询
            query = select(AppModule).where(AppModule.app_id == app_id)

            if enabled_only:
                query = query.where(AppModule.enabled == True)

            query = query.order_by(AppModule.sort_order.asc(), AppModule.id.asc())

            result = await db.execute(query)
            modules = result.scalars().all()

            modules_list = []
            for module in modules:
                modules_list.append({
                    'id': module.id,
                    'module_key': module.module_key,
                    'module_name': module.module_name,
                    'enabled': module.enabled,
                    'config': module.config or {},
                    'sort_order': module.sort_order,
                    'created_at': module.created_at.isoformat() if module.created_at else None,
                    'updated_at': module.updated_at.isoformat() if module.updated_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'modules': modules_list
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取模块列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取模块列表失败: {str(e)}'
        }), 500


@modules_bp.route('/api/admin/apps/<int:app_id>/modules', methods=['POST'])
@token_required
async def create_module(app_id):
    """
    创建新模块

    Path Parameters:
        app_id: 应用ID

    Request Body:
        {
            "module_key": "ai_show",
            "module_name": "AI百变秀",
            "enabled": true,
            "config": {...},
            "sort_order": 1
        }

    Returns:
        创建的模块信息
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['module_key', 'module_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400

        async for db in get_db():
            # 检查应用是否存在
            app_result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = app_result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 检查模块是否已存在
            existing = await db.execute(
                select(AppModule).where(
                    AppModule.app_id == app_id,
                    AppModule.module_key == data['module_key']
                )
            )
            if existing.scalar_one_or_none():
                return jsonify({
                    'code': 400,
                    'message': f'模块 {data["module_key"]} 已存在'
                }), 400

            # 创建模块
            module = AppModule(
                app_id=app_id,
                module_key=data['module_key'],
                module_name=data['module_name'],
                enabled=data.get('enabled', True),
                config=data.get('config', {}),
                sort_order=data.get('sort_order', 0)
            )

            db.add(module)
            await db.commit()
            await db.refresh(module)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='create_module',
                resource_type='module',
                resource_id=module.id,
                operation_desc=f'创建模块: {module.module_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '创建成功',
                'data': {
                    'id': module.id,
                    'module_key': module.module_key,
                    'module_name': module.module_name,
                    'enabled': module.enabled
                }
            })

    except Exception as e:
        current_app.logger.error(f'创建模块失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'创建模块失败: {str(e)}'
        }), 500


@modules_bp.route('/api/admin/apps/<int:app_id>/modules/<string:module_key>', methods=['GET'])
@token_required
async def get_module_detail(app_id, module_key):
    """
    获取模块详情

    Path Parameters:
        app_id: 应用ID
        module_key: 模块标识（如 ai_show, quiz, lottery, inner）

    Returns:
        模块详细配置
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AppModule).where(
                    AppModule.app_id == app_id,
                    AppModule.module_key == module_key
                )
            )
            module = result.scalar_one_or_none()

            if not module:
                return jsonify({
                    'code': 404,
                    'message': '模块不存在'
                }), 404

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': module.id,
                    'app_id': module.app_id,
                    'module_key': module.module_key,
                    'module_name': module.module_name,
                    'enabled': module.enabled,
                    'config': module.config or {},
                    'sort_order': module.sort_order,
                    'created_at': module.created_at.isoformat() if module.created_at else None,
                    'updated_at': module.updated_at.isoformat() if module.updated_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取模块详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取模块详情失败: {str(e)}'
        }), 500


@modules_bp.route('/api/admin/apps/<int:app_id>/modules/<string:module_key>', methods=['PUT'])
@token_required
async def update_module(app_id, module_key):
    """
    更新模块配置

    Path Parameters:
        app_id: 应用ID
        module_key: 模块标识

    Request Body:
        {
            "module_name": "新名称",
            "enabled": true,
            "config": {...},
            "sort_order": 2
        }

    Returns:
        更新成功信息
    """
    try:
        data = request.get_json()

        async for db in get_db():
            # 检查模块是否存在
            result = await db.execute(
                select(AppModule).where(
                    AppModule.app_id == app_id,
                    AppModule.module_key == module_key
                )
            )
            module = result.scalar_one_or_none()

            if not module:
                return jsonify({
                    'code': 404,
                    'message': '模块不存在'
                }), 404

            # 构建更新数据
            update_data = {}
            allowed_fields = ['module_name', 'enabled', 'config', 'sort_order']
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
                update(AppModule)
                .where(AppModule.id == module.id)
                .values(**update_data)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='update_module',
                resource_type='module',
                resource_id=module.id,
                operation_desc=f'更新模块配置: {module.module_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '更新成功'
            })

    except Exception as e:
        current_app.logger.error(f'更新模块失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新模块失败: {str(e)}'
        }), 500


@modules_bp.route('/api/admin/apps/<int:app_id>/modules/<string:module_key>', methods=['DELETE'])
@token_required
async def delete_module(app_id, module_key):
    """
    删除模块

    Path Parameters:
        app_id: 应用ID
        module_key: 模块标识
    """
    try:
        async for db in get_db():
            # 检查模块是否存在
            result = await db.execute(
                select(AppModule).where(
                    AppModule.app_id == app_id,
                    AppModule.module_key == module_key
                )
            )
            module = result.scalar_one_or_none()

            if not module:
                return jsonify({
                    'code': 404,
                    'message': '模块不存在'
                }), 404

            module_name = module.module_name

            # 删除模块
            await db.execute(
                delete(AppModule).where(AppModule.id == module.id)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='delete_module',
                resource_type='module',
                resource_id=module.id,
                operation_desc=f'删除模块: {module_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '删除成功'
            })

    except Exception as e:
        current_app.logger.error(f'删除模块失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除模块失败: {str(e)}'
        }), 500


@modules_bp.route('/api/admin/apps/<int:app_id>/modules/<string:module_key>/toggle', methods=['POST'])
@token_required
async def toggle_module(app_id, module_key):
    """
    快速切换模块启用状态

    Path Parameters:
        app_id: 应用ID
        module_key: 模块标识

    Request Body:
        {
            "enabled": true
        }

    Returns:
        切换结果
    """
    try:
        data = request.get_json()
        enabled = data.get('enabled')

        if enabled is None:
            return jsonify({
                'code': 400,
                'message': '缺少enabled参数'
            }), 400

        async for db in get_db():
            # 检查模块是否存在
            result = await db.execute(
                select(AppModule).where(
                    AppModule.app_id == app_id,
                    AppModule.module_key == module_key
                )
            )
            module = result.scalar_one_or_none()

            if not module:
                return jsonify({
                    'code': 404,
                    'message': '模块不存在'
                }), 404

            # 更新状态
            await db.execute(
                update(AppModule)
                .where(AppModule.id == module.id)
                .values(enabled=enabled)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='toggle_module',
                resource_type='module',
                resource_id=module.id,
                operation_desc=f'{"启用" if enabled else "禁用"}模块: {module.module_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '操作成功',
                'data': {
                    'enabled': enabled
                }
            })

    except Exception as e:
        current_app.logger.error(f'切换模块状态失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'切换模块状态失败: {str(e)}'
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
