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

from typing import Dict, Any, List
from pydantic import BaseModel


class VectorLayerStyle(BaseModel):
    """Style configuration for a vector layer."""
    id: str
    name: str
    type: str  # 'circle', 'line', 'fill', 'symbol'
    paint: Dict[str, Any]
    layout: Dict[str, Any] = {"visibility": "visible"}
    minzoom: int = 0
    maxzoom: int = 22
    metadata: Dict[str, Any] = {}


# Default styles for Eno fantasy world vector layers
ENO_VECTOR_STYLES = {
    "cities": [
        VectorLayerStyle(
            id="eno-cities-layer",
            name="Eno Cities",
            type="circle",
            paint={
                "circle-radius": [
                    "interpolate",
                    ["linear"],
                    ["get", "Population"],
                    0, 4,
                    10000, 6,
                    50000, 10,
                    100000, 14
                ],
                "circle-color": [
                    "case",
                    ["==", ["get", "Capital"], "capital"], "#e74c3c",
                    ["==", ["get", "Port"], "port"], "#3498db",
                    "#ff6b6b"
                ],
                "circle-stroke-color": "#ffffff",
                "circle-stroke-width": 2,
                "circle-opacity": 0.9
            },
            minzoom=3
        ),
        VectorLayerStyle(
            id="eno-cities-labels",
            name="Eno City Labels",
            type="symbol",
            layout={
                "text-field": ["get", "Burg"],
                "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                "text-offset": [0, 1.5],
                "text-anchor": "top",
                "text-size": [
                    "interpolate",
                    ["linear"],
                    ["get", "Population"],
                    0, 10,
                    10000, 12,
                    50000, 14,
                    100000, 16
                ],
                "visibility": "visible"
            },
            paint={
                "text-color": "#2c3e50",
                "text-halo-color": "#ffffff",
                "text-halo-width": 2
            },
            minzoom=5
        )
    ],
    "villages": [
        VectorLayerStyle(
            id="eno-villages-layer",
            name="Eno Villages",
            type="circle",
            paint={
                "circle-radius": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    0, 2,
                    8, 4
                ],
                "circle-color": "#ffa500",
                "circle-stroke-color": "#ffffff",
                "circle-stroke-width": 1,
                "circle-opacity": 0.9
            },
            minzoom=5
        )
    ],
    "rivers": [
        VectorLayerStyle(
            id="eno-rivers-layer",
            name="Eno Rivers",
            type="line",
            paint={
                "line-color": "#1e90ff",
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    0, 1,
                    8, 3
                ],
                "line-opacity": 0.8
            }
        )
    ],
    "lakes": [
        VectorLayerStyle(
            id="eno-lakes-layer",
            name="Eno Lakes",
            type="fill",
            paint={
                "fill-color": "#4682b4",
                "fill-opacity": 0.7,
                "fill-outline-color": "#1e90ff"
            }
        )
    ],
    "roads": [
        VectorLayerStyle(
            id="eno-roads-layer",
            name="Eno Roads",
            type="line",
            paint={
                "line-color": "#8b4513",
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    0, 0.5,
                    8, 2
                ],
                "line-opacity": 0.7
            },
            minzoom=4
        )
    ],
    "biomes": [
        VectorLayerStyle(
            id="eno-biomes-layer",
            name="Eno Biomes",
            type="fill",
            paint={
                "fill-color": [
                    "case",
                    ["==", ["get", "name"], "Forest"], "#228b22",
                    ["==", ["get", "name"], "Desert"], "#edc9af",
                    ["==", ["get", "name"], "Mountains"], "#8b7355",
                    ["==", ["get", "name"], "Grassland"], "#90ee90",
                    ["==", ["get", "name"], "Tundra"], "#dcdcdc",
                    ["==", ["get", "name"], "Swamp"], "#556b2f",
                    "#a0522d"  # default brown
                ],
                "fill-opacity": 0.25
            }
        )
    ],
    "states": [
        VectorLayerStyle(
            id="eno-states-layer",
            name="Eno States",
            type="fill",
            paint={
                "fill-color": "#ff6b6b",
                "fill-opacity": 0.1,
                "fill-outline-color": "#8b0000"
            }
        ),
        VectorLayerStyle(
            id="eno-states-labels",
            name="Eno State Labels",
            type="symbol",
            layout={
                "text-field": ["get", "State"],
                "text-font": ["Open Sans Bold", "Arial Unicode MS Bold"],
                "text-size": 14,
                "text-transform": "uppercase",
                "text-letter-spacing": 0.1,
                "visibility": "visible"
            },
            paint={
                "text-color": "#8b0000",
                "text-halo-color": "#ffffff",
                "text-halo-width": 1
            },
            minzoom=3,
            maxzoom=7
        )
    ]
}


def get_vector_layer_styles(layer_id: str) -> List[Dict[str, Any]]:
    """Get MapLibre-compatible styles for a vector layer."""
    styles = ENO_VECTOR_STYLES.get(layer_id, [])
    return [style.dict(exclude_none=True) for style in styles]


def get_all_vector_styles() -> Dict[str, List[Dict[str, Any]]]:
    """Get all vector layer styles."""
    return {
        layer_id: get_vector_layer_styles(layer_id)
        for layer_id in ENO_VECTOR_STYLES.keys()
    }


# Layer ordering (bottom to top)
LAYER_ORDER = [
    # Polygon layers (bottom)
    "eno-biomes-layer",
    "eno-states-layer",
    "eno-lakes-layer",
    # Line layers (middle)
    "eno-rivers-layer",
    "eno-roads-layer",
    # Point layers (top)
    "eno-villages-layer",
    "eno-cities-layer",
    # Label layers (topmost)
    "eno-states-labels",
    "eno-cities-labels"
]