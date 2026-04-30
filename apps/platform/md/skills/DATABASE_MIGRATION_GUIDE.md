# 数据库迁移脚本管理

> 本文档提供 SillyMD 平台数据库迁移脚本的管理规范和示例。

## 一、迁移规范

### 1.1 迁移脚本命名规范

```
{版本号}_{描述}.sql

示例:
001_initial_schema.sql
002_add_user_roles.sql
003_create_review_queue.sql
004_add_withdrawal_fields.sql
```

### 1.2 迁移脚本结构

每个迁移脚本应包含：

```sql
-- ============================================
-- 迁移脚本说明
-- ============================================
-- 版本: 001
-- 描述: 初始化数据库架构
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

-- 开启事务
BEGIN;

-- 检查迁移版本（防止重复执行）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '001') THEN
        RAISE EXCEPTION 'Migration 001 already applied';
    END IF;
END
$$;

-- ============================================
-- 迁移内容
-- ============================================

-- 1. 创建枚举类型
CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');

-- 2. 创建表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- 4. 创建触发器
CREATE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, applied_at)
VALUES ('001', '初始化数据库架构', CURRENT_TIMESTAMP);

-- 提交事务
COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
-- BEGIN;
--
-- DROP TRIGGER update_users_updated_at ON users;
-- DROP FUNCTION update_updated_at_column();
-- DROP TABLE users;
-- DROP TYPE user_role;
--
-- DELETE FROM schema_migrations WHERE version = '001';
--
-- COMMIT;
```

---

## 二、迁移脚本示例

### 2.1 初始化架构（001）

**文件**: `migrations/001_initial_schema.sql`

```sql
-- ============================================
-- 迁移脚本: 初始化数据库架构
-- 版本: 001
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '001') THEN
        RAISE EXCEPTION 'Migration 001 already applied';
    END IF;
END
$$;

-- 创建迁移版本表（如果不存在）
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rollback_available BOOLEAN DEFAULT TRUE,
    checksum VARCHAR(64)
);

-- 核心枚举类型
CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');
CREATE TYPE vendor_level AS ENUM ('normal', 'premium', 'gold');
CREATE TYPE skill_category AS ENUM ('tech', 'product', 'design', 'marketing', 'ops');
CREATE TYPE skill_type AS ENUM ('free', 'commercial');
CREATE TYPE skill_status AS ENUM ('draft', 'reviewing', 'approved', 'rejected');
CREATE TYPE team_role AS ENUM ('owner', 'admin', 'member', 'viewer');
CREATE TYPE license_type AS ENUM ('personal', 'team', 'enterprise');

-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    vendor_level vendor_level DEFAULT 'normal',
    ai_points INT DEFAULT 0,
    avatar_url VARCHAR(500),
    bio TEXT,
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS '平台用户主表';

-- 自动更新 updated_at 函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Skills 表
CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,
    skill_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    author_id BIGINT NOT NULL,
    category skill_category NOT NULL,
    type skill_type DEFAULT 'free',
    version VARCHAR(20) DEFAULT '1.0.0',
    status skill_status DEFAULT 'draft',
    is_deleted BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    repo_url VARCHAR(500),
    dependencies JSONB,
    content_hash CHAR(64),
    platform_signature VARCHAR(255),
    author_signature VARCHAR(255),
    price INT DEFAULT 0,
    license_types JSONB,
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    favorite_count INT DEFAULT 0,
    rating_avg NUMERIC(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

COMMENT ON TABLE skills IS 'Skills 主表';

CREATE TRIGGER update_skills_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 记录迁移
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('001', '初始化数据库架构', TRUE);

COMMIT;

-- 回滚脚本
/*
BEGIN;
DROP TRIGGER update_skills_updated_at ON skills;
DROP TRIGGER update_users_updated_at ON users;
DROP FUNCTION update_updated_at_column();
DROP TABLE skills;
DROP TABLE users;
DROP TYPE license_type;
DROP TYPE team_role;
DROP TYPE skill_status;
DROP TYPE skill_type;
DROP TYPE skill_category;
DROP TYPE vendor_level;
DROP TYPE user_role;
DELETE FROM schema_migrations WHERE version = '001';
COMMIT;
*/
```

### 2.2 添加团队功能（002）

**文件**: `migrations/002_add_teams.sql`

