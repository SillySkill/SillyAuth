#!/usr/bin/env python3
"""
社交化种子数据导入脚本
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "sillymd"),
    "user": os.getenv("DB_USER", "sillymd"),
    "password": os.getenv("DB_PASSWORD", "sillymd2024!!")
}

def get_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG)

def import_social_seeds():
    """导入社交化种子数据"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        print("开始导入社交化种子数据...")

        # 插入用户
        users = [
            ('阿杰Code', 'ajiecode@seed.local', 'vendor', 'gold', 'https://randomuser.me/api/portraits/men/32.jpg', '前端架构师，10年开发经验，开源社区活跃贡献者'),
            ('小雨设计', 'xiaoyu@seed.local', 'vendor', 'gold', 'https://randomuser.me/api/portraits/women/44.jpg', 'UI/UX设计师，曾任职知名互联网公司'),
            ('大鹏AI', 'dapeng@seed.local', 'vendor', 'gold', 'https://randomuser.me/api/portraits/men/75.jpg', 'AI算法工程师，专注机器学习和深度学习'),
            ('酷酷的磊', 'kuku_lei@seed.local', 'vendor', 'premium', 'https://randomuser.me/api/portraits/men/46.jpg', '全栈工程师，擅长Node.js和Python'),
            ('静静数据', 'jingjing@seed.local', 'vendor', 'premium', 'https://randomuser.me/api/portraits/women/17.jpg', '数据分析师，专注大数据和可视化'),
            ('老张Dev', 'oldzhang@seed.local', 'vendor', 'premium', 'https://randomuser.me/api/portraits/men/22.jpg', '资深后端工程师，15年架构经验'),
            ('程序员小周', 'xiaozhou@seed.local', 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/85.jpg', '独立开发者，喜欢分享技术心得'),
            ('设计师露露', 'lulu_design@seed.local', 'vendor', 'normal', 'https://randomuser.me/api/portraits/women/28.jpg', '自由设计师，擅长品牌设计和插画'),
            ('测试大师老孙', 'sun_test@seed.local', 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/67.jpg', '测试工程师，自动化测试专家'),
            ('产品小姐姐', 'pm_lady@seed.local', 'vendor', 'normal', 'https://randomuser.me/api/portraits/women/65.jpg', '产品经理，专注B端产品设计'),
            ('运维小哥', 'ops_guy@seed.local', 'vendor', 'normal', 'https://randomuser.me/api/portraits/men/91.jpg', '运维工程师，DevOps实践者'),
            ('数据姐姐', 'data_sister@seed.local', 'vendor', 'normal', 'https://randomuser.me/api/portraits/women/42.jpg', '数据科学家，AI领域研究者'),
            ('小白学编程', 'xiaobai@seed.local', 'user', 'normal', 'https://randomuser.me/api/portraits/men/12.jpg', '编程初学者，正在努力学习中'),
        ]

        for username, email, role, level, avatar, bio in users:
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, vendor_level, avatar_url, bio, is_active, is_verified, preferred_language, theme_preference)
                VALUES (%s, %s, md5('demo123456'), %s, %s, %s, %s, true, true, 'zh-CN', 'tech-blue')
                ON CONFLICT (username) DO NOTHING
                RETURNING id
            """, (username, email, role, level, avatar, bio))
            result = cur.fetchone()
            if result:
                print(f"✓ 创建用户: {username}")

        # 插入Skills
        skills = [
            ('jwt_auth_master', 'JWT认证系统完整版', '完整的JWT认证解决方案，支持用户注册、登录、密码重置、权限管理等核心功能。包含访问令牌和刷新令牌机制，确保系统安全。内置RBAC权限控制模型，可灵活配置用户角色和权限。', '阿杰Code', 'tech', 'free', '2.1.0', 0, True, 15234, 5678, 4.9, 1234, 30),
            ('react_dashboard_kit', 'React管理后台模板', '基于React18 + TypeScript + Ant Design的现代化管理后台模板，包含20+常用组件，支持动态路由、权限管理、主题切换等功能。开箱即用，快速搭建企业级后台系统。', '小雨设计', 'tech', 'free', '1.5.0', 0, True, 12345, 4567, 4.8, 987, 25),
            ('python_data_toolkit', 'Python数据分析工具集', '专业级Python数据分析工具包，集成Pandas、NumPy、Matplotlib等主流库。提供数据清洗、转换、可视化等50+实用函数，适用于数据分析、机器学习预处理等场景。', '大鹏AI', 'tech', 'free', '3.2.0', 0, True, 9876, 3456, 4.7, 765, 20),
            ('code_review_ai', 'AI代码审查助手', '基于AI的智能代码审查工具，支持Python、JavaScript、Java等多种语言。自动检测代码质量问题、安全漏洞、性能优化点，并提供详细的改进建议。集成Git Hooks，在提交代码前自动检查。', '程序员小周', 'tech', 'free', '1.0.0', 0, True, 8765, 2345, 4.6, 543, 15),
            ('ai_trading_bot_pro', 'AI量化交易机器人Pro', '专业级AI交易机器人，支持多种交易策略，适用于股票、期货、数字货币等市场。内置智能风控系统，回测功能完善，已帮助500+用户实现稳定盈利。提供完整的API接口和详细文档。', '阿杰Code', 'tech', 'commercial', '2.5.0', 2999, True, 23456, 1234, 4.9, 456, 35),
            ('enterprise_crm_system', '企业级CRM客户管理系统', '完整的企业CRM解决方案，包含客户管理、销售漏斗、合同管理、数据分析等模块。支持多租户、权限细化、自定义字段等功能。已服务于100+中小企业。', '老张Dev', 'business', 'commercial', '1.8.0', 5999, True, 18765, 890, 4.8, 321, 40),
            ('smart_marketing_platform', '智能营销自动化平台', '一站式营销自动化解决方案，支持邮件营销、短信营销、社交媒体管理、营销自动化等功能。集成主流营销平台API，提供详细的营销数据分析和报表。', '酷酷的磊', 'business', 'commercial', '3.0.0', 8999, True, 15678, 678, 4.7, 234, 28),
            ('design_system_kit', '企业级设计系统组件库', '完整的企业级设计系统，包含100+UI组件、设计规范、图标库、配色方案等。支持Figma、Sketch等设计工具，提供React/Vue等多框架组件库。帮助团队统一设计语言，提升开发效率。', '小雨设计', 'design', 'commercial', '2.0.0', 4999, True, 14320, 1234, 4.9, 567, 22),
            ('data_visualization_suite', '大数据可视化套件', '基于D3.js和ECharts的数据可视化解决方案，提供50+种图表类型，支持实时数据更新、交互式图表、大屏展示等功能。适用于数据分析、运营监控、智慧城市等场景。', '静静数据', 'tech', 'commercial', '1.5.0', 3999, True, 12123, 987, 4.8, 432, 18),
        ]

        for skill_id, name, desc, author, category, type_, version, price, featured, views, downloads, rating, reviews, days_ago in skills:
            published_at = datetime.now() - timedelta(days=days_ago)

            cur.execute("""
                INSERT INTO skills (
                    skill_id, name, description, author_id,
                    category, type, version, status,
                    price, is_featured, view_count, download_count,
                    rating_avg, rating_count, published_at
                )
                VALUES (
                    %s, %s, %s,
                    (SELECT id FROM users WHERE username = %s LIMIT 1),
                    %s, %s, %s, 'approved',
                    %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (skill_id) DO NOTHING
                RETURNING id
            """, (skill_id, name, desc, author, category, type_, version, price, featured, views, downloads, rating, reviews, published_at))

            result = cur.fetchone()
            if result:
                print(f"✓ 创建Skill: {name}")

        conn.commit()
        print("\n✅ 社交化种子数据导入完成！")

        # 显示统计
        cur.execute("SELECT COUNT(*) as count FROM users WHERE email LIKE '%@seed.local'")
        user_count = cur.fetchone()['count']

        cur.execute("""
            SELECT COUNT(*) as count FROM skills
            WHERE skill_id LIKE 'jwt_%' OR skill_id LIKE 'react_%'
            OR skill_id LIKE 'python_%' OR skill_id LIKE 'code_%'
            OR skill_id LIKE 'ai_%' OR skill_id LIKE 'enterprise_%'
            OR skill_id LIKE 'smart_%' OR skill_id LIKE 'design_%'
            OR skill_id LIKE 'data_%'
        """)
        skill_count = cur.fetchone()['count']

        print(f"\n统计信息：")
        print(f"  - 用户数量: {user_count}")
        print(f"  - Skills数量: {skill_count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ 导入失败: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import_social_seeds()
