"""
SillyMD Modules Package

This package contains modular components for the SillyMD platform.
Each module provides a specific set of features and can be loaded
dynamically by the application.

Module Structure:
    - Each module should be in its own directory under src/modules/
    - Each module must have a BaseModule class or SillyMDModule class
    - Each module should have a config.yaml with module metadata

Available Modules:
    - auth: User authentication module
    - sillyclaw: SillyClaw version management module
    - payment: Payment module (WeChat, Alipay, PayPal)
    - storage: TOS object storage module
    - transaction: Transaction management module
    - points: Points mall module
    - skills: Skills platform module
    - vendor: Vendor management module
    - messages: Messages module
    - tasks: Tasks system module
    - downloads: Downloads module
    - cms: Content management module
    - arena: Arena module
    - admin: Admin module
    - goods: Goods management module

Usage:
    from src.core import ModuleRegistry, discover_modules

    registry = ModuleRegistry()
    modules = discover_modules("src/modules")

    for module_path in modules:
        module = load_module_from_path(module_path)
        if module:
            module.register(app)
"""

# Check if we're in a proper package context by checking for __package__
import sys

def _import_core():
    """
    Import core components with fallback.
    Returns True if successful, False otherwise.
    """
    # First try: absolute import for src context
    try:
        from src.core import (
            BaseModule,
            ModuleInfo,
            ModuleState,
            ModuleRegistry,
            PluginManager,
            ConfigLoader,
            EventBus,
            get_registry,
            discover_modules,
            load_module_from_path,
        )
        # Make them available in this module's namespace
        globals().update({
            "BaseModule": BaseModule,
            "ModuleInfo": ModuleInfo,
            "ModuleState": ModuleState,
            "ModuleRegistry": ModuleRegistry,
            "PluginManager": PluginManager,
            "ConfigLoader": ConfigLoader,
            "EventBus": EventBus,
            "get_registry": get_registry,
            "discover_modules": discover_modules,
            "load_module_from_path": load_module_from_path,
        })
        return True
    except (ImportError, ModuleNotFoundError):
        pass

    # Second try: relative import for when modules is inside src package
    try:
        from ..core import (
            BaseModule,
            ModuleInfo,
            ModuleState,
            ModuleRegistry,
            PluginManager,
            ConfigLoader,
            EventBus,
            get_registry,
            discover_modules,
            load_module_from_path,
        )
        globals().update({
            "BaseModule": BaseModule,
            "ModuleInfo": ModuleInfo,
            "ModuleState": ModuleState,
            "ModuleRegistry": ModuleRegistry,
            "PluginManager": PluginManager,
            "ConfigLoader": ConfigLoader,
            "EventBus": EventBus,
            "get_registry": get_registry,
            "discover_modules": discover_modules,
            "load_module_from_path": load_module_from_path,
        })
        return True
    except (ImportError, ModuleNotFoundError, ValueError):
        pass

    # Third try: try to fix sys.path and import
    try:
        import os
        src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from core import (
            BaseModule,
            ModuleInfo,
            ModuleState,
            ModuleRegistry,
            PluginManager,
            ConfigLoader,
            EventBus,
            get_registry,
            discover_modules,
            load_module_from_path,
        )
        globals().update({
            "BaseModule": BaseModule,
            "ModuleInfo": ModuleInfo,
            "ModuleState": ModuleState,
            "ModuleRegistry": ModuleRegistry,
            "PluginManager": PluginManager,
            "ConfigLoader": ConfigLoader,
            "EventBus": EventBus,
            "get_registry": get_registry,
            "discover_modules": discover_modules,
            "load_module_from_path": load_module_from_path,
        })
        return True
    except (ImportError, ModuleNotFoundError):
        pass

    # Failed to import core - set to None
    globals().update({
        "BaseModule": None,
        "ModuleInfo": None,
        "ModuleState": None,
        "ModuleRegistry": None,
        "PluginManager": None,
        "ConfigLoader": None,
        "EventBus": None,
        "get_registry": None,
        "discover_modules": None,
        "load_module_from_path": None,
    })
    return False

# Attempt to import core components
_import_core()

__all__ = [
    # Core components (may be None if core not available)
    "BaseModule",
    "ModuleInfo",
    "ModuleState",
    "ModuleRegistry",
    "PluginManager",
    "ConfigLoader",
    "EventBus",
    "get_registry",
    "discover_modules",
    "load_module_from_path",
]
