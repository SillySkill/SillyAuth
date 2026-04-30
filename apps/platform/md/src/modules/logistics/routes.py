"""
Logistics Module Routes
FastAPI routes for logistics management endpoints

Provides express companies, shipping templates, tracking, and label generation
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request

from .schemas import (
    ExpressCompanyResponse,
    ShippingTemplateResponse,
    ShippingTemplateDetailResponse,
    ShippingTemplateCreate,
    ShippingTemplateUpdate,
    ShippingCalculateRequest,
    ShippingCalculateResponse,
    TrackingInfo,
    TrackingResponse,
    ExpressLabelRequest,
    ExpressLabelResponse,
    LogisticsResponse,
)
from .services import LogisticsService, get_logistics_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/logistics", tags=["物流管理"])


# ============================================================================
# Helper Functions
# ============================================================================

def get_current_user_id(request: Request) -> int:
    """
    Get current authenticated user ID from JWT token.

    Args:
        request: FastAPI request object with Authorization header

    Returns:
        User ID of the authenticated user.

    Raises:
        HTTPException: If token is missing or invalid
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.replace("Bearer ", "")
    try:
        from modules.auth.services import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id", 0)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_logistics_svc() -> LogisticsService:
    """Get logistics service instance."""
    return get_logistics_service()


# ============================================================================
# Express Company Routes
# ============================================================================

@router.get("/companies", response_model=List[ExpressCompanyResponse])
async def list_express_companies(
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    List all express companies.

    Returns a list of all available express companies for shipping.
    """
    companies = service.express_company_service.list_companies(status=status)
    return [c.to_response() for c in companies]


@router.get("/companies/{company_code}", response_model=ExpressCompanyResponse)
async def get_express_company(
    company_code: str,
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Get express company details by code.

    Args:
        company_code: Express company code (e.g., shunfeng, yuantong)
    """
    company = service.express_company_service.get_company(company_code)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="快递公司不存在"
        )

    return company.to_response()


# ============================================================================
# Shipping Template Routes
# ============================================================================

@router.get("/templates", response_model=List[ShippingTemplateResponse])
async def list_shipping_templates(
    status: Optional[str] = Query(None, description="Filter by status"),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    List all shipping templates.

    Returns shipping templates that define shipping fees and rules.
    """
    templates = service.shipping_template_service.list_templates(status=status)
    return [t.to_response() for t in templates]


@router.get("/templates/{template_id}", response_model=ShippingTemplateDetailResponse)
async def get_shipping_template(
    template_id: int,
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Get shipping template details with rules.

    Args:
        template_id: Template ID
    """
    template = service.shipping_template_service.get_template(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运费模板不存在"
        )

    return template.to_detail_response()


@router.post("/templates", response_model=ShippingTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_shipping_template(
    data: ShippingTemplateCreate,
    user_id: int = Depends(get_current_user_id),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Create a new shipping template.

    Creates a new shipping template with fee rules.
    """
    try:
        template = service.shipping_template_service.create_template(
            name=data.name,
            template_type=data.template_type.value,
            is_free_shipping=data.is_free_shipping,
            default_fee=data.default_fee
        )

        logger.info(f"Shipping template created: ID={template.id}, Name={template.name}")

        return template.to_response()

    except Exception as e:
        logger.error(f"Failed to create shipping template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建运费模板失败: {str(e)}"
        )


@router.put("/templates/{template_id}", response_model=ShippingTemplateResponse)
async def update_shipping_template(
    template_id: int,
    data: ShippingTemplateUpdate,
    user_id: int = Depends(get_current_user_id),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Update a shipping template.

    Args:
        template_id: Template ID
    """
    template = service.shipping_template_service.update_template(
        template_id=template_id,
        name=data.name,
        template_type=data.template_type.value if data.template_type else None,
        is_free_shipping=data.is_free_shipping,
        default_fee=data.default_fee
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运费模板不存在"
        )

    return template.to_response()


# ============================================================================
# Shipping Calculation Routes
# ============================================================================

@router.post("/calculate", response_model=ShippingCalculateResponse)
async def calculate_shipping(
    request: ShippingCalculateRequest,
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Calculate shipping fees for order items.

    Calculates shipping fees based on:
    - Order items (weight, quantity)
    - Shipping address
    - Available express companies

    Returns available shipping options with fees.
    """
    try:
        result = service.calculate_shipping(request)
        logger.info(
            f"Shipping calculated: weight={result.total_weight}kg, "
            f"options={len(result.options)}, free_shipping={result.is_free_shipping}"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to calculate shipping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"运费计算失败: {str(e)}"
        )


# ============================================================================
# Tracking Routes
# ============================================================================

@router.get("/track/{tracking_number}", response_model=TrackingResponse)
async def track_shipment(
    tracking_number: str,
    express_company: Optional[str] = Query(None, description="Express company code"),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Track a shipment by tracking number.

    Queries the express company API to get the latest tracking information.

    Args:
        tracking_number: The tracking number to query
        express_company: Optional express company code (auto-detected if not provided)
    """
    try:
        tracking_info = await service.get_tracking_info(
            tracking_number=tracking_number,
            express_company=express_company
        )

        return TrackingResponse(
            success=True,
            message="查询成功",
            data=tracking_info
        )

    except Exception as e:
        logger.error(f"Failed to track shipment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"物流查询失败: {str(e)}"
        )


@router.get("/track", response_model=TrackingResponse)
async def track_shipment_with_company(
    tracking_number: str = Query(..., description="Tracking number"),
    express_company: str = Query(..., description="Express company code"),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Track a shipment with explicit express company.

    Alternative endpoint for tracking with explicit company code.

    Args:
        tracking_number: The tracking number to query
        express_company: Express company code
    """
    return await track_shipment(tracking_number, express_company, service)


# ============================================================================
# Express Label Routes
# ============================================================================

@router.post("/print", response_model=ExpressLabelResponse)
async def generate_express_label(
    request: ExpressLabelRequest,
    user_id: int = Depends(get_current_user_id),
    service: LogisticsService = Depends(get_logistics_svc)
):
    """
    Generate express label data for printing.

    Generates label data including tracking number for printing.
    This is typically called when an order is shipped.

    Args:
        request: Express label request with sender and receiver info
    """
    try:
        label_data = service.generate_express_label(request)

        logger.info(
            f"Express label generated: order_id={request.order_id}, "
            f"express={request.express_company}, "
            f"tracking={label_data.tracking_number}"
        )

        return ExpressLabelResponse(
            success=True,
            message="面单生成成功",
            data=label_data
        )

    except Exception as e:
        logger.error(f"Failed to generate express label: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"面单生成失败: {str(e)}"
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check(service: LogisticsService = Depends(get_logistics_svc)):
    """
    Health check for logistics module.

    Returns basic module status and available services.
    """
    return LogisticsResponse(
        success=True,
        message="物流模块运行正常",
        data={
            "module": "logistics",
            "express_companies": len(service.express_company_service.list_companies()),
            "shipping_templates": len(service.shipping_template_service.list_templates())
        }
    )
