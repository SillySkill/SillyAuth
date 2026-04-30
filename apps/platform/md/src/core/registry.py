"""
Module Registry

This module provides the ModuleRegistry singleton for managing all registered
modules, and the DependencyResolver for determining proper module load order.

Example:
    >>> from src.core import ModuleRegistry, DependencyResolver
    >>> registry = ModuleRegistry()
    >>> resolver = DependencyResolver(registry)
    >>> load_order = resolver.resolve(my_module)
"""

from typing import Any, Dict, List, Optional, Set

from .module import BaseModule


class ModuleRegistry:
    """
    Singleton registry for managing SillyMD modules.

    This class provides methods for registering, unregistering, and querying
    modules. It maintains an internal dictionary of all registered modules.

    Attributes:
        _modules: Internal dictionary mapping module IDs to module instances.

    Example:
        >>> registry = ModuleRegistry()
        >>> registry.register(my_module)
        >>> module = registry.get("my_module_id")
        >>> modules = registry.list_modules()
    """

    _instance: Optional["ModuleRegistry"] = None

    def __new__(cls) -> "ModuleRegistry":
        """Ensure singleton pattern for ModuleRegistry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._modules = {}
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry if not already initialized."""
        if not hasattr(self, "_modules"):
            self._modules: Dict[str, BaseModule] = {}

    def register(self, module: BaseModule) -> None:
        """
        Register a module in the registry.

        Args:
            module: The module instance to register.

        Raises:
            ValueError: If a module with the same ID is already registered.
        """
        module_id = module.module_id
        if module_id in self._modules:
            raise ValueError(f"Module '{module_id}' is already registered")
        self._modules[module_id] = module

    def unregister(self, module_id: str) -> bool:
        """
        Unregister a module from the registry.

        Args:
            module_id: The unique identifier of the module to unregister.

        Returns:
            True if the module was found and removed, False otherwise.
        """
        if module_id in self._modules:
            del self._modules[module_id]
            return True
        return False

    def get(self, module_id: str) -> Optional[BaseModule]:
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
        return [m for m in self._modules.values() if m.state.value == "active"]

    def clear(self) -> None:
        """Clear all registered modules. Useful for testing."""
        self._modules.clear()

    def __len__(self) -> int:
        """Return the number of registered modules."""
        return len(self._modules)

    def __contains__(self, module_id: str) -> bool:
        """Check if a module is registered."""
        return module_id in self._modules


def get_registry() -> ModuleRegistry:
    """Get the module registry singleton."""
    return ModuleRegistry()


class DependencyResolver:
    """
    Resolves module dependencies to determine proper load order.

    Uses topological sorting to ensure all dependencies are loaded before
    the modules that depend on them.

    Example:
        >>> resolver = DependencyResolver(registry)
        >>> load_order = resolver.resolve(my_module)
        >>> for module in load_order:
        ...     module.install(app)
    """

    def __init__(self, registry: ModuleRegistry) -> None:
        """
        Initialize the dependency resolver.

        Args:
            registry: The ModuleRegistry instance to use for looking up modules.
        """
        self._registry = registry

    def resolve(self, module: BaseModule) -> List[BaseModule]:
        """
        Resolve the load order for a module and its dependencies.

        Performs a topological sort using Kahn's algorithm to determine
        the correct order in which modules should be loaded.

        Args:
            module: The module to resolve dependencies for.

        Returns:
            List of modules in dependency order (dependencies first).

        Raises:
            ValueError: If a circular dependency is detected.
            RuntimeError: If a required dependency is not registered.
        """
        resolved: List[BaseModule] = []
        visited: Set[str] = set()
        visiting: Set[str] = set()

        def visit(m: BaseModule) -> None:
            """Recursively visit a module and its dependencies."""
            module_id = m.module_id

            if module_id in visited:
                return

            if module_id in visiting:
                raise ValueError(f"Circular dependency detected involving module '{module_id}'")

            visiting.add(module_id)

            for dep_id in m.info.dependencies:
                dep_module = self._registry.get(dep_id)
                if dep_module is None:
                    raise RuntimeError(
                        f"Required dependency '{dep_id}' for module '{module_id}' is not registered"
                    )
                visit(dep_module)

            visiting.remove(module_id)
            visited.add(module_id)
            resolved.append(m)

        visit(module)
        return resolved

    def resolve_all(self) -> List[BaseModule]:
        """
        Resolve the load order for all registered modules.

        Returns:
            List of all modules in dependency order.

        Raises:
            ValueError: If a circular dependency is detected.
        """
        all_modules = self._registry.list_modules()
        resolved: List[BaseModule] = []
        visited: Set[str] = set()

        for module in all_modules:
            if module.module_id not in visited:
                for m in self.resolve(module):
                    if m.module_id not in visited:
                        resolved.append(m)
                        visited.add(m.module_id)

        return resolved

    def get_dependents(self, module_id: str) -> List[str]:
        """
        Get all module IDs that depend on the specified module.

        Args:
            module_id: The ID of the module to find dependents for.

        Returns:
            List of module IDs that depend on the specified module.
        """
        dependents: List[str] = []
        for module in self._registry.list_modules():
            if module_id in module.info.dependencies:
                dependents.append(module.module_id)
        return dependents

    def validate_dependencies(self, module: BaseModule) -> List[str]:
        """
        Validate that all dependencies for a module are registered.

        Args:
            module: The module to validate dependencies for.

        Returns:
            List of missing dependency IDs (empty if all dependencies are met).
        """
        missing: List[str] = []
        for dep_id in module.info.dependencies:
            if self._registry.get(dep_id) is None:
                missing.append(dep_id)
        return missing
