"""
Plugin Manager

This module provides the PluginManager class for managing module lifecycle,
enabling/disabling modules, and handling plugin hooks.

Example:
    >>> from src.core import PluginManager, ModuleRegistry
    >>> registry = ModuleRegistry()
    >>> manager = PluginManager(registry)
    >>> manager.register_module(my_module)
    >>> manager.enable_module("my_module_id")
    >>> manager.register_hook("custom_event", my_handler)
"""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

from .module import BaseModule, ModuleInfo, ModuleState
from .registry import ModuleRegistry

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages module lifecycle, enabling/disabling, and hook callbacks.

    The PluginManager acts as an intermediary between modules and the
    application, handling module registration, state management, and
    event hook registration.

    Attributes:
        _modules: Dictionary of module ID to BaseModule instances.
        _hooks: Dictionary of event name to list of callback functions.
        _registry: Reference to the ModuleRegistry singleton.

    Example:
        >>> manager = PluginManager()
        >>> manager.register_module(my_module)
        >>> manager.enable_module("my_module_id")
        >>> manager.on_startup()
    """

    def __init__(self, config_loader: Optional[Any] = None) -> None:
        """
        Initialize the plugin manager.

        Args:
            config_loader: Optional ConfigLoader instance for loading module configs.
        """
        self._registry = ModuleRegistry()
        self._modules: Dict[str, BaseModule] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._app: Optional[Any] = None
        self._config_loader = config_loader

    def set_app(self, app: Any) -> None:
        """
        Set the application reference for modules.

        Args:
            app: The parent application instance.
        """
        self._app = app

    @property
    def app(self) -> Any:
        """Get the application reference."""
        return self._app

    def register_module(self, module: BaseModule) -> None:
        """
        Register a module with the plugin manager.

        This method adds the module to the internal registry and sets
        up the module info. The module is not activated until enable_module
        is called.

        Args:
            module: The module instance to register.

        Raises:
            ValueError: If the module is already registered.
        """
        # Support both module_id property and id property
        module_id = getattr(module, 'module_id', None)
        if module_id is None:
            module_id = getattr(module, 'id', None)

        if module_id is None:
            # Try to get from info attribute (supports both dict and object)
            info = getattr(module, 'info', None)
            if info is not None:
                try:
                    if isinstance(info, dict):
                        module_id = info.get('id', 'unknown')
                    else:
                        module_id = getattr(info, 'id', 'unknown')
                except (AttributeError, TypeError):
                    module_id = 'unknown'
            else:
                module_id = 'unknown'

        if module_id in self._modules:
            raise ValueError(f"Module '{module_id}' is already registered")

        self._modules[module_id] = module
        self._registry.register(module)

    def unregister_module(self, module_id: str) -> bool:
        """
        Unregister a module from the plugin manager.

        This method removes the module from the internal registry.
        If the module is active, it will be disabled first.

        Args:
            module_id: The unique identifier of the module to unregister.

        Returns:
            True if the module was found and removed, False otherwise.
        """
        module = self._modules.get(module_id)
        if module is None:
            return False

        try:
            state = getattr(module, 'state', None)
            if state == ModuleState.ACTIVE:
                self.disable_module(module_id)
        except Exception:
            pass

        del self._modules[module_id]
        self._registry.unregister(module_id)
        return True

    def enable_module(self, module_id: str) -> bool:
        """
        Enable a module, transitioning it to the ACTIVE state.

        If the module is not installed, it will be installed first.
        The module's on_startup method will be called.

        Args:
            module_id: The unique identifier of the module to enable.

        Returns:
            True if the module was successfully enabled, False otherwise.

        Raises:
            RuntimeError: If the module encounters an error during installation.
        """
        module = self._modules.get(module_id)
        if module is None:
            return False

        try:
            # Call install if available and state is UNINSTALLED
            if hasattr(module, 'state') and module.state == ModuleState.UNINSTALLED:
                if self._app is not None and hasattr(module, 'install'):
                    module.install(self._app)
                if hasattr(module, 'state'):
                    module.state = ModuleState.INSTALLED

            # Call on_load or on_enable if available
            if hasattr(module, 'on_load'):
                import asyncio
                asyncio.create_task(module.on_load())
            elif hasattr(module, 'on_enable'):
                import asyncio
                asyncio.create_task(module.on_enable())

            if hasattr(module, 'state'):
                module.state = ModuleState.ACTIVE
            if hasattr(module, 'on_startup'):
                module.on_startup()

            self.trigger_hook("module_enabled", module_id)
            return True

        except Exception as e:
            if hasattr(module, 'state'):
                module.state = ModuleState.ERROR
            self.trigger_hook("module_error", module_id, str(e))
            raise RuntimeError(f"Failed to enable module '{module_id}': {e}") from e

    def disable_module(self, module_id: str) -> bool:
        """
        Disable a module, transitioning it to the INSTALLED state.

        The module's on_shutdown method will be called.

        Args:
            module_id: The unique identifier of the module to disable.

        Returns:
            True if the module was successfully disabled, False otherwise.
        """
        module = self._modules.get(module_id)
        if module is None:
            return False

        try:
            module.on_shutdown()
            module.state = ModuleState.INSTALLED
            self.trigger_hook("module_disabled", module_id)
            return True

        except Exception as e:
            module.state = ModuleState.ERROR
            self.trigger_hook("module_error", module_id, str(e))
            return True

    def get_module_state(self, module_id: str) -> Optional[ModuleState]:
        """
        Get the current state of a module.

        Args:
            module_id: The unique identifier of the module.

        Returns:
            The module's current state, or None if not found.
        """
        module = self._modules.get(module_id)
        if module is None:
            return None
        return module.state

    def register_hook(self, event: str, callback: Callable) -> None:
        """
        Register a callback for a specific event.

        Hooks are callbacks that are triggered when certain events occur
        in the application. Multiple callbacks can be registered for the
        same event.

        Args:
            event: The name of the event to listen for.
            callback: The function to call when the event is triggered.

        Example:
            >>> def on_user_created(user_data):
            ...     print(f"User created: {user_data}")
            >>> manager.register_hook("user_created", on_user_created)
        """
        if event not in self._hooks:
            self._hooks[event] = []
        if callback not in self._hooks[event]:
            self._hooks[event].append(callback)

    def unregister_hook(self, event: str, callback: Callable) -> bool:
        """
        Unregister a callback from a specific event.

        Args:
            event: The name of the event.
            callback: The callback function to remove.

        Returns:
            True if the callback was found and removed, False otherwise.
        """
        if event in self._hooks and callback in self._hooks[event]:
            self._hooks[event].remove(callback)
            if not self._hooks[event]:
                del self._hooks[event]
            return True
        return False

    def trigger_hook(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Trigger all callbacks registered for a specific event.

        All registered callbacks are called in the order they were registered.
        Exceptions in callbacks do not stop other callbacks from being called.

        Args:
            event: The name of the event to trigger.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.

        Returns:
            List of return values from each callback.

        Example:
            >>> results = manager.trigger_hook("user_created", user_id=123, name="John")
        """
        results: List[Any] = []
        callbacks = self._hooks.get(event, [])

        for callback in callbacks:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(e)

        return results

    def list_hooks(self) -> Dict[str, int]:
        """
        List all registered hooks and their callback counts.

        Returns:
            Dictionary mapping event names to callback counts.
        """
        return {event: len(callbacks) for event, callbacks in self._hooks.items()}

    def on_startup(self) -> None:
        """
        Called when the application starts up.

        Enables all installed modules.
        """
        for module_id, module in self._modules.items():
            try:
                state = getattr(module, 'state', None)
                if state == ModuleState.INSTALLED:
                    self.enable_module(module_id)
            except Exception as e:
                logger.warning(f"Failed to start module {module_id}: {e}")

    def on_shutdown(self) -> None:
        """
        Called when the application shuts down.

        Disables all active modules.
        """
        for module_id, module in self._modules.items():
            try:
                state = getattr(module, 'state', None)
                if state == ModuleState.ACTIVE:
                    self.disable_module(module_id)
            except Exception as e:
                logger.warning(f"Failed to stop module {module_id}: {e}")

    def get_module(self, module_id: str) -> Optional[BaseModule]:
        """
        Get a module by its ID.

        Args:
            module_id: The unique identifier of the module.

        Returns:
            The module instance if found, None otherwise.
        """
        return self._modules.get(module_id)

    def list_modules(self) -> List[BaseModule]:
        """
        List all registered modules.

        Returns:
            List of all registered module instances.
        """
        return list(self._modules.values())

    def list_active_modules(self) -> List[BaseModule]:
        """
        List all currently active modules.

        Returns:
            List of modules in ACTIVE state.
        """
        return [m for m in self._modules.values()
                if getattr(m, 'state', None) == ModuleState.ACTIVE]

    async def load_all_modules(self) -> None:
        """
        Discover and load all modules from the modules directory.
        """
        modules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modules")

        if not os.path.exists(modules_dir):
            logger.warning(f"Modules directory not found: {modules_dir}")
            return

        for entry in os.scandir(modules_dir):
            if entry.is_dir() and entry.name not in ["__pycache__", ".git"]:
                module_init = os.path.join(entry.path, "__init__.py")
                if os.path.exists(module_init):
                    try:
                        # Dynamically import module
                        import importlib
                        module_name = f"modules.{entry.name}"
                        mod = importlib.import_module(module_name)

                        # Try different patterns to find module class
                        module_instance = None

                        # Pattern 1: Module class (module-specific, highest priority)
                        # e.g., VendorModule for vendor, SkillsModule for skills
                        if hasattr(mod, f"{entry.name.title()}Module"):
                            module_class = getattr(mod, f"{entry.name.title()}Module")
                            if isinstance(module_class, type):
                                module_instance = module_class()
                            else:
                                module_instance = module_class

                        # Pattern 2: SillyMDModule class
                        elif hasattr(mod, "SillyMDModule"):
                            module_class = mod.SillyMDModule
                            module_instance = module_class()

                        # Pattern 2.5: Classes with module_id property (like transaction's BaseModule)
                        elif hasattr(mod, "BaseModule"):
                            module_class = mod.BaseModule
                            if isinstance(module_class, type):
                                # Check if it has module_id property
                                instance = module_class()
                                if hasattr(instance, 'module_id'):
                                    module_instance = instance
                                else:
                                    module_instance = None
                            else:
                                module_instance = module_class
                            # Don't fall through to other patterns if we found a valid module
                            if module_instance is not None:
                                # Set initial state if not set
                                if not hasattr(module_instance, 'state'):
                                    module_instance.state = ModuleState.INSTALLED
                                elif module_instance.state is None:
                                    module_instance.state = ModuleState.INSTALLED

                                # Register the module
                                self.register_module(module_instance)

                                # Install the module if method exists
                                if self._app is not None and hasattr(module_instance, 'install'):
                                    try:
                                        module_instance.install(self._app)
                                    except Exception as e:
                                        logger.warning(f"Failed to install module {entry.name}: {e}")

                                logger.info(f"Loaded module: {entry.name}")
                                continue  # Skip to next module

                        # Pattern 3: Module instance (lowercase)
                        elif hasattr(mod, "module"):
                            module_instance = mod.module

                        # Pattern 4: Router (for modules that only expose a router)
                        # This is a fallback for simple modules without a full module class
                        elif hasattr(mod, "router"):
                            # Create a minimal module wrapper
                            # Capture entry.name at creation time to avoid closure issues
                            module_entry_name = entry.name

                            class MinimalModule:
                                def __init__(self):
                                    self._state = ModuleState.INSTALLED
                                    self._app = None
                                    self.router = mod.router

                                @property
                                def module_id(self):
                                    return module_entry_name

                                @property
                                def info(self):
                                    return ModuleInfo(
                                        id=module_entry_name,
                                        name=f"{entry.name.title()} Module",
                                        version="1.0.0",
                                        description="",
                                        author="SillyMD"
                                    )

                                @property
                                def state(self):
                                    return self._state

                                @state.setter
                                def state(self, value):
                                    self._state = value

                                def install(self, app):
                                    self._app = app
                                    if hasattr(app, 'include_router'):
                                        app.include_router(self.router)

                                def uninstall(self):
                                    self._state = ModuleState.UNINSTALLED

                                def on_startup(self):
                                    self._state = ModuleState.ACTIVE

                                def on_shutdown(self):
                                    self._state = ModuleState.INSTALLED

                            module_instance = MinimalModule()

                        if module_instance is not None:
                            # Set initial state if not set
                            if not hasattr(module_instance, 'state'):
                                module_instance.state = ModuleState.INSTALLED
                            elif module_instance.state is None:
                                module_instance.state = ModuleState.INSTALLED

                            # Register the module
                            self.register_module(module_instance)

                            # Install the module if method exists
                            if self._app is not None and hasattr(module_instance, 'install'):
                                try:
                                    module_instance.install(self._app)
                                except Exception as e:
                                    logger.warning(f"Failed to install module {entry.name}: {e}")

                            logger.info(f"Loaded module: {entry.name}")
                        else:
                            logger.warning(f"No module class/instance found in {entry.name}")

                    except Exception as e:
                        logger.error(f"Failed to load module {entry.name}: {e}")

    async def unload_all_modules(self) -> None:
        """
        Unload all registered modules.
        """
        for module_id in list(self._modules.keys()):
            self.unregister_module(module_id)
