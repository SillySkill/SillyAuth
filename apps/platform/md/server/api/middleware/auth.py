"""
认证和授权中间件
Authentication and Authorization Middleware

实现完整的 JWT 认证和角色权限控制
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models.users import User
from ..config import settings


# ============================================
# Configuration
# ============================================

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24  # 30 天
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================
# Pydantic Models
# ============================================

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenData(BaseModel):
    user_id: int
    username: str
    email: str
    role: str = "user"


class UserAuth(BaseModel):
    user_id: int
    username: str
    email: str
    role: str = "user"
    permissions: list = []


# ============================================
# Authentication Functions
# ============================================

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前认证用户

    从 JWT Token 中解析用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 检查 token 类型
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("user_id")
        if not user_id:
            raise credentials_exception

        # 从数据库获取用户
        user = await db.get(User, user_id)
        if not user:
            raise credentials_exception

        # 检查用户是否活跃
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )

        return user

    except JWTError as e:
        raise credentials_exception
    except Exception as e:
        raise credentials_exception


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选认证）

    如果提供了有效 Token 则返回用户，否则返回 None
    """
    try:
        return await get_current_user(credentials, db)
    except:
        return None


async def require_role(*required_roles: str):
    """
    角色权限检查装饰器工厂

    用法:
        @router.get("/admin")
        @require_role("admin", "moderator")
        async def admin_endpoint(user: User = Depends(get_current_user)):
            ...
    """
    async def role_checker(
        user: User = Depends(get_current_user)
    ) -> User:
        """检查用户是否有所需角色"""
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无角色信息"
            )

        if user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(required_roles)}"
            )

        return user

    return role_checker


def require_permission(permission: str):
    """
    权限检查装饰器工厂

    用法:
        @router.post("/content")
        @require_permission("content:write")
        async def create_content(user: User = Depends(get_current_user)):
            ...
    """
    async def permission_checker(
        user: User = Depends(get_current_user)
    ) -> User:
        """检查用户是否有特定权限"""
        # TODO: 实现细粒度权限系统
        # 这里简化处理：管理员拥有所有权限
        if user.role == "admin":
            return user

        # 其他角色需要检查具体权限
        # 这里可以扩展为查询数据库的权限表
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要权限: {permission}"
        )

    return permission_checker


# ============================================
# Admin Authentication
# ============================================

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前认证的管理员

    必须是管理员角色
    """
    user = await get_current_user(credentials, db)

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    return user


# ============================================
# Rate Limiting
# ============================================

from slowapi import Limiter, _rate_limit_exceeded
from fastapi import Request

# 限流器配置
limiter = Limiter(key=get_ipaddr)

# API 限流：每分钟 60 次
api_limiter = limiter.limit("60/minute")

# 支付 API 限流：每分钟 10 次
payment_limiter = limiter.limit("10/minute")

# 认证 API 限流：每分钟 5 次
auth_limiter = limiter.limit("5/minute")

# 提交内容限流：每小时 5 次
submission_limiter = limiter.limit("5/hour")


def get_client_ip(request: Request) -> str:
    """获取客户端 IP 地址"""
    # 检查代理头
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host


# ============================================
# 导出常用的依赖
# ============================================

__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "require_permission",
    "get_current_admin",
    "create_access_token",
    "create_refresh_token",
    "Token",
    "TokenData",
    "UserAuth",
    # Rate limiters
    "api_limiter",
    "payment_limiter",
    "auth_limiter",
    "submission_limiter",
    "get_client_ip"
]
