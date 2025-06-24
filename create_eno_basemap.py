#!/usr/bin/env python3
"""
Script to create the Eno basemap in the database.
"""

import asyncio
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.database.models import CustomBasemap
import os

# Use the same database URL as the app
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://mundiuser:gdalpassword@postgresdb:5432/mundidb")

async def create_eno_basemap():
    """Create the Eno relief basemap in the database."""
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if basemap already exists
        existing = await session.get(CustomBasemap, "BUlJVMxOuaEK")
        if existing:
            print("Eno basemap already exists, updating...")
            basemap = existing
        else:
            print("Creating new Eno basemap...")
            basemap = CustomBasemap(
                id="BUlJVMxOuaEK",
                owner_uuid=uuid.UUID("00000000-0000-0000-0000-000000000000")  # System UUID
            )
        
        # Set basemap properties
        basemap.name = "Eno Relief Map"
        basemap.tile_url_template = "file:///app/Eno/tif/relief_preview.png"
        basemap.tile_format = "png"
        basemap.min_zoom = 0
        basemap.max_zoom = 18
        basemap.tile_size = 256
        basemap.attribution = "© Eno Fantasy World"
        basemap.bounds = [-73.312, -92.897, 117.287, 98.423]
        basemap.center = [21.9875, 2.763]
        basemap.default_zoom = 3
        basemap.is_public = True
        basemap.metadata_json = {
            "type": "fantasy_world",
            "projection": "custom",
            "world": "Eno"
        }
        
        session.add(basemap)
        await session.commit()
        print(f"✅ Eno basemap {'updated' if existing else 'created'} successfully!")
        print(f"   ID: {basemap.id}")
        print(f"   Name: {basemap.name}")
        print(f"   Bounds: {basemap.bounds}")
        print(f"   Center: {basemap.center}")

if __name__ == "__main__":
    asyncio.run(create_eno_basemap())