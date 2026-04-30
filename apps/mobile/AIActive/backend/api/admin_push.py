"""
后台管理 - 配置推送管理API
创建和管理配置推送任务，批量推送到设备
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import ConfigPushTask, App, AppDevice
from websocket_server import websocket_server

# 创建蓝图
push_bp = Blueprint('admin_push', __name__)


@push_bp.route('/api/admin/apps/<int:app_id>/push/tasks', methods=['POST'])
@token_required
async def create_push_task(app_id):
    """
    创建配置推送任务

    Path Parameters:
        app_id: 应用ID

    Request Body:
        {
            "task_name": "配置更新推送",
            "push_type": 1,  // 1=配置更新, 2=素材更新, 3=全量更新
            "target_devices": ["device1", "device2"],  // 空数组表示推送到所有设备
            "config_version": "v1.0.1",
            "message": "更新通知"
        }

    Returns:
        创建的任务信息
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['task_name', 'push_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400

        push_type = data['push_type']
        if push_type not in [1, 2, 3]:
            return jsonify({
                'code': 400,
                'message': '无效的推送类型'
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

            # 确定目标设备列表
            target_devices = data.get('target_devices', [])

            if not target_devices:
                # 如果未指定设备，则推送到所有设备
                devices_result = await db.execute(
                    select(AppDevice.device_id)
                    .where(AppDevice.app_id == app_id)
                )
                target_devices = [device_id for (device_id,) in devices_result.all()]

            if not target_devices:
                return jsonify({
                    'code': 400,
                    'message': '没有可推送的设备'
                }), 400

            # 创建推送任务
            task = ConfigPushTask(
                app_id=app_id,
                task_name=data['task_name'],
                push_type=push_type,
                target_devices=target_devices,
                config_version=data.get('config_version'),
                status=0,  # 待推送
                total_devices=len(target_devices),
                success_count=0,
                failed_count=0,
                created_by=g.current_admin_id
            )

            db.add(task)
            await db.commit()
            await db.refresh(task)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='create_push_task',
                resource_type='push_task',
                resource_id=task.id,
                operation_desc=f'创建推送任务: {task.task_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            # 立即执行推送（生产环境应使用Celery等后台任务队列）
            execute_push_task(task.id)

            return jsonify({
                'code': 200,
                'message': '推送任务已创建',
                'data': {
                    'id': task.id,
                    'task_name': task.task_name,
                    'push_type': task.push_type,
                    'target_devices': task.target_devices,
                    'total_devices': task.total_devices,
                    'config_version': task.config_version,
                    'status': task.status
                }
            })

    except Exception as e:
        current_app.logger.error(f'创建推送任务失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'创建推送任务失败: {str(e)}'
        }), 500


@push_bp.route('/api/admin/apps/<int:app_id>/push/tasks', methods=['GET'])
@token_required
async def get_push_tasks(app_id):
    """
    获取推送任务列表

    Path Parameters:
        app_id: 应用ID

    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        status: 状态筛选（0=待推送, 1=推送中, 2=完成, 3=部分失败）
        push_type: 推送类型筛选

    Returns:
        任务列表
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status')
        push_type = request.args.get('push_type')

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
            query = select(ConfigPushTask).where(ConfigPushTask.app_id == app_id)

            # 筛选条件
            if status is not None:
                query = query.where(ConfigPushTask.status == int(status))
            if push_type is not None:
                query = query.where(ConfigPushTask.push_type == int(push_type))

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(ConfigPushTask.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            tasks = result.scalars().all()

            tasks_list = []
            for task in tasks:
                # 计算进度百分比
                progress = 0
                if task.total_devices > 0:
                    progress = int((task.success_count + task.failed_count) / task.total_devices * 100)

                tasks_list.append({
                    'id': task.id,
                    'task_name': task.task_name,
                    'push_type': task.push_type,
                    'push_type_name': get_push_type_name(task.push_type),
                    'target_devices': task.target_devices,
                    'total_devices': task.total_devices,
                    'success_count': task.success_count,
                    'failed_count': task.failed_count,
                    'progress': progress,
                    'config_version': task.config_version,
                    'status': task.status,
                    'status_name': get_status_name(task.status),
                    'error_message': task.error_message,
                    'created_by': task.created_by,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': tasks_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取推送任务列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取推送任务列表失败: {str(e)}'
        }), 500


@push_bp.route('/api/admin/apps/<int:app_id>/push/tasks/<int:task_id>', methods=['GET'])
@token_required
async def get_push_task_detail(app_id, task_id):
    """
    获取推送任务详情

    Path Parameters:
        app_id: 应用ID
        task_id: 任务ID

    Returns:
        任务详细信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(ConfigPushTask).where(
                    ConfigPushTask.id == task_id,
                    ConfigPushTask.app_id == app_id
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                return jsonify({
                    'code': 404,
                    'message': '任务不存在'
                }), 404

            # 计算进度
            progress = 0
            if task.total_devices > 0:
                progress = int((task.success_count + task.failed_count) / task.total_devices * 100)

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': task.id,
                    'app_id': task.app_id,
                    'task_name': task.task_name,
                    'push_type': task.push_type,
                    'push_type_name': get_push_type_name(task.push_type),
                    'target_devices': task.target_devices,
                    'config_version': task.config_version,
                    'status': task.status,
                    'status_name': get_status_name(task.status),
                    'total_devices': task.total_devices,
                    'success_count': task.success_count,
                    'failed_count': task.failed_count,
                    'progress': progress,
                    'error_message': task.error_message,
                    'created_by': task.created_by,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取推送任务详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取推送任务详情失败: {str(e)}'
        }), 500


@push_bp.route('/api/admin/apps/<int:app_id>/push/tasks/<int:task_id>/cancel', methods=['POST'])
@token_required
async def cancel_push_task(app_id, task_id):
    """
    取消推送任务

    Path Parameters:
        app_id: 应用ID
        task_id: 任务ID

    注意：只能取消待推送或推送中的任务
    """
    try:
        async for db in get_db():
            # 检查任务是否存在
            result = await db.execute(
                select(ConfigPushTask).where(
                    ConfigPushTask.id == task_id,
                    ConfigPushTask.app_id == app_id
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                return jsonify({
                    'code': 404,
                    'message': '任务不存在'
                }), 404

            # 检查任务状态
            if task.status == 2:
                return jsonify({
                    'code': 400,
                    'message': '任务已完成，无法取消'
                }), 400

            # 更新任务状态为取消
            await db.execute(
                update(ConfigPushTask)
                .where(ConfigPushTask.id == task_id)
                .values(status=4)  # 4=已取消
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='cancel_push_task',
                resource_type='push_task',
                resource_id=task_id,
                operation_desc=f'取消推送任务: {task.task_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '任务已取消'
            })

    except Exception as e:
        current_app.logger.error(f'取消推送任务失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'取消推送任务失败: {str(e)}'
        }), 500


@push_bp.route('/api/admin/apps/<int:app_id>/push/tasks/<int:task_id>/retry', methods=['POST'])
@token_required
async def retry_push_task(app_id, task_id):
    """
    重试失败的推送任务

    Path Parameters:
        app_id: 应用ID
        task_id: 任务ID

    Request Body:
        {
            "retry_failed_only": true  // 是否只重试失败的设备
        }

    Returns:
        重试结果
    """
    try:
        data = request.get_json()
        retry_failed_only = data.get('retry_failed_only', True)

        async for db in get_db():
            # 检查原任务是否存在
            result = await db.execute(
                select(ConfigPushTask).where(
                    ConfigPushTask.id == task_id,
                    ConfigPushTask.app_id == app_id
                )
            )
            original_task = result.scalar_one_or_none()

            if not original_task:
                return jsonify({
                    'code': 404,
                    'message': '任务不存在'
                }), 404

            # 确定重试的设备列表
            if retry_failed_only:
                # 重试失败的设备
                failed_count = original_task.failed_count
                target_devices = original_task.target_devices[:failed_count]
            else:
                # 重试所有设备
                target_devices = original_task.target_devices

            # 创建新的推送任务
            new_task = ConfigPushTask(
                app_id=app_id,
                task_name=f'{original_task.task_name} (重试)',
                push_type=original_task.push_type,
                target_devices=target_devices,
                config_version=original_task.config_version,
                status=0,
                total_devices=len(target_devices),
                success_count=0,
                failed_count=0,
                created_by=g.current_admin_id
            )

            db.add(new_task)
            await db.commit()
            await db.refresh(new_task)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='retry_push_task',
                resource_type='push_task',
                resource_id=new_task.id,
                operation_desc=f'重试推送任务: {new_task.task_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '重试任务已创建',
                'data': {
                    'id': new_task.id,
                    'task_name': new_task.task_name,
                    'total_devices': new_task.total_devices
                }
            })

    except Exception as e:
        current_app.logger.error(f'重试推送任务失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'重试推送任务失败: {str(e)}'
        }), 500


