"""
Goods Module Schemas
Pydantic models for goods/product management

Provides product creation, update, response schemas, and category management
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ProductStatus(str, Enum):
    """Product status enumeration."""
    DRAFT = "draft"           # Draft/Not published
    PENDING = "pending"       # Pending review
    PUBLISHED = "published"   # Published and visible
    SUSPENDED = "suspended"   # Suspended by admin
    DELETED = "deleted"       # Soft deleted


class ProductType(str, Enum):
    """Product type enumeration."""
    PHYSICAL = "physical"     # Physical goods
    DIGITAL = "digital"       # Digital goods
    SERVICE = "service"       # Services
    SUBSCRIPTION = "subscription"  # Subscription-based


# ============================================
# Category Schemas
# ============================================

class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID for hierarchical categories")
    icon: Optional[str] = Field(None, max_length=50, description="Icon identifier")
    sort_order: int = Field(0, description="Display sort order")

    @field_validator('slug')
    @classmethod
    def slug_format(cls, v: str) -> str:
        """Validate slug format (lowercase, alphanumeric, hyphens only)."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = Field(None)
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = Field(None)


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    sort_order: int = 0
    product_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryTreeResponse(BaseModel):
    """Schema for category tree response (hierarchical)."""
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    product_count: int = 0
    children: List["CategoryTreeResponse"] = []

    class Config:
        from_attributes = True


# Enable forward references for recursive model
CategoryTreeResponse.model_rebuild()


# ============================================
# Product Schemas
# ============================================

class ProductImage(BaseModel):
    """Schema for product image."""
    url: str = Field(..., description="Image URL")
    alt_text: Optional[str] = Field(None, description="Alt text for accessibility")
    is_primary: bool = Field(False, description="Is this the primary product image")
    sort_order: int = Field(0, description="Display sort order")


class ProductSpecification(BaseModel):
    """Schema for product specification/attribute."""
    name: str = Field(..., description="Specification name")
    value: str = Field(..., description="Specification value")


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(..., min_length=1, description="Product description")
    short_description: Optional[str] = Field(None, max_length=500, description="Short description")
    category_id: int = Field(..., description="Category ID")
    product_type: ProductType = Field(ProductType.DIGITAL, description="Product type")
    price: Decimal = Field(..., ge=0, description="Product price")
    original_price: Optional[Decimal] = Field(None, ge=0, description="Original price for discount display")
    currency: str = Field("CNY", max_length=3, description="Currency code")
    stock: int = Field(0, ge=0, description="Stock quantity (0 for unlimited)")
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")
    images: List[ProductImage] = Field(default_factory=list, description="Product images")
    specifications: List[ProductSpecification] = Field(default_factory=list, description="Product specifications")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_featured: bool = Field(False, description="Feature this product")
    min_purchase_quantity: int = Field(1, ge=1, description="Minimum purchase quantity")
    max_purchase_quantity: Optional[int] = Field(None, ge=1, description="Maximum purchase quantity per order")

    @field_validator('original_price')
    @classmethod
    def original_price_greater_than_price(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate original price is greater than current price."""
        if v is not None and 'price' in info.data and v < info.data['price']:
            raise ValueError('Original price must be greater than or equal to the current price')
        return v


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = Field(None)
    product_type: Optional[ProductType] = None
    price: Optional[Decimal] = Field(None, ge=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    stock: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    images: Optional[List[ProductImage]] = None
    specifications: Optional[List[ProductSpecification]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    min_purchase_quantity: Optional[int] = Field(None, ge=1)
    max_purchase_quantity: Optional[int] = Field(None, ge=1)


class ProductResponse(BaseModel):
    """Schema for product response."""
    id: int
    vendor_id: int
    vendor_name: Optional[str] = None
    name: str
    slug: str
    description: str
    short_description: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    product_type: ProductType
    price: Decimal
    original_price: Optional[Decimal] = None
    currency: str
    stock: int
    sku: Optional[str] = None
    images: List[ProductImage] = []
    specifications: List[ProductSpecification] = []
    tags: List[str] = []
    status: ProductStatus
    metadata: Optional[Dict[str, Any]] = None
    is_featured: bool = False
    view_count: int = 0
    sales_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    min_purchase_quantity: int = 1
    max_purchase_quantity: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    items: List[ProductResponse]
    total: int
    page: int
    limit: int
    pages: int


class ProductStatusUpdate(BaseModel):
    """Schema for updating product status (publish/unpublish)."""
    status: ProductStatus


class ProductBulkAction(BaseModel):
    """Schema for bulk product actions."""
    product_ids: List[int] = Field(..., min_length=1, description="List of product IDs")
    action: str = Field(..., description="Action to perform: publish, unpublish, delete")


# ============================================
# Search Schemas
# ============================================

class ProductSearchQuery(BaseModel):
    """Schema for product search query parameters."""
    keyword: Optional[str] = Field(None, description="Search keyword")
    category_id: Optional[int] = Field(None, description="Filter by category")
    vendor_id: Optional[int] = Field(None, description="Filter by vendor")
    product_type: Optional[ProductType] = Field(None, description="Filter by product type")
    status: Optional[ProductStatus] = Field(ProductStatus.PUBLISHED, description="Filter by status")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    is_featured: Optional[bool] = Field(None, description="Filter featured products only")
    sort_by: str = Field("created_at", description="Sort field: created_at, price, sales, rating")
    sort_order: str = Field("desc", description="Sort order: asc, desc")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


# ============================================
# Response Wrappers
# ============================================

class GoodsResponse(BaseModel):
    """Generic response wrapper for goods module."""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
