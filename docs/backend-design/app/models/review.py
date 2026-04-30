# ============================================
# SillyMD Backend - Review Model
# ============================================

from sqlalchemy import Column, BigInteger, String, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Review(Base):
    """Review model"""
    __tablename__ = "reviews"

    id = Column(BigInteger, primary_key=True, index=True)
    skill_id = Column(BigInteger, ForeignKey("skills.id"), nullable=False)
    reviewer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Review details
    stage = Column(String(50), nullable=False)  # L1, L2, L3
    result = Column(String(50), nullable=False)  # approved, rejected, pending
    comments = Column(Text)

    # AI Review
    ai_model = Column(String(50))
    ai_confidence = Column(Numeric(3, 2))

    # Scores (JSON)
    scores = Column(Column("scores", JSON))  # {"format": 0.9, "safety": 0.85, "quality": 0.8}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    skill = relationship("Skill", backref="reviews")
    reviewer = relationship("User", backref="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, skill_id={self.skill_id}, result={self.result})>"
