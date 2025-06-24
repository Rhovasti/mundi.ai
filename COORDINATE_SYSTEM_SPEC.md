# Eno World Coordinate System Specification

## Overview

This document specifies the coordinate system and transformation logic used for the Eno fantasy world in Mundi.ai.

## Coordinate Systems

### 1. Source Coordinate System (Eno Native)
- **Type**: Geographic coordinates similar to WGS84
- **Units**: Degrees
- **Extent**: Based on Maailmankello.shp analysis
  - **Longitude**: -73.312° to 117.287° (range: ~190.6°)
  - **Latitude**: -92.897° to 98.423° (range: ~191.3°)
- **Origin**: Appears to use standard lon/lat with custom bounds

### 2. World Model Coordinate System
- **Model ID**: Wabcdefghijk (Eno World)
- **Scale Factor**: 2.5x Earth size
- **Stored Extent**: [-720°, -450°, 1080°, 450°]
- **Center**: [180.0, 0.0]
- **Purpose**: Define the full world bounds including unmapped areas

### 3. Display Coordinate System (MapLibre GL)
- **Type**: Web Mercator projection (EPSG:3857) internally
- **Units**: Degrees for API, meters for internal calculations
- **Constraints**: 
  - Longitude: -180° to 180° (wrapped)
  - Latitude: ~-85° to ~85° (Mercator limits)

## Transformation Pipeline

### Current Implementation (As Found)

```
Source Coordinates (Eno GeoJSON)
    ↓
[No transformation - coordinates used as-is]
    ↓
Basemap Configuration (bounds, center stored)
    ↓
World Model Transformation (2.5x scale applied in frontend)
    ↓
MapLibre GL Display
```

### Issues with Current Implementation

1. **Scale Factor Application**
   - Applied in `MapLibreMap.tsx` lines 806-820
   - Only scales bounds and center, not the actual data
   - GeoJSON features remain at original coordinates
   - Creates mismatch between basemap position and data position

2. **Coordinate Range**
   - Eno coordinates already exceed normal lon/lat ranges
   - Applying 2.5x scale pushes them further out of bounds
   - MapLibre GL may not handle coordinates outside [-180, 180] properly

3. **Missing Transformations**
   - No transformation applied to actual feature geometries
   - Vector tile generation doesn't apply world model transformation
   - Raster tiles assumed to be pre-transformed

## Proposed Solution

### Option 1: Transform at Data Level
- Apply transformation when serving GeoJSON/tiles
- Keep display coordinates within standard bounds
- Modify `/api/basemaps/{id}/data` endpoint

### Option 2: Remove Scale Transformation
- Use Eno coordinates as-is (they already represent a fantasy world)
- Adjust world model to match actual data bounds
- Simplify the transformation pipeline

### Option 3: Custom Projection
- Implement a custom projection in MapLibre GL
- Handle fantasy world coordinates natively
- Most complex but most correct solution

## Coordinate Examples

### Eno Cities Sample Coordinates
From kaupunkiensijainti.geojson:
```json
{
  "type": "Feature",
  "properties": {
    "Id": 1,
    "Burg": "Jouy",
    "X": 1858.5,
    "Y": 452.74,
    "Latitude": 26.78,
    "Longitude": 84.67
  },
  "geometry": {
    "type": "Point",
    "coordinates": [84.67, 26.78]
  }
}
```

Note: The file contains both X/Y and Lat/Lon coordinates, using Lat/Lon in geometry.

### With 2.5x Scale Applied
- Original: [84.67, 26.78]
- Transformed: [211.675, 66.95]
- **Issue**: This moves the point far outside the basemap bounds

## Debugging Steps

1. **Verify Source Data**
   - Check if coordinates in GeoJSON match expected positions
   - Compare with basemap visual features

2. **Test Without Transformation**
   - Disable scale factor in frontend
   - Check if alignment improves

3. **Inspect Actual Bounds**
   - Log actual data bounds from GeoJSON
   - Compare with configured basemap bounds
   - Verify world model extent matches reality

## Implementation Notes

### Frontend (MapLibreMap.tsx)
- Lines 795-821: Coordinate transformation logic
- Lines 851-852: TMS scheme for fantasy worlds
- Lines 891-912: World model change handler

### Backend (basemap_routes.py)
- `/api/basemaps/{id}/data`: Serves raw GeoJSON
- `/api/basemaps/{id}/style`: Generates MapLibre style
- No transformation currently applied at backend

### Database
- `custom_basemaps.bounds`: Stores basemap bounds
- `custom_basemaps.center`: Stores basemap center
- `world_models.extent_bounds`: Stores world extent
- `world_models.planet_scale_factor`: Stores scale factor

## Recommendations

1. **Immediate**: Remove or fix the 2.5x scale transformation
2. **Short-term**: Add coordinate validation and logging
3. **Long-term**: Implement proper fantasy world projection

## Testing Checklist

- [ ] Load basemap without world model selected
- [ ] Load basemap with world model selected
- [ ] Compare city positions with basemap features
- [ ] Test with grid overlay enabled
- [ ] Verify bounds and center calculations
- [ ] Check coordinate display at different zoom levels