"""
Kuaidi100 (快递100) Express Client
Unified tracking API through Kuaidi100
"""

from typing import Dict, Any, Optional
import logging
import aiohttp
import json

from .base import BaseExpressClient

logger = logging.getLogger(__name__)


class Kd100Client(BaseExpressClient):
    """Kuaidi100 unified tracking API client."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Kuaidi100 client."""
        super().__init__(config)
        self.api_url = self.config.get("api_url", "https://api.kuaidi100.com/api")
        self.app_key = self.config.get("app_key", "")

    @property
    def code(self) -> str:
        return "kd100"

    @property
    def name(self) -> str:
        return "快递100"

    def get_tracking_url(self, tracking_number: str, express_company: Optional[str] = None) -> str:
        """Get Kuaidi100 tracking URL."""
        if express_company:
            return f"https://www.kuaidi100.com/frame/result/{express_company}/{tracking_number}"
        return f"https://www.kuaidi100.com/?com={express_company or ''}&nu={tracking_number}"

    async def query_tracking(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query tracking information through Kuaidi100 API.

        Args:
            tracking_number: Tracking number
            express_company: Express company code (optional, will auto-detect if not provided)

        Returns:
            Tracking information dictionary
        """
        logger.info(f"Querying Kuaidi100 for tracking: {tracking_number}")

        # If no app key, return mock data
        if not self.app_key:
            logger.warning("Kuaidi100 app_key not configured, returning mock data")
            return await self._mock_tracking(tracking_number, express_company)

        try:
            # Build request URL
            url = f"{self.api_url}?id={self.app_key}&com={express_company or ''}&nu={tracking_number}&show=0&muti=1&order=desc"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_kd100_response(data, tracking_number, express_company)
                    else:
                        logger.error(f"Kuaidi100 API error: {response.status}")
                        return await self._mock_tracking(tracking_number, express_company)

        except Exception as e:
            logger.error(f"Kuaidi100 API error: {e}")
            return await self._mock_tracking(tracking_number, express_company)

    def _parse_kd100_response(
        self,
        data: Dict[str, Any],
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse Kuaidi100 API response."""
        # Kuaidi100 returns data in 'data' field with 'lastResult'
        last_result = data.get("lastResult", {})

        if not last_result:
            return {
                "success": False,
                "message": data.get("message", "查询失败"),
                "data": None
            }

        traces = []
        for item in last_result.get("data", []):
            traces.append({
                "time": item.get("ftime", item.get("time", "")),
                "status": item.get("context", ""),
                "location": item.get("location", ""),
                "description": item.get("context", "")
            })

        status_map = {
            "200": "in_transit",
            "201": "delivered",
            "301": "returned",
            "302": "exception"
        }

        status = last_result.get("state", "0")
        status_text_map = {
            "0": "pending",
            "1": "in_transit",
            "2": "delivered",
            "3": "returned",
            "4": "exception"
        }

        return {
            "success": True,
            "data": {
                "express_company": express_company or last_result.get("com", "unknown"),
                "express_company_name": self._get_company_name(express_company or last_result.get("com", "")),
                "tracking_number": tracking_number,
                "status": status_text_map.get(status, "unknown"),
                "status_text": traces[-1]["status"] if traces else "未知状态",
                "traces": traces,
                "last_update": traces[0]["time"] if traces else None
            }
        }

    async def _mock_tracking(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return mock tracking data for development."""
        company_name = self._get_company_name(express_company or "unknown")

        return {
            "success": True,
            "data": {
                "express_company": express_company or "unknown",
                "express_company_name": company_name,
                "tracking_number": tracking_number,
                "status": "in_transit",
                "status_text": "运输中",
                "traces": [
                    {
                        "time": "2024-01-15 10:00:00",
                        "status": "已揽收",
                        "location": "发货城市",
                        "description": f"{company_name}已揽收快件"
                    },
                    {
                        "time": "2024-01-15 14:00:00",
                        "status": "运输中",
                        "location": "中转中心",
                        "description": "快件已到达中转中心"
                    },
                    {
                        "time": "2024-01-16 08:00:00",
                        "status": "派送中",
                        "location": "目的城市",
                        "description": "快件正在派送中"
                    }
                ],
                "last_update": "2024-01-16T08:00:00"
            }
        }

    def _get_company_name(self, company_code: str) -> str:
        """Get company name from code."""
        company_names = {
            "shunfeng": "顺丰速运",
            "yuantong": "圆通速递",
            "zhongtong": "中通快递",
            "yunda": "韵达快递",
            "jtexpress": "极兔速递",
            "ems": "EMS",
            "sto": "申通快递"
        }
        return company_names.get(company_code.lower(), company_code)

    def calculate_fee(
        self,
        weight: float,
        address: Dict[str, str],
        calculate_type: str = "express"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate average shipping fee based on all carriers.

        Args:
            weight: Package weight in kg
            address: Address information
            calculate_type: Calculation type

        Returns:
            Fee calculation result
        """
        # Kuaidi100 doesn't provide fee calculation API
        # Return average fee for reference
        province = address.get("province", "")

        base_fee = 8.0
        remote_areas = ["西藏", "新疆", "青海", "甘肃", "内蒙古", "宁夏", "海南"]
        if province in remote_areas:
            base_fee = 15.0

        extra_fee = max(0, weight - 1) * 4.0
        fee = base_fee + extra_fee

        # Check free shipping
        total_price = address.get("total_price", 0)
        is_free = total_price >= 99

        return {
            "fee": round(fee, 2),
            "is_free": is_free,
            "estimated_days": "3-5天",
            "is_recommend": False
        }
