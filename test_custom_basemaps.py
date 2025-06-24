#!/usr/bin/env python3
"""Test script for custom basemap functionality."""

import asyncio
import httpx
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_USER_UUID = "00000000-0000-0000-0000-000000000001"

async def test_custom_basemaps():
    """Test the custom basemap API endpoints."""
    
    async with httpx.AsyncClient() as client:
        # Set auth headers
        headers = {
            "X-User-UUID": TEST_USER_UUID,
            "Content-Type": "application/json"
        }
        
        print("1. Testing basemap creation...")
        
        # Create a test basemap
        basemap_data = {
            "name": "Test Fantasy World Map",
            "tile_url_template": "https://example.com/tiles/{z}/{x}/{y}.png",
            "tile_format": "png",
            "min_zoom": 0,
            "max_zoom": 18,
            "tile_size": 256,
            "attribution": "© Test Fantasy World",
            "bounds": [-180, -90, 180, 90],
            "center": [0, 0],
            "default_zoom": 2,
            "is_public": True,
            "metadata": {
                "world_name": "Test World",
                "created_by": "Test Script"
            }
        }
        
        response = await client.post(
            f"{BASE_URL}/api/basemaps",
            headers=headers,
            json=basemap_data
        )
        
        if response.status_code == 200:
            created_basemap = response.json()
            basemap_id = created_basemap["id"]
            print(f"✅ Created basemap: {basemap_id}")
            print(f"   Name: {created_basemap['name']}")
        else:
            print(f"❌ Failed to create basemap: {response.status_code}")
            print(response.text)
            return
        
        print("\n2. Testing basemap listing...")
        
        response = await client.get(
            f"{BASE_URL}/api/basemaps",
            headers=headers
        )
        
        if response.status_code == 200:
            basemaps = response.json()
            print(f"✅ Found {len(basemaps)} basemap(s)")
            for bm in basemaps:
                print(f"   - {bm['name']} (ID: {bm['id']}, Public: {bm['is_public']})")
        else:
            print(f"❌ Failed to list basemaps: {response.status_code}")
        
        print("\n3. Testing basemap style generation...")
        
        response = await client.get(
            f"{BASE_URL}/api/basemaps/{basemap_id}/style",
            headers=headers
        )
        
        if response.status_code == 200:
            style = response.json()
            print(f"✅ Generated MapLibre GL style")
            print(f"   Sources: {list(style.get('sources', {}).keys())}")
            print(f"   Layers: {len(style.get('layers', []))}")
            print(f"   Center: {style.get('center')}")
            print(f"   Zoom: {style.get('zoom')}")
        else:
            print(f"❌ Failed to get style: {response.status_code}")
        
        print("\n4. Testing local file basemap...")
        
        # Create a basemap pointing to local Eno data
        local_basemap_data = {
            "name": "Eno Fantasy World Grid",
            "tile_url_template": "file:///root/Eno/Mundi/mundi.ai/Eno/rasterikartta/{z}/{x}/{y}.jpg",
            "tile_format": "jpg",
            "min_zoom": 0,
            "max_zoom": 4,
            "tile_size": 256,
            "attribution": "© Eno Fantasy World",
            "is_public": False,
            "metadata": {
                "source": "Eno dataset",
                "type": "grid_map"
            }
        }
        
        response = await client.post(
            f"{BASE_URL}/api/basemaps",
            headers=headers,
            json=local_basemap_data
        )
        
        if response.status_code == 200:
            local_basemap = response.json()
            print(f"✅ Created local file basemap: {local_basemap['id']}")
            
            # Test the style for local basemap
            response = await client.get(
                f"{BASE_URL}/api/basemaps/{local_basemap['id']}/style",
                headers=headers
            )
            
            if response.status_code == 200:
                local_style = response.json()
                tile_url = local_style['sources'][local_basemap['id']]['tiles'][0]
                print(f"   Local tile URL pattern: {tile_url}")
        else:
            print(f"❌ Failed to create local basemap: {response.status_code}")
            print(response.text)
        
        print("\n5. Testing basemap deletion...")
        
        response = await client.delete(
            f"{BASE_URL}/api/basemaps/{basemap_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Deleted test basemap")
        else:
            print(f"❌ Failed to delete basemap: {response.status_code}")
        
        print("\n✅ Custom basemap tests completed!")


async def test_fantasy_data_import():
    """Test importing fantasy world data."""
    print("\n6. Testing fantasy data import...")
    
    from src.util.fantasy_data_importer import import_fantasy_world_data
    
    try:
        result = await import_fantasy_world_data(TEST_USER_UUID)
        print("\n✅ Fantasy data import completed!")
        print(f"   Cities imported: {result['cities_info']['count'] if result['cities_info'] else 0}")
        print(f"   Grid basemap ID: {result['grid_basemap_id']}")
        print(f"   Relief basemap ID: {result['relief_basemap_id']}")
    except Exception as e:
        print(f"❌ Import failed: {e}")


async def main():
    """Run all tests."""
    print("🧪 Testing Custom Basemap Functionality\n")
    
    # Test API endpoints
    await test_custom_basemaps()
    
    # Test data import
    await test_fantasy_data_import()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())