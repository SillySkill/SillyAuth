"""
Downloads Module - Routes

FastAPI routes for download listing, retrieval, and SillyClaw-specific downloads.
"""

import logging
import math
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Header
from fastapi.responses import RedirectResponse, JSONResponse

from .schemas import (
    DownloadItemResponse,
    DownloadCategory,
    DownloadListResponse,
    FeaturedDownloadResponse,
    SillyClawDownloadResponse,
    LikeResponse,
    RecordDownloadResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter(prefix="/api/v1/downloads", tags=["downloads"])


def get_download_service():
    """
    Dependency to get the download service instance.

    This should be set by the module's on_startup.
    """
    from .services import get_download_service
    service = get_download_service()
    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Download service not initialized"
        )
    return service


@router.get(
    "",
    response_model=DownloadListResponse,
    summary="List downloads",
    description="Get a paginated list of download items"
)
async def list_downloads(
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service=Depends(get_download_service)
) -> DownloadListResponse:
    """
    Get a paginated list of download items.

    Supports optional category filtering and pagination.

    Args:
        category: Filter by category (application, tool, document, plugin, other)
        page: Page number (1-indexed)
        limit: Number of items per page (max 100)

    Returns:
        DownloadListResponse with items and pagination info
    """
    try:
        items, total = service.list_downloads(category=category, page=page, limit=limit)
        total_pages = math.ceil(total / limit) if total > 0 else 1

        return DownloadListResponse(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error listing downloads: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list downloads: {str(e)}"
        )


@router.get(
    "/categories",
    response_model=List[DownloadCategory],
    summary="List categories",
    description="Get all download categories with item counts"
)
async def get_categories(
    service=Depends(get_download_service)
) -> List[DownloadCategory]:
    """
    Get all download categories with their item counts.

    Returns:
        List of categories with item counts
    """
    try:
        return service.get_categories()
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get categories: {str(e)}"
        )


@router.get(
    "/featured",
    response_model=FeaturedDownloadResponse,
    summary="Get featured downloads",
    description="Get the featured download items"
)
async def get_featured_downloads(
    service=Depends(get_download_service)
) -> FeaturedDownloadResponse:
    """
    Get featured download items.

    Returns:
        FeaturedDownloadResponse with featured items
    """
    try:
        featured_item = service.get_featured_download()
        items = [featured_item] if featured_item else []
        return FeaturedDownloadResponse(items=items, total=len(items))
    except Exception as e:
        logger.error(f"Error getting featured downloads: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get featured downloads: {str(e)}"
        )


@router.get(
    "/{item_id}",
    response_model=DownloadItemResponse,
    summary="Get download item",
    description="Get details of a specific download item",
    responses={
        404: {"model": ErrorResponse, "description": "Download item not found"}
    }
)
async def get_download_item(
    item_id: int,
    service=Depends(get_download_service)
) -> DownloadItemResponse:
    """
    Get details of a specific download item.

    Args:
        item_id: Download item ID

    Returns:
        DownloadItemResponse with full details including signed URL
    """
    try:
        item = service.get_download_item(item_id)
        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Download item {item_id} not found"
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting download item {item_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get download item: {str(e)}"
        )


