"""
Messages Module Schemas
Pydantic models for messaging requests and responses

Provides message, conversation, thread, and notification schemas.
Uses Pydantic v2 conventions (model_config instead of class Config).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Any, Dict
from datetime import datetime


# ============================================================================
# Message Schemas
# ============================================================================

class MessageCreate(BaseModel):
    """Message creation request"""
    recipient_id: int = Field(..., description="Recipient user ID")
    content: str = Field(..., min_length=1, description="Message content")
    type: Literal["system", "user", "admin"] = Field(
        default="user",
        description="Message type: system, user, or admin"
    )
    attachments: Optional[List[dict]] = Field(
        default=None,
        description="List of attachment objects"
    )

    @field_validator('content')
    @classmethod
    def content_length(cls, v: str) -> str:
        """Validate message content length"""
        if len(v) > 5000:
            raise ValueError('消息内容不能超过5000个字符')
        return v

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Message response model"""
    id: int = Field(..., description="Message ID")
    sender_id: int = Field(..., description="Sender user ID")
    sender_username: Optional[str] = Field(None, description="Sender username")
    sender_avatar: Optional[str] = Field(None, description="Sender avatar URL")
    recipient_id: int = Field(..., description="Recipient user ID")
    recipient_username: Optional[str] = Field(None, description="Recipient username")
    content: str = Field(..., description="Message content")
    type: Literal["system", "user", "admin"] = Field(..., description="Message type")
    read: bool = Field(default=False, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Time when message was read")
    attachments: Optional[List[dict]] = Field(None, description="Attachments")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_own: bool = Field(default=False, description="Whether current user sent this message")

    model_config = {"from_attributes": True}


class MessageThread(BaseModel):
    """Message thread response"""
    id: int = Field(..., description="Thread ID")
    participants: List[dict] = Field(..., description="List of participant objects")
    last_message: Optional[MessageResponse] = Field(None, description="Last message in thread")
    unread_count: int = Field(default=0, description="Unread message count")
    created_at: datetime = Field(..., description="Thread creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    """Create conversation request"""
    participant_ids: List[int] = Field(..., min_length=1, description="Participant user IDs")
    initial_message: Optional[str] = Field(None, description="Initial message content")
    title: Optional[str] = Field(None, description="Conversation title (for group chats)")

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: int = Field(..., description="Conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    participants: List[dict] = Field(..., description="List of participants")
    last_message: Optional[MessageResponse] = Field(None, description="Last message")
    unread_count: int = Field(default=0, description="Unread message count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_group: bool = Field(default=False, description="Is group conversation")
    has_unread: bool = Field(default=False, description="Has unread messages")

    model_config = {"from_attributes": True}


# ============================================================================
# Conversation Schemas (for conversation-based messaging)
# ============================================================================

class CreateConversationRequest(BaseModel):
    """Request schema for creating a new conversation"""
    conversation_type: str = Field(
        default="direct",
        description="Conversation type: direct or group"
    )
    title: Optional[str] = Field(None, description="Conversation title (for group chats)")
    participant_ids: List[int] = Field(..., min_length=1, description="Participant user IDs")
    initial_message: Optional[str] = Field(None, description="Initial message content")

    model_config = {"from_attributes": True}


class CreateConversationResponse(BaseModel):
    """Response schema for conversation creation"""
    conversation_id: int = Field(..., description="New conversation ID")
    created: bool = Field(..., description="Whether the conversation was newly created")
    message: Optional[str] = Field(None, description="Status message")

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Conversation list item response"""
    id: int = Field(..., description="Conversation ID")
    conversation_type: str = Field(..., description="Conversation type (direct or group)")
    title: Optional[str] = Field(None, description="Conversation title")
    is_group: bool = Field(default=False, description="Is group conversation")
    last_message_at: Optional[datetime] = Field(None, description="Last message timestamp")
    last_message_content: Optional[str] = Field(None, description="Last message content")
    last_message_sender: Optional[str] = Field(None, description="Last message sender username")
    has_unread: bool = Field(default=False, description="Has unread messages")
    unread_count: int = Field(default=0, description="Number of unread messages")
    participants: List[Dict[str, Any]] = Field(default_factory=list, description="List of participants")

    model_config = {"from_attributes": True}


class ConversationMessageResponse(BaseModel):
    """Message response within a conversation"""
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    sender_id: int = Field(..., description="Sender user ID")
    sender_username: str = Field(..., description="Sender username")
    sender_avatar: Optional[str] = Field(None, description="Sender avatar URL")
    content: str = Field(..., description="Message content")
    message_type: str = Field(..., description="Message type")
    reply_to_id: Optional[int] = Field(None, description="Replied message ID")
    attachments: Optional[dict] = Field(None, description="Attachments")
    is_deleted: bool = Field(default=False, description="Is deleted")
    is_system: bool = Field(default=False, description="Is system message")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_own: bool = Field(default=False, description="Whether sent by current user")

    model_config = {"from_attributes": True}


class DeleteConversationResponse(BaseModel):
    """Response for conversation deletion"""
    success: bool = Field(..., description="Operation success status")
    conversation_id: int = Field(..., description="Deleted conversation ID")

    model_config = {"from_attributes": True}


# ============================================================================
# Notification Schemas
# ============================================================================

class NotificationCreate(BaseModel):
    """Notification creation request"""
    user_id: int = Field(..., description="Target user ID")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    content: str = Field(..., min_length=1, description="Notification content")
    type: Literal["info", "warning", "error", "success", "system"] = Field(
        default="info",
        description="Notification type"
    )
    action_url: Optional[str] = Field(None, description="Action URL when clicked")
    metadata: Optional[dict] = Field(None, description="Additional metadata")

    model_config = {"from_attributes": True}


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: int = Field(..., description="Notification ID")
    user_id: int = Field(..., description="Target user ID")
    title: str = Field(..., description="Notification title")
    content: str = Field(..., description="Notification content")
    type: Literal["info", "warning", "error", "success", "system"] = Field(
        ...,
        description="Notification type"
    )
    read: bool = Field(default=False, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Time when notification was read")
    action_url: Optional[str] = Field(None, description="Action URL")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Notification list response with pagination"""
    items: List[NotificationResponse] = Field(..., description="List of notifications")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    unread_count: int = Field(..., description="Total unread count")

    model_config = {"from_attributes": True}


# ============================================================================
# Generic Response Schemas
# ============================================================================

class MessageListResponse(BaseModel):
    """Message list response with pagination"""
    items: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")

    model_config = {"from_attributes": True}


class ThreadListResponse(BaseModel):
    """Thread list response with pagination"""
    items: List[ConversationResponse] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    """Send message request"""
    recipient_id: int = Field(..., description="Recipient user ID")
    content: str = Field(..., min_length=1, description="Message content")
    type: Literal["system", "user", "admin"] = Field(
        default="user",
        description="Message type"
    )
    attachments: Optional[List[dict]] = Field(None, description="Attachments")

    @field_validator('content')
    @classmethod
    def content_length(cls, v: str) -> str:
        """Validate message content length"""
        if len(v) > 5000:
            raise ValueError('消息内容不能超过5000个字符')
        return v

    model_config = {"from_attributes": True}


class MarkReadRequest(BaseModel):
    """Mark read request"""
    message_ids: Optional[List[int]] = Field(None, description="Message IDs to mark as read")
    conversation_id: Optional[int] = Field(None, description="Mark all messages in conversation as read")

    model_config = {"from_attributes": True}


class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")

    model_config = {"from_attributes": True}
