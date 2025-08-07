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

    @abstractmethod
    def get_csp_policies(self) -> Dict[str, List[str]]:
        """Return CSP policies required for this base map provider.

        Returns:
            Dict mapping CSP directive names to lists of allowed sources.
            Common directives: connect-src, img-src, font-src, style-src, script-src
        """
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

    def get_csp_policies(self) -> Dict[str, List[str]]:
        """Return CSP policies required for OpenStreetMap tiles."""
        return {
            "connect-src": [
                "https://tile.openstreetmap.org",
                "https://demotiles.maplibre.org",
            ],
            "img-src": [
                "https://tile.openstreetmap.org",
                "https://demotiles.maplibre.org",
            ],
            "font-src": ["https://demotiles.maplibre.org"],
        }


class CustomBasemapProvider(BaseMapProvider):
    """Provider for user-defined custom basemaps."""
    
    def __init__(self, basemaps: List[Dict[str, Any]] = None):
        """Initialize with a list of custom basemaps."""
        self.basemaps = basemaps or []
        self.default_provider = OpenStreetMapProvider()
    
    async def get_base_style(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Return the style for a custom basemap or fall back to default."""
        if not name:
            # Return default OSM if no name specified
            return await self.default_provider.get_base_style()
        
        # Check if it's a preset basemap
        preset = self._get_preset_basemap(name)
        if preset:
            return preset
        
        # Look for custom basemap
        for basemap in self.basemaps:
            if basemap.get('id') == name or basemap.get('name') == name:
                config = basemap.get('config', {})
                basemap_type = basemap.get('type', 'xyz')
                
                if basemap_type == 'style_json':
                    # Return the style JSON directly
                    return config.get('style', await self.default_provider.get_base_style())
                
                elif basemap_type == 'xyz':
                    # Generate style from XYZ tile template
                    return self._generate_xyz_style(basemap)
                
                elif basemap_type == 'wms':
                    # Generate style for WMS
                    return self._generate_wms_style(basemap)
                
                elif basemap_type == 'wmts':
                    # Generate style for WMTS
                    return self._generate_wmts_style(basemap)
        
        # Fall back to OpenStreetMap if not found
        return await self.default_provider.get_base_style()
    
    def get_available_styles(self) -> List[str]:
        """Return list of available basemap style names."""
        styles = ['openstreetmap']  # Always include default
        
        # Add preset basemaps
        styles.extend(self._get_preset_names())
        
        # Add custom basemap IDs
        for basemap in self.basemaps:
            styles.append(basemap.get('id', basemap.get('name', '')))
        
        return styles
    
    def get_csp_policies(self) -> Dict[str, List[str]]:
        """Return CSP policies required for all configured basemaps."""
        policies = self.default_provider.get_csp_policies()
        
        # Add policies for custom basemaps
        for basemap in self.basemaps:
            config = basemap.get('config', {})
            url = config.get('url', '')
            
            if url:
                # Extract domain from URL
                from urllib.parse import urlparse
                parsed = urlparse(url)
                if parsed.netloc:
                    domain = f"{parsed.scheme}://{parsed.netloc}"
                    
                    # Add to connect-src and img-src
                    if 'connect-src' not in policies:
                        policies['connect-src'] = []
                    if 'img-src' not in policies:
                        policies['img-src'] = []
                    
                    if domain not in policies['connect-src']:
                        policies['connect-src'].append(domain)
                    if domain not in policies['img-src']:
                        policies['img-src'].append(domain)
        
        return policies
    
    def _generate_xyz_style(self, basemap: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MapLibre style from XYZ tile configuration."""
        config = basemap.get('config', {})
        name = basemap.get('name', 'Custom Basemap')
        
        return {
            "version": 8,
            "name": name,
            "metadata": {
                "maplibre:logo": "https://maplibre.org/",
            },
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "custom": {
                    "type": "raster",
                    "tiles": [config.get('url', 'https://tile.openstreetmap.org/{z}/{x}/{y}.png')],
                    "tileSize": config.get('tileSize', 256),
                    "attribution": basemap.get('attribution', config.get('attribution', '')),
                    "minzoom": basemap.get('min_zoom', 0),
                    "maxzoom": basemap.get('max_zoom', 22),
                }
            },
            "layers": [
                {
                    "id": "custom",
                    "type": "raster",
                    "source": "custom",
                    "layout": {"visibility": "visible"},
                    "paint": {},
                }
            ],
            "center": [0, 0],
            "zoom": 2,
            "bearing": 0,
            "pitch": 0,
        }
    
    def _generate_wms_style(self, basemap: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MapLibre style from WMS configuration."""
        config = basemap.get('config', {})
        name = basemap.get('name', 'WMS Basemap')
        
        # Build WMS URL
        base_url = config.get('url', '')
        layers = config.get('layers', '')
        styles = config.get('styles', '')
        format = config.get('format', 'image/png')
        version = config.get('version', '1.3.0')
        crs = config.get('crs', 'EPSG:3857')
        
        # Construct WMS tile URL template
        wms_url = f"{base_url}?SERVICE=WMS&VERSION={version}&REQUEST=GetMap"
        wms_url += f"&LAYERS={layers}&STYLES={styles}&FORMAT={format}"
        wms_url += f"&CRS={crs}&WIDTH=256&HEIGHT=256"
        wms_url += "&BBOX={bbox-epsg-3857}"  # MapLibre will replace this
        
        return {
            "version": 8,
            "name": name,
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "wms": {
                    "type": "raster",
                    "tiles": [wms_url],
                    "tileSize": 256,
                    "attribution": basemap.get('attribution', ''),
                }
            },
            "layers": [
                {
                    "id": "wms",
                    "type": "raster",
                    "source": "wms",
                }
            ],
            "center": [0, 0],
            "zoom": 2,
        }
    
    def _generate_wmts_style(self, basemap: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MapLibre style from WMTS configuration."""
        # Similar to WMS but uses WMTS GetTile request
        config = basemap.get('config', {})
        name = basemap.get('name', 'WMTS Basemap')
        
        return self._generate_xyz_style(basemap)  # WMTS can often be treated as XYZ
    
    def _get_preset_basemap(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a preset basemap configuration."""
        presets = {
            "openstreetmap": None,  # Use default provider
            "carto-light": self._carto_light_style(),
            "carto-dark": self._carto_dark_style(),
            "stamen-terrain": self._stamen_terrain_style(),
            "stamen-watercolor": self._stamen_watercolor_style(),
            "esri-satellite": self._esri_satellite_style(),
        }
        
        return presets.get(name)
    
    def _get_preset_names(self) -> List[str]:
        """Get list of preset basemap names."""
        return ["carto-light", "carto-dark", "stamen-terrain", "stamen-watercolor", "esri-satellite"]
    
    def _carto_light_style(self) -> Dict[str, Any]:
        """Carto Light basemap style."""
        return {
            "version": 8,
            "name": "Carto Light",
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "carto": {
                    "type": "raster",
                    "tiles": ["https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"],
                    "tileSize": 256,
                    "attribution": "© CARTO © OpenStreetMap contributors",
                    "maxzoom": 19,
                }
            },
            "layers": [
                {
                    "id": "carto",
                    "type": "raster",
                    "source": "carto",
                }
            ],
            "center": [0, 0],
            "zoom": 2,
        }
    
    def _carto_dark_style(self) -> Dict[str, Any]:
        """Carto Dark basemap style."""
        return {
            "version": 8,
            "name": "Carto Dark",
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "carto": {
                    "type": "raster",
                    "tiles": ["https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"],
                    "tileSize": 256,
                    "attribution": "© CARTO © OpenStreetMap contributors",
                    "maxzoom": 19,
                }
            },
            "layers": [
                {
                    "id": "carto",
                    "type": "raster",
                    "source": "carto",
                }
            ],
            "center": [0, 0],
            "zoom": 2,
        }
    
    def _stamen_terrain_style(self) -> Dict[str, Any]:
        """Stamen Terrain basemap style."""
        return {
            "version": 8,
            "name": "Stamen Terrain",
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "stamen": {
                    "type": "raster",
                    "tiles": ["https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png"],
                    "tileSize": 256,
                    "attribution": "© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors",
                    "maxzoom": 18,
                }
            },
            "layers": [
                {
                    "id": "stamen",
                    "type": "raster",
                    "source": "stamen",
                }
            ],
            "center": [0, 0],
            "zoom": 2,
        }
    
    def _stamen_watercolor_style(self) -> Dict[str, Any]:
        """Stamen Watercolor basemap style."""
        return {
            "version": 8,
            "name": "Stamen Watercolor",
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "stamen": {
                    "type": "raster",
                    "tiles": ["https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg"],
                    "tileSize": 256,
                    "attribution": "© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors",
                    "maxzoom": 16,
                }
            },
            "layers": [
                {
                    "id": "stamen",
                    "type": "raster",
                    "source": "stamen",
                }
            ],
            "center": [0, 0],
            "zoom": 2,
        }
    
    def _esri_satellite_style(self) -> Dict[str, Any]:
        """ESRI Satellite imagery basemap style."""
        return {
            "version": 8,
            "name": "ESRI Satellite",
            "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
            "sources": {
                "esri": {
                    "type": "raster",
                    "tiles": [
                        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    ],
                    "tileSize": 256,
                    "attribution": "© Esri, Maxar, Earthstar Geographics, and the GIS User Community",
                    "maxzoom": 19,
                }
            },
            "layers": [
                {
                    "id": "esri",
                    "type": "raster",
                    "source": "esri",
                }
            ],
            "center": [0, 0],
            "zoom": 2,
        }


# Default dependency - can be overridden in closed source
def get_base_map_provider() -> BaseMapProvider:
    """Default base map provider dependency."""
    return OpenStreetMapProvider()
