#!/bin/bash

# Database Migration Script

set -e

echo "🗃️ Running database migrations..."

# Check if app container is running
if ! docker-compose ps app | grep -q "Up"; then
    echo "❌ App container is not running. Please start it first with 'docker-compose up -d'"
    exit 1
fi

# Run migrations
echo "📋 Running Alembic migrations..."
docker-compose exec app alembic upgrade head

echo "✅ Database migrations completed successfully!"

# Optionally seed with test data
read -p "Would you like to seed the database with test data? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Seeding database with test data..."
    docker-compose exec app python -c "
from app.db.database import SessionLocal
from app.db.models import User, Company
from app.utils.validators import normalize_nip
from datetime import datetime

db = SessionLocal()

# Create test user
test_user = User(
    email='test@example.com',
    password_hash='hashed_password',
    plan='premium',
    is_active=True
)
db.add(test_user)

# Create test companies
test_companies = [
    Company(nip='1234567890', name='Test Company 1'),
    Company(nip='0987654321', name='Test Company 2'),
    Company(nip='5555555555', name='Test Company 3')
]

for company in test_companies:
    db.add(company)

db.commit()
db.close()

print('✅ Test data seeded successfully!')
"
fi

echo ""
echo "🎉 Database setup completed!"
echo ""
echo "📍 Database access:"
echo "  • Admin UI:     http://localhost:${ADMINER_PORT:-8080}"
echo "  • Connection:   postgresql://companyhub:password@localhost:${DB_PORT:-5432}/companyhub"
echo ""