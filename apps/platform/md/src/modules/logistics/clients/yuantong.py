"""
Yuantong (圆通速递) Express Client
"""

from typing import Dict, Any, Optional
import logging

from .base import BaseExpressClient

logger = logging.getLogger(__name__)


class YuantongClient(BaseExpressClient):
    """Yuantong Express API client."""

    @property
    def code(self) -> str:
        return "yuantong"

    @property
    def name(self) -> str:
        return "圆通速递"

    def get_tracking_url(self, tracking_number: str) -> str:
        """Get Yuantong tracking URL."""
        return f"https://www.yto.net.cn/track/trace?billCode={tracking_number}"

    async def query_tracking(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query Yuantong tracking information.

        Args:
            tracking_number: Yuantong tracking number

        Returns:
            Tracking information dictionary
        """
        # TODO: Implement actual Yuantong API call
        # Yuantong API documentation: https://open.yto.net.cn/

        logger.info(f"Querying Yuantong tracking for: {tracking_number}")

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
                        "time": "2024-01-15 10:00:00",
                        "status": "已揽收",
                        "location": "上海市浦东新区",
                        "description": "圆通速递已取件"
                    },
                    {
                        "time": "2024-01-15 15:00:00",
                        "status": "运输中",
                        "location": "上海市",
                        "description": "快件已到达上海转运中心"
                    },
                    {
                        "time": "2024-01-16 08:00:00",
                        "status": "运输中",
                        "location": "杭州市",
                        "description": "快件已到达杭州转运中心"
                    }
                ],
                "last_update": "2024-01-16T08:00:00",
                "estimated_delivery": "2024-01-17"
            }
        }

    def calculate_fee(
        self,
        weight: float,
        address: Dict[str, str],
        calculate_type: str = "express"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate Yuantong shipping fee.

        Args:
            weight: Package weight in kg
            address: Address information
            calculate_type: Calculation type

        Returns:
            Fee calculation result
        """
        # Yuantong pricing (simplified)
        province = address.get("province", "")

        # Base fees by region
        base_fee = 8.0

        # Remote areas surcharge
        remote_areas = ["西藏", "新疆", "青海", "甘肃", "内蒙古", "宁夏", "海南"]
        if province in remote_areas:
            base_fee = 18.0
        elif province in ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉"]:
            base_fee = 8.0
        else:
            base_fee = 10.0

        # Weight calculation
        if weight <= 1:
            fee = base_fee
        else:
            extra_weight = weight - 1
            fee = base_fee + extra_weight * 4.0

        # Check free shipping
        total_price = address.get("total_price", 0)
        is_free = total_price >= 99

        return {
            "fee": round(fee, 2),
            "is_free": is_free,
            "estimated_days": "3-5天",
            "is_recommend": False
        }
