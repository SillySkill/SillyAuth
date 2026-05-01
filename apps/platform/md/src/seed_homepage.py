"""
Seed homepage data: create articles & categories & tutorials & config_data tables, insert seed data.
Uses CREATE TABLE IF NOT EXISTS to avoid destroying existing production data.
"""
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["APP_ENV"] = "development"

import core.config  # noqa
from core.db_adapter import get_db_cursor

now = datetime.utcnow()


def ensure_tables(cur):
    """Create tables if they don't exist (non-destructive)."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            slug VARCHAR(200),
            description TEXT,
            parent_id INTEGER,
            icon VARCHAR(100),
            color VARCHAR(50),
            article_count INTEGER DEFAULT 0,
            doc_count INTEGER DEFAULT 0,
            category_type VARCHAR(50) DEFAULT 'article',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            content TEXT,
            type VARCHAR(50) DEFAULT 'article',
            slug VARCHAR(500),
            excerpt TEXT,
            summary TEXT,
            cover_image VARCHAR(1000),
            tags TEXT,
            featured BOOLEAN DEFAULT FALSE,
            is_featured BOOLEAN DEFAULT FALSE,
            is_hot BOOLEAN DEFAULT FALSE,
            is_top BOOLEAN DEFAULT FALSE,
            status VARCHAR(50) DEFAULT 'draft',
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            category_id INTEGER REFERENCES categories(id),
            author_id INTEGER,
            metadata TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            published_at TIMESTAMP WITH TIME ZONE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutorials (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            slug VARCHAR(500),
            category VARCHAR(200),
            duration VARCHAR(50),
            level VARCHAR(50) DEFAULT '初级',
            icon VARCHAR(100),
            gradient VARCHAR(500),
            cover_image VARCHAR(1000),
            status VARCHAR(50) DEFAULT 'published',
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            author_id INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            published_at TIMESTAMP WITH TIME ZONE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS config_data (
            id SERIAL PRIMARY KEY,
            category VARCHAR(100) NOT NULL,
            name VARCHAR(200) NOT NULL,
            data JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(category, name)
        )
    """)
    print("Tables created/verified successfully")


def _seed_config(cur, category, name, data):
    """Insert a single config_data entry if not exists."""
    cur.execute(
        "SELECT 1 FROM config_data WHERE category=%s AND name=%s",
        (category, name)
    )
    if cur.fetchone():
        return
    cur.execute(
        "INSERT INTO config_data (category, name, data, created_at, updated_at) VALUES (%s,%s,%s,%s,%s)",
        (category, name, json.dumps(data, ensure_ascii=False), now, now)
    )


