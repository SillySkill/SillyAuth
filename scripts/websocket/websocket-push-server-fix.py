"""
服务器端 WebSocket 推送修复
在 /opt/webhook-hub/main.py 中应用此修复

问题: 当前服务器推送时未传递 tenant_id 参数，导致 device_id 格式不匹配
     客户端绑定: user_id:tenant_id:device_name
     服务器推送: user_id:device_name (缺失 tenant_id)

修复: 调用 notify_by_target 时传递 tenant_id 参数
"""

# ============ 修复说明 ============
#
# 在 main.py 中找到处理 webhook 的函数，搜索类似以下代码:
#
#   from ws_server import notify_device, notify_by_target
#
# 然后修改调用方式，确保传递 tenant_id:
#
# ============ 修复代码示例 ============

# 原代码 (不正确):
# await notify_by_target(
#     target_user_id=tenant.user_id,
#     target_device_name=device_name,
#     message=message
#     # ❌ 缺少 tenant_id 参数
# )

# 修复后代码 (正确):
# await notify_by_target(
#     target_user_id=tenant.user_id,
#     target_device_name=device_name,
#     tenant_id=tenant.id,  # ✅ 添加 tenant_id
#     message=message
# )

# ============ 企业微信 Webhook 推送修复 ============

"""
在企业微信处理函数中添加 WebSocket 推送:

在企业微信 webhook 处理函数中 (大约 line 1550 附近):

# 原注释说: "企业微信消息暂不进行 WebSocket 推送"
# 修改为以下代码:
"""

async def push_wechat_to_webhook(tenant, decrypted_xml, log_id):
    """
    企业微信消息推送到 WebSocket 设备

    参数:
        tenant: 租户对象
        decrypted_xml: 解密后的企业微信消息
        log_id: webhook 日志 ID
    """
    try:
        # 导入 WebSocket 推送函数
        from ws_server import notify_by_target
        import xml.etree.ElementTree as ET

        # 解析 XML 获取设备信息
        root = ET.fromstring(decrypted_xml)

        # 查询该租户的 OpenClaw 设备
        devices_result = await db.execute(
            text("""
                SELECT device_id, name
                FROM openclaw_devices
                WHERE tenant_id = :tenant_id
                  AND is_active = true
            """),
            {"tenant_id": tenant.id}
        )
        devices = devices_result.fetchall()

        if not devices:
            logger.info(f"[WeChat] 租户 {tenant.name} 无配置设备，跳过 WebSocket 推送")
            return

        # 构建推送消息
        ws_message = {
            "type": "wechat",
            "source": "wechat_webhook",
            "tenant_id": tenant.id,
            "tenant_name": tenant.name,
            "data": {
                "xml_content": decrypted_xml[:1000],  # 限制长度
                "msg_type": root.find('MsgType').text if root.find('MsgType') is not None else "unknown",
                "event": root.find('Event').text if root.find('Event') is not None else None,
                "from_user": root.find('FromUserName').text if root.find('FromUserName') is not None else None,
            },
            "timestamp": datetime.utcnow().isoformat(),
            "log_id": log_id
        }

        # 推送到所有活跃设备
        push_count = 0
        for device_row in devices:
            device_name = device_row.name

            try:
                # ✅ 关键修复: 传递 tenant_id 参数
                success = await notify_by_target(
                    target_user_id=tenant.user_id,
                    target_device_name=device_name,
                    tenant_id=tenant.id,  # ← 必须传递 tenant_id!
                    message=ws_message
                )

                if success:
                    push_count += 1
                    logger.info(f"[WeChat] WebSocket 推送成功: device={device_name}")
                else:
                    logger.warning(f"[WeChat] WebSocket 推送失败: device={device_name} (设备离线)")

            except Exception as push_err:
                logger.error(f"[WeChat] WebSocket 推送异常: device={device_name}, error={push_err}")

        logger.info(f"[WeChat] WebSocket 推送完成: {push_count}/{len(devices)} 个设备")

    except Exception as e:
        logger.error(f"[WeChat] WebSocket 推送异常: {e}")
        # 不影响主流程


# ============ 通用 Webhook 推送修复 ============

"""
对于通用 webhook 端点，同样需要确保传递 tenant_id:

async def handle_webhook_push(tenant, path, device_name, message_body):
    '''处理 webhook 并推送到 WebSocket'''

    # ... 验证和记录 webhook ...

    # 构建推送消息
    push_message = {
        "type": "webhook",
        "source": "webhook_hub",
        "path": path,
        "data": message_body,
        "timestamp": datetime.utcnow().isoformat()
    }

    # ✅ 修复: 传递 tenant_id
    success = await notify_by_target(
        target_user_id=tenant.user_id,
        target_device_name=device_name,
        tenant_id=tenant.id,  # ← 添加此参数
        message=push_message
    )

    if success:
        logger.info(f"[Webhook] 推送成功: device={device_name}")
    else:
        logger.warning(f"[Webhook] 推送失败: device={device_name} (设备离线)")
"""

# ============ 应用到服务器 ============
"""
# 在服务器上应用此修复:

1. SSH 到服务器
2. 编辑 /opt/webhook-hub/main.py
3. 找到 notify_by_target 调用处
4. 添加 tenant_id=tenant.id 参数
5. 重启服务: systemctl restart webhook-hub

或者使用以下命令直接应用:

ssh root@47.96.133.238 << 'EOF'
cd /opt/webhook-hub
# 备份
cp main.py main.py.bak

# 应用修复 (需要手动编辑)
# 或者使用 sed 命令批量替换

systemctl restart webhook-hub
systemctl status webhook-hub
EOF
"""
