# -*- coding: utf-8 -*-
"""
SillyMD → OpenClaw 消息桥接器 (简化版)
"""
import asyncio
import websockets
import json
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

SILLYMD_WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE4MDA1ODMsImV4cCI6MTgwMzMzNjU4M30.nrZqCDtC3Rz8D0QJLJGEFhgY9sgSyUAZWpmjVqRlHko"
SILLYMD_DEVICE = "sillyHei"
OPENCLAW_WS_URL = "ws://127.0.0.1:18789/"

print("="*70)
print("🌉 SillyMD → OpenClaw 消息桥接器")
print("="*70)

async def main():
    # 1. 连接到 SillyMD
    print("\n[1/2] 连接到 SillyMD...")
    try:
        sillymd_ws = await websockets.connect(SILLYMD_WS_URL)
        print("✅ SillyMD 连接成功!")

        # 绑定设备
        await sillymd_ws.send(json.dumps({"type": "bind", "device_name": SILLYMD_DEVICE}))

        # 接收绑定确认
        msg = await sillymd_ws.recv()
        data = json.loads(msg)
        print(f"✅ 设备绑定: {data.get('device_id')}")

    except Exception as e:
        print(f"❌ SillyMD 连接失败: {type(e).__name__}: {e}")
        return

    # 2. 连接到 OpenClaw
    print("\n[2/2] 连接到 OpenClaw...")
    try:
        openclaw_ws = await websockets.connect(OPENCLAW_WS_URL)
        print("✅ OpenClaw 连接成功!")
    except Exception as e:
        print(f"❌ OpenClaw 连接失败: {type(e).__name__}: {e}")
        print(f"   提示: 请确保 OpenClaw 正在运行")
        # OpenClaw 连接失败不影响监听 SillyMD
        openclaw_ws = None

    # 3. 开始监听和转发
    print("\n" + "="*70)
    print("✅ 桥接器已启动，等待企微消息...")
    print("="*70 + "\n")

    message_count = 0
    forwarded_count = 0

    try:
        while True:
            # 从 SillyMD 接收消息
            message = await sillymd_ws.recv()
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "pong":
                continue

            elif msg_type == "ping":
                await sillymd_ws.send(json.dumps({"type": "pong"}))

            elif data.get("data", {}).get("type") == "wechat_reply":
                # 企业微信回复
                message_count += 1
                wechat = data["data"]

                print("="*70)
                print(f"📨 收到企业微信回复 (#{message_count})")
                print("="*70)
                print(f"发送者: {wechat.get('from_user')}")
                print(f"内容: {wechat.get('content')}")
                print(f"时间: {wechat.get('timestamp')}")
                print("="*70)

                # 转发到 OpenClaw
                if openclaw_ws:
                    try:
                        forward_msg = {
                            "type": "wechat_message",
                            "source": "SillyMD",
                            "data": wechat
                        }
                        await openclaw_ws.send(json.dumps(forward_msg))
                        forwarded_count += 1
                        print(f"✅ 已转发到 OpenClaw (#{forwarded_count})")
                    except Exception as e:
                        print(f"❌ 转发失败: {e}")
                else:
                    print("⚠️  OpenClaw 未连接，消息未转发")

                print()

            elif msg_type == "bound":
                print(f"✅ 重新绑定: {data.get('device_id')}")

    except websockets.exceptions.ConnectionClosed:
        print("\n❌ SillyMD 连接已关闭")

    except KeyboardInterrupt:
        print("\n\n📊 统计:")
        print(f"  收到消息: {message_count} 条")
        print(f"  转发消息: {forwarded_count} 条")
        print("\n👋 桥接器已停止")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
