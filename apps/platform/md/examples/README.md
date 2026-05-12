# SillyMD 前端示例页面

本目录包含 SillyMD 平台前端示例页面，全部使用原生 HTML5/CSS3/JavaScript 构建，通过 `/api/v1/` 前缀连接模块化后端 API。

## 已实现的功能

### 1. 完整页面体系

| 页面 | 文件 | 说明 |
|------|------|------|
| 首页 | `index.html` | 平台主页 (Hero、Skills 展示、供应商) |
| Skills 市场 | `skills.html` | Skills 浏览与筛选 |
| Skill 详情 | `skill-detail.html` | 单个 Skill 详情展示 |
| 实时数据版 | `skills-real.html` | 连接真实 API 的 Skills 页 |
| 登录 | `login.html` | 用户登录 |
| 注册 | `register.html` | 用户注册 |
| 忘记密码 | `forgot-password.html` | 密码找回 |
| 重置密码 | `reset-password.html` | 重置密码 |
| 仪表盘 | `dashboard.html` | 用户仪表盘 |
| 用户中心 | `user-center.html` | 个人中心 |
| 下载中心 | `downloads.html` | 下载资源列表 |
| 教程中心 | `tutorials.html` | 教程浏览 |
| 任务中心 | `tasks.html` | 每日任务与签到 |
| 积分商城 | `points-mall.html` | 积分兑换 |
| 电商商城 | `store.html` | 实物商品购买 |
| 供应商 | `vendor-apply.html` | 供应商申请 |
| 消息中心 | `messages.html` | 消息与对话 |
| 数据分析 | `analytics.html` | 数据看板 |
| 平台功能 | `features.html` | 功能介绍页 |
| 创作中心 | `creation.html` | 创作管理 |
| 市场 | `marketplace.html` | 综合市场 |
| 项目 | `projects.html` | 项目管理 |
| 设置 | `settings.html` | 系统设置 |
| SillyClaw | `sillyclaw.html` | 虾拳馆 PK |
| OpenClaw | `openclaw.html` | OpenClaw 对接 |
| 测试 API | `test-api.html` | API 调试工具 |
| 调试 API | `debug-api.html` | 模块路由调试 |
| 种子演示 | `demo-seed.html` | 种子数据展示 |

### 2. 主题系统

6 种主题风格 (CSS 变量实现)：
- 科技蓝 (默认)
- 海洋 (Ocean)
- 森林 (Forest)
- 日落 (Sunset)
- 紫韵 (Purple)
- 赛博 (Cyberpunk)

主题文件位于 `css/themes/` 目录。

### 3. API 集成

示例页面通过以下方式连接后端:

```javascript
// API 基础路径
const API_BASE = 'http://localhost:8000/api/v1';

// 获取 Skills 列表
fetch(`${API_BASE}/skills?limit=10`)
  .then(res => res.json())
  .then(data => console.log(data));

// 用户登录
fetch(`${API_BASE}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
```

相关 JS 文件:
- `js/config.js` - API 配置
- `js/skills-api.js` - Skills API 调用
- `js/skill-detail-api.js` - Skill 详情 API
- `js/vendor-api.js` - 供应商 API
- `js/sillymd-realdata.js` - 真实数据加载
- `js/auth.js` - 认证逻辑
- `js/dashboard.js` - 仪表盘
- `js/analytics.js` - 数据分析
- `js/messages.js` - 消息
- `js/i18n.js` - 国际化

### 4. 响应式设计

- 断点：480px、768px、1024px
- 移动端汉堡菜单
- 触控友好交互
- 自适应布局

## 文件结构

```
examples/
├── index.html              # 首页
├── *.html                  # 各功能页面
├── styles.css              # 全局样式
├── css/                    # 样式目录
│   ├── style.css           # 主样式
│   ├── dashboard.css       # 仪表盘样式
│   ├── auth.css            # 认证页面样式
│   ├── settings.css        # 设置页面样式
│   ├── responsive.css      # 响应式样式
│   ├── tech-blue.css       # 科技蓝主题
│   └── themes/             # 主题样式
│       ├── ocean-teal.css
│       ├── emerald-green.css
│       ├── sunset-gold.css
│       ├── cyber-purple.css
│       ├── rose-pink.css
│       ├── coral-orange.css
│       └── midnight-dark.css
├── js/                     # JavaScript 脚本
│   ├── config.js           # API 配置
│   ├── main.js             # 主逻辑
│   ├── auth.js             # 认证
│   ├── i18n.js             # 国际化
│   ├── theme.js            # 主题切换
│   ├── mobile-menu.js      # 移动端菜单
│   ├── skills-api.js       # Skills API
│   ├── skill-detail-api.js # Skill 详情
│   ├── vendor-api.js       # 供应商 API
│   ├── sillymd-realdata.js # 真实数据
│   ├── dashboard.js        # 仪表盘
│   ├── analytics.js        # 分析
│   ├── messages.js         # 消息
│   ├── projects.js         # 项目
│   └── settings.js         # 设置
└── social/                 # 社交媒体图标
    ├── 抖音.png
    ├── 小红书.png
    └── 视频号.png
```

## 使用方式

### 直接在浏览器中打开

```bash
# Windows
start index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

### 使用本地服务器

```bash
# Python 3
python -m http.server 8080

# Node.js
npx http-server -p 8080

# 然后访问 http://localhost:8080
```

### 连接后端 API

1. 确保后端已启动: `cd src && python production.py`（开发模式: `uvicorn main:app --reload`）
2. 修改 `js/config.js` 中的 API 地址
3. 页面会自动通过 `/api/v1/` 前缀调用后端接口

## 技术栈

- 纯 HTML5 + CSS3
- 原生 JavaScript (ES6+, 无依赖)
- CSS Variables (主题切换)
- CSS Grid + Flexbox
- Fetch API (后端通信)
- LocalStorage (状态持久化)

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

**最后更新**: 2026-04-30
