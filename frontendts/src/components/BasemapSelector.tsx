// Copyright Bunting Labs, Inc. 2025

import { CustomBasemap, WorldModel } from '../lib/types';
import { useBasemaps } from '../hooks/useBasemaps';
import { useWorldModels } from '../hooks/useWorldModels';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Button } from "./ui/button";
import { ChevronDown, Map } from 'lucide-react';

interface BasemapSelectorProps {
  selectedBasemap: CustomBasemap | null;
  onBasemapChange: (basemap: CustomBasemap | null) => void;
  selectedWorldModel?: WorldModel | null;
}

export function BasemapSelector({ selectedBasemap, onBasemapChange, selectedWorldModel }: BasemapSelectorProps) {
  const { basemaps, loading, error } = useBasemaps();
  const { worldModels } = useWorldModels();

  // Filter basemaps based on selected world model
  const filteredBasemaps = basemaps.filter(basemap => {
    if (!selectedWorldModel) {
      // If no world model selected, show all basemaps
      return true;
    }
    // Show basemaps that belong to the selected world model or have no world model
    return basemap.world_model_id === selectedWorldModel.id || !basemap.world_model_id;
  });

  // Helper function to get world model name
  const getWorldModelName = (worldModelId: string | null | undefined) => {
    if (!worldModelId) return null;
    const worldModel = worldModels.find(wm => wm.id === worldModelId);
    return worldModel?.name || 'Unknown World';
  };

  if (loading) {
    return (
      <Button variant="outline" disabled className="w-40">
        <Map className="h-4 w-4 mr-2" />
        Loading...
      </Button>
    );
  }

  if (error) {
    return (
      <Button variant="outline" disabled className="w-40">
        <Map className="h-4 w-4 mr-2" />
        Error
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="w-40 justify-between">
          <div className="flex items-center">
            <Map className="h-4 w-4 mr-2" />
            <span className="truncate">
              {selectedBasemap ? selectedBasemap.name : 'Select Basemap'}
            </span>
          </div>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        <DropdownMenuItem onClick={() => onBasemapChange(null)}>
          <span>No Basemap</span>
        </DropdownMenuItem>
        {filteredBasemaps.map((basemap) => {
          const worldModelName = getWorldModelName(basemap.world_model_id);
          return (
            <DropdownMenuItem
              key={basemap.id}
              onClick={() => onBasemapChange(basemap)}
            >
              <div className="flex flex-col">
                <span>{basemap.name}</span>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{basemap.type === 'raster' ? 'Raster' : 'Vector'} basemap</span>
                  {worldModelName && (
                    <>
                      <span>•</span>
                      <span className="text-blue-600">{worldModelName}</span>
                    </>
                  )}
                </div>
              </div>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}