#!/usr/bin/env python3
"""
Transform only the main vector files for testing coordinate alignment.
"""

import json
from pathlib import Path
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
    
    # Linear transformation
    normalized = (coord - old_min) / (old_max - old_min)
    transformed = normalized * (new_max - new_min) + new_min
    
    return transformed

def transform_coordinates(coordinates, geometry_type):
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

def transform_geojson_file(file_path: Path) -> bool:
    """Transform a GeoJSON file."""
    try:
        print(f"Transforming: {file_path.name}")
        
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Transform features
        if geojson_data.get('type') == 'FeatureCollection' and 'features' in geojson_data:
            for feature in geojson_data['features']:
                if 'geometry' in feature and feature['geometry'] and 'coordinates' in feature['geometry']:
                    geometry_type = feature['geometry'].get('type', '')
                    feature['geometry']['coordinates'] = transform_coordinates(
                        feature['geometry']['coordinates'], 
                        geometry_type
                    )
        
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
        
        # Write transformed file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Transformed successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Transform main vector files."""
    print("🗺️  Transforming Main Vector Files")
    print("=" * 40)
    
    # Main vector files to transform
    vector_dir = Path("/app/Eno/vector")
    cities_dir = Path("/app/Eno/karttatiedostot kaupungeista")
    
    files_to_transform = [
        vector_dir / "biomes.geojson",
        vector_dir / "lakes.geojson", 
        vector_dir / "rivers.geojson",
        vector_dir / "states.geojson",
        cities_dir / "kaupunkiensijainti.geojson"  # Main cities file
    ]
    
    success_count = 0
    for file_path in files_to_transform:
        if file_path.exists():
            if transform_geojson_file(file_path):
                success_count += 1
        else:
            print(f"❌ File not found: {file_path}")
    
    print()
    print(f"✅ Successfully transformed: {success_count}/{len(files_to_transform)} files")
    
    # Test coordinate transformation
    print("\n🧪 Testing coordinate transformation:")
    test_coords = [
        [-72.720, -84.000],  # Eno min corner
        [117.243, 90.560],   # Eno max corner  
        [22.261, 3.280],     # Eno center (calculated)
    ]
    
    for eno_coord in test_coords:
        lon_transformed = transform_coordinate(eno_coord[0], 'lon')
        lat_transformed = transform_coordinate(eno_coord[1], 'lat')
        print(f"  Eno {eno_coord} → Normalized [{lon_transformed:.3f}, {lat_transformed:.3f}]")

if __name__ == "__main__":
    main()