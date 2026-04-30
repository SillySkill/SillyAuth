# AI Activity Show - Application Management Database

## 概述

本数据库架构为 AI 活动秀应用提供完整的应用管理功能，支持多应用管理、设备注册、配置版本控制、配置推送和备份等功能。

## 数据库表结构

### 核心表

#### 1. applications (应用列表)
存储应用程序的基本信息和元数据。

**主要字段:**
- `app_key`: 应用唯一标识 (如: ai_activity_show)
- `app_name`: 应用显示名称
- `package_name`: Android 包名
- `version`: 当前版本
- `status`: 状态 (0=禁用, 1=启用, 2=维护中)

**索引:**
- PRIMARY KEY: `id`
- UNIQUE KEY: `app_key`
- INDEX: `status`, `category`, `created_at`

---

#### 2. devices (设备管理)
注册和管理客户端设备信息。

**主要字段:**
- `device_id`: 设备唯一标识
- `app_id`: 关联应用 ID
- `device_type`: 设备类型 (android, ios, web)
- `device_brand`: 设备品牌
- `is_online`: 在线状态
- `last_active_time`: 最后活跃时间

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE

**索引:**
- PRIMARY KEY: `id`
- UNIQUE KEY: `device_id`
- INDEX: `app_id`, `device_type`, `is_online`, `last_active_time`

---

#### 3. app_configs (应用配置版本)
存储应用的配置版本信息。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_key`: 配置键 (如: global, quiz, lottery)
- `version`: 配置版本号
- `config_data`: 配置数据 (JSON 字符串)
- `is_active`: 是否为激活版本

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE

**唯一约束:**
- UNIQUE KEY: `(app_id, config_key, version)`

**索引:**
- INDEX: `app_id`, `config_key`, `version`, `is_active`

---

#### 4. style_configs (AI 风格配置)
管理 AI 风格转换的配置。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 父配置 ID
- `style_id`: 风格唯一标识
- `style_name`: 风格名称
- `style_config`: 风格配置数据
- `is_premium`: 是否为高级风格

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE SET NULL

---

#### 5. question_banks (题库管理)
管理知识问答的题库。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 父配置 ID
- `bank_id`: 题库唯一标识
- `bank_name`: 题库名称
- `category`: 题库分类
- `difficulty`: 难度等级
- `questions_data`: 问题数据 (JSON)
- `total_questions`: 总题数

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE SET NULL

---

#### 6. lottery_programs (抽奖程序)
管理抽奖程序的配置。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 父配置 ID
- `program_id`: 程序唯一标识
- `program_name`: 程序名称
- `program_type`: 程序类型 (lucky, wheel, box)
- `program_config`: 程序配置数据
- `prizes_config`: 奖品配置

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE SET NULL

---

#### 7. digital_human_configs (数字人配置)
管理数字人的配置。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 父配置 ID
- `human_id`: 数字人唯一标识
- `human_name`: 数字人名称
- `model_type`: 模型类型 (gif, video, 3d)
- `actions_config`: 动作配置
- `modules`: 启用的模块列表

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE SET NULL

---

#### 8. voice_configs (语音配置)
管理语音识别和合成的配置。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 父配置 ID
- `config_key`: 配置键 (asr, tts, voice_command)
- `provider`: 服务提供商 (tencent, ali, iflytek)
- `voice_config`: 语音配置数据
- `voice_type`: 语音类型
- `speed`, `pitch`, `volume`: 语音参数

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE SET NULL

---

#### 9. config_push_history (推送历史)
记录配置推送的历史记录。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 配置 ID
- `push_type`: 推送类型 (full, incremental)
- `target_type`: 目标类型 (all, device, group)
- `push_status`: 推送状态
- `total_targets`: 总目标数
- `success_count`, `failed_count`: 成功/失败计数

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE CASCADE

---

#### 10. device_push_status (设备推送状态)
跟踪每个设备的推送状态。

**主要字段:**
- `push_history_id`: 推送历史 ID
- `device_id`: 设备 ID
- `push_status`: 推送状态
- `error_code`, `error_message`: 错误信息
- `delivered_at`: 送达时间
- `confirmed_at`: 确认时间

**外键:**
- `push_history_id` -> `config_push_history(id)` ON DELETE CASCADE
- `device_id` -> `devices(id)` ON DELETE CASCADE

---

#### 11. config_backups (配置备份)
配置备份的历史记录。

**主要字段:**
- `app_id`: 关联应用 ID
- `config_id`: 原配置 ID
- `backup_name`: 备份名称
- `backup_type`: 备份类型 (manual, auto, before_push)
- `config_data`: 配置数据
- `file_size`: 文件大小
- `expires_at`: 过期时间

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `config_id` -> `app_configs(id)` ON DELETE CASCADE

---

#### 12. config_sync_logs (配置同步日志)
记录配置同步的日志。

**主要字段:**
- `app_id`: 关联应用 ID
- `device_id`: 设备 ID
- `sync_type`: 同步类型 (pull, push, check_update)
- `config_key`: 配置键
- `sync_status`: 同步状态
- `data_size`: 数据大小
- `duration`: 耗时 (毫秒)

**外键:**
- `app_id` -> `applications(id)` ON DELETE CASCADE
- `device_id` -> `devices(id)` ON DELETE SET NULL

---

## 数据库视图

### v_application_stats (应用统计)
聚合应用的统计信息，包括设备数量和配置更新时间。

```sql
SELECT * FROM v_application_stats;
```

**字段:**
- app_id, app_key, app_name
- total_devices: 总设备数
- online_devices: 在线设备数
- total_configs: 总配置数
- last_config_update: 最后配置更新时间

---

### v_active_devices (活跃设备)
显示所有活跃设备的最新信息。

```sql
SELECT * FROM v_active_devices;
```

**字段:**
- 设备基本信息
- 应用名称
- 在线状态
- 未活跃时长 (分钟)

---

### v_push_summary (推送摘要)
汇总最近的推送历史。

```sql
SELECT * FROM v_push_summary;
```

**字段:**
- 推送基本信息
- 应用和配置名称
- 推送统计
- 执行时长

---

## 存储过程

### sp_register_device
注册或更新设备信息。

```sql
CALL sp_register_device(
    'device_123',           -- p_device_id
    'ai_activity_show',     -- p_app_key
    '我的设备',              -- p_device_name
    'android',              -- p_device_type
    '{"brand":"Xiaomi","model":"Mi 11","os_version":"11"}' -- p_device_info
);
```

---

### sp_backup_config
创建配置备份。

```sql
CALL sp_backup_config(
    1,                      -- p_config_id
    '手动备份_20250206',     -- p_backup_name
    'manual',               -- p_backup_type
    'admin'                 -- p_created_by
);
```

---

### sp_update_device_status
更新设备在线状态。

```sql
CALL sp_update_device_status(
    'device_123',           -- p_device_id
    1                       -- p_is_online (1=在线, 0=离线)
);
```

---

## 触发器

### tr_devices_inactive_check
自动更新设备为离线状态。

当设备最后活跃时间超过 5 分钟时，自动将其标记为离线。

---

## 使用说明

### 1. 执行迁移脚本

```bash
# 登录 MySQL
mysql -u root -p

