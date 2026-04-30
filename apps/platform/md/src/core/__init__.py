"""
SillyMD Core Module Framework

This module provides the core infrastructure for the SillyMD modular architecture,
including module management, plugin handling, configuration loading, database
connections, and event broadcasting.

Example:
    >>> from src.core import BaseModule, ModuleRegistry, PluginManager
    >>> registry = ModuleRegistry()
    >>> plugin_manager = PluginManager(registry)
"""

# Re-export from individual module files
from .module import ModuleState, ModuleInfo, BaseModule
from .registry import ModuleRegistry, DependencyResolver, get_registry
from .plugin_manager import PluginManager
from .config_loader import ConfigLoader
from .database import Database
from .events import EventBus, HookEvent

# Module discovery utilities
from .module import load_module_from_path, discover_modules, discover_and_load_modules

__version__ = "1.0.0"

__all__ = [
    # Module classes
    "BaseModule",
    "ModuleInfo",
    "ModuleState",
    # Registry
    "ModuleRegistry",
    "DependencyResolver",
    "get_registry",
    # Plugin management
    "PluginManager",
    # Configuration
    "ConfigLoader",
    # Database
    "Database",
    # Events
    "EventBus",
    "HookEvent",
    # Utilities
    "load_module_from_path",
    "discover_modules",
    "discover_and_load_modules",
]
