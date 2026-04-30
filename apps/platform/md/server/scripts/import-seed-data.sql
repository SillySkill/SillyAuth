-- ============================================
-- 种子数据导入脚本
-- ============================================

-- 插入种子用户
INSERT INTO users (username, email, password_hash, role, vendor_level, avatar_url, bio, is_active, is_verified, preferred_language, theme_preference) VALUES
('wang1990', 'wang1990@seed.local', md5('wang1990123456'), 'vendor', 'gold', 'https://randomuser.me/api/portraits/men/32.jpg', '现任阿里巴巴高级前端工程师，专注前端领域8年。', true, true, 'zh-CN', 'tech-blue'),
('li_dev', 'li_dev@seed.local', md5('li_dev123456'), 'vendor', 'premium', 'https://randomuser.me/api/portraits/women/45.jpg', '前字节跳动设计总监，现自由职业。10年设计经验。', true, true, 'zh-CN', 'tech-blue'),
('zhang_pro', 'zhang_pro@seed.local', md5('zhang_pro123456'), 'vendor', 'gold', 'https://randomuser.me/api/portraits/men/67.jpg', '腾讯数据科学家，专注AI应用开发。', true, true, 'zh-CN', 'tech-blue'),
('chen_ai', 'chen_ai@seed.local', md5('chen_ai123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/91.jpg', '独立AI开发者，开源爱好者。', true, true, 'zh-CN', 'tech-blue'),
('demo_user', 'demo@seed.local', md5('demo123456'), 'user', 'normal', 'https://randomuser.me/api/portraits/men/12.jpg', '演示用户账号', true, true, 'zh-CN', 'tech-blue')
ON CONFLICT (username) DO NOTHING;

-- 插入种子 Skills
INSERT INTO skills (
    skill_id, name, description, author_id,
    category, type, version, status,
    price, is_featured, view_count, download_count,
    rating_avg, rating_count, published_at
) VALUES
('seed_ai_trading_bot', 'AI交易机器人Pro', '专业级AI交易机器人，支持多种交易策略，适用于量化交易场景。内置智能风控系统，已帮助500+用户实现稳定盈利。',
    (SELECT id FROM users WHERE username = 'wang1990' LIMIT 1),
    'tech', 'commercial', '1.0.0', 'approved',
    2999, true, 1234, 567, 4.8, 120, CURRENT_TIMESTAMP),

('seed_data_analysis_master', 'Python数据分析大师', '专业级Python数据分析工具，支持数据清洗、可视化、建模，适用于电商运营、金融分析场景。内置50+种分析模板。',
    (SELECT id FROM users WHERE username = 'zhang_pro' LIMIT 1),
    'tech', 'commercial', '1.0.0', 'approved',
    5999, true, 2345, 890, 4.9, 230, CURRENT_TIMESTAMP),

('seed_code_review_helper', '代码审查助手', 'AI驱动的代码审查工具，支持多种编程语言，自动检测代码质量问题，提升团队代码质量。',
    (SELECT id FROM users WHERE username = 'li_dev' LIMIT 1),
    'tech', 'free', '1.0.0', 'approved',
    0, true, 3456, 1234, 4.7, 450, CURRENT_TIMESTAMP),

('seed_automation_platform', '自动化测试平台', '一站式自动化测试解决方案，支持Web、API、移动端测试，可视化测试流程设计。',
    (SELECT id FROM users WHERE username = 'wang1990' LIMIT 1),
    'tech', 'commercial', '1.0.0', 'approved',
    12999, true, 890, 234, 4.6, 56, CURRENT_TIMESTAMP),

('seed_doc_generator', '智能文档生成器', '基于AI的文档自动生成工具，支持API文档、用户手册、技术文档等多种类型。',
    (SELECT id FROM users WHERE username = 'chen_ai' LIMIT 1),
    'tech', 'free', '1.0.0', 'approved',
    0, true, 1567, 678, 4.5, 123, CURRENT_TIMESTAMP)
ON CONFLICT (skill_id) DO NOTHING;

-- 创建种子数据管理表
CREATE TABLE IF NOT EXISTS seed_user_mapping (
    seed_id VARCHAR(50) PRIMARY KEY,
    real_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE seed_user_mapping IS '种子数据用户映射表（用于清理种子数据）';

-- 建立映射关系
INSERT INTO seed_user_mapping (seed_id, real_id)
SELECT username, id FROM users WHERE email LIKE '%@seed.local'
ON CONFLICT (seed_id) DO NOTHING;

-- 创建种子数据清理函数
CREATE OR REPLACE FUNCTION clean_seed_data()
RETURNS TEXT AS $$
DECLARE
    user_count INT;
    skill_count INT;
BEGIN
    -- 统计
    SELECT COUNT(*) INTO user_count FROM users WHERE email LIKE '%@seed.local';
    SELECT COUNT(*) INTO skill_count FROM skills WHERE skill_id LIKE 'seed_%';

    -- 删除种子 Skills 相关数据
    DELETE FROM skill_comments WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM skill_favorites WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM skill_tags WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM reviews WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM skill_versions WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM skill_dependencies WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%') OR depends_on_skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM licenses WHERE skill_id IN (SELECT id FROM skills WHERE skill_id LIKE 'seed_%');
    DELETE FROM skills WHERE skill_id LIKE 'seed_%';

    -- 删除种子用户相关数据
    DELETE FROM user_preferences WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM notifications WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM point_transactions WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM team_members WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM teams WHERE owner_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM skill_comments WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM skill_favorites WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@seed.local');
    DELETE FROM users WHERE email LIKE '%@seed.local';

    -- 删除映射表
    DELETE FROM seed_user_mapping;

    RETURN format('已删除 %d 个种子用户和 %d 个种子 Skills', user_count, skill_count);
END;
$$ LANGUAGE plpgsql;

-- 创建种子数据统计函数
CREATE OR REPLACE FUNCTION get_seed_stats()
RETURNS TABLE(
    user_count BIGINT,
    skill_count BIGINT,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM users WHERE email LIKE '%@seed.local')::BIGINT,
        (SELECT COUNT(*) FROM skills WHERE skill_id LIKE 'seed_%')::BIGINT,
        '种子数据统计'::TEXT;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION clean_seed_data() IS '清理所有种子数据的函数';
COMMENT ON FUNCTION get_seed_stats() IS '获取种子数据统计信息';

-- 显示导入结果
SELECT '种子数据导入完成！' as status;

SELECT * FROM get_seed_stats();
