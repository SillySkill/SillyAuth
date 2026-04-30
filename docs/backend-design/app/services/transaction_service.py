# ============================================
# SillyMD Backend - Transaction Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import string

from app.models.user import User
from app.models.transaction import (
    PointTransaction,
    License,
    WithdrawalRequest,
    TransactionType,
    TransactionStatus,
    LicenseType
)
from app.schemas.transaction import (
    PointTransactionCreate,
    LicenseCreate,
    WithdrawalRequestCreate
)
from app.core.config import settings


class TransactionService:
    """Transaction and wallet service"""

    async def get_user_balance(self, db: AsyncSession, user_id: int) -> int:
        """Get user's current balance"""
        # Get latest transaction balance
        result = await db.execute(
            select(PointTransaction)
            .where(PointTransaction.user_id == user_id)
            .where(PointTransaction.status == TransactionStatus.COMPLETED)
            .order_by(PointTransaction.id.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if latest:
            return latest.balance_after

        # Return AI points from user table
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        return user.ai_points if user else 0

    async def create_transaction(
        self,
        db: AsyncSession,
        user_id: int,
        amount: int,
        trans_type: TransactionType,
        description: str = None,
        related_id: int = None
    ) -> PointTransaction:
        """Create a new points transaction"""
        # Get current balance
        current_balance = await self.get_user_balance(db, user_id)

        # Check if sufficient balance
        if amount < 0 and current_balance < -amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )

        # Create transaction
        transaction = PointTransaction(
            user_id=user_id,
            amount=amount,
            type=trans_type,
            balance_after=current_balance + amount,
            description=description,
            related_id=related_id,
            status=TransactionStatus.COMPLETED
        )

        db.add(transaction)

        # Update user's AI points
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(ai_points=current_balance + amount)
        )

        await db.commit()
        await db.refresh(transaction)

        return transaction

    async def purchase_license(
        self,
        db: AsyncSession,
        user: User,
        license_in: LicenseCreate
    ) -> License:
        """Purchase commercial skill license"""
        from app.models.skill import Skill

        # Get skill
        result = await db.execute(
            select(Skill).where(Skill.id == license_in.skill_id)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found"
            )

        if skill.type != "commercial":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This is not a commercial skill"
            )

        # Calculate price based on license type
        price = self._calculate_price(skill, license_in.license_type)

        # Create license transaction (deduct points)
        await self.create_transaction(
            db,
            user.id,
            -price,
            TransactionType.PURCHASE,
            f"Purchased {skill.name} ({license_in.license_type} license)"
        )

        # Create license
        license_id = self._generate_license_id()
        license_key = self._generate_license_key()

        license = License(
            license_id=license_id,
            license_key=license_key,
            skill_id=skill.id,
            buyer_id=user.id,
            vendor_id=skill.author_id,
            license_type=license_in.license_type,
            price=price,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year validity
        )

        db.add(license)

        # Add earning to vendor
        platform_fee = int(price * settings.PLATFORM_FEE_RATE)
        vendor_earning = price - platform_fee

        await self.create_transaction(
            db,
            skill.author_id,
            vendor_earning,
            TransactionType.EARNING,
            f"Sold {skill.name} ({license_in.license_type} license) to {user.username}",
            related_id=license.id
        )

        # Update skill stats
        skill.download_count += 1
        await db.commit()
        await db.refresh(license)

        return license

    async def request_withdrawal(
        self,
        db: AsyncSession,
        user: User,
        amount: int
    ) -> WithdrawalRequest:
        """Request withdrawal"""
        # Check balance
        balance = await self.get_user_balance(db, user.id)

        # Convert CNY to points
        points_needed = int(amount * 100 / settings.POINTS_EXCHANGE_RATE)

        if balance < points_needed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Need {points_needed} points, have {balance}"
            )

        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            user_id=user.id,
            amount=amount,
            points_amount=points_needed,
            status=TransactionStatus.PENDING
        )

        db.add(withdrawal)

        # Hold the points
        await self.create_transaction(
            db,
            user.id,
            -points_needed,
            TransactionType.WITHDRAW,
            f"Withdrawal request: {amount} CNY",
            related_id=withdrawal.id
        )

        await db.commit()
        await db.refresh(withdrawal)

        return withdrawal

    async def approve_withdrawal(
        self,
        db: AsyncSession,
        withdrawal_id: int,
        admin_id: int
    ) -> WithdrawalRequest:
        """Approve withdrawal request"""
        result = await db.execute(
            select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id)
        )
        withdrawal = result.scalar_one_or_none()

        if not withdrawal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal request not found"
            )

        if withdrawal.status != TransactionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Withdrawal request already processed"
            )

        withdrawal.status = TransactionStatus.COMPLETED
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.processed_by = admin_id

        await db.commit()
        await db.refresh(withdrawal)

        return withdrawal

    async def reject_withdrawal(
        self,
        db: AsyncSession,
        withdrawal_id: int,
        admin_id: int,
        reason: str
    ) -> WithdrawalRequest:
        """Reject withdrawal request and refund points"""
        result = await db.execute(
            select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id)
        )
        withdrawal = result.scalar_one_or_none()

        if not withdrawal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal request not found"
            )

        if withdrawal.status != TransactionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Withdrawal request already processed"
            )

        # Refund points
        await self.create_transaction(
            db,
            withdrawal.user_id,
            withdrawal.points_amount,
            TransactionType.REFUND,
            f"Withdrawal rejected: {reason}"
        )

        withdrawal.status = TransactionStatus.CANCELLED
        withdrawal.rejection_reason = reason
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.processed_by = admin_id

        await db.commit()
        await db.refresh(withdrawal)

        return withdrawal

    async def get_user_licenses(
        self,
        db: AsyncSession,
        user_id: int,
        include_expired: bool = False
    ) -> List[License]:
        """Get user's purchased licenses"""
        query = select(License).where(License.buyer_id == user_id)

        if not include_expired:
            query = query.where(
                (License.expires_at > datetime.utcnow()) |
                (License.expires_at.is_(None))
            )

        result = await db.execute(query.order_by(License.created_at.desc()))
        return result.scalars().all()

    async def get_wallet_summary(
        self,
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """Get wallet summary"""
        # Get balance
        balance = await self.get_user_balance(db, user_id)

        # Get total earned
        result = await db.execute(
            select(func.coalesce(func.sum(PointTransaction.amount), 0))
            .where(PointTransaction.user_id == user_id)
            .where(PointTransaction.type == TransactionType.EARNING)
        )
        total_earned = result.scalar() or 0

        # Get total spent
        result = await db.execute(
            select(func.coalesce(func.sum(PointTransaction.amount), 0))
            .where(PointTransaction.user_id == user_id)
            .where(PointTransaction.type == TransactionType.PURCHASE)
        )
        total_spent = abs(result.scalar() or 0)

        # Get pending withdrawals
        result = await db.execute(
            select(func.count())
            .where(WithdrawalRequest.user_id == user_id)
            .where(WithdrawalRequest.status == TransactionStatus.PENDING)
        )
        pending_withdrawals = result.scalar() or 0

        return {
            "user_id": user_id,
            "balance": balance,
            "total_earned": total_earned,
            "total_spent": total_spent,
            "pending_withdrawals": pending_withdrawals
        }

    def _calculate_price(self, skill: 'Skill', license_type: LicenseType) -> int:
        """Calculate price based on license type"""
        base_price = skill.price or 0

        multipliers = {
            LicenseType.PERSONAL: 1.0,
            LicenseType.TEAM: 3.0,
            LicenseType.ENTERPRISE: 10.0
        }

        return int(base_price * multipliers.get(license_type, 1.0))

    def _generate_license_id(self) -> str:
        """Generate unique license ID"""
        return f"LIC-{secrets.token_hex(8).upper()}"

    def _generate_license_key(self) -> str:
        """Generate license key"""
        # Format: XXXX-XXXX-XXXX-XXXX
        chars = string.ascii_uppercase + string.digits
        groups = [secrets.choice(string.ascii_uppercase) +
                  ''.join(secrets.choice(chars) for _ in range(3))
                  for _ in range(4)]
        return '-'.join(groups)


# Create service instance
transaction_service = TransactionService()
