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
# Dependencies
# ------------------------------------------------------------

log "📦 Installing backend dependencies..."

docker compose exec app pip install -r requirements.txt

log "✅ Backend dependencies installed successfully!"

# ------------------------------------------------------------
# Database
# ------------------------------------------------------------

log "🗃️ Running database migrations..."

docker compose exec app alembic upgrade head

log "✅ Database migrations completed successfully!"

# ------------------------------------------------------------
# Restart
# ------------------------------------------------------------

log "🔄 Restarting backend services..."

docker compose restart

log "✅ Backend services restarted successfully!"

# ------------------------------------------------------------

log "🎉 Backend upgrade completed successfully!"
