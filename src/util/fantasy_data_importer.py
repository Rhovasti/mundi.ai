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

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import AsyncSessionLocal
from src.database.models import CustomBasemap
from src.dependencies.custom_basemap import FantasyWorldTileProvider
import uuid


def generate_id(length=12, prefix=""):
    """Generate a unique ID with optional prefix."""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length - len(prefix)))
    return prefix + random_part

class FantasyDataImporter:
    """Import fantasy world data from Eno dataset."""
    
    def __init__(self, eno_path: str = "/root/Eno/Mundi/mundi.ai/Eno"):
        self.eno_path = Path(eno_path)
        if not self.eno_path.exists():
            raise ValueError(f"Eno data path does not exist: {eno_path}")
    
    async def import_fantasy_cities_data(self, session: AsyncSession, owner_uuid: uuid.UUID):
        """Import the fantasy cities data as a reference dataset."""
        cities_file = self.eno_path / "karttatiedostot kaupungeista" / "comprehensive_city_analysis_results_updated_manually.json"
        
        if not cities_file.exists():
            print(f"Cities data file not found: {cities_file}")
            return None
        
        # Read the cities data
        with open(cities_file, 'r', encoding='utf-8') as f:
            cities_data = json.load(f)
        
        print(f"Found {len(cities_data)} fantasy cities to import")
        
        # Extract bounds from city coordinates (skip cities without coordinates)
        cities_with_coords = [city for city in cities_data if 'latitude' in city and 'longitude' in city]
        if cities_with_coords:
            lats = [city['latitude'] for city in cities_with_coords]
            lngs = [city['longitude'] for city in cities_with_coords]
            bounds = [min(lngs), min(lats), max(lngs), max(lats)]
            center = [(min(lngs) + max(lngs)) / 2, (min(lats) + max(lats)) / 2]
        else:
            bounds = [-180, -90, 180, 90]  # Default world bounds
            center = [0, 0]
        
        return {
            "cities": cities_data,
            "bounds": bounds,
            "center": center,
            "count": len(cities_data)
        }
    
    async def create_grid_basemap_config(self, session: AsyncSession, owner_uuid: uuid.UUID, 
                                       name: str = "Fantasy World Grid Map"):
        """Create a basemap configuration for the numbered grid tiles."""
        raster_path = self.eno_path / "rasterikartta"
        
        # Check if we have a proper grid structure
        tile_dirs = sorted([d for d in raster_path.iterdir() if d.is_dir() and d.name.isdigit()])
        
        if not tile_dirs:
            print("No numbered tile directories found")
            return None
        
        print(f"Found {len(tile_dirs)} tile directories")
        
        # This appears to be a 7x7 grid (1-49)
        grid_size = 7
        
        # Create a custom basemap entry for this grid-based tilemap
        basemap = CustomBasemap(
            id=generate_id(prefix="B"),
            owner_uuid=owner_uuid,
            name=name,
            tile_url_template=f"file://{raster_path.absolute()}/grid/{{z}}/{{x}}/{{y}}.jpg",
            tile_format="jpg",
            min_zoom=0,
            max_zoom=4,  # Limited zoom for grid-based map
            tile_size=256,
            attribution="© Fantasy World Map",
            is_public=False,
            metadata_json={
                "type": "grid_based",
                "grid_size": grid_size,
                "original_tiles": len(tile_dirs),
                "source_path": str(raster_path)
            }
        )
        
        session.add(basemap)
        await session.commit()
        await session.refresh(basemap)
        
        print(f"Created basemap configuration: {basemap.id}")
        return basemap
    
    async def create_relief_basemap_config(self, session: AsyncSession, owner_uuid: uuid.UUID,
                                         name: str = "Fantasy World Relief Map"):
        """Create a basemap configuration for the relief TIFF."""
        relief_path = self.eno_path / "tif" / "reliefi real_muokattu_suuriresoluutio.tif"
        
        if not relief_path.exists():
            print(f"Relief map not found: {relief_path}")
            return None
        
        # Get file size in MB
        size_mb = relief_path.stat().st_size / (1024 * 1024)
        print(f"Found relief map: {size_mb:.1f} MB")
        
        # This would need to be processed into tiles for web viewing
        # For now, we'll create a placeholder configuration
        basemap = CustomBasemap(
            id=generate_id(prefix="B"),
            owner_uuid=owner_uuid,
            name=name,
            tile_url_template=f"file://{self.eno_path.absolute()}/tif/relief_tiles/{{z}}/{{x}}/{{y}}.png",
            tile_format="png",
            min_zoom=0,
            max_zoom=12,
            tile_size=256,
            attribution="© Fantasy World Relief Map",
            is_public=False,
            metadata_json={
                "type": "relief_map",
                "source_file": str(relief_path),
                "size_mb": size_mb,
                "note": "Requires tile generation from source TIFF"
            }
        )
        
        session.add(basemap)
        await session.commit()
        await session.refresh(basemap)
        
        print(f"Created relief basemap configuration: {basemap.id}")
        return basemap


async def import_fantasy_world_data(owner_uuid: Optional[str] = None):
    """Import all fantasy world data from Eno dataset."""
    if not owner_uuid:
        # Use a demo UUID for testing
        owner_uuid = uuid.UUID("00000000-0000-0000-0000-000000000001")
    else:
        owner_uuid = uuid.UUID(owner_uuid)
    
    async with AsyncSessionLocal() as session:
        importer = FantasyDataImporter()
        
        # Import cities data
        print("Importing fantasy cities data...")
        cities_info = await importer.import_fantasy_cities_data(session, owner_uuid)
        if cities_info:
            print(f"Imported {cities_info['count']} cities")
            print(f"World bounds: {cities_info['bounds']}")
            print(f"World center: {cities_info['center']}")
        
        # Create basemap configurations
        print("\nCreating basemap configurations...")
        
        # Grid-based raster map
        grid_basemap = await importer.create_grid_basemap_config(session, owner_uuid)
        if grid_basemap:
            print(f"Grid basemap ID: {grid_basemap.id}")
        
        # Relief map
        relief_basemap = await importer.create_relief_basemap_config(session, owner_uuid)
        if relief_basemap:
            print(f"Relief basemap ID: {relief_basemap.id}")
        
        print("\nFantasy world data import completed!")
        
        return {
            "cities_info": cities_info,
            "grid_basemap_id": grid_basemap.id if grid_basemap else None,
            "relief_basemap_id": relief_basemap.id if relief_basemap else None
        }


if __name__ == "__main__":
    # Run the importer as a standalone script
    asyncio.run(import_fantasy_world_data())