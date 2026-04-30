# 数据库索引优化方案

> 本文档提供 SillyMD 平台数据库索引优化建议，包括复合索引、性能分析和执行计划。

## 一、索引优化原则

### 1.1 复合索引设计原则

1. **最左前缀原则**: 将选择性高的字段放在前面
2. **覆盖索引**: 包含查询所需的所有字段，避免回表
3. **索引选择性**: 区分度高的字段优先建索引
4. **避免过度索引**: 每个表建议不超过 5 个索引

### 1.2 适合建复合索引的场景

| 场景 | 示例 | 说明 |
|------|------|------|
| WHERE 多条件 | `WHERE category = 'tech' AND status = 'approved'` | 组合查询 |
| 排序+过滤 | `ORDER BY created_at DESC WHERE user_id = ?` | 避免文件排序 |
| 覆盖查询 | `SELECT id, name FROM skills WHERE category = ?` | 索引包含查询字段 |
| JOIN 优化 | `JOIN on user_id AND status` | 加速表连接 |

---

## 二、核心表索引优化

### 2.1 skills 表（Skills 核心表）

**当前索引**:
```sql
CREATE INDEX idx_skills_author_id ON skills(author_id);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_status ON skills(status);
CREATE INDEX idx_skills_created_at ON skills(created_at);
```

**问题分析**:
- 缺少组合查询索引：`category + status` 是常用筛选组合
- 缺少商用 Skills 查询索引：`is_commercial + status`
- 排序查询性能差：`category + created_at` 排序

**优化方案**:
```sql
-- 1. 分类+状态筛选（热门查询）
CREATE INDEX idx_skills_category_status ON skills(category, status, created_at DESC);

-- 2. 商用 Skills 查询
CREATE INDEX idx_skills_commercial_status ON skills(is_commercial, status, created_at DESC)
  WHERE is_commercial = TRUE;

-- 3. 作者 Skills 列表（含状态过滤）
CREATE INDEX idx_skills_author_status ON skills(author_id, status, updated_at DESC);

-- 4. 搜索覆盖索引（包含核心字段）
CREATE INDEX idx_skills_search_cover ON skills(category, status, created_at DESC)
  INCLUDE (name, description, author_id);

-- 5. 全文搜索优化（PostgreSQL GIN 索引）
CREATE INDEX idx_skills_content_fts ON skills USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

**预期收益**:
- 分类筛选查询提升 **60-80%**
- 排序查询消除文件排序，提升 **50%**
- 全文搜索提升 **3-5 倍**

---

### 2.2 users 表（用户表）

**优化方案**:
```sql
-- 1. 角色筛选 + 激活状态
CREATE INDEX idx_users_role_active ON users(role, is_active, created_at DESC);

-- 2. 供应商等级查询
CREATE INDEX idx_users_vendor_level ON users(role, vendor_level)
  WHERE role = 'vendor';

-- 3. 用户名/邮箱登录（唯一索引已存在，添加部分索引）
CREATE INDEX idx_users_active_username ON users(username) WHERE is_active = TRUE;
CREATE INDEX idx_users_active_email ON users(email) WHERE is_active = TRUE;

-- 4. 搜索覆盖索引
CREATE INDEX idx_users_search_cover ON users(role, is_active)
  INCLUDE (username, display_name, avatar_url);
```

---

### 2.3 point_transactions 表（积分交易）

**优化方案**:
```sql
-- 1. 用户交易历史（核心查询）
CREATE INDEX idx_transactions_user_created ON point_transactions(user_id, created_at DESC);

-- 2. 交易类型查询
CREATE INDEX idx_transactions_user_type ON point_transactions(user_id, transaction_type, created_at DESC);

-- 3. 时间范围统计
CREATE INDEX idx_transactions_created_type ON point_transactions(created_at DESC, transaction_type);

-- 4. 余额变动查询（覆盖索引）
CREATE INDEX idx_transactions_balance_cover ON point_transactions(user_id, created_at DESC)
  INCLUDE (transaction_type, amount, balance_after);
```

---

### 2.4 licenses 表（授权许可证）

**优化方案**:
```sql
-- 1. 用户授权列表
CREATE INDEX idx_licenses_user_status ON licenses(user_id, status, expires_at);

-- 2. Skill 授权查询
CREATE INDEX idx_licenses_skill_status ON licenses(skill_id, status, created_at DESC);

-- 3. 有效授权过滤
CREATE INDEX idx_licenses_valid ON licenses(user_id, skill_id, status)
  WHERE status = 'active' AND expires_at > CURRENT_TIMESTAMP;

