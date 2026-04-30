"""
后台管理 - 系统统计API
提供系统统计数据、仪表板数据、图表数据等
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required
from database_admin import get_db
from models_admin import App, AppModule, AppAsset, AppDevice, ConfigPushTask, AdminOperationLog

# 创建蓝图
stats_bp = Blueprint('admin_stats', __name__)


@stats_bp.route('/api/admin/stats/overview', methods=['GET'])
@token_required
async def get_overview_stats():
    """
    获取系统概览统计

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total_apps": 10,
                "total_devices": 1000,
                "total_assets": 5000,
                "online_devices": 650,
                "today_push_tasks": 20,
                "active_modules": 40
            }
        }
    """
    try:
        async for db in get_db():
            # 应用总数
            total_apps = await db.scalar(
                select(func.count()).select_from(App)
            )

            # 设备总数
            total_devices = await db.scalar(
                select(func.count()).select_from(AppDevice)
            )

            # 素材总数
            total_assets = await db.scalar(
                select(func.count()).select_from(AppAsset)
            )

            # 在线设备数（30分钟内有活动）
            threshold_time = datetime.utcnow() - timedelta(minutes=30)
            online_devices = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.last_active_at >= threshold_time)
            )

            # 今日推送任务数
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_push_tasks = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= today_start)
            )

            # 启用的模块数
            active_modules = await db.scalar(
                select(func.count())
                .select_from(AppModule)
                .where(AppModule.enabled == True)
            )

            # 今日操作数
            today_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(AdminOperationLog.created_at >= today_start)
            )

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_apps': total_apps or 0,
                    'total_devices': total_devices or 0,
                    'total_assets': total_assets or 0,
                    'online_devices': online_devices or 0,
                    'today_push_tasks': today_push_tasks or 0,
                    'active_modules': active_modules or 0,
                    'today_operations': today_operations or 0
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取系统统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取系统统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/apps', methods=['GET'])
@token_required
async def get_apps_stats():
    """
    获取应用统计

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total_apps": 10,
                "enabled_apps": 8,
                "disabled_apps": 2,
                "apps_stats": [...]
            }
        }
    """
    try:
        async for db in get_db():
            # 应用总数
            total_apps = await db.scalar(
                select(func.count()).select_from(App)
            )

            # 启用的应用数
            enabled_apps = await db.scalar(
                select(func.count())
                .select_from(App)
                .where(App.status == 1)
            )

            # 禁用的应用数
            disabled_apps = (total_apps or 0) - (enabled_apps or 0)

            # 每个应用的统计信息
            result = await db.execute(
                select(App.id, App.app_name, App.status)
                .order_by(App.id)
            )
            apps = result.all()

            apps_stats = []
            for app_id, app_name, app_status in apps:
                modules_count = await db.scalar(
                    select(func.count())
                    .select_from(AppModule)
                    .where(AppModule.app_id == app_id)
                )

                active_modules_count = await db.scalar(
                    select(func.count())
                    .select_from(AppModule)
                    .where(
                        AppModule.app_id == app_id,
                        AppModule.enabled == True
                    )
                )

                assets_count = await db.scalar(
                    select(func.count())
                    .select_from(AppAsset)
                    .where(AppAsset.app_id == app_id)
                )

                devices_count = await db.scalar(
                    select(func.count())
                    .select_from(AppDevice)
                    .where(AppDevice.app_id == app_id)
                )

                # 在线设备数
                threshold_time = datetime.utcnow() - timedelta(minutes=30)
                online_devices_count = await db.scalar(
                    select(func.count())
                    .select_from(AppDevice)
                    .where(
                        AppDevice.app_id == app_id,
                        AppDevice.last_active_at >= threshold_time
                    )
                )

                push_tasks_count = await db.scalar(
                    select(func.count())
                    .select_from(ConfigPushTask)
                    .where(ConfigPushTask.app_id == app_id)
                )

                apps_stats.append({
                    'id': app_id,
                    'app_name': app_name,
                    'status': app_status,
                    'modules_count': modules_count or 0,
                    'active_modules_count': active_modules_count or 0,
                    'assets_count': assets_count or 0,
                    'devices_count': devices_count or 0,
                    'online_devices_count': online_devices_count or 0,
                    'push_tasks_count': push_tasks_count or 0
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_apps': total_apps or 0,
                    'enabled_apps': enabled_apps or 0,
                    'disabled_apps': disabled_apps,
                    'apps_stats': apps_stats
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取应用统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取应用统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/devices', methods=['GET'])
@token_required
async def get_devices_stats():
    """
    获取设备统计

    Returns:
        设备统计数据
    """
    try:
        async for db in get_db():
            # 总设备数
            total_devices = await db.scalar(
                select(func.count()).select_from(AppDevice)
            )

            # 在线设备数（30分钟内有活动）
            threshold_time = datetime.utcnow() - timedelta(minutes=30)
            online_devices = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.last_active_at >= threshold_time)
            )

            # 离线设备数
            offline_devices = (total_devices or 0) - (online_devices or 0)

            # 版本分布
            result = await db.execute(
                select(AppDevice.app_version, func.count())
                .group_by(AppDevice.app_version)
                .order_by(func.count().desc())
            )
            version_distribution = {version or '未知': count for version, count in result.all()}

            # 设备型号分布（Top 10）
            result = await db.execute(
                select(AppDevice.device_model, func.count())
                .group_by(AppDevice.device_model)
                .order_by(func.count().desc())
                .limit(10)
            )
            model_distribution = [{ 'model': model or '未知', 'count': count } for model, count in result.all()]

            # 按应用统计设备数
            result = await db.execute(
                select(App.app_name, func.count())
                .select_from(AppDevice)
                .join(App, App.id == AppDevice.app_id)
                .group_by(App.id, App.app_name)
                .order_by(func.count().desc())
            )
            app_device_distribution = [{ 'app_name': app_name, 'count': count } for app_name, count in result.all()]

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_devices': total_devices or 0,
                    'online_devices': online_devices or 0,
                    'offline_devices': offline_devices,
                    'online_rate': round((online_devices or 0) / (total_devices or 1) * 100, 2),
                    'version_distribution': version_distribution,
                    'model_distribution': model_distribution,
                    'app_device_distribution': app_device_distribution
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取设备统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取设备统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/assets', methods=['GET'])
@token_required
async def get_assets_stats():
    """
    获取素材统计

    Returns:
        素材统计数据
    """
    try:
        async for db in get_db():
            # 总素材数
            total_assets = await db.scalar(
                select(func.count()).select_from(AppAsset)
            )

            # 按类型统计
            result = await db.execute(
                select(AppAsset.asset_type, func.count())
                .group_by(AppAsset.asset_type)
                .order_by(func.count().desc())
            )
            type_distribution = {asset_type: count for asset_type, count in result.all()}

            # 总文件大小
            total_size = await db.scalar(
                select(func.sum(AppAsset.file_size)).select_from(AppAsset)
            )

            # 按模块统计
            result = await db.execute(
                select(AppAsset.module_key, func.count())
                .group_by(AppAsset.module_key)
                .order_by(func.count().desc())
            )
            module_distribution = [{ 'module': module or '未分配', 'count': count } for module, count in result.all()]

            # 今日上传数
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_uploads = await db.scalar(
                select(func.count())
                .select_from(AppAsset)
                .where(AppAsset.created_at >= today_start)
            )

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_assets': total_assets or 0,
                    'total_size': total_size or 0,
                    'total_size_mb': round((total_size or 0) / (1024 * 1024), 2),
                    'type_distribution': type_distribution,
                    'module_distribution': module_distribution,
                    'today_uploads': today_uploads or 0
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取素材统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取素材统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/push', methods=['GET'])
@token_required
async def get_push_stats():
    """
    获取推送统计

    Returns:
        推送统计数据
    """
    try:
        days = int(request.args.get('days', 7))

        async for db in get_db():
            # 计算起始日期
            start_date = datetime.utcnow() - timedelta(days=days)

            # 总推送任务数
            total_tasks = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= start_date)
            )

            # 完成的任务数
            completed_tasks = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(
                    ConfigPushTask.created_at >= start_date,
                    ConfigPushTask.status == 2
                )
            )

            # 失败的任务数
            failed_tasks = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(
                    ConfigPushTask.created_at >= start_date,
                    ConfigPushTask.status == 3
                )
            )

            # 按推送类型统计
            result = await db.execute(
                select(ConfigPushTask.push_type, func.count())
                .where(ConfigPushTask.created_at >= start_date)
                .group_by(ConfigPushTask.push_type)
            )
            type_stats = {}
            for push_type, count in result.all():
                type_name = {
                    1: '配置更新',
                    2: '素材更新',
                    3: '全量更新'
                }.get(push_type, '未知类型')
                type_stats[type_name] = count

            # 总推送设备数
            total_devices = await db.scalar(
                select(func.sum(ConfigPushTask.total_devices))
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= start_date)
            )

            # 成功推送设备数
            success_devices = await db.scalar(
                select(func.sum(ConfigPushTask.success_count))
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= start_date)
            )

            # 失败推送设备数
            failed_devices = await db.scalar(
                select(func.sum(ConfigPushTask.failed_count))
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= start_date)
            )

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_tasks': total_tasks or 0,
                    'completed_tasks': completed_tasks or 0,
                    'failed_tasks': failed_tasks or 0,
                    'type_stats': type_stats,
                    'total_devices': total_devices or 0,
                    'success_devices': success_devices or 0,
                    'failed_devices': failed_devices or 0,
                    'success_rate': round((success_devices or 0) / (total_devices or 1) * 100, 2)
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取推送统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取推送统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/timeline', methods=['GET'])
@token_required
async def get_timeline_stats():
    """
    获取时间线数据（用于图表展示）

    Query Parameters:
        days: 天数（默认7天）
        type: 数据类型（operations/push_tasks/devices/assets）

    Returns:
        时间线数据
    """
    try:
        days = int(request.args.get('days', 7))
        data_type = request.args.get('type', 'operations')

        async for db in get_db():
            timeline_data = []

            for i in range(days):
                date = datetime.utcnow() - timedelta(days=days-i-1)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

                data_point = {
                    'date': date_start.strftime('%Y-%m-%d'),
                    'timestamp': date_start.timestamp()
                }

                if data_type == 'operations':
                    # 操作数统计
                    count = await db.scalar(
                        select(func.count())
                        .select_from(AdminOperationLog)
                        .where(
                            AdminOperationLog.created_at >= date_start,
                            AdminOperationLog.created_at <= date_end
                        )
                    )
                    data_point['count'] = count or 0

                elif data_type == 'push_tasks':
                    # 推送任务数统计
                    count = await db.scalar(
                        select(func.count())
                        .select_from(ConfigPushTask)
                        .where(
                            ConfigPushTask.created_at >= date_start,
                            ConfigPushTask.created_at <= date_end
                        )
                    )
                    data_point['count'] = count or 0

                elif data_type == 'devices':
                    # 新增设备数统计
                    count = await db.scalar(
                        select(func.count())
                        .select_from(AppDevice)
                        .where(
                            AppDevice.created_at >= date_start,
                            AppDevice.created_at <= date_end
                        )
                    )
                    data_point['count'] = count or 0

                elif data_type == 'assets':
                    # 新增素材数统计
                    count = await db.scalar(
                        select(func.count())
                        .select_from(AppAsset)
                        .where(
                            AppAsset.created_at >= date_start,
                            AppAsset.created_at <= date_end
                        )
                    )
                    data_point['count'] = count or 0

                timeline_data.append(data_point)

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'type': data_type,
                    'timeline': timeline_data
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取时间线数据失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取时间线数据失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/dashboard', methods=['GET'])
@token_required
async def get_dashboard_data():
    """
    获取仪表板完整数据（汇总所有统计数据）

    Returns:
        仪表板数据
    """
    try:
        async for db in get_db():
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            threshold_time = datetime.utcnow() - timedelta(minutes=30)

            # 基础统计
            total_apps = await db.scalar(select(func.count()).select_from(App))
            total_devices = await db.scalar(select(func.count()).select_from(AppDevice))
            total_assets = await db.scalar(select(func.count()).select_from(AppAsset))
            online_devices = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.last_active_at >= threshold_time)
            )

            # 今日数据
            today_push_tasks = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= today_start)
            )
            today_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(AdminOperationLog.created_at >= today_start)
            )
            today_uploads = await db.scalar(
                select(func.count())
                .select_from(AppAsset)
                .where(AppAsset.created_at >= today_start)
            )

            # 最近7天趋势数据
            trend_data = []
            for i in range(7):
                date = datetime.utcnow() - timedelta(days=7-i-1)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

                operations = await db.scalar(
                    select(func.count())
                    .select_from(AdminOperationLog)
                    .where(
                        AdminOperationLog.created_at >= date_start,
                        AdminOperationLog.created_at <= date_end
                    )
                )

                push_tasks = await db.scalar(
                    select(func.count())
                    .select_from(ConfigPushTask)
                    .where(
                        ConfigPushTask.created_at >= date_start,
                        ConfigPushTask.created_at <= date_end
                    )
                )

                uploads = await db.scalar(
                    select(func.count())
                    .select_from(AppAsset)
                    .where(
                        AppAsset.created_at >= date_start,
                        AppAsset.created_at <= date_end
                    )
                )

                trend_data.append({
                    'date': date_start.strftime('%m-%d'),
                    'operations': operations or 0,
                    'push_tasks': push_tasks or 0,
                    'uploads': uploads or 0
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'overview': {
                        'total_apps': total_apps or 0,
                        'total_devices': total_devices or 0,
                        'total_assets': total_assets or 0,
                        'online_devices': online_devices or 0,
                        'online_rate': round((online_devices or 0) / (total_devices or 1) * 100, 2)
                    },
                    'today': {
                        'push_tasks': today_push_tasks or 0,
                        'operations': today_operations or 0,
                        'uploads': today_uploads or 0
                    },
                    'trend': trend_data
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取仪表板数据失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取仪表板数据失败: {str(e)}'
        }), 500
