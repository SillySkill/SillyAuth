-- 验证认证系统所需的数据库表是否存在
-- 运行此脚本以检查数据库schema

\c sillymd;

-- 检查users表
SELECT
    'users' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN '✓ 存在' ELSE '✗ 不存在' END as status;

-- 检查password_reset_tokens表
SELECT
    'password_reset_tokens' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'password_reset_tokens') THEN '✓ 存在' ELSE '✗ 不存在' END as status;

-- 检查email_verifications表
SELECT
    'email_verifications' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'email_verifications') THEN '✓ 存在' ELSE '✗ 不存在' END as status;

-- 查看users表结构
\d users;

-- 查看password_reset_tokens表结构
\d password_reset_tokens;

-- 查看email_verifications表结构
\d email_verifications;

-- 统计表记录数
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'password_reset_tokens', COUNT(*) FROM password_reset_tokens
UNION ALL
SELECT 'email_verifications', COUNT(*) FROM email_verifications;

-- 检查password_reset_tokens索引
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'password_reset_tokens';

-- 检查email_verifications索引
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'email_verifications';

-- 检查是否有未使用的password reset tokens（可用于调试）
SELECT
    prt.id,
    u.email,
    prt.expires_at,
    prt.used_at,
    CASE
        WHEN prt.used_at IS NOT NULL THEN '已使用'
        WHEN prt.expires_at < NOW() THEN '已过期'
        ELSE '有效'
    END as token_status
FROM password_reset_tokens prt
LEFT JOIN users u ON prt.user_id = u.id
ORDER BY prt.created_at DESC
LIMIT 10;
