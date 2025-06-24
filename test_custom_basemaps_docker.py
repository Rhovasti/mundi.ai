#!/usr/bin/env python3
"""Test script for custom basemap functionality - runs via Docker."""

import subprocess
import json
import sys

def run_docker_test():
    """Run the test inside the Docker container where the environment is set up."""
    
    print("🧪 Testing Custom Basemap Functionality via Docker\n")
    
    # Test 1: List basemaps
    print("1. Testing basemap listing...")
    result = subprocess.run(
        ["docker", "exec", "mundi-app", "curl", "-s", "http://localhost:8000/api/basemaps"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            basemaps = json.loads(result.stdout)
            print(f"✅ Found {len(basemaps)} basemap(s)")
        except:
            print(f"❌ Failed to parse response: {result.stdout}")
    else:
        print(f"❌ Failed to list basemaps: {result.stderr}")
    
    # Test 2: Create a basemap
    print("\n2. Testing basemap creation...")
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
    
    result = subprocess.run([
        "docker", "exec", "mundi-app", 
        "curl", "-s", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(basemap_data),
        "http://localhost:8000/api/basemaps"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            created = json.loads(result.stdout)
            if 'id' in created:
                basemap_id = created['id']
                print(f"✅ Created basemap: {basemap_id}")
                print(f"   Name: {created.get('name', 'N/A')}")
                
                # Test 3: Get basemap style
                print("\n3. Testing basemap style generation...")
                result = subprocess.run([
                    "docker", "exec", "mundi-app",
                    "curl", "-s", f"http://localhost:8000/api/basemaps/{basemap_id}/style"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    try:
                        style = json.loads(result.stdout)
                        print(f"✅ Generated MapLibre GL style")
                        print(f"   Sources: {list(style.get('sources', {}).keys())}")
                        print(f"   Layers: {len(style.get('layers', []))}")
                    except:
                        print(f"❌ Failed to parse style: {result.stdout}")
                
                # Test 4: Delete basemap
                print("\n4. Testing basemap deletion...")
                result = subprocess.run([
                    "docker", "exec", "mundi-app",
                    "curl", "-s", "-X", "DELETE",
                    f"http://localhost:8000/api/basemaps/{basemap_id}"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Deleted test basemap")
                else:
                    print(f"❌ Failed to delete: {result.stderr}")
            else:
                print(f"❌ Unexpected response: {result.stdout}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"Response: {result.stdout}")
    else:
        print(f"❌ Failed to create basemap: {result.stderr}")
    
    # Test 5: Import fantasy data
    print("\n5. Testing fantasy data import...")
    import_script = """
import asyncio
from src.util.fantasy_data_importer import import_fantasy_world_data

async def run_import():
    try:
        result = await import_fantasy_world_data('00000000-0000-0000-0000-000000000001')
        print(f"✅ Import completed: {result}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

asyncio.run(run_import())
"""
    
    result = subprocess.run([
        "docker", "exec", "mundi-app",
        "python", "-c", import_script
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"❌ Import failed: {result.stderr}")
    
    print("\n🎉 Custom basemap tests completed!")


if __name__ == "__main__":
    run_docker_test()