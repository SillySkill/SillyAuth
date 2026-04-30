-- ============================================================================
-- AI Activity Show - Application Management Database Rollback
-- Migration: 20250206_init_app_management_rollback
-- Description: Rollback application management database schema
-- Author: Database Design Expert
-- Date: 2026-02-06
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- Drop Views
-- ============================================================================
DROP VIEW IF EXISTS `v_push_summary`;
DROP VIEW IF EXISTS `v_active_devices`;
DROP VIEW IF EXISTS `v_application_stats`;

-- ============================================================================
-- Drop Triggers
-- ============================================================================
DROP TRIGGER IF EXISTS `tr_devices_inactive_check`;

-- ============================================================================
-- Drop Stored Procedures
-- ============================================================================
DROP PROCEDURE IF EXISTS `sp_update_device_status`;
DROP PROCEDURE IF EXISTS `sp_backup_config`;
DROP PROCEDURE IF EXISTS `sp_register_device`;

-- ============================================================================
-- Drop Tables (in reverse order due to foreign key constraints)
-- ============================================================================
DROP TABLE IF EXISTS `config_sync_logs`;
DROP TABLE IF EXISTS `config_backups`;
DROP TABLE IF EXISTS `device_push_status`;
DROP TABLE IF EXISTS `config_push_history`;
DROP TABLE IF EXISTS `voice_configs`;
DROP TABLE IF EXISTS `digital_human_configs`;
DROP TABLE IF EXISTS `lottery_programs`;
DROP TABLE IF EXISTS `question_banks`;
DROP TABLE IF EXISTS `style_configs`;
DROP TABLE IF EXISTS `app_configs`;
DROP TABLE IF EXISTS `devices`;
DROP TABLE IF EXISTS `applications`;

-- ============================================================================
-- Finalize
-- ============================================================================
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Rollback Complete
-- ============================================================================