def seed_categories(cur):
    """Seed categories if empty."""
    cur.execute("SELECT COUNT(*) as c FROM categories")
    if cur.fetchone()["c"] > 0:
        print("Categories already exist, skipping")
        return

    categories = [
        ("AI 入门", "ai-intro", "AI 入门相关文章", None, "🤖", "#0066FF", 0, "article"),
        ("提示工程", "prompt-engineering", "提示工程技巧与实践", None, "💡", "#F59E0B", 0, "article"),
        ("模型微调", "fine-tuning", "模型微调教程与案例", None, "🔧", "#10B981", 0, "article"),
        ("工具使用", "tools", "AI 工具使用指南", None, "🛠️", "#8B5CF6", 0, "article"),
        ("技术", "tech", "技术开发相关", None, "⚡", "#667eea", 0, "article"),
        ("产品", "product", "产品管理相关", None, "📋", "#f093fb", 0, "article"),
        ("设计", "design", "设计相关", None, "🎨", "#4facfe", 0, "article"),
        ("运营", "ops", "运营相关", None, "📊", "#fa709a", 0, "article"),
    ]
    for cat in categories:
        cur.execute(
            """INSERT INTO categories (name, slug, description, parent_id, icon, color, article_count, category_type, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (*cat, now, now),
        )
    print(f"Seeded {len(categories)} categories")


def seed_articles(cur):
    """Seed articles as hero slides and features."""
    cur.execute("SELECT COUNT(*) as c FROM articles")
    if cur.fetchone()["c"] > 0:
        print("Articles already exist, skipping")
        return

    articles = [
        {
            "title": "挺傻的 Skills 全域资产托管平台",
            "content": "全球首个 AI Skills 供应商市场",
            "slug": "sillymd-skills-platform",
            "summary": "承认自己有时候挺傻的，这是智慧的开始。打造全球首个 AI Skills 供应商市场，让 AI 能力资产化、可交易、可复用",
            "cover_image": "/assets/hero/lay-1080.mp4",
            "type": "video",
            "tags": "AI,Skills,平台",
            "featured": True, "is_featured": True, "is_hot": True, "is_top": True,
            "status": "published", "view_count": 10000, "like_count": 856,
            "category_id": 5, "author_id": 33,
            "metadata": json.dumps({
                "badge": "现已支持 10,000+ Skills",
                "title_parts": [
                    {"text": "挺傻的 Skills", "gradient": True, "break": True},
                    {"text": "全域资产托管平台", "gradient": False, "break": False}
                ],
                "actions": [
                    {"url": "/skills", "style": "btn-primary btn-lg", "icon": "fas fa-rocket", "label": "开始探索"},
                    {"url": "/register", "style": "btn-secondary btn-lg", "icon": "fas fa-user-plus", "label": "成为供应商"}
                ]
            })
        },
        {
            "title": "AI 驱动内容安全保障",
            "content": "三级审核流程，确保每一份 Skill 都经过严格的质量检查",
            "slug": "ai-content-security",
            "summary": "三级审核流程，确保每一份 Skill 都经过严格的质量检查，准确率高达 99.9%",
            "cover_image": "/assets/hero/man-1080.mp4",
            "type": "video",
            "tags": "AI,安全,审核",
            "featured": True, "is_featured": True, "is_hot": True, "is_top": True,
            "status": "published", "view_count": 8500, "like_count": 624,
            "category_id": 1, "author_id": 33,
            "metadata": json.dumps({
                "badge": "AI 驱动",
                "title_parts": [
                    {"text": "内容安全保障", "gradient": True, "break": True},
                    {"text": "AI 驱动", "gradient": False, "break": False}
                ],
                "actions": [
                    {"url": "/docs", "style": "btn-primary btn-lg", "icon": "fas fa-shield-alt", "label": "了解审核流程"},
                    {"url": "/tutorials", "style": "btn-secondary btn-lg", "icon": "fas fa-play", "label": "观看演示"}
                ]
            })
        },
        {
            "title": "SillyClaw 自动化引擎",
            "content": "强大的自动化工作流引擎",
            "slug": "sillyclaw-automation",
            "summary": "SillyClaw 自动化引擎，连接 AI Skills 与实际业务场景，实现端到端的智能化工作流程。",
            "cover_image": "/assets/hero/sillyclaw.mp4",
            "type": "video",
            "tags": "自动化,SillyClaw,引擎",
            "featured": True, "is_featured": True, "is_hot": True, "is_top": True,
            "status": "published", "view_count": 7200, "like_count": 530,
            "category_id": 4, "author_id": 33,
            "metadata": json.dumps({
                "badge": "自动化引擎",
                "title_parts": [
                    {"text": "SillyClaw", "gradient": True, "break": True},
                    {"text": "自动化引擎", "gradient": False, "break": False}
                ],
                "actions": [
                    {"url": "/downloads", "style": "btn-primary btn-lg", "icon": "fas fa-download", "label": "免费下载"},
                    {"url": "/docs", "style": "btn-secondary btn-lg", "icon": "fas fa-book", "label": "查看文档"}
                ]
            })
        },
        # Features for team section
        {
            "title": "团队工作空间",
            "content": "为每个团队创建专属工作空间，支持多项目并行管理。团队成员可以共享 Skills 资源。",
            "slug": "team-workspace",
            "summary": "为每个团队创建专属工作空间，支持多项目并行管理。团队成员可以共享 Skills 资源，协作完成项目交付。",
            "cover_image": "", "type": "feature", "tags": "团队,工作空间",
            "featured": False, "is_featured": False, "is_hot": True, "is_top": False,
            "status": "published", "view_count": 3200, "like_count": 198,
            "category_id": 4, "author_id": 33,
            "metadata": json.dumps({
                "icon": "🏢",
                "items": ["独立团队域名", "多级权限管理体系", "成员角色灵活配置", "团队资产集中管理"]
            })
        },
        {
            "title": "项目协作管理",
            "content": "以项目为单位组织 Skills 资源，支持跨部门协作。",
            "slug": "project-collaboration",
            "summary": "以项目为单位组织 Skills 资源，支持跨部门协作。技术、产品、设计、市场、运营团队无缝配合。",
            "cover_image": "", "type": "feature", "tags": "项目,协作",
            "featured": False, "is_featured": False, "is_hot": True, "is_top": False,
            "status": "published", "view_count": 2800, "like_count": 156,
            "category_id": 4, "author_id": 33,
            "metadata": json.dumps({
                "icon": "📦",
                "items": ["项目级 Skills 仓库", "依赖关系可视化", "版本对比与回滚", "协作编辑与评论"]
            })
        },
        {
            "title": "跨领域协作",
            "content": "打破技术、产品、设计、市场、运营之间的壁垒。用 Skills 标准统一所有工作文档和流程。",
            "slug": "cross-domain-collaboration",
            "summary": "打破技术、产品、设计、市场、运营之间的壁垒。用 Skills 标准统一所有工作文档和流程。",
            "cover_image": "", "type": "feature", "tags": "协作,跨领域",
            "featured": False, "is_featured": False, "is_hot": True, "is_top": False,
            "status": "published", "view_count": 2400, "like_count": 132,
            "category_id": 4, "author_id": 33,
            "metadata": json.dumps({
                "icon": "🔗",
                "items": ["统一的 Skills 格式", "跨领域资源共享", "协作流程标准化", "知识沉淀与复用"]
            })
        },
    ]

    for i, a in enumerate(articles):
        created = now - timedelta(days=30 - i * 5)
        published = now - timedelta(days=28 - i * 5)
        cur.execute(
            """INSERT INTO articles (title, content, type, slug, excerpt, summary, cover_image,
               tags, featured, is_featured, is_hot, is_top, status, view_count, like_count,
               category_id, author_id, metadata, created_at, updated_at, published_at)
               VALUES (%(title)s, %(content)s, %(type)s, %(slug)s, %(summary)s, %(summary)s,
               %(cover_image)s, %(tags)s, %(featured)s, %(is_featured)s, %(is_hot)s, %(is_top)s,
               %(status)s, %(view_count)s, %(like_count)s, %(category_id)s, %(author_id)s,
               %(metadata)s, %(created)s, %(updated)s, %(published)s)""",
            {**a, "created": created, "updated": now, "published": published},
        )
    print(f"Seeded {len(articles)} articles")


def seed_tutorials(cur):
    """Seed featured tutorials for the learning center section."""
    cur.execute("SELECT COUNT(*) as c FROM tutorials")
    if cur.fetchone()["c"] > 0:
        print("Tutorials already exist, skipping")
        return

    tutorials = [
        {
            "title": "SillyClaw + SillyMD 快速上手",
            "description": "从零开始学习如何使用 SillyClaw 客户端连接 SillyMD 平台，快速创建你的第一个自动化工作流。",
            "slug": "sillyclaw-quickstart",
            "category": "入门教程", "duration": "8分钟", "level": "初级",
            "icon": "🎬", "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "cover_image": "", "status": "published", "view_count": 12500, "like_count": 856,
        },
        {
            "title": "Skills 发布全流程指南",
            "description": "详细讲解如何从零开始开发一个完整的 Skill，包括目录结构、配置文件编写、测试调试和发布审核。",
            "slug": "skills-publish-guide",
            "category": "进阶教程", "duration": "15分钟", "level": "中级",
            "icon": "📦", "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            "cover_image": "", "status": "published", "view_count": 9800, "like_count": 624,
        },
        {
            "title": "SillyMD API 接口文档",
            "description": "完整的 RESTful API 文档，涵盖用户认证、技能管理、订单处理、支付集成等所有接口的详细说明。",
            "slug": "api-docs",
            "category": "开发文档", "duration": "30分钟", "level": "高级",
            "icon": "🔧", "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
            "cover_image": "", "status": "published", "view_count": 7500, "like_count": 412,
        },
    ]

    for t in tutorials:
        published = now - timedelta(days=15)
        cur.execute(
            """INSERT INTO tutorials (title, description, slug, category, duration, level,
               icon, gradient, cover_image, status, view_count, like_count, author_id,
               created_at, updated_at, published_at)
               VALUES (%(title)s, %(description)s, %(slug)s, %(category)s, %(duration)s,
               %(level)s, %(icon)s, %(gradient)s, %(cover_image)s, %(status)s,
               %(view_count)s, %(like_count)s, %(author_id)s, %(created)s, %(updated)s, %(published)s)""",
            {**t, "author_id": 33, "created": now, "updated": now, "published": published},
        )
    print(f"Seeded {len(tutorials)} tutorials")


def seed_learning_categories(cur):
    """Ensure learning center doc categories exist."""
    cur.execute("SELECT COUNT(*) as c FROM categories WHERE category_type = 'doc'")
    if cur.fetchone()["c"] > 0:
        print("Learning categories already exist, skipping")
        return

    docs = [
        ("快速入门", "quickstart", "5分钟上手 SillyMD", 12, "🚀"),
        ("使用指南", "user-guide", "完整功能教程", 28, "📖"),
        ("视频教程", "videos", "手把手视频教学", 45, "🎬"),
        ("常见问题", "faq", "FAQ 疑难解答", 36, "💡"),
        ("API 文档", "api-reference", "开发者接口文档", 18, "🔧"),
        ("最佳实践", "best-practices", "经验技巧分享", 24, "🎯"),
    ]
    for name, slug, desc, count, icon in docs:
        cur.execute(
            """INSERT INTO categories (name, slug, description, icon, doc_count, category_type, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, slug, desc, icon, count, "doc", now, now),
        )
    print(f"Seeded {len(docs)} learning categories")