-- 4. 即将过期授权
CREATE INDEX idx_licenses_expiring ON licenses(expires_at)
  WHERE status = 'active' AND expires_at BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '30 days';
```

---

### 2.5 team_members 表（团队成员）

**优化方案**:
```sql
-- 1. 团队成员列表（按角色）
CREATE INDEX idx_team_members_team_role ON team_members(team_id, role, joined_at);

-- 2. 用户所属团队
CREATE INDEX idx_team_members_user_status ON team_members(user_id, status);

-- 3. 活跃成员查询
CREATE INDEX idx_team_members_active ON team_members(team_id, status)
  WHERE status = 'active';

-- 4. 管理员查询
CREATE INDEX idx_team_members_admins ON team_members(team_id, role)
  WHERE role IN ('owner', 'admin');
```

---

### 2.6 review_queues 表（审核队列）

**优化方案**:
```sql
-- 1. 待审核队列（按优先级）
CREATE INDEX idx_review_priority_pending ON review_queues(status, priority, submitted_at)
  WHERE status IN ('pending', 'reviewing');

-- 2. 审核员工作队列
CREATE INDEX idx_review_reviewer_status ON review_queues(reviewer_id, stage, status)
  WHERE status IN ('pending', 'reviewing');

-- 3. 提交人审核历史
CREATE INDEX idx_review_submitter_history ON review_queues(submitter_id, submitted_at DESC);

-- 4. Skill 审核状态
CREATE INDEX idx_review_skill_status ON review_queues(skill_id, stage, status);

-- 5. 来源统计
CREATE INDEX idx_review_source_submitted ON review_queues(source, submitted_at DESC);
```

---

### 2.7 withdrawal_requests 表（提现申请）

**优化方案**:
```sql
-- 1. 用户提现记录
CREATE INDEX idx_withdrawal_user_created ON withdrawal_requests(user_id, created_at DESC);

-- 2. 待处理提现（管理员视图）
CREATE INDEX idx_withdrawal_pending_status ON withdrawal_requests(status, created_at)
  WHERE status IN ('pending', 'processing');

-- 3. 状态统计
CREATE INDEX idx_withdrawal_status_created ON withdrawal_requests(status, created_at DESC);

-- 4. 处理人员工作队列
CREATE INDEX idx_withdrawal_processor_status ON withdrawal_requests(processed_by, status, created_at DESC)
  WHERE processed_by IS NOT NULL;
```

---

### 2.8 orders 表（订单）

**优化方案**:
```sql
-- 1. 用户订单列表
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);

-- 2. 订单状态查询
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);

-- 3. 支付状态查询
CREATE INDEX idx_orders_payment_status ON orders(payment_status, created_at);

-- 4. 订单统计覆盖索引
CREATE INDEX idx_orders_stats_cover ON orders(created_at, status)
  INCLUDE (total_amount, payment_method);
```

---

### 2.9 comments 表（评论）

**优化方案**:
```sql
-- 1. Skill 评论列表
CREATE INDEX idx_comments_skill_created ON comments(skill_id, created_at DESC)
  WHERE is_deleted = FALSE;

-- 2. 用户评论历史
CREATE INDEX idx_comments_user_created ON comments(user_id, created_at DESC)
  WHERE is_deleted = FALSE;

-- 3. 父评论回复
CREATE INDEX idx_comments_parent_created ON comments(parent_id, created_at DESC)
  WHERE parent_id IS NOT NULL AND is_deleted = FALSE;

-- 4. 热门评论（点赞数）
CREATE INDEX idx_comments_skill_likes ON comments(skill_id, like_count DESC)
  WHERE is_deleted = FALSE;
```

---

## 三、特殊索引类型

### 3.1 部分索引（Partial Index）

用于索引特定条件的行，节省索引空间：

```sql
-- 只索引活跃用户
CREATE INDEX idx_active_users ON users(email) WHERE is_active = TRUE;

-- 只索引已发布 Skills
CREATE INDEX idx_published_skills ON skills(category, created_at DESC)
  WHERE status = 'approved';

-- 只索引待审核队列
CREATE INDEX idx_pending_reviews ON review_queues(priority, submitted_at)
  WHERE status = 'pending';
```

### 3.2 表达式索引

用于索引计算后的值：

```sql
-- 不区分大小写的用户名搜索
CREATE INDEX idx_users_username_lower ON users(LOWER(username));

