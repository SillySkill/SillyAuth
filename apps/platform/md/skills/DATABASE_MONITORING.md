# 数据库监控与维护指南

> 本文档提供 SillyMD 平台 PostgreSQL 数据库的监控指标、告警策略和维护计划。

## 一、监控架构

```
┌─────────────────────────────────────────────────────────────┐
│                    监控架构概览                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │   应用层      │    │   数据库层    │    │   监控层     ││
│  │              │    │              │    │              ││
│  │ - Slow Query │───>│ - PostgreSQL │───>│ - Prometheus ││
│  │ - Error Log  │    │ - pg_stat    │    │ - Grafana    ││
│  │ - Metrics    │    │ - pg_statio  │    │ - Alertmgr   ││
│  └──────────────┘    └──────────────┘    └──────────────┘│
│                             │                           │
│                             ▼                           ▼
│                      ┌──────────────┐    ┌──────────────┐
│                      │ 告警通知     │    │ 报表系统     │
│                      │              │    │              │
│                      │ - Email      │    │ - Daily       │
│                      │ - Slack      │    │ - Weekly      │
│                      │ - DingTalk   │    │ - Monthly     │
│                      └──────────────┘    └──────────────┘
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、核心监控指标

### 2.1 连接监控

| 指标 | 说明 | 告警阈值 | 严重程度 |
|------|------|----------|----------|
| `active_connections` | 活跃连接数 | > 80% max_connections | ⚠️ 警告 |
| `idle_connections` | 空闲连接数 | > 50 | ⚠️ 警告 |
| `connection_usage` | 连接使用率 | > 90% | 🚨 严重 |
| `connection_wait_time` | 连接等待时间 | > 5s | ⚠️ 警告 |

**查询语句**:
```sql
-- 连接数统计
SELECT
    state,
    COUNT(*) AS connections,
    AVG(query_start) AS avg_query_start
FROM pg_stat_activity
GROUP BY state
ORDER BY connections DESC;

-- 连接使用率
SELECT
    COUNT(*) AS active_connections,
    (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections') AS max_connections,
    ROUND(100.0 * COUNT(*) / (SELECT setting::INT FROM pg_settings WHERE name = 'max_connections'), 2) AS usage_percentage
FROM pg_stat_activity
WHERE state = 'active';

-- 长时间运行的查询
SELECT
    pid,
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state IN ('active', 'idle in transaction')
    AND now() - query_start > INTERVAL '5 minutes'
ORDER BY duration DESC;
```

### 2.2 查询性能监控

| 指标 | 说明 | 告警阈值 | 严重程度 |
|------|------|----------|----------|
| `slow_query_count` | 慢查询数量 | > 10/min | ⚠️ 警告 |
| `query_latency_p99` | 查询延迟 P99 | > 1s | 🚨 严重 |
| `deadlock_count` | 死锁数量 | > 0 | 🚨 严重 |
| `lock_wait_time` | 锁等待时间 | > 10s | ⚠️ 警告 |

**查询语句**:
```sql
-- 慢查询统计（基于 pg_stat_statements）
SELECT
    calls,
    total_exec_time / calls AS avg_time,
    total_exec_time,
    query
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 超过 1 秒
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 锁等待
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) AS blocked_by,
    query as blocked_query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- 表锁等待
SELECT
    l.relation::regclass AS table_name,
    l.mode,
    a.query,
    a.usename,
    a.query_start
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted
ORDER BY a.query_start;
```

### 2.3 表膨胀监控

| 指标 | 说明 | 告警阈值 | 严重程度 |
|------|------|----------|----------|
| `table_bloat_ratio` | 表膨胀率 | > 20% | ⚠️ 警告 |
| `index_bloat_ratio` | 索引膨胀率 | > 30% | ⚠️ 警告 |
| `dead_tuple_ratio` | 死元组比例 | > 10% | ⚠️ 警告 |

**查询语句**:
```sql
-- 表膨胀检测
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    (SELECT n_dead_tup / (SELECT n_live_tup + n_dead_tup) AS dead_ratio
     FROM pg_stat_user_tables
     WHERE schemaname = pg_class.relnamespace::regnamespace::name
       AND relname = pg_class.relname) AS dead_ratio
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY total_size DESC;

