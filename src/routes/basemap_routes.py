# Copyright (C) 2025 Bunting Labs, Inc.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from pathlib import Path
import aiofiles
import os

from src.database.connection import get_db
from src.database.models import CustomBasemap
from src.dependencies.session import verify_session_required, verify_session_optional, UserContext
from src.dependencies.custom_basemap import TileSource, CustomTileMapProvider


router = APIRouter()


def generate_id(length=12, prefix=""):
    """Generate a unique ID with optional prefix."""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length - len(prefix)))
    return prefix + random_part


class CreateBasemapRequest(BaseModel):
    name: str
    tile_url_template: str
    tile_format: str = "png"
    min_zoom: int = 0
    max_zoom: int = 22
    tile_size: int = 256
    attribution: str = ""
    bounds: Optional[List[float]] = None
    center: Optional[List[float]] = None
    default_zoom: Optional[int] = None
    is_public: bool = False
    metadata: Optional[dict] = None
    world_model_id: Optional[str] = None
    georeferencing_points: Optional[List[dict]] = None
    transform_matrix: Optional[List[float]] = None


class BasemapResponse(BaseModel):
    id: str
    name: str
    tile_url_template: str
    tile_format: str
    min_zoom: int
    max_zoom: int
    tile_size: int
    attribution: str
    bounds: Optional[List[float]]
    center: Optional[List[float]]
    default_zoom: Optional[int]
    is_public: bool
    metadata: Optional[dict]
    owner_uuid: str
    created_at: str
    updated_at: str
    world_model_id: Optional[str]
    georeferencing_points: Optional[List[dict]]
    transform_matrix: Optional[List[float]]


@router.post("/api/basemaps", response_model=BasemapResponse)
async def create_basemap(
    request: CreateBasemapRequest,
    user_context: UserContext = Depends(verify_session_required),
    session: AsyncSession = Depends(get_db)
):
    """Create a new custom basemap configuration."""
    basemap = CustomBasemap(
        id=generate_id(prefix="B"),
        owner_uuid=uuid.UUID(user_context.get_user_id()),
        name=request.name,
        tile_url_template=request.tile_url_template,
        tile_format=request.tile_format,
        min_zoom=request.min_zoom,
        max_zoom=request.max_zoom,
        tile_size=request.tile_size,
        attribution=request.attribution,
        bounds=request.bounds,
        center=request.center,
        default_zoom=request.default_zoom,
        is_public=request.is_public,
        metadata_json=request.metadata,
        world_model_id=request.world_model_id,
        georeferencing_points=request.georeferencing_points,
        transform_matrix=request.transform_matrix
    )
    
    session.add(basemap)
    await session.commit()
    await session.refresh(basemap)
    
    return BasemapResponse(
        id=basemap.id,
        name=basemap.name,
        tile_url_template=basemap.tile_url_template,
        tile_format=basemap.tile_format,
        min_zoom=basemap.min_zoom,
        max_zoom=basemap.max_zoom,
        tile_size=basemap.tile_size,
        attribution=basemap.attribution,
        bounds=basemap.bounds,
        center=basemap.center,
        default_zoom=basemap.default_zoom,
        is_public=basemap.is_public,
        metadata=basemap.metadata_json,
        owner_uuid=str(basemap.owner_uuid),
        created_at=basemap.created_at.isoformat(),
        updated_at=basemap.updated_at.isoformat(),
        world_model_id=basemap.world_model_id,
        georeferencing_points=basemap.georeferencing_points,
        transform_matrix=basemap.transform_matrix
    )


