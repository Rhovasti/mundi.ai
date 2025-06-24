// Copyright Bunting Labs, Inc. 2025

import { useState, useEffect } from 'react';
import { CustomBasemap } from '../lib/types';
import { fetchCustomBasemaps } from '../lib/api';

export function useBasemaps() {
  const [basemaps, setBasemaps] = useState<CustomBasemap[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBasemaps = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchCustomBasemaps();
      setBasemaps(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load basemaps');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBasemaps();
  }, []);

  return { basemaps, loading, error, refetch: loadBasemaps };
}