```sql
-- ============================================
-- 迁移脚本: 添加团队协作功能
-- 版本: 002
-- ============================================

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '002') THEN
        RAISE EXCEPTION 'Migration 002 already applied';
    END IF;
END
$$;

-- 团队表
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id BIGINT NOT NULL,
    description TEXT,
    avatar_url VARCHAR(500),
    member_count INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE teams IS '团队主表';

CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 团队成员表
CREATE TABLE team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role team_role DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (team_id, user_id)
);

COMMENT ON TABLE team_members IS '团队成员关系表';

-- 索引
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('002', '添加团队协作功能', TRUE);

COMMIT;

-- 回滚脚本
/*
BEGIN;
DROP TABLE team_members;
DROP TABLE teams;
DELETE FROM schema_migrations WHERE version = '002';
COMMIT;
*/
```

### 2.3 添加审核队列（003）

**文件**: `migrations/003_add_review_queue.sql`

```sql
-- ============================================
-- 迁移脚本: 添加 AI 审核队列功能
-- 版本: 003
-- ============================================

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '003') THEN
        RAISE EXCEPTION 'Migration 003 already applied';
    END IF;
END
$$;

-- 审核相关枚举
CREATE TYPE review_stage AS ENUM ('l1_auto', 'l2_ai', 'l3_manual', 'completed', 'rejected');
CREATE TYPE review_queue_status AS ENUM ('pending', 'reviewing', 'approved', 'rejected', 'appealed');
CREATE TYPE review_priority AS ENUM ('low', 'normal', 'high', 'urgent');

-- 审核队列表
CREATE TABLE review_queues (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    submitter_id BIGINT NOT NULL,
    reviewer_id BIGINT,
    stage review_stage NOT NULL DEFAULT 'l1_auto',
    status review_queue_status NOT NULL DEFAULT 'pending',
    priority review_priority NOT NULL DEFAULT 'normal',
    source VARCHAR(50) DEFAULT 'manual',
    ai_model_version VARCHAR(50),
    ai_confidence NUMERIC(4,3),
    ai_scores JSONB,
    manual_review_note TEXT,
    reject_reason TEXT,
    submit_note TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (submitter_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES admin_users(id) ON DELETE SET NULL
);

COMMENT ON TABLE review_queues IS 'AI 审核队列表';

-- 索引
CREATE INDEX idx_review_queues_skill_id ON review_queues(skill_id);
CREATE INDEX idx_review_queues_status_priority ON review_queues(status, priority, submitted_at);

CREATE TRIGGER update_review_queues_updated_at
    BEFORE UPDATE ON review_queues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('003', '添加 AI 审核队列功能', TRUE);

COMMIT;

-- 回滚脚本
/*
BEGIN;
DROP TABLE review_queues;
DROP TYPE review_priority;
DROP TYPE review_queue_status;
DROP TYPE review_stage;
DELETE FROM schema_migrations WHERE version = '003';
COMMIT;
*/
```

### 2.4 扩展提现表（004）

**文件**: `migrations/004_extend_withdrawal_requests.sql`

```sql
-- ============================================
-- 迁移脚本: 扩展提现申请表字段
-- 版本: 004
-- ============================================

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '004') THEN
        RAISE EXCEPTION 'Migration 004 already applied';
    END IF;
END
$$;

-- 添加新字段
ALTER TABLE withdrawal_requests
    ADD COLUMN IF NOT EXISTS withdrawal_no VARCHAR(32) UNIQUE,
    ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(10,4) NOT NULL DEFAULT 1.0,
    ADD COLUMN IF NOT EXISTS cny_amount NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    ADD COLUMN IF NOT EXISTS account_name VARCHAR(100) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS admin_note TEXT;

-- 创建 withdrawal_no 唯一索引
CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_withdrawal_no
    ON withdrawal_requests(withdrawal_no);

COMMENT ON COLUMN withdrawal_requests.withdrawal_no IS '提现单号';
COMMENT ON COLUMN withdrawal_requests.exchange_rate IS '汇率（积分转人民币）';
COMMENT ON COLUMN withdrawal_requests.cny_amount IS '人民币金额';
COMMENT ON COLUMN withdrawal_requests.account_name IS '账户名称';
COMMENT ON COLUMN withdrawal_requests.admin_note IS '管理员备注';

INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('004', '扩展提现申请表字段', FALSE);  -- 不可回滚

COMMIT;

-- 回滚脚本（注意：ALTER TABLE DROP COLUMN 不可逆）
/*
BEGIN;
ALTER TABLE withdrawal_requests DROP COLUMN IF EXISTS withdrawal_no;
ALTER TABLE withdrawal_requests DROP COLUMN IF EXISTS exchange_rate;
ALTER TABLE withdrawal_requests DROP COLUMN IF EXISTS cny_amount;
ALTER TABLE withdrawal_requests DROP COLUMN IF EXISTS account_name;
ALTER TABLE withdrawal_requests DROP COLUMN IF EXISTS admin_note;
DELETE FROM schema_migrations WHERE version = '004';
COMMIT;
*/
```

