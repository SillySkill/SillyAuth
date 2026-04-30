# 数据库设计核查报告

> 生成时间: 2026-02-03
> 核查范围: skills 目录下所有包含数据库设计的文档

## 一、发现的问题总结

### 🔴 严重问题（需要立即修复）

#### 1. admin_users 表重复定义且结构不一致

| 位置 | 设计方案 | 问题 |
|------|----------|------|
| 02-architecture.md:178 | 基于 `user_id` 外键关联 | 管理员也是普通用户 |
| 19-admin-backend.md:93 | 独立的 `username/email/password` | 管理员单独的登录系统 |

**字段差异对比**:

| 字段 | 02-architecture.md | 19-admin-backend.md | 建议 |
|------|-------------------|---------------------|------|
| id | ✓ | ✓ | 保留 |
| user_id | ✓ | ✗ | 删除（采用独立登录） |
| username | ✗ | ✓ | 保留 |
| email | ✗ | ✓ | 保留 |
| password_hash | ✗ | ✓ | 保留 |
| role | ✓ | ✓ | 保留 |
| department | ✓ | ✗ | 可选保留 |
| permissions | ✓ | ✓ | 保留 |
| last_login_at | ✓ | ✓ | 保留 |
| last_login_ip | ✗ | ✓ | 保留 |

**建议方案**: 采用 19-admin-backend.md 的设计（独立登录系统），删除 02-architecture.md 中的定义。

---

#### 2. withdrawals 相关表重复定义

| 文档 | 表名 | 用途 |
|------|------|------|
| 07-commerce.md:109 | `withdrawals` | 用户提现记录 |
| 19-admin-backend.md:457 | `withdrawal_requests` | 提现申请管理 |

**字段对比**:

| 字段 | withdrawals | withdrawal_requests | 建议 |
|------|-------------|---------------------|------|
| id | ✓ | ✓ | 统一 |
| withdrawal_no | ✓ | ✗ | 保留 |
| user_id | ✓ | ✓ | 统一 |
| amount | ✓ | ✓ | 统一 |
| fee | ✓ | ✓ | 统一 |
| actual_amount | ✓ | ✓ | 统一 |
| method | ✓ | ✓ | 统一 |
| account_info | ✓ (JSONB) | ✓ (JSONB) | 统一 |
| status | ✓ | ✓ | 统一 |
| transaction_id | ✓ | ✓ | 统一 |
| rejection_reason | ✓ | ✓ | 统一 |
| processed_by | ✓ | ✓ | 统一 |
| processed_at | ✓ | ✓ | 统一 |

**建议方案**: 合并为一个表 `withdrawal_requests`，保留所有字段。

---

#### 3. review_queue 表重复定义

| 文档 | 表名 | 用途 |
|------|------|------|
| 05-ai-review.md:32 | `review_queues` | AI 审核队列 |
| 19-admin-backend.md:206 | `review_queue` | 审核队列管理 |

**字段对比**:

| 字段 | review_queues | review_queue | 差异 |
|------|---------------|--------------|------|
| id | ✓ | ✓ | - |
| skill_id | ✓ | ✓ | - |
| submitter_id | ✓ (user) | ✓ (user) | - |
| reviewer_id | ✓ (admin) | ✓ (admin) | - |
| stage | ✓ (enum) | ✗ | 05版更详细 |
| status | ✓ (enum) | ✓ (enum) | enum值略有差异 |
| priority | ✓ (enum) | ✓ (enum) | - |
| ai_model_version | ✓ | ✗ | 保留 |
| ai_confidence | ✓ | ✓ (类型不同) | 统一为 NUMERIC |
| ai_scores | ✓ (JSONB) | ✓ (JSONB) | - |
| submitted_at | ✓ | ✓ | - |
| source | ✗ | ✓ | 可选保留 |
| manual_review_note | ✓ | ✗ | 保留 |
| reject_reason | ✓ | ✓ | - |
| reviewed_by | ✗ | ✓ | 与 reviewer_id 重复 |

**建议方案**: 采用 `review_queues`（05-ai-review.md），补充 `source` 字段。

---

### 🟡 中等问题（建议优化）

#### 4. 枚举类型重复定义

以下枚举在多个文档中重复定义：

| 枚举类型 | 出现位置 | 建议 |
|----------|----------|------|
| `file_category` | 16-skills-editor.md, 17-resource-center.md, 19-admin-backend.md | 统一定义 |
| `storage_type` | 16-skills-editor.md, 19-admin-backend.md | 统一定义 |
| `notification_type` | 02-architecture.md, 19-admin-backend.md | 合并或区分用途 |
| `review_status/priority` | 05-ai-review.md, 19-admin-backend.md | 统一命名 |

**建议**: 在 03-database-overview.md 中添加"全局枚举定义"章节。

---

#### 5. 外键引用不一致

**问题案例**:

```sql
-- 06-collaboration.md
FOREIGN KEY (created_by) REFERENCES admin_users(id)

-- 但 admin_users 在两个地方定义，结构不同
```

