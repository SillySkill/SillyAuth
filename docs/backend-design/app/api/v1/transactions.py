# ============================================
# SillyMD Backend - Transaction API
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db, get_current_user, get_current_admin
from app.schemas.transaction import (
    PointTransactionResponse,
    LicenseCreate,
    LicenseResponse,
    WithdrawalRequestCreate,
    WithdrawalRequestResponse,
    WalletResponse
)
from app.services.transaction_service import transaction_service
from app.models.user import User

router = APIRouter()


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user wallet information"""
    summary = await transaction_service.get_wallet_summary(db, current_user.id)
    return WalletResponse(**summary)


@router.get("/transactions", response_model=List[PointTransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's transaction history"""
    # Simplified for demo - in real app would query DB
    return []


@router.post("/licenses/purchase", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
async def purchase_license(
    license_in: LicenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Purchase commercial skill license"""
    license = await transaction_service.purchase_license(db, current_user, license_in)
    return license


@router.get("/licenses", response_model=List[LicenseResponse])
async def get_licenses(
    include_expired: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's purchased licenses"""
    licenses = await transaction_service.get_user_licenses(
        db,
        current_user.id,
        include_expired
    )
    return licenses


@router.post("/withdrawals", response_model=WithdrawalRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_withdrawal(
    withdrawal_in: WithdrawalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request withdrawal"""
    withdrawal = await transaction_service.request_withdrawal(
        db,
        current_user,
        withdrawal_in.amount
    )
    return withdrawal


@router.get("/withdrawals", response_model=List[WithdrawalRequestResponse])
async def get_withdrawals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's withdrawal requests"""
    # Simplified for demo
    return []


@router.put("/admin/withdrawals/{withdrawal_id}/approve", response_model=WithdrawalRequestResponse)
async def approve_withdrawal(
    withdrawal_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Approve withdrawal request (admin only)"""
    withdrawal = await transaction_service.approve_withdrawal(
        db,
        withdrawal_id,
        current_admin.id
    )
    return withdrawal


@router.put("/admin/withdrawals/{withdrawal_id}/reject", response_model=WithdrawalRequestResponse)
async def reject_withdrawal(
    withdrawal_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Reject withdrawal request (admin only)"""
    withdrawal = await transaction_service.reject_withdrawal(
        db,
        withdrawal_id,
        current_admin.id,
        reason
    )
    return withdrawal


@router.post("/recharge")
async def recharge_points(
    amount: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recharge points (demo endpoint)"""
    # In production, this would integrate with payment gateway
    transaction = await transaction_service.create_transaction(
        db,
        current_user.id,
        amount,
        "recharge",
        f"Recharged {amount} points"
    )
    return {"success": True, "transaction_id": transaction.id}
