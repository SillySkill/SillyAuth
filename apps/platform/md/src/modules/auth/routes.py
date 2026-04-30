"""
Auth Module Routes
FastAPI routes for authentication endpoints

Provides login, register, refresh, profile management, and logout endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Any
from jose import jwt, JWTError
import logging

from .schemas import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    UserResponse,
    Token,
    AuthResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
)
from .services import auth_service, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from core.db_adapter import get_db_cursor

logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

# HTTP Bearer security scheme
security = HTTPBearer()


# ============================================================================
# Helper Functions
# ============================================================================

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
# Authentication Routes
# ============================================================================

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(credentials: LoginRequest):
    """
    User login

    Validates email and password, returns access and refresh tokens
    """
    result = auth_service.login(credentials.email, credentials.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    return result


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    User registration

    Creates new user account and returns JWT tokens
    """
    # Check if email exists
    existing_email = auth_service.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # Check if username exists
    existing_username = auth_service.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )

    # Create user
    new_user = auth_service.register(user_data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户创建失败"
        )

    # Create token data
    token_data = {
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role or "user"
    }

    # Generate tokens
    access_token = auth_service.create_access_token(token_data)
    refresh_token = auth_service.create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=new_user
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Token refresh

    Uses refresh token to get new access token
    """
    result = auth_service.refresh_token(request.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期"
        )

    return result


@router.post("/logout", response_model=AuthResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout

    Client should delete stored tokens. Server-side token blacklist
    can be implemented for enhanced security.
    """
    # JWT is stateless, logout is primarily handled on client
    # Optional: Implement token blacklist for enhanced security

    logger.info(f"User {current_user.get('email')} logged out")

    return AuthResponse(
        success=True,
        message="登出成功"
    )


# ============================================================================
# User Profile Routes
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile

    Returns authenticated user's profile information
    """
    return UserResponse(
        id=current_user['id'],
        username=current_user['username'],
        email=current_user['email'],
        first_name=current_user.get('first_name'),
        last_name=current_user.get('last_name'),
        created_at=current_user.get('created_at'),
        role=current_user.get('role', 'user'),
        avatar_url=current_user.get('avatar_url'),
        is_verified=current_user.get('is_verified', False),
        is_active=current_user.get('is_active', True)
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user profile

    Updates authenticated user's profile information
    """
    # Convert Pydantic model to dict, excluding None values
    update_dict = {
        k: v for k, v in update_data.model_dump().items()
        if v is not None
    }

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供更新数据"
        )

    updated_user = auth_service.update_user(current_user['id'], update_dict)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )

    return updated_user


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password

    Updates authenticated user's password
    """
    # Verify old password
    password_hash = auth_service.hash_password(request.old_password)
    if current_user.get('password_hash') != password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码不正确"
        )

    # Hash new password
    new_password_hash = auth_service.hash_password(request.new_password)

    # Update password
    with get_db_cursor() as cur:
        cur.execute(
            "UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_password_hash, current_user['id'])
        )

    logger.info(f"User {current_user['email']} changed password")

    return AuthResponse(
        success=True,
        message="密码修改成功"
    )


# ============================================================================
# Password Management Routes
# ============================================================================

@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Forgot password

    Sends password reset email with secure reset token
    """
    user = auth_service.get_user_by_email(request.email)

    if not user:
        # For security, don't reveal if email exists
        logger.warning(f"Password reset attempt for non-existent email: {request.email}")
        return AuthResponse(
            success=True,
            message="如果该邮箱存在，重置链接已发送"
        )

    # Generate reset token
    reset_token = auth_service.generate_reset_token()
    expires_at = datetime.now() + timedelta(hours=1)

    # Save reset token to database
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO password_reset_tokens (user_id, token, expires_at, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (user['id'], reset_token, expires_at))

    # TODO: Integrate email service to send reset link
    # reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
    # send_email(user.email, "Reset Your Password", reset_link)

    # Development: Log the token
    logger.info(f"Password reset token generated for {user['email']}: {reset_token}")

    return AuthResponse(
        success=True,
        message="如果该邮箱存在，重置链接已发送到您的邮箱，链接 1 小时内有效"
    )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password

    Sets new password using reset token
    """
    from datetime import datetime, timedelta

    # Verify reset token
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, user_id, expires_at
            FROM password_reset_tokens
            WHERE token = %s
              AND used_at IS NULL
              AND expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC
            LIMIT 1
        """, (request.token,))
        token_record = cur.fetchone()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置链接无效或已过期"
        )

    token_id, user_id, expires_at = token_record['id'], token_record['user_id'], token_record['expires_at']

    # Get user
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # Hash new password
    new_password_hash = auth_service.hash_password(request.new_password)

    with get_db_cursor() as cur:
        # Update password
        cur.execute(
            "UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_password_hash, user_id)
        )

        # Mark token as used
        cur.execute(
            "UPDATE password_reset_tokens SET used_at = CURRENT_TIMESTAMP WHERE id = %s",
            (token_id,)
        )

    logger.info(f"User {user['email']} reset password successfully")

    return AuthResponse(
        success=True,
        message="密码重置成功，请使用新密码登录"
    )


# ============================================================================
# Email Verification Routes
# ============================================================================

@router.post("/verify-email/{token}", response_model=AuthResponse)
async def verify_email(token: str):
    """
    Verify email

    Verifies user email using verification token
    """
    from datetime import datetime, timedelta

    # Find verification record
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, user_id, email, expires_at
            FROM email_verifications
            WHERE token = %s
              AND verified_at IS NULL
              AND expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC
            LIMIT 1
        """, (token,))
        verification = cur.fetchone()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证链接无效或已过期"
        )

    verification_id, user_id, email = verification['id'], verification['user_id'], verification['email']

    with get_db_cursor() as cur:
        # Mark as verified
        cur.execute(
            "UPDATE email_verifications SET verified_at = CURRENT_TIMESTAMP WHERE id = %s",
            (verification_id,)
        )

        # Update user verification status
        cur.execute(
            "UPDATE users SET is_verified = TRUE WHERE id = %s",
            (user_id,)
        )

    logger.info(f"User {email} verified email successfully")

    return AuthResponse(
        success=True,
        message="邮箱验证成功"
    )


# ============================================================================
# Import required for forgot-password route
# ============================================================================
from datetime import datetime, timedelta
