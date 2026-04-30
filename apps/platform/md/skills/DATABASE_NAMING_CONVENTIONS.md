# 数据库字段命名规范

> 本文档定义 SillyMD 平台数据库字段命名规范，确保跨团队、跨项目的一致性。

## 一、通用命名原则

### 1.1 基本规则

| 规则 | 说明 | 示例 |
|------|------|------|
| 小写+下划线 | 所有字段名使用小写字母和下划线 | `user_id`, `created_at` |
| 英文命名 | 使用英文单词，避免拼音 | `username` 而非 `yonghuming` |
| 完整单词 | 优先使用完整单词，而非缩写 | `email` 而非 `mail` |
| 语义清晰 | 字段名应清楚表达其含义 | `is_active` 而非 `flag` |
| 避免保留字 | 不使用 SQL 保留字 | `user_status` 而非 `status` |

### 1.2 特殊字符规则

| 字符 | 用途 | 示例 |
|------|------|------|
| `_` | 单词分隔 | `first_name` |
| `_id` | 外键引用 | `user_id`, `team_id` |
| `_at` | 时间字段 | `created_at`, `updated_at` |
| `_by` | 操作者字段 | `created_by`, `updated_by` |
| `_no` | 编号字段 | `order_no`, `invoice_no` |
| `_count` | 计数字段 | `view_count`, `download_count` |
| `_url` | 链接字段 | `avatar_url`, `repo_url` |
| `_type` | 类型字段 | `skill_type`, `payment_type` |
| `_status` | 状态字段 | `order_status`, `payment_status` |
| `is_` | 布尔字段 | `is_active`, `is_verified` |

---

## 二、标准字段定义

### 2.1 主键字段

| 字段名 | 类型 | 说明 | 使用场景 |
|--------|------|------|----------|
| `id` | BIGSERIAL | 自增主键 | 所有表的主键 |
| `{表名}_id` | VARCHAR | 外部标识符 | 人类可读的唯一标识 |

**示例**:
```sql
CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,        -- 内部 ID
    skill_id VARCHAR(50) UNIQUE      -- 外部标识符
);
```

### 2.2 外键字段

| 命名规则 | 说明 | 示例 |
|----------|------|------|
| `{关联表单数}_id` | 引用其他表的主键 | `user_id`, `team_id`, `skill_id` |
| `{关联表}_{关联字段}` | 引用其他表的特定字段 | `author_name`, `owner_email` |

**外键字段必须添加索引**:
```sql
CREATE INDEX idx_table_user_id ON table_name(user_id);
```

### 2.3 时间戳字段

| 字段名 | 类型 | 时区 | 说明 |
|--------|------|------|------|
| `created_at` | TIMESTAMPTZ | 是 | 记录创建时间 |
| `updated_at` | TIMESTAMPTZ | 是 | 记录更新时间（自动触发） |
| `deleted_at` | TIMESTAMPTZ | 是 | 软删除时间（NULL=未删除） |
| `{事件}_at` | TIMESTAMPTZ | 是 | 特定事件时间 |

**特殊时间字段**:
```sql
-- 用户相关
last_login_at       TIMESTAMPTZ  -- 最后登录时间
last_activity_at    TIMESTAMPTZ  -- 最后活跃时间

-- 订单相关
paid_at             TIMESTAMPTZ  -- 支付时间
shipped_at          TIMESTAMPTZ  -- 发货时间
completed_at        TIMESTAMPTZ  -- 完成时间
cancelled_at        TIMESTAMPTZ  -- 取消时间
refunded_at         TIMESTAMPTZ  -- 退款时间

-- 内容相关
published_at        TIMESTAMPTZ  -- 发布时间
scheduled_at        TIMESTAMPTZ  -- 计划时间
started_at          TIMESTAMPTZ  -- 开始时间
ended_at            TIMESTAMPTZ  -- 结束时间
expires_at          TIMESTAMPTZ  -- 过期时间
```

### 2.4 状态字段

