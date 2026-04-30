# SillyMD API 迁移指南 v1 → v2

> 旧系统 (server/api/main.py) → 新系统 (src/main.py) API 路径对照
> 供其他 APP / 客户端迁移参考
> 最后更新: 2026-04-30

---

## 概述

SillyMD 平台 API 已从分散的 `/api/xxx` 路径全面迁移至统一的模块化架构，前缀改为 `/api/v1/{module}`。

### 关键变更

| 变更项 | 旧系统 (v1) | 新系统 (v2) |
|--------|------------|------------|
| 入口文件 | `server/api/main.py` | `src/main.py` |
| API 前缀 | 不统一 (`/api/xxx`, `/api/v1/store`, `/application/`) | 统一 `/api/v1/{module}` |
| 架构 | 单片路由文件 | 插件模块化 (PluginManager) |
| 数据库 | 混合 (psycopg2 + SQLAlchemy) | 统一 (db_adapter: psycopg2) |
| 文件存储 | OSS (阿里云) | TOS (火山引擎) |
| 认证 | 不统一 (Depends + user_id 参数) | 统一 JWT Bearer Token |

### 迁移原则

1. **所有 API 路径都已变更**，旧路径不再可用
2. **认证方式统一**: 统一使用 `Authorization: Bearer <token>` 头
3. **响应格式不变**: 仍为 `{ "code": 200, "msg": "...", "data": {} }`
4. **查询参数基本保持**: 分页参数、筛选参数兼容
5. **新增模块**: tutorials, dashboard, analytics, config_sync, store, plus 9 v2-only 业务模块

---

## 认证模块 (Auth)

**旧前缀**: `/api/auth`
**新前缀**: `/api/v1/auth`
**前缀变更**: `/api/auth` → `/api/v1/auth`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 1 | `/api/auth/login` | `/api/v1/auth/login` | POST | 用户登录 | 路径变更，参数兼容 |
| 2 | `/api/auth/register` | `/api/v1/auth/register` | POST | 用户注册 | 路径变更 |
| 3 | `/api/auth/forgot-password` | `/api/v1/auth/forgot-password` | POST | 忘记密码 | 路径变更 |
| 4 | `/api/auth/reset-password` | `/api/v1/auth/reset-password` | POST | 重置密码 | 路径变更 |
| 5 | `/api/auth/refresh-token` | `/api/v1/auth/refresh` | POST | 刷新 Token | 路径名简化 |
| 6 | `/api/auth/verify-email/{token}` | `/api/v1/auth/verify-email/{token}` | POST | 验证邮箱 | 路径变更 |
| 7 | `/api/auth/logout` | `/api/v1/auth/logout` | POST | 退出登录 | 路径变更 |
| 8 | `/api/users/me` | `/api/v1/auth/me` | GET | 获取当前用户 | 模块从 users 移至 auth |

---

## 用户模块 (Users)

**旧前缀**: `/api/users`, `/api/user/settings`
**新前缀**: 拆分到 `/api/v1/auth` + `/api/v1/admin`
**状态**: 原独立用户模块拆分为 auth 和 admin 两个模块

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 9 | `/api/users/me` | `/api/v1/auth/me` | GET | 当前用户信息 | 模块切换 |
| 10 | `/api/users/profile` | `/api/v1/auth/me` (PUT) | PUT | 更新个人信息 | 路径变更 |
| 11 | `/api/users/favorites` | `/api/v1/auth/favorites` | GET | 收藏列表 | 路径变更 |
| 12 | `/api/users/favorites` | `/api/v1/auth/favorites` | POST | 添加收藏 | 路径变更 |
| 13 | `/api/users/favorites/{id}` | `/api/v1/auth/favorites/{id}` | DELETE | 删除收藏 | 路径变更 |
| 14 | `/api/users/stats` | `/api/v1/auth/stats` | GET | 用户统计 | 路径变更 |
| 15 | `/api/users/admin/list` | `/api/v1/admin/users` | GET | 管理员用户列表 | 移至 admin 模块 |
| 16 | `/api/user/settings/profile` | `/api/v1/auth/me` (GET/PUT) | GET | 用户设置 | 合并到 auth/me |
| 17 | `/api/user/settings/preferences` | `/api/v1/auth/preferences` | PUT | 用户偏好 | 路径变更 |
| 18 | `/api/user/settings/change-password` | `/api/v1/auth/change-password` | POST | 修改密码 | 路径变更 |
| 19 | `/api/user/settings/upload-avatar` | `/api/v1/storage/upload` | POST | 上传头像 | 使用 storage 模块 |

