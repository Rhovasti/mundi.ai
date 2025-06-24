// Copyright Bunting Labs, Inc. 2025

export interface MapProject {
  id: string;
  owner_uuid: string;
  link_accessible: boolean;
  maps: string[];
  created_on: string;
  most_recent_version?: {
    title?: string;
    description?: string;
    last_edited?: string;
  };
  postgres_connections?: PostgresConnectionDetails[];
}

export type ProjectState =
  | { type: 'not_logged_in' }
  | { type: 'loading' }
  | { type: 'loaded'; projects: MapProject[] };

export interface MapLayer {
  id: string;
  name: string;
  path: string;
  type: string;
  raster_cog_url?: string;
  metadata?: Record<string, unknown>;
  bounds?: number[];
  geometry_type?: string;
  feature_count?: number;
}

export interface PostgresConnectionDetails {
  connection_id: string;
  table_count: number;
  friendly_name: string;
}

export interface MapData {
  map_id: string;
  project_id: string;
  layers: MapLayer[];
  changelog: Array<{
    message: string;
    map_state: string;
    last_edited: string;
  }>;
  display_as_diff: boolean;
  diff?: MapDiff;
}

export interface LayerDiff {
  layer_id: string;
  name: string;
  status: string; // 'added', 'removed', 'edited', 'existing'
  changes?: {
    [key: string]: {
      old: string | object | null;
      new: string | object | null;
    };
  };
}

export interface MapDiff {
  prev_map_id?: string;
  new_map_id: string;
  layer_diffs: LayerDiff[];
}

export interface PointerPosition {
  lng: number;
  lat: number;
}

export interface PresenceData {
  value: PointerPosition;
  lastSeen: number;
}

export interface EphemeralUpdates {
  style_json: boolean;
}

export interface EphemeralAction {
  map_id: string;
  ephemeral: boolean;
  action_id: string;
  layer_id: string | null;
  action: string;
  timestamp: string;
  completed_at: string | null;
  status: "active" | "completed" | "zoom_action";
  updates: EphemeralUpdates;
  bounds?: [number, number, number, number];
  description?: string;
}

export interface CustomBasemap {
  id: string;
  name: string;
  tile_url_template: string;
  tile_format: string;
  min_zoom: number;
  max_zoom: number;
  tile_size: number;
  attribution: string;
  bounds?: [number, number, number, number] | null;
  center?: [number, number] | null;
  default_zoom?: number | null;
  is_public: boolean;
  metadata?: any;
  owner_uuid: string;
  created_at: string;
  updated_at: string;
  type?: 'raster' | 'vector'; // Derived field
  world_model_id?: string | null;
  georeferencing_points?: any[] | null;
  transform_matrix?: number[] | null;
}

export interface WorldModel {
  id: string;
  name: string;
  description?: string | null;
  planet_scale_factor: number;
  extent_bounds?: [number, number, number, number] | null;
  crs_definition?: string | null;
  transformation_matrix?: number[] | null;
  default_center?: [number, number] | null;
  default_zoom: number;
  earth_radius?: number | null;
  coordinate_system_notes?: string | null;
  is_default: boolean;
  is_public: boolean;
  owner_uuid: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}