def update_skills_categories(cur):
    """Update existing skills with varied categories for the skills carousel."""
    cur.execute("SELECT id, category FROM skills ORDER BY id")
    skills = cur.fetchall()
    if not skills:
        print("No skills found in database, skipping category update")
        return
    cats = ["tech", "product", "design", "marketing", "ops"]
    for i, s in enumerate(skills):
        if s["category"] not in cats:
            new_cat = cats[i % len(cats)]
            cur.execute("UPDATE skills SET category = %s WHERE id = %s", (new_cat, s["id"]))
    print(f"Updated {len(skills)} skill categories")


def seed_config_data(cur):
    """Seed config_data for navigation, footer, system settings, pricing, etc."""
    count = 0

    # --- System Settings ---
    _seed_config(cur, "system", "settings", {
        "site_name": "挺傻的网站",
        "tagline": "承认自己有时候挺傻的，这是智慧的开始。SillyMD 是全球首个 AI Skills 供应商市场，让你的 AI 技能资产化、可交易、可复用。",
        "copyright": "2026 SillyMD. All rights reserved.",
        "icp": "沪ICP备2023000000号-1",
        "psb": "沪公网安备 31000000000000号",
    }); count += 1

    # --- Navigation (admin-v2 format: id, label_zh, label_en, url, icon, sort_order, is_visible, children) ---
    _seed_config(cur, "navigation", "navbar", [
        {"id": 1, "label_zh": "探索 Skills", "label_en": "Explore Skills", "url": "/skills", "icon": "", "sort_order": 1, "is_visible": True, "children": []},
        {"id": 2, "label_zh": "供应商市场", "label_en": "Marketplace", "url": "/marketplace", "icon": "", "sort_order": 2, "is_visible": True, "children": []},
        {"id": 3, "label_zh": "教程", "label_en": "Tutorials", "url": "/tutorials", "icon": "", "sort_order": 3, "is_visible": True, "children": []},
        {"id": 4, "label_zh": "下载", "label_en": "Downloads", "url": "/downloads", "icon": "", "sort_order": 4, "is_visible": True, "children": []},
        {"id": 5, "label_zh": "文档", "label_en": "Documentation", "url": "/docs", "icon": "", "sort_order": 5, "is_visible": True, "children": []},
        {"id": 6, "label_zh": "团队协作", "label_en": "Teams", "url": "/teams", "icon": "", "sort_order": 6, "is_visible": True, "children": []},
    ]); count += 1

    # --- Footer Sections ---
    _seed_config(cur, "navigation", "footer_platform", [
        {"label": "探索 Skills", "url": "/skills"},
        {"label": "供应商市场", "url": "/marketplace"},
        {"label": "团队协作", "url": "/teams"},
        {"label": "定价", "url": "/pricing"},
    ]); count += 1

    _seed_config(cur, "navigation", "footer_developer", [
        {"label": "开发文档", "url": "/docs"},
        {"label": "API 参考", "url": "/docs/api-reference"},
        {"label": "社区论坛", "url": "/community"},
        {"label": "帮助中心", "url": "/help"},
    ]); count += 1

    _seed_config(cur, "navigation", "footer_about", [
        {"label": "关于我们", "url": "/about"},
        {"label": "联系我们", "url": "/contact"},
        {"label": "隐私政策", "url": "/privacy"},
        {"label": "服务条款", "url": "/terms"},
    ]); count += 1

    # --- Social Links ---
    _seed_config(cur, "footer", "social_links", [
        {"platform": "抖音", "icon": "fa-tiktok", "url": "#", "qr_image": ""},
        {"platform": "小红书", "icon": "fa-book", "url": "#", "qr_image": ""},
        {"platform": "视频号", "icon": "fa-video", "url": "#", "qr_image": ""},
    ]); count += 1

    # --- Hero Slides ---
    _seed_config(cur, "hero_slides", "slides", [
        {"title_key": "sillymd-platform", "order": 1},
        {"title_key": "ai-security", "order": 2},
        {"title_key": "sillyclaw-automation", "order": 3},
    ]); count += 1

    # --- Market Stats ---
    _seed_config(cur, "market_stats", "stats", [
        {"value": "10,000+", "label": "Skills 资产"},
        {"value": "500+", "label": "认证供应商"},
        {"value": "200+", "label": "企业团队"},
        {"value": "99.9%", "label": "AI 审核准确率"},
    ]); count += 1

    # --- Vendor Tiers ---
    _seed_config(cur, "vendor_tiers", "tiers", [
        {
            "name": "普通供应商", "emoji": "🥉", "bg": "linear-gradient(135deg, #f5f5f5, #e0e0e0)",
            "is_featured": False, "revenue_percent": 70, "revenue_color": "#10B981",
            "description": "刚起步的创作者，可以发布和销售 Skills",
            "features": ["发布免费/付费 Skills", "基础数据统计", "社区支持", "标准支付结算"]
        },
        {
            "name": "优质供应商", "emoji": "🥈", "bg": "linear-gradient(135deg, #e8f5e9, #a5d6a7)",
            "is_featured": True, "is_premium": False, "revenue_percent": 80, "revenue_color": "#059669",
            "description": "累计销售额 >= 1,000 AI Points",
            "features": ["优先搜索展示", "详细数据分析", "优先技术支持", "快速结算（T+7）", "自定义品牌页"]
        },
        {
            "name": "金牌供应商", "emoji": "🥇", "bg": "linear-gradient(135deg, #fff3e0, #ffcc02)",
            "is_featured": False, "is_premium": True, "revenue_percent": 90, "revenue_color": "#D97706",
            "description": "累计销售额 >= 10,000 AI Points，好评率 >= 95%",
            "features": ["首页推荐位", "高级数据分析", "专属客户经理", "即时结算（T+0）", "定制品牌页", "API 优先访问", "联合营销机会"]
        },
    ]); count += 1

    # --- Platform Features ---
    _seed_config(cur, "platform_features", "features", [
        {
            "icon": "fa-solid fa-rocket", "title": "Skills 市场",
            "description": "发现和使用各种 AI Skills，覆盖开发、设计、营销等多个领域",
            "items": ["10,000+ Skills", "免费/付费灵活选择", "评分与评论系统", "一键安装部署"]
        },
        {
            "icon": "fa-solid fa-shield-halved", "title": "内容安全保障",
            "description": "AI 驱动的三级审核体系，确保每个 Skill 的质量和安全性",
            "items": ["AI 自动审核", "专家人工复审", "用户反馈机制", "安全漏洞扫描"]
        },
        {
            "icon": "fa-solid fa-users", "title": "团队协作",
            "description": "打破部门壁垒，实现跨领域无缝协作",
            "items": ["团队专属工作空间", "Skills 资源共享", "多级权限管理", "项目协作工具"]
        },
    ]); count += 1

    # --- Pricing Plans ---
    _seed_config(cur, "pricing", "plan_free", {
        "name": "免费版", "currency": "¥", "amount": 0, "period": "/月",
        "description": "适合个人开发者和小团队试用",
        "is_featured": False, "badge": "",
        "features": [
            {"label": "每月 10 次 Skills 下载", "available": True},
            {"label": "基础技术支持", "available": True},
            {"label": "社区访问权限", "available": True},
            {"label": "1 GB 存储空间", "available": True},
            {"label": "API 访问", "available": True},
            {"label": "高级数据分析", "available": False},
            {"label": "优先技术支持", "available": False},
            {"label": "自定义品牌", "available": False},
        ],
        "cta_text": "免费开始", "cta_url": "/register"
    }); count += 1

    _seed_config(cur, "pricing", "plan_pro", {
        "name": "专业版", "currency": "¥", "amount": 299, "period": "/月",
        "description": "适合专业开发者和活跃的 Skills 创作者",
        "is_featured": True, "badge": "最受欢迎",
        "features": [
            {"label": "无限 Skills 下载", "available": True},
            {"label": "优先技术支持", "available": True},
            {"label": "详细数据分析", "available": True},
            {"label": "50 GB 存储空间", "available": True},
            {"label": "完整 API 访问", "available": True},
            {"label": "自定义品牌页", "available": True},
            {"label": "优先搜索排名", "available": True},
            {"label": "专属客户经理", "available": False},
        ],
        "cta_text": "立即订阅", "cta_url": "/register?plan=pro"
    }); count += 1

    _seed_config(cur, "pricing", "plan_enterprise", {
        "name": "企业版", "currency": "¥", "amount": 999, "period": "/月",
        "description": "适合企业团队和大规模 Skills 管理需求",
        "is_featured": False, "badge": "",
        "features": [
            {"label": "无限 Skills 下载", "available": True},
            {"label": "专属客户经理", "available": True},
            {"label": "定制数据分析报告", "available": True},
            {"label": "500 GB 存储空间", "available": True},
            {"label": "API 优先访问", "available": True},
            {"label": "完整品牌定制", "available": True},
            {"label": "首页推荐位", "available": True},
            {"label": "私有化部署选项", "available": True},
        ],
        "cta_text": "联系我们", "cta_url": "/contact"
    }); count += 1

    # --- About ---
    _seed_config(cur, "about", "content", {
        "title": "关于 SillyMD",
        "subtitle": "承认自己有时候挺傻的，这是智慧的开始",
        "mission": "打造全球首个 AI Skills 供应商市场，让 AI 能力资产化、可交易、可复用",
        "story": "SillyMD 诞生于一个简单的想法：每个人都有自己的专业技能，而这些技能应该可以被 AI 学习和复用。我们相信，通过将人类专业知识和 AI 技术结合，可以创造出前所未有的价值。SillyMD 是一个开放的 Skills 交易平台，让开发者可以将自己的专业知识打包成 Skills，让全球用户都能受益。",
        "values": [
            {"title": "开放共享", "description": "我们相信开放的力量，致力于打造一个开放、透明的 Skills 生态系统", "icon": "🌐"},
            {"title": "质量至上", "description": "严格的审核流程确保每个 Skill 都达到最高质量标准", "icon": "⭐"},
            {"title": "创新驱动", "description": "持续探索 AI 技术的边界，推动 Skills 生态的创新发展", "icon": "💡"},
            {"title": "社区共建", "description": "与全球开发者社区一起，共同建设 Skills 的未来", "icon": "🤝"},
        ],
        "team": [
            {"name": "张三", "role": "创始人 & CEO", "avatar": "", "bio": "连续创业者，AI 技术爱好者"},
            {"name": "李四", "role": "CTO", "avatar": "", "bio": "前大厂技术总监，全栈工程师"},
            {"name": "王五", "role": "产品负责人", "avatar": "", "bio": "10年产品经验，专注AI产品"},
        ],
    }); count += 1

    # --- Privacy Policy ---
    _seed_config(cur, "privacy", "policy_html", {
        "title": "隐私政策",
        "content": "<h2>隐私政策</h2><p>最后更新日期：2026年1月1日</p><h3>1. 信息收集</h3><p>我们收集的信息包括但不限于：注册信息（用户名、邮箱）、使用数据（浏览记录、下载记录）、设备信息（浏览器类型、操作系统）。</p><h3>2. 信息使用</h3><p>我们使用收集的信息用于：提供和改进服务、个性化用户体验、发送服务相关通知、分析和优化平台性能。</p><h3>3. 信息保护</h3><p>我们采用业界标准的安全措施保护您的个人信息，包括数据加密、访问控制和安全审计。</p><h3>4. 第三方共享</h3><p>未经您的明确同意，我们不会将您的个人信息出售或分享给第三方，除非法律要求。</p><h3>5. Cookie 政策</h3><p>我们使用 Cookie 来改善您的浏览体验。您可以在浏览器设置中管理 Cookie 偏好。</p><h3>6. 联系我们</h3><p>如果您对隐私政策有任何疑问，请通过 /contact 页面联系我们。</p>"
    }); count += 1

    # --- Terms of Service ---
    _seed_config(cur, "terms", "terms_html", {
        "title": "服务条款",
        "content": "<h2>服务条款</h2><p>最后更新日期：2026年1月1日</p><h3>1. 接受条款</h3><p>使用 SillyMD 平台即表示您同意遵守本服务条款。如果您不同意，请不要使用我们的服务。</p><h3>2. 用户账户</h3><p>您负责维护账户的安全性，并对账户下的所有活动负责。请勿分享您的账户凭据。</p><h3>3. Skills 内容</h3><p>发布 Skills 时，您保证拥有该内容的所有必要权利，且内容不侵犯任何第三方的知识产权。</p><h3>4. 交易规则</h3><p>所有 Skills 交易均受平台交易规则约束。平台保留取消欺诈性交易的权利。</p><h3>5. 知识产权</h3><p>Skills 的知识产权归创作者所有。平台拥有平台本身的全部知识产权。</p><h3>6. 责任限制</h3><p>在法律允许的最大范围内，SillyMD 不对因使用平台而产生的任何间接损失承担责任。</p><h3>7. 终止</h3><p>我们保留因违反条款而暂停或终止您账户的权利。</p>"
    }); count += 1

    # --- SillyClaw Product ---
    _seed_config(cur, "sillyclaw", "product", {
        "name": "傻福虾盘",
        "description": "即插即用的 AI 技能 USB 设备，内置 100+ 实用 Skills，让 AI 能力触手可及",
        "capacity_range": "8GB - 128GB",
        "production_count": "首批限量 1000 件",
        "purchase_links": {"taobao": "#"},
        "variants": [
            {"capacity": "8GB", "color": "科技蓝", "price": "¥99", "tags": ["入门", "便携"]},
            {"capacity": "32GB", "color": "赛博紫", "price": "¥199", "tags": ["推荐", "高性价比"]},
            {"capacity": "128GB", "color": "尊贵金", "price": "¥399", "tags": ["专业", "大容量"]},
        ]
    }); count += 1

    # --- OpenClaw ---
    _seed_config(cur, "sillyclaw", "openclaw", {
        "hero_title": "OpenClaw - 开源 AI Skills 平台",
        "hero_desc": "开源、可扩展的 AI Skills 生态系统，让每个人都能构建和分享 AI 能力",
        "features": [
            {"icon_bg": "#667eea", "icon_class": "fas fa-rocket", "title": "开源免费", "description": "完全开源的 Skills 平台，自由使用和定制"},
            {"icon_bg": "#f093fb", "icon_class": "fas fa-puzzle-piece", "title": "模块化设计", "description": "可插拔的 Skills 架构，灵活组合"},
            {"icon_bg": "#4facfe", "icon_class": "fas fa-globe", "title": "跨平台支持", "description": "Windows / macOS / Linux 全覆盖"},
            {"icon_bg": "#43e97b", "icon_class": "fas fa-users", "title": "社区驱动", "description": "全球开发者社区共同维护和改进"},
            {"icon_bg": "#fa709a", "icon_class": "fas fa-shield-halved", "title": "安全可靠", "description": "内置安全沙箱，保护您的数据和隐私"},
            {"icon_bg": "#0066FF", "icon_class": "fas fa-bolt", "title": "高性能", "description": "Rust 编写，极致性能体验"},
        ],
        "roadmap": []
    }); count += 1

    # --- Contact Info ---
    _seed_config(cur, "contact", "info", {
        "email": "support@sillymd.com",
        "qq_group": "123456789",
        "wechat": "SillyMDOfficial",
        "address": "上海市浦东新区",
        "work_hours": "周一至周五 9:00-18:00",
    }); count += 1

    print(f"Seeded {count} config_data entries")


def main():
    with get_db_cursor() as cur:
        ensure_tables(cur)
        seed_categories(cur)
        seed_articles(cur)
        seed_tutorials(cur)
        seed_learning_categories(cur)
        update_skills_categories(cur)
        seed_config_data(cur)
    print("\nSeed data complete! Restart the server to see changes.")


if __name__ == "__main__":
    main()