---

## 内容管理模块 (CMS)

**旧前缀**: (无独立模块，由 admin 覆盖)
**新前缀**: `/api/v1/cms`
**状态**: v2 新增独立 CMS 模块

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 20 | (旧 admin 内嵌) | `/api/v1/cms/articles` | GET | 文章列表 | v2 独立模块 |
| 21 | (旧 admin 内嵌) | `/api/v1/cms/articles/{id}` | GET | 文章详情 | v2 新增 |
| 22 | - | `/api/v1/cms/articles` | POST | 创建文章 | v2 新增 |
| 23 | - | `/api/v1/cms/articles/{id}` | PUT | 更新文章 | v2 新增 |
| 24 | - | `/api/v1/cms/articles/{id}` | DELETE | 删除文章 | v2 新增 |
| 25 | - | `/api/v1/cms/categories` | GET | 分类列表 | v2 新增 |
| 26 | - | `/api/v1/cms/categories` | POST | 创建分类 | v2 新增 |
| 27 | - | `/api/v1/cms/categories/{id}` | PUT | 更新分类 | v2 新增 |
| 28 | - | `/api/v1/cms/categories/{id}` | DELETE | 删除分类 | v2 新增 |
| 29 | - | `/api/v1/cms/navigation` | GET | 获取导航 | v2 新增 |
| 30 | - | `/api/v1/cms/navigation` | PUT | 更新导航 | v2 新增 |
| 31 | - | `/api/v1/cms/seo` | GET | SEO 设置 | v2 新增 |
| 32 | - | `/api/v1/cms/seo` | PUT | 更新 SEO | v2 新增 |

---

## 支付模块 (Payment)

