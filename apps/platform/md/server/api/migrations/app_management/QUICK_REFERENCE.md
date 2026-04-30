# AI Activity Show - 数据库设计快速参考

## 文件清单

### 数据库迁移脚本
```
D:\AIProgram\Claude Code\jcoden\database\migrations\
├── migration_20250206_init_app_management.sql          # 主迁移脚本 (42KB)
├── migration_20250206_init_app_management_rollback.sql # 回滚脚本 (2.4KB)
├── install.bat                                         # Windows 安装脚本
├── install.sh                                          # Linux/Mac 安装脚本
├── README.md                                           # 使用说明 (12KB)
├── DATABASE_DESIGN.md                                  # 详细设计文档 (30KB)
└── QUICK_REFERENCE.md                                  # 本文档
```

---

## 快速开始

### 1. 安装数据库

#### Windows
```cmd
cd D:\AIProgram\Claude Code\jcoden\database\migrations
install.bat
```

#### Linux/Mac
```bash
cd /d/AIProgram/Claude\ Code/jcoden/database/migrations
chmod +x install.sh
./install.sh
```

#### 手动安装
```bash
mysql -h 1.117.68.229 -u jcode -p jc_ai < migration_20250206_init_app_management.sql
```

---

### 2. 验证安装

```sql
-- 检查表是否创建
USE jc_ai;
SHOW TABLES LIKE '%application%';
SHOW TABLES LIKE '%device%';
SHOW TABLES LIKE '%config%';

-- 应该看到以下12个表:
-- applications
-- devices
-- app_configs
-- style_configs
-- question_banks
-- lottery_programs
-- digital_human_configs
-- voice_configs
-- config_push_history
-- device_push_status
-- config_backups
-- config_sync_logs

-- 检查初始数据
SELECT * FROM applications WHERE app_key = 'ai_activity_show';
SELECT * FROM app_configs WHERE app_id = 1;
SELECT COUNT(*) AS style_count FROM style_configs;
```

---

### 3. 回滚数据库

```sql
mysql -h 1.117.68.229 -u jcode -p jc_ai < migration_20250206_init_app_management_rollback.sql
```

---

## 核心表结构

### 表关系概览
```
applications (应用)
  ├── devices (设备)
  ├── app_configs (配置)
  │     ├── style_configs (风格)
  │     ├── question_banks (题库)
  │     ├── lottery_programs (抽奖)
  │     ├── digital_human_configs (数字人)
  │     └── voice_configs (语音)
  ├── config_push_history (推送历史)
  │     └── device_push_status (设备推送状态)
  ├── config_backups (备份)
  └── config_sync_logs (同步日志)
```

---

## 常用查询

### 应用管理
```sql
-- 查看所有应用
SELECT id, app_key, app_name, version, status FROM applications;

-- 查看应用统计
SELECT * FROM v_application_stats;

-- 更新应用版本
UPDATE applications
SET version = '1.0.1', version_code = 2
WHERE app_key = 'ai_activity_show';
```

### 设备管理
```sql
-- 查看所有设备
SELECT d.device_id, d.device_name, a.app_name, d.is_online, d.last_active_time
FROM devices d
JOIN applications a ON d.app_id = a.id
ORDER BY d.last_active_time DESC;

-- 查看在线设备
SELECT * FROM v_active_devices WHERE is_online = 1;

-- 查看离线设备
SELECT device_id, device_name, TIMESTAMPDIFF(MINUTE, last_active_time, NOW()) AS offline_minutes
FROM devices
WHERE is_online = 0 AND status = 1;

-- 注册设备 (使用存储过程)
CALL sp_register_device(
    'device_test_001',
    'ai_activity_show',
    '测试设备',
    'android',
    '{"brand":"Xiaomi","model":"Mi 11","os_version":"11"}'
);

-- 更新设备在线状态
CALL sp_update_device_status('device_test_001', 1);
```

### 配置管理
```sql
-- 查看所有配置
SELECT ac.config_key, ac.config_name, ac.version, ac.is_active, a.app_name
FROM app_configs ac
JOIN applications a ON ac.app_id = a.id
ORDER BY ac.created_at DESC;

-- 查看激活的配置
SELECT * FROM app_configs WHERE is_active = 1;

-- 创建配置备份
CALL sp_backup_config(
    1,                              -- config_id
    '手动备份_20250206',             -- backup_name
    'manual',                       -- backup_type
    'admin'                         -- created_by
);

-- 查看备份列表
SELECT * FROM config_backups ORDER BY created_at DESC;
```

### 推送管理
```sql
-- 查看推送历史
SELECT * FROM v_push_summary LIMIT 20;

-- 查看失败的推送
SELECT * FROM config_push_history WHERE push_status = 'failed';

-- 查看推送详情
SELECT
    ph.push_status,
    ph.total_targets,
    ph.success_count,
    ph.failed_count,
    ph.progress,
    COUNT(dps.id) AS device_count
FROM config_push_history ph
LEFT JOIN device_push_status dps ON ph.id = dps.push_history_id
WHERE ph.id = 1
GROUP BY ph.id;
```

### 数据统计
```sql
-- 应用统计
SELECT
    a.app_name,
    COUNT(DISTINCT d.id) AS total_devices,
    COUNT(DISTINCT CASE WHEN d.is_online = 1 THEN d.id END) AS online_devices,
    COUNT(DISTINCT ac.id) AS total_configs
FROM applications a
LEFT JOIN devices d ON a.id = d.app_id AND d.status = 1
LEFT JOIN app_configs ac ON a.id = ac.app_id AND ac.status = 1
GROUP BY a.id;

-- 配置类型统计
SELECT
    config_key,
    COUNT(*) AS config_count,
    COUNT(CASE WHEN is_active = 1 THEN 1 END) AS active_count
FROM app_configs
GROUP BY config_key;

-- 推送成功率统计
SELECT
    push_status,
    COUNT(*) AS count,
    AVG(success_count * 100.0 / total_targets) AS avg_success_rate
FROM config_push_history
WHERE total_targets > 0
GROUP BY push_status;
```

