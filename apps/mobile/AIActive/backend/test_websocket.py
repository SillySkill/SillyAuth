"""
WebSocket服务测试脚本
测试配置推送和广播功能
"""
import asyncio
import websockets
import json
import sys

# WebSocket服务器地址
WS_URL = "ws://localhost:5000/ws"
# 测试设备ID
TEST_DEVICE_ID = "test_device_001"
# 测试token
TEST_TOKEN = "temp_token_test_device_001"


async def test_connection():
    """测试WebSocket连接"""
    print("=" * 60)
    print("测试1: WebSocket连接")
    print("=" * 60)

    try:
        url = f"{WS_URL}?device_id={TEST_DEVICE_ID}&token={TEST_TOKEN}"
        async with websockets.connect(url) as ws:
            print(f"✓ 成功连接到: {url}")

            # 接收连接确认消息
            response = await ws.recv()
            data = json.loads(response)
            print(f"✓ 收到消息: {json.dumps(data, indent=2, ensure_ascii=False)}")

            if 'connected' in data:
                print(f"✓ 会话ID: {data['connected']['sid']}")
                return True
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


async def test_heartbeat():
    """测试心跳"""
    print("\n" + "=" * 60)
    print("测试2: 心跳")
    print("=" * 60)

    try:
        url = f"{WS_URL}?device_id={TEST_DEVICE_ID}&token={TEST_TOKEN}"
        async with websockets.connect(url) as ws:
            # 等待连接确认
            await ws.recv()

            # 发送心跳
            heartbeat_msg = {
                "heartbeat": {
                    "client_time": "2024-01-01T00:00:00"
                }
            }
            await ws.send(json.dumps(heartbeat_msg))
            print(f"✓ 发送心跳: {json.dumps(heartbeat_msg)}")

            # 接收心跳确认
            response = await ws.recv()
            data = json.loads(response)
            print(f"✓ 收到心跳确认: {json.dumps(data, indent=2, ensure_ascii=False)}")

            if 'heartbeat_ack' in data:
                print("✓ 心跳测试通过")
                return True
    except Exception as e:
        print(f"✗ 心跳测试失败: {e}")
        return False


async def test_device_status():
    """测试设备状态上报"""
    print("\n" + "=" * 60)
    print("测试3: 设备状态上报")
    print("=" * 60)

    try:
        url = f"{WS_URL}?device_id={TEST_DEVICE_ID}&token={TEST_TOKEN}"
        async with websockets.connect(url) as ws:
            # 等待连接确认
            await ws.recv()

            # 上报设备状态
            status_msg = {
                "device_status": {
                    "battery": 85,
                    "storage": 2048,
                    "network_type": "wifi",
                    "app_version": "1.0.0",
                    "config_version": "1.0.0"
                }
            }
            await ws.send(json.dumps(status_msg))
            print(f"✓ 上报设备状态: {json.dumps(status_msg, indent=2, ensure_ascii=False)}")
            print("✓ 设备状态上报测试通过")
            return True
    except Exception as e:
        print(f"✗ 设备状态上报测试失败: {e}")
        return False


async def test_broadcast():
    """测试广播接收"""
    print("\n" + "=" * 60)
    print("测试4: 接收广播消息")
    print("=" * 60)
    print("提示: 需要在另一个终端调用广播API才能测试此功能")
    print("curl -X POST http://localhost:5000/api/admin/apps/1/push/broadcast \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -H "Authorization: Bearer <token>" \\')
    print('  -d \'{"message": "测试广播", "data": {"key": "value"}}\'')
    print("\n等待广播消息...")

    try:
        url = f"{WS_URL}?device_id={TEST_DEVICE_ID}&token={TEST_TOKEN}"
        async with websockets.connect(url) as ws:
            # 等待连接确认
            await ws.recv()
            print("✓ 已连接，等待接收广播消息...")

            # 等待广播消息（30秒超时）
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(response)
                print(f"✓ 收到广播消息: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            except asyncio.TimeoutError:
                print("✗ 30秒内未收到广播消息")
                return False
    except Exception as e:
        print(f"✗ 接收广播测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n🚀 WebSocket服务测试")
    print(f"服务器地址: {WS_URL}")
    print(f"测试设备ID: {TEST_DEVICE_ID}")

    results = []

    # 运行测试
    results.append(("连接测试", await test_connection()))
    results.append(("心跳测试", await test_heartbeat()))
    results.append(("设备状态上报测试", await test_device_status()))
    results.append(("广播接收测试", await test_broadcast()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    # 检查是否安装了websockets库
    try:
        import websockets
    except ImportError:
        print("错误: 需要安装 websockets 库")
        print("请运行: pip install websockets")
        sys.exit(1)

    # 运行测试
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
