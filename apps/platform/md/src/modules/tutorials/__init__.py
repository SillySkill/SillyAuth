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
