-- ============================================================================
-- AI Activity Show - Database Verification Script
-- Purpose: Verify that the database schema is correctly installed
-- Author: Database Design Expert
-- Date: 2026-02-06
-- ============================================================================

USE jc_ai;

-- ============================================================================
-- 1. Check if all tables exist
-- ============================================================================
SELECT '=== Checking Tables ===' AS test_name;

SELECT
    TABLE_NAME AS table_name,
    CASE
        WHEN TABLE_NAME IN (
            'applications', 'devices', 'app_configs', 'style_configs',
            'question_banks', 'lottery_programs', 'digital_human_configs',
            'voice_configs', 'config_push_history', 'device_push_status',
            'config_backups', 'config_sync_logs'
        ) THEN '✓ EXISTS'
        ELSE '✗ MISSING'
    END AS status
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'jc_ai'
  AND TABLE_NAME IN (
    'applications', 'devices', 'app_configs', 'style_configs',
    'question_banks', 'lottery_programs', 'digital_human_configs',
    'voice_configs', 'config_push_history', 'device_push_status',
    'config_backups', 'config_sync_logs'
)
ORDER BY TABLE_NAME;

-- ============================================================================
-- 2. Check table counts
-- ============================================================================
SELECT '=== Table Counts ===' AS test_name;

SELECT
    'applications' AS table_name,
    COUNT(*) AS row_count
FROM applications
UNION ALL
SELECT
    'devices',
    COUNT(*)
FROM devices
UNION ALL
SELECT
    'app_configs',
    COUNT(*)
FROM app_configs
UNION ALL
SELECT
    'style_configs',
    COUNT(*)
FROM style_configs
UNION ALL
SELECT
    'question_banks',
    COUNT(*)
FROM question_banks
UNION ALL
SELECT
    'lottery_programs',
    COUNT(*)
FROM lottery_programs
UNION ALL
SELECT
    'digital_human_configs',
    COUNT(*)
FROM digital_human_configs
UNION ALL
SELECT
    'voice_configs',
    COUNT(*)
FROM voice_configs;

-- ============================================================================
-- 3. Check views
-- ============================================================================
SELECT '=== Checking Views ===' AS test_name;

SELECT
    TABLE_NAME AS view_name,
    CASE
        WHEN TABLE_NAME IN ('v_application_stats', 'v_active_devices', 'v_push_summary')
        THEN '✓ EXISTS'
        ELSE '✗ MISSING'
    END AS status
FROM information_schema.VIEWS
WHERE TABLE_SCHEMA = 'jc_ai'
  AND TABLE_NAME IN ('v_application_stats', 'v_active_devices', 'v_push_summary')
ORDER BY TABLE_NAME;

-- ============================================================================
-- 4. Check stored procedures
-- ============================================================================
SELECT '=== Checking Stored Procedures ===' AS test_name;

SELECT
    ROUTINE_NAME AS procedure_name,
    CASE
        WHEN ROUTINE_NAME IN ('sp_register_device', 'sp_backup_config', 'sp_update_device_status')
        THEN '✓ EXISTS'
        ELSE '✗ MISSING'
    END AS status
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = 'jc_ai'
  AND ROUTINE_TYPE = 'PROCEDURE'
  AND ROUTINE_NAME IN ('sp_register_device', 'sp_backup_config', 'sp_update_device_status')
ORDER BY ROUTINE_NAME;

-- ============================================================================
-- 5. Check triggers
-- ============================================================================
SELECT '=== Checking Triggers ===' AS test_name;

SELECT
    TRIGGER_NAME AS trigger_name,
    EVENT_OBJECT_TABLE AS table_name,
    CASE
        WHEN TRIGGER_NAME = 'tr_devices_inactive_check'
        THEN '✓ EXISTS'
        ELSE '✗ MISSING'
    END AS status
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'jc_ai'
  AND TRIGGER_NAME = 'tr_devices_inactive_check';

-- ============================================================================
-- 6. Check foreign keys
-- ============================================================================
SELECT '=== Checking Foreign Keys ===' AS test_name;