**旧前缀**: `/api/payment`, `/api/payment/accounts`
**新前缀**: `/api/v1/payment`
**前缀变更**: `/api/payment` → `/api/v1/payment`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 33 | `/api/payment/orders` | `/api/v1/payment/orders` | POST | 创建订单 | 路径变更 |
| 34 | `/api/payment/pay` | `/api/v1/payment/create` | POST | 创建支付 | 路径名从 pay → create |
| 35 | `/api/payment/callback/wechat` | `/api/v1/payment/notify/wechat` | POST | 微信回调 | 路径从 callback → notify |
| 36 | `/api/payment/callback/alipay` | `/api/v1/payment/notify/alipay` | POST | 支付宝回调 | 同上 |
| 37 | `/api/payment/callback/paypal` | `/api/v1/payment/notify/paypal` | POST | PayPal 回调 | 同上 |
| 38 | `/api/payment/paypal/capture/{id}` | `/api/v1/payment/paypal/capture/{id}` | POST | PayPal 捕获 | 路径变更 |
| 39 | `/api/payment/orders` | `/api/v1/payment/orders` | GET | 我的订单 | 路径变更 |
| 40 | `/api/payment/my-purchases` | `/api/v1/payment/my-purchases` | GET | 我的购买记录 | 路径变更 |
| 41 | `/api/payment/submissions` | `/api/v1/payment/submissions` | POST | 提交作品 | 路径变更 |
| 42 | `/api/payment/submissions` | `/api/v1/payment/submissions` | GET | 作品列表 | 路径变更 |
| 43 | `/api/payment/admin/pending-submissions` | `/api/v1/payment/admin/submissions` | GET | 待审核作品 | 路径简化 |
| 44 | `/api/payment/admin/submissions/{id}/approve` | `/api/v1/payment/admin/submissions/{id}/approve` | PUT | 审核通过 | 路径变更 |
| 45 | `/api/payment/admin/submissions/{id}/reject` | `/api/v1/payment/admin/submissions/{id}/reject` | PUT | 审核拒绝 | 路径变更 |
| 46 | `/api/payment/admin/revenue/stats` | `/api/v1/payment/admin/revenue/stats` | GET | 收入统计 | 路径变更 |
| 47 | `/api/payment/admin/creator/earnings` | (已合并到下方) | GET | 管理员看收益 | 合并 |
| 48 | `/api/payment/accounts/` | `/api/v1/payment/accounts` | GET | 支付账户列表 | 路径变更 |
| 49 | `/api/payment/accounts/` | `/api/v1/payment/accounts` | POST | 创建支付账户 | 路径变更 |
| 50 | `/api/payment/accounts/{id}` | `/api/v1/payment/accounts/{id}` | PUT | 更新支付账户 | 路径变更 |
| 51 | `/api/payment/accounts/{id}` | `/api/v1/payment/accounts/{id}` | DELETE | 删除支付账户 | 路径变更 |
| 52 | `/api/payment/accounts/creator/preference` | `/api/v1/payment/accounts/creator/preference` | GET | 创作者偏好 | 路径变更 |
| 53 | `/api/payment/accounts/creator/preference` | `/api/v1/payment/accounts/creator/preference` | PUT | 更新创作者偏好 | 路径变更 |
| 54 | `/api/payment/accounts/creator/earnings` | `/api/v1/payment/accounts/creator/earnings` | GET | 创作者收益 | 路径变更 |
| 55 | `/api/payment/accounts/creator/earnings/summary` | `/api/v1/payment/accounts/creator/earnings` | GET | 收益摘要 | 合并到收益接口 |
| 56 | `/api/payment/accounts/creator/settle` | `/api/v1/payment/accounts/creator/settle` | POST | 创作者结算 | 路径变更 |
| 57 | `/api/payment/accounts/creator/settlements` | `/api/v1/payment/accounts/creator/settlements` | GET | 结算记录 | 路径变更 |
| 58 | `/api/payment/accounts/admin/pending-settlements` | (已合并) | GET | 待处理结算 | 合并到 admin |
| 59 | `/api/payment/accounts/admin/settle/{user_id}` | (已合并) | POST | 管理员结算 | 合并到 admin |

---

## 积分模块 (Points)

**旧前缀**: `/api/points`
**新前缀**: `/api/v1/points`
**前缀变更**: `/api/points` → `/api/v1/points`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 60 | `/api/points/categories` | `/api/v1/points/categories` | GET | 商品分类 | 路径变更 |
| 61 | `/api/points/products` | `/api/v1/points/mall/items` | GET | 商品列表 | 路径名变更 |
| 62 | `/api/points/products/{id}` | `/api/v1/points/mall/items/{id}` | GET | 商品详情 | 路径名变更 |
| 63 | `/api/points/products` | `/api/v1/points/admin/products` | POST | 创建商品 | 路径移至 admin |
| 64 | `/api/points/products/{id}` | `/api/v1/points/admin/products/{id}` | PUT | 更新商品 | 同上 |
| 65 | `/api/points/products/{id}` | `/api/v1/points/admin/products/{id}` | DELETE | 删除商品 | 同上 |
| 66 | `/api/points/cart` | `/api/v1/points/cart` | GET | 购物车 | 路径变更，认证改为 Token |
| 67 | `/api/points/cart` | `/api/v1/points/cart` | POST | 添加到购物车 | 路径变更 |
| 68 | `/api/points/cart/{id}` | `/api/v1/points/cart/{id}` | PUT | 更新购物车 | 路径变更 |
| 69 | `/api/points/cart/{id}` | `/api/v1/points/cart/{id}` | DELETE | 删除购物车项 | 路径变更 |
| 70 | `/api/points/cart` (DELETE) | `/api/v1/points/cart` (DELETE) | DELETE | 清空购物车 | 路径变更 |
| 71 | `/api/points/exchange` | `/api/v1/points/mall/exchange` | POST | 兑换商品 | 路径变更 |
| 72 | `/api/points/exchanges` | `/api/v1/points/history` | GET | 兑换记录 | 合并到积分历史 |
| 73 | `/api/points/balance` | `/api/v1/points/balance` | GET | 积分余额 | 路径变更 |
| 74 | `/api/points/stats` | `/api/v1/points/stats/admin` | GET | 积分统计 | 路径变更 |
| 75 | `/api/points/transactions` | `/api/v1/points/history` | GET | 积分流水 | 合并到积分历史 |
| 76 | `/api/points/stats/user` | `/api/v1/points/stats/user` | GET | 用户积分统计 | 路径变更 |

