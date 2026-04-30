# ============================================
# SillyMD Backend - Auth Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings
from typing import Optional


class AuthService:
    """Authentication service"""

    async def register(
        self,
        db: AsyncSession,
        user_in: UserCreate
    ) -> User:
        """Register new user"""
        # Check if username exists
        result = await db.execute(
            select(User).where(User.username == user_in.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email exists
        result = await db.execute(
            select(User).where(User.email == user_in.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            role="user",
            vendor_level="normal"
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    async def login(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Token:
        """Login user and return tokens"""
        user = await self.authenticate(db, username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # Update last login
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        await db.commit()

        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> Token:
        """Refresh access token"""
        from jose import jwt, JWTError

        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: int = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )


# Create service instance
auth_service = AuthService()
