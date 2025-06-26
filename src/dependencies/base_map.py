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
from typing import Dict, Any, Optional, List
import os


class BaseMapProvider(ABC):
    """Abstract base class for base map providers."""

    @abstractmethod
    async def get_base_style(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Return the base MapLibre GL style JSON."""
        pass

    @abstractmethod
    def get_available_styles(self) -> List[str]:
        """Return list of available basemap style names."""
        pass


class OpenStreetMapProvider(BaseMapProvider):
    """Default base map provider using OpenStreetMap tiles."""

    async def get_base_style(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Return a basic MapLibre GL style using OpenStreetMap tiles.

        Args:
            name: Basemap name parameter (ignored in public version)
        """
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

    def get_available_styles(self) -> List[str]:
        """Return list of available basemap style names."""
        return ["openstreetmap"]


class FantasyWorldProvider(BaseMapProvider):
    """Fantasy world base map provider using custom tile sources."""

    async def get_base_style(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Return a MapLibre GL style for fantasy world basemaps.

        Args:
            name: Fantasy world name ("opengeofiction", "custom", etc.)
        """
        # Default to OpenGeofiction if no specific world is requested
        if name is None or name == "opengeofiction":
            return await self._get_opengeofiction_style()
        elif name == "custom":
            return await self._get_custom_fantasy_style()
        else:
            # Fallback to OpenGeofiction for unknown fantasy worlds
            return await self._get_opengeofiction_style()

    async def _get_opengeofiction_style(self) -> Dict[str, Any]:
        """Return OpenGeofiction tile style."""
        # Use local proxy to avoid CORS issues
        base_url = os.environ.get("WEBSITE_DOMAIN", "http://localhost:8000")
        return {
            "version": 8,
            "name": "OpenGeofiction Fantasy World",
            "metadata": {
                "maplibre:logo": "https://maplibre.org/",
            },
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "opengeofiction": {
                    "type": "raster",
                    "tiles": [f"{base_url}/api/basemaps/tiles/opengeofiction/{{z}}/{{x}}/{{y}}.png"],
                    "tileSize": 256,
                    "attribution": "© OpenGeofiction contributors (CC BY-NC-SA 3.0)",
                    "maxzoom": 19,
                }
            },
            "layers": [
                {
                    "id": "opengeofiction",
                    "type": "raster",
                    "source": "opengeofiction",
                    "layout": {"visibility": "visible"},
                    "paint": {},
                }
            ],
            "center": [0, 0],
            "zoom": 2,
            "bearing": 0,
            "pitch": 0,
        }

    async def _get_custom_fantasy_style(self) -> Dict[str, Any]:
        """Return custom fantasy world tile style."""
        # Check if we have a custom tile server running
        tile_server_url = os.environ.get("FANTASY_TILE_SERVER_URL", "http://localhost:3000")
        
        return {
            "version": 8,
            "name": "Custom Fantasy World",
            "metadata": {
                "maplibre:logo": "https://maplibre.org/",
            },
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "custom_fantasy": {
                    "type": "vector",
                    "tiles": [f"{tile_server_url}/tiles/{{z}}/{{x}}/{{y}}.pbf"],
                    "attribution": "© Custom Fantasy World",
                    "maxzoom": 19,
                }
            },
            "layers": [
                # Land and water layers
                {
                    "id": "land",
                    "type": "fill",
                    "source": "custom_fantasy",
                    "source-layer": "land",
                    "layout": {"visibility": "visible"},
                    "paint": {
                        "fill-color": "#f8f4e6",
                        "fill-opacity": 1
                    }
                },
                {
                    "id": "water",
                    "type": "fill",
                    "source": "custom_fantasy",
                    "source-layer": "water",
                    "layout": {"visibility": "visible"},
                    "paint": {
                        "fill-color": "#4a90e2",
                        "fill-opacity": 0.7
                    }
                },
                # Enchanted forests with special styling
                {
                    "id": "enchanted-forest",
                    "type": "fill",
                    "source": "custom_fantasy",
                    "source-layer": "landuse",
                    "filter": ["==", ["get", "fantasy:enchanted"], "yes"],
                    "layout": {"visibility": "visible"},
                    "paint": {
                        "fill-color": "#2d8659",
                        "fill-opacity": 0.8,
                        "fill-pattern": "forest-enchanted"
                    }
                },
                # Roads and paths
                {
                    "id": "roads",
                    "type": "line",
                    "source": "custom_fantasy",
                    "source-layer": "transportation",
                    "layout": {"visibility": "visible"},
                    "paint": {
                        "line-color": "#8b4513",
                        "line-width": {
                            "base": 1.2,
                            "stops": [[6, 0.5], [10, 1], [14, 2]]
                        }
                    }
                },
                # Fantasy buildings
                {
                    "id": "castles",
                    "type": "fill",
                    "source": "custom_fantasy",
                    "source-layer": "buildings",
                    "filter": ["==", ["get", "building"], "castle"],
                    "layout": {"visibility": "visible"},
                    "paint": {
                        "fill-color": "#8b7355",
                        "fill-opacity": 0.9,
                        "fill-outline-color": "#5d4e37"
                    }
                },
                # Place labels
                {
                    "id": "place-labels",
                    "type": "symbol",
                    "source": "custom_fantasy",
                    "source-layer": "places",
                    "layout": {
                        "text-field": ["get", "name"],
                        "text-font": ["Open Sans Regular"],
                        "text-size": {
                            "base": 1.2,
                            "stops": [[6, 10], [10, 14], [14, 18]]
                        },
                        "text-anchor": "center"
                    },
                    "paint": {
                        "text-color": "#2c1810",
                        "text-halo-color": "#f8f4e6",
                        "text-halo-width": 1
                    }
                }
            ],
            "center": [0, 0],
            "zoom": 2,
            "bearing": 0,
            "pitch": 0,
        }

    def get_available_styles(self) -> List[str]:
        """Return list of available fantasy basemap style names."""
        styles = ["opengeofiction"]
        
        # Check if custom fantasy tile server is available
        if os.environ.get("FANTASY_TILE_SERVER_URL"):
            styles.append("custom")
            
        return styles


# Default dependency - can be overridden in closed source
def get_base_map_provider() -> BaseMapProvider:
    """Default base map provider dependency."""
    # Check if fantasy mode is enabled via environment variable
    if os.environ.get("MUNDI_BASEMAP_MODE", "osm").lower() == "fantasy":
        return FantasyWorldProvider()
    else:
        return OpenStreetMapProvider()

def get_fantasy_map_provider() -> FantasyWorldProvider:
    """Fantasy world base map provider dependency."""
    return FantasyWorldProvider()
