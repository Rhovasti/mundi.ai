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

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from uuid import UUID
import secrets
import string

from src.structures import async_conn
from src.dependencies.base_map import CustomBasemapProvider
from src.dependencies.session import session_user_id

# Create router for custom basemap endpoints
custom_basemap_router = APIRouter()


class BasemapConfig(BaseModel):
    """Configuration for a basemap"""
    url: Optional[str] = Field(None, description="URL template for tiles")
    tileSize: Optional[int] = Field(256, description="Tile size in pixels")
    attribution: Optional[str] = Field(None, description="Attribution text")
    layers: Optional[str] = Field(None, description="WMS/WMTS layers")
    styles: Optional[str] = Field(None, description="WMS/WMTS styles")
    format: Optional[str] = Field(None, description="Image format")
    version: Optional[str] = Field(None, description="Service version")
    crs: Optional[str] = Field(None, description="Coordinate reference system")
    style: Optional[Dict[str, Any]] = Field(None, description="Full MapLibre style JSON")


class CreateBasemapRequest(BaseModel):
    """Request to create a new custom basemap"""
    name: str = Field(..., description="Display name for the basemap")
    description: Optional[str] = Field(None, description="Description of the basemap")
    type: str = Field("xyz", description="Type of basemap: xyz, wms, wmts, style_json")
    config: BasemapConfig = Field(..., description="Basemap configuration")
    project_id: Optional[str] = Field(None, description="Project ID to associate with")
    is_public: bool = Field(False, description="Whether basemap is publicly accessible")
    attribution: Optional[str] = Field(None, description="Attribution text")
    min_zoom: Optional[int] = Field(0, description="Minimum zoom level")
    max_zoom: Optional[int] = Field(22, description="Maximum zoom level")


class UpdateBasemapRequest(BaseModel):
    """Request to update a custom basemap"""
    name: Optional[str] = Field(None, description="Display name for the basemap")
    description: Optional[str] = Field(None, description="Description of the basemap")
    config: Optional[BasemapConfig] = Field(None, description="Basemap configuration")
    is_public: Optional[bool] = Field(None, description="Whether basemap is publicly accessible")
    attribution: Optional[str] = Field(None, description="Attribution text")
    min_zoom: Optional[int] = Field(None, description="Minimum zoom level")
    max_zoom: Optional[int] = Field(None, description="Maximum zoom level")


class BasemapResponse(BaseModel):
    """Response containing basemap information"""
    id: str
    name: str
    description: Optional[str]
    type: str
    config: Dict[str, Any]
    thumbnail_url: Optional[str]
    owner_uuid: str
    project_id: Optional[str]
    is_public: bool
    is_default: bool
    attribution: Optional[str]
    min_zoom: int
    max_zoom: int
    created_at: str
    updated_at: str


def generate_basemap_id() -> str:
    """Generate a unique basemap ID starting with 'B'"""
    # Generate 11 random characters
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(11))
    return f"B{random_part}"


@custom_basemap_router.post("/custom", response_model=BasemapResponse)
async def create_custom_basemap(
    request: CreateBasemapRequest,
    current_user: str = Depends(session_user_id),
):
    """Create a new custom basemap"""
    basemap_id = generate_basemap_id()
    
    async with async_conn("create_custom_basemap") as conn:
        # If project_id is provided, verify user has access to it
        if request.project_id:
            project = await conn.fetchrow(
                """
                SELECT id FROM user_mundiai_projects 
                WHERE id = $1 AND (
                    owner_uuid = $2 OR 
                    $2 = ANY(editor_uuids) OR 
                    link_accessible = true
                )
                AND soft_deleted_at IS NULL
                """,
                request.project_id,
                current_user,
            )
            if not project:
                raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        # Insert the new basemap
        result = await conn.fetchrow(
            """
            INSERT INTO custom_basemaps (
                id, name, description, type, config, 
                owner_uuid, project_id, is_public, attribution,
                min_zoom, max_zoom
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
            """,
            basemap_id,
            request.name,
            request.description,
            request.type,
            request.config.dict(),
            current_user,
            request.project_id,
            request.is_public,
            request.attribution,
            request.min_zoom or 0,
            request.max_zoom or 22,
        )
        
        return BasemapResponse(
            id=result["id"],
            name=result["name"],
            description=result["description"],
            type=result["type"],
            config=result["config"],
            thumbnail_url=result["thumbnail_url"],
            owner_uuid=str(result["owner_uuid"]),
            project_id=result["project_id"],
            is_public=result["is_public"],
            is_default=result["is_default"],
            attribution=result["attribution"],
            min_zoom=result["min_zoom"],
            max_zoom=result["max_zoom"],
            created_at=result["created_at"].isoformat(),
            updated_at=result["updated_at"].isoformat(),
        )


