"""
Vendor Module Services
开发者入驻模块服务层

提供开发者入驻、认证、等级管理的核心业务逻辑
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
import yaml
import os

from .schemas import (
    VendorApplicationCreate,
    VendorApplicationDetail,
    VendorProfile,
    VendorStats,
    ApplicationStatus,
    VendorTier,
)

logger = logging.getLogger(__name__)


class VendorService:
    """开发者服务类"""

    def __init__(self, db: AsyncSession, config_path: Optional[str] = None):
        """
        初始化开发者服务

        Args:
            db: 数据库会话
            config_path: 配置文件路径
        """
        self.db = db
        self._config = self._load_config(config_path)
        self._tiers = self._config.get("config", {}).get("tiers", [])

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            # 默认从模块目录加载
            config_path = os.path.join(
                os.path.dirname(__file__),
                "config.yaml"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load vendor config: {e}")
            return {
                "config": {
                    "tiers": [
                        {"id": "basic", "name": "基础开发者", "commission_rate": 0.7, "features": ["skills_basic", "skills_publish"]},
                        {"id": "standard", "name": "标准开发者", "commission_rate": 0.8, "features": ["skills_basic", "skills_publish", "analytics", "api_access"]},
                        {"id": "premium", "name": "高级开发者", "commission_rate": 0.85, "features": ["all"]},
                    ]
                }
            }

    def get_tier_config(self, tier_id: str) -> Optional[Dict[str, Any]]:
        """获取等级配置"""
        for tier in self._tiers:
            if tier["id"] == tier_id:
                return tier
        return None

    def get_all_tiers(self) -> List[Dict[str, Any]]:
        """获取所有等级配置"""
        return self._tiers

    async def submit_application(
        self,
        user_id: int,
        data: VendorApplicationCreate
    ) -> VendorApplicationDetail:
        """
        提交开发者入驻申请

        Args:
            user_id: 用户ID
            data: 申请数据

        Returns:
            VendorApplicationDetail: 申请详情
        """
        # 检查是否已有待处理的申请
        existing = await self.db.execute(
            select(VendorApplication).where(
                and_(
                    VendorApplication.user_id == user_id,
                    VendorApplication.status == "pending"
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("您已有待处理的申请，请等待审核完成")

        # 检查是否已是开发者
        existing_vendor = await self.db.execute(
            select(Vendor).where(Vendor.user_id == user_id)
        )
        if existing_vendor.scalar_one_or_none():
            raise ValueError("您已是认证开发者，无需再次申请")

        # 创建申请记录
        application = VendorApplication(
            user_id=user_id,
            company_name=data.company_name,
            contact_email=data.contact_email,
            website=data.website,
            description=data.description,
            status="pending",
            submitted_at=datetime.utcnow()
        )
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)

        return VendorApplicationDetail(
            id=application.id,
            user_id=application.user_id,
            company_name=application.company_name,
            contact_email=application.contact_email,
            website=application.website,
            description=application.description,
            status=ApplicationStatus.PENDING,
            rejection_reason=None,
            submitted_at=application.submitted_at,
            reviewed_at=None,
            reviewed_by=None
        )

    async def approve_application(
        self,
        application_id: int,
        admin_id: int,
        tier_id: str = "basic"
    ) -> Vendor:
        """
        批准开发者入驻申请

        Args:
            application_id: 申请ID
            admin_id: 管理员ID
            tier_id: 初始等级

        Returns:
            Vendor: 创建的开发者记录
        """
        # 获取申请
        application = await self.db.get(VendorApplication, application_id)
        if not application:
            raise ValueError("申请不存在")

        if application.status != "pending":
            raise ValueError("该申请已被处理")

        # 获取等级配置
        tier_config = self.get_tier_config(tier_id)
        if not tier_config:
            raise ValueError(f"无效的等级: {tier_id}")

        # 创建开发者记录
        vendor = Vendor(
            user_id=application.user_id,
            company_name=application.company_name,
            contact_email=application.contact_email,
            website=application.website,
            description=application.description,
            tier=tier_id,
            commission_rate=tier_config["commission_rate"],
            features=",".join(tier_config["features"]),
            is_verified=False,
            created_at=datetime.utcnow()
        )
        self.db.add(vendor)

        # 更新申请状态
        application.status = "approved"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = admin_id

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    async def reject_application(
        self,
        application_id: int,
        admin_id: int,
        reason: str
    ) -> VendorApplication:
        """
        拒绝开发者入驻申请

        Args:
            application_id: 申请ID
            admin_id: 管理员ID
            reason: 拒绝原因

        Returns:
            VendorApplication: 更新后的申请记录
        """
        application = await self.db.get(VendorApplication, application_id)
        if not application:
            raise ValueError("申请不存在")

        if application.status != "pending":
            raise ValueError("该申请已被处理")

        application.status = "rejected"
        application.rejection_reason = reason
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = admin_id

        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def get_application_status(self, user_id: int) -> Optional[VendorApplicationDetail]:
        """
        获取用户的申请状态

        Args:
            user_id: 用户ID

        Returns:
            Optional[VendorApplicationDetail]: 申请详情
        """
        result = await self.db.execute(
            select(VendorApplication).where(
                and_(
                    VendorApplication.user_id == user_id,
                    VendorApplication.status.in_(["pending", "approved", "rejected"])
                )
            ).order_by(VendorApplication.submitted_at.desc())
        )
        application = result.scalar_one_or_none()

        if not application:
            return None

        return VendorApplicationDetail(
            id=application.id,
            user_id=application.user_id,
            company_name=application.company_name,
            contact_email=application.contact_email,
            website=application.website,
            description=application.description,
            status=ApplicationStatus(application.status),
            rejection_reason=application.rejection_reason,
            submitted_at=application.submitted_at,
            reviewed_at=application.reviewed_at,
            reviewed_by=application.reviewed_by
        )

    async def get_vendor_profile(self, vendor_id: int) -> Optional[VendorProfile]:
        """
        获取开发者档案

        Args:
            vendor_id: 开发者ID

        Returns:
            Optional[VendorProfile]: 开发者档案
        """
        result = await self.db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        vendor = result.scalar_one_or_none()

        if not vendor:
            return None

        # 获取用户信息
        user_result = await self.db.execute(
            select(User).where(User.id == vendor.user_id)
        )
        user = user_result.scalar_one_or_none()

        # 获取统计信息
        stats = await self.get_vendor_stats(vendor_id)

        return VendorProfile(
            vendor_id=vendor.id,
            user_id=vendor.user_id,
            username=user.username if user else "Unknown",
            company_name=vendor.company_name,
            tier=VendorTier(vendor.tier),
            commission_rate=vendor.commission_rate,
            features=vendor.features.split(",") if vendor.features else [],
            is_verified=vendor.is_verified,
            stats=stats,
            created_at=vendor.created_at,
            updated_at=vendor.updated_at
        )

    async def get_vendor_by_user_id(self, user_id: int) -> Optional[Vendor]:
        """通过用户ID获取开发者记录"""
        result = await self.db.execute(
            select(Vendor).where(Vendor.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_vendor_profile(
        self,
        vendor_id: int,
        data: Dict[str, Any]
    ) -> Vendor:
        """
        更新开发者档案

        Args:
            vendor_id: 开发者ID
            data: 更新数据

        Returns:
            Vendor: 更新后的开发者记录
        """
        vendor = await self.db.get(Vendor, vendor_id)
        if not vendor:
            raise ValueError("开发者不存在")

        # 更新字段
        if "company_name" in data:
            vendor.company_name = data["company_name"]
        if "website" in data:
            vendor.website = data["website"]
        if "description" in data:
            vendor.description = data["description"]
        if "contact_email" in data:
            vendor.contact_email = data["contact_email"]

        vendor.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    async def update_vendor_tier(
        self,
        vendor_id: int,
        tier_id: str
    ) -> Vendor:
        """
        更新开发者等级

        Args:
            vendor_id: 开发者ID
            tier_id: 新的等级ID

        Returns:
            Vendor: 更新后的开发者记录
        """
        vendor = await self.db.get(Vendor, vendor_id)
        if not vendor:
            raise ValueError("开发者不存在")

        tier_config = self.get_tier_config(tier_id)
        if not tier_config:
            raise ValueError(f"无效的等级: {tier_id}")

        vendor.tier = tier_id
        vendor.commission_rate = tier_config["commission_rate"]
        vendor.features = ",".join(tier_config["features"])
        vendor.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    async def get_vendor_stats(self, vendor_id: int) -> Dict[str, Any]:
        """
        获取开发者统计信息

        Args:
            vendor_id: 开发者ID

        Returns:
            dict: 统计信息
        """
        # 获取开发者信息
        vendor = await self.db.get(Vendor, vendor_id)
        if not vendor:
            return {}

        # 获取技能数量
        skills_result = await self.db.execute(
            select(func.count(Skill.id)).where(
                and_(
                    Skill.author_id == vendor.user_id,
                    Skill.status == "approved",
                    Skill.is_deleted == False
                )
            )
        )
        total_skills = skills_result.scalar() or 0

        # 获取下载量
        downloads_result = await self.db.execute(
            select(func.coalesce(func.sum(Skill.download_count), 0)).where(
                and_(
                    Skill.author_id == vendor.user_id,
                    Skill.status == "approved",
                    Skill.is_deleted == False
                )
            )
        )
        total_downloads = downloads_result.scalar() or 0

        # 获取收入统计（从订单表）
        revenue_result = await self.db.execute(
            select(
                func.coalesce(func.sum(Order.final_price), 0),
                func.count(Order.id)
            ).join(
                Skill, Order.content_id == Skill.id
            ).where(
                and_(
                    Skill.author_id == vendor.user_id,
                    Order.payment_status == "paid"
                )
            )
        )
        total_revenue_row = revenue_result.first()
        total_revenue = float(total_revenue_row[0]) if total_revenue_row else 0.0

        # 计算开发者收益
        total_earnings = total_revenue * vendor.commission_rate

        # 获取评分统计
        rating_result = await self.db.execute(
            select(
                func.avg(Skill.rating_avg),
                func.sum(Skill.rating_count)
            ).where(
                and_(
                    Skill.author_id == vendor.user_id,
                    Skill.status == "approved",
                    Skill.is_deleted == False,
                    Skill.rating_avg > 0
                )
            )
        )
        rating_row = rating_result.first()
        avg_rating = float(rating_row[0]) if rating_row and rating_row[0] else 0.0
        total_reviews = rating_row[1] if rating_row and rating_row[1] else 0

        # 获取月度统计
        monthly_result = await self.db.execute(
            select(
                func.coalesce(func.sum(Order.final_price), 0),
                func.count(Order.id)
            ).join(
                Skill, Order.content_id == Skill.id
            ).where(
                and_(
                    Skill.author_id == vendor.user_id,
                    Order.payment_status == "paid",
                    Order.paid_at >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
                )
            )
        )
        monthly_row = monthly_result.first()
        monthly_revenue = float(monthly_row[0]) if monthly_row else 0.0

        # 获取活跃订阅者数
        active_subscribers = await self._get_active_subscribers(vendor.user_id)

        return {
            "total_skills": total_skills,
            "total_downloads": total_downloads,
            "total_revenue": round(total_revenue, 2),
            "total_earnings": round(total_earnings, 2),
            "avg_rating": round(avg_rating, 2),
            "total_reviews": total_reviews,
            "monthly_revenue": round(monthly_revenue, 2),
            "monthly_downloads": 0,
            "active_subscribers": active_subscribers
        }

    async def _get_active_subscribers(self, user_id: int) -> int:
        """获取活跃订阅者数"""
        result = await self.db.execute(
            select(func.count(func.distinct(Order.user_id))).join(
                Skill, Order.content_id == Skill.id
            ).where(
                and_(
                    Skill.author_id == user_id,
                    Order.payment_status == "paid",
                    Order.purchase_type == "subscription",
                    or_(
                        Order.expires_at.is_(None),
                        Order.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalar() or 0

    async def submit_verification(
        self,
        vendor_id: int,
        documents: List[Dict[str, Any]]
    ) -> VendorVerification:
        """
        提交认证材料

        Args:
            vendor_id: 开发者ID
            documents: 认证材料列表

        Returns:
            VendorVerification: 认证信息
        """
        vendor = await self.db.get(Vendor, vendor_id)
        if not vendor:
            raise ValueError("开发者不存在")

        # 保存认证材料
        for doc in documents:
            verification = VendorVerification(
                vendor_id=vendor_id,
                document_type=doc.get("document_type"),
                file_url=doc.get("file_url"),
                file_name=doc.get("file_name"),
                uploaded_at=datetime.utcnow()
            )
            self.db.add(verification)

        await self.db.commit()

        return VendorVerification(
            verified=False,
            verification_documents=documents,
            verified_at=None
        )

    async def verify_vendor(
        self,
        vendor_id: int,
        admin_id: int,
        approved: bool = True
    ) -> Vendor:
        """
        认证开发者

        Args:
            vendor_id: 开发者ID
            admin_id: 管理员ID
            approved: 是否通过认证

        Returns:
            Vendor: 更新后的开发者记录
        """
        vendor = await self.db.get(Vendor, vendor_id)
        if not vendor:
            raise ValueError("开发者不存在")

        vendor.is_verified = approved
        vendor.verified_at = datetime.utcnow() if approved else None
        vendor.verified_by = admin_id
        vendor.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    async def list_pending_applications(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[VendorApplicationDetail], int]:
        """
        获取待处理的申请列表

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            tuple: (申请列表, 总数)
        """
        # 统计总数
        count_result = await self.db.execute(
            select(func.count(VendorApplication.id)).where(
                VendorApplication.status == "pending"
            )
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(VendorApplication)
            .where(VendorApplication.status == "pending")
            .order_by(VendorApplication.submitted_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        applications = result.scalars().all()

        items = [
            VendorApplicationDetail(
                id=app.id,
                user_id=app.user_id,
                company_name=app.company_name,
                contact_email=app.contact_email,
                website=app.website,
                description=app.description,
                status=ApplicationStatus(app.status),
                rejection_reason=app.rejection_reason,
                submitted_at=app.submitted_at,
                reviewed_at=app.reviewed_at,
                reviewed_by=app.reviewed_by
            )
            for app in applications
        ]

        return items, total


# ============================================
# Database Models (SQLAlchemy)
# ============================================

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VendorApplication(Base):
    """开发者入驻申请表"""
    __tablename__ = "vendor_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    company_name = Column(String(200), nullable=False)
    contact_email = Column(String(255), nullable=False)
    website = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    rejection_reason = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, nullable=True)


class Vendor(Base):
    """开发者表"""
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    company_name = Column(String(200), nullable=False)
    contact_email = Column(String(255), nullable=False)
    website = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    tier = Column(String(20), nullable=False, default="basic")
    commission_rate = Column(Float, nullable=False, default=0.7)
    features = Column(String(500), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)


class VendorVerification(Base):
    """开发者认证材料表"""
    __tablename__ = "vendor_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================
# Reference Models (需要从主项目导入)
# ============================================
# 这些模型需要根据实际项目结构进行导入或定义


class User:
    """用户模型引用 - 需要根据实际项目导入"""
    pass


class Skill:
    """技能模型引用 - 需要根据实际项目导入"""
    pass


class Order:
    """订单模型引用 - 需要根据实际项目导入"""
    pass
