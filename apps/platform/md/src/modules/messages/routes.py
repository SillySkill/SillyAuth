"""
Messages Module Routes
FastAPI routes for messaging and notification endpoints

Provides message sending, conversation retrieval, thread management,
and notification endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from jose import jwt, JWTError
import logging
import os

from .schemas import (
    SendMessageRequest,
    MessageResponse,
    MessageListResponse,
    ConversationResponse,
    ThreadListResponse,
    NotificationResponse,
    NotificationListResponse,
    MarkReadRequest,
    ApiResponse,
    CreateConversationRequest,
    CreateConversationResponse,
    DeleteConversationResponse,
)
from .services import message_service, notification_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/messages", tags=["消息"])

# HTTP Bearer security scheme
security = HTTPBearer()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "sillymd"),
    "user": os.getenv("DB_USER", "sillyAdmin"),
    "password": os.getenv("DB_PASSWORD", "")
}

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production-2024-sillymd-api")
ALGORITHM = "HS256"


# ============================================================================
# Helper Functions
# ============================================================================

def get_db_cursor():
    """Get database cursor"""
    from server.api.database import get_db_cursor
    return get_db_cursor(DB_CONFIG)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dict from database

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("user_id")
        if not user_id:
            raise credentials_exception

        # Get user from database
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()

        if not user:
            raise credentials_exception

        # Check if user is active
        if not user.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )

        return user

    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise credentials_exception


# ============================================================================
# Message Routes
# ============================================================================

@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to another user

    Args:
        request: SendMessageRequest with recipient_id, content, type, attachments
        current_user: Authenticated user

    Returns:
        Created message
    """
    # Cannot send message to self
    if request.recipient_id == current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能给自己发送消息"
        )

    result = message_service.send_message(
        sender_id=current_user['id'],
        recipient_id=request.recipient_id,
        content=request.content,
        msg_type=request.type,
        attachments=request.attachments
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败"
        )

    return result


