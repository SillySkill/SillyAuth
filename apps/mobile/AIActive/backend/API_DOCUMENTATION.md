# 后台管理系统API文档

## 概述

本文档描述AI活动秀后台管理系统的所有API接口。

**基础URL**: `https://www.jcoding.chat/api/admin`

**认证方式**: JWT Token (Bearer Token)

## 认证相关

### 1. 管理员登录

```
POST /api/admin/auth/login
```

**请求Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "admin": {
      "id": 1,
      "username": "admin",
      "real_name": "超级管理员",
      "email": "admin@example.com",
      "role": 1,
      "role_name": "超级管理员"
    }
  }
}
```

### 2. 管理员登出

```
POST /api/admin/auth/logout
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "登出成功"
}
```

### 3. 获取个人信息

```
GET /api/admin/auth/profile
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "real_name": "超级管理员",
    "email": "admin@example.com",
    "phone": "13800138000",
    "role": 1,
    "role_name": "超级管理员",
    "status": 1,
    "last_login_at": "2026-02-07T10:30:00",
    "last_login_ip": "192.168.1.100",
    "created_at": "2026-01-01T00:00:00"
  }
}
```

### 4. 修改密码

```
PUT /api/admin/auth/password
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "old_password": "admin123",
  "new_password": "newpassword123"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

## 应用管理

### 1. 获取应用列表

```
GET /api/admin/apps
```

**Headers**: `Authorization: Bearer {token}`

**Query参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `keyword`: 搜索关键词（应用名称/应用Key）
- `status`: 状态筛选（0=禁用, 1=启用）
- `created_by`: 创建人ID筛选

**示例**:
```bash
curl -X GET "https://www.jcoding.chat/api/admin/apps?page=1&page_size=20&status=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "app_key": "ai_activity_show",
        "app_name": "AI活动秀",
        "app_name_en": "AI Activity Show",
        "app_description": "基于AI的活动展示应用",
        "app_icon": "https://...",
        "package_name": "com.jcoding.aiactivity",
        "version": "1.0.0",
        "status": 1,
        "created_by": 1,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-02-07T10:30:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

### 2. 创建应用

```
POST /api/admin/apps
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "app_name": "AI活动秀",
  "app_name_en": "AI Activity Show",
  "app_description": "基于AI的活动展示应用",
  "app_icon": "https://...",
  "package_name": "com.jcoding.aiactivity",
  "version": "1.0.0",
  "status": 1
}
```

**响应**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "app_key": "app_a1b2c3d4e5f6g7h8",
    "app_name": "AI活动秀",
    "version": "1.0.0",
    "status": 1
  }
}
```

### 3. 获取应用详情

```
GET /api/admin/apps/{app_id}
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "app_key": "ai_activity_show",
    "app_name": "AI活动秀",
    "app_name_en": "AI Activity Show",
    "app_description": "基于AI的活动展示应用",
    "app_icon": "https://...",
    "package_name": "com.jcoding.aiactivity",
    "version": "1.0.0",
    "status": 1,
    "created_by": 1,
    "creator": {
      "id": 1,
      "username": "admin",
      "real_name": "超级管理员"
    },
    "created_at": "2026-01-01T00:00:00",
    "updated_at": "2026-02-07T10:30:00"
  }
}
```

### 4. 更新应用

```
PUT /api/admin/apps/{app_id}
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "app_name": "新应用名称",
  "app_description": "新描述",
  "version": "1.0.1",
  "status": 1
}
```

**响应**:
```json
{
  "code": 200,
  "message": "更新成功"
}
```

### 5. 删除应用

```
DELETE /api/admin/apps/{app_id}
```

**Headers**: `Authorization: Bearer {token}`

**注意**: 仅超级管理员可删除，会级联删除所有关联数据

**响应**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

### 6. 获取应用统计

```
GET /api/admin/apps/{app_id}/stats
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "modules_count": 4,
    "assets_count": 150,
    "devices_count": 50,
    "online_devices_count": 30,
    "push_tasks_count": 10
  }
}
```

## 模块配置

### 1. 获取应用的所有模块

```
GET /api/admin/apps/{app_id}/modules
```

**Headers**: `Authorization: Bearer {token}`

