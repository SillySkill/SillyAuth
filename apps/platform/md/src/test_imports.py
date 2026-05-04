"""
Module Loading Test Script

Verifies that all 28 modules can be imported without errors and that the
FastAPI application can start successfully with all routers registered.

Usage:
    python test_imports.py          # Run all tests
    python test_imports.py basic    # Only test imports (no DB)
    python test_imports.py app      # Test FastAPI app creation
"""

import sys
import os
import importlib
import logging
import traceback

# Ensure src/ is on the path
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("test_imports")

# All expected modules (28)
EXPECTED_MODULES = [
    "admin", "affiliate", "analytics", "arena", "auth", "cms",
    "config_data", "config_sync", "dashboard", "downloads", "goods",
    "i18n", "logistics", "marketplace", "messages", "payment",
    "points", "promotion", "recommendations", "sillyfu", "skills",
    "staff", "storage", "store", "tasks", "transaction", "tutorials", "vendor",
]

# ──────────────────────────────────────────────
# Test 1: Basic Module Import
# ──────────────────────────────────────────────

def test_module_imports() -> dict:
    """Try to import each module's __init__.py and routes."""
    results = {}
    for mod_name in EXPECTED_MODULES:
        mod_results = {"__init__": None, "routes": None, "error": None}

        # Test __init__.py
        try:
            mod = importlib.import_module(f"modules.{mod_name}")
            mod_results["__init__"] = "OK"
        except Exception as e:
            mod_results["__init__"] = f"ERROR: {e}"
            mod_results["error"] = traceback.format_exc()
            results[mod_name] = mod_results
            continue

        # Test routes.py (if exists)
        routes_path = os.path.join(_src_dir, "modules", mod_name, "routes.py")
        if os.path.exists(routes_path):
            try:
                importlib.import_module(f"modules.{mod_name}.routes")
                mod_results["routes"] = "OK"
            except Exception as e:
                mod_results["routes"] = f"ERROR: {e}"
                if mod_results["error"] is None:
                    mod_results["error"] = traceback.format_exc()

        # Check for router attribute
        if hasattr(mod, "router"):
            mod_results["has_router"] = True
        elif hasattr(mod, "SillyMDModule"):
            mod_results["has_router"] = hasattr(mod.SillyMDModule, "router")
        else:
            mod_results["has_router"] = False

        results[mod_name] = mod_results

    return results


# ──────────────────────────────────────────────
# Test 2: FastAPI App Creation
# ──────────────────────────────────────────────

def test_app_creation() -> dict:
    """Try to create the FastAPI app and load all modules."""
    results = {"app_created": False, "modules_loaded": [], "errors": []}

    try:
        # This will trigger the lifespan which calls load_all_modules
        import asyncio
        from fastapi.testclient import TestClient
        from main import app

        results["app_created"] = True

        # Check app state after lifespan
        # We need to manually trigger lifespan since TestClient handles it
        with TestClient(app) as client:
            # Check health endpoint (might fail without DB, but app should be responsive)
            health_resp = client.get("/api/health")
            results["health_status"] = health_resp.status_code
            results["health_body"] = health_resp.json()

            # Check for registered routes
            routes = [r.path for r in app.routes]
            results["routes_count"] = len(routes)

            # Try to find module routers
            module_routes = [r for r in routes if "/api/" in r]
            results["module_routes"] = module_routes

            # Check if modules were loaded
            if hasattr(app.state, "manager"):
                loaded = list(app.state.manager._modules.keys())
                results["modules_loaded"] = loaded
                results["modules_count"] = len(loaded)

    except Exception as e:
        results["errors"].append(f"App creation failed: {e}")
        results["traceback"] = traceback.format_exc()

    return results


# ──────────────────────────────────────────────
# Test 3: Core Imports
# ──────────────────────────────────────────────

def test_core_imports() -> dict:
    """Test that core modules can be imported."""
    results = {}
    core_modules = [
        "core.db_adapter",
        "core.plugin_manager",
        "core.module",
        "core.registry",
        "core.config",
        "core.database",
    ]

    for mod_name in core_modules:
        try:
            importlib.import_module(mod_name)
            results[mod_name] = "OK"
        except Exception as e:
            results[mod_name] = f"ERROR: {e}"

    return results


# ──────────────────────────────────────────────
# Report Generation
# ──────────────────────────────────────────────

def print_report(title: str, results: dict):
    """Print a formatted test report."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

    if not results:
        print("  (no results)")
        return

    # Determine column widths
    items = list(results.items())
    max_key_len = max(len(k) for k in results.keys())

    for key, value in items:
        if isinstance(value, dict):
            print(f"  {key.ljust(max_key_len)}  :")
            for sub_key, sub_val in value.items():
                status = "OK" if sub_val == "OK" else str(sub_val)
                print(f"    {sub_key}: {status}")
        else:
            status = "OK" if value == "OK" else str(value)
            print(f"  {key.ljust(max_key_len)}  : {status}")


def main():
    """Run all tests and print report."""
    test_mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    print(f"\n{'#'*60}")
    print(f"#  SillyMD Module Loading Test Suite")
    print(f"{'#'*60}")
    print(f"  Mode: {test_mode}")

    # Test 1: Core imports
    print(f"\n{'─'*60}")
    print("  Phase 1: Core Module Imports")
    print(f"{'─'*60}")
    core_results = test_core_imports()
    print_report("Core Imports", core_results)
    core_errors = [k for k, v in core_results.items() if v != "OK"]

    # Test 2: Module imports
    print(f"\n{'─'*60}")
    print("  Phase 2: Module Imports")
    print(f"{'─'*60}")
    mod_results = test_module_imports()
    print_report("Module Imports", mod_results)
    mod_errors = [k for k, v in mod_results.items() if v.get("error")]

    # Summary
    print(f"\n{'─'*60}")
    print("  Summary")
    print(f"{'─'*60}")

    total = len(EXPECTED_MODULES)
    ok = sum(1 for v in mod_results.values() if v.get("__init__") == "OK")
    routes_ok = sum(1 for v in mod_results.values() if v.get("routes") == "OK")
    routes_total = sum(1 for v in mod_results.values() if "routes" in v.get("routes", "") or v.get("routes") == "OK")

    print(f"  Modules with __init__.py OK : {ok}/{total}")
    print(f"  Modules with routes OK      : {routes_ok}/{routes_total}")
    print(f"  Core import errors          : {len(core_errors)}")
    print(f"  Module import errors        : {len(mod_errors)}")

    if mod_errors:
        print(f"\n  Failed modules:")
        for name in mod_errors:
            err = mod_results[name].get("error", "unknown error")
            print(f"    - {name}: {err.split(chr(10))[0]}")

    # Test 3: App creation (skipped in 'basic' mode)
    if test_mode != "basic":
        print(f"\n{'─'*60}")
        print("  Phase 3: FastAPI App Creation")
        print(f"{'─'*60}")
        app_results = test_app_creation()
        print_report("App Creation", app_results)
        print()

    # Return exit code
    if mod_errors:
        return 1
    if core_errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
