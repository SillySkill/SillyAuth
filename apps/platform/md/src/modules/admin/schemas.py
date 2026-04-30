"""
Admin Module Schemas
Pydantic models for admin API requests and responses

Provides schemas for user management, content moderation,
system statistics, and audit logging
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class ContentAction(str, Enum):
    """Content moderation action"""
    APPROVE = "approve"
    REJECT = "reject"


class ContentType(str, Enum):
    """Content types for moderation"""
    ARTICLE = "article"
    COMMENT = "comment"
    IMAGE = "image"
    VIDEO = "video"
    POST = "post"


# ============================================================================
# User Management Schemas
# ============================================================================

class UserManagement(BaseModel):
    """User management action log"""
    user_id: int = Field(..., description="User ID")
    action: str = Field(..., description="Action performed")
    details: Optional[str] = Field(None, description="Action details")


class UserListItem(BaseModel):
    """User list item for admin view"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verified status")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list response"""
    users: List[UserListItem] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")


class UpdateUserStatusRequest(BaseModel):
    """Request to update user status"""
    status: UserStatus = Field(..., description="New user status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class UpdateUserStatusResponse(BaseModel):
    """Response after updating user status"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="Affected user ID")
    new_status: UserStatus = Field(..., description="New status")


class ResetPasswordResponse(BaseModel):
    """Response after resetting user password"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="Affected user ID")
    temporary_password: Optional[str] = Field(None, description="Temporary password (if applicable)")


class UserDetailsResponse(BaseModel):
    """Detailed user information response"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verified status")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# ============================================================================
# Content Moderation Schemas
# ============================================================================

class ContentModeration(BaseModel):
    """Content moderation action log"""
    content_id: int = Field(..., description="Content ID")
    action: ContentAction = Field(..., description="Moderation action")
    reason: Optional[str] = Field(None, description="Reason for action")


class ContentModerationItem(BaseModel):
    """Content item pending moderation"""
    id: int = Field(..., description="Content ID")
    type: ContentType = Field(..., description="Content type")
    title: Optional[str] = Field(None, description="Content title")
    content: Optional[str] = Field(None, description="Content preview")
    author_id: int = Field(..., description="Author user ID")
    author_username: str = Field(..., description="Author username")
    created_at: datetime = Field(..., description="Creation timestamp")
    status: str = Field(..., description="Current status")
    flags: Optional[int] = Field(0, description="Number of flags")

    class Config:
        from_attributes = True


class PendingContentResponse(BaseModel):
    """Paginated pending content response"""
    items: List[ContentModerationItem] = Field(..., description="List of pending content")
    total: int = Field(..., description="Total number of pending items")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")


class RejectContentRequest(BaseModel):
    """Request to reject content"""
    reason: str = Field(..., min_length=1, max_length=1000, description="Rejection reason")


class ContentModerationResponse(BaseModel):
    """Content moderation action response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    content_id: int = Field(..., description="Affected content ID")
    action: ContentAction = Field(..., description="Action taken")


# ============================================================================
# System Statistics Schemas
# ============================================================================

class SystemStats(BaseModel):
    """System statistics"""
    total_users: int = Field(0, description="Total number of users")
    active_users: int = Field(0, description="Number of active users")
    new_users_today: int = Field(0, description="New users today")
    new_users_this_week: int = Field(0, description="New users this week")
    new_users_this_month: int = Field(0, description="New users this month")
    total_content: int = Field(0, description="Total content items")
    pending_moderation: int = Field(0, description="Items pending moderation")
    revenue: float = Field(0.0, description="Total revenue")
    revenue_today: float = Field(0.0, description="Revenue today")
    revenue_this_week: float = Field(0.0, description="Revenue this week")
    revenue_this_month: float = Field(0.0, description="Revenue this month")
    storage_used_gb: float = Field(0.0, description="Storage used in GB")
    bandwidth_gb: float = Field(0.0, description="Bandwidth used in GB")
    api_calls_today: int = Field(0, description="API calls today")
    error_rate: float = Field(0.0, description="Error rate percentage")
    uptime_hours: float = Field(0.0, description="System uptime in hours")


class DashboardData(BaseModel):
    """Dashboard data with charts and metrics"""
    stats: SystemStats = Field(..., description="System statistics")
    user_growth: List[Dict[str, Any]] = Field(default_factory=list, description="User growth data")
    content_growth: List[Dict[str, Any]] = Field(default_factory=list, description="Content growth data")
    revenue_history: List[Dict[str, Any]] = Field(default_factory=list, description="Revenue history")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent platform activity")
    top_content: List[Dict[str, Any]] = Field(default_factory=list, description="Top performing content")
    active_modules: List[str] = Field(default_factory=list, description="Active module IDs")


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogEntry(BaseModel):
    """Audit log entry"""
    id: int = Field(..., description="Log entry ID")
    admin_id: int = Field(..., description="Admin user ID")
    admin_username: str = Field(..., description="Admin username")
    action: str = Field(..., description="Action performed")
    target_type: Optional[str] = Field(None, description="Target entity type")
    target_id: Optional[int] = Field(None, description="Target entity ID")
    target: Optional[str] = Field(None, description="Target description")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    ip_address: Optional[str] = Field(None, description="Admin IP address")
    user_agent: Optional[str] = Field(None, description="Admin user agent")
    timestamp: datetime = Field(..., description="Action timestamp")

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """Paginated audit log response"""
    logs: List[AuditLogEntry] = Field(..., description="List of audit log entries")
    total: int = Field(..., description="Total number of log entries")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")


class AuditLogFilter(BaseModel):
    """Audit log filter parameters"""
    admin_id: Optional[int] = Field(None, description="Filter by admin ID")
    action: Optional[str] = Field(None, description="Filter by action type")
    target_type: Optional[str] = Field(None, description="Filter by target type")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")


# ============================================================================
# Module Management Schemas
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = Field(..., description="Module ID")
    name: str = Field(..., description="Module name")
    version: str = Field(..., description="Module version")
    description: str = Field(..., description="Module description")
    status: str = Field(..., description="Module status")
    dependencies: List[str] = Field(default_factory=list, description="Module dependencies")
    config: Optional[Dict[str, Any]] = Field(None, description="Module configuration")


class ModuleListResponse(BaseModel):
    """Module list response"""
    modules: List[ModuleInfo] = Field(..., description="List of modules")
    total: int = Field(..., description="Total number of modules")


class ModuleActionResponse(BaseModel):
    """Module enable/disable action response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    module_id: str = Field(..., description="Module ID")
    new_status: str = Field(..., description="New module status")


# ============================================================================
# Generic Response Schemas
# ============================================================================

class AdminResponse(BaseModel):
    """Generic admin API response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
