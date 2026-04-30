"""
Storage Module Routes - API 路由

提供存储服务的 RESTful API 接口
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from .services import get_storage_service, StorageService
from .schemas import (
    UploadResponse,
    FileInfo,
    FileListResponse,
    SignedUrlRequest,
    SignedUrlResponse,
    StorageUsageStats
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/storage", tags=["Storage"])


def get_storage() -> StorageService:
    """获取存储服务实例的依赖"""
    try:
        return get_storage_service()
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Storage service not initialized. Please configure TOS credentials."
        )


# ========== 上传路由 ==========

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder: str = Form("", description="存储文件夹路径"),
    storage: StorageService = Depends(get_storage)
):
    """
    上传文件到 TOS

    上传文件到指定的存储文件夹，支持图片、视频、音频、文档、压缩包等格式。

    Args:
        file: 上传的文件
        folder: 存储文件夹路径，如 'images/', 'videos/', 'documents/'

    Returns:
        UploadResponse: 包含 url, key, size, checksum
    """
    try:
        # 读取文件内容
        content = await file.read()

        # 获取内容类型
        content_type = file.content_type

        # 上传文件
        result = storage.upload(
            file_content=content,
            folder=folder,
            filename=file.filename or "unknown",
            content_type=content_type
        )

        logger.info(f"File uploaded successfully: {result.key}")

        return result

    except ValueError as e:
        logger.warning(f"Upload validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/upload/webs", response_model=UploadResponse)
async def upload_to_webs(
    file: UploadFile = File(...),
    storage: StorageService = Depends(get_storage)
):
    """
    上传文件到 webs 文件夹（网站数据默认存储位置）

    网站图片、静态资源等文件上传到 webs 文件夹。

    Args:
        file: 上传的文件

    Returns:
        UploadResponse: 包含 url, key, size, checksum
    """
    try:
        # 读取文件内容
        content = await file.read()

        # 获取内容类型
        content_type = file.content_type

        # 上传到 webs 文件夹
        result = storage.upload_to_webs(
            file_content=content,
            filename=file.filename or "unknown",
            content_type=content_type
        )

        logger.info(f"File uploaded to webs: {result.key}")

        return result

    except ValueError as e:
        logger.warning(f"Upload validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload to webs failed: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


# ========== 特定路由 (必须在 /{key:path} 之前) ==========

@router.get("/products/images")
async def get_product_images(
    storage: StorageService = Depends(get_storage)
):
    """
    获取傻福虾盘产品图片

    从 TOS 获取傻福虾盘产品图片列表。

    Returns:
        JSONResponse: 产品图片列表
    """
    try:
        # 直接调用 TOS client 获取文件列表
        from datetime import datetime

        # 获取 webs/USilly/sillypan/ 下的图片
        folder = "webs/USilly/sillypan"
        if not folder.endswith("/"):
            folder += "/"

        keys = storage._client.list_files(folder, max_keys=50)

        images = []
        for key in keys:
            # 只保留图片文件
            if not key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                continue

            # 获取文件信息
            info = storage._client.get_file_info(key)
            if info:
                last_modified = info.get("last_modified")
                if isinstance(last_modified, datetime):
                    last_modified = last_modified.isoformat()

                images.append({
                    "key": key,
                    "url": storage._client._build_url(key),
                    "size": info.get("size", 0),
                    "last_modified": last_modified
                })

        return JSONResponse(content={
            "success": True,
            "images": images
        })
    except Exception as e:
        logger.error(f"Get product images failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取产品图片失败: {str(e)}")


@router.get("/list/{folder:path}", response_model=FileListResponse)
async def list_files(
    folder: str,
    max_keys: int = Query(100, ge=1, le=1000, description="最大返回数量"),
    storage: StorageService = Depends(get_storage)
):
    """
    列出文件夹中的文件

    列出指定文件夹下的所有文件。

    Args:
        folder: 文件夹路径
        max_keys: 最大返回数量

    Returns:
        FileListResponse: 文件列表
    """
    try:
        result = storage.list(folder=folder, max_keys=max_keys)
        return result

    except Exception as e:
        logger.error(f"List files failed for folder {folder}: {e}")
        raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")


@router.get("/stats/usage", response_model=StorageUsageStats)
async def get_usage_stats(
    user_id: Optional[str] = Query(None, description="用户 ID"),
    storage: StorageService = Depends(get_storage)
):
    """
    获取存储使用统计

    获取当前存储的使用情况统计。

    Args:
        user_id: 用户 ID (可选)

    Returns:
        StorageUsageStats: 存储使用统计
    """
    try:
        stats = storage.get_usage_stats(user_id=user_id)
        return stats

    except Exception as e:
        logger.error(f"Get usage stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/batch/delete")
async def batch_delete_files(
    keys: List[str],
    storage: StorageService = Depends(get_storage)
):
    """
    批量删除文件

    删除多个指定路径的文件。

    Args:
        keys: 文件 key 列表

    Returns:
        JSONResponse: 批量删除结果
    """
    try:
        deleted = []
        failed = []

        for key in keys:
            try:
                if storage.file_exists(key):
                    storage.delete(key)
                    deleted.append(key)
                else:
                    failed.append({"key": key, "error": "文件不存在"})
            except Exception as e:
                failed.append({"key": key, "error": str(e)})

        return JSONResponse(
            content={
                "success": len(failed) == 0,
                "deleted": deleted,
                "failed": failed,
                "total": len(keys),
                "deleted_count": len(deleted),
                "failed_count": len(failed)
            }
        )

    except Exception as e:
        logger.error(f"Batch delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查

    检查存储服务状态。

    Returns:
        JSONResponse: 健康状态
    """
    try:
        storage = get_storage()
        # 尝试列出文件来检查连接
        storage.list(folder="", max_keys=1)
        return {
            "status": "healthy",
            "service": "storage",
            "tos_connected": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "storage",
            "tos_connected": False,
            "error": str(e)
        }


