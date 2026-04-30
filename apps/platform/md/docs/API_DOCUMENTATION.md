# SillyMD API 文档 v2.0

> 基于 FastAPI 模块化架构，统一 `/api/v1/` 前缀

## 基础信息

- **Base URL**: `/api/v1`
- **认证方式**: JWT Bearer Token (HS256)
- **响应格式**: JSON
- **字符编码**: UTF-8
- **入口**: `src/main.py` (PluginManager.load_all_modules)

## 统一响应格式

所有 API 返回统一 JSON 格式:

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

### 通用状态码

| code | 说明 |
|------|------|
| 200 | 操作成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 (Token 无效或过期) |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 分页响应格式

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": []
  }
}
```

---

## 1. 认证模块 (auth)

**Base**: `/api/v1/auth`

### 1.1 登录

```
POST /auth/login
```

**请求体**

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@sillymd.com",
      "role": "admin",
      "avatar": "https://..."
    }
  }
}
```

### 1.2 注册

```
POST /auth/register
```

**请求体**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 (3-32字符) |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 (6-128字符) |

```json
{
  "username": "new_user",
  "email": "new_user@example.com",
  "password": "securepassword"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "id": 2,
    "username": "new_user",
    "email": "new_user@example.com",
    "role": "user"
  }
}
```

### 1.3 获取当前用户

```
GET /auth/me
```

**请求头**

```
Authorization: Bearer <access_token>
```

**响应**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@sillymd.com",
    "role": "admin",
    "avatar": "https://...",
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

### 1.4 刷新 Token

```
POST /auth/refresh
```

**请求体**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**响应**

```json
{
  "code": 200,
  "msg": "Token 刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

---

## 2. 管理模块 (admin)

**Base**: `/api/v1/admin`

**权限要求**: admin

### 2.1 用户列表

```
GET /admin/users
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20 |
| keyword | string | 否 | 搜索关键词 (用户名/邮箱) |
| role | string | 否 | 角色筛选 |
| status | integer | 否 | 状态筛选 |

**响应**

```json
{
  "code": 200,
  "data": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@sillymd.com",
        "role": "admin",
        "status": 1,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 2.2 模块列表

```
GET /admin/modules
```

**响应**

```json
{
  "code": 200,
  "data": {
    "modules": [
      {
        "name": "auth",
        "enabled": true,
        "version": "2.0.0",
        "status": "running"
      },
      {
        "name": "cms",
        "enabled": true,
        "version": "2.0.0",
        "status": "running"
      }
    ]
  }
}
```

### 2.3 启用模块

```
POST /admin/modules/{id}/enable
```

**响应**

```json
{
  "code": 200,
  "msg": "模块已启用",
  "data": { "module": "payment", "enabled": true }
}
```

### 2.4 禁用模块

```
POST /admin/modules/{id}/disable
```

**响应**

```json
{
  "code": 200,
  "msg": "模块已禁用",
  "data": { "module": "payment", "enabled": false }
}
```

---

## 3. 内容管理模块 (cms)

**Base**: `/api/v1/cms`

### 3.1 文章列表 (分页)

```
GET /cms/articles
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20 |
| category_id | integer | 否 | 分类 ID |
| status | string | 否 | 状态筛选 (published/draft) |
| keyword | string | 否 | 搜索关键词 |

### 3.2 文章详情

```
GET /cms/articles/{id}
```

**响应**

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "Getting Started with AI Skills",
    "slug": "getting-started-ai-skills",
    "content": "# Markdown content...",
    "category_id": 1,
    "author_id": 1,
    "status": "published",
    "view_count": 1234,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-04-20T08:30:00Z"
  }
}
```

### 3.3 创建文章

```
POST /cms/articles
```

**请求体**

```json
{
  "title": "New Article Title",
  "content": "# Markdown Content",
  "category_id": 1,
  "status": "published",
  "tags": ["AI", "tutorial"],
  "featured_image": "https://..."
}
```

### 3.4 更新文章

```
PUT /cms/articles/{id}
```

**请求体**

```json
{
  "title": "Updated Title",
  "content": "# Updated Content",
  "status": "published"
}
```

### 3.5 删除文章

```
DELETE /cms/articles/{id}
```

**响应**

```json
{
  "code": 200,
  "msg": "文章已删除"
}
```

### 3.6 分类列表

```
GET /cms/categories
```

**响应**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "Tutorials",
      "slug": "tutorials",
      "parent_id": null,
      "sort_order": 1,
      "article_count": 25
    }
  ]
}
```

### 3.7 创建分类

```
POST /cms/categories
```

**请求体**

```json
{
  "name": "AI Skills",
  "slug": "ai-skills",
  "parent_id": null,
  "sort_order": 2
}
```

