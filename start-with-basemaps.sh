#!/bin/bash

echo "🚀 Starting Mundi.ai with Custom Basemap Support..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running or accessible. Please start Docker and ensure your user has permissions."
    echo "   You may need to run: sudo usermod -aG docker $USER"
    echo "   Then log out and back in, or run with sudo."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Copying .env.local to .env..."
    cp .env.local .env
    echo "✅ Environment file ready"
else
    echo "✅ Environment file exists"
fi

echo ""
echo "🏗️  Building and starting services..."

# Start all services
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d

# Wait a moment for services to start
sleep 5

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🌐 Access Points:"
echo "   • Main Application: http://localhost:8000"
echo "   • MinIO Console: http://localhost:9001 (admin/password)"
echo ""
echo "🗺️  Custom Basemap Features:"
echo "   • The globe button now shows a dropdown with multiple basemap options"
echo "   • Includes preset basemaps: OSM, Carto Light/Dark, Stamen, ESRI Satellite"
echo "   • Users can add custom XYZ tile servers via the API"
echo ""
echo "🔧 To test custom basemaps:"
echo "   1. Open http://localhost:8000"
echo "   2. Create a new map"
echo "   3. Click the globe button to see basemap options"
echo "   4. Try different preset basemaps"
echo ""
echo "📝 Logs: docker compose logs -f app"
echo "⏹️  Stop: docker compose down"