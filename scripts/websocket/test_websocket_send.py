# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

async def test_message():
    uri = 'ws://127.0.0.1:9000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE5NTYzNDMsImV4cCI6MTgwMzQ5MjM0M30.ImJhL_1j8s2Wr3L8Lh6yRbcscQaUdaE7Xa8iPMDviRQ'

    async with websockets.connect(uri) as ws:
        # 接收连接确认
        msg1 = await ws.recv()
        data1 = json.loads(msg1)
        print(f"服务器: {data1.get('type')}")

        # 绑定设备
        await ws.send(json.dumps({"type": "bind", "device_name": "wechat"}))
        msg2 = await ws.recv()
        data2 = json.loads(msg2)
        print(f"绑定: {data2.get('device_id')}")

        print("\n开始监听...")

        # 等待5秒看看有没有消息
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(msg)
            print(f"\n收到消息: {data.get('type')}")
            if 'data' in data:
                print(f"内容: {data['data']}")
        except asyncio.TimeoutError:
            print("\n5秒内没有收到新消息")

if __name__ == "__main__":
    asyncio.run(test_message())
