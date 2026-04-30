# ============================================
# SillyMD Backend - Skills API Router
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_db, get_current_user, get_current_vendor
from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
    SkillListResponse
)
from app.services.skill_service import skill_service
from app.models.user import User
from app.models.skill import Skill

router = APIRouter()


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_in: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_vendor)
):
    """
    Create new skill (requires vendor privileges)
    """
    skill = await skill_service.create(db, skill_in, current_user)
    return skill


@router.get("/", response_model=SkillListResponse)
async def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    type: Optional[str] = None
):
    """
    List skills with pagination and filters
    """
    # Note: In real app, db would come from Depends(get_db)
    # This is simplified for demo
    return SkillListResponse(
        items=[],
        total=0,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str):
    """
    Get skill by ID
    """
    # Note: Implementation simplified for demo
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    skill_in: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_vendor)
):
    """
    Update skill (author or admin only)
    """
    # Note: Implementation simplified for demo
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_vendor)
):
    """
    Delete skill (author or admin only)
    """
    # Note: Implementation simplified for demo
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )
