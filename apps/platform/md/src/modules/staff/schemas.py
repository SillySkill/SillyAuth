"""
Staff Module Schemas
Pydantic models for staff management API requests and responses

Provides schemas for:
- Staff user management
- Role management
- Permission management
- Audit logging
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class StaffStatus(str, Enum):
    """Staff account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

    def __str__(self):
        return self.value


class AuditAction(str, Enum):
    """Audit log action types"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESET_PASSWORD = "reset_password"
    CHANGE_STATUS = "change_status"


# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Staff login request"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class LoginResponse(BaseModel):
    """Staff login response"""
    success: bool = Field(..., description="登录是否成功")
    message: str = Field(..., description="响应消息")
    access_token: Optional[str] = Field(None, description="JWT访问令牌")
    token_type: Optional[str] = Field(None, description="令牌类型")
    expires_in: Optional[int] = Field(None, description="过期时间(秒)")
    user: Optional["StaffUserResponse"] = Field(None, description="用户信息")


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=100, description="确认新密码")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class ResetPasswordRequest(BaseModel):
    """Reset password request (admin)"""
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


# ============================================================================
# Staff User Schemas
# ============================================================================

class StaffUserBase(BaseModel):
    """Base staff user schema"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    role_id: int = Field(..., description="角色ID")
    status: StaffStatus = Field(StaffStatus.ACTIVE, description="状态")


class StaffUserCreate(StaffUserBase):
    """Create staff user request"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class StaffUserUpdate(BaseModel):
    """Update staff user request"""
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    role_id: Optional[int] = Field(None, description="角色ID")
    status: Optional[StaffStatus] = Field(None, description="状态")


class StaffUserResponse(BaseModel):
    """Staff user response"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    role_id: int = Field(..., description="角色ID")
    role_name: Optional[str] = Field(None, description="角色名称")
    status: str = Field(..., description="状态")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    created_by: Optional[int] = Field(None, description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class StaffUserListResponse(BaseModel):
    """Paginated staff user list response"""
    users: List[StaffUserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    limit: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class StaffUserStatusUpdate(BaseModel):
    """Update staff user status request"""
    status: StaffStatus = Field(..., description="新状态")


class StaffPasswordUpdate(BaseModel):
    """Update staff password request (admin)"""
    password: str = Field(..., min_length=6, max_length=100, description="新密码")


class StaffUserResponseWrapper(BaseModel):
    """Wrapper for single staff user response"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    user: Optional[StaffUserResponse] = Field(None, description="用户信息")


class StaffOperationResponse(BaseModel):
    """Generic staff operation response"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据")


# ============================================================================
# Role Schemas
# ============================================================================

class RoleBase(BaseModel):
    """Base role schema"""
    code: str = Field(..., min_length=2, max_length=50, description="角色代码")
    name: str = Field(..., min_length=2, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, max_length=500, description="角色描述")
    permissions: List[str] = Field(default_factory=list, description="权限列表")


class RoleCreate(RoleBase):
    """Create role request"""
    is_system: bool = Field(False, description="是否为系统角色")


class RoleUpdate(BaseModel):
    """Update role request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, max_length=500, description="角色描述")
    permissions: Optional[List[str]] = Field(None, description="权限列表")


class RoleResponse(BaseModel):
    """Role response"""
    id: int = Field(..., description="角色ID")
    code: str = Field(..., description="角色代码")
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    is_system: bool = Field(..., description="是否为系统角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Paginated role list response"""
    roles: List[RoleResponse] = Field(..., description="角色列表")
    total: int = Field(..., description="总数")


class RoleOperationResponse(BaseModel):
    """Generic role operation response"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    role: Optional[RoleResponse] = Field(None, description="角色信息")


# ============================================================================
# Permission Schemas
# ============================================================================

class PermissionCategory(str, Enum):
    """Permission categories"""
    ORDERS = "orders"
    GOODS = "goods"
    PROMOTION = "promotion"
    LOGISTICS = "logistics"
    STAFF = "staff"
    STORAGE = "storage"
    POINTS = "points"
    FINANCE = "finance"


class PermissionResponse(BaseModel):
    """Permission response"""
    id: int = Field(..., description="权限ID")
    code: str = Field(..., description="权限代码")
    name: str = Field(..., description="权限名称")
    category: str = Field(..., description="权限分类")
    description: Optional[str] = Field(None, description="权限描述")

    class Config:
        from_attributes = True


class PermissionTreeNode(BaseModel):
    """Permission tree node"""
    key: str = Field(..., description="权限代码")
    label: str = Field(..., description="权限名称")
    category: str = Field(..., description="权限分类")
    description: Optional[str] = Field(None, description="权限描述")
    children: List["PermissionTreeNode"] = Field(default_factory=list, description="子权限")

    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """Permission list response"""
    permissions: List[PermissionResponse] = Field(..., description="权限列表")
    total: int = Field(..., description="总数")


class PermissionTreeResponse(BaseModel):
    """Permission tree response"""
    tree: List[PermissionTreeNode] = Field(..., description="权限树")


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogEntry(BaseModel):
    """Audit log entry"""
    id: int = Field(..., description="日志ID")
    user_id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    action: str = Field(..., description="操作类型")
    resource: str = Field(..., description="资源类型")
    resource_id: Optional[int] = Field(None, description="资源ID")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    ip: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="User Agent")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Audit log filter parameters"""
    user_id: Optional[int] = Field(None, description="用户ID")
    action: Optional[str] = Field(None, description="操作类型")
    resource: Optional[str] = Field(None, description="资源类型")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")


class AuditLogResponse(BaseModel):
    """Audit log response"""
    logs: List[AuditLogEntry] = Field(..., description="日志列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    limit: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


# ============================================================================
# Role Assignment Schemas
# ============================================================================

class AssignRoleRequest(BaseModel):
    """Assign role to user request"""
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")


class AssignRoleResponse(BaseModel):
    """Assign role response"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")


# ============================================================================
# Module Info Schemas
# ============================================================================

class ModuleInfo(BaseModel):
    """Module information"""
    id: str = "staff"
    name: str = "员工权限管理模块"
    version: str = "1.0.0"
    description: str = "提供员工管理、角色管理和权限控制系统"
    dependencies: List[str] = ["auth"]


# Update forward references
LoginResponse.model_rebuild()
