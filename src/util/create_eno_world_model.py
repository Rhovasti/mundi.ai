#!/usr/bin/env python3
"""Create default Eno world model in the database."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.database.connection import get_db, engine
from src.database.models import WorldModel


async def create_eno_world_model():
    """Create the default Eno world model."""
    async with AsyncSession(engine) as session:
        # Check if Eno world model already exists
        query = select(WorldModel).where(WorldModel.name == "Eno World")
        result = await session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"Eno world model already exists with ID: {existing.id}")
            return existing
        
        # Create Eno world model
        # Based on the extent from Maailmankello.shp: (-720, -450) to (1080, 450)
        # This suggests the planet is roughly 2.5x the width of Earth (1800° vs 360°)
        # and 5x the height (900° vs 180°)
        # Average scale factor: ~3.75x, but we'll use 2.5x for conservative scaling
        
        eno_world = WorldModel(
            id="W" + "".join([chr(ord('a') + i % 26) for i in range(11)]),  # Generate ID
            name="Eno World",
            description="Fantasy world of Eno with custom coordinate system",
            planet_scale_factor=2.5,  # 2.5x Earth size
            extent_bounds=[-720.0, -450.0, 1080.0, 450.0],  # From Maailmankello.shp
            crs_definition=None,  # Using modified WGS84
            transformation_matrix=None,  # No transformation needed for base world
            default_center=[180.0, 0.0],  # Center of the world
            default_zoom=2,
            earth_radius=6378137.0 * 2.5,  # Earth radius * scale factor
            coordinate_system_notes=(
                "Eno world uses an extended coordinate system based on WGS84. "
                "Longitude ranges from -720° to 1080° (5x Earth's range). "
                "Latitude ranges from -450° to 450° (5x Earth's range). "
                "The planet is approximately 2.5x the size of Earth."
            ),
            is_default=True,
            is_public=True,
            owner_uuid=uuid.UUID("00000000-0000-0000-0000-000000000000"),  # System owner
            metadata_json={
                "source": "Maailmankello.shp extent",
                "coordinate_type": "extended_wgs84",
                "render_world_copies": False
            }
        )
        
        session.add(eno_world)
        await session.commit()
        await session.refresh(eno_world)
        
        print(f"Created Eno world model with ID: {eno_world.id}")
        print(f"Extent bounds: {eno_world.extent_bounds}")
        print(f"Planet scale factor: {eno_world.planet_scale_factor}")
        print(f"Earth radius: {eno_world.earth_radius}")
        
        return eno_world


if __name__ == "__main__":
    asyncio.run(create_eno_world_model())