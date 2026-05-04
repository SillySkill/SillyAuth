"""
SillyMD Dev Stubs

为 admin-v2 前端提供后端尚未实现的 API 桩端点。
仅在 APP_ENV=development 时加载，返回 mock 数据。
"""
import logging
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

_now = datetime.now()


def _paginated(items: list, page: int = 1, page_size: int = 20):
    """包装分页响应"""
    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


def _ok(data, message: str = "ok"):
    """包装单条响应"""
    return {"success": True, "data": data, "message": message}


# ---------------------------------------------------------------------------
# Mock 数据
# ---------------------------------------------------------------------------

_mock_vendors = [
    {"id": 1, "name": "北京智谱华章", "slug": "zhipu", "description": "GLM 系列模型开发商", "logo": "", "website": "https://zhipu.ai", "category": "ai-model", "contact_email": "contact@zhipu.ai", "contact_phone": "010-88888888", "is_active": True, "is_verified": True, "sort_order": 1, "created_at": (_now - timedelta(days=90)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "深度求索", "slug": "deepseek", "description": "DeepSeek 系列模型开发商", "logo": "", "website": "https://deepseek.com", "category": "ai-model", "contact_email": "contact@deepseek.com", "contact_phone": "010-88888888", "is_active": True, "is_verified": True, "sort_order": 2, "created_at": (_now - timedelta(days=60)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "月之暗面", "slug": "moonshot", "description": "Kimi 智能助手开发商", "logo": "", "website": "https://kimi.moonshot.cn", "category": "ai-application", "contact_email": "contact@moonshot.cn", "contact_phone": "010-88888888", "is_active": True, "is_verified": False, "sort_order": 3, "created_at": (_now - timedelta(days=30)).isoformat(), "updated_at": _now.isoformat()},
]

_mock_commission_records = [
    {"id": 1, "user_id": 1, "user": {"id": 1, "username": "admin", "email": "admin@sillymd.com", "role": "ADMIN", "is_active": True, "created_at": _now.isoformat()}, "order_id": 1001, "amount": 50.00, "rate": 0.1, "description": "文章推广佣金", "status": "approved", "created_at": (_now - timedelta(days=5)).isoformat(), "updated_at": (_now - timedelta(days=4)).isoformat()},
    {"id": 2, "user_id": 2, "user": {"id": 2, "username": "creator1", "email": "creator1@sillymd.com", "role": "CREATOR", "is_active": True, "created_at": _now.isoformat()}, "order_id": 1002, "amount": 30.00, "rate": 0.15, "description": "教程推广佣金", "status": "pending", "created_at": (_now - timedelta(days=2)).isoformat(), "updated_at": (_now - timedelta(days=2)).isoformat()},
    {"id": 3, "user_id": 3, "user": {"id": 3, "username": "creator2", "email": "creator2@sillymd.com", "role": "CREATOR", "is_active": True, "created_at": _now.isoformat()}, "order_id": 1003, "amount": 20.00, "rate": 0.12, "description": "下载推广佣金", "status": "pending", "created_at": (_now - timedelta(days=1)).isoformat(), "updated_at": (_now - timedelta(days=1)).isoformat()},
]

_mock_seo_configs = [
    {"id": 1, "page": "home", "title": "SillyMD - AI 技能内容平台", "description": "发现和学习 AI 技能", "keywords": "AI,技能,教程,内容平台", "og_title": "SillyMD AI 平台", "og_description": "发现和学习 AI 技能", "og_image": "", "canonical_url": "https://sillymd.com", "updated_at": _now.isoformat()},
    {"id": 2, "page": "articles", "title": "文章 - SillyMD", "description": "AI 技能相关文章", "keywords": "AI,文章,教程", "updated_at": _now.isoformat()},
]

_mock_nav_items = [
    {"id": 1, "label_zh": "首页", "label_en": "Home", "url": "/", "icon": "HomeOutlined", "sort_order": 1, "is_visible": True, "children": []},
    {"id": 2, "label_zh": "探索 Skills", "label_en": "Explore Skills", "url": "/skills", "icon": "SearchOutlined", "sort_order": 2, "is_visible": True, "children": []},
    {"id": 3, "label_zh": "教程", "label_en": "Tutorials", "url": "/tutorials", "icon": "PlaySquareOutlined", "sort_order": 3, "is_visible": True, "children": []},
    {"id": 4, "label_zh": "下载", "label_en": "Downloads", "url": "/downloads", "icon": "DownloadOutlined", "sort_order": 4, "is_visible": True, "children": []},
    {"id": 5, "label_zh": "供应商市场", "label_en": "Marketplace", "url": "/marketplace", "icon": "ShopOutlined", "sort_order": 5, "is_visible": True, "children": []},
    {"id": 6, "label_zh": "商店", "label_en": "Store", "url": "/store", "icon": "ShoppingCartOutlined", "sort_order": 6, "is_visible": True, "children": []},
    {"id": 7, "label_zh": "团队协作", "label_en": "Teams", "url": "/teams", "icon": "TeamOutlined", "sort_order": 7, "is_visible": True, "children": []},
    {"id": 8, "label_zh": "文档", "label_en": "Docs", "url": "/docs", "icon": "ReadOutlined", "sort_order": 8, "is_visible": True, "children": []},
]

_mock_translations = [
    {"id": 1, "locale": "zh-CN", "namespace": "common", "key": "welcome", "value": "欢迎", "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "locale": "en", "namespace": "common", "key": "welcome", "value": "Welcome", "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "locale": "ja", "namespace": "common", "key": "welcome", "value": "ようこそ", "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
]

_mock_tutorial_chapters = {
    1: [
        {"id": 1, "tutorial_id": 1, "title": "什么是 AI", "content": "AI 即人工智能...", "order": 1, "video_url": None, "duration": 600, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
        {"id": 2, "tutorial_id": 1, "title": "机器学习基础", "content": "机器学习是 AI 的核心...", "order": 2, "video_url": None, "duration": 900, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    ],
}

_mock_cms_stats = {
    "total_articles": 128,
    "total_categories": 8,
    "total_drafts": 15,
    "total_published": 108,
    "total_archived": 5,
    "total_views": 45230,
    "total_likes": 3890,
    "articles_by_category": [
        {"category": "AI 入门", "count": 35},
        {"category": "提示工程", "count": 28},
        {"category": "模型微调", "count": 22},
        {"category": "工具使用", "count": 43},
    ],
}

_mock_audit_logs = [
    {"id": 1, "action": "user.login", "description": "管理员登录系统", "user_id": 1, "user": {"id": 1, "username": "admin"}, "target_type": "user", "target_id": 1, "created_at": (_now - timedelta(minutes=5)).isoformat()},
    {"id": 2, "action": "article.create", "description": "创建新文章: AI 入门指南", "user_id": 1, "user": {"id": 1, "username": "admin"}, "target_type": "article", "target_id": 101, "created_at": (_now - timedelta(minutes=30)).isoformat()},
    {"id": 3, "action": "article.update", "description": "更新文章: 提示工程技巧", "user_id": 2, "user": {"id": 2, "username": "editor"}, "target_type": "article", "target_id": 102, "created_at": (_now - timedelta(hours=1)).isoformat()},
]

# ---------------------------------------------------------------------------
# Mock 计数器（用于 POST/PUT 生成新 ID）
# ---------------------------------------------------------------------------

_next_ids = {
    "vendor": 4,
    "translation": 4,
    "audit_log": 4,
}

# ---------------------------------------------------------------------------
# Router 定义
# ---------------------------------------------------------------------------

router = APIRouter()


# === Auth (dev mode login) ===

@router.post("/api/v1/auth/login")
async def stub_login():
    """Dev mode: accept known test credentials and return a JWT token."""
    from jose import jwt as jose_jwt
    secret = os.getenv("JWT_SECRET", "dev-secret")
    payload = {
        "user_id": 1,
        "username": "admin",
        "email": "admin@sillymd.com",
        "role": "super_admin",
        "type": "access",
        "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
    }
    access_token = jose_jwt.encode(payload, secret, algorithm="HS256")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@sillymd.com",
            "role": "super_admin",
        },
    }


@router.post("/api/v1/auth/dev-login")
async def stub_dev_login():
    """Dev mode: bypass database auth, return admin JWT token."""
    from jose import jwt as jose_jwt
    secret = os.getenv("JWT_SECRET", "dev-secret")
    payload = {
        "user_id": 1,
        "username": "admin",
        "email": "admin@sillymd.com",
        "role": "super_admin",
        "type": "access",
        "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
    }
    access_token = jose_jwt.encode(payload, secret, algorithm="HS256")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@sillymd.com",
            "role": "super_admin",
        },
    }


# === Admin / Modules ===

_mock_modules = [
    {"id": 1, "name": "认证管理", "key": "auth", "description": "用户认证与授权", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 2, "name": "内容管理", "key": "cms", "description": "文章与内容发布管理", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 3, "name": "技能管理", "key": "skills", "description": "AI 技能库管理", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 4, "name": "教程管理", "key": "tutorials", "description": "教程与课程管理", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 5, "name": "下载管理", "key": "downloads", "description": "文件下载管理", "is_enabled": False, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 6, "name": "用户管理", "key": "users", "description": "用户账户管理", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 7, "name": "积分系统", "key": "points", "description": "用户积分与等级", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 8, "name": "支付系统", "key": "payment", "description": "支付与结算管理", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 9, "name": "店铺管理", "key": "store", "description": "商家店铺管理", "is_enabled": False, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
    {"id": 10, "name": "消息通知", "key": "messages", "description": "站内消息与通知", "is_enabled": True, "version": "1.0.0", "installed_at": "2026-01-01T00:00:00"},
]

@router.get("/api/v1/admin/modules")
async def stub_admin_modules():
    return _ok(_mock_modules)

@router.post("/api/v1/admin/modules/{module_id}/enable")
async def stub_enable_module(module_id: int):
    return _ok({"id": module_id, "is_enabled": True}, "模块已启用")

@router.post("/api/v1/admin/modules/{module_id}/disable")
async def stub_disable_module(module_id: int):
    return _ok({"id": module_id, "is_enabled": False}, "模块已禁用")


# === Vendors ===

@router.get("/api/v1/vendors")
async def stub_get_vendors(page: int = 1, page_size: int = 20):
    return _paginated(_mock_vendors, page, page_size)


@router.get("/api/v1/vendors/{vendor_id}")
async def stub_get_vendor(vendor_id: int):
    for v in _mock_vendors:
        if v["id"] == vendor_id:
            return _ok(v)
    return JSONResponse({"success": False, "message": "Vendor not found"}, status_code=404)


@router.post("/api/v1/vendors")
async def stub_create_vendor():
    return _ok({"id": 1, "name": "New Vendor", "is_active": True})


@router.put("/api/v1/vendors/{vendor_id}")
async def stub_update_vendor(vendor_id: int):
    return _ok({"id": vendor_id, "updated": True})


@router.delete("/api/v1/vendors/{vendor_id}")
async def stub_delete_vendor(vendor_id: int):
    return _ok({"id": vendor_id, "deleted": True})


# === Tutorials (write ops + list) ===

@router.get("/api/v1/tutorials")
@router.get("/api/v1/tutorials/")
async def stub_list_tutorials(page: int = 1, page_size: int = 20):
    return {
        "items": [],
        "total": 0, "page": page, "limit": page_size, "pages": 1,
    }


@router.post("/api/v1/tutorials")
async def stub_create_tutorial():
    return _ok({
        "id": 99, "title": "New Tutorial", "slug": "new-tutorial",
        "description": "New tutorial description", "content": "",
        "difficulty_level": "beginner", "status": "draft",
        "view_count": 0, "sort_order": 0,
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    })


@router.put("/api/v1/tutorials/{tutorial_id}")
async def stub_update_tutorial(tutorial_id: int):
    return _ok({"id": tutorial_id, "updated": True})


@router.delete("/api/v1/tutorials/{tutorial_id}")
async def stub_delete_tutorial(tutorial_id: int):
    return _ok({"id": tutorial_id, "deleted": True})


# === Tutorial Chapters ===

@router.get("/api/v1/tutorials/{tutorial_id}/chapters")
async def stub_get_chapters(tutorial_id: int):
    chapters = _mock_tutorial_chapters.get(tutorial_id, [])
    return _ok(chapters)


@router.post("/api/v1/tutorials/{tutorial_id}/chapters")
async def stub_create_chapter(tutorial_id: int):
    return _ok({
        "id": 99, "tutorial_id": tutorial_id,
        "title": "New Chapter", "content": "",
        "order": 1, "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    })


@router.put("/api/v1/tutorials/{tutorial_id}/chapters/{chapter_id}")
async def stub_update_chapter(tutorial_id: int, chapter_id: int):
    return _ok({"id": chapter_id, "tutorial_id": tutorial_id, "updated": True})


@router.delete("/api/v1/tutorials/{tutorial_id}/chapters/{chapter_id}")
async def stub_delete_chapter(tutorial_id: int, chapter_id: int):
    return _ok({"id": chapter_id, "deleted": True})


# === Admin: User Management (DB fallback stubs) ===

_mock_admin_users = [
    {"id": 1, "username": "admin", "email": "admin@sillymd.com", "role": "super_admin", "is_active": True, "created_at": (_now - timedelta(days=365)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "username": "editor", "email": "editor@sillymd.com", "role": "content_admin", "is_active": True, "created_at": (_now - timedelta(days=180)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "username": "zhangsan", "email": "zhangsan@example.com", "role": "user", "is_active": True, "created_at": (_now - timedelta(days=30)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 4, "username": "lisi", "email": "lisi@example.com", "role": "user", "is_active": False, "created_at": (_now - timedelta(days=15)).isoformat(), "updated_at": _now.isoformat()},
]


@router.get("/api/v1/admin/users")
async def stub_admin_users(page: int = 1, page_size: int = 20, search: str = ""):
    items = _mock_admin_users
    if search:
        items = [u for u in items if search.lower() in u["username"].lower() or search.lower() in u["email"].lower()]
    return _paginated(items, page, page_size)


@router.get("/api/v1/admin/users/{user_id}")
async def stub_admin_user_detail(user_id: int):
    for u in _mock_admin_users:
        if u["id"] == user_id:
            return _ok(u)
    return JSONResponse({"success": False, "message": "User not found"}, status_code=404)


@router.put("/api/v1/admin/users/{user_id}/status")
async def stub_admin_user_status(user_id: int):
    return _ok({"id": user_id, "status": "updated"})


@router.get("/api/v1/admin/dashboard")
async def stub_admin_dashboard():
    return _ok({
        "total_users": 42, "new_users_today": 2, "active_users_today": 7,
        "total_articles": 128, "total_revenue": 15800.00,
    })


@router.get("/api/v1/admin/stats")
async def stub_admin_stats():
    return _ok({
        "total_users": 42, "total_articles": 128, "total_skills": 16,
        "total_tutorials": 24, "total_downloads": 35, "total_revenue": 15800.00,
    })


# === Dashboard (DB fallback stubs) ===

@router.get("/api/v1/dashboard/overview")
async def stub_dashboard_overview():
    return _ok({
        "stats": {
            "total_users": 42, "total_articles": 128, "total_skills": 16,
            "total_tutorials": 24, "total_downloads": 35, "total_revenue": 15800.00,
            "active_users_today": 7, "new_users_today": 2,
        },
        "revenue_trend": [{"date": (_now - timedelta(days=i)).strftime("%Y-%m-%d"), "amount": round(500 + i * 10, 2)} for i in range(6, -1, -1)],
        "user_growth": [{"date": (_now - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 40 + i} for i in range(6, -1, -1)],
        "content_distribution": [
            {"type": "article", "count": 128}, {"type": "tutorial", "count": 24},
            {"type": "download", "count": 35}, {"type": "skill", "count": 16},
        ],
        "top_articles": [],
        "top_creators": [],
    })


@router.get("/api/v1/dashboard/stats")
async def stub_dashboard_stats(days: int = 30):
    return _ok({
        "total_users": 42, "total_articles": 128, "total_skills": 16,
        "total_tutorials": 24, "total_downloads": 35, "total_revenue": 15800.00,
        "active_users_today": 7, "new_users_today": 2,
    })


@router.get("/api/v1/dashboard/recent-activity")
async def stub_dashboard_recent_activity(limit: int = 20):
    return _ok([
        {"id": 1, "action": "user.login", "description": "管理员登录", "user_id": 1,
         "user": {"id": 1, "username": "admin"}, "target_type": None, "target_id": None,
         "created_at": (_now - timedelta(minutes=5)).isoformat()},
        {"id": 2, "action": "article.publish", "description": "发布文章: AI 入门指南", "user_id": 1,
         "user": {"id": 1, "username": "admin"}, "target_type": "article", "target_id": 101,
         "created_at": (_now - timedelta(minutes=30)).isoformat()},
        {"id": 3, "action": "tutorial.create", "description": "创建教程: 提示工程入门", "user_id": 2,
         "user": {"id": 2, "username": "editor"}, "target_type": "tutorial", "target_id": 5,
         "created_at": (_now - timedelta(hours=1)).isoformat()},
        {"id": 4, "action": "user.register", "description": "新用户注册: zhangsan@example.com", "user_id": 3,
         "user": {"id": 3, "username": "zhangsan"}, "target_type": "user", "target_id": 3,
         "created_at": (_now - timedelta(hours=2)).isoformat()},
    ])


# === Downloads (write ops) ===

@router.post("/api/v1/downloads")
async def stub_create_download():
    return _ok({
        "id": 99, "title": "New Download", "slug": "new-download",
        "description": "", "file_url": "", "file_size": 0,
        "file_type": "zip", "is_active": True,
        "download_count": 0,
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    })


@router.put("/api/v1/downloads/{download_id}")
async def stub_update_download(download_id: int):
    return _ok({"id": download_id, "updated": True})


@router.delete("/api/v1/downloads/{download_id}")
async def stub_delete_download(download_id: int):
    return _ok({"id": download_id, "deleted": True})


# === Commission ===

@router.get("/api/v1/commission/records")
async def stub_get_commission_records(page: int = 1, page_size: int = 20):
    return _paginated(_mock_commission_records, page, page_size)


@router.get("/api/v1/commission/stats")
async def stub_get_commission_stats():
    return _ok({
        "total_commission": 100.00,
        "total_pending": 50.00,
        "total_approved": 50.00,
        "total_rejected": 0.00,
        "average_rate": 0.12,
    })


# === SEO ===

@router.get("/api/v1/seo")
async def stub_get_seo():
    return _ok(_mock_seo_configs)


@router.put("/api/v1/seo")
async def stub_update_seo():
    return _ok({"id": 1, "updated": True})


# === Navigation ===

@router.get("/api/v1/navigation")
async def stub_get_navigation():
    return {"success": True, "items": _mock_nav_items}


@router.put("/api/v1/navigation")
async def stub_update_navigation():
    return {"success": True, "message": "ok"}


# === Headless CMS Navigation (frontend calls /cms/navigation) ===

@router.get("/api/v1/cms/navigation")
async def stub_cms_get_navigation():
    return {"success": True, "items": _mock_nav_items}


@router.put("/api/v1/cms/navigation")
async def stub_cms_update_navigation():
    return {"success": True, "message": "ok"}


@router.get("/api/v1/cms/seo")
async def stub_cms_get_seo():
    return _ok(_mock_seo_configs)


@router.put("/api/v1/cms/seo")
async def stub_cms_update_seo():
    return _ok({"id": 1, "updated": True})


# === i18n CRUD ===

@router.post("/api/v1/i18n/translations")
async def stub_create_translation():
    return _ok({
        "id": 99, "locale": "zh-CN", "namespace": "common",
        "key": "new_key", "value": "新值",
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    })


@router.put("/api/v1/i18n/translations/{translation_id}")
async def stub_update_translation(translation_id: int):
    return _ok({"id": translation_id, "updated": True})


@router.delete("/api/v1/i18n/translations/{translation_id}")
async def stub_delete_translation(translation_id: int):
    return _ok({"id": translation_id, "deleted": True})


# === CMS Categories (dev stub) ===

_mock_categories = [
    {"id": 1, "name": "AI 入门", "slug": "ai-intro", "description": "AI 入门相关文章", "sort_order": 1, "is_active": True, "created_at": (_now - timedelta(days=90)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "提示工程", "slug": "prompt-engineering", "description": "提示工程技巧与实践", "sort_order": 2, "is_active": True, "created_at": (_now - timedelta(days=80)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "模型微调", "slug": "fine-tuning", "description": "模型微调教程与案例", "sort_order": 3, "is_active": True, "created_at": (_now - timedelta(days=70)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 4, "name": "工具使用", "slug": "tools", "description": "AI 工具使用指南", "sort_order": 4, "is_active": True, "created_at": (_now - timedelta(days=60)).isoformat(), "updated_at": _now.isoformat()},
]


@router.get("/api/v1/cms/categories")
async def stub_cms_categories():
    return _ok(_mock_categories)


# === CMS Articles (dev stub) ===

_mock_articles = [
    {"id": 1, "title": "AI 入门指南：从零开始了解人工智能", "slug": "ai-intro-guide", "content": "人工智能（AI）是计算机科学的一个重要分支...", "excerpt": "适合初学者的 AI 入门文章", "category_id": 1, "category": _mock_categories[0], "author_id": 1, "author": {"id": 1, "username": "admin", "email": "admin@sillymd.com", "role": "admin"}, "tags": ["AI", "入门", "人工智能"], "status": "published", "view_count": 1520, "like_count": 89, "is_featured": True, "created_at": (_now - timedelta(days=30)).isoformat(), "updated_at": (_now - timedelta(days=1)).isoformat(), "published_at": (_now - timedelta(days=28)).isoformat()},
    {"id": 2, "title": "提示工程进阶技巧", "slug": "prompt-engineering-advanced", "content": "提示工程是人工智能应用中的关键技能...", "excerpt": "掌握高级提示技巧", "category_id": 2, "category": _mock_categories[1], "author_id": 1, "author": {"id": 1, "username": "admin", "email": "admin@sillymd.com", "role": "admin"}, "tags": ["提示工程", "AI", "技巧"], "status": "published", "view_count": 2340, "like_count": 156, "is_featured": True, "created_at": (_now - timedelta(days=20)).isoformat(), "updated_at": (_now - timedelta(days=2)).isoformat(), "published_at": (_now - timedelta(days=18)).isoformat()},
    {"id": 3, "title": "使用 LoRA 微调大语言模型", "slug": "lora-fine-tuning", "content": "LoRA（Low-Rank Adaptation）是一种高效的模型微调方法...", "excerpt": "LoRA 微调实战教程", "category_id": 3, "category": _mock_categories[2], "author_id": 2, "author": {"id": 2, "username": "editor", "email": "editor@sillymd.com", "role": "editor"}, "tags": ["LoRA", "微调", "大语言模型"], "status": "published", "view_count": 890, "like_count": 45, "is_featured": False, "created_at": (_now - timedelta(days=15)).isoformat(), "updated_at": _now.isoformat(), "published_at": (_now - timedelta(days=13)).isoformat()},
    {"id": 4, "title": "AI 工具推荐：2024 年必备清单", "slug": "ai-tools-2024", "content": "本文整理了 2024 年最实用的 AI 工具...", "excerpt": "年度 AI 工具推荐", "category_id": 4, "category": _mock_categories[3], "author_id": 2, "author": {"id": 2, "username": "editor", "email": "editor@sillymd.com", "role": "editor"}, "tags": ["AI工具", "推荐", "效率"], "status": "draft", "view_count": 0, "like_count": 0, "is_featured": False, "created_at": (_now - timedelta(days=1)).isoformat(), "updated_at": _now.isoformat(), "published_at": None},
]


@router.get("/api/v1/cms/articles")
async def stub_cms_articles(page: int = 1, page_size: int = 20, status: str = "", category_id: int = 0):
    items = _mock_articles
    if status:
        items = [a for a in items if a["status"] == status]
    if category_id:
        items = [a for a in items if a["category_id"] == category_id]
    return _paginated(items, page, page_size)


# === CMS Stats (admin) ===

@router.get("/api/v1/cms/stats/articles")
async def stub_cms_stats():
    return _ok(_mock_cms_stats)


# === Admin: Audit Logs ===

@router.get("/api/v1/admin/audit-logs")
async def stub_audit_logs(page: int = 1, page_size: int = 20):
    return _paginated(_mock_audit_logs, page, page_size)


# === Admin: Content Moderation ===

@router.get("/api/v1/admin/content/pending")
async def stub_pending_content(page: int = 1, page_size: int = 20):
    return _paginated([], page, page_size)


@router.post("/api/v1/admin/content/{content_id}/approve")
async def stub_approve_content(content_id: int):
    return _ok({"id": content_id, "status": "approved"})


@router.post("/api/v1/admin/content/{content_id}/reject")
async def stub_reject_content(content_id: int):
    return _ok({"id": content_id, "status": "rejected"})


# === Payment Accounts (DB fallback stubs) ===

_mock_payment_accounts = [
    {"id": 1, "user_id": 1, "user": {"id": 1, "username": "admin", "email": "admin@sillymd.com", "role": "ADMIN", "is_active": True, "created_at": _now.isoformat()}, "account_type": "alipay", "account_name": "管理员", "account_number": "13800138000", "is_verified": True, "is_default": True, "created_at": (_now - timedelta(days=90)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "user_id": 2, "user": {"id": 2, "username": "creator1", "email": "creator1@sillymd.com", "role": "CREATOR", "is_active": True, "created_at": _now.isoformat()}, "account_type": "wechat", "account_name": "创作者1", "account_number": "wx_creator1", "is_verified": False, "is_default": True, "created_at": (_now - timedelta(days=30)).isoformat(), "updated_at": _now.isoformat()},
]


@router.get("/api/v1/payment/accounts")
async def stub_payment_accounts():
    return _ok(_mock_payment_accounts)


@router.post("/api/v1/payment/accounts")
async def stub_create_payment_account():
    return _ok({"id": 3, "account_type": "alipay", "is_verified": False, "is_default": False})


@router.put("/api/v1/payment/accounts/{account_id}")
async def stub_update_payment_account(account_id: int):
    return _ok({"id": account_id, "updated": True})


@router.delete("/api/v1/payment/accounts/{account_id}")
async def stub_delete_payment_account(account_id: int):
    return _ok({"id": account_id, "deleted": True})


# === Creator Earnings (admin settlement + revenue stubs) ===

# The CreatorEarnings.tsx component expects each settlement item to have:
#   user_id, username, email, settlement_method, pending_count, total_pending_amount, oldest_earning_date

_mock_pending_settlements = [
    {"user_id": 2, "username": "creator1", "email": "creator1@sillymd.com", "settlement_method": "alipay", "pending_count": 5, "total_pending_amount": 850.50, "oldest_earning_date": (_now - timedelta(days=45)).isoformat()},
    {"user_id": 3, "username": "creator2", "email": "creator2@sillymd.com", "settlement_method": "wechat", "pending_count": 3, "total_pending_amount": 1200.00, "oldest_earning_date": (_now - timedelta(days=30)).isoformat()},
    {"user_id": 4, "username": "creator3", "email": "creator3@sillymd.com", "settlement_method": "bank", "pending_count": 8, "total_pending_amount": 3200.00, "oldest_earning_date": (_now - timedelta(days=60)).isoformat()},
]


@router.get("/api/v1/payment/accounts/admin/pending-settlements")
async def stub_pending_settlements(page: int = 1, page_size: int = 20):
    return _paginated(_mock_pending_settlements, page, page_size)


@router.post("/api/v1/payment/accounts/admin/settle/{user_id}")
async def stub_settle_creator(user_id: int):
    return _ok({"user_id": user_id, "settled": True, "amount": 850.50, "settled_at": _now.isoformat()})


# The CreatorEarnings.tsx component expects revenue stats as an array of
# {date, paid_orders, total_revenue} items (either direct array in data, or items in paginated wrapper)

_mock_daily_revenue = [
    {"date": (_now - timedelta(days=i)).strftime("%Y-%m-%d"), "paid_orders": 8 + i % 7, "total_revenue": round(1200 + i * 45.5, 2)}
    for i in range(30, 0, -1)
]


@router.get("/api/v1/payment/admin/revenue/stats")
async def stub_revenue_stats(days: int = 30):
    items = _mock_daily_revenue[-days:] if days < len(_mock_daily_revenue) else _mock_daily_revenue
    return _ok(items)


# === Points Categories (DB fallback stub) ===

_mock_points_categories = [
    {"id": 1, "name": "数码产品", "description": "电子数码类商品", "sort_order": 1, "created_at": _now.isoformat()},
    {"id": 2, "name": "虚拟商品", "description": "电子卡券、会员等", "sort_order": 2, "created_at": _now.isoformat()},
    {"id": 3, "name": "周边商品", "description": "品牌周边产品", "sort_order": 3, "created_at": _now.isoformat()},
]


@router.get("/api/v1/points/categories")
async def stub_points_categories():
    return _ok(_mock_points_categories)


# === Points Mall Items (products + exchange management) ===

_mock_points_products = [
    {"id": 1, "name": "SillyMD 定制 T 恤", "description": "限量版品牌 T 恤", "points_required": 500, "price": 49.90, "stock": 100, "image": "", "category_id": 3, "category_name": "周边商品", "is_active": True, "sort_order": 1, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "50 元话费充值卡", "description": "移动/联通/电信通用", "points_required": 1000, "price": 50.00, "stock": 50, "image": "", "category_id": 2, "category_name": "虚拟商品", "is_active": True, "sort_order": 2, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "蓝牙耳机", "description": "高品质无线蓝牙耳机", "points_required": 3000, "price": 199.00, "stock": 20, "image": "", "category_id": 1, "category_name": "数码产品", "is_active": True, "sort_order": 3, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
]

_next_points_product_id = 4


@router.get("/api/v1/points/mall/items")
async def stub_points_mall_items(page: int = 1, page_size: int = 20):
    return _paginated(_mock_points_products, page, page_size)


@router.post("/api/v1/points/mall/items")
async def stub_create_points_product():
    global _next_points_product_id
    pid = _next_points_product_id
    _next_points_product_id += 1
    return _ok({"id": pid, **{"name": "", "points_required": 0, "stock": 0, "is_active": True, "category_id": None}})


@router.put("/api/v1/points/mall/items/{item_id}")
async def stub_update_points_product(item_id: int):
    return _ok({"id": item_id, "updated": True})


@router.delete("/api/v1/points/products/{product_id}")
async def stub_delete_points_product(product_id: int):
    return _ok({"id": product_id, "deleted": True})


_mock_exchanges = [
    {"id": 1, "user_id": 2, "user": {"id": 2, "username": "creator1", "email": "creator1@sillymd.com"}, "product_id": 1, "product_name": "SillyMD 定制 T 恤", "points_spent": 500, "quantity": 1, "status": "completed", "shipping_address": "北京市朝阳区...", "tracking_number": "SF1234567890", "created_at": (_now - timedelta(days=10)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "user_id": 3, "user": {"id": 3, "username": "creator2", "email": "creator2@sillymd.com"}, "product_id": 2, "product_name": "50 元话费充值卡", "points_spent": 1000, "quantity": 1, "status": "pending", "shipping_address": None, "tracking_number": None, "created_at": (_now - timedelta(days=2)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "user_id": 1, "user": {"id": 1, "username": "admin", "email": "admin@sillymd.com"}, "product_id": 3, "product_name": "蓝牙耳机", "points_spent": 3000, "quantity": 1, "status": "shipped", "shipping_address": "上海市浦东新区...", "tracking_number": "YD9876543210", "created_at": (_now - timedelta(days=5)).isoformat(), "updated_at": _now.isoformat()},
]


@router.get("/api/v1/points/mall/all-exchanges")
async def stub_all_exchanges(page: int = 1, page_size: int = 20):
    return _paginated(_mock_exchanges, page, page_size)


@router.put("/api/v1/points/mall/exchanges/{exchange_id}/status")
async def stub_update_exchange_status(exchange_id: int):
    return _ok({"id": exchange_id, "status": "completed", "updated": True})


# === Downloads (DB/TOS fallback stub) ===

_mock_downloads = [
    {"id": 1, "title": "SillyFu v1.0.0", "slug": "sillyfu-v1", "description": "SillyFu 桌面客户端", "file_url": "https://example.com/sillyfu-v1.zip", "file_size": 52428800, "file_type": "zip", "version": "1.0.0", "category": "client", "platform": "windows", "download_count": 1280, "is_active": True, "created_at": (_now - timedelta(days=60)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "title": "SillyFu v1.0.0 (macOS)", "slug": "sillyfu-v1-mac", "description": "SillyFu 桌面客户端 for macOS", "file_url": "https://example.com/sillyfu-v1.dmg", "file_size": 48234567, "file_type": "dmg", "version": "1.0.0", "category": "client", "platform": "mac", "download_count": 856, "is_active": True, "created_at": (_now - timedelta(days=60)).isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "title": "AI 模型入门指南 PDF", "slug": "ai-guide-pdf", "description": "AI 模型入门学习资料", "file_url": "https://example.com/ai-guide.pdf", "file_size": 10485760, "file_type": "pdf", "version": "1.0", "category": "document", "platform": "all", "download_count": 3520, "is_active": True, "created_at": (_now - timedelta(days=30)).isoformat(), "updated_at": _now.isoformat()},
]


@router.get("/api/v1/downloads")
async def stub_downloads(page: int = 1, page_size: int = 20):
    return _paginated(_mock_downloads, page, page_size)


# === i18n Translations list (backend has route but broken without DB) ===

@router.get("/api/v1/i18n/translations")
async def stub_i18n_translations(page: int = 1, page_size: int = 20):
    return _paginated(_mock_translations, page, page_size)


# === Affiliate / Commission (extra) ===

@router.get("/api/v1/affiliate/staffs")
async def stub_staffs(page: int = 1, page_size: int = 20):
    return _paginated([], page, page_size)


# ===========================================================================
# === ConfigData (admin-v2 ConfigDataManagement.tsx) ===
# ===========================================================================

_mock_config_data = {
    "hero_slides": [
        {"id": 1, "name": "slides", "data": [
            {"image": "/static/img/hero-bg.svg", "title": "AI Skills 托管中心", "subtitle": "发现、学习和分享 AI Skills", "cta_text": "探索 Skills", "cta_url": "/skills"},
            {"image": "/static/img/hero-bg.svg", "title": "掌握 AI 编程工具", "subtitle": "学习 Claude Code、OpenClaw 等最新 AI 工具", "cta_text": "查看教程", "cta_url": "/tutorials"},
            {"image": "/static/img/hero-bg.svg", "title": "成为供应商", "subtitle": "分享你的专业技能，实现知识变现", "cta_text": "立即入驻", "cta_url": "/vendor-apply"},
        ]},
    ],
    "navigation": [
        {"id": 2, "name": "navbar", "data": [
            {"id": 1, "label_zh": "首页", "label_en": "Home", "url": "/", "icon": "HomeOutlined", "sort_order": 1, "is_visible": True, "children": []},
            {"id": 2, "label_zh": "探索 Skills", "label_en": "Explore Skills", "url": "/skills", "icon": "SearchOutlined", "sort_order": 2, "is_visible": True, "children": []},
            {"id": 3, "label_zh": "教程", "label_en": "Tutorials", "url": "/tutorials", "icon": "PlaySquareOutlined", "sort_order": 3, "is_visible": True, "children": []},
            {"id": 4, "label_zh": "下载", "label_en": "Downloads", "url": "/downloads", "icon": "DownloadOutlined", "sort_order": 4, "is_visible": True, "children": []},
            {"id": 5, "label_zh": "供应商市场", "label_en": "Marketplace", "url": "/marketplace", "icon": "ShopOutlined", "sort_order": 5, "is_visible": True, "children": []},
            {"id": 6, "label_zh": "商店", "label_en": "Store", "url": "/store", "icon": "ShoppingCartOutlined", "sort_order": 6, "is_visible": True, "children": []},
        ]},
        {"id": 3, "name": "footer_platform", "data": [
            {"label": "探索 Skills", "url": "/skills"},
            {"label": "供应商市场", "url": "/marketplace"},
            {"label": "团队协作", "url": "/teams"},
            {"label": "定价", "url": "/pricing"},
        ]},
        {"id": 4, "name": "footer_developer", "data": [
            {"label": "开发文档", "url": "/docs"},
            {"label": "API 参考", "url": "/docs/api-reference"},
            {"label": "社区论坛", "url": "/community"},
            {"label": "帮助中心", "url": "/help"},
        ]},
        {"id": 5, "name": "footer_about", "data": [
            {"label": "关于我们", "url": "/about"},
            {"label": "联系我们", "url": "/contact"},
            {"label": "隐私政策", "url": "/privacy"},
            {"label": "服务条款", "url": "/terms"},
        ]},
    ],
    "system": [
        {"id": 6, "name": "settings", "data": {"site_name": "挺傻的网站", "site_title": "SillyMD - AI Skills Platform", "tagline": "承认自己有时候挺傻的，这是智慧的开始", "copyright": "2026 SillyMD. All rights reserved.", "icp": "京ICP备XXXXXXXX号-1"}},
    ],
    "footer": [
        {"id": 7, "name": "social_links", "data": [
            {"platform": "微信公众号", "qr_image": "/static/img/qr-wechat.png"},
            {"platform": "QQ群", "qr_image": "/static/img/qr-qq.png"},
            {"platform": "GitHub", "qr_image": "/static/img/qr-github.png"},
        ]},
    ],
    "pricing": [
        {"id": 8, "name": "plan_free", "data": {"name": "免费版", "name_en": "Free", "price": "0", "price_display": "免费", "features": ["5 个 Skills", "基础下载", "社区支持"], "cta_text": "免费开始", "highlighted": False}},
        {"id": 9, "name": "plan_pro", "data": {"name": "专业版", "name_en": "Pro", "price": "99", "price_display": "¥99/月", "features": ["50 个 Skills", "高速下载", "API 访问", "优先支持"], "cta_text": "立即订阅", "highlighted": True}},
        {"id": 10, "name": "plan_enterprise", "data": {"name": "企业版", "name_en": "Enterprise", "price": "299", "price_display": "¥299/月", "features": ["无限 Skills", "专属域名", "API 全量访问", "7x24 技术支持", "SLA 保障"], "cta_text": "联系我们", "highlighted": False}},
    ],
    "about": [
        {"id": 11, "name": "content", "data": {"title": "关于挺傻的", "content": "<p>我们致力于打造最好的 AI Skills 托管平台，让每个人都能轻松发现、学习和分享 AI 技能。</p>", "mission": "让 AI 技术触手可及，降低使用门槛，赋能每一位创作者和开发者。", "values": [{"icon": "🚀", "title": "创新驱动", "description": "持续探索 AI 技术的边界"}, {"icon": "🤝", "title": "开放共享", "description": "构建开放的 AI Skills 生态系统"}, {"icon": "💡", "title": "赋能创造", "description": "让每个人都能创造 AI 价值"}], "team": [{"name": "创始人", "role": "CEO", "bio": "资深 AI 开发者"}, {"name": "CTO", "role": "技术负责人", "bio": "全栈工程师"}], "stats": [{"value": "10,000+", "label": "注册用户"}, {"value": "5,000+", "label": "Skills"}, {"value": "500+", "label": "供应商"}]}},
    ],
    "privacy": [
        {"id": 12, "name": "policy_html", "data": {"title": "隐私政策", "content": "<h2>隐私政策</h2><p>我们重视您的隐私。本隐私政策说明我们如何收集、使用和保护您的个人信息。</p><h3>1. 信息收集</h3><p>我们收集您在使用服务时提供的信息。</p><h3>2. 信息使用</h3><p>我们使用收集的信息来提供、维护和改进我们的服务。</p><h3>3. 信息安全</h3><p>我们采取合理的安全措施保护您的个人信息。</p>"}},
    ],
    "terms": [
        {"id": 13, "name": "policy_html", "data": {"title": "服务条款", "content": "<h2>服务条款</h2><p>使用本网站即表示您同意以下服务条款。</p><h3>1. 服务说明</h3><p>SillyMD 提供 AI Skills 托管和交易平台服务。</p><h3>2. 用户责任</h3><p>用户应遵守法律法规，不得上传违法或侵权内容。</p><h3>3. 知识产权</h3><p>用户上传的 Skills 内容的知识产权归原作者所有。</p>"}},
    ],
}

# Config data endpoint helpers
_MOCK_CONFIG_ITEMS = []
for _cat, _entries in _mock_config_data.items():
    for _entry in _entries:
        _MOCK_CONFIG_ITEMS.append({
            "category": _cat,
            "name": _entry["name"],
            "data": _entry["data"],
            "created_at": _now.isoformat(),
            "updated_at": _now.isoformat(),
        })


@router.get("/api/v1/config-data/list/{category}")
async def stub_config_list(category: str, page: int = 1, page_size: int = 20):
    items = [i for i in _MOCK_CONFIG_ITEMS if i["category"] == category]
    return _paginated(items, page, page_size)


@router.get("/api/v1/config-data/item/{category}/{name}")
async def stub_config_item(category: str, name: str):
    for item in _MOCK_CONFIG_ITEMS:
        if item["category"] == category and item["name"] == name:
            return _ok(item)
    return {"success": False, "message": "Not found"}


@router.post("/api/v1/config-data")
async def stub_config_create(request: Request):
    return _ok({"category": "system", "name": "settings", "data": {"site_name": "测试"}, "created_at": _now.isoformat()})


@router.put("/api/v1/config-data/item/{category}/{name}")
async def stub_config_update(category: str, name: str, request: Request):
    return _ok({"category": category, "name": name, "data": {}, "updated_at": _now.isoformat()})


@router.delete("/api/v1/config-data/item/{category}/{name}")
async def stub_config_delete(category: str, name: str):
    return _ok(None)


# ===========================================================================
# === Store Management (admin-v2 StoreManagement.tsx) ===
# ===========================================================================

_mock_collections = [
    {"id": 1, "name": "SillyFu 系列", "slug": "sillyfu-series", "description": "SillyFu 实体产品", "image_url": "", "sort_order": 1, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "周边商品", "slug": "merchandise", "description": "品牌周边商品", "image_url": "", "sort_order": 2, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "数字产品", "slug": "digital", "description": "数字下载产品", "image_url": "", "sort_order": 3, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
]

_mock_store_products = [
    {"id": 1, "name": "SillyFu U盘 128GB", "slug": "sillyfu-usb-128", "description": "SillyFu 定制 U 盘 128GB", "price": 99.00, "currency": "CNY", "images": [], "collection_id": 1, "collection": {"id": 1, "name": "SillyFu 系列"}, "stock": 200, "is_active": True, "sort_order": 1, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "SillyFu T恤", "slug": "sillyfu-tshirt", "description": "品牌限量 T 恤", "price": 49.90, "currency": "CNY", "images": [], "collection_id": 2, "collection": {"id": 2, "name": "周边商品"}, "stock": 500, "is_active": True, "sort_order": 2, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "AI Skills 模板包", "slug": "ai-skills-template", "description": "AI Skills 开发模板合集", "price": 29.90, "currency": "CNY", "images": [], "collection_id": 3, "collection": {"id": 3, "name": "数字产品"}, "stock": 9999, "is_active": True, "sort_order": 3, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
]

_next_store_id = [100]

# --- Collections ---

@router.get("/api/v1/store/admin/collections")
async def stub_store_collections(page: int = 1, page_size: int = 20):
    return _paginated(_mock_collections, page, page_size)


@router.post("/api/v1/store/admin/collections")
async def stub_store_create_collection(request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    cid = _next_store_id[0]; _next_store_id[0] += 1
    collection = {
        "id": cid, "name": body.get("name", "新分组"),
        "slug": body.get("slug", f"new-collection-{cid}"),
        "description": body.get("description", ""),
        "image_url": body.get("image_url", ""),
        "sort_order": body.get("sort_order", 99),
        "is_active": body.get("is_active", True),
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    }
    _mock_collections.append(collection)
    return _ok(collection)


@router.put("/api/v1/store/admin/collections/{collection_id}")
async def stub_store_update_collection(collection_id: int, request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    for c in _mock_collections:
        if c["id"] == collection_id:
            c.update({k: v for k, v in body.items() if v is not None and k in ["name", "slug", "description", "image_url", "sort_order", "is_active"]})
            c["updated_at"] = _now.isoformat()
            return _ok(c)
    return {"success": False, "message": "Not found"}


@router.delete("/api/v1/store/admin/collections/{collection_id}")
async def stub_store_delete_collection(collection_id: int):
    return _ok(None)


# --- Products ---

@router.get("/api/v1/store/admin/products")
async def stub_store_products(page: int = 1, page_size: int = 20):
    return _paginated(_mock_store_products, page, page_size)


@router.post("/api/v1/store/admin/products")
async def stub_store_create_product(request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    pid = _next_store_id[0]; _next_store_id[0] += 1
    product = {
        "id": pid, "name": body.get("name", "新产品"),
        "slug": body.get("slug", f"new-product-{pid}"),
        "description": body.get("description", ""),
        "price": body.get("price", 0), "currency": body.get("currency", "CNY"),
        "images": body.get("images", []),
        "collection_id": body.get("collection_id"), "collection": None,
        "stock": body.get("stock", 0),
        "is_active": body.get("is_active", True),
        "sort_order": body.get("sort_order", 99),
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    }
    _mock_store_products.append(product)
    return _ok(product)


@router.put("/api/v1/store/admin/products/{product_id}")
async def stub_store_update_product(product_id: int, request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    for p in _mock_store_products:
        if p["id"] == product_id:
            updatable = ["name", "slug", "description", "price", "currency", "images", "collection_id", "stock", "sort_order", "is_active"]
            p.update({k: v for k, v in body.items() if v is not None and k in updatable})
            p["updated_at"] = _now.isoformat()
            return _ok(p)
    return {"success": False, "message": "Not found"}


@router.delete("/api/v1/store/admin/products/{product_id}")
async def stub_store_delete_product(product_id: int):
    return _ok(None)


# ===========================================================================
# === Tasks Management (admin-v2 TasksManagement.tsx) ===
# ===========================================================================

_mock_task_definitions = [
    {"id": 1, "name": "每日签到", "description": "每日签到获取积分", "points_reward": 10, "action_type": "daily_checkin", "action_config": {"reward": 10, "streak_bonus": 5}, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "下载 Skills", "description": "下载一个 Skills 获取积分", "points_reward": 20, "action_type": "download_skill", "action_config": {"daily_limit": 5}, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "发布评论", "description": "在 Skills 下发表评论", "points_reward": 5, "action_type": "post_comment", "action_config": {"daily_limit": 10}, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
]

_mock_achievements = [
    {"id": 1, "name": "签到达人", "description": "连续签到 7 天", "icon": "🏆", "badge_image": "", "criteria_type": "checkin_streak", "criteria_value": 7, "points_reward": 100, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 2, "name": "下载狂热", "description": "累计下载 100 个 Skills", "icon": "📥", "badge_image": "", "criteria_type": "download_count", "criteria_value": 100, "points_reward": 500, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
    {"id": 3, "name": "社区之星", "description": "发布评论数超过 50 条", "icon": "⭐", "badge_image": "", "criteria_type": "comment_count", "criteria_value": 50, "points_reward": 200, "is_active": True, "created_at": _now.isoformat(), "updated_at": _now.isoformat()},
]

# --- Task Definitions ---

@router.get("/api/v1/tasks/definitions")
async def stub_task_definitions(page: int = 1, page_size: int = 20):
    return _paginated(_mock_task_definitions, page, page_size)


@router.post("/api/v1/tasks/definitions")
async def stub_task_create_definition(request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    tid = _next_store_id[0]; _next_store_id[0] += 1
    task = {
        "id": tid, "name": body.get("name", "新任务"),
        "description": body.get("description", ""),
        "points_reward": body.get("points_reward", 0),
        "action_type": body.get("action_type", "custom"),
        "action_config": body.get("action_config", {}),
        "is_active": body.get("is_active", True),
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    }
    _mock_task_definitions.append(task)
    return _ok(task)


@router.put("/api/v1/tasks/definitions/{definition_id}")
async def stub_task_update_definition(definition_id: int, request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    for t in _mock_task_definitions:
        if t["id"] == definition_id:
            updatable = ["name", "description", "points_reward", "action_type", "action_config", "is_active"]
            t.update({k: v for k, v in body.items() if v is not None and k in updatable})
            t["updated_at"] = _now.isoformat()
            return _ok(t)
    return {"success": False, "message": "Not found"}


@router.delete("/api/v1/tasks/definitions/{definition_id}")
async def stub_task_delete_definition(definition_id: int):
    return _ok(None)


# --- Achievements ---

@router.get("/api/v1/tasks/achievements")
async def stub_achievements(page: int = 1, page_size: int = 20):
    return _paginated(_mock_achievements, page, page_size)


@router.post("/api/v1/tasks/achievements")
async def stub_achievement_create(request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    aid = _next_store_id[0]; _next_store_id[0] += 1
    achievement = {
        "id": aid, "name": body.get("name", "新成就"),
        "description": body.get("description", ""),
        "icon": body.get("icon", "🏆"), "badge_image": body.get("badge_image", ""),
        "criteria_type": body.get("criteria_type", "custom"),
        "criteria_value": body.get("criteria_value", 0),
        "points_reward": body.get("points_reward", 0),
        "is_active": body.get("is_active", True),
        "created_at": _now.isoformat(), "updated_at": _now.isoformat(),
    }
    _mock_achievements.append(achievement)
    return _ok(achievement)


@router.put("/api/v1/tasks/achievements/{achievement_id}")
async def stub_achievement_update(achievement_id: int, request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    for a in _mock_achievements:
        if a["id"] == achievement_id:
            updatable = ["name", "description", "icon", "badge_image", "criteria_type", "criteria_value", "points_reward", "is_active"]
            a.update({k: v for k, v in body.items() if v is not None and k in updatable})
            a["updated_at"] = _now.isoformat()
            return _ok(a)
    return {"success": False, "message": "Not found"}


@router.delete("/api/v1/tasks/achievements/{achievement_id}")
async def stub_achievement_delete(achievement_id: int):
    return _ok(None)


# ===========================================================================
# 安装函数
# ===========================================================================

def install_dev_stubs(app: FastAPI):
    """仅在开发模式下安装桩端点（在模块加载后调用，会覆盖真实模块的冲突路由）"""
    env = os.getenv("APP_ENV", "production")
    if env == "production":
        logger.info("Production mode: skipping dev stubs")
        return

    # 收集所有桩路由的 (path, methods) 信息
    stub_info = []  # (path, methods, endpoint)
    for r in router.routes:
        if hasattr(r, "path") and hasattr(r, "methods"):
            stub_info.append((r.path.rstrip("/"), r.methods, getattr(r, "endpoint", None)))

    # 步骤 1: 尝试从 app.routes 中移除冲突的真实路由
    stub_path_set = set()
    for path, methods, _ in stub_info:
        stub_path_set.add((path, tuple(methods or [])))

    before = len(app.routes)
    kept = []
    found = []
    for r in app.routes:
        if hasattr(r, "path") and hasattr(r, "methods"):
            key = (r.path.rstrip("/"), tuple(r.methods or []))
            if key in stub_path_set:
                found.append(key[0])
            else:
                kept.append(r)
        else:
            kept.append(r)
    app.router.routes = kept

    # 步骤 2: 通过 app.add_api_route 注册所有的桩路由到 app
    # 对于那些已通过步骤 1 移除的真实路由，这会添加对应的桩路由
    # 对于那些无法通过步骤 1 匹配的真实路由（prefix 包含在 APIRouter 中的模块），
    # 新加入的桩路由会被 move 到路由列表最前面
    for path, methods, endpoint in stub_info:
        if endpoint and methods:
            for method in methods:
                app.add_api_route(
                    path,
                    endpoint,
                    methods=[method],
                    include_in_schema=True,
                )

    # 步骤 3: 将所有注册过的 stub 端点移到路由列表最前面
    stub_endpoints = {ep for _, _, ep in stub_info if ep}
    stub_routes = []
    other_routes = []
    for r in app.routes:
        ep = getattr(r, "endpoint", None)
        if ep in stub_endpoints:
            stub_routes.append(r)
        else:
            other_routes.append(r)
    app.router.routes = stub_routes + other_routes

    after = len(app.routes)
    logger.info(
        f"Dev stubs installed: {len(stub_info)} endpoints "
        f"(removed {len(found)} conflicting routes)"
    )
