"""
Skill2 Routes
API endpoints for Skill2 processing, review, and packaging
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from .schemas import (
    ProcessRequest,
    ScanResult,
    StatusResponse,
    LicenseVerifyRequest,
    LicenseVerifyResponse,
    UsageLogRequest,
    DeveloperStats,
)
from .services import skill2_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/skill2", tags=["Skill2"])


# ============================================
# Auth Helpers
# ============================================

def get_current_admin():
    """Get current admin user (placeholder)."""
    return {"id": 1, "username": "admin", "role": "super_admin"}


HAS_AUTH = True


# ============================================
# Processing Endpoints
# ============================================

@router.post("/process/{skill_id}", response_model=dict)
async def process_skill(
    skill_id: int,
    request: Request,
    force_reprocess: bool = Query(False, description="Force re-processing"),
):
    """
    Process a skill: scan content with P1-P5 strategy.
    If auto_package is enabled, full packaging runs as background task.
    """
    user = getattr(request.state, "user", None)
    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="需要登录")

    try:
        scan_result = skill2_service.scan_skill_content(skill_id)
        if not scan_result:
            raise HTTPException(status_code=404, detail="Skill 不存在或无法扫描")

        # If auto-package is enabled, trigger full pipeline in background
        from core.config import get_skill2_config
        if get_skill2_config().auto_package_on_publish:
            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, skill2_service.process_full_pipeline, skill_id)

        return {
            "success": True,
            "message": "Scan complete",
            "data": scan_result,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Skill2 process failed for skill {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/process/{skill_id}/review", response_model=dict)
async def review_skill(
    skill_id: int,
    request: Request,
):
    """
    Run P1-P5 auto-review on a skill without triggering full packaging.
    Returns scan results for admin preview.
    """
    try:
        scan_result = skill2_service.scan_skill_content(skill_id)
        if not scan_result:
            raise HTTPException(status_code=404, detail="Skill 不存在")

        return {
            "success": True,
            "message": "评审完成",
            "data": scan_result,
        }

    except Exception as e:
        logger.error(f"Skill2 review failed for skill {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=f"评审失败: {str(e)}")


# ============================================
# Status Endpoint
# ============================================

@router.get("/status/{skill_id}", response_model=dict)
async def get_processing_status(skill_id: int):
    """Check the Skill2 processing status for a skill."""
    record = skill2_service.get_processing_status(skill_id)

    if not record:
        return {
            "success": True,
            "data": {
                "skill_id": skill_id,
                "status": "pending",
                "total_sensitive": 0,
                "sensitive_items": [],
            }
        }

    # Parse scan_summary JSONB
    sensitive_items = []
    scan_summary = record.get('scan_summary')
    if scan_summary:
        if isinstance(scan_summary, str):
            import json
            try:
                scan_summary = json.loads(scan_summary)
            except Exception:
                scan_summary = None
        if scan_summary and isinstance(scan_summary, dict):
            sensitive_items = scan_summary.get('items', [])

    return {
        "success": True,
        "data": {
            "skill_id": record['skill_id'],
            "status": record['status'],
            "total_sensitive": record.get('sensitive_count', 0),
            "sensitive_items": sensitive_items,
            "package_url": record.get('package_url'),
            "manifest_url": record.get('manifest_url'),
            "platform_signature": record.get('platform_signature'),
            "error_message": record.get('error_message'),
            "created_at": str(record.get('created_at', '')),
            "updated_at": str(record.get('updated_at', '')),
        }
    }


# ============================================
# License & Usage Endpoints (for Agent integration)
# ============================================

@router.post("/verify", response_model=dict)
async def verify_license(
    req: LicenseVerifyRequest,
    request: Request,
):
    """
    Verify a License Token for a skill.
    Called by Agent runtime to authorize skill execution.
    """
    result = skill2_service.verify_license(
        declaration_id=req.declaration_id,
        license_token=req.license_token,
        device_fingerprint=req.device_fingerprint,
    )
    return {
        "success": result['status'] == 'success',
        "data": result,
    }


@router.post("/log_usage", response_model=dict)
async def log_usage(
    req: UsageLogRequest,
    request: Request,
):
    """Log skill usage for tracking and revenue sharing."""
    success = skill2_service.log_usage(req.model_dump())
    return {
        "success": success,
        "message": "Usage logged",
    }


@router.get("/developer/stats", response_model=dict)
async def get_developer_stats(
    author_id: int = Query(..., description="Author ID"),
    request: Request = None,
):
    """Get usage statistics and revenue for a developer."""
    stats = skill2_service.get_developer_stats(author_id)
    return {
        "success": True,
        "data": stats,
    }


# ============================================
# Admin Endpoints
# ============================================

@router.post("/admin/generate-key", response_model=dict)
async def generate_key_pair(
    request: Request,
    current_admin = Depends(get_current_admin) if HAS_AUTH else None,
):
    """Admin: Generate a new platform RSA-2048 key pair."""
    if HAS_AUTH and not current_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    result = skill2_service.generate_key_pair()
    if not result:
        raise HTTPException(status_code=500, detail="密钥生成失败")

    return {
        "success": True,
        "message": "密钥已生成",
        "data": {
            "key_version": result['key_version'],
            "algorithm": result['algorithm'],
        }
    }


@router.post("/admin/process/{skill_id}/package", response_model=dict)
async def admin_package_skill(
    skill_id: int,
    request: Request,
    current_admin = Depends(get_current_admin) if HAS_AUTH else None,
):
    """Admin: Manually trigger full Skill2 packaging."""
    if HAS_AUTH and not current_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        result = skill2_service.process_full_pipeline(skill_id)
        if not result:
            raise HTTPException(status_code=500, detail="打包失败")

        return {
            "success": True,
            "message": "打包完成",
            "data": result,
        }

    except Exception as e:
        logger.error(f"Admin packaging failed for skill {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=f"打包失败: {str(e)}")