@custom_basemap_router.get("/custom", response_model=List[BasemapResponse])
async def list_custom_basemaps(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    include_public: bool = Query(True, description="Include public basemaps"),
    include_defaults: bool = Query(True, description="Include default basemaps"),
    current_user: str = Depends(session_user_id),
):
    """List custom basemaps accessible to the current user"""
    async with async_conn("list_custom_basemaps") as conn:
        # Build query conditions
        conditions = []
        params = []
        param_count = 0
        
        if current_user:
            param_count += 1
            params.append(current_user)
            if include_public:
                conditions.append(f"(owner_uuid = ${param_count} OR is_public = true)")
            else:
                conditions.append(f"owner_uuid = ${param_count}")
        else:
            # Anonymous users can only see public basemaps
            conditions.append("is_public = true")
        
        if not include_defaults:
            conditions.append("is_default = false")
        
        if project_id:
            param_count += 1
            params.append(project_id)
            conditions.append(f"(project_id = ${param_count} OR project_id IS NULL)")
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        query = f"""
            SELECT * FROM custom_basemaps 
            WHERE {where_clause}
            ORDER BY 
                is_default DESC,
                is_public DESC,
                created_at DESC
        """
        
        results = await conn.fetch(query, *params)
        
        return [
            BasemapResponse(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                type=row["type"],
                config=row["config"],
                thumbnail_url=row["thumbnail_url"],
                owner_uuid=str(row["owner_uuid"]),
                project_id=row["project_id"],
                is_public=row["is_public"],
                is_default=row["is_default"],
                attribution=row["attribution"],
                min_zoom=row["min_zoom"],
                max_zoom=row["max_zoom"],
                created_at=row["created_at"].isoformat(),
                updated_at=row["updated_at"].isoformat(),
            )
            for row in results
        ]


@custom_basemap_router.get("/custom/{basemap_id}", response_model=BasemapResponse)
async def get_custom_basemap(
    basemap_id: str,
    current_user: str = Depends(session_user_id),
):
    """Get a specific custom basemap by ID"""
    async with async_conn("get_custom_basemap") as conn:
        # Fetch basemap if user has access
        if current_user:
            result = await conn.fetchrow(
                """
                SELECT * FROM custom_basemaps 
                WHERE id = $1 AND (
                    owner_uuid = $2 OR 
                    is_public = true OR
                    is_default = true
                )
                """,
                basemap_id,
                current_user,
            )
        else:
            # Anonymous users can only see public basemaps
            result = await conn.fetchrow(
                """
                SELECT * FROM custom_basemaps 
                WHERE id = $1 AND (is_public = true OR is_default = true)
                """,
                basemap_id,
            )
        
        if not result:
            raise HTTPException(status_code=404, detail="Basemap not found or access denied")
        
        return BasemapResponse(
            id=result["id"],
            name=result["name"],
            description=result["description"],
            type=result["type"],
            config=result["config"],
            thumbnail_url=result["thumbnail_url"],
            owner_uuid=str(result["owner_uuid"]),
            project_id=result["project_id"],
            is_public=result["is_public"],
            is_default=result["is_default"],
            attribution=result["attribution"],
            min_zoom=result["min_zoom"],
            max_zoom=result["max_zoom"],
            created_at=result["created_at"].isoformat(),
            updated_at=result["updated_at"].isoformat(),
        )


