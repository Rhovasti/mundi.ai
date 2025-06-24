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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
import numpy as np

from src.database.connection import get_db
from src.database.models import WorldModel
from src.dependencies.session import verify_session_required, verify_session_optional, UserContext


router = APIRouter()


def generate_id(length=12, prefix=""):
    """Generate a unique ID with optional prefix."""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length - len(prefix)))
    return prefix + random_part


class CreateWorldModelRequest(BaseModel):
    name: str
    description: Optional[str] = None
    planet_scale_factor: float = Field(default=1.0, ge=0.1, le=3.5)
    extent_bounds: Optional[List[float]] = Field(default=None, description="[west, south, east, north] in WGS84")
    crs_definition: Optional[str] = None
    transformation_matrix: Optional[List[float]] = Field(default=None, description="6-parameter affine transformation")
    default_center: Optional[List[float]] = Field(default=None, description="[lng, lat] default map center")
    default_zoom: int = Field(default=2, ge=0, le=22)
    earth_radius: Optional[float] = Field(default=None, description="Custom planet radius in meters")
    coordinate_system_notes: Optional[str] = None
    is_default: bool = False
    is_public: bool = True
    metadata: Optional[dict] = None


class WorldModelResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    planet_scale_factor: float
    extent_bounds: Optional[List[float]]
    crs_definition: Optional[str]
    transformation_matrix: Optional[List[float]]
    default_center: Optional[List[float]]
    default_zoom: int
    earth_radius: Optional[float]
    coordinate_system_notes: Optional[str]
    is_default: bool
    is_public: bool
    owner_uuid: str
    metadata: Optional[dict]
    created_at: str
    updated_at: str


class CoordinateTransformRequest(BaseModel):
    from_coords: List[List[float]]  # [[x1, y1], [x2, y2], ...]
    from_crs: str = "EPSG:4326"  # Source CRS
    to_crs: str = "EPSG:3857"    # Target CRS


class CoordinateTransformResponse(BaseModel):
    to_coords: List[List[float]]
    transformation_matrix: Optional[List[float]]


@router.post("/api/world-models", response_model=WorldModelResponse)
async def create_world_model(
    request: CreateWorldModelRequest,
    user_context: UserContext = Depends(verify_session_required),
    session: AsyncSession = Depends(get_db)
):
    """Create a new world model configuration."""
    
    # Calculate earth radius based on scale factor if not provided
    earth_radius = request.earth_radius
    if earth_radius is None:
        earth_radius = 6378137.0 * request.planet_scale_factor  # WGS84 radius * scale
    
    world_model = WorldModel(
        id=generate_id(prefix="W"),
        owner_uuid=uuid.UUID(user_context.get_user_id()),
        name=request.name,
        description=request.description,
        planet_scale_factor=request.planet_scale_factor,
        extent_bounds=request.extent_bounds,
        crs_definition=request.crs_definition,
        transformation_matrix=request.transformation_matrix,
        default_center=request.default_center,
        default_zoom=request.default_zoom,
        earth_radius=earth_radius,
        coordinate_system_notes=request.coordinate_system_notes,
        is_default=request.is_default,
        is_public=request.is_public,
        metadata_json=request.metadata
    )
    
    session.add(world_model)
    await session.commit()
    await session.refresh(world_model)
    
    return WorldModelResponse(
        id=world_model.id,
        name=world_model.name,
        description=world_model.description,
        planet_scale_factor=world_model.planet_scale_factor,
        extent_bounds=world_model.extent_bounds,
        crs_definition=world_model.crs_definition,
        transformation_matrix=world_model.transformation_matrix,
        default_center=world_model.default_center,
        default_zoom=world_model.default_zoom,
        earth_radius=world_model.earth_radius,
        coordinate_system_notes=world_model.coordinate_system_notes,
        is_default=world_model.is_default,
        is_public=world_model.is_public,
        owner_uuid=str(world_model.owner_uuid),
        metadata=world_model.metadata_json,
        created_at=world_model.created_at.isoformat(),
        updated_at=world_model.updated_at.isoformat()
    )


