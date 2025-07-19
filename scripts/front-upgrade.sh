#!/bin/bash

# Frontend upgrade script
# Pulls latest changes, installs dependencies, builds, and restarts service

set -e

echo "Starting frontend upgrade..."

# Navigate to frontend directory
cd frontend

echo "Pulling latest changes..."
git pull

echo "Installing dependencies..."
pnpm i

echo "Building frontend..."
pnpm build

echo "Restarting service..."
sudo systemctl restart company-hub-web.service

echo "Frontend upgrade completed successfully!"