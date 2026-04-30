"""
Staff Module Middleware
Permission checking middleware for staff API endpoints

Provides:
- Authentication dependency
- Permission checking dependency
- Role-based access control
"""

import logging
from typing import Optional, List, Callable

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from .services import (
    auth_service,
    staff_user_service,
    expand_permissions,
    check_permission,
    JWT_SECRET,
    JWT_ALGORITHM,
)

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()


# ============================================================================
# Current User Dependency
# ============================================================================

async def get_current_staff_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated staff user from JWT token

    This is a FastAPI dependency that:
    1. Extracts the JWT token from Authorization header
    2. Verifies the token
    3. Returns the user data

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dict from token payload

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

        # Verify token
        success, payload = auth_service.verify_token(token)
        if not success:
            raise credentials_exception

        # Check token type
        if payload.get("type") != "staff_access":
            raise credentials_exception

        # Get user data from payload
        user_data = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role_id": payload.get("role_id"),
            "role_name": payload.get("role_name"),
            "permissions": payload.get("permissions", []),
        }

        if not user_data["id"]:
            raise credentials_exception

        # Optionally verify user still exists and is active
        user = staff_user_service.get_user_by_id(user_data["id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"账户已被禁用 (状态: {user.status})"
            )

        # Update user_data with fresh data
        user_data["role_name"] = user.role_name

        return user_data

    except HTTPException:
        raise
    except JWTError as e:
        logger.warning(f"JWT error in get_current_staff_user: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error in get_current_staff_user: {e}")
        raise credentials_exception


# ============================================================================
# Optional Current User Dependency
# ============================================================================

async def get_optional_staff_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    Get current authenticated staff user, but allow unauthenticated requests

    This is useful for endpoints that work differently for authenticated vs
    unauthenticated users.

    Args:
        credentials: Optional Bearer token

    Returns:
        User dict if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_staff_user(credentials)
    except HTTPException:
        return None


# ============================================================================
# Permission Checker Dependency
# ============================================================================

def require_permissions(*required_permissions: str):
    """
    Dependency factory for checking multiple permissions

    Usage:
        @router.get("/orders", dependencies=[Depends(require_permissions("orders:order:read"))])
        async def get_orders():
            ...

        @router.put("/orders/{id}", dependencies=[Depends(require_permissions("orders:order:update"))])
        async def update_order():
            ...

        # Multiple permissions (AND logic)
        @router.delete("/orders/{id}", dependencies=[Depends(require_permissions("orders:order:update", "orders:order:delete"))])
        async def delete_order():
            ...

    Args:
        *required_permissions: Permission codes required for this endpoint

    Returns:
        FastAPI dependency that checks permissions
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_staff_user)
    ) -> dict:
        # Get user's expanded permissions
        user_permissions = expand_permissions(current_user.get("permissions", []))

        # Check each required permission
        missing_permissions = []
        for perm in required_permissions:
            if not check_permission(user_permissions, perm):
                missing_permissions.append(perm)

        if missing_permissions:
            logger.warning(
                f"User {current_user['username']} denied access. "
                f"Missing permissions: {missing_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "权限不足",
                    "required_permissions": list(required_permissions),
                    "missing_permissions": missing_permissions
                }
            )

        return current_user

    return permission_checker


def require_any_permission(*required_permissions: str):
    """
    Dependency factory for checking any of the specified permissions (OR logic)

    Usage:
        @router.get("/reports", dependencies=[Depends(require_any_permission("orders:order:read", "finance:report:read"))])
        async def get_reports():
            ...

    Args:
        *required_permissions: Any of these permissions grants access

    Returns:
        FastAPI dependency that checks permissions
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_staff_user)
    ) -> dict:
        # Get user's expanded permissions
        user_permissions = expand_permissions(current_user.get("permissions", []))

        # Check if user has any of the required permissions
        for perm in required_permissions:
            if check_permission(user_permissions, perm):
                return current_user

        logger.warning(
            f"User {current_user['username']} denied access. "
            f"Required any of: {required_permissions}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "权限不足",
                "required_permissions": list(required_permissions),
                "missing_permissions": list(required_permissions)
            }
        )

    return permission_checker


# ============================================================================
# Role Checker Dependency
# ============================================================================

def require_roles(*allowed_roles: str):
    """
    Dependency factory for checking user roles

    Usage:
        @router.delete("/users/{id}", dependencies=[Depends(require_roles("super_admin", "admin"))])
        async def delete_user():
            ...

    Args:
        *allowed_roles: Role codes that are allowed to access this endpoint

    Returns:
        FastAPI dependency that checks roles
    """
    async def role_checker(
        current_user: dict = Depends(get_current_staff_user)
    ) -> dict:
        user_role = current_user.get("role_name", "").lower()

        # Super admin has access to everything
        if user_role == "super_admin":
            return current_user

        if user_role not in [r.lower() for r in allowed_roles]:
            logger.warning(
                f"User {current_user['username']} (role: {user_role}) "
                f"denied access. Required roles: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "角色权限不足",
                    "required_roles": list(allowed_roles),
                    "user_role": current_user.get("role_name")
                }
            )

        return current_user

    return role_checker


# ============================================================================
# Super Admin Checker
# ============================================================================

async def require_super_admin(
    current_user: dict = Depends(get_current_staff_user)
) -> dict:
    """
    Dependency that requires super_admin role

    Usage:
        @router.delete("/roles/{id}", dependencies=[Depends(require_super_admin)])
        async def delete_role():
            ...
    """
    if current_user.get("role_name") != "超级管理员" and current_user.get("role_name", "").lower() != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要超级管理员权限"
        )

    return current_user


# ============================================================================
# Request Logging Middleware
# ============================================================================

async def log_request_middleware(request: Request, call_next):
    """
    Middleware to log all requests to staff API endpoints

    This is registered in the routes module for the /api/staff prefix.
    """
    # Skip logging for certain paths
    skip_paths = {"/api/staff/health", "/api/staff/health/"}

    if request.url.path in skip_paths:
        return await call_next(request)

    # Log request
    logger.debug(
        f"Staff API: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    response = await call_next(request)

    # Log response status
    logger.debug(
        f"Staff API Response: {request.method} {request.url.path} "
        f"-> {response.status_code}"
    )

    return response


# ============================================================================
# Helper Functions
# ============================================================================

def get_client_ip(request: Request) -> Optional[str]:
    """Get client IP from request, considering proxies"""
    # Check X-Forwarded-For header first (for proxied requests)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    if request.client:
        return request.client.host

    return None


def get_user_agent(request: Request) -> Optional[str]:
    """Get User-Agent from request headers"""
    return request.headers.get("user-agent")


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "get_current_staff_user",
    "get_optional_staff_user",
    "require_permissions",
    "require_any_permission",
    "require_roles",
    "require_super_admin",
    "get_client_ip",
    "get_user_agent",
    "security",
]
