# Custom Basemaps for Fantasy Worlds

This document explains how to use the new custom basemap functionality in Mundi for fantasy world mapping.

## Overview

The custom basemap feature allows you to:
- Use your own tile servers (XYZ format)
- Load tiles from local directories
- Configure custom coordinate systems (coming soon)
- Import Fantasy Map Generator data (coming soon)

## API Endpoints

### Create a Custom Basemap

```bash
POST /api/basemaps
Content-Type: application/json

{
  "name": "My Fantasy World",
  "tile_url_template": "https://myserver.com/tiles/{z}/{x}/{y}.png",
  "tile_format": "png",
  "min_zoom": 0,
  "max_zoom": 18,
  "tile_size": 256,
  "attribution": "© My Fantasy World",
  "bounds": [-180, -90, 180, 90],
  "center": [0, 0],
  "default_zoom": 2,
  "is_public": false,
  "metadata": {
    "world_name": "Azeroth",
    "created_date": "2024-01-01"
  }
}
```

### List Available Basemaps

```bash
GET /api/basemaps
```

Returns your basemaps and any public basemaps.

### Get MapLibre Style for a Basemap

```bash
GET /api/basemaps/{basemap_id}/style
```

Returns a complete MapLibre GL style JSON that can be used directly in your map.

### Delete a Basemap

```bash
DELETE /api/basemaps/{basemap_id}
```

## Using Local Tile Directories

For tiles stored on your local filesystem:

```json
{
  "name": "Local Fantasy Map",
  "tile_url_template": "file:///path/to/tiles/{z}/{x}/{y}.png",
  "tile_format": "png"
}
```

The system will automatically serve these tiles through the API at:
```
/api/tiles/local/{basemap_id}/{z}/{x}/{y}.png
```

## Frontend Integration

In your MapLibre GL map:

```javascript
// Fetch the basemap style
const response = await fetch(`/api/basemaps/${basemapId}/style`);
const style = await response.json();

// Create the map with custom basemap
const map = new maplibregl.Map({
  container: 'map',
  style: style,
  center: style.center,
  zoom: style.zoom
});
```

## Fantasy World Data Import

Use the import utility to load your fantasy world data:

```python
from src.util.fantasy_data_importer import import_fantasy_world_data

# Import with a specific user UUID
result = await import_fantasy_world_data("your-user-uuid")

# This will:
# - Import city data from comprehensive_city_analysis_results_updated_manually.json
# - Create basemap configurations for raster maps
# - Set up relief map configuration
```

## Next Steps

- **Custom Coordinate Systems**: Define non-Earth projections for your fantasy worlds
- **Fantasy Map Generator Import**: Direct import from FMG .map files
- **SpacetimeDB Integration**: Real-time collaborative editing
- **Graph Database**: Query spatial relationships between fantasy locations

## Example: Eno Fantasy World

The Eno dataset includes:
- 120+ fictional cities with detailed attributes
- Building footprints and districts for each city
- Castle locations and defensive structures
- Relief maps showing terrain
- Road networks connecting cities

To use this data:
1. Run the fantasy data importer
2. Select the created basemap in your map
3. Add city layers from the imported GeoJSON files
4. Style the layers based on city attributes (population, elevation, etc.)