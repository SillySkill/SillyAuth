"""
CMS Module Schemas
Pydantic models for content management requests and responses

Provides article, tutorial, guide, and category management schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
import re


class ArticleType(str, Enum):
    """Article type enumeration."""
    TUTORIAL = "tutorial"
    ARTICLE = "article"
    GUIDE = "guide"


class ArticleStatus(str, Enum):
    """Article status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# ============================================================================
# Article Schemas
# ============================================================================

class ArticleCreate(BaseModel):
    """Schema for creating a new article."""
    title: str = Field(..., min_length=1, max_length=255, description="Article title")
    content: str = Field(..., min_length=1, description="Article content (markdown or html)")
    type: ArticleType = Field(..., description="Article type: tutorial, article, or guide")
    category_id: Optional[int] = Field(None, description="Category ID")
    tags: Optional[List[str]] = Field(default_factory=list, description="Article tags")
    featured: bool = Field(False, description="Featured article flag")
    status: ArticleStatus = Field(ArticleStatus.DRAFT, description="Article status")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    excerpt: Optional[str] = Field(None, max_length=500, description="Article excerpt")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags are not empty strings."""
        if v:
            return [tag.strip() for tag in v if tag.strip()]
        return []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Article title")
    content: Optional[str] = Field(None, min_length=1, description="Article content")
    type: Optional[ArticleType] = Field(None, description="Article type")
    category_id: Optional[int] = Field(None, description="Category ID")
    tags: Optional[List[str]] = Field(None, description="Article tags")
    featured: Optional[bool] = Field(None, description="Featured article flag")
    status: Optional[ArticleStatus] = Field(None, description="Article status")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    excerpt: Optional[str] = Field(None, max_length=500, description="Article excerpt")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags are not empty strings."""
        if v is not None:
            return [tag.strip() for tag in v if tag.strip()]
        return v


class AuthorInfo(BaseModel):
    """Author information schema."""
    id: int = Field(..., description="Author ID")
    username: str = Field(..., description="Author username")
    avatar_url: Optional[str] = Field(None, description="Author avatar URL")
    display_name: Optional[str] = Field(None, description="Author display name")


class ArticleResponse(BaseModel):
    """Schema for article response."""
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    type: ArticleType = Field(..., description="Article type")
    slug: str = Field(..., description="URL-friendly slug")
    excerpt: Optional[str] = Field(None, description="Article excerpt")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    featured: bool = Field(False, description="Featured flag")
    status: ArticleStatus = Field(..., description="Article status")
    view_count: int = Field(0, description="View count")
    like_count: int = Field(0, description="Like count")
    category_id: Optional[int] = Field(None, description="Category ID")
    category_name: Optional[str] = Field(None, description="Category name")
    author: Optional[AuthorInfo] = Field(None, description="Author information")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    published_at: Optional[datetime] = Field(None, description="Published timestamp")

    class Config:
        from_attributes = True


class ArticleListItem(BaseModel):
    """Schema for article list item (simplified)."""
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    type: ArticleType = Field(..., description="Article type")
    slug: str = Field(..., description="URL-friendly slug")
    excerpt: Optional[str] = Field(None, description="Article excerpt")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    featured: bool = Field(False, description="Featured flag")
    view_count: int = Field(0, description="View count")
    like_count: int = Field(0, description="Like count")
    category_id: Optional[int] = Field(None, description="Category ID")
    category_name: Optional[str] = Field(None, description="Category name")
    author_username: Optional[str] = Field(None, description="Author username")
    author_avatar: Optional[str] = Field(None, description="Author avatar URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ArticleList(BaseModel):
    """Paginated article list response."""
    items: List[ArticleListItem] = Field(..., description="Article items")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")


class ArticleSearchResult(BaseModel):
    """Article search result."""
    items: List[ArticleListItem] = Field(..., description="Search results")
    total: int = Field(..., description="Total matches")
    query: str = Field(..., description="Search query")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")


class FeaturedArticlesResponse(BaseModel):
    """Featured articles response."""
    items: List[ArticleListItem] = Field(..., description="Featured articles")
    total: int = Field(..., description="Total featured articles")


class LikeResponse(BaseModel):
    """Article like response."""
    article_id: int = Field(..., description="Article ID")
    like_count: int = Field(..., description="New like count")


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryCreate(BaseModel):
    """Schema for creating a new category."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    icon: Optional[str] = Field(None, max_length=50, description="Category icon")
    color: Optional[str] = Field(None, max_length=7, description="Category color (hex)")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="URL-friendly slug")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    icon: Optional[str] = Field(None, max_length=50, description="Category icon")
    color: Optional[str] = Field(None, max_length=7, description="Category color (hex)")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Validate slug format."""
        if v is not None and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    icon: Optional[str] = Field(None, description="Category icon")
    color: Optional[str] = Field(None, description="Category color")
    article_count: int = Field(0, description="Number of articles in category")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class CategoryList(BaseModel):
    """Category list response."""
    items: List[CategoryResponse] = Field(..., description="Category items")
    total: int = Field(..., description="Total count")


class CategoryWithArticles(BaseModel):
    """Category with articles."""
    category: CategoryResponse = Field(..., description="Category info")
    articles: ArticleList = Field(..., description="Articles in category")


# ============================================================================
# Generic Responses
# ============================================================================

class CMSResponse(BaseModel):
    """Generic CMS response."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")


class CMSDeleteResponse(BaseModel):
    """CMS delete response."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    deleted_id: int = Field(..., description="Deleted item ID")
