# ============================================
# SillyMD Backend - User Schemas
# ============================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, VendorLevel


class UserBase(BaseModel):
    """User base schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """User create schema"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema"""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInDB(UserBase):
    """User in database schema"""
    id: int
    role: UserRole
    vendor_level: VendorLevel
    ai_points: int
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User response schema"""
    pass


class Token(BaseModel):
    """Token schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: int  # user_id
    exp: int
    type: str = "access"


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str
