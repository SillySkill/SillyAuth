# -*- coding: utf-8 -*-
"""
SillyMD → OpenClaw 消息桥接器

功能：
1. 连接到 webhook.sillymd.com (设备名: sillyHei) 接收企微消息
2. 连接到 OpenClaw 本地 WebSocket (ws://127.0.0.1:18789/)
3. 实时转发消息
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

# 修复 Windows 编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# SillyMD WebSocket 配置
SILLYMD_WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE4MDA1ODMsImV4cCI6MTgwMzMzNjU4M30.nrZqCDtC3Rz8D0QJLJGEFhgY9sgSyUAZWpmjVqRlHko"
SILLYMD_DEVICE = "sillyHei"

# OpenClaw WebSocket 配置
OPENCLAW_WS_URL = "ws://127.0.0.1:18789/"


class MessageBridge:
    """消息桥接器"""

    def __init__(self):
        self.sillymd_ws = None
        self.openclaw_ws = None
        self.sillymd_connected = False
        self.openclaw_connected = False
        self.message_count = 0
        self.forwarded_count = 0

    async def connect_to_sillymd(self):
        """连接到 SillyMD 服务器"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在连接到 SillyMD...")
        print(f"    URL: {SILLYMD_WS_URL[:50]}...")
        print(f"    设备名: {SILLYMD_DEVICE}")

        try:
            self.sillymd_ws = await asyncio.wait_for(
                websockets.connect(SILLYMD_WS_URL, ping_interval=20, ping_timeout=10),
                timeout=10
            )

            # 发送设备绑定消息
            await self.sillymd_ws.send(json.dumps({
                "type": "bind",
                "device_name": SILLYMD_DEVICE
            }))

            # 接收绑定确认
            msg = await self.sillymd_ws.recv()
            data = json.loads(msg)

            if data.get("type") == "bound":
                self.sillymd_connected = True
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ SillyMD 连接成功!")
                print(f"    设备ID: {data.get('device_id')}")
                return True

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ SillyMD 连接失败: {e}")
            return False

    async def connect_to_openclaw(self):
        """连接到 OpenClaw 本地 WebSocket"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在连接到 OpenClaw...")
        print(f"    URL: {OPENCLAW_WS_URL}")

        try:
            self.openclaw_ws = await asyncio.wait_for(
                websockets.connect(OPENCLAW_WS_URL),
                timeout=5
            )
            self.openclaw_connected = True
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ OpenClaw 连接成功!")
            return True

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenClaw 连接失败: {e}")
            print(f"    请确保 OpenClaw 正在运行并监听 ws://127.0.0.1:18789/")
            return False

    def format_message(self, data: dict) -> dict:
        """格式化消息以适配 OpenClaw"""
        # 提取企微回复内容
        if data.get("type") == "webhook":
            # SillyMD 格式
            wechat_data = data.get("data", {})

            if wechat_data.get("type") == "wechat_reply":
                # 转换为 OpenClaw 格式
                return {
                    "type": "wechat_message",
                    "source": "SillyMD",
                    "data": {
                        "from_user": wechat_data.get("from_user"),
                        "content": wechat_data.get("content"),
                        "msg_type": wechat_data.get("msg_type"),
                        "timestamp": wechat_data.get("timestamp")
                    }
                }

        # 其他消息类型直接转发
        return data

    async def forward_to_openclaw(self, message: dict):
        """转发消息到 OpenClaw"""
        if not self.openclaw_connected:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  OpenClaw 未连接，跳过转发")
            return False

        try:
            await self.openclaw_ws.send(json.dumps(message))
            self.forwarded_count += 1
            return True

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 转发失败: {e}")
            return False

    async def listen_sillymd(self):
        """监听 SillyMD 消息并转发到 OpenClaw"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎧 开始监听 SillyMD 消息...")
        print("="*70)

        try:
            while True:
                try:
                    message = await asyncio.wait_for(self.sillymd_ws.recv(), timeout=30.0)
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg_type = data.get("type")

                    if msg_type == "pong":
                        continue

                    elif msg_type == "ping":
                        await self.sillymd_ws.send(json.dumps({"type": "pong"}))

                    elif data.get("data", {}).get("type") == "wechat_reply":
                        # 企业微信回复消息
                        self.message_count += 1
                        wechat = data["data"]

                        print()
                        print("="*70)
                        print(f"[{timestamp}] 📨 收到企业微信回复 (#{self.message_count})")
                        print("="*70)
                        print(f"发送者: {wechat.get('from_user')}")
                        print(f"内容: {wechat.get('content')}")
                        print(f"时间: {wechat.get('timestamp')}")
                        print("="*70)
                        print()

                        # 转发到 OpenClaw
                        formatted = self.format_message(data)
                        success = await self.forward_to_openclaw(formatted)

                        if success:
                            print(f"[{timestamp}] ✅ 已转发到 OpenClaw (总计: {self.forwarded_count})")
                        else:
                            print(f"[{timestamp}] ❌ 转发失败")

                    elif msg_type == "ack":
                        # ACK 响应
                        pass

                    else:
                        print(f"[{timestamp}] 📩 其他消息: {msg_type}")

                except asyncio.TimeoutError:
                    # 超时，发送心跳
                    await self.sillymd_ws.send(json.dumps({"type": "ping"}))

        except websockets.exceptions.ConnectionClosed:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ SillyMD 连接已关闭")
            self.sillymd_connected = False

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 监听错误: {e}")

    async def listen_openclaw(self):
        """监听 OpenClaw 的响应（可选）"""
        try:
            while True:
                message = await self.openclaw_ws.recv()
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ← OpenClaw: {message[:100]}")

        except websockets.exceptions.ConnectionClosed:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenClaw 连接已关闭")
            self.openclaw_connected = False

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenClaw 监听错误: {e}")

    async def run(self):
        """启动桥接器"""
        print("="*70)
        print("🌉 SillyMD → OpenClaw 消息桥接器")
        print("="*70)
        print()

        # 连接到 SillyMD
        if not await self.connect_to_sillymd():
            print()
            print("❌ 无法连接到 SillyMD，退出...")
            return

        print()

        # 连接到 OpenClaw
        if not await self.connect_to_openclaw():
            print()
            print("⚠️  OpenClaw 未连接，将只监听 SillyMD 消息...")
            print()

        print()
        print("="*70)
        print("📊 桥接器状态:")
        print(f"  SillyMD:   {'✅ 已连接' if self.sillymd_connected else '❌ 未连接'}")
        print(f"  OpenClaw:  {'✅ 已连接' if self.openclaw_connected else '❌ 未连接'}")
        print("="*70)
        print()

        # 启动监听任务
        tasks = [self.listen_sillymd()]

        if self.openclaw_connected:
            tasks.append(self.listen_openclaw())

        # 并发运行
        await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    """主函数"""
    bridge = MessageBridge()

    while True:
        try:
            await bridge.run()

        except KeyboardInterrupt:
            print()
            print()
            print("="*70)
            print("📊 统计信息:")
            print(f"  收到消息: {bridge.message_count} 条")
            print(f"  转发消息: {bridge.forwarded_count} 条")
            print("="*70)
            print()
            print("👋 桥接器已停止")
            break

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            print("🔄 5秒后重新连接...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    print()
    asyncio.run(main())
