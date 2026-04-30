# 第二十八章：API 接口文档

> 本文档提供 SillyMD 平台所有 REST API 端点的完整参考。

## 28.1 API 概览

### 28.1.1 基础信息

| 项目 | 内容 |
|------|------|
| Base URL | `https://api.sillymd.com/v1` |
| 认证方式 | Bearer Token (JWT) / API Key |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 限流策略 | 1000 requests/hour per user |

### 28.1.2 通用响应格式

**成功响应**
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  }
}
```

### 28.1.3 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 无内容（删除成功） |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

## 28.2 认证与授权

### 28.2.1 用户注册

```
POST /auth/register
```

**请求体**
```json
{
  "username": "string (3-50字符)",
  "email": "string (有效邮箱)",
  "password": "string (8-100字符)",
  "role": "user | vendor"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "user_id": "number",
    "username": "string",
    "email": "string",
    "role": "string",
    "access_token": "string (JWT)",
    "refresh_token": "string"
  }
}
```

### 28.2.2 用户登录

```
POST /auth/login
```

**请求体**
```json
{
  "username_or_email": "string",
  "password": "string"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "user_id": "number",
    "access_token": "string",
    "refresh_token": "string",
    "expires_in": 86400
  }
}
```

### 28.2.3 刷新 Token

```
POST /auth/refresh
```

**请求体**
```json
{
  "refresh_token": "string"
}
```

### 28.2.4 OAuth 登录

```
POST /auth/oauth/{provider}
```

**参数**
- `provider`: `github` | `google` | `wechat`

**请求体**
```json
{
  "code": "string",
  "redirect_uri": "string"
}
```

## 28.3 用户管理

### 28.3.1 获取当前用户信息

```
GET /users/me
```

**响应**
```json
{
  "success": true,
  "data": {
    "id": 12345,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "vendor",
    "avatar_url": "https://...",
    "bio": "全栈开发者",
    "created_at": "2024-01-01T00:00:00Z",
    "points": 5000,
    "level": 5
  }
}
```

### 28.3.2 更新用户信息

```
PATCH /users/me
```

**请求体**
```json
{
  "bio": "string",
  "avatar_url": "string",
  "preferences": {
    "theme": "light | dark",
    "language": "zh-CN | en-US",
    "notifications": {
      "email": true,
      "push": false
    }
  }
}
```

### 28.3.3 获取用户公开信息

```
GET /users/{user_id}
```

### 28.3.4 修改密码

```
POST /users/me/change-password
```

**请求体**
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

## 28.4 Skills 管理

### 28.4.1 创建 Skill

```
POST /skills
```

**请求体**
```json
{
  "name": "string (3-100字符)",
  "description": "string (1-500字符)",
  "category": "tech | product | design | marketing | ops",
  "content": "string (Markdown格式)",
  "tags": ["tag1", "tag2"],
  "is_commercial": false,
  "license_type": "free | commercial"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "id": 789,
    "name": "React 组件开发规范",
    "slug": "react-component-guidelines",
    "version": "1.0.0",
    "author": {
      "id": 12345,
      "username": "johndoe"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "content_hash": "sha256:..."
  }
}
```

### 28.4.2 获取 Skill 详情

```
GET /skills/{skill_id}
```

**查询参数**
- `version`: 指定版本（可选）

### 28.4.3 更新 Skill

```
PUT /skills/{skill_id}
```

**请求体**
```json
{
  "name": "string",
  "description": "string",
  "content": "string",
  "tags": ["array"],
  "version_bump": "major | minor | patch"
}
```

### 28.4.4 删除 Skill

```
DELETE /skills/{skill_id}
```

### 28.4.5 搜索 Skills

```
GET /skills
```

**查询参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| q | string | 搜索关键词 |
| category | string | 分类筛选 |
| tags | string | 标签筛选（逗号分隔） |
| sort | string | 排序：`relevance`, `latest`, `popular`, `rating` |
| page | integer | 页码（默认1） |
| page_size | integer | 每页数量（默认20，最大100） |
| is_commercial | boolean | 是否商用 |

**示例**
```
GET /skills?q=react&category=tech&sort=popular&page=1&page_size=20
```

**响应**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 789,
        "name": "React 组件开发规范",
        "description": "...",
        "category": "tech",
        "author": {
          "username": "johndoe"
        },
        "stats": {
          "views": 1523,
          "favorites": 89,
          "rating": 4.7
        }
      }
    ],
    "total": 152,
    "page": 1,
    "page_size": 20
  }
}
```

### 28.4.6 Fork Skill

```
POST /skills/{skill_id}/fork
```

**响应**
```json
{
  "success": true,
  "data": {
    "id": 790,
    "parent_id": 789,
    "name": "React 组件开发规范 (Fork)",
    "forked_from": {
      "id": 789,
      "author": "johndoe"
    }
  }
}
```

