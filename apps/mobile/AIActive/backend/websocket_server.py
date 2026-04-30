"""
WebSocket 推送服务
为Android客户端提供实时配置推送功能
"""
import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Set, Optional
from flask import request
from flask_sock import Sock
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入 JWT 验证辅助模块
# 添加路径以导入共享模块
ws_helper_path = Path(__file__).parent.parent / "md" / "server" / "websocket"
import sys
if str(ws_helper_path) not in sys.path:
    sys.path.insert(0, str(ws_helper_path))

try:
    from jwt_helper import verify_device_token, get_user_from_token
    JWT_AVAILABLE = True
except ImportError:
    # 如果共享模块不可用，定义备用函数
    JWT_AVAILABLE = False
    logger.warning("JWT helper module not available, using simplified verification")

    def verify_device_token(token: str, device_id: str) -> bool:
        if not token or not device_id:
            return False
        # 临时 Token 格式: temp_token_<device_id>
        if token.startswith('temp_token_'):
            return token == f'temp_token_{device_id}'
        # 生产环境应该验证 JWT，这里简化处理
        return len(token) > 20

    def get_user_from_token(token: str) -> Optional[Dict]:
        return None

# 存储活跃的WebSocket连接
# 结构: {device_id: {'ws': Sock, 'sid': str, 'app_id': int}}
active_connections: Dict[str, dict] = {}

# 存储会话ID映射
# 结构: {sid: device_id}
sid_to_device: Dict[str, str] = {}


