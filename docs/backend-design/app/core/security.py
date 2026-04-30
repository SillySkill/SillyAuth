# ============================================
# SillyMD Backend - Security Module
# ============================================

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: int, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: int) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash for content"""
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()


def sign_skill(content_hash: str) -> str:
    """Sign skill with platform key"""
    import hmac
    import base64

    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        content_hash.encode(),
        hashlib.sha256
    ).digest()

    return base64.b64encode(signature).decode()


def verify_signature(content_hash: str, signature: str) -> bool:
    """Verify skill signature"""
    import hmac
    import base64

    expected_signature = hmac.new(
        settings.SECRET_KEY.encode(),
        content_hash.encode(),
        hashlib.sha256
    ).digest()

    decoded_signature = base64.b64decode(signature)
    return hmac.compare_digest(expected_signature, decoded_signature)
