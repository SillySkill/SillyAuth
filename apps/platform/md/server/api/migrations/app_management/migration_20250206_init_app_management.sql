-- ============================================================================
-- AI Activity Show - Application Management Database Schema
-- Migration: 20250206_init_app_management
-- Description: Initialize database schema for multi-application management system
-- Author: Database Design Expert
-- Date: 2026-02-06
-- ============================================================================

-- Set character set and collation
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- Table: applications
-- Description: Store application metadata and configurations
-- ============================================================================
DROP TABLE IF EXISTS `applications`;
CREATE TABLE `applications` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Application ID',
    `app_key` VARCHAR(64) NOT NULL UNIQUE COMMENT 'Application unique key (e.g., ai_activity_show)',
    `app_name` VARCHAR(100) NOT NULL COMMENT 'Application display name',
    `app_name_en` VARCHAR(100) DEFAULT NULL COMMENT 'Application English name',
    `package_name` VARCHAR(200) DEFAULT NULL COMMENT 'Android package name',
    `version` VARCHAR(20) DEFAULT '1.0.0' COMMENT 'Current version',
    `version_code` INT DEFAULT 1 COMMENT 'Version code for Android',
    `min_sdk_version` INT DEFAULT 24 COMMENT 'Minimum Android SDK version',
    `target_sdk_version` INT DEFAULT 34 COMMENT 'Target Android SDK version',
    `icon_url` VARCHAR(500) DEFAULT NULL COMMENT 'Application icon URL',
    `description` TEXT DEFAULT NULL COMMENT 'Application description',
    `description_en` TEXT DEFAULT NULL COMMENT 'English description',
    `features` JSON DEFAULT NULL COMMENT 'Application features list',
    `screenshots` JSON DEFAULT NULL COMMENT 'Screenshots URLs',
    `download_url` VARCHAR(500) DEFAULT NULL COMMENT 'APK download URL',
    `download_count` BIGINT UNSIGNED DEFAULT 0 COMMENT 'Download count',
    `category` VARCHAR(50) DEFAULT 'entertainment' COMMENT 'Application category',
    `tags` JSON DEFAULT NULL COMMENT 'Application tags',
    `developer` VARCHAR(100) DEFAULT 'jCoding' COMMENT 'Developer name',
    `website` VARCHAR(200) DEFAULT NULL COMMENT 'Official website',
    `contact_email` VARCHAR(100) DEFAULT NULL COMMENT 'Contact email',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=enabled, 2=maintenance',
    `is_default` TINYINT(1) DEFAULT 0 COMMENT 'Is default application',
    `sort_order` INT DEFAULT 0 COMMENT 'Display order',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    INDEX `idx_app_key` (`app_key`),
    INDEX `idx_status` (`status`),
    INDEX `idx_category` (`category`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Applications table';

-- ============================================================================
-- Table: devices
-- Description: Device registration and management
-- ============================================================================
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Device ID',
    `device_id` VARCHAR(100) NOT NULL UNIQUE COMMENT 'Unique device identifier',
    `device_sn` VARCHAR(100) DEFAULT NULL COMMENT 'Device serial number',
    `device_name` VARCHAR(100) DEFAULT NULL COMMENT 'Device name',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `device_type` VARCHAR(20) NOT NULL DEFAULT 'android' COMMENT 'Device type: android, ios, web',
    `device_brand` VARCHAR(50) DEFAULT NULL COMMENT 'Device brand (e.g., Xiaomi, Huawei)',
    `device_model` VARCHAR(100) DEFAULT NULL COMMENT 'Device model',
    `os_version` VARCHAR(50) DEFAULT NULL COMMENT 'OS version',
    `app_version` VARCHAR(20) DEFAULT NULL COMMENT 'Installed app version',
    `screen_resolution` VARCHAR(20) DEFAULT NULL COMMENT 'Screen resolution',
    `network_type` VARCHAR(20) DEFAULT NULL COMMENT 'Network type: wifi, 4g, 5g',
    `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'Last known IP address',
    `location` JSON DEFAULT NULL COMMENT 'Device location (latitude, longitude)',
    `push_token` VARCHAR(500) DEFAULT NULL COMMENT 'Push notification token',
    `is_online` TINYINT(1) DEFAULT 0 COMMENT 'Online status: 0=offline, 1=online',
    `last_active_time` DATETIME DEFAULT NULL COMMENT 'Last active timestamp',
    `registration_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Registration timestamp',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=active, 2=banned',
    `notes` TEXT DEFAULT NULL COMMENT 'Additional notes',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_device_id` (`device_id`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_device_type` (`device_type`),
    INDEX `idx_is_online` (`is_online`),
    INDEX `idx_status` (`status`),
    INDEX `idx_last_active_time` (`last_active_time`),
    INDEX `idx_app_device` (`app_id`, `device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Device registration and management';

-- ============================================================================
-- Table: app_configs
-- Description: Application configuration versions
-- ============================================================================
DROP TABLE IF EXISTS `app_configs`;
CREATE TABLE `app_configs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Config ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_key` VARCHAR(100) NOT NULL COMMENT 'Configuration key (e.g., global, quiz, lottery)',
    `config_name` VARCHAR(100) NOT NULL COMMENT 'Configuration display name',
    `version` VARCHAR(20) NOT NULL COMMENT 'Configuration version',
    `config_type` VARCHAR(50) NOT NULL DEFAULT 'json' COMMENT 'Config type: json, xml, yaml',
    `config_path` VARCHAR(200) DEFAULT NULL COMMENT 'Original asset path',
    `config_data` LONGTEXT NOT NULL COMMENT 'Configuration data (JSON string)',
    `config_schema` JSON DEFAULT NULL COMMENT 'Configuration schema for validation',
    `description` TEXT DEFAULT NULL COMMENT 'Configuration description',
    `change_log` TEXT DEFAULT NULL COMMENT 'Change log',
    `is_active` TINYINT(1) DEFAULT 0 COMMENT 'Is active version',
    `is_default` TINYINT(1) DEFAULT 0 COMMENT 'Is default configuration',
    `file_size` INT UNSIGNED DEFAULT 0 COMMENT 'Configuration file size in bytes',
    `checksum` VARCHAR(64) DEFAULT NULL COMMENT 'MD5 checksum for verification',
    `created_by` VARCHAR(100) DEFAULT 'system' COMMENT 'Creator username',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=draft, 1=published, 2=archived',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY `uk_app_config_version` (`app_id`, `config_key`, `version`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_config_key` (`config_key`),
    INDEX `idx_version` (`version`),
    INDEX `idx_is_active` (`is_active`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Application configuration versions';

-- ============================================================================
-- Table: style_configs
-- Description: AI style configurations
-- ============================================================================
DROP TABLE IF EXISTS `style_configs`;
CREATE TABLE `style_configs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Style config ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'Parent config ID',
    `style_id` VARCHAR(64) NOT NULL COMMENT 'Style unique identifier',
    `style_name` VARCHAR(100) NOT NULL COMMENT 'Style name',
    `style_name_en` VARCHAR(100) DEFAULT NULL COMMENT 'English style name',
    `category` VARCHAR(50) DEFAULT NULL COMMENT 'Style category',
    `thumbnail_url` VARCHAR(500) DEFAULT NULL COMMENT 'Style thumbnail image',
    `sample_image_url` VARCHAR(500) DEFAULT NULL COMMENT 'Sample result image',
    `style_config` JSON NOT NULL COMMENT 'Style configuration data',
    `api_params` JSON DEFAULT NULL COMMENT 'API parameters for style transfer',
    `processing_time` INT DEFAULT NULL COMMENT 'Average processing time in seconds',
    `quality_score` DECIMAL(3,2) DEFAULT NULL COMMENT 'Quality score (0.00-1.00)',
    `is_premium` TINYINT(1) DEFAULT 0 COMMENT 'Is premium style',
    `credits_required` INT DEFAULT 0 COMMENT 'Credits required per use',
    `usage_count` BIGINT UNSIGNED DEFAULT 0 COMMENT 'Total usage count',
    `like_count` INT UNSIGNED DEFAULT 0 COMMENT 'Like count',
    `sort_order` INT DEFAULT 0 COMMENT 'Display order',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=enabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY `uk_app_style_id` (`app_id`, `style_id`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_style_id` (`style_id`),
    INDEX `idx_category` (`category`),
    INDEX `idx_is_premium` (`is_premium`),
    INDEX `idx_status` (`status`),
    INDEX `idx_sort_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI style configurations';

-- ============================================================================
-- Table: question_banks
-- Description: Quiz question banks
-- ============================================================================
DROP TABLE IF EXISTS `question_banks`;
CREATE TABLE `question_banks` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Question bank ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'Parent config ID',
    `bank_id` VARCHAR(64) NOT NULL COMMENT 'Question bank unique identifier',
    `bank_name` VARCHAR(100) NOT NULL COMMENT 'Question bank name',
    `bank_name_en` VARCHAR(100) DEFAULT NULL COMMENT 'English bank name',
    `category` VARCHAR(50) DEFAULT NULL COMMENT 'Question category',
    `difficulty` VARCHAR(20) DEFAULT 'medium' COMMENT 'Difficulty: easy, medium, hard',
    `total_questions` INT UNSIGNED DEFAULT 0 COMMENT 'Total question count',
    `choice_count` INT UNSIGNED DEFAULT 0 COMMENT 'Choice question count',
    `judgement_count` INT UNSIGNED DEFAULT 0 COMMENT 'Judgement question count',
    `questions_data` LONGTEXT DEFAULT NULL COMMENT 'Questions JSON data',
    `thumbnail_url` VARCHAR(500) DEFAULT NULL COMMENT 'Thumbnail image',
    `description` TEXT DEFAULT NULL COMMENT 'Bank description',
    `tags` JSON DEFAULT NULL COMMENT 'Tags array',
    `play_count` BIGINT UNSIGNED DEFAULT 0 COMMENT 'Total play count',
    `avg_score` DECIMAL(5,2) DEFAULT NULL COMMENT 'Average score',
    `completion_rate` DECIMAL(5,2) DEFAULT NULL COMMENT 'Completion rate percentage',
    `time_limit` INT DEFAULT NULL COMMENT 'Time limit in seconds',
    `passing_score` INT DEFAULT 60 COMMENT 'Passing score',
    `is_premium` TINYINT(1) DEFAULT 0 COMMENT 'Is premium bank',
    `sort_order` INT DEFAULT 0 COMMENT 'Display order',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=enabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY `uk_app_bank_id` (`app_id`, `bank_id`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_bank_id` (`bank_id`),
    INDEX `idx_category` (`category`),
    INDEX `idx_difficulty` (`difficulty`),
    INDEX `idx_status` (`status`),
    INDEX `idx_sort_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Quiz question banks';

-- ============================================================================
-- Table: lottery_programs
-- Description: Lottery programs configuration
-- ============================================================================
DROP TABLE IF EXISTS `lottery_programs`;
CREATE TABLE `lottery_programs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Lottery program ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'Parent config ID',
    `program_id` VARCHAR(64) NOT NULL COMMENT 'Program unique identifier',
    `program_name` VARCHAR(100) NOT NULL COMMENT 'Program name',
    `program_name_en` VARCHAR(100) DEFAULT NULL COMMENT 'English program name',
    `program_type` VARCHAR(50) DEFAULT 'lucky' COMMENT 'Program type: lucky, wheel, box',
    `description` TEXT DEFAULT NULL COMMENT 'Program description',
    `thumbnail_url` VARCHAR(500) DEFAULT NULL COMMENT 'Thumbnail image',
    `background_image_url` VARCHAR(500) DEFAULT NULL COMMENT 'Background image',
    `program_config` JSON NOT NULL COMMENT 'Program configuration data',
    `prizes_config` JSON DEFAULT NULL COMMENT 'Prizes configuration',
    `rules` TEXT DEFAULT NULL COMMENT 'Lottery rules',
    `background_music` VARCHAR(500) DEFAULT NULL COMMENT 'Background music URL',
    `animation_config` JSON DEFAULT NULL COMMENT 'Animation configuration',
    `draw_count` INT UNSIGNED DEFAULT 0 COMMENT 'Total draw count',
    `win_count` INT UNSIGNED DEFAULT 0 COMMENT 'Total win count',
    `win_rate` DECIMAL(5,2) DEFAULT NULL COMMENT 'Win rate percentage',
    `is_premium` TINYINT(1) DEFAULT 0 COMMENT 'Is premium program',
    `max_participants` INT DEFAULT NULL COMMENT 'Max participants limit',
    `duration` INT DEFAULT NULL COMMENT 'Duration in seconds',
    `cooldown_period` INT DEFAULT NULL COMMENT 'Cooldown period in seconds',
    `sort_order` INT DEFAULT 0 COMMENT 'Display order',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=enabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY `uk_app_program_id` (`app_id`, `program_id`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_program_id` (`program_id`),
    INDEX `idx_program_type` (`program_type`),
    INDEX `idx_status` (`status`),
    INDEX `idx_sort_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Lottery programs configuration';

-- ============================================================================
-- Table: digital_human_configs
-- Description: Digital human configurations
-- ============================================================================
DROP TABLE IF EXISTS `digital_human_configs`;
CREATE TABLE `digital_human_configs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Digital human config ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'Parent config ID',
    `human_id` VARCHAR(64) NOT NULL COMMENT 'Digital human unique identifier',
    `human_name` VARCHAR(100) NOT NULL COMMENT 'Digital human name',
    `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT 'Avatar image URL',
    `model_type` VARCHAR(50) DEFAULT 'gif' COMMENT 'Model type: gif, video, 3d',
    `gender` VARCHAR(20) DEFAULT NULL COMMENT 'Gender: male, female, neutral',
    `age_group` VARCHAR(30) DEFAULT NULL COMMENT 'Age group: child, young, adult, senior',
    `style` VARCHAR(50) DEFAULT NULL COMMENT 'Style: cartoon, realistic, anime',
    `actions_config` JSON NOT NULL COMMENT 'Actions configuration',
    `default_action` VARCHAR(50) DEFAULT 'idle' COMMENT 'Default action',
    `tts_enabled` TINYINT(1) DEFAULT 1 COMMENT 'TTS enabled',
    `voice_type` VARCHAR(50) DEFAULT NULL COMMENT 'Voice type',
    `language` VARCHAR(10) DEFAULT 'zh-CN' COMMENT 'Language code',
    `gesture_enabled` TINYINT(1) DEFAULT 1 COMMENT 'Gesture enabled',
    `expression_enabled` TINYINT(1) DEFAULT 1 COMMENT 'Expression enabled',
    `background_image_url` VARCHAR(500) DEFAULT NULL COMMENT 'Background image URL',
    `position_config` JSON DEFAULT NULL COMMENT 'Position configuration (x, y, scale)',
    `animation_config` JSON DEFAULT NULL COMMENT 'Animation configuration',
    `modules` JSON DEFAULT NULL COMMENT 'Enabled modules array',
    `usage_count` BIGINT UNSIGNED DEFAULT 0 COMMENT 'Usage count',
    `is_premium` TINYINT(1) DEFAULT 0 COMMENT 'Is premium digital human',
    `sort_order` INT DEFAULT 0 COMMENT 'Display order',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=enabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY `uk_app_human_id` (`app_id`, `human_id`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_human_id` (`human_id`),
    INDEX `idx_model_type` (`model_type`),
    INDEX `idx_status` (`status`),
    INDEX `idx_sort_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Digital human configurations';

-- ============================================================================
-- Table: voice_configs
-- Description: Voice and TTS/ASR configurations
-- ============================================================================
DROP TABLE IF EXISTS `voice_configs`;
CREATE TABLE `voice_configs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Voice config ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'Parent config ID',
    `config_key` VARCHAR(100) NOT NULL COMMENT 'Config key: asr, tts, voice_command',
    `provider` VARCHAR(50) NOT NULL DEFAULT 'tencent' COMMENT 'Provider: tencent, ali, iflytek',
    `voice_config` JSON NOT NULL COMMENT 'Voice configuration data',
    `app_id_key` VARCHAR(200) DEFAULT NULL COMMENT 'Application ID/Key',
    `app_secret` VARCHAR(500) DEFAULT NULL COMMENT 'Application secret (encrypted)',
    `project_id` VARCHAR(100) DEFAULT NULL COMMENT 'Project ID',
    `region` VARCHAR(50) DEFAULT NULL COMMENT 'Service region',
    `engine_type` VARCHAR(50) DEFAULT NULL COMMENT 'Engine type',
    `voice_type` VARCHAR(50) DEFAULT NULL COMMENT 'Voice type for TTS',
    `sample_rate` INT DEFAULT 16000 COMMENT 'Sample rate',
    `bit_rate` INT DEFAULT NULL COMMENT 'Bit rate',
    `encoding` VARCHAR(20) DEFAULT 'pcm' COMMENT 'Audio encoding',
    `language` VARCHAR(10) DEFAULT 'zh-CN' COMMENT 'Language code',
    `accent` VARCHAR(50) DEFAULT NULL COMMENT 'Accent/dialect',
    `speed` DECIMAL(3,2) DEFAULT 1.00 COMMENT 'Speech speed (0.50-2.00)',
    `pitch` DECIMAL(3,2) DEFAULT 1.00 COMMENT 'Pitch adjustment (0.50-2.00)',
    `volume` DECIMAL(3,2) DEFAULT 1.00 COMMENT 'Volume (0.50-2.00)',
    `enable_punctuation` TINYINT(1) DEFAULT 1 COMMENT 'Enable punctuation prediction',
    `enable_digitization` TINYINT(1) DEFAULT 1 COMMENT 'Enable number conversion',
    `filter_sensitive` TINYINT(1) DEFAULT 1 COMMENT 'Filter sensitive words',
    `custom_keywords` JSON DEFAULT NULL COMMENT 'Custom keywords list',
    `hot_words` JSON DEFAULT NULL COMMENT 'Hot words for recognition',
    `timeout` INT DEFAULT 60 COMMENT 'Recognition timeout in seconds',
    `max_duration` INT DEFAULT 60 COMMENT 'Max audio duration in seconds',
    `description` TEXT DEFAULT NULL COMMENT 'Configuration description',
    `is_default` TINYINT(1) DEFAULT 0 COMMENT 'Is default configuration',
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Status: 0=disabled, 1=enabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY `uk_app_config_key` (`app_id`, `config_key`),
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_config_key` (`config_key`),
    INDEX `idx_provider` (`provider`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Voice and TTS/ASR configurations';

-- ============================================================================
-- Table: config_push_history
-- Description: Configuration push history tracking
-- ============================================================================
DROP TABLE IF EXISTS `config_push_history`;
CREATE TABLE `config_push_history` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Push history ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED NOT NULL COMMENT 'Configuration ID',
    `push_type` VARCHAR(50) NOT NULL COMMENT 'Push type: full, incremental',
    `target_type` VARCHAR(20) NOT NULL COMMENT 'Target type: all, device, group',
    `target_devices` JSON DEFAULT NULL COMMENT 'Target device IDs array',
    `push_method` VARCHAR(20) NOT NULL DEFAULT 'ws' COMMENT 'Push method: ws, http, polling',
    `push_status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'Status: pending, sending, completed, failed, cancelled',
    `total_targets` INT UNSIGNED DEFAULT 0 COMMENT 'Total target count',
    `success_count` INT UNSIGNED DEFAULT 0 COMMENT 'Success count',
    `failed_count` INT UNSIGNED DEFAULT 0 COMMENT 'Failed count',
    `progress` DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Progress percentage',
    `error_message` TEXT DEFAULT NULL COMMENT 'Error message if failed',
    `retry_count` INT UNSIGNED DEFAULT 0 COMMENT 'Retry count',
    `max_retry` INT UNSIGNED DEFAULT 3 COMMENT 'Max retry attempts',
    `priority` TINYINT DEFAULT 5 COMMENT 'Priority: 1=low, 5=normal, 10=high',
    `push_config` JSON DEFAULT NULL COMMENT 'Push configuration',
    `result_summary` JSON DEFAULT NULL COMMENT 'Push result summary',
    `started_at` DATETIME DEFAULT NULL COMMENT 'Start time',
    `completed_at` DATETIME DEFAULT NULL COMMENT 'Completion time',
    `created_by` VARCHAR(100) DEFAULT NULL COMMENT 'Creator username',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_config_id` (`config_id`),
    INDEX `idx_push_status` (`push_status`),
    INDEX `idx_push_type` (`push_type`),
    INDEX `idx_target_type` (`target_type`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_started_at` (`started_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Configuration push history tracking';

-- ============================================================================
-- Table: device_push_status
-- Description: Per-device push status tracking
-- ============================================================================
DROP TABLE IF EXISTS `device_push_status`;
CREATE TABLE `device_push_status` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Push status ID',
    `push_history_id` BIGINT UNSIGNED NOT NULL COMMENT 'Push history ID',
    `device_id` BIGINT UNSIGNED NOT NULL COMMENT 'Device ID',
    `push_status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'Status: pending, sending, delivered, confirmed, failed',
    `retry_count` INT UNSIGNED DEFAULT 0 COMMENT 'Retry count',
    `error_code` VARCHAR(50) DEFAULT NULL COMMENT 'Error code',
    `error_message` TEXT DEFAULT NULL COMMENT 'Error message',
    `delivered_at` DATETIME DEFAULT NULL COMMENT 'Delivery time',
    `confirmed_at` DATETIME DEFAULT NULL COMMENT 'Confirmation time',
    `config_version` VARCHAR(20) DEFAULT NULL COMMENT 'Received config version',
    `device_response` JSON DEFAULT NULL COMMENT 'Device response data',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    FOREIGN KEY (`push_history_id`) REFERENCES `config_push_history`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`device_id`) REFERENCES `devices`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_push_history_id` (`push_history_id`),
    INDEX `idx_device_id` (`device_id`),
    INDEX `idx_push_status` (`push_status`),
    INDEX `idx_delivered_at` (`delivered_at`),
    UNIQUE KEY `uk_push_device` (`push_history_id`, `device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Per-device push status tracking';

-- ============================================================================
-- Table: config_backups
-- Description: Configuration backup history
-- ============================================================================
DROP TABLE IF EXISTS `config_backups`;
CREATE TABLE `config_backups` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Backup ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `config_id` BIGINT UNSIGNED NOT NULL COMMENT 'Original configuration ID',
    `backup_name` VARCHAR(200) NOT NULL COMMENT 'Backup name',
    `backup_type` VARCHAR(50) NOT NULL COMMENT 'Backup type: manual, auto, before_push',
    `config_key` VARCHAR(100) NOT NULL COMMENT 'Configuration key',
    `config_version` VARCHAR(20) NOT NULL COMMENT 'Configuration version',
    `config_data` LONGTEXT NOT NULL COMMENT 'Configuration data (JSON)',
    `file_size` INT UNSIGNED DEFAULT 0 COMMENT 'Backup file size in bytes',
    `checksum` VARCHAR(64) DEFAULT NULL COMMENT 'MD5 checksum',
    `description` TEXT DEFAULT NULL COMMENT 'Backup description',
    `backup_path` VARCHAR(500) DEFAULT NULL COMMENT 'Storage path if external',
    `is_automatic` TINYINT(1) DEFAULT 0 COMMENT 'Is automatic backup',
    `retention_days` INT DEFAULT 30 COMMENT 'Retention period in days',
    `expires_at` DATETIME DEFAULT NULL COMMENT 'Expiration date',
    `created_by` VARCHAR(100) DEFAULT 'system' COMMENT 'Creator username',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `app_configs`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_config_id` (`config_id`),
    INDEX `idx_config_key` (`config_key`),
    INDEX `idx_backup_type` (`backup_type`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Configuration backup history';

-- ============================================================================
-- Table: config_sync_logs
-- Description: Configuration synchronization logs
-- ============================================================================
DROP TABLE IF EXISTS `config_sync_logs`;
CREATE TABLE `config_sync_logs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'Sync log ID',
    `app_id` INT UNSIGNED NOT NULL COMMENT 'Application ID',
    `device_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'Device ID',
    `sync_type` VARCHAR(50) NOT NULL COMMENT 'Sync type: pull, push, check_update',
    `config_key` VARCHAR(100) DEFAULT NULL COMMENT 'Configuration key',
    `local_version` VARCHAR(20) DEFAULT NULL COMMENT 'Local version',
    `remote_version` VARCHAR(20) DEFAULT NULL COMMENT 'Remote version',
    `sync_status` VARCHAR(20) NOT NULL COMMENT 'Status: success, failed, partial',
    `sync_method` VARCHAR(20) DEFAULT NULL COMMENT 'Sync method: ws, http, polling',
    `data_size` INT UNSIGNED DEFAULT 0 COMMENT 'Data size in bytes',
    `duration` INT UNSIGNED DEFAULT NULL COMMENT 'Sync duration in milliseconds',
    `error_code` VARCHAR(50) DEFAULT NULL COMMENT 'Error code',
    `error_message` TEXT DEFAULT NULL COMMENT 'Error message',
    `request_params` JSON DEFAULT NULL COMMENT 'Request parameters',
    `response_data` JSON DEFAULT NULL COMMENT 'Response data',
    `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'Client IP address',
    `user_agent` VARCHAR(500) DEFAULT NULL COMMENT 'User agent string',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    FOREIGN KEY (`app_id`) REFERENCES `applications`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`device_id`) REFERENCES `devices`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX `idx_app_id` (`app_id`),
    INDEX `idx_device_id` (`device_id`),
    INDEX `idx_sync_type` (`sync_type`),
    INDEX `idx_sync_status` (`sync_status`),
    INDEX `idx_config_key` (`config_key`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Configuration synchronization logs';

-- ============================================================================
-- Insert Initial Data for AI Activity Show Application
-- ============================================================================

-- Insert AI Activity Show as default application
INSERT INTO `applications` (
    `app_key`, `app_name`, `app_name_en`, `package_name`,
    `version`, `version_code`, `min_sdk_version`, `target_sdk_version`,
    `description`, `description_en`, `category`, `status`, `is_default`
) VALUES (
    'ai_activity_show',
    'AI活动秀',
    'AI Activity Show',
    'com.jcoding.aiactivity',
    '1.0.0',
    1,
    24,
    34,
    '集成AI技术的Android活动应用，包含AI百变秀、知识问答、幸运抽奖和内场秀功能',
    'Android activity app integrated with AI technologies, featuring AI styling, quiz, lottery, and inner show',
    'entertainment',
    1,
    1
);

-- Get the application ID for subsequent inserts (assuming ID = 1)
SET @app_id = LAST_INSERT_ID();

-- Insert initial global configuration
INSERT INTO `app_configs` (
    `app_id`, `config_key`, `config_name`, `version`,
    `config_type`, `config_path`, `config_data`, `is_active`, `is_default`, `status`
) VALUES (
    @app_id,
    'global',
    '全局配置',
    '1.0.0',
    'json',
    'config.json',
    '{"digital_human_enabled":true,"voice_enabled":true,"auto_update":true,"offline_mode":true}',
    1,
    1,
    1
);

-- Insert initial style configuration
INSERT INTO `style_configs` (
    `app_id`, `style_id`, `style_name`, `category`,
    `style_config`, `sort_order`, `status`
) VALUES (
    @app_id,
    'portrait_basic',
    '人像基础',
    'portrait',
    '{"filter_strength":0.7,"color_enhance":true,"smooth_factor":0.5}',
    1,
    1
), (
    @app_id,
    'cartoon_style',
    '卡通风格',
    'cartoon',
    '{"edge_thickness":2,"color_palette":"vibrant","simplify_level":0.6}',
    2,
    1
), (
    @app_id,
    'oil_painting',
    '油画风格',
    'artistic',
    '{"brush_size":8,"texture_overlay":true,"color_blend":0.8}',
    3,
    1
);

-- Insert initial question bank
INSERT INTO `question_banks` (
    `app_id`, `bank_id`, `bank_name`, `category`,
    `difficulty`, `total_questions`, `choice_count`, `judgement_count`,
    `time_limit`, `passing_score`, `sort_order`, `status`
) VALUES (
    @app_id,
    'jcq101',
    '综合知识库',
    'general',
    'medium',
    100,
    80,
    20,
    300,
    60,
    1,
    1
), (
    @app_id,
    'jcq102',
    '科技知识',
    'technology',
    'hard',
    50,
    40,
    10,
    240,
    70,
    2,
    1
);

-- Insert initial lottery program
INSERT INTO `lottery_programs` (
    `app_id`, `program_id`, `program_name`, `program_type`,
    `description`, `program_config`, `prizes_config`, `sort_order`, `status`
) VALUES (
    @app_id,
    'lottery_001',
    '幸运大抽奖',
    'lucky',
    '经典抽奖程序，支持多奖品配置',
    '{"animation_type":"wheel","draw_mode":"random","show_result":true}',
    '{"prizes":[{"name":"一等奖","count":1,"probability":0.01},{"name":"二等奖","count":5,"probability":0.05}]}',
    1,
    1
), (
    @app_id,
    'lottery_002',
    '欢乐转盘',
    'wheel',
    '转盘抽奖，视觉效果丰富',
    '{"animation_type":"wheel","draw_mode":"spin","show_result":true}',
    '{"prizes":[{"name":"特等奖","count":1,"probability":0.005},{"name":"参与奖","count":100,"probability":0.5}]}',
    2,
    1
);

-- Insert initial digital human configuration
INSERT INTO `digital_human_configs` (
    `app_id`, `human_id`, `human_name`, `model_type`,
    `gender`, `style`, `actions_config`, `modules`, `sort_order`, `status`
) VALUES (
    @app_id,
    'digital_human_001',
    'AI助手',
    'gif',
    'female',
    'realistic',
    '{"idle":"idle.gif","talking":"talking.gif","actions":["wave","point","clap"]}',
    '["quiz","lottery","inner"]',
    1,
    1
);

-- Insert initial voice configuration
INSERT INTO `voice_configs` (
    `app_id`, `config_key`, `provider`,
    `voice_config`, `language`, `speed`, `volume`, `is_default`, `status`
) VALUES (
    @app_id,
    'asr',
    'tencent',
    '{"engine_type":"16k_zh","enable_punctuation":true,"enable_digitization":true}',
    'zh-CN',
    1.00,
    1.00,
    1,
    1
), (
    @app_id,
    'tts',
    'tencent',
    '{"voice_type":"101001","codec":"pcm","sample_rate":16000}',
    'zh-CN',
    1.00,
    1.00,
    1,
    1
);

-- ============================================================================
-- Create Views for Common Queries
-- ============================================================================

-- View: Application statistics
CREATE OR REPLACE VIEW `v_application_stats` AS
SELECT
    a.id AS app_id,
    a.app_key,
    a.app_name,
    COUNT(DISTINCT d.id) AS total_devices,
    COUNT(DISTINCT CASE WHEN d.is_online = 1 THEN d.id END) AS online_devices,
    COUNT(DISTINCT ac.id) AS total_configs,
    MAX(ac.created_at) AS last_config_update
FROM
    applications a
LEFT JOIN
    devices d ON a.id = d.app_id AND d.status = 1
LEFT JOIN
    app_configs ac ON a.id = ac.app_id AND ac.status = 1
GROUP BY
    a.id, a.app_key, a.app_name;

-- View: Active devices with latest info
CREATE OR REPLACE VIEW `v_active_devices` AS
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
FROM
    devices d
INNER JOIN
    applications a ON d.app_id = a.id
WHERE
    d.status = 1
ORDER BY
    d.last_active_time DESC;

-- View: Recent push history summary
CREATE OR REPLACE VIEW `v_push_summary` AS
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
FROM
    config_push_history ph
INNER JOIN
    applications a ON ph.app_id = a.id
INNER JOIN
    app_configs ac ON ph.config_id = ac.id
ORDER BY
    ph.created_at DESC;

-- ============================================================================
-- Create Stored Procedures for Common Operations
-- ============================================================================

DELIMITER $$

-- Procedure: Register or update device
CREATE PROCEDURE `sp_register_device`(
    IN p_device_id VARCHAR(100),
    IN p_app_key VARCHAR(64),
    IN p_device_name VARCHAR(100),
    IN p_device_type VARCHAR(20),
    IN p_device_info JSON
)
BEGIN
    DECLARE v_app_id INT;
    DECLARE v_device_exists INT;

    -- Get application ID
    SELECT id INTO v_app_id FROM applications WHERE app_key = p_app_key AND status = 1 LIMIT 1;

    IF v_app_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Application not found';
    END IF;

    -- Check if device exists
    SELECT COUNT(*) INTO v_device_exists FROM devices WHERE device_id = p_device_id;

    IF v_device_exists > 0 THEN
        -- Update existing device
        UPDATE devices
        SET
            device_name = p_device_name,
            device_type = p_device_type,
            device_brand = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.brand')),
            device_model = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.model')),
            os_version = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.os_version')),
            app_version = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.app_version')),
            screen_resolution = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.resolution')),
            network_type = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.network_type')),
            ip_address = JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.ip_address')),
            is_online = 1,
            last_active_time = NOW(),
            updated_at = NOW()
        WHERE device_id = p_device_id;
    ELSE
        -- Insert new device
        INSERT INTO devices (
            device_id, app_id, device_name, device_type,
            device_brand, device_model, os_version, app_version,
            screen_resolution, network_type, ip_address,
            is_online, last_active_time, registration_time
        ) VALUES (
            p_device_id, v_app_id, p_device_name, p_device_type,
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.brand')),
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.model')),
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.os_version')),
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.app_version')),
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.resolution')),
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.network_type')),
            JSON_UNQUOTE(JSON_EXTRACT(p_device_info, '$.ip_address')),
            1, NOW(), NOW()
        );
    END IF;
END$$

-- Procedure: Create configuration backup
CREATE PROCEDURE `sp_backup_config`(
    IN p_config_id BIGINT,
    IN p_backup_name VARCHAR(200),
    IN p_backup_type VARCHAR(50),
    IN p_created_by VARCHAR(100)
)
BEGIN
    DECLARE v_app_id INT;
    DECLARE v_config_key VARCHAR(100);
    DECLARE v_config_version VARCHAR(20);
    DECLARE v_config_data LONGTEXT;
    DECLARE v_file_size INT;

    -- Get config details
    SELECT
        app_id, config_key, version, config_data, LENGTH(config_data)
    INTO
        v_app_id, v_config_key, v_config_version, v_config_data, v_file_size
    FROM app_configs
    WHERE id = p_config_id
    LIMIT 1;

    IF v_app_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Configuration not found';
    END IF;

    -- Insert backup
    INSERT INTO config_backups (
        app_id, config_id, backup_name, backup_type,
        config_key, config_version, config_data, file_size,
        checksum, created_by
    ) VALUES (
        v_app_id, p_config_id, p_backup_name, p_backup_type,
        v_config_key, v_config_version, v_config_data, v_file_size,
        MD5(v_config_data), p_created_by
    );
END$$

-- Procedure: Update device online status
CREATE PROCEDURE `sp_update_device_status`(
    IN p_device_id VARCHAR(100),
    IN p_is_online TINYINT
)
BEGIN
    UPDATE devices
    SET
        is_online = p_is_online,
        last_active_time = NOW(),
        updated_at = NOW()
    WHERE device_id = p_device_id;
END$$

DELIMITER ;

-- ============================================================================
-- Create Triggers for Automatic Timestamp Updates
-- ============================================================================

-- Trigger: Update device inactive status
DELIMITER $$
CREATE TRIGGER `tr_devices_inactive_check`
AFTER UPDATE ON `devices`
FOR EACH ROW
BEGIN
    IF NEW.is_online = 1 AND NEW.last_active_time < DATE_SUB(NOW(), INTERVAL 5 MINUTE) THEN
        UPDATE devices SET is_online = 0 WHERE id = NEW.id;
    END IF;
END$$
DELIMITER ;

-- ============================================================================
-- Grant Permissions (Optional - uncomment if needed)
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON jc_ai.* TO 'jcode'@'%';
-- FLUSH PRIVILEGES;

-- ============================================================================
-- Finalize
-- ============================================================================
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Total tables created: 12
-- Total views created: 3
-- Total stored procedures created: 3
-- Total triggers created: 1
-- ============================================================================