# ========== 动态路由 (必须在最后) ==========

@router.get("/{key:path}", response_model=FileInfo)
async def get_file_info(
    key: str,
    storage: StorageService = Depends(get_storage)
):
    """
    获取文件信息

    获取指定文件的详细信息，包括大小、修改时间、内容类型等。

    Args:
        key: 文件的存储 key (路径)

    Returns:
        FileInfo: 文件信息
    """
    try:
        info = storage.get_file_info(key)

        if not info:
            raise HTTPException(status_code=404, detail="文件不存在")

        return info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file info failed for {key}: {e}")
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")


@router.delete("/{key:path}")
async def delete_file(
    key: str,
    storage: StorageService = Depends(get_storage)
):
    """
    删除文件

    删除指定存储路径的文件。

    Args:
        key: 文件的存储 key (路径)

    Returns:
        JSONResponse: 删除结果
    """
    try:
        # 检查文件是否存在
        if not storage.file_exists(key):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 删除文件
        success = storage.delete(key)

        if success:
            logger.info(f"File deleted: {key}")
            return JSONResponse(
                content={
                    "success": True,
                    "message": "文件删除成功",
                    "key": key
                }
            )
        else:
            raise HTTPException(status_code=500, detail="删除失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed for {key}: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/{key:path}/url", response_model=SignedUrlResponse)
async def get_signed_url(
    key: str,
    expires_seconds: int = Query(3600, ge=60, le=86400, description="URL 有效期（秒）"),
    storage: StorageService = Depends(get_storage)
):
    """
    获取文件签名 URL

    生成一个带签名的临时访问 URL，用于授权访问私有文件。

    Args:
        key: 文件的存储 key (路径)
        expires_seconds: URL 有效期（秒），范围 60-86400

    Returns:
        SignedUrlResponse: 包含签名 URL 和有效期
    """
    try:
        # 检查文件是否存在
        if not storage.file_exists(key):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 生成签名 URL
        signed_url = storage.get_url(key, signed=True, expires_seconds=expires_seconds)

        return SignedUrlResponse(
            url=signed_url,
            expires_in=expires_seconds,
            key=key
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate signed URL failed for {key}: {e}")
        raise HTTPException(status_code=500, detail=f"生成签名 URL 失败: {str(e)}")


@router.get("/{key:path}/download")
async def download_file(
    key: str,
    storage: StorageService = Depends(get_storage)
):
    """
    下载文件

    下载指定路径的文件内容。

    Args:
        key: 文件的存储 key (路径)

    Returns:
        StreamingResponse: 文件流响应
    """
    try:
        # 检查文件是否存在
        if not storage.file_exists(key):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 获取文件信息
        info = storage.get_file_info(key)

        # 获取签名 URL
        signed_url = storage.get_url(key, signed=True, expires_seconds=3600)

        # 返回重定向到签名 URL 或直接返回文件
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=signed_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed for {key}: {e}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
