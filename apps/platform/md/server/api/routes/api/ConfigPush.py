# -*- coding: utf-8 -*-
"""
配置推送 API 接口
提供批量推送、状态查询、取消推送等功能
"""

from flask import request, jsonify
from web.controllers.api import api_blueprint
from services.push_service import PushService
from websocket.push_server import get_connected_devices, get_device_count, is_device_connected
from common.libs.log.LogService import LogService
import logging

logger = logging.getLogger(__name__)


# 获取推送服务实例（需要在应用启动时注入）
_push_service = None


def init_push_service(service):
    """初始化推送服务"""
    global _push_service
    _push_service = service


@api_blueprint.route("/push/config", methods=["POST"])
def create_push_task():
    """
    创建配置推送任务

    请求体:
    {
        "version": "v1.2.0",
        "version_code": 120,
        "force_update": false,
        "release_notes": "更新说明",
        "files": [
            {
                "path": "config.json",
                "size": 1024,
                "md5": "abc123...",
                "url": "/api/config/file?path=config.json",
                "compressed": false,
                "essential": true
            }
        ],
        "target_devices": ["device_001", "device_002"],  // 可选
        "target_groups": ["group_001"]  // 可选
    }

    响应:
    {
        "code": 200,
        "message": "success",
        "data": {
            "task_id": "uuid",
            "status": "pending"
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"code": 400, "message": "请求体为空"}), 400

        # 验证必需字段
        required_fields = ['version', 'version_code', 'files']
        for field in required_fields:
            if field not in data:
                return jsonify({"code": 400, "message": f"缺少必需字段: {field}"}), 400

        if not isinstance(data['files'], list) or len(data['files']) == 0:
            return jsonify({"code": 400, "message": "files 必须是非空数组"}), 400

        # 创建推送任务
        task_id = _push_service.create_push_task(
            config_version=data,
            target_devices=data.get('target_devices'),
            target_groups=data.get('target_groups')
        )

        return jsonify({
            "code": 200,
            "message": "推送任务创建成功",
            "data": {
                "task_id": task_id,
                "status": "pending"
            }
        })

    except Exception as e:
        logger.error(f"创建推送任务失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/<task_id>/start", methods=["POST"])
def start_push_task(task_id):
    """
    启动推送任务

    响应:
    {
        "code": 200,
        "message": "任务已启动，目标设备数: 10",
        "data": {
            "task_id": "uuid",
            "status": "in_progress",
            "total_devices": 10
        }
    }
    """
    try:
        if not _push_service:
            return jsonify({"code": 500, "message": "推送服务未初始化"}), 500

        success, message = _push_service.start_push_task(task_id)

        if success:
            task_info = _push_service.get_task_status(task_id)
            return jsonify({
                "code": 200,
                "message": message,
                "data": {
                    "task_id": task_id,
                    "status": task_info.get('status'),
                    "total_devices": task_info.get('total_devices', 0)
                }
            })
        else:
            return jsonify({"code": 400, "message": message}), 400

    except Exception as e:
        logger.error(f"启动推送任务失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/<task_id>", methods=["GET"])
def get_push_status(task_id):
    """
    获取推送任务状态

    响应:
    {
        "code": 200,
        "message": "success",
        "data": {
            "task_id": "uuid",
            "version": "v1.2.0",
            "version_code": 120,
            "status": "in_progress",
            "total_devices": 10,
            "success_devices": 5,
            "failed_devices": 1,
            "pending_devices": ["device_003"],
            "created_at": "2026-02-06T10:00:00",
            "started_at": "2026-02-06T10:01:00",
            "completed_at": null
        }
    }
    """
    try:
        if not _push_service:
            return jsonify({"code": 500, "message": "推送服务未初始化"}), 500

        task_info = _push_service.get_task_status(task_id)

        if not task_info:
            return jsonify({"code": 404, "message": "任务不存在"}), 404

        return jsonify({
            "code": 200,
            "message": "success",
            "data": task_info
        })

    except Exception as e:
        logger.error(f"获取推送状态失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/<task_id>", methods=["DELETE"])
def cancel_push_task(task_id):
    """
    取消推送任务

    响应:
    {
        "code": 200,
        "message": "任务已取消",
        "data": {
            "task_id": "uuid",
            "status": "cancelled"
        }
    }
    """
    try:
        if not _push_service:
            return jsonify({"code": 500, "message": "推送服务未初始化"}), 500

        success, message = _push_service.cancel_push_task(task_id)

        if success:
            return jsonify({
                "code": 200,
                "message": message,
                "data": {
                    "task_id": task_id,
                    "status": "cancelled"
                }
            })
        else:
            return jsonify({"code": 400, "message": message}), 400

    except Exception as e:
        logger.error(f"取消推送任务失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/tasks", methods=["GET"])
def list_push_tasks():
    """
    获取所有推送任务列表

    查询参数:
    - status: 过滤状态 (pending, in_progress, completed, cancelled)
    - limit: 返回数量限制（默认50）
    - offset: 偏移量

    响应:
    {
        "code": 200,
        "message": "success",
        "data": {
            "total": 100,
            "tasks": [...]
        }
    }
    """
    try:
        if not _push_service:
            return jsonify({"code": 500, "message": "推送服务未初始化"}), 500

        status_filter = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        all_tasks = _push_service.get_all_tasks()

        # 过滤
        if status_filter:
            all_tasks = [t for t in all_tasks if t['status'] == status_filter]

        # 分页
        total = len(all_tasks)
        tasks = all_tasks[offset:offset + limit]

        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "total": total,
                "tasks": tasks
            }
        })

    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/devices/online", methods=["GET"])
def get_online_devices():
    """
    获取在线设备列表

    响应:
    {
        "code": 200,
        "message": "success",
        "data": {
            "total": 5,
            "devices": [
                {
                    "sid": "abc123",
                    "device_id": "device_001",
                    "connect_time": "2026-02-06T10:00:00",
                    "last_heartbeat": "2026-02-06T10:05:00"
                }
            ]
        }
    }
    """
    try:
        devices = get_connected_devices()

        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "total": len(devices),
                "devices": devices
            }
        })

    except Exception as e:
        logger.error(f"获取在线设备失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/devices/<device_id>/status", methods=["GET"])
def get_device_status(device_id):
    """
    获取指定设备的状态

    响应:
    {
        "code": 200,
        "message": "success",
        "data": {
            "device_id": "device_001",
            "online": true,
            "connect_time": "2026-02-06T10:00:00"
        }
    }
    """
    try:
        online = is_device_connected(device_id)

        data = {
            "device_id": device_id,
            "online": online
        }

        if online:
            # 获取连接详情
            devices = get_connected_devices()
            for device in devices:
                if device['device_id'] == device_id:
                    data['connect_time'] = device['connect_time']
                    data['last_heartbeat'] = device['last_heartbeat']
                    break

        return jsonify({
            "code": 200,
            "message": "success",
            "data": data
        })

    except Exception as e:
        logger.error(f"获取设备状态失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@api_blueprint.route("/push/broadcast", methods=["POST"])
def broadcast_to_all():
    """
    向所有在线设备广播消息

    请求体:
    {
        "event": "config_update",
        "data": {
            "message": "系统维护通知"
        }
    }

    响应:
    {
        "code": 200,
        "message": "广播成功",
        "data": {
            "device_count": 10
        }
    }
    """
    try:
        from websocket.push_server import broadcast_to_all

        data = request.get_json()
        event = data.get('event', 'notification')
        message_data = data.get('data', {})

        device_count = get_device_count()
        broadcast_to_all(event, message_data)

        return jsonify({
            "code": 200,
            "message": "广播成功",
            "data": {
                "device_count": device_count
            }
        })

    except Exception as e:
        logger.error(f"广播消息失败: {e}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500
