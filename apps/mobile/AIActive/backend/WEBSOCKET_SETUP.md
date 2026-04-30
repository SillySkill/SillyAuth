# WebSocket 推送服务部署指南

## 概述

WebSocket服务为Android客户端提供实时配置推送功能，支持：
- 设备连接管理
- 心跳保活
- 配置更新推送
- 广播消息
- 设备状态上报

## 架构说明

```
Android客户端                WebSocket服务器            推送管理API
     │                            │                         │
     ├─── WebSocket连接 ────────> │                         │
     │<─── connected ──────────── │                         │
     │                            │                         │
     ├─── heartbeat ───────────> │                         │
     │<─── heartbeat_ack ─────── │                         │
     │                            │                         │
     │                            │<─── 创建推送任务 ───────│
     │                            │                         │
     │<─── config_update ─────── │                         │
     │                            │                         │
     ├─── config_ack ──────────> │─── 更新任务状态 ──────>│
     │                            │                         │
     ├─── device_status ───────> │                         │
```

## 安装步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

新增依赖：
- `Flask-Sock==0.7.0` - WebSocket支持

### 2. 验证安装

```bash
python -c "from flask_sock import Sock; print('Flask-Sock installed successfully')"
```

### 3. 配置环境变量

创建 `.env` 文件（如果不存在）：

```bash
cp .env.example .env
```

确保配置以下变量：

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://...
```

## 启动服务

### 开发环境

```bash
cd backend
python app.py
```

服务将在 `http://localhost:5000` 启动
WebSocket端点: `ws://localhost:5000/ws`

### 生产环境 (使用Gunicorn)

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 -k geventwebsocket worker:app
```

或使用启动脚本：

```bash
./deploy_baota.sh
```

## 测试WebSocket服务

### 1. 运行自动化测试

```bash
# 安装测试依赖
pip install websockets

# 运行测试
python test_websocket.py
```

### 2. 手动测试 (使用wscat)

安装wscat：
```bash
npm install -g wscat
```

连接测试：
```bash
wscat -c "ws://localhost:5000/ws?device_id=test001&token=temp_token_test001"
```

发送心跳：
```json
{"heartbeat": {"client_time": "2024-01-01T00:00:00"}}
```

### 3. 测试推送功能

#### 创建推送任务

```bash
curl -X POST http://localhost:5000/api/admin/apps/1/push/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "task_name": "测试推送",
    "push_type": 1,
    "target_devices": ["test001"],
    "config_version": "1.0.1"
  }'
```

#### 广播消息

```bash
curl -X POST http://localhost:5000/api/admin/apps/1/push/broadcast \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "message": "系统通知",
    "data": {"key": "value"}
  }'
```

#### 查看在线设备

```bash
curl http://localhost:5000/api/admin/apps/1/devices/online \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Android客户端配置

客户端已集成推送功能，连接地址配置：

**文件**: `android/app/src/main/java/com/jcoding/aiactivity/network/ConfigPushClient.java`

```java
private String buildServerUrl() {
    return "api.jcoding.tech";  // 修改为你的服务器地址
}
```

### 本地测试配置

将服务器地址改为 `localhost` 或局域网IP：

```java
private String buildServerUrl() {
    return "192.168.1.100";  // 局域网IP
    // return "10.0.2.2";     // Android模拟器访问主机
}
```

## 监控和日志

### 查看连接日志

```bash
# 实时查看WebSocket连接日志
tail -f /var/log/gunicorn/access.log | grep ws
```

### 查看推送日志

Android客户端logcat：

```bash
adb logcat | grep -E "ConfigPush|WebSocket"
```

## 故障排除

### 问题1: 连接被拒绝 (HTTP 400)

**原因**: 缺少必填参数 `device_id` 或 `token`

**解决**: 确保URL包含必要参数
```
ws://server/ws?device_id=xxx&token=xxx
```

### 问题2: 连接失败 (Expected HTTP 101)

**原因**: 服务器不支持WebSocket或WSGI配置错误

**解决**:
- 检查是否安装了 `flask-sock`
- 使用正确的worker类型: `-k geventwebsocket`

### 问题3: 频繁断线重连

**原因**: 心跳超时或网络不稳定

**解决**:
- 检查心跳间隔（默认30秒）
- 检查网络连接稳定性
- 调整服务器超时设置

### 问题4: 推送消息未收到

**原因**: 设备未连接或会话已过期

**解决**:
- 检查设备是否在线: `ws_server.get_connected_devices()`
- 查看Android客户端日志确认连接状态
- 重新创建推送任务

## 生产环境部署

### Nginx反向代理配置

```nginx
# WebSocket代理配置
location /ws {
    proxy_pass http://127.0.0.1:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

### SSL/TLS配置

生产环境建议使用WSS (WebSocket Secure):

```nginx
location /ws {
    proxy_pass https://127.0.0.1:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    # ... 其他配置
}
```

客户端修改为：
```java
private static final String WS_SCHEME = "wss://";
```

### 负载均衡

多实例部署时，需要使用Redis Pub/Sub或消息队列实现跨服务器推送：

```python
# TODO: 实现Redis Pub/Sub
import redis
redis_client = redis.Redis()

# 发布消息
redis_client.publish(f'device:{device_id}', message)
```

## API参考

### WebSocket消息类型

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| connected | 服务→客户端 | 连接确认 |
| heartbeat | 客户端→服务 | 心跳 |
| heartbeat_ack | 服务→客户端 | 心跳确认 |
| config_update | 服务→客户端 | 配置更新推送 |
| config_ack | 客户端→服务 | 配置更新确认 |
| device_status | 客户端→服务 | 设备状态上报 |
| broadcast | 服务→客户端 | 广播消息 |

### REST API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/admin/apps/<id>/push/tasks` | POST | 创建推送任务 |
| `/api/admin/apps/<id>/push/tasks` | GET | 获取任务列表 |
| `/api/admin/apps/<id>/push/tasks/<id>` | GET | 获取任务详情 |
| `/api/admin/apps/<id>/push/broadcast` | POST | 广播消息 |
| `/ws` | WebSocket | WebSocket连接 |

## 维护

### 重启服务

```bash
# 开发环境
pkill -f "python app.py"
python app.py &

# 生产环境
sudo systemctl restart gunicorn
```

### 查看连接统计

在Python shell中：

```python
from websocket_server import websocket_server

# 查看连接数
print(websocket_server.get_connection_count())

# 查看在线设备
for device in websocket_server.get_connected_devices():
    print(device)
```

## 后续优化

- [ ] 实现Redis Pub/Sub支持多实例部署
- [ ] 添加JWT token验证
- [ ] 实现消息持久化和离线推送
- [ ] 添加推送进度实时通知
- [ ] 实现设备分组推送
- [ ] 添加推送统计和报表
