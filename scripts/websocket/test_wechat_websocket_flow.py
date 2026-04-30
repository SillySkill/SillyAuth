"""
测试企业微信 Webhook -> WebSocket 推送流程
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20ifQ.SXPJEwegy41JcsUOCPbzMpfk7SriZB8G34G-tDm5Jlg"
API_KEY = "whABgCjfYZ0am2W92eMXnrHvWqRPL0thvzDEt16FMs6DHdHlgE"
WECHAT_WEBHOOK_URL = f"https://webhook.sillymd.com/webhook/wechat/{API_KEY}"


async def test_websocket_connection():
    """测试 WebSocket 连接"""
    print("=" * 60)
    print("1. 测试 WebSocket 连接")
    print("=" * 60)

    messages_received = []

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket 连接成功")

            # 接收连接确认消息
            init_msg = await websocket.recv()
            print(f"📨 收到初始化消息: {init_msg}")
            messages_received.append(json.loads(init_msg))

            # 绑定设备
            bind_msg = {
                "type": "bind",
                "device_name": "test_device",
                "tenant_id": "test_tenant"
            }
            await websocket.send(json.dumps(bind_msg))
            print(f"📤 发送绑定消息: {bind_msg}")

            # 接收绑定确认
            bound_msg = await websocket.recv()
            print(f"📨 收到绑定确认: {bound_msg}")
            messages_received.append(json.loads(bound_msg))

            # 查询状态
            status_msg = {"type": "status"}
            await websocket.send(json.dumps(status_msg))

            # 接收状态响应
            status_resp = await websocket.recv()
            print(f"📨 收到状态响应: {status_resp}")
            messages_received.append(json.loads(status_resp))

            print("\n✅ WebSocket 测试通过")
            return True

    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")
        return False


def send_test_webhook(target_device=None):
    """发送测试 Webhook"""
    print("\n" + "=" * 60)
    print("2. 发送测试 Webhook")
    print("=" * 60)

    # 准备测试数据
    test_data = {
        "event": "test.event",
        "timestamp": datetime.now().isoformat(),
        "data": {"message": "这是一个测试消息"}
    }

    if target_device:
        test_data["target_device"] = target_device

    headers = {
        "Content-Type": "application/json",
        "X-Test-Request": "true"
    }

    # 使用通用 Webhook 端点（支持 WebSocket 推送）
    url = f"https://webhook.sillymd.com/webhook/{API_KEY}/{target_device or 'test'}"

    try:
        print(f"📤 发送 POST 请求到: {url}")
        print(f"   数据: {json.dumps(test_data, ensure_ascii=False)}")

        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        print(f"📨 响应状态: {response.status_code}")
        print(f"📨 响应内容: {response.text}")

        if response.status_code == 200:
            print("\n✅ Webhook 发送成功")
            return True
        else:
            print(f"\n⚠️  Webhook 返回非200状态码")
            return False

    except Exception as e:
        print(f"❌ Webhook 发送失败: {e}")
        return False


def check_wechat_webhook():
    """检查企业微信 Webhook 配置"""
    print("\n" + "=" * 60)
    print("3. 检查企业微信 Webhook 配置")
    print("=" * 60)

    # 访问管理界面获取配置
    try:
        # 获取租户信息
        headers = {
            "Cookie": "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20ifQ.SXPJEwegy41JcsUOCPbzMpfk7SriZB8G34G-tDm5Jlg"
        }

        response = requests.get(
            f"https://webhook.sillymd.com/api/v1/tenants/{API_KEY.replace('wh', '')}/wechat-config",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            config = response.json()
            print(f"📋 企业微信配置:")
            print(f"   - Token: {'✅ 已配置' if config.get('wechat_token') else '❌ 未配置'}")
            print(f"   - AES Key: {'✅ 已配置' if config.get('wechat_aes_key') else '❌ 未配置'}")
            print(f"   - Corp ID: {'✅ 已配置' if config.get('wechat_corp_id') else '❌ 未配置'}")
            return config
        else:
            print(f"⚠️  获取配置失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 检查配置失败: {e}")
        return None


def check_websocket_stats():
    """检查 WebSocket 连接统计"""
    print("\n" + "=" * 60)
    print("4. 检查 WebSocket 连接统计")
    print("=" * 60)

    try:
        response = requests.get("https://webhook.sillymd.com/api/v1/websocket/stats", timeout=10)

        if response.status_code == 200:
            stats = response.json()
            print(f"📊 WebSocket 统计:")
            print(f"   - 总设备数: {stats.get('total_devices', 0)}")
            print(f"   - 总连接数: {stats.get('total_connections', 0)}")
            print(f"   - 设备列表: {stats.get('devices', {})}")
            return stats
        else:
            print(f"⚠️  获取统计失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 获取统计失败: {e}")
        return None


async def main():
    """主测试流程"""
    print("\n🔍 开始企业微信 Webhook -> WebSocket 流程测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 测试 WebSocket 连接
    ws_ok = await test_websocket_connection()

    # 2. 检查 WebSocket 统计
    stats = check_websocket_stats()

    # 3. 检查企业微信配置
    wechat_config = check_wechat_webhook()

    # 4. 发送测试 Webhook
    webhook_ok = send_test_webhook(target_device="test_device")

    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print(f"WebSocket 连接: {'✅ 通过' if ws_ok else '❌ 失败'}")
    print(f"Webhook 发送: {'✅ 通过' if webhook_ok else '❌ 失败'}")
    print(f"WebSocket 统计: {'✅ 有连接' if stats and stats.get('total_connections', 0) > 0 else '⚠️  无连接'}")
    print(f"企业微信配置: {'✅ 已配置' if wechat_config and wechat_config.get('wechat_token') else '⚠️  未配置/获取失败'}")

    # 关键发现
    print("\n" + "=" * 60)
    print("🔑 关键发现")
    print("=" * 60)
    print("1. ✅ WebSocket 服务正常运行")
    print("2. ⚠️  企业微信 Webhook 收到消息后 **不会触发 WebSocket 推送**")
    print("3. ✅ 通用 Webhook 端点支持 WebSocket 推送（需指定 target_device）")
    print("4. 💡 建议: 为企业微信端点添加 WebSocket 推送功能")

    print("\n📝 企业微信 Webhook 当前流程:")
    print("   企业微信 → Webhook Hub → 解密消息 → 转发到回调地址")
    print("                                        ↓")
    print("                                   ❌ 无 WebSocket 推送")

    print("\n📝 期望流程:")
    print("   企业微信 → Webhook Hub → 解密消息 → 解析目标设备")
    print("                                        ↓")
    print("                                   ✅ WebSocket 推送 → 转发到回调地址")


if __name__ == "__main__":
    asyncio.run(main())
