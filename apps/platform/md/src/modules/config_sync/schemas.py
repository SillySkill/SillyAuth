"""
Config Sync Schemas
Pydantic models for configuration sync requests and responses
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class VersionInfo(BaseModel):
    """版本信息"""
    version: str
    version_code: int
    release_date: Optional[datetime] = None
    release_notes: str = ""
    force_update: bool = False
    min_compatible_version: Optional[str] = None
    files: List[Dict[str, Any]] = []
    deleted_files: List[str] = []


class VersionListResponse(BaseModel):
    """版本列表响应"""
    current_version: Optional[VersionInfo] = None
    versions: List[VersionInfo] = []
    latest_version: Optional[str] = None


class UpdateReportRequest(BaseModel):
    """更新结果上报"""
    device_id: str = Field(..., min_length=1)
    old_version: str = Field(..., min_length=1)
    new_version: str = Field(..., min_length=1)
    status: str = Field(..., pattern="^(success|failed|rollback)$")
    error_message: Optional[str] = None


class PublishConfigRequest(BaseModel):
    """发布新版本"""
    version: str = Field(..., min_length=1)
    version_code: int = Field(..., gt=0)
    release_notes: str = ""
    force_update: bool = False
    min_compatible_version: Optional[str] = None
    files: List[Dict[str, Any]] = Field(default_factory=list)
    deleted_files: List[str] = Field(default_factory=list)


class UpdateStats(BaseModel):
    """更新统计"""
    total_updates: int = 0
    successful_updates: int = 0
    failed_updates: int = 0
    version_distribution: Dict[str, int] = {}
    last_update_time: Optional[datetime] = None