### 3.8 更新分类

```
PUT /cms/categories/{id}
```

### 3.9 删除分类

```
DELETE /cms/categories/{id}
```

### 3.10 获取导航

```
GET /cms/navigation
```

**响应**

```json
{
  "code": 200,
  "data": {
    "primary": [
      { "label": "Home", "url": "/", "children": [] },
      { "label": "Skills", "url": "/skills", "children": [] }
    ],
    "footer": [
      { "label": "About", "url": "/about" },
      { "label": "Contact", "url": "/contact" }
    ]
  }
}
```

### 3.11 更新导航

```
PUT /cms/navigation
```

**请求体**

```json
{
  "primary": [
    { "label": "Skills", "url": "/skills", "children": [] }
  ],
  "footer": []
}
```

---

## 4. 支付模块 (payment)

**Base**: `/api/v1/payment`

**权限要求**: 认证用户

### 4.1 创建支付

```
POST /payment/create
```

**请求体**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order_id | string | 是 | 订单编号 |
| amount | number | 是 | 金额 (分) |
| method | string | 是 | 支付方式 (wechat/alipay/paypal) |
| description | string | 否 | 支付描述 |

```json
{
  "order_id": "ORD-20260430-001",
  "amount": 2999,
  "method": "wechat",
  "description": "Skill Purchase - AI Trading Bot"
}
```

**响应**

```json
{
  "code": 200,
  "data": {
    "payment_id": "PAY-20260430-001",
    "status": "pending",
    "qr_code": "https://...",
    "expires_at": "2026-04-30T12:30:00Z"
  }
}
```

### 4.2 查询支付

```
GET /payment/{id}
```

### 4.3 支付回调通知

```
POST /payment/notify/{provider}
```

**路径参数**: provider = wechat | alipay | paypal

### 4.4 退款

```
POST /payment/refund
```

**请求体**

```json
{
  "payment_id": "PAY-20260430-001",
  "amount": 2999,
  "reason": "Customer request"
}
```

### 4.5 获取支付方式

```
GET /payment/methods
```

**响应**

```json
{
  "code": 200,
  "data": [
    { "method": "wechat", "name": "微信支付", "enabled": true },
    { "method": "alipay", "name": "支付宝", "enabled": true },
    { "method": "paypal", "name": "PayPal", "enabled": true }
  ]
}
```

### 4.6 PayPal 捕获

```
POST /payment/paypal/capture/{id}
```

### 4.7 创建订单

```
POST /payment/orders
```

**请求体**

```json
{
  "skill_id": 1,
  "payment_method": "wechat"
}
```

### 4.8 我的订单

```
GET /payment/orders
```

### 4.9 我的购买记录

```
GET /payment/my-purchases
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20 |
| status | string | 否 | 状态筛选 |

### 4.10 提交作品

```
POST /payment/submissions
```

### 4.11 作品列表

```
GET /payment/submissions
```

### 4.12 创作者账户

```
GET /payment/accounts
```

```
POST /payment/accounts
```

```
PUT /payment/accounts/{id}
```

```
DELETE /payment/accounts/{id}
```

**请求体 (POST/PUT)**

```json
{
  "account_type": "alipay",
  "account_name": "张三",
  "account_number": "13800000000"
}
```

### 4.13 创作者偏好设置

```
GET /payment/accounts/creator/preference
```

```
PUT /payment/accounts/creator/preference
```

### 4.14 创作者收益

```
GET /payment/accounts/creator/earnings
```

**响应**

```json
{
  "code": 200,
  "data": {
    "total_earnings": 158000,
    "available_balance": 125000,
    "pending_balance": 33000,
    "this_month": 8500
  }
}
```

### 4.15 创作者结算

```
POST /payment/accounts/creator/settle
```

```
GET /payment/accounts/creator/settlements
```

### 4.16 管理端收入统计

```
GET /payment/admin/revenue/stats
```

**权限要求**: admin

**响应**

```json
{
  "code": 200,
  "data": {
    "today_revenue": 150000,
    "this_month": 2500000,
    "total_revenue": 15800000,
    "trend": [1000, 1200, 900, ...]
  }
}
```

---

## 5. 积分模块 (points)

**Base**: `/api/v1/points`

**权限要求**: 认证用户

### 5.1 积分余额

```
GET /points/balance
```

**响应**

```json
{
  "code": 200,
  "data": {
    "balance": 2500,
    "total_earned": 5000,
    "total_spent": 2500
  }
}
```

### 5.2 积分历史

```
GET /points/history
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| type | string | 否 | 类型 (earn/spend) |

### 5.3 每日签到

```
POST /points/check-in
```

**响应**

