"""
统一用户模型
====================================

版本: v1.0
创建日期: 2026-02-12
说明: 统一用户表，支持百变秀和一块变两种场景
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """用户基础信息"""
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    status: int = 1  # 0=禁用, 1=正常


class User(UserBase):
    """完整用户信息"""
    id: int
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    status: int
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        """用户配置（可选）"""
        scene_type: str  # 'activity' | 'personal'


class UserRegister(BaseModel):
    """用户注册/登录"""
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录"""
    code: str
    encrypted_data: str  # 加密数据


class UserProfile(BaseModel):
    """用户资料"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None


class UserBalance(BaseModel):
    """用户余额"""
    growth_points: int
    image_points: int
    video_points: int
    total_recharged: float
    total_discount: float