**Query参数**:
- `enabled`: 是否只返回启用的模块（true/false）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "modules": [
      {
        "id": 1,
        "module_key": "ai_show",
        "module_name": "AI百变秀",
        "enabled": true,
        "config": {
          "invite_code_mode": true,
          "payment_mode": true,
          "employee_mode": true,
          "auto_close_time": 20,
          "enabled_styles": ["jst100001", "jst100002"]
        },
        "sort_order": 1,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-02-07T10:30:00"
      },
      {
        "id": 2,
        "module_key": "quiz",
        "module_name": "知识问答",
        "enabled": true,
        "config": {
          "voice_input": false,
          "color_theme": "tech_blue"
        },
        "sort_order": 2,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-02-07T10:30:00"
      }
    ]
  }
}
```

### 2. 创建模块

```
POST /api/admin/apps/{app_id}/modules
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "module_key": "ai_show",
  "module_name": "AI百变秀",
  "enabled": true,
  "config": {
    "invite_code_mode": true,
    "payment_mode": true,
    "employee_mode": true,
    "auto_close_time": 20,
    "enabled_styles": ["jst100001", "jst100002"]
  },
  "sort_order": 1
}
```

**响应**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "module_key": "ai_show",
    "module_name": "AI百变秀",
    "enabled": true
  }
}
```

### 3. 获取模块详情

```
GET /api/admin/apps/{app_id}/modules/{module_key}
```

**Headers**: `Authorization: Bearer {token}`

**示例**: `/api/admin/apps/1/modules/ai_show`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "app_id": 1,
    "module_key": "ai_show",
    "module_name": "AI百变秀",
    "enabled": true,
    "config": {
      "invite_code_mode": true,
      "payment_mode": true,
      "employee_mode": true,
      "auto_close_time": 20,
      "enabled_styles": ["jst100001", "jst100002"]
    },
    "sort_order": 1,
    "created_at": "2026-01-01T00:00:00",
    "updated_at": "2026-02-07T10:30:00"
  }
}
```

### 4. 更新模块配置

```
PUT /api/admin/apps/{app_id}/modules/{module_key}
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "module_name": "AI百变秀",
  "enabled": true,
  "config": {
    "invite_code_mode": false,
    "payment_mode": true
  },
  "sort_order": 1
}
```

**响应**:
```json
{
  "code": 200,
  "message": "更新成功"
}
```

### 5. 删除模块

```
DELETE /api/admin/apps/{app_id}/modules/{module_key}
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

### 6. 切换模块状态

```
POST /api/admin/apps/{app_id}/modules/{module_key}/toggle
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "enabled": false
}
```

**响应**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "enabled": false
  }
}
```

## 素材管理

### 1. 上传素材

```
POST /api/admin/apps/{app_id}/assets/upload
```

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

**Form参数**:
- `file`: 文件对象（必填）
- `asset_type`: 素材类型（image/video/audio/config/banner）
- `module_key`: 模块标识（可选）
- `asset_name`: 素材名称（可选，默认使用文件名）

**示例**:
```bash
curl -X POST "https://www.jcoding.chat/api/admin/apps/1/assets/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "asset_type=image" \
  -F "module_key=ai_show" \
  -F "asset_name=示例图片"
```

**响应**:
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "id": 1,
    "asset_key": "image_a1b2c3d4e5f6g7h8",
    "asset_name": "示例图片",
    "asset_type": "image",
    "file_url": "https://jc-st.oss-cn-shanghai.aliyuncs.com/admin/1/image/xxx.jpg",
    "file_size": 102400
  }
}
```

### 2. 批量上传素材

```
POST /api/admin/apps/{app_id}/assets/batch-upload
```

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

**Form参数**:
- `files`: 多个文件对象（必填）
- `asset_type`: 素材类型
- `module_key`: 模块标识（可选）

**响应**:
```json
{
  "code": 200,
  "message": "批量上传完成",
  "data": {
    "success_count": 5,
    "failed_count": 1,
    "failed_files": [
      {
        "filename": "error.jpg",
        "reason": "文件大小超过限制"
      }
    ],
    "uploaded_assets": [
      {
        "id": 1,
        "asset_key": "image_xxx",
        "asset_name": "image1.jpg",
        "file_url": "https://..."
      }
    ]
  }
}
```

### 3. 获取素材列表

```
GET /api/admin/apps/{app_id}/assets
```

**Headers**: `Authorization: Bearer {token}`