```json
{
  "code": 200,
  "msg": "签到成功",
  "data": {
    "earned": 10,
    "streak": 7,
    "total_balance": 2510
  }
}
```

### 5.4 商城物品列表

```
GET /points/mall/items
```

### 5.5 兑换物品

```
POST /points/mall/exchange
```

**请求体**

```json
{
  "item_id": 1,
  "quantity": 1
}
```

### 5.6 积分分类

```
GET /points/categories
```

### 5.7 购物车操作

```
GET /points/cart
```

```
POST /points/cart
```

**请求体**

```json
{
  "item_id": 1,
  "quantity": 1
}
```

```
PUT /points/cart/{id}
```

```
DELETE /points/cart/{id}
```

### 5.8 购物车结算

```
POST /points/cart/checkout
```

### 5.9 用户统计

```
GET /points/stats/user
```

---

## 6. 任务模块 (tasks)

**Base**: `/api/v1/tasks`

**权限要求**: 认证用户

### 6.1 每日任务

```
GET /tasks/daily
```

**响应**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "每日登录",
      "description": "登录平台即可获得奖励",
      "points": 5,
      "completed": true,
      "claimable": false
    },
    {
      "id": 2,
      "name": "下载一个 Skill",
      "description": "下载任意一个 Skill",
      "points": 10,
      "completed": false,
      "progress": "0/1"
    }
  ]
}
```

### 6.2 领取任务奖励

```
POST /tasks/{id}/claim
```

**响应**

```json
{
  "code": 200,
  "msg": "奖励已领取",
  "data": { "earned_points": 10 }
}
```

### 6.3 签到

```
POST /tasks/check-in
```

### 6.4 获取签到状态

```
GET /tasks/check-in
```

### 6.5 签到日历

```
GET /tasks/check-in/calendar
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| month | string | 否 | 月份，格式 YYYY-MM |

### 6.6 成就列表

```
GET /tasks/achievements
```

### 6.7 任务统计

```
GET /tasks/stats
```

### 6.8 任务定义

```
GET /tasks/definitions
```

### 6.9 成就定义

```
GET /tasks/achievement-definitions
```

---

## 7. 下载模块 (downloads)

**Base**: `/api/v1/downloads`

### 7.1 下载列表 (分页)

```
GET /downloads
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20 |
| category | string | 否 | 分类筛选 |
| keyword | string | 否 | 搜索关键词 |
| sort | string | 否 | 排序 (latest/downloads/rating) |

### 7.2 下载详情

```
GET /downloads/{id}
```

### 7.3 通过 Slug 获取

```
GET /downloads/slug/{slug}
```

### 7.4 创建下载

```
POST /downloads
```

**请求体**

```json
{
  "title": "AI Trading Bot v1.0",
  "slug": "ai-trading-bot",
  "description": "Automated trading bot with AI predictions",
  "file_url": "https://tos.example.com/files/bot.zip",
  "file_size": 1024000,
  "category": "tools",
  "version": "1.0.0",
  "platform": ["windows", "linux"]
}
```

### 7.5 更新下载

```
PUT /downloads/{id}
```

### 7.6 删除下载

```
DELETE /downloads/{id}
```

### 7.7 点赞

```
POST /downloads/{id}/like
```

**响应**

```json
{
  "code": 200,
  "data": { "likes": 42, "liked": true }
}
```

### 7.8 记录下载

```
POST /downloads/{id}/record-download
```

---

## 8. 消息模块 (messages)

**Base**: `/api/v1/messages`

**权限要求**: 认证用户

### 8.1 消息列表

```
GET /messages
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversation_id | integer | 否 | 会话 ID |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |

### 8.2 发送消息

```
POST /messages
```

**请求体**

```json
{
  "conversation_id": 1,
  "content": "你好，请问这个 Skill 支持 Python 3.12 吗？",
  "type": "text"
}
```

### 8.3 对话列表

```
GET /messages/conversations
```

**响应**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "type": "direct",
      "participants": [
        { "id": 1, "username": "user1", "avatar": "https://..." },
        { "id": 2, "username": "user2", "avatar": "https://..." }
      ],
      "last_message": {
        "content": "好的，谢谢！",
        "created_at": "2026-04-30T10:00:00Z"
      },
      "unread_count": 0,
      "updated_at": "2026-04-30T10:00:00Z"
    }
  ]
}
```

### 8.4 创建对话

```
POST /messages/conversations
```

**请求体**

```json
{
  "type": "direct",
  "participant_ids": [2]
}
```

### 8.5 删除对话

```
DELETE /messages/conversations/{id}
```

### 8.6 通知列表

```
GET /messages/notifications
```

---

## 9. 教程模块 (tutorials)

**Base**: `/api/v1/tutorials`

### 9.1 教程列表 (分页)

```
GET /tutorials
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| category_id | integer | 否 | 分类 ID |
| difficulty | string | 否 | 难度 (beginner/intermediate/advanced) |
| keyword | string | 否 | 搜索关键词 |

