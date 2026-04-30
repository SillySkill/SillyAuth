"""
Arena Module - Routes

FastAPI routes for arena PK battles including room management,
battle operations, and ranking queries.
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Header, Body
from fastapi.responses import JSONResponse

from .schemas import (
    RoomCreate, RoomResponse, RoomListResponse, ParticipantInfo,
    BattleStart, BattleResponse, AnswerSubmit, AnswerResponse,
    BattleResultResponse, RankingListResponse, ArenaRanking,
    BattleHistoryResponse, BattleHistoryEntry, BattleReward,
    ErrorResponse, RoomStatus, BattleStatus
)

logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(prefix="/api/v1/arena", tags=["arena"])


# ============== Service Dependencies ==============

def get_arena_service():
    """Dependency to get the arena service instance."""
    from . import _arena_service
    if _arena_service is None:
        raise HTTPException(
            status_code=503,
            detail="Arena service not initialized"
        )
    return _arena_service


def get_battle_service():
    """Dependency to get the battle service instance."""
    from . import _battle_service
    if _battle_service is None:
        raise HTTPException(
            status_code=503,
            detail="Battle service not initialized"
        )
    return _battle_service


def get_ranking_service():
    """Dependency to get the ranking service instance."""
    from . import _ranking_service
    if _ranking_service is None:
        raise HTTPException(
            status_code=503,
            detail="Ranking service not initialized"
        )
    return _ranking_service


# ============== Authentication Dependency ==============

def get_current_user_id(x_user_id: str = Header(None, alias="X-User-ID")) -> str:
    """
    Dependency to get current user ID from header.

    In production, this should validate the user session/token.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return x_user_id


# ============== Room Routes ==============

@router.post(
    "/rooms",
    response_model=RoomResponse,
    status_code=201,
    summary="Create room",
    description="Create a new arena PK room",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def create_room(
    data: RoomCreate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_arena_service)
) -> RoomResponse:
    """
    Create a new arena PK room.

    The creating user will automatically join the room as the first participant.

    Args:
        data: Room creation details
        user_id: Current user ID (from header)
        service: Arena service instance

    Returns:
        Created room information
    """
    try:
        return service.create_room(user_id, data)
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )


