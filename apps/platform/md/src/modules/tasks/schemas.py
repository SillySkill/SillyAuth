"""
Tasks Module Schemas
Pydantic models for task system requests and responses

Provides models for daily tasks, check-ins, achievements, and user progress
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class TaskType(str, Enum):
    """Task type enumeration"""
    DAILY = "daily"              # Daily task
    WEEKLY = "weekly"            # Weekly task
    ACHIEVEMENT = "achievement"  # Achievement
    SPECIAL = "special"          # Special event task


class RewardType(str, Enum):
    """Reward type enumeration"""
    POINTS = "points"           # Points reward
    BADGE = "badge"              # Badge reward
    TITLE = "title"              # Title reward
    ITEM = "item"                # Item reward


class TaskDefinition(BaseModel):
    """Task definition model"""
    id: str = Field(..., description="Task unique identifier")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    type_: TaskType = Field(..., description="Task type")
    reward_type: RewardType = Field(..., description="Reward type")
    reward_amount: int = Field(..., description="Reward amount")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Task completion conditions")
    icon: Optional[str] = Field(None, description="Task icon URL")
    sort_order: int = Field(0, description="Display sort order")
    is_active: bool = Field(True, description="Whether task is active")

    model_config = {"from_attributes": True}


class TaskProgress(BaseModel):
    """Task progress model"""
    task_id: str = Field(..., description="Task ID")
    user_id: int = Field(..., description="User ID")
    progress: int = Field(0, description="Current progress value")
    target: int = Field(..., description="Target progress value")
    completed: bool = Field(False, description="Whether task is completed")
    claimed: bool = Field(False, description="Whether reward is claimed")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    claimed_at: Optional[datetime] = Field(None, description="Reward claim time")

    model_config = {"from_attributes": True}


class Achievement(BaseModel):
    """Achievement definition model"""
    id: str = Field(..., description="Achievement unique identifier")
    name: str = Field(..., description="Achievement name")
    description: str = Field(..., description="Achievement description")
    icon: Optional[str] = Field(None, description="Achievement icon URL")
    condition_type: str = Field(..., description="Condition type (e.g., 'sign_in_days', 'total_points')")
    condition_value: int = Field(..., description="Condition target value")
    reward_type: RewardType = Field(..., description="Reward type")
    reward_amount: int = Field(..., description="Reward amount")
    rarity: str = Field("common", description="Rarity: common, rare, epic, legendary")
    is_active: bool = Field(True, description="Whether achievement is active")

    model_config = {"from_attributes": True}


class UserAchievement(BaseModel):
    """User achievement model"""
    achievement_id: str = Field(..., description="Achievement ID")
    user_id: int = Field(..., description="User ID")
    unlocked_at: Optional[datetime] = Field(None, description="Unlock timestamp")
    claimed: bool = Field(False, description="Whether reward is claimed")
    claimed_at: Optional[datetime] = Field(None, description="Reward claim timestamp")
    achievement: Optional[Achievement] = Field(None, description="Achievement details")

    model_config = {"from_attributes": True}


class DailyTask(BaseModel):
    """Daily task with completion status"""
    task_id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    type_: TaskType = Field(..., description="Task type")
    icon: Optional[str] = Field(None, description="Task icon URL")
    reward_type: RewardType = Field(..., description="Reward type")
    reward_amount: int = Field(..., description="Reward amount")
    progress: int = Field(0, description="Current progress")
    target: int = Field(..., description="Target progress")
    completed: bool = Field(False, description="Whether task is completed")
    claimed: bool = Field(False, description="Whether reward is claimed")
    available: bool = Field(True, description="Whether task is available today")

    model_config = {"from_attributes": True}


class CheckInRecord(BaseModel):
    """Check-in record model"""
    id: int = Field(..., description="Record ID")
    user_id: int = Field(..., description="User ID")
    check_in_date: date
    points_earned: int = Field(..., description="Points earned")
    streak_days: int = Field(..., description="Current streak days")
    bonus_points: int = Field(0, description="Bonus points from streak")
    created_at: datetime = Field(..., description="Record creation time")

    model_config = {"from_attributes": True}


class CheckInStatus(BaseModel):
    """Check-in status response"""
    user_id: int = Field(..., description="User ID")
    checked_in_today: bool = Field(..., description="Whether checked in today")
    current_streak: int = Field(0, description="Current streak days")
    longest_streak: int = Field(0, description="Longest streak days")
    total_check_ins: int = Field(0, description="Total check-in count")
    next_bonus_in: Optional[int] = Field(None, description="Days until next bonus")
    base_points: int = Field(..., description="Base points per check-in")
    streak_bonus: int = Field(..., description="Streak bonus per day")

    model_config = {"from_attributes": True}


class ClaimResponse(BaseModel):
    """Generic claim response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    reward_type: Optional[RewardType] = Field(None, description="Reward type")
    reward_amount: Optional[int] = Field(None, description="Reward amount")
    total_points: Optional[int] = Field(None, description="Current total points")

    model_config = {"from_attributes": True}


class TaskStats(BaseModel):
    """Task statistics response"""
    user_id: int = Field(..., description="User ID")
    total_tasks_completed: int = Field(0, description="Total tasks completed")
    daily_tasks_completed: int = Field(0, description="Daily tasks completed")
    weekly_tasks_completed: int = Field(0, description="Weekly tasks completed")
    achievements_unlocked: int = Field(0, description="Achievements unlocked")
    achievements_total: int = Field(0, description="Total achievements")
    total_points_earned: int = Field(0, description="Total points earned from tasks")

    model_config = {"from_attributes": True}


class DailyTaskListResponse(BaseModel):
    """Daily task list response"""
    date: date
    tasks: List["DailyTask"] = []
    total_count: int = Field(..., description="Total task count")
    completed_count: int = Field(..., description="Completed task count")
    claimed_count: int = Field(..., description="Claimed task count")

    model_config = {"from_attributes": True}


class AchievementListResponse(BaseModel):
    """Achievement list response"""
    achievements: List["UserAchievement"] = []
    unlocked_count: int = Field(..., description="Unlocked count")
    total_count: int = Field(..., description="Total count")
    claimed_count: int = Field(..., description="Claimed count")

    model_config = {"from_attributes": True}


# ============================================================================
# Sign-In Calendar Schemas
# ============================================================================

class SignInCalendarDay(BaseModel):
    """Single day entry in the sign-in calendar"""
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    consecutive_days: int = Field(0, description="Consecutive check-in days at this date")
    points_earned: int = Field(0, description="Points earned for this day's check-in")
    bonus_points: int = Field(0, description="Bonus points from streak")

    model_config = {"from_attributes": True}


class SignInCalendarResponse(BaseModel):
    """Monthly sign-in calendar response"""
    year: int = Field(..., description="Calendar year")
    month: int = Field(..., description="Calendar month (1-12)")
    records: List[SignInCalendarDay] = Field(default_factory=list, description="Check-in records for this month")
    checked_days: int = Field(0, description="Number of days checked in this month")
    total_days: int = Field(0, description="Total days checked in all time")

    model_config = {"from_attributes": True}
