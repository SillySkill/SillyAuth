"""
Module Base Classes

This module defines the core abstractions for SillyMD modules, including
the ModuleInfo dataclass, ModuleState enum, and BaseModule abstract class.

Example:
    >>> from src.core import BaseModule, ModuleInfo, ModuleState
    >>> class MyModule(BaseModule):
    ...     def install(self, app):
    ...         pass
    ...     def uninstall(self):
    ...         pass
    ...     def on_startup(self):
    ...         pass
    ...     def on_shutdown(self):
    ...         pass
"""

import importlib
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .registry import ModuleRegistry

logger = logging.getLogger(__name__)


class ModuleState(Enum):
    """
    Enumeration of possible module states.

    Attributes:
        UNINSTALLED: Module is not installed in the system.
        INSTALLED: Module is installed but not currently active.
        ACTIVE: Module is installed and running.
        ERROR: Module encountered an error during installation or execution.
    """

    UNINSTALLED = "uninstalled"
    INSTALLED = "installed"
    ACTIVE = "active"
    ERROR = "error"


@dataclass
class ModuleInfo:
    """
    Metadata container for a module.

    Attributes:
        id: Unique identifier for the module.
        name: Human-readable name of the module.
        version: Semantic version string (e.g., "1.0.0").
        description: Brief description of the module's functionality.
        author: Name or identifier of the module author.
        dependencies: List of module IDs that this module depends on.
    """

    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate module info after initialization."""
        if not self.id:
            raise ValueError("Module ID cannot be empty")
        if not self.name:
            raise ValueError("Module name cannot be empty")
        if not self.version:
            raise ValueError("Module version cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert module info to a dictionary representation.

        Returns:
            Dictionary containing all module metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModuleInfo":
        """
        Create a ModuleInfo instance from a dictionary.

        Args:
            data: Dictionary containing module metadata.

        Returns:
            New ModuleInfo instance.
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            dependencies=data.get("dependencies", []),
        )


class BaseModule(ABC):
    """
    Abstract base class for all SillyMD modules.

    Subclasses must implement all lifecycle methods to define module behavior.

    Attributes:
        info: ModuleInfo instance containing module metadata.
        state: Current state of the module.
        app: Reference to the parent application instance.

    Example:
        >>> class MyModule(BaseModule):
        ...     def install(self, app):
        ...         self.app = app
        ...         self.state = ModuleState.INSTALLED
        ...     def uninstall(self):
        ...         self.state = ModuleState.UNINSTALLED
        ...     def on_startup(self):
        ...         self.state = ModuleState.ACTIVE
        ...     def on_shutdown(self):
        ...         self.state = ModuleState.INSTALLED
    """

    def __init__(self) -> None:
        """Initialize the base module with default state."""
        self._info: Optional[ModuleInfo] = None
        self._state: ModuleState = ModuleState.UNINSTALLED
        self._app: Optional[Any] = None

    @property
    def info(self) -> ModuleInfo:
        """
        Get the module's metadata.

        Raises:
            RuntimeError: If info has not been set.
        """
        if self._info is None:
            raise RuntimeError(f"Module {self.__class__.__name__} has no info set")
        return self._info

    @info.setter
    def info(self, value: ModuleInfo) -> None:
        """Set the module's metadata."""
        self._info = value

    @property
    def state(self) -> ModuleState:
        """Get the current module state."""
        return self._state

    @state.setter
    def state(self, value: ModuleState) -> None:
        """Set the current module state."""
        self._state = value

    @property
    def app(self) -> Any:
        """Get the parent application reference."""
        return self._app

    @app.setter
    def app(self, value: Any) -> None:
        """Set the parent application reference."""
        self._app = value

    @property
    @abstractmethod
    def module_id(self) -> str:
        """
        Get the unique identifier for this module.

        Returns:
            The module's unique ID string.
        """
        pass

    @abstractmethod
    def install(self, app: Any) -> None:
        """
        Install the module into the application.

        This method is called when the module is first registered.
        Use it to set up resources, database tables, or configuration.

        Args:
            app: Reference to the parent application instance.
        """
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """
        Uninstall the module from the application.

        This method is called when the module is being removed.
        Use it to clean up resources, database tables, or configuration.
        """
        pass

    @abstractmethod
    def on_startup(self) -> None:
        """
        Called when the application starts up.

        Use this method to initialize module-specific services or start background tasks.
        """
        pass

    @abstractmethod
    def on_shutdown(self) -> None:
        """
        Called when the application shuts down.

        Use this method to gracefully stop services or save state.
        """
        pass


# ============================================
# Module Discovery Utilities
# ============================================

def load_module_from_path(module_path: str) -> Optional["BaseModule"]:
    """
    Load a module class from a file path.

    Args:
        module_path: Path to the module directory

    Returns:
        Module instance or None if loading fails
    """
    init_path = os.path.join(module_path, "__init__.py")

    if not os.path.exists(init_path):
        logger.error(f"Module __init__.py not found at {init_path}")
        return None

    try:
        spec = importlib.util.spec_from_file_location("module", init_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for SillyMDModule class
            if hasattr(module, "SillyMDModule"):
                return module.SillyMDModule()
            elif hasattr(module, "BaseModule"):
                return module.BaseModule()

        logger.error(f"No module class found in {module_path}")
        return None

    except Exception as e:
        logger.error(f"Failed to load module from {module_path}: {e}")
        return None


def discover_modules(modules_dir: str) -> List[str]:
    """
    Discover all modules in a directory.

    Args:
        modules_dir: Path to modules directory

    Returns:
        List of module directory paths
    """
    modules = []

    if not os.path.exists(modules_dir):
        logger.warning(f"Modules directory not found: {modules_dir}")
        return modules

    for entry in os.scandir(modules_dir):
        if entry.is_dir() and entry.name not in ["__pycache__", ".git"]:
            init_path = os.path.join(entry.path, "__init__.py")
            if os.path.exists(init_path):
                modules.append(entry.path)

    return modules


def discover_and_load_modules(
    modules_dir: str,
    registry: Optional["ModuleRegistry"] = None
) -> List["BaseModule"]:
    """
    Discover and load all modules from a directory.

    Args:
        modules_dir: Path to modules directory
        registry: Optional module registry to register modules with

    Returns:
        List of loaded module instances
    """
    if registry is None:
        from .registry import get_registry
        registry = get_registry()

    loaded = []
    module_paths = discover_modules(modules_dir)

    for module_path in module_paths:
        module = load_module_from_path(module_path)
        if module:
            loaded.append(module)
            if hasattr(module, "module_id"):
                registry.register(module)

    return loaded