@router.get(
    "/rooms",
    response_model=RoomListResponse,
    summary="List rooms",
    description="List arena rooms with pagination",
    responses={
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def list_rooms(
    status: Optional[RoomStatus] = Query(None, description="Filter by room status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service=Depends(get_arena_service)
) -> RoomListResponse:
    """
    List arena rooms with optional status filter and pagination.

    Args:
        status: Optional room status filter
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        service: Arena service instance

    Returns:
        Paginated list of rooms
    """
    try:
        rooms, total = service.list_rooms(status=status, page=page, limit=limit)
        return RoomListResponse(
            rooms=rooms,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing rooms: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list rooms: {str(e)}"
        )


@router.get(
    "/rooms/{room_id}",
    response_model=RoomResponse,
    summary="Get room",
    description="Get details of a specific room",
    responses={
        404: {"model": ErrorResponse, "description": "Room not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_room(
    room_id: str,
    service=Depends(get_arena_service)
) -> RoomResponse:
    """
    Get details of a specific arena room.

    Args:
        room_id: Room ID to retrieve
        service: Arena service instance

    Returns:
        Room information
    """
    try:
        room = service.get_room(room_id)
        if room is None:
            raise HTTPException(
                status_code=404,
                detail=f"Room {room_id} not found"
            )
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting room {room_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get room: {str(e)}"
        )


@router.post(
    "/rooms/{room_id}/join",
    response_model=RoomResponse,
    summary="Join room",
    description="Join an existing arena room",
    responses={
        400: {"model": ErrorResponse, "description": "Cannot join room"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Room not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def join_room(
    room_id: str,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_arena_service)
) -> RoomResponse:
    """
    Join an existing arena room.

    Args:
        room_id: Room ID to join
        user_id: Current user ID (from header)
        service: Arena service instance

    Returns:
        Updated room information
    """
    try:
        return service.join_room(room_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error joining room {room_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to join room: {str(e)}"
        )


@router.post(
    "/rooms/{room_id}/leave",
    status_code=204,
    summary="Leave room",
    description="Leave an arena room",
    responses={
        400: {"model": ErrorResponse, "description": "Cannot leave room"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Room not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def leave_room(
    room_id: str,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_arena_service)
):
    """
    Leave an arena room.

    Args:
        room_id: Room ID to leave
        user_id: Current user ID (from header)
        service: Arena service instance

    Returns:
        No content on success
    """
    try:
        service.leave_room(room_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error leaving room {room_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to leave room: {str(e)}"
        )


# ============== Battle Routes ==============

@router.post(
    "/battles/{room_id}/start",
    response_model=BattleResponse,
    status_code=201,
    summary="Start battle",
    description="Start a battle in a room with specified participants",
    responses={
        400: {"model": ErrorResponse, "description": "Cannot start battle"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Room not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def start_battle(
    room_id: str,
    participant_ids: list = Body(..., description="List of participant user IDs"),
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_battle_service)
) -> BattleResponse:
    """
    Start a battle in a room.

    Args:
        room_id: Room ID to start battle in
        participant_ids: List of participant user IDs for the battle
        user_id: Current user ID (from header)
        service: Battle service instance

    Returns:
        Battle information
    """
    try:
        return service.start_battle(room_id, participant_ids)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting battle in room {room_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start battle: {str(e)}"
        )


@router.post(
    "/battles/{battle_id}/answer",
    response_model=AnswerResponse,
    summary="Submit answer",
    description="Submit an answer for the current battle question",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid submission"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Battle not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def submit_answer(
    battle_id: str,
    data: AnswerSubmit,
    correct_answer: str = Body(..., description="The correct answer for scoring"),
    points_per_question: int = Body(100, description="Points per question"),
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_battle_service)
) -> AnswerResponse:
    """
    Submit an answer for the current battle question.

    Args:
        battle_id: Battle ID
        data: Answer submission details
        correct_answer: The correct answer (for scoring)
        points_per_question: Points awarded for correct answer
        user_id: Current user ID (from header)
        service: Battle service instance

    Returns:
        Answer result with scoring
    """
    try:
        result = service.submit_answer(
            battle_id=battle_id,
            user_id=user_id,
            answer=data.answer,
            time_taken=data.time_taken,
            correct_answer=correct_answer,
            points_per_question=points_per_question
        )
        return AnswerResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting answer for battle {battle_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.get(
    "/battles/{battle_id}/result",
    response_model=BattleResultResponse,
    summary="Get battle result",
    description="Get the result of a finished battle",
    responses={
        400: {"model": ErrorResponse, "description": "Battle not finished"},
        404: {"model": ErrorResponse, "description": "Battle not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_battle_result(
    battle_id: str,
    service=Depends(get_battle_service)
) -> BattleResultResponse:
    """
    Get the result of a finished battle.

    Args:
        battle_id: Battle ID
        service: Battle service instance

    Returns:
        Battle result with winner, scores, and rewards
    """
    try:
        return service.finish_battle(battle_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting battle result for {battle_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get battle result: {str(e)}"
        )


# ============== Ranking Routes ==============

@router.get(
    "/rankings",
    response_model=RankingListResponse,
    summary="Get rankings",
    description="Get arena rankings with pagination",
    responses={
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_rankings(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service=Depends(get_ranking_service)
) -> RankingListResponse:
    """
    Get arena rankings with pagination.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        service: Ranking service instance

    Returns:
        Paginated list of rankings
    """
    try:
        rankings, total = service.get_rankings(page=page, limit=limit)
        return RankingListResponse(
            rankings=rankings,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting rankings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get rankings: {str(e)}"
        )


@router.get(
    "/rankings/me",
    response_model=ArenaRanking,
    summary="My rank",
    description="Get current user's arena ranking",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "User not ranked"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_my_rank(
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_ranking_service)
) -> ArenaRanking:
    """
    Get current user's arena ranking.

    Args:
        user_id: Current user ID (from header)
        service: Ranking service instance

    Returns:
        User's ranking information
    """
    try:
        ranking = service.get_user_rank(user_id)
        if ranking is None:
            raise HTTPException(
                status_code=404,
                detail="User not ranked yet. Play some battles to get ranked!"
            )
        return ranking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rank for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user rank: {str(e)}"
        )


# ============== Battle History Routes ==============

@router.get(
    "/battles/history",
    response_model=BattleHistoryResponse,
    summary="Battle history",
    description="Get current user's battle history",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_battle_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_battle_service)
) -> BattleHistoryResponse:
    """
    Get current user's battle history.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        user_id: Current user ID (from header)
        service: Battle service instance

    Returns:
        Paginated list of battle history entries
    """
    try:
        battles, total = service.get_battle_history(user_id, page=page, limit=limit)
        return BattleHistoryResponse(
            battles=battles,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting battle history for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get battle history: {str(e)}"
        )
