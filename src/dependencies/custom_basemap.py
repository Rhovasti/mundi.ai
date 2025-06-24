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

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.dependencies.base_map import BaseMapProvider
import os
from pathlib import Path


class TileSource(BaseModel):
    """Configuration for a custom tile source."""
    id: str
    name: str
    tile_url_template: str  # e.g., "https://example.com/{z}/{x}/{y}.png" or "file:///path/{z}/{x}/{y}.png"
    min_zoom: int = 0
    max_zoom: int = 22
    tile_size: int = 256
    attribution: str = ""
    bounds: Optional[List[float]] = None  # [west, south, east, north]
    center: Optional[List[float]] = None  # [lng, lat]
    default_zoom: Optional[int] = None


class CustomTileMapProvider(BaseMapProvider):
    """Provider for custom tile-based basemaps."""
    
    def __init__(self, tile_source: TileSource):
        self.tile_source = tile_source
    
    async def get_base_style(self) -> Dict[str, Any]:
        """Generate MapLibre GL style for custom tilemap."""
        # Check if this is a vector source (GeoJSON)
        if self.tile_source.tile_url_template.startswith("geojson://"):
            # Handle GeoJSON vector sources
            geojson_path = self.tile_source.tile_url_template.replace("geojson://", "")
            
            # Use the API endpoint to serve the GeoJSON
            data_url = f"/api/basemaps/{self.tile_source.id}/data"
            
            style = {
                "version": 8,
                "name": self.tile_source.name,
                "metadata": {
                    "maplibre:logo": "https://maplibre.org/",
                    "mundi:custom_basemap": True,
                    "mundi:basemap_id": self.tile_source.id,
                },
                "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
                "sources": {
                    self.tile_source.id: {
                        "type": "geojson",
                        "data": data_url,
                        "attribution": self.tile_source.attribution,
                    }
                },
                "layers": [
                    {
                        "id": f"{self.tile_source.id}-points",
                        "type": "circle",
                        "source": self.tile_source.id,
                        "filter": ["==", "$type", "Point"],
                        "paint": {
                            "circle-radius": 5,
                            "circle-color": "#ff0000",
                            "circle-stroke-width": 1,
                            "circle-stroke-color": "#ffffff"
                        }
                    },
                    {
                        "id": f"{self.tile_source.id}-labels",
                        "type": "symbol",
                        "source": self.tile_source.id,
                        "filter": ["==", "$type", "Point"],
                        "layout": {
                            "text-field": ["get", "name"],
                            "text-size": 12,
                            "text-offset": [0, 1.5],
                            "text-anchor": "top"
                        },
                        "paint": {
                            "text-color": "#000000",
                            "text-halo-color": "#ffffff",
                            "text-halo-width": 2
                        }
                    }
                ],
            }
        else:
            # Handle raster sources
            tile_urls = [self.tile_source.tile_url_template]
            if self.tile_source.tile_url_template.startswith("file://"):
                # Convert file URL to relative path for serving
                local_path = self.tile_source.tile_url_template.replace("file://", "")
                tile_urls = [f"/api/tiles/local/{self.tile_source.id}/{{z}}/{{x}}/{{y}}.png"]
            
            style = {
                "version": 8,
                "name": self.tile_source.name,
                "metadata": {
                    "maplibre:logo": "https://maplibre.org/",
                    "mundi:custom_basemap": True,
                    "mundi:basemap_id": self.tile_source.id,
                },
                "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
                "sources": {
                    self.tile_source.id: {
                        "type": "raster",
                        "tiles": tile_urls,
                        "tileSize": self.tile_source.tile_size,
                        "attribution": self.tile_source.attribution,
                        "minzoom": self.tile_source.min_zoom,
                        "maxzoom": self.tile_source.max_zoom,
                    }
                },
                "layers": [
                    {
                        "id": f"{self.tile_source.id}-layer",
                        "type": "raster",
                        "source": self.tile_source.id,
                        "layout": {"visibility": "visible"},
                        "paint": {},
                    }
                ],
            }
        
        # Add bounds if specified
        if self.tile_source.bounds:
            style["sources"][self.tile_source.id]["bounds"] = self.tile_source.bounds
        
        # Set center and zoom
        if self.tile_source.center:
            style["center"] = self.tile_source.center
        else:
            style["center"] = [0, 0]
            
        if self.tile_source.default_zoom is not None:
            style["zoom"] = self.tile_source.default_zoom
        else:
            style["zoom"] = 2
            
        style["bearing"] = 0
        style["pitch"] = 0
        
        return style


class LocalTileMapProvider(CustomTileMapProvider):
    """Provider specifically for local tile directories."""
    
    def __init__(self, tile_directory: str, name: str = "Local Tilemap", 
                 tile_format: str = "png", **kwargs):
        """
        Initialize provider for local tile directory.
        
        Args:
            tile_directory: Path to directory containing tiles in {z}/{x}/{y} structure
            name: Display name for the basemap
            tile_format: File extension for tiles (png, jpg, etc.)
            **kwargs: Additional TileSource parameters
        """
        # Ensure directory exists
        tile_path = Path(tile_directory)
        if not tile_path.exists():
            raise ValueError(f"Tile directory does not exist: {tile_directory}")
        
        # Detect zoom levels if not provided
        if 'min_zoom' not in kwargs or 'max_zoom' not in kwargs:
            zoom_levels = [int(d.name) for d in tile_path.iterdir() if d.is_dir() and d.name.isdigit()]
            if zoom_levels:
                kwargs['min_zoom'] = min(zoom_levels)
                kwargs['max_zoom'] = max(zoom_levels)
        
        tile_source = TileSource(
            id=f"local-{tile_path.name}",
            name=name,
            tile_url_template=f"file://{tile_path.absolute()}/{{z}}/{{x}}/{{y}}.{tile_format}",
            **kwargs
        )
        super().__init__(tile_source)


class FantasyWorldTileProvider(LocalTileMapProvider):
    """Specialized provider for fantasy world raster maps."""
    
    def __init__(self, world_name: str, tile_directory: str, **kwargs):
        """
        Initialize provider for fantasy world tiles.
        
        Args:
            world_name: Name of the fantasy world
            tile_directory: Path to raster tile directory
            **kwargs: Additional configuration
        """
        # Set fantasy world specific defaults
        kwargs.setdefault('attribution', f'© {world_name} Fantasy World')
        kwargs.setdefault('center', [0, 0])  # Center on world origin
        
        super().__init__(
            tile_directory=tile_directory,
            name=f"{world_name} World Map",
            **kwargs
        )