### 9.2 精选教程

```
GET /tutorials/featured
```

### 9.3 教程分类

```
GET /tutorials/categories
```

### 9.4 教程详情

```
GET /tutorials/{id_or_slug}
```

**响应**

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "Building Your First AI Skill",
    "slug": "building-first-ai-skill",
    "content": "# Markdown tutorial content...",
    "difficulty": "beginner",
    "category": { "id": 1, "name": "Getting Started" },
    "author": { "id": 1, "username": "admin" },
    "view_count": 5678,
    "like_count": 234,
    "duration_minutes": 30,
    "created_at": "2026-01-15T00:00:00Z"
  }
}
```

### 9.5 记录浏览

```
POST /tutorials/{id}/view
```

### 9.6 点赞

```
POST /tutorials/{id}/like
```

---

## 10. 仪表盘模块 (dashboard)

**Base**: `/api/v1/dashboard`

**权限要求**: 认证用户

### 10.1 统计数据

```
GET /dashboard/stats
```

**响应**

```json
{
  "code": 200,
  "data": {
    "total_skills": 1250,
    "total_users": 8500,
    "total_downloads": 125000,
    "today_visits": 3200
  }
}
```

### 10.2 最近活动

```
GET /dashboard/recent-activity
```

### 10.3 快捷操作

```
GET /dashboard/quick-actions
```

### 10.4 用户活动

```
GET /dashboard/user-activity
```

### 10.5 概览

```
GET /dashboard/overview
```

---

## 11. 分析模块 (analytics)

**Base**: `/api/v1/analytics`

**权限要求**: admin

### 11.1 概览

```
GET /analytics/overview
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| period | string | 否 | 周期 (today/week/month/year) |

**响应**

```json
{
  "code": 200,
  "data": {
    "total_visits": 50000,
    "unique_visitors": 12500,
    "avg_duration": 320,
    "bounce_rate": 35.2,
    "conversion_rate": 4.8
  }
}
```

### 11.2 趋势

```
GET /analytics/trend
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| metric | string | 否 | 指标 (visits/users/downloads/revenue) |
| days | integer | 否 | 天数，默认 30 |

### 11.3 热门页面

```
GET /analytics/top-pages
```

### 11.4 用户活动

```
GET /analytics/user-activity
```

### 11.5 每小时分析

```
GET /analytics/hourly
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期，格式 YYYY-MM-DD |

### 11.6 导出

```
GET /analytics/export
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 否 | 导出格式 (csv/json)，默认 csv |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |

---

## 12. 配置同步模块 (config_sync)

**Base**: `/api/v1/config`

**权限要求**: admin (写操作)

### 12.1 版本列表

```
GET /config/versions
```

**响应**

```json
{
  "code": 200,
  "data": [
    {
      "version": "2.1.0",
      "published_at": "2026-04-30T08:00:00Z",
      "published_by": "admin",
      "changes": "Updated navigation config"
    }
  ]
}
```

### 12.2 获取指定版本

```
GET /config/version/{version}
```

### 12.3 获取最新配置

```
GET /config/latest
```

### 12.4 配置检查

```
GET /config/check
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| current_version | string | 否 | 当前客户端版本 |

**响应**

```json
{
  "code": 200,
  "data": {
    "has_update": true,
    "latest_version": "2.1.0",
    "current_version": "2.0.0"
  }
}
```

### 12.5 发布配置

```
POST /config/publish
```

**请求体**

```json
{
  "version": "2.1.0",
  "config_data": { "theme": "dark", "language": "zh-CN" },
  "changes": "Updated default theme"
}
```

---

## 13. 商城模块 (store)

**Base**: `/api/v1/store`

### 13.1 商品集合

```
GET /store/collections
```

**响应**

```json
{
  "code": 200,
  "data": [
    {
      "key": "featured",
      "name": "Featured Products",
      "product_count": 10
    }
  ]
}
```

### 13.2 集合详情

```
GET /store/collections/{key}
```

### 13.3 集合商品

```
GET /store/collections/{key}/products
```

### 13.4 商品详情

```
GET /store/products/{id}
```

### 13.5 购物车

```
GET /store/cart
```

```
POST /store/cart
```

**请求体**

```json
{
  "product_id": 1,
  "quantity": 1
}
```

```
PUT /store/cart/{id}
```

```
DELETE /store/cart/{id}
```

### 13.6 订单

