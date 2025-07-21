#!/bin/bash

# Database Migration Script

set -e

echo "🗃️ Running database migrations..."

# Check if app container is running
if ! docker compose ps app | grep -q "Up"; then
    echo "❌ App container is not running. Please start it first with 'docker compose up -d'"
    exit 1
fi

# Run migrations
echo "📋 Running Alembic migrations..."
docker compose exec app alembic upgrade head

echo "✅ Database migrations completed successfully!"

# Optionally seed with test data
read -p "Would you like to seed the database with test data? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Seeding database with test data..."
    docker compose exec app python app/db/seed.py
fi

echo ""
echo "🎉 Database setup completed!"
echo ""
echo "📍 Database access:"
echo "  • Admin UI:     http://localhost:${PGADMIN_PORT:-8080}"
echo "  • Connection:   postgresql://${POSTGRES_USER:-companyhub}:${POSTGRES_PASSWORD:-password}@localhost:${DB_PORT:-5432}/${POSTGRES_DB:-companyhub}"
echo ""