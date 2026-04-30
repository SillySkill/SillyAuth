# AI Activity Show - Application Management Database Design Document

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档标题 | AI 活动秀应用管理数据库设计文档 |
| 版本 | 1.0.0 |
| 创建日期 | 2026-02-06 |
| 作者 | Database Design Expert |
| 数据库 | MySQL 8.0+ |
| 字符集 | utf8mb4 |
| 排序规则 | utf8mb4_unicode_ci |

---

## 目录

1. [设计概述](#1-设计概述)
2. [ER 图](#2-er-图)
3. [表结构详细设计](#3-表结构详细设计)
4. [索引设计](#4-索引设计)
5. [外键约束](#5-外键约束)
6. [视图设计](#6-视图设计)
7. [存储过程](#7-存储过程)
8. [触发器](#8-触发器)
9. [数据字典](#9-数据字典)
10. [性能优化](#10-性能优化)

---

## 1. 设计概述

### 1.1 设计目标

本数据库设计旨在为 AI 活动秀应用提供完整的应用管理功能，支持：

- **多应用管理**: 支持多个应用的统一管理
- **设备管理**: 设备注册、状态跟踪、远程控制
- **配置版本控制**: 配置版本管理、历史回溯
- **配置推送**: WebSocket/HTTP 实时推送配置更新
- **配置备份**: 自动和手动备份功能
- **审计追踪**: 完整的操作日志和同步日志

### 1.2 设计原则

1. **规范化设计**: 遵循第三范式 (3NF)，减少数据冗余
2. **性能优先**: 合理的索引设计，优化查询性能
3. **可扩展性**: 支持多应用、多设备、多配置类型
4. **数据完整性**: 外键约束确保数据一致性
5. **审计追踪**: 时间戳记录创建和更新时间

### 1.3 命名规范

- **表名**: 小写，下划线分隔，复数形式 (如: `applications`, `devices`)
- **字段名**: 小写，下划线分隔 (如: `app_id`, `created_at`)
- **主键**: `id` (BIGINT/INT UNSIGNED AUTO_INCREMENT)
- **外键**: `{关联表}_id` (如: `app_id`, `device_id`)
- **时间戳**: `{动作}_at` (如: `created_at`, `updated_at`)
- **布尔字段**: `is_{状态}` (如: `is_active`, `is_online`)
- **状态字段**: `status` (使用整数枚举)

### 1.4 通用字段规范

所有表都应包含以下基础字段：

```sql
id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
status          TINYINT(1) NOT NULL DEFAULT 1  -- 0=disabled, 1=enabled
created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
created_by      VARCHAR(100) DEFAULT NULL       -- 可选，记录创建人
```

---

## 2. ER 图

```
┌─────────────────────┐
│   applications      │
│─────────────────────│
│ id (PK)            │
│ app_key (UQ)       │
│ app_name           │
│ version            │
│ status             │
│ ...                │
└─────────┬───────────┘
          │
          ├──────────────────────────────────────────┐
          │                                          │
┌─────────▼───────────┐                  ┌──────────▼──────────┐
│      devices        │                  │    app_configs      │
│─────────────────────│                  │─────────────────────│
│ id (PK)            │                  │ id (PK)            │
│ device_id (UQ)     │                  │ app_id (FK)        │
│ app_id (FK)        │                  │ config_key (UQ)    │
│ is_online          │                  │ version            │
│ ...                │                  │ config_data        │
└─────────┬───────────┘                  │ ...                │
          │                              └─────────┬──────────┘
          │                                        │
          │              ┌─────────────────────────┼────────────────────┐
          │              │                         │                    │
┌─────────▼───────────┐  ┌──────────▼──────┐  ┌───▼───────┐  ┌──────▼──────────┐
│ config_push_history│  │ style_configs   │  │question_  │  │lottery_programs │
│────────────────────│  │─────────────────│  │banks      │  │─────────────────│
│ id (PK)           │  │ id (PK)         │  │───────────│  │ id (PK)         │
│ app_id (FK)       │  │ app_id (FK)     │  │ id (PK)   │  │ app_id (FK)     │
│ config_id (FK)    │  │ config_id (FK)  │  │ app_id..  │  │ config_id (FK)  │
│ push_status       │  │ style_id (UQ)   │  │ bank_id.. │  │ program_id (UQ) │
│ ...               │  │ ...             │  │ ...       │  │ ...             │
└─────────┬───────────┘  └─────────────────┘  └───────────┘  └─────────────────┘
          │
┌─────────▼──────────────┐
│ device_push_status     │
│────────────────────────│
│ id (PK)               │
│ push_history_id (FK)  │
│ device_id (FK)        │
│ push_status           │
│ ...                   │
└────────────────────────┘

┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ config_backups  │  │ config_sync_logs │  │voice_configs    │
│─────────────────│  │──────────────────│  │─────────────────│
│ id (PK)         │  │ id (PK)          │  │ id (PK)         │
│ app_id (FK)     │  │ app_id (FK)      │  │ app_id (FK)     │
│ config_id (FK)  │  │ device_id (FK)   │  │ config_id (FK)  │
│ backup_type     │  │ sync_type        │  │ config_key (UQ) │
│ ...             │  │ ...              │  │ ...             │
└─────────────────┘  └──────────────────┘  └─────────────────┘

┌──────────────────────┐
│digital_human_configs │
│──────────────────────│
│ id (PK)              │
│ app_id (FK)          │
│ config_id (FK)       │
│ human_id (UQ)        │
│ ...                  │
└──────────────────────┘
```

---

## 3. 表结构详细设计

### 3.1 applications - 应用列表表

**表说明**: 存储应用程序的基本信息和元数据。

| 字段名 | 类型 | 长度 | 允许NULL | 默认值 | 键 | 说明 |
|--------|------|------|---------|--------|-----|------|
| id | INT | UNSIGNED | NO | AUTO_INCREMENT | PK | 应用ID |
| app_key | VARCHAR | 64 | NO | - | UQ | 应用唯一标识 |
| app_name | VARCHAR | 100 | NO | - | IDX | 应用显示名称 |
| app_name_en | VARCHAR | 100 | YES | NULL | - | 英文名称 |
| package_name | VARCHAR | 200 | YES | NULL | - | Android包名 |
| version | VARCHAR | 20 | NO | '1.0.0' | - | 当前版本 |
| version_code | INT | - | NO | 1 | - | 版本号 |
| min_sdk_version | INT | - | NO | 24 | - | 最低SDK版本 |
| target_sdk_version | INT | - | NO | 34 | - | 目标SDK版本 |
| icon_url | VARCHAR | 500 | YES | NULL | - | 图标URL |
| description | TEXT | - | YES | NULL | - | 应用描述 |
| description_en | TEXT | - | YES | NULL | - | 英文描述 |
| features | JSON | - | YES | NULL | - | 功能列表 |
| screenshots | JSON | - | YES | NULL | - | 截图URL数组 |
| download_url | VARCHAR | 500 | YES | NULL | - | 下载地址 |
| download_count | BIGINT | UNSIGNED | NO | 0 | - | 下载次数 |
| category | VARCHAR | 50 | NO | 'entertainment' | IDX | 应用分类 |
| tags | JSON | - | YES | NULL | - | 标签数组 |
| developer | VARCHAR | 100 | NO | 'jCoding' | - | 开发者 |
| website | VARCHAR | 200 | YES | NULL | - | 官方网站 |
| contact_email | VARCHAR | 100 | YES | NULL | - | 联系邮箱 |
| status | TINYINT | 1 | NO | 1 | IDX | 状态 |
| is_default | TINYINT | 1 | NO | 0 | - | 是否默认 |
| sort_order | INT | - | NO | 0 | - | 排序 |
| created_at | DATETIME | - | NO | CURRENT_TIMESTAMP | IDX | 创建时间 |
| updated_at | DATETIME | - | NO | CURRENT_TIMESTAMP | IDX | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE KEY: `app_key`
- INDEX: `status`, `category`, `created_at`

**约束**:
- `app_key` 全局唯一
- `status` IN (0, 1, 2) - 0=禁用, 1=启用, 2=维护中

---

### 3.2 devices - 设备管理表

**表说明**: 注册和管理客户端设备信息。

| 字段名 | 类型 | 长度 | 允许NULL | 默认值 | 键 | 说明 |
|--------|------|------|---------|--------|-----|------|
| id | BIGINT | UNSIGNED | NO | AUTO_INCREMENT | PK | 设备ID |
| device_id | VARCHAR | 100 | NO | - | UQ | 设备唯一标识 |
| device_sn | VARCHAR | 100 | YES | NULL | - | 设备序列号 |
| device_name | VARCHAR | 100 | YES | NULL | - | 设备名称 |
| app_id | INT | UNSIGNED | NO | - | FK, IDX | 应用ID |
| device_type | VARCHAR | 20 | NO | 'android' | IDX | 设备类型 |
| device_brand | VARCHAR | 50 | YES | NULL | - | 设备品牌 |
| device_model | VARCHAR | 100 | YES | NULL | - | 设备型号 |
| os_version | VARCHAR | 50 | YES | NULL | - | 系统版本 |
| app_version | VARCHAR | 20 | YES | NULL | - | 应用版本 |
| screen_resolution | VARCHAR | 20 | YES | NULL | - | 屏幕分辨率 |
| network_type | VARCHAR | 20 | YES | NULL | - | 网络类型 |
| ip_address | VARCHAR | 50 | YES | NULL | - | IP地址 |
| location | JSON | - | YES | NULL | - | 位置信息 |
| push_token | VARCHAR | 500 | YES | NULL | - | 推送令牌 |
| is_online | TINYINT | 1 | NO | 0 | IDX | 在线状态 |
| last_active_time | DATETIME | - | YES | NULL | IDX | 最后活跃时间 |
| registration_time | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 注册时间 |
| status | TINYINT | 1 | NO | 1 | IDX | 状态 |
| notes | TEXT | - | YES | NULL | - | 备注 |
| created_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE KEY: `device_id`
- FOREIGN KEY: `app_id` -> `applications(id)`
- INDEX: `app_id`, `device_type`, `is_online`, `status`, `last_active_time`
- COMPOSITE INDEX: `app_id, device_id`

**约束**:
- `device_type` IN ('android', 'ios', 'web')
- `is_online` IN (0, 1)
- `status` IN (0, 1, 2) - 0=禁用, 1=活跃, 2=封禁

---

### 3.3 app_configs - 应用配置版本表

**表说明**: 存储应用的配置版本信息。

| 字段名 | 类型 | 长度 | 允许NULL | 默认值 | 键 | 说明 |
|--------|------|------|---------|--------|-----|------|
| id | BIGINT | UNSIGNED | NO | AUTO_INCREMENT | PK | 配置ID |
| app_id | INT | UNSIGNED | NO | - | FK, IDX | 应用ID |
| config_key | VARCHAR | 100 | NO | - | IDX | 配置键 |
| config_name | VARCHAR | 100 | NO | - | - | 配置名称 |
| version | VARCHAR | 20 | NO | - | IDX | 版本号 |
| config_type | VARCHAR | 50 | NO | 'json' | - | 配置类型 |
| config_path | VARCHAR | 200 | YES | NULL | - | 配置路径 |
| config_data | LONGTEXT | - | NO | - | - | 配置数据 |
| config_schema | JSON | - | YES | NULL | - | 配置架构 |
| description | TEXT | - | YES | NULL | - | 描述 |
| change_log | TEXT | - | YES | NULL | - | 变更日志 |
| is_active | TINYINT | 1 | NO | 0 | IDX | 是否激活 |
| is_default | TINYINT | 1 | NO | 0 | - | 是否默认 |
| file_size | INT | UNSIGNED | NO | 0 | - | 文件大小 |
| checksum | VARCHAR | 64 | YES | NULL | - | MD5校验和 |
| created_by | VARCHAR | 100 | NO | 'system' | - | 创建者 |
| status | TINYINT | 1 | NO | 1 | IDX | 状态 |
| created_at | DATETIME | - | NO | CURRENT_TIMESTAMP | IDX | 创建时间 |
| updated_at | DATETIME | - | NO | CURRENT_TIMESTAMP | IDX | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `app_id` -> `applications(id)`
- UNIQUE KEY: `app_id, config_key, version`
- INDEX: `app_id`, `config_key`, `version`, `is_active`, `status`, `created_at`

**约束**:
- `config_type` IN ('json', 'xml', 'yaml')
- `status` IN (0, 1, 2) - 0=草稿, 1=已发布, 2=已归档

---

### 3.4 style_configs - AI风格配置表

**表说明**: 管理AI风格转换的配置。

| 字段名 | 类型 | 长度 | 允许NULL | 默认值 | 键 | 说明 |
|--------|------|------|---------|--------|-----|------|
| id | BIGINT | UNSIGNED | NO | AUTO_INCREMENT | PK | 风格ID |
| app_id | INT | UNSIGNED | NO | - | FK, IDX | 应用ID |
| config_id | BIGINT | UNSIGNED | YES | NULL | FK | 配置ID |
| style_id | VARCHAR | 64 | NO | - | UQ, IDX | 风格ID |
| style_name | VARCHAR | 100 | NO | - | - | 风格名称 |
| style_name_en | VARCHAR | 100 | YES | NULL | - | 英文名称 |
| category | VARCHAR | 50 | YES | NULL | IDX | 风格分类 |
| thumbnail_url | VARCHAR | 500 | YES | NULL | - | 缩略图 |
| sample_image_url | VARCHAR | 500 | YES | NULL | - | 示例图 |
| style_config | JSON | - | NO | - | - | 风格配置 |
| api_params | JSON | - | YES | NULL | - | API参数 |
| processing_time | INT | - | YES | NULL | - | 处理时间(秒) |
| quality_score | DECIMAL | 3,2 | YES | NULL | - | 质量分数 |
| is_premium | TINYINT | 1 | NO | 0 | IDX | 是否高级 |
| credits_required | INT | - | NO | 0 | - | 所需积分 |
| usage_count | BIGINT | UNSIGNED | NO | 0 | - | 使用次数 |
| like_count | INT | UNSIGNED | NO | 0 | - | 点赞数 |
| sort_order | INT | - | NO | 0 | - | 排序 |
| status | TINYINT | 1 | NO | 1 | IDX | 状态 |
| created_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `app_id` -> `applications(id)`
- FOREIGN KEY: `config_id` -> `app_configs(id)`
- UNIQUE KEY: `app_id, style_id`
- INDEX: `app_id`, `style_id`, `category`, `is_premium`, `status`, `sort_order`

---

### 3.5 question_banks - 题库管理表

**表说明**: 管理知识问答的题库。

| 字段名 | 类型 | 长度 | 允许NULL | 默认值 | 键 | 说明 |
|--------|------|------|---------|--------|-----|------|
| id | BIGINT | UNSIGNED | NO | AUTO_INCREMENT | PK | 题库ID |
| app_id | INT | UNSIGNED | NO | - | FK, IDX | 应用ID |
| config_id | BIGINT | UNSIGNED | YES | NULL | FK | 配置ID |
| bank_id | VARCHAR | 64 | NO | - | UQ, IDX | 题库ID |
| bank_name | VARCHAR | 100 | NO | - | - | 题库名称 |
| bank_name_en | VARCHAR | 100 | YES | NULL | - | 英文名称 |
| category | VARCHAR | 50 | YES | NULL | IDX | 题库分类 |
| difficulty | VARCHAR | 20 | NO | 'medium' | IDX | 难度 |
| total_questions | INT | UNSIGNED | NO | 0 | - | 总题数 |
| choice_count | INT | UNSIGNED | NO | 0 | - | 选择题数 |
| judgement_count | INT | UNSIGNED | NO | 0 | - | 判断题数 |
| questions_data | LONGTEXT | - | YES | NULL | - | 题目数据 |
| thumbnail_url | VARCHAR | 500 | YES | NULL | - | 缩略图 |
| description | TEXT | - | YES | NULL | - | 描述 |
| tags | JSON | - | YES | NULL | - | 标签 |
| play_count | BIGINT | UNSIGNED | NO | 0 | - | 游玩次数 |
| avg_score | DECIMAL | 5,2 | YES | NULL | - | 平均分 |
| completion_rate | DECIMAL | 5,2 | YES | NULL | - | 完成率 |
| time_limit | INT | - | YES | NULL | - | 时间限制(秒) |
| passing_score | INT | - | NO | 60 | - | 及格分 |
| is_premium | TINYINT | 1 | NO | 0 | - | 是否高级 |
| sort_order | INT | - | NO | 0 | - | 排序 |
| status | TINYINT | 1 | NO | 1 | IDX | 状态 |
| created_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `app_id` -> `applications(id)`
- FOREIGN KEY: `config_id` -> `app_configs(id)`
- UNIQUE KEY: `app_id, bank_id`
- INDEX: `app_id`, `bank_id`, `category`, `difficulty`, `status`, `sort_order`

---

### 3.6 lottery_programs - 抽奖程序表

**表说明**: 管理抽奖程序的配置。

| 字段名 | 类型 | 长度 | 允许NULL | 默认值 | 键 | 说明 |
|--------|------|------|---------|--------|-----|------|
| id | BIGINT | UNSIGNED | NO | AUTO_INCREMENT | PK | 程序ID |
| app_id | INT | UNSIGNED | NO | - | FK, IDX | 应用ID |
| config_id | BIGINT | UNSIGNED | YES | NULL | FK | 配置ID |
| program_id | VARCHAR | 64 | NO | - | UQ, IDX | 程序ID |
| program_name | VARCHAR | 100 | NO | - | - | 程序名称 |
| program_name_en | VARCHAR | 100 | YES | NULL | - | 英文名称 |
| program_type | VARCHAR | 50 | NO | 'lucky' | IDX | 程序类型 |
| description | TEXT | - | YES | NULL | - | 描述 |
| thumbnail_url | VARCHAR | 500 | YES | NULL | - | 缩略图 |
| background_image_url | VARCHAR | 500 | YES | NULL | - | 背景图 |
| program_config | JSON | - | NO | - | - | 程序配置 |
| prizes_config | JSON | - | YES | NULL | - | 奖品配置 |
| rules | TEXT | - | YES | NULL | - | 规则 |
| background_music | VARCHAR | 500 | YES | NULL | - | 背景音乐 |
| animation_config | JSON | - | YES | NULL | - | 动画配置 |
| draw_count | INT | UNSIGNED | NO | 0 | - | 抽奖次数 |
| win_count | INT | UNSIGNED | NO | 0 | - | 中奖次数 |
| win_rate | DECIMAL | 5,2 | YES | NULL | - | 中奖率 |
| is_premium | TINYINT | 1 | NO | 0 | - | 是否高级 |
| max_participants | INT | - | YES | NULL | - | 最大参与人数 |
| duration | INT | - | YES | NULL | - | 持续时间(秒) |
| cooldown_period | INT | - | YES | NULL | - | 冷却时间(秒) |
| sort_order | INT | - | NO | 0 | - | 排序 |
| status | TINYINT | 1 | NO | 1 | IDX | 状态 |
| created_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NO | CURRENT_TIMESTAMP | - | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `app_id` -> `applications(id)`
- FOREIGN KEY: `config_id` -> `app_configs(id)`
- UNIQUE KEY: `app_id, program_id`
- INDEX: `app_id`, `program_id`, `program_type`, `status`, `sort_order`

---

## 4. 索引设计

### 4.1 索引策略

#### 主键索引
所有表都使用自增 BIGINT UNSIGNED 作为主键，确保插入性能。

#### 唯一索引
- `applications.app_key`: 应用唯一标识
- `devices.device_id`: 设备唯一标识
- `app_configs(app_id, config_key, version)`: 配置版本唯一性
- `style_configs(app_id, style_id)`: 风格ID唯一性
- `question_banks(app_id, bank_id)`: 题库ID唯一性
- `lottery_programs(app_id, program_id)`: 程序ID唯一性

#### 外键索引
所有外键字段都建立索引，优化 JOIN 查询性能。

#### 查询索引
- `status`: 状态过滤查询
- `created_at`, `updated_at`: 时间范围查询
- `is_online`: 在线设备查询
- `category`, `difficulty`: 分类和难度查询

#### 复合索引
- `devices(app_id, device_id)`: 应用设备查询
- `config_push_history(app_id, created_at)`: 应用推送历史查询

### 4.2 索引维护

```sql
-- 分析表
ANALYZE TABLE applications;
ANALYZE TABLE devices;
ANALYZE TABLE app_configs;

-- 优化表
OPTIMIZE TABLE applications;
OPTIMIZE TABLE devices;

-- 检查索引使用情况
SHOW INDEX FROM applications;
```

---

## 5. 外键约束

### 5.1 外键关系

| 子表 | 外键字段 | 父表 | 父表字段 | ON DELETE | ON UPDATE |
|------|---------|------|---------|-----------|-----------|
| devices | app_id | applications | id | CASCADE | CASCADE |
| app_configs | app_id | applications | id | CASCADE | CASCADE |
| style_configs | app_id | applications | id | CASCADE | CASCADE |
| style_configs | config_id | app_configs | id | SET NULL | CASCADE |
| question_banks | app_id | applications | id | CASCADE | CASCADE |
| question_banks | config_id | app_configs | id | SET NULL | CASCADE |
| lottery_programs | app_id | applications | id | CASCADE | CASCADE |
| lottery_programs | config_id | app_configs | id | SET NULL | CASCADE |
| digital_human_configs | app_id | applications | id | CASCADE | CASCADE |
| digital_human_configs | config_id | app_configs | id | SET NULL | CASCADE |
| voice_configs | app_id | applications | id | CASCADE | CASCADE |
| voice_configs | config_id | app_configs | id | SET NULL | CASCADE |
| config_push_history | app_id | applications | id | CASCADE | CASCADE |
| config_push_history | config_id | app_configs | id | CASCADE | CASCADE |
| device_push_status | push_history_id | config_push_history | id | CASCADE | CASCADE |
| device_push_status | device_id | devices | id | CASCADE | CASCADE |
| config_backups | app_id | applications | id | CASCADE | CASCADE |
| config_backups | config_id | app_configs | id | CASCADE | CASCADE |
| config_sync_logs | app_id | applications | id | CASCADE | CASCADE |
| config_sync_logs | device_id | devices | id | SET NULL | CASCADE |

### 5.2 级联操作说明

- **CASCADE**: 父记录删除时，子记录同时删除
- **SET NULL**: 父记录删除时，子记录的外键字段设为 NULL
- **RESTRICT**: 禁止删除有关联记录的父记录

---

## 6. 视图设计

### 6.1 v_application_stats - 应用统计视图

**用途**: 聚合应用的设备数量和配置更新时间。

**SQL**:
```sql
CREATE VIEW v_application_stats AS
SELECT
    a.id AS app_id,
    a.app_key,
    a.app_name,
    COUNT(DISTINCT d.id) AS total_devices,
    COUNT(DISTINCT CASE WHEN d.is_online = 1 THEN d.id END) AS online_devices,
    COUNT(DISTINCT ac.id) AS total_configs,
    MAX(ac.created_at) AS last_config_update
FROM applications a
LEFT JOIN devices d ON a.id = d.app_id AND d.status = 1
LEFT JOIN app_configs ac ON a.id = ac.app_id AND ac.status = 1
GROUP BY a.id, a.app_key, a.app_name;
```

**使用示例**:
```sql
-- 查询所有应用的统计信息
SELECT * FROM v_application_stats;

-- 查询在线设备大于0的应用
SELECT * FROM v_application_stats WHERE online_devices > 0;
```

---

### 6.2 v_active_devices - 活跃设备视图

**用途**: 显示所有活跃设备及其未活跃时长。

**SQL**:
```sql
CREATE VIEW v_active_devices AS
SELECT
    d.id,
    d.device_id,
    d.device_name,
    a.app_name,
    d.device_type,
    d.device_brand,
    d.device_model,
    d.app_version,
    d.is_online,
    d.last_active_time,
    TIMESTAMPDIFF(MINUTE, d.last_active_time, NOW()) AS inactive_minutes
FROM devices d
INNER JOIN applications a ON d.app_id = a.id
WHERE d.status = 1
ORDER BY d.last_active_time DESC;
```

**使用示例**:
```sql
-- 查询离线超过10分钟的设备
SELECT * FROM v_active_devices WHERE inactive_minutes > 10;

-- 查询在线设备
SELECT * FROM v_active_devices WHERE is_online = 1;
```

---

### 6.3 v_push_summary - 推送摘要视图

**用途**: 汇总最近的推送历史和执行情况。

**SQL**:
```sql
CREATE VIEW v_push_summary AS
SELECT
    ph.id,
    ph.app_id,
    a.app_name,
    ac.config_key,
    ac.config_name,
    ac.version,
    ph.push_type,
    ph.target_type,
    ph.push_status,
    ph.total_targets,
    ph.success_count,
    ph.failed_count,
    ph.progress,
    ph.started_at,
    ph.completed_at,
    TIMESTAMPDIFF(SECOND, ph.started_at, ph.completed_at) AS duration_seconds
FROM config_push_history ph
INNER JOIN applications a ON ph.app_id = a.id
INNER JOIN app_configs ac ON ph.config_id = ac.id
ORDER BY ph.created_at DESC;
```

**使用示例**:
```sql
-- 查询最近10次推送
SELECT * FROM v_push_summary LIMIT 10;

-- 查询失败的推送
SELECT * FROM v_push_summary WHERE push_status = 'failed';
```

---

## 7. 存储过程

### 7.1 sp_register_device - 注册设备

**用途**: 注册新设备或更新现有设备信息。

**参数**:
- `p_device_id` VARCHAR(100): 设备唯一ID
- `p_app_key` VARCHAR(64): 应用键
- `p_device_name` VARCHAR(100): 设备名称
- `p_device_type` VARCHAR(20): 设备类型
- `p_device_info` JSON: 设备信息 (brand, model, os_version, etc.)

**返回**: 无

**使用示例**:
```sql
CALL sp_register_device(
    'device_123',
    'ai_activity_show',
    '我的小米设备',
    'android',
    '{"brand":"Xiaomi","model":"Mi 11","os_version":"11","app_version":"1.0.0","network_type":"wifi","ip_address":"192.168.1.100"}'
);
```

---

### 7.2 sp_backup_config - 备份配置

**用途**: 为指定配置创建备份记录。

**参数**:
- `p_config_id` BIGINT: 配置ID
- `p_backup_name` VARCHAR(200): 备份名称
- `p_backup_type` VARCHAR(50): 备份类型 (manual, auto, before_push)
- `p_created_by` VARCHAR(100): 创建者

**返回**: 无

**使用示例**:
```sql
CALL sp_backup_config(
    1,
    '推送前自动备份',
    'before_push',
    'system'
);
```

---

### 7.3 sp_update_device_status - 更新设备状态

**用途**: 更新设备的在线状态。

**参数**:
- `p_device_id` VARCHAR(100): 设备ID
- `p_is_online` TINYINT: 在线状态 (1=在线, 0=离线)

**返回**: 无

**使用示例**:
```sql
-- 标记设备为在线
CALL sp_update_device_status('device_123', 1);

-- 标记设备为离线
CALL sp_update_device_status('device_123', 0);
```

---

## 8. 触发器

### 8.1 tr_devices_inactive_check - 设备离线检查

**用途**: 自动更新长时间未活跃的设备为离线状态。

**触发时机**: AFTER UPDATE ON devices

**逻辑**:
```sql
IF NEW.is_online = 1 AND NEW.last_active_time < DATE_SUB(NOW(), INTERVAL 5 MINUTE) THEN
    UPDATE devices SET is_online = 0 WHERE id = NEW.id;
END IF;
```

**说明**: 当设备更新时，如果标记为在线但最后活跃时间超过5分钟，自动标记为离线。

---

## 9. 数据字典

### 9.1 枚举值定义

#### applications.status
| 值 | 说明 |
|----|------|
| 0 | 禁用 |
| 1 | 启用 |
| 2 | 维护中 |

#### devices.device_type
| 值 | 说明 |
|----|------|
| android | Android设备 |
| ios | iOS设备 |
| web | Web浏览器 |

#### devices.status
| 值 | 说明 |
|----|------|
| 0 | 禁用 |
| 1 | 活跃 |
| 2 | 封禁 |

#### app_configs.status
| 值 | 说明 |
|----|------|
| 0 | 草稿 |
| 1 | 已发布 |
| 2 | 已归档 |

#### config_push_history.push_status
| 值 | 说明 |
|----|------|
| pending | 等待中 |
| sending | 发送中 |
| completed | 已完成 |
| failed | 失败 |
| cancelled | 已取消 |

---

### 9.2 状态码定义

所有表的状态字段遵循以下规范：

- **0**: 禁用/删除/失败
- **1**: 启用/活跃/成功
- **2**: 特殊状态 (如维护中、封禁、草稿等)

---

## 10. 性能优化

### 10.1 查询优化

#### 使用索引覆盖
```sql
-- 好的查询 - 使用索引
SELECT id, app_name, status FROM applications WHERE status = 1;

-- 避免的查询 - 不使用索引
SELECT * FROM applications WHERE LOWER(app_name) = 'ai活动秀';
```

#### 避免全表扫描
```sql
-- 好的查询 - 使用索引
SELECT * FROM devices WHERE app_id = 1 AND is_online = 1;

-- 避免的查询 - 全表扫描
SELECT * FROM devices WHERE YEAR(created_at) = 2026;
```

#### 使用 LIMIT 分页
```sql
-- 好的查询 - 使用分页
SELECT * FROM config_push_history ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- 避免的查询 - 无分页
SELECT * FROM config_push_history ORDER BY created_at DESC;
```

---

### 10.2 分区策略

对于大表，建议按时间分区：

```sql
-- config_sync_logs 按月分区
ALTER TABLE config_sync_logs
PARTITION BY RANGE (TO_DAYS(created_at)) (
    PARTITION p202601 VALUES LESS THAN (TO_DAYS('2026-02-01')),
    PARTITION p202602 VALUES LESS THAN (TO_DAYS('2026-03-01')),
    PARTITION p202603 VALUES LESS THAN (TO_DAYS('2026-04-01')),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

---

### 10.3 数据归档

定期归档历史数据：

```sql
-- 归档3个月前的同步日志
INSERT INTO config_sync_logs_archive
SELECT * FROM config_sync_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);

DELETE FROM config_sync_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);

-- 归档6个月前的推送历史
INSERT INTO config_push_history_archive
SELECT * FROM config_push_history
WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);

DELETE FROM config_push_history
WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);
```

---

### 10.4 缓存策略

对于频繁访问但不常变更的数据：

```python
# Python Flask 示例
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300, key_prefix='app_config')
def get_app_config(app_key, config_key):
    return AppConfig.query.filter_by(app_key=app_key, config_key=config_key).first()
```

---

## 附录

### A. 数据库连接配置

```python
# config/base_setting.py
SQLALCHEMY_DATABASE_URI = 'mysql://jcode:password@localhost:3306/jc_ai?charset=utf8mb4'
SQLALCHEMY_ENCODING = "utf8mb4"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # 生产环境设为 False
```

### B. 备份脚本

```bash
#!/bin/bash
# 数据库备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mysql"
DB_NAME="jc_ai"

mysqldump -u root -p${DB_PASS} ${DB_NAME} | gzip > ${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz

# 保留最近30天的备份
find ${BACK_DIR} -name "${DB_NAME}_*.sql.gz" -mtime +30 -delete
```

### C. 监控查询

```sql
-- 查看表大小
SELECT
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'jc_ai'
ORDER BY size_mb DESC;

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';

-- 查看InnoDB状态
SHOW ENGINE INNODB STATUS;
```

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-06
**维护者**: Database Design Expert
