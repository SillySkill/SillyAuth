# -*- coding: utf-8 -*-
"""
WebSocket 推送服务器
使用 Flask-SocketIO 实现设备连接、配置推送、心跳检测和消息确认
"""

import os
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms, disconnect
from services.push_service import PushService
from common.libs.log.LogService import LogService
import json
import logging
from datetime import datetime

# 导入 JWT 验证辅助模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "websocket"))
from jwt_helper import verify_device_token, get_user_from_token

# 配置日志
logger = logging.getLogger(__name__)

# CORS 配置 - 从环境变量读取，默认限制本地开发
ALLOWED_ORIGINS = os.getenv(
    "WS_CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8080,https://sillymd.com"
).split(",")

socketio = SocketIO(
    cors_allowed_origins=ALLOWED_ORIGINS,
    async_mode='threading',
    logger=True,
    engineio_logger=False
)

# 设备连接存储: {sid: {device_id, connect_time, last_heartbeat}}
connected_devices = {}

# 推送服务实例
push_service = None


def init_push_service(service):
    """初始化推送服务"""
    global push_service
    push_service = service
    logger.info("推送服务已初始化")


@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    from flask import session
    sid = request.sid

    logger.info(f"客户端连接: sid={sid}")

    # 获取认证信息
    device_id = request.args.get('device_id')
    token = request.args.get('token')

    if not device_id or not token:
        logger.warning(f"连接被拒绝: 缺少认证信息 (sid={sid})")
        emit('error', {'code': 401, 'message': '缺少认证信息'})
        disconnect()
        return False

    # 验证 token 有效性
    if not verify_device_token(token, device_id):
        logger.warning(f"连接被拒绝: Token 无效 (sid={sid}, device_id={device_id})")
        emit('error', {'code': 403, 'message': 'Token 无效或已过期'})
        disconnect()
        return False

    # 记录设备连接
    connected_devices[sid] = {
        'device_id': device_id,
        'token': token,
        'connect_time': datetime.now(),
        'last_heartbeat': datetime.now()
    }

    # 加入设备专属房间
    room = f"device_{device_id}"
    join_room(room)

    # 通知连接成功
    emit('connected', {
        'sid': sid,
        'device_id': device_id,
        'server_time': datetime.now().isoformat()
    })

    # 如果有待推送的配置，立即推送
    if push_service:
        pending_push = push_service.get_pending_push(device_id)
        if pending_push:
            logger.info(f"发现待推送配置，立即推送到设备: {device_id}")
            _send_config_push(sid, device_id, pending_push)

    logger.info(f"设备已连接: device_id={device_id}, sid={sid}, 当前连接数={len(connected_devices)}")
    return True


@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    sid = request.sid
    device_info = connected_devices.get(sid)

    if device_info:
        device_id = device_info['device_id']
        room = f"device_{device_id}"
        leave_room(room)

        logger.info(f"设备断开连接: device_id={device_id}, sid={sid}, 连接时长={(datetime.now() - device_info['connect_time']).seconds}秒")

        # 从连接列表中移除
        del connected_devices[sid]

        # 通知推送服务
        if push_service:
            push_service.on_device_disconnected(device_id)
    else:
        logger.warning(f"未知设备断开连接: sid={sid}")


@socketio.on('heartbeat')
def handle_heartbeat(data):
    """处理心跳包"""
    sid = request.sid
    device_info = connected_devices.get(sid)

    if device_info:
        device_info['last_heartbeat'] = datetime.now()

        # 响应心跳
        emit('heartbeat_ack', {
            'server_time': datetime.now().isoformat(),
            'device_time': data.get('client_time')
        })

        logger.debug(f"收到心跳: device_id={device_info['device_id']}, sid={sid}")
    else:
        logger.warning(f"心跳来自未知设备: sid={sid}")


@socketio.on('config_ack')
def handle_config_ack(data):
    """处理配置更新确认"""
    sid = request.sid
    device_info = connected_devices.get(sid)

    if not device_info:
        logger.warning(f"配置确认来自未知设备: sid={sid}")
        return

    device_id = device_info['device_id']
    push_id = data.get('push_id')
    status = data.get('status')  # success, failed
    message = data.get('message', '')
    received_files = data.get('received_files', [])
    failed_files = data.get('failed_files', [])

    logger.info(f"收到配置确认: device_id={device_id}, push_id={push_id}, status={status}")

    # 通知推送服务更新状态
    if push_service:
        push_service.on_config_ack(device_id, push_id, status, message, received_files, failed_files)

    # 响应确认
    emit('config_ack_received', {
        'push_id': push_id,
        'status': 'acknowledged'
    })


