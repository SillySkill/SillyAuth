# -*- coding: utf-8 -*-
"""
检查 OpenClaw 连接状态
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# JWT Token
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE4MDA1ODMsImV4cCI6MTgwMzMzNjU4M30.nrZqCDtC3Rz8D0QJLJGEFhgY9sgSyUAZWpmjVqRlHko"
WS_URL = "wss://webhook.sillymd.com/ws"
DEVICE_NAME = "sillyHei"  # 尝试这个设备名

async def test_connection():
    """测试 OpenClaw 连接"""
    uri = f"{WS_URL}?token={JWT_TOKEN}"

    print("=" * 60)
    print("OpenClaw 连接检查")
    print("=" * 60)
    print(f"WebSocket URL: {WS_URL}")
    print(f"设备名称: {DEVICE_NAME}")
    print(f"User ID: 33")
    print("=" * 60)
    print()

    try:
        async with websockets.connect(uri) as ws:
            print("✅ WebSocket 连接成功！")

            # 接收连接确认
            msg1 = await ws.recv()
            data1 = json.loads(msg1)
            print(f"📩 服务器响应: {data1.get('message')}")
            print(f"   User ID: {data1.get('user_id')}")
            print()

            # 发送设备绑定消息
            print(f"📤 正在绑定设备: {DEVICE_NAME}")
            bind_message = {
                "type": "bind",
                "device_name": DEVICE_NAME
            }
            await ws.send(json.dumps(bind_message))
            print(f"   已发送: {bind_message}")
            print()

            # 接收绑定确认
            msg2 = await ws.recv()
            data2 = json.loads(msg2)

            if data2.get("type") == "bound":
                device_id = data2.get("device_id")
                print(f"✅ 设备绑定成功!")
                print(f"   设备ID: {device_id}")
                print()
            else:
                print(f"❌ 绑定失败: {data2}")
                return

            print("=" * 60)
            print("✅ 监听中...等待企微消息")
            print("=" * 60)
            print(f"   时间: {datetime.now().strftime('%H:%M:%S')}")
            print()

            # 持续监听 60 秒
            try:
                while True:
                    message = await asyncio.wait_for(ws.recv(), timeout=60.0)
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg_type = data.get("type")

                    print(f"[{timestamp}] 收到消息类型: {msg_type}")

                    if msg_type == "webhook":
                        # Webhook 消息
                        webhook_data = data.get("data", {})
                        sub_type = webhook_data.get("type")

                        if sub_type == "wechat_reply":
                            print("🎉 收到企业微信回复！")
                            print(f"   发送者: {webhook_data.get('from_user')}")
                            print(f"   内容: {webhook_data.get('content')}")
                            print(f"   推送设备: {data.get('target_device')}")
                            print()
                        else:
                            print(f"   Webhook 类型: {sub_type}")
                            print(f"   数据: {webhook_data}")
                            print()

                    elif msg_type == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        print("   收到 Ping -> 发送 Pong")
                    else:
                        print(f"   完整消息: {data}")
                        print()

            except asyncio.TimeoutError:
                print("60秒内没有收到消息，监听结束")

    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print()
    print("🚀 启动 OpenClaw 连接检查")
    print()
    asyncio.run(test_connection())
