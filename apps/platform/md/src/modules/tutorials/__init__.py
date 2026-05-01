"""
技术教程模块 (Tutorials Module)

提供技术教程的浏览、分类筛选、搜索和章节管理功能

功能:
- 教程列表查询（支持分类、难度、精选、搜索筛选）
- 精选教程推荐
- 教程分类统计
- 教程详情（包含章节内容）
- 教程浏览次数记录
- 教程点赞
"""
from __future__ import annotations

from typing import List
from pydantic import BaseModel

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from core.template_helpers import render_template

from .routes import router as tutorials_router
from .services import TutorialService
from .schemas import (
    TutorialListItem,
    TutorialChapter,
    TutorialDetail,
    TutorialListResponse,
    TutorialResponse,
    CategoryCount,
)


# ============================================
# Module Info
# ============================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "tutorials"
    name: str = "技术教程模块"
    version: str = "1.0.0"
    description: str = "提供技术教程的浏览、分类筛选、搜索和章节管理功能"
    dependencies: List[str] = ["auth"]


# ============================================
# BaseModule
# ============================================

class BaseModule:
    """模块基类"""

    def __init__(self):
        self.id = "tutorials"
        self.name = "技术教程模块"
        self.version = "1.0.0"
        self.description = "提供技术教程的浏览、分类筛选、搜索和章节管理功能"
        self.dependencies = ["auth"]
        self.router = tutorials_router
        self._info = ModuleInfo()

    @property
    def module_id(self) -> str:
        """Get the unique identifier for this module."""
        return "tutorials"

    @property
    def info(self):
        """Get module info."""
        return self._info

    def get_router(self):
        """获取路由"""
        return self.router

    def install(self, app: FastAPI) -> None:
        """安装模块到应用"""
        app.include_router(self.router)
        # Page routes
        @app.get("/tutorials", response_class=HTMLResponse, include_in_schema=False)
        async def tutorials_page(request: Request):
            try:
                svc = TutorialService()
                result = svc.list_tutorials(featured=None, is_published=True, page=1, page_size=20)
                items = result.get("data", {}).get("items", []) if result.get("success") else []
                total_pages = result.get("data", {}).get("total_pages", 1) if result.get("success") else 1
                tutorials = []
                for t in items:
                    tutorials.append({
                        "slug": t.get("slug", ""),
                        "thumbnail": t.get("thumbnail") or "/static/img/tutorial-default.svg",
                        "title": t.get("title", ""),
                        "difficulty": t.get("difficulty", "beginner"),
                        "difficulty_label": t.get("difficulty", "beginner"),
                        "duration": t.get("video_duration", ""),
                        "category_name": t.get("category", ""),
                        "description": t.get("description", ""),
                        "views": t.get("view_count", 0),
                        "likes": t.get("like_count", 0),
                        "author_avatar": "/static/img/avatar-default.svg",
                        "author": "SillyMD",
                    })

                cats_result = svc.get_categories()
                cat_data = cats_result.get("data", {}) if cats_result.get("success") else {}
                categories = [
                    {"slug": k, "icon": v.get("icon", "fa-book"), "name": v.get("name", k), "count": v.get("count", 0)}
                    for k, v in cat_data.items()
                ]

                # Featured tutorial
                feat_result = svc.list_tutorials(featured=True, is_published=True, page=1, page_size=1)
                feat_data = feat_result.get("data", {}).get("items", []) if feat_result.get("success") else []
                featured = None
                if feat_data:
                    f = feat_data[0]
                    featured = {
                        "slug": f.get("slug", ""),
                        "thumbnail": f.get("thumbnail") or "/static/img/tutorial-default.svg",
                        "title": f.get("title", ""),
                        "description": f.get("description", ""),
                    }
            except Exception:
                tutorials, categories, featured, total_pages = [], [], None, 1

            return render_template(request, "tutorials/list.html", {
                "tutorials": tutorials,
                "categories": categories,
                "featured": featured,
                "current_filter": "all",
                "available_filters": [
                    {"slug": "all", "name": "全部"},
                    {"slug": "installation", "name": "安装"},
                    {"slug": "usage", "name": "使用"},
                    {"slug": "tips", "name": "技巧"},
                    {"slug": "advanced", "name": "进阶"},
                ],
                "total_pages": total_pages,
            })

        # --- Tutorial Detail Page ---
        @app.get("/tutorials/{id_or_slug}", response_class=HTMLResponse, include_in_schema=False)
        async def tutorial_detail_page(request: Request, id_or_slug: str):
            tutorial = {}
            chapters = []
            try:
                svc = TutorialService()
                result = svc.get_tutorial(id_or_slug)
                if result.get("success"):
                    data = result.get("data", {})
                    tutorial = {
                        "title": data.get("title", ""),
                        "description": data.get("description", ""),
                        "difficulty": data.get("difficulty", "beginner"),
                        "duration": data.get("video_duration", ""),
                        "video_url": data.get("video_url", ""),
                        "content": data.get("content", ""),
                        "thumbnail": data.get("thumbnail") or "/static/img/tutorial-default.svg",
                        "category": data.get("category", ""),
                        "tags": data.get("tags", []),
                        "view_count": data.get("view_count", 0),
                        "like_count": data.get("like_count", 0),
                    }
                    chapters = [
                        {
                            "title": ch.get("title", ""),
                            "content": ch.get("content", ""),
                            "video_url": ch.get("video_url", ""),
                            "duration": ch.get("video_start_time", ""),
                            "chapter_order": ch.get("chapter_order", i + 1),
                        }
                        for i, ch in enumerate(data.get("chapters", []))
                    ]
                    tutorial["chapters"] = chapters  # nested for template
            except Exception:
                tutorial, chapters = {}, []

            return render_template(request, "tutorials/detail.html", {
                "tutorial": tutorial,
                "chapters": chapters,
            })

    def get_services(self):
        """获取服务实例"""
        return {
            "tutorials": TutorialService
        }

    def get_config(self):
        """获取模块配置"""
        return {
            "page_size_default": 20,
            "featured_count": 6
        }


# 创建模块实例
module = BaseModule()


# 导出
__all__ = [
    # 模块信息
    "ModuleInfo",

    # 路由
    "tutorials_router",

    # 服务
    "TutorialService",

    # 模型
    "TutorialListItem",
    "TutorialChapter",
    "TutorialDetail",
    "TutorialListResponse",
    "TutorialResponse",
    "CategoryCount",

    # 模块
    "BaseModule",
    "module"
]
