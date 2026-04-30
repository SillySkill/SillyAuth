"""
SillyClaw Version Management Module - Routes

FastAPI routes for version checking, downloading, and publishing.
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends, Header
from fastapi.responses import RedirectResponse, JSONResponse

from .schemas import (
    VersionInfo,
    VersionCheckResponse,
    PublishVersionRequest,
    VersionListResponse,
    DownloadResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/sillyclaw/version", tags=["sillyclaw"])


class MockVersionService:
    """Mock service for testing when database is not configured."""

    def get_latest_version(self):
        from .schemas import VersionInfo
        return VersionInfo(
            version="1.2.0",
            release_date="2026-03-20",
            download_url="https://skills.sillymd.com/sillyclaw/releases/v1.2.0/SillyClaw-Setup.exe",
            release_notes="1. 新增大虾塘动画效果\n2. 优化虾拳馆 PK 流程\n3. 修复若干 Bug",
            file_size=52428800,
            checksum="demo123"
        )

    def get_all_versions(self):
        from .schemas import VersionInfo
        return [
            VersionInfo(
                version="1.2.0",
                release_date="2026-03-20",
                download_url="https://skills.sillymd.com/sillyclaw/releases/v1.2.0/SillyClaw-Setup.exe",
                release_notes="Latest version"
            ),
            VersionInfo(
                version="1.1.0",
                release_date="2026-03-10",
                download_url="https://skills.sillymd.com/sillyclaw/releases/v1.1.0/SillyClaw-Setup.exe",
                release_notes="Previous version"
            )
        ]

    def get_version(self, version):
        from .schemas import VersionInfo
        return VersionInfo(
            version=version,
            release_date="2026-03-20",
            download_url=f"https://skills.sillymd.com/sillyclaw/releases/{version}/SillyClaw-Setup.exe",
            release_notes=f"Version {version} release"
        )

    def check_update(self, current_version):
        from .schemas import VersionInfo, VersionCheckResponse, VersionComparison
        latest = self.get_latest_version()
        needs_update = current_version < latest.version
        return VersionCheckResponse(
            needs_update=needs_update,
            current=current_version,
            latest=latest,
            comparison=VersionComparison.UPDATE if needs_update else VersionComparison.LATEST
        )


def get_version_service():
    """
    Dependency to get the version service instance.

    Returns mock service if database is not configured.
    """
    from . import _version_service
    if _version_service is None:
        return MockVersionService()
    return _version_service


def require_admin(api_key: Optional[str] = Header(None)):
    """
    Dependency to require admin authentication.

    In production, this should validate the API key against configured secrets.
    """
    expected_key = None  # Will be loaded from config

    # Get admin API key from environment or config
    try:
        expected_key = __import__('os').getenv('SILLYCLAW_ADMIN_API_KEY')
    except Exception:
        pass

    if expected_key and api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key for admin operations"
        )

    return True


@router.get(
    "",
    response_model=VersionInfo,
    summary="Get latest version",
    description="Get information about the latest SillyClaw version"
)
async def get_latest_version(
    service=Depends(get_version_service)
) -> VersionInfo:
    """
    Get the latest SillyClaw version information.

    Returns the most recent version's details including:
    - Version number
    - Release date
    - Download URL
    - Release notes (if available)
    - File size (if available)
    - Checksum (if available)

    This endpoint is cached for performance.
    """
    try:
        version_info = service.get_latest_version()
        if version_info is None:
            raise HTTPException(
                status_code=404,
                detail="No versions available"
            )
        return version_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest version: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest version: {str(e)}"
        )


@router.get(
    "/all",
    response_model=VersionListResponse,
    summary="List all versions",
    description="Get a list of all SillyClaw versions"
)
async def list_all_versions(
    service=Depends(get_version_service)
) -> VersionListResponse:
    """
    Get a list of all SillyClaw versions.

    Returns versions ordered by release date (newest first).
    """
    try:
        versions = service.get_all_versions()
        return VersionListResponse(
            versions=versions,
            total=len(versions)
        )
    except Exception as e:
        logger.error(f"Error listing versions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list versions: {str(e)}"
        )


@router.get(
    "/{version}",
    response_model=VersionInfo,
    summary="Get specific version",
    description="Get information about a specific SillyClaw version"
)
async def get_version(
    version: str,
    service=Depends(get_version_service)
) -> VersionInfo:
    """
    Get information about a specific SillyClaw version.

    Args:
        version: Version number (e.g., "1.2.0" or "v1.2.0")

    Returns:
        VersionInfo for the specified version
    """
    try:
        version_info = service.get_version(version)
        if version_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version} not found"
            )
        return version_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting version {version}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get version: {str(e)}"
        )


@router.get(
    "/{version}/download",
    summary="Download version file",
    description="Get a download URL for a specific version"
)
async def download_version(
    version: str,
    service=Depends(get_version_service)
):
    """
    Get a signed download URL for a specific version.

    This redirects to the signed TOS URL for downloading the installer.

    Args:
        version: Version number (e.g., "1.2.0" or "v1.2.0")

    Returns:
        Redirect response to the signed download URL
    """
    try:
        # Verify version exists
        version_info = service.get_version(version)
        if version_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version} not found"
            )

        # Get the download URL
        download_url = service.tos_client.get_download_url(version)

        # Redirect to download URL
        return RedirectResponse(url=download_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL for {version}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(e)}"
        )


@router.post(
    "",
    response_model=VersionInfo,
    status_code=201,
    summary="Publish new version",
    description="Publish a new SillyClaw version (Admin only)",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        409: {"model": ErrorResponse, "description": "Version already exists"}
    }
)
async def publish_version(
    data: PublishVersionRequest,
    admin: bool = Depends(require_admin),
    service=Depends(get_version_service)
) -> VersionInfo:
    """
    Publish a new SillyClaw version.

    This endpoint is restricted to admin users only. It will:
    1. Validate the version format
    2. Upload version metadata to the database
    3. Mark the new version as the latest
    4. Clear relevant caches

    Args:
        data: PublishVersionRequest with version details

    Returns:
        VersionInfo for the newly published version
    """
    try:
        version_info = service.publish_version(data)
        logger.info(f"Published version {data.version}")
        return version_info
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error publishing version: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish version: {str(e)}"
        )


# Separate router for update check (simpler endpoint)
check_update_router = APIRouter(prefix="/api/v1/sillyclaw", tags=["sillyclaw"])


@check_update_router.get(
    "/check-update",
    response_model=VersionCheckResponse,
    summary="Check for updates",
    description="Check if an update is available for the current version"
)
async def check_update(
    current: str = Query(..., alias="current", description="Current version number"),
    service=Depends(get_version_service)
) -> VersionCheckResponse:
    """
    Check if an update is available for SillyClaw.

    This endpoint is used by the SillyClaw control panel to check
    for available updates.

    Args:
        current: Current version string (e.g., "1.0.0")

    Returns:
        VersionCheckResponse with update status and latest version info

    Example response when update is available:
    ```json
    {
        "needs_update": true,
        "current": "1.0.0",
        "latest": {
            "version": "1.2.0",
            "release_date": "2026-03-20",
            "download_url": "https://...",
            "release_notes": "..."
        }
    }
    ```

    Example response when already latest:
    ```json
    {
        "needs_update": false,
        "current": "1.2.0",
        "latest": {
            "version": "1.2.0",
            ...
        }
    }
    ```
    """
    try:
        return service.check_update(current)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error checking update for {current}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check update: {str(e)}"
        )


@check_update_router.delete(
    "/sillyclaw/version/{version}",
    summary="Delete version",
    description="Delete a specific version (Admin only)",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Version not found"}
    }
)
async def delete_version(
    version: str,
    admin: bool = Depends(require_admin),
    service=Depends(get_version_service)
):
    """
    Delete a specific SillyClaw version.

    This endpoint is restricted to admin users only.

    Note: You cannot delete the only remaining version.

    Args:
        version: Version number to delete

    Returns:
        Success message
    """
    try:
        service.delete_version(version)
        return {"message": f"Version {version} deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting version {version}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete version: {str(e)}"
        )