| 命名规则 | 说明 | 示例 |
|----------|------|------|
| `{实体}_status` | 业务状态 | `order_status`, `payment_status` |
| `status` | 通用状态 | `status` (当只有一个状态时) |

**常见状态值**:
```sql
-- 通用状态
pending    -- 待处理
processing -- 处理中
active     -- 活跃
inactive   -- 非活跃
completed  -- 已完成
failed     -- 失败
cancelled  -- 已取消
deleted    -- 已删除

-- 订单状态
pending    -- 待支付
paid       -- 已支付
completed  -- 已完成
refunded   -- 已退款

-- 审核状态
pending    -- 待审核
reviewing  -- 审核中
approved   -- 已通过
rejected   -- 已拒绝
```

### 2.5 布尔字段

| 命名规则 | 说明 | 示例 |
|----------|------|------|
| `is_{形容词}` | 状态标记 | `is_active`, `is_verified` |
| `has_{名词}` | 拥有关系 | `has_permission`, `has_trial` |
| `can_{动词}` | 能力标记 | `can_edit`, `can_delete` |
| `enable_{功能}` | 功能开关 | `enable_notification` |

**默认值规范**:
```sql
is_active    BOOLEAN DEFAULT TRUE   -- 默认激活
is_verified  BOOLEAN DEFAULT FALSE  -- 默认未验证
is_deleted   BOOLEAN DEFAULT FALSE  -- 默认未删除
is_featured  BOOLEAN DEFAULT FALSE  -- 默认非精选
```

### 2.6 金额字段

| 字段名 | 类型 | 说明 | 单位 |
|--------|------|------|------|
| `price` | NUMERIC(10,2) | 单价 | 元 |
| `amount` | INT | 数量/金额 | 积分 |
| `total_amount` | INT | 总金额 | 积分 |
| `fee` | INT | 手续费 | 积分 |
| `{类型}_amount` | INT | 特定金额 | 积分 |

**金额字段使用 INT 存储积分，使用 NUMERIC 存储人民币**:
```sql
-- 积分相关（整数）
price            INT       -- 价格（积分）
total_amount     INT       -- 总金额（积分）
discount_amount  INT       -- 折扣金额（积分）

-- 人民币相关（精确到分）
cny_price        NUMERIC(10,2)  -- 价格（元）
cny_amount       NUMERIC(10,2)  -- 金额（元）
exchange_rate    NUMERIC(10,4)  -- 汇率
```

### 2.7 计数字段

| 命名规则 | 说明 | 示例 |
|----------|------|------|
| `{名词}_count` | 数量统计 | `view_count`, `like_count` |
| `member_count` | 成员数量 | `team.member_count` |
| `{名词}_total` | 总数 | `download_total` |

**常见计数字段**:
```sql
-- 内容统计
view_count       INT DEFAULT 0    -- 浏览次数
download_count   INT DEFAULT 0    -- 下载次数
favorite_count   INT DEFAULT 0    -- 收藏次数
share_count      INT DEFAULT 0    -- 分享次数
comment_count    INT DEFAULT 0    -- 评论次数

-- 用户统计
follower_count   INT DEFAULT 0    -- 粉丝数
following_count  INT DEFAULT 0    -- 关注数
post_count       INT DEFAULT 0    -- 发帖数

-- 评分统计
rating_count     INT DEFAULT 0    -- 评分人数
rating_avg       NUMERIC(3,2) DEFAULT 0.00  -- 平均评分
```

### 2.8 文本字段

| 字段名 | 类型 | 长度 | 说明 |
|--------|------|------|------|
| `name` | VARCHAR | 50-200 | 短名称 |
| `title` | VARCHAR | 100-255 | 标题 |
| `description` | TEXT | - | 描述 |
| `content` | TEXT | - | 长内容 |
| `reason` | TEXT | - | 原因说明 |
| `note` | TEXT | - | 备注 |
| `comment` | TEXT | - | 评论 |

