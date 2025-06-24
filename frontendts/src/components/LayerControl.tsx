// Copyright Bunting Labs, Inc. 2025

import { useState, useEffect, RefObject } from 'react';
import { Map as MapLibreMap } from 'maplibre-gl';

interface LayerControlProps {
  mapRef: RefObject<MapLibreMap | null>;
}

interface LayerInfo {
  id: string;
  name: string;
  visible: boolean;
}

export function LayerControl({ mapRef }: LayerControlProps) {
  const [layers, setLayers] = useState<LayerInfo[]>([
    { id: 'eno-rivers-layer', name: 'Rivers', visible: true },
    { id: 'eno-lakes-layer', name: 'Lakes', visible: true },
    { id: 'eno-states-layer', name: 'States', visible: true },
    { id: 'eno-biomes-layer', name: 'Biomes', visible: true },
    { id: 'eno-cities-layer', name: 'Cities', visible: true },
    { id: 'eno-cities-labels', name: 'City Labels', visible: true }
  ]);

  const [isOpen, setIsOpen] = useState(false);

  const toggleLayer = (layerId: string) => {
    const map = mapRef.current;
    if (!map) return;

    setLayers(prev => 
      prev.map(layer => {
        if (layer.id === layerId) {
          const newVisible = !layer.visible;
          const visibility = newVisible ? 'visible' : 'none';
          
          try {
            map.setLayoutProperty(layerId, 'visibility', visibility);
            console.log(`Set ${layerId} visibility to ${visibility}`);
          } catch (err) {
            console.warn(`Failed to toggle ${layerId}:`, err);
          }
          
          return { ...layer, visible: newVisible };
        }
        return layer;
      })
    );
  };

  // Toggle with keyboard shortcut (L key)
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'l' || e.key === 'L') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  if (!isOpen) {
    return (
      <div className="fixed top-4 left-4 z-40">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-black bg-opacity-60 text-white text-xs px-3 py-2 rounded hover:bg-opacity-80 transition-opacity"
          title="Show layer control (L key)"
        >
          📋 Layers
        </button>
      </div>
    );
  }

  return (
    <div className="fixed top-4 left-4 z-40 bg-white bg-opacity-95 backdrop-blur-sm border border-gray-300 rounded-lg shadow-lg p-3 min-w-48">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-bold text-gray-800">Vector Layers</h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-600 hover:text-gray-800 text-xs"
          title="Hide (L key)"
        >
          ✕
        </button>
      </div>

      <div className="space-y-2">
        {layers.map(layer => (
          <label key={layer.id} className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={layer.visible}
              onChange={() => toggleLayer(layer.id)}
              className="mr-2"
            />
            <span className="text-sm text-gray-700 select-none">
              {layer.name}
            </span>
          </label>
        ))}
      </div>

      <div className="text-xs text-gray-500 mt-3 pt-2 border-t border-gray-200">
        Press L to toggle
      </div>
    </div>
  );
}