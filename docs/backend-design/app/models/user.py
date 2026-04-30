# ============================================
# SillyMD Backend - User Model
# ============================================

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Integer, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class UserRole(str, enum.Enum):
    """User role enum"""
    USER = "user"
    VENDOR = "vendor"
    ADMIN = "admin"


class VendorLevel(str, enum.Enum):
    """Vendor level enum"""
    NORMAL = "normal"
    PREMIUM = "premium"
    GOLD = "gold"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Role & Level
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    vendor_level = Column(SQLEnum(VendorLevel), default=VendorLevel.NORMAL)

    # Points
    ai_points = Column(Integer, default=0, nullable=False)

    # Profile
    avatar_url = Column(String(500))
    bio = Column(Text)

    # Timestamps
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