**VARCHAR 长度建议**:
```sql
username        VARCHAR(50)    -- 用户名
email           VARCHAR(100)   -- 邮箱
password_hash   VARCHAR(255)   -- 密码哈希
title           VARCHAR(200)   -- 标题
description     VARCHAR(500)   -- 简短描述
url             VARCHAR(500)   -- URL
ip_address      VARCHAR(45)    -- IP 地址
user_agent      VARCHAR(500)   -- 用户代理
```

### 2.9 JSON 字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `metadata` | JSONB | 元数据 |
| `{实体}_config` | JSONB | 配置信息 |
| `{实体}_data` | JSONB | 扩展数据 |
| `{实体}_details` | JSONB | 详细信息 |

**JSON 字段使用 JSONB 类型（支持索引）**:
```sql
-- 配置类
permissions      JSONB     -- 权限列表
config           JSONB     -- 配置信息
settings         JSONB     -- 设置

-- 扩展类
extra_info       JSONB     -- 额外信息
custom_data      JSONB     -- 自定义数据
metadata         JSONB     -- 元数据
```

---

## 三、业务字段命名规范

### 3.1 用户相关

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `username` | VARCHAR(50) | 用户名 |
| `email` | VARCHAR(100) | 邮箱 |
| `password_hash` | VARCHAR(255) | 密码哈希 |
| `avatar_url` | VARCHAR(500) | 头像 URL |
| `bio` | TEXT | 个人简介 |
| `display_name` | VARCHAR(100) | 显示名称 |
| `role` | ENUM | 角色 |
| `vendor_level` | ENUM | 供应商等级 |

### 3.2 内容相关

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | VARCHAR(200) | 名称 |
| `title` | VARCHAR(200) | 标题 |
| `summary` | VARCHAR(500) | 摘要 |
| `description` | TEXT | 描述 |
| `content` | TEXT | 内容 |
| `cover_image` | VARCHAR(500) | 封面图 |
| `category` | ENUM | 分类 |
| `tags` | JSONB/TEXT | 标签 |

### 3.3 团队协作

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `team_id` | BIGINT | 团队 ID |
| `team_name` | VARCHAR(100) | 团队名称 |
| `team_slug` | VARCHAR(100) | 团队 URL 标识 |
| `owner_id` | BIGINT | 所有者 ID |
| `member_count` | INT | 成员数量 |
| `project_id` | BIGINT | 项目 ID |
| `project_name` | VARCHAR(200) | 项目名称 |

### 3.4 交易支付

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `order_no` | VARCHAR(32) | 订单编号 |
| `payment_no` | VARCHAR(32) | 支付编号 |
| `transaction_no` | VARCHAR(32) | 交易编号 |
| `buyer_id` | BIGINT | 买家 ID |
| `seller_id` | BIGINT | 卖家 ID |
| `vendor_id` | BIGINT | 供应商 ID |
| `amount` | INT | 金额（积分） |
| `fee` | INT | 手续费 |
| `income` | INT | 收入 |
| `refund_amount` | INT | 退款金额 |

### 3.5 审核流程

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `submitter_id` | BIGINT | 提交人 ID |
| `reviewer_id` | BIGINT | 审核人 ID |
| `assigned_to` | BIGINT | 分配给谁 |
| `priority` | ENUM | 优先级 |
| `stage` | ENUM | 阶段 |
| `ai_confidence` | NUMERIC(4,3) | AI 置信度 |
| `ai_scores` | JSONB | AI 评分 |
| `manual_note` | TEXT | 人工备注 |
| `reject_reason` | TEXT | 驳回原因 |

---

## 四、命名禁忌

### 4.1 禁止使用的命名

| 类型 | 禁止使用 | 原因 | 替代方案 |
|------|----------|------|----------|
| 缩写 | `usr`, `pwd`, `msg` | 不易读 | `user`, `password`, `message` |
| 拼音 | `yonghuming`, `dizhi` | 不国际化 | `username`, `address` |
| 数字后缀 | `name1`, `type2` | 含义不清 | `first_name`, `secondary_type` |
| 保留字 | `order`, `group`, `user` | SQL 关键字 | `orders`, `groups`, `users` |
| 模糊命名 | `data`, `info`, `temp` | 不明确 | 根据实际业务命名 |

