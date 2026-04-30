# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

async def test():
    # 使用服务器日志中验证成功的 token
    uri = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE4MDA1ODMsImV4cCI6MTgwMzMzNjU4M30.nrZqCDtC3Rz8D0QJLJGEFhgY9sgSyUAZWpmjVqRlHko"

    try:
        async with websockets.connect(uri) as ws:
            print("Connected!")

            msg1 = await ws.recv()
            print(f"Msg1: {msg1}")

            await ws.send(json.dumps({"type": "bind", "device_name": "sillyHei"}))
            print("Bind sent: sillyHei")

            msg2 = await ws.recv()
            print(f"Msg2: {msg2}")

            print("\nListening for messages (20s)...")
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=20)
                print(f"Received: {msg}")
            except asyncio.TimeoutError:
                print("No messages")

    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
