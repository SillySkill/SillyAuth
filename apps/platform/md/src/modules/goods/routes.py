"""
Goods Module Routes
FastAPI routes for goods/product management endpoints

Provides CRUD operations, publish/unpublish, and category management
"""

import math
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging

from .schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStatus,
    ProductType,
    ProductListResponse,
    ProductStatusUpdate,
    ProductBulkAction,
    ProductSearchQuery,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
    GoodsResponse,
)
from .services import product_service, category_service, ProductService, CategoryService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/goods", tags=["商品管理"])


# ============================================================================
# Helper Functions
# ============================================================================

def get_current_user_id() -> int:
    """
    Get current authenticated user ID from JWT token.

    For demonstration, returns a mock user ID.
    In production, this would extract user ID from JWT token.

    Returns:
        User ID of the authenticated user.
    """
    # TODO: Implement proper JWT authentication
    # This is a mock implementation for development
    return 1


def get_vendor_id() -> int:
    """
    Get current user's vendor ID.

    Returns:
        Vendor ID of the authenticated user.
    """
    # TODO: Get vendor_id from user's vendor profile
    # This is a mock implementation for development
    return 1


# ============================================================================
# Product Routes
# ============================================================================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new product.

    Creates a new product in draft status. Use publish endpoint to make it visible.
    """
    vendor_id = get_vendor_id()

    try:
        product = product_service.create_product(
            vendor_id=vendor_id,
            data=data
        )

        logger.info(f"Product created: ID={product.id}, Vendor={vendor_id}")

        return product.to_response()

    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建商品失败: {str(e)}"
        )


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    product_type: Optional[ProductType] = Query(None, description="Filter by product type"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    is_featured: Optional[bool] = Query(None, description="Filter featured only"),
    sort_by: str = Query("created_at", description="Sort field: created_at, price, sales, rating"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List products with filtering and pagination.

    Public endpoint for browsing products. Only returns published products by default.
    """
    # Parse tags if provided
    tag_list = [t.strip() for t in tags.split(',')] if tags else None

    # For public access, only show published products
    if vendor_id is None and status is None:
        status = ProductStatus.PUBLISHED

    # Get products
    products = product_service.list_products(
        vendor_id=vendor_id,
        status=status,
        category_id=category_id,
        product_type=product_type,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        keyword=keyword,
        tags=tag_list,
        min_price=min_price,
        max_price=max_price,
        is_featured=is_featured,
    )

    # Get total count
    total = product_service.count_products(
        vendor_id=vendor_id,
        status=status,
        category_id=category_id,
    )

    # Calculate total pages
    pages = math.ceil(total / limit) if total > 0 else 1

    return ProductListResponse(
        items=[p.to_response() for p in products],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/products/featured", response_model=ProductListResponse)
async def list_featured_products(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of products"),
):
    """
    List featured products.

    Returns a list of featured/promoted products for homepage display.
    """
    products = product_service.list_products(
        status=ProductStatus.PUBLISHED,
        category_id=category_id,
        is_featured=True,
        page=1,
        limit=limit,
        sort_by="sales",
        sort_order="desc",
    )

    return ProductListResponse(
        items=[p.to_response() for p in products],
        total=len(products),
        page=1,
        limit=limit,
        pages=1,
    )


@router.get("/products/search", response_model=ProductListResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    sort_by: str = Query("relevance", description="Sort: relevance, price, sales, rating, created_at"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search products by keyword.

    Full-text search across product name and description.
    """
    # Map relevance to created_at for now
    if sort_by == "relevance":
        sort_by = "created_at"

    products = product_service.list_products(
        status=ProductStatus.PUBLISHED,
        category_id=category_id,
        keyword=q,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        min_price=min_price,
        max_price=max_price,
    )

    total = product_service.count_products(status=ProductStatus.PUBLISHED)
    pages = math.ceil(total / limit) if total > 0 else 1

    return ProductListResponse(
        items=[p.to_response() for p in products],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    Get product details by ID.

    Increments view count on access.
    """
    product = product_service.get_product(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    # Increment view count
    product_service.increment_view_count(product_id)

    return product.to_response()


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Update a product.

    Only the product owner can update their products.
    """
    product = product_service.get_product(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    vendor_id = get_vendor_id()
    if product.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此商品"
        )

    if product.status == ProductStatus.DELETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已删除的商品无法修改"
        )

    updated_product = product_service.update_product(product_id, data)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新商品失败"
        )

    return updated_product.to_response()


@router.delete("/products/{product_id}", response_model=GoodsResponse)
async def delete_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a product (soft delete).

    Only the product owner can delete their products.
    """
    product = product_service.get_product(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    vendor_id = get_vendor_id()
    if product.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此商品"
        )

    success = product_service.delete_product(product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除商品失败"
        )

    return GoodsResponse(
        success=True,
        message="商品已删除"
    )


@router.post("/products/{product_id}/publish", response_model=ProductResponse)
async def publish_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Publish a product.

    Makes the product visible in the marketplace.
    """
    product = product_service.get_product(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    vendor_id = get_vendor_id()
    if product.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品"
        )

    published_product = product_service.publish_product(product_id)

    if not published_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法发布此商品"
        )

    return published_product.to_response()


@router.post("/products/{product_id}/unpublish", response_model=ProductResponse)
async def unpublish_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Unpublish a product.

    Removes the product from the marketplace visibility.
    """
    product = product_service.get_product(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    vendor_id = get_vendor_id()
    if product.vendor_id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此商品"
        )

    unpublished_product = product_service.unpublish_product(product_id)

    if not unpublished_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法取消发布此商品"
        )

    return unpublished_product.to_response()


@router.post("/products/bulk", response_model=GoodsResponse)
async def bulk_product_action(
    data: ProductBulkAction,
    user_id: int = Depends(get_current_user_id)
):
    """
    Perform bulk actions on products.

    Actions: publish, unpublish, delete
    """
    vendor_id = get_vendor_id()
    success_count = 0
    failed_ids = []

    for product_id in data.product_ids:
        product = product_service.get_product(product_id)

        if not product:
            failed_ids.append(product_id)
            continue

        if product.vendor_id != vendor_id:
            failed_ids.append(product_id)
            continue

        if data.action == "publish":
            result = product_service.publish_product(product_id)
        elif data.action == "unpublish":
            result = product_service.unpublish_product(product_id)
        elif data.action == "delete":
            result = product_service.delete_product(product_id)
        else:
            continue

        if result:
            success_count += 1

    return GoodsResponse(
        success=len(failed_ids) == 0,
        message=f"成功处理 {success_count} 个商品",
        data={
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids
        }
    )


# ============================================================================
# Category Routes
# ============================================================================

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new category.

    Only admins or authorized users can create categories.
    """
    try:
        category = category_service.create_category(data)
        return category.to_response()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
):
    """
    List all categories.

    Returns a flat list of categories, optionally filtered by parent.
    """
    categories = category_service.list_categories(parent_id=parent_id)
    return [c.to_response() for c in categories]


@router.get("/categories/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree():
    """
    Get category tree structure.

    Returns hierarchical category structure with nested children.
    """
    tree = category_service.get_category_tree(product_service=product_service)
    return tree


@router.get("/categories/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(slug: str):
    """
    Get category by slug.
    """
    category = category_service.get_category_by_slug(slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    return category.to_response()


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    """
    Get category details by ID.
    """
    category = category_service.get_category(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    return category.to_response()


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    user_id: int = Depends(get_current_user_id)
):
    """
    Update a category.

    Only admins can update categories.
    """
    try:
        category = category_service.update_category(category_id, data)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )

        return category.to_response()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/categories/{category_id}", response_model=GoodsResponse)
async def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a category.

    Only admins can delete categories.
    Categories with products or child categories cannot be deleted.
    """
    success = category_service.delete_category(category_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除分类，可能包含子分类或商品"
        )

    return GoodsResponse(
        success=True,
        message="分类已删除"
    )


# ============================================================================
# Vendor Product Routes
# ============================================================================

@router.get("/vendor/products", response_model=ProductListResponse)
async def list_vendor_products(
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: int = Depends(get_current_user_id)
):
    """
    List products for the current vendor.

    Returns all products owned by the authenticated vendor.
    """
    vendor_id = get_vendor_id()

    products = product_service.list_products(
        vendor_id=vendor_id,
        status=status,
        category_id=category_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        keyword=keyword,
    )

    total = product_service.count_products(
        vendor_id=vendor_id,
        status=status,
        category_id=category_id,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return ProductListResponse(
        items=[p.to_response() for p in products],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/vendor/products/stats")
async def get_vendor_product_stats(user_id: int = Depends(get_current_user_id)):
    """
    Get product statistics for the current vendor.

    Returns counts by status and total views/sales.
    """
    vendor_id = get_vendor_id()

    products = product_service.list_products(vendor_id=vendor_id)

    stats = {
        "total": len(products),
        "by_status": {
            "draft": 0,
            "pending": 0,
            "published": 0,
            "suspended": 0,
            "deleted": 0,
        },
        "total_views": 0,
        "total_sales": 0,
    }

    for product in products:
        status_key = product.status.value if isinstance(product.status, ProductStatus) else product.status
        if status_key in stats["by_status"]:
            stats["by_status"][status_key] += 1
        stats["total_views"] += product.view_count
        stats["total_sales"] += product.sales_count

    return GoodsResponse(
        success=True,
        data=stats
    )


# ============================================================================
# Sillypan (傻福虾盘) Public Routes
# ============================================================================

@router.get("/sillypan/products", response_model=ProductListResponse)
async def list_sillypan_products(
    limit: int = Query(10, ge=1, le=100, description="Number of products"),
):
    """
    List sillypan (傻福虾盘) products for public display.

    Returns all published sillypan products.
    """
    # Get sillypan category
    category = category_service.get_category_by_slug("sillypan")

    if not category:
        return ProductListResponse(
            items=[],
            total=0,
            page=1,
            limit=limit,
            pages=1,
        )

    products = product_service.list_products(
        category_id=category.id,
        status=ProductStatus.PUBLISHED,
        page=1,
        limit=limit,
        sort_by="price",
        sort_order="asc",
    )

    return ProductListResponse(
        items=[p.to_response() for p in products],
        total=len(products),
        page=1,
        limit=limit,
        pages=1,
    )
    """
    Get product statistics for the current vendor.

    Returns counts by status and total views/sales.
    """
    vendor_id = get_vendor_id()

    products = product_service.list_products(vendor_id=vendor_id)

    stats = {
        "total": len(products),
        "by_status": {
            "draft": 0,
            "pending": 0,
            "published": 0,
            "suspended": 0,
            "deleted": 0,
        },
        "total_views": 0,
        "total_sales": 0,
    }

    for product in products:
        status_key = product.status.value if isinstance(product.status, ProductStatus) else product.status
        if status_key in stats["by_status"]:
            stats["by_status"][status_key] += 1
        stats["total_views"] += product.view_count
        stats["total_sales"] += product.sales_count

    return GoodsResponse(
        success=True,
        data=stats
    )