> **重要变更**: 旧 points 模块使用 `user_id` 查询参数认证，新系统统一使用 JWT Bearer Token。

---

## 任务模块 (Tasks)

**旧前缀**: `/api/tasks`
**新前缀**: `/api/v1/tasks`
**前缀变更**: `/api/tasks` → `/api/v1/tasks`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 77 | `/api/tasks/sign-in` | `/api/v1/tasks/check-in` | POST | 每日签到 | 路径名变更 |
| 78 | `/api/tasks/sign-in/status` | `/api/v1/tasks/check-in` | GET | 签到状态 | 路径名变更 |
| 79 | `/api/tasks/sign-in/calendar` | `/api/v1/tasks/check-in/calendar` | GET | 签到日历 | 路径名变更 |
| 80 | `/api/tasks/daily` | `/api/v1/tasks/daily` | GET | 每日任务 | 路径变更 |
| 81 | `/api/tasks/daily/{id}/claim` | `/api/v1/tasks/{id}/claim` | POST | 领取奖励 | 路径简化 |
| 82 | `/api/tasks/achievements` | `/api/v1/tasks/achievements` | GET | 成就列表 | 路径变更 |
| 83 | `/api/tasks/achievements/unlocked` | `/api/v1/tasks/achievements` | GET | 已解锁成就 | 合并到成就列表 |
| 84 | `/api/tasks/stats` | `/api/v1/tasks/stats` | GET | 任务统计 | 路径变更 |
| 85 | `/api/tasks/admin/daily-tasks` | `/api/v1/tasks/definitions` | GET | 任务定义 | 路径变更 |
| 86 | `/api/tasks/admin/achievements` | `/api/v1/tasks/achievement-definitions` | GET | 成就定义 | 路径变更 |

---

## 下载模块 (Downloads)

**旧前缀**: `/api/content/downloads`
**新前缀**: `/api/v1/downloads`
**前缀变更**: `/api/content/downloads` → `/api/v1/downloads`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 87 | `/api/content/downloads/` | `/api/v1/downloads` | GET | 下载列表 | 移除 content 前缀 |
| 88 | `/api/content/downloads/featured` | `/api/v1/downloads` (featured=true) | GET | 精选下载 | 改为查询参数 |
| 89 | `/api/content/downloads/categories` | `/api/v1/downloads/categories` | GET | 分类列表 | 路径变更 |
| 90 | `/api/content/downloads/{id_or_slug}` | `/api/v1/downloads/{id}` | GET | 下载详情 | 支持 ID 或 slug |
| 91 | `/api/content/downloads/{id}/record-download` | `/api/v1/downloads/{id}/record-download` | POST | 记录下载 | 路径变更 |
| 92 | `/api/content/downloads/{id}/like` | `/api/v1/downloads/{id}/like` | POST | 点赞 | 路径变更 |

---

## 消息模块 (Messages)

