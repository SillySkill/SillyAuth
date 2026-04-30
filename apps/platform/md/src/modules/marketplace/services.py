"""
Marketplace Module Services
Business logic for marketplace listings and purchases

Provides listing management, purchase workflow, and review handling
"""

import uuid
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple

from .schemas import (
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    ListingStatus,
    PurchaseItem,
    PurchaseRequest,
    PurchaseResponse,
    PurchaseStatus,
    PaymentMethod,
    ReviewCreate,
    ReviewResponse,
    MarketplaceStats,
    VendorSalesStats,
)

logger = logging.getLogger(__name__)


class Listing:
    """Listing model representing a marketplace product listing."""

    def __init__(
        self,
        id: int,
        product_id: int,
        vendor_id: int,
        product_name: str,
        product_slug: str,
        price: Decimal,
        quantity: int,
        sold_quantity: int = 0,
        original_price: Optional[Decimal] = None,
        currency: str = "CNY",
        min_quantity: int = 1,
        max_quantity: Optional[int] = None,
        description: Optional[str] = None,
        product_images: Optional[List[Dict]] = None,
        status: ListingStatus = ListingStatus.ACTIVE,
        is_featured: bool = False,
        rating: float = 0.0,
        review_count: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.product_id = product_id
        self.vendor_id = vendor_id
        self.product_name = product_name
        self.product_slug = product_slug
        self.price = price
        self.original_price = original_price
        self.currency = currency
        self.quantity = quantity
        self.sold_quantity = sold_quantity
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.description = description
        self.product_images = product_images or []
        self.status = status
        self.is_featured = is_featured
        self.rating = rating
        self.review_count = review_count
        self.start_time = start_time
        self.end_time = end_time
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def available_quantity(self) -> int:
        """Get the currently available quantity."""
        return max(0, self.quantity - self.sold_quantity)

    def to_response(
        self,
        vendor_name: Optional[str] = None
    ) -> ListingResponse:
        """Convert to ListingResponse schema."""
        return ListingResponse(
            id=self.id,
            product_id=self.product_id,
            vendor_id=self.vendor_id,
            vendor_name=vendor_name,
            product_name=self.product_name,
            product_slug=self.product_slug,
            product_images=self.product_images,
            price=self.price,
            original_price=self.original_price,
            currency=self.currency,
            quantity=self.quantity,
            sold_quantity=self.sold_quantity,
            available_quantity=self.available_quantity,
            min_quantity=self.min_quantity,
            max_quantity=self.max_quantity,
            description=self.description,
            status=self.status,
            is_featured=self.is_featured,
            rating=self.rating,
            review_count=self.review_count,
            start_time=self.start_time,
            end_time=self.end_time,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def is_available(self) -> bool:
        """Check if the listing is available for purchase."""
        now = datetime.utcnow()

        # Check status
        if self.status != ListingStatus.ACTIVE:
            return False

        # Check quantity
        if self.available_quantity <= 0:
            return False

        # Check time window
        if self.start_time and now < self.start_time:
            return False

        if self.end_time and now > self.end_time:
            return False

        return True


class Purchase:
    """Purchase model representing a marketplace purchase."""

    def __init__(
        self,
        id: int,
        order_id: str,
        buyer_id: int,
        items: List[Dict],
        subtotal: Decimal,
        total_amount: Decimal,
        currency: str = "CNY",
        discount_amount: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        shipping_amount: Decimal = Decimal("0"),
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        payment_status: str = "pending",
        purchase_status: PurchaseStatus = PurchaseStatus.PENDING,
        coupon_code: Optional[str] = None,
        notes: Optional[str] = None,
        shipping_address: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.buyer_id = buyer_id
        self.items = items
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.shipping_amount = shipping_amount
        self.total_amount = total_amount
        self.currency = currency
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.purchase_status = purchase_status
        self.coupon_code = coupon_code
        self.notes = notes
        self.shipping_address = shipping_address
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_response(self) -> PurchaseResponse:
        """Convert to PurchaseResponse schema."""
        return PurchaseResponse(
            id=self.id,
            order_id=self.order_id,
            buyer_id=self.buyer_id,
            items=[PurchaseItem(**item) if isinstance(item, dict) else item for item in self.items],
            subtotal=self.subtotal,
            discount_amount=self.discount_amount,
            tax_amount=self.tax_amount,
            shipping_amount=self.shipping_amount,
            total_amount=self.total_amount,
            currency=self.currency,
            payment_method=self.payment_method,
            payment_status=self.payment_status,
            purchase_status=self.purchase_status,
            coupon_code=self.coupon_code,
            notes=self.notes,
            shipping_address=self.shipping_address,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class Review:
    """Review model representing a product review."""

    def __init__(
        self,
        id: int,
        purchase_id: int,
        listing_id: int,
        buyer_id: int,
        rating: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        images: Optional[List[str]] = None,
        attributes: Optional[Dict[str, str]] = None,
        buyer_name: Optional[str] = None,
        is_verified: bool = False,
        helpful_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.purchase_id = purchase_id
        self.listing_id = listing_id
        self.buyer_id = buyer_id
        self.rating = rating
        self.title = title
        self.content = content
        self.images = images or []
        self.attributes = attributes or {}
        self.buyer_name = buyer_name
        self.is_verified = is_verified
        self.helpful_count = helpful_count
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_response(self) -> ReviewResponse:
        """Convert to ReviewResponse schema."""
        return ReviewResponse(
            id=self.id,
            purchase_id=self.purchase_id,
            listing_id=self.listing_id,
            buyer_id=self.buyer_id,
            buyer_name=self.buyer_name,
            rating=self.rating,
            title=self.title,
            content=self.content,
            images=self.images,
            attributes=self.attributes,
            is_verified=self.is_verified,
            helpful_count=self.helpful_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ListingService:
    """Service for managing marketplace listings."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._listings: Dict[int, Listing] = {}
        self._product_listing_index: Dict[int, List[int]] = {}  # product_id -> list of listing_ids
        self._vendor_listing_index: Dict[int, List[int]] = {}  # vendor_id -> list of listing_ids
        self._next_id: int = 1
        self._config = config or {}

    def create_listing(
        self,
        product_id: int,
        vendor_id: int,
        product_data: Dict[str, Any],
        data: ListingCreate,
        vendor_name: Optional[str] = None
    ) -> Listing:
        """
        Create a new marketplace listing.

        Args:
            product_id: The product ID to list.
            vendor_id: The vendor creating the listing.
            product_data: Product information for the listing.
            data: Listing creation data.
            vendor_name: Optional vendor name for response.

        Returns:
            The created Listing instance.
        """
        listing = Listing(
            id=self._next_id,
            product_id=product_id,
            vendor_id=vendor_id,
            product_name=product_data.get('name', ''),
            product_slug=product_data.get('slug', ''),
            price=data.price,
            original_price=product_data.get('original_price'),
            currency=product_data.get('currency', 'CNY'),
            quantity=data.quantity,
            min_quantity=data.min_quantity,
            max_quantity=data.max_quantity,
            description=data.description,
            product_images=product_data.get('images', []),
            status=ListingStatus.ACTIVE,
            is_featured=data.is_featured,
            start_time=data.start_time,
            end_time=data.end_time,
            metadata=data.metadata,
        )

        self._listings[listing.id] = listing
        self._next_id += 1

        # Update indexes
        if product_id not in self._product_listing_index:
            self._product_listing_index[product_id] = []
        self._product_listing_index[product_id].append(listing.id)

        if vendor_id not in self._vendor_listing_index:
            self._vendor_listing_index[vendor_id] = []
        self._vendor_listing_index[vendor_id].append(listing.id)

        logger.info(f"Listing created: ID={listing.id}, Product={product_id}, Vendor={vendor_id}")
        return listing

    def get_listing(self, listing_id: int) -> Optional[Listing]:
        """
        Get a listing by ID.

        Args:
            listing_id: The ID of the listing.

        Returns:
            The Listing instance if found, None otherwise.
        """
        return self._listings.get(listing_id)

    def update_listing(
        self,
        listing_id: int,
        data: ListingUpdate
    ) -> Optional[Listing]:
        """
        Update a listing.

        Args:
            listing_id: The ID of the listing to update.
            data: Listing update data.

        Returns:
            The updated Listing instance if found, None otherwise.
        """
        listing = self._listings.get(listing_id)
        if not listing:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and hasattr(listing, field):
                setattr(listing, field, value)

        listing.updated_at = datetime.utcnow()

        logger.info(f"Listing updated: ID={listing.id}")
        return listing

    def delete_listing(self, listing_id: int) -> bool:
        """
        Delete a listing.

        Args:
            listing_id: The ID of the listing to delete.

        Returns:
            True if deleted, False if not found.
        """
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        # Remove from indexes
        if listing.product_id in self._product_listing_index:
            self._product_listing_index[listing.product_id].remove(listing_id)

        if listing.vendor_id in self._vendor_listing_index:
            self._vendor_listing_index[listing.vendor_id].remove(listing_id)

        listing.status = ListingStatus.REMOVED
        listing.updated_at = datetime.utcnow()

        logger.info(f"Listing deleted: ID={listing_id}")
        return True

    def activate_listing(self, listing_id: int) -> Optional[Listing]:
        """Activate a listing."""
        listing = self._listings.get(listing_id)
        if listing:
            listing.status = ListingStatus.ACTIVE
            listing.updated_at = datetime.utcnow()
        return listing

    def deactivate_listing(self, listing_id: int) -> Optional[Listing]:
        """Deactivate a listing."""
        listing = self._listings.get(listing_id)
        if listing:
            listing.status = ListingStatus.INACTIVE
            listing.updated_at = datetime.utcnow()
        return listing

    def mark_sold_out(self, listing_id: int) -> Optional[Listing]:
        """Mark a listing as sold out."""
        listing = self._listings.get(listing_id)
        if listing:
            listing.status = ListingStatus.SOLD_OUT
            listing.updated_at = datetime.utcnow()
        return listing

    def reserve_stock(self, listing_id: int, quantity: int) -> bool:
        """
        Reserve stock for a purchase.

        Args:
            listing_id: The listing ID.
            quantity: Quantity to reserve.

        Returns:
            True if reservation successful, False otherwise.
        """
        listing = self._listings.get(listing_id)
        if not listing or not listing.is_available():
            return False

        if listing.available_quantity < quantity:
            return False

        listing.sold_quantity += quantity
        listing.updated_at = datetime.utcnow()

        # Mark as sold out if no more available
        if listing.available_quantity <= 0:
            listing.status = ListingStatus.SOLD_OUT

        return True

    def release_stock(self, listing_id: int, quantity: int) -> bool:
        """
        Release reserved stock (e.g., on order cancellation).

        Args:
            listing_id: The listing ID.
            quantity: Quantity to release.

        Returns:
            True if release successful, False otherwise.
        """
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        if listing.sold_quantity < quantity:
            quantity = listing.sold_quantity

        listing.sold_quantity -= quantity
        listing.updated_at = datetime.utcnow()

        # Reactivate if was sold out
        if listing.status == ListingStatus.SOLD_OUT and listing.available_quantity > 0:
            listing.status = ListingStatus.ACTIVE

        return True

    def list_listings(
        self,
        vendor_id: Optional[int] = None,
        product_id: Optional[int] = None,
        status: Optional[ListingStatus] = None,
        category_id: Optional[int] = None,
        keyword: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        min_rating: Optional[float] = None,
        is_featured: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20,
    ) -> List[Listing]:
        """
        List listings with filtering and pagination.

        Args:
            Various filter parameters.

        Returns:
            List of Listing instances.
        """
        listings = list(self._listings.values())

        # Filter by vendor
        if vendor_id is not None:
            listings = [l for l in listings if l.vendor_id == vendor_id]

        # Filter by product
        if product_id is not None:
            listings = [l for l in listings if l.product_id == product_id]

        # Filter by status
        if status is not None:
            listings = [l for l in listings if l.status == status]
        else:
            # By default, only show active listings
            listings = [l for l in listings if l.status == ListingStatus.ACTIVE and l.is_available()]

        # Filter by keyword
        if keyword:
            keyword_lower = keyword.lower()
            listings = [
                l for l in listings
                if keyword_lower in l.product_name.lower() or
                   (l.description and keyword_lower in l.description.lower())
            ]

        # Filter by price
        if min_price is not None:
            listings = [l for l in listings if l.price >= min_price]

        if max_price is not None:
            listings = [l for l in listings if l.price <= max_price]

        # Filter by rating
        if min_rating is not None:
            listings = [l for l in listings if l.rating >= min_rating]

        # Filter featured
        if is_featured is not None:
            listings = [l for l in listings if l.is_featured == is_featured]

        # Sort
        reverse = sort_order.lower() == "desc"
        if sort_by == "price":
            listings.sort(key=lambda l: float(l.price), reverse=reverse)
        elif sort_by == "sales":
            listings.sort(key=lambda l: l.sold_quantity, reverse=reverse)
        elif sort_by == "rating":
            listings.sort(key=lambda l: l.rating, reverse=reverse)
        else:
            listings.sort(key=lambda l: l.created_at, reverse=reverse)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        return listings[start:end]

    def count_listings(
        self,
        vendor_id: Optional[int] = None,
        status: Optional[ListingStatus] = None,
    ) -> int:
        """Count listings matching the criteria."""
        listings = list(self._listings.values())

        if vendor_id is not None:
            listings = [l for l in listings if l.vendor_id == vendor_id]

        if status is not None:
            listings = [l for l in listings if l.status == status]
        else:
            listings = [l for l in listings if l.status == ListingStatus.ACTIVE]

        return len(listings)

    def update_rating(self, listing_id: int, rating: float, review_count: int) -> Optional[Listing]:
        """Update listing rating."""
        listing = self._listings.get(listing_id)
        if listing:
            listing.rating = rating
            listing.review_count = review_count
        return listing


class PurchaseService:
    """Service for managing marketplace purchases."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._purchases: Dict[int, Purchase] = {}
        self._order_index: Dict[str, int] = {}  # order_id -> purchase_id
        self._buyer_index: Dict[int, List[int]] = {}  # buyer_id -> list of purchase_ids
        self._next_id: int = 1
        self._config = config or {}
        self._purchase_config = self._config.get("purchase", {})
        self._max_quantity = self._purchase_config.get("max_quantity_per_order", 99)
        self._allow_oversell = self._purchase_config.get("allow_oversell", False)

    def generate_order_id(self) -> str:
        """Generate a unique order ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_part = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_part}"

    def calculate_totals(
        self,
        items: List[PurchaseItem],
        coupon_code: Optional[str] = None,
        shipping_amount: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0")
    ) -> Dict[str, Decimal]:
        """
        Calculate purchase totals.

        Args:
            items: Purchase items.
            coupon_code: Optional coupon code.
            shipping_amount: Shipping cost.
            tax_rate: Tax rate (e.g., 0.1 for 10%).

        Returns:
            Dict with subtotal, discount, tax, and total amounts.
        """
        subtotal = sum(item.price * item.quantity for item in items)

        # Apply coupon discount (mock - would integrate with coupon service)
        discount_amount = Decimal("0")
        if coupon_code:
            # Mock discount calculation
            discount_amount = subtotal * Decimal("0.1")  # 10% off

        # Calculate tax
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * tax_rate

        # Calculate total
        total = taxable_amount + tax_amount + shipping_amount

        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "shipping_amount": shipping_amount,
            "total": total,
        }

    def create_purchase(
        self,
        buyer_id: int,
        items: List[PurchaseItem],
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        coupon_code: Optional[str] = None,
        notes: Optional[str] = None,
        shipping_address: Optional[Dict[str, Any]] = None,
        listing_service: Optional[ListingService] = None
    ) -> Optional[Purchase]:
        """
        Create a new purchase.

        Args:
            buyer_id: The buyer ID.
            items: Purchase items.
            payment_method: Payment method.
            coupon_code: Optional coupon code.
            notes: Order notes.
            shipping_address: Shipping address.
            listing_service: ListingService for stock management.

        Returns:
            The created Purchase instance if successful, None otherwise.
        """
        # Validate and reserve stock
        if listing_service:
            for item in items:
                listing = listing_service.get_listing(item.listing_id)
                if not listing or not listing.is_available():
                    logger.warning(f"Listing not available: {item.listing_id}")
                    return None

                if not listing.is_available():
                    logger.warning(f"Listing out of stock: {item.listing_id}")
                    return None

                if item.quantity > listing.available_quantity:
                    if not self._allow_oversell:
                        logger.warning(f"Insufficient stock for listing {item.listing_id}")
                        return None

                # Reserve stock
                if not listing_service.reserve_stock(item.listing_id, item.quantity):
                    logger.warning(f"Failed to reserve stock for listing {item.listing_id}")
                    return None

        # Calculate totals
        totals = self.calculate_totals(items, coupon_code)

        # Create purchase
        order_id = self.generate_order_id()
        purchase = Purchase(
            id=self._next_id,
            order_id=order_id,
            buyer_id=buyer_id,
            items=[item.model_dump() for item in items],
            subtotal=totals["subtotal"],
            discount_amount=totals["discount_amount"],
            tax_amount=totals["tax_amount"],
            shipping_amount=totals["shipping_amount"],
            total_amount=totals["total"],
            currency="CNY",
            payment_method=payment_method,
            payment_status="pending",
            purchase_status=PurchaseStatus.PENDING,
            coupon_code=coupon_code,
            notes=notes,
            shipping_address=shipping_address,
        )

        self._purchases[purchase.id] = purchase
        self._order_index[purchase.order_id] = purchase.id
        self._next_id += 1

        # Update buyer index
        if buyer_id not in self._buyer_index:
            self._buyer_index[buyer_id] = []
        self._buyer_index[buyer_id].append(purchase.id)

        logger.info(f"Purchase created: Order={order_id}, Buyer={buyer_id}, Total={purchase.total_amount}")
        return purchase

    def get_purchase(self, purchase_id: int) -> Optional[Purchase]:
        """Get a purchase by ID."""
        return self._purchases.get(purchase_id)

    def get_purchase_by_order_id(self, order_id: str) -> Optional[Purchase]:
        """Get a purchase by order ID."""
        purchase_id = self._order_index.get(order_id)
        if purchase_id:
            return self._purchases.get(purchase_id)
        return None

    def list_purchases(
        self,
        buyer_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        status: Optional[PurchaseStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> List[Purchase]:
        """
        List purchases with filtering.

        Args:
            buyer_id: Filter by buyer.
            vendor_id: Filter by vendor.
            status: Filter by status.
            page: Page number.
            limit: Items per page.

        Returns:
            List of Purchase instances.
        """
        purchases = list(self._purchases.values())

        if buyer_id is not None:
            purchases = [p for p in purchases if p.buyer_id == buyer_id]

        if status is not None:
            purchases = [p for p in purchases if p.purchase_status == status]

        # Sort by creation time (newest first)
        purchases.sort(key=lambda p: p.created_at, reverse=True)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        return purchases[start:end]

    def count_purchases(
        self,
        buyer_id: Optional[int] = None,
        status: Optional[PurchaseStatus] = None,
    ) -> int:
        """Count purchases matching criteria."""
        purchases = list(self._purchases.values())

        if buyer_id is not None:
            purchases = [p for p in purchases if p.buyer_id == buyer_id]

        if status is not None:
            purchases = [p for p in purchases if p.purchase_status == status]

        return len(purchases)

    def update_purchase_status(
        self,
        purchase_id: int,
        purchase_status: PurchaseStatus,
        payment_status: Optional[str] = None
    ) -> Optional[Purchase]:
        """
        Update purchase status.

        Args:
            purchase_id: The purchase ID.
            purchase_status: New purchase status.
            payment_status: Optional new payment status.

        Returns:
            The updated Purchase instance if found, None otherwise.
        """
        purchase = self._purchases.get(purchase_id)
        if not purchase:
            return None

        purchase.purchase_status = purchase_status
        if payment_status:
            purchase.payment_status = payment_status
        purchase.updated_at = datetime.utcnow()

        logger.info(f"Purchase status updated: Order={purchase.order_id}, Status={purchase_status}")
        return purchase

    def cancel_purchase(
        self,
        purchase_id: int,
        listing_service: Optional[ListingService] = None
    ) -> Optional[Purchase]:
        """
        Cancel a purchase and release stock.

        Args:
            purchase_id: The purchase ID.
            listing_service: ListingService for stock release.

        Returns:
            The cancelled Purchase instance if successful, None otherwise.
        """
        purchase = self._purchases.get(purchase_id)
        if not purchase:
            return None

        if purchase.purchase_status not in [
            PurchaseStatus.PENDING,
            PurchaseStatus.PAID
        ]:
            logger.warning(f"Cannot cancel purchase in status: {purchase.purchase_status}")
            return None

        # Release stock for each item
        if listing_service:
            for item_data in purchase.items:
                item = PurchaseItem(**item_data) if isinstance(item_data, dict) else item_data
                listing_service.release_stock(item.listing_id, item.quantity)

        purchase.purchase_status = PurchaseStatus.CANCELLED
        purchase.payment_status = "cancelled"
        purchase.updated_at = datetime.utcnow()

        logger.info(f"Purchase cancelled: Order={purchase.order_id}")
        return purchase

    def complete_purchase(self, purchase_id: int) -> Optional[Purchase]:
        """Mark a purchase as completed."""
        purchase = self._purchases.get(purchase_id)
        if not purchase:
            return None

        purchase.purchase_status = PurchaseStatus.COMPLETED
        purchase.updated_at = datetime.utcnow()

        logger.info(f"Purchase completed: Order={purchase.order_id}")
        return purchase


class ReviewService:
    """Service for managing product reviews."""

    def __init__(self):
        self._reviews: Dict[int, Review] = {}
        self._listing_review_index: Dict[int, List[int]] = {}  # listing_id -> list of review_ids
        self._buyer_review_index: Dict[int, int] = {}  # (buyer_id, listing_id) -> review_id
        self._next_id: int = 1

    def create_review(
        self,
        purchase_id: int,
        listing_id: int,
        buyer_id: int,
        data: ReviewCreate,
        buyer_name: Optional[str] = None
    ) -> Review:
        """
        Create a new review.

        Args:
            purchase_id: The associated purchase ID.
            listing_id: The listing being reviewed.
            buyer_id: The buyer creating the review.
            data: Review data.
            buyer_name: Optional buyer name for display.

        Returns:
            The created Review instance.
        """
        review = Review(
            id=self._next_id,
            purchase_id=purchase_id,
            listing_id=listing_id,
            buyer_id=buyer_id,
            rating=data.rating,
            title=data.title,
            content=data.content,
            images=data.images,
            attributes=data.attributes,
            buyer_name=buyer_name,
            is_verified=True,  # Reviews from actual purchases are verified
        )

        self._reviews[review.id] = review
        self._next_id += 1

        # Update indexes
        if listing_id not in self._listing_review_index:
            self._listing_review_index[listing_id] = []
        self._listing_review_index[listing_id].append(review.id)

        self._buyer_review_index[(buyer_id, listing_id)] = review.id

        logger.info(f"Review created: ID={review.id}, Listing={listing_id}, Buyer={buyer_id}")
        return review

    def get_review(self, review_id: int) -> Optional[Review]:
        """Get a review by ID."""
        return self._reviews.get(review_id)

    def list_reviews(
        self,
        listing_id: Optional[int] = None,
        buyer_id: Optional[int] = None,
        min_rating: Optional[int] = None,
        page: int = 1,
        limit: int = 20,
    ) -> List[Review]:
        """
        List reviews with filtering.

        Args:
            listing_id: Filter by listing.
            buyer_id: Filter by buyer.
            min_rating: Minimum rating filter.
            page: Page number.
            limit: Items per page.

        Returns:
            List of Review instances.
        """
        reviews = list(self._reviews.values())

        if listing_id is not None:
            reviews = [r for r in reviews if r.listing_id == listing_id]

        if buyer_id is not None:
            reviews = [r for r in reviews if r.buyer_id == buyer_id]

        if min_rating is not None:
            reviews = [r for r in reviews if r.rating >= min_rating]

        # Sort by creation time (newest first)
        reviews.sort(key=lambda r: r.created_at, reverse=True)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        return reviews[start:end]

    def calculate_average_rating(self, listing_id: int) -> Tuple[float, int]:
        """
        Calculate average rating for a listing.

        Args:
            listing_id: The listing ID.

        Returns:
            Tuple of (average_rating, review_count).
        """
        reviews = self._reviews.values()
        listing_reviews = [r for r in reviews if r.listing_id == listing_id]

        if not listing_reviews:
            return 0.0, 0

        total_rating = sum(r.rating for r in listing_reviews)
        avg_rating = total_rating / len(listing_reviews)

        return round(avg_rating, 2), len(listing_reviews)

    def has_reviewed(self, buyer_id: int, listing_id: int) -> bool:
        """Check if a buyer has already reviewed a listing."""
        return (buyer_id, listing_id) in self._buyer_review_index


# Singleton instances
listing_service = ListingService()
purchase_service = PurchaseService()
review_service = ReviewService()
