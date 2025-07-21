#!/bin/bash

# CompanyHub Production Setup Script

set -e

echo "🚀 Setting up CompanyHub production environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Load environment variables for production
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo "✅ Environment variables loaded."
else
    echo "⚠️  Warning: .env file not found. Using default values."
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your production values."
    echo "🛑 Setup stopped. Please configure .env file before running again."
    exit 1
fi

# Build and start services
echo "🔧 Building and starting services..."
docker compose -f docker-compose.prod.yml down --volumes
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker compose -f docker-compose.prod.yml exec db pg_isready -U ${POSTGRES_USER:-companyhub} -d ${POSTGRES_DB:-companyhub}; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

# Check Redis
if docker compose -f docker-compose.prod.yml exec redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
    exit 1
fi

# Check FastAPI app
if curl -f http://localhost:${DOCKER_APP_PORT:-8000}/health &> /dev/null; then
    echo "✅ FastAPI app is ready"
else
    echo "❌ FastAPI app is not ready"
    exit 1
fi

echo ""
echo "🎉 Production environment is ready!"
echo ""
echo "📍 Services:"
echo "  • API:              http://localhost:${DOCKER_APP_PORT:-8000}"
echo "  • API Docs:         http://localhost:${DOCKER_APP_PORT:-8000}/docs"
echo "  • Database Admin:   http://localhost:${PGADMIN_PORT:-5050}"
echo ""
echo "🔧 Useful commands:"
echo "  • View logs:        docker compose -f docker-compose.prod.yml logs -f"
echo "  • Stop services:    docker compose -f docker-compose.prod.yml down"
echo "  • Rebuild:          docker compose -f docker-compose.prod.yml build"
echo "  • Run tests:        docker compose -f docker-compose.prod.yml exec app pytest"
echo ""
echo "📝 Next steps:"
echo "  • Verify .env file has production values"
echo "  • Run database migrations: ./scripts/db-migrate.sh"
echo "  • Monitor logs: docker compose -f docker-compose.prod.yml logs -f"
echo ""