@push_bp.route('/api/admin/apps/<int:app_id>/push/broadcast', methods=['POST'])
@token_required
async def broadcast_push(app_id):
    """
    广播推送（推送到所有在线设备）

    Path Parameters:
        app_id: 应用ID

    Request Body:
        {
            "message": "广播消息",
            "data": {...}  // 附加数据
        }

    Returns:
        推送结果
    """
    try:
        data = request.get_json()
        message = data.get('message', '系统通知')

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

            # 构建广播消息
            broadcast_message = {
                "broadcast": {
                    "message": message,
                    "data": data.get('data', {}),
                    "timestamp": datetime.now().isoformat()
                }
            }

            # 通过WebSocket广播到所有在线设备
            count = websocket_server.broadcast_to_all(broadcast_message)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='broadcast_push',
                resource_type='push',
                operation_desc=f'广播推送: {message}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '广播成功',
                'data': {
                    'message': message,
                    'data': data.get('data', {}),
                    'broadcast_count': count
                }
            })

    except Exception as e:
        current_app.logger.error(f'广播推送失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'广播推送失败: {str(e)}'
        }), 500


@push_bp.route('/api/admin/apps/<int:app_id>/push/tasks/<int:task_id>', methods=['DELETE'])
@token_required
async def delete_push_task(app_id, task_id):
    """
    删除推送任务

    Path Parameters:
        app_id: 应用ID
        task_id: 任务ID

    注意：只能删除已完成或已取消的任务
    """
    try:
        async for db in get_db():
            # 检查任务是否存在
            result = await db.execute(
                select(ConfigPushTask).where(
                    ConfigPushTask.id == task_id,
                    ConfigPushTask.app_id == app_id
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                return jsonify({
                    'code': 404,
                    'message': '任务不存在'
                }), 404

            # 检查任务状态
            if task.status in [0, 1]:
                return jsonify({
                    'code': 400,
                    'message': '任务进行中，无法删除'
                }), 400

            task_name = task.task_name

            # 删除任务
            await db.execute(
                delete(ConfigPushTask).where(ConfigPushTask.id == task_id)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='delete_push_task',
                resource_type='push_task',
                resource_id=task_id,
                operation_desc=f'删除推送任务: {task_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '删除成功'
            })

    except Exception as e:
        current_app.logger.error(f'删除推送任务失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除推送任务失败: {str(e)}'
        }), 500