-- 需要清理的表
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
    AND (n_dead_tup::FLOAT / NULLIF(n_live_tup + n_dead_tup, 0)) > 0.1
ORDER BY dead_ratio DESC;
```

### 2.4 索引监控

| 指标 | 说明 | 告警阈值 | 严重程度 |
|------|------|----------|----------|
| `unused_index_count` | 未使用索引 | > 5 | ⚠️ 警告 |
| `index_size_ratio` | 索引/表大小比 | > 50% | ⚠️ 警告 |
| `duplicate_index` | 重复索引 | > 0 | ⚠️ 警告 |

**查询语句**:
```sql
-- 未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS index_scans
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 重复索引（相同前导列）
SELECT
    pg_size_pretty(SUM(pg_relation_size(indexrelid))) AS total_size,
    array_agg(indexname) AS indexes
FROM pg_stat_user_indexes
GROUP BY schemaname, tablename, indkey
HAVING COUNT(*) > 1
ORDER BY SUM(pg_relation_size(indexrelid)) DESC;

-- 索引大小与表大小对比
SELECT
    t.tablename,
    pg_size_pretty(pg_relation_size(t.tablename::regclass)) AS table_size,
    pg_size_pretty(SUM(pg_relation_size(i.indexrelid))) AS indexes_size,
    ROUND(100.0 * SUM(pg_relation_size(i.indexrelid)) / NULLIF(pg_relation_size(t.tablename::regclass), 0), 2) AS index_ratio
FROM pg_tables t
JOIN pg_indexes i ON i.tablename = t.tablename
GROUP BY t.tablename
HAVING SUM(pg_relation_size(i.indexrelid)) > pg_relation_size(t.tablename::regclass) * 0.5
ORDER BY index_ratio DESC;
```

### 2.5 复制与备份监控

| 指标 | 说明 | 告警阈值 | 严重程度 |
|------|------|----------|----------|
| `replication_lag` | 复制延迟 | > 10s | ⚠️ 警告 |
| `replication_status` | 复制状态 | not streaming | 🚨 严重 |
| `backup_age` | 备份时效 | > 25h | 🚨 严重 |
| `backup_status` | 备份状态 | failed | 🚨 严重 |

**查询语句**:
```sql
-- 复制延迟（流复制）
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(replay_lsn, sent_lsn) AS lag_bytes,
    pg_wal_replay_pause_state AS replay_paused
FROM pg_stat_replication;

-- WAL 生成速率
SELECT
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) AS pending_wal,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag
FROM pg_stat_replication;

-- 最近备份时间（假设使用 pg_probackup）
SELECT
    backup_id,
    backup_mode,
    start_time,
    end_time,
    status,
    pg_size_pysize(data_size)