**影响**: 如果采用 19-admin-backend.md 的 admin_users 设计，02-architecture.md 中的 `user_id` 外键将失效。

---

#### 6. 缺少必要的索引

部分表缺少复合索引，影响查询性能：

| 表名 | 缺少索引 | 影响 |
|------|----------|------|
| skills | (category, is_commercial, status) | 分类筛选性能 |
| point_transactions | (user_id, created_at) | 用户交易历史查询 |
| team_members | (team_id, role) | 团队成员管理 |

---

### 🟢 轻微问题（可选优化）

#### 7. 字段命名不一致

| 概念 | 不同命名 | 建议 |
|------|----------|------|
| 撤销/删除时间 | `deleted_at`, `closed_at` | 统一为 `deleted_at` |
| 用户标识 | `user_id`, `submitter_id`, `author_id` | 根据语境使用 |
| 内容哈希 | `content_hash`, `hash` | 统一为 `content_hash` |

---

#### 8. COMMENT 注释不完整

- 02-architecture.md: 完全缺少 COMMENT
- 05-ai-review.md: 有 COMMENT
- 19-admin-backend.md: 有 COMMENT
- 其他文档: 部分有 COMMENT

**建议**: 统一添加 COMMENT 注释。

---

## 二、各文档数据库设计评估

### ✅ 设计完善的文档

| 文档 | 表数量 | 评分 | 说明 |
|------|--------|------|------|
| 02-architecture.md | 20 | 85分 | 核心表设计完整，但部分表与其他文档重复 |
| 05-ai-review.md | 6 | 90分 | AI审核流程完整，枚举定义清晰 |
| 06-collaboration.md | 6 | 88分 | 协作功能设计合理 |
| 07-commerce.md | 7 | 85分 | 交易流程完整，但与其他表有重复 |
| 08-digital-proof.md | 5 | 92分 | 数字存证设计完善 |
| 09-user-permissions.md | 10 | 95分 | 权限系统设计非常完善 |
| 10-operations.md | 9 | 90分 | 运营功能设计完整 |
| 16-skills-editor.md | 7 | 88分 | 编辑器功能设计完整 |
| 17-resource-center.md | 7 | 90分 | 资源管理设计完整 |
| 18-community.md | 15 | 85分 | 社区功能多，设计基本完整 |
| 19-admin-backend.md | 19 | 88分 | 管理后台功能完整，但与核心文档有重复 |

---

## 三、修复建议优先级

### P0 - 立即修复（影响系统一致性）

1. **删除 02-architecture.md 中的 admin_users 表定义**
   - 采用 19-admin-backend.md 的独立登录设计
   - 更新所有引用该表的外键

2. **合并 withdrawals 相关表**
   - 统一使用 `withdrawal_requests`
   - 更新 07-commerce.md 和 19-admin-backend.md

3. **统一 review_queue 表定义**
   - 采用 05-ai-review.md 的 `review_queues`
   - 补充缺失的 `source` 字段

### P1 - 高优先级（影响代码质量）

4. **统一枚举类型定义**
   - 在 03-database-overview.md 添加全局枚举章节
   - 删除各文档中的重复定义

5. **补充缺失索引**
   - 为高频查询添加复合索引

6. **统一 COMMENT 注释**
   - 为所有表和字段添加 COMMENT

### P2 - 中优先级（优化建议）

7. **字段命名规范化**
   - 制定命名规范文档
   - 逐步统一字段命名

8. **外键关系梳理**
   - 绘制完整的 ER 图
   - 检查所有外键引用的正确性

---

## 四、推荐修复方案

### 方案 A: 最小改动（推荐）

只修复 P0 问题，其他保持不变：

1. 删除 02-architecture.md 中的 `admin_users` 定义
2. 将 07-commerce.md 的 `withdrawals` 改为引用 `withdrawal_requests`
3. 统一使用 `review_queues` 表名

### 方案 B: 完整重构（理想方案）

按优先级修复所有问题，需要较大工作量：

1. 创建全局枚举定义文档
2. 统一所有重复表定义
3. 补充所有索引和注释
4. 生成完整的 ER 图
5. 编写数据库迁移脚本

---

## 五、修复执行计划

### 第一阶段：解决重复定义（1-2小时）

- [ ] 删除 02-architecture.md 中的 admin_users
- [ ] 合并 withdrawals 表定义
- [ ] 统一 review_queue 表名

### 第二阶段：补充索引和注释（2-3小时）

- [ ] 为所有表添加 COMMENT
- [ ] 添加缺失的复合索引
- [ ] 更新 03-database-overview.md

### 第三阶段：验证和测试（1-2小时）

- [ ] 检查所有外键引用
- [ ] 验证枚举类型一致性
- [ ] 生成数据库迁移脚本

---

## 六、数据库统计

| 指标 | 数值 |
|------|------|
| 总表数 | 89 |
| 重复表 | 3 |
| 缺少索引的表 | 8 |
| 缺少COMMENT的表 | 35 |
| 枚举类型总数 | 50+ |
| 重复枚举类型 | 4 |

---

**报告生成人**: Claude AI
**审核建议**: 请技术负责人审核后执行修复
