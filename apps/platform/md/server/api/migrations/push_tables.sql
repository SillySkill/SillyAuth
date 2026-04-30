-- WebSocket 配置推送系统数据库表

-- 推送任务表
CREATE TABLE IF NOT EXISTS `push_tasks` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `task_id` VARCHAR(64) NOT NULL COMMENT '任务ID',
    `version` VARCHAR(32) NOT NULL COMMENT '配置版本',
    `version_code` INT(11) NOT NULL COMMENT '版本代码',
    `force_update` TINYINT(1) DEFAULT 0 COMMENT '是否强制更新',
    `release_notes` TEXT COMMENT '更新说明',
    `status` VARCHAR(32) DEFAULT 'pending' COMMENT '任务状态: pending, in_progress, completed, cancelled, failed',
    `target_devices` TEXT COMMENT '目标设备列表(JSON)',
    `target_groups` TEXT COMMENT '目标设备组列表(JSON)',
    `total_devices` INT(11) DEFAULT 0 COMMENT '总设备数',
    `success_devices` INT(11) DEFAULT 0 COMMENT '成功设备数',
    `failed_devices` INT(11) DEFAULT 0 COMMENT '失败设备数',
    `pending_devices` TEXT COMMENT '待推送设备列表(JSON)',
    `files` TEXT COMMENT '文件列表(JSON)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `started_at` DATETIME DEFAULT NULL COMMENT '开始时间',
    `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    `error_message` TEXT COMMENT '错误信息',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_task_id` (`task_id`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推送任务表';

-- 设备推送记录表
CREATE TABLE IF NOT EXISTS `push_device_records` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `task_id` VARCHAR(64) NOT NULL COMMENT '任务ID',
    `device_id` VARCHAR(64) NOT NULL COMMENT '设备ID',
    `status` VARCHAR(32) DEFAULT 'pending' COMMENT '推送状态: pending, sent, success, failed',
    `received_files` TEXT COMMENT '已接收文件列表(JSON)',
    `failed_files` TEXT COMMENT '失败文件列表(JSON)',
    `message` TEXT COMMENT '消息',
    `sent_at` DATETIME DEFAULT NULL COMMENT '发送时间',
    `ack_at` DATETIME DEFAULT NULL COMMENT '确认时间',
    PRIMARY KEY (`id`),
    KEY `idx_task_id` (`task_id`),
    KEY `idx_device_id` (`device_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备推送记录表';

-- 设备在线状态表
CREATE TABLE IF NOT EXISTS `device_online_status` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `device_id` VARCHAR(64) NOT NULL COMMENT '设备ID',
    `is_online` TINYINT(1) DEFAULT 0 COMMENT '是否在线',
    `sid` VARCHAR(64) DEFAULT NULL COMMENT 'WebSocket Session ID',
    `last_connect_time` DATETIME DEFAULT NULL COMMENT '最后连接时间',
    `last_heartbeat` DATETIME DEFAULT NULL COMMENT '最后心跳时间',
    `app_version` VARCHAR(32) DEFAULT NULL COMMENT '应用版本',
    `config_version` VARCHAR(32) DEFAULT NULL COMMENT '配置版本',
    `battery` INT(11) DEFAULT NULL COMMENT '电池电量',
    `storage` INT(11) DEFAULT NULL COMMENT '可用存储(MB)',
    `network_type` VARCHAR(32) DEFAULT NULL COMMENT '网络类型',
    `total_push_count` INT(11) DEFAULT 0 COMMENT '总推送次数',
    `success_push_count` INT(11) DEFAULT 0 COMMENT '成功推送次数',
    `failed_push_count` INT(11) DEFAULT 0 COMMENT '失败推送次数',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_device_id` (`device_id`),
    KEY `idx_is_online` (`is_online`),
    KEY `idx_last_heartbeat` (`last_heartbeat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备在线状态表';

-- 插入测试数据（可选）
-- INSERT INTO `device_online_status` (`device_id`, `is_online`, `app_version`, `config_version`) VALUES
-- ('test_device_001', 0, '1.0.0', 'v1.0.0'),
-- ('test_device_002', 0, '1.0.0', 'v1.0.0');