@custom_basemap_router.put("/custom/{basemap_id}", response_model=BasemapResponse)
async def update_custom_basemap(
    basemap_id: str,
    request: UpdateBasemapRequest,
    current_user: str = Depends(session_user_id),
):
    """Update a custom basemap"""
    async with async_conn("update_custom_basemap") as conn:
        # Check if user owns the basemap
        existing = await conn.fetchrow(
            """
            SELECT * FROM custom_basemaps 
            WHERE id = $1 AND owner_uuid = $2
            """,
            basemap_id,
            current_user,
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Basemap not found or access denied")
        
        # Build update query dynamically
        updates = []
        params = [basemap_id]
        param_count = 1
        
        if request.name is not None:
            param_count += 1
            params.append(request.name)
            updates.append(f"name = ${param_count}")
        
        if request.description is not None:
            param_count += 1
            params.append(request.description)
            updates.append(f"description = ${param_count}")
        
        if request.config is not None:
            param_count += 1
            params.append(request.config.dict())
            updates.append(f"config = ${param_count}")
        
        if request.is_public is not None:
            param_count += 1
            params.append(request.is_public)
            updates.append(f"is_public = ${param_count}")
        
        if request.attribution is not None:
            param_count += 1
            params.append(request.attribution)
            updates.append(f"attribution = ${param_count}")
        
        if request.min_zoom is not None:
            param_count += 1
            params.append(request.min_zoom)
            updates.append(f"min_zoom = ${param_count}")
        
        if request.max_zoom is not None:
            param_count += 1
            params.append(request.max_zoom)
            updates.append(f"max_zoom = ${param_count}")
        
        if not updates:
            # No updates provided, return existing
            return BasemapResponse(
                id=existing["id"],
                name=existing["name"],
                description=existing["description"],
                type=existing["type"],
                config=existing["config"],
                thumbnail_url=existing["thumbnail_url"],
                owner_uuid=str(existing["owner_uuid"]),
                project_id=existing["project_id"],
                is_public=existing["is_public"],
                is_default=existing["is_default"],
                attribution=existing["attribution"],
                min_zoom=existing["min_zoom"],
                max_zoom=existing["max_zoom"],
                created_at=existing["created_at"].isoformat(),
                updated_at=existing["updated_at"].isoformat(),
            )
        
        # Add updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        update_query = f"""
            UPDATE custom_basemaps 
            SET {', '.join(updates)}
            WHERE id = $1
            RETURNING *
        """
        
        result = await conn.fetchrow(update_query, *params)
        
        return BasemapResponse(
            id=result["id"],
            name=result["name"],
            description=result["description"],
            type=result["type"],
            config=result["config"],
            thumbnail_url=result["thumbnail_url"],
            owner_uuid=str(result["owner_uuid"]),
            project_id=result["project_id"],
            is_public=result["is_public"],
            is_default=result["is_default"],
            attribution=result["attribution"],
            min_zoom=result["min_zoom"],
            max_zoom=result["max_zoom"],
            created_at=result["created_at"].isoformat(),
            updated_at=result["updated_at"].isoformat(),
        )


@custom_basemap_router.delete("/custom/{basemap_id}")
async def delete_custom_basemap(
    basemap_id: str,
    current_user: str = Depends(session_user_id),
):
    """Delete a custom basemap"""
    async with async_conn("delete_custom_basemap") as conn:
        # Check if user owns the basemap
        existing = await conn.fetchrow(
            """
            SELECT id FROM custom_basemaps 
            WHERE id = $1 AND owner_uuid = $2
            """,
            basemap_id,
            current_user,
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Basemap not found or access denied")
        
        # Delete the basemap
        await conn.execute(
            "DELETE FROM custom_basemaps WHERE id = $1",
            basemap_id,
        )
        
        return {"message": "Basemap deleted successfully"}


@custom_basemap_router.get("/presets", response_model=List[Dict[str, Any]])
async def get_preset_basemaps():
    """Get list of available preset basemap templates"""
    presets = [
        {
            "id": "openstreetmap",
            "name": "OpenStreetMap",
            "description": "Standard OpenStreetMap tiles",
            "type": "xyz",
            "thumbnail": "/api/basemaps/presets/openstreetmap/thumbnail",
            "config": {
                "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attribution": "© OpenStreetMap contributors",
                "maxZoom": 19,
            }
        },
        {
            "id": "carto-light",
            "name": "Carto Light",
            "description": "Light themed basemap from CARTO",
            "type": "xyz",
            "thumbnail": "/api/basemaps/presets/carto-light/thumbnail",
            "config": {
                "url": "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                "attribution": "© CARTO © OpenStreetMap contributors",
                "maxZoom": 19,
            }
        },
        {
            "id": "carto-dark",
            "name": "Carto Dark",
            "description": "Dark themed basemap from CARTO",
            "type": "xyz",
            "thumbnail": "/api/basemaps/presets/carto-dark/thumbnail",
            "config": {
                "url": "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
                "attribution": "© CARTO © OpenStreetMap contributors",
                "maxZoom": 19,
            }
        },
        {
            "id": "stamen-terrain",
            "name": "Stamen Terrain",
            "description": "Terrain visualization from Stamen Design",
            "type": "xyz",
            "thumbnail": "/api/basemaps/presets/stamen-terrain/thumbnail",
            "config": {
                "url": "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png",
                "attribution": "© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors",
                "maxZoom": 18,
            }
        },
        {
            "id": "stamen-watercolor",
            "name": "Stamen Watercolor",
            "description": "Artistic watercolor style map",
            "type": "xyz",
            "thumbnail": "/api/basemaps/presets/stamen-watercolor/thumbnail",
            "config": {
                "url": "https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg",
                "attribution": "© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors",
                "maxZoom": 16,
            }
        },
        {
            "id": "esri-satellite",
            "name": "ESRI Satellite",
            "description": "High-resolution satellite imagery",
            "type": "xyz",
            "thumbnail": "/api/basemaps/presets/esri-satellite/thumbnail",
            "config": {
                "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                "attribution": "© Esri, Maxar, Earthstar Geographics, and the GIS User Community",
                "maxZoom": 19,
            }
        },
    ]
    
    return presets