**Query参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `asset_type`: 素材类型筛选
- `module_key`: 模块筛选
- `keyword`: 搜索关键词

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "asset_key": "image_a1b2c3d4",
        "asset_name": "示例图片",
        "asset_type": "image",
        "module_key": "ai_show",
        "file_url": "https://...",
        "file_size": 102400,
        "mime_type": "image/jpeg",
        "status": 1,
        "created_at": "2026-02-07T10:30:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 4. 获取素材详情

```
GET /api/admin/apps/{app_id}/assets/{asset_id}
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "app_id": 1,
    "module_key": "ai_show",
    "asset_type": "image",
    "asset_key": "image_a1b2c3d4",
    "asset_name": "示例图片",
    "file_path": "admin/1/image/xxx.jpg",
    "file_url": "https://...",
    "file_size": 102400,
    "file_hash": "md5_hash_value",
    "mime_type": "image/jpeg",
    "metadata": {
      "width": 1920,
      "height": 1080
    },
    "status": 1,
    "uploaded_by": 1,
    "created_at": "2026-02-07T10:30:00",
    "updated_at": "2026-02-07T10:30:00"
  }
}
```

### 5. 更新素材信息

```
PUT /api/admin/apps/{app_id}/assets/{asset_id}
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "asset_name": "新名称",
  "status": 1
}
```

**响应**:
```json
{
  "code": 200,
  "message": "更新成功"
}
```

### 6. 删除素材

```
DELETE /api/admin/apps/{app_id}/assets/{asset_id}
```

**Headers**: `Authorization: Bearer {token}`

**注意**: 仅删除数据库记录，OSS文件需要手动清理

**响应**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

## 设备管理

### 1. 获取设备列表

```
GET /api/admin/apps/{app_id}/devices
```

**Headers**: `Authorization: Bearer {token}`

**Query参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `status`: 状态筛选（0=离线, 1=在线）
- `keyword`: 搜索关键词

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "device_id": "device_unique_id_001",
        "device_name": "展示设备1",
        "device_model": "Xiaomi 14",
        "os_version": "Android 14",
        "app_version": "1.0.0",
        "push_token": "firebase_push_token",
        "status": 1,
        "last_active_at": "2026-02-07T10:30:00",
        "inactive_seconds": 300,
        "created_at": "2026-01-01T00:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
}
```

### 2. 获取在线设备

```
GET /api/admin/apps/{app_id}/devices/online
```

**Headers**: `Authorization: Bearer {token}`

**Query参数**:
- `minutes`: 在线定义（分钟，默认30）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "online_count": 30,
    "devices": [
      {
        "id": 1,
        "device_id": "device_001",
        "device_name": "展示设备1",
        "device_model": "Xiaomi 14",
        "os_version": "Android 14",
        "app_version": "1.0.0",
        "last_active_at": "2026-02-07T10:30:00"
      }
    ]
  }
}
```

### 3. 获取设备详情

```
GET /api/admin/apps/{app_id}/devices/{device_id}
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "app_id": 1,
    "device_id": "device_001",
    "device_name": "展示设备1",
    "device_model": "Xiaomi 14",
    "os_version": "Android 14",
    "app_version": "1.0.0",
    "push_token": "firebase_push_token",
    "status": 1,
    "is_online": true,
    "last_active_at": "2026-02-07T10:30:00",
    "inactive_seconds": 300,
    "created_at": "2026-01-01T00:00:00",
    "updated_at": "2026-02-07T10:30:00"
  }
}
```

### 4. 解绑设备

```
DELETE /api/admin/apps/{app_id}/devices/{device_id}
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "解绑成功"
}
```

### 5. 获取设备统计

```
GET /api/admin/apps/{app_id}/devices/stats
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_devices": 100,
    "online_devices": 50,
    "offline_devices": 50,
    "version_distribution": {
      "1.0.0": 60,
      "1.0.1": 40
    }
  }
}
```

### 6. 推送配置到设备

```
POST /api/admin/apps/{app_id}/devices/{device_id}/push
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "message": "配置更新通知",
  "config_version": "v1.0.1"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "推送成功",
  "data": {
    "device_id": "device_001",
    "message": "配置更新通知",
    "config_version": "v1.0.1"
  }
}
```

### 7. 批量解绑设备

```
POST /api/admin/apps/{app_id}/devices/batch-unbind
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "device_ids": ["device_001", "device_002", "device_003"]
}
```

