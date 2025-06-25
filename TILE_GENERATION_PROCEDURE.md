# Tile Generation Procedure for Eno Fantasy World

This document describes the working procedure for generating properly aligned Web Mercator tiles from EPSG:3857 projected images.

## Prerequisites
- Source images must be in EPSG:3857 (Web Mercator) projection
- GDAL tools installed (specifically `gdal2tiles.py`)
- Docker environment for serving tiles

## Working Procedure

### 1. Generate Tiles
Use the system GDAL installation to generate XYZ tiles:

```bash
# For relief map
/usr/bin/gdal2tiles.py --xyz --profile=mercator --zoom=0-8 "./Eno/skaalatut/projisoidut/reliefi.tif" tiles/eno_relief_fixed/

# For satellite map
/usr/bin/gdal2tiles.py --xyz --profile=mercator --zoom=0-8 "./Eno/skaalatut/projisoidut/satellite.tif" tiles/eno_satellite_fixed/
```

**Important parameters:**
- `--xyz`: Use XYZ tile naming scheme (required for Web Mercator)
- `--profile=mercator`: Use Web Mercator profile
- `--zoom=0-8`: Generate zoom levels 0 through 8

### 2. Add Tile Serving Endpoint
Add endpoint to `src/routes/basemap_routes.py`:

```python
@router.get("/api/tiles/eno-relief-fixed/{z}/{x}/{y}.png")
async def serve_eno_relief_fixed_tile(z: int, x: int, y: int):
    """Serve fixed Eno relief tiles from tiles/eno_relief_fixed directory."""
    tile_path = Path(f"tiles/eno_relief_fixed/{z}/{x}/{y}.png").resolve()
    
    if not tile_path.exists():
        raise HTTPException(status_code=404, detail="Tile not found")
    
    # Security check - ensure path is within tiles directory
    tiles_dir = Path("tiles").resolve()
    if not str(tile_path).startswith(str(tiles_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read and return the tile
    try:
        async with aiofiles.open(tile_path, "rb") as f:
            content = await f.read()
        
        return Response(content=content, media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")
```

### 3. Copy Tiles to Docker Container
```bash
docker cp tiles/eno_relief_fixed mundi-app:/app/tiles/
docker cp tiles/eno_satellite_fixed mundi-app:/app/tiles/
```

### 4. Create Basemap Entry
```bash
# Relief map
curl -X POST "http://localhost:8000/api/basemaps" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eno Relief Map (Web Mercator Fixed)",
    "tile_url_template": "http://localhost:8000/api/tiles/eno-relief-fixed/{z}/{x}/{y}.png",
    "tile_format": "png",
    "min_zoom": 0,
    "max_zoom": 8,
    "tile_size": 256,
    "attribution": "Eno Fantasy World - EPSG:3857",
    "center": [0.0, 0.0],
    "default_zoom": 1,
    "is_public": true
  }'

# Satellite map
curl -X POST "http://localhost:8000/api/basemaps" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eno Satellite Map (Web Mercator Fixed)",
    "tile_url_template": "http://localhost:8000/api/tiles/eno-satellite-fixed/{z}/{x}/{y}.png",
    "tile_format": "png",
    "min_zoom": 0,
    "max_zoom": 8,
    "tile_size": 256,
    "attribution": "Eno Fantasy World Satellite - EPSG:3857",
    "center": [0.0, 0.0],
    "default_zoom": 1,
    "is_public": true
  }'
```

### 5. Verify
Test tiles are serving correctly:
```bash
curl -s "http://localhost:8000/api/tiles/eno-relief-fixed/2/2/1.png" | file -
# Should output: PNG image data, 256 x 256, 8-bit/color RGBA, non-interlaced
```

## Key Points
- Input images MUST be in EPSG:3857 projection
- Use system GDAL (`/usr/bin/gdal2tiles.py`) not conda GDAL
- Always use `--xyz --profile=mercator` flags
- Tiles must be copied to Docker container
- Endpoints must return proper PNG MIME type
- Add caching headers for performance

## Troubleshooting
- If tiles return 404, check the exact tile path exists
- If tiles show misalignment, verify source image is EPSG:3857
- If MIME type errors occur, ensure Response uses `media_type="image/png"`