"""
Skills Module Schemas
Pydantic models for Skills management requests and responses

Provides skill creation, update, listing, and response schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# Enums
# ============================================

class SkillCategory(str, Enum):
    """Skill category enumeration"""
    TECH = "tech"
    PRODUCT = "product"
    DESIGN = "design"
    MARKETING = "marketing"
    OPS = "ops"


class SkillType(str, Enum):
    """Skill type enumeration"""
    FREE = "free"
    COMMERCIAL = "commercial"


class SkillStatus(str, Enum):
    """Skill status enumeration"""
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class LicenseType(str, Enum):
    """License type enumeration"""
    PERSONAL = "personal"
    TEAM = "team"
    ENTERPRISE = "enterprise"


# ============================================
# Base Schemas
# ============================================

class SkillBase(BaseModel):
    """Base skill schema with common fields"""
    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Skill name (3-200 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Skill description (max 500 characters)"
    )
    category: SkillCategory = Field(
        ...,
        description="Skill category"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Skill tags"
    )

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags"""
        if len(v) > 10:
            raise ValueError('最多只能添加 10 个标签')
        return [tag.strip().lower() for tag in v if tag.strip()]


class SkillCreate(SkillBase):
    """Skill creation schema"""
    code_content: str = Field(
        ...,
        description="Skill code/content in Markdown format"
    )
    skill_id: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Custom skill identifier (optional)"
    )
    type: SkillType = Field(
        SkillType.FREE,
        description="Skill type: free or commercial"
    )
    version: str = Field(
        "1.0.0",
        description="Semantic version"
    )
    price: Optional[int] = Field(
        0,
        ge=0,
        description="Price in points (for commercial skills)"
    )
    license_types: Optional[List[LicenseType]] = Field(
        None,
        description="Available license types"
    )

    @field_validator('skill_id')
    @classmethod
    def validate_skill_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate skill_id format"""
        if v is None:
            return v
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Skill ID 只能包含字母、数字、连字符和下划线')
        return v.lower()


class SkillUpdate(BaseModel):
    """Skill update schema for partial updates"""
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Skill name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Skill description"
    )
    category: Optional[SkillCategory] = Field(
        None,
        description="Skill category"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Skill tags"
    )
    code_content: Optional[str] = Field(
        None,
        description="Skill code/content"
    )
    type: Optional[SkillType] = Field(
        None,
        description="Skill type"
    )
    price: Optional[int] = Field(
        None,
        ge=0,
        description="Price in points"
    )
    license_types: Optional[List[LicenseType]] = Field(
        None,
        description="Available license types"
    )
    repo_url: Optional[str] = Field(
        None,
        description="Repository URL"
    )

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and normalize tags"""
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError('最多只能添加 10 个标签')
        return [tag.strip().lower() for tag in v if tag.strip()]


# ============================================
# Response Schemas
# ============================================

class SkillStats(BaseModel):
    """Skill statistics schema"""
    view_count: int = Field(0, description="View count")
    download_count: int = Field(0, description="Download count")
    favorite_count: int = Field(0, description="Favorite count")
    rating_avg: float = Field(0.0, description="Average rating")
    rating_count: int = Field(0, description="Rating count")

    class Config:
        from_attributes = True


class AuthorInfo(BaseModel):
    """Author information schema"""
    id: int = Field(..., description="Author ID")
    username: str = Field(..., description="Username")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")

    class Config:
        from_attributes = True


class SkillResponse(BaseModel):
    """Full skill response schema"""
    id: int = Field(..., description="Skill internal ID")
    skill_id: str = Field(..., description="Skill identifier")
    name: str = Field(..., description="Skill name")
    description: Optional[str] = Field(None, description="Skill description")
    author: AuthorInfo = Field(..., description="Author information")
    category: SkillCategory = Field(..., description="Category")
    type: SkillType = Field(..., description="Type")
    version: str = Field(..., description="Version")
    status: SkillStatus = Field(..., description="Status")
    tags: List[str] = Field(default_factory=list, description="Tags")
    stats: SkillStats = Field(default_factory=SkillStats, description="Statistics")
    price: int = Field(0, description="Price in points")
    license_types: Optional[List[str]] = Field(None, description="License types")
    repo_url: Optional[str] = Field(None, description="Repository URL")
    is_featured: bool = Field(False, description="Is featured")
    published_at: Optional[datetime] = Field(None, description="Published at")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    class Config:
        from_attributes = True


class SkillListItem(BaseModel):
    """Skill list item schema (lighter response)"""
    id: int = Field(..., description="Skill ID")
    skill_id: str = Field(..., description="Skill identifier")
    name: str = Field(..., description="Skill name")
    description: Optional[str] = Field(None, description="Description")
    author: AuthorInfo = Field(..., description="Author")
    category: SkillCategory = Field(..., description="Category")
    type: SkillType = Field(..., description="Type")
    version: str = Field(..., description="Version")
    tags: List[str] = Field(default_factory=list, description="Tags")
    stats: SkillStats = Field(default_factory=SkillStats, description="Stats")
    price: int = Field(0, description="Price")
    is_featured: bool = Field(False, description="Is featured")
    published_at: Optional[datetime] = Field(None, description="Published at")
    created_at: datetime = Field(..., description="Created at")

    class Config:
        from_attributes = True


class SkillListResponse(BaseModel):
    """Paginated skill list response"""
    items: List[SkillListItem] = Field(..., description="Skill items")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")

    class Config:
        from_attributes = True


class CategoryInfo(BaseModel):
    """Category information schema"""
    key: str = Field(..., description="Category key")
    name: str = Field(..., description="Category name (zh)")
    name_en: str = Field(..., description="Category name (en)")
    description: Optional[str] = Field(None, description="Description")
    icon: Optional[str] = Field(None, description="Icon")
    skill_count: int = Field(0, description="Skill count")

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """Category response with skill count"""
    categories: List[CategoryInfo] = Field(..., description="Categories")

    class Config:
        from_attributes = True


class SkillVersionInfo(BaseModel):
    """Skill version information"""
    version: str = Field(..., description="Version number")
    content: str = Field(..., description="Content")
    content_hash: str = Field(..., description="Content hash")
    commit_message: Optional[str] = Field(None, description="Commit message")
    created_at: datetime = Field(..., description="Created at")

    class Config:
        from_attributes = True


class PublishResponse(BaseModel):
    """Publish skill response"""
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Message")
    skill_id: Optional[int] = Field(None, description="Skill ID")
    status: Optional[SkillStatus] = Field(None, description="New status")

    class Config:
        from_attributes = True


class SkillStatsResponse(BaseModel):
    """Skill statistics response"""
    skill_id: int = Field(..., description="Skill ID")
    view_count: int = Field(..., description="View count")
    download_count: int = Field(..., description="Download count")
    favorite_count: int = Field(..., description="Favorite count")
    rating_avg: float = Field(..., description="Average rating")
    rating_count: int = Field(..., description="Rating count")
    total_comments: int = Field(0, description="Total comments")

    class Config:
        from_attributes = True


# ============================================
# API Response Wrappers
# ============================================

class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(True, description="Success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
