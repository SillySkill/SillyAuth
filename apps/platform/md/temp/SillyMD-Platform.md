# SillyMD Skills 在线平台 - 完整设计文档 v11.0

> **平台愿景**：打造专业的 AI Skills 托管与协作平台，支持 Skills 资产化管理、多领域团队协作、商用授权交易。

---

## 目录

1. [平台概述](#一平台概述)
2. [技术架构](#二技术架构)
3. [核心功能模块](#三核心功能模块)
4. [Skills 分类体系](#四skills-分类体系)
5. [AI 审核系统](#五ai-审核系统)
6. [多领域协作系统](#六多领域协作系统)
7. [商用授权与交易系统](#七商用授权与交易系统)
8. [区块链存储架构](#八区块链存储架构)
9. [用户与权限系统](#九用户与权限系统)
10. [开发路线图](#十开发路线图)
11. [安全设计](#十一安全设计)
12. [快速开始](#十二快速开始)

---

## 一、平台概述

### 1.1 基本信息

| 项目 | 内容 |
|------|------|
| 网站域名 | sillymd.com |
| 团队协作域名 | sillymd.com/组织名 |
| 服务器地址 | 47.96.133.238 |
| 平台定位 | AI Skills 托管中心 + 多领域协作网络 + 商用授权市场 |

### 1.2 名字内涵

- **"挺傻的"**：代表对 AI 现状的诚实认知，有时候 "AI，挺傻的"
- **人生态度**：容纳自身不足，持续迭代进化
- **技术理念**：承认 AI 局限，通过 Skills 补全能力边界

### 1.3 核心定义

**Skills 是什么？**

> Skills 是智能体与大模型交互的标准化说明文档，按需加载，降低 AI 管理成本。

**Skills 标准化的扩展：**

Skills 不仅限于编程代码，还可以是：
- 产品需求文档 (PRD)
- 设计规范文档 (Design Specs)
- 市场推广方案 (Marketing Plans)
- 运营流程手册 (Operations Guides)
- 用户研究报告 (User Research)

**所有项目协作都可以按照 Skills 文件标准进行管理。**

### 1.4 核心价值

| 价值 | 说明 |
|------|------|
| **资产化** | 将 Skills 从"文档"升级为"数字资产" |
| **可授权** | 商用 Skills 支持授权交易，资产可流转 |
| **可验证** | 商用 Skills 具有链上哈希指纹，确保内容不被篡改 |
| **标准化** | 统一 Skills 格式，跨团队、跨领域协作无障碍 |
| **安全可靠** | 商用 Skills 区块链存储，数据不可篡改 |

### 1.5 Skills 分类

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills 分类体系                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
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
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、技术架构

### 2.1 技术栈选型

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | React 18 + TypeScript | 单页应用，组件化开发 |
| 后端 | Python + Flask | RESTful API，业务逻辑 |
| 数据库 | MySQL 8.0 | 关系型数据存储 |
| 缓存 | Redis 7.0 | 会话、队列、热点数据 |
| 消息队列 | RabbitMQ | 异步任务处理 |
| AI 审核 | DeepSeek / Claude API | 内容合规性审核 |
| 区块链 | 联盟链 / Hyperledger | 商用 Skills 存储验证 |
| 存储 | 对象存储 (OSS) | Skills 文件存储 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│   │  Web端   │  │  管理后台 │  │  API文档  │  │  SDK工具  │      │
│   └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘      │
├─────────┼──────────────┼──────────────┼──────────────┼──────────┤
│         │              │              │              │          │
│   ┌─────▼──────────────▼──────────────▼──────────────▼──────┐   │
│   │                    API Gateway                          │   │
│   │              (认证 + 限流 + 日志)                        │   │
│   └─────────────────────────────┬───────────────────────────┘   │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│   ┌─────────────────────────────▼───────────────────────────┐   │
│   │                      业务逻辑层 (Flask)                  │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │ 用户服务 │ │ Skills服务│ │ 审核服务 │ │ 交易服务 │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │ 团队服务 │ │ 积分服务 │ │ 授权服务 │ │ 钱包服务 │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   └─────────────────────────────┬───────────────────────────┘   │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│   ┌─────────────────────────────▼───────────────────────────┐   │
│   │                        数据存储层                        │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │  MySQL   │ │  Redis   │ │   OSS    │ │ 区块链   │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 SDK 设计

#### 2.3.1 NPM 包

```bash
# 核心 SDK
npm install @sillymd/sdk

# MCP Server (用于 Claude Code)
npm install @sillymd/mcp-server

# CLI 工具
npm install -g @sillymd/cli
```

#### 2.3.2 SDK 使用示例

```javascript
import { SillyClient } from '@sillymd/sdk';

const client = new SillyClient({
  apiKey: process.env.SILLY_API_KEY,
  endpoint: 'https://api.sillymd.com'
});

// 获取 Skill
const skill = await client.skills.get('skill-id');

// 执行 Skill
const result = await client.skills.execute('skill-id', {
  input: '用户输入',
  context: {}
});

// 列出 Skills
const skills = await client.skills.list({
  category: 'tech',
  type: 'free',
  limit: 10
});
```

### 2.4 数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'vendor', 'admin') DEFAULT 'user',
    ai_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Skills 表
CREATE TABLE skills (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    author_id BIGINT NOT NULL,
    category ENUM('tech', 'product', 'design', 'marketing', 'ops') NOT NULL,
    type ENUM('free', 'commercial') NOT NULL DEFAULT 'free',
    version VARCHAR(20) DEFAULT '1.0.0',
    status ENUM('draft', 'reviewing', 'approved', 'rejected') DEFAULT 'draft',
    content_hash CHAR(64),                    -- SHA-256 哈希
    blockchain_tx_hash VARCHAR(128),          -- 区块链交易哈希（商用）
    price INT DEFAULT 0,                      -- AI Points 价格
    download_count INT DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id),
    INDEX idx_skill_id (skill_id),
    INDEX idx_category (category),
    INDEX idx_type (type),
    INDEX idx_status (status)
);

-- Skills 版本表
CREATE TABLE skill_versions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_id BIGINT NOT NULL,
    version VARCHAR(20) NOT NULL,
    content LONGTEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    commit_message VARCHAR(500),
    author_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (author_id) REFERENCES users(id),
    INDEX idx_skill_id (skill_id),
    UNIQUE KEY uk_skill_version (skill_id, version)
);

-- 团队表
CREATE TABLE teams (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id BIGINT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    INDEX idx_team_slug (team_slug)
);

-- 团队成员表
CREATE TABLE team_members (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role ENUM('owner', 'admin', 'member', 'viewer') DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uk_team_user (team_id, user_id)
);

-- 授权记录表
CREATE TABLE licenses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    license_id VARCHAR(50) UNIQUE NOT NULL,
    skill_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    license_type ENUM('personal', 'team', 'enterprise') NOT NULL,
    price INT NOT NULL,
    expires_at TIMESTAMP NULL,
    blockchain_tx_hash VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (vendor_id) REFERENCES users(id),
    INDEX idx_license_id (license_id),
    INDEX idx_buyer_id (buyer_id)
);

-- 积分交易表
CREATE TABLE point_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    type ENUM('recharge', 'purchase', 'earning', 'refund') NOT NULL,
    balance_after INT NOT NULL,
    related_id BIGINT,                    -- 关联的订单/授权ID
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_type (type)
);

-- 审核记录表
CREATE TABLE reviews (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_id BIGINT NOT NULL,
    reviewer_id BIGINT NOT NULL,
    stage ENUM('L1', 'L2', 'L3') NOT NULL,
    result ENUM('approved', 'rejected', 'revision_required') NOT NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id),
    INDEX idx_skill_id (skill_id)
);
```

---

## 三、核心功能模块

### 3.1 Skills 托管中心

#### 3.1.1 免费 Skills 区域

| 特性 | 说明 |
|------|------|
| 内容类型 | AI 使用技巧、最佳实践、开源工具 |
| 访问权限 | 公开，所有用户可查看下载 |
| 编辑权限 | 作者可编辑，他人可 Fork |
| 许可证 | MIT / Apache 2.0 / CC BY |

#### 3.1.2 商用 Skills 区域

| 特性 | 说明 |
|------|------|
| 内容类型 | 行业解决方案、企业级应用、专业工具 |
| 访问权限 | 需购买授权或订阅 |
| 存储方式 | 区块链存储，确保不可篡改 |
| 授权类型 | 个人授权 / 团队授权 / 企业授权 |

### 3.2 版本管理

| 功能 | 说明 |
|------|------|
| Git 风格版本控制 | 版本历史、分支、回滚 |
| 版本对比 | 可视化展示版本间差异 |
| 版本标签 | 支持为重要版本打标签 |
| 自动备份 | 每次修改自动备份 |

### 3.3 搜索与发现

| 搜索维度 | 说明 |
|----------|------|
| 关键词搜索 | 全文检索 |
| 分类筛选 | 按领域/类型筛选 |
| 标签筛选 | 按自定义标签筛选 |
| 排序方式 | 热度/评分/最新/价格 |

---

## 四、Skills 分类体系

### 4.1 按领域分类

#### 4.1.1 技术 Skills (Tech Skills)

| 子类 | 示例 |
|------|------|
| 开发工具 | 代码生成器、调试工具、性能分析 |
| 架构设计 | 系统架构、微服务、API 设计 |
| 自动化 | CI/CD、脚本、工作流自动化 |
| 数据处理 | ETL、数据清洗、数据可视化 |

#### 4.1.2 产品 Skills (Product Skills)

| 子类 | 示例 |
|------|------|
| 需求管理 | PRD 模板、需求分析框架 |
| 用户研究 | 用户画像、调研方法 |
| 产品规划 | 路线图、OKR、优先级管理 |
| 数据分析 | 埋点方案、漏斗分析 |

#### 4.1.3 设计 Skills (Design Skills)

| 子类 | 示例 |
|------|------|
| UI 设计 | 组件库、设计规范、配色方案 |
| UX 设计 | 交互模式、用户旅程、可用性测试 |
| 品牌设计 | Logo 规范、品牌指南、VI 系统 |

#### 4.1.4 市场 Skills (Marketing Skills)

| 子类 | 示例 |
|------|------|
| 内容营销 | 文案模板、内容规划 |
| 社交媒体 | 运营策略、涨粉技巧 |
| 广告投放 | 投放策略、素材模板 |
| 数据分析 | 获客分析、转化优化 |

#### 4.1.5 运营 Skills (Operations Skills)

| 子类 | 示例 |
|------|------|
| 用户运营 | 用户分层、留存策略 |
| 活动运营 | 活动策划、执行流程 |
| 内容运营 | 内容规划、发布策略 |

### 4.2 按授权类型分类

```
┌─────────────────────────────────────────────────────────────┐
│                    授权类型                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  免费 (Free)                                                │
│  ├── 开源许可 - MIT、Apache、GPL                            │
│  └── CC 许可 - CC BY、CC BY-SA                              │
│                                                             │
│  商用 (Commercial)                                          │
│  ├── 个人授权 - 单用户使用                                  │
│  ├── 团队授权 - 团队内共享 (最多 N 人)                      │
│  └── 企业授权 - 企业内使用 (无人数限制)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 五、AI 审核系统

### 5.1 审核目的

所有上架的 Skills 必须通过 AI 审核，确保：
- **合规性**：符合法律法规，无违法违规内容
- **安全性**：无恶意代码、无病毒木马
- **准确性**：内容真实有效，无虚假宣传
- **格式规范**：符合 Skills 格式标准

### 5.2 审核流程

```
┌─────────────────────────────────────────────────────────────┐
│                      AI 审核流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户提交 Skills                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L1 初审   │  AI 自动审核                               │
│  │  (AI 自动)  │  - 格式检查                                │
│  └──────┬──────┘  - 基础合规检查                            │
│         │          - 重复检测                                │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L2 复审   │  AI 深度审核                               │
│  │ (AI + 人工) │  - 专业准确性                              │
│  └──────┬──────┘  - 商业价值评估                            │
│         │          - 定价合理性                              │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L3 终审   │  平台管理员                                │
│  │  (管理员)   │  - 最终质量把关                            │
│  └──────┬──────┘  - 上架决定                                │
│         │                                                   │
│         ▼                                                   │
│   上架 / 驳回                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 审核维度

| 维度 | 技术 Skills | 产品 Skills | 设计 Skills | 市场/运营 Skills |
|------|-------------|-------------|-------------|------------------|
| 法律合规 | ✅ | ✅ | ✅ | ✅ |
| 内容安全 | ✅ | ✅ | ✅ | ✅ |
| 格式规范 | ✅ | ✅ | ✅ | ✅ |
| 专业准确 | ✅ | ✅ | ✅ | ✅ |
| 商业价值 | ✅ | ✅ | ✅ | ✅ |

### 5.4 审核结果处理

| 结果 | 说明 | 处理方式 |
|------|------|----------|
| **通过** | 符合所有标准 | 自动上架 |
| **需修正** | 存在小问题，可修正 | 返回用户修正后重新提交 |
| **驳回** | 存在重大问题 | 拒绝上架，说明原因 |

---

## 六、多领域协作系统

### 6.1 协作理念

**核心理念**：将 Skills 标准化扩展到所有工作领域。

传统的项目协作各自为政：
- 技术团队用 Git
- 产品团队用文档系统
- 设计团队用设计工具
- 市场团队用营销系统

**SillyMD 的解决方案**：所有团队都用 Skills 标准来管理和协作。

### 6.2 团队组织结构

```
团队域名结构：sillymd.com/{team_slug}

示例：
├── sillymd.com/acme-tech          → ACME 科技公司
├── sillymd.com/design-studio      → 某设计工作室
├── sillymd.com/marketing-agency   → 某营销公司
└── sillymd.com/startup-abc        → 某创业团队
```

### 6.3 团队角色

| 角色 | 权限 | 说明 |
|------|------|------|
| **Owner** | 完全控制 | 团队创建者，可解散团队 |
| **Admin** | 管理 | 管理成员、设置、项目 |
| **Member** | 编辑 | 创建/编辑 Skills，参与项目 |
| **Viewer** | 查看 | 只读访问团队内容 |

### 6.4 项目协作模式

```
┌─────────────────────────────────────────────────────────────┐
│                    项目协作模式                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  项目启动                                                   │
│    ├── 产品经理创建 "产品需求 Skill"                        │
│    ├── 设计师基于需求创建 "设计规范 Skill"                  │
│    ├── 开发者基于规范创建 "技术实现 Skill"                  │
│    └── 运营创建 "推广方案 Skill"                            │
│                                                             │
│  项目迭代                                                   │
│    ├── 每个 Skill 独立版本控制                              │
│    ├── Skill 之间可以引用关联                               │
│    ├── 变更通知相关成员                                     │
│    └── 形成完整的知识沉淀                                   │
│                                                             │
│  项目交付                                                   │
│    ├── 所有 Skills 形成项目资产                             │
│    ├── 可导出为完整项目文档                                 │
│    └── 可复用至新项目                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.5 Skills 引用系统

Skills 可以相互引用，形成知识网络：

```yaml
# 产品需求 Skill
skill:
  id: "prd-user-auth"
  name: "用户认证需求"
  depends_on:
    - skill_id: "design-auth-ui"
      type: "design"
    - skill_id: "impl-auth-api"
      type: "tech"
```

---

## 七、商用授权与交易系统

### 7.1 AI 积分体系

**AI Points (AI 积分)** 是平台内的虚拟积分单位。

| 获取方式 | 说明 |
|----------|------|
| 充值购买 | 支持支付宝、微信、银行卡 |
| 销售收益 | 出售商用 Skills 获得 |
| 活动奖励 | 平台活动、推广奖励 |
| 贡献奖励 | 贡献优质免费 Skills |

### 7.2 商用 Skills 定价

| Skills 类型 | 建议价格区间 | 说明 |
|-------------|--------------|------|
| 基础工具类 | 100-500 AI Points | 通用脚本、模板 |
| 专业应用类 | 500-2000 AI Points | 行业解决方案 |
| 企业级方案 | 2000-10000 AI Points | 完整系统、复杂集成 |
| 独家定制类 | 10000+ AI Points | 高度定制化 |

### 7.3 授权类型与价格

| 授权类型 | 价格倍数 | 使用范围 |
|----------|----------|----------|
| **个人授权** | 1x | 单用户使用 |
| **团队授权** | 3x | 团队内共享 (最多 10 人) |
| **企业授权** | 10x | 企业内使用 (无人数限制) |

### 7.4 交易流程

```
┌─────────────────────────────────────────────────────────────┐
│                    交易流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  买家                                                      │
│    │                                                       │
│    ├── 浏览商用 Skills                                     │
│    ├── 选择授权类型 (个人/团队/企业)                        │
│    ├── 确认订单，扣除 AI Points                            │
│    └── 获得授权许可，可访问 Skills 内容                    │
│                                                             │
│  平台                                                      │
│    │                                                       │
│    ├── 记录交易                                            │
│    ├── 平台抽成 (15%)                                      │
│    └── 供应商到账 (85%)                                    │
│                                                             │
│  供应商                                                    │
│    │                                                       │
│    ├── 查看销售数据                                        │
│    ├── AI Points 余额增加                                  │
│    └── 可申请提现                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.5 平台抽成规则

| 供应商等级 | 销售额 | 平台抽成 | 供应商收益 |
|------------|--------|----------|------------|
| 普通供应商 | - | 20% | 80% |
| 优质供应商 | ≥ 5,000 Points | 15% | 85% |
| 金牌供应商 | ≥ 50,000 Points | 10% | 90% |

### 7.6 提现规则

| 规则项 | 说明 |
|--------|------|
| 最低提现 | 500 AI Points |
| 提现周期 | 每周一处理 |
| 提现方式 | 支付宝、银行转账 |
| 汇率 | 100 AI Points = 10 元人民币 |

---

## 八、区块链存储架构

### 8.1 为什么商用 Skills 需要区块链

| 需求 | 传统存储 | 区块链存储 |
|------|----------|------------|
| 数据完整性 | 中心化可篡改 | 不可篡改 |
| 版权证明 | 需第三方公证 | 链上哈希即证明 |
| 授权记录 | 可被伪造 | 链上可追溯 |
| 数据安全 | 依赖服务商安全 | 分布式高可用 |

### 8.2 区块链架构

```
┌─────────────────────────────────────────────────────────────┐
│                商用 Skills 区块链存储架构                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  上链数据                                                   │
│  ├── Skill ID (唯一标识)                                   │
│  ├── Content Hash (SHA-256 内容哈希)                       │
│  ├── Author (创作者钱包地址)                               │
│  ├── Creation Time (创建时间戳)                            │
│  └── Metadata (元数据)                                     │
│                                                             │
│  链下存储                                                   │
│  └── Skills 完整内容存储于 OSS，哈希上链验证                │
│                                                             │
│  验证流程                                                   │
│  1. 下载 Skills 内容                                       │
│  2. 计算本地 SHA-256 哈希                                  │
│  3. 对比链上哈希值                                        │
│  4. 一致则内容未被篡改                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 链上数据结构

```json
{
  "skill_id": "skill_com_abc123",
  "content_hash": "0x3a7b8c9d1e2f...4b5m6n",
  "author": "ACME_Technologies",
  "name": "Enterprise Payment Gateway Solution",
  "version": "2.1.0",
  "category": "tech",
  "created_at": 1737657600,
  "block_number": 12345678,
  "transaction_hash": "0x9f8e7d6c5b4a...3210"
}
```

### 8.4 上链策略

| Skills 类型 | 是否上链 | 原因 |
|-------------|----------|------|
| 免费 Skills | ❌ | 开源共享，无需版权证明 |
| 商用 Skills | ✅ | 需要版权保护和防篡改 |
| 企业私有 Skills | ✅ | 需要高安全性 |

### 8.5 区块链选型考虑

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 联盟链 | 高性能、易合规 | 需联盟维护 | 企业级商用 |
| 许可链 | 可控、安全 | 去中心化程度低 | 平台初期 |
| 公链 | 去中心化 | 性能低、成本高 | 未来扩展 |

---

## 九、用户与权限系统

### 9.1 用户类型

| 用户类型 | 权限 | 升级条件 |
|----------|------|----------|
| **普通用户** | 浏览、下载免费 Skills | 注册即可 |
| **供应商** | 创建商用 Skills、设置价格 | 实名认证 + 审核 |
| **团队管理员** | 创建团队、管理成员 | 创建团队 |
| **平台管理员** | 全局管理权限 | 平台任命 |

### 9.2 登录方式

| 方式 | 说明 |
|------|------|
| 邮箱注册 | 基础方式 |
| 手机号 | 国内用户 |
| GitHub OAuth | 开发者友好 |
| 企业微信 | 企业用户 |

### 9.3 权限矩阵

| 操作 | 访客 | 普通用户 | 供应商 | 管理员 |
|------|------|----------|--------|--------|
| 浏览免费 Skills | ✅ | ✅ | ✅ | ✅ |
| 下载免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建商用 Skills | ❌ | ❌ | ✅ | ✅ |
| 审核 Skills | ❌ | ❌ | ❌ | ✅ |
| 管理用户 | ❌ | ❌ | ❌ | ✅ |

---

## 十、开发路线图

### Phase 1: MVP 基础版 (0-3个月)

**目标：验证核心价值**

- [x] 用户注册/登录
- [x] Skills CRUD 基础功能
- [x] 简单版本控制
- [x] 基础权限管理
- [ ] AI 积分系统
- [ ] Skills 浏览与搜索

### Phase 2: 协作功能 (3-6个月)

**目标：支持团队协作**

- [ ] 团队创建与管理
- [ ] 团队成员管理
- [ ] Skills 共享与协作
- [ ] 权限细分控制
- [ ] 评论与反馈系统

### Phase 3: AI 审核 (6-9个月)

**目标：自动化审核流程**

- [ ] L1 AI 自动审核
- [ ] L2 AI+人工复审
- [ ] L3 管理员终审
- [ ] 审核工作流引擎
- [ ] 审核反馈机制

### Phase 4: 商用交易 (9-12个月)

**目标：商业化功能**

- [ ] 商用 Skills 创建
- [ ] AI Points 充值系统
- [ ] 订单与支付
- [ ] 授权管理系统
- [ ] 供应商工作台

### Phase 5: 区块链存储 (12-15个月)

**目标：商用 Skills 安全存储**

- [ ] 区块链节点部署
- [ ] Skills 哈希上链
- [ ] 链上数据验证
- [ ] 授权记录上链
- [ ] 版权证明生成

### Phase 6: 多领域扩展 (15-18个月)

**目标：支持全领域协作**

- [ ] 产品 Skills 模板
- [ ] 设计 Skills 模板
- [ ] 市场 Skills 模板
- [ ] 运营 Skills 模板
- [ ] 跨领域引用系统

### Phase 7: 生态完善 (18个月+)

**目标：构建生态**

- [ ] SDK 与 API 完善
- [ ] 开发者社区
- [ ] 移动端 APP
- [ ] 国际化支持

---

## 十一、安全设计

### 11.1 数据安全

| 措施 | 说明 |
|------|------|
| 传输加密 | HTTPS/TLS 1.3 |
| 存储加密 | 敏感数据 AES-256 加密 |
| 密码安全 | bcrypt 哈希 + 盐值 |
| SQL 防护 | 参数化查询，防止注入 |

### 11.2 访问控制

| 措施 | 说明 |
|------|------|
| 会话管理 | JWT Token，自动续期 |
| 限流保护 | API 限流，防止滥用 |
| IP 白名单 | 企业用户可选 |
| 操作审计 | 关键操作日志记录 |

### 11.3 内容安全

| 措施 | 说明 |
|------|------|
| AI 审核 | 上架前审核 |
| 人工复核 | 争议内容人工审核 |
| 用户举报 | 违规内容举报机制 |
| 定期巡查 | 定期检查存量内容 |

### 11.4 交易安全

| 措施 | 说明 |
|------|------|
| 积分锁 | 交易中锁定积分 |
| 交易记录 | 完整交易日志 |
| 退款机制 | 争议可退款 |
| 区块链存证 | 商用授权链上记录 |

---

## 十二、快速开始

### 12.1 安装部署

```bash
# 1. 克隆项目
git clone https://github.com/sillymd/platform.git
cd platform

# 2. 后端环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置

# 4. 初始化数据库
flask db upgrade

# 5. 启动后端服务
flask run

# 6. 前端环境
cd frontend
npm install
npm run dev

# 7. 访问平台
open http://localhost:3000
```

### 12.2 SDK 使用

```bash
# 安装 SDK
npm install @sillymd/sdk

# 在代码中使用
import { SillyClient } from '@sillymd/sdk';

const client = new SillyClient({
  apiKey: 'your-api-key',
  endpoint: 'https://api.sillymd.com'
});
```

### 12.3 快速链接

| 链接 | 地址 |
|------|------|
| 官网 | https://sillymd.com |
| 文档 | https://docs.sillymd.com |
| API | https://api.sillymd.com |
| 社区 | https://community.sillymd.com |

---

## 附录：Skills 示例

### 示例 A: 技术 Skill - Python 数据分析模板

```yaml
skill:
  id: "tech-python-data-analysis"
  name: "Python 数据分析模板"
  version: "1.0.0"
  category: "tech"
  type: "free"
  author: "SillyMD Team"
  description: "标准化的 Python 数据分析项目模板"
  tags: ["python", "data", "analysis"]

setup:
  requirements:
    - python>=3.8
    - pandas>=1.3.0
    - numpy>=1.21.0
    - matplotlib>=3.4.0

structure:
  - data/           # 数据目录
  - notebooks/      # Jupyter 笔记本
  - src/            # 源代码
  - tests/          # 测试
  - README.md       # 说明文档
```

### 示例 B: 产品 Skill - PRD 模板

```yaml
skill:
  id: "prod-prd-template"
  name: "产品需求文档 (PRD) 模板"
  version: "2.0.0"
  category: "product"
  type: "free"
  author: "SillyMD Product Team"
  description: "标准化的产品需求文档模板"
  tags: ["prd", "product", "template"]

sections:
  - 背景与目标
  - 用户分析
  - 需求列表
  - 功能规格
  - 交互设计
  - 数据指标
  - 发布计划
```

### 示例 C: 商用 Skill - 企业支付网关

```yaml
skill:
  id: "com-payment-gateway"
  name: "企业支付网关解决方案"
  version: "2.1.0"
  category: "tech"
  type: "commercial"
  author: "ACME Technologies"
  description: "完整的企业级支付网关集成方案"
  tags: ["payment", "enterprise", "integration"]
  price: 5000
  license_types: ["team", "enterprise"]

features:
  - 支持多支付渠道
  - 完整的对账系统
  - 高可用架构
  - 安全合规

blockchain:
  content_hash: "0x3a7b8c9d1e2f...4b5m6n"
  transaction_hash: "0x9f8e7d6c5b4a...3210"
  verified: true
```

---

**文档版本**: v11.0
**最后更新**: 2026-02-01
**维护团队**: SillyMD Team

---

*"承认自己有时候挺傻的，这是智慧的开始。"*
