"""
Promotion Module Services
Business logic for promotion/coupon/flash sale management

Provides CRUD operations, validation, and discount calculations
"""

import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple

from .schemas import (
    PromotionCreate,
    PromotionUpdate,
    PromotionResponse,
    PromotionStatus,
    PromotionType,
    PromotionRule,
    CouponCreate,
    CouponResponse,
    CouponStatus,
    CouponType,
    CouponValidateRequest,
    CouponValidateResponse,
    FlashSaleCreate,
    FlashSaleResponse,
    FlashSaleListResponse,
    CouponUsageResponse,
    DiscountCalculationRequest,
    DiscountCalculationResponse,
    OrderItemForDiscount,
)

logger = logging.getLogger(__name__)


# ============================================
# Helper Functions
# ============================================

def generate_coupon_code(prefix: str = "CPN") -> str:
    """
    Generate a unique coupon code.

    Args:
        prefix: Prefix for the coupon code

    Returns:
        Unique coupon code string
    """
    unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"{prefix}{unique_id}"


def calculate_percentage_discount(amount: Decimal, percentage: Decimal, max_discount: Optional[Decimal] = None) -> Decimal:
    """
    Calculate percentage-based discount.

    Args:
        amount: Original amount
        percentage: Discount percentage (0-100)
        max_discount: Optional maximum discount cap

    Returns:
        Discount amount
    """
    discount = amount * (percentage / Decimal("100"))

    if max_discount is not None and discount > max_discount:
        discount = max_discount

    return discount.quantize(Decimal("0.01"))


def calculate_fixed_discount(amount: Decimal, fixed_amount: Decimal) -> Decimal:
    """
    Calculate fixed amount discount.

    Args:
        amount: Original amount
        fixed_amount: Fixed discount amount

    Returns:
        Discount amount (capped at original amount)
    """
    return min(amount, fixed_amount).quantize(Decimal("0.01"))


# ============================================
# Promotion Model & Service
# ============================================

