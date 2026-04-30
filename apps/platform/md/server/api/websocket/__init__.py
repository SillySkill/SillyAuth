# -*- coding: utf-8 -*-
"""
WebSocket 推送系统集成

在应用启动时初始化 WebSocket 服务器和推送服务
"""

from websocket.push_server import socketio, init_push_service, start_heartbeat_check
from services.push_service import PushService
from web.controllers.api.ConfigPush import init_push_service as api_init_push_service


def init_push_system(app, db):
    """
    初始化推送系统

    Args:
        app: Flask 应用实例
        db: SQLAlchemy 数据库实例

    Returns:
        socketio: SocketIO 实例
    """
    # 创建推送服务
    push_service = PushService(db)

    # 初始化 WebSocket 服务器
    init_push_service(push_service)

    # 初始化 API 接口
    api_init_push_service(push_service)

    # 初始化 SocketIO
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    # 启动心跳检查
    start_heartbeat_check()

    print("[WebSocket Push System] 推送系统初始化完成")
    print("[WebSocket Push System] SocketIO 已绑定到应用")

    return socketio
