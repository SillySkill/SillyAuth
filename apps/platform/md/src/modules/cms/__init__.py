"""
CMS Module
SillyMD Content Management Module

Provides tutorials, articles, guides, and category management functionality.

This module enables:
- Creating and managing articles (tutorials, articles, guides)
- Organizing content with categories
- Article search and filtering
- Featured articles
- Article likes and view tracking
- Category hierarchy management

Usage:
    from src.modules.cms import SillyMDModule, article_service, category_service

    # In your FastAPI app:
    cms_module = SillyMDModule()
    cms_module.register(app)

Module Structure:
    - config.yaml: Module configuration
    - schemas.py: Pydantic request/response models
    - services.py: Business logic layer (ArticleService, CategoryService)
    - routes.py: FastAPI route handlers
    - __init__.py: Module entry point

Example:
    ```python
    from src.modules.cms import SillyMDModule

    cms_module = SillyMDModule()
    cms_module.register(app)
    ```

Routes:
    Articles:
        - POST /api/cms/articles - Create article (Auth required)
        - GET /api/cms/articles - List articles (Public)
        - GET /api/cms/articles/featured - Get featured articles (Public)
        - GET /api/cms/articles/search - Search articles (Public)
        - GET /api/cms/articles/{id} - Get article (Public)
        - PUT /api/cms/articles/{id} - Update article (Auth required)
        - DELETE /api/cms/articles/{id} - Delete article (Auth required)
        - POST /api/cms/articles/{id}/like - Like article (Auth required)

    Categories:
        - GET /api/cms/categories - List categories (Public)
        - GET /api/cms/categories/{id} - Get category (Public)
        - GET /api/cms/categories/{id}/articles - Get category with articles (Public)
        - POST /api/cms/categories - Create category (Admin)
        - PUT /api/cms/categories/{id} - Update category (Admin)
        - DELETE /api/cms/categories/{id} - Delete category (Admin)

    Statistics:
        - GET /api/cms/stats/articles - Get article stats (Admin)
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yaml

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template
from pydantic import BaseModel

# Import components
from .schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListItem,
    ArticleList,
    ArticleSearchResult,
    FeaturedArticlesResponse,
    LikeResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryList,
    CategoryWithArticles,
    CMSResponse,
    CMSDeleteResponse,
    ArticleType,
    ArticleStatus,
)

from .services import (
    ArticleService,
    CategoryService,
    article_service,
    category_service,
)

from .routes import router as cms_router

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information."""
    id: str = "cms"
    name: str = "CMS 内容管理模块"
    version: str = "1.0.0"
    description: str = "提供教程、文章管理功能"
    dependencies: list = ["auth", "storage"]


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration."""
    max_article_length: int = 100000
    allowed_content_types: list = ["markdown", "html"]
    featured_articles_limit: int = 10


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD CMS Module

    Extends BaseModule pattern to integrate content management
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "cms"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CMS Module.

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        # Initialize services
        self.article_service = ArticleService(
            self.config.model_dump() if self.config else {}
        )
        self.category_service = CategoryService(
            self.config.model_dump() if self.config else {}
        )

        logger.info(f"CMS module initialized (v{self.info.version})")

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load module configuration from YAML file.

        Args:
            config_path: Optional path to config file
        """
        if config_path is None:
            # Default to module's config.yaml
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)

                # Load module-level config
                if config_data and 'config' in config_data:
                    self.config = ModuleConfig(**config_data['config'])
                else:
                    self.config = ModuleConfig()

                logger.info(f"Loaded config from {config_path}")

            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                self.config = ModuleConfig()
        else:
            logger.warning(f"Config file not found: {config_path}")
            self.config = ModuleConfig()

    def register(self, app: FastAPI) -> None:
        """
        Register module routes with FastAPI application.

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Include CMS routes
        app.include_router(cms_router)

        logger.info(f"CMS routes registered at {cms_router.prefix}")

        # Page routes
        @app.get("/", response_class=HTMLResponse, include_in_schema=False)
        async def index_page(request: Request):
            # Get hero slides from CMS articles
            try:
                hero_slides = self.article_service.get_hero_slides(limit=5)
            except Exception:
                hero_slides = []
            if not hero_slides:
                hero_slides = [{
                    "type": "image",
                    "src": "",
                    "title": "SillyMD",
                    "title_parts": [{"text": "SillyMD", "gradient": True, "break": False}],
                    "description": "AI Skills 创作与分享平台",
                    "badge": "AI 驱动",
                    "actions": [
                        {"url": "/skills", "style": "btn-primary btn-lg", "icon": "fas fa-compass", "label": "探索 Skills"},
                        {"url": "/creation", "style": "btn-ghost btn-lg", "icon": "fas fa-newspaper", "label": "精选好文"},
                    ],
                }, {
                    "type": "image",
                    "src": "",
                    "title": "开放共创",
                    "title_parts": [{"text": "开放共创", "gradient": True, "break": False}, {"text": " 释放 AI 创造力", "gradient": False, "break": False}],
                    "description": "社区驱动的 AI Skills 生态，让每个人都能参与 AI 应用创新",
                    "badge": "社区驱动",
                    "actions": [
                        {"url": "/register", "style": "btn-primary btn-lg", "icon": "fas fa-user-plus", "label": "立即加入"},
                    ],
                }]

            # Get aggregate stats
            try:
                stats = self.article_service.get_homepage_stats()
            except Exception:
                stats = []

            # Get featured skills from skills service
            featured_skills = []
            try:
                from modules.skills.services import skill_service as skills_svc
                all_skills, total = skills_svc.list_skills(
                    status='approved', page=1, limit=20
                )
                # Transform service data to template format
                for s in all_skills:
                    cat = s.get("category", "")
                    # Presentation-only mappings (not hardcoded data)
                    bg_map = {
                        "tech": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        "product": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                        "design": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                        "marketing": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
                        "ops": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
                    }
                    emoji_map = {
                        "tech": "⚡", "product": "📋", "design": "🎨",
                        "marketing": "📈", "ops": "🛠"
                    }
                    featured_skills.append({
                        "is_free": s.get("type") == "free",
                        "bg_gradient": bg_map.get(cat, "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
                        "emoji": emoji_map.get(cat, "🚀"),
                        "category": cat,
                        "id": s.get("id"),
                        "rating": float(s.get("rating_avg", 0) or 0),
                        "name": s.get("display_name") or s.get("name", ""),
                        "slug": s.get("skill_id", ""),
                        "description": s.get("display_description") or s.get("description", ""),
                        "author_avatar": s.get("author_avatar") or "/static/img/avatar-default.svg",
                        "author": s.get("author_username", ""),
                        "downloads": s.get("download_count", 0),
                        "likes": s.get("favorite_count", 0),
                        "price": f"¥{s['price']}" if s.get("price", 0) > 0 else "免费"
                    })
            except Exception as e:
                logger.warning(f"Failed to load featured skills: {e}")

            # Get vendors from service
            try:
                vendors = self.article_service.get_homepage_vendors(limit=8)
            except Exception:
                vendors = []

            # Get platform features
            try:
                features = self.article_service.get_homepage_features()
            except Exception:
                features = []

            # Get learning center categories
            try:
                categories = self.article_service.get_homepage_categories(limit=6)
            except Exception:
                categories = []

            # Get featured tutorials
            try:
                tutorials = self.article_service.get_homepage_tutorials(limit=3)
            except Exception:
                tutorials = []

            return render_template(request, "index.html", {
                "hero_slides": hero_slides,
                "stats": stats,
                "featured_skills": featured_skills,
                "vendors": vendors,
                "features": features,
                "categories": categories,
                "tutorials": tutorials
            })

        @app.get("/features", response_class=HTMLResponse, include_in_schema=False)
        async def features_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                features = []
                pricing_plans = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("platform_features", "features"))
                        row = cur.fetchone()
                        if row and row.get("data"):
                            raw = row["data"]
                            import json as _jf
                            raw_features = _jf.loads(raw) if isinstance(raw, str) else raw
                            icon_bg_map = ["#10B981", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444", "#06B6D4"]
                            for i, f in enumerate(raw_features):
                                features.append({
                                    "title": f.get("title", ""),
                                    "description": f.get("description", ""),
                                    "icon_class": f.get("icon", "fa-star"),
                                    "icon_bg": icon_bg_map[i % len(icon_bg_map)],
                                })
                except Exception:
                    features = []

                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT name, data FROM config_data WHERE category=%s ORDER BY name", ("pricing",))
                        rows = cur.fetchall()
                        plan_order = {"plan_free": 0, "plan_pro": 1, "plan_enterprise": 2}
                        import json as _jp
                        for r in sorted(rows, key=lambda x: plan_order.get(x.get("name", ""), 99)):
                            raw = r["data"]
                            p = _jp.loads(raw) if isinstance(raw, str) else raw
                            pricing_plans.append({
                                "name": p.get("name", ""),
                                "amount": p.get("amount", 0),
                                "currency": p.get("currency", "¥"),
                                "period": p.get("period", "/月"),
                                "description": p.get("description", ""),
                                "featured": p.get("is_featured", False),
                                "badge": p.get("badge", ""),
                                "features_list": p.get("features", []),
                                "cta_url": p.get("cta_url", "/register"),
                                "cta_text": p.get("cta_text", "开始使用"),
                            })
                except Exception:
                    pricing_plans = []
            except Exception:
                features, pricing_plans = [], []

            return render_template(request, "sillyfu/features.html", {
                "features": features,
                "pricing_plans": pricing_plans,
            })

        @app.get("/user-center", response_class=HTMLResponse, include_in_schema=False)
        async def user_center_page(request: Request):
            user = getattr(request.state, "user", None)
            profile = dict(user) if user else {}
            if user and user.get("id"):
                try:
                    from core.db_adapter import get_db_cursor
                    with get_db_cursor() as cur:
                        cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE author_id = %s AND is_deleted = FALSE", (user["id"],))
                        profile["skills_count"] = cur.fetchone()["cnt"]
                        cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE user_id = %s", (user["id"],))
                        profile["orders_count"] = cur.fetchone()["cnt"]
                        cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM user_points WHERE user_id = %s AND amount > 0", (user["id"],))
                        profile["points"] = cur.fetchone()["total"]
                except Exception:
                    pass
            return render_template(request, "user/center.html", {"profile": profile})

        @app.get("/settings", response_class=HTMLResponse, include_in_schema=False)
        async def settings_page(request: Request):
            return render_template(request, "user/settings.html")

        @app.get("/projects", response_class=HTMLResponse, include_in_schema=False)
        async def projects_page(request: Request):
            return render_template(request, "user/projects.html")

        @app.get("/creation", response_class=HTMLResponse, include_in_schema=False)
        async def featured_articles_page(request: Request):
            """精选好文页面 - 展示管理员后台发布的已发布文章"""
            articles = []
            try:
                result = self.article_service.list_articles(
                    article_type="article", status="published", limit=20
                )
                if isinstance(result, tuple):
                    result = result[0]
                for a in (result if isinstance(result, list) else []):
                    articles.append({
                        "id": a.get("id", 0),
                        "title": a.get("title", ""),
                        "slug": a.get("slug", ""),
                        "summary": a.get("summary", "") or a.get("description", ""),
                        "content": a.get("content", ""),
                        "category_name": a.get("category_name", ""),
                        "author_username": a.get("author_username", ""),
                        "created_at": str(a.get("created_at", ""))[:10],
                        "view_count": a.get("view_count", 0),
                        "tags": a.get("tags", []),
                        "featured_image": a.get("featured_image", ""),
                    })
            except Exception as e:
                logger.warning(f"Failed to load featured articles: {e}")

            return render_template(request, "user/creation.html", {
                "articles": articles,
            })

        # --- Pricing Page ---
        @app.get("/pricing", response_class=HTMLResponse, include_in_schema=False)
        async def pricing_page(request: Request):
            try:
                from core.db_adapter import get_db_cursor
                pricing_plans = []
                try:
                    with get_db_cursor() as cur:
                        cur.execute("SELECT name, data FROM config_data WHERE category=%s ORDER BY name", ("pricing",))
                        rows = cur.fetchall()
                        import json as _jp2
                        plan_order = {"plan_free": 0, "plan_pro": 1, "plan_enterprise": 2}
                        for r in sorted(rows, key=lambda x: plan_order.get(x.get("name", ""), 99)):
                            raw = r["data"]
                            p = _jp2.loads(raw) if isinstance(raw, str) else raw
                            pricing_plans.append({
                                "name": p.get("name", ""),
                                "amount": p.get("amount", 0),
                                "currency": p.get("currency", "¥"),
                                "period": p.get("period", "/月"),
                                "description": p.get("description", ""),
                                "featured": p.get("is_featured", False),
                                "badge": p.get("badge", ""),
                                "features_list": p.get("features", []),
                                "cta_url": p.get("cta_url", "/register"),
                                "cta_text": p.get("cta_text", "开始使用"),
                            })
                except Exception:
                    pass
            except Exception:
                pricing_plans = []
            return render_template(request, "pricing.html", {"pricing_plans": pricing_plans})

        # --- About Page ---
        @app.get("/about", response_class=HTMLResponse, include_in_schema=False)
        async def about_page(request: Request):
            about_data = {}
            try:
                from core.db_adapter import get_db_cursor
                with get_db_cursor() as cur:
                    cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("about", "content"))
                    row = cur.fetchone()
                    if row and row.get("data"):
                        raw = row["data"]
                        import json as _ja2
                        about_data = _ja2.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                pass
            return render_template(request, "about.html", {"about_data": about_data})

        # --- Contact Page ---
        @app.get("/contact", response_class=HTMLResponse, include_in_schema=False)
        async def contact_page(request: Request):
            contact_info = {}
            try:
                from core.db_adapter import get_db_cursor
                with get_db_cursor() as cur:
                    cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", ("contact", "info"))
                    row = cur.fetchone()
                    if row and row.get("data"):
                        raw = row["data"]
                        import json as _jc
                        contact_info = _jc.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                pass
            return render_template(request, "contact.html", {
                "contact_info": contact_info,
                "csrf_token": "",
            })

        # --- Privacy Policy Page ---
        @app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
        async def privacy_page(request: Request):
            return await self._policy_page(request, "privacy", "隐私政策")

        # --- Terms of Service Page ---
        @app.get("/terms", response_class=HTMLResponse, include_in_schema=False)
        async def terms_page(request: Request):
            return await self._policy_page(request, "terms", "服务条款")

        # --- Help Center Page ---
        @app.get("/help", response_class=HTMLResponse, include_in_schema=False)
        async def help_page(request: Request):
            help_articles = []
            try:
                help_articles = self.article_service.list_articles(
                    article_type="help", status="published", limit=50
                )
                if isinstance(help_articles, tuple):
                    help_articles = help_articles[0]
                help_articles = [{
                    "title": a.get("title", ""),
                    "slug": a.get("slug", ""),
                    "summary": a.get("summary", "") or a.get("description", ""),
                    "category": a.get("category_name", "常见问题"),
                } for a in (help_articles if isinstance(help_articles, list) else [])]
            except Exception:
                pass
            return render_template(request, "help.html", {"help_articles": help_articles})

        # --- Community Page ---
        @app.get("/community", response_class=HTMLResponse, include_in_schema=False)
        async def community_page(request: Request):
            return render_template(request, "community.html")

        # --- Teams Page ---
        @app.get("/teams", response_class=HTMLResponse, include_in_schema=False)
        async def teams_page(request: Request):
            return render_template(request, "teams.html", {"teams": []})

        # --- Upload Page ---
        @app.get("/upload", response_class=HTMLResponse, include_in_schema=False)
        async def upload_page(request: Request):
            return render_template(request, "upload.html")

        # --- Docs Index Page ---
        @app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
        async def docs_index_page(request: Request):
            doc_categories = []
            try:
                cat_result = self.category_service.list_categories()
                items = cat_result.items if hasattr(cat_result, 'items') else cat_result
                if isinstance(items, dict) and 'items' in items:
                    items = items['items']
                for c in (items if isinstance(items, list) else []):
                    cid = c.id if hasattr(c, 'id') else c.get('id', 0)
                    cname = c.name if hasattr(c, 'name') else c.get('name', '')
                    cslug = c.slug if hasattr(c, 'slug') else c.get('slug', '')
                    cdesc = c.description if hasattr(c, 'description') else c.get('description', '')
                    doc_categories.append({
                        "id": cid, "name": cname, "slug": cslug,
                        "description": cdesc, "article_count": 0,
                    })
            except Exception:
                pass
            return render_template(request, "docs/index.html", {
                "doc_categories": doc_categories,
                "quick_start_articles": [],
            })

        # --- Docs Category Page ---
        @app.get("/docs/{slug}", response_class=HTMLResponse, include_in_schema=False)
        async def docs_category_page(request: Request, slug: str):
            category = {"name": slug, "description": ""}
            articles = []
            try:
                cat_result = self.category_service.list_categories()
                items = cat_result.items if hasattr(cat_result, 'items') else cat_result
                if isinstance(items, dict) and 'items' in items:
                    items = items['items']
                for c in (items if isinstance(items, list) else []):
                    cs = c.slug if hasattr(c, 'slug') else c.get('slug', '')
                    if cs == slug:
                        cn = c.id if hasattr(c, 'id') else c.get('id')
                        category = {
                            "id": cn, "name": c.name if hasattr(c, 'name') else c.get('name', slug),
                            "slug": cs,
                            "description": c.description if hasattr(c, 'description') else c.get('description', ''),
                        }
                        arts, _ = self.article_service.list_articles(category_id=cn, status="published", limit=100)
                        for a in (arts if isinstance(arts, list) else []):
                            articles.append({
                                "title": a.get("title", ""),
                                "slug": a.get("slug", ""),
                                "summary": a.get("summary", "") or a.get("description", ""),
                                "tags": a.get("tags", []),
                            })
                        break
            except Exception:
                pass
            return render_template(request, "docs/category.html", {"category": category, "articles": articles})

        # --- Article Detail Page ---
        @app.get("/articles/{slug}", response_class=HTMLResponse, include_in_schema=False)
        async def article_detail_page(request: Request, slug: str):
            article = {}
            try:
                with get_db_cursor() as cur:
                    cur.execute("SELECT id FROM articles WHERE slug = %s AND status = 'published'", (slug,))
                    row = cur.fetchone()
                    if row:
                        a = self.article_service.get_article(row["id"], increment_views=True)
                        if a:
                            title_val = a.title if hasattr(a, 'title') else a.get("title", "")
                            content_val = a.content if hasattr(a, 'content') else a.get("content", "")
                            summary_val = a.summary if hasattr(a, 'summary') else (a.get("summary", "") if isinstance(a, dict) else "")
                            category_name_val = a.category.name if (hasattr(a, 'category') and a.category) else ""
                            category_slug_val = a.category.slug if (hasattr(a, 'category') and a.category) else ""
                            read_time = max(1, len(content_val.split()) // 200) if content_val else 1
                            import re
                            headings = []
                            for m in re.finditer(r'<[hH]([2-4])[^>]*>(.*?)</[hH]\\1>', content_val or ""):
                                h_text = re.sub(r'<[^>]+>', '', m.group(2))
                                headings.append({"anchor": "heading-" + str(len(headings)), "text": h_text, "level": int(m.group(1))})
                            article = {
                                "title": title_val,
                                "content": content_val,
                                "author": a.author.username if (hasattr(a, 'author') and a.author) else (a.get("author_username", "") if isinstance(a, dict) else ""),
                                "created_at": str(a.created_at if hasattr(a, 'created_at') else a.get("created_at", "")),
                                "category_name": category_name_val,
                                "category_slug": category_slug_val,
                                "tags": a.tags if hasattr(a, 'tags') else a.get("tags", []),
                                "view_count": a.view_count if hasattr(a, 'view_count') else a.get("view_count", 0),
                                "summary": summary_val,
                                "read_time": read_time,
                                "headings": headings,
                                "prev_article": None,
                                "next_article": None,
                                "related_articles": [],
                            }
            except Exception:
                pass
            return render_template(request, "articles/detail.html", {"article": article})

    async def _policy_page(self, request: Request, policy_type: str, title: str):
        """Shared handler for privacy and terms pages."""
        policy_content = ""
        policy_title = title
        try:
            from core.db_adapter import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("SELECT data FROM config_data WHERE category=%s AND name=%s", (policy_type, "policy_html"))
                row = cur.fetchone()
                if row and row.get("data"):
                    raw = row["data"]
                    import json as _jpo
                    data = _jpo.loads(raw) if isinstance(raw, str) else raw
                    if isinstance(data, dict):
                        policy_content = data.get("content", data.get("html", title))
                        policy_title = data.get("title", title)
                    else:
                        policy_content = str(data)
        except Exception:
            pass
        return render_template(request, "policy.html", {
            "policy_title": policy_title,
            "policy_content": policy_content,
        })

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook.

        Called when the application starts.
        Performs initialization tasks like:
        - Database connection verification
        - Cache initialization
        - Background task registration
        """
        logger.info("CMS module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            cursor = get_db_cursor()
            if cursor:
                with cursor as cur:
                    cur.execute("SELECT 1")
                logger.info("CMS module database connection verified")
        except Exception as e:
            logger.warning(f"CMS module database connection check failed: {e}")

        # TODO: Initialize search index
        # TODO: Start background tasks for statistics aggregation

        logger.info("CMS module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook.

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Canceling background tasks
        """
        logger.info("CMS module shutting down...")

        # TODO: Flush search index
        # TODO: Cancel background tasks
        # TODO: Close database connections

        logger.info("CMS module shutdown complete")

    def get_routes(self) -> list:
        """
        Get list of registered routes.

        Returns:
            List of route dictionaries with method, path, and handler info
        """
        if not self.app:
            return []

        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/cms'):
                routes.append({
                    "method": getattr(route, 'methods', {'GET'}).__iter__().__next__(),
                    "path": route.path,
                    "name": getattr(route, 'name', 'unnamed')
                })

        return routes

    def get_info(self) -> Dict[str, Any]:
        """
        Get module information.

        Returns:
            Dict containing module info
        """
        return {
            "id": self.info.id,
            "name": self.info.name,
            "version": self.info.version,
            "description": self.info.description,
            "dependencies": self.info.dependencies,
            "config": self.config.model_dump() if self.config else None
        }


# ============================================================================
# Exports
# ============================================================================

__version__ = "1.0.0"

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "ArticleService",
    "CategoryService",
    "article_service",
    "category_service",

    # Schemas - Article
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleResponse",
    "ArticleListItem",
    "ArticleList",
    "ArticleSearchResult",
    "FeaturedArticlesResponse",
    "LikeResponse",
    "ArticleType",
    "ArticleStatus",

    # Schemas - Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryList",
    "CategoryWithArticles",

    # Schemas - Generic
    "CMSResponse",
    "CMSDeleteResponse",

    # Routes
    "router",
]
