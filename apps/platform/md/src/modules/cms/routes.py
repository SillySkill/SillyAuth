"""
CMS Module Routes
FastAPI routes for content management endpoints

Provides article, tutorial, guide, and category management endpoints
"""

import os
import math
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

from .services import article_service, category_service, ArticleService, CategoryService
from core.db_adapter import get_db_cursor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/cms", tags=["内容管理"])

# HTTP Bearer security scheme
security = HTTPBearer()

# ============================================================================
# Helper Functions
# ============================================================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dict from database

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from .services import SECRET_KEY, ALGORITHM
    from jose import jwt, JWTError

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Get secret key and algorithm from auth module
        try:
            from server.modules.auth.services import SECRET_KEY, ALGORITHM
        except ImportError:
            SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION")
            ALGORITHM = "HS256"

        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("user_id")
        if not user_id:
            raise credentials_exception

        # Get user from database
        db_cursor = get_db_cursor()
        if db_cursor:
            with db_cursor as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()

            if not user:
                raise credentials_exception

            # Check if user is active
            if not user.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户已被禁用"
                )

            return user
        else:
            raise credentials_exception

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise credentials_exception


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current admin user.

    Args:
        current_user: Current authenticated user

    Returns:
        User dict if admin

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get('role') not in ['admin', 'moderator']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def check_admin_permission(user: dict) -> bool:
    """
    Check if user has admin permission.

    Args:
        user: User dict

    Returns:
        True if user is admin or moderator
    """
    return user.get('role') in ['admin', 'moderator']


# ============================================================================
# Article Routes
# ============================================================================

@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new article.

    Requires authentication. Admin/Moderator can create articles for any user.
    Regular users create articles as themselves.

    Args:
        article_data: Article creation data

    Returns:
        Created article
    """
    author_id = article_data.author_id if (
        check_admin_permission(current_user) and hasattr(article_data, 'author_id')
    ) else current_user['id']

    article = article_service.create_article(author_id, article_data)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文章创建失败，请检查内容长度是否超过限制"
        )

    logger.info(f"Article created: {article.id} by user {author_id}")
    return article


@router.get("/articles", response_model=ArticleList)
async def list_articles(
    category_id: Optional[int] = Query(None, description="Category ID filter"),
    tag: Optional[str] = Query(None, description="Tag filter"),
    author_id: Optional[int] = Query(None, description="Author ID filter"),
    type: Optional[ArticleType] = Query(None, description="Article type filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    include_unpublished: bool = Query(False, description="Include unpublished (admin only)")
):
    """
    List articles with filtering and pagination.

    Public endpoint. By default only shows published articles.
    Admin/Moderator can include unpublished articles.

    Args:
        category_id: Filter by category ID
        tag: Filter by tag
        author_id: Filter by author ID
        type: Filter by article type
        page: Page number (1-indexed)
        limit: Items per page
        include_unpublished: Include unpublished articles

    Returns:
        Paginated article list
    """
    status_filter = None if include_unpublished else ArticleStatus.PUBLISHED

    articles, total = article_service.list_articles(
        category_id=category_id,
        tag=tag,
        author_id=author_id,
        article_type=type,
        status=status_filter,
        page=page,
        limit=limit
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return ArticleList(
        items=articles,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/articles/featured", response_model=FeaturedArticlesResponse)
async def get_featured_articles(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of articles")
):
    """
    Get featured articles.

    Public endpoint. Returns articles marked as featured.

    Args:
        limit: Maximum number of articles to return

    Returns:
        Featured articles
    """
    return article_service.get_featured(limit=limit)


@router.get("/articles/search", response_model=ArticleSearchResult)
async def search_articles(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Search articles by keyword.

    Public endpoint. Searches in title, content, and tags.

    Args:
        q: Search query string
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Search results with matching articles
    """
    return article_service.search_articles(query=q, page=page, limit=limit)


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    increment_views: bool = Query(True, description="Increment view count")
):
    """
    Get article by ID.

    Public endpoint. Returns full article content.
    View count is incremented by default.

    Args:
        article_id: Article ID
        increment_views: Whether to increment view count

    Returns:
        Article details
    """
    article = article_service.get_article(article_id, increment_views=increment_views)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    return article


@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing article.

    Requires authentication. Only article author, admin, or moderator can update.

    Args:
        article_id: Article ID
        article_data: Article update data

    Returns:
        Updated article
    """
    # Check if article exists
    existing_article = article_service.get_article(article_id, increment_views=False)
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    # Check permission
    is_author = existing_article.author and existing_article.author.id == current_user['id']
    is_admin = check_admin_permission(current_user)

    if not is_author and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此文章"
        )

    # If status is being changed, require admin/moderator
    if article_data.status and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以修改文章状态"
        )

    updated_article = article_service.update_article(article_id, article_data)

    if not updated_article:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文章更新失败"
        )

    logger.info(f"Article updated: {article_id} by user {current_user['id']}")
    return updated_article


@router.delete("/articles/{article_id}", response_model=CMSDeleteResponse)
async def delete_article(
    article_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an article.

    Requires authentication. Only article author, admin, or moderator can delete.

    Args:
        article_id: Article ID

    Returns:
        Delete confirmation
    """
    # Check if article exists
    existing_article = article_service.get_article(article_id, increment_views=False)
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    # Check permission
    is_author = existing_article.author and existing_article.author.id == current_user['id']
    is_admin = check_admin_permission(current_user)

    if not is_author and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此文章"
        )

    success = article_service.delete_article(article_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文章删除失败"
        )

    logger.info(f"Article deleted: {article_id} by user {current_user['id']}")

    return CMSDeleteResponse(
        success=True,
        message="文章删除成功",
        deleted_id=article_id
    )


