#!/usr/bin/env python3
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

"""
Batch conversion script for converting GeoJSON files to OSM PBF format
using custom fantasy world translations.

Usage:
    python scripts/geojson_to_pbf.py <input_dir> <output_file.pbf>
    python scripts/geojson_to_pbf.py data/fantasy_geojson/ fantasy_world.pbf
"""

import argparse
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional

# Add src to path to import fantasy translation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import ogr2osm
    from fantasy.translation import FantasyTranslation
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure ogr2pbf is installed: pip install ogr2pbf")
    sys.exit(1)


def find_geojson_files(directory: str) -> List[str]:
    """Find all GeoJSON files in a directory."""
    geojson_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.geojson', '.json')):
                geojson_files.append(os.path.join(root, file))
    return geojson_files


def convert_geojson_to_osm(input_file: str, output_file: str, translation_class=None) -> bool:
    """Convert a single GeoJSON file to OSM XML format."""
    try:
        print(f"Converting {input_file} to {output_file}...")
        
        # Use custom translation if provided
        if translation_class:
            translation = translation_class()
            
            # Open data source
            datasource = ogr2osm.OgrDatasource(translation)
            datasource.open_datasource(input_file)
            
            # Convert to OSM
            osmdata = ogr2osm.OsmData(translation)
            osmdata.process(datasource)
            
            # Write output
            datawriter = ogr2osm.OsmDataWriter(output_file)
            osmdata.output(datawriter)
        else:
            # Use command line ogr2osm
            cmd = ["ogr2osm", input_file, "-o", output_file]
            subprocess.run(cmd, check=True)
        
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {e}")
        return False


def convert_osm_to_pbf(osm_file: str, pbf_file: str) -> bool:
    """Convert OSM XML to PBF format using osmium."""
    try:
        print(f"Converting {osm_file} to {pbf_file}...")
        cmd = ["osmium", "cat", osm_file, "-o", pbf_file]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error converting {osm_file} to PBF: {e}")
        return False


def merge_pbf_files(pbf_files: List[str], output_file: str) -> bool:
    """Merge multiple PBF files into one using osmium."""
    try:
        print(f"Merging {len(pbf_files)} PBF files into {output_file}...")
        cmd = ["osmium", "merge"] + pbf_files + ["-o", output_file]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error merging PBF files: {e}")
        return False


def validate_pbf(pbf_file: str) -> bool:
    """Validate PBF file using osmium fileinfo."""
    try:
        print(f"Validating {pbf_file}...")
        cmd = ["osmium", "fileinfo", pbf_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("PBF file validation successful!")
            print(result.stdout)
            return True
        else:
            print(f"PBF file validation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error validating PBF file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert GeoJSON files to OSM PBF format with fantasy world translations"
    )
    parser.add_argument(
        "input", 
        help="Input directory containing GeoJSON files or single GeoJSON file"
    )
    parser.add_argument(
        "output", 
        help="Output PBF file path"
    )
    parser.add_argument(
        "--no-fantasy-translation", 
        action="store_true",
        help="Skip fantasy translation and use default ogr2osm translation"
    )
    parser.add_argument(
        "--keep-intermediate", 
        action="store_true",
        help="Keep intermediate OSM XML files for debugging"
    )
    parser.add_argument(
        "--validate", 
        action="store_true",
        help="Validate output PBF file"
    )
    
    args = parser.parse_args()
    
    # Check if input exists
    if not os.path.exists(args.input):
        print(f"Error: Input path {args.input} does not exist")
        sys.exit(1)
    
    # Determine translation class
    translation_class = None if args.no_fantasy_translation else FantasyTranslation
    
    # Get list of GeoJSON files
    if os.path.isfile(args.input):
        geojson_files = [args.input]
    else:
        geojson_files = find_geojson_files(args.input)
    
    if not geojson_files:
        print(f"No GeoJSON files found in {args.input}")
        sys.exit(1)
    
    print(f"Found {len(geojson_files)} GeoJSON files to convert")
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        osm_files = []
        pbf_files = []
        
        # Convert each GeoJSON to OSM XML
        for i, geojson_file in enumerate(geojson_files):
            base_name = os.path.splitext(os.path.basename(geojson_file))[0]
            osm_file = os.path.join(temp_dir, f"{base_name}_{i}.osm")
            pbf_file = os.path.join(temp_dir, f"{base_name}_{i}.pbf")
            
            # Convert GeoJSON to OSM
            if convert_geojson_to_osm(geojson_file, osm_file, translation_class):
                osm_files.append(osm_file)
                
                # Convert OSM to PBF
                if convert_osm_to_pbf(osm_file, pbf_file):
                    pbf_files.append(pbf_file)
                
                # Keep intermediate files if requested
                if not args.keep_intermediate:
                    try:
                        os.remove(osm_file)
                    except:
                        pass
        
        if not pbf_files:
            print("No PBF files were successfully created")
            sys.exit(1)
        
        # Merge all PBF files or copy single file
        if len(pbf_files) == 1:
            # Just copy the single file
            import shutil
            shutil.copy2(pbf_files[0], args.output)
            print(f"Single PBF file copied to {args.output}")
        else:
            # Merge multiple files
            if not merge_pbf_files(pbf_files, args.output):
                print("Failed to merge PBF files")
                sys.exit(1)
        
        # Validate output if requested
        if args.validate:
            if not validate_pbf(args.output):
                print("PBF validation failed")
                sys.exit(1)
    
    print(f"Successfully created fantasy world PBF: {args.output}")
    print("\nNext steps:")
    print("1. Import PBF into PostGIS: osm2pgsql -d mundidb fantasy_world.pbf")
    print("2. Set up tile server (martin/tileserver-gl) to serve vector tiles")
    print("3. Update MUNDI_BASEMAP_MODE=fantasy in environment variables")


if __name__ == "__main__":
    main()