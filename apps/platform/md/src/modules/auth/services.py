"""
Auth Module Services
Business logic for authentication operations

Provides login, registration, token management, and password verification
"""

from passlib.hash import bcrypt
import secrets
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from pydantic import EmailStr

from .schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    Token,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60  # 30 days in minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7



class AuthService:
    """Authentication service class"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash. Supports both bcrypt and legacy SHA-256.

        Args:
            password: Plain text password
            password_hash: Stored password hash

        Returns:
            True if password matches, False otherwise
        """
        # bcrypt hashes start with $2b$ or $2a$
        if password_hash.startswith("$2"):
            return bcrypt.verify(password, password_hash)
        # Legacy SHA-256 hash (64 hex characters)
        if len(password_hash) == 64 and all(c in "0123456789abcdef" for c in password_hash.lower()):
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest() == password_hash
        return False

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token

        Args:
            data: Token payload data (user_id, username, email, role)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token

        Args:
            data: Token payload data (user_id, username, email, role)

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token

        Args:
            token: JWT token string

        Returns:
            Token payload dict or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"JWT decode error: {str(e)}")
            return None

    @staticmethod
    def generate_reset_token() -> str:
        """
        Generate secure password reset token

        Returns:
            URL-safe random token string
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_db_cursor():
        """
        Get database cursor with auto-commit

        Yields:
            Database cursor
        """
        from core.db_adapter import get_db_cursor
        return get_db_cursor()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address

        Args:
            email: User email

        Returns:
            User dict or None
        """
        with self.get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            return cur.fetchone()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            User dict or None
        """
        with self.get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            return cur.fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User dict or None
        """
        with self.get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            return cur.fetchone()

    def login(self, email: str, password: str) -> Optional[Token]:
        """
        Authenticate user and return tokens

        Args:
            email: User email
            password: User password

        Returns:
            Token object with access/refresh tokens or None if failed
        """
        # Find user by email
        user = self.get_user_by_email(email)

        if not user:
            logger.warning(f"Login attempt for non-existent email: {email}")
            return None

        # Verify password
        if not self.verify_password(password, user.get('password_hash')):
            logger.warning(f"Invalid password attempt for email: {email}")
            return None

        # Check if account is active
        if not user.get('is_active', True):
            logger.warning(f"Login attempt for disabled account: {email}")
            return None

        # Update last login time
        with self.get_db_cursor() as cur:
            cur.execute(
                "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s",
                (user['id'],)
            )

        # Create token data
        token_data = {
            "user_id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user.get('role', 'user')
        }

        # Generate tokens
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        logger.info(f"User {email} logged in successfully")

        # Build user response
        user_response = UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            first_name=user.get('first_name'),
            last_name=user.get('last_name'),
            created_at=user.get('created_at'),
            role=user.get('role', 'user'),
            avatar_url=user.get('avatar_url'),
            is_verified=user.get('is_verified', False),
            is_active=user.get('is_active', True)
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            user=user_response
        )

    def register(self, data: RegisterRequest) -> Optional[UserResponse]:
        """
        Register new user

        Args:
            data: Registration request data

        Returns:
            Created user response or None if failed
        """
        # Check if email already exists
        existing_email = self.get_user_by_email(data.email)
        if existing_email:
            logger.warning(f"Registration attempt with existing email: {data.email}")
            return None

        # Check if username already exists
        existing_username = self.get_user_by_username(data.username)
        if existing_username:
            logger.warning(f"Registration attempt with existing username: {data.username}")
            return None

        # Hash password
        password_hash = self.hash_password(data.password)

        # Create new user
        with self.get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO users (
                    username, email, password_hash, first_name, last_name,
                    role, is_active, is_verified, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, 'user', TRUE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id, username, email, first_name, last_name, role, avatar_url, is_verified, is_active, created_at
            """, (
                data.username,
                data.email,
                password_hash,
                data.first_name,
                data.last_name
            ))
            new_user = cur.fetchone()

        logger.info(f"New user {data.email} registered successfully")

        return UserResponse(
            id=new_user['id'],
            username=new_user['username'],
            email=new_user['email'],
            first_name=new_user.get('first_name'),
            last_name=new_user.get('last_name'),
            created_at=new_user.get('created_at'),
            role=new_user.get('role', 'user'),
            avatar_url=new_user.get('avatar_url'),
            is_verified=new_user.get('is_verified', False),
            is_active=new_user.get('is_active', True)
        )

    def refresh_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token string

        Returns:
            New Token object or None if invalid
        """
        try:
            # Decode refresh token
            payload = self.decode_token(refresh_token)

            if not payload:
                logger.warning("Invalid refresh token: decode failed")
                return None

            # Check token type
            if payload.get("type") != "refresh":
                logger.warning("Invalid refresh token: wrong type")
                return None

            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("Invalid refresh token: no user_id")
                return None

            # Get user from database
            user = self.get_user_by_id(user_id)
            if not user or not user.get('is_active', True):
                logger.warning(f"Refresh token for non-existent or disabled user: {user_id}")
                return None

            # Create new token data
            token_data = {
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user.get('role', 'user')
            }

            # Generate new tokens
            access_token = self.create_access_token(token_data)
            new_refresh_token = self.create_refresh_token(token_data)

            # Build user response
            user_response = UserResponse(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                first_name=user.get('first_name'),
                last_name=user.get('last_name'),
                created_at=user.get('created_at'),
                role=user.get('role', 'user'),
                avatar_url=user.get('avatar_url'),
                is_verified=user.get('is_verified', False),
                is_active=user.get('is_active', True)
            )

            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )

        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return None

    def update_user(self, user_id: int, data: Dict[str, Any]) -> Optional[UserResponse]:
        """
        Update user profile

        Args:
            user_id: User ID
            data: Update data dict

        Returns:
            Updated user response or None if failed
        """
        # Build update query dynamically
        update_fields = []
        values = []

        allowed_fields = ['first_name', 'last_name', 'nickname', 'avatar_url']

        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        if not update_fields:
            return None

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        query = f"""
            UPDATE users
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, username, email, first_name, last_name, role, avatar_url, is_verified, is_active, created_at
        """

        with self.get_db_cursor() as cur:
            cur.execute(query, values)
            updated_user = cur.fetchone()

        if not updated_user:
            return None

        return UserResponse(
            id=updated_user['id'],
            username=updated_user['username'],
            email=updated_user['email'],
            first_name=updated_user.get('first_name'),
            last_name=updated_user.get('last_name'),
            created_at=updated_user.get('created_at'),
            role=updated_user.get('role', 'user'),
            avatar_url=updated_user.get('avatar_url'),
            is_verified=updated_user.get('is_verified', False),
            is_active=updated_user.get('is_active', True)
        )


# Singleton instance
auth_service = AuthService()
