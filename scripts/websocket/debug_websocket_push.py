"""
诊断 WebSocket 推送问题
测试不同 device_id 格式的推送
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime

# 配置
WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20ifQ.SXPJEwegy41JcsUOCPbzMpfk7SriZB8G34G-tDm5Jlg"
API_KEY = "whIUiRObm2IldE3ftCurAdvSLL6DN5BXYB0czC6FjKKnRxxi1p"

DEVICE_NAME = "test_debug_device"
TENANT_ID = "51ae5b72-279c-4e39-88c0-a42c9f2b5be1"
USER_ID = "33"


async def test_device_id_format(device_name: str, tenant_id: str = None):
    """测试特定 device_id 格式"""
    print("\n" + "="*60)
    print(f"测试 device_id 格式: {tenant_id if tenant_id else '无 tenant_id'}")
    print("="*60)

    messages_received = []

    try:
        async with websockets.connect(WS_URL) as websocket:
            # 接收连接确认
            init_msg = await websocket.recv()
            init_data = json.loads(init_msg)
            print(f"✅ 连接成功: user_id={init_data.get('user_id')}")

            # 绑定设备
            bind_msg = {
                "type": "bind",
                "device_name": device_name
            }
            if tenant_id:
                bind_msg["tenant_id"] = tenant_id

            await websocket.send(json.dumps(bind_msg))
            print(f"📤 发送绑定: {bind_msg}")

            # 接收绑定确认
            bound_msg = await websocket.recv()
            bound_data = json.loads(bound_msg)
            device_id = bound_data.get("device_id")
            print(f"✅ 绑定成功: device_id={device_id}")

            # 查询状态
            status_msg = {"type": "status"}
            await websocket.send(json.dumps(status_msg))
            status_resp = await websocket.recv()
            status_data = json.loads(status_resp)
            print(f"📊 状态: {status_data.get('stats')}")

            # 等待可能的推送消息（最多10秒）
            print("\n⏳ 等待推送消息（10秒）...")
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                msg_data = json.loads(msg)
                print(f"📨 收到消息: {msg_data}")
                messages_received.append(msg_data)
            except asyncio.TimeoutError:
                print("⏰ 超时：未收到推送消息")

            return device_id, messages_received

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None, []


async def trigger_webhook():
    """触发一个测试 Webhook"""
    print("\n" + "="*60)
    print("触发测试 Webhook")
    print("="*60)

    test_data = {
        "event": "debug.test",
        "timestamp": datetime.now().isoformat(),
        "message": "WebSocket 推送测试"
    }

    try:
        # 使用通用 webhook 端点
        url = f"https://webhook.sillymd.com/webhook/{API_KEY}/test_debug"
        response = requests.post(url, json=test_data, timeout=10)
        print(f"📤 Webhook 发送: {response.status_code}")
        print(f"📨 响应: {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Webhook 发送失败: {e}")
        return False


async def main():
    """主测试流程"""
    print("\n🔍 WebSocket 推送诊断测试")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 测试1: 带 tenant_id 的绑定
    print("\n\n📋 测试 1: 带 tenant_id 绑定")
    device_id_1, msgs_1 = await test_device_id_format(DEVICE_NAME, TENANT_ID)

    # 触发 webhook
    webhook_ok = await trigger_webhook()

    # 等待并检查消息
    await asyncio.sleep(2)

    # 测试2: 不带 tenant_id 的绑定
    print("\n\n📋 测试 2: 不带 tenant_id 绑定")
    device_id_2, msgs_2 = await test_device_id_format(DEVICE_NAME, None)

    # 再次触发 webhook
    webhook_ok = await trigger_webhook()

    # 等待并检查消息
    await asyncio.sleep(2)

    # 总结
    print("\n\n" + "="*60)
    print("📋 诊断总结")
    print("="*60)
    print(f"device_id (带 tenant_id):  {device_id_1}")
    print(f"device_id (不带 tenant_id): {device_id_2}")
    print(f"\n服务器推送使用的格式: 33:{DEVICE_NAME}")
    print(f"\n匹配情况:")
    if device_id_1:
        match_1 = device_id_1 == f"{USER_ID}:{DEVICE_NAME}"
        print(f"  - 带 tenant_id 格式匹配: {'❌ 否' if not match_1 else '✅ 是'}")
    if device_id_2:
        match_2 = device_id_2 == f"{USER_ID}:{DEVICE_NAME}"
        print(f"  - 不带 tenant_id 格式匹配: {'✅ 是' if match_2 else '❌ 否'}")

    print(f"\n结论: ")
    print(f"  - 客户端应使用{'不带 tenant_id' if device_id_2 == f'{USER_ID}:{DEVICE_NAME}' else '带 tenant_id'} 的格式绑定")
    print(f"  - 服务器推送时应{'添加' if device_id_1 and device_id_1 != f'{USER_ID}:{DEVICE_NAME}' else '省略'} tenant_id 参数")


if __name__ == "__main__":
    asyncio.run(main())
