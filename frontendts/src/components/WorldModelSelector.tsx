// Copyright Bunting Labs, Inc. 2025

import { useState } from 'react';
import { WorldModel } from '../lib/types';
import { useWorldModels } from '../hooks/useWorldModels';

interface WorldModelSelectorProps {
  selectedWorldModelId?: string | null;
  onWorldModelChange: (worldModel: WorldModel | null) => void;
  className?: string;
}

export function WorldModelSelector({ 
  selectedWorldModelId, 
  onWorldModelChange, 
  className = "" 
}: WorldModelSelectorProps) {
  const { worldModels, loading, error } = useWorldModels();
  const [isOpen, setIsOpen] = useState(false);

  const selectedWorldModel = worldModels.find(wm => wm.id === selectedWorldModelId) || null;

  const handleSelect = (worldModel: WorldModel | null) => {
    onWorldModelChange(worldModel);
    setIsOpen(false);
  };

  if (loading) {
    return (
      <div className={`p-2 text-sm text-gray-500 ${className}`}>
        Loading world models...
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-2 text-sm text-red-500 ${className}`}>
        Error loading world models: {error}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 text-left bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            {selectedWorldModel ? (
              <div>
                <div className="text-sm font-medium text-gray-900 truncate">
                  {selectedWorldModel.name}
                </div>
                <div className="text-xs text-gray-500">
                  Scale: {selectedWorldModel.planet_scale_factor}x Earth
                  {selectedWorldModel.is_default && " (Default)"}
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">Select a world model...</div>
            )}
          </div>
          <svg
            className={`w-5 h-5 ml-2 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
          <div className="py-1">
            <button
              onClick={() => handleSelect(null)}
              className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
            >
              <div className="font-medium">No world model</div>
              <div className="text-xs text-gray-500">Use standard Earth coordinates</div>
            </button>
            
            {worldModels.map((worldModel) => (
              <button
                key={worldModel.id}
                onClick={() => handleSelect(worldModel)}
                className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100 ${
                  selectedWorldModelId === worldModel.id 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'text-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium flex items-center gap-2">
                      {worldModel.name}
                      {worldModel.is_default && (
                        <span className="text-xs bg-green-100 text-green-700 px-1 rounded">
                          Default
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500">
                      Scale: {worldModel.planet_scale_factor}x Earth
                      {worldModel.extent_bounds && (
                        <span className="ml-2">
                          Extent: {worldModel.extent_bounds[0].toFixed(0)}° to {worldModel.extent_bounds[2].toFixed(0)}°
                        </span>
                      )}
                    </div>
                    {worldModel.description && (
                      <div className="text-xs text-gray-400 mt-1 line-clamp-2">
                        {worldModel.description}
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}