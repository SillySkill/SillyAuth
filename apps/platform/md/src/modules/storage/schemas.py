"""
Storage Module Schemas - 数据模型定义

定义存储模块的请求和响应数据结构
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """文件上传请求"""
    folder: str = Field(..., description="存储文件夹路径，如 'images/'")
    filename: str = Field(..., description="文件名，包含扩展名")
    content_type: Optional[str] = Field(None, description="文件 MIME 类型")


class UploadResponse(BaseModel):
    """文件上传响应"""
    url: str = Field(..., description="文件访问 URL")
    key: str = Field(..., description="文件存储 key")
    size: int = Field(..., description="文件大小（字节）")
    checksum: str = Field(..., description="文件 MD5 校验和")


class FileInfo(BaseModel):
    """文件信息"""
    key: str = Field(..., description="文件存储 key")
    size: int = Field(..., description="文件大小（字节）")
    last_modified: Optional[datetime] = Field(None, description="最后修改时间")
    url: Optional[str] = Field(None, description="文件访问 URL")
    content_type: Optional[str] = Field(None, description="文件 MIME 类型")


class FileListResponse(BaseModel):
    """文件列表响应"""
    files: List[FileInfo] = Field(..., description="文件列表")
    total: int = Field(..., description="文件总数")
    prefix: str = Field(..., description="查询的前缀")


class SignedUrlRequest(BaseModel):
    """获取签名 URL 请求"""
    expires_seconds: int = Field(3600, ge=60, le=86400, description="URL 有效期（秒），范围 60-86400")


class SignedUrlResponse(BaseModel):
    """签名 URL 响应"""
    url: str = Field(..., description="签名的访问 URL")
    expires_in: int = Field(..., description="有效期（秒）")
    key: str = Field(..., description="文件 key")


class StorageUsageStats(BaseModel):
    """存储使用统计"""
    total_files: int = Field(0, description="总文件数")
    total_size: int = Field(0, description="总存储大小（字节）")
    by_folder: dict = Field(default_factory=dict, description="按文件夹统计")
    by_type: dict = Field(default_factory=dict, description="按文件类型统计")


class StorageConfig(BaseModel):
    """存储配置"""
    max_file_size_mb: int = Field(500, description="最大文件大小（MB）")
    allowed_types: List[str] = Field(
        default_factory=lambda: ["image", "video", "audio", "document", "archive"],
        description="允许的文件类型"
    )
    custom_domain: str = Field("", description="自定义域名")
