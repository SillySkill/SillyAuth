# ============================================
# SillyMD Backend - Rate Limiting
# ============================================

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_user_id(request: Request) -> str:
    """Get user ID for rate limiting"""
    # Try to get user from token first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return f"user:{auth_header[7:]}"

    # Fall back to IP
    return f"ip:{get_remote_address(request)}"


# Create rate limiter
limiter = Limiter(
    key_func=get_user_id,
    default_limits=["200/minute"],
    storage_uri="redis://localhost:6379/3"
)
