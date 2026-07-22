#!/bin/bash

# CompanyHub Complete Deployment Script
# This script orchestrates the complete deployment by pulling latest changes,
# building and deploying the frontend, and restarting/migrating the backend
#
# Usage: scripts/deploy.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

echo -e "${GREEN}🚀 Starting complete CompanyHub deployment...${NC}"

# Step 1: Pull latest changes
echo -e "${YELLOW}📦 Step 1: Pulling latest changes...${NC}"
cd "$PROJECT_DIR"
git pull

# Step 2: Build and deploy frontend
echo -e "${YELLOW}🔨 Step 2: Building and deploying frontend...${NC}"
"$SCRIPTS_DIR/frontend_build_deploy.sh"

# Step 3: Restart backend and migrate
echo -e "${YELLOW}🐳 Step 3: Restarting backend and running migrations...${NC}"
"$SCRIPTS_DIR/backend_restart_migrate.sh"

echo ""
echo -e "${GREEN}✅ Complete deployment finished successfully!${NC}"
