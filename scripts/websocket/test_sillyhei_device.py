# -*- coding: utf-8 -*-
"""
模拟 OpenClaw 连接测试
绑定到 sillyHei 设备，接收企微回复
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# JWT Token (傻小黑)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiaHVnaHdhbmdAc2lsbHltZC5jb20iLCJleHAiOjE3NzQ1NjY0MjcsImlhdCI6MTc3MVk3NDQyN30.hqWdSFQDSiml2GbBdJGhlpONZcfMWF8iEyAZm2712gs"
WS_URL = "wss://webhook.sillymd.com/ws"
DEVICE_NAME = "sillyHei"  # 小写的 sillyHei

async def connect_sillyhei():
    """连接并绑定到 sillyHei 设备"""

    print("=" * 60)
    print("OpenClaw 连接测试 - 设备: sillyHei")
    print("=" * 60)
    print(f"WebSocket URL: {WS_URL}")
    print(f"Device Name: {DEVICE_NAME}")
    print(f"User ID: 33 (傻小黑)")
    print("=" * 60)
    print()

    uri = f"{WS_URL}?token={JWT_TOKEN}"

    try:
        async with websockets.connect(uri) as ws:
            print("✅ WebSocket 连接成功！\n")

            # 接收服务器连接确认
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
                print(f"   Device ID: {device_id}")
                print()
            else:
                print(f"❌ 绑定失败: {data2}")
                return

            # 显示监听状态
            print("=" * 60)
            print("✅ 监听中...企微回复将实时显示")
            print("=" * 60)
            print()
            print("💡 请在企微中发送消息...")
            print("💡 按 Ctrl+C 退出")
            print()
            print("-" * 60)

            message_count = 0

            # 持续监听消息
            while True:
                try:
                    # 接收消息（设置超时用于心跳）
                    message = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    message_count += 1

                    # 解析消息
                    data = json.loads(message)
                    msg_type = data.get("type")
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    # 处理不同类型的消息
                    if msg_type == "pong":
                        # 心跳响应
                        print(f"💓 [{timestamp}] Pong - 心跳正常")

                    elif msg_type == "webhook":
                        # Webhook 消息
                        webhook_data = data.get("data", {})
                        sub_type = webhook_data.get("type")

                        if sub_type == "wechat_reply":
                            # 企业微信回复消息
                            print()
                            print("=" * 60)
                            print(f"🎉 [{timestamp}] 收到企业微信回复！")
                            print("=" * 60)
                            print(f"👤 发送者: {webhook_data.get('from_user')}")
                            print(f"📝 消息类型: {webhook_data.get('msg_type')}")
                            print(f"💬 内容: {webhook_data.get('content')}")
                            print(f"⏰ 时间: {webhook_data.get('timestamp')}")
                            print(f"📱 推送设备: {data.get('target_device')}")
                            print("=" * 60)
                            print()

                            # 保存到文件（可选）
                            with open("E:/silly/sillyhei_messages.log", "a", encoding="utf-8") as f:
                                f.write(f"\n[{timestamp}] From: {webhook_data.get('from_user')}\n")
                                f.write(f"Content: {webhook_data.get('content')}\n")
                                f.write(f"-" * 60 + "\n")

                        else:
                            # 其他 webhook 消息
                            print(f"📩 [{timestamp}] Webhook: {sub_type}")
                            print(f"   设备: {data.get('target_device')}")

                    elif msg_type == "bound":
                        # 重复绑定确认
                        print(f"✅ [{timestamp}] 重新绑定成功")

                    elif msg_type == "ping":
                        # 心跳请求
                        print(f"💓 [{timestamp}] Ping 收到，发送 Pong")
                        await ws.send(json.dumps({"type": "pong"}))

                    elif msg_type == "error":
                        # 错误消息
                        print(f"❌ [{timestamp}] 错误: {data.get('message')}")

                    else:
                        # 未知消息类型
                        print(f"❓ [{timestamp}] 其他消息: {msg_type}")

                except asyncio.TimeoutError:
                    # 超时，发送心跳
                    print("💓 发送 Ping...")
                    await ws.send(json.dumps({"type": "ping"}))

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ 连接被拒绝: HTTP {e.status_code}")
        if e.status_code == 401:
            print("💡 Token 可能无效或已过期")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"\n❌ 连接已关闭: {e.code} - {e.reason}")

    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")

    finally:
        print()
        print("=" * 60)
        print("🔌 连接已断开")
        print(f"📊 总共收到 {message_count} 条企微回复")
        print("=" * 60)


if __name__ == "__main__":
    print()
    print("🚀 启动 OpenClau 模拟客户端 (设备: sillyHei)")
    print()

    try:
        asyncio.run(connect_sillyhei())
    except KeyboardInterrupt:
        print("\n\n⏹️  用户主动退出")
