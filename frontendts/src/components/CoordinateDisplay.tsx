// Copyright Bunting Labs, Inc. 2025

import { useState, useEffect, RefObject } from 'react';
import { Map as MapLibreMap } from 'maplibre-gl';

interface CoordinateDisplayProps {
  mapRef: RefObject<MapLibreMap | null>;
}

export function CoordinateDisplay({ mapRef }: CoordinateDisplayProps) {
  const [coordinates, setCoordinates] = useState({
    mouse: { lng: 0, lat: 0 },
    center: { lng: 0, lat: 0 },
    zoom: 0,
    bounds: {
      sw: { lng: 0, lat: 0 },
      ne: { lng: 0, lat: 0 }
    }
  });
  const [showDisplay, setShowDisplay] = useState(false);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Update center, zoom, and bounds
    const updateMapState = () => {
      const center = map.getCenter();
      const zoom = map.getZoom();
      const bounds = map.getBounds();
      
      setCoordinates(prev => ({
        ...prev,
        center: { lng: center.lng, lat: center.lat },
        zoom,
        bounds: {
          sw: { lng: bounds.getSouthWest().lng, lat: bounds.getSouthWest().lat },
          ne: { lng: bounds.getNorthEast().lng, lat: bounds.getNorthEast().lat }
        }
      }));
    };

    // Update mouse coordinates
    const updateMouseCoords = (e: any) => {
      setCoordinates(prev => ({
        ...prev,
        mouse: { lng: e.lngLat.lng, lat: e.lngLat.lat }
      }));
    };

    // Event listeners
    map.on('move', updateMapState);
    map.on('zoom', updateMapState);
    map.on('mousemove', updateMouseCoords);

    // Initial update
    updateMapState();

    // Cleanup
    return () => {
      map.off('move', updateMapState);
      map.off('zoom', updateMapState);
      map.off('mousemove', updateMouseCoords);
    };
  }, [mapRef]);

  // Toggle display with keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'c' && e.ctrlKey) {
        e.preventDefault();
        setShowDisplay(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const formatCoordinate = (value: number, decimals: number = 4) => {
    return value.toFixed(decimals);
  };

  const getWorldModelInfo = () => {
    return {
      name: 'Eno Fantasy World',
      scale: 1.0,
      id: 'hardcoded-eno'
    };
  };

  if (!showDisplay) {
    // Show toggle hint
    return (
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={() => setShowDisplay(true)}
          className="bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded hover:bg-opacity-80 transition-opacity"
          title="Show coordinate display (Ctrl+C)"
        >
          📍 Coords
        </button>
      </div>
    );
  }

  const worldModelInfo = getWorldModelInfo();

  return (
    <div className="fixed bottom-4 right-4 z-40 bg-black bg-opacity-80 text-white p-3 rounded-lg shadow-lg font-mono text-sm max-w-sm">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-xs font-bold text-gray-300">COORDINATES</h3>
        <button
          onClick={() => setShowDisplay(false)}
          className="text-gray-400 hover:text-white text-xs"
          title="Hide (Ctrl+C)"
        >
          ✕
        </button>
      </div>

      <div className="space-y-1 text-xs">
        <div>
          <span className="text-gray-400">Mouse:</span>{' '}
          <span className="text-green-400">
            {formatCoordinate(coordinates.mouse.lng)}°, {formatCoordinate(coordinates.mouse.lat)}°
          </span>
        </div>
        
        <div>
          <span className="text-gray-400">Center:</span>{' '}
          <span className="text-blue-400">
            {formatCoordinate(coordinates.center.lng)}°, {formatCoordinate(coordinates.center.lat)}°
          </span>
        </div>
        
        <div>
          <span className="text-gray-400">Zoom:</span>{' '}
          <span className="text-yellow-400">{formatCoordinate(coordinates.zoom, 2)}</span>
        </div>
        
        <div className="border-t border-gray-600 pt-1 mt-2">
          <div className="text-gray-400 text-xs">Bounds:</div>
          <div className="text-xs">
            <div>
              <span className="text-gray-500">SW:</span>{' '}
              <span className="text-purple-400">
                {formatCoordinate(coordinates.bounds.sw.lng, 2)}°, {formatCoordinate(coordinates.bounds.sw.lat, 2)}°
              </span>
            </div>
            <div>
              <span className="text-gray-500">NE:</span>{' '}
              <span className="text-purple-400">
                {formatCoordinate(coordinates.bounds.ne.lng, 2)}°, {formatCoordinate(coordinates.bounds.ne.lat, 2)}°
              </span>
            </div>
          </div>
        </div>

        {worldModelInfo && (
          <div className="border-t border-gray-600 pt-1 mt-2">
            <div className="text-gray-400 text-xs">World Model:</div>
            <div className="text-xs">
              <div className="text-orange-400">{worldModelInfo.name}</div>
              <div className="text-gray-500">
                Scale: {worldModelInfo.scale}x | ID: {worldModelInfo.id}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="text-xs text-gray-500 mt-2 pt-1 border-t border-gray-600">
        Press Ctrl+C to toggle
      </div>
    </div>
  );
}