**旧前缀**: `/api` (直接定义)
**新前缀**: `/api/v1/messages`
**前缀变更**: `/api/conversations` → `/api/v1/messages/conversations`, `/api/messages` → `/api/v1/messages`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 93 | `/api/conversations` | `/api/v1/messages/conversations` | GET | 对话列表 | 前缀 + 模块路径变更 |
| 94 | `/api/conversations/{id}/messages` | `/api/v1/messages?conversation_id={id}` | GET | 对话消息 | 改为查询参数 |
| 95 | `/api/conversations` | `/api/v1/messages/conversations` | POST | 创建对话 | 前缀变更 |
| 96 | `/api/messages` | `/api/v1/messages` | POST | 发送消息 | 前缀变更 |
| 97 | `/api/messages/{id}/read` | `/api/v1/messages/{id}/read` | PUT | 标记已读 | 前缀变更 |
| 98 | `/api/conversations/{id}/read` | `/api/v1/messages/conversations/{id}/read` | PUT | 标记对话已读 | 前缀变更 |
| 99 | `/api/conversations/unread-count` | `/api/v1/messages/unread-count` | GET | 未读计数 | 路径变更 |
| 100 | `/api/conversations/{id}` | `/api/v1/messages/conversations/{id}` | DELETE | 删除对话 | 前缀变更 |

---

## 教程模块 (Tutorials)

**旧前缀**: `/api/content/tutorials`
**新前缀**: `/api/v1/tutorials`
**状态**: v2 独立模块

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 101 | `/api/content/tutorials/` | `/api/v1/tutorials` | GET | 教程列表 | 移除 content 前缀 |
| 102 | `/api/content/tutorials/featured` | `/api/v1/tutorials/featured` | GET | 精选教程 | 路径变更 |
| 103 | `/api/content/tutorials/categories` | `/api/v1/tutorials/categories` | GET | 教程分类 | 路径变更 |
| 104 | `/api/content/tutorials/{id_or_slug}` | `/api/v1/tutorials/{id_or_slug}` | GET | 教程详情 | 路径变更 |
| 105 | `/api/content/tutorials/{id}/view` | `/api/v1/tutorials/{id}/view` | POST | 记录浏览 | 路径变更 |
| 106 | `/api/content/tutorials/{id}/like` | `/api/v1/tutorials/{id}/like` | POST | 点赞教程 | 路径变更 |

---

## 仪表盘模块 (Dashboard)

**旧前缀**: `/api/dashboard`
**新前缀**: `/api/v1/dashboard`
**状态**: v2 独立模块

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 107 | `/api/dashboard/stats` | `/api/v1/dashboard/stats` | GET | 统计概览 | 路径变更 |
| 108 | `/api/dashboard/recent-activity` | `/api/v1/dashboard/recent-activity` | GET | 最近活动 | 路径变更 |
| 109 | `/api/dashboard/quick-actions` | `/api/v1/dashboard/quick-actions` | GET | 快捷操作 | 路径变更 |
| 110 | `/api/dashboard/user-activity` | `/api/v1/dashboard/user-activity` | GET | 用户活动 | 路径变更 |
| 111 | `/api/dashboard/overview` | `/api/v1/dashboard/overview` | GET | 仪表盘总览 | 路径变更 |

---

## 分析模块 (Analytics)

**旧前缀**: `/api/analytics`
**新前缀**: `/api/v1/analytics`
**状态**: v2 独立模块，增加权限控制

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 112 | `/api/analytics/overview` | `/api/v1/analytics/overview` | GET | 分析概览 | 路径变更，需 admin |
| 113 | `/api/analytics/trend` | `/api/v1/analytics/trend` | GET | 趋势数据 | 路径变更 |
| 114 | `/api/analytics/top-pages` | `/api/v1/analytics/top-pages` | GET | 热门页面 | 路径变更 |
| 115 | `/api/analytics/user-activity` | `/api/v1/analytics/user-activity` | GET | 用户活动 | 路径变更 |
| 116 | `/api/analytics/hourly` | `/api/v1/analytics/hourly` | GET | 每小时统计 | 路径变更 |
| 117 | `/api/analytics/export` | `/api/v1/analytics/export` | GET | 导出数据 | 路径变更 |

---

## 配置同步模块 (Config Sync)

