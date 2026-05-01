"""
Template Middleware - Extracts JWT, theme, and lang from cookies
and attaches them to request.state for template rendering.
"""
import logging
import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "sillymd-jwt-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Use python-jose for JWT decoding (available in the project dependencies)
try:
    from jose import jwt as jose_jwt
    _jwt_available = True
except ImportError:
    jose_jwt = None
    _jwt_available = False
    logger.warning("python-jose not available; JWT cookie decoding disabled")


class TemplateContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds user, theme, lang to request.state from cookies.
    Applied to all requests but only used by page-rendering routes.
    """

    async def dispatch(self, request: Request, call_next):
        # Defaults
        request.state.user = None
        request.state.theme = request.cookies.get("theme", "tech-blue")
        request.state.lang = request.cookies.get("lang", "zh-CN")

        # Try to extract user from JWT cookie
        token = request.cookies.get("access_token")
        if token and _jwt_available:
            try:
                payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                request.state.user = {
                    "id": payload.get("sub"),
                    "username": payload.get("username", ""),
                    "email": payload.get("email", ""),
                    "role": payload.get("role", "user"),
                }
            except jose_jwt.ExpiredSignatureError:
                logger.debug("JWT token expired")
            except jose_jwt.JWTError:
                logger.debug("Invalid JWT token")
            except Exception as e:
                logger.debug(f"JWT decode error: {e}")

        response = await call_next(request)
        return response
