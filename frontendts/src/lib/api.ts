// Copyright Bunting Labs, Inc. 2025

import { CustomBasemap, WorldModel } from './types';

const API_BASE_URL = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';

export async function fetchCustomBasemaps(): Promise<CustomBasemap[]> {
  const response = await fetch(`${API_BASE_URL}/api/basemaps`);
  if (!response.ok) {
    throw new Error(`Failed to fetch basemaps: ${response.statusText}`);
  }
  const basemaps = await response.json();
  
  // Derive type based on tile_format and metadata
  return basemaps.map((basemap: any) => ({
    ...basemap,
    type: deriveBasemapType(basemap)
  }));
}

function deriveBasemapType(basemap: any): 'raster' | 'vector' {
  // Check metadata for explicit type
  if (basemap.metadata?.type === 'vector') {
    return 'vector';
  }
  
  // Check tile format
  if (basemap.tile_format === 'json' || basemap.tile_format === 'geojson') {
    return 'vector';
  }
  
  // Default to raster for image formats
  return 'raster';
}

export function getBasemapTileUrl(basemap: CustomBasemap): string {
  let tileUrl = basemap.tile_url_template;
  
  // Handle different URL schemes
  if (tileUrl.startsWith('file://') || tileUrl.startsWith('geojson://')) {
    // File and GeoJSON URLs need to be served through our backend
    if (basemap.type === 'vector') {
      return `${API_BASE_URL}/api/basemaps/${basemap.id}/vector/{z}/{x}/{y}.json`;
    } else {
      // Use the correct tile format from the basemap
      const format = basemap.tile_format || 'png';
      return `${API_BASE_URL}/api/tiles/local/${basemap.id}/{z}/{x}/{y}.${format}`;
    }
  }
  
  // Replace {basemap_id} placeholder if present
  if (tileUrl.includes('{basemap_id}')) {
    tileUrl = tileUrl.replace('{basemap_id}', basemap.id);
  }
  
  // If it's a relative URL starting with /api, prepend the API base URL
  if (tileUrl.startsWith('/api')) {
    tileUrl = `${API_BASE_URL}${tileUrl}`;
  }
  
  return tileUrl;
}

export async function fetchWorldModels(): Promise<WorldModel[]> {
  const response = await fetch(`${API_BASE_URL}/api/world-models`);
  if (!response.ok) {
    throw new Error(`Failed to fetch world models: ${response.statusText}`);
  }
  return await response.json();
}

export async function fetchWorldModel(id: string): Promise<WorldModel> {
  const response = await fetch(`${API_BASE_URL}/api/world-models/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch world model: ${response.statusText}`);
  }
  return await response.json();
}

export async function getWorldModelBounds(id: string): Promise<{
  bounds?: [number, number, number, number] | null;
  center?: [number, number] | null;
  zoom: number;
  planet_scale_factor: number;
  earth_radius?: number | null;
}> {
  const response = await fetch(`${API_BASE_URL}/api/world-models/${id}/bounds`);
  if (!response.ok) {
    throw new Error(`Failed to fetch world model bounds: ${response.statusText}`);
  }
  return await response.json();
}