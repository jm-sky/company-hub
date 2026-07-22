#!/usr/bin/env bash
# Rebuild and restart the backend, then run migrations.
#
# Usage:
#   COMPOSE_FILE=docker-compose.prod.yml bash scripts/backend_restart_migrate.sh
#   bash scripts/backend_restart_migrate.sh
#
# Called by deploy.sh — can also be run standalone from the project root.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if [ ! -f "$PROJECT_DIR/$COMPOSE_FILE" ]; then
  echo -e "${RED}Error: Docker Compose file not found: $PROJECT_DIR/$COMPOSE_FILE${NC}" >&2
  exit 1
fi

echo -e "${GREEN}Restarting backend (${COMPOSE_FILE})...${NC}"

cd "$PROJECT_DIR"

echo -e "${YELLOW}Building app image...${NC}"
docker compose -f "$COMPOSE_FILE" build app

echo -e "${YELLOW}Recreating app container...${NC}"
docker compose -f "$COMPOSE_FILE" up -d --force-recreate app

echo -e "${YELLOW}Waiting for app to be healthy...${NC}"
sleep 5

echo -e "${YELLOW}Running migrations...${NC}"
docker compose -f "$COMPOSE_FILE" exec app alembic upgrade head

echo -e "${GREEN}Backend restarted and migrations applied (${COMPOSE_FILE})${NC}"