@router.get("/api/world-models", response_model=List[WorldModelResponse])
async def list_world_models(
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """List available world models (user's own and public ones)."""
    
    # Build query to get user's world models and public world models
    conditions = [WorldModel.is_public == True]
    if user_context:
        conditions.append(WorldModel.owner_uuid == uuid.UUID(user_context.get_user_id()))
    
    query = select(WorldModel).where(or_(*conditions)).order_by(WorldModel.is_default.desc(), WorldModel.name)
    result = await session.execute(query)
    world_models = result.scalars().all()
    
    return [
        WorldModelResponse(
            id=wm.id,
            name=wm.name,
            description=wm.description,
            planet_scale_factor=wm.planet_scale_factor,
            extent_bounds=wm.extent_bounds,
            crs_definition=wm.crs_definition,
            transformation_matrix=wm.transformation_matrix,
            default_center=wm.default_center,
            default_zoom=wm.default_zoom,
            earth_radius=wm.earth_radius,
            coordinate_system_notes=wm.coordinate_system_notes,
            is_default=wm.is_default,
            is_public=wm.is_public,
            owner_uuid=str(wm.owner_uuid),
            metadata=wm.metadata_json,
            created_at=wm.created_at.isoformat(),
            updated_at=wm.updated_at.isoformat()
        )
        for wm in world_models
    ]


@router.get("/api/world-models/{world_model_id}", response_model=WorldModelResponse)
async def get_world_model(
    world_model_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific world model by ID."""
    query = select(WorldModel).where(WorldModel.id == world_model_id)
    result = await session.execute(query)
    world_model = result.scalar_one_or_none()
    
    if not world_model:
        raise HTTPException(status_code=404, detail="World model not found")
    
    # Check access permissions
    if not world_model.is_public and (not user_context or str(world_model.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return WorldModelResponse(
        id=world_model.id,
        name=world_model.name,
        description=world_model.description,
        planet_scale_factor=world_model.planet_scale_factor,
        extent_bounds=world_model.extent_bounds,
        crs_definition=world_model.crs_definition,
        transformation_matrix=world_model.transformation_matrix,
        default_center=world_model.default_center,
        default_zoom=world_model.default_zoom,
        earth_radius=world_model.earth_radius,
        coordinate_system_notes=world_model.coordinate_system_notes,
        is_default=world_model.is_default,
        is_public=world_model.is_public,
        owner_uuid=str(world_model.owner_uuid),
        metadata=world_model.metadata_json,
        created_at=world_model.created_at.isoformat(),
        updated_at=world_model.updated_at.isoformat()
    )


@router.post("/api/world-models/{world_model_id}/transform", response_model=CoordinateTransformResponse)
async def transform_coordinates(
    world_model_id: str,
    request: CoordinateTransformRequest,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Transform coordinates using a world model's coordinate system."""
    
    # Get world model
    query = select(WorldModel).where(WorldModel.id == world_model_id)
    result = await session.execute(query)
    world_model = result.scalar_one_or_none()
    
    if not world_model:
        raise HTTPException(status_code=404, detail="World model not found")
    
    # Check access permissions
    if not world_model.is_public and (not user_context or str(world_model.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Simple coordinate transformation based on world model parameters
        transformed_coords = []
        
        for coord in request.from_coords:
            x, y = coord[0], coord[1]
            
            # Apply transformation matrix if available
            if world_model.transformation_matrix and len(world_model.transformation_matrix) == 6:
                # Affine transformation: [a, b, c, d, e, f]
                # x' = a*x + b*y + c
                # y' = d*x + e*y + f
                a, b, c, d, e, f = world_model.transformation_matrix
                transformed_x = a * x + b * y + c
                transformed_y = d * x + e * y + f
            else:
                # Apply scale factor if no transformation matrix
                scale = world_model.planet_scale_factor
                
                # If extent bounds are defined, transform to local coordinate space
                if world_model.extent_bounds:
                    west, south, east, north = world_model.extent_bounds
                    # Normalize to [0,1] space and then scale
                    norm_x = (x - west) / (east - west) if east != west else 0
                    norm_y = (y - south) / (north - south) if north != south else 0
                    
                    # Apply scale factor to the normalized space
                    transformed_x = norm_x * scale * 360 - 180  # Scale to world space
                    transformed_y = norm_y * scale * 180 - 90
                else:
                    # Simple scaling around the origin
                    transformed_x = x * scale
                    transformed_y = y * scale
            
            transformed_coords.append([transformed_x, transformed_y])
        
        return CoordinateTransformResponse(
            to_coords=transformed_coords,
            transformation_matrix=world_model.transformation_matrix
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coordinate transformation failed: {str(e)}")


@router.get("/api/world-models/{world_model_id}/bounds")
async def get_world_model_bounds(
    world_model_id: str,
    user_context: Optional[UserContext] = Depends(verify_session_optional),
    session: AsyncSession = Depends(get_db)
):
    """Get the extent bounds and default view for a world model."""
    
    query = select(WorldModel).where(WorldModel.id == world_model_id)
    result = await session.execute(query)
    world_model = result.scalar_one_or_none()
    
    if not world_model:
        raise HTTPException(status_code=404, detail="World model not found")
    
    # Check access permissions
    if not world_model.is_public and (not user_context or str(world_model.owner_uuid) != user_context.get_user_id()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "bounds": world_model.extent_bounds,
        "center": world_model.default_center,
        "zoom": world_model.default_zoom,
        "planet_scale_factor": world_model.planet_scale_factor,
        "earth_radius": world_model.earth_radius
    }


@router.delete("/api/world-models/{world_model_id}")
async def delete_world_model(
    world_model_id: str,
    user_context: UserContext = Depends(verify_session_required),
    session: AsyncSession = Depends(get_db)
):
    """Delete a world model (only by owner, and only if not default)."""
    query = select(WorldModel).where(
        and_(
            WorldModel.id == world_model_id,
            WorldModel.owner_uuid == uuid.UUID(user_context.get_user_id())
        )
    )
    result = await session.execute(query)
    world_model = result.scalar_one_or_none()
    
    if not world_model:
        raise HTTPException(status_code=404, detail="World model not found or access denied")
    
    if world_model.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default world model")
    
    await session.delete(world_model)
    await session.commit()
    
    return {"status": "success", "message": "World model deleted"}