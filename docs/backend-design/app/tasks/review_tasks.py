# ============================================
# SillyMD Backend - Review Tasks
# ============================================

from app.tasks.celery_app import celery_app
from app.services.ai_review_service import ai_review_service
from app.db.session import async_session
from sqlalchemy import select
from app.models.review import Review
from app.models.skill import Skill
import asyncio


@celery_app.task
def trigger_ai_review(skill_id: int):
    """Trigger AI review for a skill"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_process_review(skill_id))
        return result
    finally:
        loop.close()


async def _process_review(skill_id: int) -> dict:
    """Process AI review"""
    async with async_session() as db:
        # Get skill
        result = await db.execute(select(Skill).where(Skill.id == skill_id))
        skill = result.scalar_one_or_none()

        if not skill:
            return {"error": "Skill not found"}

        # Prepare data
        skill_data = {
            "name": skill.name,
            "description": skill.description,
            "category": skill.category,
            "type": skill.type
        }

        # Run AI review
        review_result = await ai_review_service.review_skill(skill_data)

        # Create review record
        review = Review(
            skill_id=skill.id,
            reviewer_id=1,  # System user
            stage="L1",
            result="approved" if review_result["approved"] else "rejected",
            scores=review_result["scores"],
            ai_model=settings.AI_REVIEW_MODEL,
            ai_confidence=review_result["confidence"]
        )

        db.add(review)

        # Update skill status based on review
        if review_result["approved"]:
            skill.status = "approved"
            skill.published_at = func.now()
        else:
            skill.status = "reviewing"

        await db.commit()

        return {
            "skill_id": skill_id,
            "approved": review_result["approved"],
            "confidence": review_result["confidence"]
        }


from sqlalchemy import func
from app.core.config import settings


@celery_app.task
def run_crawler_task():
    """Run crawler task"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_run_crawler())
        return result
    finally:
        loop.close()


async def _run_crawler():
    """Run crawler"""
    from app.services.crawler_service import crawler_service

    async with async_session() as db:
        await crawler_service.run_crawler(db)

    return {"status": "completed"}


@celery_app.task
def publish_skill_notification(skill_id: int, skill_name: str):
    """Send notification when skill is published"""
    # TODO: Implement notification sending
    return {"status": "notification_sent"}