```
POST /store/orders
```

```
GET /store/orders
```

### 13.7 订单支付

```
POST /store/orders/{no}/pay
```

### 13.8 支付回调

```
POST /store/callback/wechat
```

```
POST /store/callback/alipay
```

---

## 14. 文件存储模块 (storage)

**Base**: `/api/v1/storage`

**权限要求**: 认证用户 (上传/删除)

### 14.1 文件上传

```
POST /storage/upload
```

**请求**: multipart/form-data

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 上传文件 |
| folder | string | 否 | 存储目录 |

**响应**

```json
{
  "code": 200,
  "data": {
    "key": "uploads/2026/04/file_abc123.png",
    "url": "https://your-domain.tos-cn-shanghai.volces.com/uploads/2026/04/file_abc123.png",
    "size": 204800,
    "mime_type": "image/png"
  }
}
```

### 14.2 Base64 上传

```
POST /storage/upload/base64
```

**请求体**

```json
{
  "data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "filename": "screenshot.png",
  "folder": "screenshots"
}
```

### 14.3 获取文件

```
GET /storage/file/{key}
```

### 14.4 删除文件

```
DELETE /storage/file/{key}
```

### 14.5 签名 URL

```
GET /storage/signed-url/{key}
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| expires | integer | 否 | 过期秒数，默认 3600 |

**响应**

```json
{
  "code": 200,
  "data": {
    "url": "https://...?signature=...",
    "expires_at": "2026-04-30T11:00:00Z"
  }
}
```

---

## 15. 国际化模块 (i18n)

**Base**: `/api/v1/i18n`

### 15.1 翻译列表

```
GET /i18n/translations
```

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| lang | string | 否 | 语言代码 (zh-CN/en/ja/ko) |
| namespace | string | 否 | 命名空间 |

### 15.2 创建翻译

```
POST /i18n/translations
```

**请求体**

```json
{
  "lang": "en",
  "key": "nav.home",
  "value": "Home",
  "namespace": "common"
}
```

### 15.3 更新翻译

```
PUT /i18n/translations/{id}
```

### 15.4 删除翻译

```
DELETE /i18n/translations/{id}
```

### 15.5 语言包

```
GET /i18n/{lang}/messages
```

**响应**

```json
{
  "code": 200,
  "data": {
    "common": {
      "nav.home": "首页",
      "nav.skills": "技能",
      "nav.market": "市场"
    },
    "auth": {
      "login.title": "登录",
      "login.submit": "立即登录"
    }
  }
}
```

---

## 16. Skills 模块 (skills)

**Base**: `/api/v1/skills`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/skills` | Skills 列表 (分页、搜索、筛选) |
| GET | `/skills/{id_or_slug}` | Skill 详情 |
| POST | `/skills` | 创建 Skill (认证) |
| PUT | `/skills/{id}` | 更新 Skill (作者/admin) |
| DELETE | `/skills/{id}` | 删除 Skill (作者/admin) |
| GET | `/skills/categories` | Skills 分类 |
| GET | `/skills/stats` | 平台 Skills 统计 |
| POST | `/skills/{id}/review` | 提交审核 (admin) |

---

## 17. 供应商模块 (vendor)

**Base**: `/api/v1/vendor`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/vendor/list` | 供应商列表 |
| GET | `/vendor/{id}` | 供应商详情 |
| POST | `/vendor/apply` | 申请成为供应商 (认证) |
| PUT | `/vendor/profile` | 更新供应商信息 (认证) |
| GET | `/vendor/stats` | 供应商统计 |
| GET | `/vendor/levels` | 供应商等级说明 |

---

## 18. 联属营销模块 (affiliate)

**Base**: `/api/v1/affiliate`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/affiliate/dashboard` | 联属仪表盘 |
| GET | `/affiliate/links` | 推广链接列表 |
| POST | `/affiliate/links` | 创建推广链接 |
| GET | `/affiliate/commissions` | 佣金记录 |
| GET | `/affiliate/stats` | 推广统计 |
| POST | `/affiliate/withdraw` | 佣金提现 |

---

## 19. 通知模块 (notifications)

**Base**: `/api/v1/notifications`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/notifications` | 通知列表 |
| POST | `/notifications/{id}/read` | 标记已读 |
| POST | `/notifications/read-all` | 全部已读 |
| GET | `/notifications/unread-count` | 未读数量 |
| DELETE | `/notifications/{id}` | 删除通知 |
| PUT | `/notifications/settings` | 通知偏好设置 |

---

## 20. SillyClaw 模块 (sillyclaw)

**Base**: `/api/v1/sillyclaw`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/sillyclaw/version` | 获取最新版本 |
| GET | `/sillyclaw/rooms` | 房间列表 |
| POST | `/sillyclaw/rooms` | 创建房间 |
| GET | `/sillyclaw/task-types` | PK 任务类型 |
| GET | `/sillyclaw/show/rooms/{uuid}` | 房间详情 |
| POST | `/sillyclaw/show/rooms/{uuid}/join` | 加入房间 |
| POST | `/sillyclaw/show/rooms/{uuid}/start` | 开始战斗 |
| POST | `/sillyclaw/show/rooms/{uuid}/submit` | 提交结果 |

