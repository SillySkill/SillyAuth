# -*- coding: utf-8 -*-
"""
企微消息监听服务 + OpenClaw 推送
基于 listen_wechat_now.py，添加 OpenClaw 推送功能
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

# 强制刷新输出
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# 修复 Windows 编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# WebSocket 配置
WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE5NTYzNDMsImV4cCI6MTgwMzQ5MjM0M30.ImJhL_1j8s2Wr3L8Lh6yRbcscQaUdaE7Xa8iPMDviRQ"
DEVICES = ["wechat", "sillyHei"]

# OpenClaw WebSocket 配置
OPENCLAW_WS_URL = "ws://127.0.0.1:18789/"
openclaw_ws = None
openclaw_connected = False

message_count = 0
forwarded_count = 0


async def connect_openclaw():
    """连接到 OpenClaw WebSocket"""
    global openclaw_ws, openclaw_connected

    print("\n[OpenClaw] 正在连接到 ws://127.0.0.1:18789/ ...", flush=True)

    try:
        openclaw_ws = await asyncio.wait_for(
            websockets.connect(OPENCLAW_WS_URL),
            timeout=5
        )
        openclaw_connected = True
        print("[OpenClaw] ✅ 连接成功!", flush=True)
        return True
    except asyncio.TimeoutError:
        print("[OpenClaw] ⚠️  连接超时 (OpenClaw 可能未运行)", flush=True)
        return False
    except Exception as e:
        print(f"[OpenClaw] ❌ 连接失败: {type(e).__name__}: {e}", flush=True)
        return False


async def forward_to_openclaw(wechat_data: dict):
    """转发企微消息到 OpenClaw"""
    global openclaw_ws, openclaw_connected, forwarded_count

    if not openclaw_connected or openclaw_ws is None:
        return False

    try:
        # 构造消息格式
        message = {
            "type": "wechat_message",
            "source": "SillyMD",
            "data": wechat_data
        }

        await openclaw_ws.send(json.dumps(message))
        forwarded_count += 1

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[OpenClaw][{timestamp}] ✅ 已转发 (总计: {forwarded_count})")
        return True

    except Exception as e:
        print(f"[OpenClaw] ❌ 转发失败: {e}")
        openclaw_connected = False
        return False


async def connect_device(device_name: str):
    """连接并监听指定设备"""
    global message_count, forwarded_count
    uri = f"{WS_URL}"

    print(f"\n{'='*60}")
    print(f"连接设备: {device_name}")
    print('='*60)

    try:
        async with websockets.connect(uri) as ws:
            # 接收连接确认
            msg1 = await ws.recv()
            print(f"[{device_name}] 连接成功")

            # 绑定设备
            await ws.send(json.dumps({"type": "bind", "device_name": device_name}))
            print(f"[{device_name}] 绑定请求已发送")

            # 接收绑定确认
            msg2 = await ws.recv()
            data2 = json.loads(msg2)

            if data2.get("type") == "bound":
                device_id = data2.get("device_id")
                print(f"[{device_name}] 绑定成功: {device_id}")
            else:
                print(f"[{device_name}] 绑定响应: {data2}")
                return

            print(f"[{device_name}] 开始监听...")
            print("-"*60)

            # 持续监听
            while True:
                timestamp = datetime.now().strftime("%H:%M:%S")
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=35.0)
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")  # Update timestamp for received message
                    msg_type = data.get("type")

                    if msg_type == "pong":
                        print(f"[{device_name}][{timestamp}] Pong")

                    elif data.get("data", {}).get("type") == "wechat_reply":
                        # 企微回复消息
                        wechat = data["data"]
                        message_count += 1

                        print()
                        print("="*60)
                        print(f"[{device_name}][{timestamp}] 收到企微回复！")
                        print("="*60)
                        print(f"发送者: {wechat.get('from_user')}")
                        print(f"内容: {wechat.get('content')}")
                        print(f"时间: {wechat.get('timestamp')}")
                        print("="*60)

                        # 转发到 OpenClaw
                        await forward_to_openclaw(wechat)
                        print()

                    elif msg_type == "bound":
                        print(f"[{device_name}][{timestamp}] 重新绑定成功")

                    elif msg_type == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        print(f"[{device_name}][{timestamp}] Ping -> Pong")

                    else:
                        print(f"[{device_name}][{timestamp}] {msg_type}: {str(data)[:100]}")

                except asyncio.TimeoutError:
                    print(f"[{device_name}][{timestamp}] 超时，发送心跳")
                    await ws.send(json.dumps({"type": "ping"}))

    except Exception as e:
        print(f"\n[{device_name}] 错误: {type(e).__name__}: {e}")


async def main():
    """启动所有设备监听"""
    print("="*60, flush=True)
    print("企微回复监听服务 + OpenClaw 推送", flush=True)
    print("="*60, flush=True)
    print(f"设备列表: {DEVICES}", flush=True)
    print(f"User ID: 33 (傻小黑)", flush=True)
    print(f"SillyMD 服务器: {WS_URL}", flush=True)
    print(f"OpenClaw 本地: {OPENCLAW_WS_URL}", flush=True)
    print("="*60, flush=True)
    print("\n正在连接所有设备...\n", flush=True)

    # 先尝试连接 OpenClaw
    await connect_openclaw()

    # 创建所有监听任务
    tasks = []
    for device in DEVICES:
        tasks.append(connect_device(device))

    # 并发运行所有任务
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n监听已停止")
        print(f"\n📊 统计:")
        print(f"  收到消息: {message_count} 条")
        print(f"  转发消息: {forwarded_count} 条")
