#!/bin/bash

# Frontend upgrade script
# Pulls latest changes, installs dependencies, builds, and restarts service

set -e

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Starting frontend upgrade..."

# Navigate to frontend directory
cd frontend

# ------------------------------------------------------------
# Git
# ------------------------------------------------------------

log "📥 Pulling latest changes..."

git pull

log "✅ Git pull completed successfully!"

# ------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------

log "📦 Installing dependencies..."

pnpm install

# ------------------------------------------------------------
# Build
# ------------------------------------------------------------

log "🏗️ Building frontend..."

pnpm run build

# ------------------------------------------------------------
# Restart
# ------------------------------------------------------------

log "🔄 Restarting service..."
sudo systemctl restart company-hub-web.service

# ------------------------------------------------------------

log "🎉 Frontend upgrade completed successfully!"
