"""
Arena Module - Schemas

Pydantic schemas for arena PK API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoomStatus(str, Enum):
    """Room status enumeration"""
    WAITING = "waiting"  # Waiting for participants
    READY = "ready"  # All participants ready, can start battle
    BATTLING = "battling"  # Battle in progress
    FINISHED = "finished"  # Battle finished


class BattleStatus(str, Enum):
    """Battle status enumeration"""
    PENDING = "pending"  # Battle created, waiting to start
    IN_PROGRESS = "in_progress"  # Battle ongoing
    FINISHED = "finished"  # Battle completed


# ============== Room Schemas ==============

class RoomCreate(BaseModel):
    """Schema for creating a new room"""
    name: str = Field(..., min_length=1, max_length=50, description="Room name")
    description: Optional[str] = Field(None, max_length=200, description="Room description")
    max_participants: int = Field(4, ge=2, le=8, description="Maximum number of participants")
    is_private: bool = Field(False, description="Whether room requires password")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "高手对战房",
                "description": "高手之间的巅峰对决",
                "max_participants": 4,
                "is_private": False
            }
        }


class ParticipantInfo(BaseModel):
    """Schema for participant information"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    elo_rating: int = Field(..., description="Current ELO rating")
    is_ready: bool = Field(False, description="Ready status")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "username": "虾王",
                "elo_rating": 1500,
                "is_ready": True
            }
        }


class RoomResponse(BaseModel):
    """Schema for room response"""
    id: str = Field(..., description="Room ID")
    name: str = Field(..., description="Room name")
    description: Optional[str] = Field(None, description="Room description")
    status: RoomStatus = Field(..., description="Room status")
    participants: List[ParticipantInfo] = Field(default_factory=list, description="List of participants")
    max_participants: int = Field(..., description="Maximum participants allowed")
    is_private: bool = Field(False, description="Whether room is private")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "room_abc123",
                "name": "高手对战房",
                "description": "高手之间的巅峰对决",
                "status": "waiting",
                "participants": [],
                "max_participants": 4,
                "is_private": False,
                "created_by": "user123",
                "created_at": "2026-03-26T10:00:00Z"
            }
        }


class RoomListResponse(BaseModel):
    """Schema for paginated room list"""
    rooms: List[RoomResponse] = Field(..., description="List of rooms")
    total: int = Field(..., description="Total number of rooms")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")


# ============== Battle Schemas ==============

class BattleStart(BaseModel):
    """Schema for starting a battle"""
    room_id: str = Field(..., description="Room ID to start battle in")
    participant_ids: List[str] = Field(..., min_length=2, description="Participant IDs for the battle")

    class Config:
        json_schema_extra = {
            "example": {
                "room_id": "room_abc123",
                "participant_ids": ["user123", "user456"]
            }
        }


class BattleQuestion(BaseModel):
    """Schema for a battle question"""
    question_id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    options: Optional[List[str]] = Field(None, description="Answer options if applicable")
    time_limit: int = Field(30, description="Time limit in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "question": "1 + 1 = ?",
                "options": ["1", "2", "3", "4"],
                "time_limit": 30
            }
        }


class BattleResponse(BaseModel):
    """Schema for battle response"""
    battle_id: str = Field(..., description="Battle ID")
    room_id: str = Field(..., description="Room ID")
    status: BattleStatus = Field(..., description="Battle status")
    participants: List[ParticipantInfo] = Field(..., description="Battle participants")
    current_question: Optional[BattleQuestion] = Field(None, description="Current question")
    question_index: int = Field(0, description="Current question index")
    total_questions: int = Field(..., description="Total questions in battle")
    started_at: Optional[datetime] = Field(None, description="Battle start time")
    ends_at: Optional[datetime] = Field(None, description="Expected end time")

    class Config:
        json_schema_extra = {
            "example": {
                "battle_id": "battle_xyz789",
                "room_id": "room_abc123",
                "status": "in_progress",
                "participants": [],
                "current_question": None,
                "question_index": 0,
                "total_questions": 10,
                "started_at": "2026-03-26T10:00:00Z",
                "ends_at": "2026-03-26T10:05:00Z"
            }
        }


class AnswerSubmit(BaseModel):
    """Schema for submitting an answer"""
    answer: str = Field(..., description="Answer content")
    time_taken: float = Field(..., ge=0, description="Time taken to answer in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "B",
                "time_taken": 5.5
            }
        }


