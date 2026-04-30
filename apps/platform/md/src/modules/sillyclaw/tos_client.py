"""
SillyClaw Version Management Module - TOS Client

Volces TOS (Table Object Storage) client for uploading and downloading
version files.
"""

import os
import logging
from typing import Optional
from urllib.parse import urljoin

import tos
from tos.exceptions import TosServerError

logger = logging.getLogger(__name__)


class TosClient:
    """
    TOS (Table Object Storage) client for version file management.

    Uses Volces TOS SDK to interact with object storage for storing
    and retrieving SillyClaw version files.
    """

    def __init__(
        self,
        endpoint: str,
        bucket: str,
        access_key: str,
        secret_key: str,
        region: str = "cn-shanghai",
        custom_domain: Optional[str] = None,
        release_path: str = "sillyclaw/releases/"
    ):
        """
        Initialize TOS client.

        Args:
            endpoint: TOS endpoint URL (e.g., tos-cn-shanghai.volces.com)
            bucket: TOS bucket name
            access_key: TOS access key ID
            secret_key: TOS secret access key
            region: TOS region (default: cn-shanghai)
            custom_domain: Custom domain for download URLs (optional)
            release_path: Path prefix for release files
        """
        self.bucket_name = bucket
        self.custom_domain = custom_domain
        self.release_path = release_path.rstrip('/') + '/'

        # Initialize TOS client
        self._client = tos.TosClientV2(
            region=region,
            access_key_id=access_key,
            access_key_secret=secret_key,
            endpoint=endpoint
        )

        logger.info(f"TOS client initialized for bucket: {bucket}")

    def _get_object_key(self, version: str, filename: Optional[str] = None) -> str:
        """
        Generate object key for a version file.

        Args:
            version: Version number (e.g., "1.2.0")
            filename: Optional filename, defaults to SillyClaw-{version}.exe

        Returns:
            Object key path in TOS
        """
        if filename is None:
            filename = f"SillyClaw-{version}.exe"
        # Normalize version (remove 'v' prefix if present)
        version = version.lstrip('v')
        return f"{self.release_path}v{version}/{filename}"

    def upload_version_file(
        self,
        version: str,
        file_content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload a version file to TOS.

        Args:
            version: Version number (e.g., "1.2.0")
            file_content: File content as bytes
            content_type: MIME type of the file

        Returns:
            Download URL for the uploaded file

        Raises:
            TosServerError: If upload fails
        """
        object_key = self._get_object_key(version)

        try:
            # Upload file to TOS
            self._client.put_object(
                bucket=self.bucket_name,
                key=object_key,
                content=file_content,
                content_type=content_type
            )

            logger.info(f"Successfully uploaded version {version} to TOS: {object_key}")

            # Generate download URL
            return self.get_download_url(version)

        except TosServerError as e:
            logger.error(f"Failed to upload version {version}: {e}")
            raise

    def get_version_file(self, version: str, filename: Optional[str] = None) -> bytes:
        """
        Download a version file from TOS.

        Args:
            version: Version number (e.g., "1.2.0")
            filename: Optional filename, defaults to SillyClaw-{version}.exe

        Returns:
            File content as bytes

        Raises:
            TosServerError: If download fails
        """
        object_key = self._get_object_key(version, filename)

        try:
            response = self._client.get_object(
                bucket=self.bucket_name,
                key=object_key
            )

            # Read content from response
            content = response.read()

            logger.info(f"Successfully downloaded version {version} from TOS")
            return content

        except TosServerError as e:
            logger.error(f"Failed to download version {version}: {e}")
            raise

    def get_download_url(self, version: str, filename: Optional[str] = None) -> str:
        """
        Get a signed download URL for a version file.

        Args:
            version: Version number (e.g., "1.2.0")
            filename: Optional filename, defaults to SillyClaw-{version}.exe

        Returns:
            Signed download URL (valid for 24 hours by default)

        Raises:
            TosServerError: If URL generation fails
        """
        object_key = self._get_object_key(version, filename)

        try:
            # Generate signed URL with 24-hour expiration
            signed_url = self._client.pre_signed_url(
                bucket=self.bucket_name,
                key=object_key,
                expires=86400  # 24 hours
            )

            logger.debug(f"Generated signed URL for version {version}")

            # If custom domain is configured, use it instead
            if self.custom_domain:
                # Extract the object key from the signed URL and construct with custom domain
                base_url = f"https://{self.custom_domain}/{object_key}"
                # Note: For production, you would need to configure your custom domain
                # to work with signed URLs or use a CDN in front of TOS
                return base_url

            return signed_url

        except TosServerError as e:
            logger.error(f"Failed to generate download URL for version {version}: {e}")
            raise

    def delete_version_file(self, version: str, filename: Optional[str] = None) -> bool:
        """
        Delete a version file from TOS.

        Args:
            version: Version number (e.g., "1.2.0")
            filename: Optional filename

        Returns:
            True if deletion was successful

        Raises:
            TosServerError: If deletion fails
        """
        object_key = self._get_object_key(version, filename)

        try:
            self._client.delete_object(
                bucket=self.bucket_name,
                key=object_key
            )

            logger.info(f"Successfully deleted version {version} from TOS")
            return True

        except TosServerError as e:
            logger.error(f"Failed to delete version {version}: {e}")
            raise

    def list_version_files(self, prefix: Optional[str] = None) -> list:
        """
        List all version files in the release path.

        Args:
            prefix: Optional prefix to filter results

        Returns:
            List of object keys
        """
        search_prefix = prefix or self.release_path

        try:
            result = self._client.list_objects(
                bucket=self.bucket_name,
                prefix=search_prefix
            )

            objects = []
            for obj in result.contents:
                objects.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified
                })

            return objects

        except TosServerError as e:
            logger.error(f"Failed to list objects: {e}")
            raise

    def version_file_exists(self, version: str, filename: Optional[str] = None) -> bool:
        """
        Check if a version file exists in TOS.

        Args:
            version: Version number (e.g., "1.2.0")
            filename: Optional filename

        Returns:
            True if the file exists
        """
        object_key = self._get_object_key(version, filename)

        try:
            self._client.head_object(
                bucket=self.bucket_name,
                key=object_key
            )
            return True

        except TosServerError:
            return False


def create_tos_client_from_config(config: dict) -> TosClient:
    """
    Create a TOS client from configuration dictionary.

    Args:
        config: Configuration dictionary with tos settings

    Returns:
        Configured TosClient instance
    """
    # Get credentials from environment variables
    access_key = os.getenv("TOS_ACCESS_KEY")
    secret_key = os.getenv("TOS_SECRET_KEY")

    if not access_key or not secret_key:
        raise ValueError(
            "TOS credentials not found. Please set TOS_ACCESS_KEY and TOS_SECRET_KEY "
            "environment variables."
        )

    return TosClient(
        endpoint=config.get("endpoint", "tos-cn-shanghai.volces.com"),
        bucket=config.get("bucket", "sillymd-skills"),
        access_key=access_key,
        secret_key=secret_key,
        custom_domain=config.get("custom_domain"),
        release_path=config.get("release_path", "sillyclaw/releases/")
    )
