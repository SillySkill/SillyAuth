-- ============================================
-- 社交化种子数据导入脚本
-- ============================================

-- 清理旧种子数据（可选）
-- SELECT clean_seed_data();

-- 插入社交化种子用户
INSERT INTO users (username, email, password_hash, role, vendor_level, avatar_url, bio, is_active, is_verified, preferred_language, theme_preference) VALUES
-- 金牌供应商
('阿杰Code', 'ajiecode@seed.local', md5('demo123456'), 'vendor', 'gold', 'https://randomuser.me/api/portraits/men/32.jpg', '前端架构师，10年开发经验，开源社区活跃贡献者', true, true, 'zh-CN', 'tech-blue'),
('小雨设计', 'xiaoyu@seed.local', md5('demo123456'), 'vendor', 'gold', 'https://randomuser.me/api/portraits/women/44.jpg', 'UI/UX设计师，曾任职知名互联网公司', true, true, 'zh-CN', 'tech-blue'),
('大鹏AI', 'dapeng@seed.local', md5('demo123456'), 'vendor', 'gold', 'https://randomuser.me/api/portraits/men/75.jpg', 'AI算法工程师，专注机器学习和深度学习', true, true, 'zh-CN', 'tech-blue'),

-- 优质供应商
('酷酷的磊', 'kuku_lei@seed.local', md5('demo123456'), 'vendor', 'premium', 'https://randomuser.me/api/portraits/men/46.jpg', '全栈工程师，擅长Node.js和Python', true, true, 'zh-CN', 'tech-blue'),
('静静数据', 'jingjing@seed.local', md5('demo123456'), 'vendor', 'premium', 'https://randomuser.me/api/portraits/women/17.jpg', '数据分析师，专注大数据和可视化', true, true, 'zh-CN', 'tech-blue'),
('老张Dev', 'oldzhang@seed.local', md5('demo123456'), 'vendor', 'premium', 'https://randomuser.me/api/portraits/men/22.jpg', '资深后端工程师，15年架构经验', true, true, 'zh-CN', 'tech-blue'),