class AnswerResponse(BaseModel):
    """Schema for answer submission response"""
    correct: bool = Field(..., description="Whether answer is correct")
    correct_answer: Optional[str] = Field(None, description="Correct answer if wrong")
    points_earned: int = Field(..., description="Points earned for this answer")
    total_points: int = Field(..., description="Total points so far")

    class Config:
        json_schema_extra = {
            "example": {
                "correct": True,
                "correct_answer": None,
                "points_earned": 100,
                "total_points": 500
            }
        }


# ============== Battle Result Schemas ==============

class BattleReward(BaseModel):
    """Schema for battle rewards"""
    experience: int = Field(0, description="Experience points earned")
    coins: int = Field(0, description="Coins earned")
    rating_change: int = Field(0, description="ELO rating change")

    class Config:
        json_schema_extra = {
            "example": {
                "experience": 100,
                "coins": 50,
                "rating_change": 15
            }
        }


class BattleResultResponse(BaseModel):
    """Schema for battle result"""
    battle_id: str = Field(..., description="Battle ID")
    winner_id: str = Field(..., description="Winner user ID")
    winner_name: str = Field(..., description="Winner username")
    loser_id: str = Field(..., description="Loser user ID")
    loser_name: str = Field(..., description="Loser username")
    score: dict = Field(..., description="Final scores by user ID")
    rewards: dict = Field(..., description="Rewards by user ID")
    elo_changes: dict = Field(..., description="ELO rating changes by user ID")
    finished_at: datetime = Field(..., description="Battle finish time")

    class Config:
        json_schema_extra = {
            "example": {
                "battle_id": "battle_xyz789",
                "winner_id": "user123",
                "winner_name": "虾王",
                "loser_id": "user456",
                "loser_name": "小虾",
                "score": {
                    "user123": 800,
                    "user456": 600
                },
                "rewards": {
                    "user123": {"experience": 100, "coins": 50},
                    "user456": {"experience": 50, "coins": 25}
                },
                "elo_changes": {
                    "user123": 15,
                    "user456": -15
                },
                "finished_at": "2026-03-26T10:05:00Z"
            }
        }


# ============== Ranking Schemas ==============

class ArenaRanking(BaseModel):
    """Schema for arena ranking entry"""
    rank: int = Field(..., description="Rank position")
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    elo_rating: int = Field(..., description="Current ELO rating")
    wins: int = Field(..., description="Total wins")
    losses: int = Field(..., description="Total losses")
    win_rate: float = Field(..., description="Win rate percentage")
    streak: int = Field(0, description="Current win/loss streak")

    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "user_id": "user123",
                "username": "虾王",
                "elo_rating": 1800,
                "wins": 50,
                "losses": 10,
                "win_rate": 83.33,
                "streak": 5
            }
        }


class RankingListResponse(BaseModel):
    """Schema for paginated ranking list"""
    rankings: List[ArenaRanking] = Field(..., description="List of rankings")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")


# ============== Battle History Schemas ==============

class BattleHistoryEntry(BaseModel):
    """Schema for a battle history entry"""
    battle_id: str = Field(..., description="Battle ID")
    room_name: str = Field(..., description="Room name")
    opponent_id: str = Field(..., description="Opponent user ID")
    opponent_name: str = Field(..., description="Opponent username")
    result: str = Field(..., description="WIN, LOSE, or DRAW")
    my_score: int = Field(..., description="Your final score")
    opponent_score: int = Field(..., description="Opponent final score")
    elo_change: int = Field(..., description="ELO rating change")
    new_elo: int = Field(..., description="New ELO rating")
    played_at: datetime = Field(..., description="Battle timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "battle_id": "battle_xyz789",
                "room_name": "高手对战房",
                "opponent_id": "user456",
                "opponent_name": "小虾",
                "result": "WIN",
                "my_score": 800,
                "opponent_score": 600,
                "elo_change": 15,
                "new_elo": 1515,
                "played_at": "2026-03-26T10:05:00Z"
            }
        }


class BattleHistoryResponse(BaseModel):
    """Schema for battle history"""
    battles: List[BattleHistoryEntry] = Field(..., description="List of battle history entries")
    total: int = Field(..., description="Total number of battles")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")


# ============== Error Schemas ==============

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Room not found",
                "code": "ROOM_NOT_FOUND"
            }
        }
