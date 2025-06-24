#!/usr/bin/env python3
"""
GeoTIFF to Web Tiles Processor

Converts large GeoTIFF files to web-compatible XYZ tiles for use with MapLibre.
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Tuple
import json

class GeoTIFFProcessor:
    """Process GeoTIFF files into web tiles."""
    
    def __init__(self, geotiff_path: str, output_dir: str):
        self.geotiff_path = Path(geotiff_path)
        self.output_dir = Path(output_dir)
        
        if not self.geotiff_path.exists():
            raise FileNotFoundError(f"GeoTIFF not found: {geotiff_path}")
    
    def get_geotiff_info(self) -> dict:
        """Get information about the GeoTIFF using gdalinfo."""
        try:
            result = subprocess.run([
                'gdalinfo', '-json', str(self.geotiff_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"gdalinfo error: {result.stderr}")
                return {}
        except Exception as e:
            print(f"Error getting GeoTIFF info: {e}")
            return {}
    
    def generate_overview_tiles(self, max_zoom: int = 8, tile_size: int = 256) -> bool:
        """
        Generate overview tiles using gdal2tiles.py.
        
        For a 3.3GB file, we start with lower zoom levels for quick preview.
        """
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Generating tiles from {self.geotiff_path.name}...")
            print(f"Output directory: {self.output_dir}")
            print(f"Max zoom level: {max_zoom}")
            
            # Use gdal2tiles to generate web tiles
            cmd = [
                'gdal2tiles.py',
                '--processes=4',  # Use multiple processes
                f'--zoom=0-{max_zoom}',  # Zoom range
                '--webp',  # Use WebP format for better compression
                '--tilesize=256',  # Standard tile size
                '--resampling=average',  # Good for relief data
                str(self.geotiff_path),
                str(self.output_dir)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            # Run the command with progress updates
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Print progress
            for line in process.stdout:
                if line.strip():
                    print(f"  {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print("✅ Tile generation completed successfully!")
                return True
            else:
                print(f"❌ Tile generation failed with code {process.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating tiles: {e}")
            return False
    
    def generate_small_preview(self, output_path: str, max_size: int = 2048) -> bool:
        """Generate a small preview image for quick testing."""
        try:
            preview_path = Path(output_path)
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                'gdal_translate',
                '-of', 'PNG',
                '-outsize', str(max_size), str(max_size),
                str(self.geotiff_path),
                str(preview_path)
            ]
            
            print(f"Generating preview: {preview_path.name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Preview generated: {preview_path}")
                return True
            else:
                print(f"❌ Preview generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating preview: {e}")
            return False


def process_eno_relief_map():
    """Process the Eno relief map specifically."""
    
    geotiff_path = "/root/Eno/Mundi/mundi.ai/Eno/tif/reliefi real_muokattu_suuriresoluutio.tif"
    tiles_output = "/root/Eno/Mundi/mundi.ai/Eno/tif/relief_tiles"
    preview_output = "/root/Eno/Mundi/mundi.ai/Eno/tif/relief_preview.png"
    
    processor = GeoTIFFProcessor(geotiff_path, tiles_output)
    
    # Get file info
    print("📊 Analyzing GeoTIFF...")
    info = processor.get_geotiff_info()
    if info:
        size = info.get('size', [])
        if size:
            print(f"   Dimensions: {size[0]} x {size[1]} pixels")
        
        bands = info.get('bands', [])
        print(f"   Bands: {len(bands)}")
        
        coord_sys = info.get('coordinateSystem', {})
        if coord_sys:
            print(f"   Coordinate System: {coord_sys.get('wkt', 'Unknown')[:50]}...")
    
    # Generate small preview first (faster)
    print("\n🖼️ Generating preview image...")
    preview_success = processor.generate_small_preview(preview_output)
    
    # Ask user if they want to proceed with full tile generation
    if preview_success:
        print(f"\n✅ Preview created at: {preview_output}")
        print("\n⚠️  Full tile generation will take significant time and disk space.")
        print("   Would you like to proceed with generating web tiles? (y/n)")
        
        # For automated execution, we'll start with zoom level 6 max
        print("   Starting tile generation with max zoom 6 for testing...")
        tiles_success = processor.generate_overview_tiles(max_zoom=6)
        
        if tiles_success:
            return tiles_output
    
    return None


if __name__ == "__main__":
    result = process_eno_relief_map()
    if result:
        print(f"\n🎉 Success! Tiles available at: {result}")
    else:
        print("\n❌ Processing failed")