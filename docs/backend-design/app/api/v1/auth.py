# ============================================
# SillyMD Backend - Auth API Router
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import auth_service
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user
    """
    user = await auth_service.register(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password
    """
    return await auth_service.login(
        db,
        login_data.username,
        login_data.password
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token
    """
    return await auth_service.refresh_token(db, refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user info
    """
    return current_user


# Re-export get_current_user for use in other routers
from app.api.deps import get_current_user
