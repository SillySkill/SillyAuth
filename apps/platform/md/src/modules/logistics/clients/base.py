"""
Logistics Module - Express Company Clients
Base interface and implementations for express company APIs
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseExpressClient(ABC):
    """Base class for express company API clients."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the express client.

        Args:
            config: Client configuration dictionary
        """
        self.config = config or {}
        self._enabled = self.config.get("enabled", True)

    @property
    @abstractmethod
    def code(self) -> str:
        """Get express company code."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get express company name."""
        pass

    @property
    def enabled(self) -> bool:
        """Check if this express company is enabled."""
        return self._enabled

    @abstractmethod
    async def query_tracking(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query tracking information.

        Args:
            tracking_number: The tracking number
            express_company: Optional express company code for unified APIs

        Returns:
            Dict containing tracking information
        """
        pass

    def get_tracking_url(self, tracking_number: str) -> str:
        """
        Get the tracking URL for this express company.

        Args:
            tracking_number: The tracking number

        Returns:
            URL string for tracking
        """
        return ""

    def calculate_fee(
        self,
        weight: float,
        address: Dict[str, str],
        calculate_type: str = "express"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate shipping fee.

        Args:
            weight: Package weight in kg
            address: Address information
            calculate_type: Calculation type

        Returns:
            Dict containing fee information or None
        """
        # Default implementation returns None
        # Subclasses should override this method
        return None


class MockExpressClient(BaseExpressClient):
    """Mock express client for testing and development."""

    @property
    def code(self) -> str:
        return "mock"

    @property
    def name(self) -> str:
        return "Mock快递"

    async def query_tracking(
        self,
        tracking_number: str,
        express_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return mock tracking data."""
        return {
            "success": True,
            "data": {
                "express_company": express_company or self.code,
                "express_company_name": self.name,
                "tracking_number": tracking_number,
                "status": "in_transit",
                "status_text": "运输中",
                "traces": [
                    {
                        "time": "2024-01-01 10:00:00",
                        "status": "已揽收",
                        "location": "深圳市",
                        "description": "快件已揽收"
                    },
                    {
                        "time": "2024-01-01 14:00:00",
                        "status": "运输中",
                        "location": "深圳市",
                        "description": "快件已到达中转场"
                    },
                    {
                        "time": "2024-01-02 09:00:00",
                        "status": "运输中",
                        "location": "广州市",
                        "description": "快件正在运输中"
                    }
                ],
                "last_update": "2024-01-02T09:00:00"
            }
        }

    def calculate_fee(
        self,
        weight: float,
        address: Dict[str, str],
        calculate_type: str = "express"
    ) -> Optional[Dict[str, Any]]:
        """Calculate mock shipping fee."""
        # Base fee calculation
        base_fee = 10.0
        weight_fee = max(0, weight - 1.0) * 5.0
        total_fee = base_fee + weight_fee

        # Free shipping for orders over 99
        is_free = address.get("total_price", 0) >= 99

        return {
            "fee": total_fee if not is_free else 0,
            "is_free": is_free,
            "estimated_days": "2-3天",
            "is_recommend": True
        }


def get_express_client(
    company_code: str,
    config: Optional[Dict[str, Any]] = None
) -> BaseExpressClient:
    """
    Get express company client by code.

    Args:
        company_code: Express company code
        config: Configuration dictionary

    Returns:
        BaseExpressClient instance
    """
    from .shunfeng import ShunfengClient
    from .yuantong import YuantongClient
    from .zhongtong import ZhongtongClient
    from .kd100 import Kd100Client
    from .yunda import YundaClient
    from .jtexpress import JtexpressClient
    from .sto import StoClient
    from .ems import EmsClient

    clients = {
        "shunfeng": ShunfengClient,
        "yuantong": YuantongClient,
        "zhongtong": ZhongtongClient,
        "kd100": Kd100Client,
        "yunda": YundaClient,
        "jtexpress": JtexpressClient,
        "sto": StoClient,
        "ems": EmsClient,
    }

    client_class = clients.get(company_code.lower())
    if client_class:
        return client_class(config)

    logger.warning(f"Unknown express company code: {company_code}, using mock client")
    return MockExpressClient(config)


def get_all_clients(config: Optional[Dict[str, Any]] = None) -> List[BaseExpressClient]:
    """
    Get all enabled express company clients.

    Args:
        config: Configuration dictionary

    Returns:
        List of enabled express clients
    """
    from .shunfeng import ShunfengClient
    from .yuantong import YuantongClient
    from .zhongtong import ZhongtongClient
    from .kd100 import Kd100Client

    all_clients = [
        ShunfengClient,
        YuantongClient,
        ZhongtongClient,
        Kd100Client,
    ]

    enabled_clients = []
    for client_class in all_clients:
        try:
            client = client_class(config)
            if client.enabled:
                enabled_clients.append(client)
        except Exception as e:
            logger.warning(f"Failed to initialize {client_class.__name__}: {e}")

    return enabled_clients