**旧前缀**: `/api/config` (在 main.py 中指定)
**新前缀**: `/api/v1/config`
**状态**: v2 独立模块，重构端点

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 118 | `/api/config/version` | `/api/v1/config/versions` | GET | 版本列表 | 路径变更 |
| 119 | `/api/config/version/{version}` | `/api/v1/config/version/{version}` | GET | 指定版本 | 路径变更 |
| 120 | `/api/config/publish` | `/api/v1/config/publish` | POST | 发布配置 | 路径变更 |
| 121 | `/api/config/stats` | (已移除) | GET | 配置统计 | 不再提供 |
| 122 | `/api/config/file` | (已移除) | GET | 下载配置文件 | 不再提供，使用 storage |

---

## 商城模块 (Store)

**旧前缀**: `/api/v1/store` (已用 v1 前缀)
**新前缀**: `/api/v1/store` (保持不变)
**状态**: 路径基本不变，认证方式增强

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 123 | `/api/v1/store/collections` | `/api/v1/store/collections` | GET | 商品集合 | 不变 |
| 124 | `/api/v1/store/collections/{key}` | `/api/v1/store/collections/{key}` | GET | 集合详情 | 不变 |
| 125 | `/api/v1/store/collections/{key}/products` | `/api/v1/store/collections/{key}/products` | GET | 集合商品 | 不变 |
| 126 | `/api/v1/store/products/{id}` | `/api/v1/store/products/{id}` | GET | 商品详情 | 不变 |
| 127 | `/api/v1/store/cart` | `/api/v1/store/cart` | GET | 购物车 | 认证改为 Token |
| 128-131 | ... | ... | ... | 购物车 CRUD | 路径不变，认证改为 Token |
| 132 | `/api/v1/store/orders` | `/api/v1/store/orders` | POST | 创建订单 | 认证改为 Token |
| 133 | `/api/v1/store/orders` | `/api/v1/store/orders` | GET | 订单列表 | 认证改为 Token |
| 136 | `/api/v1/store/orders/{no}/pay` | `/api/v1/store/orders/{no}/pay` | POST | 支付 | 认证改为 Token |
| 141-153 | `/api/v1/store/admin/*` | `/api/v1/store/admin/*` | GET/POST/PUT/DELETE | 管理端 | 路径不变，需 admin Token |

> **注意**: store 模块旧系统已使用 `/api/v1/` 前缀，路径基本不变。但认证方式从 `user_id` 查询参数改为 JWT Bearer Token。

---

## Skills/供应商/系统模块

### Skills

**旧前缀**: `/api/skills`
**新前缀**: `/api/v1/skills`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 154 | `/api/skills` | `/api/v1/skills` | GET | Skills 列表 | 前缀变更 |
| 155 | `/api/skills/{id}` | `/api/v1/skills/{id}` | GET | Skill 详情 | 前缀变更 |
| 156 | - | `/api/v1/skills` | POST | 创建 Skill | v2 新增 |
| 157 | - | `/api/v1/skills/{id}` | PUT | 更新 Skill | v2 新增 |
| 158 | - | `/api/v1/skills/{id}` | DELETE | 删除 Skill | v2 新增 |

### 供应商

**旧前缀**: (无独立模块)
**新前缀**: `/api/v1/vendor`

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 159 | - | `/api/v1/vendor/list` | GET | 供应商列表 | v2 新增 |
| 160 | - | `/api/v1/vendor/apply` | POST | 申请供应商 | v2 新增 |

### 系统

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 161 | `/api/health` | `/api/health` | GET | 健康检查 | 不变 |
| 162 | `/api/debug/routes` | `/api/v1/debug/routes` | GET | 路由调试 | 前缀变更 |
| 163 | `/api/market/stats` | `/api/v1/skills/stats` | GET | 市场统计 | 移至 skills 模块 |
| 164 | `/api/users` | `/api/v1/admin/users` | GET | 用户列表 | 移至 admin 模块 |
| 165 | `/api/users/{username}` | `/api/v1/admin/users/{id}` | GET | 用户详情 | 以 ID 替代 username |
| 166 | `/api/teams` | (已移除) | GET | 团队列表 | 不再提供 |

---

## 文件上传 (Upload → Storage)

**旧系统**: OSS 上传
**新系统**: TOS 上传

