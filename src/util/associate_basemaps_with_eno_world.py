#!/usr/bin/env python3
"""Associate existing Eno basemaps with the Eno world model."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from src.database.connection import get_db, engine
from src.database.models import CustomBasemap, WorldModel


async def associate_basemaps_with_eno_world():
    """Associate existing Eno basemaps with the Eno world model."""
    async with AsyncSession(engine) as session:
        # Get the Eno world model
        query = select(WorldModel).where(WorldModel.name == "Eno World")
        result = await session.execute(query)
        eno_world = result.scalar_one_or_none()
        
        if not eno_world:
            print("Eno world model not found!")
            return
        
        print(f"Found Eno world model: {eno_world.id}")
        
        # Get all existing basemaps that appear to be Eno-related
        eno_basemap_ids = [
            "BGBov1d6Svoy",  # Eno Fantasy World
            "BwFKKVCxBm6o",  # Eno Relief Preview  
            "BTxKGw6JlkzT",  # Eno Relief Map - Tiled
            "BUlJVMxOuaEK",  # Eno Relief Map - Docker
            "BxBJQPSOAiO8",  # Eno Cities Vector Layer
            "BRpEy7CJaWuQ",  # Eno Cities Vector Style
            "BxvFhuzMcnuy"   # Eno Cities Vector - Docker
        ]
        
        # Update basemaps to associate with Eno world model
        for basemap_id in eno_basemap_ids:
            query = select(CustomBasemap).where(CustomBasemap.id == basemap_id)
            result = await session.execute(query)
            basemap = result.scalar_one_or_none()
            
            if basemap:
                # Update the basemap to associate with Eno world model
                update_stmt = (
                    update(CustomBasemap)
                    .where(CustomBasemap.id == basemap_id)
                    .values(world_model_id=eno_world.id)
                )
                await session.execute(update_stmt)
                print(f"Associated basemap '{basemap.name}' ({basemap_id}) with Eno world model")
            else:
                print(f"Basemap {basemap_id} not found, skipping")
        
        await session.commit()
        print(f"\nSuccessfully associated {len(eno_basemap_ids)} basemaps with Eno world model")


if __name__ == "__main__":
    asyncio.run(associate_basemaps_with_eno_world())