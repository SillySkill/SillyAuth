"""
Shunfeng (顺丰速运) Express Client
"""

from typing import Dict, Any, Optional
import logging

from .base import BaseExpressClient

logger = logging.getLogger(__name__)


class ShunfengClient(BaseExpressClient):
    """Shunfeng Express API client."""

    @property
    def code(self) -> str:
        return "shunfeng"

    @property
    def name(self) -> str:
        return "顺丰速运"

    def get_tracking_url(self, tracking_number: str) -> str:
        """Get Shunfeng tracking URL."""
        return f"https://www.sf-express.com/sf-service-owf-web/query/{tracking_number}"

    async def query_tracking(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query Shunfeng tracking information.

        In production, this would call the Shunfeng API.
        For now, returns mock data.

        Args:
            tracking_number: Shunfeng tracking number

        Returns:
            Tracking information dictionary
        """
        # TODO: Implement actual Shunfeng API call
        # Shunfeng API documentation: https://www.sf-express.com/sf-service-owf-web/

        logger.info(f"Querying Shunfeng tracking for: {tracking_number}")

        # Mock data for development
        return {
            "success": True,
            "data": {
                "express_company": self.code,
                "express_company_name": self.name,
                "tracking_number": tracking_number,
                "status": "in_transit",
                "status_text": "运输中",
                "traces": [
                    {
                        "time": "2024-01-15 09:30:00",
                        "status": "已揽收",
                        "location": "深圳市福田区",
                        "description": "顺丰速运已取件"
                    },
                    {
                        "time": "2024-01-15 11:00:00",
                        "status": "运输中",
                        "location": "深圳市",
                        "description": "快件已到达深圳分拨中心"
                    },
                    {
                        "time": "2024-01-15 18:00:00",
                        "status": "运输中",
                        "location": "广州市",
                        "description": "快件已到达广州分拨中心"
                    }
                ],
                "last_update": "2024-01-15T18:00:00",
                "estimated_delivery": "2024-01-16"
            }
        }

    def calculate_fee(
        self,
        weight: float,
        address: Dict[str, str],
        calculate_type: str = "express"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate Shunfeng shipping fee.

        Args:
            weight: Package weight in kg
            address: Address information
            calculate_type: Calculation type (express/economic)

        Returns:
            Fee calculation result
        """
        # Shunfeng pricing (simplified)
        province = address.get("province", "")

        # Base fees by region
        base_fee = 13.0  # Starting from 13 yuan

        # Remote areas surcharge
        remote_areas = ["西藏", "新疆", "青海", "甘肃", "内蒙古", "宁夏", "海南"]
        if province in remote_areas:
            base_fee = 23.0
        elif province in ["北京", "上海", "广州", "深圳", "杭州", "南京"]:
            base_fee = 13.0
        else:
            base_fee = 15.0

        # Weight calculation
        if weight <= 1:
            fee = base_fee
        else:
            extra_weight = weight - 1
            if calculate_type == "economic":
                fee = base_fee + extra_weight * 5.0
            else:
                fee = base_fee + extra_weight * 10.0

        # Check free shipping
        total_price = address.get("total_price", 0)
        is_free = total_price >= 99

        return {
            "fee": round(fee, 2),
            "is_free": is_free,
            "estimated_days": "1-2天" if province not in ["西藏", "新疆", "海南"] else "3-5天",
            "is_recommend": True  # Shunfeng is recommended for fast delivery
        }
