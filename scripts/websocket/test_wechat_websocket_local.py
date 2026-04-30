"""
企业微信 WebSocket 接收测试 - 本地客户端
连接到 webhook 服务器，实时接收企业微信回复消息
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

# WebSocket 连接配置
WS_URL = "wss://webhook.sillymd.com/ws"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiaHVnaHdhbmdAc2lsbHltZC5jb20iLCJleHAiOjE3NzQ1NjY0MjcsImlhdCI6MTc3MTk3NDQyN30.hqWdSFQDSiml2GbBdJGhlpONZcfMWF8iEyAZm2712gs"
DEVICE_NAME = "wechat"  # 绑定的设备名称，用于接收企微回复

# 完整的 URI
URI = f"{WS_URL}?token={JWT_TOKEN}"


async def connect_and_listen():
    """连接 WebSocket 并监听消息"""

    print("=" * 60)
    print("企业微信 WebSocket 客户端")
    print("=" * 60)
    print(f"📡 连接地址: {WS_URL}")
    print(f"🔑 Token: {JWT_TOKEN[:50]}...")
    print(f"📱 设备名称: {DEVICE_NAME}")
    print(f"👤 User ID: 33 (傻小黑)")
    print("=" * 60)
    print()

    try:
        # 连接 WebSocket
        print("⏳ 正在连接 WebSocket 服务器...")
        async with websockets.connect(
            URI,
            ping_interval=30,
            ping_timeout=10,
            close_timeout=5
        ) as websocket:

            print("✅ WebSocket 连接成功！")
            print()

            # 接收服务器连接确认消息
            print("📩 等待服务器确认...")
            msg1 = await websocket.recv()
            data1 = json.loads(msg1)
            print(f"✅ 服务器响应: {data1.get('message')}")
            print(f"   类型: {data1.get('type')}")
            print(f"   User ID: {data1.get('user_id')}")
            print()

            # 发送设备绑定消息
            print(f"📤 正在绑定设备: {DEVICE_NAME}")
            bind_message = {
                "type": "bind",
                "device_name": DEVICE_NAME
            }
            await websocket.send(json.dumps(bind_message))
            print(f"   已发送: {bind_message}")
            print()

            # 接收绑定确认
            print("📩 等待绑定确认...")
            msg2 = await websocket.recv()
            data2 = json.loads(msg2)
            print(f"✅ 绑定响应: {data2.get('message')}")
            print(f"   设备ID: {data2.get('device_id')}")
            print(f"   类型: {data2.get('type')}")
            print()

            # 显示监听状态
            print("=" * 60)
            print("✅ 设备绑定成功！开始监听消息...")
            print("=" * 60)
            print()
            print("🎧 监听中...请在企业微信中回复消息")
            print("💡 提示: 按 Ctrl+C 退出")
            print()
            print("-" * 60)

            message_count = 0

            # 持续监听消息
            while True:
                try:
                    # 接收消息（设置超时用于心跳）
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    message_count += 1

                    # 解析消息
                    data = json.loads(message)

                    # 处理不同类型的消息
                    msg_type = data.get("type")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

                        else:
                            # 其他 webhook 消息
                            print(f"📩 [{timestamp}] Webhook 消息")
                            print(f"   子类型: {sub_type}")
                            print(f"   目标设备: {data.get('target_device')}")
                            print(f"   数据: {json.dumps(webhook_data, ensure_ascii=False)[:200]}")

                    elif msg_type == "bound":
                        # 重复绑定确认
                        print(f"✅ [{timestamp}] 重新绑定成功: {data.get('device_id')}")

                    elif msg_type == "error":
                        # 错误消息
                        print(f"❌ [{timestamp}] 错误: {data.get('message')}")

                    elif msg_type == "connected":
                        # 连接确认
                        print(f"✅ [{timestamp}] 连接已确认")

                    else:
                        # 未知消息类型
                        print(f"❓ [{timestamp}] 未处理的消息类型: {msg_type}")
                        print(f"   完整消息: {json.dumps(data, ensure_ascii=False)[:200]}")

                except asyncio.TimeoutError:
                    # 超时，发送心跳
                    print("💓 发送 Ping...")
                    await websocket.send(json.dumps({"type": "ping"}))

                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析错误: {e}")
                    print(f"   原始消息: {message[:200]}")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ 连接被拒绝: HTTP {e.status_code}")
        if e.status_code == 401:
            print("💡 Token 可能无效或已过期")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ 连接已关闭: {e.code} - {e.reason}")

    except ConnectionRefusedError:
        print("❌ 连接被拒绝，服务器可能未运行")

    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")

    finally:
        print()
        print("=" * 60)
        print("🔌 WebSocket 连接已断开")
        print(f"📊 总共收到 {message_count} 条消息")
        print("=" * 60)


if __name__ == "__main__":
    print()
    print("🚀 启动企业微信 WebSocket 客户端")
    print()

    try:
        asyncio.run(connect_and_listen())
    except KeyboardInterrupt:
        print()
        print("\n⏹️  用户主动退出")