FROM pg_backup_history
ORDER BY start_time DESC
LIMIT 10;
```

---

## 三、告警规则

### 3.1 Prometheus 告警规则

**文件**: `alerts/postgresql.yml`

```yaml
groups:
  - name: postgresql_alerts
    interval: 30s
    rules:
      # 连接数告警
      - alert: PostgresqlHighConnectionUsage
        expr: |
          pg_stat_activity_count{datname="sillymd"}
          / pg_settings_max_connections > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL 连接数过高"
          description: "连接数使用率超过 90% (当前: {{ $value }}%)"

      # 慢查询告警
      - alert: PostgresqlSlowQueries
        expr: |
          rate(pg_stat_statements_calls{mean_exec_time_ms > 1000}[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "检测到大量慢查询"
          description: "5 分钟内慢查询数量: {{ $value }}"

      # 表膨胀告警
      - alert: PostgresqlTableBloat
        expr: |
          pg_stat_user_tables_dead_ratio > 0.2
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "表膨胀率过高"
          description: "表 {{ $labels.tablename }} 死元组比例: {{ $value }}%"

      # 死锁告警
      - alert: PostgresqlDeadlocks
        expr: |
          rate(pg_stat_database_deadlocks[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "检测到死锁"
          description: "数据库发生死锁"

      # 复制延迟告警
      - alert: PostgresqlReplicationLag
        expr: |
          pg_stat_replication_lag_seconds > 30
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "复制延迟过高"
          description: "复制延迟: {{ $value }} 秒"

      # WAL 目录大小告警
      - alert: PostgresqlWalDirectorySize
        expr: |
          pg_wal_directory_size_bytes > 10737418240  # 10GB
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "WAL 目录过大"
          description: "WAL 目录大小: {{ $value }}"
```

### 3.2 告警通知渠道

| 严重程度 | 通知渠道 | 响应时间 |
|----------|----------|----------|
| 🚨 Critical | 电话 + 钉钉 + Slack | 立即 |
| ⚠️ Warning | 钉钉 + 邮件 | 15分钟 |
| ℹ️ Info | 邮件 | 工作时间 |

---

## 四、日常维护任务

### 4.1 每日任务

| 任务 | 脚本 | 时间 |
|------|------|------|
| 检查慢查询 | `scripts/check_slow_queries.sh` | 09:00 |
| 检查连接数 | `scripts/check_connections.sh` | 09:00 |
| 检查磁盘空间 | `scripts/check_disk_space.sh` | 09:00 |
| 备份验证 | `scripts/verify_backup.sh` | 02:00 |

### 4.2 每周任务

| 任务 | 脚本 | 日期 |
|------|------|------|
| 表膨胀检测 | `scripts/check_table_bloat.sh` | 周一 |
| 索引使用分析 | `scripts/analyze_index_usage.sh` | 周二 |
| 查询性能报告 | `scripts/generate_query_report.sh` | 周三 |
| 安全审计 | `scripts/security_audit.sh` | 周五 |

### 4.3 每月任务

| 任务 | 脚本 | 时间 |
|------|------|------|
| 完整数据库备份 | `pg_probackup backup` | 每月1日 |
| 统计信息更新 | `ANALYZE` | 每月1日 |
| 索引重建 | `scripts/rebuild_indexes.sh` | 每月15日 |
| 清理旧数据 | `scripts/cleanup_old_data.sh` | 每月最后一天 |

---

## 五、维护脚本

### 5.1 表清理脚本

**文件**: `scripts/vacuum_tables.sh`

```bash
#!/bin/bash
# VACUUM 清理脚本

set -e

DB_NAME="${DB_NAME:-sillymd}"
LOG_FILE="/var/log/postgresql/vacuum_$(date +%Y%m%d).log"

echo "=== VACUUM 清理开始 $(date) ===" | tee -a "$LOG_FILE"

# 只清理死元组较多的表
psql -d "$DB_NAME" <<EOF | tee -a "$LOG_FILE"
-- 清理死元组
VACUUM (VERBOSE, ANALYZE) skills;
VACUUM (VERBOSE, ANALYZE) users;
VACUUM (VERBOSE, ANALYZE) orders;
VACUUM (VERBOSE, ANALYZE) point_transactions;
VACUUM (VERBOSE, ANALYZE) review_queues;

-- 完整清理（每月执行一次）
-- VACUUM FULL (VERBOSE) large_table;
EOF

echo "=== VACUUM 清理完成 $(date) ===" | tee -a "$LOG_FILE"
```

### 5.2 统计信息更新脚本

**文件**: `scripts/update_statistics.sh`

```bash
#!/bin/bash
# 统计信息更新脚本

set -e

DB_NAME="${DB_NAME:-sillymd}"

echo "=== 更新统计信息 $(date) ==="

# 更新所有表的统计信息
psql -d "$DB_NAME" <<EOF
-- 更新数据库级统计
ANALYZE;

-- 更新表级统计
ANALYZE skills;
ANALYZE users;
ANALYZE teams;
ANALYZE orders;
ANALYZE licenses;
ANALYZE point_transactions;
ANALYZE review_queues;

-- 更新扩展统计
ANALYZE pg_stat_user_indexes;
ANALYZE pg_stat_user_tables;
EOF

echo "=== 统计信息更新完成 ==="
```

### 5.3 索引重建脚本

**文件**: `scripts/rebuild_indexes.sh`

```bash
#!/bin/bash
# 索引重建脚本

set -e

DB_NAME="${DB_NAME:-sillymd}"

echo "=== 索引重建 $(date) ==="

psql -d "$DB_NAME" <<EOF
-- 并发重建索引（不锁表）
REINDEX INDEX CONCURRENTLY idx_skills_category_status;
REINDEX INDEX CONCURRENTLY idx_skills_author_status;
REINDEX INDEX CONCURRENTLY idx_orders_user_created;
REINDEX INDEX CONCURRENTLY idx_licenses_user_status;
REINDEX INDEX CONCURRENTLY idx_review_queues_status_priority;
EOF

echo "=== 索引重建完成 ==="
```

---

## 六、性能基准测试

### 6.1 基准查询

```sql
-- 1. Skills 列表查询（基准）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM skills
WHERE category = 'tech' AND status = 'approved'
ORDER BY created_at DESC
LIMIT 20;

-- 预期结果：Index Scan, < 5ms

-- 2. 用户授权查询（基准）
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM licenses
WHERE user_id = 12345
  AND status = 'active'
  AND expires_at > CURRENT_TIMESTAMP;

-- 预期结果：Index Scan, < 3ms

-- 3. 团队成员查询（基准）
EXPLAIN (ANALYZE, BUFFERS)
SELECT u.* FROM users u
JOIN team_members tm ON u.id = tm.user_id
WHERE tm.team_id = 100
ORDER BY tm.joined_at;

-- 预期结果：Nested Loop with Index, < 10ms
```

### 6.2 压力测试

```bash
# 使用 pgbench 进行压力测试

# 初始化测试数据
pgbench -i -s 100 sillymd

# 运行基准测试（10 个客户端，持续 5 分钟）
pgbench -c 10 -T 300 -p sillymd > benchmark_$(date +%Y%m%d).log

# 分析结果
pgbench -R benchmark_$(date +%Y%m%d).log
```

---

## 七、故障处理手册

### 7.1 常见问题处理

#### 问题 1: 连接数耗尽

```sql
-- 1. 查看当前连接
SELECT
    usename,
    application_name,
    client_addr,
    state,
    COUNT(*)
FROM pg_stat_activity
GROUP BY usename, application_name, client_addr, state
ORDER BY COUNT DESC;

-- 2. 终止长时间运行的查询
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
    AND now() - query_start > INTERVAL '1 hour';

-- 3. 增加 max_connections（需要重启）
ALTER SYSTEM SET max_connections = 200;
```

#### 问题 2: 查询性能突然下降

```sql
-- 1. 检查锁等待
SELECT * FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

-- 2. 检查表膨胀
SELECT * FROM check_table_bloat();

-- 3. 更新统计信息
ANALYZE;

-- 4. 清理表
VACUUM ANALYZE table_name;
```

#### 问题 3: 磁盘空间不足

```bash
# 1. 检查空间使用
df -h /var/lib/postgresql

# 2. 清理 WAL 文件
pg_archivecleanup -d /var/lib/postgresql/wal

# 3. 清理旧备份
pg_probackup delete --expire-before="7 days"

# 4. 清理表空间
VACUUM FULL table_name;
```

---

## 八、监控仪表盘配置

### 8.1 Grafana 仪表盘配置

```json
{
  "dashboard": {
    "title": "SillyMD PostgreSQL Monitoring",
    "panels": [
      {
        "title": "连接数监控",
        "targets": [
          {
            "expr": "pg_stat_activity_count{datname=\"sillymd\"}",
            "legendFormat": "{{ state }}"
          }
        ]
      },
      {
        "title": "查询性能",
        "targets": [
          {
            "expr": "rate(pg_stat_statements_calls[5m])",
            "legendFormat": "{{ query }}"
          }
        ]
      },
      {
        "title": "表大小趋势",
        "targets": [
          {
            "expr": "pg_relation_size_bytes / 1024 / 1024 / 1024",
            "legendFormat": "{{ tablename }}"
          }
        ]
      },
      {
        "title": "复制延迟",
        "targets": [
          {
            "expr": "pg_stat_replication_lag_seconds",
            "legendFormat": "{{ application_name }}"
          }
        ]
      }
    ]
  }
}
```

---

**文档版本**: v1.0 | **最后更新**: 2026-02-03
**维护人**: 数据库运维团队
**审核人**: 技术架构组