# ==================== 辅助函数 ====================

def get_push_type_name(push_type):
    """获取推送类型名称"""
    types = {
        1: '配置更新',
        2: '素材更新',
        3: '全量更新'
    }
    return types.get(push_type, '未知类型')


def get_status_name(status):
    """获取任务状态名称"""
    statuses = {
        0: '待推送',
        1: '推送中',
        2: '完成',
        3: '部分失败',
        4: '已取消'
    }
    return statuses.get(status, '未知状态')


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


# ==================== WebSocket推送集成 ====================

def execute_push_task(task_id: int):
    """
    执行推送任务
    通过WebSocket向在线设备推送配置更新

    Args:
        task_id: 推送任务ID
    """
    import threading
    # 在后台线程中执行推送，避免阻塞API响应
    thread = threading.Thread(target=_execute_push_task_thread, args=(task_id,))
    thread.daemon = True
    thread.start()


def _execute_push_task_thread(task_id: int):
    """
    推送任务执行线程
    """
    import asyncio
    from datetime import datetime

    async def _push():
        async for db in get_db():
            try:
                # 获取任务信息
                result = await db.execute(
                    select(ConfigPushTask).where(ConfigPushTask.id == task_id)
                )
                task = result.scalar_one_or_none()

                if not task:
                    current_app.logger.error(f"推送任务不存在: {task_id}")
                    return

                if task.status != 0:
                    current_app.logger.warning(f"推送任务状态不是待推送: {task.status}")
                    return

                # 更新任务状态为推送中
                task.status = 1
                task.started_at = datetime.now()
                await db.commit()

                # 准备推送数据
                # TODO: 从配置版本获取实际的文件列表
                files = [
                    {
                        "path": "config.json",
                        "url": "https://api.jcoding.tech/api/config/download/config.json",
                        "md5": "abc123"
                    }
                ]

                # 通过WebSocket推送
                push_result = websocket_server.push_config_update(
                    device_ids=task.target_devices,
                    push_id=str(task.id),
                    version=task.config_version or "1.0.0",
                    version_code=1,
                    force_update=True,
                    release_notes=f"推送任务: {task.task_name}",
                    files=files
                )

                # 更新推送结果
                task.success_count = len(push_result.get('success', []))
                task.failed_count = len(push_result.get('failed', []))

                # 确定最终状态
                if task.failed_count == 0:
                    task.status = 2  # 全部成功
                elif task.success_count == 0:
                    task.status = 3  # 全部失败
                else:
                    task.status = 3  # 部分失败

                task.completed_at = datetime.now()
                await db.commit()

                current_app.logger.info(
                    f"推送任务完成: {task_id}, "
                    f"成功={task.success_count}, 失败={task.failed_count}"
                )

            except Exception as e:
                current_app.logger.error(f"执行推送任务失败: {str(e)}")
                # 更新任务状态为失败
                task.status = 3
                task.error_message = str(e)
                task.completed_at = datetime.now()
                await db.commit()

    # 运行异步任务
    asyncio.run(_push())
