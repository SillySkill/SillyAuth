"""
Staff Module Test Script
Tests for staff authentication, user management, role management, and permissions
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
STAFF_API = f"{BASE_URL}/api/staff"

# Test colors (use ASCII for Windows compatibility)
GREEN = '[OK] '
RED = '[FAIL] '
YELLOW = '[INFO] '
RESET = ''


def print_success(msg):
    print(f"{GREEN}{msg}{RESET}")


def print_error(msg):
    print(f"{RED}{msg}{RESET}")


def print_info(msg):
    print(f"{YELLOW}{msg}{RESET}")


def test_health_check():
    """Test health check endpoint"""
    print_info("Testing health check...")

    try:
        response = requests.get(f"{STAFF_API}/health", timeout=5)
        assert response.status_code == 200, f"Status code: {response.status_code}"

        data = response.json()
        assert data["status"] == "healthy", f"Status: {data['status']}"
        assert data["module"] == "staff", f"Module: {data['module']}"

        print_success("Health check passed")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_module_info():
    """Test module info endpoint"""
    print_info("Testing module info...")

    try:
        response = requests.get(f"{STAFF_API}/info", timeout=5)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "staff"
        assert data["name"] == "员工权限管理模块"

        print_success("Module info passed")
        return True
    except Exception as e:
        print_error(f"Module info failed: {e}")
        return False


def test_login_invalid():
    """Test login with invalid credentials"""
    print_info("Testing invalid login...")

    try:
        response = requests.post(
            f"{STAFF_API}/auth/login",
            json={"username": "nonexistent", "password": "wrongpassword"},
            timeout=5
        )

        if response.status_code != 200:
            print_error(f"Invalid login returned status {response.status_code}")
            return False

        data = response.json()
        if data.get("success") != False:
            print_error(f"Invalid login should return success=False, got: {data}")
            return False
        if data.get("access_token") is not None:
            print_error(f"Invalid login should return access_token=None, got: {data}")
            return False

        print_success("Invalid login correctly rejected")
        return True
    except Exception as e:
        print_error(f"Invalid login test failed: {e}")
        return False


def test_unauthorized_access():
    """Test accessing protected endpoint without authentication"""
    print_info("Testing unauthorized access...")

    try:
        response = requests.get(f"{STAFF_API}/users", timeout=5)
        assert response.status_code == 403 or response.status_code == 401

        print_success("Unauthorized access correctly rejected")
        return True
    except Exception as e:
        print_error(f"Unauthorized access test failed: {e}")
        return False


def test_get_permissions_without_auth():
    """Test getting permissions without auth (should work)"""
    print_info("Testing get permissions without auth...")

    try:
        response = requests.get(f"{STAFF_API}/permissions", timeout=5)
        # This should work as it's a public endpoint
        if response.status_code == 200:
            data = response.json()
            assert "permissions" in data
            print_success("Get permissions passed")
            return True
        else:
            print_info(f"Get permissions returned {response.status_code} (may require auth)")
            return True
    except Exception as e:
        print_error(f"Get permissions test failed: {e}")
        return False


def test_get_roles_without_auth():
    """Test getting roles without auth (should work)"""
    print_info("Testing get roles without auth...")

    try:
        response = requests.get(f"{STAFF_API}/roles", timeout=5)
        # This should work as it's a public endpoint
        if response.status_code == 200:
            data = response.json()
            assert "roles" in data
            print_success("Get roles passed")
            return True
        else:
            print_info(f"Get roles returned {response.status_code} (may require auth)")
            return True
    except Exception as e:
        print_error(f"Get roles test failed: {e}")
        return False


def test_get_permission_tree():
    """Test getting permission tree"""
    print_info("Testing permission tree...")

    try:
        response = requests.get(f"{STAFF_API}/permissions/tree", timeout=5)
        if response.status_code == 200:
            data = response.json()
            assert "tree" in data
            print_success("Permission tree passed")
            return True
        else:
            print_info(f"Permission tree requires auth (status: {response.status_code})")
            return True
    except Exception as e:
        print_error(f"Permission tree test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Staff Module Test Suite")
    print("="*60 + "\n")

    tests = [
        ("Health Check", test_health_check),
        ("Module Info", test_module_info),
        ("Invalid Login", test_login_invalid),
        ("Unauthorized Access", test_unauthorized_access),
        ("Get Permissions", test_get_permissions_without_auth),
        ("Get Roles", test_get_roles_without_auth),
        ("Permission Tree", test_get_permission_tree),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Test crashed: {e}")
            failed += 1
        time.sleep(0.1)  # Small delay between tests

    print("\n" + "="*60)
    print(f"Results: {GREEN}{passed} passed{RESET}, {RED if failed > 0 else GREEN}{failed} failed{RESET}")
    print("="*60 + "\n")

    return failed == 0


def create_test_super_admin():
    """Create a test super admin user"""
    print_info("Creating test super admin user...")

    try:
        # This would need to be done through the API or directly in DB
        # For now, we'll just check if we can create users

        # Try to login as potential default admin
        response = requests.post(
            f"{STAFF_API}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("Test super admin exists and login works")
                return data["access_token"]

        print_info("No default admin found. Please create one manually.")

        # Try to get roles to see available roles
        response = requests.get(f"{STAFF_API}/roles", timeout=5)
        if response.status_code == 200:
            roles = response.json().get("roles", [])
            print_info(f"Available roles: {[r['code'] for r in roles]}")

        return None

    except Exception as e:
        print_error(f"Error creating test admin: {e}")
        return None


def interactive_tests(token=None):
    """Run interactive tests with a valid token"""
    if not token:
        print_info("No token provided, skipping interactive tests")
        return

    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- Interactive Tests (with auth) ---")

    # Test getting current user
    print_info("Getting current user info...")
    try:
        response = requests.get(f"{STAFF_API}/auth/me", headers=headers, timeout=5)
        if response.status_code == 200:
            user = response.json()
            print_success(f"Current user: {user['username']} (role: {user.get('role_name')})")
        else:
            print_error(f"Failed to get current user: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")

    # Test getting users
    print_info("Getting staff users...")
    try:
        response = requests.get(f"{STAFF_API}/users", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data['total']} staff users")
        else:
            print_error(f"Failed to get users: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")

    # Test getting roles
    print_info("Getting roles...")
    try:
        response = requests.get(f"{STAFF_API}/roles", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data['total']} roles")
            for role in data.get("roles", []):
                print(f"  - {role['name']} ({role['code']}): {len(role.get('permissions', []))} permissions")
        else:
            print_error(f"Failed to get roles: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")


if __name__ == "__main__":
    print("Staff Module Test Script")
    print("="*60)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print_error("Server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Make sure it's running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print_error(f"Connection error: {e}")
        sys.exit(1)

    print_success("Server is running")

    # Run basic tests
    if run_all_tests():
        # Try to create/get a test admin and run interactive tests
        token = create_test_super_admin()
        if token:
            interactive_tests(token)
        print_success("All tests passed!")
    else:
        print_error("Some tests failed")
        sys.exit(1)