-- 提取邮箱域名
CREATE INDEX idx_users_email_domain ON users(SUBSTRING(email FROM POSITION('@' IN email) + 1));

-- 计算字段索引
CREATE INDEX idx_skills_name_length ON skills(LENGTH(name));
```

### 3.3 JSONB 索引

用于索引 JSON/JSONB 字段：

```sql
-- GIN 索引（包含查询）
CREATE INDEX idx_skills_tags_gin ON skills USING gin(tags);

-- JSONB 路径索引
CREATE INDEX idx_review_ai_scores ON review_queues USING gin(ai_scores);

-- JSONB 存在性索引
CREATE INDEX idx_config_public ON platform_config USING gin(config_key)
  WHERE is_public = TRUE;
```

---

## 四、索引维护策略

### 4.1 索引监控

```sql
-- 查看未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 查看索引使用统计
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### 4.2 索引重建

```sql
-- 重建索引（REINDEX）
REINDEX INDEX idx_skills_category_status;

-- 并发重建（不锁表）
REINDEX INDEX CONCURRENTLY idx_skills_category_status;

-- 重建表的所有索引
REINDEX TABLE skills;
```

### 4.3 索引清理策略

| 策略 | 频率 | 说明 |
|------|------|------|
| 分析统计信息 | 每周 | `ANALYZE` |
| 重建碎片索引 | 每月 | `REINDEX` |
| 清理未使用索引 | 每季度 | 根据监控数据 |
| 真空清理表 | 每月 | `VACUUM FULL` |

---

## 五、查询优化案例

### 5.1 案例 1: Skills 列表查询

**优化前**:
```sql
SELECT * FROM skills
WHERE category = 'tech' AND status = 'approved'
ORDER BY created_at DESC
LIMIT 20;

-- 执行计划：Seq Scan + Sort
-- 耗时：150ms
```

**优化后**:
```sql
-- 使用复合索引 idx_skills_category_status
CREATE INDEX idx_skills_category_status ON skills(category, status, created_at DESC);

-- 执行计划：Index Scan using idx_skills_category_status
-- 耗时：5ms（提升 30 倍）
```

### 5.2 案例 2: 用户授权查询

**优化前**:
```sql
SELECT * FROM licenses
WHERE user_id = 12345 AND status = 'active'
  AND expires_at > CURRENT_TIMESTAMP;

-- 执行计划：Seq Scan
-- 耗时：80ms
```

**优化后**:
```sql
-- 使用部分索引 idx_licenses_valid
CREATE INDEX idx_licenses_valid ON licenses(user_id, skill_id, status)
  WHERE status = 'active' AND expires_at > CURRENT_TIMESTAMP;

-- 执行计划：Index Scan
-- 耗时：3ms（提升 26 倍）
```

---

## 六、索引优化检查清单

### 新建表时

- [ ] 主键使用 BIGSERIAL
- [ ] 外键字段建立索引
- [ ] 高频查询字段建立索引
- [ ] 状态字段考虑部分索引
- [ ] JSONB 字段建立 GIN 索引
- [ ] 排序字段包含在复合索引中

### 上线前

- [ ] 执行 EXPLAIN ANALYZE 检查查询计划
- [ ] 测试慢查询性能
- [ ] 验证索引是否被使用
- [ ] 检查索引大小是否合理

### 运维中

- [ ] 每周监控索引使用情况
- [ ] 每月分析统计信息
- [ ] 每季度清理未使用索引
- [ ] 及时调整索引策略

---

## 七、索引优化执行计划

### 阶段一：核心表优化（1 周）

- [ ] skills 表复合索引
- [ ] users 表复合索引
- [ ] point_transactions 表复合索引
- [ ] licenses 表复合索引

### 阶段二：扩展表优化（1 周）

- [ ] team_members 表复合索引
- [ ] review_queues 表复合索引
- [ ] withdrawal_requests 表复合索引
- [ ] orders 表复合索引

### 阶段三：验证与调优（3 天）

- [ ] 执行 EXPLAIN ANALYZE 验证
- [ ] 压力测试性能对比
- [ ] 调整索引配置
- [ ] 文档更新

---

## 八、参考资源

- [PostgreSQL Indexes 官方文档](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL EXPLAIN 使用指南](https://www.postgresql.org/docs/current/sql-explain.html)
- [索引设计最佳实践](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

---

**文档版本**: v1.0 | **最后更新**: 2026-02-03
**负责人**: 数据库团队
**审核人**: 技术架构组
