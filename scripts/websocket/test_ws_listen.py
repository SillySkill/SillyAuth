# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
from datetime import datetime

async def listen():
    uri = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiaHVnaHdhbmdAc2lsbHltZC5jb20iLCJleHAiOjE3NzQ1NjY0MjcsImlhdCI6MTc3MTk3NDQyN30.hqWdSFQDSiml2GbBdJGhlpONZcfMWF8iEyAZm2712gs"

    print("=" * 60)
    print("企业微信回复监听器")
    print("=" * 60)
    print("正在连接...")

    async with websockets.connect(uri) as ws:
        print("已连接!")

        # 接收连接确认
        msg1 = await ws.recv()
        print(f"服务器: {json.loads(msg1).get('message')}")

        # 绑定设备
        await ws.send(json.dumps({"type": "bind", "device_name": "wechat"}))
        msg2 = await ws.recv()
        device_id = json.loads(msg2).get('device_id')
        print(f"设备已绑定: {device_id}")

        print("\n" + "=" * 60)
        print("监听中...请在企业微信中回复消息")
        print("=" * 60 + "\n")

        # 持续监听
        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            timestamp = datetime.now().strftime("%H:%M:%S")

            # 检查是否是企微回复
            if data.get("data", {}).get("type") == "wechat_reply":
                wechat = data["data"]
                print("\n" + "=" * 60)
                print(f"[{timestamp}] 收到企业微信回复!")
                print("=" * 60)
                print(f"发送者: {wechat.get('from_user')}")
                print(f"类型: {wechat.get('msg_type')}")
                print(f"内容: {wechat.get('content')}")
                print("=" * 60 + "\n")
            else:
                print(f"[{timestamp}] 其他消息: {data.get('type')}")

if __name__ == "__main__":
    try:
        asyncio.run(listen())
    except KeyboardInterrupt:
        print("\n\n监听已停止")
