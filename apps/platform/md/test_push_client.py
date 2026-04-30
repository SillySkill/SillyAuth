#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebSocket 推送测试客户端
用于测试和调试 WebSocket 服务器
"""

import asyncio
import websockets
import json
import time
from datetime import datetime


class PushTestClient:
    """推送测试客户端"""

    def __init__(self, url, device_id, token):
        self.url = url
        self.device_id = device_id
        self.token = token
        self.websocket = None
        self.connected = False

    async def connect(self):
        """连接到服务器"""
        # 构建 WebSocket URL
        ws_url = f"{self.url}?device_id={self.device_id}&token={self.token}"

        print(f"正在连接到: {ws_url}")

        try:
            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            print("✓ 连接成功")

            # 启动心跳和消息监听
            await asyncio.gather(
                self.send_heartbeat(),
                self.listen_messages()
            )

        except Exception as e:
            print(f"✗ 连接失败: {e}")
            self.connected = False

    async def listen_messages(self):
        """监听服务器消息"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("✗ 连接已关闭")
            self.connected = False
        except Exception as e:
            print(f"✗ 接收消息错误: {e}")

    async def handle_message(self, message):
        """处理收到的消息"""
        try:
            data = json.loads(message)
            msg_type = list(data.keys())[0]
            msg_content = data[msg_type]

            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 收到消息: {msg_type}")

            if msg_type == 'connected':
                print(f"  - Session ID: {msg_content.get('sid')}")
                print(f"  - Device ID: {msg_content.get('device_id')}")
                print(f"  - Server Time: {msg_content.get('server_time')}")

            elif msg_type == 'config_update':
                print(f"  - Push ID: {msg_content.get('push_id')}")
                print(f"  - Version: {msg_content.get('version')} ({msg_content.get('version_code')})")
                print(f"  - Force Update: {msg_content.get('force_update')}")
                print(f"  - Files: {len(msg_content.get('files', []))} 个文件")

                # 自动确认
                await self.send_config_ack(
                    msg_content.get('push_id'),
                    success=True,
                    message="测试：自动确认"
                )

            elif msg_type == 'heartbeat_ack':
                server_time = msg_content.get('server_time')
                print(f"  - Server Time: {server_time}")

            elif msg_type == 'error':
                print(f"  ✗ Error: {msg_content.get('code')} - {msg_content.get('message')}")

        except json.JSONDecodeError:
            print(f"  无法解析消息: {message}")
        except Exception as e:
            print(f"  处理消息错误: {e}")

    async def send_heartbeat(self):
        """发送心跳"""
        while self.connected:
            try:
                heartbeat_data = {
                    "client_time": int(time.time() * 1000)
                }
                message = json.dumps({"heartbeat": heartbeat_data})
                await self.websocket.send(message)

                # 每30秒发送一次心跳
                await asyncio.sleep(30)

            except Exception as e:
                print(f"✗ 发送心跳失败: {e}")
                break

    async def send_config_ack(self, push_id, success=True, message="",
                              received_files=None, failed_files=None):
        """发送配置确认"""
        try:
            ack_data = {
                "push_id": push_id,
                "status": "success" if success else "failed",
                "message": message,
                "received_files": received_files or [],
                "failed_files": failed_files or []
            }
            message = json.dumps({"config_ack": ack_data})
            await self.websocket.send(message)

            print(f"✓ 已发送配置确认: push_id={push_id}, status={ack_data['status']}")

        except Exception as e:
            print(f"✗ 发送确认失败: {e}")

    async def send_device_status(self):
        """上报设备状态"""
        try:
            status_data = {
                "battery": 85,
                "storage": 1024,
                "network_type": "wifi",
                "app_version": "1.0.0",
                "config_version": "v1.0.0"
            }
            message = json.dumps({"device_status": status_data})
            await self.websocket.send(message)

            print("✓ 已上报设备状态")

        except Exception as e:
            print(f"✗ 上报状态失败: {e}")

    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("✓ 连接已关闭")


async def main():
    """主函数"""
    # 配置
    SERVER_URL = "ws://localhost:5000/ws"
    DEVICE_ID = "test_device_001"
    TOKEN = "test_token"

    print("=" * 60)
    print("WebSocket 推送测试客户端")
    print("=" * 60)

    # 创建客户端
    client = PushTestClient(SERVER_URL, DEVICE_ID, TOKEN)

    try:
        # 连接到服务器
        await client.connect()

    except KeyboardInterrupt:
        print("\n\n正在退出...")
    finally:
        await client.close()


async def test_send_message():
    """测试发送消息"""
    SERVER_URL = "ws://localhost:5000/ws"
    DEVICE_ID = "test_device_001"
    TOKEN = "test_token"

    client = PushTestClient(SERVER_URL, DEVICE_ID, TOKEN)

    try:
        await client.connect()

        # 等待连接建立
        await asyncio.sleep(2)

        # 上报设备状态
        await client.send_device_status()

        # 保持连接，等待消息
        await asyncio.sleep(60)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    print("\n选择测试模式:")
    print("1. 持续连接监听模式")
    print("2. 发送消息测试模式")

    choice = input("\n请输入选择 (1/2): ").strip()

    if choice == "2":
        asyncio.run(test_send_message())
    else:
        asyncio.run(main())
