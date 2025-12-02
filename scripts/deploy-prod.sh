#!/bin/bash

set -e

echo "🚀 Starting production deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes from git..."
git pull origin $(git branch --show-current)

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🔄 Restarting services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Show running containers
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Running containers:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔍 Service status:"
echo "  Backend API: http://localhost:${DOCKER_APP_PORT:-8000}"
echo "  Frontend: http://localhost:${DOCKER_FRONTEND_PORT:-3000}"
echo ""
echo "📝 View logs with:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
