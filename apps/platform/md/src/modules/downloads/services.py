"""
Downloads Module - Services

Business logic for download management including item retrieval,
URL generation, download counting, and category management.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import os

from psycopg2.extras import RealDictCursor

from .schemas import (
    DownloadItemCreate,
    DownloadItemResponse,
    DownloadCategory,
    VersionedDownload,
    SillyClawDownloadResponse,
    LikeResponse,
    RecordDownloadResponse
)

logger = logging.getLogger(__name__)


class DownloadService:
    """
    Service for managing download items.

    Handles download item storage, retrieval, URL generation,
    download counting, and category management with database integration.
    """

    def __init__(
        self,
        db_config: dict,
        storage_service: Any,
        config: Dict[str, Any]
    ):
        """
        Initialize download service.

        Args:
            db_config: Database connection configuration
            storage_service: Storage service for URL generation
            config: Module configuration dictionary
        """
        self.db_config = db_config
        self.storage_service = storage_service
        self.config = config
        self.download_base_url = config.get("download_base_url", "https://skills.sillymd.com")
        self.featured_downloads = config.get("featured_downloads", [])
        self.cache_ttl = config.get("cache_ttl", 3600)
        self._cache: Dict[str, Any] = {}  # Simple in-memory cache

    def _get_db_connection(self):
        """Get a database connection using the configured settings."""
        import psycopg2
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"]
        )

    def _get_signed_url(self, file_key: str, expires_seconds: int = 3600) -> str:
        """
        Generate a signed download URL for a file.

        Args:
            file_key: Storage key for the file
            expires_seconds: URL expiration time in seconds

        Returns:
            Signed download URL
        """
        try:
            # Try to use storage service for signed URL
            if hasattr(self.storage_service, 'get_url'):
                return self.storage_service.get_url(file_key, signed=True, expires_seconds=expires_seconds)
        except Exception as e:
            logger.warning(f"Failed to get signed URL from storage service: {e}")

        # Fallback to direct URL construction
        return f"{self.download_base_url}/{file_key}"

    def _row_to_download_item(self, row: dict, include_url: bool = True) -> DownloadItemResponse:
        """
        Convert a database row to DownloadItemResponse schema.

        Args:
            row: Database row dictionary
            include_url: Whether to include signed URL

        Returns:
            DownloadItemResponse instance
        """
        download_url = ""
        if include_url:
            download_url = self._get_signed_url(row['file_key'])

        return DownloadItemResponse(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            category=row['category'],
            file_key=row['file_key'],
            version=row.get('version'),
            size=row.get('size', 0),
            downloads_count=row.get('downloads_count', 0),
            like_count=row.get('like_count', 0),
            view_count=row.get('view_count', 0),
            slug=row.get('slug'),
            download_url=download_url,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )

    def get_download_item(self, item_id: int) -> Optional[DownloadItemResponse]:
        """
        Get a download item by ID with signed URL.

        Args:
            item_id: Download item ID

        Returns:
            DownloadItemResponse with signed URL, or None if not found

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, name, description, category, file_key,
                               version, size, downloads_count, like_count,
                               view_count, slug, created_at, updated_at
                        FROM download_items
                        WHERE id = %s AND is_published = TRUE
                    """, (item_id,))
                    row = cur.fetchone()

                    if row:
                        return self._row_to_download_item(row)

                    return None

        except psycopg2.Error as e:
            logger.error(f"Database error getting download item {item_id}: {e}")
            raise

    def list_downloads(
        self,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[DownloadItemResponse], int]:
        """
        List download items with optional category filter and pagination.

        Args:
            category: Optional category filter
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (list of DownloadItemResponse, total count)

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Build query conditions
                    conditions = ["is_published = TRUE"]
                    params = []

                    if category:
                        conditions.append("category = %s")
                        params.append(category)

                    # Count total
                    count_query = f"SELECT COUNT(*) as total FROM download_items WHERE {' AND '.join(conditions)}"
                    cur.execute(count_query, params)
                    total = cur.fetchone()['total']

                    # Get items with pagination
                    offset = (page - 1) * limit
                    list_query = f"""
                        SELECT id, name, description, category, file_key,
                               version, size, downloads_count, like_count,
                               view_count, slug, created_at, updated_at
                        FROM download_items
                        WHERE {' AND '.join(conditions)}
                        ORDER BY position ASC, created_at DESC
                        LIMIT %s OFFSET %s
                    """
                    cur.execute(list_query, params + [limit, offset])
                    rows = cur.fetchall()

                    items = [self._row_to_download_item(row) for row in rows]
                    return items, total

        except psycopg2.Error as e:
            logger.error(f"Database error listing downloads: {e}")
            raise

    def get_categories(self) -> List[DownloadCategory]:
        """
        Get all download categories with item counts.

        Returns:
            List of DownloadCategory with counts

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        # Category display names mapping
        category_names = {
            "application": "应用程序",
            "tool": "开发工具",
            "document": "文档资料",
            "plugin": "插件扩展",
            "other": "其他资源"
        }

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT category, COUNT(*) as items_count
                        FROM download_items
                        WHERE is_published = TRUE
                        GROUP BY category
                    """)
                    rows = cur.fetchall()

                    categories = []
                    for row in rows:
                        categories.append(DownloadCategory(
                            id=row['category'],
                            name=category_names.get(row['category'], row['category']),
                            items_count=row['items_count']
                        ))

                    return categories

        except psycopg2.Error as e:
            logger.error(f"Database error getting categories: {e}")
            raise

    def increment_download_count(self, item_id: int) -> int:
        """
        Increment the download count for an item.

        Args:
            item_id: Download item ID

        Returns:
            New download count

        Raises:
            ValueError: If item not found
            Exception: If database operation fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Update count and return new value
                    cur.execute("""
                        UPDATE download_items
                        SET downloads_count = downloads_count + 1
                        WHERE id = %s AND is_published = TRUE
                        RETURNING downloads_count
                    """, (item_id,))
                    row = cur.fetchone()

                    if not row:
                        raise ValueError(f"Download item {item_id} not found")

                    conn.commit()
                    return row['downloads_count']

        except psycopg2.Error as e:
            logger.error(f"Database error incrementing download count for {item_id}: {e}")
            raise

    def get_featured_download(self) -> Optional[DownloadItemResponse]:
        """
        Get the featured SillyClaw download with latest version.

        This retrieves the SillyClaw featured download based on module config.

        Returns:
            DownloadItemResponse for featured item, or None if not found
        """
        import psycopg2

        # Find sillyclaw in featured downloads
        sillyclaw_config = None
        for item in self.featured_downloads:
            if item.get('id') == 'sillyclaw':
                sillyclaw_config = item
                break

        if not sillyclaw_config:
            logger.warning("SillyClaw not found in featured downloads config")
            return None

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get the latest SillyClaw version
                    cur.execute("""
                        SELECT v.id, v.name, v.description, v.category, v.file_key,
                               v.version, v.size, v.downloads_count,
                               v.like_count, v.view_count, v.slug,
                               v.created_at, v.updated_at
                        FROM download_items v
                        INNER JOIN (
                            SELECT file_key, MAX(created_at) as max_date
                            FROM download_items
                            WHERE category = 'application'
                            AND name LIKE '%SillyClaw%'
                            AND is_published = TRUE
                            GROUP BY file_key
                        ) latest ON v.file_key = latest.file_key
                        AND v.created_at = latest.max_date
                        WHERE v.category = 'application'
                        AND v.is_published = TRUE
                        ORDER BY v.created_at DESC
                        LIMIT 1
                    """)
                    row = cur.fetchone()

                    if row:
                        return self._row_to_download_item(row)

                    return None

        except psycopg2.Error as e:
            logger.error(f"Database error getting featured download: {e}")
            raise

    def get_sillyclaw_download(self, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get SillyClaw download information.

        If version is provided, returns that specific version.
        Otherwise returns the latest version.

        Args:
            version: Optional specific version to retrieve

        Returns:
            Dictionary with SillyClaw download info, or None if not found
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if version:
                        # Normalize version string
                        version = version.lstrip('v')
                        if not version.startswith('v'):
                            version = 'v' + version

                        cur.execute("""
                            SELECT version, release_date, download_url,
                                   release_notes, file_size, checksum
                            FROM sillyclaw_versions
                            WHERE version = %s OR version = %s
                            ORDER BY created_at DESC
                            LIMIT 1
                        """, (version, version.lstrip('v')))
                    else:
                        # Get latest version
                        cur.execute("""
                            SELECT version, release_date, download_url,
                                   release_notes, file_size, checksum
                            FROM sillyclaw_versions
                            WHERE is_latest = TRUE
                            ORDER BY created_at DESC
                            LIMIT 1
                        """)

                        # If no latest marked, get most recent
                        if cur.fetchone() is None:
                            cur.execute("""
                                SELECT version, release_date, download_url,
                                       release_notes, file_size, checksum
                                FROM sillyclaw_versions
                                ORDER BY created_at DESC
                                LIMIT 1
                            """)

                    row = cur.fetchone()

                    if row:
                        return {
                            "version": row['version'],
                            "release_date": str(row['release_date']) if row['release_date'] else None,
                            "download_url": row['download_url'],
                            "release_notes": row.get('release_notes'),
                            "file_size": row.get('file_size'),
                            "checksum": row.get('checksum')
                        }

                    return None

        except psycopg2.Error as e:
            logger.error(f"Database error getting SillyClaw download: {e}")
            raise

    def like_download(self, item_id: int) -> dict:
        """
        Increment the like count for a download item.

        Args:
            item_id: Download item ID

        Returns:
            Dict with success status and updated like count

        Raises:
            ValueError: If item not found
            Exception: If database operation fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        UPDATE download_items
                        SET like_count = like_count + 1
                        WHERE id = %s AND is_published = TRUE
                        RETURNING like_count
                    """, (item_id,))
                    row = cur.fetchone()

                    if not row:
                        raise ValueError(f"Download item {item_id} not found")

                    conn.commit()
                    return {
                        "success": True,
                        "like_count": row['like_count'],
                        "item_id": item_id
                    }

        except psycopg2.Error as e:
            logger.error(f"Database error liking download item {item_id}: {e}")
            raise

    def get_download_by_slug(self, slug: str) -> Optional[DownloadItemResponse]:
        """
        Get a download item by its URL-friendly slug.

        Supports slug-based lookup as an alternative to numeric ID.

        Args:
            slug: URL-friendly slug string

        Returns:
            DownloadItemResponse with signed URL, or None if not found

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, name, description, category, file_key,
                               version, size, downloads_count, like_count,
                               view_count, slug, created_at, updated_at
                        FROM download_items
                        WHERE slug = %s AND is_published = TRUE
                    """, (slug,))
                    row = cur.fetchone()

                    if row:
                        return self._row_to_download_item(row)

                    return None

        except psycopg2.Error as e:
            logger.error(f"Database error getting download by slug '{slug}': {e}")
            raise

    def record_download(self, item_id: int, user_id: Optional[int] = None) -> dict:
        """
        Record a download event and increment download count.

        This also logs the download in download_records table for analytics.

        Args:
            item_id: Download item ID
            user_id: Optional user ID who performed the download

        Returns:
            Dict with success status and updated download count

        Raises:
            ValueError: If item not found
            Exception: If database operation fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Increment download count and return new value
                    cur.execute("""
                        UPDATE download_items
                        SET downloads_count = downloads_count + 1
                        WHERE id = %s AND is_published = TRUE
                        RETURNING downloads_count
                    """, (item_id,))
                    row = cur.fetchone()

                    if not row:
                        raise ValueError(f"Download item {item_id} not found")

                    new_count = row['downloads_count']

                    # Log download record if download_records table exists
                    try:
                        cur.execute("""
                            INSERT INTO download_records (user_id, download_id, download_status, created_at)
                            VALUES (%s, %s, 'completed', CURRENT_TIMESTAMP)
                        """, (user_id, item_id))
                    except psycopg2.Error:
                        # download_records table may not exist yet, that's OK
                        conn.rollback()
                        # Re-run the increment since we rolled back
                        cur.execute("""
                            UPDATE download_items
                            SET downloads_count = downloads_count + 1
                            WHERE id = %s AND is_published = TRUE
                            RETURNING downloads_count
                        """, (item_id,))
                        row = cur.fetchone()
                        if row:
                            new_count = row['downloads_count']

                    conn.commit()
                    return {
                        "success": True,
                        "download_count": new_count,
                        "item_id": item_id
                    }

        except psycopg2.Error as e:
            logger.error(f"Database error recording download for {item_id}: {e}")
            raise

    def initialize_database(self) -> None:
        """
        Initialize the database tables for download items.

        Creates the download_items table if it doesn't exist.

        Raises:
            Exception: If table creation fails
        """
        import psycopg2

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS download_items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL DEFAULT 'other',
            file_key TEXT NOT NULL,
            version VARCHAR(50),
            size BIGINT DEFAULT 0,
            downloads_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            slug VARCHAR(255),
            is_published BOOLEAN DEFAULT TRUE,
            is_featured BOOLEAN DEFAULT FALSE,
            position INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS download_records (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            download_id INTEGER NOT NULL REFERENCES download_items(id) ON DELETE CASCADE,
            download_status VARCHAR(50) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for faster queries
        CREATE INDEX IF NOT EXISTS idx_download_items_category
        ON download_items(category);

        CREATE INDEX IF NOT EXISTS idx_download_items_is_published
        ON download_items(is_published);

        CREATE INDEX IF NOT EXISTS idx_download_items_is_featured
        ON download_items(is_featured) WHERE is_featured = TRUE;

        -- Create trigger to auto-update updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        DROP TRIGGER IF EXISTS update_download_items_updated_at ON download_items;
        CREATE TRIGGER update_download_items_updated_at
            BEFORE UPDATE ON download_items
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """

        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_sql)
                    conn.commit()
                    logger.info("Download items table initialized successfully")

        except psycopg2.Error as e:
            logger.error(f"Database error initializing table: {e}")
            raise


# Global service instance
_download_service: Optional[DownloadService] = None


def get_download_service() -> Optional[DownloadService]:
    """Get the global download service instance."""
    return _download_service


def set_download_service(service: DownloadService) -> None:
    """Set the global download service instance."""
    global _download_service
    _download_service = service
