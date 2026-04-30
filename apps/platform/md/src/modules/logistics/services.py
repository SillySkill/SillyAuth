"""
Logistics Module Services
Business logic for logistics operations
"""

import uuid
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

from .schemas import (
    ExpressCompanyResponse,
    ShippingTemplateResponse,
    ShippingTemplateDetailResponse,
    ShippingTemplateRule,
    ShippingCalculateRequest,
    ShippingCalculateResponse,
    ShippingOption,
    TrackingInfo,
    TrackingTrace,
    LogisticsStatus,
    ExpressLabelData,
    ExpressLabelRequest,
    RegionResponse,
)
from .clients import get_express_client, get_all_clients, BaseExpressClient

logger = logging.getLogger(__name__)


# ============================================
# Express Company Service
# ============================================

class ExpressCompany:
    """Express company model."""

    def __init__(
        self,
        id: int,
        code: str,
        name: str,
        logo_url: Optional[str] = None,
        tracking_url: Optional[str] = None,
        status: str = "active",
        sort_order: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.code = code
        self.name = name
        self.logo_url = logo_url
        self.tracking_url = tracking_url
        self.status = status
        self.sort_order = sort_order
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

    def to_response(self) -> ExpressCompanyResponse:
        """Convert to response schema."""
        return ExpressCompanyResponse(
            id=self.id,
            code=self.code,
            name=self.name,
            logo_url=self.logo_url,
            tracking_url=self.tracking_url,
            status=self.status,
            sort_order=self.sort_order,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class ExpressCompanyService:
    """Service for managing express companies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the service."""
        self._companies: Dict[str, ExpressCompany] = {}
        self._next_id = 1
        self._config = config or {}
        self._init_default_companies()

    def _init_default_companies(self):
        """Initialize default express companies."""
        default_companies = [
            {"code": "shunfeng", "name": "顺丰速运", "sort_order": 1},
            {"code": "yuantong", "name": "圆通速递", "sort_order": 2},
            {"code": "zhongtong", "name": "中通快递", "sort_order": 3},
            {"code": "yunda", "name": "韵达快递", "sort_order": 4},
            {"code": "jtexpress", "name": "极兔速递", "sort_order": 5},
            {"code": "sto", "name": "申通快递", "sort_order": 6},
            {"code": "ems", "name": "EMS", "sort_order": 7},
        ]

        for company_data in default_companies:
            self._companies[company_data["code"]] = ExpressCompany(
                id=self._next_id,
                code=company_data["code"],
                name=company_data["name"],
                sort_order=company_data["sort_order"]
            )
            self._next_id += 1

    def list_companies(self, status: Optional[str] = None) -> List[ExpressCompany]:
        """List all express companies."""
        companies = list(self._companies.values())
        if status:
            companies = [c for c in companies if c.status == status]
        companies.sort(key=lambda c: c.sort_order)
        return companies

    def get_company(self, code: str) -> Optional[ExpressCompany]:
        """Get express company by code."""
        return self._companies.get(code)

    def get_company_by_id(self, company_id: int) -> Optional[ExpressCompany]:
        """Get express company by ID."""
        for company in self._companies.values():
            if company.id == company_id:
                return company
        return None


# ============================================
# Shipping Template Service
# ============================================

class ShippingTemplate:
    """Shipping template model."""

    def __init__(
        self,
        id: int,
        name: str,
        template_type: str = "by_weight",
        is_free_shipping: bool = False,
        default_fee: Optional[Decimal] = None,
        status: str = "active",
        rules: Optional[List[Dict]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.template_type = template_type
        self.is_free_shipping = is_free_shipping
        self.default_fee = default_fee
        self.status = status
        self.rules = rules or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

    def to_response(self) -> ShippingTemplateResponse:
        """Convert to response schema."""
        return ShippingTemplateResponse(
            id=self.id,
            name=self.name,
            template_type=self.template_type,
            is_free_shipping=self.is_free_shipping,
            default_fee=self.default_fee,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def to_detail_response(self) -> ShippingTemplateDetailResponse:
        """Convert to detail response with rules."""
        rules = [
            ShippingTemplateRule(
                id=rule.get("id", 0),
                template_id=self.id,
                region_ids=rule.get("region_ids", []),
                region_names=rule.get("region_names", []),
                first_unit=rule.get("first_unit", 1.0),
                first_fee=Decimal(str(rule.get("first_fee", 0))),
                continue_unit=rule.get("continue_unit", 1.0),
                continue_fee=Decimal(str(rule.get("continue_fee", 0)))
            )
            for rule in self.rules
        ]
        return ShippingTemplateDetailResponse(
            id=self.id,
            name=self.name,
            template_type=self.template_type,
            is_free_shipping=self.is_free_shipping,
            default_fee=self.default_fee,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            rules=rules
        )


class ShippingTemplateService:
    """Service for managing shipping templates."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the service."""
        self._templates: Dict[int, ShippingTemplate] = {}
        self._next_id = 1
        self._config = config or {}
        self._init_default_templates()

    def _init_default_templates(self):
        """Initialize default shipping templates."""
        # Template 1: Free shipping over 99
        self._templates[1] = ShippingTemplate(
            id=1,
            name="全场包邮",
            template_type="by_weight",
            is_free_shipping=True,
            default_fee=Decimal("0"),
            rules=[]
        )

        # Template 2: Standard shipping
        default_rule = {
            "id": 1,
            "region_ids": [],
            "region_names": ["全国"],
            "first_unit": 1.0,
            "first_fee": 10.0,
            "continue_unit": 1.0,
            "continue_fee": 5.0
        }

        self._templates[2] = ShippingTemplate(
            id=2,
            name="标准快递",
            template_type="by_weight",
            is_free_shipping=False,
            default_fee=Decimal("10"),
            rules=[default_rule]
        )

        # Template 3: Express shipping
        express_rule = {
            "id": 2,
            "region_ids": [],
            "region_names": ["全国"],
            "first_unit": 1.0,
            "first_fee": 15.0,
            "continue_unit": 1.0,
            "continue_fee": 8.0
        }

        self._templates[3] = ShippingTemplate(
            id=3,
            name="次日达",
            template_type="by_weight",
            is_free_shipping=False,
            default_fee=Decimal("15"),
            rules=[express_rule]
        )

        self._next_id = 4

    def create_template(
        self,
        name: str,
        template_type: str = "by_weight",
        is_free_shipping: bool = False,
        default_fee: Optional[Decimal] = None
    ) -> ShippingTemplate:
        """Create a new shipping template."""
        template = ShippingTemplate(
            id=self._next_id,
            name=name,
            template_type=template_type,
            is_free_shipping=is_free_shipping,
            default_fee=default_fee
        )
        self._templates[template.id] = template
        self._next_id += 1
        return template

    def get_template(self, template_id: int) -> Optional[ShippingTemplate]:
        """Get shipping template by ID."""
        return self._templates.get(template_id)

    def list_templates(self, status: Optional[str] = None) -> List[ShippingTemplate]:
        """List all shipping templates."""
        templates = list(self._templates.values())
        if status:
            templates = [t for t in templates if t.status == status]
        return templates

    def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        template_type: Optional[str] = None,
        is_free_shipping: Optional[bool] = None,
        default_fee: Optional[Decimal] = None
    ) -> Optional[ShippingTemplate]:
        """Update a shipping template."""
        template = self._templates.get(template_id)
        if not template:
            return None

        if name is not None:
            template.name = name
        if template_type is not None:
            template.template_type = template_type
        if is_free_shipping is not None:
            template.is_free_shipping = is_free_shipping
        if default_fee is not None:
            template.default_fee = default_fee

        template.updated_at = datetime.utcnow()
        return template


# ============================================
# Logistics Service
# ============================================

class LogisticsService:
    """Main service for logistics operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the logistics service."""
        self._config = config or {}
        self._express_company_service = ExpressCompanyService(config)
        self._shipping_template_service = ShippingTemplateService(config)

        # Tracking cache
        self._tracking_cache: Dict[str, TrackingInfo] = {}

        # Default free shipping threshold
        self._free_shipping_threshold = Decimal(
            str(self._config.get("shipping", {}).get("free_shipping_threshold", 99))
        )

    @property
    def express_company_service(self) -> ExpressCompanyService:
        """Get express company service."""
        return self._express_company_service

    @property
    def shipping_template_service(self) -> ShippingTemplateService:
        """Get shipping template service."""
        return self._shipping_template_service

    def calculate_shipping(
        self,
        request: ShippingCalculateRequest
    ) -> ShippingCalculateResponse:
        """
        Calculate shipping fees for order items.

        Args:
            request: Shipping calculation request

        Returns:
            Shipping calculation response with available options
        """
        # Calculate total weight
        total_weight = sum(item.weight * item.quantity for item in request.items)

        # Get total price for free shipping check
        total_price = Decimal("0")
        for item in request.items:
            if item.price:
                total_price += item.price * item.quantity

        is_free_shipping = total_price >= self._free_shipping_threshold

        # Build address dict for fee calculation
        address_dict = {
            "province": request.address.province,
            "city": request.address.city,
            "district": request.address.district,
            "total_price": float(total_price)
        }

        # Get all express companies
        companies = self._express_company_service.list_companies(status="active")

        # Calculate fees for each company
        options = []
        for company in companies:
            client = get_express_client(company.code, self._config)
            fee_info = client.calculate_fee(
                weight=total_weight,
                address=address_dict,
                calculate_type=request.calculate_type.value
            )

            if fee_info:
                option = ShippingOption(
                    express_company_code=company.code,
                    express_company_name=company.name,
                    express_company_logo=company.logo_url,
                    fee=Decimal(str(fee_info["fee"])),
                    estimated_days=fee_info.get("estimated_days"),
                    is_free=fee_info.get("is_free", False) or is_free_shipping,
                    is_recommend=fee_info.get("is_recommend", False)
                )
                options.append(option)

        # Sort by: free first, then by recommend, then by fee
        options.sort(key=lambda x: (
            0 if x.is_free else 1,
            0 if x.is_recommend else 1,
            float(x.fee)
        ))

        return ShippingCalculateResponse(
            total_weight=round(total_weight, 2),
            free_shipping_threshold=self._free_shipping_threshold,
            is_free_shipping=is_free_shipping,
            options=options
        )

    async def get_tracking_info(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> TrackingInfo:
        """
        Get tracking information for a shipment.

        Args:
            tracking_number: Tracking number
            express_company: Express company code (optional)

        Returns:
            Tracking information
        """
        # Check cache first
        cache_key = f"{express_company or ''}_{tracking_number}"
        if cache_key in self._tracking_cache:
            cached = self._tracking_cache[cache_key]
            # Check if cache is still valid (1 hour)
            if cached.last_update:
                age = (datetime.utcnow() - cached.last_update).total_seconds()
                if age < 3600:
                    return cached

        # Get express client
        company_code = express_company
        if not company_code:
            # Try to detect company from tracking number
            company_code = self._detect_express_company(tracking_number)

        client = get_express_client(company_code or "kd100", self._config)

        # Query tracking
        result = await client.query_tracking(tracking_number, express_company)

        if result.get("success") and result.get("data"):
            data = result["data"]
            traces = [
                TrackingTrace(
                    time=trace["time"],
                    status=trace["status"],
                    location=trace.get("location"),
                    description=trace.get("description")
                )
                for trace in data.get("traces", [])
            ]

            tracking_info = TrackingInfo(
                express_company=data.get("express_company", company_code or "unknown"),
                express_company_name=data.get("express_company_name", "未知"),
                tracking_number=tracking_number,
                status=LogisticsStatus(data.get("status", "unknown")),
                status_text=data.get("status_text", "未知状态"),
                traces=traces,
                last_update=datetime.fromisoformat(data["last_update"]) if data.get("last_update") else None,
                estimated_delivery=data.get("estimated_delivery")
            )

            # Update cache
            self._tracking_cache[cache_key] = tracking_info
            return tracking_info

        # Return empty tracking info if query failed
        return TrackingInfo(
            express_company=company_code or "unknown",
            express_company_name="未知",
            tracking_number=tracking_number,
            status=LogisticsStatus.UNKNOWN,
            status_text="查询失败",
            traces=[]
        )

    def _detect_express_company(self, tracking_number: str) -> Optional[str]:
        """
        Detect express company from tracking number pattern.

        Args:
            tracking_number: Tracking number

        Returns:
            Express company code or None
        """
        # Common tracking number patterns
        patterns = {
            "shunfeng": ["SF", "sf", "SF1"],
            "yuantong": ["YT", "YT0", "YT1"],
            "zhongtong": ["ZT", "ZT0", "YT7"],
            "yunda": ["YD", "YD0"],
            "jtexpress": ["JT", "JT0"],
            "sto": ["STO", "ST"],
            "ems": ["E", "EA", "EB", "R", "RA", "RB"]
        }

        tracking_number = tracking_number.upper()

        for company, prefixes in patterns.items():
            for prefix in prefixes:
                if tracking_number.startswith(prefix):
                    return company

        return None

    def generate_express_label(self, request: ExpressLabelRequest) -> ExpressLabelData:
        """
        Generate express label data for printing.

        Args:
            request: Express label request

        Returns:
            Express label data
        """
        # Get express company info
        company = self._express_company_service.get_company(request.express_company)

        # Generate tracking number (in production, this would come from the API)
        tracking_number = self._generate_tracking_number(request.express_company)

        return ExpressLabelData(
            order_id=request.order_id,
            express_company=request.express_company,
            express_company_name=company.name if company else "未知",
            tracking_number=tracking_number,
            sender={
                "name": request.sender_name,
                "phone": request.sender_phone,
                "address": request.sender_address
            },
            receiver={
                "name": request.receiver_name,
                "phone": request.receiver_phone,
                "address": request.receiver_address
            },
            goods_name=request.goods_name,
            goods_weight=request.goods_weight,
            created_at=datetime.utcnow()
        )

    def _generate_tracking_number(self, express_company: str) -> str:
        """
        Generate a tracking number.

        In production, this would call the express company's API
        to get a real tracking number.

        Args:
            express_company: Express company code

        Returns:
            Generated tracking number
        """
        # For development, generate a mock tracking number
        prefix_map = {
            "shunfeng": "SF",
            "yuantong": "YT",
            "zhongtong": "YT",
            "yunda": "YD",
            "jtexpress": "JT"
        }

        prefix = prefix_map.get(express_company, "XX")
        import random
        number = ''.join([str(random.randint(0, 9)) for _ in range(12)])

        return f"{prefix}{number}"


# Singleton instance
logistics_service = LogisticsService()


def get_logistics_service(config: Optional[Dict[str, Any]] = None) -> LogisticsService:
    """
    Get logistics service instance.

    Args:
        config: Optional configuration

    Returns:
        LogisticsService instance
    """
    global logistics_service
    if config:
        logistics_service = LogisticsService(config)
    return logistics_service
