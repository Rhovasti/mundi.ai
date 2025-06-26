# Fantasy Geography Basemaps in Mundi.ai

## Overview

Mundi.ai now supports custom fantasy geography basemaps as an alternative to traditional OpenStreetMap tiles. This feature allows you to create immersive GIS experiences using fantasy worlds, either from existing projects like OpenGeofiction or from your own custom GeoJSON data.

## Features

### 1. OpenGeofiction Integration
- **Direct tile access**: Uses OpenGeofiction's public tile server
- **Collaborative fantasy world**: Community-created fictional geography
- **CC BY-NC-SA 3.0 licensed**: Attribution-required, non-commercial use

### 2. Custom Fantasy Worlds
- **GeoJSON to PBF conversion**: Transform your GeoJSON data into OSM-compatible format
- **Fantasy-specific tags**: Custom OSM tags for magical elements, kingdoms, creatures
- **Vector tile generation**: High-performance tile serving via PostGIS

### 3. Fantasy Tag System
The system supports extensive fantasy-themed tagging:

#### Kingdoms and Realms
- `fantasy:kingdom` - Name of the ruling kingdom
- `fantasy:realm` - Broader geographical realm
- `fantasy:capital` - Mark capital cities

#### Magical Elements  
- `fantasy:magic` - Type of magic present
- `fantasy:magic_level` - Intensity of magical presence
- `fantasy:enchanted` - Mark enchanted areas
- `fantasy:cursed` - Mark cursed locations

#### Creatures and Inhabitants
- `fantasy:creature` - Creature type inhabiting area
- `fantasy:race` - Dominant race in the region
- `fantasy:inhabitant` - Specific inhabitant (e.g., dragon in lair)

#### Buildings and Structures
- `building=castle` + `fantasy:type=fortress`
- `building=tower` + `fantasy:type=wizard_tower`
- `building=temple` + `fantasy:type=divine_temple`
- `building=ruins` + `fantasy:type=ancient_ruins`

#### Landscapes
- `landuse=forest` + `fantasy:enchanted=yes`
- `natural=cave` + `fantasy:inhabitant=dragon`
- `natural=spring` + `fantasy:magical=yes`
- `waterway=river` + `fantasy:sacred=yes`

## Implementation Guide

### Quick Start: OpenGeofiction
1. Set environment variable: `MUNDI_BASEMAP_MODE=fantasy`
2. Restart the application
3. OpenGeofiction tiles will be used as the default basemap

### Custom Fantasy World Creation

#### Step 1: Prepare Your GeoJSON Data
Structure your GeoJSON files with fantasy-themed properties:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [...]
  },
  "properties": {
    "name": "Enchanted Forest of Elderwood",
    "landuse": "enchanted_forest",
    "fantasy:magic_level": "high",
    "fantasy:kingdom": "Elvendale",
    "fantasy:creature": "unicorn"
  }
}
```

#### Step 2: Convert to PBF Format
Use the provided conversion script:

```bash
# Convert single file
python scripts/geojson_to_pbf.py kingdoms.geojson fantasy_world.pbf

# Convert entire directory
python scripts/geojson_to_pbf.py data/fantasy_geojson/ complete_world.pbf

# Validate output
python scripts/geojson_to_pbf.py data/fantasy/ world.pbf --validate
```

#### Step 3: Import to PostGIS
```bash
# Install osm2pgsql if not already available
apt-get install osm2pgsql

# Import PBF to database
osm2pgsql -d mundidb -U mundiuser fantasy_world.pbf
```

#### Step 4: Configure Tile Server
Set up vector tile serving:

```bash
# Option 1: Using Martin (recommended)
export FANTASY_TILE_SERVER_URL="http://martin:3000"

# Option 2: Using TileServer-GL with MBTiles
# Generate MBTiles from PostGIS first
```

#### Step 5: Enable Fantasy Mode
```bash
export MUNDI_BASEMAP_MODE=fantasy
export FANTASY_TILE_SERVER_URL=http://localhost:3000
```

## Advanced Configuration

### Docker Compose Integration
Add to your `docker-compose.yml`:

```yaml
services:
  martin:
    image: maplibre/martin
    environment:
      - DATABASE_URL=postgresql://mundiuser:gdalpassword@postgresdb:5432/mundidb
    ports:
      - "3000:3000"
    depends_on:
      - postgresdb
```

### Multiple Fantasy Worlds
Support multiple fantasy worlds by organizing data:

```bash
# Medieval fantasy
python scripts/geojson_to_pbf.py data/medieval/ medieval_world.pbf

# Sci-fi world  
python scripts/geojson_to_pbf.py data/scifi/ scifi_world.pbf

# Import with prefixed table names
osm2pgsql -d mundidb --prefix medieval_ medieval_world.pbf
osm2pgsql -d mundidb --prefix scifi_ scifi_world.pbf
```

## API Endpoints

### Available Basemaps
```http
GET /api/basemaps/available
```

Returns list of available basemap styles including fantasy options.

### Map Style with Fantasy Basemap
```http
GET /api/maps/{map_id}/style.json?basemap=opengeofiction
GET /api/maps/{map_id}/style.json?basemap=custom
```

## Performance Considerations

### Tile Caching
- Vector tiles are generated on-demand from PostGIS
- Consider implementing tile caching for production use
- Monitor database performance with complex fantasy queries

### Data Size
- Large fantasy worlds may require significant PostgreSQL storage
- Use appropriate indexing on fantasy-specific columns
- Consider data partitioning for very large datasets

## Troubleshooting

### Common Issues

**"No fantasy tiles displaying"**
- Check `FANTASY_TILE_SERVER_URL` environment variable
- Verify PostGIS data import was successful
- Test tile server directly: `curl http://localhost:3000/tiles/0/0/0.pbf`

**"Conversion script fails"**
- Ensure `ogr2pbf` and `osmium` are installed
- Check GeoJSON files are valid
- Verify write permissions to output directory

**"Map shows blank/error tiles"**
- Check PostgreSQL connection from tile server
- Verify fantasy-specific tables exist in database
- Review tile server logs for errors

### Dependencies
Required packages for full functionality:
- `ogr2pbf` - GeoJSON to PBF conversion
- `osmium` - PBF file manipulation
- `osm2pgsql` - PostGIS import
- `martin` or `tileserver-gl` - Vector tile serving

## Examples

### Fantasy Kingdom Dataset
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Kingdom of Aethermoor",
        "place": "capital",
        "fantasy:kingdom": "Aethermoor",
        "fantasy:race": "human",
        "population": "50000"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [12.345, 67.890]
      }
    }
  ]
}
```

### Trade Route Network
```json
{
  "type": "Feature",
  "properties": {
    "name": "Great Trade Route",
    "highway": "trade_route",
    "fantasy:protected": "yes",
    "fantasy:danger": "low"
  },
  "geometry": {
    "type": "LineString",
    "coordinates": [[0, 0], [1, 1], [2, 0]]
  }
}
```

## Contributing

To extend the fantasy tag system:
1. Edit `src/fantasy/translation.py`
2. Add new mappings to the `filter_tags` method
3. Update this documentation
4. Test with sample GeoJSON data

## License

Fantasy basemap functionality is released under the same AGPL-3.0 license as Mundi.ai.

OpenGeofiction data is CC BY-NC-SA 3.0 licensed and requires attribution.