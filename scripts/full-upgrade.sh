#!/bin/bash

# Git pull

set -e

echo "🔄 Pulling latest changes..."

git pull

# ------------------------------------------------------------
# Backend
# ------------------------------------------------------------

echo "🗃️ Running database migrations..."

docker compose exec app alembic upgrade head

echo "✅ Database migrations completed successfully!"

echo "🔄 Restarting backend services..."

docker compose restart

echo "✅ Backend services restarted successfully!"

# ------------------------------------------------------------
# Frontend
# ------------------------------------------------------------
echo "🔄 Installing frontend dependencies..."

cd frontend

pnpm install

pnpm run build

echo "✅ Frontend build completed successfully!"

echo "🔄 Restarting frontend services..."

sudo systemctl restart company-hub-web.service

echo "✅ Frontend services restarted successfully!"

echo "Upgrade completed successfully!"
