"""
Vendor Module Routes
开发者入驻模块API路由

提供开发者入驻、认证、等级管理相关的API接口
"""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    VendorApplicationCreate,
    VendorApplicationResponse,
    VendorApplicationDetail,
    VendorProfile,
    VendorProfileUpdate,
    VendorTierUpdate,
    VendorTierResponse,
    VendorVerification,
    VerificationSubmit,
    VendorStats,
    VendorStatsResponse,
    VendorResponse,
    ApplicationListResponse,
    TierListResponse,
    VendorTierInfo,
    ApplicationStatus,
)
from .services import VendorService, VendorApplication, Vendor, User, Skill, Order

# Import auth dependencies with fallback
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from server.api.middleware.auth import get_current_user, get_current_admin
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False
    get_current_user = None
    get_current_admin = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vendor", tags=["开发者入驻"])


# ============================================
# Database Session Dependency
# ============================================

async def get_db() -> AsyncSession:
    """获取数据库会话 - 需要根据实际项目配置"""
    # TODO: 实现实际的数据库会话获取
    # 临时返回 None，实际使用时需要替换为真实的会话获取
    raise NotImplementedError("需要配置数据库会话")


def get_vendor_service(db: AsyncSession = Depends(get_db)) -> VendorService:
    """获取VendorService实例"""
    return VendorService(db)


# ============================================
# Application Endpoints
# ============================================

