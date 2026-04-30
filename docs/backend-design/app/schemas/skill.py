# ============================================
# SillyMD Backend - Skill Schemas
# ============================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.models.skill import SkillCategory, SkillType, SkillStatus


class SkillBase(BaseModel):
    """Skill base schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: SkillCategory
    type: SkillType = SkillType.FREE
    version: str = "1.0.0"
    repo_url: Optional[str] = None
    price: int = 0


class SkillCreate(SkillBase):
    """Skill create schema"""
    tags: Optional[List[str]] = []
    dependencies: Optional[Dict] = None


class SkillUpdate(BaseModel):
    """Skill update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    version: Optional[str] = None
    repo_url: Optional[str] = None
    price: Optional[int] = None


class SkillInDB(SkillBase):
    """Skill in database schema"""
    id: int
    skill_id: str
    author_id: int
    status: SkillStatus
    is_featured: bool
    published_at: Optional[datetime]
    view_count: int
    download_count: int
    favorite_count: int
    rating_avg: float
    rating_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillResponse(SkillInDB):
    """Skill response schema"""
    author: Optional[Dict] = None
    tags: Optional[List[str]] = None


class SkillListResponse(BaseModel):
    """Skill list response schema"""
    items: List[SkillResponse]
    total: int
    page: int
    page_size: int
