"""
API 数据模型定义
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class SkillListResponse(BaseModel):
    """Skills 列表响应"""
    id: Any
    skill_id: str
    name: str
    description: Optional[str]
    category: str
    type: str
    version: str
    status: str
    price: Any
    is_featured: Any
    view_count: Any
    download_count: Any
    favorite_count: Any
    rating_avg: Any
    rating_count: Any
    published_at: Optional[Any]
    author_username: str
    author_avatar: Optional[str]
    author_level: str
    author_bio: Optional[str]

    class Config:
        from_attributes = True


class SkillDetail(BaseModel):
    """Skill 详情"""
    id: Any
    skill_id: str
    name: str
    description: Optional[str]
    category: str
    type: str
    version: str
    status: str
    price: Any
    is_featured: Any
    view_count: Any
    download_count: Any
    favorite_count: Any
    rating_avg: Any
    rating_count: Any
    published_at: Optional[Any]
    created_at: Any
    updated_at: Any
    author_id: Any
    author_username: str
    author_email: str
    author_avatar: Optional[str]
    author_level: str
    author_bio: Optional[str]
    skill_count: Optional[Any] = None
    total_downloads: Optional[Any] = None
    avg_rating: Optional[Any] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    id: Any
    username: str
    email: str
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    vendor_level: str
    created_at: Any
    skill_count: Any

    class Config:
        from_attributes = True


class UserDetail(BaseModel):
    """用户详情"""
    id: Any
    username: str
    email: str
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    vendor_level: str
    ai_points: Any
    preferred_language: str
    theme_preference: str
    is_active: Any
    is_verified: Any
    created_at: Any
    updated_at: Any
    skill_count: Any
    total_downloads: Any
    avg_rating: Any

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """团队列表响应"""
    id: Any
    team_name: str
    team_slug: str
    description: Optional[str]
    avatar_url: Optional[str]
    member_count: Any
    created_at: Any
    owner_username: str
    project_count: Any

    class Config:
        from_attributes = True


class TeamDetail(BaseModel):
    """团队详情"""
    id: Any
    team_name: str
    team_slug: str
    description: Optional[str]
    avatar_url: Optional[str]
    member_count: Any
    is_active: Any
    created_at: Any
    updated_at: Any
    owner_id: Any
    owner_username: str
    owner_email: str
    project_count: Any
    member_list: list = []

    class Config:
        from_attributes = True


class MarketStats(BaseModel):
    """市场统计"""
    total_users: int
    total_skills: int
    total_vendors: int
    free_skills: int
    paid_skills: int
    total_teams: int


# ==================== 积分商城模型 ====================

class PointsCategory(BaseModel):
    """积分商品分类"""
    id: Any
    category_key: str
    name_en: str
    name_zh: str
    description: Optional[str]
    icon: Optional[str]
    sort_order: Any
    is_active: Any

    class Config:
        from_attributes = True


class PointsProduct(BaseModel):
    """积分商品"""
    id: Any
    product_key: str
    category_key: str
    name_en: str
    name_zh: str
    description_en: Optional[str]
    description_zh: Optional[str]
    image_url: Optional[str]
    points_required: int
    stock_count: Any
    sold_count: Any
    is_active: Any
    is_featured: Any
    sort_order: Any
    valid_days: Optional[Any]
    metadata: Any
    created_at: Any

    class Config:
        from_attributes = True


class PointsProductDetail(PointsProduct):
    """积分商品详情（含分类信息）"""
    category_name: str
    category_icon: Optional[str]
    available: bool = True


class ShoppingCartItem(BaseModel):
    """购物车项"""
    id: Any
    user_id: int
    product_id: int
    quantity: Any
    product_key: str
    product_name: str
    product_image: Optional[str]
    points_required: int
    total_points: int
    stock_available: bool

    class Config:
        from_attributes = True


class ExchangeRecord(BaseModel):
    """兑换记录"""
    id: Any
    exchange_no: str
    user_id: int
    product_id: int
    product_name: str
    points_used: int
    quantity: Any
    status: str
    metadata: Any
    created_at: Any

    class Config:
        from_attributes = True


class ExchangeRequest(BaseModel):
    """兑换请求"""
    product_id: int
    quantity: int = Field(default=1, ge=1, le=10)


class CartRequest(BaseModel):
    """购物车请求"""
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class PointsBalance(BaseModel):
    """积分余额"""
    user_id: int
    username: str
    ai_points: int
    total_exchanges: int
    total_points_used: int


class ProductCreate(BaseModel):
    """创建商品请求"""
    product_key: str = Field(..., min_length=1, max_length=100)
    category_key: str = Field(..., min_length=1, max_length=50)
    name_en: str = Field(..., min_length=1, max_length=200)
    name_zh: str = Field(..., min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_zh: Optional[str] = None
    image_url: Optional[str] = None
    points_required: int = Field(..., ge=0)
    stock_count: int = Field(default=-1, ge=-1)
    is_featured: bool = False
    sort_order: int = 0
    valid_days: Optional[int] = None


class ProductUpdate(BaseModel):
    """更新商品请求"""
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_zh: Optional[str] = None
    image_url: Optional[str] = None
    points_required: Optional[int] = Field(None, ge=0)
    stock_count: Optional[int] = Field(None, ge=-1)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None
    valid_days: Optional[int] = None
