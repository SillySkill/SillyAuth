"""
企业微信应用消息推送测试脚本
使用企业微信应用 API 发送消息
"""
import requests
import json
from datetime import datetime

# 企业微信应用配置
CORP_ID = "ww55fa54d3dfaf09de"  # 企业ID
CORP_SECRET = "bbMsAGExeZAGvzDxR7P1-iHbb_zJVTfXb2K50GNJ7Gk"  # 应用的 Secret
AGENT_ID = "1000006"  # 应用ID

# 推送目标配置
PUSH_TARGET = "@all"  # 可选: "@all" | 用户ID | 部门ID


def get_access_token():
    """获取 access_token"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}"

    print(f"📡 正在获取 access_token...")
    response = requests.get(url, timeout=10)
    data = response.json()

    if data.get('errcode') == 0:
        access_token = data['access_token']
        expires_in = data['expires_in']
        print(f"✅ 获取 access_token 成功！有效期: {expires_in} 秒")
        return access_token
    else:
        print(f"❌ 获取 access_token 失败: {data}")
        return None


def send_message(access_token, message, target=PUSH_TARGET):
    """发送消息到企业微信应用"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

    # 构建消息体
    message_data = {
        "touser": target,
        "msgtype": "text",
        "agentid": int(AGENT_ID),
        "text": {
            "content": str(message)
        },
        "safe": 0
    }

    print(f"\n📤 发送消息到企业微信应用...")
    print(f"   目标: {target}")
    print(f"   内容: {message}")
    print(f"   应用ID: {AGENT_ID}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    response = requests.post(url, json=message_data, timeout=10)
    result = response.json()

    print(f"\n📨 响应:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get('errcode') == 0:
        print(f"\n✅ 消息发送成功！")
        invaliduser = result.get('invaliduser', [])
        if invaliduser:
            print(f"⚠️  无效用户: {invaliduser}")
        return True
    else:
        print(f"\n❌ 消息发送失败: {result.get('errmsg', 'Unknown error')}")
        return False


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         企业微信应用消息推送测试工具                          ║
║                                                                    ║
║  功能: 通过企业微信应用 API 发送消息                            ║
║  应用: AgentID=1000006                                            ║
╚════════════════════════════════════════════════════════════════╝
    """)

    print(f"📋 当前配置:")
    print(f"   企业ID: {CORP_ID}")
    print(f"   应用ID: {AGENT_ID}")
    print(f"   推送目标: {PUSH_TARGET}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 获取 access_token
    access_token = get_access_token()
    if not access_token:
        return

    # 发送测试消息
    message = input("\n请输入要发送的消息内容: ").strip()

    if not message:
        message = f"这是来自 webhook 服务器的测试消息 - {datetime.now().strftime('%H:%M:%S')}"
        print(f"ℹ️  使用默认测试消息: {message}")

    # 选择推送目标
    print(f"\n📱 选择推送目标:")
    print(f"   1. @all (所有人)")
    print(f"   2. 自定义用户ID/部门ID")

    choice = input("\n请选择 (1 或 2，直接回车默认@all): ").strip()

    if choice == "2":
        PUSH_TARGET = input("请输入用户ID或部门ID: ").strip()
        if not PUSH_TARGET:
            print("❌ 未输入目标，使用默认 @all")
            PUSH_TARGET = "@all"

    # 发送消息
    success = send_message(access_token, message, PUSH_TARGET)

    if success:
        print(f"\n🎉 测试完成！")
    else:
        print(f"\n❌ 测试失败，请检查配置")


if __name__ == "__main__":
    main()
