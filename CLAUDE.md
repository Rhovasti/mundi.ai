# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mundi is an AI-native GIS (Geographic Information System) platform built with:
- **Backend**: Python/FastAPI with async support, GDAL for geospatial operations
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Databases**: PostgreSQL with PostGIS, Redis, MinIO (S3-compatible)
- **Real-time**: DriftDB for collaborative map editing

## Essential Commands

### Development
```bash
# Full stack development (recommended)
docker-compose up

# Backend only (requires external services)
uvicorn src.wsgi:app --host 0.0.0.0 --port 8000 --log-level debug --access-log --use-colors

# Frontend development
cd frontendts && npm run dev

# Documentation site
cd docs && npm run dev
```

### Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m s3        # S3/MinIO tests
pytest -m postgres  # PostgreSQL tests
pytest -m asyncio   # Async tests
```

### Frontend Build
```bash
cd frontendts
npm run build      # Production build
npm run preview    # Preview production build
npm run watch      # Development with HMR
```

## Architecture

### Backend API Structure
- **src/routes/**: API endpoints organized by domain (maps, layers, vectors, etc.)
- **src/database/**: SQLAlchemy models and database connections
- **src/dependencies/**: Dependency injection for services (S3, database, auth)
- **src/renderer/**: Map rendering engine using MapLibre
- **src/symbology/**: Map styling and symbology logic
- **src/wsgi.py**: Main FastAPI application entry point

### Frontend Architecture
- **frontendts/src/components/**: React components, with reusable UI in `ui/` subdirectory
- **frontendts/src/hooks/**: Custom React hooks for map interactions and data fetching
- **frontendts/src/lib/**: Shared utilities, types, and API client code

### Key Dependencies
- **Geospatial**: GDAL, Shapely, GeoAlchemy2, MapLibre GL
- **API**: FastAPI, Pydantic, SQLAlchemy
- **Real-time**: DriftDB client for collaborative features
- **AI/LLM**: OpenAI client with support for local models (Ollama)

## Database Migrations

Use Alembic for database schema changes:
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Configuration

Key environment variables (see docker-compose.yml for defaults):
- `MUNDI_AUTH_MODE`: "edit" or "view_only"
- `S3_*`: MinIO/S3 configuration
- `POSTGRES_*`: Database connection
- `OPENAI_API_KEY`: For AI features (optional, can use Ollama locally)
- `DRIFTDB_SERVER_URL`: Real-time collaboration server

## API Patterns

### Route Organization
- Routes return Pydantic models for type safety
- Use dependency injection for services (get_s3, get_db, etc.)
- Async/await throughout for performance
- File uploads handled via FastAPI's UploadFile

### Frontend API Calls
- API client utilities in `frontendts/src/lib/`
- React Query or SWR patterns for data fetching
- WebSocket connections for real-time updates via DriftDB

## Testing Approach

- Unit tests alongside source files (test_*.py)
- Use pytest fixtures for database and S3 setup
- Mark tests with appropriate markers (@pytest.mark.s3, etc.)
- Test files should mirror the structure of source files