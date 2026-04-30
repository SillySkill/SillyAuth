"""
Goods Module Services
Business logic for goods/product management operations

Provides product CRUD operations, publishing workflow, and category management
"""

import uuid
import hashlib
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

from .schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStatus,
    ProductType,
    ProductImage,
    ProductSpecification,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
)

logger = logging.getLogger(__name__)


def generate_product_slug(name: str, product_id: int) -> str:
    """
    Generate a URL-friendly slug from product name.

    Args:
        name: Product name
        product_id: Product ID for uniqueness

    Returns:
        URL-friendly slug
    """
    # Create base slug from name
    slug = name.lower()
    slug = slug.replace(' ', '-')
    slug = slug.replace('_', '-')

    # Remove special characters except hyphens
    slug = ''.join(c if c.isalnum() or c == '-' else '' for c in slug)

    # Remove consecutive hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')

    # Trim hyphens from start/end
    slug = slug.strip('-')

    # Add unique suffix using product ID
    return f"{slug}-{product_id}"


class Product:
    """Product model representing a goods item."""

    def __init__(
        self,
        id: int,
        vendor_id: int,
        name: str,
        description: str,
        category_id: int,
        product_type: ProductType,
        price: Decimal,
        status: ProductStatus = ProductStatus.DRAFT,
        short_description: Optional[str] = None,
        original_price: Optional[Decimal] = None,
        currency: str = "CNY",
        stock: int = 0,
        sku: Optional[str] = None,
        images: Optional[List[Dict]] = None,
        specifications: Optional[List[Dict]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_featured: bool = False,
        view_count: int = 0,
        sales_count: int = 0,
        rating: float = 0.0,
        review_count: int = 0,
        min_purchase_quantity: int = 1,
        max_purchase_quantity: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id
        self.vendor_id = vendor_id
        self.name = name
        self.description = description
        self.category_id = category_id
        self.product_type = product_type
        self.price = price
        self.status = status
        self.short_description = short_description
        self.original_price = original_price
        self.currency = currency
        self.stock = stock
        self.sku = sku
        self.images = images or []
        self.specifications = specifications or []
        self.tags = tags or []
        self.metadata = metadata or {}
        self.is_featured = is_featured
        self.view_count = view_count
        self.sales_count = sales_count
        self.rating = rating
        self.review_count = review_count
        self.min_purchase_quantity = min_purchase_quantity
        self.max_purchase_quantity = max_purchase_quantity
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.published_at = published_at

        # Generate slug from name
        self.slug = generate_product_slug(name, id)

    def to_response(self, vendor_name: Optional[str] = None, category_name: Optional[str] = None) -> ProductResponse:
        """Convert to ProductResponse schema."""
        return ProductResponse(
            id=self.id,
            vendor_id=self.vendor_id,
            vendor_name=vendor_name,
            name=self.name,
            slug=self.slug,
            description=self.description,
            short_description=self.short_description,
            category_id=self.category_id,
            category_name=category_name,
            product_type=self.product_type,
            price=self.price,
            original_price=self.original_price,
            currency=self.currency,
            stock=self.stock,
            sku=self.sku,
            images=[ProductImage(**img) if isinstance(img, dict) else img for img in self.images],
            specifications=[ProductSpecification(**spec) if isinstance(spec, dict) else spec for spec in self.specifications],
            tags=self.tags,
            status=self.status,
            metadata=self.metadata,
            is_featured=self.is_featured,
            view_count=self.view_count,
            sales_count=self.sales_count,
            rating=self.rating,
            review_count=self.review_count,
            min_purchase_quantity=self.min_purchase_quantity,
            max_purchase_quantity=self.max_purchase_quantity,
            created_at=self.created_at,
            updated_at=self.updated_at,
            published_at=self.published_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "category_id": self.category_id,
            "product_type": self.product_type.value if isinstance(self.product_type, ProductType) else self.product_type,
            "price": float(self.price),
            "original_price": float(self.original_price) if self.original_price else None,
            "currency": self.currency,
            "stock": self.stock,
            "sku": self.sku,
            "images": self.images,
            "specifications": self.specifications,
            "tags": self.tags,
            "status": self.status.value if isinstance(self.status, ProductStatus) else self.status,
            "metadata": self.metadata,
            "is_featured": self.is_featured,
            "view_count": self.view_count,
            "sales_count": self.sales_count,
            "rating": self.rating,
            "review_count": self.review_count,
            "min_purchase_quantity": self.min_purchase_quantity,
            "max_purchase_quantity": self.max_purchase_quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }


class Category:
    """Category model for product categorization."""

    def __init__(
        self,
        id: int,
        name: str,
        slug: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        icon: Optional[str] = None,
        sort_order: int = 0,
        product_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.slug = slug
        self.description = description
        self.parent_id = parent_id
        self.icon = icon
        self.sort_order = sort_order
        self.product_count = product_count
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_response(self) -> CategoryResponse:
        """Convert to CategoryResponse schema."""
        return CategoryResponse(
            id=self.id,
            name=self.name,
            slug=self.slug,
            description=self.description,
            parent_id=self.parent_id,
            icon=self.icon,
            sort_order=self.sort_order,
            product_count=self.product_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_tree_response(self, children: List["CategoryTreeResponse"] = None) -> CategoryTreeResponse:
        """Convert to CategoryTreeResponse schema."""
        return CategoryTreeResponse(
            id=self.id,
            name=self.name,
            slug=self.slug,
            icon=self.icon,
            product_count=self.product_count,
            children=children or [],
        )


class ProductService:
    """Service for managing products/goods."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._products: Dict[int, Product] = {}
        self._next_id: int = 1
        self._config = config or {}
        self._pagination_config = self._config.get("pagination", {})
        self._default_page_size = self._pagination_config.get("default_page_size", 20)
        self._max_page_size = self._pagination_config.get("max_page_size", 100)

    def create_product(
        self,
        vendor_id: int,
        data: ProductCreate,
        vendor_name: Optional[str] = None,
        category_name: Optional[str] = None
    ) -> Product:
        """
        Create a new product.

        Args:
            vendor_id: The ID of the vendor creating the product.
            data: Product creation data.
            vendor_name: Optional vendor name for response.
            category_name: Optional category name for response.

        Returns:
            The created Product instance.
        """
        product = Product(
            id=self._next_id,
            vendor_id=vendor_id,
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            product_type=data.product_type,
            price=data.price,
            status=ProductStatus.DRAFT,
            short_description=data.short_description,
            original_price=data.original_price,
            currency=data.currency,
            stock=data.stock,
            sku=data.sku,
            images=[img.model_dump() for img in data.images],
            specifications=[spec.model_dump() for spec in data.specifications],
            tags=data.tags,
            metadata=data.metadata,
            is_featured=data.is_featured,
            min_purchase_quantity=data.min_purchase_quantity,
            max_purchase_quantity=data.max_purchase_quantity,
        )

        self._products[product.id] = product
        self._next_id += 1

        logger.info(f"Product created: ID={product.id}, Name={product.name}, Vendor={vendor_id}")
        return product

    def get_product(self, product_id: int) -> Optional[Product]:
        """
        Get a product by ID.

        Args:
            product_id: The ID of the product.

        Returns:
            The Product instance if found, None otherwise.
        """
        return self._products.get(product_id)

    def update_product(
        self,
        product_id: int,
        data: ProductUpdate
    ) -> Optional[Product]:
        """
        Update a product.

        Args:
            product_id: The ID of the product to update.
            data: Product update data.

        Returns:
            The updated Product instance if found, None otherwise.
        """
        product = self._products.get(product_id)
        if not product:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                if field == 'images':
                    setattr(product, field, [img.model_dump() if isinstance(img, ProductImage) else img for img in value])
                elif field == 'specifications':
                    setattr(product, field, [spec.model_dump() if isinstance(spec, ProductSpecification) else spec for spec in value])
                elif hasattr(product, field):
                    setattr(product, field, value)

        product.updated_at = datetime.utcnow()

        logger.info(f"Product updated: ID={product.id}")
        return product

    def delete_product(self, product_id: int, hard: bool = False) -> bool:
        """
        Delete a product (soft delete by default).

        Args:
            product_id: The ID of the product to delete.
            hard: If True, permanently delete; otherwise soft delete.

        Returns:
            True if deleted, False if not found.
        """
        product = self._products.get(product_id)
        if not product:
            return False

        if hard:
            del self._products[product_id]
            logger.info(f"Product hard deleted: ID={product_id}")
        else:
            product.status = ProductStatus.DELETED
            product.updated_at = datetime.utcnow()
            logger.info(f"Product soft deleted: ID={product_id}")

        return True

    def publish_product(self, product_id: int) -> Optional[Product]:
        """
        Publish a product (make it visible in the marketplace).

        Args:
            product_id: The ID of the product to publish.

        Returns:
            The published Product instance if found, None otherwise.
        """
        product = self._products.get(product_id)
        if not product:
            return None

        if product.status == ProductStatus.DELETED:
            logger.warning(f"Cannot publish deleted product: ID={product_id}")
            return None

        product.status = ProductStatus.PUBLISHED
        product.published_at = datetime.utcnow()
        product.updated_at = datetime.utcnow()

        logger.info(f"Product published: ID={product.id}, Name={product.name}")
        return product

    def unpublish_product(self, product_id: int) -> Optional[Product]:
        """
        Unpublish a product (make it invisible in the marketplace).

        Args:
            product_id: The ID of the product to unpublish.

        Returns:
            The unpublished Product instance if found, None otherwise.
        """
        product = self._products.get(product_id)
        if not product:
            return None

        if product.status != ProductStatus.PUBLISHED:
            logger.warning(f"Product is not published: ID={product_id}")
            return None

        product.status = ProductStatus.DRAFT
        product.updated_at = datetime.utcnow()

        logger.info(f"Product unpublished: ID={product.id}")
        return product

    def suspend_product(self, product_id: int) -> Optional[Product]:
        """
        Suspend a product (admin action).

        Args:
            product_id: The ID of the product to suspend.

        Returns:
            The suspended Product instance if found, None otherwise.
        """
        product = self._products.get(product_id)
        if not product:
            return None

        product.status = ProductStatus.SUSPENDED
        product.updated_at = datetime.utcnow()

        logger.info(f"Product suspended: ID={product.id}")
        return product

    def list_products(
        self,
        vendor_id: Optional[int] = None,
        status: Optional[ProductStatus] = None,
        category_id: Optional[int] = None,
        product_type: Optional[ProductType] = None,
        page: int = 1,
        limit: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        keyword: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_featured: Optional[bool] = None,
    ) -> List[Product]:
        """
        List products with filtering and pagination.

        Args:
            vendor_id: Filter by vendor ID.
            status: Filter by status.
            category_id: Filter by category ID.
            product_type: Filter by product type.
            page: Page number (1-indexed).
            limit: Number of items per page.
            sort_by: Sort field.
            sort_order: Sort order (asc/desc).
            keyword: Search keyword.
            tags: Filter by tags.
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            is_featured: Filter featured products only.

        Returns:
            List of Product instances.
        """
        # Set default pagination
        limit = limit or self._default_page_size
        limit = min(limit, self._max_page_size)

        # Filter products
        products = list(self._products.values())

        if vendor_id is not None:
            products = [p for p in products if p.vendor_id == vendor_id]

        if status is not None:
            products = [p for p in products if p.status == status]

        if category_id is not None:
            products = [p for p in products if p.category_id == category_id]

        if product_type is not None:
            products = [p for p in products if p.product_type == product_type]

        if keyword:
            keyword_lower = keyword.lower()
            products = [
                p for p in products
                if keyword_lower in p.name.lower() or keyword_lower in p.description.lower()
            ]

        if tags:
            products = [p for p in products if any(tag in p.tags for tag in tags)]

        if min_price is not None:
            products = [p for p in products if p.price >= min_price]

        if max_price is not None:
            products = [p for p in products if p.price <= max_price]

        if is_featured is not None:
            products = [p for p in products if p.is_featured == is_featured]

        # Sort products
        reverse = sort_order.lower() == "desc"
        if sort_by == "price":
            products.sort(key=lambda p: float(p.price), reverse=reverse)
        elif sort_by == "sales":
            products.sort(key=lambda p: p.sales_count, reverse=reverse)
        elif sort_by == "rating":
            products.sort(key=lambda p: p.rating, reverse=reverse)
        else:
            products.sort(key=lambda p: p.created_at, reverse=reverse)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        return products[start:end]

    def count_products(
        self,
        vendor_id: Optional[int] = None,
        status: Optional[ProductStatus] = None,
        category_id: Optional[int] = None,
    ) -> int:
        """Count products matching the criteria."""
        products = list(self._products.values())

        if vendor_id is not None:
            products = [p for p in products if p.vendor_id == vendor_id]

        if status is not None:
            products = [p for p in products if p.status == status]

        if category_id is not None:
            products = [p for p in products if p.category_id == category_id]

        return len(products)

    def increment_view_count(self, product_id: int) -> Optional[Product]:
        """Increment the view count of a product."""
        product = self._products.get(product_id)
        if product:
            product.view_count += 1
        return product

    def increment_sales_count(self, product_id: int, quantity: int = 1) -> Optional[Product]:
        """Increment the sales count of a product."""
        product = self._products.get(product_id)
        if product:
            product.sales_count += quantity
        return product

    def update_rating(self, product_id: int, new_rating: float, review_count: int) -> Optional[Product]:
        """Update product rating and review count."""
        product = self._products.get(product_id)
        if product:
            product.rating = new_rating
            product.review_count = review_count
        return product


class CategoryService:
    """Service for managing product categories."""

    def __init__(self):
        self._categories: Dict[int, Category] = {}
        self._slug_index: Dict[str, int] = {}
        self._next_id: int = 1

    def create_category(self, data: CategoryCreate) -> Category:
        """
        Create a new category.

        Args:
            data: Category creation data.

        Returns:
            The created Category instance.
        """
        # Check for duplicate slug
        if data.slug in self._slug_index:
            raise ValueError(f"Category with slug '{data.slug}' already exists")

        # Validate parent exists if provided
        if data.parent_id is not None and data.parent_id not in self._categories:
            raise ValueError(f"Parent category with ID '{data.parent_id}' does not exist")

        category = Category(
            id=self._next_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            parent_id=data.parent_id,
            icon=data.icon,
            sort_order=data.sort_order,
        )

        self._categories[category.id] = category
        self._slug_index[category.slug] = category.id
        self._next_id += 1

        logger.info(f"Category created: ID={category.id}, Name={category.name}")
        return category

    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Get a category by ID.

        Args:
            category_id: The ID of the category.

        Returns:
            The Category instance if found, None otherwise.
        """
        return self._categories.get(category_id)

    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """
        Get a category by slug.

        Args:
            slug: The slug of the category.

        Returns:
            The Category instance if found, None otherwise.
        """
        category_id = self._slug_index.get(slug)
        if category_id:
            return self._categories.get(category_id)
        return None

    def update_category(self, category_id: int, data: CategoryUpdate) -> Optional[Category]:
        """
        Update a category.

        Args:
            category_id: The ID of the category to update.
            data: Category update data.

        Returns:
            The updated Category instance if found, None otherwise.
        """
        category = self._categories.get(category_id)
        if not category:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                if field == 'slug':
                    # Check for duplicate slug
                    if value in self._slug_index and self._slug_index[value] != category_id:
                        raise ValueError(f"Category with slug '{value}' already exists")
                    # Update slug index
                    del self._slug_index[category.slug]
                    self._slug_index[value] = category_id
                    setattr(category, field, value)
                elif hasattr(category, field):
                    setattr(category, field, value)

        category.updated_at = datetime.utcnow()

        logger.info(f"Category updated: ID={category.id}")
        return category

    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category.

        Args:
            category_id: The ID of the category to delete.

        Returns:
            True if deleted, False if not found or has children.
        """
        category = self._categories.get(category_id)
        if not category:
            return False

        # Check for children
        children = [c for c in self._categories.values() if c.parent_id == category_id]
        if children:
            logger.warning(f"Cannot delete category with children: ID={category_id}")
            return False

        # Remove from slug index
        if category.slug in self._slug_index:
            del self._slug_index[category.slug]

        del self._categories[category_id]

        logger.info(f"Category deleted: ID={category_id}")
        return True

    def list_categories(
        self,
        parent_id: Optional[int] = None,
        include_counts: bool = True
    ) -> List[Category]:
        """
        List categories.

        Args:
            parent_id: Filter by parent ID (None for root categories).
            include_counts: Whether to include product counts.

        Returns:
            List of Category instances.
        """
        categories = list(self._categories.values())

        if parent_id is not None:
            categories = [c for c in categories if c.parent_id == parent_id]
        else:
            categories = [c for c in categories if c.parent_id is None]

        categories.sort(key=lambda c: (c.sort_order, c.name))

        return categories

    def get_category_tree(
        self,
        product_service: Optional[ProductService] = None
    ) -> List[CategoryTreeResponse]:
        """
        Get category tree structure.

        Args:
            product_service: Optional ProductService for counting products.

        Returns:
            List of CategoryTreeResponse with nested children.
        """
        def build_tree(parent_id: Optional[int] = None) -> List[CategoryTreeResponse]:
            children = []
            for category in self._categories.values():
                if category.parent_id == parent_id:
                    # Update product count if service provided
                    if product_service:
                        category.product_count = product_service.count_products(category_id=category.id)
                    child_tree = build_tree(category.id)
                    children.append(category.to_tree_response(children=child_tree))

            children.sort(key=lambda c: c.id)
            return children

        return build_tree(parent_id=None)

    def count_categories(self) -> int:
        """Count total categories."""
        return len(self._categories)


# Singleton instances
product_service = ProductService()
category_service = CategoryService()


def seed_sillypan_products():
    """Initialize sillypan U盘 products for GDPS campaign."""
    from decimal import Decimal
    from .schemas import ProductCreate, ProductType, ProductStatus, ProductImage, ProductSpecification

    # First, create a category for sillypan products
    try:
        category = category_service.create_category(
            CategoryCreate(
                name="傻福虾盘",
                slug="sillypan",
                description="傻福虾定制周边产品",
                icon="shopping-outlined",
                sort_order=1
            )
        )
    except ValueError:
        # Category already exists
        category = category_service.get_category_by_slug("sillypan")
        if not category:
            return

    category_id = category.id

    # Sillypan U盘 products - GDPS 8折活动价
    sillypan_products = [
        {
            "name": "傻福虾 U盘 128GB 银色",
            "description": "傻福虾定制 U盘，128GB 大容量，USB3.0 高速接口。GDPS 活动价 8 折！",
            "price": Decimal("479"),
            "original_price": Decimal("599"),
            "stock": 50,
            "specifications": [
                {"name": "容量", "value": "128GB"},
                {"name": "颜色", "value": "银色"},
                {"name": "接口", "value": "USB3.0"},
                {"name": "质保", "value": "终身质保"},
            ],
            "tags": ["U盘", "128GB", "银色", "GDPS活动"],
            "image": "/webs/USilly/sillypan/1-傻福虾U盘印刷-正面-银色.png",
        },
        {
            "name": "傻福虾 U盘 256GB 银色",
            "description": "傻福虾定制 U盘，256GB 大容量，USB3.0 高速接口。GDPS 活动价 8 折！",
            "price": Decimal("849"),
            "original_price": Decimal("1062"),
            "stock": 30,
            "specifications": [
                {"name": "容量", "value": "256GB"},
                {"name": "颜色", "value": "银色"},
                {"name": "接口", "value": "USB3.0"},
                {"name": "质保", "value": "终身质保"},
            ],
            "tags": ["U盘", "256GB", "银色", "GDPS活动"],
            "image": "/webs/USilly/sillypan/1-傻福虾U盘印刷-正面-银色.png",
        },
        {
            "name": "傻福虾 U盘 512GB 枪灰银",
            "description": "傻福虾定制 U盘，512GB 超大容量，USB3.0 高速接口。GDPS 活动价 8 折！",
            "price": Decimal("1489"),
            "original_price": Decimal("1862"),
            "stock": 20,
            "specifications": [
                {"name": "容量", "value": "512GB"},
                {"name": "颜色", "value": "枪灰银"},
                {"name": "接口", "value": "USB3.0"},
                {"name": "质保", "value": "终身质保"},
            ],
            "tags": ["U盘", "512GB", "枪灰银", "GDPS活动"],
            "image": "/webs/USilly/sillypan/1-正面效果图-黑色.png",
        },
        {
            "name": "傻福虾 U盘 1TB 枪灰银",
            "description": "傻福虾定制 U盘，1TB 顶级容量，USB3.0 高速接口。GDPS 活动价 8 折！",
            "price": Decimal("2089"),
            "original_price": Decimal("2612"),
            "stock": 10,
            "specifications": [
                {"name": "容量", "value": "1TB"},
                {"name": "颜色", "value": "枪灰银"},
                {"name": "接口", "value": "USB3.0"},
                {"name": "质保", "value": "终身质保"},
            ],
            "tags": ["U盘", "1TB", "枪灰银", "GDPS活动"],
            "image": "/webs/USilly/sillypan/2-U盘侧面.png",
        },
    ]

    # Create products if they don't exist (check by name prefix)
    existing_names = [p.name for p in product_service.list_products()]
    vendor_id = 1  # System vendor for sillypan products

    for prod_data in sillypan_products:
        # Check if product already exists
        if any(prod_data["name"] in name for name in existing_names):
            continue

        # Create images
        images = [
            ProductImage(
                url=prod_data["image"],
                alt_text=prod_data["name"],
                is_primary=True,
                sort_order=0
            )
        ]

        # Create specifications
        specs = [
            ProductSpecification(name=s["name"], value=s["value"])
            for s in prod_data["specifications"]
        ]

        # Create product data
        product_data = ProductCreate(
            name=prod_data["name"],
            description=prod_data["description"],
            category_id=category_id,
            product_type=ProductType.PHYSICAL,
            price=prod_data["price"],
            original_price=prod_data["original_price"],
            stock=prod_data["stock"],
            images=images,
            specifications=specs,
            tags=prod_data["tags"],
            is_featured=True,
        )

        # Create and publish product
        product = product_service.create_product(
            vendor_id=vendor_id,
            data=product_data
        )
        product_service.publish_product(product.id)
        logger.info(f"Seeded sillypan product: {product.name}")


# Initialize sillypan products on module load
seed_sillypan_products()