### 4.2 反模式示例

```sql
-- ❌ 错误示例
CREATE TABLE bad_example (
    usr VARCHAR(50),           -- 缩写
    pwd VARCHAR(255),          -- 缩写
    msg TEXT,                  -- 缩写
    data1 TEXT,                -- 含义不清
    flag1 BOOLEAN,             -- 含义不清
    type INT,                  -- 类型模糊
    status INT                 -- 应使用 ENUM
);

-- ✅ 正确示例
CREATE TABLE good_example (
    username VARCHAR(50),       -- 清晰
    password_hash VARCHAR(255), -- 明确
    message TEXT,               -- 完整
    config_data TEXT,           -- 语义化
    is_active BOOLEAN,          -- 布尔前缀
    account_type account_type,  -- 使用枚举
    status status_type          -- 使用枚举
);
```

---

## 五、一致性检查清单

### 5.1 新建表时检查

- [ ] 主键使用 `id BIGSERIAL PRIMARY KEY`
- [ ] 外键命名为 `{表名}_id` 并添加索引
- [ ] 时间字段使用 `TIMESTAMPTZ` 类型
- [ ] 时间字段命名符合 `{事件}_at` 规范
- [ ] 布尔字段使用 `is_` 前缀
- [ ] 状态字段使用 `{实体}_status` 或 `status` 枚举
- [ ] JSON 字段使用 `JSONB` 类型
- [ ] 金额字段明确单位（积分/人民币）
- [ ] 为所有表和字段添加 COMMENT
- [ ] 创建 `updated_at` 触发器

### 5.2 现有表迁移检查

- [ ] 字段命名符合本规范
- [ ] 外键字段有索引
- [ ] 时间字段统一为 `TIMESTAMPTZ`
- [ ] 布尔字段统一为 `is_` 前缀
- [ ] COMMENT 注释完整

---

## 六、工具和脚本

### 6.1 命名检查脚本（Python）

```python
import re

def check_field_name(field_name):
    """检查字段名是否符合规范"""
    patterns = {
        'primary_key': r'^id$',                           # 主键
        'foreign_key': r'.+_id$',                         # 外键
        'timestamp': r'.+_at$',                           # 时间戳
        'status': r'.+_status$|^status$',                 # 状态
        'boolean': r'^is_',                               # 布尔
        'count': r'.+_count$',                           # 计数
        'url': r'.+_url$',                               # 链接
        'type': r'.+_type$',                             # 类型
    }

    # 检查是否全小写+下划线
    if not re.match(r'^[a-z][a-z0-9_]*$', field_name):
        return False, "字段名应使用小写字母和下划线"

    # 检查是否使用保留字
    reserved_words = ['order', 'group', 'user', 'select', 'from']
    if field_name in reserved_words:
        return False, f"字段名使用了保留字: {field_name}"

    # 检查是否使用了禁止的缩写
    abbreviations = ['usr', 'pwd', 'msg', 'info', 'data']
    if field_name in abbreviations:
        return False, f"字段名使用了缩写: {field_name}"

    return True, "字段名符合规范"
```

### 6.2 自动生成 COMMENT

```sql
-- 为表生成 COMMENT 的函数
CREATE OR REPLACE FUNCTION generate_table_comments(table_name TEXT)
RETURNS TEXT AS $$
DECLARE
    comment_text TEXT;
BEGIN
    comment_text := format('COMMENT ON TABLE %s IS ''%s表'';', table_name, table_name);
    RETURN comment_text;
END;
$$ LANGUAGE plpgsql;
```

---

## 七、参考资源

- [PostgreSQL 命名规范](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [数据库字段命名最佳实践](https://www.sqlstyle.guide/)
- [阿里巴巴 Java 开发手册 - 数据规范](https://github.com/alibaba/p3c)

---

**文档版本**: v1.0 | **最后更新**: 2026-02-03
**维护人**: 数据库架构团队
**审核人**: 技术委员会
