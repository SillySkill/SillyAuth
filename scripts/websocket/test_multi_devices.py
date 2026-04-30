# -*- coding: utf-8 -*-
"""
测试多设备 WebSocket 连接
同时连接多个设备，验证企微回复是否推送到所有设备
"""

import asyncio
import websockets
import json
from datetime import datetime

# 配置
WS_URL = "wss://webhook.sillymd.com/ws"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiaHVnaHdhbmdAc2lsbHltZC5jb20iLCJleHAiOjE3NzQ1NjY0MjcsImlhdCI6MTc3MVk3NDQyN30.hqWdSFQDSiml2GbBdJGhlpONZcfMWF8iEyAZm2712gs"

# 设备列表
DEVICES = ["wechat", "my_claw"]


async def connect_device(device_name: str):
    """连接单个设备"""
    uri = f"{WS_URL}?token={JWT_TOKEN}"

    print(f"[{device_name}] 正在连接...")

    try:
        async with websockets.connect(uri) as ws:
            # 接收连接确认
            msg1 = await ws.recv()
            print(f"[{device_name}] {json.loads(msg1).get('message')}")

            # 绑定设备
            await ws.send(json.dumps({"type": "bind", "device_name": device_name}))

            # 接收绑定确认
            msg2 = await ws.recv()
            device_id = json.loads(msg2).get('device_id')
            print(f"[{device_name}] 设备已绑定: {device_id}")

            # 持续监听
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                timestamp = datetime.now().strftime("%H:%M:%S")

                if data.get("data", {}).get("type") == "wechat_reply":
                    wechat = data["data"]
                    print(f"\n{'='*60}")
                    print(f"[{device_name}] [{timestamp}] 收到企微回复!")
                    print(f"{'='*60}")
                    print(f"发送者: {wechat.get('from_user')}")
                    print(f"内容: {wechat.get('content')}")
                    print(f"{'='*60}\n")
                else:
                    print(f"[{device_name}] [{timestamp}] {data.get('type')}")

    except Exception as e:
        print(f"[{device_name}] 错误: {e}")


async def main():
    """同时连接多个设备"""
    print("=" * 60)
    print("多设备 WebSocket 测试")
    print("=" * 60)
    print(f"设备列表: {DEVICES}")
    print(f"User ID: 33 (傻小黑)")
    print("=" * 60)
    print()

    # 创建任务列表
    tasks = [connect_device(device) for device in DEVICES]

    print("启动所有设备连接...\n")

    # 并发运行所有任务
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试停止")
