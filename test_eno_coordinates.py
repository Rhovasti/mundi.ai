#!/usr/bin/env python3
"""Test script to analyze Eno coordinates and transformation logic."""

import json
import statistics

# Sample coordinates from the GeoJSON
sample_coords = [
    {"name": "Jouy", "coords": [84.67, 26.78]},
    {"name": "Motu", "coords": [98.33, 23.56]},
    {"name": "Palwede", "coords": [51.35, 84.07]},
    {"name": "Guild", "coords": [115.62, -5.45]},
    {"name": "Gyba", "coords": [-23.88, 75.47]},
    {"name": "Beitsa", "coords": [35.11, -73.58]},
    {"name": "Alos", "coords": [-63.57, 49.15]},
    {"name": "Jiafeng", "coords": [-69.65, -5.66]},
]

def analyze_coordinates():
    """Analyze the coordinate system used in Eno world."""
    
    print("=== Eno World Coordinate Analysis ===\n")
    
    # Extract lon/lat
    lons = [c["coords"][0] for c in sample_coords]
    lats = [c["coords"][1] for c in sample_coords]
    
    print(f"Longitude range: {min(lons):.2f} to {max(lons):.2f}")
    print(f"Latitude range: {min(lats):.2f} to {max(lats):.2f}")
    print(f"Longitude span: {max(lons) - min(lons):.2f}°")
    print(f"Latitude span: {max(lats) - min(lats):.2f}°")
    
    print("\n=== With 2.5x Scale Factor ===")
    scaled_lons = [lon * 2.5 for lon in lons]
    scaled_lats = [lat * 2.5 for lat in lats]
    
    print(f"Scaled longitude range: {min(scaled_lons):.2f} to {max(scaled_lons):.2f}")
    print(f"Scaled latitude range: {min(scaled_lats):.2f} to {max(scaled_lats):.2f}")
    
    print("\n=== Basemap Bounds (from database) ===")
    basemap_bounds = [-73.312, -92.897, 117.287, 98.423]
    print(f"Original: {basemap_bounds}")
    print(f"Scaled 2.5x: [{basemap_bounds[0]*2.5:.2f}, {basemap_bounds[1]*2.5:.2f}, "
          f"{basemap_bounds[2]*2.5:.2f}, {basemap_bounds[3]*2.5:.2f}]")
    
    print("\n=== World Model Extent ===")
    world_extent = [-720, -450, 1080, 450]
    print(f"Configured extent: {world_extent}")
    
    print("\n=== Analysis ===")
    print("1. Eno coordinates already use extended range (-73 to 117 lon, -92 to 98 lat)")
    print("2. These are NOT standard Earth coordinates (Earth: -180 to 180, -90 to 90)")
    print("3. Applying 2.5x scale pushes coordinates even further out of bounds")
    print("4. The world model extent [-720, -450, 1080, 450] seems arbitrary")
    print("5. MapLibre GL expects coordinates in standard ranges")
    
    print("\n=== Recommendations ===")
    print("1. Remove the 2.5x scale transformation")
    print("2. Use Eno coordinates as-is (they already represent the fantasy world)")
    print("3. Configure MapLibre to handle extended coordinate ranges")
    print("4. Update world model extent to match actual data bounds")

if __name__ == "__main__":
    analyze_coordinates()