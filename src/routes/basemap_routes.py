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

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from pathlib import Path
import aiofiles
import os

from src.database.connection import get_db
from src.database.models import CustomBasemap
from src.dependencies.session import verify_session_required, verify_session_optional, UserContext
from src.dependencies.custom_basemap import TileSource, CustomTileMapProvider


router = APIRouter()


def generate_id(length=12, prefix=""):
    """Generate a unique ID with optional prefix."""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length - len(prefix)))
    return prefix + random_part


class CreateBasemapRequest(BaseModel):
    name: str
    tile_url_template: str
    tile_format: str = "png"
    min_zoom: int = 0
    max_zoom: int = 22
    tile_size: int = 256
    attribution: str = ""
    bounds: Optional[List[float]] = None
    center: Optional[List[float]] = None
    default_zoom: Optional[int] = None
    is_public: bool = False
    metadata: Optional[dict] = None
    world_model_id: Optional[str] = None
    georeferencing_points: Optional[List[dict]] = None
    transform_matrix: Optional[List[float]] = None


class BasemapResponse(BaseModel):
    id: str
    name: str
    tile_url_template: str
    tile_format: str
    min_zoom: int
    max_zoom: int
    tile_size: int
    attribution: str
    bounds: Optional[List[float]]
    center: Optional[List[float]]
    default_zoom: Optional[int]
    is_public: bool
    metadata: Optional[dict]
    owner_uuid: str
    created_at: str
    updated_at: str
    world_model_id: Optional[str]
    georeferencing_points: Optional[List[dict]]
    transform_matrix: Optional[List[float]]


@router.post("/api/basemaps", response_model=BasemapResponse)
async def create_basemap(
    request: CreateBasemapRequest,
    user_context: UserContext = Depends(verify_session_required),
    session: AsyncSession = Depends(get_db)
):
    """Create a new custom basemap configuration."""
    basemap = CustomBasemap(
        id=generate_id(prefix="B"),
        owner_uuid=uuid.UUID(user_context.get_user_id()),
        name=request.name,
        tile_url_template=request.tile_url_template,
        tile_format=request.tile_format,
        min_zoom=request.min_zoom,
        max_zoom=request.max_zoom,
        tile_size=request.tile_size,
        attribution=request.attribution,
        bounds=request.bounds,
        center=request.center,
        default_zoom=request.default_zoom,
        is_public=request.is_public,
        metadata_json=request.metadata,
        world_model_id=request.world_model_id,
        georeferencing_points=request.georeferencing_points,
        transform_matrix=request.transform_matrix
    )
    
    session.add(basemap)
    await session.commit()
    await session.refresh(basemap)
    
    return BasemapResponse(
        id=basemap.id,
        name=basemap.name,
        tile_url_template=basemap.tile_url_template,
        tile_format=basemap.tile_format,
        min_zoom=basemap.min_zoom,
        max_zoom=basemap.max_zoom,
        tile_size=basemap.tile_size,
        attribution=basemap.attribution,
        bounds=basemap.bounds,
        center=basemap.center,
        default_zoom=basemap.default_zoom,
        is_public=basemap.is_public,
        metadata=basemap.metadata_json,
        owner_uuid=str(basemap.owner_uuid),
        created_at=basemap.created_at.isoformat(),
        updated_at=basemap.updated_at.isoformat(),
        world_model_id=basemap.world_model_id,
        georeferencing_points=basemap.georeferencing_points,
        transform_matrix=basemap.transform_matrix
    )


