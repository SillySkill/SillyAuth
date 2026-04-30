# ============================================
# SillyMD Backend - Tests
# ============================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import async_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash


@pytest.fixture
async def client():
    """Test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db():
    """Database session fixture"""
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_vendor(db: AsyncSession):
    """Create test vendor"""
    vendor = User(
        username="testvendor",
        email="vendor@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.VENDOR,
        is_active=True,
        is_verified=True
    )
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user):
    """Get authentication headers"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================
# Authentication Tests
# ============================================

class TestAuth:
    """Authentication tests"""

    async def test_register_user(self, client: AsyncClient):
        """Test user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with duplicate username"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400

    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"


# ============================================
# Skills Tests
# ============================================

class TestSkills:
    """Skills tests"""

    async def test_create_skill_unauthorized(self, client: AsyncClient):
        """Test creating skill without authentication"""
        response = await client.post(
            "/api/v1/skills/",
            json={
                "name": "Test Skill",
                "description": "A test skill",
                "category": "tech",
                "type": "free"
            }
        )
        assert response.status_code == 401

    async def test_create_skill_as_vendor(
        self, client: AsyncClient, test_vendor
    ):
        """Test creating skill as vendor"""
        # Login as vendor
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testvendor",
                "password": "password123"
            }
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create skill
        response = await client.post(
            "/api/v1/skills/",
            headers=headers,
            json={
                "name": "Vendor Skill",
                "description": "A skill from vendor",
                "category": "tech",
                "type": "free",
                "tags": ["api", "test"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Vendor Skill"

    async def test_list_skills(self, client: AsyncClient):
        """Test listing skills"""
        response = await client.get("/api/v1/skills/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# ============================================
# Transaction Tests
# ============================================

class TestTransactions:
    """Transaction tests"""

    async def test_get_wallet(self, client: AsyncClient, auth_headers):
        """Test getting wallet information"""
        response = await client.get(
            "/api/v1/transactions/wallet",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data

    async def test_recharge_points(self, client: AsyncClient, auth_headers):
        """Test recharging points"""
        response = await client.post(
            "/api/v1/transactions/recharge",
            params={"amount": 1000},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_purchase_license_insufficient_balance(
        self, client: AsyncClient, auth_headers
    ):
        """Test purchasing license with insufficient balance"""
        response = await client.post(
            "/api/v1/transactions/licenses/purchase",
            headers=auth_headers,
            json={
                "skill_id": 1,
                "license_type": "personal"
            }
        )
        # Should fail if balance is too low
        assert response.status_code in [400, 404]

    async def test_request_withdrawal_minimum_amount(
        self, client: AsyncClient, auth_headers
    ):
        """Test withdrawal with amount below minimum"""
        response = await client.post(
            "/api/v1/transactions/withdrawals",
            headers=auth_headers,
            json={"amount": 100}
        )
        assert response.status_code == 422  # Validation error


# ============================================
# Security Tests
# ============================================

class TestSecurity:
    """Security tests"""

    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test SQL injection protection"""
        response = await client.get(
            "/api/v1/skills/",
            params={"search": "'; DROP TABLE users; --"}
        )
        # Should not crash
        assert response.status_code in [200, 400, 422]

    async def test_xss_protection(self, client: AsyncClient, auth_headers):
        """Test XSS protection in skill creation"""
        response = await client.post(
            "/api/v1/skills/",
            headers=auth_headers,
            json={
                "name": "<script>alert('xss')</script>",
                "description": "Test",
                "category": "tech",
                "type": "free"
            }
        )
        # Should handle input safely
        assert response.status_code in [201, 400, 401]

    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting"""
        # Make many requests
        responses = []
        for _ in range(100):
            response = await client.get("/api/v1/skills/")
            responses.append(response.status_code)

        # At least some should be rate limited
        assert 429 in responses


# ============================================
# Performance Tests
# ============================================

class TestPerformance:
    """Performance tests"""

    async def test_concurrent_requests(self, client: AsyncClient):
        """Test handling concurrent requests"""
        import asyncio

        async def make_request():
            return await client.get("/api/v1/skills/")

        tasks = [make_request() for _ in range(50)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

    async def test_pagination_performance(self, client: AsyncClient):
        """Test pagination performance"""
        import time

        start = time.time()
        response = await client.get("/api/v1/skills/?limit=100")
        end = time.time()

        # Should respond quickly
        assert end - start < 1.0
        assert response.status_code == 200
