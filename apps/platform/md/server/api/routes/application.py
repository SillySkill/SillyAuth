"""
AI活动秀应用路由
路径前缀: /application/com.jcoding.aiactivity

用于将所有API路由统一到应用包名下
"""

from fastapi import APIRouter
from routes.upload import router as upload_router

# 创建应用路由
router = APIRouter(prefix="/application/com.jcoding.aiactivity")

# 注册上传路由
# 注意：upload_router 需要设置为空prefix，因为已经在application路由中
upload_router.tags = ["upload"]
router.include_router(upload_router, prefix="/upload", tags=["upload"])

# 导出路由供main.py使用
__all__ = ["router"]
