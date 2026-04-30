"""
技术教程 API 路由
提供教程的查询、分类筛选、搜索等功能
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .services import TutorialService

router = APIRouter(prefix="/api/v1/tutorials", tags=["tutorials"])


# ============================================
# GET / - 获取教程列表
# ============================================

@router.get("/")
async def list_tutorials(
    category: Optional[str] = Query(None, description="工具分类"),
    subcategory: Optional[str] = Query(None, description="子分类"),
    difficulty: Optional[str] = Query(None, description="难度级别"),
    featured: Optional[bool] = Query(None, description="是否精选"),
    is_published: bool = Query(True, description="是否已发布"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    lang: str = Query("zh-CN", description="语言"),
):
    """
    获取教程列表

    支持按分类、难度、精选状态筛选，支持关键词搜索
    """
    try:
        service = TutorialService()
        result = service.list_tutorials(
            category=category,
            subcategory=subcategory,
            difficulty=difficulty,
            featured=featured,
            is_published=is_published,
            page=page,
            page_size=page_size,
            search=search,
            lang=lang,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GET /featured - 获取精选教程
# ============================================

@router.get("/featured")
async def get_featured_tutorials(
    limit: int = Query(6, ge=1, le=20, description="返回数量"),
    lang: str = Query("zh-CN", description="语言"),
):
    """
    获取精选教程列表

    用于首页推荐
    """
    try:
        service = TutorialService()
        result = service.get_featured(limit=limit, lang=lang)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GET /categories - 获取教程分类统计
# ============================================

@router.get("/categories")
async def get_tutorial_categories():
    """
    获取教程分类统计

    返回每个分类下的教程数量
    """
    try:
        service = TutorialService()
        result = service.get_categories()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GET /{id_or_slug} - 获取教程详情
# ============================================

@router.get("/{id_or_slug}")
async def get_tutorial_detail(
    id_or_slug: str,
    lang: str = Query("zh-CN", description="语言"),
):
    """
    获取教程详情

    支持通过 ID 或 slug 查询
    同时返回章节列表
    """
    try:
        service = TutorialService()
        result = service.get_tutorial(id_or_slug=id_or_slug, lang=lang)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POST /{tutorial_id}/view - 记录浏览
# ============================================

@router.post("/{tutorial_id}/view")
async def record_tutorial_view(tutorial_id: int):
    """
    记录教程浏览次数
    """
    try:
        service = TutorialService()
        result = service.record_view(tutorial_id=tutorial_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POST /{tutorial_id}/like - 点赞教程
# ============================================

@router.post("/{tutorial_id}/like")
async def like_tutorial(tutorial_id: int):
    """
    点赞教程
    """
    try:
        service = TutorialService()
        result = service.like_tutorial(tutorial_id=tutorial_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
