# ============================================
# SillyMD Backend - API v1 Router
# ============================================

from fastapi import APIRouter
from app.api.v1 import auth, skills, transactions

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])


# Health check
@api_router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy"}
