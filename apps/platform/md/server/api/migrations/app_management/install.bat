@echo off
REM ============================================================================
REM AI Activity Show - Database Installation Script
REM Author: Database Design Expert
REM Date: 2026-02-06
REM ============================================================================

echo ========================================
echo AI Activity Show - Database Installer
echo ========================================
echo.

REM Configuration
set DB_HOST=1.117.68.229
set DB_PORT=3306
set DB_USER=jcode
set DB_NAME=jc_ai
set DB_PASS=rm-uf6td5ot07c390k138o

REM Get script directory
set SCRIPT_DIR=%~dp0
set MIGRATION_FILE=%SCRIPT_DIR%migration_20250206_init_app_management.sql

echo Database Configuration:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: %DB_NAME%
echo   User: %DB_USER%
echo.

REM Check if migration file exists
if not exist "%MIGRATION_FILE%" (
    echo ERROR: Migration file not found!
    echo   Expected: %MIGRATION_FILE%
    pause
    exit /b 1
)

echo Migration file found: %MIGRATION_FILE%
echo.

REM Prompt user
echo This will install the application management database schema.
echo WARNING: This will modify the database structure!
echo.
set /p CONTINUE="Continue? (y/n): "

if /i not "%CONTINUE%"=="y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo Starting installation...
echo.

REM Execute migration
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% %DB_NAME% < "%MIGRATION_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Installation completed successfully!
    echo ========================================
    echo.
    echo Next steps:
    echo   1. Verify installation: mysql -u %DB_USER% -p -e "USE %DB_NAME%; SHOW TABLES;"
    echo   2. Check initial data: mysql -u %DB_USER% -p -e "USE %DB_NAME%; SELECT * FROM applications;"
    echo.
) else (
    echo.
    echo ========================================
    echo Installation failed!
    echo ========================================
    echo.
    echo Please check:
    echo   1. Database credentials are correct
    echo   2. Database exists: CREATE DATABASE %DB_NAME%;
    echo   3. User has proper privileges
    echo.
)

pause
