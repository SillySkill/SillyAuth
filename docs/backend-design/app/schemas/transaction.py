# ============================================
# SillyMD Backend - Transaction Schemas
# ============================================

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, LicenseType, TransactionStatus


class PointTransactionCreate(BaseModel):
    """Create points transaction"""
    amount: int = Field(..., ge=-100000, le=100000)
    type: TransactionType
    description: Optional[str] = None


class PointTransactionResponse(BaseModel):
    """Points transaction response"""
    id: int
    user_id: int
    amount: int
    type: TransactionType
    balance_after: int
    description: Optional[str]
    status: TransactionStatus
    created_at: datetime

    class Config:
        from_attributes = True


class LicenseCreate(BaseModel):
    """Create license purchase"""
    skill_id: int
    license_type: LicenseType


class LicenseResponse(BaseModel):
    """License response"""
    id: int
    license_id: str
    license_key: str
    skill_id: int
    buyer_id: int
    vendor_id: int
    license_type: LicenseType
    price: int
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WithdrawalRequestCreate(BaseModel):
    """Create withdrawal request"""
    amount: int = Field(..., ge=500, description="Minimum withdrawal is 500 CNY")

    @validator('amount')
    def validate_amount(cls, v):
        if v % 100 != 0:
            raise ValueError('Amount must be a multiple of 100')
        return v


class WithdrawalRequestResponse(BaseModel):
    """Withdrawal request response"""
    id: int
    user_id: int
    amount: int
    points_amount: int
    status: TransactionStatus
    rejection_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WalletResponse(BaseModel):
    """User wallet response"""
    user_id: int
    balance: int
    total_earned: int
    total_spent: int
    pending_withdrawals: int
