"""
API Functional Test Script

Tests core API endpoints to verify server functionality.
Run with: python test_api.py

Requires: the server to be running on localhost:8000
"""
import os
import sys
import json
import urllib.request
import urllib.error
import ssl

BASE_URL = "http://localhost:8000"

# Set env vars from .env for DB connectivity
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
except ImportError:
    print("dotenv not available, using existing env vars")

def api(method, path, body=None, headers=None):
    """Make an API call and return parsed JSON response."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(
        url,
        data=data,
        headers=req_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.read() else ""
        try:
            return e.code, json.loads(body) if body else {"error": str(e)}
        except json.JSONDecodeError:
            return e.code, {"error": body, "status": e.code}
    except Exception as e:
        return 0, {"error": str(e)}


def print_result(test_name, status, data):
    """Print test result."""
    status_str = f"PASS ({status})" if status < 400 else f"FAIL ({status})"
    print(f"  [{status_str}] {test_name}")
    if status >= 400:
        detail = data.get("detail", data)
        print(f"           Detail: {detail}")


# =====================================================
# Tests
# =====================================================

def test_health():
    """Test health check endpoint."""
    print("\n--- Health Check ---")
    status, data = api("GET", "/api/health")
    print_result("GET /api/health", status, data)
    return status < 500


def test_auth():
    """Test auth endpoints."""
    print("\n--- Auth ---")
    results = []

    # Login
    status, data = api("POST", "/api/v1/auth/login", {
        "email": "admin@sillymd.com",
        "password": "admin123456"
    })
    print_result("POST /api/v1/auth/login", status, data)
    results.append(status < 500)

    if status == 200 and "access_token" in data:
        token = data["access_token"]
        print(f"  Token: {token[:50]}...")

        # Me endpoint
        status, data = api("GET", "/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        print_result("GET /api/v1/auth/me", status, data)
        results.append(status < 500)

    return all(results)


def test_module_endpoints():
    """Test basic endpoints from each module."""
    print("\n--- Module Endpoints ---")

    endpoints = [
        ("GET", "/api/v1/cms/articles", "CMS Articles"),
        ("GET", "/api/v1/skills", "Skills List"),
        ("GET", "/api/v1/tutorials/", "Tutorials"),
        ("GET", "/api/v1/downloads/", "Downloads"),
        ("GET", "/api/v1/staff/health", "Staff Health"),
        ("GET", "/api/v1/logistics/health", "Logistics Health"),
        ("GET", "/api/v1/logistics/companies", "Logistics Companies"),
    ]

    results = []
    for method, path, name in endpoints:
        status, data = api(method, path)
        print_result(f"{method} {path} ({name})", status, data)
        results.append(status < 500)

    return all(results)


def test_modules_with_auth():
    """Test endpoints that require auth but may return 500 due to DB."""
    print("\n--- Module Endpoints (with auth header) ---")

    endpoints = [
        ("GET", "/api/v1/admin/health", "Admin Health"),
        ("GET", "/api/v1/admin/dashboard", "Admin Dashboard"),
    ]

    results = []
    for method, path, name in endpoints:
        status, data = api(method, path, headers={
            "Authorization": "Bearer test"
        })
        print_result(f"{method} {path} ({name})", status, data)
        results.append(status < 500)

    return all(results)


def test_route_inventory():
    """List all registered routes."""
    print("\n--- Route Inventory ---")
    status, data = api("GET", "/api/openapi.json")
    if status == 200:
        paths = list(data.get("paths", {}).keys())
        print(f"  Total registered routes: {len(paths)}")
        for p in sorted(paths):
            print(f"    {p}")
        return True
    else:
        # Try to get routes from app directly
        print(f"  Could not fetch OpenAPI spec (status={status})")
        return False


# =====================================================
# Main
# =====================================================

def main():
    print("=" * 60)
    print("  SillyMD API Functional Tests")
    print("=" * 60)
    print(f"  Server: {BASE_URL}")

    results = {}

    # Test 1: Health
    results["health"] = test_health()

    # Test 2: Auth
    results["auth"] = test_auth()

    # Test 3: Module Endpoints
    results["module_endpoints"] = test_module_endpoints()

    # Test 4: Module Endpoints (auth)
    results["module_auth_endpoints"] = test_modules_with_auth()

    # Test 5: Route Inventory
    results["route_inventory"] = test_route_inventory()

    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")
    for name, result in results.items():
        print(f"    {'PASS' if result else 'FAIL'}: {name}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