**响应**:
```json
{
  "code": 200,
  "message": "批量解绑成功",
  "data": {
    "deleted_count": 3
  }
}
```

## 推送管理

### 1. 创建推送任务

```
POST /api/admin/apps/{app_id}/push/tasks
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "task_name": "配置更新推送",
  "push_type": 1,
  "target_devices": ["device_001", "device_002"],
  "config_version": "v1.0.1",
  "message": "更新通知"
}
```

**push_type说明**:
- 1: 配置更新
- 2: 素材更新
- 3: 全量更新

如果`target_devices`为空数组，则推送到所有设备

**响应**:
```json
{
  "code": 200,
  "message": "推送任务已创建",
  "data": {
    "id": 1,
    "task_name": "配置更新推送",
    "push_type": 1,
    "target_devices": ["device_001", "device_002"],
    "total_devices": 2,
    "config_version": "v1.0.1",
    "status": 0
  }
}
```

### 2. 获取推送任务列表

```
GET /api/admin/apps/{app_id}/push/tasks
```

**Headers**: `Authorization: Bearer {token}`

**Query参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `status`: 状态筛选（0=待推送, 1=推送中, 2=完成, 3=部分失败）
- `push_type`: 推送类型筛选

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "task_name": "配置更新推送",
        "push_type": 1,
        "push_type_name": "配置更新",
        "target_devices": ["device_001", "device_002"],
        "total_devices": 2,
        "success_count": 2,
        "failed_count": 0,
        "progress": 100,
        "config_version": "v1.0.1",
        "status": 2,
        "status_name": "完成",
        "error_message": null,
        "created_by": 1,
        "created_at": "2026-02-07T10:00:00",
        "completed_at": "2026-02-07T10:05:00"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

### 3. 获取推送任务详情

```
GET /api/admin/apps/{app_id}/push/tasks/{task_id}
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "app_id": 1,
    "task_name": "配置更新推送",
    "push_type": 1,
    "push_type_name": "配置更新",
    "target_devices": ["device_001", "device_002"],
    "config_version": "v1.0.1",
    "status": 2,
    "status_name": "完成",
    "total_devices": 2,
    "success_count": 2,
    "failed_count": 0,
    "progress": 100,
    "error_message": null,
    "created_by": 1,
    "created_at": "2026-02-07T10:00:00",
    "completed_at": "2026-02-07T10:05:00"
  }
}
```

### 4. 取消推送任务

```
POST /api/admin/apps/{app_id}/push/tasks/{task_id}/cancel
```

**Headers**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 200,
  "message": "任务已取消"
}
```

### 5. 重试推送任务

```
POST /api/admin/apps/{app_id}/push/tasks/{task_id}/retry
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "retry_failed_only": true
}
```

**响应**:
```json
{
  "code": 200,
  "message": "重试任务已创建",
  "data": {
    "id": 2,
    "task_name": "配置更新推送 (重试)",
    "total_devices": 5
  }
}
```

### 6. 广播推送

```
POST /api/admin/apps/{app_id}/push/broadcast
```

**Headers**: `Authorization: Bearer {token}`

**请求Body**:
```json
{
  "message": "系统维护通知",
  "data": {
    "maintenance_time": "2026-02-08 02:00:00",
    "duration": "2小时"
  }
}
```

**响应**:
```json
{
  "code": 200,
  "message": "广播成功",
  "data": {
    "message": "系统维护通知",
    "data": {
      "maintenance_time": "2026-02-08 02:00:00",
      "duration": "2小时"
    }
  }
}
```

### 7. 删除推送任务

```
DELETE /api/admin/apps/{app_id}/push/tasks/{task_id}
```

**Headers**: `Authorization: Bearer {token}`

**注意**: 只能删除已完成或已取消的任务

**响应**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 测试账号

```
用户名: admin
密码: admin123
```

## 注意事项

1. 所有需要认证的接口都必须在请求头中携带JWT Token:
   ```
   Authorization: Bearer YOUR_TOKEN
   ```

2. 分页参数从1开始

3. 时间格式均为ISO 8601格式: `2026-02-07T10:30:00`

4. 文件上传大小限制为50MB

5. 支持的图片格式: PNG, JPG, JPEG, GIF, WEBP, SVG

6. 30分钟内有活动的设备视为在线

7. 推送任务状态:
   - 0: 待推送
   - 1: 推送中
   - 2: 完成
   - 3: 部分失败
   - 4: 已取消
