# -*- coding: utf-8 -*-
import requests
import json
import sys

# Configuration from database
CORP_ID = "ww55fa54d3dfaf09de"
CORP_SECRET = "bbMsAGExeZAGvzDxR7P1-iHbb_zJVTfXb2K50GNJ7Gk"
AGENT_ID = "1000006"
PUSH_TARGET = "HughWang"

print("=" * 60)
print("WeChat App Push Test")
print("=" * 60)
print(f"Corp ID: {CORP_ID}")
print(f"Agent ID: {AGENT_ID}")
print(f"Target: {PUSH_TARGET}")
print(f"Secret: {CORP_SECRET[:20]}...{CORP_SECRET[-10:]}")
print("=" * 60)

def get_access_token():
    """Step 1: Get access_token"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}"
    print(f"\n[1] Requesting access_token...")
    print(f"    URL: {url[:50]}...")

    response = requests.get(url, timeout=10)
    data = response.json()

    print(f"\n[1] Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    errcode = data.get('errcode')
    if errcode == 0:
        print(f"\n[OK] Access token obtained, valid for {data.get('expires_in')} seconds")
        return data['access_token']
    else:
        print(f"\n[ERROR] Failed to get access token!")
        print(f"       Error code: {errcode}")
        print(f"       Message: {data.get('errmsg')}")

        # Common error codes
        error_tips = {
            40001: "Invalid credential - secret may be wrong or expired",
            40013: "Invalid corp_id",
            40014: "Invalid access_token",
            40091: "Secret does not exist",
        }
        if errcode in error_tips:
            print(f"       Hint: {error_tips[errcode]}")
        return None

def send_message(access_token, message, target=PUSH_TARGET):
    """Step 2: Send message"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

    message_data = {
        "touser": target,
        "msgtype": "text",
        "agentid": int(AGENT_ID),
        "text": {"content": str(message)},
        "safe": 0
    }

    print(f"\n[2] Sending message...")
    print(f"    Target: {target}")
    print(f"    Content: {message}")

    response = requests.post(url, json=message_data, timeout=10)
    result = response.json()

    print(f"\n[2] Response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    errcode = result.get('errcode')
    if errcode == 0:
        print(f"\n[OK] Message sent successfully!")
        return True
    else:
        print(f"\n[ERROR] Failed to send message!")
        print(f"       Error code: {errcode}")
        print(f"       Message: {result.get('errmsg')}")

        # Check for invalid user
        if 'invaliduser' in result:
            print(f"       Invalid users: {result.get('invaliduser')}")
        if 'invalidparty' in result:
            print(f"       Invalid parties: {result.get('invalidparty')}")
        if 'invalidtag' in result:
            print(f"       Invalid tags: {result.get('invalidtag')}")

        return False

if __name__ == "__main__":
    # Step 1: Get access token
    token = get_access_token()

    if token:
        print(f"\nAccess token: {token[:30]}...")

        # Step 2: Send test message
        success = send_message(token, "Test from webhook-hub to HughWang")

        print("\n" + "=" * 60)
        if success:
            print("[SUCCESS] Message sent to HughWang")
        else:
            print("[FAILED] Please check the error messages above")
        print("=" * 60)
        sys.exit(0 if success else 1)
    else:
        print("\n" + "=" * 60)
        print("[FAILED] Could not obtain access token")
        print("         Please verify:")
        print("         1. Corp ID is correct")
        print("         2. Corp Secret is correct and not expired")
        print("         3. Application is properly configured")
        print("=" * 60)
        sys.exit(1)
