"""
Configuration Loader

This module provides the ConfigLoader class for loading and caching module
and global configuration from YAML files.

Example:
    >>> from sillys.md.core import ConfigLoader
    >>> loader = ConfigLoader(config_dir="/path/to/config")
    >>> module_config = loader.load_module_config("my_module")
    >>> global_config = loader.load_global_config()
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from functools import lru_cache
except ImportError:
    def lru_cache(maxsize: int = 128):
        """Simple fallback for lru_cache if not available."""
        def decorator(func):
            func._cache = {}
            def wrapper(*args, **kwargs):
                key = str(args) + str(kwargs)
                if key not in func._cache:
                    func._cache[key] = func(*args, **kwargs)
                return func._cache[key]
            return wrapper
        return decorator


class ConfigLoader:
    """
    Configuration loader with caching support for YAML configuration files.

    The ConfigLoader handles loading module-specific and global configuration
    files, with automatic caching to reduce file I/O.

    Attributes:
        _cache: Internal cache for loaded configurations.
        _config_dir: Base directory for configuration files.

    Example:
        >>> loader = ConfigLoader(config_dir="./config")
        >>> config = loader.load_module_config("my_module")
        >>> global_config = loader.load_global_config()
    """

    def __init__(self, config_dir: Optional[str] = None) -> None:
        """
        Initialize the configuration loader.

        Args:
            config_dir: Base directory for configuration files.
                       Defaults to "./config" if not provided.
        """
        if config_dir is None:
            config_dir = os.path.join(os.getcwd(), "config")

        self._config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}
        self._cache_enabled = True

        if not self._config_dir.exists():
            self._config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self._config_dir

    @config_dir.setter
    def config_dir(self, value: str) -> None:
        """Set the configuration directory path."""
        self._config_dir = Path(value)
        if not self._config_dir.exists():
            self._config_dir.mkdir(parents=True, exist_ok=True)
        self.clear_cache()

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()

    def enable_cache(self) -> None:
        """Enable configuration caching."""
        self._cache_enabled = True

    def disable_cache(self) -> None:
        """Disable configuration caching."""
        self._cache_enabled = False

    def _get_cache_key(self, module_id: Optional[str] = None) -> str:
        """
        Generate a cache key for a module or global config.

        Args:
            module_id: The module ID, or None for global config.

        Returns:
            The cache key string.
        """
        if module_id is None:
            return "global"
        return f"module:{module_id}"

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a YAML file.

        Args:
            file_path: Path to the YAML file.

        Returns:
            Dictionary containing the parsed YAML data.

        Raises:
            ImportError: If PyYAML is not installed.
            FileNotFoundError: If the file does not exist.
        """
        if not HAS_YAML:
            raise ImportError("PyYAML is required for configuration loading. Install with: pip install pyyaml")

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data if data is not None else {}

    def _get_module_config_path(self, module_id: str) -> Path:
        """
        Get the configuration file path for a module.

        Args:
            module_id: The module identifier.

        Returns:
            Path to the module's configuration file.
        """
        # First try: config/modules/{module_id}.yaml
        config_path = self._config_dir / "modules" / f"{module_id}.yaml"
        if config_path.exists():
            return config_path

        # Second try: modules/{module_id}/config.yaml
        alt_path = self._config_dir / "modules" / module_id / "config.yaml"
        if alt_path.exists():
            return alt_path

        # Return default path even if it doesn't exist
        return config_path

    def _get_global_config_path(self) -> Path:
        """
        Get the global configuration file path.

        Returns:
            Path to the global configuration file.
        """
        # First try: config/global.yaml
        config_path = self._config_dir / "global.yaml"
        if config_path.exists():
            return config_path

        # Second try: config.yaml (in the base directory)
        alt_path = self._config_dir / "config.yaml"
        if alt_path.exists():
            return alt_path

        # Return default path even if it doesn't exist
        return config_path

    def load_module_config(self, module_id: str) -> Dict[str, Any]:
        """
        Load configuration for a specific module.

        Configuration is cached after first load. Use clear_cache() to
        force reload.

        Args:
            module_id: The unique identifier of the module.

        Returns:
            Dictionary containing the module's configuration.

        Example:
            >>> config = loader.load_module_config("auth")
            >>> db_host = config.get("database", {}).get("host", "localhost")
        """
        cache_key = self._get_cache_key(module_id)

        if self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        config_path = self._get_module_config_path(module_id)

        try:
            config = self._load_yaml_file(config_path)
        except FileNotFoundError:
            config = {}

        if self._cache_enabled:
            self._cache[cache_key] = config

        return config

    def load_all_modules_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Load configuration for all modules.

        Searches the modules configuration directory for all YAML files
        and loads them into a dictionary keyed by module ID.

        Returns:
            Dictionary mapping module IDs to their configurations.

        Example:
            >>> all_configs = loader.load_all_modules_config()
            >>> for module_id, config in all_configs.items():
            ...     print(f"{module_id}: {config}")
        """
        cache_key = "all_modules"

        if self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        modules_dir = self._config_dir / "modules"
        all_configs: Dict[str, Dict[str, Any]] = {}

        if modules_dir.exists():
            for config_file in modules_dir.glob("*.yaml"):
                module_id = config_file.stem
                try:
                    all_configs[module_id] = self._load_yaml_file(config_file)
                except Exception:
                    all_configs[module_id] = {}

        if self._cache_enabled:
            self._cache[cache_key] = all_configs

        return all_configs

    def load_global_config(self) -> Dict[str, Any]:
        """
        Load the global configuration.

        Returns:
            Dictionary containing global configuration settings.

        Example:
            >>> config = loader.load_global_config()
            >>> debug_mode = config.get("debug", False)
        """
        cache_key = self._get_cache_key(None)

        if self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        config_path = self._get_global_config_path()

        try:
            config = self._load_yaml_file(config_path)
        except FileNotFoundError:
            config = {}

        if self._cache_enabled:
            self._cache[cache_key] = config

        return config

    def save_module_config(self, module_id: str, config: Dict[str, Any]) -> None:
        """
        Save configuration for a specific module.

        Args:
            module_id: The unique identifier of the module.
            config: Configuration dictionary to save.

        Example:
            >>> loader.save_module_config("auth", {"enabled": True})
        """
        if not HAS_YAML:
            raise ImportError("PyYAML is required for configuration saving. Install with: pip install pyyaml")

        config_path = self._get_module_config_path(module_id)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        cache_key = self._get_cache_key(module_id)
        if self._cache_enabled:
            self._cache[cache_key] = config

    def save_global_config(self, config: Dict[str, Any]) -> None:
        """
        Save the global configuration.

        Args:
            config: Global configuration dictionary to save.

        Example:
            >>> loader.save_global_config({"debug": True, "log_level": "INFO"})
        """
        if not HAS_YAML:
            raise ImportError("PyYAML is required for configuration saving. Install with: pip install pyyaml")

        config_path = self._get_global_config_path()

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        cache_key = self._get_cache_key(None)
        if self._cache_enabled:
            self._cache[cache_key] = config

    def get_setting(
        self,
        module_id: Optional[str],
        key: str,
        default: Any = None,
        use_global_fallback: bool = True
    ) -> Any:
        """
        Get a specific setting value with optional global fallback.

        Args:
            module_id: The module identifier, or None for global settings.
            key: The setting key (supports dot notation for nested keys).
            default: Default value if setting is not found.
            use_global_fallback: If True, falls back to global config if not
                                found in module config.

        Returns:
            The setting value or default.

        Example:
            >>> db_host = loader.get_setting("auth", "database.host", "localhost")
        """
        config = self.load_module_config(module_id) if module_id else self.load_global_config()

        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                if use_global_fallback and module_id is not None:
                    global_config = self.load_global_config()
                    value = global_config
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            return default
                    return value
                return default

        return value