@router.post("/apply", response_model=VendorResponse)
async def submit_application(
    data: VendorApplicationCreate,
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service)
):
    """
    提交开发者入驻申请

    用户提交入驻申请，包括公司信息、联系方式等
    """
    try:
        application = await service.submit_application(current_user.id, data)
        return VendorResponse(
            success=True,
            message="申请提交成功，请等待审核",
            data={
                "id": application.id,
                "status": application.status.value,
                "company_name": application.company_name,
                "submitted_at": application.submitted_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit application: {e}")
        raise HTTPException(status_code=500, detail="申请提交失败")


@router.get("/apply/status", response_model=VendorResponse)
async def check_application_status(
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service)
):
    """
    查询入驻申请状态

    用户查看自己的申请状态和详情
    """
    try:
        application = await service.get_application_status(current_user.id)
        if not application:
            return VendorResponse(
                success=True,
                message="暂无申请记录",
                data=None
            )

        return VendorResponse(
            success=True,
            message="查询成功",
            data={
                "id": application.id,
                "status": application.status.value,
                "company_name": application.company_name,
                "contact_email": application.contact_email,
                "website": application.website,
                "description": application.description,
                "rejection_reason": application.rejection_reason,
                "submitted_at": application.submitted_at.isoformat(),
                "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None
            }
        )
    except Exception as e:
        logger.error(f"Failed to check application status: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


@router.get("/apply/list", response_model=ApplicationListResponse)
async def list_pending_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    service: VendorService = Depends(get_vendor_service)
):
    """
    获取待处理的申请列表（管理员）

    仅限管理员查看待处理的入驻申请
    """
    try:
        items, total = await service.list_pending_applications(page, page_size)

        return ApplicationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


@router.put("/apply/{application_id}/approve", response_model=VendorResponse)
async def approve_application(
    application_id: int,
    tier_id: str = Query("basic", description="初始等级"),
    current_admin: User = Depends(get_current_admin),
    service: VendorService = Depends(get_vendor_service)
):
    """
    批准入驻申请（管理员）

    管理员批准入驻申请并设置初始等级
    """
    try:
        vendor = await service.approve_application(application_id, current_admin.id, tier_id)
        return VendorResponse(
            success=True,
            message="申请已批准",
            data={
                "vendor_id": vendor.id,
                "user_id": vendor.user_id,
                "tier": vendor.tier,
                "commission_rate": vendor.commission_rate
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to approve application: {e}")
        raise HTTPException(status_code=500, detail="操作失败")


@router.put("/apply/{application_id}/reject", response_model=VendorResponse)
async def reject_application(
    application_id: int,
    reason: str = Query(..., description="拒绝原因"),
    current_admin: User = Depends(get_current_admin),
    service: VendorService = Depends(get_vendor_service)
):
    """
    拒绝入驻申请（管理员）

    管理员拒绝入驻申请并填写拒绝原因
    """
    try:
        application = await service.reject_application(application_id, current_admin.id, reason)
        return VendorResponse(
            success=True,
            message="申请已拒绝",
            data={
                "application_id": application.id,
                "status": application.status.value,
                "rejection_reason": application.rejection_reason
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to reject application: {e}")
        raise HTTPException(status_code=500, detail="操作失败")


# ============================================
# Profile Endpoints
# ============================================

@router.get("/profile", response_model=VendorResponse)
async def get_vendor_profile(
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service)
):
    """
    获取开发者档案

    获取当前用户的开发者档案信息
    """
    try:
        # 通过用户ID查找开发者
        vendor = await service.get_vendor_by_user_id(current_user.id)
        if not vendor:
            raise HTTPException(status_code=404, detail="您还不是认证开发者")

        profile = await service.get_vendor_profile(vendor.id)
        return VendorResponse(
            success=True,
            message="查询成功",
            data=profile.model_dump() if profile else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vendor profile: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


@router.get("/profile/{vendor_id}", response_model=VendorResponse)
async def get_vendor_profile_by_id(
    vendor_id: int,
    service: VendorService = Depends(get_vendor_service)
):
    """
    通过开发者ID获取档案

    公开接口，任何人可查看开发者信息
    """
    try:
        profile = await service.get_vendor_profile(vendor_id)
        if not profile:
            raise HTTPException(status_code=404, detail="开发者不存在")

        return VendorResponse(
            success=True,
            message="查询成功",
            data=profile.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vendor profile: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


@router.put("/profile", response_model=VendorResponse)
async def update_vendor_profile(
    data: VendorProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service)
):
    """
    更新开发者档案

    开发者更新自己的档案信息
    """
    try:
        vendor = await service.get_vendor_by_user_id(current_user.id)
        if not vendor:
            raise HTTPException(status_code=404, detail="您还不是认证开发者")

        update_data = data.model_dump(exclude_unset=True)
        updated_vendor = await service.update_vendor_profile(vendor.id, update_data)

        return VendorResponse(
            success=True,
            message="档案更新成功",
            data={
                "vendor_id": updated_vendor.id,
                "company_name": updated_vendor.company_name,
                "website": updated_vendor.website,
                "description": updated_vendor.description,
                "contact_email": updated_vendor.contact_email
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update vendor profile: {e}")
        raise HTTPException(status_code=500, detail="更新失败")


# ============================================
# Tier Endpoints
# ============================================

@router.get("/tiers", response_model=TierListResponse)
async def list_vendor_tiers(
    service: VendorService = Depends(get_vendor_service)
):
    """
    获取开发者等级列表

    获取所有可用的开发者等级及其配置
    """
    try:
        tiers = service.get_all_tiers()
        tier_infos = [
            VendorTierInfo(
                id=tier["id"],
                name=tier["name"],
                commission_rate=tier["commission_rate"],
                features=tier["features"]
            )
            for tier in tiers
        ]

        return TierListResponse(tiers=tier_infos)
    except Exception as e:
        logger.error(f"Failed to list tiers: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


@router.put("/tier", response_model=VendorResponse)
async def update_vendor_tier(
    data: VendorTierUpdate,
    current_admin: User = Depends(get_current_admin),
    service: VendorService = Depends(get_vendor_service)
):
    """
    更新开发者等级（管理员）

    管理员修改开发者的等级
    """
    try:
        # 需要指定vendor_id，这里暂时通过查询参数获取
        # 实际使用时可能需要通过其他方式指定
        raise HTTPException(status_code=400, detail="需要指定开发者ID (vendor_id)")

        vendor = await service.update_vendor_tier(vendor_id, data.tier_id)

        return VendorResponse(
            success=True,
            message="等级更新成功",
            data={
                "vendor_id": vendor.id,
                "tier": vendor.tier,
                "commission_rate": vendor.commission_rate,
                "features": vendor.features.split(",") if vendor.features else []
            }
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update vendor tier: {e}")
        raise HTTPException(status_code=500, detail="更新失败")


@router.put("/tier/{vendor_id}", response_model=VendorResponse)
async def update_vendor_tier_by_id(
    vendor_id: int,
    data: VendorTierUpdate,
    current_admin: User = Depends(get_current_admin),
    service: VendorService = Depends(get_vendor_service)
):
    """
    通过ID更新开发者等级（管理员）

    管理员通过开发者ID修改其等级
    """
    try:
        vendor = await service.update_vendor_tier(vendor_id, data.tier_id)

        return VendorResponse(
            success=True,
            message="等级更新成功",
            data={
                "vendor_id": vendor.id,
                "tier": vendor.tier,
                "commission_rate": vendor.commission_rate,
                "features": vendor.features.split(",") if vendor.features else []
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update vendor tier: {e}")
        raise HTTPException(status_code=500, detail="更新失败")


# ============================================
# Stats Endpoints
# ============================================

@router.get("/stats", response_model=VendorResponse)
async def get_vendor_stats(
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service)
):
    """
    获取开发者统计信息

    获取当前用户的开发者统计信息
    """
    try:
        vendor = await service.get_vendor_by_user_id(current_user.id)
        if not vendor:
            raise HTTPException(status_code=404, detail="您还不是认证开发者")

        stats = await service.get_vendor_stats(vendor.id)

        return VendorResponse(
            success=True,
            message="查询成功",
            data=VendorStatsResponse(
                vendor_id=vendor.id,
                period="monthly",
                stats=VendorStats(**stats),
                updated_at=datetime.utcnow()
            ).model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vendor stats: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


@router.get("/stats/{vendor_id}", response_model=VendorResponse)
async def get_vendor_stats_by_id(
    vendor_id: int,
    service: VendorService = Depends(get_vendor_service)
):
    """
    通过ID获取开发者统计信息

    获取指定开发者的统计信息
    """
    try:
        stats = await service.get_vendor_stats(vendor_id)
        if not stats:
            raise HTTPException(status_code=404, detail="开发者不存在")

        return VendorResponse(
            success=True,
            message="查询成功",
            data=VendorStatsResponse(
                vendor_id=vendor_id,
                period="monthly",
                stats=VendorStats(**stats),
                updated_at=datetime.utcnow()
            ).model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vendor stats: {e}")
        raise HTTPException(status_code=500, detail="查询失败")


# ============================================
# Verification Endpoints
# ============================================

@router.post("/verify", response_model=VendorResponse)
async def submit_verification(
    data: VerificationSubmit,
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service)
):
    """
    提交认证材料

    开发者提交认证所需材料
    """
    try:
        vendor = await service.get_vendor_by_user_id(current_user.id)
        if not vendor:
            raise HTTPException(status_code=404, detail="您还不是认证开发者")

        documents = [
            {
                "document_type": doc.document_type,
                "file_url": doc.file_url,
                "file_name": doc.file_name,
                "uploaded_at": doc.uploaded_at
            }
            for doc in data.documents
        ]

        verification = await service.submit_verification(vendor.id, documents)

        return VendorResponse(
            success=True,
            message="认证材料提交成功，请等待审核",
            data=verification.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit verification: {e}")
        raise HTTPException(status_code=500, detail="提交失败")


@router.put("/verify/{vendor_id}", response_model=VendorResponse)
async def verify_vendor(
    vendor_id: int,
    approved: bool = Query(True, description="是否通过认证"),
    current_admin: User = Depends(get_current_admin),
    service: VendorService = Depends(get_vendor_service)
):
    """
    认证开发者（管理员）

    管理员审核并认证开发者
    """
    try:
        vendor = await service.verify_vendor(vendor_id, current_admin.id, approved)

        return VendorResponse(
            success=True,
            message="认证操作成功",
            data={
                "vendor_id": vendor.id,
                "is_verified": vendor.is_verified,
                "verified_at": vendor.verified_at.isoformat() if vendor.verified_at else None
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to verify vendor: {e}")
        raise HTTPException(status_code=500, detail="操作失败")


# ============================================
# Placeholder Dependencies
# ============================================

async def get_current_user():
    """获取当前用户 - 需要根据实际项目配置"""
    raise NotImplementedError("需要配置用户认证")


async def get_current_admin():
    """获取当前管理员 - 需要根据实际项目配置"""
    raise NotImplementedError("需要配置管理员认证")
