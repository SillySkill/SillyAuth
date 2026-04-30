"""
SillyMD Modular API Entry Point (v2.0.0)

使用 PluginManager + db_adapter 的新模块化架构。
替代旧的 server/api/main.py。

启动: python main.py
或:   uvicorn main:app --host 0.0.0.0 --port 8000
"""

import logging
import sys
import os
from contextlib import asynccontextmanager

# 确保 src/ 在 sys.path 中，以便 PluginManager 的 modules.* 导入生效
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 应用初始化
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时: 加载所有模块
    logger.info("Starting SillyMD Modular API v2.0.0 ...")
    try:
        from core.plugin_manager import PluginManager
        app.state.manager = PluginManager()
        app.state.manager.set_app(app)
        await app.state.manager.load_all_modules()
        logger.info(
            f"Loaded {len(app.state.manager._modules)} modules successfully"
        )
    except Exception as e:
        logger.error(f"Failed to load modules: {e}", exc_info=True)

    yield

    # 关闭时: 卸载所有模块
    logger.info("Shutting down SillyMD Modular API ...")
    try:
        if hasattr(app.state, 'manager'):
            app.state.manager.on_shutdown()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(
    title="SillyMD Modular API",
    version="2.0.0",
    description="AI Skills 内容管理与交易平台 - 模块化 API",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 过渡期兼容端点
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    status = "healthy"
    db_status = "unknown"

    try:
        from core.db_adapter import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
        status = "degraded"

    return JSONResponse({
        "status": status,
        "version": "2.0.0",
        "database": db_status,
    })


@app.get("/api/file", tags=["系统"])
async def proxy_file(request: Request):
    """
    过渡期文件代理端点 (已迁移至 TOS)

    公开文件: 302 重定向到 TOS 自定义域名
    私有文件: 生成 TOS 签名 URL 后 302 重定向
    """
    logger.warning("Deprecation: /api/file endpoint is deprecated, use TOS direct URLs instead")

    path = request.query_params.get("path", "")
    if not path:
        return JSONResponse({"error": "Missing path parameter"}, status_code=400)

    is_private = request.query_params.get("private", "").lower() in ("1", "true", "yes")

    # TOS 为主存储方案
    tos_domain = os.getenv("TOS_CUSTOM_DOMAIN", "")
    if tos_domain:
        if is_private:
            # 私有文件: 生成 TOS 签名 URL 后重定向
            try:
                from src.modules.storage.tos_client import get_tos_client
                tos_config = {
                    "endpoint": os.getenv("TOS_ENDPOINT", "tos-cn-shanghai.volces.com"),
                    "bucket": os.getenv("TOS_BUCKET", "jc-st"),
                    "access_key": os.getenv("TOS_ACCESS_KEY", ""),
                    "secret_key": os.getenv("TOS_SECRET_KEY", ""),
                    "custom_domain": tos_domain,
                }
                client = get_tos_client(tos_config)
                signed_url = client.get_signed_url(path, expires_seconds=3600)
                return RedirectResponse(url=signed_url)
            except Exception as e:
                logger.error(f"Failed to generate TOS signed URL: {e}")
                return JSONResponse(
                    {"error": "Failed to generate signed URL"},
                    status_code=500
                )
        else:
            # 公开文件: 直接重定向到 TOS 自定义域名
            url = f"https://{tos_domain}/{path}"
            return RedirectResponse(url=url)

    return JSONResponse(
        {"error": "Storage service not configured. Set TOS_CUSTOM_DOMAIN."},
        status_code=503
    )


# ---------------------------------------------------------------------------
# 直接启动
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("APP_ENV", "production") != "production",
    )
