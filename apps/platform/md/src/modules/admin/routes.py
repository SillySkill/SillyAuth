"""
Admin Module Routes
FastAPI routes for admin API endpoints

Provides user management, content moderation, system statistics,
audit logs, and module management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from jose import jwt, JWTError
import logging
import os

from .schemas import (
    UserStatus,
    ContentType,
    ContentAction,
    UserListResponse,
    UpdateUserStatusRequest,
    UpdateUserStatusResponse,
    ResetPasswordResponse,
    UserDetailsResponse,
    PendingContentResponse,
    RejectContentRequest,
    ContentModerationResponse,
    SystemStats,
    DashboardData,
    AuditLogResponse,
    AuditLogFilter,
    ModuleListResponse,
    ModuleInfo,
    ModuleActionResponse,
    AdminResponse,
    ErrorResponse,
)

from .services import (
    user_management_service,
    content_moderation_service,
    system_service,
    audit_log_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/admin", tags=["管理后台"])

# HTTP Bearer security scheme
security = HTTPBearer()

# JWT configuration (should match auth module)
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION")
ALGORITHM = "HS256"

# Admin roles configuration
ADMIN_ROLES = ['super_admin', 'content_admin', 'user_admin', 'finance_admin']



# ============================================================================
# Helper Functions
# ============================================================================

def get_db_cursor():
    """Get database cursor"""
    from core.db_adapter import get_db_cursor
    return get_db_cursor()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated admin user from JWT token

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dict from database

    Raises:
        HTTPException: If token is invalid, user not found, or not admin
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    not_admin_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="需要管理员权限"
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

        # Check if user has admin role
        user_role = user.get('role', 'user')
        if user_role not in ADMIN_ROLES:
            logger.warning(f"Non-admin user {user_id} attempted to access admin endpoint")
            raise not_admin_exception

        return user

    except JWTError:
        raise credentials_exception
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin auth error: {str(e)}")
        raise credentials_exception


def log_admin_action(
    admin_id: int,
    action: str,
    target: Optional[str] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
) -> None:
    """
    Log admin action to audit log

    Args:
        admin_id: Admin user ID
        action: Action performed
        target: Target description
        details: Additional details
        request: FastAPI request object for IP/user-agent
    """
    ip_address = None
    user_agent = None

    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')

    audit_log_service.log_action(
        admin_id=admin_id,
        action=action,
        target=target,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )


# ============================================================================
# User Management Routes
# ============================================================================

@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = 1,
    limit: int = 20,
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    verified: Optional[bool] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get paginated list of users

    Requires admin role authorization.
    """
    # Build filters
    filters = {}
    if role:
        filters['role'] = role
    if status:
        filters['status'] = status
    if search:
        filters['search'] = search
    if verified is not None:
        filters['verified'] = verified

    # Validate pagination
    page = max(1, page)
    limit = min(100, max(1, limit))

    # Get users
    users, total = user_management_service.get_users(filters, page, limit)

    # Log action
    log_admin_action(
        current_admin['id'],
        'list_users',
        details={'filters': filters, 'page': page, 'limit': limit}
    )

    # Calculate pages
    pages = (total + limit - 1) // limit if total > 0 else 0

    return UserListResponse(
        users=users,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/users/{user_id}", response_model=UserDetailsResponse)
async def get_user_details(
    user_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get detailed user information

    Requires admin role authorization.
    """
    user = user_management_service.get_user_details(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # Log action
    log_admin_action(
        current_admin['id'],
        'view_user_details',
        target=f'user:{user_id}'
    )

    return user


@router.put("/users/{user_id}/status", response_model=UpdateUserStatusResponse)
async def update_user_status(
    user_id: int,
    request: UpdateUserStatusRequest,
    http_request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Update user account status

    Requires admin role authorization.
    """
    # Check if user exists
    user = user_management_service.get_user_details(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # Cannot modify own status
    if user_id == current_admin['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )

    # Update status
    success = user_management_service.update_user_status(
        user_id,
        request.status,
        request.reason
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="状态更新失败"
        )

    # Log action
    log_admin_action(
        current_admin['id'],
        'update_user_status',
        target=f'user:{user_id}',
        details={
            'new_status': request.status.value,
            'reason': request.reason
        },
        request=http_request
    )

    return UpdateUserStatusResponse(
        success=True,
        message="用户状态已更新",
        user_id=user_id,
        new_status=request.status
    )


@router.post("/users/{user_id}/reset-password", response_model=ResetPasswordResponse)
async def reset_user_password(
    user_id: int,
    http_request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Reset user password to a temporary password

    Requires admin role authorization.
    """
    # Check if user exists
    user = user_management_service.get_user_details(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # Cannot reset own password through this endpoint
    if user_id == current_admin['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能重置自己的密码，请使用密码修改功能"
        )

    # Reset password
    success, temp_password = user_management_service.reset_user_password(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败"
        )

    # Log action
    log_admin_action(
        current_admin['id'],
        'reset_user_password',
        target=f'user:{user_id}',
        request=http_request
    )

    return ResetPasswordResponse(
        success=True,
        message="密码已重置，请在安全的地方保存临时密码",
        user_id=user_id,
        temporary_password=temp_password
    )


# ============================================================================
# Content Moderation Routes
# ============================================================================

@router.get("/content/pending", response_model=PendingContentResponse)
async def get_pending_content(
    content_type: Optional[ContentType] = None,
    page: int = 1,
    limit: int = 20,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get paginated list of pending content for moderation

    Requires admin role authorization.
    """
    # Validate pagination
    page = max(1, page)
    limit = min(100, max(1, limit))

    # Get pending content
    items, total = content_moderation_service.get_pending_content(content_type, page, limit)

    # Log action
    log_admin_action(
        current_admin['id'],
        'list_pending_content',
        details={'content_type': content_type.value if content_type else None}
    )

    return PendingContentResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        content_type=content_type
    )


@router.post("/content/{content_id}/approve", response_model=ContentModerationResponse)
async def approve_content(
    content_id: int,
    content_type: str = "article",
    http_request: Request = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Approve content

    Requires admin role authorization.
    """
    # Approve content
    success = content_moderation_service.approve_content(content_id, content_type)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内容审核失败"
        )

    # Log action
    log_admin_action(
        current_admin['id'],
        'approve_content',
        target=f'{content_type}:{content_id}',
        request=http_request
    )

    return ContentModerationResponse(
        success=True,
        message="内容已通过审核",
        content_id=content_id,
        action=ContentAction.APPROVE
    )


@router.post("/content/{content_id}/reject", response_model=ContentModerationResponse)
async def reject_content(
    content_id: int,
    request: RejectContentRequest,
    content_type: str = "article",
    http_request: Request = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Reject content

    Requires admin role authorization.
    """
    # Reject content
    success = content_moderation_service.reject_content(
        content_id,
        request.reason,
        content_type
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内容审核失败"
        )

    # Log action
    log_admin_action(
        current_admin['id'],
        'reject_content',
        target=f'{content_type}:{content_id}',
        details={'reason': request.reason},
        request=http_request
    )

    return ContentModerationResponse(
        success=True,
        message="内容已拒绝",
        content_id=content_id,
        action=ContentAction.REJECT
    )


# ============================================================================
# System Statistics Routes
# ============================================================================

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get system statistics

    Requires admin role authorization.
    """
    # Log action
    log_admin_action(
        current_admin['id'],
        'view_system_stats'
    )

    return system_service.get_system_stats()


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get dashboard data with charts and metrics

    Requires admin role authorization.
    """
    # Log action
    log_admin_action(
        current_admin['id'],
        'view_dashboard'
    )

    return system_service.get_dashboard_data()


# ============================================================================
# Audit Log Routes
# ============================================================================

@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get paginated audit logs

    Requires admin role authorization.
    """
    # Build filters
    from datetime import datetime
    filters = AuditLogFilter(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None
    )

    # Validate pagination
    page = max(1, page)
    limit = min(100, max(1, limit))

    # Get audit logs
    logs, total = audit_log_service.get_audit_logs(filters, page, limit)

    # Calculate pages
    pages = (total + limit - 1) // limit if total > 0 else 0

    return AuditLogResponse(
        logs=logs,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


# ============================================================================
# Module Management Routes
# ============================================================================

@router.get("/modules", response_model=ModuleListResponse)
async def get_modules(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get list of all modules

    Requires admin role authorization.
    """
    # Get modules from plugin manager
    modules = []

    try:
        # Import here to avoid circular imports
        from src.core.plugin_manager import PluginManager
        from src.core.module import ModuleState

        # Access plugin manager from app state (would need proper integration)
        # For now, return a placeholder response
        modules = []

    except ImportError:
        logger.warning("Could not import plugin manager")

    # Log action
    log_admin_action(
        current_admin['id'],
        'list_modules'
    )

    return ModuleListResponse(
        modules=modules,
        total=len(modules)
    )


@router.post("/modules/{module_id}/enable", response_model=ModuleActionResponse)
async def enable_module(
    module_id: str,
    http_request: Request = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Enable a module

    Requires admin role authorization.
    """
    try:
        # Import here to avoid circular imports
        from src.core.plugin_manager import PluginManager

        # Would need proper integration with app state
        # For now, return a placeholder response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="模块管理功能需要完整的应用集成"
        )

    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模块管理系统不可用"
        )


@router.post("/modules/{module_id}/disable", response_model=ModuleActionResponse)
async def disable_module(
    module_id: str,
    http_request: Request = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Disable a module

    Requires admin role authorization.
    """
    try:
        # Import here to avoid circular imports
        from src.core.plugin_manager import PluginManager

        # Would need proper integration with app state
        # For now, return a placeholder response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="模块管理功能需要完整的应用集成"
        )

    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模块管理系统不可用"
        )


# ============================================================================
# Health Check (for internal use)
# ============================================================================

@router.get("/health")
async def admin_health_check():
    """
    Admin module health check

    No authentication required.
    """
    return {
        "status": "healthy",
        "module": "admin",
        "version": "1.0.0"
    }
