#!/usr/bin/env python3
"""
Create an Eno Cities Demo Project with proper map setup.
"""

import asyncio
import uuid
from datetime import datetime
from src.structures import get_async_db_connection

async def create_eno_project():
    """Create the Eno project and map."""
    
    async with get_async_db_connection() as conn:
        # System/demo user UUID
        demo_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        
        # Create project ID that matches the expected ID from the URL
        project_id = "BxvFhuzMcnuy"  # Use the same ID for consistency
        map_id = "M" + project_id[1:]  # Create a map ID: MxvFhuzMcnuy
        
        print(f"Creating project: {project_id}")
        print(f"Creating map: {map_id}")
        
        # Check if project already exists
        existing_project = await conn.fetchrow(
            "SELECT id FROM user_mundiai_projects WHERE id = $1", 
            project_id
        )
        
        if existing_project:
            print("Project already exists, updating...")
            # Update the project
            await conn.execute("""
                UPDATE user_mundiai_projects 
                SET maps = $1, link_accessible = true
                WHERE id = $2
            """, [map_id], project_id)
        else:
            print("Creating new project...")
            # Create the project
            await conn.execute("""
                INSERT INTO user_mundiai_projects (
                    id, owner_uuid, editor_uuids, viewer_uuids, 
                    link_accessible, created_on, maps, map_diff_messages
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                project_id, demo_uuid, [], [], 
                True, datetime.utcnow(), [map_id], []
            )
        
        # Check if map already exists
        existing_map = await conn.fetchrow(
            "SELECT id FROM user_mundiai_maps WHERE id = $1", 
            map_id
        )
        
        if existing_map:
            print("Map already exists, updating...")
            # Update the map to ensure it has no layers (so it uses basemap only)
            await conn.execute("""
                UPDATE user_mundiai_maps 
                SET layers = $1, project_id = $2
                WHERE id = $3
            """, [], project_id, map_id)
        else:
            print("Creating new map...")
            # Create the map
            await conn.execute("""
                INSERT INTO user_mundiai_maps (
                    id, project_id, owner_uuid, layers, 
                    soft_deleted_at, created_on, title, description
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                map_id, project_id, demo_uuid, [],
                None, datetime.utcnow(), "Eno Cities Demo Map", "Demo map showing Eno fantasy world with cities"
            )
        
        print(f"✅ Eno project created successfully!")
        print(f"   Project ID: {project_id}")
        print(f"   Map ID: {map_id}")
        print(f"   URL: http://localhost:8000/project/{project_id}")
        print(f"   This map will use the default basemap provider logic.")

if __name__ == "__main__":
    asyncio.run(create_eno_project())