### 28.4.7 收藏/取消收藏

```
POST /skills/{skill_id}/favorite
DELETE /skills/{skill_id}/favorite
```

### 28.4.8 评分

```
POST /skills/{skill_id}/rate
```

**请求体**
```json
{
  "rating": "number (1-5)",
  "comment": "string (可选)"
}
```

## 28.5 版本控制

### 28.5.1 获取版本列表

```
GET /skills/{skill_id}/versions
```

**响应**
```json
{
  "success": true,
  "data": {
    "versions": [
      {
        "version": "1.0.0",
        "created_at": "2024-01-15T10:30:00Z",
        "message": "初始版本"
      },
      {
        "version": "1.1.0",
        "created_at": "2024-01-20T14:22:00Z",
        "message": "新增组件示例"
      }
    ]
  }
}
```

### 28.5.2 版本对比

```
GET /skills/{skill_id}/versions/compare
```

**查询参数**
- `from`: 起始版本
- `to`: 目标版本

### 28.5.3 回滚版本

```
POST /skills/{skill_id}/versions/rollback
```

**请求体**
```json
{
  "version": "string"
}
```

## 28.6 团队协作

### 28.6.1 创建团队

```
POST /teams
```

**请求体**
```json
{
  "name": "string (3-50字符)",
  "description": "string",
  "avatar_url": "string",
  "visibility": "public | private"
}
```

### 28.6.2 获取团队信息

```
GET /teams/{team_id}
```

### 28.6.3 邀请成员

```
POST /teams/{team_id}/members
```

**请求体**
```json
{
  "user_id": "number",
  "role": "owner | admin | member | guest"
}
```

### 28.6.4 移除成员

```
DELETE /teams/{team_id}/members/{user_id}
```

### 28.6.5 更新成员角色

```
PATCH /teams/{team_id}/members/{user_id}
```

**请求体**
```json
{
  "role": "string"
}
```

### 28.6.6 创建项目

```
POST /teams/{team_id}/projects
```

**请求体**
```json
{
  "name": "string",
  "description": "string",
  "skills": ["skill_id1", "skill_id2"]
}
```

## 28.7 商用交易

### 28.7.1 创建商用 Skill

```
POST /commercial-skills
```

**请求体**
```json
{
  "skill_id": "number",
  "license_type": "personal | team | enterprise",
  "prices": {
    "personal": 100,
    "team": 300,
    "enterprise": 1000
  },
  "demo_content": "string"
}
```

### 28.7.2 购买授权

```
POST /orders
```

**请求体**
```json
{
  "items": [
    {
      "skill_id": 789,
      "license_type": "team",
      "quantity": 1
    }
  ],
  "payment_method": "points | alipay | wechat"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "order_id": "ORD20240115001",
    "total_amount": 300,
    "payment_url": "https://...",
    "expires_at": "2024-01-15T11:00:00Z"
  }
}
```

### 28.7.3 查询订单状态

```
GET /orders/{order_id}
```

### 28.7.4 获取我的授权

```
GET /licenses
```

**查询参数**
- `status`: `active` | `expired` | `all`

