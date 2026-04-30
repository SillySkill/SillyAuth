"""
企业微信 WebSocket 推送功能补丁
添加到 /opt/webhook-hub/main.py 的企业微信处理函数中
"""

# 在企业微信处理函数中，"企业微信消息暂不进行 WebSocket 推送" 注释之后，
# 添加以下代码：

# ========== 开始：WebSocket 推送功能 ==========

    # 解析企业微信 XML 消息，提取用户标识
    try:
        import xml.etree.ElementTree as ET
        if decrypted_xml:
            root = ET.fromstring(decrypted_xml)

            # 提取用户ID（企业微信消息格式）
            # 可能的字段：UserID, FromUserName, ToUserName
            user_id_node = root.find('.//UserID')
            from_user_node = root.find('FromUserName')

            wechat_user_id = None
            if user_id_node is not None:
                wechat_user_id = user_id_node.text
                logger.info(f"[WeChat] 从 UserID 字段提取到用户: {wechat_user_id}")
            elif from_user_node is not None:
                wechat_user_id = from_user_node.text
                logger.info(f"[WeChat] 从 FromUserName 字段提取到用户: {wechat_user_id}")

            # 如果提取到了用户标识，查询该用户的设备并推送
            if wechat_user_id:
                # 查询该租户下配置的 OpenClaw 设备
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

                if devices:
                    logger.info(f"[WeChat] 找到 {len(devices)} 个设备，准备 WebSocket 推送")

                    # 构建 WebSocket 推送消息
                    ws_message = {
                        "type": "wechat",
                        "source": "wechat_webhook",
                        "wechat_user_id": wechat_user_id,
                        "tenant_id": tenant.id,
                        "tenant_name": tenant.name,
                        "data": {
                            "xml_content": decrypted_xml[:1000],  # 限制长度
                            "msg_type": root.find('MsgType').text if root.find('MsgType') is not None else "unknown",
                            "event": root.find('Event').text if root.find('Event') is not None else None
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                        "log_id": log_id
                    }

                    # 推送到所有在线设备
                    push_count = 0
                    for device_row in devices:
                        device_name = device_row.name
                        device_id = device_row.device_id

                        try:
                            # 导入 WebSocket 推送函数
                            from ws_server import notify_by_target

                            # 异步推送消息
                            await notify_by_target(
                                target_user_id=tenant.user_id,
                                target_device_name=device_name,
                                message=ws_message
                            )
                            push_count += 1
                            logger.info(f"[WeChat] WebSocket 推送成功: device={device_name}, wechat_user={wechat_user_id}")

                        except Exception as push_err:
                            logger.error(f"[WeChat] WebSocket 推送失败: device={device_name}, error={push_err}")

                    logger.info(f"[WeChat] WebSocket 推送完成: 成功 {push_count}/{len(devices)} 个设备")

                else:
                    logger.info(f"[WeChat] 租户 {tenant.name} 未配置 OpenClaw 设备，跳过 WebSocket 推送")
            else:
                logger.warning(f"[WeChat] 无法从消息中提取用户标识，跳过 WebSocket 推送")

    except Exception as ws_err:
        logger.error(f"[WeChat] WebSocket 推送异常: {ws_err}")
        # 不影响主流程，继续执行转发

# ========== 结束：WebSocket 推送功能 ==========
