# 应用配置管理 API 文档

## 概述

应用配置管理API提供完整的配置管理功能，包括创建、读取、更新、删除配置，以及配置验证和重置功能。

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0+ (使用 SQLAlchemy 异步 ORM)
- **认证**: JWT (与后台管理系统共用)
- **端口**: 8000 (与Flask主应用的5000端口分离)

## 数据库表结构

### application_configs

```sql
CREATE TABLE application_configs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    app_id VARCHAR(100) NOT NULL UNIQUE COMMENT '统一应用标识',
    app_name VARCHAR(100) NOT NULL COMMENT '应用名称',
    package_name VARCHAR(100) COMMENT '包名',
    version VARCHAR(20) COMMENT '版本号',
    config JSON NOT NULL COMMENT 'JSON配置，存储所有配置项',
    status SMALLINT DEFAULT 1 COMMENT '状态: 1=启用, 0=禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_app_id (app_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## API 端点

### 基础URL
```
http://your-server:8000/api/admin/application/config
```

### 认证

所有API都需要JWT认证，在请求头中携带：
```
Authorization: Bearer <your-jwt-token>
```

### 1. 获取配置列表

**GET** `/api/admin/application/config`

**Query参数:**
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20, 最大: 100)
- `keyword`: 搜索关键词 (搜索app_name, app_id, package_name)
- `status`: 状态筛选 (1=启用, 0=禁用)

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "app_id": "com.jcoding.aiactivity",
        "app_name": "AI活动秀",
        "package_name": "com.jcoding.aiactivity",
        "version": "1.0.0",
        "config": {...},
        "status": 1,
        "created_at": "2026-02-07T12:00:00",
        "updated_at": "2026-02-07T12:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

### 2. 获取单个应用配置

**GET** `/api/admin/application/config/{app_id}`

**路径参数:**
- `app_id`: 应用标识 (如: com.jcoding.aiactivity)

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "app_id": "com.jcoding.aiactivity",
    "app_name": "AI活动秀",
    "package_name": "com.jcoding.aiactivity",
    "version": "1.0.0",
    "config": {
      "app": {
        "name": "AI活动秀",
        "version": "1.0.0",
        "debug": true
      },
      "features": {
        "ai_show": {
          "enabled": true,
          "invite_code_mode": true,
          "payment_mode": true,
          "employee_mode": true,
          "auto_close_time": 20
        },
        "quiz": {
          "enabled": true,
          "voice_input": false,
          "push_prize": true
        },
        "lottery": {
          "enabled": true,
          "voice_trigger": false,
          "push_winner": true
        },
        "inner_show": {
          "enabled": true,
          "digital_human_announce": true
        }
      }
    },
    "status": 1,
    "created_at": "2026-02-07T12:00:00",
    "updated_at": "2026-02-07T12:00:00"
  }
}
```

### 3. 创建应用配置

**POST** `/api/admin/application/config`

**请求体:**
```json
{
  "app_id": "com.jcoding.aiactivity",
  "app_name": "AI活动秀",
  "package_name": "com.jcoding.aiactivity",
  "version": "1.0.0",
  "config": {
    "app": {...},
    "features": {...}
  }
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "app_id": "com.jcoding.aiactivity",
    "app_name": "AI活动秀",
    "version": "1.0.0"
  }
}
```

### 4. 完整更新配置

**PUT** `/api/admin/application/config/{app_id}`

**请求体:** 所有字段都是可选的，只更新提供的字段
```json
{
  "app_name": "AI活动秀(新版本)",
  "config": {
    "app": {...},
    "features": {...}
  }
}
```

**注意:** 这是完整替换，config字段会完全覆盖原有配置。

### 5. 部分更新配置 (推荐)

**PATCH** `/api/admin/application/config/{app_id}`

**请求体:** 会与现有配置合并
```json
{
  "config": {
    "features": {
      "quiz": {
        "enabled": false
      }
    }
  }
}
```

**注意:** 只更新指定的字段，其他字段保持不变。推荐使用此方法进行配置更新。

### 6. 删除配置

**DELETE** `/api/admin/application/config/{app_id}`

**权限:** 仅超级管理员

**响应示例:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

### 7. 获取配置结构

