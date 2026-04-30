"""
技术教程数据模型
定义教程系统相关的Pydantic v2模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any


class TutorialListItem(BaseModel):
    """教程列表项"""
    id: int
    tutorial_key: str
    slug: str
    title: str
    title_zh_CN: str
    title_en: Optional[str] = None
    description: str
    description_zh_CN: str
    description_en: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    difficulty: str
    tags: List[str] = []
    thumbnail: Optional[str] = None
    video_url: Optional[str] = None
    video_type: Optional[str] = None
    video_duration: Optional[int] = None
    github_url: Optional[str] = None
    documentation_url: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    featured: bool = False
    is_published: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TutorialChapter(BaseModel):
    """教程章节"""
    id: int
    chapter_order: int
    chapter_key: str
    title: str
    title_zh_CN: str
    title_en: Optional[str] = None
    description: Optional[str] = None
    description_zh_CN: Optional[str] = None
    description_en: Optional[str] = None
    content: Optional[str] = None
    content_zh_CN: Optional[str] = None
    content_en: Optional[str] = None
    video_url: Optional[str] = None
    video_start_time: Optional[int] = None
    video_end_time: Optional[int] = None
    is_free: bool = False
    code_snippets: List[dict] = []
    attachments: List[dict] = []


class TutorialDetail(BaseModel):
    """教程详情"""
    id: int
    tutorial_key: str
    slug: str
    title: str
    title_zh_CN: str
    title_en: Optional[str] = None
    description: str
    description_zh_CN: str
    description_en: Optional[str] = None
    content: Optional[str] = None
    content_zh_CN: Optional[str] = None
    content_en: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    difficulty: str
    tags: List[str] = []
    thumbnail: Optional[str] = None
    video_url: Optional[str] = None
    video_type: Optional[str] = None
    video_duration: Optional[int] = None
    video_file_size: Optional[int] = None
    github_url: Optional[str] = None
    documentation_url: Optional[str] = None
    official_website: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    featured: bool = False
    is_pinned: bool = False
    is_published: bool = False
    chapters: List[TutorialChapter] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PaginatedData(BaseModel):
    """分页数据"""
    items: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class TutorialListResponse(BaseModel):
    """教程列表响应"""
    success: bool
    data: PaginatedData


class TutorialResponse(BaseModel):
    """教程详情响应"""
    success: bool
    data: TutorialDetail


class CategoryCountItem(BaseModel):
    """分类统计项"""
    name: str
    icon: str
    count: int = 0


class CategoryCount(BaseModel):
    """分类统计"""
    category: str
    name: str
    icon: str
    count: int = 0


class CategoriesResponse(BaseModel):
    """分类列表响应"""
    success: bool
    data: dict
