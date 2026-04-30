# SillyMD API 端点清单 v2.0

> 基于 FastAPI 模块化架构，统一 `/api/v1/` 前缀
> 总计 31 模块 ~400+ 端点，所有端点按功能分组
> 最后更新: 2026-04-30

---

## 目录

1. [认证模块 (auth)](#1-认证模块-auth)
2. [管理模块 (admin)](#2-管理模块-admin)
3. [内容管理模块 (cms)](#3-内容管理模块-cms)
4. [支付模块 (payment)](#4-支付模块-payment)
5. [积分模块 (points)](#5-积分模块-points)
6. [任务模块 (tasks)](#6-任务模块-tasks)
7. [下载模块 (downloads)](#7-下载模块-downloads)
8. [消息模块 (messages)](#8-消息模块-messages)
9. [教程模块 (tutorials)](#9-教程模块-tutorials)
10. [仪表盘模块 (dashboard)](#10-仪表盘模块-dashboard)
11. [分析模块 (analytics)](#11-分析模块-analytics)
12. [配置同步模块 (config_sync)](#12-配置同步模块-config_sync)
13. [商城模块 (store)](#13-商城模块-store)
14. [文件存储模块 (storage)](#14-文件存储模块-storage)
15. [国际化模块 (i18n)](#15-国际化模块-i18n)
16. [Skills 模块 (skills)](#16-skills-模块-skills)
17. [供应商模块 (vendor)](#17-供应商模块-vendor)
18. [联属营销模块 (affiliate)](#18-联属营销模块-affiliate)
19. [通知模块 (notifications)](#19-通知模块-notifications)
20. [SillyClaw 模块 (sillyclaw)](#20-sillyclaw-模块-sillyclaw)
21. [搜索模块 (search)](#21-搜索模块-search)
22. [定时任务模块 (scheduler)](#22-定时任务模块-scheduler)
23. [竞技场模块 (arena)](#23-竞技场模块-arena)
24. [推荐模块 (recommendations)](#24-推荐模块-recommendations)
25. [商品模块 (goods)](#25-商品模块-goods)
26. [交易市场模块 (marketplace)](#26-交易市场模块-marketplace)
27. [促销模块 (promotion)](#27-促销模块-promotion)
28. [员工管理模块 (staff)](#28-员工管理模块-staff)
29. [交易订单模块 (transaction)](#29-交易订单模块-transaction)
30. [物流模块 (logistics)](#30-物流模块-logistics)
31. [配置数据模块 (config_data)](#31-配置数据模块-config_data)
32. [系统端点](#32-系统端点)

---

## 通用约定

### 基础信息

| 项目 | 值 |
|------|-----|
| Base URL (开发) | `http://localhost:8000` |
| API 前缀 | `/api/v1` |
| 认证方式 | JWT Bearer Token (Header: `Authorization: Bearer <token>`) |
| 响应格式 | JSON |
| 字符编码 | UTF-8 |

### 统一响应格式

```json
{
  "code": 200,
  "msg": "success",
  "data": { }
}
```

### 状态码

| code | 说明 |
|------|------|
| 200 | 操作成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 (Token 无效或过期) |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 (如版本已存在) |
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
    "items": [ ]
  }
}
```

### 通用查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| page_size | integer | 20 | 每页数量 (最大 100) |
| sort | string | - | 排序字段 |
| order | string | desc | 排序方向 (asc/desc) |

---

## 1. 认证模块 (auth)

**Base URL**: `/api/v1/auth`

### 端点列表

| 方法 | 路径 | 功能 | 认证 | 说明 |
|------|------|------|------|------|
| POST | `/auth/login` | 用户登录 | 无 | 返回 access_token + refresh_token |
| POST | `/auth/register` | 用户注册 | 无 | 创建新账户 |
| POST | `/auth/forgot-password` | 忘记密码 | 无 | 发送重置邮件 |
| POST | `/auth/reset-password` | 重置密码 | 无 | 使用 token 重置密码 |
| POST | `/auth/refresh` | 刷新 Token | 无 | 使用 refresh_token 获取新的 access_token |
| POST | `/auth/verify-email/{token}` | 验证邮箱 | 无 | 验证注册邮箱 |
| POST | `/auth/logout` | 退出登录 | 无 | 使当前 Token 失效 |
| GET | `/auth/me` | 获取当前用户信息 | Bearer Token | 返回当前登录用户的详细信息 |

### 详细用法

#### POST /auth/login

**功能**: 用户登录，返回 JWT Token

**请求体**:
```json
{
  "email": "admin@sillymd.com",
  "password": "admin123456"
}
```

**成功响应 (200)**:
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

**错误响应 (401)**:
```json
{
  "code": 401,
  "msg": "邮箱或密码错误"
}
```

#### POST /auth/register

**功能**: 注册新用户

**请求体**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 (3-32字符) |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 (6-128字符) |

```json
{
  "username": "new_user",
  "email": "new@example.com",
  "password": "securepassword"
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "id": 2,
    "username": "new_user",
    "email": "new@example.com",
    "role": "user"
  }
}
```

#### GET /auth/me

**功能**: 获取当前登录用户信息

**请求头**: `Authorization: Bearer <access_token>`

**成功响应 (200)**:
```json
{
  "code": 200,
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

#### POST /auth/refresh

**功能**: 使用 refresh_token 刷新 access_token

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**成功响应 (200)**:
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

### Token 生命周期

| Token 类型 | 有效期 | 用途 |
|-----------|--------|------|
| access_token | 1 小时 | 所有 API 请求认证 |
| refresh_token | 7 天 | 刷新 access_token |

### 角色权限

| 角色 | 权限范围 |
|------|---------|
| admin | 全部权限 (用户管理、模块管理、数据分析) |
| vendor | Skills 管理、收益查看、供应商数据 |
| editor | 内容管理 (文章、教程、分类) |
| user | 基本操作 (浏览、购买、下载、消息) |

---

## 2. 管理模块 (admin)

**Base URL**: `/api/v1/admin`
**权限要求**: admin 角色

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/admin/users` | 用户列表 | page, page_size, keyword, role, status | 分页查询所有用户 |
| GET | `/admin/users/{id}` | 用户详情 | - | 获取单个用户信息 |
| PUT | `/admin/users/{id}` | 更新用户 | - | 修改用户角色/状态 |
| DELETE | `/admin/users/{id}` | 删除用户 | - | 删除用户账户 |
| GET | `/admin/modules` | 模块列表 | - | 查看所有已加载模块及状态 |
| POST | `/admin/modules/{id}/enable` | 启用模块 | - | 动态启用指定模块 |
| POST | `/admin/modules/{id}/disable` | 禁用模块 | - | 动态禁用指定模块 |
| GET | `/admin/audit-logs` | 审计日志 | page, page_size, user_id, action, start_date, end_date | 查看操作审计日志 |
| POST | `/admin/seeds/import` | 导入种子数据 | - | 批量导入模拟数据 |
| POST | `/admin/seeds/clear` | 清空种子数据 | - | 删除所有模拟数据 |

### 详细用法

#### GET /admin/users

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量 |
| keyword | str | 否 | - | 搜索关键词 (用户名/邮箱) |
| role | str | 否 | - | 角色筛选 (admin/vendor/editor/user) |
| status | int | 否 | - | 状态筛选 (0=禁用, 1=正常) |

**请求头**: `Authorization: Bearer <admin_token>`

**成功响应**:
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
        "avatar": "https://...",
        "created_at": "2026-01-01T00:00:00Z",
        "last_login": "2026-04-30T08:00:00Z"
      }
    ]
  }
}
```

#### GET /admin/modules

**功能**: 查看所有已加载模块状态

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "modules": [
      {
        "name": "auth",
        "enabled": true,
        "version": "2.0.0",
        "status": "running",
        "depends": []
      },
      {
        "name": "cms",
        "enabled": true,
        "version": "2.0.0",
        "status": "running",
        "depends": ["db_adapter"]
      }
    ]
  }
}
```

#### POST /admin/modules/{id}/enable

**功能**: 动态启用指定模块

**成功响应**:
```json
{
  "code": 200,
  "msg": "模块已启用",
  "data": { "module": "payment", "enabled": true }
}
```

---

## 3. 内容管理模块 (cms)

**Base URL**: `/api/v1/cms`
**权限要求**: 写操作需 editor/admin 角色

### 端点列表 - 文章

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/cms/articles` | 文章列表 | page, page_size, category_id, status, keyword | 无 |
| GET | `/cms/articles/{id}` | 文章详情 | - | 无 |
| POST | `/cms/articles` | 创建文章 | - | editor+ |
| PUT | `/cms/articles/{id}` | 更新文章 | - | editor+ |
| DELETE | `/cms/articles/{id}` | 删除文章 | - | admin |

### 端点列表 - 分类

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/cms/categories` | 分类列表 | - | 无 |
| POST | `/cms/categories` | 创建分类 | - | editor+ |
| PUT | `/cms/categories/{id}` | 更新分类 | - | editor+ |
| DELETE | `/cms/categories/{id}` | 删除分类 | - | admin |

### 端点列表 - 导航

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/cms/navigation` | 获取导航配置 | - | 无 |
| PUT | `/cms/navigation` | 更新导航配置 | - | admin |

### 端点列表 - SEO

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/cms/seo` | 获取 SEO 设置 | - | 无 |
| PUT | `/cms/seo` | 更新 SEO 设置 | - | admin |

### 详细用法

#### GET /cms/articles

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量 |
| category_id | int | 否 | - | 分类 ID 筛选 |
| status | str | 否 | - | 状态筛选 (published/draft) |
| keyword | str | 否 | - | 标题/内容搜索 |

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "title": "Getting Started with AI Skills",
        "slug": "getting-started-ai-skills",
        "excerpt": "Learn how to...",
        "category": { "id": 1, "name": "Tutorials" },
        "author": { "id": 1, "username": "admin" },
        "status": "published",
        "view_count": 1234,
        "tags": ["AI", "beginner"],
        "created_at": "2026-01-15T10:00:00Z"
      }
    ]
  }
}
```

#### POST /cms/articles

**功能**: 创建文章 (editor/admin)

**请求体**:
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

**成功响应 (201)**:
```json
{
  "code": 201,
  "msg": "文章创建成功",
  "data": { "id": 2, "slug": "new-article-title" }
}
```

#### GET /cms/navigation

**功能**: 获取站点导航配置

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "primary": [
      { "label": "Home", "url": "/", "children": [] },
      { "label": "Skills", "url": "/skills", "children": [
        { "label": "AI Skills", "url": "/skills?category=ai" }
      ]}
    ],
    "footer": [
      { "label": "About", "url": "/about" },
      { "label": "Contact", "url": "/contact" }
    ]
  }
}
```

---

## 4. 支付模块 (payment)

**Base URL**: `/api/v1/payment`
**权限要求**: 大多数端点需认证用户

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| POST | `/payment/create` | 创建支付 | - | 认证用户 |
| GET | `/payment/{id}` | 查询支付状态 | - | 认证用户 |
| POST | `/payment/notify/{provider}` | 支付回调通知 | - | 无 |
| POST | `/payment/refund` | 退款 | - | 认证用户 |
| GET | `/payment/methods` | 获取支付方式列表 | - | 无 |
| POST | `/payment/paypal/capture/{id}` | PayPal 支付捕获 | - | 认证用户 |
| POST | `/payment/orders` | 创建订单 | - | 认证用户 |
| GET | `/payment/orders` | 我的订单列表 | status, page, page_size | 认证用户 |
| GET | `/payment/my-purchases` | 我的购买记录 | content_type, page, page_size | 认证用户 |
| POST | `/payment/submissions` | 提交作品 | - | 认证用户 |
| GET | `/payment/submissions` | 作品列表 | status | 认证用户 |
| GET | `/payment/accounts` | 支付账户列表 | - | admin |
| POST | `/payment/accounts` | 创建支付账户 | - | admin |
| PUT | `/payment/accounts/{id}` | 更新支付账户 | - | admin |
| DELETE | `/payment/accounts/{id}` | 删除支付账户 | - | admin |
| GET | `/payment/accounts/creator/preference` | 创作者偏好 | - | 认证用户 |
| PUT | `/payment/accounts/creator/preference` | 更新创作者偏好 | - | 认证用户 |
| GET | `/payment/accounts/creator/earnings` | 创作者收益 | status, page, page_size | 认证用户 |
| POST | `/payment/accounts/creator/settle` | 创作者结算 | - | 认证用户 |
| GET | `/payment/accounts/creator/settlements` | 结算记录 | page, page_size | 认证用户 |
| GET | `/payment/admin/revenue/stats` | 管理端收入统计 | days | admin |

### 详细用法

#### POST /payment/create

**功能**: 创建支付，获取支付凭证 (二维码等)

**请求体**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order_id | str | 是 | 订单编号 |
| amount | int | 是 | 金额 (单位为分) |
| method | str | 是 | 支付方式: wechat/alipay/paypal |
| description | str | 否 | 支付描述 |

```json
{
  "order_id": "ORD-20260430-001",
  "amount": 2999,
  "method": "wechat",
  "description": "Skill Purchase - AI Trading Bot"
}
```

**成功响应**:
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

#### GET /payment/methods

**功能**: 获取当前支持的支付方式

**成功响应**:
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

#### GET /payment/admin/revenue/stats

**功能**: 管理员查看平台收入统计 (admin only)

**Query 参数**: `days` (默认 30)

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "today_revenue": 150000,
    "this_month": 2500000,
    "total_revenue": 15800000,
    "trend": [1000, 1200, 900, 1500, 2000]
  }
}
```

---

## 5. 积分模块 (points)

**Base URL**: `/api/v1/points`
**权限要求**: 大多数端点需认证用户

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/points/balance` | 积分余额 | - | 认证用户 |
| GET | `/points/history` | 积分历史 | page, page_size, type(earn/spend) | 认证用户 |
| POST | `/points/check-in` | 每日签到 | - | 认证用户 |
| GET | `/points/mall/items` | 商城物品列表 | category, is_featured, page, page_size | 无 |
| POST | `/points/mall/exchange` | 兑换物品 | - | 认证用户 |
| GET | `/points/categories` | 积分商品分类 | - | 无 |
| GET | `/points/cart` | 购物车 | - | 认证用户 |
| POST | `/points/cart` | 添加购物车 | - | 认证用户 |
| PUT | `/points/cart/{id}` | 更新购物车 | - | 认证用户 |
| DELETE | `/points/cart/{id}` | 删除购物车项 | - | 认证用户 |
| POST | `/points/cart/checkout` | 购物车结算 | - | 认证用户 |
| GET | `/points/stats/user` | 用户积分统计 | - | 认证用户 |

### 详细用法

#### GET /points/balance

**功能**: 获取当前用户积分余额

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
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

#### POST /points/check-in

**功能**: 每日签到获取积分

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
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

**错误响应 (已签到)**:
```json
{
  "code": 400,
  "msg": "今日已签到"
}
```

#### POST /points/mall/exchange

**功能**: 使用积分兑换商城物品

**请求体**:
```json
{
  "item_id": 1,
  "quantity": 1
}
```

**成功响应**:
```json
{
  "code": 200,
  "msg": "兑换成功",
  "data": {
    "item_name": "VIP 体验卡",
    "points_spent": 500,
    "remaining_balance": 2000
  }
}
```

---

## 6. 任务模块 (tasks)

**Base URL**: `/api/v1/tasks`
**权限要求**: 认证用户

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/tasks/daily` | 每日任务列表 | - | 含进度和完成状态 |
| POST | `/tasks/{id}/claim` | 领取任务奖励 | - | 完成后领取积分 |
| POST | `/tasks/check-in` | 签到 | - | 每日签到 |
| GET | `/tasks/check-in` | 获取签到状态 | - | 今日是否已签到 |
| GET | `/tasks/check-in/calendar` | 签到日历 | month (YYYY-MM) | 月度签到记录 |
| GET | `/tasks/achievements` | 成就列表 | - | 所有成就及进度 |
| GET | `/tasks/stats` | 任务统计 | - | 用户完成任务统计 |
| GET | `/tasks/definitions` | 任务定义列表 | - | 所有可用任务定义 |
| GET | `/tasks/achievement-definitions` | 成就定义列表 | - | 所有成就定义 |

### 详细用法

#### GET /tasks/daily

**功能**: 获取今日可完成的每日任务及进度

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
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

#### POST /tasks/{id}/claim

**功能**: 领取已完成任务的奖励

**路径参数**: `id` - 任务 ID

**成功响应**:
```json
{
  "code": 200,
  "msg": "奖励已领取",
  "data": { "earned_points": 10 }
}
```

---

## 7. 下载模块 (downloads)

**Base URL**: `/api/v1/downloads`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/downloads` | 下载列表 | page, page_size, category, keyword, sort | 无 |
| GET | `/downloads/{id}` | 下载详情 | - | 无 |
| GET | `/downloads/slug/{slug}` | 通过 Slug 获取 | - | 无 |
| POST | `/downloads` | 创建下载资源 | - | editor+ |
| PUT | `/downloads/{id}` | 更新下载资源 | - | editor+ |
| DELETE | `/downloads/{id}` | 删除下载资源 | - | admin |
| POST | `/downloads/{id}/like` | 点赞下载资源 | - | 认证用户 |
| POST | `/downloads/{id}/record-download` | 记录下载 | - | 认证用户 |

### 详细用法

#### GET /downloads

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量 |
| category | str | 否 | - | 分类 (tools/templates/datasets/plugins) |
| keyword | str | 否 | - | 搜索关键词 |
| sort | str | 否 | - | 排序: latest/downloads/rating |

#### POST /downloads

**功能**: 创建下载资源 (editor/admin)

**请求体**:
```json
{
  "title": "AI Trading Bot v1.0",
  "slug": "ai-trading-bot",
  "description": "Automated trading bot with AI predictions",
  "file_url": "https://cdn.example.com/files/bot.zip",
  "file_size": 1024000,
  "category": "tools",
  "version": "1.0.0",
  "platform": ["windows", "linux"]
}
```

---

## 8. 消息模块 (messages)

**Base URL**: `/api/v1/messages`
**权限要求**: 认证用户

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/messages` | 消息列表 | conversation_id, page, page_size | 获取指定会话的消息 |
| POST | `/messages` | 发送消息 | - | 发送文本消息 |
| GET | `/messages/conversations` | 对话列表 | page, page_size | 所有对话列表 |
| POST | `/messages/conversations` | 创建对话 | - | 创建新对话 |
| DELETE | `/messages/conversations/{id}` | 删除对话 | - | 删除指定对话 |
| GET | `/messages/notifications` | 通知列表 | page, page_size | 系统通知 |

### 详细用法

#### GET /messages/conversations

**功能**: 获取当前用户的所有对话列表

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
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

#### POST /messages/conversations

**功能**: 创建新对话

**请求体**:
```json
{
  "type": "direct",
  "participant_ids": [2]
}
```

**成功响应**:
```json
{
  "code": 200,
  "data": { "id": 2, "type": "direct" }
}
```

#### POST /messages

**功能**: 发送消息到指定对话

**请求体**:
```json
{
  "conversation_id": 1,
  "content": "你好，请问这个 Skill 支持 Python 3.12 吗？",
  "type": "text"
}
```

---

## 9. 教程模块 (tutorials)

**Base URL**: `/api/v1/tutorials`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/tutorials` | 教程列表 | page, page_size, category_id, difficulty, keyword | 无 |
| GET | `/tutorials/featured` | 精选教程 | limit | 无 |
| GET | `/tutorials/categories` | 教程分类 | - | 无 |
| GET | `/tutorials/{id_or_slug}` | 教程详情 | - | 无 |
| POST | `/tutorials/{id}/view` | 记录浏览 | - | 无 |
| POST | `/tutorials/{id}/like` | 点赞教程 | - | 认证用户 |

### 详细用法

#### GET /tutorials

**Query 参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |
| category_id | int | 否 | 分类 ID |
| difficulty | str | 否 | 难度: beginner/intermediate/advanced |
| keyword | str | 否 | 搜索关键词 |

#### GET /tutorials/{id_or_slug}

**功能**: 获取教程详情 (支持 ID 或 Slug)

**成功响应**:
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

---

## 10. 仪表盘模块 (dashboard)

**Base URL**: `/api/v1/dashboard`
**权限要求**: 认证用户

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/dashboard/stats` | 统计数据 | - | 平台关键指标 |
| GET | `/dashboard/recent-activity` | 最近活动 | limit | 最近活动列表 |
| GET | `/dashboard/quick-actions` | 快捷操作 | - | 常用功能入口 |
| GET | `/dashboard/user-activity` | 用户活动 | user_id, days | 指定用户活动 |
| GET | `/dashboard/overview` | 概览 | - | 仪表盘总览 |

### 详细用法

#### GET /dashboard/stats

**功能**: 获取平台关键统计

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
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

#### GET /dashboard/recent-activity

**功能**: 获取最近平台活动

**Query 参数**: `limit` (默认 10)

---

## 11. 分析模块 (analytics)

**Base URL**: `/api/v1/analytics`
**权限要求**: admin

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/analytics/overview` | 分析概览 | period (today/week/month/year) | 访问统计总览 |
| GET | `/analytics/trend` | 趋势数据 | metric, days | 指标趋势图数据 |
| GET | `/analytics/top-pages` | 热门页面 | limit, days | 访问量最高的页面 |
| GET | `/analytics/user-activity` | 用户活动 | days | 用户活跃度分析 |
| GET | `/analytics/hourly` | 每小时统计 | date | 24小时访问分布 |
| GET | `/analytics/export` | 导出数据 | format(csv/json), start_date, end_date | 导出分析报告 |

### 详细用法

#### GET /analytics/overview

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| period | str | 否 | today | 统计周期: today/week/month/year |

**成功响应**:
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

#### GET /analytics/trend

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| metric | str | 否 | visits | 指标: visits/users/downloads/revenue |
| days | int | 否 | 30 | 统计天数 |

#### GET /analytics/export

**功能**: 导出分析数据

**Query 参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | str | 否 | 导出格式: csv/json (默认 csv) |
| start_date | str | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | str | 否 | 结束日期 (YYYY-MM-DD) |

---

## 12. 配置同步模块 (config_sync)

**Base URL**: `/api/v1/config`
**权限要求**: 写操作需 admin

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/config/versions` | 版本列表 | - | 所有配置版本历史 |
| GET | `/config/version/{version}` | 获取指定版本 | - | 按版本号获取配置 |
| GET | `/config/latest` | 获取最新配置 | - | 最新版本的配置数据 |
| GET | `/config/check` | 配置检查 | current_version | 检查是否有新版本 |
| POST | `/config/publish` | 发布配置 | - | 发布新版本配置 (admin) |

### 详细用法

#### GET /config/check

**功能**: 客户端检查是否有新配置版本

**Query 参数**: `current_version` - 当前客户端版本号

**成功响应 (有新版本)**:
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

**成功响应 (已最新)**:
```json
{
  "code": 200,
  "data": {
    "has_update": false,
    "latest_version": "2.0.0",
    "current_version": "2.0.0"
  }
}
```

#### POST /config/publish

**功能**: 发布新版本配置 (admin only)

**请求体**:
```json
{
  "version": "2.1.0",
  "config_data": {
    "theme": "dark",
    "language": "zh-CN",
    "features": { "new_ui": true }
  },
  "changes": "Updated default theme and UI settings"
}
```

---

## 13. 商城模块 (store)

**Base URL**: `/api/v1/store`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/store/collections` | 商品集合列表 | - | 无 |
| GET | `/store/collections/{key}` | 集合详情 | - | 无 |
| GET | `/store/collections/{key}/products` | 集合商品列表 | is_active | 无 |
| GET | `/store/products/{id}` | 商品详情 | - | 无 |
| GET | `/store/cart` | 购物车 | - | 认证用户 |
| POST | `/store/cart` | 添加到购物车 | - | 认证用户 |
| PUT | `/store/cart/{id}` | 更新购物车项 | - | 认证用户 |
| DELETE | `/store/cart/{id}` | 删除购物车项 | - | 认证用户 |
| POST | `/store/orders` | 创建订单 | - | 认证用户 |
| GET | `/store/orders` | 订单列表 | status, page, page_size | 认证用户 |
| POST | `/store/orders/{no}/pay` | 支付订单 | - | 认证用户 |
| POST | `/store/callback/wechat` | 微信支付回调 | - | 无 |
| POST | `/store/callback/alipay` | 支付宝支付回调 | - | 无 |

### 商城管理端点

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/store/admin/collections` | 管理集合列表 | admin |
| POST | `/store/admin/collections` | 创建集合 | admin |
| PUT | `/store/admin/collections/{id}` | 更新集合 | admin |
| DELETE | `/store/admin/collections/{id}` | 删除集合 | admin |
| GET | `/store/admin/products` | 管理商品列表 | admin |
| POST | `/store/admin/products` | 创建商品 | admin |
| PUT | `/store/admin/products/{id}` | 更新商品 | admin |
| DELETE | `/store/admin/products/{id}` | 删除商品 | admin |
| GET | `/store/admin/orders` | 管理订单列表 | admin |
| PUT | `/store/admin/orders/{no}/status` | 更新订单状态 | admin |
| GET | `/store/admin/stats` | 商城统计 | admin |

### 详细用法

#### GET /store/collections

**功能**: 获取所有商品集合

**成功响应**:
```json
{
  "code": 200,
  "data": [
    {
      "key": "featured",
      "name": "Featured Products",
      "description": "精选商品推荐",
      "product_count": 10
    }
  ]
}
```

#### POST /store/orders/{no}/pay

**功能**: 发起订单支付

**请求体**:
```json
{
  "payment_method": "wechat"
}
```

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "order_no": "ORD-20260430-001",
    "status": "pending",
    "payment_url": "https://..."
  }
}
```

---

## 14. 文件存储模块 (storage)

**Base URL**: `/api/v1/storage`
**权限要求**: 上传/删除需认证用户

### 端点列表

| 方法 | 路径 | 功能 | Query/Body 参数 | 说明 |
|------|------|------|---------------|------|
| POST | `/storage/upload` | 文件上传 | multipart: file, folder | 上传文件到 TOS |
| POST | `/storage/upload/base64` | Base64 上传 | body: data, filename, folder | Base64 编码上传 |
| GET | `/storage/file/{key}` | 获取文件信息 | - | 文件元数据 |
| DELETE | `/storage/file/{key}` | 删除文件 | - | 删除指定文件 |
| GET | `/storage/signed-url/{key}` | 签名 URL | expires (秒) | 临时访问链接 |
| GET | `/storage/list/{folder}` | 列出文件 | max_keys | 文件夹清单 |
| GET | `/storage/stats/usage` | 存储统计 | user_id | 用量统计 |
| POST | `/storage/batch/delete` | 批量删除 | body: keys[] | 批量删除文件 |

### 详细用法

#### POST /storage/upload

**功能**: 上传文件到 TOS (火山引擎对象存储)

**请求格式**: `multipart/form-data`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 上传的文件 |
| folder | str | 否 | 存储目录 (如 "uploads/2026") |

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "key": "uploads/2026/04/file_abc123.png",
    "url": "https://cdn.example.com/uploads/2026/04/file_abc123.png",
    "size": 204800,
    "mime_type": "image/png"
  }
}
```

#### POST /storage/upload/base64

**功能**: 以 Base64 编码上传文件

**请求体**:
```json
{
  "data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "filename": "screenshot.png",
  "folder": "screenshots"
}
```

#### GET /storage/signed-url/{key}

**功能**: 生成临时访问 URL (用于私有文件)

**Query 参数**: `expires` - 过期秒数 (默认 3600, 最大 86400)

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "url": "https://...?signature=...&expires=...",
    "expires_at": "2026-04-30T11:00:00Z"
  }
}
```

---

## 15. 国际化模块 (i18n)

**Base URL**: `/api/v1/i18n`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/i18n/languages` | 支持的语言 | - | 语言列表和默认语言 |
| GET | `/i18n/translations` | 翻译内容 | lang, namespace | 获取指定语言的翻译 |
| POST | `/i18n/translations` | 创建翻译 | - | 添加翻译条目 |
| PUT | `/i18n/translations/{id}` | 更新翻译 | - | 修改翻译条目 |
| DELETE | `/i18n/translations/{id}` | 删除翻译 | - | 删除翻译条目 |
| GET | `/i18n/{lang}/messages` | 语言包 | - | 获取完整语言包 |
| GET | `/i18n/translate` | 翻译单个键 | key, lang | 单键翻译 |
| POST | `/i18n/translate/batch` | 批量翻译 | - | 批量键翻译 |
| GET | `/i18n/detect` | 语言检测 | - | 检测用户偏好语言 |
| POST | `/i18n/set-language` | 设置语言 | lang | 切换语言 |

### 详细用法

#### GET /i18n/translations

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| lang | str | 否 | en | 语言代码 (zh/en/ja/ko) |
| namespace | str | 否 | - | 命名空间 (common/auth/skills) |

#### GET /i18n/{lang}/messages

**功能**: 获取完整语言包 (前端 i18n 初始化用)

**路径参数**: `lang` - 语言代码

**成功响应**:
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

#### GET /i18n/detect

**功能**: 自动检测用户偏好语言 (从 URL 参数、Cookie、Accept-Language 头)

**成功响应**:
```json
{
  "detected": "zh",
  "name": "中文",
  "all_supported": ["zh", "en", "ja", "ko"]
}
```

---

## 16. Skills 模块 (skills)

**Base URL**: `/api/v1/skills`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/skills` | Skills 列表 | page, page_size, category, type, search, sort, industry, scenario, min_price, max_price | 无 |
| GET | `/skills/{id_or_slug}` | Skill 详情 | - | 无 |
| POST | `/skills` | 创建 Skill | - | 认证用户 |
| PUT | `/skills/{id}` | 更新 Skill | - | 作者/admin |
| DELETE | `/skills/{id}` | 删除 Skill | - | 作者/admin |
| GET | `/skills/categories` | Skills 分类 | - | 无 |
| GET | `/skills/stats` | 平台统计 | - | 无 |
| POST | `/skills/{id}/review` | 审核 Skill | - | admin |

### 详细用法

#### GET /skills

**Query 参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |
| category | str | 否 | 分类筛选 |
| type | str | 否 | 类型: code/design/product/marketing |
| search | str | 否 | 搜索关键词 |
| sort | str | 否 | 排序: popular/newest/price |
| industry | str | 否 | 行业筛选 |
| scenario | str | 否 | 场景筛选 |
| min_price | int | 否 | 最低价格 |
| max_price | int | 否 | 最高价格 |

---

## 17. 供应商模块 (vendor)

**Base URL**: `/api/v1/vendor`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 认证 |
|------|------|------|-----------|------|
| GET | `/vendor/list` | 供应商列表 | page, page_size, level | 无 |
| GET | `/vendor/{id}` | 供应商详情 | - | 无 |
| POST | `/vendor/apply` | 申请成为供应商 | - | 认证用户 |
| PUT | `/vendor/profile` | 更新供应商信息 | - | 认证用户 |
| GET | `/vendor/stats` | 供应商统计 | - | 认证用户 |
| GET | `/vendor/levels` | 供应商等级说明 | - | 无 |

---

## 18. 联属营销模块 (affiliate)

**Base URL**: `/api/v1/affiliate`
**权限要求**: 认证用户

### 端点列表

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/affiliate/dashboard` | 联属仪表盘 | 推广数据总览 |
| GET | `/affiliate/links` | 推广链接列表 | 所有创建的推广链接 |
| POST | `/affiliate/links` | 创建推广链接 | 生成新的推广链接 |
| GET | `/affiliate/commissions` | 佣金记录 | 推广佣金明细 |
| GET | `/affiliate/stats` | 推广统计 | 点击/转化数据 |
| POST | `/affiliate/withdraw` | 佣金提现 | 提现到支付账户 |

---

## 19. 通知模块 (notifications)

**Base URL**: `/api/v1/notifications`
**权限要求**: 认证用户

### 端点列表

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/notifications` | 通知列表 | 分页获取所有通知 |
| POST | `/notifications/{id}/read` | 标记已读 | 单条标记已读 |
| POST | `/notifications/read-all` | 全部已读 | 一键标记全部已读 |
| GET | `/notifications/unread-count` | 未读数量 | 获取未读通知数量 |
| DELETE | `/notifications/{id}` | 删除通知 | 删除单条通知 |
| PUT | `/notifications/settings` | 通知偏好 | 设置通知接收偏好 |

### 详细用法

#### GET /notifications/unread-count

**功能**: 获取未读通知数量 (用于角标显示)

**请求头**: `Authorization: Bearer <token>`

**成功响应**:
```json
{
  "code": 200,
  "data": { "count": 5 }
}
```

#### PUT /notifications/settings

**功能**: 设置通知偏好

**请求体**:
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "notification_types": ["system", "message", "payment", "activity"]
}
```

---

## 20. SillyClaw 模块 (sillyclaw)

**Base URL**: `/api/v1/sillyclaw`

### 端点列表

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/sillyclaw/version` | 获取最新版本 | SillyClaw 客户端版本检查 |
| GET | `/sillyclaw/rooms` | 房间列表 | PK 对战场地列表 |
| POST | `/sillyclaw/rooms` | 创建房间 | 创建新的 PK 对战房间 |
| GET | `/sillyclaw/task-types` | PK 任务类型 | 可用的对战任务类型 |
| GET | `/sillyclaw/show/rooms/{uuid}` | 房间详情 | 指定房间的详细信息 |
| POST | `/sillyclaw/show/rooms/{uuid}/join` | 加入房间 | 加入指定 PK 房间 |
| POST | `/sillyclaw/show/rooms/{uuid}/start` | 开始战斗 | 开始 PK 对战 |
| POST | `/sillyclaw/show/rooms/{uuid}/submit` | 提交结果 | 提交对战结果 |

### 版本检查端点 (独立 router)

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/sillyclaw/version` | 获取最新版本 | 返回最新版本信息 |
| GET | `/sillyclaw/version/all` | 版本列表 | 所有历史版本 |
| GET | `/sillyclaw/version/{version}` | 版本详情 | 指定版本信息 |
| GET | `/sillyclaw/version/{version}/download` | 版本下载 | 302 重定向到下载 URL |
| GET | `/sillyclaw/check-update` | 检查更新 | Query: current=1.0.0 |

---

## 21. 搜索模块 (search)

**Base URL**: `/api/v1/search`

### 端点列表

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/search` | 全局搜索 | q, type, page, page_size | 搜索 Skills/教程/文章 |
| GET | `/search/suggestions` | 搜索建议 | q, limit | 输入联想建议 |
| GET | `/search/hot` | 热门搜索 | limit | 热门搜索关键词 |

### 详细用法

#### GET /search

**Query 参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| q | str | 是 | - | 搜索关键词 |
| type | str | 否 | all | 搜索类型: all/skills/tutorials/articles |
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量 |

**成功响应**:
```json
{
  "code": 200,
  "data": {
    "total": 42,
    "query": "AI",
    "results": {
      "skills": [ { "id": 1, "name": "AI Trading Bot", "type": "skill" } ],
      "tutorials": [ { "id": 1, "title": "AI入门教程", "type": "tutorial" } ],
      "articles": [ { "id": 1, "title": "AI Skills 指南", "type": "article" } ]
    }
  }
}
```

#### GET /search/hot

**功能**: 获取热门搜索关键词

**Query 参数**: `limit` (默认 10)

---

## 22. 定时任务模块 (scheduler)

**Base URL**: `/api/v1/scheduler`
**权限要求**: admin

### 端点列表

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/scheduler/jobs` | 任务列表 | 所有定时任务 |
| POST | `/scheduler/jobs` | 创建任务 | 创建新的定时任务 |
| PUT | `/scheduler/jobs/{id}` | 更新任务 | 修改定时任务配置 |
| DELETE | `/scheduler/jobs/{id}` | 删除任务 | 删除定时任务 |
| POST | `/scheduler/jobs/{id}/trigger` | 手动触发 | 立即执行任务 |
| GET | `/scheduler/jobs/{id}/history` | 执行历史 | 任务执行记录 |

---

## 23. 竞技场模块 (arena)

**路由前缀**: `/api/v1/arena` | **需要认证**: 是 (Bearer Token)

### 房间管理

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/arena/rooms` | 创建房间 | 创建新的竞技场房间 |
| GET | `/arena/rooms` | 房间列表 | 分页查询，按状态筛选 |
| GET | `/arena/rooms/{room_id}` | 房间详情 | 获取指定房间信息 |
| POST | `/arena/rooms/{room_id}/join` | 加入房间 | 参与竞技场房间 |
| POST | `/arena/rooms/{room_id}/leave` | 离开房间 | 退出竞技场房间 |

### 对战管理

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/arena/battles/{room_id}/start` | 开始对战 | 发起对战并指定参与者 |
| POST | `/arena/battles/{battle_id}/answer` | 提交回答 | 提交当前题目答案 |
| GET | `/arena/battles/{battle_id}/result` | 对战结果 | 获取已完成对战结果 |

### 排行榜

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/arena/rankings` | 排名称 | 分页查询竞技场排名称 |
| GET | `/arena/rankings/me` | 我的排名 | 查询当前用户排名 |
| GET | `/arena/battles/history` | 对战历史 | 查询用户对战记录 |

---

## 24. 推荐模块 (recommendations)

**路由前缀**: (由 PluginManager 挂载) | **需要认证**: 部分端点

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/recommended` | 推荐 Skills | 从 ClawHub 获取推荐列表 |
| GET | `/trending` | 热门 Skills | 获取热门/流行列表 |
| GET | `/latest` | 最新 Skills | 获取最新 Skills 列表 |
| POST | `/refresh` | 刷新推荐 | 手动刷新推荐数据 |
| POST | `/sync` | 同步至 TOS | 同步 Skills 至 TOS 存储 |
| GET | `/download/{skill_index}` | 下载链接 | 获取签名下载 URL (1 小时有效) |
| GET | `/sources` | 数据源信息 | 获取配置的外部数据源 |
| GET | `/clawhub` | ClawHub Skills | 从 DB 查 ClawHub Skills 列表 (分页) |

---

## 25. 商品模块 (goods)

**路由前缀**: `/api/v1/goods` | **需要认证**: 写操作

### 商品 CRUD

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/goods/products` | 创建商品 | 创建新商品 (草稿状态) |
| GET | `/goods/products` | 商品列表 | 分页 + 筛选查询 |
| GET | `/goods/products/featured` | 推荐商品 | 首页推荐商品列表 |
| GET | `/goods/products/search` | 搜索商品 | 全文本关键词搜索 |
| GET | `/goods/products/{product_id}` | 商品详情 | 获取商品详情 (增加浏览量) |
| PUT | `/goods/products/{product_id}` | 更新商品 | 更新商品信息 (所有者) |
| DELETE | `/goods/products/{product_id}` | 删除商品 | 软删除商品 (所有者) |
| POST | `/goods/products/{product_id}/publish` | 发布商品 | 发布上架 |
| POST | `/goods/products/{product_id}/unpublish` | 下架商品 | 下架商品 |
| POST | `/goods/products/bulk` | 批量操作 | 批量发布/下架/删除 |

### 分类管理

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/goods/categories` | 创建分类 | 新建商品分类 |
| GET | `/goods/categories` | 分类列表 | 按父级查询分类 |
| GET | `/goods/categories/tree` | 分类树 | 层级树形结构 |
| GET | `/goods/categories/slug/{slug}` | 按标识查分类 | slug 查询分类 |
| GET | `/goods/categories/{category_id}` | 分类详情 | 按 ID 查分类 |
| PUT | `/goods/categories/{category_id}` | 更新分类 | 修改分类信息 |
| DELETE | `/goods/categories/{category_id}` | 删除分类 | 删除商品分类 |

### 供应商端

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/goods/vendor/products` | 供应商商品 | 当前供应商商品列表 |
| GET | `/goods/vendor/products/stats` | 商品统计 | 当前供应商商品统计 |
| GET | `/goods/sillypan/products` | SillyPan 商品 | 公开商品展示 |

---

## 26. 交易市场模块 (marketplace)

**路由前缀**: `/api/v1/marketplace` | **需要认证**: 写操作

### 挂牌管理

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/marketplace/listings` | 创建挂牌 | 新建市场挂牌 |
| GET | `/marketplace/listings` | 挂牌列表 | 分页 + 筛选查询 |
| GET | `/marketplace/listings/featured` | 推荐挂牌 | 精选挂牌列表 |
| GET | `/marketplace/listings/search` | 搜索挂牌 | 全文本关键词搜索 |
| GET | `/marketplace/listings/{listing_id}` | 挂牌详情 | 按 ID 查挂牌 |
| PUT | `/marketplace/listings/{listing_id}` | 更新挂牌 | 修改挂牌 (所有者) |
| DELETE | `/marketplace/listings/{listing_id}` | 删除挂牌 | 删除挂牌 (所有者) |
| POST | `/marketplace/listings/{listing_id}/activate` | 激活挂牌 | 挂牌开放购买 |
| POST | `/marketplace/listings/{listing_id}/deactivate` | 停用挂牌 | 暂停销售 |

### 购买管理

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/marketplace/purchases` | 创建订单 | 新建购买订单 |
| GET | `/marketplace/purchases` | 我的订单 | 当前用户购买记录 |
| GET | `/marketplace/purchases/order/{order_id}` | 按订单号查 | 按订单号查购买 |
| GET | `/marketplace/purchases/{purchase_id}` | 购买详情 | 按 ID 查购买详情 |
| POST | `/marketplace/purchases/{purchase_id}/cancel` | 取消购买 | 取消未发货订单 |
| POST | `/marketplace/purchases/{purchase_id}/pay` | 支付 | 处理支付 |

### 评价与统计

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/marketplace/reviews` | 创建评价 | 对购买进行评价 |
| GET | `/marketplace/listings/{listing_id}/reviews` | 挂牌评价 | 查看挂牌评价列表 |
| GET | `/marketplace/reviews/{review_id}` | 评价详情 | 按 ID 查评价 |
| GET | `/marketplace/stats` | 市场统计 | 交易市场总统计 |
| GET | `/marketplace/vendor/stats` | 供应商统计 | 当前供应商销售统计 |
| GET | `/marketplace/vendor/listings` | 供应商挂牌 | 当前供应商挂牌列表 |

---

## 27. 促销模块 (promotion)

**路由前缀**: `/api/v1/promotions` | **注意**: 前缀为 `promotions` (复数)

### 促销活动

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/promotions/` | 创建促销 | 新建促销活动 (admin) |
| GET | `/promotions/active` | 当前有效促销 | 获取所有有效促销 (公开) |
| GET | `/promotions/` | 促销列表 | 筛选查询 (admin) |
| GET | `/promotions/stats` | 促销统计 | 促销数据统计 (admin) |
| GET | `/promotions/{promotion_id}` | 促销详情 | 按 ID 查促销 |
| PUT | `/promotions/{promotion_id}` | 更新促销 | 修改促销 (admin) |
| DELETE | `/promotions/{promotion_id}` | 删除促销 | 删除促销 (admin) |
| POST | `/promotions/{promotion_id}/activate` | 激活促销 | 使促销生效 (admin) |
| POST | `/promotions/{promotion_id}/deactivate` | 停用促销 | 暂停促销 (admin) |

### 优惠券

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/promotions/coupons` | 创建优惠券 | 新建优惠券 (admin) |
| GET | `/promotions/coupons` | 我的优惠券 | 当前用户优惠券 |
| GET | `/promotions/coupons/{code}` | 按码查券 | 按券码查详情 + 校验 |
| POST | `/promotions/coupons/validate` | 校验优惠券 | 校验券是否可用 |
| POST | `/promotions/coupons/{code}/redeem` | 领取优惠券 | 用户领取券 |
| POST | `/promotions/coupons/{code}/apply` | 使用优惠券 | 应用到订单 |
| POST | `/promotions/calculate-discount` | 计算折扣 | 预计算折扣 (不实际使用) |
| GET | `/promotions/usage/history` | 使用历史 | 当前用户使用记录 |
| GET | `/promotions/usage/history/all` | 全部使用历史 | 所有用户使用记录 (admin) |

### 闪购

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/promotions/flash-sales` | 创建闪购 | 新建闪购活动 (admin) |
| GET | `/promotions/flash-sales` | 闪购列表 | 筛选查询闪购 |
| GET | `/promotions/flash-sales/ongoing` | 进行中闪购 | 当前进行中的闪购 |
| GET | `/promotions/flash-sales/{flash_sale_id}` | 闪购详情 | 按 ID 查闪购 |
| GET | `/promotions/flash-sales/product/{product_id}` | 商品闪购 | 查询商品当前闪购 |
| POST | `/promotions/flash-sales/{flash_sale_id}/purchase` | 参与闪购 | 从闪购中购买 |

---

## 28. 员工管理模块 (staff)

**路由前缀**: `/api/v1/staff` | **需要认证**: 是 + RBAC 权限

### 认证

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/staff/auth/login` | 员工登录 | 返回 JWT access token |
| POST | `/staff/auth/logout` | 员工登出 | 审计日志记录 |
| POST | `/staff/auth/change-password` | 修改密码 | 修改当前用户密码 |
| GET | `/staff/auth/me` | 当前用户 | 获取当前认证用户信息 |

### 用户管理

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/staff/users` | 用户列表 | 分页查员工用户 (需要 `staff:user:read`) |
| GET | `/staff/users/{user_id}` | 用户详情 | 按 ID 查员工用户 |
| POST | `/staff/users` | 创建用户 | 新建员工用户 |
| PUT | `/staff/users/{user_id}` | 更新用户 | 修改员工用户信息 |
| PUT | `/staff/users/{user_id}/password` | 重置密码 | 重置员工密码 (admin) |
| PUT | `/staff/users/{user_id}/status` | 更新状态 | 启用/禁用员工账号 |
| DELETE | `/staff/users/{user_id}` | 删除用户 | 删除员工 (super_admin) |

### 角色与权限

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/staff/roles` | 角色列表 | 所有角色 |
| GET | `/staff/roles/{role_id}` | 角色详情 | 按 ID 查角色 |
| POST | `/staff/roles` | 创建角色 | 新建角色 |
| PUT | `/staff/roles/{role_id}` | 更新角色 | 修改角色 (系统角色受保护) |
| DELETE | `/staff/roles/{role_id}` | 删除角色 | 删除角色 (系统角色受保护) |
| GET | `/staff/permissions` | 权限列表 | 所有可用权限 |
| GET | `/staff/permissions/tree` | 权限树 | 按分类展示权限树 |
| GET | `/staff/permissions/check` | 权限检查 | 检查用户是否有某权限 |
| GET | `/staff/audit-logs` | 审计日志 | 分页查审计记录 |
| GET | `/staff/health` | 健康检查 | 模块健康检查 |
| GET | `/staff/info` | 模块信息 | 模块基本信息 |

---

## 29. 交易订单模块 (transaction)

**注意**: 此模块定义了两个路由组

### 用户端 (`/api/v1/transaction`)

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/transaction/orders` | 创建订单 | 创建新订单 |
| GET | `/transaction/orders` | 订单列表 | 分页查用户订单 |
| GET | `/transaction/orders/{order_id}` | 订单详情 | 按 ID 查订单 |
| PUT | `/transaction/orders/{order_id}/status` | 更新状态 | 更新订单状态 |
| DELETE | `/transaction/orders/{order_id}` | 取消订单 | 取消订单 |
| POST | `/transaction/settlements` | 创建结算 | 新建结算申请 |
| GET | `/transaction/settlements` | 结算列表 | 供应商结算记录 |
| POST | `/transaction/settlements/{settlement_id}/process` | 处理结算 | 处理结算申请 |
| POST | `/transaction/refunds` | 创建退款 | 新建退款申请 |
| GET | `/transaction/refunds` | 退款列表 | 筛选查退款 |
| GET | `/transaction/refunds/{refund_id}` | 退款详情 | 按 ID 查退款 |
| PUT | `/transaction/refunds/{refund_id}/approve` | 批准退款 | 批准退款请求 |
| PUT | `/transaction/refunds/{refund_id}/reject` | 拒绝退款 | 拒绝退款请求 |

### 管理端 (`/api/v1/admin/orders`)

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/admin/orders` | 订单列表 | 高级筛选所有订单 |
| GET | `/admin/orders/stats` | 订单统计 | 订单统计概览 |
| GET | `/admin/orders/{order_id}` | 订单详情 | 管理端查看订单 |
| GET | `/admin/orders/no/{order_no}` | 按单号查 | 按订单号查订单 |
| PUT | `/admin/orders/{order_id}/status` | 更新状态 | 管理端更新订单状态 |
| POST | `/admin/orders/{order_id}/ship` | 发货 | 填写物流信息发货 |
| POST | `/admin/orders/{order_id}/refund` | 退款处理 | 处理订单退款 |
| POST | `/admin/orders/batch-ship` | 批量发货 | 批量发货多订单 |
| GET | `/admin/orders/export/download` | 导出订单 | JSON 或 CSV 导出 |

---

## 30. 物流模块 (logistics)

**路由前缀**: `/api/v1/logistics` | **需要认证**: 写操作 (admin/供应商)

### 快递公司

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/logistics/companies` | 快递公司列表 | 所有快递公司 |
| GET | `/logistics/companies/{company_code}` | 公司详情 | 按代码查快递公司 |

### 运费模板

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/logistics/templates` | 模板列表 | 所有运费模板 |
| GET | `/logistics/templates/{template_id}` | 模板详情 | 模板详情含计费规则 |
| POST | `/logistics/templates` | 创建模板 | 新建运费模板 |
| PUT | `/logistics/templates/{template_id}` | 更新模板 | 修改运费模板 |

### 物流操作

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| POST | `/logistics/calculate` | 计费计算 | 根据订单项计算运费 |
| GET | `/logistics/track/{tracking_number}` | 物流追踪 | 按快递单号追踪 |
| GET | `/logistics/track` | 指定公司追踪 | 带公司代码的追踪 (query: `company_code`) |
| POST | `/logistics/print` | 电子面单 | 生成快递电子面单数据 |
| GET | `/logistics/health` | 健康检查 | 物流模块健康检查 |

---

## 31. 配置数据模块 (config_data)

**路由前缀**: `/api/v1/config-data` | **需要认证**: 是 (admin)

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/config-data/list/{category}` | 按分类查询 | 获取某分类下所有配置项 |
| GET | `/config-data/item/{category}/{name}` | 按名称查询 | 获取单个配置项 |
| POST | `/config-data` | 创建配置 | 新建配置数据 |
| PUT | `/config-data/{category}/{name}` | 更新配置 | 修改配置项 |
| DELETE | `/config-data/{category}/{name}` | 删除配置 | 删除配置项 |
| POST | `/config-data/batch-update` | 批量更新 | 批量更新配置 (如拖拽保存坐标) |

---

## 32. 系统端点

### 系统级别

| 方法 | 路径 | 功能 | Query 参数 | 说明 |
|------|------|------|-----------|------|
| GET | `/api/health` | 健康检查 | - | 数据库连接 + 服务状态 |
| GET | `/api/file` | 文件代理 | path, private | **已废弃** → 302 到 TOS |
| GET | `/docs` | Swagger 文档 | - | FastAPI 自动生成的 API 文档 |
| GET | `/redoc` | ReDoc 文档 | - | 替代 API 文档格式 |
| GET | `/api/v1/debug/routes` | 路由调试 | - | 列出所有已注册路由 |

### 健康检查

```bash
GET /api/health

# 响应
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "connected"
}
```

### 文件代理 (过渡期)

```bash
GET /api/file?path=uploads/image.png

# 公开文件: 302 → TOS 自定义域名
# 私有文件: 302 → TOS 签名 URL
```

> **注意**: `/api/file` 已标记为废弃，建议直接使用 `/api/v1/storage/*` 端点。

---

## 附录 A: 认证方式汇总

### 无认证端点

以下模块/端点无需 Token 即可访问:
- auth: `/login`, `/register`, `/refresh`
- skills: `/skills` (GET), `/skills/{id}` (GET), `/skills/categories`, `/skills/stats`
- cms: `/cms/articles` (GET), `/cms/categories` (GET), `/cms/navigation` (GET)
- tutorials: 所有 GET 端点
- downloads: 所有 GET 端点
- store: 所有 GET 端点
- search: 所有端点
- i18n: 所有 GET 端点
- vendor: `/vendor/list`, `/vendor/{id}`, `/vendor/levels`
- config: `/config/versions`, `/config/version/{version}`, `/config/latest`, `/config/check`

### Bearer Token 认证

以下操作需要携带 JWT Token:
- 所有 POST/PUT/DELETE 操作
- `/auth/me`
- 所有 `payment/*` (除回调)
- 所有 `points/*`
- 所有 `tasks/*`
- 所有 `messages/*`
- 所有 `dashboard/*`
- 所有 `notifications/*`
- 所有 `affiliate/*`
- 所有 `storage/*` (上传/删除)

### Admin 认证

以下操作需要 admin 角色:
- 所有 `/admin/*`
- 所有 `/analytics/*`
- 所有 `/scheduler/*`
- 支付管理: `/payment/admin/*`
- 商城管理: `/store/admin/*`
- 配置发布: `POST /config/publish`
- Skills 审核: `POST /skills/{id}/review`

---

## 附录 B: 快速测试脚本

```bash
# 设置 API 地址
API="http://localhost:8000/api/v1"

# 1. 登录
TOKEN=$(curl -s -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sillymd.com","password":"admin123456"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

echo "Token: ${TOKEN:0:20}..."

# 2. 获取用户信息
curl -s "$API/auth/me" -H "Authorization: Bearer $TOKEN" | python -m json.tool

# 3. Skills 列表
curl -s "$API/skills?limit=5" | python -m json.tool

# 4. 仪表盘统计
curl -s "$API/dashboard/stats" -H "Authorization: Bearer $TOKEN" | python -m json.tool

# 5. 未读通知数
curl -s "$API/notifications/unread-count" -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

---

## 附录 C: 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-30 | 2.0.0 | 全新模块化端点清单，31 模块 ~400+ 端点完整文档 |
| 2026-04-29 | 1.0.0 | 迁移至模块化架构，统一 `/api/v1/*` 格式 |
