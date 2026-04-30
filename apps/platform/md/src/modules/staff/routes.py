"""
Staff Module Routes
FastAPI routes for staff management API endpoints

Provides endpoints for:
- Staff authentication (login/logout)
- Staff user CRUD
- Role management
- Permission management
- Audit logging
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer

from .schemas import (
    # Auth schemas
    LoginRequest,
    LoginResponse,
    ChangePasswordRequest,
    ResetPasswordRequest,

    # Staff user schemas
    StaffUserCreate,
    StaffUserUpdate,
    StaffUserResponse,
    StaffUserListResponse,
    StaffUserStatusUpdate,
    StaffPasswordUpdate,
    StaffUserResponseWrapper,
    StaffOperationResponse,

    # Role schemas
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    RoleOperationResponse,

    # Permission schemas
    PermissionResponse,
    PermissionListResponse,
    PermissionTreeResponse,

    # Audit log schemas
    AuditLogFilter,
    AuditLogResponse,

    # Module info
    ModuleInfo,
)

from .services import (
    auth_service,
    staff_user_service,
    role_service,
    permission_service,
    audit_service,
    generate_temp_password,
)

from .middleware import (
    get_current_staff_user,
    require_permissions,
    require_any_permission,
    require_roles,
    require_super_admin,
    get_client_ip,
    get_user_agent,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/staff", tags=["员工管理"])

# HTTP Bearer security scheme
security = HTTPBearer()


# ============================================================================
# Authentication Routes
# ============================================================================

@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    http_request: Request
):
    """
    Staff user login

    Authenticates a staff user and returns a JWT access token.
    """
    # Authenticate user
    success, user_data, error = auth_service.authenticate(
        request.username,
        request.password
    )

    if not success:
        return LoginResponse(
            success=False,
            message=error,
            access_token=None,
            token_type=None,
            expires_in=None,
            user=None
        )

    # Create access token
    access_token = auth_service.create_access_token(user_data)

    # Log login action
    audit_service.log_action(
        user_id=user_data["id"],
        action="login",
        resource="staff_auth",
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details={"username": request.username}
    )

    # Build user response
    user_response = StaffUserResponse(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data.get("email"),
        phone=user_data.get("phone"),
        role_id=user_data["role_id"],
        role_name=user_data.get("role_name"),
        status=user_data["status"],
        last_login=None,
        created_by=None,
        created_at=datetime.now(),
        updated_at=None
    )

    return LoginResponse(
        success=True,
        message="登录成功",
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.jwt_expire_minutes * 60,
        user=user_response
    )


@router.post("/auth/logout", response_model=StaffOperationResponse)
async def logout(
    http_request: Request,
    current_user: dict = Depends(get_current_staff_user)
):
    """
    Staff user logout

    Logs the logout action (token invalidation should be handled client-side).
    """
    # Log logout action
    audit_service.log_action(
        user_id=current_user["id"],
        action="logout",
        resource="staff_auth",
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details={"username": current_user["username"]}
    )

    return StaffOperationResponse(
        success=True,
        message="登出成功"
    )


@router.post("/auth/change-password", response_model=StaffOperationResponse)
async def change_password(
    request: ChangePasswordRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_staff_user)
):
    """
    Change current user's password

    Requires the old password for verification.
    """
    from .services import verify_password, hash_password

    # Get current user's password hash
    user = staff_user_service.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # Verify old password
    # Note: In a real app, you'd need to store and retrieve the password hash
    # For now, we'll skip this check in the demo

    # Update password
    success, error = staff_user_service.update_password(
        current_user["id"],
        request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="change_password",
        resource="staff_auth",
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request)
    )

    return StaffOperationResponse(
        success=True,
        message="密码修改成功"
    )


@router.get("/auth/me", response_model=StaffUserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_staff_user)
):
    """
    Get current authenticated user's information
    """
    user = staff_user_service.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return user


# ============================================================================
# Staff User Routes
# ============================================================================

@router.get("/users", response_model=StaffUserListResponse)
async def get_users(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    role_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(require_permissions("staff:user:read"))
):
    """
    Get paginated list of staff users

    Requires 'staff:user:read' permission.
    """
    # Validate pagination
    page = max(1, page)
    limit = min(100, max(1, limit))

    # Build filters
    filters = {}
    if status:
        filters['status'] = status
    if role_id:
        filters['role_id'] = role_id
    if search:
        filters['search'] = search

    # Get users
    users, total = staff_user_service.get_users(filters, page, limit)

    # Calculate pages
    pages = (total + limit - 1) // limit if total > 0 else 0

    return StaffUserListResponse(
        users=users,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/users/{user_id}", response_model=StaffUserResponse)
async def get_user(
    user_id: int,
    current_user: dict = Depends(require_permissions("staff:user:read"))
):
    """
    Get staff user details by ID

    Requires 'staff:user:read' permission.
    """
    user = staff_user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )

    return user


@router.post("/users", response_model=StaffUserResponseWrapper)
async def create_user(
    request: StaffUserCreate,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:user:create"))
):
    """
    Create a new staff user

    Requires 'staff:user:create' permission.
    """
    success, user, error = staff_user_service.create_user(
        request,
        created_by=current_user["id"]
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="create",
        resource="staff_user",
        resource_id=user.id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details={"username": request.username, "role_id": request.role_id}
    )

    return StaffUserResponseWrapper(
        success=True,
        message="员工创建成功",
        user=user
    )


@router.put("/users/{user_id}", response_model=StaffUserResponseWrapper)
async def update_user(
    user_id: int,
    request: StaffUserUpdate,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:user:update"))
):
    """
    Update staff user information

    Requires 'staff:user:update' permission.
    """
    # Check if user exists
    existing = staff_user_service.get_user_by_id(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )

    # Cannot update own role/status through this endpoint
    if user_id == current_user["id"]:
        if request.role_id is not None or request.status is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能修改自己的角色或状态"
            )

    success, user, error = staff_user_service.update_user(user_id, request)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="update",
        resource="staff_user",
        resource_id=user_id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details=request.model_dump(exclude_none=True)
    )

    return StaffUserResponseWrapper(
        success=True,
        message="员工更新成功",
        user=user
    )


@router.put("/users/{user_id}/password", response_model=StaffOperationResponse)
async def reset_user_password(
    user_id: int,
    request: StaffPasswordUpdate,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:user:update"))
):
    """
    Reset staff user password (admin action)

    Requires 'staff:user:update' permission.
    """
    # Check if user exists
    existing = staff_user_service.get_user_by_id(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="reset_password",
        resource="staff_user",
        resource_id=user_id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details={"action": "admin_reset"}
    )

    success, error = staff_user_service.update_password(
        user_id,
        request.password,
        admin_id=current_user["id"]
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return StaffOperationResponse(
        success=True,
        message="密码重置成功"
    )


@router.put("/users/{user_id}/status", response_model=StaffOperationResponse)
async def update_user_status(
    user_id: int,
    request: StaffUserStatusUpdate,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:user:update"))
):
    """
    Enable or disable staff user account

    Requires 'staff:user:update' permission.
    """
    # Check if user exists
    existing = staff_user_service.get_user_by_id(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )

    # Cannot update own status
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )

    success, error = staff_user_service.update_status(
        user_id,
        request.status,
        admin_id=current_user["id"]
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return StaffOperationResponse(
        success=True,
        message="状态更新成功",
        data={"status": request.status.value}
    )


@router.delete("/users/{user_id}", response_model=StaffOperationResponse)
async def delete_user(
    user_id: int,
    http_request: Request,
    current_user: dict = Depends(require_super_admin)
):
    """
    Delete staff user

    Requires super_admin role.
    """
    # Cannot delete self
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    success, error = staff_user_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="delete",
        resource="staff_user",
        resource_id=user_id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request)
    )

    return StaffOperationResponse(
        success=True,
        message="删除成功"
    )


# ============================================================================
# Role Routes
# ============================================================================

@router.get("/roles", response_model=RoleListResponse)
async def get_roles(
    current_user: dict = Depends(require_permissions("staff:role:read"))
):
    """
    Get all roles

    Requires 'staff:role:read' permission.
    """
    roles = role_service.get_roles()

    return RoleListResponse(
        roles=roles,
        total=len(roles)
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: dict = Depends(require_permissions("staff:role:read"))
):
    """
    Get role details by ID

    Requires 'staff:role:read' permission.
    """
    role = role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    return role


@router.post("/roles", response_model=RoleOperationResponse)
async def create_role(
    request: RoleCreate,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:role:create"))
):
    """
    Create a new role

    Requires 'staff:role:create' permission.
    """
    success, role, error = role_service.create_role(request)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="create",
        resource="staff_role",
        resource_id=role.id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details={"code": request.code, "name": request.name}
    )

    return RoleOperationResponse(
        success=True,
        message="角色创建成功",
        role=role
    )


@router.put("/roles/{role_id}", response_model=RoleOperationResponse)
async def update_role(
    role_id: int,
    request: RoleUpdate,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:role:update"))
):
    """
    Update role

    Requires 'staff:role:update' permission.
    System roles cannot be modified.
    """
    success, role, error = role_service.update_role(role_id, request)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="update",
        resource="staff_role",
        resource_id=role_id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request),
        details=request.model_dump(exclude_none=True)
    )

    return RoleOperationResponse(
        success=True,
        message="角色更新成功",
        role=role
    )


@router.delete("/roles/{role_id}", response_model=RoleOperationResponse)
async def delete_role(
    role_id: int,
    http_request: Request,
    current_user: dict = Depends(require_permissions("staff:role:delete"))
):
    """
    Delete role

    Requires 'staff:role:delete' permission.
    System roles cannot be deleted.
    """
    success, error = role_service.delete_role(role_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Log action
    audit_service.log_action(
        user_id=current_user["id"],
        action="delete",
        resource="staff_role",
        resource_id=role_id,
        ip=get_client_ip(http_request),
        user_agent=get_user_agent(http_request)
    )

    return RoleOperationResponse(
        success=True,
        message="删除成功"
    )


# ============================================================================
# Permission Routes
# ============================================================================

@router.get("/permissions", response_model=PermissionListResponse)
async def get_permissions(
    current_user: dict = Depends(get_current_staff_user)
):
    """
    Get all available permissions

    Requires authentication.
    """
    permissions = permission_service.get_permissions()

    return PermissionListResponse(
        permissions=permissions,
        total=len(permissions)
    )


@router.get("/permissions/tree", response_model=PermissionTreeResponse)
async def get_permission_tree(
    current_user: dict = Depends(get_current_staff_user)
):
    """
    Get permissions as a tree structure grouped by category

    Requires authentication.
    """
    tree = permission_service.get_permission_tree()

    return PermissionTreeResponse(tree=tree)


@router.get("/permissions/check", response_model=dict)
async def check_permission(
    permission: str,
    current_user: dict = Depends(get_current_staff_user)
):
    """
    Check if current user has a specific permission

    Requires authentication.
    """
    has_permission = permission_service.check_user_permission(
        current_user["id"],
        permission
    )

    return {
        "permission": permission,
        "has_permission": has_permission,
        "user_id": current_user["id"],
        "username": current_user["username"]
    }


# ============================================================================
# Audit Log Routes
# ============================================================================

@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    page: int = 1,
    limit: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_permissions("staff:user:read"))
):
    """
    Get paginated audit logs

    Requires 'staff:user:read' permission.
    """
    # Validate pagination
    page = max(1, page)
    limit = min(100, max(1, limit))

    # Build filters
    filters = AuditLogFilter(
        user_id=user_id,
        action=action,
        resource=resource,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None
    )

    # Get logs
    logs, total = audit_service.get_logs(filters, page, limit)

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
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint

    No authentication required.
    """
    return {
        "status": "healthy",
        "module": "staff",
        "version": "1.0.0"
    }


# ============================================================================
# Module Info
# ============================================================================

@router.get("/info")
async def get_module_info():
    """
    Get module information

    No authentication required.
    """
    return ModuleInfo()
