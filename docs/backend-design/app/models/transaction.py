# ============================================
# SillyMD Backend - Transaction Models
# ============================================

from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Text, Boolean, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class TransactionType(str, enum.Enum):
    """Transaction type enum"""
    RECHARGE = "recharge"       # 充值
    PURCHASE = "purchase"       # 购买 Skills
    EARNING = "earning"         # 收益（出售 Skills）
    REFUND = "refund"           # 退款
    WITHDRAW = "withdraw"       # 提现


class LicenseType(str, enum.Enum):
    """License type enum"""
    PERSONAL = "personal"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class TransactionStatus(str, enum.Enum):
    """Transaction status enum"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PointTransaction(Base):
    """Points transaction model"""
    __tablename__ = "point_transactions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # 可为负数（支出）
    type = Column(SQLEnum(TransactionType), nullable=False)
    balance_after = Column(Integer, nullable=False)
    related_id = Column(BigInteger)  # 关联的订单/许可证 ID
    description = Column(String(500))
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.COMPLETED)
    metadata = Column(Text)  # JSON 字符串
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="transactions")

    def __repr__(self):
        return f"<PointTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount})>"


class License(Base):
    """License model for commercial skills"""
    __tablename__ = "licenses"

    id = Column(BigInteger, primary_key=True, index=True)
    license_id = Column(String(50), unique=True, nullable=False, index=True)
    license_key = Column(String(100), unique=True, nullable=False)
    skill_id = Column(BigInteger, ForeignKey("skills.id"), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    license_type = Column(SQLEnum(LicenseType), nullable=False)
    price = Column(Integer, nullable=False)  # 积分
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    skill = relationship("Skill", backref="licenses")
    buyer = relationship("User", foreign_keys=[buyer_id], backref="purchased_licenses")
    vendor = relationship("User", foreign_keys=[vendor_id], backref="sold_licenses")

    def __repr__(self):
        return f"<License(id={self.id}, license_id={self.license_id}, type={self.license_type})>"


class WithdrawalRequest(Base):
    """Withdrawal request model"""
    __tablename__ = "withdrawal_requests"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    points_amount = Column(Integer, nullable=False)  # 扣除的积分数
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    rejection_reason = Column(Text)
    processed_at = Column(DateTime(timezone=True))
    processed_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="withdrawals")
    processor = relationship("User", foreign_keys=[processed_by])

    def __repr__(self):
        return f"<WithdrawalRequest(id={self.id}, user_id={self.user_id}, amount={self.amount})>"
