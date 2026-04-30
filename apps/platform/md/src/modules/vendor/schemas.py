"""
Vendor Module Schemas
开发者入驻模块数据模型

提供开发者入驻、认证、等级管理相关的数据模型定义
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    """申请状态枚举"""
    PENDING = "pending"       # 待审核
    APPROVED = "approved"     # 已通过
    REJECTED = "rejected"     # 已拒绝
    CANCELLED = "cancelled"     # 已取消


class VendorTier(str, Enum):
    """开发者等级枚举"""
    BASIC = "basic"           # 基础开发者
    STANDARD = "standard"     # 标准开发者
    PREMIUM = "premium"       # 高级开发者


# ============================================
# Application Schemas
# ============================================

class VendorApplicationCreate(BaseModel):
    """创建开发者入驻申请"""
    company_name: str = Field(..., min_length=1, max_length=200, description="公司/团队名称")
    contact_email: EmailStr = Field(..., description="联系邮箱")
    website: Optional[str] = Field(None, max_length=500, description="公司网站")
    description: Optional[str] = Field(None, max_length=2000, description="公司简介")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "北京某某科技有限公司",
                "contact_email": "contact@example.com",
                "website": "https://www.example.com",
                "description": "专注于AI技术研发的科技公司"
            }
        }


class VendorApplicationResponse(BaseModel):
    """开发者入驻申请响应"""
    id: int
    status: ApplicationStatus
    company_name: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class VendorApplicationDetail(BaseModel):
    """开发者入驻申请详情"""
    id: int
    user_id: int
    company_name: str
    contact_email: str
    website: Optional[str] = None
    description: Optional[str] = None
    status: ApplicationStatus
    rejection_reason: Optional[str] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================
# Profile Schemas
# ============================================

class VendorProfile(BaseModel):
    """开发者档案"""
    vendor_id: int
    user_id: int
    username: str
    company_name: str
    tier: VendorTier
    commission_rate: float
    features: List[str]
    is_verified: bool
    stats: dict
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VendorProfileUpdate(BaseModel):
    """更新开发者档案"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    contact_email: Optional[EmailStr] = None


# ============================================
# Tier Schemas
# ============================================

class VendorTierInfo(BaseModel):
    """开发者等级信息"""
    id: str
    name: str
    commission_rate: float
    features: List[str]


class VendorTierUpdate(BaseModel):
    """更新开发者等级"""
    tier_id: str = Field(..., description="等级ID: basic, standard, premium")


class VendorTierResponse(BaseModel):
    """开发者等级响应"""
    tier_id: str
    tier_name: str
    commission_rate: float
    features: List[str]


# ============================================
# Verification Schemas
# ============================================

class VendorVerification(BaseModel):
    """开发者认证信息"""
    verified: bool
    verification_documents: List[dict]
    verified_at: Optional[datetime] = None


class VerificationDocument(BaseModel):
    """认证文件"""
    document_type: str = Field(..., description="文件类型: business_license, id_card, tax_certificate等")
    file_url: str = Field(..., description="文件URL")
    file_name: str
    uploaded_at: datetime


class VerificationSubmit(BaseModel):
    """提交认证材料"""
    documents: List[VerificationDocument] = Field(..., min_length=1, description="认证材料列表")


# ============================================
# Stats Schemas
# ============================================

class VendorStats(BaseModel):
    """开发者统计信息"""
    total_skills: int = 0
    total_downloads: int = 0
    total_revenue: float = 0.0
    total_earnings: float = 0.0
    avg_rating: float = 0.0
    total_reviews: int = 0
    monthly_revenue: float = 0.0
    monthly_downloads: int = 0
    active_subscribers: int = 0


class VendorStatsResponse(BaseModel):
    """开发者统计响应"""
    vendor_id: int
    period: str  # daily, weekly, monthly, yearly, all
    stats: VendorStats
    updated_at: datetime


# ============================================
# Response Wrappers
# ============================================

class VendorResponse(BaseModel):
    """通用响应包装"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class ApplicationListResponse(BaseModel):
    """申请列表响应"""
    items: List[VendorApplicationDetail]
    total: int
    page: int
    page_size: int
    total_pages: int


class TierListResponse(BaseModel):
    """等级列表响应"""
    tiers: List[VendorTierInfo]