@socketio.on('device_status')
def handle_device_status(data):
    """处理设备状态上报"""
    sid = request.sid
    device_info = connected_devices.get(sid)

    if not device_info:
        logger.warning(f"设备状态来自未知设备: sid={sid}")
        return

    device_id = device_info['device_id']
    status_info = {
        'battery': data.get('battery'),
        'storage': data.get('storage'),
        'network_type': data.get('network_type'),
        'app_version': data.get('app_version'),
        'config_version': data.get('config_version'),
        'timestamp': datetime.now().isoformat()
    }

    logger.info(f"设备状态上报: device_id={device_id}, status={status_info}")

    # 保存设备状态到数据库（如果需要）
    if push_service:
        push_service.on_device_status(device_id, status_info)


@socketio.on('error')
def handle_error(data):
    """处理客户端错误上报"""
    sid = request.sid
    device_info = connected_devices.get(sid)

    if device_info:
        device_id = device_info['device_id']
        error_msg = data.get('error', 'Unknown error')
        logger.error(f"设备错误: device_id={device_id}, error={error_msg}")

        # 通知推送服务
        if push_service:
            push_service.on_device_error(device_id, error_msg)


def broadcast_to_all(event_name, data):
    """向所有连接的设备广播消息"""
    emit(event_name, data, broadcast=True)
    logger.info(f"广播消息: event={event_name}, 连接数={len(connected_devices)}")


def send_to_device(device_id, event_name, data):
    """向指定设备发送消息"""
    room = f"device_{device_id}"
    socketio.emit(event_name, data, room=room)
    logger.info(f"发送消息到设备: device_id={device_id}, event={event_name}")


def send_to_sid(sid, event_name, data):
    """向指定连接发送消息"""
    socketio.emit(event_name, data, room=sid)
    logger.debug(f"发送消息到 sid: sid={sid}, event={event_name}")


def _send_config_push(sid, device_id, push_info):
    """发送配置推送（内部方法）"""
    try:
        push_data = {
            'push_id': push_info.get('push_id'),
            'version': push_info.get('version'),
            'version_code': push_info.get('version_code'),
            'force_update': push_info.get('force_update', False),
            'release_notes': push_info.get('release_notes', ''),
            'files': push_info.get('files', []),
            'server_time': datetime.now().isoformat()
        }

        send_to_sid(sid, 'config_update', push_data)
        logger.info(f"配置推送已发送: device_id={device_id}, push_id={push_info.get('push_id')}")
        return True
    except Exception as e:
        logger.error(f"发送配置推送失败: device_id={device_id}, error={e}")
        return False


def get_connected_devices():
    """获取已连接的设备列表"""
    devices = []
    for sid, info in connected_devices.items():
        devices.append({
            'sid': sid,
            'device_id': info['device_id'],
            'connect_time': info['connect_time'].isoformat(),
            'last_heartbeat': info['last_heartbeat'].isoformat()
        })
    return devices


def get_device_count():
    """获取当前连接的设备数量"""
    return len(connected_devices)


def is_device_connected(device_id):
    """检查设备是否在线"""
    for info in connected_devices.values():
        if info['device_id'] == device_id:
            return True
    return False


def start_heartbeat_check():
    """启动心跳检查（定期检查超时设备）"""
    def check_heartbeat():
        from threading import Thread
        import time

        HEARTBEAT_TIMEOUT = 60  # 60秒心跳超时

        while True:
            try:
                current_time = datetime.now()
                timeout_sids = []

                for sid, info in connected_devices.items():
                    last_heartbeat = info['last_heartbeat']
                    if (current_time - last_heartbeat).seconds > HEARTBEAT_TIMEOUT:
                        timeout_sids.append(sid)

                # 断开超时连接
                for sid in timeout_sids:
                    device_id = connected_devices[sid]['device_id']
                    logger.warning(f"设备心跳超时，断开连接: device_id={device_id}, sid={sid}")
                    socketio.disconnect(sid)

                time.sleep(30)  # 每30秒检查一次

            except Exception as e:
                logger.error(f"心跳检查异常: {e}")

    thread = Thread(target=check_heartbeat, daemon=True)
    thread.start()
    logger.info("心跳检查已启动")
