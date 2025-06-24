#!/usr/bin/env python3
"""Test script to create vector basemap with Docker-accessible paths."""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_vector_basemap_docker():
    """Create a vector basemap with Docker-accessible path."""
    basemap_data = {
        "name": "Eno Cities Vector - Docker",
        "tile_url_template": "geojson:///app/Eno/karttatiedostot kaupungeista/kaupunkiensijainti.geojson",
        "tile_format": "json",
        "min_zoom": 0,
        "max_zoom": 18,
        "tile_size": 256,
        "attribution": "© Eno Fantasy World Cities",
        "bounds": [-73.312, -92.897, 117.287, 98.423],
        "center": [21.9875, 2.763],
        "default_zoom": 3,
        "is_public": True,
        "metadata": {
            "type": "vector",
            "source": "Eno Cities GeoJSON",
            "feature_count": 141,
            "docker_path": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/basemaps", json=basemap_data)
    
    if response.status_code == 200:
        basemap = response.json()
        print(f"✅ Created vector basemap: {basemap['id']}")
        return basemap['id']
    else:
        print(f"❌ Failed to create basemap: {response.status_code}")
        print(response.text)
        return None

def test_vector_tile(basemap_id):
    """Test vector tile endpoint."""
    # Test different zoom levels
    test_tiles = [
        (0, 0, 0),  # Whole world
        (1, 1, 0),  # NE quadrant
        (2, 2, 1),  # More zoomed in
        (3, 4, 3),  # Even more detail
    ]
    
    for z, x, y in test_tiles:
        tile_url = f"{BASE_URL}/api/basemaps/{basemap_id}/vector/{z}/{x}/{y}.json"
        response = requests.get(tile_url)
        
        if response.status_code == 200:
            data = response.json()
            feature_count = len(data.get('features', []))
            print(f"✅ Tile z={z} x={x} y={y}: {feature_count} features")
            
            # Show first few cities at this zoom level
            for i, feature in enumerate(data.get('features', [])[:3]):
                props = feature.get('properties', {})
                print(f"   - {props.get('Burg')} (Pop: {props.get('Population')})")
        else:
            print(f"❌ Failed z={z} x={x} y={y}: {response.status_code}")
            print(f"   {response.text}")

def main():
    print("🗺️  Testing Vector Basemap with Docker Paths")
    print("=" * 50)
    
    # Create vector basemap
    basemap_id = create_vector_basemap_docker()
    
    if basemap_id:
        print(f"\n📍 Testing vector tiles for basemap {basemap_id}...")
        test_vector_tile(basemap_id)
        
        print(f"\n💡 To visualize this vector basemap:")
        print(f"   1. The frontend needs MapLibre GL JS vector support")
        print(f"   2. Or convert to raster tiles using tippecanoe")
        print(f"   3. Vector URL pattern: /api/basemaps/{basemap_id}/vector/{{z}}/{{x}}/{{y}}.json")

if __name__ == "__main__":
    main()