# 企业微信多设备推送 - 测试指南

## ✅ 功能已部署

### 当前配置
```
租户: 傻小黑
推送设备列表: ["wechat", "my_claw"]
```

企微回复将同时推送到这两个设备。

---

## 🧪 测试步骤

### 方式 1: 使用测试脚本（推荐）

#### 1. 运行多设备测试脚本

```bash
cd E:/silly
python test_multi_devices.py
```

#### 2. 在企微中发送消息

在企微应用（傻小黑）中发送任意消息，例如：
- "测试多设备推送"
- "Hello"

#### 3. 查看测试窗口输出

预期输出：
```
============================================================
[wechat] [23:25:30] 收到企微回复!
============================================================
发送者: HughWang
内容: 测试多设备推送
============================================================

============================================================
[my_claw] [23:25:30] 收到企微回复!
============================================================
发送者: HughWang
内容: 测试多设备推送
============================================================
```

两个设备都应该收到相同的消息！

---

### 方式 2: 使用两个独立的客户端

#### 客户端 1: 绑定到 wechat

```bash
cd E:/silly
python test_ws_listen.py
```

#### 客户端 2: 绑定到 my_claw

修改 `test_ws_listen.py`：
```python
DEVICE_NAME = "my_claw"  # 改为 my_claw
```

然后运行：
```bash
python test_ws_listen_modified.py
```

在企微中发送消息，两个客户端都应该收到！

---

## 📋 配置管理

### 查看当前配置

```bash
curl -X GET \
  "https://webhook.sillymd.com/api/v1/tenants/{tenant_id}/wechat-config" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 更新设备列表

```bash
curl -X POST \
  "https://webhook.sillymd.com/api/v1/tenants/{tenant_id}/wechat-push-config" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "push_devices": ["wechat", "my_claw", "openclaw_01"]
  }'
```

### 添加更多设备

支持的设备名称：
- `wechat` - 企微回复专用
- `my_claw` - OpenClaw 设备
- `openclaw_01`, `openclaw_02`, ... - 多个 OpenClaw 实例
- 任何自定义设备名称

---

## 🔍 服务器日志查看

### 查看多设备推送日志

```bash
ssh -i e:/silly/md/.ignore/silly.pem root@webhook.sillymd.com \
  "journalctl -u webhook-hub -f | grep '企微回复已推送到设备'"
```

预期输出：
```
[WeChat] 企微回复已推送到设备: user_id=33, device=wechat, from_user=HughWang, msg_type=text
[WeChat] 企微回复已推送到设备: user_id=33, device=my_claw, from_user=HughWang, msg_type=text
```

---

## ✅ 验证清单

- [x] 数据库字段已添加
- [x] 服务代码已更新
- [x] 服务已重启
- [x] 傻小黑配置已更新
- [ ] 测试脚本运行成功
- [ ] 多个设备都收到消息
- [ ] 日志显示推送到所有设备

---

## 🎯 OpenClaw 配置

要使 OpenClaw 服务收到消息，确保它绑定到以下设备之一：

### 选项 A: 绑定到 "wechat"

```python
# OpenClaw 连接代码
await ws.send(json.dumps({
    "type": "bind",
    "device_name": "wechat"  # 使用 wechat
}))
```

### 选项 B: 绑定到 "my_claw"

```python
# OpenClaw 连接代码
await ws.send(json.dumps({
    "type": "bind",
    "device_name": "my_claw"  # 使用 my_claw
}))
```

### 选项 C: 添加到设备列表

如果 OpenClaw 使用其他设备名，更新配置：

```bash
UPDATE tenants
SET wechat_push_devices = '["wechat", "my_claw", "openclaw_01"]'
WHERE name = '傻小黑';
```

---

## 📞 需要帮助？

如遇问题，请检查：

1. **设备是否正确绑定？**
   - 查看服务器日志确认绑定成功

2. **设备列表是否正确？**
   - 查询数据库验证配置

3. **服务是否正常？**
   - 运行健康检查：`curl http://webhook.sillymd.com/health`

---

**现在可以开始测试了！** 🚀
