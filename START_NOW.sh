#!/bin/bash

echo "🚀 Starting Mundi.ai (without DriftDB - collaboration features disabled)"
echo ""
echo "Building and starting services..."
echo "This will take several minutes on first run..."
echo ""

# Stop any existing containers
sudo docker compose down 2>/dev/null

# Build and start services
sudo docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Service Status:"
sudo docker compose ps

echo ""
echo "✅ Services are starting!"
echo ""
echo "🌐 Access Mundi.ai at: http://localhost:8000"
echo "📦 MinIO Console at: http://localhost:9001 (admin/password)"
echo ""
echo "📋 Monitor logs with: sudo docker compose logs -f app"
echo "🛑 Stop with: sudo docker compose down"