SELECT
    TABLE_NAME AS table_name,
    CONSTRAINT_NAME AS constraint_name,
    REFERENCED_TABLE_NAME AS referenced_table,
    '✓ EXISTS' AS status
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'jc_ai'
  AND REFERENCED_TABLE_NAME IS NOT NULL
  AND TABLE_NAME IN ('devices', 'app_configs', 'style_configs', 'question_banks',
                      'lottery_programs', 'digital_human_configs', 'voice_configs',
                      'config_push_history', 'device_push_status', 'config_backups',
                      'config_sync_logs')
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- ============================================================================
-- 7. Check initial data
-- ============================================================================
SELECT '=== Checking Initial Data ===' AS test_name;

-- Check AI Activity Show application
SELECT
    'AI Activity Show Application' AS data_name,
    CASE
        WHEN COUNT(*) > 0 THEN '✓ INSERTED'
        ELSE '✗ MISSING'
    END AS status,
    COUNT(*) AS count
FROM applications
WHERE app_key = 'ai_activity_show';

-- Check global config
SELECT
    'Global Configuration' AS data_name,
    CASE
        WHEN COUNT(*) > 0 THEN '✓ INSERTED'
        ELSE '✗ MISSING'
    END AS status,
    COUNT(*) AS count
FROM app_configs
WHERE config_key = 'global';

-- Check style configs
SELECT
    'Style Configurations' AS data_name,
    CASE
        WHEN COUNT(*) >= 3 THEN '✓ INSERTED'
        ELSE '✗ INCOMPLETE'
    END AS status,
    COUNT(*) AS count
FROM style_configs;

-- Check question banks
SELECT
    'Question Banks' AS data_name,
    CASE
        WHEN COUNT(*) >= 2 THEN '✓ INSERTED'
        ELSE '✗ INCOMPLETE'
    END AS status,
    COUNT(*) AS count
FROM question_banks;

-- Check lottery programs
SELECT
    'Lottery Programs' AS data_name,
    CASE
        WHEN COUNT(*) >= 2 THEN '✓ INSERTED'
        ELSE '✗ INCOMPLETE'
    END AS status,
    COUNT(*) AS count
FROM lottery_programs;

-- Check digital human config
SELECT
    'Digital Human Configuration' AS data_name,
    CASE
        WHEN COUNT(*) >= 1 THEN '✓ INSERTED'
        ELSE '✗ MISSING'
    END AS status,
    COUNT(*) AS count
FROM digital_human_configs;

-- Check voice configs
SELECT
    'Voice Configurations' AS data_name,
    CASE
        WHEN COUNT(*) >= 2 THEN '✓ INSERTED'
        ELSE '✗ INCOMPLETE'
    END AS status,
    COUNT(*) AS count
FROM voice_configs;

-- ============================================================================
-- 8. Check indexes
-- ============================================================================
SELECT '=== Checking Important Indexes ===' AS test_name;

SELECT
    TABLE_NAME AS table_name,
    INDEX_NAME AS index_name,
    CASE
        WHEN INDEX_NAME IN ('PRIMARY', 'app_key', 'device_id', 'config_key', 'style_id',
                           'bank_id', 'program_id', 'human_id')
        THEN '✓ EXISTS'
        ELSE '✗ MISSING'
    END AS status
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'jc_ai'
  AND TABLE_NAME IN ('applications', 'devices', 'app_configs', 'style_configs',
                     'question_banks', 'lottery_programs', 'digital_human_configs')
  AND INDEX_NAME IN ('PRIMARY', 'app_key', 'device_id', 'config_key', 'style_id',
                     'bank_id', 'program_id', 'human_id')
ORDER BY TABLE_NAME, INDEX_NAME;

-- ============================================================================
-- 9. Test view queries
-- ============================================================================
SELECT '=== Testing View Queries ===' AS test_name;

-- Test v_application_stats
SELECT
    'v_application_stats' AS view_name,
    CASE
        WHEN COUNT(*) > 0 THEN '✓ WORKING'
        ELSE '✗ NO DATA'
    END AS status,
    COUNT(*) AS count
FROM v_application_stats;

-- Test v_active_devices
SELECT
    'v_active_devices' AS view_name,
    '✓ QUERY EXECUTED' AS status,
    COUNT(*) AS count
FROM v_active_devices;

-- Test v_push_summary
SELECT
    'v_push_summary' AS view_name,
    '✓ QUERY EXECUTED' AS status,
    COUNT(*) AS count
FROM v_push_summary;

-- ============================================================================
-- 10. Summary
-- ============================================================================
SELECT '=== Verification Summary ===' AS test_name;

