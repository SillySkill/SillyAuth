#!/usr/bin/env python
"""
Quick test runner script for payment security tests
"""
import sys
import subprocess

def main():
    """Run tests with appropriate configuration"""
    print("=" * 70)
    print("SillyMD Payment Security Test Suite")
    print("=" * 70)
    print()

    # Check if pytest is installed
    try:
        import pytest
        print(f"✓ pytest version: {pytest.__version__}")
    except ImportError:
        print("✗ pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pytest==7.4.3", "pytest-asyncio==0.21.1"])
        import pytest
        print(f"✓ pytest installed: {pytest.__version__}")

    print()
    print("Running tests...")
    print("-" * 70)

    # Run pytest with verbose output
    result = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "-x"  # Stop on first failure
    ])

    print()
    print("=" * 70)

    if result == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
