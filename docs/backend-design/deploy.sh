# ============================================
# SillyMD Backend - Deploy Script
# ============================================

#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="47.96.133.238"
SERVER_USER="root"
SSH_KEY=".ignore/silly.pem"
PROJECT_DIR="/root/sillymd-backend"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SillyMD Backend Deployment Script  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print colored output
print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_error "SSH key not found at $SSH_KEY"
    exit 1
fi

# Test SSH connection
print_info "Testing SSH connection to $SERVER_IP..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'Connection successful'" || {
    print_error "Failed to connect to server"
    exit 1
}
print_success "SSH connection test passed"

# Prepare project files
print_info "Preparing project files..."
rm -rf dist build
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Create deployment package
print_info "Creating deployment package..."
tar -czf sillymd-backend.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.mypy_cache' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='*.egg-info' \
    . || {
    print_error "Failed to create deployment package"
    exit 1
}
print_success "Deployment package created"

# Upload to server
print_info "Uploading to server..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no sillymd-backend.tar.gz "$SERVER_USER@$SERVER_IP:/tmp/" || {
    print_error "Failed to upload package"
    exit 1
}
print_success "Upload completed"

# Remote deployment
print_info "Deploying on remote server..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
set -e

echo "[INFO] Stopping existing containers..."
cd /root/sillymd-backend 2>/dev/null || mkdir -p /root/sillymd-backend
docker-compose down 2>/dev/null || true

echo "[INFO] Extracting new files..."
cd /tmp
tar -xzf sillymd-backend.tar.gz -C /root/sillymd-backend
cd /root/sillymd-backend

echo "[INFO] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[INFO] Created .env from .env.example"
fi

echo "[INFO] Building Docker images..."
docker-compose build --no-cache

echo "[INFO] Starting services..."
docker-compose up -d

echo "[INFO] Waiting for services to be healthy..."
sleep 10

echo "[INFO] Running database migrations..."
# docker-compose exec backend alembic upgrade head

echo "[INFO] Cleaning up..."
rm /tmp/sillymd-backend.tar.gz

echo "[SUCCESS] Deployment completed!"
echo ""
echo "[INFO] Service status:"
docker-compose ps

ENDSSH

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully!"
    echo ""
    print_info "Backend API: http://$SERVER_IP:8000"
    print_info "API Docs: http://$SERVER_IP:8000/docs"
    print_info "Health Check: curl http://$SERVER_IP:8000/health"
else
    print_error "Deployment failed"
    exit 1
fi

# Cleanup local package
print_info "Cleaning up local files..."
rm -f sillymd-backend.tar.gz
print_success "Local cleanup completed"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Deployment Finished Successfully!   ${NC}"
echo -e "${GREEN}========================================${NC}"
