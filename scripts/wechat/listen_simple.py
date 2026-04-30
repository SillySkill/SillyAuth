# -*- coding: utf-8 -*-
"""
企微消息监听服务 + OpenClaw 推送 (修复版)
确保输出被正确刷新
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime
import httpx

# 强制无缓冲输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
else:
    sys.stdout.reconfigure(line_buffering=True)

# WebSocket 配置
WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJpYXQiOjE3NzE5NTYzNDMsImV4cCI6MTgwMzQ5MjM0M30.ImJhL_1j8s2Wr3L8Lh6yRbcscQaUdaE7Xa8iPMDviRQ"
DEVICES = ["wechat", "sillyHei"]

# OpenClaw HTTP API 配置
OPENCLAW_API_URL = "http://127.0.0.1:18789/api/sessions/send"
OPENCLAW_API_TOKEN = "sillymd.com"
session_key = None
http_client = None

message_count = 0
forwarded_count = 0


def log(msg):
    """确保输出的日志函数"""
    print(msg, flush=True)


async def init_http_client():
    """初始化 HTTP 客户端"""
    global http_client
    http_client = httpx.AsyncClient(timeout=10.0)


async def forward_to_openclaw(wechat_data: dict):
    """使用 HTTP API 转发企微消息到 OpenClaw"""
    global forwarded_count, session_key, http_client

    if not session_key:
        log("[WARNING] Session key 未配置，跳过推送")
        return False

    if not http_client:
        await init_http_client()

    try:
        content = wechat_data.get('content', '')
        from_user = wechat_data.get('from_user', 'Unknown')
        timestamp = wechat_data.get('timestamp', '')

        # 格式化消息
        message = f"📨 [企微] 来自 {from_user}: {content}\n⏰ {timestamp}"

        headers = {
            "Content-Type": "application/json",
            "X-OpenClaw-Token": OPENCLAW_API_TOKEN
        }

        data = {
            "session_key": session_key,
            "message": message,
            "message_type": "text",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "SillyMD",
                "wechat_data": wechat_data
            }
        }

        response = await http_client.post(
            OPENCLAW_API_URL,
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            forwarded_count += 1
            time_str = datetime.now().strftime("%H:%M:%S")
            log(f"[OpenClaw][{time_str}] ✅ 已推送到 session (总计: {forwarded_count})")
            return True
        else:
            log(f"[OpenClaw] ❌ 推送失败: HTTP {response.status_code} - {response.text}")
            return False

    except httpx.ConnectError:
        log("[OpenClaw] ⚠️  连接失败 (OpenClaw 可能未运行)")
        return False
    except Exception as e:
        log(f"[OpenClaw] ❌ 推送异常: {type(e).__name__}: {e}")
        return False


async def connect_device(device_name: str):
    """连接并监听指定设备"""
    global message_count, forwarded_count

    log(f"\n{'='*60}")
    log(f"连接设备: {device_name}")
    log('='*60)

    try:
        async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=10) as ws:
            # 接收连接确认
            msg1 = await ws.recv()
            log(f"[{device_name}] 连接成功")

            # 绑定设备
            await ws.send(json.dumps({"type": "bind", "device_name": device_name}))
            log(f"[{device_name}] 绑定请求已发送")

            # 接收绑定确认
            msg2 = await ws.recv()
            data2 = json.loads(msg2)

            if data2.get("type") == "bound":
                device_id = data2.get("device_id")
                log(f"[{device_name}] 绑定成功: {device_id}")
            else:
                log(f"[{device_name}] 绑定响应: {data2}")
                return

            log(f"[{device_name}] 开始监听...")
            log("-"*60)

            # 持续监听
            while True:
                timestamp = datetime.now().strftime("%H:%M:%S")
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=35.0)
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg_type = data.get("type")

                    if msg_type == "pong":
                        log(f"[{device_name}][{timestamp}] Pong")

                    elif data.get("data", {}).get("type") == "wechat_reply":
                        # 企微回复消息
                        wechat = data["data"]
                        message_count += 1

                        log("")
                        log("="*60)
                        log(f"[{device_name}][{timestamp}] 收到企微回复！")
                        log("="*60)
                        log(f"发送者: {wechat.get('from_user')}")
                        log(f"内容: {wechat.get('content')}")
                        log(f"时间: {wechat.get('timestamp')}")
                        log("="*60)

                        # 转发到 OpenClaw
                        await forward_to_openclaw(wechat)
                        log("")

                    elif msg_type == "bound":
                        log(f"[{device_name}][{timestamp}] 重新绑定成功")

                    elif msg_type == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        log(f"[{device_name}][{timestamp}] Ping -> Pong")

                    else:
                        log(f"[{device_name}][{timestamp}] {msg_type}: {str(data)[:100]}")

                except asyncio.TimeoutError:
                    log(f"[{device_name}][{timestamp}] 超时，发送心跳")
                    await ws.send(json.dumps({"type": "ping"}))

    except Exception as e:
        log(f"\n[{device_name}] 错误: {type(e).__name__}: {e}")


async def main():
    """启动所有设备监听"""
    global session_key

    # 从命令行参数获取 session key
    if len(sys.argv) > 1:
        session_key = sys.argv[1]
    else:
        import os
        session_key = os.getenv("OPENCLAW_SESSION_KEY")

    log("="*60)
    log("企微回复监听服务 + OpenClaw HTTP API 推送")
    log("="*60)
    log(f"设备列表: {DEVICES}")
    log(f"User ID: 33 (傻小黑)")
    log(f"SillyMD 服务器: {WS_URL[:60]}...")
    log(f"OpenClaw API: {OPENCLAW_API_URL}")
    log(f"Session Key: {session_key[:20]}..." if session_key else "Session Key: 未配置")
    log("="*60)

    if not session_key:
        log("\n⚠️  警告: 未配置 Session Key，消息将不会被推送到 OpenClaw")
        log("\n设置方法:")
        log("  1. 命令行参数: python listen_simple.py <session_key>")
        log("  2. 环境变量: set OPENCLAW_SESSION_KEY=<session_key>")
        log()

    # 初始化 HTTP 客户端
    await init_http_client()

    log("\n正在连接所有设备...\n")

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
        log("\n\n监听已停止")
        log(f"\n📊 统计:")
        log(f"  收到消息: {message_count} 条")
        log(f"  转发消息: {forwarded_count} 条")

        if http_client:
            asyncio.run(http_client.aclose())
