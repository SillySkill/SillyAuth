# SillyMD Skills 在线平台 - 文档导航

> **平台愿景**：打造专业的 AI Skills 托管与协作平台，支持 Skills 资产化管理、多领域团队协作、商用授权交易。

## 文档阅读顺序建议

本文档按照推荐的阅读顺序排列，帮助您从宏观到微观逐步了解平台。

---

## 一、概述系列 (入门必读)

### 核心文档
| 文档 | 说明 | 优先级 |
|------|------|--------|
| [01-overview.md](./01-overview.md) | 平台概述与愿景 | P0 |
| [02-architecture.md](./02-architecture.md) | 技术架构设计 | P0 |
| [03-database-overview.md](./03-database-overview.md) | 数据库设计总览 | P0 |
| [04-quickstart.md](./14-quickstart.md) | 快速开始指南 | P0 |

---

## 二、核心功能 (Skills 体系)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [05-skills-system.md](./04-skills-system.md) | Skills 分类体系 | P1 |
| [06-skills-editor.md](./16-skills-editor.md) | Skills 编辑器 | P1 |
| [07-core-modules.md](./03-core-modules.md) | 核心功能模块 | P0 |

---

## 三、协作与交易

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [10-collaboration.md](./06-collaboration.md) | 多领域协作系统 | P1 |
| [11-commerce.md](./07-commerce.md) | 商用授权与交易 | P1 |
| [12-digital-proof.md](./08-digital-proof.md) | 数字存证架构 | P2 |

---

## 四、平台系统 (后端核心)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [15-ai-review.md](./05-ai-review.md) | AI 审核系统 | P1 |
| [16-user-permissions.md](./09-user-permissions.md) | 用户与权限系统 | P1 |
| [17-operations.md](./10-operations.md) | 运营与增长系统 | P2 |
| [18-admin-backend.md](./19-admin-backend.md) | 管理后台系统 | P1 |

---

## 五、用户端模块

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [20-community.md](./18-community.md) | 交流学习社区 | P1 |
| [21-resource-center.md](./17-resource-center.md) | 资源下载中心 | P1 |
| [22-frontend.md](./15-frontend.md) | 前端设计规范 | P0 |

---

## 六、运维与规划

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [25-roadmap.md](./11-roadmap.md) | 开发路线图 | P2 |
| [26-security.md](./12-security.md) | 安全设计 | P0 |
| [27-infrastructure.md](./13-infrastructure.md) | 基础设施与部署 | P0 |
| [28-api-reference.md](./28-api-reference.md) | API 接口文档 | P0 |

---

## 平台核心信息

| 项目 | 内容 |
|------|------|
| 网站域名 | sillymd.com（已完成备案） |
| 服务器地址 | 47.96.133.238 |
| SSH私钥路径 | .ignore/silly.pem |
| 平台定位 | AI Skills 托管中心 + 多领域协作网络 + 商用授权市场 |

## Skills 是什么？

Skills 是智能体与大模型交互的标准化说明文档，按需加载，降低 AI 管理成本。

Skills 不仅限于编程代码，还可以是：
- 产品需求文档 (PRD)
- 设计规范文档 (Design Specs)
- 市场推广方案 (Marketing Plans)
- 运营流程手册 (Operations Guides)
- 用户研究报告 (User Research)

## 核心价值

| 价值 | 说明 |
|------|------|
| **资产化** | 将 Skills 从"文档"升级为"数字资产" |
| **可授权** | 商用 Skills 支持授权交易，资产可流转 |
| **可验证** | 商用 Skills 具有数字签名指纹，确保内容真实 |
| **标准化** | 统一 Skills 格式，跨团队、跨领域协作无障碍 |
| **安全可靠** | 多层安全机制，数据加密存储 |

## 技术栈概览

| 层级 | 技术选型 |
|------|----------|
| 前端 | React 18 + TypeScript + Zustand + Vite |
| UI 框架 | TailwindCSS + shadcn/ui |
| 后端 | Python 3.11+ + FastAPI |
| 数据库 | PostgreSQL 16+ |
| 缓存 | Redis 7.2 Cluster |
| 消息队列 | Kafka |
| 搜索 | Meilisearch |
| 存储 | 阿里云 OSS |

## Skills 分类体系

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills 分类体系                           │
├─────────────────────────────────────────────────────────────┤
│  按收费分类                                                 │
│  ├── 免费Skills (Free Skills)       - 开源共享              │
│  └── 商用Skills (Commercial Skills) - 付费授权              │
│                                                             │
│  按领域分类                                                 │
│  ├── 技术Skills (Tech Skills)       - 代码、架构、工具      │
│  ├── 产品Skills (Product Skills)    - 需求、规划、研究      │
│  ├── 设计Skills (Design Skills)     - UI/UX、视觉、品牌     │
│  ├── 市场Skills (Marketing Skills)  - 推广、策略、分析      │
│  └── 运营Skills (Ops Skills)        - 流程、增长、数据      │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 克隆项目
git clone https://github.com/sillymd/platform.git

# 安装依赖
cd platform && npm install

# 启动开发服务器
npm run dev
```

详细安装说明请参考 [04-quickstart.md](./14-quickstart.md)

## 贡献指南

欢迎贡献 Skills！请查看 [05-skills-system.md](./04-skills-system.md) 了解 Skills 格式规范。

## 许可证

本项目采用 Apache 2.0 许可证。详见 [LICENSE](../LICENSE) 文件。

---

**文档版本**: v15.0 | **最后更新**: 2026-02-03