---

## 索引维护

### 分析表
```sql
ANALYZE TABLE applications;
ANALYZE TABLE devices;
ANALYZE TABLE app_configs;
ANALYZE TABLE config_push_history;
```

### 优化表
```sql
OPTIMIZE TABLE applications;
OPTIMIZE TABLE devices;
OPTIMIZE TABLE config_sync_logs;
```

### 查看索引使用情况
```sql
-- 查看表的索引
SHOW INDEX FROM applications;
SHOW INDEX FROM devices;

-- 查看索引统计
SELECT
    table_name,
    index_name,
    cardinality,
    index_type
FROM information_schema.statistics
WHERE table_schema = 'jc_ai'
ORDER BY table_name, index_name;
```

---

## 数据清理

### 清理过期备份
```sql
-- 删除过期的配置备份
DELETE FROM config_backups
WHERE expires_at < NOW();

-- 删除30天前的备份
DELETE FROM config_backups
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### 清理旧日志
```sql
-- 删除3个月前的同步日志
DELETE FROM config_sync_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);

-- 删除6个月前的推送历史
DELETE FROM config_push_history
WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH)
  AND push_status = 'completed';
```

### 清理离线设备
```sql
-- 查看长时间未活跃的设备
SELECT device_id, device_name, last_active_time
FROM devices
WHERE last_active_time < DATE_SUB(NOW(), INTERVAL 90 DAY)
  AND status = 1;

-- 标记为离线
UPDATE devices
SET is_online = 0
WHERE last_active_time < DATE_SUB(NOW(), INTERVAL 5 MINUTE)
  AND is_online = 1;
```

---

## 常见问题

### 1. 外键约束错误
```
ERROR 1452: Cannot add or update a child row:
a foreign key constraint fails
```

**解决**: 检查父记录是否存在
```sql
-- 检查应用是否存在
SELECT * FROM applications WHERE id = 1;

-- 检查设备是否存在
SELECT * FROM devices WHERE device_id = 'xxx';
```

### 2. 字符编码问题
```
ERROR 1366: Incorrect string value
```

**解决**: 确保使用 utf8mb4
```sql
-- 检查表字符集
SHOW CREATE TABLE applications;

-- 修改表字符集
ALTER TABLE applications CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 连接超时
```
ERROR 2006: MySQL server has gone away
```

**解决**: 增加超时时间
```sql
SET GLOBAL wait_timeout = 28800;
SET GLOBAL interactive_timeout = 28800;
```

---

## 性能调优

### 慢查询分析
```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log%';
```

### 连接池配置
```python
# Flask SQLAlchemy 配置
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_MAX_OVERFLOW = 10
```

### 查询缓存
```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# 缓存应用配置
@cache.cached(timeout=300, key_prefix='app_config')
def get_app_config(app_key):
    return Application.query.filter_by(app_key=app_key).first()
```

---

## 数据导出/导入

### 导出数据
```bash
# 导出整个数据库
mysqldump -u jcode -p jc_ai > jc_ai_backup_$(date +%Y%m%d).sql

# 导出特定表
mysqldump -u jcode -p jc_ai applications devices > tables_backup.sql

# 导出数据结构
mysqldump -u jcode -p --no-data jc_ai > schema_backup.sql
```

### 导入数据
```bash
# 导入数据库
mysql -u jcode -p jc_ai < jc_ai_backup_20250206.sql

# 导入特定表
mysql -u jcode -p jc_ai < tables_backup.sql
```

---

## 监控命令

### 数据库状态
```sql
-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';

-- 查看表大小
SELECT
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'jc_ai'
ORDER BY size_mb DESC;

-- 查看InnoDB状态
SHOW ENGINE INNODB STATUS\G
```

### 实时监控
```bash
# 实时查看慢查询
mysqldumpslow -s t -t 10 /var/log/mysql/slow-query.log

# 实时查看连接
watch -n 1 'mysql -e "SHOW PROCESSLIST"'
```

---

## 联系方式

- **文档位置**: D:\AIProgram\Claude Code\jcoden\database\migrations\
- **创建日期**: 2026-02-06
- **版本**: 1.0.0

---

## 附录

### 字段类型说明
- **BIGINT UNSIGNED**: 大整数主键，支持最大值 18,446,744,073,709,551,615
- **INT UNSIGNED**: 整数，支持最大值 4,294,967,295
- **TINYINT(1)**: 布尔值，0 或 1
- **VARCHAR(n)**: 变长字符串，最大长度 n
- **TEXT**: 长文本，最大 65,535 字节
- **LONGTEXT**: 超长文本，最大 4GB
- **JSON**: JSON 数据类型，支持 JSON 函数
- **DATETIME**: 日期时间，范围 '1000-01-01' 到 '9999-12-31'

### 索引类型说明
- **PRIMARY KEY**: 主键索引，唯一且非空
- **UNIQUE KEY**: 唯一索引，值唯一但可为空
- **INDEX**: 普通索引，加速查询
- **FULLTEXT**: 全文索引，支持全文搜索
- **SPATIAL**: 空间索引，用于地理数据

### 外键约束说明
- **CASCADE**: 级联删除/更新
- **SET NULL**: 设为 NULL
- **RESTRICT**: 禁止删除/更新
- **NO ACTION**: 不执行操作（默认）
- **SET DEFAULT**: 设为默认值