---

## 三、迁移执行工具

### 3.1 使用 Alembic（Python）

```python
# alembic/env.py

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
target_metadata = None

def run_migrations_online():
    """在线迁移模式"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

### 3.2 使用纯 SQL 脚本

```bash
#!/bin/bash
# migrate.sh - 迁移执行脚本

set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-sillymd}"
DB_USER="${DB_USER:-postgres}"
MIGRATIONS_DIR="./migrations"

# 检查迁移版本
check_version() {
    local version=$1
    local count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -tAc "SELECT COUNT(*) FROM schema_migrations WHERE version = '$version'")

    if [ "$count" -gt 0 ]; then
        echo "迁移 $version 已应用，跳过"
        return 1
    fi
    return 0
}

# 执行迁移
apply_migration() {
    local file=$1
    local version=$(basename "$file" | cut -d'_' -f1)

    echo "应用迁移: $file"

    if ! check_version "$version"; then
        return 0
    fi

    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file"

    if [ $? -eq 0 ]; then
        echo "迁移 $version 应用成功"
    else
        echo "迁移 $version 应用失败"
        exit 1
    fi
}

# 执行所有迁移
for migration in "$MIGRATIONS_DIR"/*.sql; do
    apply_migration "$migration"
done

echo "所有迁移完成"
```

---

## 四、迁移最佳实践

### 4.1 迁移脚本编写规范

1. **原子性**: 所有迁移放在事务中
2. **幂等性**: 支持重复执行
3. **可回滚**: 提供回滚脚本
4. **版本控制**: 记录迁移版本
5. **完整性检查**: 迁移后验证数据

### 4.2 迁移前检查清单

- [ ] 备份当前数据库
- [ ] 在测试环境验证迁移
- [ ] 评估迁移执行时间
- [ ] 准备回滚方案
- [ ] 通知相关人员

### 4.3 迁移后验证

```sql
-- 验证表结构
\d table_name

-- 验证数据完整性
SELECT COUNT(*) FROM table_name;

-- 验证外键约束
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- 验证索引
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename = 'table_name';
```

---

## 五、迁移版本管理

### 5.1 版本查询

```sql
-- 查看所有已应用的迁移
SELECT * FROM schema_migrations ORDER BY applied_at;

-- 查看当前数据库版本
SELECT version FROM schema_migrations
ORDER BY applied_at DESC
LIMIT 1;
```

### 5.2 版本对比

```bash
# 比较迁移文件和数据库版本
python scripts/check_migrations.py

# 输出示例:
# 待应用迁移:
# - 004_extend_withdrawal_requests.sql
# - 005_add_notifications.sql
# 已应用迁移:
# - 001_initial_schema.sql
# - 002_add_teams.sql
# - 003_add_review_queue.sql
```

---

## 六、故障处理

### 6.1 迁移失败处理

```sql
-- 1. 检查迁移状态
SELECT * FROM schema_migrations WHERE version = '004';

-- 2. 手动标记迁移为失败
UPDATE schema_migrations
SET applied_at = NULL
WHERE version = '004';

-- 3. 回滚到上一个版本
-- 执行 004 的回滚脚本

-- 4. 修复问题后重试
-- 重新执行 004 迁移
```

### 6.2 数据修复脚本

**文件**: `migrations/fix/004_fix_withdrawal_data.sql`

```sql
-- ============================================
-- 数据修复脚本
-- 说明: 修复提现申请的汇率数据
-- ============================================

BEGIN;

-- 修复历史数据的汇率
UPDATE withdrawal_requests
SET
    exchange_rate = 0.1,
    cny_amount = ROUND(amount * exchange_rate, 2)
WHERE exchange_rate IS NULL
  OR exchange_rate = 0;

-- 验证修复结果
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE exchange_rate > 0) AS fixed
FROM withdrawal_requests;

COMMIT;
```

---

**文档版本**: v1.0 | **最后更新**: 2026-02-03
**维护人**: 数据库运维团队
