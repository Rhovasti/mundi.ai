# Local Deployment Guide for Mundi.ai

This guide will help you set up Mundi.ai locally with LLM support for testing purposes.

## Prerequisites

1. **Docker & Docker Compose** - Required for running all services
   - Install Docker: https://docs.docker.com/get-docker/
   - Docker Compose is included with Docker Desktop

2. **Git** - For cloning dependencies
   - Install Git: https://git-scm.com/downloads

3. **LLM Access** (Choose one):
   - **OpenAI API Key** (Recommended) - Get from https://platform.openai.com/api-keys
   - **Ollama** (Free, Local) - Install from https://ollama.com

## Quick Start

### 1. Configure LLM Access

Copy the environment template:
```bash
cp .env.local .env
```

Edit `.env` and configure your LLM:

**Option A: OpenAI API (Recommended)**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o for better results
```

**Option B: Ollama (Local, Free)**
```bash
# First install Ollama and pull a model
ollama pull llama3.2

# Then in .env, uncomment:
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3.2
```

### 2. Start the Application

Run the startup script:
```bash
./start-local.sh
```

Or manually with Docker Compose:
```bash
# Create data directories
mkdir -p data/{postgres,minio,redis,uploads}

# Clone DriftDB if needed
git clone https://github.com/drifting-in-space/driftdb.git driftdb

# Start services
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build
```

### 3. Access the Application

Once running, access:
- **Mundi.ai**: http://localhost:8000
- **MinIO Console** (S3 storage): http://localhost:9001
  - Username: `admin`
  - Password: `password`

## Services Architecture

The local deployment includes:

| Service | Port | Description |
|---------|------|-------------|
| Mundi App | 8000 | Main FastAPI application |
| PostgreSQL | 5432 | Database with PostGIS |
| MinIO | 9000/9001 | S3-compatible storage |
| Redis | 6379 | Caching and sessions |
| DriftDB | 8080 | Real-time collaboration |
| QGIS Processing | 8817 | Geoprocessing engine |

## Testing the Deployment

### 1. Create Your First Map
1. Open http://localhost:8000
2. Click "Create New Map"
3. Upload a GeoJSON, Shapefile, or other spatial data
4. Use the AI assistant to style and analyze your data

### 2. Test LLM Features
- Ask the AI to style your layers
- Request spatial analysis
- Generate map descriptions
- Query your data using natural language

### 3. Test Data Sources
- Upload local files (GeoJSON, Shapefile, GeoPackage)
- Connect to PostGIS databases
- Load point clouds (LAZ/LAS files)
- Import raster data (GeoTIFF)

## Common Commands

```bash
# View logs
docker-compose logs -f app

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Run tests
docker-compose exec app pytest

# Access PostgreSQL
docker-compose exec postgresdb psql -U mundiuser -d mundidb

# Rebuild after code changes
docker-compose up --build app
```

## Troubleshooting

### Docker Issues
- **"Cannot connect to Docker daemon"**: Make sure Docker Desktop is running
- **Port conflicts**: Change ports in `docker-compose.local.yml` if needed

### LLM Issues
- **"No LLM configured"**: Check your `.env` file has valid API keys
- **Ollama connection failed**: Ensure Ollama is running (`ollama serve`)
- **OpenAI errors**: Verify your API key and check quota/billing

### Database Issues
- **Migration errors**: Clear data and restart: `docker-compose down -v && docker-compose up`
- **PostGIS not found**: The init script should auto-install, check logs

### Performance
- **Slow startup**: First run downloads images, subsequent runs are faster
- **High memory usage**: Adjust Docker Desktop memory limits in settings

## Development Mode

For hot-reloading during development:
1. Source code is mounted as volumes
2. Backend auto-reloads on Python file changes
3. Frontend requires rebuild: `docker-compose exec app npm run build`

## Data Persistence

Data is stored in `./data/`:
- `postgres/` - Database files
- `minio/` - Uploaded files and tiles
- `redis/` - Cache data
- `uploads/` - Temporary uploads

To reset everything:
```bash
docker-compose down -v
rm -rf data/
```

## Security Notes

⚠️ **This configuration is for local testing only!**
- Uses default passwords
- No HTTPS/SSL
- Open authentication mode
- Exposed database ports

For production deployment, see the official documentation.

## Next Steps

1. Review the [documentation](https://docs.mundi.ai)
2. Try the [demo PostGIS database](https://docs.mundi.ai/getting-started/connecting-to-demo-postgis/)
3. Explore [geoprocessing features](https://docs.mundi.ai/guides/geoprocessing-from-qgis/)
4. Join the [Discord community](https://discord.gg/V63VbgH8dT)

## Support

- GitHub Issues: https://github.com/BuntingLabs/mundi.ai/issues
- Discord: https://discord.gg/V63VbgH8dT
- Documentation: https://docs.mundi.ai