**响应**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "license_id": "LIC20240115001",
        "skill": {
          "id": 789,
          "name": "React 组件开发规范"
        },
        "license_type": "team",
        "expires_at": "2025-01-15T00:00:00Z",
        "status": "active",
        "certificate_url": "https://..."
      }
    ]
  }
}
```

### 28.7.5 验证授权

```
POST /licenses/verify
```

**请求体**
```json
{
  "license_id": "string",
  "skill_id": "number"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "license_type": "team",
    "expires_at": "2025-01-15T00:00:00Z",
    "content_hash": "sha256:...",
    "signature": "..."
  }
}
```

### 28.7.6 积分充值

```
POST /wallet/recharge
```

**请求体**
```json
{
  "amount": 1000,
  "payment_method": "alipay | wechat"
}
```

## 28.8 AI 审核

### 28.8.1 提交审核

```
POST /review/submit
```

**请求体**
```json
{
  "skill_id": "number"
}
```

### 28.8.2 查询审核状态

```
GET /review/{skill_id}
```

**响应**
```json
{
  "success": true,
  "data": {
    "status": "reviewing",
    "priority": "normal",
    "ai_result": {
      "approved": false,
      "confidence": 0.85,
      "scores": {
        "format": 0.9,
        "safety": 0.8,
        "quality": 0.7
      }
    },
    "submitted_at": "2024-01-15T10:00:00Z",
    "estimated_review_time": "2024-01-15T12:00:00Z"
  }
}
```

### 28.8.3 获取审核队列（管理员）

```
GET /admin/review/queue
```

**查询参数**
- `status`: `pending` | `reviewing` | `approved` | `rejected`
- `priority`: `low` | `normal` | `high` | `urgent`

### 28.8.4 审核通过/驳回（管理员）

```
POST /admin/review/{skill_id}/approve
POST /admin/review/{skill_id}/reject
```

## 28.9 资源中心

### 28.9.1 获取资源列表

```
GET /resources
```

**查询参数**
| 参数 | 说明 |
|------|------|
| type | `ide_plugin` | `ai_model` | `dev_tool` | `doc_template` |
| platform | `windows` | `macos` | `linux` |
| category | 资源分类ID |

### 28.9.2 下载资源

```
POST /resources/{resource_id}/download
```

**响应**
```json
{
  "success": true,
  "data": {
    "download_url": "https://...",
    "token": "string",
    "expires_at": "2024-01-15T11:00:00Z"
  }
}
```

## 28.10 社区功能

### 28.10.1 创建帖子

```
POST /community/posts
```

**请求体**
```json
{
  "title": "string",
  "content": "string (Markdown)",
  "topics": ["topic1", "topic2"]
}
```

### 28.10.2 获取帖子列表

```
GET /community/posts
```

**查询参数**
- `sort`: `latest` | `hot` | `top`

### 28.10.3 点赞帖子

```
POST /community/posts/{post_id}/like
DELETE /community/posts/{post_id}/like
```

### 28.10.4 评论帖子

```
POST /community/posts/{post_id}/comments
```

## 28.11 运营功能

### 28.11.1 获取排行榜

```
GET /leaderboards/{type}
```

**参数**
- `type`: `skills_hot` | `skills_new` | `users_active` | `vendors_earnings`

### 28.11.2 邀请用户

```
POST /invitations
```

**响应**
```json
{
  "success": true,
  "data": {
    "invitation_code": "ABCD1234",
    "invitation_url": "https://sillymd.com/register?invite=ABCD1234"
  }
}
```

## 28.12 管理后台

### 28.12.1 爬虫任务

```
POST /admin/crawler/tasks
GET /admin/crawler/tasks
POST /admin/crawler/tasks/{task_id}/start
POST /admin/crawler/tasks/{task_id}/pause
```

### 28.12.2 平台配置

```
GET /admin/config
PUT /admin/config
```

### 28.12.3 系统通知

```
POST /admin/notifications
GET /admin/notifications
PUT /admin/notifications/{id}
DELETE /admin/notifications/{id}
```

### 28.12.4 用户举报

```
GET /admin/reports
POST /admin/reports/{report_id}/resolve
```

## 28.13 WebSocket API

### 28.13.1 连接

```
wss://api.sillymd.com/v1/ws
```

**连接参数**
- `token`: JWT Token

### 28.13.2 订阅事件

```json
{
  "action": "subscribe",
  "channels": ["notifications", "skills:789"]
}
```

### 28.13.3 实时事件类型

| 事件 | 说明 |
|------|------|
| `notification.new` | 新通知 |
| `skill.updated` | Skill 更新 |
| `comment.new` | 新评论 |
| `team.invite` | 团队邀请 |

## 28.14 错误码参考

| 错误码 | 说明 |
|--------|------|
| `AUTH_001` | Token 无效 |
| `AUTH_002` | Token 已过期 |
| `USER_001` | 用户不存在 |
| `USER_002` | 用户名已被占用 |
| `SKILL_001` | Skill 不存在 |
| `SKILL_002` | 无权限修改此 Skill |
| `TEAM_001` | 团队不存在 |
| `TEAM_002` | 不是团队成员 |
| `PAYMENT_001` | 积分不足 |
| `PAYMENT_002` | 支付已过期 |
| `REVIEW_001` | Skill 正在审核中 |
| `RATE_LIMIT` | 请求过于频繁 |

## 28.15 SDK 使用示例

### Python SDK

```python
from sillymd import SillyMDClient

# 初始化客户端
client = SillyMDClient(api_key="your_api_key")

# 获取 Skill
skill = client.skills.get(789)

# 创建 Skill
new_skill = client.skills.create(
    name="My Skill",
    description="Description",
    content="# Content",
    category="tech"
)

# 搜索 Skills
results = client.skills.search(q="react", category="tech")
```

### JavaScript SDK

```javascript
import { SillyMDClient } from '@sillymd/sdk';

const client = new SillyMDClient({ apiKey: 'your_api_key' });

// 获取 Skill
const skill = await client.skills.get(789);

// 创建 Skill
const newSkill = await client.skills.create({
  name: 'My Skill',
  description: 'Description',
  content: '# Content',
  category: 'tech'
});

// 搜索 Skills
const results = await client.skills.search({
  q: 'react',
  category: 'tech'
});
```

---

**文档版本**: v1.0 | **最后更新**: 2026-02-03
