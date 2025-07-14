#!/bin/bash

# CompanyHub Development Setup Script

set -e

echo "🚀 Setting up CompanyHub development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
fi

# Build and start services
echo "🔧 Building and starting services..."
docker-compose down --volumes
docker-compose build
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec db pg_isready -U companyhub -d companyhub; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

# Check Redis
if docker-compose exec redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
    exit 1
fi

# Check FastAPI app
if curl -f http://localhost:${APP_PORT:-8000}/health &> /dev/null; then
    echo "✅ FastAPI app is ready"
else
    echo "❌ FastAPI app is not ready"
    exit 1
fi

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📍 Services:"
echo "  • API:              http://localhost:${APP_PORT:-8000}"
echo "  • API Docs:         http://localhost:${APP_PORT:-8000}/docs"
echo "  • Database Admin:   http://localhost:${ADMINER_PORT:-8080}"
echo "  • Redis Admin:      http://localhost:${REDIS_COMMANDER_PORT:-8081}"
echo ""
echo "🔧 Useful commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop services:    docker-compose down"
echo "  • Rebuild:          docker-compose build"
echo "  • Run tests:        docker-compose exec app pytest"
echo ""
echo "📝 Don't forget to:"
echo "  • Update .env with your API keys"
echo "  • Run database migrations if needed"
echo ""