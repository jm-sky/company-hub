#!/bin/bash

# Frontend Build and Deploy Script
# Rebuilds and recreates the Next.js frontend container (Docker Compose).
#
# Usage: scripts/frontend_build_deploy.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

echo -e "${GREEN}🔨 Starting frontend build and deploy...${NC}"

cd "$PROJECT_DIR"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo -e "${RED}Error: Docker Compose file not found: $COMPOSE_FILE${NC}" >&2
  exit 1
fi

echo -e "${YELLOW}📦 Building frontend image (${COMPOSE_FILE})...${NC}"
docker compose -f "$COMPOSE_FILE" build frontend

echo -e "${YELLOW}🔄 Recreating frontend container...${NC}"
docker compose -f "$COMPOSE_FILE" up -d --force-recreate frontend

echo -e "${GREEN}✅ Frontend build and deploy completed successfully!${NC}"
