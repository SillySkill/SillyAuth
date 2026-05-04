"""
SillyFu Version Management Module - Services

Business logic for SillyFu version management including version checking,
comparison, publishing, and retrieval.
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, date
import re

from psycopg2.extras import RealDictCursor

from .schemas import VersionInfo, VersionCheckResponse, PublishVersionRequest, VersionComparison
from .tos_client import TosClient, create_tos_client_from_config

logger = logging.getLogger(__name__)


class SillyFuVersionService:
    """
    Service for managing SillyFu versions.

    Handles version storage, retrieval, comparison, and publishing
    operations with database and TOS integration.
    """

    def __init__(
        self,
        db_config: dict,
        tos_client: TosClient,
        cache_ttl: int = 3600
    ):
        """
        Initialize version service.

        Args:
            db_config: Database connection configuration
            tos_client: Configured TOS client for file storage
            cache_ttl: Cache TTL for version check results in seconds
        """
        self.db_config = db_config
        self.tos_client = tos_client
        self.cache_ttl = cache_ttl
        self._cache = {}  # Simple in-memory cache for version info

    def _parse_version(self, version: str) -> Tuple[int, ...]:
        """
        Parse semantic version string into tuple of integers.

        Args:
            version: Version string (e.g., "1.2.0" or "v1.2.0")

        Returns:
            Tuple of version components (major, minor, patch)
        """
        # Remove 'v' prefix if present
        version = version.lstrip('v')

        # Split by '.' and convert to integers
        parts = version.split('.')
        result = []
        for part in parts:
            try:
                result.append(int(part))
            except ValueError:
                result.append(0)

        # Pad with zeros to ensure at least 3 components
        while len(result) < 3:
            result.append(0)

        return tuple(result)

    def compare_versions(self, current: str, latest: str) -> str:
        """
        Compare two version strings.

        Args:
            current: Current version string
            latest: Latest version string

        Returns:
            'update' if current < latest, 'latest' otherwise
        """
        current_tuple = self._parse_version(current)
        latest_tuple = self._parse_version(latest)

        if current_tuple < latest_tuple:
            return VersionComparison.UPDATE.value
        return VersionComparison.LATEST.value

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

    def _row_to_version_info(self, row: dict) -> VersionInfo:
        """Convert a database row to VersionInfo schema."""
        return VersionInfo(
            version=row['version'],
            release_date=str(row['release_date']),
            download_url=row['download_url'],
            release_notes=row.get('release_notes'),
            file_size=row.get('file_size'),
            checksum=row.get('checksum')
        )

    def get_latest_version(self) -> Optional[VersionInfo]:
        """
        Get the latest version information.

        Returns:
            VersionInfo for the latest version, or None if no versions exist

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        # Check cache first
        cache_key = "latest_version"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if datetime.now().timestamp() - cached['timestamp'] < self.cache_ttl:
                return cached['data']

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT version, release_date, download_url, release_notes,
                               file_size, checksum
                        FROM sillyfu_versions
                        WHERE is_latest = TRUE
                        ORDER BY created_at DESC
                        LIMIT 1
                    """)
                    row = cur.fetchone()

                    if not row:
                        # If no version marked as latest, get the most recent one
                        cur.execute("""
                            SELECT version, release_date, download_url, release_notes,
                                   file_size, checksum
                            FROM sillyfu_versions
                            ORDER BY created_at DESC
                            LIMIT 1
                        """)
                        row = cur.fetchone()

                    if row:
                        version_info = self._row_to_version_info(row)
                        # Cache the result
                        self._cache[cache_key] = {
                            'data': version_info,
                            'timestamp': datetime.now().timestamp()
                        }
                        return version_info

                    return None

        except psycopg2.Error as e:
            logger.error(f"Database error getting latest version: {e}")
            raise

    def get_version(self, version: str) -> Optional[VersionInfo]:
        """
        Get version information for a specific version.

        Args:
            version: Version string (e.g., "1.2.0" or "v1.2.0")

        Returns:
            VersionInfo for the specified version, or None if not found

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        # Normalize version string
        version = version.lstrip('v')
        if not version.startswith('v'):
            version = 'v' + version

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT version, release_date, download_url, release_notes,
                               file_size, checksum
                        FROM sillyfu_versions
                        WHERE version = %s OR version = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (version, version.lstrip('v')))
                    row = cur.fetchone()

                    if row:
                        return self._row_to_version_info(row)

                    return None

        except psycopg2.Error as e:
            logger.error(f"Database error getting version {version}: {e}")
            raise

    def get_all_versions(self) -> List[VersionInfo]:
        """
        Get all version information.

        Returns:
            List of VersionInfo objects, ordered by creation date (newest first)

        Raises:
            Exception: If database query fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT version, release_date, download_url, release_notes,
                               file_size, checksum
                        FROM sillyfu_versions
                        ORDER BY created_at DESC
                    """)
                    rows = cur.fetchall()

                    return [self._row_to_version_info(row) for row in rows]

        except psycopg2.Error as e:
            logger.error(f"Database error getting all versions: {e}")
            raise

    def check_update(self, current_version: str) -> VersionCheckResponse:
        """
        Check if an update is available for the given version.

        Args:
            current_version: Current version string

        Returns:
            VersionCheckResponse with update status and latest version info

        Raises:
            ValueError: If current_version format is invalid
            Exception: If operation fails
        """
        # Validate version format
        version_pattern = r'^v?\d+\.\d+(\.\d+)?$'
        if not re.match(version_pattern, current_version):
            raise ValueError(f"Invalid version format: {current_version}")

        # Get latest version
        latest_info = self.get_latest_version()

        if latest_info is None:
            raise ValueError("No versions available in the system")

        # Compare versions
        comparison = self.compare_versions(current_version, latest_info.version)

        return VersionCheckResponse(
            needs_update=comparison == VersionComparison.UPDATE.value,
            current=current_version,
            latest=latest_info
        )

    def publish_version(self, data: PublishVersionRequest) -> VersionInfo:
        """
        Publish a new version.

        This will:
        1. Upload version info to database
        2. Mark the new version as latest
        3. Clear relevant caches

        Args:
            data: PublishVersionRequest with version details

        Returns:
            VersionInfo for the newly published version

        Raises:
            ValueError: If version already exists or data is invalid
            Exception: If publishing fails
        """
        import psycopg2

        # Normalize version
        version = data.version.lstrip('v')
        if not version.startswith('v'):
            version = 'v' + version

        # Validate version format
        version_pattern = r'^v\d+\.\d+(\.\d+)?$'
        if not re.match(version_pattern, version):
            raise ValueError(
                f"Invalid version format: {data.version}. "
                "Expected semantic versioning (e.g., 1.2.0)"
            )

        # Validate release date
        try:
            release_date = datetime.strptime(data.release_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(
                f"Invalid release date format: {data.release_date}. "
                "Expected YYYY-MM-DD"
            )

        # Generate download URL
        download_url = self.tos_client.get_download_url(version)

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if version already exists
                    cur.execute(
                        "SELECT id FROM sillyfu_versions WHERE version = %s",
                        (version,)
                    )
                    if cur.fetchone():
                        raise ValueError(f"Version {version} already exists")

                    # Clear is_latest flag from all other versions
                    cur.execute("""
                        UPDATE sillyfu_versions
                        SET is_latest = FALSE
                        WHERE is_latest = TRUE
                    """)

                    # Insert new version
                    cur.execute("""
                        INSERT INTO sillyfu_versions
                        (version, release_date, download_url, release_notes,
                         file_size, checksum, is_latest)
                        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                        RETURNING version, release_date, download_url,
                                  release_notes, file_size, checksum
                    """, (
                        version,
                        release_date,
                        download_url,
                        data.release_notes,
                        data.file_size,
                        data.checksum
                    ))

                    row = cur.fetchone()
                    conn.commit()

                    version_info = self._row_to_version_info(row)

                    # Clear cache
                    self._cache.clear()

                    logger.info(f"Published version {version}")
                    return version_info

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error publishing version: {e}")
            raise ValueError(f"Version {version} already exists")
        except psycopg2.Error as e:
            logger.error(f"Database error publishing version: {e}")
            raise

    def initialize_database(self) -> None:
        """
        Initialize the database table for version storage.

        Creates the sillyfu_versions table if it doesn't exist.

        Raises:
            Exception: If table creation fails
        """
        import psycopg2

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sillyfu_versions (
            id SERIAL PRIMARY KEY,
            version VARCHAR(20) NOT NULL UNIQUE,
            release_date DATE NOT NULL,
            download_url TEXT NOT NULL,
            release_notes TEXT,
            file_size BIGINT,
            checksum VARCHAR(64),
            is_latest BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create index for faster version lookups
        CREATE INDEX IF NOT EXISTS idx_sillyfu_versions_version
        ON sillyfu_versions(version);

        -- Create index for faster latest version queries
        CREATE INDEX IF NOT EXISTS idx_sillyfu_versions_is_latest
        ON sillyfu_versions(is_latest) WHERE is_latest = TRUE;

        -- Create index for faster date-based queries
        CREATE INDEX IF NOT EXISTS idx_sillyfu_versions_release_date
        ON sillyfu_versions(release_date DESC);
        """

        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_sql)
                    conn.commit()
                    logger.info("SillyFu versions table initialized successfully")

        except psycopg2.Error as e:
            logger.error(f"Database error initializing table: {e}")
            raise

    def delete_version(self, version: str) -> bool:
        """
        Delete a specific version.

        Args:
            version: Version string to delete

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If trying to delete the only version
            Exception: If deletion fails
        """
        import psycopg2

        # Normalize version
        version = version.lstrip('v')
        if not version.startswith('v'):
            version = 'v' + version

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if version exists
                    cur.execute(
                        "SELECT id, is_latest FROM sillyfu_versions WHERE version = %s",
                        (version,)
                    )
                    row = cur.fetchone()

                    if not row:
                        raise ValueError(f"Version {version} not found")

                    # Count total versions
                    cur.execute("SELECT COUNT(*) as count FROM sillyfu_versions")
                    count_row = cur.fetchone()

                    if count_row['count'] == 1:
                        raise ValueError("Cannot delete the only version")

                    # Delete the version
                    cur.execute(
                        "DELETE FROM sillyfu_versions WHERE version = %s",
                        (version,)
                    )

                    # If deleted version was latest, mark the most recent as latest
                    if row['is_latest']:
                        cur.execute("""
                            UPDATE sillyfu_versions
                            SET is_latest = TRUE
                            WHERE version = (
                                SELECT version FROM sillyfu_versions
                                ORDER BY created_at DESC LIMIT 1
                            )
                        """)

                    conn.commit()

                    # Clear cache
                    self._cache.clear()

                    logger.info(f"Deleted version {version}")
                    return True

        except psycopg2.Error as e:
            logger.error(f"Database error deleting version: {e}")
            raise
