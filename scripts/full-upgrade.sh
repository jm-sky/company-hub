#!/bin/bash

# Full upgrade script - runs both backend and frontend upgrades

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Starting full system upgrade..."

log "📥 Pulling latest changes..."
git pull

log "✅ Git pull completed successfully!"

# ------------------------------------------------------------
# Backend Upgrade
# ------------------------------------------------------------
log "🔧 Running backend upgrade..."

"$SCRIPT_DIR/back-upgrade.sh"

# ------------------------------------------------------------
# Frontend Upgrade
# ------------------------------------------------------------
log "🎨 Running frontend upgrade..."

"$SCRIPT_DIR/front-upgrade.sh"

log "🎉 Full system upgrade completed successfully!"