| # | 旧路径 | 新路径 | 方法 | 功能 | 变更说明 |
|---|--------|--------|------|------|---------|
| 167 | `/application/upload/api` | `/api/v1/storage/upload` | POST | 文件上传 | OSS → TOS，认证改为 Token |
| 168 | `/application/uploads/{filename}` | `/api/v1/storage/signed-url/{key}` | GET | 获取文件 | 改为签名 URL 方式 |
| 169 | `/application/upload/query` | `/api/v1/storage/list/{folder}` | GET | 查询文件 | 路径和参数格式变更 |
| 170 | `/application/upload/url` | `/api/v1/storage/upload/base64` | POST | URL/Base64 上传 | 功能变更 |
| 171 | `/api/file?path=xxx` | `/api/file?path=xxx` | GET | 文件代理 | 保留兼容，改为 TOS 302 |

---

## v2 模块速览 (无旧路径映射)

以下模块在 v2 中独立存在，旧系统中无直接对应路径。对客户端而言属于新接口，可直接按 `/api/v1/{module}` 调用。

| 模块 | 前缀 | 核心功能 |
|------|------|---------|
| affiliate | `/api/v1/affiliate` | 联属营销 (推广链接、佣金、提现) |
| notifications | `/api/v1/notifications` | 系统通知 (列表、已读、偏好设置) |
| sillyclaw | `/api/v1/sillyclaw` | 版本升级检查 |
| search | `/api/v1/search` | 全局搜索 (Skills/教程/文章) |
| scheduler | `/api/v1/scheduler` | 定时任务管理 (admin) |
| i18n | `/api/v1/i18n` | 国际化 (语言切换、翻译管理) |
| storage | `/api/v1/storage` | 统一文件存储 (TOS 上传/下载/管理) |

