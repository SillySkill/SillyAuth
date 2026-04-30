"""
Tasks Module Routes
FastAPI routes for task system endpoints

Provides daily tasks, check-ins, achievements, and task statistics endpoints
"""

import os
from typing import Optional, List
from datetime import date

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .schemas import (
    DailyTask,
    DailyTaskListResponse,
    CheckInRecord,
    CheckInStatus,
    ClaimResponse,
    UserAchievement,
    AchievementListResponse,
    TaskStats,
    TaskType,
    RewardType,
    SignInCalendarDay,
    SignInCalendarResponse,
)
from .services import (
    TaskService,
    CheckInService,
    AchievementService,
    TaskStatsService,
    DEFAULT_SIGN_IN_CONFIG,
    get_db_config,
    get_db,
)


# Create router
router = APIRouter(prefix="/api/v1/tasks", tags=["任务系统"])


# ============================================================================
# Helper Functions
# ============================================================================

def get_sign_in_config() -> dict:
    """Get check-in configuration"""
    return DEFAULT_SIGN_IN_CONFIG


# ============================================================================
# Daily Tasks Routes
# ============================================================================

@router.get("/daily", response_model=DailyTaskListResponse)
async def get_daily_tasks(
    user_id: int = Query(..., description="User ID")
):
    """
    Get daily tasks for the current user

    Returns all active daily tasks with their current progress and completion status.
    Tasks reset daily at midnight (UTC).
    """
    try:
        tasks = TaskService.get_daily_tasks(user_id)
        daily_tasks = [DailyTask(**task) for task in tasks]

        total_count = len(daily_tasks)
        completed_count = sum(1 for t in daily_tasks if t.completed)
        claimed_count = sum(1 for t in daily_tasks if t.claimed)

        return DailyTaskListResponse(
            date=date.today(),
            tasks=daily_tasks,
            total_count=total_count,
            completed_count=completed_count,
            claimed_count=claimed_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/claim", response_model=ClaimResponse)
async def claim_task_reward(
    task_id: str,
    user_id: int = Query(..., description="User ID")
):
    """
    Claim reward for a completed task

    - task_id: Task ID to claim
    - user_id: User ID

    The task must be completed before claiming the reward.
    """
    try:
        result = TaskService.claim_task_reward(user_id, task_id)
        return ClaimResponse(
            success=result['success'],
            message=result['message'],
            reward_type=RewardType(result['reward_type']),
            reward_amount=result['reward_amount'],
            total_points=result['total_points']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/progress")
async def update_task_progress(
    task_id: str,
    user_id: int = Query(..., description="User ID"),
    progress_delta: int = Query(1, ge=1, description="Progress to add")
):
    """
    Update task progress

    - task_id: Task ID to update
    - user_id: User ID
    - progress_delta: Progress amount to add (default: 1)

    Returns whether the task was completed after the update.
    """
    try:
        completed = TaskService.update_progress(user_id, task_id, progress_delta)
        return {
            "success": True,
            "task_id": task_id,
            "progress_updated": progress_delta,
            "completed": completed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Check-In Routes
# ============================================================================

@router.get("/check-in", response_model=CheckInStatus)
async def get_check_in_status(
    user_id: int = Query(..., description="User ID")
):
    """
    Get check-in status for the current user

    Returns:
    - Whether checked in today
    - Current streak days
    - Longest streak days
    - Total check-in count
    - Next bonus information
    """
    try:
        config = get_sign_in_config()
        status = CheckInService.get_check_in_status(user_id, config)
        return CheckInStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-in", response_model=CheckInRecord)
async def perform_check_in(
    user_id: int = Query(..., description="User ID")
):
    """
    Perform daily check-in

    Awards points based on:
    - Base points (default: 10)
    - Streak bonus (default: 2 per day, up to max streak)

    Resets streak if a day is missed.
    """
    try:
        config = get_sign_in_config()
        result = CheckInService.check_in(user_id, config)
        return CheckInRecord(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-in/history", response_model=List[CheckInRecord])
async def get_check_in_history(
    user_id: int = Query(..., description="User ID"),
    limit: int = Query(30, ge=1, le=100, description="Number of records to return")
):
    """
    Get check-in history

    - user_id: User ID
    - limit: Maximum number of records (default: 30, max: 100)
    """
    try:
        from psycopg2.extras import RealDictCursor

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM check_in_records
                    WHERE user_id = %s
                    ORDER BY check_in_date DESC
                    LIMIT %s
                """, (user_id, limit))

                records = [dict(row) for row in cur.fetchall()]
                return [CheckInRecord(**record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-in/calendar", response_model=SignInCalendarResponse)
async def get_check_in_calendar(
    user_id: int = Query(..., description="User ID"),
    year: Optional[int] = Query(None, description="Calendar year (defaults to current year)"),
    month: Optional[int] = Query(None, description="Calendar month 1-12 (defaults to current month)"),
):
    """
    Get monthly sign-in calendar view

    Returns all check-in records for the specified month, showing which days
    the user checked in, their streak at each day, and points earned.

    - user_id: User ID
    - year: Calendar year (defaults to current year)
    - month: Calendar month 1-12 (defaults to current month)
    """
    from datetime import datetime as dt

    if year is None:
        year = dt.now().year
    if month is None:
        month = dt.now().month

    try:
        calendar_data = CheckInService.get_calendar(user_id, year, month)
        return SignInCalendarResponse(**calendar_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Achievement Routes
# ============================================================================

@router.get("/achievements", response_model=AchievementListResponse)
async def get_achievements(
    user_id: int = Query(..., description="User ID")
):
    """
    Get all achievements with unlock status

    Returns all achievements including:
    - Unlocked achievements with unlock timestamp
    - Locked achievements
    - Claimed status for each
    """
    try:
        achievements = AchievementService.get_achievements(user_id)
        user_achievements = [UserAchievement(**ach) for ach in achievements]

        unlocked_count = sum(1 for a in user_achievements if a.unlocked_at is not None)
        total_count = len(user_achievements)
        claimed_count = sum(1 for a in user_achievements if a.claimed)

        return AchievementListResponse(
            achievements=user_achievements,
            unlocked_count=unlocked_count,
            total_count=total_count,
            claimed_count=claimed_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/achievements/{achievement_id}/claim", response_model=ClaimResponse)
async def claim_achievement_reward(
    achievement_id: str,
    user_id: int = Query(..., description="User ID")
):
    """
    Claim achievement reward

    - achievement_id: Achievement ID to claim
    - user_id: User ID

    The achievement must be unlocked before claiming the reward.
    """
    try:
        result = AchievementService.claim_achievement_reward(user_id, achievement_id)
        return ClaimResponse(
            success=result['success'],
            message=result['message'],
            reward_type=RewardType(result['reward_type']),
            reward_amount=result['reward_amount'],
            total_points=result['total_points']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/achievements/{achievement_id}/check")
async def check_achievement_unlock(
    achievement_id: str,
    user_id: int = Query(..., description="User ID")
):
    """
    Manually check if an achievement should be unlocked

    - achievement_id: Achievement ID to check
    - user_id: User ID

    Returns whether the achievement was unlocked.
    """
    try:
        unlocked = AchievementService.check_achievement_unlock(user_id, achievement_id)
        return {
            "achievement_id": achievement_id,
            "unlocked": unlocked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Statistics Routes
# ============================================================================

@router.get("/stats", response_model=TaskStats)
async def get_task_stats(
    user_id: int = Query(..., description="User ID")
):
    """
    Get comprehensive task statistics for the current user

    Returns:
    - Total tasks completed
    - Daily tasks completed
    - Weekly tasks completed
    - Achievements unlocked / total
    - Total points earned from tasks
    """
    try:
        stats = TaskStatsService.get_user_stats(user_id)
        return TaskStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streak")
async def get_streak(
    user_id: int = Query(..., description="User ID")
):
    """
    Get current check-in streak for the user

    Returns the number of consecutive days the user has checked in.
    """
    try:
        streak = CheckInService.get_streak(user_id)
        return {
            "user_id": user_id,
            "current_streak": streak
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Task Definitions Routes (Admin)
# ============================================================================

@router.get("/definitions")
async def get_task_definitions(
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    is_active: bool = Query(True, description="Filter by active status")
):
    """
    Get all task definitions

    Admin endpoint to view all task definitions.
    """
    try:
        from psycopg2.extras import RealDictCursor

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM task_definitions WHERE 1=1"
                params = []

                if task_type:
                    query += " AND type = %s"
                    params.append(task_type)

                if is_active is not None:
                    query += " AND is_active = %s"
                    params.append(is_active)

                query += " ORDER BY sort_order ASC, type ASC"

                cur.execute(query, params)
                tasks = [dict(row) for row in cur.fetchall()]
                return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievement-definitions")
async def get_achievement_definitions(
    is_active: bool = Query(True, description="Filter by active status")
):
    """
    Get all achievement definitions

    Admin endpoint to view all achievement definitions.
    """
    try:
        from psycopg2.extras import RealDictCursor

        with get_db(get_db_config()) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM achievement_definitions WHERE 1=1"
                params = []

                if is_active is not None:
                    query += " AND is_active = %s"
                    params.append(is_active)

                query += " ORDER BY condition_value ASC"

                cur.execute(query, params)
                achievements = [dict(row) for row in cur.fetchall()]
                return {"achievements": achievements, "count": len(achievements)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
