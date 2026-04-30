"""
FastAPI应用入口 - 后台管理系统
用于管理应用配置等高级功能
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入API路由
from api.admin_application_config import router as application_config_router

# 创建FastAPI应用
app = FastAPI(
    title="AI活动秀后台管理API",
    description="应用配置管理系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(application_config_router)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "code": 200,
        "message": "AI活动秀后台管理API服务正在运行",
        "version": "1.0.0",
        "service": "fastapi"
    }


@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # 开发环境
    if os.getenv('FLASK_ENV') == 'development':
        uvicorn.run(
            "fastapi_app:app",
            host="0.0.0.0",
            port=8000,  # 使用8000端口，避免与Flask的5000端口冲突
            reload=True
        )
    else:
        # 生产环境
        uvicorn.run(
            "fastapi_app:app",
            host="0.0.0.0",
            port=8000,
            workers=4
        )