@router.get("/api/basemaps", response_model=List[BasemapResponse])
async def list_basemaps(
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """List available basemaps (user's own and public ones)."""
    # Build query to get user's basemaps and public basemaps
    conditions = [CustomBasemap.is_public == True]
    if user_context:
        conditions.append(CustomBasemap.owner_uuid == uuid.UUID(user_context.get_user_id()))
    
    query = select(CustomBasemap).where(or_(*conditions))
    result = await session.execute(query)
    basemaps = result.scalars().all()
    
    return [
        BasemapResponse(
            id=b.id,
            name=b.name,
            tile_url_template=b.tile_url_template,
            tile_format=b.tile_format,
            min_zoom=b.min_zoom,
            max_zoom=b.max_zoom,
            tile_size=b.tile_size,
            attribution=b.attribution,
            bounds=b.bounds,
            center=b.center,
            default_zoom=b.default_zoom,
            is_public=b.is_public,
            metadata=b.metadata_json,
            owner_uuid=str(b.owner_uuid),
            created_at=b.created_at.isoformat(),
            updated_at=b.updated_at.isoformat(),
            world_model_id=b.world_model_id,
            georeferencing_points=b.georeferencing_points,
            transform_matrix=b.transform_matrix
        )
        for b in basemaps
    ]


@router.get("/api/basemaps/{basemap_id}", response_model=BasemapResponse)
async def get_basemap(
    basemap_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific basemap by ID."""
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BasemapResponse(
        id=basemap.id,
        name=basemap.name,
        tile_url_template=basemap.tile_url_template,
        tile_format=basemap.tile_format,
        min_zoom=basemap.min_zoom,
        max_zoom=basemap.max_zoom,
        tile_size=basemap.tile_size,
        attribution=basemap.attribution,
        bounds=basemap.bounds,
        center=basemap.center,
        default_zoom=basemap.default_zoom,
        is_public=basemap.is_public,
        metadata=basemap.metadata_json,
        owner_uuid=str(basemap.owner_uuid),
        created_at=basemap.created_at.isoformat(),
        updated_at=basemap.updated_at.isoformat(),
        world_model_id=basemap.world_model_id,
        georeferencing_points=basemap.georeferencing_points,
        transform_matrix=basemap.transform_matrix
    )


@router.get("/api/basemaps/{basemap_id}/style")
async def get_basemap_style(
    basemap_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get MapLibre GL style JSON for a basemap."""
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create tile source from database model
    tile_source = TileSource(
        id=basemap.id,
        name=basemap.name,
        tile_url_template=basemap.tile_url_template,
        min_zoom=basemap.min_zoom,
        max_zoom=basemap.max_zoom,
        tile_size=basemap.tile_size,
        attribution=basemap.attribution,
        bounds=basemap.bounds,
        center=basemap.center,
        default_zoom=basemap.default_zoom
    )
    
    provider = CustomTileMapProvider(tile_source)
    style = await provider.get_base_style()
    
    return style


@router.get("/api/basemaps/{basemap_id}/data")
async def get_basemap_data(
    basemap_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get the raw GeoJSON data for a basemap."""
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extract GeoJSON path from tile_url_template
    if not basemap.tile_url_template.startswith("geojson://"):
        raise HTTPException(status_code=400, detail="Not a GeoJSON source")
    
    geojson_path = basemap.tile_url_template.replace("geojson://", "")
    geojson_file = Path(geojson_path).resolve()
    
    if not geojson_file.exists():
        raise HTTPException(status_code=404, detail="GeoJSON file not found")
    
    # Read and return the GeoJSON
    try:
        import json
        async with aiofiles.open(geojson_file, "r", encoding="utf-8") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Fix 3D coordinates if present (MapLibre expects 2D for most uses)
        if "features" in geojson_data:
            for feature in geojson_data["features"]:
                if feature.get("geometry", {}).get("type") == "Point":
                    coords = feature["geometry"].get("coordinates", [])
                    if len(coords) > 2:
                        # Keep only lon, lat (remove elevation)
                        feature["geometry"]["coordinates"] = coords[:2]
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading GeoJSON: {str(e)}")


@router.get("/api/tiles/eno-relief/{z}/{x}/{y}.png")
async def serve_eno_relief_tile(z: int, x: int, y: int):
    """Serve Eno relief tiles from tiles/eno_relief directory."""
    tile_path = Path(f"tiles/eno_relief/{z}/{x}/{y}.png").resolve()
    
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


@router.get("/api/tiles/eno-satellite-hd/{z}/{x}/{y}.png")
async def serve_eno_satellite_hd_tile(z: int, x: int, y: int):
    """Serve Eno HD satellite tiles from local generated tiles."""
    tile_path = Path(f"tiles/eno_satellite_hd/{z}/{x}/{y}.png").resolve()
    
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
        
        return Response(content=content, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")


@router.get("/api/maptiler/eno_style")
async def get_maptiler_eno_style():
    """Proxy the MapTiler Eno style with our settings."""
    import httpx
    
    maptiler_url = "https://api.maptiler.com/maps/01965e52-7535-7737-8dd6-d874aaf7d55f/style.json?key=wlMkQ9IDDyv6h7iXvze2"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(maptiler_url)
            if response.status_code == 200:
                style = response.json()
                # Override with our settings
                style["center"] = [21.92, 3.42]  # Center on Eno world
                style["zoom"] = 3
                style["bearing"] = 0
                style["pitch"] = 0
                return style
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch MapTiler style")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MapTiler style: {str(e)}")


@router.get("/api/eno/alignment_style")
async def get_alignment_test_style():
    """Get a MapLibre style that combines OpenStreetMap with Eno vector layers for alignment testing."""
    
    # Create a comprehensive style with OSM base + all Eno vector layers
    style = {
        "version": 8,
        "name": "Eno Alignment Test Style",
        "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
        "sources": {
            "osm": {
                "type": "raster",
                "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                "tileSize": 256,
                "attribution": "© OpenStreetMap contributors"
            },
            "eno-cities": {
                "type": "geojson",
                "data": "/api/eno/vector/cities"
            },
            "eno-villages": {
                "type": "geojson", 
                "data": "/api/eno/vector/villages"
            },
            "eno-rivers": {
                "type": "geojson",
                "data": "/api/eno/vector/rivers"
            },
            "eno-lakes": {
                "type": "geojson",
                "data": "/api/eno/vector/lakes"
            },
            "eno-roads": {
                "type": "geojson",
                "data": "/api/eno/vector/roads"
            },
            "eno-biomes": {
                "type": "geojson",
                "data": "/api/eno/vector/biomes"
            }
        },
        "layers": [
            {
                "id": "osm",
                "type": "raster",
                "source": "osm"
            },
            {
                "id": "eno-biomes",
                "type": "fill",
                "source": "eno-biomes",
                "paint": {
                    "fill-color": [
                        "match",
                        ["get", "biome"],
                        "Forest", "#228B22",
                        "Desert", "#D2691E", 
                        "Mountains", "#8B4513",
                        "Plains", "#9ACD32",
                        "Water", "#4682B4",
                        "#CCCCCC"
                    ],
                    "fill-opacity": 0.3
                }
            },
            {
                "id": "eno-lakes",
                "type": "fill",
                "source": "eno-lakes",
                "paint": {
                    "fill-color": "#4682B4",
                    "fill-opacity": 0.6
                }
            },
            {
                "id": "eno-rivers",
                "type": "line",
                "source": "eno-rivers",
                "paint": {
                    "line-color": "#4682B4",
                    "line-width": 2
                }
            },
            {
                "id": "eno-roads",
                "type": "line",
                "source": "eno-roads",
                "paint": {
                    "line-color": "#8B4513",
                    "line-width": 1
                }
            },
            {
                "id": "eno-villages",
                "type": "circle",
                "source": "eno-villages",
                "paint": {
                    "circle-radius": 3,
                    "circle-color": "#FFA500",
                    "circle-stroke-color": "#FFFFFF",
                    "circle-stroke-width": 1
                }
            },
            {
                "id": "eno-cities",
                "type": "circle",
                "source": "eno-cities",
                "paint": {
                    "circle-radius": [
                        "case",
                        ["==", ["get", "Burg"], "Palwede"], 12,
                        6
                    ],
                    "circle-color": [
                        "case", 
                        ["==", ["get", "Burg"], "Palwede"], "#FF0000",
                        "#0080FF"
                    ],
                    "circle-stroke-color": "#FFFFFF",
                    "circle-stroke-width": 2
                }
            },
            {
                "id": "eno-cities-labels",
                "type": "symbol",
                "source": "eno-cities",
                "layout": {
                    "text-field": ["get", "Burg"],
                    "text-font": ["Open Sans Regular"],
                    "text-size": [
                        "case",
                        ["==", ["get", "Burg"], "Palwede"], 14,
                        10
                    ],
                    "text-offset": [0, 1.5],
                    "text-anchor": "top"
                },
                "paint": {
                    "text-color": [
                        "case",
                        ["==", ["get", "Burg"], "Palwede"], "#FF0000", 
                        "#000000"
                    ],
                    "text-halo-color": "#FFFFFF",
                    "text-halo-width": 2
                }
            },
            {
                "id": "eno-villages-labels",
                "type": "symbol",
                "source": "eno-villages", 
                "layout": {
                    "text-field": ["get", "Name"],
                    "text-font": ["Open Sans Regular"],
                    "text-size": 8,
                    "text-offset": [0, 1.2],
                    "text-anchor": "top"
                },
                "paint": {
                    "text-color": "#FFA500",
                    "text-halo-color": "#FFFFFF",
                    "text-halo-width": 1
                }
            }
        ],
        "center": [51.35, 84.07],  # Center on Palwede
        "zoom": 5,
        "bearing": 0,
        "pitch": 0
    }
    
    return style


@router.get("/eno_relief_test", response_class=Response)
async def eno_relief_test():
    """Serve simple Eno relief map test page."""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Eno Relief Map Test</title>
    <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
    <script src="https://unpkg.com/maplibre-gl@4.5.2/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@4.5.2/dist/maplibre-gl.css" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        .info {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info">
        <h3>Eno Relief Map</h3>
        <p>Local tiles from tiles/eno_relief/</p>
    </div>

    <script>
        const map = new maplibregl.Map({
            container: 'map',
            style: '/api/basemaps/BBvNGnzVT0oq/style',
            center: [21.92, 3.42],
            zoom: 3
        });

        map.addControl(new maplibregl.NavigationControl());
        
        map.on('load', function() {
            console.log('Map loaded successfully');
        });
        
        map.on('error', function(e) {
            console.error('Map error:', e.error.message);
        });
    </script>
</body>
</html>'''
    
    return Response(content=html_content, media_type="text/html")


@router.get("/test_working_alignment", response_class=Response)
async def test_working_alignment():
    """Serve the working alignment test page via API endpoint."""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Working Alignment Test - Eno Cities</title>
    <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
    <script src="https://unpkg.com/maplibre-gl@4.5.2/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@4.5.2/dist/maplibre-gl.css" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        .controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            min-width: 300px;
        }
        .status {
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-top: 10px;
        }
        .status.loading { background: #fff3cd; color: #856404; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        button {
            width: 100%;
            padding: 8px;
            margin-bottom: 8px;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #007cba;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover { background: #005a8b; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="controls">
        <h3 style="margin-top: 0; color: #333;">🎯 Working Alignment Test</h3>
        
        <button onclick="centerOnPalwede()">🎯 Focus on Palwede</button>
        <button onclick="showAllCities()">🌍 Show All Cities</button>
        <button onclick="toggleCityLabels()">🏷️ Toggle Labels</button>
        <button onclick="switchToCustomBasemap()">🗺️ Switch to Custom Basemap</button>
        
        <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px; margin-top: 10px;">
            <strong>Status:</strong><br>
            • Map loads with OpenStreetMap<br>
            • Cities overlay with proper styling<br>
            • Palwede highlighted at [51.35, 84.07]<br>
            • Glyphs configured for text labels
        </div>
        
        <div id="status" class="status loading">Initializing...</div>
    </div>

    <script>
        let map;
        let citiesLoaded = false;
        let labelsVisible = true;
        let customBasemap = false;
        
        const palwedeCoords = [51.35, 84.07];
        
        function updateStatus(message, type = 'loading') {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
        }
        
        function initMap() {
            updateStatus('Loading map...', 'loading');
            
            map = new maplibregl.Map({
                container: 'map',
                style: {
                    version: 8,
                    glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
                    sources: {
                        osm: {
                            type: 'raster',
                            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                            tileSize: 256,
                            attribution: '© OpenStreetMap contributors'
                        }
                    },
                    layers: [
                        {
                            id: 'osm',
                            type: 'raster',
                            source: 'osm'
                        }
                    ]
                },
                center: palwedeCoords,
                zoom: 5
            });

            map.addControl(new maplibregl.NavigationControl());
            
            map.on('load', function() {
                updateStatus('Map loaded. Loading cities...', 'loading');
                loadCities();
            });
            
            map.on('error', function(e) {
                updateStatus('Map error: ' + e.error.message, 'error');
            });
        }
        
        function loadCities() {
            fetch('/api/basemaps/BxvFhuzMcnuy/data')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status);
                    }
                    return response.json();
                })
                .then(citiesData => {
                    updateStatus(`Cities loaded: ${citiesData.features.length} cities`, 'success');
                    
                    map.addSource('cities', {
                        type: 'geojson',
                        data: citiesData
                    });

                    map.addLayer({
                        id: 'cities',
                        type: 'circle',
                        source: 'cities',
                        paint: {
                            'circle-radius': [
                                'case',
                                ['==', ['get', 'Burg'], 'Palwede'], 12,
                                6
                            ],
                            'circle-color': [
                                'case',
                                ['==', ['get', 'Burg'], 'Palwede'], '#ff0000',
                                '#0080ff'
                            ],
                            'circle-stroke-color': '#ffffff',
                            'circle-stroke-width': 2
                        }
                    });

                    map.addLayer({
                        id: 'city-labels',
                        type: 'symbol',
                        source: 'cities',
                        layout: {
                            'text-field': ['get', 'Burg'],
                            'text-font': ['Open Sans Regular'],
                            'text-size': [
                                'case',
                                ['==', ['get', 'Burg'], 'Palwede'], 14,
                                10
                            ],
                            'text-offset': [0, 1.5],
                            'text-anchor': 'top'
                        },
                        paint: {
                            'text-color': [
                                'case',
                                ['==', ['get', 'Burg'], 'Palwede'], '#ff0000',
                                '#000000'
                            ],
                            'text-halo-color': '#ffffff',
                            'text-halo-width': 2
                        }
                    });
                    
                    citiesLoaded = true;
                    updateStatus('✅ Cities visible! Palwede highlighted in red.', 'success');
                })
                .catch(error => {
                    updateStatus('Error loading cities: ' + error.message, 'error');
                    console.error('Error loading cities:', error);
                });
        }

        function centerOnPalwede() {
            map.flyTo({
                center: palwedeCoords,
                zoom: 8,
                duration: 1000
            });
            updateStatus('Centered on Palwede [51.35, 84.07]', 'success');
        }

        function showAllCities() {
            map.flyTo({
                center: [21.92, 3.42],
                zoom: 3,
                duration: 1500
            });
            updateStatus('Showing all cities', 'success');
        }

        function toggleCityLabels() {
            labelsVisible = !labelsVisible;
            const visibility = labelsVisible ? 'visible' : 'none';
            
            if (map.getLayer('city-labels')) {
                map.setLayoutProperty('city-labels', 'visibility', visibility);
            }
            updateStatus('Labels ' + (labelsVisible ? 'shown' : 'hidden'), 'success');
        }
        
        function switchToCustomBasemap() {
            if (customBasemap) {
                updateStatus('Already using custom basemap', 'success');
                return;
            }
            
            updateStatus('Switching to custom basemap...', 'loading');
            
            fetch('/api/basemaps/BSGhO6eBzkRB/style')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status);
                    }
                    return response.json();
                })
                .then(style => {
                    const citiesSource = map.getSource('cities');
                    const citiesData = citiesSource ? citiesSource._data : null;
                    
                    map.setStyle(style);
                    
                    map.once('styledata', function() {
                        if (citiesData) {
                            setTimeout(() => {
                                loadCitiesOnCustomStyle(citiesData);
                            }, 500);
                        }
                    });
                    
                    customBasemap = true;
                    updateStatus('Switched to custom relief basemap', 'success');
                })
                .catch(error => {
                    updateStatus('Failed to switch basemap: ' + error.message, 'error');
                    console.error('Error switching basemap:', error);
                });
        }
        
        function loadCitiesOnCustomStyle(citiesData) {
            try {
                map.addSource('cities-overlay', {
                    type: 'geojson',
                    data: citiesData
                });

                map.addLayer({
                    id: 'cities-overlay',
                    type: 'circle',
                    source: 'cities-overlay',
                    paint: {
                        'circle-radius': [
                            'case',
                            ['==', ['get', 'Burg'], 'Palwede'], 12,
                            6
                        ],
                        'circle-color': [
                            'case',
                            ['==', ['get', 'Burg'], 'Palwede'], '#ff0000',
                            '#0080ff'
                        ],
                        'circle-stroke-color': '#ffffff',
                        'circle-stroke-width': 2
                    }
                });

                map.addLayer({
                    id: 'cities-overlay-labels',
                    type: 'symbol',
                    source: 'cities-overlay',
                    layout: {
                        'text-field': ['get', 'Burg'],
                        'text-font': ['Open Sans Regular'],
                        'text-size': [
                            'case',
                            ['==', ['get', 'Burg'], 'Palwede'], 14,
                            10
                        ],
                        'text-offset': [0, 1.5],
                        'text-anchor': 'top'
                    },
                    paint: {
                        'text-color': [
                            'case',
                            ['==', ['get', 'Burg'], 'Palwede'], '#ff0000',
                            '#000000'
                        ],
                        'text-halo-color': '#ffffff',
                        'text-halo-width': 2
                    }
                });
                
                updateStatus('✅ Custom basemap with cities overlay loaded!', 'success');
            } catch (error) {
                updateStatus('Error adding cities to custom style: ' + error.message, 'error');
                console.error('Error adding cities overlay:', error);
            }
        }

        initMap();
    </script>
</body>
</html>'''
    
    return Response(content=html_content, media_type="text/html")


@router.get("/api/tiles/eno-satellite-new/{z}/{x}/{y}.png")
async def serve_eno_satellite_new_tile(z: int, x: int, y: int):
    """Serve new Eno satellite tiles generated with --profile=raster."""
    # Force use of new satellite tiles  
    tile_path = Path(f"tiles/satellite/tiles/{z}/{x}/{y}.png").resolve()
    
    # Only fallback if new tiles don't exist
    if not tile_path.exists():
        tile_path = Path(f"tiles/eno_satellite_hd/{z}/{x}/{y}.png").resolve()
    
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
        
        return Response(content=content, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")


@router.get("/api/tiles/eno-relief-new/{z}/{x}/{y}.png")
async def serve_eno_relief_new_tile(z: int, x: int, y: int):
    """Serve new Eno relief tiles generated with --profile=raster."""
    # Force use of new relief tiles
    tile_path = Path(f"tiles/relief/tiles2/{z}/{x}/{y}.png").resolve()
    
    # Only fallback if new tiles don't exist
    if not tile_path.exists():
        tile_path = Path(f"tiles/eno_relief/{z}/{x}/{y}.png").resolve()
    
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
        
        return Response(content=content, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")


@router.get("/test_eno_alignment.html")
async def serve_alignment_test():
    """Serve the alignment test HTML page."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Eno Fantasy Map - Alignment Test</title>
    <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
    <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
    <style>
        body { 
            margin: 0; 
            padding: 0; 
        }
        #map { 
            position: absolute; 
            top: 0; 
            bottom: 0; 
            width: 100%; 
        }
        .controls {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            z-index: 1000;
        }
        .control-group {
            margin-bottom: 10px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        select, button {
            width: 200px;
            padding: 5px;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="controls">
        <div class="control-group">
            <label for="basemap-select">Basemap:</label>
            <select id="basemap-select">
                <option value="satellite">Satellite (New)</option>
                <option value="relief">Relief (New)</option>
                <option value="none">No Basemap</option>
            </select>
        </div>
        <div class="control-group">
            <label>
                <input type="checkbox" id="show-cities" checked> Show Cities
            </label>
            <label>
                <input type="checkbox" id="show-alignment" checked> Show Alignment Points
            </label>
        </div>
        <div class="control-group">
            <button onclick="zoomToAlignment()">Zoom to Alignment Points</button>
            <button onclick="zoomToCenter()">Zoom to Center</button>
        </div>
        <div class="control-group">
            <small>
                <div>Vector Bounds: [-71.78, -80.09, 115.62, 86.93]</div>
                <div>Vector Center: [21.92, 3.42]</div>
                <div>Size: 187.4 × 167.0 degrees</div>
            </small>
        </div>
    </div>

    <div id="map"></div>

    <script>
        // Eno fantasy world configuration - using actual vector data bounds
        const ENO_BOUNDS = [-71.78, -80.09, 115.62, 86.93];
        const ENO_CENTER = [21.92, 3.42];  // Matches actual vector data center
        const ALIGNMENT_POINTS = [
            { name: 'Upperleft', coordinates: [-73.312, 98.423] },
            { name: 'Upperright', coordinates: [117.287, 98.423] },
            { name: 'Lowerleft', coordinates: [-73.312, -92.897] },
            { name: 'Lowerright', coordinates: [117.287, -92.897] },
            { name: 'center', coordinates: [21.988, 2.763] }  // Corrected center
        ];

        // Initialize map with Eno bounds and center
        const map = new maplibregl.Map({
            container: 'map',
            style: {
                version: 8,
                sources: {},
                layers: []
            },
            center: ENO_CENTER,
            zoom: 3,
            maxBounds: [
                [ENO_BOUNDS[0] - 10, ENO_BOUNDS[1] - 10], // Southwest coordinates
                [ENO_BOUNDS[2] + 10, ENO_BOUNDS[3] + 10]  // Northeast coordinates
            ]
        });

        // Basemap configurations
        const basemapConfigs = {
            satellite: {
                source: {
                    type: 'raster',
                    tiles: ['/api/tiles/eno-satellite-new/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    minzoom: 0,
                    maxzoom: 8,
                    bounds: ENO_BOUNDS
                },
                layer: {
                    id: 'satellite-tiles',
                    type: 'raster',
                    source: 'satellite-source'
                }
            },
            relief: {
                source: {
                    type: 'raster',
                    tiles: ['/api/tiles/eno-relief-new/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    minzoom: 0,
                    maxzoom: 8,
                    bounds: ENO_BOUNDS
                },
                layer: {
                    id: 'relief-tiles',
                    type: 'raster',
                    source: 'relief-source'
                }
            }
        };

        // Cities data source - fix CORS and make it work
        const citiesSource = {
            type: 'geojson',
            data: '/api/vector/citystateswithalighmentpoints.geojson'
        };

        // Add sources and layers to map
        map.on('load', () => {
            // Add cities source
            map.addSource('cities-source', citiesSource);

            // Add basemap sources
            map.addSource('satellite-source', basemapConfigs.satellite.source);
            map.addSource('relief-source', basemapConfigs.relief.source);

            // Add satellite layer (start with this)
            map.addLayer(basemapConfigs.satellite.layer);

            // Add cities layer
            map.addLayer({
                id: 'cities',
                type: 'circle',
                source: 'cities-source',
                filter: ['!=', ['get', 'Burg'], 'Upperleft'],
                paint: {
                    'circle-radius': 6,
                    'circle-color': '#ff6b6b',
                    'circle-stroke-color': '#ffffff',
                    'circle-stroke-width': 2
                }
            });

            // Add city labels
            map.addLayer({
                id: 'city-labels',
                type: 'symbol',
                source: 'cities-source',
                filter: ['!=', ['get', 'Burg'], 'Upperleft'],
                layout: {
                    'text-field': ['get', 'Burg'],
                    'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
                    'text-offset': [0, 1.5],
                    'text-anchor': 'top',
                    'text-size': 12
                },
                paint: {
                    'text-color': '#ffffff',
                    'text-halo-color': '#000000',
                    'text-halo-width': 2
                }
            });

            // Add alignment points layer
            map.addLayer({
                id: 'alignment-points',
                type: 'circle',
                source: 'cities-source',
                filter: ['in', ['get', 'Burg'], ['literal', ['Upperleft', 'Upperright', 'Lowerleft', 'Lowerright', 'center']]],
                paint: {
                    'circle-radius': 8,
                    'circle-color': '#4ecdc4',
                    'circle-stroke-color': '#ffffff',
                    'circle-stroke-width': 3
                }
            });

            // Add alignment point labels
            map.addLayer({
                id: 'alignment-labels',
                type: 'symbol',
                source: 'cities-source',
                filter: ['in', ['get', 'Burg'], ['literal', ['Upperleft', 'Upperright', 'Lowerleft', 'Lowerright', 'center']]],
                layout: {
                    'text-field': ['get', 'Burg'],
                    'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
                    'text-offset': [0, -2],
                    'text-anchor': 'bottom',
                    'text-size': 14
                },
                paint: {
                    'text-color': '#4ecdc4',
                    'text-halo-color': '#ffffff',
                    'text-halo-width': 2
                }
            });

            console.log('Map loaded with Eno fantasy world configuration');
        });

        // Basemap switching
        document.getElementById('basemap-select').addEventListener('change', (e) => {
            const selectedBasemap = e.target.value;
            
            // Hide all basemap layers
            ['satellite-tiles', 'relief-tiles'].forEach(layerId => {
                if (map.getLayer(layerId)) {
                    map.setLayoutProperty(layerId, 'visibility', 'none');
                }
            });

            // Show selected basemap
            if (selectedBasemap !== 'none') {
                const layerId = basemapConfigs[selectedBasemap].layer.id;
                if (!map.getLayer(layerId)) {
                    map.addLayer(basemapConfigs[selectedBasemap].layer);
                }
                map.setLayoutProperty(layerId, 'visibility', 'visible');
            }
        });

        // Layer toggles
        document.getElementById('show-cities').addEventListener('change', (e) => {
            const visibility = e.target.checked ? 'visible' : 'none';
            map.setLayoutProperty('cities', 'visibility', visibility);
            map.setLayoutProperty('city-labels', 'visibility', visibility);
        });

        document.getElementById('show-alignment').addEventListener('change', (e) => {
            const visibility = e.target.checked ? 'visible' : 'none';
            map.setLayoutProperty('alignment-points', 'visibility', visibility);
            map.setLayoutProperty('alignment-labels', 'visibility', visibility);
        });

        // Navigation functions
        function zoomToAlignment() {
            map.fitBounds(ENO_BOUNDS, { padding: 50 });
        }

        function zoomToCenter() {
            map.flyTo({
                center: ENO_CENTER,
                zoom: 5,
                duration: 1000
            });
        }

        // Add click handlers for debugging
        map.on('click', (e) => {
            console.log('Clicked at:', e.lngLat.toArray());
        });

        // Add popup for features
        map.on('click', ['cities', 'alignment-points'], (e) => {
            if (e.features.length > 0) {
                const feature = e.features[0];
                const props = feature.properties;
                
                let content = `<h3>${props.Burg}</h3>`;
                if (props.Population) {
                    content += `<p><strong>Population:</strong> ${props.Population}</p>`;
                }
                if (props.State) {
                    content += `<p><strong>State:</strong> ${props.State}</p>`;
                }
                content += `<p><strong>Coordinates:</strong> [${e.lngLat.lng.toFixed(3)}, ${e.lngLat.lat.toFixed(3)}]</p>`;
                
                new maplibregl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(content)
                    .addTo(map);
            }
        });

        // Change cursor on hover
        map.on('mouseenter', ['cities', 'alignment-points'], () => {
            map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseleave', ['cities', 'alignment-points'], () => {
            map.getCanvas().style.cursor = '';
        });
    </script>
</body>
</html>"""
    return Response(content=html_content, media_type="text/html")


@router.get("/api/vector/{layer_name}.geojson")
async def serve_vector_layer(layer_name: str):
    """Serve vector layers as GeoJSON."""
    vector_path = Path(f"tiles/vector/{layer_name}.geojson").resolve()
    
    if not vector_path.exists():
        raise HTTPException(status_code=404, detail="Vector layer not found")
    
    # Security check - ensure path is within tiles directory
    tiles_dir = Path("tiles").resolve()
    if not str(vector_path).startswith(str(tiles_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read and return the GeoJSON
    try:
        async with aiofiles.open(vector_path, "r", encoding="utf-8") as f:
            content = await f.read()
        
        return Response(content=content, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading vector layer: {str(e)}")


@router.get("/api/tiles/local/{basemap_id}/{z}/{x}/{y}.{format}")
async def serve_local_tile(
    basemap_id: str,
    z: int,
    x: int,
    y: int,
    format: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Serve tiles from local filesystem for custom basemaps."""
    # Get basemap configuration
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extract local path from tile_url_template
    if not basemap.tile_url_template.startswith("file://"):
        raise HTTPException(status_code=400, detail="Not a local tile source")
    
    local_path = basemap.tile_url_template.replace("file://", "")
    
    # Handle single image files (for previews)
    if not ("{z}" in local_path and "{x}" in local_path and "{y}" in local_path):
        # Single image file - serve it for all tile requests
        tile_file = Path(local_path).resolve()
    else:
        # Standard XYZ tile structure
        tile_path = local_path.replace("{z}", str(z)).replace("{x}", str(x)).replace("{y}", str(y))
        tile_file = Path(tile_path).resolve()
    
    if not tile_file.exists():
        raise HTTPException(status_code=404, detail="Tile not found")
    
    # Determine content type
    content_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp"
    }
    content_type = content_types.get(format, "application/octet-stream")
    
    # Read and return tile
    async with aiofiles.open(tile_file, "rb") as f:
        content = await f.read()
    
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.delete("/api/basemaps/{basemap_id}")
async def delete_basemap(
    basemap_id: str,
    user_context: UserContext = Depends(verify_session_required),
    session: AsyncSession = Depends(get_db)
):
    """Delete a custom basemap."""
    query = select(CustomBasemap).where(
        and_(
            CustomBasemap.id == basemap_id,
            CustomBasemap.owner_uuid == uuid.UUID(user_context.get_user_id())
        )
    )
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found or access denied")
    
    await session.delete(basemap)
    await session.commit()
    
    return {"status": "success", "message": "Basemap deleted"}


@router.get("/api/basemaps/{basemap_id}/vector/{z}/{x}/{y}.json")
async def serve_vector_tile(
    basemap_id: str,
    z: int,
    x: int,
    y: int,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Serve vector tiles (GeoJSON) for custom basemaps."""
    # Get basemap configuration
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extract GeoJSON path from tile_url_template
    if not basemap.tile_url_template.startswith("geojson://"):
        raise HTTPException(status_code=400, detail="Not a vector tile source")
    
    geojson_path = basemap.tile_url_template.replace("geojson://", "")
    geojson_file = Path(geojson_path).resolve()
    
    if not geojson_file.exists():
        raise HTTPException(status_code=404, detail="Vector data not found")
    
    # For simplicity, return the entire GeoJSON for now
    # In production, you'd want to implement proper vector tile clipping
    try:
        import json
        async with aiofiles.open(geojson_file, "r") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Simple bounding box filter based on tile coordinates
        # This is a basic implementation - production would use proper tile math
        from math import pow, atan, sinh, pi
        
        n = pow(2, z)
        lon_min = x / n * 360.0 - 180.0
        lon_max = (x + 1) / n * 360.0 - 180.0
        lat_max = atan(sinh(pi * (1 - 2 * y / n))) * 180.0 / pi
        lat_min = atan(sinh(pi * (1 - 2 * (y + 1) / n))) * 180.0 / pi
        
        # Filter features within tile bounds
        filtered_features = []
        for feature in geojson_data.get("features", []):
            if feature.get("geometry", {}).get("type") == "Point":
                coords = feature["geometry"]["coordinates"]
                if lon_min <= coords[0] <= lon_max and lat_min <= coords[1] <= lat_max:
                    filtered_features.append(feature)
        
        # Return filtered GeoJSON
        return {
            "type": "FeatureCollection",
            "features": filtered_features
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing vector data: {str(e)}")


@router.get("/test_aligned_basemaps.html")
async def serve_aligned_basemaps_test():
    """Serve the aligned basemaps test HTML page."""
    try:
        async with aiofiles.open("test_aligned_basemaps.html", "r", encoding="utf-8") as f:
            html_content = await f.read()
        return Response(content=html_content, media_type="text/html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading test page: {str(e)}")


@router.get("/test_single_city_alignment.html")
async def serve_single_city_alignment_test():
    """Serve the single city alignment test HTML page."""
    try:
        async with aiofiles.open("test_single_city_alignment.html", "r", encoding="utf-8") as f:
            html_content = await f.read()
        return Response(content=html_content, media_type="text/html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading test page: {str(e)}")


@router.get("/api/tiles/epsg3857-relief/{z}/{x}/{y}.png")
async def serve_epsg3857_relief_tile(z: int, x: int, y: int):
    """Serve EPSG:3857 projected relief tiles."""
    tile_path = Path(f"tiles/epsg3857_relief/{z}/{x}/{y}.png").resolve()
    
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
        
        return Response(content=content, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")


@router.get("/api/tiles/epsg3857-satellite/{z}/{x}/{y}.png")
async def serve_epsg3857_satellite_tile(z: int, x: int, y: int):
    """Serve EPSG:3857 projected satellite tiles."""
    tile_path = Path(f"tiles/epsg3857_satellite/{z}/{x}/{y}.png").resolve()
    
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
        
        return Response(content=content, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")


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


@router.get("/api/tiles/eno-satellite-fixed/{z}/{x}/{y}.png")
async def serve_eno_satellite_fixed_tile(z: int, x: int, y: int):
    """Serve fixed Eno satellite tiles from tiles/eno_satellite_fixed directory."""
    tile_path = Path(f"tiles/eno_satellite_fixed/{z}/{x}/{y}.png").resolve()
    
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


@router.get("/api/cities.geojson")
async def get_cities_geojson():
    """Get cities GeoJSON data directly for alignment testing."""
    geojson_path = Path("Eno/karttatiedostot kaupungeista/kaupunkiensijainti.geojson").resolve()
    
    if not geojson_path.exists():
        # Try Docker path
        geojson_path = Path("/app/Eno/karttatiedostot kaupungeista/kaupunkiensijainti.geojson").resolve()
    
    if not geojson_path.exists():
        raise HTTPException(status_code=404, detail="Cities GeoJSON file not found")
    
    try:
        import json
        async with aiofiles.open(geojson_path, "r", encoding="utf-8") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Fix 3D coordinates if present (MapLibre expects 2D for most uses)
        if "features" in geojson_data:
            for feature in geojson_data["features"]:
                if feature.get("geometry", {}).get("type") == "Point":
                    coords = feature["geometry"].get("coordinates", [])
                    if len(coords) > 2:
                        # Keep only lon, lat (remove elevation)
                        feature["geometry"]["coordinates"] = coords[:2]
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading GeoJSON: {str(e)}")

@router.get("/debug_map_test")
async def serve_debug_map_test():
    """Serve a simple map debug test page."""
    html_content = """<\!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Debug Map Test</title>
    <script src="https://unpkg.com/maplibre-gl@4.5.2/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@4.5.2/dist/maplibre-gl.css" rel="stylesheet">
</head>
<body>
    <div id="map" style="width: 100%; height: 100vh;"></div>
    <div style="position: absolute; top: 10px; left: 10px; background: white; padding: 10px; font-family: monospace; font-size: 12px;">
        <div id="debug">Testing map...</div>
    </div>
    <script>
        const map = new maplibregl.Map({
            container: "map",
            style: {
                version: 8,
                sources: {
                    osm: {
                        type: "raster",
                        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                        tileSize: 256
                    }
                },
                layers: [{
                    id: "osm",
                    type: "raster", 
                    source: "osm"
                }]
            },
            center: [0, 0],
            zoom: 2
        });
        map.on("load", () => {
            document.getElementById("debug").innerHTML = "✅ Map loaded successfully\!";
        });
        map.on("error", (e) => {
            document.getElementById("debug").innerHTML = "❌ Error: " + e.error.message;
        });
    </script>
</body>
</html>"""
    return Response(content=html_content, media_type="text/html")


@router.get("/tiles/eno_relief/{z}/{x}/{y}.png")
async def serve_eno_relief_tile_static(z: int, x: int, y: int):
    """Serve relief tiles with proper PNG MIME type."""
    tile_path = Path(f"tiles/eno_relief/{z}/{x}/{y}.png").resolve()
    
    if not tile_path.exists():
        raise HTTPException(status_code=404, detail="Tile not found")
    
    # Security check - ensure path is within tiles directory
    tiles_dir = Path("tiles").resolve()
    if not str(tile_path).startswith(str(tiles_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        async with aiofiles.open(tile_path, "rb") as f:
            content = await f.read()
        
        return Response(
            content=content, 
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tile: {str(e)}")

