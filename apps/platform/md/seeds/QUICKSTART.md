# SillyMD 种子数据 - 快速上手指南

## 目标

在 SillyMD 平台启动时，自动生成：
1. **50-200 个模拟内部账号** (供应商 + 普通用户)
2. **100-500 个模拟 Skills** (通过爬虫/随机生成)
3. **模拟用户上传行为** (随机账号发布随机 Skills)

## 5分钟快速开始

### 步骤1：进入 seeds 目录

```bash
cd seeds
```

### 步骤2：安装依赖 (仅需一次)

```bash
npm install
```

### 步骤3：生成种子数据

```bash
# 小规模测试 (20用户 + 50 Skills)
npm run generate:small

# 中等规模 (50用户 + 200 Skills) - 推荐
npm run generate:medium

# 大规模 (100用户 + 500 Skills)
npm run generate:large
```

生成后的文件在 `seeds/output/` 目录：
- `mock-users.json` - 模拟用户数据
- `mock-skills.json` - 模拟 Skills 数据
- `demo-data.json` - 前端演示数据 (已裁剪)

### 步骤4：启动后端并导入

```bash
# 1. 确保后端 API 运行中
cd ../src
python main.py

# 2. 获取 admin token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sillymd.com","password":"admin123456"}'

# 3. 导入种子数据
curl -X POST http://localhost:8000/api/v1/admin/seeds/import \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d @../seeds/output/mock-skills.json
```

### 步骤5：查看演示

1. 打开浏览器
2. 访问 `examples/demo-seed.html`
3. 即可看到生成的模拟数据展示

## 生成的数据内容

### 模拟用户账号分布

| 类型 | 占比 | 说明 |
|------|------|------|
| 普通用户 | 20% | 只能购买，不能发布 |
| 普通供应商 | 35% | 可发布 Skills |
| 优质供应商 | 30% | 销售额达标 |
| 金牌供应商 | 15% | 头部创作者 |

### Skills 数据分布

| 维度 | 分布 |
|------|------|
| 行业 | 8大行业随机 (金融/电商/教育/医疗/制造/旅游/娱乐/餐饮) |
| 场景 | 7大场景随机 (数据分析/自动化/客服/营销/开发/管理/内容) |
| 类型 | 代码/设计/产品/营销/内容/运营 |
| 定价 | 30%免费 + 70%付费 (100-15000 AP) |
| 评分 | 3.5-5.0 随机分布 |

### 字段示例

**用户数据**:
```json
{
  "id": "user_001",
  "username": "dev_master",
  "displayName": "开发大师",
  "avatar": "https://api.dicebear.com/...",
  "bio": "专注金融领域8年，服务过300+企业客户",
  "role": "vendor",
  "vendorLevel": "premium",
  "joinDate": "2025-08-15",
  "stats": {
    "totalSkills": 12,
    "totalSales": 15800,
    "rating": 4.8
  }
}
```

**Skills 数据**:
```json
{
  "id": "skill_001",
  "name": "AI 数据分析大师 Pro",
  "description": "专业级数据分析工具，支持AI智能建议、一键导出报告...",
  "authorId": "user_001",
  "authorName": "开发大师",
  "authorAvatar": "https://api.dicebear.com/...",
  "authorLevel": "premium",
  "type": "code",
  "industry": "金融",
  "industryIcon": "🟣",
  "scenario": "数据分析",
  "scenarioIcon": "📊",
  "pricing": { "type": "onetime", "price": 2999 },
  "rating": 4.7,
  "downloads": 1234,
  "tags": ["AI", "数据分析", "Python"],
  "icon": "fa-chart-line",
  "status": "approved"
}
```

## 前端展示

### demo-seed.html 功能

- 动态渲染 Skills 卡片
- 行业/场景/价格/评分筛选
- 分页展示
- 排序 (综合/最新/下载量/价格)
- 统计数据展示
- 用户头像/徽章显示

### 集成到主站

将生成的数据集成到示例页面:

```javascript
// 1. 复制数据到 examples 目录
copy seeds\output\demo-data.json examples\js\

// 2. 在 skills.html 中引入
<script src="js/demo-data.json"></script>
<script src="../seeds/demo-loader.js"></script>
<script>
  SillyMDDemo.init();
</script>
```

## 自定义配置

### 修改生成参数

编辑 `seed-generator.js` 中的 CONFIG:

```javascript
const CONFIG = {
  // 修改行业
  industries: [
    { name: '金融', icon: '🟣', color: '#FFD700' },
    { name: '电商', icon: '🟢', color: '#4CAF50' },
    // ... 添加更多行业
  ],

  // 修改供应商分布
  vendorDistribution: {
    user: 0.1,      // 10% 普通用户
    normal: 0.4,    // 40% 普通供应商
    premium: 0.35,  // 35% 优质供应商
    gold: 0.15      // 15% 金牌供应商
  }
};
```

### 命令行参数

```bash
# 自定义数量
node seed-generator.js --users 100 --skills 300

# 指定随机种子 (保证可重复)
node seed-generator.js --seed 12345

# 指定输出目录
node seed-generator.js --output ./my-data
```

## 爬虫数据 (进阶)

系统支持从真实数据源爬取 Skills:

```bash
# 启用爬虫模式
node seed-generator.js --crawl --users 50 --skills 200
```

支持的数据源:
- GitHub (代码仓库、README)
- CSDN (技术博客)
- 掘金 (技术文章)

爬虫配置在 `crawler.js` 中。

## 数据库导入 (PostgreSQL)

种子数据通过后端 API 导入到 PostgreSQL:

```bash
# 通过 API 批量导入 (推荐)
curl -X POST http://localhost:8000/api/v1/admin/seeds/import \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d @output/mock-skills.json
```

## 清理模拟数据

如需清空所有模拟数据:

```bash
# 通过 API 清理
curl -X POST http://localhost:8000/api/v1/admin/seeds/clear \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

这会删除所有 `is_mock = TRUE` 的记录。

## 数据规模建议

| 阶段 | 用户数 | Skills数 | 说明 |
|------|--------|----------|------|
| 本地开发 | 20 | 50 | 快速测试 |
| 内测 | 50 | 200 | 功能验证 |
| 公测 | 100 | 500 | 压力测试 |
| 正式运营 | 500+ | 2000+ | 真实感 |

## 常见问题

### Q: 生成的数据可以重复使用吗？
A: 可以！使用 `--seed` 参数指定随机种子，相同种子会生成相同数据。

### Q: 如何修改 Skills 名称风格？
A: 编辑 `seed-generator.js` 中的 `DICTIONARY.skillCores` 数组。

### Q: 头像加载慢怎么办？
A: 演示使用的是 DiceBear API。生产环境建议：
1. 下载头像到本地
2. 使用本地占位图
3. 使用首字母头像

### Q: 可以导入到其他数据库吗？
A: 可以。`mock-users.json` 和 `mock-skills.json` 是标准 JSON 格式，可导入任何数据库。

## 需要帮助？

查看详细文档：`seeds/README.md`

---

**最后更新**: 2026-04-30
