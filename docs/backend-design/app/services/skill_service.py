# ============================================
# SillyMD Backend - Skill Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.skill import Skill, Tag, skill_tags
from app.schemas.skill import SkillCreate, SkillUpdate
from app.models.user import User
import random
import string


class SkillService:
    """Skill service"""

    async def create(
        self,
        db: AsyncSession,
        skill_in: SkillCreate,
        author: User
    ) -> Skill:
        """Create new skill"""
        # Generate unique skill_id
        skill_id = self._generate_skill_id(skill_in.name)

        # Create skill
        skill = Skill(
            skill_id=skill_id,
            name=skill_in.name,
            description=skill_in.description,
            author_id=author.id,
            category=skill_in.category,
            type=skill_in.type,
            version=skill_in.version,
            repo_url=skill_in.repo_url,
            price=skill_in.price,
            dependencies=skill_in.dependencies,
            status="reviewing"  # Go through review process
        )

        db.add(skill)
        await db.commit()
        await db.refresh(skill)

        # Add tags
        if skill_in.tags:
            await self._add_tags(db, skill, skill_in.tags)

        # Trigger AI review
        from app.tasks.review_tasks import trigger_ai_review
        await trigger_ai_review(skill.id)

        return skill

    async def get(
        self,
        db: AsyncSession,
        skill_id: str
    ) -> Optional[Skill]:
        """Get skill by skill_id"""
        result = await db.execute(
            select(Skill).where(Skill.skill_id == skill_id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        type: Optional[str] = None,
        status: str = "approved"
    ) -> tuple[List[Skill], int]:
        """Get multiple skills with filters"""
        # Build query
        query = select(Skill).where(Skill.is_deleted == False)

        if category:
            query = query.where(Skill.category == category)
        if type:
            query = query.where(Skill.type == type)
        if status:
            query = query.where(Skill.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        skills = result.scalars().all()

        return list(skills), total

    async def update(
        self,
        db: AsyncSession,
        skill: Skill,
        skill_in: SkillUpdate
    ) -> Skill:
        """Update skill"""
        update_data = skill_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(skill, field, value)

        await db.commit()
        await db.refresh(skill)

        return skill

    async def delete(
        self,
        db: AsyncSession,
        skill: Skill
    ) -> Skill:
        """Soft delete skill"""
        skill.is_deleted = True
        await db.commit()
        await db.refresh(skill)

        return skill

    def _generate_skill_id(self, name: str) -> str:
        """Generate unique skill_id"""
        # Generate short random string
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

        # Create skill_id from name prefix + random string
        prefix = name.lower().replace(' ', '-')[:20]
        return f"{prefix}-{random_str}"

    async def _add_tags(
        self,
        db: AsyncSession,
        skill: Skill,
        tag_names: List[str]
    ):
        """Add tags to skill"""
        for tag_name in tag_names:
            # Get or create tag
            result = await db.execute(
                select(Tag).where(Tag.name == tag_name)
            )
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()

            # Link skill and tag
            skill.tags.append(tag)

        await db.commit()


# Create service instance
skill_service = SkillService()