---

## 21. 搜索模块 (search)

**Base**: `/api/v1/search`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/search` | 全局搜索 (Skills/教程/文章) |
| GET | `/search/suggestions` | 搜索建议 |
| GET | `/search/hot` | 热门搜索 |

---

## 22. 定时任务模块 (scheduler)

**Base**: `/api/v1/scheduler`

**权限要求**: admin

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/scheduler/jobs` | 任务列表 |
| POST | `/scheduler/jobs` | 创建定时任务 |
| PUT | `/scheduler/jobs/{id}` | 更新任务 |
| DELETE | `/scheduler/jobs/{id}` | 删除任务 |
| POST | `/scheduler/jobs/{id}/trigger` | 手动触发 |
| GET | `/scheduler/jobs/{id}/history` | 执行历史 |

---

## 23. 对战竞技场模块 (arena)

**Base**: `/api/v1/arena`

**权限要求**: 认证用户 (创建/加入/对战)

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/arena/rooms` | 创建 PK 房间 |
| GET | `/arena/rooms` | 房间列表 |
| GET | `/arena/rooms/{room_id}` | 房间详情 |
| POST | `/arena/rooms/{room_id}/join` | 加入房间 |
| POST | `/arena/rooms/{room_id}/leave` | 离开房间 |
| POST | `/arena/battles/{room_id}/start` | 开始对战 |
| POST | `/arena/battles/{battle_id}/answer` | 提交答案 |
| GET | `/arena/battles/{battle_id}/result` | 对战结果 |
| GET | `/arena/rankings` | 排行榜 |
| GET | `/arena/rankings/me` | 我的排名 |
| GET | `/arena/battles/history` | 对战历史 |

---

## 24. 推荐模块 (recommendations)

**Base**: 根级别 (无 `/api/v1/` 前缀)

**权限要求**: 管理员 (refresh/sync)

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/recommended` | 推荐列表 |
| GET | `/trending` | 热门趋势 |
| GET | `/latest` | 最新内容 |
| POST | `/refresh` | 刷新推荐 (admin) |
| POST | `/sync` | 同步推荐数据 (admin) |
| GET | `/download/{skill_index}` | 获取下载地址 |
| GET | `/sources` | 数据来源列表 |
| GET | `/clawhub` | ClawHub 推荐 |

> 注意: recommendations 模块的 router 无前缀，路由直接注册在应用根级别。

---

## 25. 商品模块 (goods)

**Base**: `/api/v1/goods`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/goods/products` | 创建商品 |
| GET | `/goods/products` | 商品列表 |
| GET | `/goods/products/featured` | 精选商品 |
| GET | `/goods/products/search` | 商品搜索 |
| GET | `/goods/products/{id}` | 商品详情 |
| PUT | `/goods/products/{id}` | 更新商品 |
| DELETE | `/goods/products/{id}` | 删除商品 |
| POST | `/goods/products/{id}/publish` | 发布商品 |
| POST | `/goods/products/{id}/unpublish` | 下架商品 |
| POST | `/goods/products/bulk` | 批量创建 |
| POST | `/goods/categories` | 创建分类 |
| GET | `/goods/categories` | 分类列表 |
| GET | `/goods/categories/tree` | 分类树 |
| GET | `/goods/categories/slug/{slug}` | 按 Slug 查分类 |
| GET | `/goods/categories/{id}` | 分类详情 |
| PUT | `/goods/categories/{id}` | 更新分类 |
| DELETE | `/goods/categories/{id}` | 删除分类 |
| GET | `/goods/vendor/products` | 供应商商品列表 |
| GET | `/goods/vendor/products/stats` | 供应商商品统计 |
| GET | `/goods/sillypan/products` | SillyPan 商品 |

---

## 26. 交易市场模块 (marketplace)

**Base**: `/api/v1/marketplace`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/marketplace/listings` | 创建挂牌 |
| GET | `/marketplace/listings` | 挂牌列表 |
| GET | `/marketplace/listings/featured` | 精选挂牌 |
| GET | `/marketplace/listings/search` | 搜索挂牌 |
| GET | `/marketplace/listings/{id}` | 挂牌详情 |
| PUT | `/marketplace/listings/{id}` | 更新挂牌 |
| DELETE | `/marketplace/listings/{id}` | 删除挂牌 |
| POST | `/marketplace/listings/{id}/activate` | 激活挂牌 |
| POST | `/marketplace/listings/{id}/deactivate` | 停用挂牌 |
| POST | `/marketplace/purchases` | 创建购买 |
| GET | `/marketplace/purchases` | 购买记录 |
| GET | `/marketplace/purchases/{id}` | 购买详情 |
| POST | `/marketplace/purchases/{id}/cancel` | 取消购买 |
| POST | `/marketplace/purchases/{id}/pay` | 支付购买 |
| POST | `/marketplace/reviews` | 创建评价 |
| GET | `/marketplace/listings/{id}/reviews` | 挂牌评价 |
| GET | `/marketplace/reviews/{id}` | 评价详情 |
| GET | `/marketplace/stats` | 市场统计 |
| GET | `/marketplace/vendor/stats` | 供应商市场统计 |
| GET | `/marketplace/vendor/listings` | 供应商挂牌列表 |

