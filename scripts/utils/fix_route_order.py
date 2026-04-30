#!/usr/bin/env python3
"""
Move WeChat route before the generic webhook route
"""
import shutil
from pathlib import Path

MAIN_FILE = Path("/opt/webhook-hub/main.py")

# Read the file
with open(MAIN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# WeChat endpoint code (extracted from current location)
wechat_code = '''# ========== 企业微信应用回调端点 ==========
@app.post("/webhook/wechat/{tenant_path:path}")
async def receive_wechat_callback(
    request: Request,
    tenant_path: str,
    db: AsyncSession = Depends(get_db)
):
    """
    接收企业微信应用的消息回调
    1. 解析XML消息
    2. 验证租户
    3. 推送到WebSocket (via Redis)
    """
    from ws_server import redis_conn, WS_CHANNEL
    import xml.etree.ElementTree as ET
    import logging

    body = await request.body()

    try:
        # 解析XML
        root = ET.fromstring(body.decode("utf-8"))

        # 查找租户
        result = await db.execute(
            text("SELECT id, name, user_id FROM tenants WHERE api_key = :key AND is_active = true"),
            {"key": tenant_path}
        )
        row = result.fetchone()

        if not row:
            logging.warning(f"[WeChatCallback] Tenant not found: {tenant_path}")
            return Response(content="success", media_type="text/plain")

        row_dict = row._mapping
        tenant_id = str(row_dict["id"])
        user_id = str(row_dict["user_id"])

        # 提取消息内容
        msg_type = root.find("MsgType").text if root.find("MsgType") is not None else "unknown"
        from_user = root.find("FromUserName").text if root.find("FromUserName") is not None else ""
        content = root.find("Content").text if root.find("Content") is not None else ""
        create_time = root.find("CreateTime").text if root.find("CreateTime") is not None else ""

        logging.info(f"[WeChatCallback] Received from {from_user}: {content}")

        # 推送到WebSocket (via Redis)
        if redis_conn:
            ws_message = {
                "type": "wechat",
                "source": "wechat_callback",
                "tenant_id": tenant_id,
                "user_id": user_id,
                "data": {
                    "msg_type": msg_type,
                    "from_user": from_user,
                    "content": content,
                    "create_time": create_time,
                    "xml_content": body.decode("utf-8")[:1000]
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            await redis_conn.publish(
                WS_CHANNEL,
                json.dumps({
                    "broadcast_type": "wechat",
                    "target_user_id": user_id,
                    "message": ws_message
                })
            )
            logging.info(f"[WeChatCallback] Published to Redis for user {user_id}")

        # 企业微信要求返回success
        return Response(content="success", media_type="text/plain")

    except Exception as e:
        logging.error(f"[WeChatCallback] Error: {e}", exc_info=True)
        # 即使出错也返回success，避免企业微信重试
        return Response(content="success", media_type="text/plain")


'''

# Step 1: Remove WeChat route from its current location
import re
# Match the entire WeChat route block
pattern = r'# ========== 企业微信应用回调端点 ===========\n@app\.post\("/webhook/wechat/\{tenant_path:path\}"\).*?(?=\n# 健康检查|\n@app\.post\("/api/v1/wechat/push/test"'
content, count = re.subn(pattern, '', content, flags=re.DOTALL)

print(f"Removed {count} occurrence(s) of WeChat route")

# Step 2: Insert it before the generic webhook route
# Find the position to insert (before @app.post("/webhook/{tenant_path:path}"))
insert_marker = '@app.post("/webhook/{tenant_path:path}", response_model=WebhookResponse)'
if insert_marker in content:
    content = content.replace(insert_marker, wechat_code + insert_marker)
    print("✅ WeChat route moved before generic webhook route")
else:
    print("❌ Could not find insertion marker!")
    exit(1)

# Write back
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Successfully updated {MAIN_FILE}")