# 选择数据库
USE jc_ai;

# 执行迁移脚本
SOURCE D:/AIProgram/Claude Code/jcoden/database/migrations/migration_20250206_init_app_management.sql;
```

### 2. 回滚数据库

```bash
# 执行回滚脚本
SOURCE D:/AIProgram/Claude Code/jcoden/database/migrations/migration_20250206_init_app_management_rollback.sql;
```

### 3. 验证安装

```sql
-- 检查表是否创建成功
SHOW TABLES LIKE '%applications%';
SHOW TABLES LIKE '%devices%';
SHOW TABLES LIKE '%config%';

-- 检查初始数据
SELECT * FROM applications WHERE app_key = 'ai_activity_show';
SELECT * FROM devices LIMIT 10;
```

---

## 初始数据

迁移脚本会自动插入以下初始数据：

1. **应用**: AI 活动秀 (ai_activity_show)
2. **配置**: 全局配置、风格配置、题库配置等
3. **风格**: 人像基础、卡通风格、油画风格
4. **题库**: 综合知识库、科技知识
5. **抽奖程序**: 幸运大抽奖、欢乐转盘
6. **数字人**: AI 助手
7. **语音配置**: ASR 和 TTS 配置

---

## 外键关系图

```
applications (1)
    ├── (N) devices
    ├── (N) app_configs
    │     ├── (N) style_configs
    │     ├── (N) question_banks
    │     ├── (N) lottery_programs
    │     ├── (N) digital_human_configs
    │     └── (N) voice_configs
    ├── (N) config_push_history
    │     └── (N) device_push_status
    ├── (N) config_backups
    └── (N) config_sync_logs
```

---

## 性能优化建议

### 1. 索引优化
所有查询频繁的字段都已添加索引，包括：
- 外键字段
- 状态字段
- 时间字段
- 唯一标识字段

### 2. 分区策略
对于大数据量表，建议按时间分区：
- `config_sync_logs`: 按月分区
- `config_push_history`: 按月分区

### 3. 数据归档
定期归档历史数据：
- 推送历史保留 6 个月
- 同步日志保留 3 个月
- 配置备份根据 `expires_at` 自动清理

---

## 安全建议

### 1. 敏感数据加密
- `voice_configs.app_secret` 应使用加密存储
- 考虑使用 AES-256 加密算法

### 2. 权限控制
```sql
-- 创建只读用户
CREATE USER 'app_readonly'@'%' IDENTIFIED BY 'password';
GRANT SELECT ON jc_ai.* TO 'app_readonly'@'%';

-- 创建应用用户
CREATE USER 'app_user'@'%' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE ON jc_ai.* TO 'app_user'@'%';
```

### 3. 备份策略
- 每日全量备份
- 每小时增量备份
- 保留 30 天备份历史

---

## 维护脚本

### 清理过期备份
```sql
DELETE FROM config_backups
WHERE expires_at < NOW();
```

### 清理旧日志
```sql
DELETE FROM config_sync_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

### 更新设备在线状态
```sql
UPDATE devices
SET is_online = 0
WHERE last_active_time < DATE_SUB(NOW(), INTERVAL 5 MINUTE)
  AND is_online = 1;
```

---

## 故障排查

### 常见问题

1. **外键约束失败**
   - 检查父子表的记录是否存在
   - 确认 `FOREIGN_KEY_CHECKS` 已启用

2. **字符编码问题**
   - 确保数据库、表、连接都使用 `utf8mb4`
   - 检查 `SQLALCHEMY_ENCODING` 配置

3. **存储过程执行失败**
   - 检查分隔符设置 (`DELIMITER $$`)
   - 确认参数类型和数量

---

## 更新日志

### 2026-02-06
- 初始版本创建
- 添加 12 个核心表
- 创建 3 个视图
- 实现 3 个存储过程
- 添加触发器自动更新设备状态

---

## 联系方式

如有问题或建议，请联系：
- 开发者: Database Design Expert
- 邮箱: [待补充]
- 项目地址: D:\AIProgram\Claude Code\jcoden

---

## 许可证

本数据库架构遵循项目整体许可证。
