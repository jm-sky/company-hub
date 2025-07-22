#!/bin/bash

# Backend upgrade script
# Installs dependencies, runs migrations, and restarts services

set -e

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Starting backend upgrade..."

# ------------------------------------------------------------
# Git
# ------------------------------------------------------------

log "📥 Pulling latest changes..."

git pull

log "✅ Git pull completed successfully!"

# ------------------------------------------------------------
# Build
# ------------------------------------------------------------

log "🏗️ Rebuilding backend container..."

docker compose -f docker-compose.prod.yml build app

log "✅ Backend container rebuilt successfully!"

# ------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------

log "📦 Installing backend dependencies..."

docker compose -f docker-compose.prod.yml exec app pip install -r requirements.txt

log "✅ Backend dependencies installed successfully!"

# ------------------------------------------------------------
# Database
# ------------------------------------------------------------

log "🗃️ Running database migrations..."

docker compose -f docker-compose.prod.yml exec app alembic upgrade head

log "✅ Database migrations completed successfully!"

# ------------------------------------------------------------
# Restart
# ------------------------------------------------------------

log "🔄 Restarting backend services..."

docker compose -f docker-compose.prod.yml up -d app

log "✅ Backend services restarted successfully!"

# ------------------------------------------------------------

log "🎉 Backend upgrade completed successfully!"
