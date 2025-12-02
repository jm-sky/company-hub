#!/bin/bash

# Quick script to view production logs

SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "📝 Showing all logs (last 100 lines)..."
    docker-compose -f docker-compose.prod.yml logs --tail=100 -f
else
    echo "📝 Showing logs for: $SERVICE"
    docker-compose -f docker-compose.prod.yml logs --tail=100 -f "$SERVICE"
fi
