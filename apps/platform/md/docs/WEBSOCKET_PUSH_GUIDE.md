# WebSocket 配置推送系统使用指南

## Phase 1 更新

> WebSocket 服务通过 `src/main.py` 启动, API 路径统一为 `/ws`。
> 旧 `server/api/` 中的 WebSocket 代码已废弃。

## 系统架构

```
┌─────────────────┐      WebSocket      ┌─────────────────┐
│   后端服务器      │ ──────────────────> │  Android 客户端  │
│                 │                     │                 │
│  - SocketIO     │ <────────────────── │  - OkHttp WS    │
│  - PushService  │      消息确认        │  - ConfigSync   │
└─────────────────┘                     └─────────────────┘
```

## 后端集成

### 1. 在应用启动时初始化推送系统

编辑 `manager.py` 或应用入口文件：

```python
from websocket import init_push_system

# 在创建 app 后初始化
socketio = init_push_system(app, db)

# 使用 socketio 运行应用
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### 2. 安装依赖

```bash
pip install flask-socketio
pip install python-socketio
```

更新 `requirements.txt`：

```
flask-socketio==5.3.0
python-socketio==5.9.0
```

### 3. API 端点

#### 创建推送任务

```bash
POST /api/push/config
Content-Type: application/json

{
    "version": "v1.2.0",
    "version_code": 120,
    "force_update": false,
    "release_notes": "修复了一些bug，优化了性能",
    "files": [
        {
            "path": "config.json",
            "size": 1024,
            "md5": "abc123...",
            "url": "/api/config/file?path=config.json",
            "compressed": false,
            "essential": true
        },
        {
            "path": "style/style.json",
            "size": 2048,
            "md5": "def456...",
            "url": "/api/config/file?path=style/style.json",
            "compressed": true,
            "essential": true
        }
    ],
    "target_devices": ["device_001", "device_002"],
    "target_groups": ["group_001"]
}
```

#### 启动推送任务

```bash
POST /api/push/<task_id>/start
```

#### 查询推送状态

```bash
GET /api/push/<task_id>
```

#### 取消推送任务

```bash
DELETE /api/push/<task_id>
```

#### 获取在线设备

```bash
GET /api/push/devices/online
```

## Android 客户端集成

### 1. 在 Application 中启动推送服务

```java
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();

        // 启动配置推送
        ConfigPushManager pushManager = ConfigPushManager.getInstance(this);
        pushManager.start();
    }
}
```

### 2. 在需要的地方监听推送

```java
public class MainActivity extends AppCompatActivity {
    private ConfigPushManager pushManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        pushManager = ConfigPushManager.getInstance(this);

        if (!pushManager.isConnected()) {
            // 显示连接中提示
            showConnectingDialog();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // 注意：不要在 Activity 销毁时停止推送，应该在整个应用生命周期保持连接
    }
}
```

### 3. 处理配置更新

`ConfigPushManager` 已经集成了配置更新处理逻辑：

1. 接收推送通知
2. 下载配置文件
3. 验证 MD5
4. 应用新配置
5. 发送确认

### 4. 自定义处理逻辑

如需自定义配置更新处理，可以修改 `ConfigPushManager.handleConfigUpdate()` 方法。

## WebSocket 消息协议

### 服务器 -> 客户端

#### connected - 连接确认

```json
{
    "connected": {
        "sid": "abc123",
        "device_id": "device_001",
        "server_time": "2026-02-06T10:00:00"
    }
}
```

#### config_update - 配置更新推送

```json
{
    "config_update": {
        "push_id": "uuid",
        "version": "v1.2.0",
        "version_code": 120,
        "force_update": false,
        "release_notes": "更新说明",
        "files": [
            {
                "path": "config.json",
                "size": 1024,
                "md5": "abc123...",
                "url": "/api/config/file?path=config.json",
                "compressed": false,
                "essential": true
            }
        ],
        "server_time": "2026-02-06T10:00:00"
    }
}
```

#### heartbeat_ack - 心跳确认

```json
{
    "heartbeat_ack": {
        "server_time": "2026-02-06T10:00:00",
        "device_time": "2026-02-06T10:00:00"
    }
}
```

#### error - 错误消息

```json
{
    "error": {
        "code": 401,
        "message": "Token 无效"
    }
}
```

### 客户端 -> 服务器

#### heartbeat - 心跳

```json
{
    "heartbeat": {
        "client_time": 1644123456789
    }
}
```

#### config_ack - 配置确认

```json
{
    "config_ack": {
        "push_id": "uuid",
        "status": "success",
        "message": "更新成功",
        "received_files": ["config.json", "style/style.json"],
        "failed_files": []
    }
}
```

#### device_status - 设备状态上报

```json
{
    "device_status": {
        "battery": 85,
        "storage": 1024,
        "network_type": "wifi",
        "app_version": "1.0.0",
        "config_version": "v1.1.0"
    }
}
```

## 测试

### 使用 wscat 测试 WebSocket 连接

```bash
# 安装 wscat
npm install -g wscat

# 连接到服务器
wscat -c "wss://api.jcoding.tech/ws?device_id=test_device&token=test_token"

# 发送心跳
{"heartbeat": {"client_time": 1644123456789}}

# 发送配置确认
{"config_ack": {"push_id": "uuid", "status": "success", "message": "OK", "received_files": [], "failed_files": []}}
```

### 使用 Postman 测试 API

1. 创建推送任务：
   - Method: POST
   - URL: https://api.jcoding.tech/api/push/config
   - Body: raw JSON（参考上面的请求示例）

2. 启动推送任务：
   - Method: POST
   - URL: https://api.jcoding.tech/api/push/{task_id}/start

3. 查询状态：
   - Method: GET
   - URL: https://api.jcoding.tech/api/push/{task_id}

## 监控和日志

### 服务器端日志

```python
import logging

# 启用详细日志
logging.getLogger('websocket.push_server').setLevel(logging.DEBUG)
logging.getLogger('services.push_service').setLevel(logging.DEBUG)
```

### 客户端日志

```bash
# 使用 logcat 查看 WebSocket 相关日志
adb logcat | grep ConfigPush
adb logcat | grep ConfigPushManager
adb logcat | grep ConfigSyncManager
```

## 故障排查

### 客户端无法连接

1. 检查服务器地址和端口
2. 检查 Token 是否有效
3. 检查网络连接
4. 查看 logcat 日志

### 推送未送达

1. 检查设备是否在线
2. 检查推送任务状态
3. 检查 WebSocket 连接状态
4. 查看服务器日志

### 配置更新失败

1. 检查文件 URL 是否可访问
2. 检查 MD5 校验是否通过
3. 检查存储空间是否充足
4. 查看错误日志

## 性能优化

### 服务器端

1. 使用 Redis 存储设备连接信息（当前使用内存）
2. 使用消息队列处理大批量推送
3. 实现推送任务分批处理

### 客户端

1. 优化心跳间隔
2. 实现增量配置更新
3. 使用断点续传下载大文件

## 安全建议

1. 使用 WSS（WebSocket over TLS）
2. 验证 Token 有效性
3. 实现设备认证机制
4. 限制推送频率
5. 记录所有推送操作日志

## 扩展功能

可以添加的功能：

1. 推送进度实时反馈
2. 设备分组管理
3. 推送优先级
4. 定时推送
5. 推送统计和分析