---

## 27. 促销模块 (promotion)

**Base**: `/api/v1/promotions`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/promotions/` | 创建促销 |
| GET | `/promotions/active` | 活跃促销 |
| GET | `/promotions/` | 促销列表 |
| GET | `/promotions/stats` | 促销统计 |
| GET | `/promotions/{id}` | 促销详情 |
| PUT | `/promotions/{id}` | 更新促销 |
| DELETE | `/promotions/{id}` | 删除促销 |
| POST | `/promotions/{id}/activate` | 激活 |
| POST | `/promotions/{id}/deactivate` | 停用 |
| POST | `/promotions/coupons` | 创建优惠券 |
| GET | `/promotions/coupons` | 优惠券列表 |
| GET | `/promotions/coupons/{code}` | 按码查券 |
| POST | `/promotions/coupons/validate` | 验证优惠券 |
| POST | `/promotions/coupons/{code}/redeem` | 兑换优惠券 |
| POST | `/promotions/coupons/{code}/apply` | 使用优惠券 |
| POST | `/promotions/calculate-discount` | 计算折扣 |
| POST | `/promotions/flash-sales` | 创建秒杀 |
| GET | `/promotions/flash-sales` | 秒杀列表 |
| GET | `/promotions/flash-sales/ongoing` | 进行中的秒杀 |
| GET | `/promotions/flash-sales/{id}` | 秒杀详情 |
| GET | `/promotions/flash-sales/product/{id}` | 商品秒杀信息 |
| POST | `/promotions/flash-sales/{id}/purchase` | 秒杀购买 |
| GET | `/promotions/usage/history` | 用户使用历史 |
| GET | `/promotions/usage/history/all` | 全部使用历史 (admin) |

---

## 28. 员工管理模块 (staff)

**Base**: `/api/v1/staff`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/staff/auth/login` | 员工登录 |
| POST | `/staff/auth/logout` | 员工退出 |
| POST | `/staff/auth/change-password` | 修改密码 |
| GET | `/staff/auth/me` | 当前员工信息 |
| GET | `/staff/users` | 员工列表 |
| POST | `/staff/users` | 创建员工 |
| GET | `/staff/users/{id}` | 员工详情 |
| PUT | `/staff/users/{id}` | 更新员工 |
| PUT | `/staff/users/{id}/password` | 重置密码 |
| PUT | `/staff/users/{id}/status` | 更新状态 |
| DELETE | `/staff/users/{id}` | 删除员工 |
| GET | `/staff/roles` | 角色列表 |
| GET | `/staff/roles/{id}` | 角色详情 |
| POST | `/staff/roles` | 创建角色 |
| PUT | `/staff/roles/{id}` | 更新角色 |
| DELETE | `/staff/roles/{id}` | 删除角色 |
| GET | `/staff/permissions` | 权限列表 |
| GET | `/staff/permissions/tree` | 权限树 |
| GET | `/staff/permissions/check` | 权限检查 |
| GET | `/staff/audit-logs` | 审计日志 |
| GET | `/staff/health` | 健康检查 |
| GET | `/staff/info` | 员工系统信息 |

---

## 29. 交易模块 (transaction)

**Base**: `/api/v1/transaction` (用户端) + `/api/v1/admin/orders` (管理端)