class Promotion:
    """Promotion model representing a promotion activity."""

    def __init__(
        self,
        id: int,
        name: str,
        promotion_type: PromotionType,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        status: PromotionStatus = PromotionStatus.DRAFT,
        rules: Optional[List[Dict]] = None,
        max_usage: Optional[int] = None,
        max_usage_per_user: Optional[int] = None,
        min_order_amount: Optional[Decimal] = None,
        current_usage: int = 0,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.promotion_type = promotion_type
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.rules = rules or []
        self.max_usage = max_usage
        self.max_usage_per_user = max_usage_per_user
        self.min_order_amount = min_order_amount
        self.current_usage = current_usage
        self.is_active = is_active
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_response(self) -> PromotionResponse:
        """Convert to PromotionResponse schema."""
        rules_list = [PromotionRule(**r) if isinstance(r, dict) else r for r in self.rules]
        return PromotionResponse(
            id=self.id,
            name=self.name,
            description=self.description,
            promotion_type=self.promotion_type,
            start_time=self.start_time,
            end_time=self.end_time,
            status=self.status,
            rules=rules_list,
            rules_json=str(self.rules),
            max_usage=self.max_usage,
            max_usage_per_user=self.max_usage_per_user,
            min_order_amount=self.min_order_amount,
            current_usage=self.current_usage,
            is_active=self.is_active,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def is_valid(self) -> bool:
        """Check if promotion is currently valid."""
        now = datetime.utcnow()
        return (
            self.is_active and
            self.status == PromotionStatus.ACTIVE and
            self.start_time <= now <= self.end_time
        )


class PromotionService:
    """Service for managing promotions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._promotions: Dict[int, Promotion] = {}
        self._next_id: int = 1
        self._config = config or {}

        # Seed some sample promotions
        self._seed_promotions()

    def _seed_promotions(self) -> None:
        """Seed sample promotions for demonstration."""
        if self._promotions:
            return

        # Welcome discount promotion
        welcome = Promotion(
            id=self._next_id,
            name="新人专属优惠",
            description="新用户首单立减10元",
            promotion_type=PromotionType.COUPON,
            start_time=datetime.utcnow() - timedelta(days=30),
            end_time=datetime.utcnow() + timedelta(days=365),
            status=PromotionStatus.ACTIVE,
            rules=[{"rule_type": "first_order", "rule_value": True, "description": "仅限首单使用"}],
            max_usage=10000,
            max_usage_per_user=1,
            min_order_amount=Decimal("50"),
            is_active=True,
        )
        self._promotions[welcome.id] = welcome
        self._next_id += 1

        # Summer sale promotion
        summer = Promotion(
            id=self._next_id,
            name="夏季大促",
            description="全场85折起",
            promotion_type=PromotionType.DISCOUNT,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=30),
            status=PromotionStatus.ACTIVE,
            rules=[{"rule_type": "min_amount", "rule_value": 100, "description": "满100元可用"}],
            is_active=True,
        )
        self._promotions[summer.id] = summer
        self._next_id += 1

        logger.info(f"Seeded {len(self._promotions)} sample promotions")

    def create_promotion(self, data: PromotionCreate) -> Promotion:
        """
        Create a new promotion.

        Args:
            data: Promotion creation data

        Returns:
            The created Promotion instance
        """
        promotion = Promotion(
            id=self._next_id,
            name=data.name,
            description=data.description,
            promotion_type=data.promotion_type,
            start_time=data.start_time,
            end_time=data.end_time,
            status=PromotionStatus.DRAFT,
            rules=[r.model_dump() for r in data.rules] if data.rules else [],
            max_usage=data.max_usage,
            max_usage_per_user=data.max_usage_per_user,
            min_order_amount=data.min_order_amount,
            is_active=data.is_active,
            metadata=data.metadata,
        )

        self._promotions[promotion.id] = promotion
        self._next_id += 1

        logger.info(f"Promotion created: ID={promotion.id}, Name={promotion.name}")
        return promotion

    def get_promotion(self, promotion_id: int) -> Optional[Promotion]:
        """Get a promotion by ID."""
        return self._promotions.get(promotion_id)

    def update_promotion(self, promotion_id: int, data: PromotionUpdate) -> Optional[Promotion]:
        """Update a promotion."""
        promotion = self._promotions.get(promotion_id)
        if not promotion:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                if field == 'rules' and value:
                    setattr(promotion, field, [r.model_dump() if hasattr(r, 'model_dump') else r for r in value])
                elif hasattr(promotion, field):
                    setattr(promotion, field, value)

        promotion.updated_at = datetime.utcnow()
        logger.info(f"Promotion updated: ID={promotion.id}")
        return promotion

    def delete_promotion(self, promotion_id: int) -> bool:
        """Delete a promotion."""
        if promotion_id in self._promotions:
            del self._promotions[promotion_id]
            logger.info(f"Promotion deleted: ID={promotion_id}")
            return True
        return False

    def list_promotions(
        self,
        status: Optional[PromotionStatus] = None,
        promotion_type: Optional[PromotionType] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> List[Promotion]:
        """List promotions with filtering and pagination."""
        promotions = list(self._promotions.values())

        if status is not None:
            promotions = [p for p in promotions if p.status == status]

        if promotion_type is not None:
            promotions = [p for p in promotions if p.promotion_type == promotion_type]

        if is_active is not None:
            promotions = [p for p in promotions if p.is_active == is_active]

        # Sort by created_at descending
        promotions.sort(key=lambda p: p.created_at, reverse=True)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        return promotions[start:end]

    def get_active_promotions(self) -> List[Promotion]:
        """Get all currently active promotions."""
        now = datetime.utcnow()
        return [
            p for p in self._promotions.values()
            if p.is_active and p.status == PromotionStatus.ACTIVE and p.start_time <= now <= p.end_time
        ]

    def activate_promotion(self, promotion_id: int) -> Optional[Promotion]:
        """Activate a promotion."""
        promotion = self._promotions.get(promotion_id)
        if promotion:
            promotion.status = PromotionStatus.ACTIVE
            promotion.is_active = True
            promotion.updated_at = datetime.utcnow()
        return promotion

    def deactivate_promotion(self, promotion_id: int) -> Optional[Promotion]:
        """Deactivate a promotion."""
        promotion = self._promotions.get(promotion_id)
        if promotion:
            promotion.status = PromotionStatus.CANCELLED
            promotion.is_active = False
            promotion.updated_at = datetime.utcnow()
        return promotion


# ============================================
# Coupon Model & Service
# ============================================

class Coupon:
    """Coupon model representing a coupon."""

    def __init__(
        self,
        id: int,
        code: str,
        coupon_type: CouponType,
        value: Decimal,
        promotion_id: Optional[int] = None,
        min_amount: Optional[Decimal] = None,
        max_discount: Optional[Decimal] = None,
        total_count: int = 1,
        used_count: int = 0,
        user_id: Optional[int] = None,
        valid_start: datetime = None,
        valid_end: datetime = None,
        status: CouponStatus = CouponStatus.ACTIVE,
        is_transferable: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.promotion_id = promotion_id
        self.code = code
        self.coupon_type = coupon_type
        self.value = value
        self.min_amount = min_amount
        self.max_discount = max_discount
        self.total_count = total_count
        self.used_count = used_count
        self.user_id = user_id
        self.valid_start = valid_start or datetime.utcnow()
        self.valid_end = valid_end or (datetime.utcnow() + timedelta(days=30))
        self.status = status
        self.is_transferable = is_transferable
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def remaining_count(self) -> int:
        """Get remaining coupon count."""
        return max(0, self.total_count - self.used_count)

    def is_valid(self, user_id: Optional[int] = None, order_amount: Optional[Decimal] = None) -> Tuple[bool, str]:
        """
        Check if coupon is valid.

        Returns:
            Tuple of (is_valid, message)
        """
        now = datetime.utcnow()

        # Check if coupon is active
        if self.status != CouponStatus.ACTIVE:
            return False, "优惠券已禁用"

        # Check validity period
        if now < self.valid_start:
            return False, "优惠券尚未开始"
        if now > self.valid_end:
            return False, "优惠券已过期"

        # Check remaining count
        if self.remaining_count <= 0:
            return False, "优惠券已用完"

        # Check user-specific restriction
        if self.user_id is not None and user_id is not None and self.user_id != user_id:
            return False, "此优惠券不适用于当前用户"

        # Check minimum amount
        if self.min_amount is not None and order_amount is not None and order_amount < self.min_amount:
            return False, f"订单金额需达到{self.min_amount}元"

        return True, "优惠券可用"

    def calculate_discount(self, order_amount: Decimal) -> Decimal:
        """Calculate discount amount for given order amount."""
        if self.coupon_type == CouponType.PERCENTAGE:
            return calculate_percentage_discount(order_amount, self.value, self.max_discount)
        else:  # FIXED
            return calculate_fixed_discount(order_amount, self.value)

    def to_response(self) -> CouponResponse:
        """Convert to CouponResponse schema."""
        return CouponResponse(
            id=self.id,
            promotion_id=self.promotion_id,
            code=self.code,
            coupon_type=self.coupon_type,
            value=self.value,
            min_amount=self.min_amount,
            max_discount=self.max_discount,
            total_count=self.total_count,
            used_count=self.used_count,
            user_id=self.user_id,
            valid_start=self.valid_start,
            valid_end=self.valid_end,
            status=self.status,
            is_transferable=self.is_transferable,
            remaining_count=self.remaining_count,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class CouponUsage:
    """Coupon usage record model."""

    def __init__(
        self,
        id: int,
        coupon_id: int,
        user_id: int,
        coupon_code: Optional[str] = None,
        order_id: Optional[str] = None,
        discount_amount: Optional[Decimal] = None,
        used_at: Optional[datetime] = None,
    ):
        self.id = id
        self.coupon_id = coupon_id
        self.coupon_code = coupon_code
        self.user_id = user_id
        self.order_id = order_id
        self.discount_amount = discount_amount
        self.used_at = used_at or datetime.utcnow()

    def to_response(self) -> CouponUsageResponse:
        """Convert to CouponUsageResponse schema."""
        return CouponUsageResponse(
            id=self.id,
            coupon_id=self.coupon_id,
            coupon_code=self.coupon_code,
            user_id=self.user_id,
            order_id=self.order_id,
            discount_amount=self.discount_amount,
            used_at=self.used_at,
        )


class CouponService:
    """Service for managing coupons."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._coupons: Dict[int, Coupon] = {}
        self._coupon_codes: Dict[str, int] = {}  # code -> id index
        self._coupon_usages: Dict[int, List[CouponUsage]] = {}  # coupon_id -> usages
        self._next_id: int = 1
        self._usage_next_id: int = 1
        self._config = config or {}

        # Seed sample coupons
        self._seed_coupons()

    def _seed_coupons(self) -> None:
        """Seed sample coupons for demonstration."""
        if self._coupons:
            return

        # Welcome coupon
        welcome = Coupon(
            id=self._next_id,
            code="WELCOME10",
            coupon_type=CouponType.FIXED,
            value=Decimal("10"),
            min_amount=Decimal("50"),
            total_count=1000,
            valid_start=datetime.utcnow() - timedelta(days=30),
            valid_end=datetime.utcnow() + timedelta(days=365),
        )
        self._coupons[welcome.id] = welcome
        self._coupon_codes[welcome.code] = welcome.id
        self._next_id += 1

        # Percentage discount coupon
        percent = Coupon(
            id=self._next_id,
            code="SUMMER20",
            coupon_type=CouponType.PERCENTAGE,
            value=Decimal("20"),
            min_amount=Decimal("100"),
            max_discount=Decimal("50"),
            total_count=500,
            valid_start=datetime.utcnow(),
            valid_end=datetime.utcnow() + timedelta(days=30),
        )
        self._coupons[percent.id] = percent
        self._coupon_codes[percent.code] = percent.id
        self._next_id += 1

        logger.info(f"Seeded {len(self._coupons)} sample coupons")

    def create_coupon(self, data: CouponCreate) -> Coupon:
        """
        Create a new coupon.

        Args:
            data: Coupon creation data

        Returns:
            The created Coupon instance
        """
        # Generate code if not provided
        code = data.code or generate_coupon_code()

        # Check for duplicate code
        if code in self._coupon_codes:
            code = generate_coupon_code()

        coupon = Coupon(
            id=self._next_id,
            code=code,
            coupon_type=data.coupon_type,
            value=data.value,
            promotion_id=data.promotion_id,
            min_amount=data.min_amount,
            max_discount=data.max_discount,
            total_count=data.total_count,
            user_id=data.user_id,
            valid_start=data.valid_start,
            valid_end=data.valid_end,
            is_transferable=data.is_transferable,
            metadata=data.metadata,
        )

        self._coupons[coupon.id] = coupon
        self._coupon_codes[coupon.code] = coupon.id
        self._coupon_usages[coupon.id] = []
        self._next_id += 1

        logger.info(f"Coupon created: ID={coupon.id}, Code={coupon.code}")
        return coupon

    def get_coupon(self, coupon_id: int) -> Optional[Coupon]:
        """Get a coupon by ID."""
        return self._coupons.get(coupon_id)

    def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """Get a coupon by code."""
        coupon_id = self._coupon_codes.get(code.upper())
        if coupon_id:
            return self._coupons.get(coupon_id)
        return None

    def validate_coupon(self, code: str, order_amount: Optional[Decimal] = None, user_id: Optional[int] = None) -> CouponValidateResponse:
        """
        Validate a coupon.

        Args:
            code: Coupon code
            order_amount: Order amount for validation
            user_id: User ID for user-specific validation

        Returns:
            CouponValidateResponse with validation result
        """
        coupon = self.get_coupon_by_code(code)

        if not coupon:
            return CouponValidateResponse(
                valid=False,
                message="优惠券不存在"
            )

        is_valid, message = coupon.is_valid(user_id, order_amount)

        if is_valid and order_amount is not None:
            discount = coupon.calculate_discount(order_amount)
            return CouponValidateResponse(
                valid=True,
                coupon=coupon.to_response(),
                discount_amount=discount,
                message=message
            )

        return CouponValidateResponse(
            valid=is_valid,
            coupon=coupon.to_response() if coupon else None,
            message=message
        )

    def redeem_coupon(self, code: str, user_id: int) -> Tuple[Optional[Coupon], str]:
        """
        Redeem/claim a coupon for a user.

        Args:
            code: Coupon code
            user_id: User ID

        Returns:
            Tuple of (Coupon or None, message)
        """
        coupon = self.get_coupon_by_code(code)

        if not coupon:
            return None, "优惠券不存在"

        is_valid, message = coupon.is_valid(user_id)

        if not is_valid:
            return None, message

        # Check user hasn't already redeemed this coupon (if user-specific)
        if coupon.user_id is not None and coupon.user_id != user_id:
            return None, "此优惠券不适用于当前用户"

        # Check if user already has this coupon
        user_usages = self._coupon_usages.get(coupon.id, [])
        user_redeemed = any(u.user_id == user_id for u in user_usages)
        if user_redeemed:
            return None, "您已领取过此优惠券"

        # Create redemption record
        usage = CouponUsage(
            id=self._usage_next_id,
            coupon_id=coupon.id,
            coupon_code=coupon.code,
            user_id=user_id,
        )
        self._coupon_usages.setdefault(coupon.id, []).append(usage)
        self._usage_next_id += 1

        logger.info(f"Coupon redeemed: Code={code}, User={user_id}")
        return coupon, "优惠券领取成功"

    def apply_coupon(self, code: str, user_id: int, order_id: str, order_amount: Decimal) -> Tuple[Optional[Decimal], str]:
        """
        Apply a coupon to an order.

        Args:
            code: Coupon code
            user_id: User ID
            order_id: Order ID
            order_amount: Order amount

        Returns:
            Tuple of (discount_amount or None, message)
        """
        coupon = self.get_coupon_by_code(code)

        if not coupon:
            return None, "优惠券不存在"

        is_valid, message = coupon.is_valid(user_id, order_amount)

        if not is_valid:
            return None, message

        # Calculate discount
        discount = coupon.calculate_discount(order_amount)

        # Update coupon usage with order info
        user_usages = self._coupon_usages.get(coupon.id, [])
        for usage in user_usages:
            if usage.user_id == user_id and usage.order_id is None:
                usage.order_id = order_id
                usage.discount_amount = discount
                break

        # Increment used count
        coupon.used_count += 1
        coupon.updated_at = datetime.utcnow()

        logger.info(f"Coupon applied: Code={code}, Order={order_id}, Discount={discount}")
        return discount, "优惠券已应用"

    def list_user_coupons(
        self,
        user_id: int,
        status: Optional[CouponStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> List[Coupon]:
        """List coupons for a user."""
        now = datetime.utcnow()
        user_coupons = []

        for coupon in self._coupons.values():
            if coupon.user_id is not None and coupon.user_id != user_id:
                continue

            usages = self._coupon_usages.get(coupon.id, [])
            has_redeemed = any(u.user_id == user_id for u in usages)

            if not has_redeemed:
                continue

            # Determine effective status
            effective_status = coupon.status
            if now > coupon.valid_end:
                effective_status = CouponStatus.EXPIRED
            elif coupon.remaining_count <= 0:
                effective_status = CouponStatus.USED

            if status and status != effective_status:
                continue

            user_coupons.append(coupon)

        user_coupons.sort(key=lambda c: c.valid_end, reverse=True)
        return user_coupons

    def get_usage_history(
        self,
        user_id: Optional[int] = None,
        coupon_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[CouponUsage], int]:
        """Get coupon usage history."""
        all_usages = []

        for usages in self._coupon_usages.values():
            for usage in usages:
                if user_id and usage.user_id != user_id:
                    continue
                if coupon_id and usage.coupon_id != coupon_id:
                    continue
                all_usages.append(usage)

        all_usages.sort(key=lambda u: u.used_at, reverse=True)

        # Paginate
        start = (page - 1) * limit
        end = start + limit

        return all_usages[start:end], len(all_usages)


# ============================================
# Flash Sale Model & Service
# ============================================

class FlashSale:
    """Flash sale model representing a flash sale item."""

    def __init__(
        self,
        id: int,
        product_id: int,
        flash_price: Decimal,
        promotion_id: Optional[int] = None,
        product_name: Optional[str] = None,
        original_price: Optional[Decimal] = None,
        stock: int = 0,
        sold_count: int = 0,
        max_per_user: int = 1,
        start_time: datetime = None,
        end_time: datetime = None,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.promotion_id = promotion_id
        self.product_id = product_id
        self.product_name = product_name
        self.flash_price = flash_price
        self.original_price = original_price
        self.stock = stock
        self.sold_count = sold_count
        self.max_per_user = max_per_user
        self.start_time = start_time or datetime.utcnow()
        self.end_time = end_time or (datetime.utcnow() + timedelta(hours=24))
        self.is_active = is_active
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def remaining_stock(self) -> int:
        """Get remaining stock."""
        return max(0, self.stock - self.sold_count)

    @property
    def is_sold_out(self) -> bool:
        """Check if sold out."""
        return self.remaining_stock <= 0

    @property
    def discount_rate(self) -> Optional[float]:
        """Calculate discount rate as percentage."""
        if self.original_price and self.original_price > 0:
            return float((1 - self.flash_price / self.original_price) * 100)
        return None

    @property
    def is_ongoing(self) -> bool:
        """Check if flash sale is currently ongoing."""
        now = datetime.utcnow()
        return (
            self.is_active and
            self.start_time <= now <= self.end_time and
            not self.is_sold_out
        )

    def is_valid_for_user(self, user_id: int, quantity: int = 1) -> Tuple[bool, str]:
        """
        Check if flash sale is valid for a user.

        Returns:
            Tuple of (is_valid, message)
        """
        now = datetime.utcnow()

        if not self.is_active:
            return False, "限时抢购已结束"

        if now < self.start_time:
            return False, "限时抢购尚未开始"

        if now > self.end_time:
            return False, "限时抢购已结束"

        if self.is_sold_out:
            return False, "已售罄"

        if quantity > self.max_per_user:
            return False, f"每人最多购买{self.max_per_user}件"

        return True, "可以购买"

    def purchase(self, user_id: int, quantity: int = 1) -> Tuple[bool, str]:
        """
        Attempt to purchase from flash sale.

        Args:
            user_id: User ID
            quantity: Quantity to purchase

        Returns:
            Tuple of (success, message)
        """
        is_valid, message = self.is_valid_for_user(user_id, quantity)

        if not is_valid:
            return False, message

        if quantity > self.remaining_stock:
            return False, "库存不足"

        # Update sold count
        self.sold_count += quantity
        self.updated_at = datetime.utcnow()

        logger.info(f"Flash sale purchase: ID={self.id}, User={user_id}, Quantity={quantity}")
        return True, "购买成功"

    def to_response(self) -> FlashSaleResponse:
        """Convert to FlashSaleResponse schema."""
        return FlashSaleResponse(
            id=self.id,
            promotion_id=self.promotion_id,
            product_id=self.product_id,
            product_name=self.product_name,
            flash_price=self.flash_price,
            original_price=self.original_price,
            discount_rate=self.discount_rate,
            stock=self.stock,
            sold_count=self.sold_count,
            remaining_stock=self.remaining_stock,
            max_per_user=self.max_per_user,
            start_time=self.start_time,
            end_time=self.end_time,
            is_active=self.is_active,
            is_ongoing=self.is_ongoing,
            is_sold_out=self.is_sold_out,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class FlashSaleService:
    """Service for managing flash sales."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._flash_sales: Dict[int, FlashSale] = {}
        self._product_flash_sales: Dict[int, List[int]] = {}  # product_id -> flash_sale_ids
        self._user_purchases: Dict[int, Dict[int, int]] = {}  # user_id -> {flash_sale_id: quantity}
        self._next_id: int = 1
        self._config = config or {}

        # Seed sample flash sales
        self._seed_flash_sales()

    def _seed_flash_sales(self) -> None:
        """Seed sample flash sales for demonstration."""
        if self._flash_sales:
            return

        # 128GB U盘 flash sale
        flash1 = FlashSale(
            id=self._next_id,
            product_id=1,
            product_name="傻福虾 U盘 128GB 银色",
            flash_price=Decimal("399"),
            original_price=Decimal("599"),
            stock=20,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=24),
        )
        self._flash_sales[flash1.id] = flash1
        self._product_flash_sales.setdefault(flash1.product_id, []).append(flash1.id)
        self._next_id += 1

        # 256GB U盘 flash sale
        flash2 = FlashSale(
            id=self._next_id,
            product_id=2,
            product_name="傻福虾 U盘 256GB 银色",
            flash_price=Decimal("699"),
            original_price=Decimal("1062"),
            stock=15,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=24),
        )
        self._flash_sales[flash2.id] = flash2
        self._product_flash_sales.setdefault(flash2.product_id, []).append(flash2.id)
        self._next_id += 1

        logger.info(f"Seeded {len(self._flash_sales)} sample flash sales")

    def create_flash_sale(self, data: FlashSaleCreate) -> FlashSale:
        """
        Create a new flash sale.

        Args:
            data: Flash sale creation data

        Returns:
            The created FlashSale instance
        """
        flash_sale = FlashSale(
            id=self._next_id,
            product_id=data.product_id,
            product_name=data.product_name,
            flash_price=data.flash_price,
            original_price=data.original_price,
            promotion_id=data.promotion_id,
            stock=data.stock,
            sold_count=data.sold_count,
            max_per_user=data.max_per_user,
            start_time=data.start_time,
            end_time=data.end_time,
            is_active=data.is_active,
            metadata=data.metadata,
        )

        self._flash_sales[flash_sale.id] = flash_sale
        self._product_flash_sales.setdefault(flash_sale.product_id, []).append(flash_sale.id)
        self._next_id += 1

        logger.info(f"Flash sale created: ID={flash_sale.id}, Product={flash_sale.product_id}")
        return flash_sale

    def get_flash_sale(self, flash_sale_id: int) -> Optional[FlashSale]:
        """Get a flash sale by ID."""
        return self._flash_sales.get(flash_sale_id)

    def get_flash_sale_by_product(self, product_id: int) -> Optional[FlashSale]:
        """Get current active flash sale for a product."""
        flash_sale_ids = self._product_flash_sales.get(product_id, [])
        now = datetime.utcnow()

        for fs_id in flash_sale_ids:
            fs = self._flash_sales.get(fs_id)
            if fs and fs.is_active and fs.start_time <= now <= fs.end_time and not fs.is_sold_out:
                return fs

        return None

    def update_flash_sale(self, flash_sale_id: int, data: FlashSaleCreate) -> Optional[FlashSale]:
        """Update a flash sale."""
        flash_sale = self._flash_sales.get(flash_sale_id)
        if not flash_sale:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and hasattr(flash_sale, field):
                setattr(flash_sale, field, value)

        flash_sale.updated_at = datetime.utcnow()
        logger.info(f"Flash sale updated: ID={flash_sale.id}")
        return flash_sale

    def delete_flash_sale(self, flash_sale_id: int) -> bool:
        """Delete a flash sale."""
        if flash_sale_id in self._flash_sales:
            flash_sale = self._flash_sales[flash_sale_id]
            if flash_sale.product_id in self._product_flash_sales:
                self._product_flash_sales[flash_sale.product_id].remove(flash_sale_id)
            del self._flash_sales[flash_sale_id]
            logger.info(f"Flash sale deleted: ID={flash_sale_id}")
            return True
        return False

    def get_flash_sales(
        self,
        is_active: Optional[bool] = None,
        is_ongoing: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[FlashSale], int]:
        """Get flash sales with filtering."""
        flash_sales = list(self._flash_sales.values())

        if is_active is not None:
            flash_sales = [fs for fs in flash_sales if fs.is_active == is_active]

        if is_ongoing:
            flash_sales = [fs for fs in flash_sales if fs.is_ongoing]

        flash_sales.sort(key=lambda fs: fs.start_time, reverse=True)

        # Paginate
        start = (page - 1) * limit
        end = start + limit

        return flash_sales[start:end], len(flash_sales)

    def get_ongoing_flash_sales(self) -> List[FlashSale]:
        """Get all currently ongoing flash sales."""
        return [fs for fs in self._flash_sales.values() if fs.is_ongoing]

    def purchase(self, flash_sale_id: int, user_id: int, quantity: int = 1) -> Tuple[bool, str]:
        """
        Attempt to purchase from flash sale.

        Args:
            flash_sale_id: Flash sale ID
            user_id: User ID
            quantity: Quantity to purchase

        Returns:
            Tuple of (success, message)
        """
        flash_sale = self._flash_sales.get(flash_sale_id)

        if not flash_sale:
            return False, "限时抢购不存在"

        # Check user's purchase history
        user_purchases = self._user_purchases.setdefault(user_id, {})
        previous_purchases = user_purchases.get(flash_sale_id, 0)

        if previous_purchases + quantity > flash_sale.max_per_user:
            return False, f"您已购买{previous_purchases}件，每人限购{flash_sale.max_per_user}件"

        success, message = flash_sale.purchase(user_id, quantity)

        if success:
            user_purchases[flash_sale_id] = previous_purchases + quantity

        return success, message


# ============================================
# Singleton Instances
# ============================================

promotion_service = PromotionService()
coupon_service = CouponService()
flash_sale_service = FlashSaleService()