@router.get(
    "/{item_id}/file",
    summary="Download file",
    description="Redirect to signed download URL",
    responses={
        302: {"description": "Redirect to download URL"},
        404: {"model": ErrorResponse, "description": "Download item not found"}
    }
)
async def download_file(
    item_id: int,
    service=Depends(get_download_service)
):
    """
    Get download file URL and redirect to it.

    This endpoint increments the download count and redirects
    to the signed download URL.

    Args:
        item_id: Download item ID

    Returns:
        Redirect response to signed download URL
    """
    try:
        # Get the item
        item = service.get_download_item(item_id)
        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Download item {item_id} not found"
            )

        # Increment download count
        service.increment_download_count(item_id)

        # Redirect to download URL
        return RedirectResponse(url=item.download_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {item_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )


@router.get(
    "/sillyclaw",
    response_model=SillyClawDownloadResponse,
    summary="Get SillyClaw latest",
    description="Get the latest SillyClaw download",
    responses={
        404: {"model": ErrorResponse, "description": "No SillyClaw version found"}
    }
)
async def get_sillyclaw_latest(
    service=Depends(get_download_service)
) -> SillyClawDownloadResponse:
    """
    Get the latest SillyClaw version download.

    Returns:
        SillyClawDownloadResponse with latest version info
    """
    try:
        download_info = service.get_sillyclaw_download(version=None)
        if download_info is None:
            raise HTTPException(
                status_code=404,
                detail="No SillyClaw version found"
            )
        return SillyClawDownloadResponse(**download_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SillyClaw latest: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get SillyClaw version: {str(e)}"
        )


@router.get(
    "/sillyclaw/{version}",
    response_model=SillyClawDownloadResponse,
    summary="Get SillyClaw specific version",
    description="Get a specific SillyClaw version download",
    responses={
        404: {"model": ErrorResponse, "description": "Version not found"}
    }
)
async def get_sillyclaw_version(
    version: str,
    service=Depends(get_download_service)
) -> SillyClawDownloadResponse:
    """
    Get a specific SillyClaw version download.

    Args:
        version: Version string (e.g., "1.2.0" or "v1.2.0")

    Returns:
        SillyClawDownloadResponse with version info
    """
    try:
        download_info = service.get_sillyclaw_download(version=version)
        if download_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"SillyClaw version {version} not found"
            )
        return SillyClawDownloadResponse(**download_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SillyClaw version {version}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get SillyClaw version: {str(e)}"
        )


# ============================================================================
# Slug-based Lookup & Social Endpoints
# ============================================================================

@router.get(
    "/slug/{slug}",
    response_model=DownloadItemResponse,
    summary="Get download by slug",
    description="Get details of a download item by its URL-friendly slug",
    responses={
        404: {"model": ErrorResponse, "description": "Download item not found"}
    }
)
async def get_download_by_slug(
    slug: str,
    service=Depends(get_download_service)
) -> DownloadItemResponse:
    """
    Get details of a download item using its slug.

    Supports slug-based lookup as an alternative to numeric ID.

    Args:
        slug: URL-friendly slug identifier

    Returns:
        DownloadItemResponse with full details including signed URL
    """
    try:
        item = service.get_download_by_slug(slug)
        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Download item with slug '{slug}' not found"
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting download by slug '{slug}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get download item: {str(e)}"
        )


@router.post(
    "/{item_id}/like",
    response_model=LikeResponse,
    summary="Like a download item",
    description="Increment the like/favorite count for a download item",
    responses={
        404: {"model": ErrorResponse, "description": "Download item not found"}
    }
)
async def like_download(
    item_id: int,
    service=Depends(get_download_service)
) -> LikeResponse:
    """
    Like/favorite a download item.

    Increments the like_count for the specified download item.

    Args:
        item_id: Download item ID

    Returns:
        LikeResponse with success status and updated like count
    """
    try:
        result = service.like_download(item_id)
        return LikeResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error liking download item {item_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to like download item: {str(e)}"
        )


@router.post(
    "/{item_id}/record-download",
    response_model=RecordDownloadResponse,
    summary="Record a download event",
    description="Record a download event and increment download count",
    responses={
        404: {"model": ErrorResponse, "description": "Download item not found"}
    }
)
async def record_download(
    item_id: int,
    user_id: Optional[int] = None,
    service=Depends(get_download_service)
) -> RecordDownloadResponse:
    """
    Record a download event for tracking.

    Increments download_count and logs the download event.
    This is separate from the file download redirect endpoint and is
    useful for client-side download tracking.

    Args:
        item_id: Download item ID
        user_id: Optional user ID who performed the download

    Returns:
        RecordDownloadResponse with success status and updated download count
    """
    try:
        result = service.record_download(item_id, user_id=user_id)
        return RecordDownloadResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error recording download {item_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record download: {str(e)}"
        )
