#!/bin/bash

# Mundi.ai Local Development Startup Script
set -e

echo "=========================================="
echo "     Mundi.ai Local Development Setup     "
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker permissions
if ! docker info &> /dev/null; then
    echo "⚠️  Docker requires sudo privileges. Please run with sudo:"
    echo "   sudo ./start-local.sh"
    echo ""
    echo "   Or add your user to the docker group:"
    echo "   sudo usermod -aG docker $USER"
    echo "   Then log out and back in."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.local .env
    echo "✅ Created .env file. Please configure your LLM settings:"
    echo ""
    echo "   Option 1: OpenAI API"
    echo "   - Edit .env and set OPENAI_API_KEY=sk-your-key"
    echo ""
    echo "   Option 2: Ollama (Local LLM)"
    echo "   - Install Ollama: https://ollama.com"
    echo "   - Run: ollama pull llama3.2"
    echo "   - Uncomment Ollama settings in .env"
    echo ""
    read -p "Press Enter to continue after configuring .env..."
fi

# Load environment variables
source .env

# Check LLM configuration
echo "🤖 Checking LLM configuration..."
if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "ollama" ]; then
    echo "✅ Using OpenAI API"
elif [ "$OPENAI_API_KEY" = "ollama" ]; then
    echo "✅ Using Ollama at ${OPENAI_BASE_URL:-http://host.docker.internal:11434/v1}"
    
    # Check if Ollama is running on host
    if command -v ollama &> /dev/null; then
        if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "⚠️  Ollama is installed but not running. Starting Ollama..."
            ollama serve &
            sleep 3
        fi
        echo "✅ Ollama is running on host"
    else
        echo "⚠️  Ollama not found on host. Make sure it's installed and running."
    fi
else
    echo "⚠️  No LLM configured. AI features will be limited."
    echo "   Configure OPENAI_API_KEY in .env for full functionality."
fi

# Create necessary directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/{postgres,minio,redis,uploads,ollama}
mkdir -p scripts

# Clone DriftDB if not present
if [ ! -d "driftdb" ]; then
    echo "📦 Cloning DriftDB for collaborative features..."
    git clone https://github.com/drifting-in-space/driftdb.git driftdb
fi

# Build and start services
echo ""
echo "🚀 Starting Mundi.ai services..."
echo "   This may take several minutes on first run..."
echo ""

# Use docker compose or docker-compose based on availability
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Build and start with local configuration
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.local.yml up --build -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service health
echo ""
echo "🔍 Checking service status..."
$DOCKER_COMPOSE ps

# Show logs for app container to check startup
echo ""
echo "📋 Application logs (last 20 lines):"
$DOCKER_COMPOSE logs --tail=20 app

echo ""
echo "=========================================="
echo "✅ Mundi.ai is starting up!"
echo ""
echo "🌐 Access the application at: http://localhost:8000"
echo "📊 MinIO Console (S3): http://localhost:9001"
echo "   Username: admin"
echo "   Password: password"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        $DOCKER_COMPOSE logs -f app"
echo "   Stop services:    $DOCKER_COMPOSE down"
echo "   Restart services: $DOCKER_COMPOSE restart"
echo "   Run tests:        $DOCKER_COMPOSE exec app pytest"
echo ""
echo "🔧 Troubleshooting:"
echo "   If services fail to start, check logs with:"
echo "   $DOCKER_COMPOSE logs [service-name]"
echo "=========================================="