### 用户端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/transaction/orders` | 创建订单 |
| GET | `/transaction/orders` | 订单列表 |
| GET | `/transaction/orders/{id}` | 订单详情 |
| PUT | `/transaction/orders/{id}/status` | 更新订单状态 |
| DELETE | `/transaction/orders/{id}` | 删除订单 |
| POST | `/transaction/settlements` | 创建结算 |
| GET | `/transaction/settlements` | 结算列表 |
| POST | `/transaction/settlements/{id}/process` | 处理结算 |
| POST | `/transaction/refunds` | 创建退款 |
| GET | `/transaction/refunds` | 退款列表 |
| GET | `/transaction/refunds/{id}` | 退款详情 |
| PUT | `/transaction/refunds/{id}/approve` | 批准退款 |
| PUT | `/transaction/refunds/{id}/reject` | 拒绝退款 |

### 管理端点 (`/api/v1/admin/orders`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/admin/orders` | 订单列表 |
| GET | `/admin/orders/stats` | 订单统计 |
| GET | `/admin/orders/{id}` | 订单详情 |
| GET | `/admin/orders/no/{order_no}` | 按单号查询 |
| PUT | `/admin/orders/{id}/status` | 更新订单状态 |
| POST | `/admin/orders/{id}/ship` | 发货 |
| POST | `/admin/orders/{id}/refund` | 退款 |
| POST | `/admin/orders/batch-ship` | 批量发货 |
| GET | `/admin/orders/export/download` | 导出订单 |

---

## 30. 物流模块 (logistics)

**Base**: `/api/v1/logistics`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/logistics/companies` | 快递公司列表 |
| GET | `/logistics/companies/{code}` | 快递公司详情 |
| GET | `/logistics/templates` | 运费模板列表 |
| GET | `/logistics/templates/{id}` | 运费模板详情 |
| POST | `/logistics/templates` | 创建运费模板 |
| PUT | `/logistics/templates/{id}` | 更新运费模板 |
| POST | `/logistics/calculate` | 计算运费 |
| GET | `/logistics/track/{tracking_number}` | 按运单号追踪 |
| GET | `/logistics/track` | 按订单追踪 |
| POST | `/logistics/print` | 打印面单 |
| GET | `/logistics/health` | 健康检查 |

---

## 31. 配置数据模块 (config_data)

**Base**: `/api/v1/config-data`

### 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/config-data/list/{category}` | 按分类列出配置 |
| GET | `/config-data/item/{category}/{name}` | 获取单个配置 |
| POST | `/config-data` | 创建配置项 |
| PUT | `/config-data/{category}/{name}` | 更新配置项 |
| DELETE | `/config-data/{category}/{name}` | 删除配置项 |
| POST | `/config-data/batch-update` | 批量更新配置 |

---

## 认证说明

### JWT Token 格式

所有需要认证的接口，在请求头中携带:

```
Authorization: Bearer <access_token>
```

### Token 生命周期

| Token | 有效期 | 说明 |
|-------|--------|------|
| access_token | 1 小时 | 用于 API 请求认证 |
| refresh_token | 7 天 | 用于刷新 access_token |

### 角色权限

| 角色 | 权限范围 |
|------|---------|
| admin | 全部权限 (用户管理、模块管理、数据分析) |
| vendor | Skills 管理、收益查看、供应商数据 |
| user | 基本操作 (浏览、购买、下载、消息) |
| editor | 内容管理 (文章、教程、分类) |

---

## 附录

### A. API 前缀规则

- 所有模块统一使用 `/api/v1/{module}`
- 旧路径 `/api/admin/*`、`/api/xxx` 已废弃
- 入口文件: `src/main.py`
- 模块通过 `PluginManager.load_all_modules()` 自动加载

### B. 通用查询参数

以下参数适用于所有列表类接口:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| page_size | integer | 20 | 每页数量 (最大 100) |
| sort | string | - | 排序字段 |
| order | string | desc | 排序方向 (asc/desc) |

### C. 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-30 | 2.0.0 | 全新模块化架构文档，31 模块完整 API 参考 (~400+ 端点) |
| 2026-04-29 | 1.0.0 | Phase 1: 迁移至 `/api/v1/*` 统一格式 |

### D. 相关文档

| 文档 | 路径 | 用途 |
|------|------|------|
| API 端点清单 | [API_ENDPOINT_CHECKLIST.md](./API_ENDPOINT_CHECKLIST.md) | 每个接口的功能、参数、认证、用法一览表 |
| v1→v2 迁移指南 | [API_MIGRATION_GUIDE.md](./API_MIGRATION_GUIDE.md) | 旧 API 路径 → 新 API 路径对照 (161→170+ 端点) |
| 项目 README | [../README.md](../README.md) | 项目总览和快速开始 |
| 快速开始 | [../QUICKSTART.md](../QUICKSTART.md) | 5 分钟快速启动指南 |
| 部署指南 | [../QUICK_DEPLOY.md](../QUICK_DEPLOY.md) | 生产环境部署文档 |