> 此外还有 **9 个业务模块** (arena, recommendations, goods, marketplace, promotion, staff, transaction, logistics, config_data) 属于 v2 新建，详见下方 [v2 新增模块 (旧系统无对应)](#v2-新增模块-旧系统无对应) 章节。

---

## 客户端迁移清单

### Android/iOS 客户端

```kotlin
// 旧
const val BASE_URL = "https://api.example.com"
const val API_AUTH = "$BASE_URL/api/auth"
const val API_PAYMENT = "$BASE_URL/api/payment"

// 新
const val BASE_URL = "https://api.example.com"
const val API_VERSION = "/api/v1"
const val API_AUTH = "$BASE_URL$API_VERSION/auth"
const val API_PAYMENT = "$BASE_URL$API_VERSION/payment"
```

### Web 前端

```javascript
// 旧
const api = axios.create({ baseURL: '/api' })
api.get('/auth/login', data)

// 新
const api = axios.create({ baseURL: '/api/v1' })
api.get('/auth/login', data)
```

### SillyClaw 客户端

```cpp
// 旧
#define API_BASE "https://api.example.com"
#define CHECK_UPDATE "/api/v1/sillyclaw/check-update"

// 新 (不变 - SillyClaw 已使用 v1 前缀)
#define API_BASE "https://api.example.com"
#define CHECK_UPDATE "/api/v1/sillyclaw/check-update"
```

### 认证方式变更

```javascript
// 旧 (部分端点使用 user_id 查询参数)
fetch('/api/points/balance?user_id=123')

// 新 (统一使用 JWT Bearer Token)
fetch('/api/v1/points/balance', {
  headers: { 'Authorization': 'Bearer ' + accessToken }
})
```

---

## 快速查阅表

### 按旧路径前缀查找新路径

| 旧路径前缀 | 新路径前缀 |
|-----------|-----------|
| `/api/auth/*` | `/api/v1/auth/*` |
| `/api/users/*` | `/api/v1/auth/*` 或 `/api/v1/admin/*` |
| `/api/user/settings/*` | `/api/v1/auth/*` |
| `/api/payment/*` | `/api/v1/payment/*` |
| `/api/points/*` | `/api/v1/points/*` |
| `/api/tasks/*` | `/api/v1/tasks/*` |
| `/api/conversations/*` | `/api/v1/messages/conversations/*` |
| `/api/messages/*` | `/api/v1/messages/*` |
| `/api/content/tutorials/*` | `/api/v1/tutorials/*` |
| `/api/content/downloads/*` | `/api/v1/downloads/*` |
| `/api/dashboard/*` | `/api/v1/dashboard/*` |
| `/api/analytics/*` | `/api/v1/analytics/*` |
| `/api/config/*` | `/api/v1/config/*` |
| `/api/v1/store/*` | `/api/v1/store/*` (不变) |
| `/api/skills/*` | `/api/v1/skills/*` |
| `/application/*` | `/api/v1/storage/*` |
| `/api/health` | `/api/health` (不变) |
| `/api/file` | `/api/file` (兼容，已废弃) |

---

## v2 新增模块 (旧系统无对应)

以下模块仅在 v2 (模块化架构) 存在，v1 系统中无对应端点。旧客户端无需迁移，可直接对接新 API。

| # | 模块 | 前缀 | 说明 | 端点数 |
|---|------|------|------|--------|
| 1 | `arena` | `/api/v1/arena` | 竞技场 PK 房间、对战、排行榜 | 11 |
| 2 | `recommendations` | (挂载决定) | Skills 推荐/热门/最新列表，ClawHub 同步 | 8 |
| 3 | `goods` | `/api/v1/goods` | 商品 CRUD + 分类树 + 供应商管理 | 20 |
| 4 | `marketplace` | `/api/v1/marketplace` | 交易市场挂牌/购买/评价/统计 | 21 |
| 5 | `promotion` | `/api/v1/promotions` | 促销活动/优惠券/闪购 | 24 |
| 6 | `staff` | `/api/v1/staff` | 员工 RBAC 管理 (用户/角色/权限/审计) | 22 |
| 7 | `transaction` | `/api/v1/transaction` + `/api/v1/admin/orders` | 订单/结算/退款 (用户端 + 管理端双路由) | 22 |
| 8 | `logistics` | `/api/v1/logistics` | 快递公司/运费模板/物流追踪/电子面单 | 11 |
| 9 | `config_data` | `/api/v1/config-data` | 结构化配置数据 CRUD (拖拽坐标等) | 6 |

### 新增模块的典型使用场景

| 场景 | 使用的模块 |
|------|-----------|
| 用户 PK 对战 | `arena` — 创建房间 → 加入 → 开始对战 → 提交答案 → 查看结果/排名 |
| Skills 发现与分发 | `recommendations` — 推荐/热门/最新列表 + 下载 ClawHub Skills |
| 实体商品电商 | `goods` + `marketplace` — 商品上架 → 分类 → 挂牌 → 购买 → 评价 |
| 营销活动 | `promotion` — 创建优惠券/促销/闪购 → 用户领取 → 应用订单 |
| 内部管理 | `staff` — 角色权限 RBAC + 用户管理 + 审计日志 |
| 交易履约 | `transaction` + `logistics` — 下单 → 支付 → 发货/追踪 → 结算/退款 |
| 配置热更新 | `config_data` — 按分类读写配置项，支持批量更新 |

### 新模块认证要求

所有新增模块统一使用 JWT Bearer Token 认证：
- **公开查询**: `arena/*` (GET), `recommendations/*` (GET), `goods/products*` (GET), `marketplace/listings*` (GET), `promotions/active`, `logistics/companies`
- **用户认证**: 所有 POST/PUT/DELETE 及个人信息端点
- **管理权限**: `staff/*`, `promotion/*` (admin), `transaction/admin/*`

---

## 附录

### 迁移注意事项

1. **逐步迁移**: 建议先切换认证模块，再逐步迁移业务模块
2. **保留旧 Token 机制**: JWT 格式不变，无需重新设计认证流程
3. **测试环境验证**: 新 API 端口建议先在测试环境验证完整功能
4. **回退方案**: 保留 `server/api/` 备份，出现问题可快速回退

### 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-30 | 2.0.0 | 完整迁移文档，161 个旧端点 → 280+ 个新端点对照，含 9 个 v2 新增模块 |
