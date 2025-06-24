#!/usr/bin/env python3
"""
Transform Eno coordinate system to normalized world coordinates.

This script transforms vector data from the original Eno coordinate system
to normalized geographic coordinates that work with MapLibre GL.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Union
import shutil
from datetime import datetime

# Coordinate bounds (actual bounds from vector data analysis)
ENO_BOUNDS = {
    'lon_min': -72.720,
    'lon_max': 117.243, 
    'lat_min': -84.000,
    'lat_max': 90.560
}

NORMALIZED_BOUNDS = {
    'lon_min': -180,
    'lon_max': 180,
    'lat_min': -85,
    'lat_max': 85
}

def transform_coordinate(coord: float, axis: str) -> float:
    """Transform a single coordinate from Eno to normalized system."""
    if axis == 'lon':
        old_min, old_max = ENO_BOUNDS['lon_min'], ENO_BOUNDS['lon_max']
        new_min, new_max = NORMALIZED_BOUNDS['lon_min'], NORMALIZED_BOUNDS['lon_max']
    elif axis == 'lat':
        old_min, old_max = ENO_BOUNDS['lat_min'], ENO_BOUNDS['lat_max']
        new_min, new_max = NORMALIZED_BOUNDS['lat_min'], NORMALIZED_BOUNDS['lat_max']
    else:
        raise ValueError(f"Invalid axis: {axis}")
    
    # Linear transformation: new = (old - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
    normalized = (coord - old_min) / (old_max - old_min)
    transformed = normalized * (new_max - new_min) + new_min
    
    return transformed

def transform_coordinates(coordinates: Union[List, float], geometry_type: str) -> Union[List, float]:
    """Transform coordinates based on geometry type."""
    if isinstance(coordinates, (int, float)):
        return coordinates
    
    if not isinstance(coordinates, list):
        return coordinates
        
    # Check if this is a coordinate pair [lon, lat]
    if (len(coordinates) == 2 and 
        isinstance(coordinates[0], (int, float)) and 
        isinstance(coordinates[1], (int, float))):
        
        lon, lat = coordinates
        transformed_lon = transform_coordinate(lon, 'lon')
        transformed_lat = transform_coordinate(lat, 'lat')
        return [transformed_lon, transformed_lat]
    
    # Recursively transform nested coordinate arrays
    return [transform_coordinates(coord, geometry_type) for coord in coordinates]

def transform_geojson_geometry(geometry: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a GeoJSON geometry."""
    if not geometry or 'coordinates' not in geometry:
        return geometry
    
    geometry_type = geometry.get('type', '')
    transformed_geometry = geometry.copy()
    transformed_geometry['coordinates'] = transform_coordinates(
        geometry['coordinates'], 
        geometry_type
    )
    
    return transformed_geometry

def transform_geojson_feature(feature: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a GeoJSON feature."""
    transformed_feature = feature.copy()
    
    if 'geometry' in feature and feature['geometry']:
        transformed_feature['geometry'] = transform_geojson_geometry(feature['geometry'])
    
    return transformed_feature

def transform_geojson_file(input_path: Path, output_path: Path = None) -> bool:
    """Transform a GeoJSON file from Eno to normalized coordinates."""
    try:
        print(f"Transforming: {input_path}")
        
        # Read the original file
        with open(input_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Transform the data
        if geojson_data.get('type') == 'FeatureCollection':
            if 'features' in geojson_data:
                geojson_data['features'] = [
                    transform_geojson_feature(feature) 
                    for feature in geojson_data['features']
                ]
        elif geojson_data.get('type') == 'Feature':
            geojson_data = transform_geojson_feature(geojson_data)
        elif 'coordinates' in geojson_data:
            # Direct geometry
            geojson_data = transform_geojson_geometry(geojson_data)
        
        # Add transformation metadata
        if 'metadata' not in geojson_data:
            geojson_data['metadata'] = {}
        geojson_data['metadata'].update({
            'coordinate_system': 'normalized_geographic',
            'transformed_from': 'eno_fantasy_world',
            'transformation_date': datetime.utcnow().isoformat(),
            'original_bounds': ENO_BOUNDS,
            'normalized_bounds': NORMALIZED_BOUNDS
        })
        
        # Determine output path
        if output_path is None:
            output_path = input_path
        
        # Create backup if overwriting
        if output_path == input_path:
            backup_path = input_path.with_suffix('.geojson.backup')
            if not backup_path.exists():
                shutil.copy2(input_path, backup_path)
                print(f"  Created backup: {backup_path}")
        
        # Write transformed file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Transformed successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error transforming {input_path}: {e}")
        return False

def find_geojson_files(directory: Path) -> List[Path]:
    """Find all GeoJSON files in a directory."""
    geojson_files = []
    
    for pattern in ['*.geojson', '*.json']:
        geojson_files.extend(directory.glob(pattern))
        geojson_files.extend(directory.glob(f'**/{pattern}'))
    
    return sorted(geojson_files)

def main():
    """Main transformation function."""
    print("🗺️  Eno Coordinate Transformation Script")
    print("=" * 50)
    
    # Define paths
    eno_base = Path("/app/Eno")
    vector_dir = eno_base / "vector"
    cities_dir = eno_base / "karttatiedostot kaupungeista"
    
    # Find all GeoJSON files
    all_files = []
    
    if vector_dir.exists():
        vector_files = find_geojson_files(vector_dir)
        all_files.extend(vector_files)
        print(f"Found {len(vector_files)} vector files in {vector_dir}")
    
    if cities_dir.exists():
        cities_files = find_geojson_files(cities_dir)
        all_files.extend(cities_files)
        print(f"Found {len(cities_files)} city files in {cities_dir}")
    
    print(f"\nTotal files to transform: {len(all_files)}")
    print()
    
    # Transform all files
    success_count = 0
    for file_path in all_files:
        if transform_geojson_file(file_path):
            success_count += 1
    
    print()
    print("=" * 50)
    print(f"Transformation complete!")
    print(f"✅ Successfully transformed: {success_count}/{len(all_files)} files")
    
    if success_count < len(all_files):
        print(f"❌ Failed to transform: {len(all_files) - success_count} files")
    
    # Test coordinate transformation
    print("\n🧪 Testing coordinate transformation:")
    test_coords = [
        [-73.312, -92.897],  # Eno min corner
        [117.287, 98.423],   # Eno max corner  
        [21.9875, 2.763],    # Eno center
    ]
    
    for eno_coord in test_coords:
        lon_transformed = transform_coordinate(eno_coord[0], 'lon')
        lat_transformed = transform_coordinate(eno_coord[1], 'lat')
        print(f"  Eno {eno_coord} → Normalized [{lon_transformed:.3f}, {lat_transformed:.3f}]")

if __name__ == "__main__":
    main()