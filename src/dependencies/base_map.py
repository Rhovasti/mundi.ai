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

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseMapProvider(ABC):
    """Abstract base class for base map providers."""

    @abstractmethod
    async def get_base_style(self) -> Dict[str, Any]:
        """Return the base MapLibre GL style JSON."""
        pass


class OpenStreetMapProvider(BaseMapProvider):
    """Default base map provider using OpenStreetMap tiles."""

    async def get_base_style(self) -> Dict[str, Any]:
        """Return a basic MapLibre GL style using OpenStreetMap tiles."""
        return {
            "version": 8,
            "name": "OpenStreetMap",
            "metadata": {
                "maplibre:logo": "https://maplibre.org/",
            },
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "osm": {
                    "type": "raster",
                    "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                    "tileSize": 256,
                    "attribution": "© OpenStreetMap contributors",
                    "maxzoom": 19,
                }
            },
            "layers": [
                {
                    "id": "osm",
                    "type": "raster",
                    "source": "osm",
                    "layout": {"visibility": "visible"},
                    "paint": {},
                }
            ],
            "center": [0, 0],
            "zoom": 2,
            "bearing": 0,
            "pitch": 0,
        }


class EnoWorldProvider(BaseMapProvider):
    """Base map provider for Eno fantasy world using image basemap."""

    async def get_base_style(self) -> Dict[str, Any]:
        """Return a MapLibre GL style using the Eno relief image with normalized coordinates."""
        # Normalize Eno coordinates to standard geographic bounds
        # Original Eno bounds: [-73.312, -92.897, 117.287, 98.423] 
        # Map to: longitude [-180, 180], latitude [-85, 85] (Web Mercator limits)
        return {
            "version": 8,
            "name": "Eno World",
            "metadata": {
                "maplibre:logo": "https://maplibre.org/",
            },
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "eno-relief": {
                    "type": "image",
                    "url": "/api/tiles/local/BUlJVMxOuaEK/0/0/0.png",
                    "coordinates": [
                        [-180, 85],   # top-left (normalized)
                        [180, 85],    # top-right (normalized)  
                        [180, -85],   # bottom-right (normalized)
                        [-180, -85]   # bottom-left (normalized)
                    ]
                }
            },
            "layers": [
                {
                    "id": "eno-relief-layer",
                    "type": "raster",
                    "source": "eno-relief",
                    "layout": {"visibility": "visible"},
                    "paint": {"raster-opacity": 1.0},
                }
            ],
            "center": [0, 0],  # Center of normalized world
            "zoom": 2,         # Lower zoom to see full world
            "bearing": 0,
            "pitch": 0,
        }


class MapTilerEnoProvider(BaseMapProvider):
    """
    MapTiler-based provider for Eno fantasy world with proper coordinate alignment.
    
    TODO: This is a TEMPORARY solution using proprietary MapTiler service.
    Future improvements should migrate to:
    1. Self-hosted tile server using the re-projected data from /skaalatut/projisoidut/
    2. Local coordinate transformation pipeline
    3. Open-source tile generation from the relief and vector data
    
    The MapTiler solution provides professional georeferencing as a bridge
    until we can implement a fully self-hosted alternative.
    """

    def __init__(self, api_key: str = "wlMkQ9IDDyv6h7iXvze2"):
        """Initialize with MapTiler API key."""
        self.api_key = api_key
        self.style_id = "01965e52-7535-7737-8dd6-d874aaf7d55f"

    async def get_base_style(self) -> Dict[str, Any]:
        """Return MapTiler style JSON with proper Eno coordinate alignment."""
        import aiohttp
        import json
        
        # Fetch the MapTiler style JSON
        style_url = f"https://api.maptiler.com/maps/{self.style_id}/style.json?key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(style_url) as response:
                    if response.status == 200:
                        style_data = await response.json()
                        
                        # Customize for Mundi integration
                        style_data["name"] = "Eno World (MapTiler)"
                        style_data["metadata"] = {
                            "maplibre:logo": "https://maplibre.org/",
                            "maptiler:copyright": "© MapTiler © OpenStreetMap contributors"
                        }
                        
                        return style_data
                    else:
                        # Fallback to basic style if MapTiler is unavailable
                        return await self._get_fallback_style()
                        
        except Exception as e:
            print(f"Error fetching MapTiler style: {e}")
            return await self._get_fallback_style()

    async def _get_fallback_style(self) -> Dict[str, Any]:
        """Fallback style if MapTiler is unavailable."""
        return {
            "version": 8,
            "name": "Eno World (Fallback)",
            "sources": {},
            "layers": [],
            "center": [0, 0],
            "zoom": 2
        }


# Default dependency - can be overridden in closed source
def get_base_map_provider() -> BaseMapProvider:
    """Default base map provider dependency."""
    return OpenStreetMapProvider()


async def get_base_map_provider_for_map(map_id: str) -> BaseMapProvider:
    """Get the appropriate base map provider for a specific map."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from ..database.models import CustomBasemap, WorldModel
    from ..database.connection import engine
    
    # Check if this map is associated with the Eno world model
    async with AsyncSession(engine) as session:
        # Query to find if any basemap for this map is associated with Eno world
        query = select(CustomBasemap).join(WorldModel).where(
            WorldModel.name == "Eno World"
        )
        result = await session.execute(query)
        eno_basemaps = result.scalars().all()
        
        # Check if the map ID matches any Eno-related basemap
        eno_map_ids = ["BxvFhuzMcnuy", "MxvFhuzMcnuy", "BUlJVMxOuaEK", "BGBov1d6Svoy", "BwFKKVCxBm6o"]
        
        if map_id in eno_map_ids or any(basemap.id == map_id for basemap in eno_basemaps):
            # Use MapTiler provider for proper coordinate alignment
            return MapTilerEnoProvider()
    
    # Default to OpenStreetMap for all other maps
    return OpenStreetMapProvider()
