#!/bin/bash
# ============================================================================
# AI Activity Show - Database Installation Script (Linux/Mac)
# Author: Database Design Expert
# Date: 2026-02-06
# ============================================================================

echo "========================================"
echo "AI Activity Show - Database Installer"
echo "========================================"
echo ""

# Configuration
DB_HOST="1.117.68.229"
DB_PORT="3306"
DB_USER="jcode"
DB_NAME="jc_ai"
DB_PASS="rm-uf6td5ot07c390k138o"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="$SCRIPT_DIR/migration_20250206_init_app_management.sql"

# Database Configuration
echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "ERROR: Migration file not found!"
    echo "  Expected: $MIGRATION_FILE"
    exit 1
fi

echo "Migration file found: $MIGRATION_FILE"
echo ""

# Prompt user
echo "This will install the application management database schema."
echo "WARNING: This will modify the database structure!"
echo ""
read -p "Continue? (y/n): " CONTINUE

if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "Starting installation..."
echo ""

# Execute migration
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Installation completed successfully!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "  1. Verify installation: mysql -u $DB_USER -p -e \"USE $DB_NAME; SHOW TABLES;\""
    echo "  2. Check initial data: mysql -u $DB_USER -p -e \"USE $DB_NAME; SELECT * FROM applications;\""
    echo ""
else
    echo ""
    echo "========================================"
    echo "Installation failed!"
    echo "========================================"
    echo ""
    echo "Please check:"
    echo "  1. Database credentials are correct"
    echo "  2. Database exists: CREATE DATABASE $DB_NAME;"
    echo "  3. User has proper privileges"
    echo ""
    exit 1
fi
