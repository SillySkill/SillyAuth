"""
Skills Module
SillyMD Skills Platform Module

Provides skills hosting, publishing, and management functionality.
This module handles CRUD operations, version control, and publishing workflows
for AI Skills on the SillyMD platform.

Features:
- Skill creation, editing, and deletion
- Version management
- Category and tag organization
- Publishing workflow (draft -> reviewing -> approved)
- Statistics tracking
- Admin approval system

Usage:
    from src.modules.skills import SillyMDModule

    # In your FastAPI app:
    skills_module = SillyMDModule()
    skills_module.register(app)

Module Structure:
    - config.yaml: Module configuration
    - schemas.py: Pydantic request/response models
    - services.py: Business logic layer
    - routes.py: FastAPI route handlers
    - __init__.py: Module entry point
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template
from pydantic import BaseModel

# Import routes at module level
from .routes import router as skills_router

# Import services
from .services import SkillService, skill_service

logger = logging.getLogger(__name__)


# ============================================================================
# Module Info
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "skills"
    name: str = "Skills 平台模块"
    version: str = "1.0.0"
    description: str = "提供 Skills 托管、发布、管理功能"
    dependencies: list = ["auth", "storage", "skill2"]


# ============================================================================
# Module Config
# ============================================================================

class ModuleConfig(BaseModel):
    """Module configuration"""
    max_skill_size_mb: int = 100
    allowed_extensions: List[str] = ["py", "js", "json", "yaml"]
    approval_required: bool = True


# ============================================================================
# SillyMD Module
# ============================================================================

class SillyMDModule:
    """
    SillyMD Skills Module

    Extends BaseModule pattern to integrate skills
    functionality into the SillyMD application.
    """

    # Module identifier for PluginManager registration
    module_id: str = "skills"

    # Module info
    info = ModuleInfo()

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Skills Module

        Args:
            config_path: Optional path to config.yaml file
        """
        self.config: Optional[ModuleConfig] = None
        self.app: Optional[FastAPI] = None
        self.state = None
        self._load_config(config_path)

        # Initialize services
        self.skill_service = SkillService()

        logger.info(f"Skills module initialized (v{self.info.version})")

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load module configuration from YAML file

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
        Register module routes with FastAPI application

        Args:
            app: FastAPI application instance
        """
        self.app = app

        # Include skills routes
        app.include_router(skills_router)

        logger.info(f"Skills routes registered at {skills_router.prefix} (v2)")

        # Page routes
        @app.get("/skills", response_class=HTMLResponse, include_in_schema=False)
        async def skills_list_page(request: Request):
            search_query = request.query_params.get("search", "")
            sort_by = request.query_params.get("sort", "default")
            page = int(request.query_params.get("page", 1))

            skills_list = []
            total_count = 0
            try:
                all_skills, total_count = self.skill_service.list_skills(
                    search=search_query if search_query else None,
                    page=page,
                    limit=20,
                    status="approved"
                )
                # Transform to template format
                cat_label_map = {
                    "tech": "技术", "product": "产品", "design": "设计",
                    "marketing": "市场", "ops": "运营"
                }
                bg_map = {
                    "tech": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "product": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                    "design": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                    "marketing": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
                    "ops": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
                }
                for s in all_skills:
                    cat = s.get("category", "")
                    skills_list.append({
                        "id": s.get("id"),
                        "is_free": s.get("type") == "free",
                        "bg_gradient": bg_map.get(cat, "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
                        "emoji": "⚡",
                        "category_label": cat_label_map.get(cat, cat),
                        "category": cat,
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
                logger.warning(f"Failed to load skills list: {e}")

            # Sort (client-side request only, re-query with sort param)
            current_sort = sort_by

            # Build filter groups from categories
            filter_groups = []
            try:
                categories = self.skill_service.get_categories()
                cat_options = []
                for cat in categories:
                    cat_options.append({
                        "value": cat["key"],
                        "label": cat["name"],
                        "selected": False  # No active category filter by default
                    })
                filter_groups.append({
                    "label": "分类",
                    "name": "category",
                    "options": cat_options
                })
                filter_groups.append({
                    "label": "类型",
                    "name": "type",
                    "options": [
                        {"value": "free", "label": "免费", "selected": False},
                        {"value": "commercial", "label": "付费", "selected": False}
                    ]
                })
            except Exception as e:
                logger.debug(f"Failed to load filter groups: {e}")

            hot_tags = ["JWT", "React", "Redis", "微服务", "DevOps", "Figma", "数据分析"]

            return render_template(request, "skills/list.html", {
                "search_query": search_query,
                "hot_tags": hot_tags,
                "filter_groups": filter_groups,
                "total_count": total_count,
                "total_pages": (total_count + 19) // 20,
                "current_page": page,
                "current_sort": current_sort,
                "skills": skills_list
            })

        @app.get("/skills/{skill_id}", response_class=HTMLResponse, include_in_schema=False)
        async def skill_detail_page(request: Request, skill_id: int):
            try:
                raw = skill_service.get_skill_by_id(skill_id)
                if raw is None:
                    raise ValueError("Skill not found")
                tags = raw.get("tags")
                if isinstance(tags, str):
                    try:
                        import json as _j
                        tags = _j.loads(tags)
                    except Exception:
                        tags = [t.strip() for t in tags.split(",") if t.strip()]
                elif not isinstance(tags, list):
                    tags = []
                price_val = raw.get("price", 0) or 0
                is_free = str(raw.get("type", "")).lower() == "free" or price_val == 0
                skill = {
                    "skill_id": skill_id,
                    "name": raw.get("name", ""),
                    "industry": None,
                    "scenario": None,
                    "level": raw.get("skill_id", "")[:1].upper() if raw.get("skill_id") else None,
                    "description": raw.get("description", ""),
                    "rating": float(raw.get("rating_avg", 0) or 0),
                    "downloads": raw.get("download_count", 0),
                    "version": raw.get("version", "1.0.0"),
                    "updated_at": str(raw.get("updated_at", ""))[:10] if raw.get("updated_at") else "",
                    "review_count": raw.get("rating_count", 0),
                    "features": [],
                    "quickstart": None,
                    "author_avatar": raw.get("author_avatar") or "/static/img/avatar-default.svg",
                    "author": raw.get("author_username", ""),
                    "author_bio": None,
                    "vendor_level": None,
                    "vendor_stats": {"skills_count": 0, "sales": 0, "rating": 0},
                    "documentation": None,
                    "config_example": None,
                    "reviews": [],
                    "changelog": [],
                    "price_display": "免费" if is_free else f"¥{price_val}",
                    "purchase_url": None,
                    "benefits": [],
                    "tags": tags,
                    "category": raw.get("category", ""),
                }
            except Exception as e:
                logger.warning(f"Skill detail page failed for skill_id={skill_id}: {e}")
                skill = {"skill_id": skill_id, "name": "Skill 未找到", "description": "该 Skill 不存在或已被删除"}
            return render_template(request, "skills/detail.html", {"skill": skill})

        # --- Creation Hub Page Routes (removed - 精选好文 replaces creation center) ---

    def install(self, app: FastAPI) -> None:
        """Alias for register() - for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """
        Module startup hook

        Called when the application starts.
        Performs initialization tasks like:
        - Database connection verification
        - Cache initialization
        - Background task registration
        """
        logger.info("Skills module starting up...")

        # Verify database connection
        try:
            from .services import get_db_cursor
            with get_db_cursor() as cur:
                cur.execute("SELECT 1")
            logger.info("Skills module database connection verified")
        except Exception as e:
            logger.error(f"Skills module database connection failed: {e}")

        logger.info("Skills module startup complete")

    def on_shutdown(self) -> None:
        """
        Module shutdown hook

        Called when the application shuts down.
        Performs cleanup tasks like:
        - Closing database connections
        - Flushing caches
        - Canceling background tasks
        """
        logger.info("Skills module shutting down...")

        logger.info("Skills module shutdown complete")

    def get_routes(self) -> list:
        """
        Get list of registered routes

        Returns:
            List of route dictionaries with method, path, and handler info
        """
        if not self.app:
            return []

        from .routes import router as skills_router
        routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path.startswith(skills_router.prefix):
                methods = getattr(route, 'methods', {'GET'})
                routes.append({
                    "method": list(methods)[0] if methods else "GET",
                    "path": route.path,
                    "name": getattr(route, 'name', 'unnamed')
                })

        return routes

    def get_info(self) -> Dict[str, Any]:
        """
        Get module information

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

__all__ = [
    # Module class
    "SillyMDModule",

    # Module info
    "ModuleInfo",

    # Services
    "SkillService",
    "skill_service",

    # Routes
    "router",

    # Schemas
    "schemas",
]

# Also export skills_router for plugin_manager
router = skills_router
