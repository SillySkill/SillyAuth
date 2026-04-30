"""
后台管理 - 设备管理API
管理应用设备、查看在线状态、推送配置
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AppDevice, App

# 创建蓝图
devices_bp = Blueprint('admin_devices', __name__)


@devices_bp.route('/api/admin/apps/<int:app_id>/devices', methods=['GET'])
@token_required
async def get_devices_list(app_id):
    """
    获取设备列表（分页、筛选）

    Path Parameters:
        app_id: 应用ID

    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        status: 状态筛选（0=离线, 1=在线）
        keyword: 搜索关键词（设备ID/设备名称）

    Returns:
        设备列表
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status')
        keyword = request.args.get('keyword', '').strip()

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
            query = select(AppDevice).where(AppDevice.app_id == app_id)

            # 筛选条件
            if status is not None:
                query = query.where(AppDevice.status == int(status))
            if keyword:
                query = query.where(
                    (AppDevice.device_id.like(f'%{keyword}%')) |
                    (AppDevice.device_name.like(f'%{keyword}%'))
                )

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(AppDevice.last_active_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            devices = result.scalars().all()

            devices_list = []
            for device in devices:
                # 计算距离上次活跃的时间
                last_active = device.last_active_at
                time_diff = None
                if last_active:
                    now = datetime.utcnow()
                    time_diff = (now - last_active).total_seconds()

                devices_list.append({
                    'id': device.id,
                    'device_id': device.device_id,
                    'device_name': device.device_name,
                    'device_model': device.device_model,
                    'os_version': device.os_version,
                    'app_version': device.app_version,
                    'push_token': device.push_token,
                    'status': device.status,
                    'last_active_at': device.last_active_at.isoformat() if device.last_active_at else None,
                    'inactive_seconds': time_diff,
                    'created_at': device.created_at.isoformat() if device.created_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': devices_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取设备列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取设备列表失败: {str(e)}'
        }), 500


@devices_bp.route('/api/admin/apps/<int:app_id>/devices/online', methods=['GET'])
@token_required
async def get_online_devices(app_id):
    """
    获取在线设备列表

    Path Parameters:
        app_id: 应用ID

    Query Parameters:
        minutes: 在线定义（分钟，默认30分钟内有活动视为在线）

    Returns:
        在线设备列表
    """
    try:
        minutes = int(request.args.get('minutes', 30))

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

            # 计算在线阈值时间
            threshold_time = datetime.utcnow() - timedelta(minutes=minutes)

            # 查询在线设备
            result = await db.execute(
                select(AppDevice)
                .where(
                    AppDevice.app_id == app_id,
                    AppDevice.last_active_at >= threshold_time
                )
                .order_by(AppDevice.last_active_at.desc())
            )
            devices = result.scalars().all()

            devices_list = []
            for device in devices:
                devices_list.append({
                    'id': device.id,
                    'device_id': device.device_id,
                    'device_name': device.device_name,
                    'device_model': device.device_model,
                    'os_version': device.os_version,
                    'app_version': device.app_version,
                    'last_active_at': device.last_active_at.isoformat() if device.last_active_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'online_count': len(devices_list),
                    'devices': devices_list
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取在线设备失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取在线设备失败: {str(e)}'
        }), 500


@devices_bp.route('/api/admin/apps/<int:app_id>/devices/<string:device_id>', methods=['GET'])
@token_required
async def get_device_detail(app_id, device_id):
    """
    获取设备详情

    Path Parameters:
        app_id: 应用ID
        device_id: 设备ID

    Returns:
        设备详细信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AppDevice).where(
                    AppDevice.app_id == app_id,
                    AppDevice.device_id == device_id
                )
            )
            device = result.scalar_one_or_none()

            if not device:
                return jsonify({
                    'code': 404,
                    'message': '设备不存在'
                }), 404

            # 计算距离上次活跃的时间
            last_active = device.last_active_at
            time_diff = None
            is_online = False
            if last_active:
                now = datetime.utcnow()
                time_diff = (now - last_active).total_seconds()
                is_online = time_diff < 1800  # 30分钟内有活动视为在线

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': device.id,
                    'app_id': device.app_id,
                    'device_id': device.device_id,
                    'device_name': device.device_name,
                    'device_model': device.device_model,
                    'os_version': device.os_version,
                    'app_version': device.app_version,
                    'push_token': device.push_token,
                    'status': device.status,
                    'is_online': is_online,
                    'last_active_at': device.last_active_at.isoformat() if device.last_active_at else None,
                    'inactive_seconds': time_diff,
                    'created_at': device.created_at.isoformat() if device.created_at else None,
                    'updated_at': device.updated_at.isoformat() if device.updated_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取设备详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取设备详情失败: {str(e)}'
        }), 500


@devices_bp.route('/api/admin/apps/<int:app_id>/devices/<string:device_id>', methods=['DELETE'])
@token_required
async def unbind_device(app_id, device_id):
    """
    解绑设备

    Path Parameters:
        app_id: 应用ID
        device_id: 设备ID

    注意：解绑后设备需要重新注册才能连接
    """
    try:
        async for db in get_db():
            # 检查设备是否存在
            result = await db.execute(
                select(AppDevice).where(
                    AppDevice.app_id == app_id,
                    AppDevice.device_id == device_id
                )
            )
            device = result.scalar_one_or_none()

            if not device:
                return jsonify({
                    'code': 404,
                    'message': '设备不存在'
                }), 404

            device_name = device.device_name or device.device_id

            # 删除设备
            await db.execute(
                delete(AppDevice).where(AppDevice.id == device.id)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='unbind_device',
                resource_type='device',
                resource_id=device.id,
                operation_desc=f'解绑设备: {device_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '解绑成功'
            })

    except Exception as e:
        current_app.logger.error(f'解绑设备失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'解绑设备失败: {str(e)}'
        }), 500


@devices_bp.route('/api/admin/apps/<int:app_id>/devices/stats', methods=['GET'])
@token_required
async def get_devices_stats(app_id):
    """
    获取设备统计信息

    Path Parameters:
        app_id: 应用ID

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total_devices": 100,
                "online_devices": 50,
                "offline_devices": 50,
                "version_distribution": {
                    "1.0.0": 60,
                    "1.0.1": 40
                }
            }
        }
    """
    try:
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

            # 总设备数
            total_devices = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.app_id == app_id)
            )

            # 在线设备数（30分钟内有活动）
            threshold_time = datetime.utcnow() - timedelta(minutes=30)
            online_devices = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(
                    AppDevice.app_id == app_id,
                    AppDevice.last_active_at >= threshold_time
                )
            )

            # 离线设备数
            offline_devices = (total_devices or 0) - (online_devices or 0)

            # 版本分布
            result = await db.execute(
                select(AppDevice.app_version, func.count())
                .where(AppDevice.app_id == app_id)
                .group_by(AppDevice.app_version)
            )
            version_rows = result.all()
            version_distribution = {version: count for version, count in version_rows}

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_devices': total_devices or 0,
                    'online_devices': online_devices or 0,
                    'offline_devices': offline_devices,
                    'version_distribution': version_distribution
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取设备统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取设备统计失败: {str(e)}'
        }), 500


@devices_bp.route('/api/admin/apps/<int:app_id>/devices/<string:device_id>/push', methods=['POST'])
@token_required
async def push_to_device(app_id, device_id):
    """
    推送配置到单个设备

    Path Parameters:
        app_id: 应用ID
        device_id: 设备ID

    Request Body:
        {
            "message": "配置更新通知",
            "config_version": "v1.0.1"
        }

    Returns:
        推送结果
    """
    try:
        data = request.get_json()
        message = data.get('message', '配置更新')
        config_version = data.get('config_version')

        async for db in get_db():
            # 检查设备是否存在
            result = await db.execute(
                select(AppDevice).where(
                    AppDevice.app_id == app_id,
                    AppDevice.device_id == device_id
                )
            )
            device = result.scalar_one_or_none()

            if not device:
                return jsonify({
                    'code': 404,
                    'message': '设备不存在'
                }), 404

            # TODO: 实现实际的推送逻辑
            # 方案1: Firebase Cloud Messaging
            # 方案2: WebSocket推送
            # 方案3: MQTT推送

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='push_to_device',
                resource_type='device',
                resource_id=device.id,
                operation_desc=f'推送配置到设备: {device.device_name or device.device_id}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '推送成功',
                'data': {
                    'device_id': device_id,
                    'message': message,
                    'config_version': config_version
                }
            })

    except Exception as e:
        current_app.logger.error(f'推送配置失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'推送配置失败: {str(e)}'
        }), 500


@devices_bp.route('/api/admin/apps/<int:app_id>/devices/batch-unbind', methods=['POST'])
@token_required
async def batch_unbind_devices(app_id):
    """
    批量解绑设备

    Path Parameters:
        app_id: 应用ID

    Request Body:
        {
            "device_ids": ["device1", "device2", ...]
        }

    Returns:
        批量操作结果
    """
    try:
        data = request.get_json()
        device_ids = data.get('device_ids', [])

        if not device_ids:
            return jsonify({
                'code': 400,
                'message': '请选择要解绑的设备'
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

            # 批量删除设备
            result = await db.execute(
                delete(AppDevice)
                .where(
                    AppDevice.app_id == app_id,
                    AppDevice.device_id.in_(device_ids)
                )
            )
            deleted_count = result.rowcount
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='batch_unbind_devices',
                resource_type='device',
                operation_desc=f'批量解绑设备: {deleted_count}个',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '批量解绑成功',
                'data': {
                    'deleted_count': deleted_count
                }
            })

    except Exception as e:
        current_app.logger.error(f'批量解绑设备失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'批量解绑设备失败: {str(e)}'
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
