# Eno Fantasy Map - Simplified Project Scope

## Project Goal (Revised)

Create a fully functional GIS system using the **Eno fantasy world** as a single, dedicated basemap with proper vector data overlay capabilities.

## Simplified Scope

### ✅ **In Scope**
- **Single Eno Basemap**: Focus on one working relief map basemap
- **Vector Data Overlay**: Eno cities and user-uploaded GIS data
- **Core GIS Functionality**: Upload, display, query, and interact with geospatial data
- **Coordinate System**: Native Eno coordinates (already working)
- **Current Architecture**: Keep existing DriftDB and overall system

### ❌ **Out of Scope (Removed)**
- Multi-world model system
- Multiple basemap support and basemap selector
- Generic fantasy world abstractions
- DriftDB replacement with SpacetimeDB
- Support for other fantasy worlds (future project)

## Technical Simplifications

### 1. Remove World Model Complexity
- Remove `WorldModelSelector` component
- Remove world model API endpoints and database tables
- Hardcode Eno coordinate system in the application
- Remove transformation logic (already done)

### 2. Single Basemap Focus
- Remove `BasemapSelector` component  
- Choose one primary Eno basemap (relief map recommended)
- Hardcode basemap configuration
- Remove custom basemap API for multiple maps

### 3. Streamlined UI
- Remove selector dropdowns from map interface
- Focus on core GIS tools (layer management, upload, etc.)
- Keep coordinate display for debugging
- Simplified, clean interface

## Implementation Plan

### Phase 1: Remove Complexity
1. Remove world model selector from UI
2. Remove basemap selector from UI  
3. Hardcode single Eno basemap
4. Remove unused API endpoints
5. Clean up database (remove world model tables)

### Phase 2: Focus on Core GIS
1. Ensure vector data displays correctly over Eno basemap
2. Test data upload and display functionality
3. Verify coordinate alignment is working
4. Test standard GIS operations

### Phase 3: Polish and Document
1. Update documentation to reflect simplified scope
2. Create user guide for Eno GIS system
3. Test end-to-end workflows
4. Prepare for production use

## File Changes Required

### Remove/Simplify
- `frontendts/src/components/WorldModelSelector.tsx` (remove)
- `frontendts/src/components/BasemapSelector.tsx` (remove)
- `frontendts/src/hooks/useWorldModels.ts` (remove)
- `src/routes/world_model_routes.py` (remove)
- Database: `world_models` table (remove)
- Database: `custom_basemaps` complexity (simplify)

### Update  
- `frontendts/src/components/MapLibreMap.tsx` (hardcode Eno basemap)
- `src/routes/basemap_routes.py` (simplify to single basemap)
- Main application routing and initialization

## Expected Benefits

1. **Reduced Complexity**: Easier to understand, maintain, and debug
2. **Focused Functionality**: All effort goes into making Eno GIS work perfectly
3. **Faster Development**: No time spent on abstractions and multiple world support
4. **Better UX**: Simpler interface focused on GIS tasks, not world/basemap selection
5. **Production Ready**: Single-purpose tool that does one thing very well

## Success Criteria

✅ **Primary Success**: User can load Eno map and see properly aligned vector data
✅ **GIS Success**: User can upload GeoJSON/Shapefile and see it correctly positioned on Eno map  
✅ **Interaction Success**: User can click on features, view attributes, and perform basic GIS operations
✅ **Performance Success**: Map loads quickly and responds smoothly

## Next Steps

1. Start by removing the world model and basemap selectors from UI
2. Hardcode the best working Eno basemap (relief map + cities)
3. Test vector data overlay functionality thoroughly  
4. Clean up unused backend code
5. Document the simplified system

This focused approach will result in a production-ready Eno GIS system rather than a complex multi-world framework that's difficult to complete and maintain.