SELECT
    'Tables' AS item,
    (SELECT COUNT(*) FROM information_schema.TABLES
     WHERE TABLE_SCHEMA = 'jc_ai'
       AND TABLE_NAME IN ('applications', 'devices', 'app_configs', 'style_configs',
                          'question_banks', 'lottery_programs', 'digital_human_configs',
                          'voice_configs', 'config_push_history', 'device_push_status',
                          'config_backups', 'config_sync_logs')) AS created,
    '12' AS expected,
    CASE
        WHEN (SELECT COUNT(*) FROM information_schema.TABLES
              WHERE TABLE_SCHEMA = 'jc_ai'
                AND TABLE_NAME IN ('applications', 'devices', 'app_configs', 'style_configs',
                                   'question_banks', 'lottery_programs', 'digital_human_configs',
                                   'voice_configs', 'config_push_history', 'device_push_status',
                                   'config_backups', 'config_sync_logs')) = 12
        THEN '✓ PASS'
        ELSE '✗ FAIL'
    END AS status
UNION ALL
SELECT
    'Views',
    (SELECT COUNT(*) FROM information_schema.VIEWS
     WHERE TABLE_SCHEMA = 'jc_ai'
       AND TABLE_NAME IN ('v_application_stats', 'v_active_devices', 'v_push_summary')),
    '3',
    CASE
        WHEN (SELECT COUNT(*) FROM information_schema.VIEWS
              WHERE TABLE_SCHEMA = 'jc_ai'
                AND TABLE_NAME IN ('v_application_stats', 'v_active_devices', 'v_push_summary')) = 3
        THEN '✓ PASS'
        ELSE '✗ FAIL'
    END
UNION ALL
SELECT
    'Stored Procedures',
    (SELECT COUNT(*) FROM information_schema.ROUTINES
     WHERE ROUTINE_SCHEMA = 'jc_ai'
       AND ROUTINE_TYPE = 'PROCEDURE'
       AND ROUTINE_NAME IN ('sp_register_device', 'sp_backup_config', 'sp_update_device_status')),
    '3',
    CASE
        WHEN (SELECT COUNT(*) FROM information_schema.ROUTINES
              WHERE ROUTINE_SCHEMA = 'jc_ai'
                AND ROUTINE_TYPE = 'PROCEDURE'
                AND ROUTINE_NAME IN ('sp_register_device', 'sp_backup_config', 'sp_update_device_status')) = 3
        THEN '✓ PASS'
        ELSE '✗ FAIL'
    END
UNION ALL
SELECT
    'Triggers',
    (SELECT COUNT(*) FROM information_schema.TRIGGERS
     WHERE TRIGGER_SCHEMA = 'jc_ai'
       AND TRIGGER_NAME = 'tr_devices_inactive_check'),
    '1',
    CASE
        WHEN (SELECT COUNT(*) FROM information_schema.TRIGGERS
              WHERE TRIGGER_SCHEMA = 'jc_ai'
                AND TRIGGER_NAME = 'tr_devices_inactive_check') = 1
        THEN '✓ PASS'
        ELSE '✗ FAIL'
    END
UNION ALL
SELECT
    'Initial Data',
    (SELECT COUNT(*) FROM applications WHERE app_key = 'ai_activity_show')
    + (SELECT COUNT(*) FROM app_configs WHERE config_key = 'global')
    + (SELECT COUNT(*) FROM style_configs)
    + (SELECT COUNT(*) FROM question_banks)
    + (SELECT COUNT(*) FROM lottery_programs)
    + (SELECT COUNT(*) FROM digital_human_configs)
    + (SELECT COUNT(*) FROM voice_configs),
    '11',
    CASE
        WHEN ((SELECT COUNT(*) FROM applications WHERE app_key = 'ai_activity_show')
              + (SELECT COUNT(*) FROM app_configs WHERE config_key = 'global')
              + (SELECT COUNT(*) FROM style_configs)
              + (SELECT COUNT(*) FROM question_banks)
              + (SELECT COUNT(*) FROM lottery_programs)
              + (SELECT COUNT(*) FROM digital_human_configs)
              + (SELECT COUNT(*) FROM voice_configs)) >= 11
        THEN '✓ PASS'
        ELSE '✗ FAIL'
    END;

-- ============================================================================
-- Verification Complete
-- ============================================================================
SELECT '=== Verification Complete ===' AS message;
