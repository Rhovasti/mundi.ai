#!/usr/bin/env python3
"""Test script to create and verify vector basemap functionality."""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_vector_basemap():
    """Create a vector basemap for Eno cities."""
    basemap_data = {
        "name": "Eno Cities Vector Layer",
        "tile_url_template": "geojson:///root/Eno/Mundi/mundi.ai/Eno/karttatiedostot kaupungeista/kaupunkiensijainti.geojson",
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
            "properties": ["Population", "Walls", "Port", "Citadel", "Temple"]
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
    # Test tile at zoom 2, covering most of the world
    tile_url = f"{BASE_URL}/api/basemaps/{basemap_id}/vector/2/2/1.json"
    
    response = requests.get(tile_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Vector tile retrieved successfully")
        print(f"   - Feature count: {len(data.get('features', []))}")
        
        # Print first few cities
        for i, feature in enumerate(data.get('features', [])[:5]):
            props = feature.get('properties', {})
            print(f"   - City {i+1}: {props.get('Burg')} (Pop: {props.get('Population')})")
    else:
        print(f"❌ Failed to get vector tile: {response.status_code}")
        print(response.text)

def create_vector_style_basemap():
    """Create a MapLibre style that uses vector tiles."""
    # This would be a more complex basemap that references vector tiles
    style_data = {
        "name": "Eno Cities Vector Style",
        "tile_url_template": "http://localhost:8000/api/basemaps/{basemap_id}/vector/{z}/{x}/{y}.json",
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
            "type": "vector-style",
            "note": "This would need frontend support for vector rendering"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/basemaps", json=style_data)
    
    if response.status_code == 200:
        basemap = response.json()
        print(f"✅ Created vector style basemap: {basemap['id']}")
        return basemap['id']
    else:
        print(f"❌ Failed to create style basemap: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🗺️  Testing Vector Basemap Support")
    print("=" * 50)
    
    # Create vector basemap
    basemap_id = create_vector_basemap()
    
    if basemap_id:
        print("\n📍 Testing vector tile retrieval...")
        test_vector_tile(basemap_id)
        
        print("\n🎨 Creating vector style basemap...")
        create_vector_style_basemap()
    
    print("\n✅ Vector basemap test complete!")
    print("\nNote: Full vector tile support would require:")
    print("  - Frontend MapLibre GL JS configuration for vector layers")
    print("  - Proper vector tile generation (MVT format)")
    print("  - Style configuration for rendering features")

if __name__ == "__main__":
    main()