@router.get("/api/basemaps", response_model=List[BasemapResponse])
async def list_basemaps(
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """List available basemaps (user's own and public ones)."""
    # Build query to get user's basemaps and public basemaps
    conditions = [CustomBasemap.is_public == True]
    if user_context:
        conditions.append(CustomBasemap.owner_uuid == uuid.UUID(user_context.get_user_id()))
    
    query = select(CustomBasemap).where(or_(*conditions))
    result = await session.execute(query)
    basemaps = result.scalars().all()
    
    return [
        BasemapResponse(
            id=b.id,
            name=b.name,
            tile_url_template=b.tile_url_template,
            tile_format=b.tile_format,
            min_zoom=b.min_zoom,
            max_zoom=b.max_zoom,
            tile_size=b.tile_size,
            attribution=b.attribution,
            bounds=b.bounds,
            center=b.center,
            default_zoom=b.default_zoom,
            is_public=b.is_public,
            metadata=b.metadata_json,
            owner_uuid=str(b.owner_uuid),
            created_at=b.created_at.isoformat(),
            updated_at=b.updated_at.isoformat(),
            world_model_id=b.world_model_id,
            georeferencing_points=b.georeferencing_points,
            transform_matrix=b.transform_matrix
        )
        for b in basemaps
    ]


@router.get("/api/basemaps/{basemap_id}", response_model=BasemapResponse)
async def get_basemap(
    basemap_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific basemap by ID."""
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BasemapResponse(
        id=basemap.id,
        name=basemap.name,
        tile_url_template=basemap.tile_url_template,
        tile_format=basemap.tile_format,
        min_zoom=basemap.min_zoom,
        max_zoom=basemap.max_zoom,
        tile_size=basemap.tile_size,
        attribution=basemap.attribution,
        bounds=basemap.bounds,
        center=basemap.center,
        default_zoom=basemap.default_zoom,
        is_public=basemap.is_public,
        metadata=basemap.metadata_json,
        owner_uuid=str(basemap.owner_uuid),
        created_at=basemap.created_at.isoformat(),
        updated_at=basemap.updated_at.isoformat(),
        world_model_id=basemap.world_model_id,
        georeferencing_points=basemap.georeferencing_points,
        transform_matrix=basemap.transform_matrix
    )


@router.get("/api/basemaps/{basemap_id}/style")
async def get_basemap_style(
    basemap_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get MapLibre GL style JSON for a basemap."""
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create tile source from database model
    tile_source = TileSource(
        id=basemap.id,
        name=basemap.name,
        tile_url_template=basemap.tile_url_template,
        min_zoom=basemap.min_zoom,
        max_zoom=basemap.max_zoom,
        tile_size=basemap.tile_size,
        attribution=basemap.attribution,
        bounds=basemap.bounds,
        center=basemap.center,
        default_zoom=basemap.default_zoom
    )
    
    provider = CustomTileMapProvider(tile_source)
    style = await provider.get_base_style()
    
    return style


@router.get("/api/basemaps/{basemap_id}/data")
async def get_basemap_data(
    basemap_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get the raw GeoJSON data for a basemap."""
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extract GeoJSON path from tile_url_template
    if not basemap.tile_url_template.startswith("geojson://"):
        raise HTTPException(status_code=400, detail="Not a GeoJSON source")
    
    geojson_path = basemap.tile_url_template.replace("geojson://", "")
    geojson_file = Path(geojson_path).resolve()
    
    if not geojson_file.exists():
        raise HTTPException(status_code=404, detail="GeoJSON file not found")
    
    # Read and return the GeoJSON
    try:
        import json
        async with aiofiles.open(geojson_file, "r", encoding="utf-8") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading GeoJSON: {str(e)}")


@router.get("/api/tiles/local/{basemap_id}/{z}/{x}/{y}.{format}")
async def serve_local_tile(
    basemap_id: str,
    z: int,
    x: int,
    y: int,
    format: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Serve tiles from local filesystem for custom basemaps."""
    # Get basemap configuration
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extract local path from tile_url_template
    if not basemap.tile_url_template.startswith("file://"):
        raise HTTPException(status_code=400, detail="Not a local tile source")
    
    local_path = basemap.tile_url_template.replace("file://", "")
    
    # Handle single image files (for previews)
    if not ("{z}" in local_path and "{x}" in local_path and "{y}" in local_path):
        # Single image file - serve it for all tile requests
        tile_file = Path(local_path).resolve()
    else:
        # Standard XYZ tile structure
        tile_path = local_path.replace("{z}", str(z)).replace("{x}", str(x)).replace("{y}", str(y))
        tile_file = Path(tile_path).resolve()
    
    if not tile_file.exists():
        raise HTTPException(status_code=404, detail="Tile not found")
    
    # Determine content type
    content_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp"
    }
    content_type = content_types.get(format, "application/octet-stream")
    
    # Read and return tile
    async with aiofiles.open(tile_file, "rb") as f:
        content = await f.read()
    
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.delete("/api/basemaps/{basemap_id}")
async def delete_basemap(
    basemap_id: str,
    user_context: UserContext = Depends(verify_session_required),
    session: AsyncSession = Depends(get_db)
):
    """Delete a custom basemap."""
    query = select(CustomBasemap).where(
        and_(
            CustomBasemap.id == basemap_id,
            CustomBasemap.owner_uuid == uuid.UUID(user_context.get_user_id())
        )
    )
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found or access denied")
    
    await session.delete(basemap)
    await session.commit()
    
    return {"status": "success", "message": "Basemap deleted"}


@router.get("/api/basemaps/{basemap_id}/vector/{z}/{x}/{y}.json")
async def serve_vector_tile(
    basemap_id: str,
    z: int,
    x: int,
    y: int,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Serve vector tiles (GeoJSON) for custom basemaps."""
    # Get basemap configuration
    query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
    result = await session.execute(query)
    basemap = result.scalar_one_or_none()
    
    if not basemap:
        raise HTTPException(status_code=404, detail="Basemap not found")
    
    # Check access permissions
    if not basemap.is_public and (not user_context or str(basemap.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extract GeoJSON path from tile_url_template
    if not basemap.tile_url_template.startswith("geojson://"):
        raise HTTPException(status_code=400, detail="Not a vector tile source")
    
    geojson_path = basemap.tile_url_template.replace("geojson://", "")
    geojson_file = Path(geojson_path).resolve()
    
    if not geojson_file.exists():
        raise HTTPException(status_code=404, detail="Vector data not found")
    
    # For simplicity, return the entire GeoJSON for now
    # In production, you'd want to implement proper vector tile clipping
    try:
        import json
        async with aiofiles.open(geojson_file, "r") as f:
            content = await f.read()
            geojson_data = json.loads(content)
        
        # Simple bounding box filter based on tile coordinates
        # This is a basic implementation - production would use proper tile math
        from math import pow, atan, sinh, pi
        
        n = pow(2, z)
        lon_min = x / n * 360.0 - 180.0
        lon_max = (x + 1) / n * 360.0 - 180.0
        lat_max = atan(sinh(pi * (1 - 2 * y / n))) * 180.0 / pi
        lat_min = atan(sinh(pi * (1 - 2 * (y + 1) / n))) * 180.0 / pi
        
        # Filter features within tile bounds
        filtered_features = []
        for feature in geojson_data.get("features", []):
            if feature.get("geometry", {}).get("type") == "Point":
                coords = feature["geometry"]["coordinates"]
                if lon_min <= coords[0] <= lon_max and lat_min <= coords[1] <= lat_max:
                    filtered_features.append(feature)
        
        # Return filtered GeoJSON
        return {
            "type": "FeatureCollection",
            "features": filtered_features
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing vector data: {str(e)}")