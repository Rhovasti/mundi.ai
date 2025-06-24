# Eno Fantasy World Integration - Project Status

## Project Overview

This document tracks the current status of integrating the Eno fantasy world into the Mundi.ai GIS platform. The goal is to create a functional mapping system for fantasy worlds with proper coordinate alignment and custom basemaps.

## Current Date: 2025-06-24

## System Architecture

### Components
1. **World Model System** - Defines coordinate systems and transformations for fantasy worlds
2. **Custom Basemap System** - Serves raster and vector tiles from local files
3. **Frontend Map Display** - MapLibre GL based map viewer with world/basemap selection
4. **Demo Pages** - Simplified viewers for testing individual basemaps

### Data Flow
```
Eno Source Files (GeoJSON, GeoTIFF)
    ↓
Custom Basemap Configuration (Database)
    ↓
API Endpoints (Style, Tiles, Data)
    ↓
MapLibre GL Rendering
    ↓
User Interface (with World Model transformation)
```

## Current Issues

### 1. Demo Page Blank Screen (HIGH PRIORITY)
- **URL**: http://localhost:8000/demo/basemap/BxvFhuzMcnuy
- **Status**: Shows blank white screen with console errors
- **Root Cause**: MapLibre initialization issues with vector GeoJSON sources
- **Debug Tool**: Created enhanced debug page at `/demo/basemap-debug/BxvFhuzMcnuy`

### 2. Coordinate Alignment Issues (HIGH PRIORITY)
- **Problem**: Basemaps and vector data don't align properly
- **Current Approach**: 2.5x scale factor transformation
- **Issues**: 
  - Transformation may be applied incorrectly
  - Different behavior for raster vs vector sources
  - No visual debugging tools

### 3. Architecture Complexity
- **Problem**: Multiple transformation points make debugging difficult
- **Areas**:
  - World model transformation
  - Basemap-level transformation
  - Layer-level transformation
  - Frontend coordinate handling

## Implemented Features

### Backend
✅ World Model database schema and API
✅ Custom Basemap database schema and API
✅ Raster tile serving from local files
✅ GeoJSON data serving for vector basemaps
✅ MapLibre style generation
✅ Coordinate transformation endpoints

### Frontend
✅ World Model selector component
✅ Basemap selector with world model filtering
✅ Basic map display with MapLibre GL
✅ Integration with main project view

### Data
✅ Eno World Model created (ID: Wabcdefghijk)
✅ Multiple basemaps registered:
  - BGBov1d6Svoy - Eno Fantasy World
  - BwFKKVCxBm6o - Eno Relief Preview
  - BTxKGw6JlkzT - Eno Relief Map - Tiled
  - BUlJVMxOuaEK - Eno Relief Map - Docker
  - BxBJQPSOAiO8 - Eno Cities Vector Layer
  - BRpEy7CJaWuQ - Eno Cities Vector Style
  - BxvFhuzMcnuy - Eno Cities Vector - Docker

## Pending Tasks

### Immediate (This Session)
1. ⏳ Fix demo page rendering issue
2. ⏳ Debug coordinate alignment
3. ⏳ Add coordinate display overlay to main map
4. ⏳ Document transformation logic
5. ⏳ Consolidate duplicate basemap entries

### Short Term
1. Create test dataset with known coordinates
2. Implement visual debugging tools (grid overlay)
3. Add coordinate transformation tests
4. Improve error handling and logging

### Long Term
1. Implement proper vector tile generation (MVT format)
2. Add tile caching layer
3. Create georeferencing UI
4. Support multiple coordinate systems
5. Performance optimization

## Technical Details

### Coordinate System
- **Source CRS**: WGS84 (EPSG:4326)
- **Eno World Extent**: -720°, -450°, 1080°, 450° (from Maailmankello.shp)
- **Scale Factor**: 2.5x Earth size
- **Center**: [180.0, 0.0]

### File Locations
- **Eno Source Data**: `/app/Eno/`
- **Relief Tiles**: `/app/Eno/tif/relief_tiles/{z}/{x}/{y}.png`
- **Cities GeoJSON**: `/app/Eno/karttatiedostot kaupungeista/kaupunkiensijainti.geojson`

### API Endpoints
- **Basemap Info**: GET /api/basemaps/{id}
- **Basemap Style**: GET /api/basemaps/{id}/style
- **GeoJSON Data**: GET /api/basemaps/{id}/data
- **Raster Tiles**: GET /api/tiles/local/{id}/{z}/{x}/{y}.png
- **Vector Tiles**: GET /api/basemaps/{id}/vector/{z}/{x}/{y}.json

### Debug Tools
- **Enhanced Debug Page**: http://localhost:8000/demo/basemap-debug/{basemap_id}
  - Extensive logging
  - Coordinate display
  - Grid overlay toggle
  - Data endpoint testing
  - Error diagnostics

## Next Steps

1. **Debug Demo Page** - Use the enhanced debug tool to identify exact rendering issue
2. **Test Coordinate Transformations** - Create simple test case with known coordinates
3. **Visual Debugging** - Implement grid overlay in main application
4. **Documentation** - Create detailed coordinate transformation specification
5. **Simplification** - Consider removing unnecessary complexity

## Notes for Future Sessions

- The debug page at `/demo/basemap-debug/BxvFhuzMcnuy` provides extensive logging
- Check browser console for detailed error messages
- The main issue appears to be with MapLibre's handling of GeoJSON sources
- Consider whether the world model system is over-engineered for current needs
- Test with both raster (BUlJVMxOuaEK) and vector (BxvFhuzMcnuy) basemaps

## Resources

- **Original Project**: https://github.com/BuntingLabs/mundi.ai
- **This Fork**: https://github.com/Rhovasti/mundi.ai
- **MapLibre GL JS**: https://maplibre.org/
- **Previous Progress**: See WORLD_MODEL_PROGRESS.md and CUSTOM_BASEMAPS_SUMMARY.md