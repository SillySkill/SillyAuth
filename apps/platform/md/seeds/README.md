# SillyMD 种子数据生成系统

## 概述

这个系统用于 SillyMD 平台启动时自动生成：
1. **爬虫数据** - 从多数据源爬取 Skills
2. **模拟账号** - 随机生成指定数量的内部账号
3. **模拟上传** - 用这些账号随机上传爬取的 Skills

## 文件说明

| 文件 | 用途 |
|------|------|
| `crawler.js` | 通用爬虫 (GitHub/CSDN/掘金等) |
| `seed-generator.js` | 种子数据生成器 (账号 + Skills) |
| `demo-loader.js` | 前端演示加载器 |
| `output/mock-users.json` | 生成的模拟用户数据 |
| `output/mock-skills.json` | 生成的模拟 Skills 数据 |
| `output/demo-data.json` | 前端演示数据 (已裁剪) |

## 快速开始

### 1. 安装依赖

```bash
cd seeds
npm install
```

### 2. 生成模拟数据

```bash
# 生成 50 个模拟账号 + 200 个随机 Skills
node seed-generator.js --users 50 --skills 200

# 完整模式：先爬取真实数据，再生成模拟账号关联
node seed-generator.js --crawl --users 50 --skills 200
```

### 3. 导入到数据库 (PostgreSQL)

种子数据通过后端 API 导入 PostgreSQL:

```bash
# 通过 SillyMD API 批量导入
curl -X POST http://localhost:8000/api/v1/admin/seeds/import \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d @output/mock-skills.json
```

### 4. 前端演示

打开 `examples/demo-seed.html` 查看生成的模拟数据展示。

## 数据生成策略

### 模拟账号结构

```javascript
{
  id: "user_001",
  username: "dev_master",           // 随机用户名
  displayName: "开发大师",          // 随机显示名
  avatar: "https://...",            // 随机头像
  bio: "10年全栈开发经验...",        // 随机简介
  role: "vendor",                   // 角色：vendor/supplier/gold
  vendorLevel: "premium",           // 供应商等级
  joinDate: "2026-01-15",           // 随机加入日期
  stats: {
    totalSkills: 12,
    totalSales: 15800,
    rating: 4.8
  }
}
```

### Skills 数据结构

```javascript
{
  id: "skill_001",
  name: "Python 数据分析大师",
  description: "...",
  authorId: "user_001",             // 关联模拟账号
  type: "code",                     // code/design/product/marketing
  industry: "电商",                  // 8大行业
  scenario: "数据分析",              // 7大场景
  pricing: {
    type: "onetime",                // onetime/subscription/free
    price: 2999
  },
  rating: 4.7,
  downloads: 1234,
  tags: ["python", "pandas", "数据分析"],
  createdAt: "2026-01-20",
  status: "approved"
}
```

## 爬虫配置

### 支持的数据源

| 平台 | 内容类型 | 状态 |
|------|----------|------|
| GitHub | 代码仓库/README | 支持 |
| CSDN | 技术博客 | 支持 |
| 掘金 | 技术文章 | 支持 |
| Medium | 英文技术文章 | 支持 |
| 知乎 | 技术回答 | 待开发 |

### 爬虫使用

```javascript
const { UniversalCrawler } = require('./crawler');

const crawler = new UniversalCrawler({
  sources: ['github', 'csdn', 'juejin'],
  keywords: ['AI', '自动化', 'Python', '数据分析'],
  maxResults: 100
});

const skills = await crawler.crawl();
```

## 模拟账号类型分布

生成账号时按以下比例分配：

| 类型 | 比例 | 说明 |
|------|------|------|
| 普通供应商 | 60% | 基础供应商权限 |
| 优质供应商 | 30% | 销售额达标 |
| 金牌供应商 | 10% | 头部创作者 |
| 普通用户 | 20% | 仅购买权限 |

## 随机内容生成规则

### Skills 名称生成

```javascript
// 组合方式：[领域] + [功能] + [Pro/大师/AI/工具]
[
  "Python 数据分析大师",
  "AI 交易机器人 Pro",
  "自动化测试工具",
  "React 组件库设计",
  "用户增长策略指南"
]
```

### 描述生成

```javascript
// 模板：[功能介绍] + [适用场景] + [核心特性]
// 示例：
"专业级[Python数据分析]工具，支持[数据清洗/可视化/建模]，
 适用于[电商运营/金融分析/科研统计]场景，
 内置[50+种分析模板/AI智能建议/一键导出报告]功能。"
```

## 配置选项

### seed-generator.js 参数

```bash
Options:
  --users <number>      生成账号数量 (默认: 50)
  --skills <number>     生成 Skills 数量 (默认: 200)
  --crawl               启用爬虫获取真实数据
  --industries <list>   指定行业 (默认: 全部8个)
  --scenarios <list>    指定场景 (默认: 全部7个)
  --output <path>       输出目录 (默认: ./output)
  --seed <number>       随机种子 (保证可重复)
```

## 数据库导入

种子数据导入到 SillyMD 的 PostgreSQL 数据库。通过后端 API 而非直接 SQL 导入，确保数据经过业务逻辑校验。

### PostgreSQL 表结构 (参考)

```sql
-- 用户表
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  avatar_url VARCHAR(500),
  bio TEXT,
  role VARCHAR(20) DEFAULT 'user',
  vendor_level VARCHAR(20) DEFAULT 'none',
  is_mock BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills 表
CREATE TABLE skills (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  slug VARCHAR(200) UNIQUE NOT NULL,
  description TEXT,
  author_id INTEGER NOT NULL REFERENCES users(id),
  type VARCHAR(50),
  industry VARCHAR(50),
  scenario VARCHAR(50),
  pricing_type VARCHAR(20) DEFAULT 'free',
  price INTEGER DEFAULT 0,
  rating DECIMAL(2,1) DEFAULT 5.0,
  downloads INTEGER DEFAULT 0,
  tags JSONB,
  status VARCHAR(20) DEFAULT 'approved',
  is_mock BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 前端演示

### demo-seed.html 功能

1. **随机展示** - 每次刷新显示不同的模拟 Skills
2. **用户卡片** - 展示模拟供应商信息
3. **筛选测试** - 测试按行业/场景/价格筛选
4. **搜索测试** - 测试搜索功能

## 生产环境注意事项

1. **标记模拟数据** - 所有生成数据带有 `is_mock = TRUE` 标记
2. **可清空** - 提供一键清空模拟数据的 API
3. **不影响真实用户** - 模拟账号使用特殊 ID 前缀
4. **数据隔离** - 建议使用独立的种子数据标记字段

## 数据量建议

| 平台阶段 | 建议账号数 | 建议 Skills 数 |
|----------|-----------|---------------|
| 内测期 | 20-50 | 100-300 |
| 公测期 | 100-200 | 500-1000 |
| 正式运营 | 500+ | 2000+ |

## 调试

```bash
# 查看生成的数据
node seed-generator.js --users 10 --skills 20 --output ./debug

# 验证数据完整性
node validate.js

# 通过 API 清空模拟数据
curl -X POST http://localhost:8000/api/v1/admin/seeds/clear \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

**最后更新**: 2026-04-30
