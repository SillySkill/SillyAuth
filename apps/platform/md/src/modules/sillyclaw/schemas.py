"""
SillyClaw Version Management Module - Schemas

Pydantic schemas for version management API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class VersionComparison(str, Enum):
    """Version comparison result"""
    UPDATE = "update"  # A new version is available
    LATEST = "latest"  # Already on the latest version


class VersionInfo(BaseModel):
    """Version information schema"""
    version: str = Field(..., description="Version number (semantic versioning)")
    release_date: str = Field(..., description="Release date in ISO 8601 format")
    download_url: str = Field(..., description="Download URL for the version")
    release_notes: Optional[str] = Field(None, description="Release notes/changelog")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="SHA-256 checksum of the file")

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.2.0",
                "release_date": "2026-03-20",
                "download_url": "https://skills.sillymd.com/sillyclaw/releases/v1.2.0/SillyClaw-Setup.exe",
                "release_notes": "1. 新增大虾塘动画效果\n2. 优化虾拳馆 PK 流程\n3. 修复若干 Bug",
                "file_size": 52428800,
                "checksum": "a1b2c3d4e5f6..."
            }
        }


class VersionCheckRequest(BaseModel):
    """Version check request schema (query parameter based)"""
    current_version: str = Field(..., description="Current version to check against")


class VersionCheckResponse(BaseModel):
    """Version check response schema"""
    needs_update: bool = Field(..., description="Whether an update is available")
    current: str = Field(..., description="The version the client is currently on")
    latest: VersionInfo = Field(..., description="Latest version information")

    class Config:
        json_schema_extra = {
            "example": {
                "needs_update": True,
                "current": "1.0.0",
                "latest": {
                    "version": "1.2.0",
                    "release_date": "2026-03-20",
                    "download_url": "https://skills.sillymd.com/sillyclaw/releases/v1.2.0/SillyClaw-Setup.exe",
                    "release_notes": "1. 新增大虾塘动画效果\n2. 优化虾拳馆 PK 流程"
                }
            }
        }


class PublishVersionRequest(BaseModel):
    """Publish new version request schema"""
    version: str = Field(..., description="Version number to publish")
    release_date: str = Field(..., description="Release date in ISO 8601 format (YYYY-MM-DD)")
    release_notes: Optional[str] = Field(None, description="Release notes/changelog")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="SHA-256 checksum of the file")

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.2.0",
                "release_date": "2026-03-20",
                "release_notes": "1. 新增大虾塘动画效果\n2. 优化虾拳馆 PK 流程",
                "file_size": 52428800,
                "checksum": "a1b2c3d4e5f6..."
            }
        }


class VersionListResponse(BaseModel):
    """Response schema for listing all versions"""
    versions: List[VersionInfo] = Field(..., description="List of all versions")
    total: int = Field(..., description="Total number of versions")


class DownloadResponse(BaseModel):
    """Download redirect response schema"""
    url: str = Field(..., description="Signed download URL")
    expires_in: int = Field(..., description="URL expiration time in seconds")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Version not found",
                "code": "VERSION_NOT_FOUND"
            }
        }
