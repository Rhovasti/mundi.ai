# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mundi.ai is an open-source, AI-native GIS (Geographic Information System) application that combines mapping functionality with AI/LLM capabilities for geospatial data analysis and visualization.

## Development Commands

### Backend (Python/FastAPI)
```bash
# Run the backend server
python -m src.wsgi

# Run tests
pytest

# Run specific test
pytest src/test_bounds.py::test_name

# Run tests with specific markers
pytest -m postgres  # Tests requiring PostgreSQL
pytest -m s3        # Tests requiring S3/MinIO
```

### Frontend (React/TypeScript)
```bash
cd frontendts

# Development server
npm run dev

# Build production
npm run build

# Linting
npm run lint

# Watch mode for development
npm run watch
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up

# Rebuild containers
docker-compose build
```

## Architecture Overview

### Core Components

**Backend Architecture (FastAPI)**
- Main application entry: `src/wsgi.py` - FastAPI application with routers for different API endpoints
- Database models: `src/database/models.py` - SQLAlchemy models for PostgreSQL with PostGIS support
- API routers organized by feature in `src/routes/`:
  - `postgres_routes.py` - PostGIS connection and data operations
  - `layer_router.py` - Map layer management
  - `conversation_routes.py` - AI conversation handling
  - `websocket.py` - Real-time WebSocket connections for collaborative features
  - `project_routes.py` - Project/map management

**Frontend Architecture (React/Vite)**
- Entry point: `frontendts/src/main.tsx`
- Map rendering: `frontendts/src/components/MapLibreMap.tsx` - Core mapping component using MapLibre GL JS
- State management: React Query for server state, local state with hooks
- UI components: Shadcn/ui components in `frontendts/src/components/ui/`

**Database Layer**
- PostgreSQL with PostGIS extension for spatial data
- Alembic migrations in `alembic/versions/`
- Connection pooling via asyncpg
- Support for external PostGIS databases

**AI/LLM Integration**
- Chat completion system in `src/dependencies/chat_completions.py`
- System prompts handling in `src/dependencies/system_prompt.py`
- Symbology generation via LLM in `src/symbology/llm.py`
- Support for OpenAI API and local Ollama models

**Geospatial Processing**
- GDAL/OGR for raster and vector operations
- DuckDB for spatial queries (`src/duckdb.py`)
- QGIS processing server integration (`qgis-processing/`)
- Support for various formats: GeoJSON, Shapefile, GeoPackage, LAZ/LAS point clouds, COG/GeoTIFF

**Real-time Collaboration**
- DriftDB integration for collaborative editing
- WebSocket connections for live updates
- Room-based collaboration model

## Key Technical Details

- **Map Rendering**: Uses MapLibre GL JS with custom style generation
- **Vector Tiles**: Generates MVT tiles from PostGIS using ST_AsMVT
- **Raster Support**: COG (Cloud Optimized GeoTIFF) with dynamic tiling
- **Point Clouds**: LAZ/LAS visualization using deck.gl
- **Authentication**: Configurable auth modes, SuperTokens integration optional
- **File Storage**: Local filesystem with LRU cache (`src/fs_lru.py`)
- **Projections**: Automatic CRS detection and reprojection using GDAL/Proj

## Testing Strategy

- Unit tests for individual components
- Integration tests for API endpoints
- Fixtures in `test_fixtures/` for geospatial data testing
- Async test support with pytest-asyncio
- Test markers for conditional test execution (postgres, s3)

## Environment Variables

Key environment variables to configure:
- `MUNDI_AUTH_MODE`: Authentication mode (e.g., "edit" for open access)
- `DATABASE_URL`: PostgreSQL connection string
- OpenAI/LLM configuration for AI features
- S3/storage configuration for cloud deployments