@router.get("/conversation/{user_id}", response_model=MessageListResponse)
async def get_conversation(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get conversation with another user

    Args:
        user_id: Other user ID
        page: Page number
        limit: Items per page
        current_user: Authenticated user

    Returns:
        Paginated list of messages
    """
    messages, total = message_service.get_conversation(
        user_id=current_user['id'],
        other_user_id=user_id,
        page=page,
        limit=limit
    )

    return MessageListResponse(
        items=messages,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/threads", response_model=ThreadListResponse)
async def get_threads(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get message threads for current user

    Args:
        page: Page number
        limit: Items per page
        current_user: Authenticated user

    Returns:
        Paginated list of conversations/threads
    """
    threads, total = message_service.get_threads(
        user_id=current_user['id'],
        page=page,
        limit=limit
    )

    # Build conversation responses
    conversations = []
    for thread in threads:
        participant = {
            'user_id': thread['participant_id'],
            'username': thread['participant_username'],
            'avatar_url': thread['participant_avatar']
        }

        last_message = None
        if thread['last_message']:
            last_message = MessageResponse(
                id=thread['last_message'].get('id', 0),
                sender_id=thread['last_message'].get('sender_id', 0),
                sender_username=thread['last_message'].get('sender_username'),
                sender_avatar=None,
                recipient_id=0,
                recipient_username=None,
                content=thread['last_message'].get('content', ''),
                type=thread['last_message'].get('type', 'user'),
                read=False,
                read_at=None,
                attachments=None,
                created_at=thread['last_message'].get('created_at'),
                is_own=thread['last_message'].get('is_own', False)
            )

        conversation = ConversationResponse(
            id=thread['participant_id'],  # Use participant_id as conversation ID
            title=None,
            participants=[participant],
            last_message=last_message,
            unread_count=thread['unread_count'],
            created_at=thread['last_message_at'],
            updated_at=thread['last_message_at'],
            is_group=False,
            has_unread=thread['unread_count'] > 0
        )
        conversations.append(conversation)

    return ThreadListResponse(
        items=conversations,
        total=total,
        page=page,
        limit=limit
    )


@router.put("/{message_id}/read", response_model=ApiResponse)
async def mark_message_read(
    message_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a message as read

    Args:
        message_id: Message ID
        current_user: Authenticated user

    Returns:
        Success response
    """
    success = message_service.mark_as_read(message_id, current_user['id'])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或无权操作"
        )

    return ApiResponse(
        success=True,
        message="消息已标记为已读"
    )


@router.put("/conversation/{user_id}/read", response_model=ApiResponse)
async def mark_conversation_read(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark all messages in a conversation as read

    Args:
        user_id: Other user ID
        current_user: Authenticated user

    Returns:
        Success response with count
    """
    count = message_service.mark_conversation_read(current_user['id'], user_id)

    return ApiResponse(
        success=True,
        message=f"已标记 {count} 条消息为已读",
        data={"count": count}
    )


@router.delete("/{message_id}", response_model=ApiResponse)
async def delete_message(
    message_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a message (soft delete)

    Args:
        message_id: Message ID
        current_user: Authenticated user

    Returns:
        Success response
    """
    success = message_service.delete_message(message_id, current_user['id'])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或无权删除"
        )

    return ApiResponse(
        success=True,
        message="消息已删除"
    )


@router.get("/unread-count", response_model=dict)
async def get_unread_message_count(
    current_user: dict = Depends(get_current_user)
):
    """
    Get total unread message count

    Args:
        current_user: Authenticated user

    Returns:
        Unread count
    """
    count = message_service.get_unread_count(current_user['id'])

    return {"unread_count": count}


# ============================================================================
# Conversation Routes
# ============================================================================

@router.post(
    "/conversations",
    response_model=CreateConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Create a new direct or group conversation"
)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new conversation.

    Supports both direct (1-on-1) and group conversations.
    Validates participants exist and checks for existing direct conversations.

    Args:
        request: CreateConversationRequest with conversation details
        current_user: Authenticated user

    Returns:
        CreateConversationResponse with conversation ID and creation status
    """
    try:
        result = message_service.create_conversation(
            created_by=current_user['id'],
            request=request
        )
        return CreateConversationResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话失败"
        )


@router.delete(
    "/conversations/{conversation_id}",
    response_model=DeleteConversationResponse,
    summary="Delete a conversation",
    description="Soft-delete a conversation (removes current user from it)"
)
async def delete_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation (soft delete).

    Removes the current user from the conversation participants.
    The conversation remains visible to other participants.

    Args:
        conversation_id: Conversation ID to delete
        current_user: Authenticated user

    Returns:
        DeleteConversationResponse with success status
    """
    try:
        success = message_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user['id']
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在或无权删除"
            )

        return DeleteConversationResponse(
            success=True,
            conversation_id=conversation_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除对话失败"
        )


# ============================================================================
# Notification Routes
# ============================================================================

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="Filter to unread only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get notifications for current user

    Args:
        unread_only: Filter to unread only
        page: Page number
        limit: Items per page
        current_user: Authenticated user

    Returns:
        Paginated list of notifications
    """
    notifications, total, unread_count = notification_service.get_notifications(
        user_id=current_user['id'],
        unread_only=unread_only,
        page=page,
        limit=limit
    )

    return NotificationListResponse(
        items=notifications,
        total=total,
        page=page,
        limit=limit,
        unread_count=unread_count
    )


@router.put("/notifications/{notification_id}/read", response_model=ApiResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a notification as read

    Args:
        notification_id: Notification ID
        current_user: Authenticated user

    Returns:
        Success response
    """
    success = notification_service.mark_notification_read(
        notification_id,
        current_user['id']
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在或无权操作"
        )

    return ApiResponse(
        success=True,
        message="通知已标记为已读"
    )


@router.put("/notifications/read-all", response_model=ApiResponse)
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user)
):
    """
    Mark all notifications as read

    Args:
        current_user: Authenticated user

    Returns:
        Success response with count
    """
    count = notification_service.mark_all_read(current_user['id'])

    return ApiResponse(
        success=True,
        message=f"已标记 {count} 条通知为已读",
        data={"count": count}
    )


@router.get("/notifications/unread-count", response_model=dict)
async def get_unread_notification_count(
    current_user: dict = Depends(get_current_user)
):
    """
    Get unread notification count

    Args:
        current_user: Authenticated user

    Returns:
        Unread count
    """
    count = notification_service.get_unread_count(current_user['id'])

    return {"unread_count": count}


@router.delete("/notifications/{notification_id}", response_model=ApiResponse)
async def delete_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a notification

    Args:
        notification_id: Notification ID
        current_user: Authenticated user

    Returns:
        Success response
    """
    success = notification_service.delete_notification(
        notification_id,
        current_user['id']
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在或无权删除"
        )

    return ApiResponse(
        success=True,
        message="通知已删除"
    )


# ============================================================================
# Admin Routes (for system notifications)
# ============================================================================

@router.post("/notifications/broadcast", response_model=ApiResponse)
async def broadcast_notification(
    title: str = Query(..., description="Notification title"),
    content: str = Query(..., description="Notification content"),
    notif_type: str = Query("system", description="Notification type"),
    target_role: Optional[str] = Query(None, description="Target user role (optional)")
):
    """
    Broadcast a notification to all users or specific role

    Args:
        title: Notification title
        content: Notification content
        notif_type: Notification type
        target_role: Optional role to filter users

    Returns:
        Success response with count
    """
    try:
        # Get target users
        with get_db_cursor() as cur:
            if target_role:
                cur.execute(
                    "SELECT id FROM users WHERE role = %s AND is_active = TRUE",
                    (target_role,)
                )
            else:
                cur.execute(
                    "SELECT id FROM users WHERE is_active = TRUE"
                )

            users = cur.fetchall()

        count = 0
        for user in users:
            result = notification_service.send_notification(
                user_id=user['id'],
                title=title,
                content=content,
                notif_type=notif_type
            )
            if result:
                count += 1

        return ApiResponse(
            success=True,
            message=f"已发送 {count} 条通知",
            data={"count": count}
        )

    except Exception as e:
        logger.error(f"Failed to broadcast notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="广播通知失败"
        )
