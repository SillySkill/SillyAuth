"""
Config Sync Routes
FastAPI routes for configuration sync API.

Prefix: /api/v1/config

Endpoints:
  GET  /version       -- Query version info
  GET  /file          -- Download config file
  POST /report        -- Client reports update result
  POST /publish       -- Admin publishes new version
  GET  /stats         -- Get update statistics
"""

import logging
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response

from .services import get_config_sync_service
from .schemas import UpdateReportRequest, PublishConfigRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/config", tags=["Config Sync"])


# ----------------------------------------------------------------
# GET /version
# ----------------------------------------------------------------

@router.get("/version", summary="Get version information")
async def get_version(
    request: Request,
    version: Optional[str] = Query(
        None,
        description="Version string, e.g. 'current' or 'v1.0.1'. Defaults to latest.",
    ),
):
    """
    Retrieve configuration version information.

    - **version**: Optional version string. Use ``current`` (or omit) to get
      the latest version. Use a specific tag like ``v1.0.1`` for a particular
      release.
    """
    try:
        service = get_config_sync_service()
        result = service.build_version_response(version=version)
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception("Failed to get version info")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------
# GET /file
# ----------------------------------------------------------------

@router.get("/file", summary="Download a configuration file")
async def download_file(
    request: Request,
    version: str = Query(..., description="Target version, e.g. 'v1.0.1'"),
    path: str = Query(..., description="File path relative to version root, e.g. 'config.json'"),
):
    """
    Download a specific configuration file for a given version.

    - **version**: Required version string (e.g. ``v1.0.1``).
    - **path**: Relative file path within that version (e.g. ``config.json``).
    """
    try:
        service = get_config_sync_service()
        file_data = service.get_file(version, path)

        if file_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"File '{path}' not found in version '{version}'",
            )

        return Response(
            content=file_data["content"],
            media_type="application/octet-stream",
            headers={
                "X-File-MD5": file_data.get("md5", ""),
                "X-File-Size": str(file_data.get("size", "")),
                "Content-Disposition": f'attachment; filename="{Path(path).name}"',
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to download file")
        raise HTTPException(status_code=500, detail=str(e))



# ----------------------------------------------------------------
# POST /report
# ----------------------------------------------------------------

@router.post("/report", summary="Report client update result")
async def report_update(
    request: Request,
    body: UpdateReportRequest,
):
    """
    Report the result of a client configuration update.

    The client reports whether the update succeeded, failed, or was rolled back.
    """
    try:
        service = get_config_sync_service()
        entry = service.report_update(
            device_id=body.device_id,
            old_version=body.old_version,
            new_version=body.new_version,
            status=body.status,
            error_message=body.error_message,
        )
        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "message": "Update report recorded",
                    "timestamp": entry["timestamp"],
                },
            }
        )
    except Exception as e:
        logger.exception("Failed to report update")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------
# POST /publish
# ----------------------------------------------------------------

@router.post("/publish", summary="Publish a new configuration version")
async def publish_version(
    request: Request,
    body: PublishConfigRequest,
):
    """
    Publish a new configuration version (admin endpoint).

    The request body specifies the version, release notes, files, and
    related metadata.
    """
    try:
        service = get_config_sync_service()
        version_entry = service.publish_version(body.model_dump())
        return JSONResponse(
            content={
                "success": True,
                "data": version_entry,
            }
        )
    except ValueError as e:
        logger.warning(f"Publish validation error: {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.exception("Failed to publish version")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------
# GET /stats
# ----------------------------------------------------------------

@router.get("/stats", summary="Get update statistics")
async def get_stats(request: Request):
    """
    Retrieve aggregated update statistics from the log file.

    Includes total updates, success/failure counts, version distribution,
    and the timestamp of the most recent update.
    """
    try:
        service = get_config_sync_service()
        stats = service.get_stats()
        return JSONResponse(
            content={
                "success": True,
                "data": stats.model_dump(),
            }
        )
    except Exception as e:
        logger.exception("Failed to get stats")
        raise HTTPException(status_code=500, detail=str(e))
