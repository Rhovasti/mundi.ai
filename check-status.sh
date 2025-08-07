#!/bin/bash

echo "🔍 Checking Mundi.ai service status..."
echo ""

# Check all services
echo "📊 Docker Compose Services:"
sudo docker compose ps
echo ""

# Check if app is running
APP_STATUS=$(sudo docker compose ps app --format json 2>/dev/null | grep -o '"State":"[^"]*' | cut -d'"' -f4)
if [ "$APP_STATUS" = "running" ]; then
    echo "✅ Mundi app is running!"
    
    # Test if the app is responding
    echo "🌐 Testing application response..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|301\|302"; then
        echo "✅ Application is responding at http://localhost:8000"
    else
        echo "⚠️  Application not responding yet. It may still be starting up..."
        echo "   Check logs: sudo docker compose logs app"
    fi
else
    echo "❌ Mundi app is not running"
    echo "   Starting app..."
    sudo docker compose up -d app
fi

echo ""
echo "📋 Recent app logs:"
sudo docker compose logs --tail=10 app

echo ""
echo "💡 Quick commands:"
echo "   View full logs:  sudo docker compose logs -f app"
echo "   Restart app:     sudo docker compose restart app"
echo "   Stop all:        sudo docker compose down"
echo "   Start missing:   sudo docker compose up -d"