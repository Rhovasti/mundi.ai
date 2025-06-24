#!/usr/bin/env python3
"""
Simple coordinate clamping for Eno vector data.
Instead of transforming, just clamp latitude values to valid Web Mercator range.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def clamp_latitude(lat: float) -> float:
    """Clamp latitude to Web Mercator safe range [-85, 85]."""
    return max(-85.0, min(85.0, lat))

def clamp_coordinates(coordinates):
    """Clamp coordinates to valid ranges."""
    if isinstance(coordinates, (int, float)):
        return coordinates
    
    if not isinstance(coordinates, list):
        return coordinates
        
    # Check if this is a coordinate pair [lon, lat]
    if (len(coordinates) == 2 and 
        isinstance(coordinates[0], (int, float)) and 
        isinstance(coordinates[1], (int, float))):
        
        lon, lat = coordinates
        # Longitude is already valid (-72 to 117 is fine within -180 to 180)
        # Just clamp latitude to Web Mercator safe range
        clamped_lat = clamp_latitude(lat)
        return [lon, clamped_lat]
    
    # Recursively process nested coordinate arrays
    return [clamp_coordinates(coord) for coord in coordinates]

def process_geojson_file(file_path: Path) -> bool:
    """Process a GeoJSON file to clamp coordinates."""
    try:
        print(f"Processing: {file_path.name}")
        
        # Check if backup exists, if so restore from backup first
        backup_path = file_path.with_suffix('.geojson.backup')
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
            print(f"  Restored from backup")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        clamped_count = 0
        
        # Process features
        if geojson_data.get('type') == 'FeatureCollection' and 'features' in geojson_data:
            for feature in geojson_data['features']:
                if 'geometry' in feature and feature['geometry'] and 'coordinates' in feature['geometry']:
                    original_coords = feature['geometry']['coordinates']
                    clamped_coords = clamp_coordinates(original_coords)
                    
                    # Count if any coordinates were actually clamped
                    if str(original_coords) != str(clamped_coords):
                        clamped_count += 1
                    
                    feature['geometry']['coordinates'] = clamped_coords
        
        # Add metadata
        if 'metadata' not in geojson_data:
            geojson_data['metadata'] = {}
        geojson_data['metadata'].update({
            'coordinate_system': 'geographic_clamped',
            'clamped_features': clamped_count,
            'processing_date': datetime.utcnow().isoformat(),
            'latitude_range': '[-85, 85]',
            'note': 'Latitude values clamped to Web Mercator safe range'
        })
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Processed successfully ({clamped_count} features clamped)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main coordinate clamping function."""
    print("🗺️  Eno Coordinate Clamping")
    print("=" * 35)
    print("Restoring from backups and clamping latitude values to [-85, 85]")
    print()
    
    # Main vector files to process
    vector_dir = Path("/app/Eno/vector")
    cities_dir = Path("/app/Eno/karttatiedostot kaupungeista")
    
    files_to_process = [
        vector_dir / "biomes.geojson",
        vector_dir / "lakes.geojson", 
        vector_dir / "rivers.geojson",
        vector_dir / "states.geojson",
        cities_dir / "kaupunkiensijainti.geojson"
    ]
    
    success_count = 0
    for file_path in files_to_process:
        if file_path.exists() or file_path.with_suffix('.geojson.backup').exists():
            if process_geojson_file(file_path):
                success_count += 1
        else:
            print(f"❌ File not found: {file_path}")
    
    print()
    print(f"✅ Successfully processed: {success_count}/{len(files_to_process)} files")
    
    # Verify final bounds
    print("\n🔍 Verifying final coordinate bounds:")
    for file_path in files_to_process[:4]:  # Check main vector files
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if 'features' in data and data['features']:
                    sample_coords = []
                    for feature in data['features'][:2]:  # Check first 2 features
                        if 'geometry' in feature and 'coordinates' in feature['geometry']:
                            coords = feature['geometry']['coordinates']
                            if isinstance(coords[0], list) and isinstance(coords[0][0], list):
                                sample_coords.append(coords[0][0])  # Polygon
                            elif isinstance(coords[0], list):
                                sample_coords.append(coords[0])     # LineString
                            else:
                                sample_coords.append(coords)       # Point
                    
                    print(f"  {file_path.name}: Sample coordinates = {sample_coords}")
            except Exception as e:
                print(f"  {file_path.name}: Error reading = {e}")

if __name__ == "__main__":
    main()