@router.post("/articles/{article_id}/like", response_model=LikeResponse)
async def like_article(
    article_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Like or unlike an article.

    Requires authentication. Toggles like status.
    Same user liking again will unlike.

    Args:
        article_id: Article ID

    Returns:
        Like count after the operation
    """
    like_count = article_service.like_article(current_user['id'], article_id)

    if like_count is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    return LikeResponse(
        article_id=article_id,
        like_count=like_count
    )


@router.get("/articles/by-slug/{slug}", response_model=ArticleResponse)
async def get_article_by_slug(
    slug: str,
    increment_views: bool = Query(True, description="Increment view count")
):
    """
    Get article by slug.

    Public endpoint. Returns article by its URL-friendly slug.

    Args:
        slug: Article slug
        increment_views: Whether to increment view count

    Returns:
        Article details
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM articles WHERE slug = %s", (slug,))
            row = cur.fetchone()
            if row:
                return article_service.get_article(row['id'], increment_views=increment_views)
    except Exception as e:
        logger.debug(f"Database query skipped: {e}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="文章不存在"
    )


# ============================================================================
# Category Routes
# ============================================================================

@router.get("/categories", response_model=CategoryList)
async def list_categories(
    parent_id: Optional[int] = Query(None, description="Parent category ID filter")
):
    """
    List all categories.

    Public endpoint. Returns hierarchical category structure.

    Args:
        parent_id: Filter by parent category ID (None for root categories)

    Returns:
        Category list
    """
    return category_service.list_categories(parent_id=parent_id)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    """
    Get category by ID.

    Public endpoint.

    Args:
        category_id: Category ID

    Returns:
        Category details
    """
    category = category_service.get_category(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    return category


@router.get("/categories/{category_id}/articles", response_model=CategoryWithArticles)
async def get_category_with_articles(
    category_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get category with its articles.

    Public endpoint. Returns category info and paginated article list.

    Args:
        category_id: Category ID
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Category with articles
    """
    result = category_service.get_category_with_articles(category_id, page, limit)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    return result


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new category.

    Requires admin or moderator role.

    Args:
        category_data: Category creation data

    Returns:
        Created category
    """
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    category = category_service.create_category(category_data)

    logger.info(f"Category created: {category.id} by user {current_user['id']}")
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing category.

    Requires admin or moderator role.

    Args:
        category_id: Category ID
        category_data: Category update data

    Returns:
        Updated category
    """
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    category = category_service.update_category(category_id, category_data)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    logger.info(f"Category updated: {category_id} by user {current_user['id']}")
    return category


@router.delete("/categories/{category_id}", response_model=CMSDeleteResponse)
async def delete_category(
    category_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a category.

    Requires admin or moderator role.
    Articles in this category will have their category_id set to NULL.

    Args:
        category_id: Category ID

    Returns:
        Delete confirmation
    """
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    success = category_service.delete_category(category_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    logger.info(f"Category deleted: {category_id} by user {current_user['id']}")

    return CMSDeleteResponse(
        success=True,
        message="分类删除成功",
        deleted_id=category_id
    )


# ============================================================================
# Statistics Routes (Admin)
# ============================================================================

@router.get("/stats/articles")
async def get_article_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get article statistics.

    Requires admin or moderator role.

    Returns:
        Article statistics
    """
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    try:
        with get_db_cursor() as cur:
            # Total articles
            cur.execute("SELECT COUNT(*) as total FROM articles")
            total = cur.fetchone()["total"]

            # Published articles
            cur.execute("SELECT COUNT(*) as published FROM articles WHERE status = 'published'")
            published = cur.fetchone()["published"]

            # Draft articles
            cur.execute("SELECT COUNT(*) as draft FROM articles WHERE status = 'draft'")
            draft = cur.fetchone()["draft"]

            # Featured articles
            cur.execute("SELECT COUNT(*) as featured FROM articles WHERE featured = TRUE")
            featured = cur.fetchone()["featured"]

            # Total views
            cur.execute("SELECT COALESCE(SUM(view_count), 0) as views FROM articles")
            views = cur.fetchone()["views"]

            # Total likes
            cur.execute("SELECT COALESCE(SUM(like_count), 0) as likes FROM articles")
            likes = cur.fetchone()["likes"]

            # Articles by type
            cur.execute("""
                SELECT type, COUNT(*) as count
                FROM articles
                GROUP BY type
            """)
            by_type = {row["type"]: row["count"] for row in cur.fetchall()}

            return {
                "success": True,
                "data": {
                    "total": total,
                    "published": published,
                    "draft": draft,
                    "featured": featured,
                    "views": views,
                    "likes": likes,
                    "by_type": by_type
                }
            }
    except Exception as e:
        logger.error(f"Stats query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )
