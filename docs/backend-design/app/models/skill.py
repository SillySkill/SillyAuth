# ============================================
# SillyMD Backend - Skill Model
# ============================================

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Integer, Enum as SQLEnum, Numeric, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class SkillCategory(str, enum.Enum):
    """Skill category enum"""
    TECH = "tech"
    PRODUCT = "product"
    DESIGN = "design"
    MARKETING = "marketing"
    OPS = "ops"


class SkillType(str, enum.Enum):
    """Skill type enum"""
    FREE = "free"
    COMMERCIAL = "commercial"


class SkillStatus(str, enum.Enum):
    """Skill status enum"""
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class Skill(Base):
    """Skill model"""
    __tablename__ = "skills"

    id = Column(BigInteger, primary_key=True, index=True)
    skill_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Author
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Classification
    category = Column(SQLEnum(SkillCategory), nullable=False)
    type = Column(SQLEnum(SkillType), default=SkillType.FREE, nullable=False)
    version = Column(String(20), default="1.0.0")
    status = Column(SQLEnum(SkillStatus), default=SkillStatus.DRAFT, nullable=False)

    # Flags
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    # Publishing
    published_at = Column(DateTime(timezone=True))
    repo_url = Column(String(500))

    # Dependencies
    dependencies = Column(JSON)

    # Digital Signature (for commercial skills)
    content_hash = Column(String(64))
    platform_signature = Column(String(255))
    author_signature = Column(String(255))

    # Commercial (for paid skills)
    price = Column(Integer, default=0)
    license_types = Column(JSON)
    original_price = Column(Integer, default=0)
    promo_until = Column(DateTime(timezone=True))

    # Statistics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    rating_avg = Column(Numeric(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    author = relationship("User", backref="skills")
    versions = relationship("SkillVersion", back_populates="skill", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="skill_tags", backref="skills")

    def __repr__(self):
        return f"<Skill(id={self.id}, skill_id={self.skill_id}, name={self.name})>"


class SkillVersion(Base):
    """Skill version model"""
    __tablename__ = "skill_versions"

    id = Column(BigInteger, primary_key=True, index=True)
    skill_id = Column(BigInteger, ForeignKey("skills.id"), nullable=False)
    version = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    commit_message = Column(String(500))
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    skill = relationship("Skill", back_populates="versions")

    def __repr__(self):
        return f"<SkillVersion(id={self.id}, skill_id={self.skill_id}, version={self.version})>"


class Tag(Base):
    """Tag model"""
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


from sqlalchemy import Table
skill_tags = Table(
    "skill_tags",
    Base.metadata,
    Column("skill_id", BigInteger, ForeignKey("skills.id"), primary_key=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)
