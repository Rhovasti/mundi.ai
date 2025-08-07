#!/bin/bash

echo "🔍 Checking DriftDB status..."
echo ""

# Check logs
echo "📋 DriftDB logs (last 20 lines):"
sudo docker compose -f docker-compose.driftdb.yml logs driftdb --tail=20

echo ""
echo "🔍 Testing DriftDB connectivity:"

# Test if DriftDB is responding
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ DriftDB is responding on port 8080"
else
    echo "❌ DriftDB is not responding"
    echo ""
    echo "Trying to fix health check..."
    
    # Update health check to be less strict
    sudo docker compose -f docker-compose.driftdb.yml exec driftdb ls / > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Container is running, health check might be too strict"
    fi
fi

echo ""
echo "🔍 Testing room creation:"
# Try to create a test room
RESPONSE=$(curl -s -X POST http://localhost:8080/new)
if [ ! -z "$RESPONSE" ]; then
    echo "✅ Room creation endpoint works"
    echo "Response: $RESPONSE"
else
    echo "❌ Room creation failed"
fi

echo ""
echo "📊 Container status:"
sudo docker compose -f docker-compose.driftdb.yml ps

echo ""
echo "💡 If DriftDB is unhealthy but responding, the app should still work."
echo "   Try creating a map at http://localhost:8000"