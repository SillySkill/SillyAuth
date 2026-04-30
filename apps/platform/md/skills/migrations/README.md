# SillyMD 数据库迁移脚本

> 本目录包含 SillyMD 平台 PostgreSQL 数据库的版本化迁移脚本。

## 迁移脚本列表

| 版本 | 文件 | 描述 | 状态 |
|------|------|------|------|
| 001 | `001_initial_schema.sql` | 初始化数据库架构（枚举类型和核心表） | ✅ |
| 002 | `002_add_teams.sql` | 添加团队协作功能 | ✅ |
| 004 | `004_add_message_system.sql` | 添加消息系统 | ✅ |
| 005 | `005_add_vendor_system.sql` | 添加供应商系统 | ✅ |
| 006 | `006_add_user_preferences.sql` | 添加用户偏好和认证 | ✅ |
| 007 | `007_add_operations_tables.sql` | 添加运营统计表 | ✅ |
| 008 | `008_add_commerce_tables.sql` | 添加商用交易表 | ✅ |
| 009 | `009_add_upload_records.sql` | 添加外部应用集成（AI活动秀文件上传） | ✅ |

## 快速开始

### 方式一：使用执行脚本（推荐）

**Linux / macOS:**
```bash
# 设置环境变量（可选，有默认值）
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=sillymd
export DB_USER=postgres
export DB_PASSWORD=your_password

# 执行迁移
cd migrations
chmod +x migrate.sh
./migrate.sh
```

**Windows:**
```cmd
# 设置环境变量（可选）
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=sillymd
set DB_USER=postgres
set DB_PASSWORD=your_password

# 执行迁移
cd migrations
migrate.bat
```

### 方式二：手动执行

```bash
# 连接到数据库
psql -h localhost -U postgres -d sillymd

# 手动执行每个迁移文件
\i 001_initial_schema.sql
\i 002_add_teams.sql
\i 004_add_message_system.sql
\i 005_add_vendor_system.sql
\i 006_add_user_preferences.sql
\i 007_add_operations_tables.sql
\i 008_add_commerce_tables.sql
\i 009_add_upload_records.sql
```

### 方式三：使用迁移工具（Alembic）

如果使用 Python 的 Alembic 进行迁移管理，可以参考以下配置：

**alembic/env.py:**
```python
from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
target_metadata = None

def run_migrations_online():
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

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_HOST` | localhost | 数据库主机地址 |
| `DB_PORT` | 5432 | 数据库端口 |
| `DB_NAME` | sillymd | 数据库名称 |
| `DB_USER` | postgres | 数据库用户名 |
| `DB_PASSWORD` | (空) | 数据库密码 |

## 查看迁移状态

```sql
-- 查看所有已应用的迁移
SELECT * FROM schema_migrations ORDER BY applied_at;

-- 查看当前数据库版本
SELECT version FROM schema_migrations
ORDER BY applied_at DESC
LIMIT 1;
```

## 回滚迁移

每个迁移脚本文件末尾都包含注释掉的回滚脚本。如需回滚：

1. 找到对应迁移文件末尾的回滚脚本
2. 取消注释
3. 执行回滚脚本

**示例：回滚 001 迁移**
```bash
psql -h localhost -U postgres -d sillymd
```

然后复制粘贴 `001_initial_schema.sql` 文件末尾的回滚脚本（去掉 `/* */` 注释）。

## 注意事项

1. **备份**：在生产环境执行迁移前，务必备份数据库
   ```bash
   pg_dump -h localhost -U postgres sillymd > backup_$(date +%Y%m%d).sql
   ```

2. **测试环境**：建议先在测试环境验证迁移脚本

3. **权限**：执行迁移的用户需要 CREATE、CREATE TYPE、CREATE TABLE 等权限

4. **事务**：每个迁移都在事务中执行，失败会自动回滚

5. **幂等性**：迁移脚本会检查是否已应用，避免重复执行

## 故障处理

### 迁移失败

如果迁移执行失败：

1. 查看日志文件：`migration_*.log`
2. 检查错误信息
3. 修复问题后重新执行（会跳过已成功的迁移）

### 部分迁移失败

如果某个迁移执行失败，后续迁移会自动停止。修复问题后：

1. 检查失败原因
2. 手动修复数据库状态
3. 删除失败的迁移记录（如果需要）
   ```sql
   DELETE FROM schema_migrations WHERE version = '00X';
   ```
4. 重新执行迁移脚本

## 数据库表结构

迁移完成后，数据库将包含以下表：

**核心表（001）:**
- users - 用户表
- skills - Skills 主表
- skill_versions - Skills 版本表
- skill_dependencies - Skills 依赖关系表
- tags - 标签表
- skill_tags - Skills-标签关联表
- skill_favorites - Skills 收藏表
- skill_comments - Skills 评论表
- reviews - 审核记录表
- achievements - 成就表
- user_achievements - 用户成就关联表
- licenses - 授权记录表
- point_transactions - 积分交易表
- audit_logs - 操作日志表
- notifications - 消息通知表
- invitations - 邀请记录表

**团队协作表（002）:**
- teams - 团队表
- team_members - 团队成员表
- team_projects - 团队项目表
- project_skills - 项目-Skills 关联表
- project_milestones - 项目里程碑表

**消息系统表（004）:**
- conversations - 对话表
- conversation_participants - 对话参与者表
- messages - 消息表

**供应商系统表（005）:**
- vendor_applications - 供应商申请表
- vendor_verifications - 供应商实名认证表
- vendor_tiers - 供应商等级表

**用户偏好和认证（006）:**
- user_preferences - 用户偏好设置表
- password_reset_tokens - 密码重置令牌表
- email_verifications - 邮箱验证表

**运营统计表（007）:**
- page_views - 页面访问统计表
- user_activity_logs - 用户活动日志表

**商用交易表（008）:**
- orders - 订单表
- payments - 支付记录表
- withdrawal_requests - 提现申请表
- commission_records - 佣金记录表

**外部应用集成表（009）:**
- upload_records - AI活动秀文件上传记录表

## 支持

如有问题，请参考：
- [DATABASE_MIGRATION_GUIDE.md](../DATABASE_MIGRATION_GUIDE.md) - 迁移规范
- [DATABASE_NAMING_CONVENTIONS.md](../DATABASE_NAMING_CONVENTIONS.md) - 命名规范
- [02-architecture.md](../02-architecture.md) - 数据库设计文档

---

**版本**: v1.1 | **最后更新**: 2026-02-05
**维护人**: 数据库运维团队