class WebSocketServer:
    """WebSocket服务器"""

    def __init__(self, app=None):
        self.sock = Sock(app)
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """初始化WebSocket服务器"""
        self.sock = Sock(app)
        self.sock.route('/ws')(self.handle_connection)
        logger.info("WebSocket路由已注册: /ws")

    def handle_connection(self, ws):
        """
        处理WebSocket连接
        URL参数: device_id, token
        """
        try:
            # 获取连接参数
            device_id = request.args.get('device_id')
            token = request.args.get('token', '')

            if not device_id:
                logger.warning("连接被拒绝: 缺少device_id参数")
                ws.close(1008, "Missing device_id")
                return

            # 验证token（简化版本，实际应该验证JWT）
            if not self._validate_token(token, device_id):
                logger.warning(f"连接被拒绝: 无效的token (device_id={device_id})")
                ws.close(1008, "Invalid token")
                return

            # 生成会话ID
            sid = self._generate_sid()

            # 注册连接
            active_connections[device_id] = {
                'ws': ws,
                'sid': sid,
                'connected_at': datetime.now(),
                'app_id': 1  # TODO: 从token解析app_id
            }
            sid_to_device[sid] = device_id

            logger.info(f"WebSocket连接已建立: device_id={device_id}, sid={sid}")

            # 发送连接确认消息
            self._send_connected(ws, sid)

            # 处理消息循环
            for message in ws:
                try:
                    self._handle_message(ws, device_id, message)
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")

        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")

        finally:
            # 清理连接
            self._cleanup_connection(device_id, sid)

    def _validate_token(self, token: str, device_id: str) -> bool:
        """
        验证访问令牌
        使用 JWT helper 进行完整验证
        """
        if not token:
            return False

        # 使用共享的 JWT 验证模块
        return verify_device_token(token, device_id)

    def _generate_sid(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())

    def _send_connected(self, ws, sid: str):
        """发送连接确认消息"""
        message = {
            "connected": {
                "sid": sid,
                "server_time": datetime.now().isoformat()
            }
        }
        ws.send(json.dumps(message))

    def _handle_message(self, ws, device_id: str, message: str):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            msg_type = list(data.keys())[0] if data else None

            if msg_type == "heartbeat":
                # 心跳消息
                self._handle_heartbeat(ws, data[msg_type])
            elif msg_type == "device_status":
                # 设备状态上报
                self._handle_device_status(device_id, data[msg_type])
            elif msg_type == "config_ack":
                # 配置更新确认
                self._handle_config_ack(device_id, data[msg_type])
            else:
                logger.warning(f"未知消息类型: {msg_type}")

        except json.JSONDecodeError:
            logger.warning(f"无效的JSON消息: {message}")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")

    def _handle_heartbeat(self, ws, data: dict):
        """处理心跳消息"""
        # 回复心跳确认
        response = {
            "heartbeat_ack": {
                "server_time": datetime.now().isoformat()
            }
        }
        ws.send(json.dumps(response))

    def _handle_device_status(self, device_id: str, data: dict):
        """处理设备状态上报"""
        logger.info(f"收到设备状态: device_id={device_id}, status={data}")

        # TODO: 存储到数据库
        # await DeviceStatus.create(device_id=device_id, status=data)

    def _handle_config_ack(self, device_id: str, data: dict):
        """处理配置更新确认"""
        push_id = data.get('push_id')
        status = data.get('status')
        message = data.get('message')
        received_files = data.get('received_files', [])
        failed_files = data.get('failed_files', [])

        logger.info(f"配置更新确认: device_id={device_id}, push_id={push_id}, status={status}")

        # TODO: 更新推送任务状态到数据库
        # await update_push_task_status(push_id, device_id, status, ...)

    def _cleanup_connection(self, device_id: str, sid: str):
        """清理断开的连接"""
        if device_id in active_connections:
            del active_connections[device_id]
        if sid in sid_to_device:
            del sid_to_device[sid]

        logger.info(f"WebSocket连接已清理: device_id={device_id}, sid={sid}")

    # ==================== 推送方法 ====================

    def broadcast_to_all(self, message: dict):
        """广播消息到所有连接的设备"""
        message_str = json.dumps(message)
        count = 0

        for device_id, conn in list(active_connections.items()):
            try:
                conn['ws'].send(message_str)
                count += 1
            except Exception as e:
                logger.error(f"广播到设备 {device_id} 失败: {e}")
                # 移除失效的连接
                self._cleanup_connection(device_id, conn['sid'])

        logger.info(f"广播消息已发送到 {count} 个设备")
        return count

    def send_to_device(self, device_id: str, message: dict) -> bool:
        """发送消息到指定设备"""
        if device_id not in active_connections:
            logger.warning(f"设备 {device_id} 未连接")
            return False

        try:
            message_str = json.dumps(message)
            active_connections[device_id]['ws'].send(message_str)
            logger.info(f"消息已发送到设备: {device_id}")
            return True
        except Exception as e:
            logger.error(f"发送消息到设备 {device_id} 失败: {e}")
            # 移除失效的连接
            self._cleanup_connection(device_id, active_connections[device_id]['sid'])
            return False

    def send_to_devices(self, device_ids: list, message: dict) -> dict:
        """发送消息到多个设备"""
        results = {
            'success': [],
            'failed': []
        }

        for device_id in device_ids:
            if self.send_to_device(device_id, message):
                results['success'].append(device_id)
            else:
                results['failed'].append(device_id)

        return results

    def push_config_update(self, device_ids: list, push_id: str, version: str,
                          version_code: int, force_update: bool,
                          release_notes: str, files: list) -> dict:
        """
        推送配置更新

        Args:
            device_ids: 设备ID列表
            push_id: 推送任务ID
            version: 版本号
            version_code: 版本代码
            force_update: 是否强制更新
            release_notes: 更新说明
            files: 文件列表

        Returns:
            推送结果
        """
        message = {
            "config_update": {
                "push_id": push_id,
                "version": version,
                "version_code": version_code,
                "force_update": force_update,
                "release_notes": release_notes,
                "files": files
            }
        }

        return self.send_to_devices(device_ids, message)

    def get_connected_devices(self) -> list:
        """获取所有在线设备列表"""
        devices = []
        for device_id, conn in active_connections.items():
            devices.append({
                'device_id': device_id,
                'sid': conn['sid'],
                'connected_at': conn['connected_at'].isoformat(),
                'app_id': conn['app_id']
            })
        return devices

    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(active_connections)


# 创建全局WebSocket服务器实例
websocket_server = WebSocketServer()


def init_websocket(app):
    """初始化WebSocket服务"""
    websocket_server.init_app(app)
    return websocket_server