**GET** `/api/admin/application/config/{app_id}/schema`

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "app_id": "com.jcoding.aiactivity",
    "current_config": {...},
    "schema": {...},
    "default_config": {...},
    "ui_schema": {...}
  }
}
```

**用途:** 前端可以使用schema和ui_schema动态生成配置表单。

### 8. 重置为默认配置

**POST** `/api/admin/application/config/{app_id}/reset`

**响应示例:**
```json
{
  "code": 200,
  "message": "重置成功",
  "data": {
    "config": {
      "app": {...},
      "features": {...}
    }
  }
}
```

### 9. 验证配置

**POST** `/api/admin/application/config/{app_id}/validate`

**请求体:** 要验证的配置
```json
{
  "app": {...},
  "features": {...}
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "验证完成",
  "data": {
    "valid": true,
    "errors": []
  }
}
```

**用途:** 在保存前验证配置是否正确，不实际保存到数据库。

### 10. 获取配置修改历史

**GET** `/api/admin/application/config/{app_id}/history`

**Query参数:**
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20)

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 123,
        "operation": "update_config",
        "operation_desc": "更新应用配置: AI活动秀",
        "request_ip": "192.168.1.100",
        "status": 1,
        "created_at": "2026-02-07T12:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

## 配置结构说明

### 配置Schema

配置分为两个主要部分：

1. **app**: 应用基础信息
   - `name` (string, required): 应用名称
   - `version` (string): 版本号，格式为 x.y.z
   - `debug` (boolean): 调试模式

2. **features**: 功能模块配置
   - **ai_show**: AI百变秀配置
     - `enabled` (boolean): 启用
     - `invite_code_mode` (boolean): 邀请码模式
     - `payment_mode` (boolean): 支付模式
     - `employee_mode` (boolean): 员工模式
     - `auto_close_time` (integer, 5-300): 自动关闭时间(秒)

   - **quiz**: 知识问答配置
     - `enabled` (boolean): 启用
     - `voice_input` (boolean): 语音输入
     - `push_prize` (boolean): 推送奖品信息

   - **lottery**: 幸运抽奖配置
     - `enabled` (boolean): 启用
     - `voice_trigger` (boolean): 语音触发抽奖
     - `push_winner` (boolean): 推送中奖信息

   - **inner_show**: 内场秀配置
     - `enabled` (boolean): 启用
     - `digital_human_announce` (boolean): 数字人播报

### 配置验证规则

- **类型验证**: 每个字段必须符合指定的数据类型
- **必填验证**: 必填字段不能为空
- **格式验证**: version字段必须匹配 x.y.z 格式
- **范围验证**: auto_close_time必须在5-300之间

## 部署说明

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 创建数据库表

```bash
python scripts/create_application_config_table.py
```

### 3. 启动服务

**开发环境:**
```bash
python fastapi_app.py
# 服务运行在 http://localhost:8000
```

**生产环境:**
```bash
# 使用uvicorn启动
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 使用systemd管理 (Linux)

创建 `/etc/systemd/system/aiactivity-fastapi.service`:

```ini
[Unit]
Description=AI活动秀 FastAPI服务
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aiactivity-fastapi
sudo systemctl start aiactivity-fastapi
```

## 使用示例

### Python示例

```python
import requests

# 1. 登录获取token
login_response = requests.post('http://localhost:8000/api/admin/auth/login', json={
    'username': 'admin',
    'password': 'your-password'
})
token = login_response.json()['data']['token']

# 2. 获取配置
headers = {'Authorization': f'Bearer {token}'}
config_response = requests.get(
    'http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity',
    headers=headers
)
config = config_response.json()['data']

# 3. 部分更新配置
update_response = requests.patch(
    'http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity',
    headers=headers,
    json={
        'config': {
            'features': {
                'quiz': {
                    'enabled': False
                }
            }
        }
    }
)
```

### cURL示例

```bash
# 1. 登录获取token
TOKEN=$(curl -X POST http://localhost:8000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  | jq -r '.data.token')

# 2. 获取配置
curl http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity \
  -H "Authorization: Bearer $TOKEN"

# 3. 部分更新配置
curl -X PATCH http://localhost:8000/api/admin/application/config/com.jcoding.aiactivity \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "features": {
        "quiz": {
          "enabled": false
        }
      }
    }
  }'
```

## 错误码说明

- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权（token无效或过期）
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 注意事项

1. **端口冲突**: FastAPI运行在8000端口，Flask运行在5000端口，确保两个端口都不被占用
2. **JWT认证**: 需要先调用 `/api/admin/auth/login` 获取token
3. **配置验证**: 所有配置更新都会经过验证，不符合规则的配置会被拒绝
4. **操作日志**: 所有配置修改操作都会记录到 `admin_operation_logs` 表
5. **权限控制**: 删除操作仅限超级管理员

## 与现有系统的集成

### 与Flask主应用的关系

- **Flask (5000端口)**: 原有的API服务，处理图片生成、上传等功能
- **FastAPI (8000端口)**: 新增的后台管理API，处理配置管理

两个服务可以同时运行，互不干扰。前端需要根据功能调用不同的服务。

### 数据库共享

两个服务使用同一个MySQL数据库，确保数据一致性。

### 配置同步

Android客户端可以继续使用现有的Flask API `/api/config/sync` 获取配置，该接口会从 `application_configs` 表读取数据。
