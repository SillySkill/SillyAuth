# -*- coding: utf-8 -*-
import asyncio
import websockets
import json

async def test():
    uri = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiaHVnaHdhbmdAc2lsbHltZC5jb20iLCJleHAiOjE3NzQ1NjY0MjcsImlhdCI6MTc3MTk3NDQyN30.hqWdSFQDSiml2GbBdJGhlpONZcfMWF8iEyAZm2712gs"

    print("Connecting...")

    try:
        async with websockets.connect(uri, timeout=10) as ws:
            print("Connected!")

            msg1 = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Msg 1: {msg1}")

            await ws.send(json.dumps({"type": "bind", "device_name": "wechat"}))
            print("Bind sent")

            msg2 = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Msg 2: {msg2}")

            print("\nSuccess! Listening for messages (10 seconds)...")
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                print(f"Received: {msg}")
            except asyncio.TimeoutError:
                print("No messages in 10s")

    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
