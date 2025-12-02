#!/bin/bash

# Quick status check for production services

echo "📊 Production Services Status"
echo "=============================="
echo ""

docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔍 Service Health:"
echo ""

# Check backend
BACKEND_PORT=$(grep DOCKER_APP_PORT .env 2>/dev/null | cut -d= -f2 || echo "8000")
if curl -s -f "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
    echo "✅ Backend API (port $BACKEND_PORT): Healthy"
else
    echo "❌ Backend API (port $BACKEND_PORT): Not responding"
fi

# Check frontend
FRONTEND_PORT=$(grep DOCKER_FRONTEND_PORT .env 2>/dev/null | cut -d= -f2 || echo "3000")
if curl -s -f "http://localhost:${FRONTEND_PORT}/api/health" > /dev/null 2>&1; then
    echo "✅ Frontend (port $FRONTEND_PORT): Healthy"
else
    echo "❌ Frontend (port $FRONTEND_PORT): Not responding"
fi

echo ""
