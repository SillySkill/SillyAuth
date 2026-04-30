# 后台管理API端点快速参考

**更新时间**: 2026-02-08
**版本**: v1.0
**状态**: ✅ 完整

---

## 快速导航

- [认证管理](#认证管理) - 4个端点
- [应用管理](#应用管理) - 6个端点
- [模块管理](#模块管理) - 6个端点
- [素材管理](#素材管理) - 6个端点
- [设备管理](#设备管理) - 7个端点
- [推送管理](#推送管理) - 7个端点
- [管理员用户管理](#管理员用户管理) - 7个端点 🔥
- [操作日志管理](#操作日志管理) - 6个端点 🔥
- [系统统计](#系统统计) - 7个端点 🔥
- [应用配置管理](#应用配置管理) - 5个端点

**总计**: 61个API端点

---

## 认证管理

**文件**: `api/admin_auth.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/admin/auth/login` | 管理员登录 |
| POST | `/api/admin/auth/logout` | 管理员登出 |
| GET | `/api/admin/auth/profile` | 获取个人信息 |
| PUT | `/api/admin/auth/password` | 修改密码 |

---

## 应用管理

**文件**: `api/admin_apps.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/apps` | 获取应用列表（分页、搜索） |
| POST | `/api/admin/apps` | 创建应用 |
| GET | `/api/admin/apps/<id>` | 获取应用详情 |
| PUT | `/api/admin/apps/<id>` | 更新应用 |
| DELETE | `/api/admin/apps/<id>` | 删除应用 |
| GET | `/api/admin/apps/<id>/stats` | 获取应用统计 |

---

## 模块管理

**文件**: `api/admin_modules.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/apps/<app_id>/modules` | 获取模块列表 |
| POST | `/api/admin/apps/<app_id>/modules` | 创建模块 |
| GET | `/api/admin/apps/<app_id>/modules/<module_key>` | 获取模块详情 |
| PUT | `/api/admin/apps/<app_id>/modules/<module_key>` | 更新模块 |
| DELETE | `/api/admin/apps/<app_id>/modules/<module_key>` | 删除模块 |
| POST | `/api/admin/apps/<app_id>/modules/<module_key>/toggle` | 切换模块状态 |

**模块类型**: `ai_show`, `quiz`, `lottery`, `inner`

---

## 素材管理

**文件**: `api/admin_assets.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/admin/apps/<app_id>/assets/upload` | 上传素材 |
| POST | `/api/admin/apps/<app_id>/assets/batch-upload` | 批量上传 |
| GET | `/api/admin/apps/<app_id>/assets` | 获取素材列表 |
| GET | `/api/admin/apps/<app_id>/assets/<asset_id>` | 获取素材详情 |
| PUT | `/api/admin/apps/<app_id>/assets/<asset_id>` | 更新素材 |
| DELETE | `/api/admin/apps/<app_id>/assets/<asset_id>` | 删除素材 |

**素材类型**: `image`, `video`, `audio`, `config`, `banner`

---

## 设备管理

**文件**: `api/admin_devices.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/apps/<app_id>/devices` | 获取设备列表 |
| GET | `/api/admin/apps/<app_id>/devices/online` | 获取在线设备 |
| GET | `/api/admin/apps/<app_id>/devices/<device_id>` | 获取设备详情 |
| DELETE | `/api/admin/apps/<app_id>/devices/<device_id>` | 解绑设备 |
| POST | `/api/admin/apps/<app_id>/devices/<device_id>/push` | 推送到设备 |
| GET | `/api/admin/apps/<app_id>/devices/stats` | 获取设备统计 |
| POST | `/api/admin/apps/<app_id>/devices/batch-unbind` | 批量解绑设备 |

---

## 推送管理

**文件**: `api/admin_push.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/admin/apps/<app_id>/push/tasks` | 创建推送任务 |
| GET | `/api/admin/apps/<app_id>/push/tasks` | 获取推送任务列表 |
| GET | `/api/admin/apps/<app_id>/push/tasks/<task_id>` | 获取任务详情 |
| POST | `/api/admin/apps/<app_id>/push/tasks/<task_id>/cancel` | 取消任务 |
| POST | `/api/admin/apps/<app_id>/push/tasks/<task_id>/retry` | 重试任务 |
| POST | `/api/admin/apps/<app_id>/push/broadcast` | 广播推送 |
| DELETE | `/api/admin/apps/<app_id>/push/tasks/<task_id>` | 删除任务 |

**推送类型**: `1`=配置更新, `2`=素材更新, `3`=全量更新

---

## 管理员用户管理 🔥 新增

**文件**: `api/admin_users.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/users` | 获取管理员列表 |
| POST | `/api/admin/users` | 创建管理员 |
| GET | `/api/admin/users/<id>` | 获取管理员详情 |
| PUT | `/api/admin/users/<id>` | 更新管理员 |
| DELETE | `/api/admin/users/<id>` | 删除管理员 |
| POST | `/api/admin/users/<id>/reset-password` | 重置密码 |
| POST | `/api/admin/users/<id>/toggle-status` | 切换状态 |

**角色**: `1`=超级管理员, `2`=应用管理员

---

## 操作日志管理 🔥 新增

**文件**: `api/admin_logs.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/logs` | 获取日志列表 |
| GET | `/api/admin/logs/<id>` | 获取日志详情 |
| GET | `/api/admin/logs/stats` | 获取日志统计 |
| DELETE | `/api/admin/logs/before/<date>` | 删除历史日志 |
| GET | `/api/admin/logs/operations` | 获取操作类型列表 |
| GET | `/api/admin/logs/export` | 导出日志（CSV） |

---

## 系统统计 🔥 新增

**文件**: `api/admin_stats.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/stats/overview` | 系统概览统计 |
| GET | `/api/admin/stats/apps` | 应用统计 |
| GET | `/api/admin/stats/devices` | 设备统计 |
| GET | `/api/admin/stats/assets` | 素材统计 |
| GET | `/api/admin/stats/push` | 推送统计 |
| GET | `/api/admin/stats/timeline` | 时间线数据 |
| GET | `/api/admin/stats/dashboard` | 仪表板数据 |

---

## 应用配置管理

**文件**: `api/admin_application_config.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/apps/<app_id>/config` | 获取应用配置 |
| PUT | `/api/admin/apps/<app_id>/config` | 更新应用配置 |
| POST | `/api/admin/apps/<app_id>/config/publish` | 发布配置版本 |
| GET | `/api/admin/apps/<app_id>/config/versions` | 获取配置版本历史 |
| POST | `/api/admin/apps/<app_id>/config/rollback` | 回滚到指定版本 |

---

## 通用参数

### 分页参数
```
page: 页码（默认1）
page_size: 每页数量（默认20）
```

### 搜索参数
```
keyword: 搜索关键词
status: 状态筛选（0/1）
start_date: 开始日期（YYYY-MM-DD）
end_date: 结束日期（YYYY-MM-DD）
```

### 认证
```
Authorization: Bearer <token>
```

---

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误描述"
}
```

---

## HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 客户端错误（参数错误） |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 快速测试

### 1. 获取Token
```bash
curl -X POST http://localhost:5000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'
```

### 2. 获取应用列表
```bash
curl -X GET http://localhost:5000/api/admin/apps \
  -H "Authorization: Bearer <token>"
```

### 3. 获取系统统计
```bash
curl -X GET http://localhost:5000/api/admin/stats/overview \
  -H "Authorization: Bearer <token>"
```

---

## 文件结构

```
backend/api/
├── admin_auth.py              # 认证管理 (4端点)
├── admin_users.py             # 管理员用户 (7端点) 🔥
├── admin_apps.py              # 应用管理 (6端点)
├── admin_modules.py           # 模块管理 (6端点)
├── admin_assets.py            # 素材管理 (6端点)
├── admin_devices.py           # 设备管理 (7端点)
├── admin_push.py              # 推送管理 (7端点)
├── admin_logs.py              # 操作日志 (6端点) 🔥
├── admin_stats.py             # 系统统计 (7端点) 🔥
└── admin_application_config.py # 应用配置 (5端点)
```

---

**总计**: 10个模块, 61个API端点
**状态**: ✅ 完整实现
**文档版本**: v1.0
**最后更新**: 2026-02-08
