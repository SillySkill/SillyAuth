"""
Downloads Module - Schemas

Pydantic schemas for download management API requests and responses.
Uses Pydantic v2 conventions (model_config instead of class Config).
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class DownloadCategoryEnum(str, Enum):
    """Download category types"""
    APPLICATION = "application"
    TOOL = "tool"
    DOCUMENT = "document"
    PLUGIN = "plugin"
    OTHER = "other"


class DownloadItemCreate(BaseModel):
    """Schema for creating a new download item"""
    name: str = Field(..., description="Download item name")
    description: str = Field(..., description="Download item description")
    category: DownloadCategoryEnum = Field(..., description="Category of the download")
    file_key: str = Field(..., description="Storage key for the file")
    version: Optional[str] = Field(None, description="Version string (optional)")
    size: int = Field(..., description="File size in bytes")
    downloads_count: int = Field(default=0, description="Number of downloads")

    model_config = {"from_attributes": True}


class DownloadItemResponse(BaseModel):
    """Response schema for a download item with full details"""
    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Download item name")
    description: str = Field(..., description="Download item description")
    category: str = Field(..., description="Category of the download")
    file_key: str = Field(..., description="Storage key for the file")
    version: Optional[str] = Field(None, description="Version string")
    size: int = Field(..., description="File size in bytes")
    downloads_count: int = Field(..., description="Number of downloads")
    is_published: bool = Field(default=True, description="Whether item is published")
    is_featured: bool = Field(default=False, description="Whether item is featured")
    position: int = Field(default=0, description="Display position")
    download_url: str = Field(..., description="Signed download URL")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "SillyFu 控制面板",
                "description": "SillyFu 桌面控制面板程序",
                "category": "application",
                "file_key": "sillyfu/releases/v1.2.0/SillyFu-Setup.exe",
                "version": "1.2.0",
                "size": 52428800,
                "downloads_count": 1523,
                "download_url": "https://skills.sillymd.com/sillyfu/releases/v1.2.0/SillyFu-Setup.exe?signed=true&expires=1234567890",
                "created_at": "2026-03-20T10:00:00Z",
                "updated_at": "2026-03-20T10:00:00Z"
            }
        }
    }


class DownloadCategory(BaseModel):
    """Schema for a download category with item count"""
    id: str = Field(..., description="Category identifier")
    name: str = Field(..., description="Category display name")
    items_count: int = Field(..., description="Number of items in this category")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "application",
                "name": "应用程序",
                "items_count": 5
            }
        }
    }


class VersionedDownload(BaseModel):
    """Schema for a versioned download item"""
    item_id: int = Field(..., description="Download item ID")
    version: str = Field(..., description="Version string")
    download_url: str = Field(..., description="Download URL for this version")
    release_date: Optional[date] = Field(None, description="Release date")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="File checksum (SHA-256)")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "item_id": 1,
                "version": "1.2.0",
                "download_url": "https://skills.sillymd.com/sillyfu/releases/v1.2.0/SillyFu-Setup.exe",
                "release_date": "2026-03-20",
                "file_size": 52428800,
                "checksum": "a1b2c3d4e5f6..."
            }
        }
    }


class DownloadListResponse(BaseModel):
    """Response schema for listing downloads"""
    items: List[DownloadItemResponse] = Field(..., description="List of download items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "items": [],
                "total": 10,
                "page": 1,
                "page_size": 20,
                "total_pages": 1
            }
        }
    }


class FeaturedDownloadResponse(BaseModel):
    """Response schema for featured downloads"""
    items: List[DownloadItemResponse] = Field(..., description="List of featured download items")
    total: int = Field(..., description="Total number of featured items")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "SillyFu 控制面板",
                        "description": "SillyFu 桌面控制面板程序",
                        "category": "application",
                        "file_key": "sillyfu/releases/v1.2.0/SillyFu-Setup.exe",
                        "version": "1.2.0",
                        "size": 52428800,
                        "downloads_count": 1523,
                        "download_url": "https://skills.sillymd.com/..."
                    }
                ],
                "total": 1
            }
        }
    }


class SillyClawDownloadResponse(BaseModel):
    """Response schema for SillyFu download"""
    version: str = Field(..., description="Version number")
    release_date: str = Field(..., description="Release date")
    download_url: str = Field(..., description="Download URL")
    release_notes: Optional[str] = Field(None, description="Release notes/changelog")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="SHA-256 checksum")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "version": "1.2.0",
                "release_date": "2026-03-20",
                "download_url": "https://skills.sillymd.com/sillyfu/releases/v1.2.0/SillyFu-Setup.exe",
                "release_notes": "1. 新增大虾塘动画效果\n2. 优化虾拳馆 PK 流程\n3. 修复若干 Bug",
                "file_size": 52428800,
                "checksum": "a1b2c3d4e5f6..."
            }
        }
    }


class LikeResponse(BaseModel):
    """Response schema for like/favorite action"""
    success: bool = Field(..., description="Operation success status")
    download_count: int = Field(..., description="Updated download count")
    item_id: int = Field(..., description="Download item ID")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "success": True,
                "download_count": 43,
                "item_id": 1
            }
        }
    }


class RecordDownloadResponse(BaseModel):
    """Response schema for recording a download"""
    success: bool = Field(..., description="Operation success status")
    download_count: int = Field(..., description="Updated download count")
    item_id: int = Field(..., description="Download item ID")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "success": True,
                "download_count": 1524,
                "item_id": 1
            }
        }
    }


class DownloadDetailResponse(BaseModel):
    """Response schema for full download detail including version history"""
    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Download item name")
    description: str = Field(..., description="Download item description")
    category: str = Field(..., description="Category of the download")
    file_key: str = Field(..., description="Storage key for the file")
    version: Optional[str] = Field(None, description="Version string")
    size: int = Field(..., description="File size in bytes")
    downloads_count: int = Field(..., description="Number of downloads")
    is_published: bool = Field(default=True, description="Whether item is published")
    is_featured: bool = Field(default=False, description="Whether item is featured")
    position: int = Field(default=0, description="Display position")
    download_url: str = Field(..., description="Signed download URL")
    screenshot_urls: List[str] = Field(default_factory=list, description="List of screenshot URLs")
    versions: List[VersionedDownload] = Field(default_factory=list, description="List of available versions")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "SillyFu 控制面板",
                "description": "SillyFu 桌面控制面板程序",
                "category": "application",
                "file_key": "sillyfu/releases/v1.2.0/SillyFu-Setup.exe",
                "version": "1.2.0",
                "size": 52428800,
                "downloads_count": 1523,
                "download_url": "https://skills.sillymd.com/...",
                "screenshot_urls": [],
                "versions": [],
                "created_at": "2026-03-20T10:00:00Z",
                "updated_at": "2026-03-20T10:00:00Z"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "detail": "Download item not found",
                "code": "DOWNLOAD_NOT_FOUND"
            }
        }
    }
