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

from fastapi import APIRouter, HTTPException, Response
from pathlib import Path
import aiofiles
import json
import os

router = APIRouter()

# Base paths for Eno vector data
ENO_VECTOR_BASE = "/app/Eno/vector"
ENO_CITIES_BASE = "/app/Eno/karttatiedostot kaupungeista"
ENO_PROJECTED_BASE = "/app/Eno/skaalatut/projisoidut"

# Define available vector layers - using re-projected data for proper coordinate alignment
VECTOR_LAYERS = {
    "rivers": {
        "path": f"{ENO_PROJECTED_BASE}/joet.geojson",
        "name": "Eno Rivers",
        "type": "LineString"
    },
    "lakes": {
        "path": f"{ENO_PROJECTED_BASE}/jarvet.geojson", 
        "name": "Eno Lakes",
        "type": "Polygon"
    },
    "biomes": {
        "path": f"{ENO_PROJECTED_BASE}/biomes.geojson",
        "name": "Eno Biomes", 
        "type": "Polygon"
    },
    "states": {
        "path": f"{ENO_VECTOR_BASE}/states.geojson",  # Keep original if no projected version
        "name": "Eno States",
        "type": "Polygon"
    },
    "cities": {
        "path": f"{ENO_PROJECTED_BASE}/kaupungit.geojson",
        "name": "Eno Cities",
        "type": "Point"
    },
    "villages": {
        "path": f"{ENO_PROJECTED_BASE}/kylat.geojson",
        "name": "Eno Villages",
        "type": "Point"
    },
    "roads": {
        "path": f"{ENO_PROJECTED_BASE}/tiet.geojson",
        "name": "Eno Roads",
        "type": "LineString"
    }
}


@router.get("/api/eno/vector")
async def list_vector_layers():
    """List available Eno vector layers."""
    available_layers = []
    
    for layer_id, layer_info in VECTOR_LAYERS.items():
        file_path = Path(layer_info["path"])
        if file_path.exists():
            available_layers.append({
                "id": layer_id,
                "name": layer_info["name"],
                "type": layer_info["type"],
                "endpoint": f"/api/eno/vector/{layer_id}"
            })
    
    return {
        "layers": available_layers,
        "total": len(available_layers)
    }


@router.get("/api/eno/vector/{layer_id}")
async def get_vector_layer(layer_id: str):
    """Get GeoJSON data for a specific Eno vector layer."""
    if layer_id not in VECTOR_LAYERS:
        raise HTTPException(status_code=404, detail=f"Layer '{layer_id}' not found")
    
    layer_info = VECTOR_LAYERS[layer_id]
    file_path = Path(layer_info["path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Data file for layer '{layer_id}' not found")
    
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Add layer metadata
        geojson_data["metadata"] = {
            "layer_id": layer_id,
            "name": layer_info["name"],
            "type": layer_info["type"]
        }
        
        return geojson_data
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid GeoJSON in {layer_id}: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading layer {layer_id}: {str(e)}")


@router.get("/api/eno/buildings/{city_name}")
async def get_city_buildings(city_name: str):
    """Get building data for a specific city."""
    # Clean and normalize city name
    clean_name = city_name.lower().replace(" ", "_")
    
    # Try different building file patterns
    possible_paths = [
        f"{ENO_CITIES_BASE}/buildings/buildings_{clean_name}.geojson_fixed.geojson_poly.geojson",
        f"{ENO_CITIES_BASE}/buildings/buildings_{clean_name}.geojson_poly.geojson"
    ]
    
    building_file = None
    for path in possible_paths:
        if Path(path).exists():
            building_file = Path(path)
            break
    
    if not building_file:
        raise HTTPException(status_code=404, detail=f"Buildings not found for city '{city_name}'")
    
    try:
        async with aiofiles.open(building_file, "r", encoding="utf-8") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Add metadata
        geojson_data["metadata"] = {
            "city": city_name,
            "type": "buildings",
            "layer_type": "Polygon"
        }
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading buildings for {city_name}: {str(e)}")


@router.get("/api/eno/castles/{city_name}")
async def get_city_castles(city_name: str):
    """Get castle data for a specific city."""
    # Clean and normalize city name
    clean_name = city_name.lower().replace(" ", "_")
    
    # Try different castle file patterns
    possible_paths = [
        f"{ENO_CITIES_BASE}/castles/castle_{clean_name}.geojson_fixed.geojson_poly.geojson",
        f"{ENO_CITIES_BASE}/castles/castle_{clean_name}.geojson_poly.geojson"
    ]
    
    castle_file = None
    for path in possible_paths:
        if Path(path).exists():
            castle_file = Path(path)
            break
    
    if not castle_file:
        raise HTTPException(status_code=404, detail=f"Castles not found for city '{city_name}'")
    
    try:
        async with aiofiles.open(castle_file, "r", encoding="utf-8") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Add metadata
        geojson_data["metadata"] = {
            "city": city_name,
            "type": "castles", 
            "layer_type": "Polygon"
        }
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading castles for {city_name}: {str(e)}")


@router.get("/api/eno/roads")
async def get_roads():
    """Get road data from GeoPackage file."""
    roads_file = Path(f"{ENO_CITIES_BASE}/Tiet/tiet.gpkg")
    
    if not roads_file.exists():
        raise HTTPException(status_code=404, detail="Roads data not found")
    
    try:
        # For GeoPackage files, we'd need to use ogr2ogr or similar to convert to GeoJSON
        # For now, return a placeholder response indicating GPKG support needed
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {
                "message": "GeoPackage support needed for roads data",
                "file_path": str(roads_file),
                "layer_type": "LineString"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading roads: {str(e)}")