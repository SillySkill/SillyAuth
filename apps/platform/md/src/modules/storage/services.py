"""
Storage Service - 存储服务层

提供高级存储操作接口，封装 TOS 客户端
"""

import logging
import hashlib
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from .tos_client import TosClient, get_tos_client
from .schemas import (
    UploadResponse,
    FileInfo,
    FileListResponse,
    SignedUrlResponse,
    StorageUsageStats
)

logger = logging.getLogger(__name__)


# 常见 MIME 类型映射
MIME_TYPE_MAP = {
    # Images
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".bmp": "image/bmp",
    # Videos
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".wmv": "video/x-ms-wmv",
    ".flv": "video/x-flv",
    # Audio
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
    ".m4a": "audio/mp4",
    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    # Archives
    ".zip": "application/zip",
    ".rar": "application/x-rar-compressed",
    ".7z": "application/x-7z-compressed",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
}


class StorageService:
    """
    存储服务类

    提供高级存储操作，包括文件上传、下载、删除、列表等
    """

    def __init__(self, tos_client: TosClient, config: Optional[Dict[str, Any]] = None):
        """
        初始化存储服务

        Args:
            tos_client: TOS 客户端实例
            config: 存储配置
        """
        self._client = tos_client
        self._config = config or {}

        # 上传配置
        upload_config = self._config.get("upload", {})
        self.max_file_size_mb = upload_config.get("max_file_size_mb", 500)
        self.allowed_types = upload_config.get("allowed_types", [
            "image", "video", "audio", "document", "archive"
        ])
        # 默认上传文件夹
        self.default_folder = self._config.get("default_folder", "webs")

        # 类型到扩展名映射
        self._type_extensions = {
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
            "video": [".mp4", ".webm", ".avi", ".mov", ".wmv", ".flv"],
            "audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
            "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".json", ".xml", ".html", ".css", ".js"],
            "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
        }

    def upload_to_webs(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None
    ) -> UploadResponse:
        """
        上传文件到 webs 文件夹（网站数据默认存储位置）

        Args:
            file_content: 文件内容 (bytes)
            filename: 文件名
            content_type: 文件 MIME 类型 (可选)

        Returns:
            UploadResponse: 包含 url, key, size, checksum
        """
        return self.upload(file_content, self.default_folder, filename, content_type)

    def _get_content_type(self, filename: str, content_type: Optional[str] = None) -> str:
        """获取文件的 MIME 类型"""
        if content_type:
            return content_type

        ext = os.path.splitext(filename)[1].lower()
        return MIME_TYPE_MAP.get(ext, "application/octet-stream")

    def _generate_unique_key(self, folder: str, filename: str) -> str:
        """生成唯一的文件 key"""
        # 确保 folder 以 / 结尾
        if folder and not folder.endswith("/"):
            folder += "/"

        # 生成唯一文件名：时间戳_UUID_原文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        ext = os.path.splitext(safe_filename)[1]

        return f"{folder}{timestamp}_{unique_id}{ext}"

    def _get_file_category(self, filename: str) -> str:
        """获取文件类型分类"""
        ext = os.path.splitext(filename)[1].lower()
        for category, extensions in self._type_extensions.items():
            if ext in extensions:
                return category
        return "other"

    def upload(
        self,
        file_content: bytes,
        folder: str,
        filename: str,
        content_type: Optional[str] = None
    ) -> UploadResponse:
        """
        上传文件

        Args:
            file_content: 文件内容 (bytes)
            folder: 存储文件夹路径
            filename: 文件名
            content_type: 文件 MIME 类型 (可选，自动从文件名推断)

        Returns:
            UploadResponse: 包含 url, key, size, checksum

        Raises:
            ValueError: 文件大小超过限制或类型不允许
            RuntimeError: 上传失败
        """
        # 检查文件大小
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(
                f"文件大小 {file_size_mb:.2f}MB 超过限制 {self.max_file_size_mb}MB"
            )

        # 检查文件类型
        file_category = self._get_file_category(filename)
        if self.allowed_types and file_category not in self.allowed_types and "other" not in self.allowed_types:
            raise ValueError(
                f"文件类型 '{file_category}' 不允许。上传的文件类型: {', '.join(self.allowed_types)}"
            )

        # 生成唯一 key
        key = self._generate_unique_key(folder, filename)

        # 获取 MIME 类型
        mime_type = self._get_content_type(filename, content_type)

        # 上传到 TOS
        result = self._client.upload_file(key, file_content, mime_type)

        logger.info(f"File uploaded: {key}, size: {result['size']}, category: {file_category}")

        return UploadResponse(
            url=result["url"],
            key=result["key"],
            size=result["size"],
            checksum=result["checksum"]
        )

    def get_url(self, key: str, signed: bool = False, expires_seconds: int = 3600) -> str:
        """
        获取文件访问 URL

        Args:
            key: 文件存储 key
            signed: 是否返回签名 URL
            expires_seconds: 签名 URL 有效期（秒）

        Returns:
            str: 文件访问 URL
        """
        if signed:
            return self._client.get_signed_url(key, expires_seconds)
        return self._client._build_url(key)

    def delete(self, key: str) -> bool:
        """
        删除文件

        Args:
            key: 文件存储 key

        Returns:
            bool: 删除是否成功
        """
        result = self._client.delete_file(key)
        logger.info(f"File deleted: {key}")
        return result

    def list(self, folder: str = "", max_keys: int = 100) -> FileListResponse:
        """
        列出文件夹中的文件

        Args:
            folder: 文件夹路径
            max_keys: 最大返回数量

        Returns:
            FileListResponse: 文件列表响应
        """
        # 确保 folder 以 / 结尾
        if folder and not folder.endswith("/"):
            folder += "/"

        keys = self._client.list_files(folder, max_keys)

        files = []
        for key in keys:
            info = self._client.get_file_info(key)
            if info:
                files.append(FileInfo(
                    key=info["key"],
                    size=info.get("size", 0),
                    last_modified=info.get("last_modified"),
                    url=self._client._build_url(key),
                    content_type=info.get("content_type")
                ))

        return FileListResponse(
            files=files,
            total=len(files),
            prefix=folder
        )

    def get_usage_stats(self, user_id: Optional[str] = None) -> StorageUsageStats:
        """
        获取存储使用统计

        注意: 这是一个简化实现，实际统计可能需要额外的数据库支持

        Args:
            user_id: 用户 ID (可选，用于按用户统计)

        Returns:
            StorageUsageStats: 存储使用统计
        """
        # 基础统计（可以扩展为从数据库查询更详细的统计）
        stats = StorageUsageStats(
            total_files=0,
            total_size=0,
            by_folder={},
            by_type={}
        )

        # 如果有配置信息，尝试获取统计
        if self._config:
            # 可以在这里添加从 TOS 或数据库获取更详细统计的逻辑
            pass

        return stats

    def get_file_info(self, key: str) -> Optional[FileInfo]:
        """
        获取文件详细信息

        Args:
            key: 文件存储 key

        Returns:
            FileInfo 或 None
        """
        info = self._client.get_file_info(key)
        if not info:
            return None

        return FileInfo(
            key=info["key"],
            size=info.get("size", 0),
            last_modified=info.get("last_modified"),
            url=self._client._build_url(key),
            content_type=info.get("content_type")
        )

    def file_exists(self, key: str) -> bool:
        """
        检查文件是否存在

        Args:
            key: 文件存储 key

        Returns:
            bool: 文件是否存在
        """
        return self._client.file_exists(key)


# 全局服务实例
_storage_service: Optional[StorageService] = None


def get_storage_service(config: Optional[Dict[str, Any]] = None) -> StorageService:
    """
    获取全局存储服务实例

    Args:
        config: 存储配置

    Returns:
        StorageService: 存储服务实例
    """
    global _storage_service

    if config is not None:
        # 初始化 TOS 客户端
        tos_config = config.get("tos", {})
        tos_client = get_tos_client(tos_config)

        # 创建存储服务
        _storage_service = StorageService(tos_client, config)
        return _storage_service

    if _storage_service is None:
        raise RuntimeError("Storage service not initialized. Call get_storage_service(config) first.")
    return _storage_service
