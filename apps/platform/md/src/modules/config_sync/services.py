"""
Config Sync Service
File-based configuration version management service.

Uses versions.json for version registry and update_logs.jsonl for
append-only update tracking. MD5 hashing ensures file integrity.
No database dependency -- all state lives on the filesystem.
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path

from .schemas import VersionInfo, UpdateStats

logger = logging.getLogger(__name__)

# Default storage path; override via CONFIG_STORAGE_PATH environment variable
DEFAULT_STORAGE_PATH = "/data/config"


def _get_storage_root() -> Path:
    """Resolve the storage root directory from env or default."""
    env_path = os.getenv("CONFIG_STORAGE_PATH", "").strip()
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_STORAGE_PATH)


def _ensure_dir(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def _compute_md5(content: bytes) -> str:
    """Compute the MD5 hex digest of the given byte content."""
    return hashlib.md5(content).hexdigest()


class ConfigSyncService:
    """
    Configuration sync service.

    Responsibilities
    ----------------
    - Maintain a version registry in ``versions.json`` inside the storage root.
    - Store distributed configuration files on disk (by version).
    - Append update reports to ``update_logs.jsonl``.
    - Serve version info, file downloads, and aggregated statistics.
    """

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self._root = Path(storage_path)
        else:
            self._root = _get_storage_root()

        _ensure_dir(self._root)
        self._versions_file = self._root / "versions.json"
        self._logs_file = self._root / "update_logs.jsonl"

        # Bootstrap empty data files if they do not exist
        self._init_data_files()
        logger.info(f"ConfigSyncService initialized with root={self._root}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_data_files(self) -> None:
        """Create versions.json and update_logs.jsonl if missing."""
        if not self._versions_file.exists():
            self._write_versions({"versions": [], "latest": None})
            logger.info(f"Created versions file: {self._versions_file}")

        if not self._logs_file.exists():
            self._logs_file.touch()
            logger.info(f"Created logs file: {self._logs_file}")

    def _read_versions(self) -> Dict[str, Any]:
        """Read the full versions registry from disk."""
        try:
            with open(self._versions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read versions file, returning empty registry: {e}")
            return {"versions": [], "latest": None}

    def _write_versions(self, data: Dict[str, Any]) -> None:
        """Atomically write the versions registry to disk."""
        tmp = self._versions_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        tmp.replace(self._versions_file)

    def _append_log(self, entry: Dict[str, Any]) -> None:
        """Append a single JSON line to the update log."""
        entry["timestamp"] = entry.get("timestamp", datetime.now(timezone.utc).isoformat())
        with open(self._logs_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _read_logs(self) -> List[Dict[str, Any]]:
        """Read all log entries from the jsonl log file."""
        entries: List[Dict[str, Any]] = []
        if not self._logs_file.exists():
            return entries
        with open(self._logs_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning(f"Skipping malformed log line: {line[:100]}")
        return entries

    def _version_dir(self, version: str) -> Path:
        """Return the directory where files for a specific version live."""
        return self._root / version

    # ------------------------------------------------------------------
    # Version management
    # ------------------------------------------------------------------

    def get_version(self, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve version info.

        Parameters
        ----------
        version : str or None
            Specific version string (e.g. "v1.0.1"). If None or "current",
            returns the latest version.

        Returns
        -------
        dict or None
        """
        registry = self._read_versions()
        versions: List[Dict[str, Any]] = registry.get("versions", [])

        if not versions:
            return None

        if version is None or version == "current":
            latest = registry.get("latest")
            if latest:
                for v in versions:
                    if v.get("version") == latest:
                        return v
            # Fallback: last entry
            return versions[-1] if versions else None

        # Specific version lookup
        for v in versions:
            if v.get("version") == version:
                return v
        return None

    def list_versions(self) -> List[Dict[str, Any]]:
        """Return all registered versions, newest first."""
        registry = self._read_versions()
        versions = registry.get("versions", [])
        # Sort by version_code descending
        return sorted(versions, key=lambda v: v.get("version_code", 0), reverse=True)

    def publish_version(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a new configuration version.

        Parameters
        ----------
        data : dict
            Must contain 'version', 'version_code'. Optional: 'release_notes',
            'force_update', 'min_compatible_version', 'files', 'deleted_files'.

        Returns
        -------
        dict
            The newly created version entry.
        """
        registry = self._read_versions()
        versions = registry.get("versions", [])

        # Check for duplicate version string
        for v in versions:
            if v.get("version") == data["version"]:
                raise ValueError(f"Version '{data['version']}' already exists")

        version_entry: Dict[str, Any] = {
            "version": data["version"],
            "version_code": data["version_code"],
            "release_date": datetime.now(timezone.utc).isoformat(),
            "release_notes": data.get("release_notes", ""),
            "force_update": data.get("force_update", False),
            "min_compatible_version": data.get("min_compatible_version"),
            "files": data.get("files", []),
            "deleted_files": data.get("deleted_files", []),
        }

        versions.append(version_entry)

        # Enforce max_versions (keep newest by version_code)
        max_ver = int(os.getenv("CONFIG_MAX_VERSIONS", "10"))
        if len(versions) > max_ver:
            versions = sorted(versions, key=lambda v: v.get("version_code", 0), reverse=True)
            removed = versions[max_ver:]
            versions = versions[:max_ver]
            for r in removed:
                logger.info(f"Pruned old version: {r['version']}")

        # Determine latest
        latest = max(versions, key=lambda v: v["version_code"]) if versions else data["version"]

        registry["versions"] = versions
        registry["latest"] = latest["version"] if isinstance(latest, dict) else latest
        self._write_versions(registry)

        # Store any file blobs
        version_dir = self._version_dir(data["version"])
        _ensure_dir(version_dir)
        for file_info in data.get("files", []):
            file_path_str = file_info.get("path", "")
            content_b64 = file_info.get("content", "")
            if file_path_str and content_b64:
                import base64
                try:
                    content_bytes = base64.b64decode(content_b64)
                except Exception:
                    content_bytes = content_b64.encode("utf-8")
                dest_path = version_dir / file_path_str.lstrip("/")
                _ensure_dir(dest_path.parent)
                with open(dest_path, "wb") as dest:
                    dest.write(content_bytes)
                # Record MD5 in the version entry
                file_info["md5"] = _compute_md5(content_bytes)
                file_info["size"] = len(content_bytes)
                # Remove base64 content from registry (it is on disk now)
                file_info.pop("content", None)

        logger.info(f"Published version {data['version']} (code={data['version_code']})")
        return version_entry

    # ------------------------------------------------------------------
    # File serving
    # ------------------------------------------------------------------

    def get_file(self, version: str, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a configuration file for a specific version.

        Returns
        -------
        dict with keys ``content`` (bytes), ``md5``, ``size``, or None.
        """
        version_data = self.get_version(version)
        if version_data is None:
            return None

        # Look up file metadata from the version entry
        file_meta = None
        for f in version_data.get("files", []):
            if f.get("path") == file_path:
                file_meta = f
                break

        if file_meta is None:
            return None

        # Read file from disk
        disk_path = self._version_dir(version) / file_path.lstrip("/")
        if not disk_path.exists() or not disk_path.is_file():
            return None

        content = disk_path.read_bytes()
        return {
            "content": content,
            "md5": file_meta.get("md5", _compute_md5(content)),
            "size": file_meta.get("size", len(content)),
            "path": file_path,
        }

    def list_files(self, version: str) -> List[Dict[str, Any]]:
        """List all file metadata for a given version."""
        version_data = self.get_version(version)
        if version_data is None:
            return []
        return version_data.get("files", [])

    # ------------------------------------------------------------------
    # Update reporting
    # ------------------------------------------------------------------

    def report_update(self, device_id: str, old_version: str,
                      new_version: str, status: str,
                      error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Record a client update report.

        Parameters
        ----------
        device_id : str
            Unique device identifier.
        old_version : str
            Version before update.
        new_version : str
            Version after update.
        status : str
            One of 'success', 'failed', 'rollback'.
        error_message : str or None
            Optional error description (for failed/rollback).
        """
        entry = {
            "device_id": device_id,
            "old_version": old_version,
            "new_version": new_version,
            "status": status,
            "error_message": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_log(entry)
        logger.info(
            f"Update report: device={device_id}, {old_version} -> {new_version}, "
            f"status={status}"
        )
        return entry

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> UpdateStats:
        """
        Compute aggregated update statistics from the log file.
        """
        logs = self._read_logs()
        total = len(logs)
        successful = sum(1 for e in logs if e.get("status") == "success")
        failed = sum(1 for e in logs if e.get("status") == "failed")
        rollback = sum(1 for e in logs if e.get("status") == "rollback")

        version_distribution: Dict[str, int] = {}
        for e in logs:
            ver = e.get("new_version", "unknown")
            version_distribution[ver] = version_distribution.get(ver, 0) + 1

        last_update: Optional[datetime] = None
        latest_ts = None
        for e in logs:
            ts = e.get("timestamp")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    if latest_ts is None or dt > latest_ts:
                        latest_ts = dt
                        last_update = dt
                except (ValueError, TypeError):
                    pass

        return UpdateStats(
            total_updates=total,
            successful_updates=successful,
            failed_updates=failed + rollback,
            version_distribution=version_distribution,
            last_update_time=last_update,
        )

    # ------------------------------------------------------------------
    # Convenience: full response builder
    # ------------------------------------------------------------------

    def build_version_response(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Build a full version-list response dict with current/latest/all versions."""
        current = self.get_version(version)
        versions = self.list_versions()
        registry = self._read_versions()

        response: Dict[str, Any] = {
            "success": True,
            "data": {
                "current_version": current,
                "versions": versions,
                "latest_version": registry.get("latest"),
            },
        }
        return response


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_config_sync_service: Optional[ConfigSyncService] = None


def get_config_sync_service(storage_path: Optional[str] = None) -> ConfigSyncService:
    """
    Get or create the global ConfigSyncService instance.

    Parameters
    ----------
    storage_path : str or None
        Override the storage root directory. Only used on first creation.
    """
    global _config_sync_service
    if _config_sync_service is None:
        _config_sync_service = ConfigSyncService(storage_path=storage_path)
    return _config_sync_service
