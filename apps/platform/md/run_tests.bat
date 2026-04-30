@echo off
REM Test runner for Windows - SillyMD Payment Security Tests
echo ===================================================================
echo SillyMD Payment Security Test Suite
echo ===================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    exit /b 1
)

echo Python found
echo.

REM Check if pytest is installed
python -c "import pytest" >nul 2>&1
if %errorlevel% neq 0 (
    echo pytest not found. Installing...
    pip install pytest==7.4.3 pytest-asyncio==0.21.1 -q
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install pytest
        exit /b 1
    )
    echo pytest installed successfully
    echo.
)

echo Running tests...
echo -------------------------------------------------------------------
echo.

REM Run tests
python -m pytest tests/ -v --tb=short --disable-warnings

echo.
echo ===================================================================
if %errorlevel% equ 0 (
    echo SUCCESS: All tests passed!
) else (
    echo WARNING: Some tests failed or had errors
)
echo ===================================================================

pause