-- 普通供应商/创作者
('程序员小周', 'xiaozhou@seed.local', md5('demo123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/85.jpg', '独立开发者，喜欢分享技术心得', true, true, 'zh-CN', 'tech-blue'),
('设计师露露', 'lulu_design@seed.local', md5('demo123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/women/28.jpg', '自由设计师，擅长品牌设计和插画', true, true, 'zh-CN', 'tech-blue'),
('测试大师老孙', 'sun_test@seed.local', md5('demo123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/67.jpg', '测试工程师，自动化测试专家', true, true, 'zh-CN', 'tech-blue'),
('产品小姐姐', 'pm_lady@seed.local', md5('demo123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/women/65.jpg', '产品经理，专注B端产品设计', true, true, 'zh-CN', 'tech-blue'),
('运维小哥', 'ops_guy@seed.local', md5('demo123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/91.jpg', '运维工程师，DevOps实践者', true, true, 'zh-CN', 'tech-blue'),
('数据姐姐', 'data_sister@seed.local', md5('demo123456'), 'vendor', 'normal', 'https://randomuser.me/api/portraits/women/42.jpg', '数据科学家，AI领域研究者', true, true, 'zh-CN', 'tech-blue'),

-- 普通用户
('小白学编程', 'xiaobai@seed.local', md5('demo123456'), 'user', 'normal', 'https://randomuser.me/api/portraits/men/12.jpg', '编程初学者，正在努力学习中', true, true, 'zh-CN', 'tech-blue')
ON CONFLICT (username) DO NOTHING;

-- 插入种子 Skills
INSERT INTO skills (
    skill_id, name, description, author_id,
    category, type, version, status,
    price, is_featured, view_count, download_count,
    rating_avg, rating_count, published_at
) VALUES
-- 免费Skills
('jwt_auth_master', 'JWT认证系统完整版', '完整的JWT认证解决方案，支持用户注册、登录、密码重置、权限管理等核心功能。包含访问令牌和刷新令牌机制，确保系统安全。内置RBAC权限控制模型，可灵活配置用户角色和权限。',
    (SELECT id FROM users WHERE username = '阿杰Code' LIMIT 1),
    'tech', 'free', '2.1.0', 'approved',
    0, true, 15234, 5678, 4.9, 1234, CURRENT_TIMESTAMP - INTERVAL '30 days'),

('react_dashboard_kit', 'React管理后台模板', '基于React18 + TypeScript + Ant Design的现代化管理后台模板，包含20+常用组件，支持动态路由、权限管理、主题切换等功能。开箱即用，快速搭建企业级后台系统。',
    (SELECT id FROM users WHERE username = '小雨设计' LIMIT 1),
    'tech', 'free', '1.5.0', 'approved',
    0, true, 12345, 4567, 4.8, 987, CURRENT_TIMESTAMP - INTERVAL '25 days'),

('python_data_toolkit', 'Python数据分析工具集', '专业级Python数据分析工具包，集成Pandas、NumPy、Matplotlib等主流库。提供数据清洗、转换、可视化等50+实用函数，适用于数据分析、机器学习预处理等场景。',
    (SELECT id FROM users WHERE username = '大鹏AI' LIMIT 1),
    'tech', 'free', '3.2.0', 'approved',
    0, true, 9876, 3456, 4.7, 765, CURRENT_TIMESTAMP - INTERVAL '20 days'),

('code_review_ai', 'AI代码审查助手', '基于AI的智能代码审查工具，支持Python、JavaScript、Java等多种语言。自动检测代码质量问题、安全漏洞、性能优化点，并提供详细的改进建议。集成Git Hooks，在提交代码前自动检查。',
    (SELECT id FROM users WHERE username = '程序员小周' LIMIT 1),
    'tech', 'free', '1.0.0', 'approved',
    0, true, 8765, 2345, 4.6, 543, CURRENT_TIMESTAMP - INTERVAL '15 days'),

-- 付费Skills
('ai_trading_bot_pro', 'AI量化交易机器人Pro', '专业级AI交易机器人，支持多种交易策略，适用于股票、期货、数字货币等市场。内置智能风控系统，回测功能完善，已帮助500+用户实现稳定盈利。提供完整的API接口和详细文档。',
    (SELECT id FROM users WHERE username = '阿杰Code' LIMIT 1),
    'tech', 'commercial', '2.5.0', 'approved',
    2999, true, 23456, 1234, 4.9, 456, CURRENT_TIMESTAMP - INTERVAL '35 days'),

('enterprise_crm_system', '企业级CRM客户管理系统', '完整的企业CRM解决方案，包含客户管理、销售漏斗、合同管理、数据分析等模块。支持多租户、权限细化、自定义字段等功能。已服务于100+中小企业。',
    (SELECT id FROM users WHERE username = '老张Dev' LIMIT 1),
    'business', 'commercial', '1.8.0', 'approved',
    5999, true, 18765, 890, 4.8, 321, CURRENT_TIMESTAMP - INTERVAL '40 days'),

('smart_marketing_platform', '智能营销自动化平台', '一站式营销自动化解决方案，支持邮件营销、短信营销、社交媒体管理、营销自动化等功能。集成主流营销平台API，提供详细的营销数据分析和报表。',
    (SELECT id FROM users WHERE username = '酷酷的磊' LIMIT 1),
    'business', 'commercial', '3.0.0', 'approved',
    8999, true, 15678, 678, 4.7, 234, CURRENT_TIMESTAMP - INTERVAL '28 days'),

('design_system_kit', '企业级设计系统组件库', '完整的企业级设计系统，包含100+UI组件、设计规范、图标库、配色方案等。支持Figma、Sketch等设计工具，提供React/Vue等多框架组件库。帮助团队统一设计语言，提升开发效率。',
    (SELECT id FROM users WHERE username = '小雨设计' LIMIT 1),
    'design', 'commercial', '2.0.0', 'approved',
    4999, true, 14320, 1234, 4.9, 567, CURRENT_TIMESTAMP - INTERVAL '22 days'),

('data_visualization_suite', '大数据可视化套件', '基于D3.js和ECharts的数据可视化解决方案，提供50+种图表类型，支持实时数据更新、交互式图表、大屏展示等功能。适用于数据分析、运营监控、智慧城市等场景。',
    (SELECT id FROM users WHERE username = '静静数据' LIMIT 1),
    'tech', 'commercial', '1.5.0', 'approved',
    3999, true, 12123, 987, 4.8, 432, CURRENT_TIMESTAMP - INTERVAL '18 days')
ON CONFLICT (skill_id) DO NOTHING;

-- 插入标签数据
INSERT INTO skill_tags (skill_id, tag) VALUES
-- 免费Skills标签
((SELECT id FROM skills WHERE skill_id = 'jwt_auth_master'), 'JWT'),
((SELECT id FROM skills WHERE skill_id = 'jwt_auth_master'), '认证'),
((SELECT id FROM skills WHERE skill_id = 'jwt_auth_master'), '安全'),
((SELECT id FROM skills WHERE skill_id = 'jwt_auth_master'), 'Node.js'),

((SELECT id FROM skills WHERE skill_id = 'react_dashboard_kit'), 'React'),
((SELECT id FROM skills WHERE skill_id = 'react_dashboard_kit'), 'TypeScript'),
((SELECT id FROM skills WHERE skill_id = 'react_dashboard_kit'), '管理后台'),
((SELECT id FROM skills WHERE skill_id = 'react_dashboard_kit'), 'Ant Design'),

((SELECT id FROM skills WHERE skill_id = 'python_data_toolkit'), 'Python'),
((SELECT id FROM skills WHERE skill_id = 'python_data_toolkit'), '数据分析'),
((SELECT id FROM skills WHERE skill_id = 'python_data_toolkit'), 'Pandas'),
((SELECT id FROM skills WHERE skill_id = 'python_data_toolkit'), '可视化'),

((SELECT id FROM skills WHERE skill_id = 'code_review_ai'), 'AI'),
((SELECT id FROM skills WHERE skill_id = 'code_review_ai'), '代码审查'),
((SELECT id FROM skills WHERE skill_id = 'code_review_ai'), 'Git'),
((SELECT id FROM skills WHERE skill_id = 'code_review_ai'), '自动化'),

-- 付费Skills标签
((SELECT id FROM skills WHERE skill_id = 'ai_trading_bot_pro'), 'AI'),
((SELECT id FROM skills WHERE skill_id = 'ai_trading_bot_pro'), '量化交易'),
((SELECT id FROM skills WHERE skill_id = 'ai_trading_bot_pro'), '机器人'),
((SELECT id FROM skills WHERE skill_id = 'ai_trading_bot_pro'), 'Python'),

((SELECT id FROM skills WHERE skill_id = 'enterprise_crm_system'), 'CRM'),
((SELECT id FROM skills WHERE skill_id = 'enterprise_crm_system'), '企业级'),
((SELECT id FROM skills WHERE skill_id = 'enterprise_crm_system'), '客户管理'),
((SELECT id FROM skills WHERE skill_id = 'enterprise_crm_system'), '销售'),

((SELECT id FROM skills WHERE skill_id = 'smart_marketing_platform'), '营销'),
((SELECT id FROM skills WHERE skill_id = 'smart_marketing_platform'), '自动化'),
((SELECT id FROM skills WHERE skill_id = 'smart_marketing_platform'), '邮件营销'),
((SELECT id FROM skills WHERE skill_id = 'smart_marketing_platform'), '数据分析'),

((SELECT id FROM skills WHERE skill_id = 'design_system_kit'), '设计系统'),
((SELECT id FROM skills WHERE skill_id = 'design_system_kit'), 'UI组件'),
((SELECT id FROM skills WHERE skill_id = 'design_system_kit'), 'React'),
((SELECT id FROM skills WHERE skill_id = 'design_system_kit'), 'Figma'),

((SELECT id FROM skills WHERE skill_id = 'data_visualization_suite'), '可视化'),
((SELECT id FROM skills WHERE skill_id = 'data_visualization_suite'), 'D3.js'),
((SELECT id FROM skills WHERE skill_id = 'data_visualization_suite'), 'ECharts'),
((SELECT id FROM skills WHERE skill_id = 'data_visualization_suite'), '大数据')
ON CONFLICT DO NOTHING;

-- 显示导入结果
SELECT '社交化种子数据导入完成！' as status;

-- 统计数据
SELECT
    (SELECT COUNT(*) FROM users WHERE email LIKE '%@seed.local') as user_count,
    (SELECT COUNT(*) FROM skills WHERE skill_id LIKE 'seed_%' OR skill_id LIKE '%_pro' OR skill_id LIKE '%_kit' OR skill_id LIKE '%_system' OR skill_id LIKE '%_platform' OR skill_id LIKE '%_suite') as skill_count,
    (SELECT COUNT(*) FROM skill_tags) as tag_count;
