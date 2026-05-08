"""
Skill2 Module Schemas
Pydantic models for Skill2 processing, review, and packaging
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# Enums
# ============================================

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    SCANNED = "scanned"
    PACKAGED = "packaged"
    FAILED = "failed"


# ============================================
# Scan / Review Schemas
# ============================================

class SensitiveItem(BaseModel):
    """A single sensitive content finding from P1-P5 scan"""
    marker_type: str = Field(..., description="p1_explicit, p2_field_name, p3_format, p4_semantic, p5_position")
    content_preview: str = Field(..., description="First 100 chars of matched content")
    line_number: int = Field(0, description="Line number in the source content")
    column: int = Field(0, description="Column position")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    suggested_action: str = Field(..., description="encrypt or review")


class ScanResult(BaseModel):
    """Result of a P1-P5 content scan"""
    skill_id: int = Field(..., description="Skill ID")
    status: ProcessingStatus = Field(..., description="Processing status")
    total_sensitive: int = Field(0, description="Total sensitive items found")
    items: List[SensitiveItem] = Field(default_factory=list, description="Sensitive items")
    scan_time_ms: int = Field(0, description="Scan duration in milliseconds")
    content_hash: str = Field("", description="SHA-256 of scanned content")


# ============================================
# Encryption / Packaging Schemas
# ============================================

class EncryptedBlock(BaseModel):
    """An encrypted block within the .skill2 package"""
    name: str = Field(..., description="Block identifier")
    marker_type: str = Field(..., description="Type of marker")
    iv_hex: str = Field(..., description="Initialization vector (hex)")
    ciphertext_hex: str = Field(..., description="Encrypted content (hex)")
    tag_hex: str = Field(..., description="GCM authentication tag (hex)")


class Skill2Manifest(BaseModel):
    """The .skill2 manifest.json structure"""
    skill2_version: str = Field(..., description="Skill2 format version")
    identity: Dict[str, Any] = Field(..., description="Identity block: skill_id, declaration_id, name, version")
    author: Dict[str, Any] = Field(..., description="Author block: author_id, name")
    fee: Dict[str, Any] = Field(..., description="Fee block: type, amount, currency")
    content: Dict[str, Any] = Field(..., description="Content block: encrypted, checksum")


class Skill2Package(BaseModel):
    """Full Skill2 package result"""
    skill_id: int = Field(..., description="Skill ID")
    package_version: str = Field("1.0.0", description="Package version")
    declaration_id: str = Field(..., description="Unique declaration UUID")
    content_hash: str = Field(..., description="SHA-256 of original content")
    key_version: int = Field(1, description="Platform key version used")
    encrypted_blocks: List[EncryptedBlock] = Field(default_factory=list)
    platform_signature: str = Field("", description="RSA signature of manifest")
    package_url: str = Field("", description="TOS URL prefix of .skill2 package")
    manifest_url: str = Field("", description="TOS URL of manifest.json")
    created_at: str = Field("", description="ISO timestamp")


# ============================================
# API Request / Response Schemas
# ============================================

class ProcessRequest(BaseModel):
    """Request to trigger Skill2 processing"""
    skill_id: int = Field(..., description="Skill ID to process")
    force_reprocess: bool = Field(False, description="Force re-processing if already processed")


class StatusResponse(BaseModel):
    """Skill2 processing status response"""
    skill_id: int = Field(..., description="Skill ID")
    status: ProcessingStatus = Field(..., description="Current processing status")
    total_sensitive: int = Field(0, description="Total sensitive items found")
    sensitive_items: List[SensitiveItem] = Field(default_factory=list, description="Scan findings")
    package_url: Optional[str] = Field(None, description="TOS URL of .skill2 package")
    manifest_url: Optional[str] = Field(None, description="TOS URL of manifest.json")
    platform_signature: Optional[str] = Field(None, description="Platform signature")
    error_message: Optional[str] = Field(None, description="Error details if failed")
    created_at: Optional[str] = Field(None, description="Processing timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class LicenseVerifyRequest(BaseModel):
    """License verification request"""
    declaration_id: str = Field(..., description="Declaration ID of the skill")
    license_token: str = Field(..., description="License token from user")
    device_fingerprint: str = Field(..., description="Device fingerprint")


class LicenseVerifyResponse(BaseModel):
    """License verification response"""
    status: str = Field(..., description="success or failed")
    session_key: Optional[str] = Field(None, description="Session key if verified")
    author_id: Optional[str] = Field(None, description="Author ID")
    expires_in: int = Field(3600, description="Session expiry in seconds")


class UsageLogRequest(BaseModel):
    """Usage logging request"""
    skill_id: str = Field(..., description="Skill ID")
    declaration_id: str = Field(..., description="Declaration ID")
    author_id: str = Field(..., description="Author ID")
    usage_type: str = Field("run", description="Usage type: run, download, etc.")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")


class DeveloperStats(BaseModel):
    """Developer statistics response"""
    total_uses: int = Field(0, description="Total usage count")
    total_revenue: float = Field(0.0, description="Total revenue")
    skills: List[Dict[str, Any]] = Field(default_factory=list, description="Per-skill stats")


class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(True, description="Success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
