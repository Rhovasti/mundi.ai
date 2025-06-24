// Copyright Bunting Labs, Inc. 2025

import { useState, useEffect } from 'react';
import { WorldModel } from '../lib/types';
import { fetchWorldModels, fetchWorldModel, getWorldModelBounds } from '../lib/api';

export function useWorldModels() {
  const [worldModels, setWorldModels] = useState<WorldModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWorldModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const models = await fetchWorldModels();
      setWorldModels(models);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load world models');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorldModels();
  }, []);

  return { worldModels, loading, error, refetch: loadWorldModels };
}

export function useWorldModel(id: string | null) {
  const [worldModel, setWorldModel] = useState<WorldModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setWorldModel(null);
      setLoading(false);
      setError(null);
      return;
    }

    async function loadWorldModel() {
      try {
        setLoading(true);
        setError(null);
        const model = await fetchWorldModel(id!); // id is guaranteed to be non-null here
        setWorldModel(model);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load world model');
        setWorldModel(null);
      } finally {
        setLoading(false);
      }
    }

    loadWorldModel();
  }, [id]);

  return { worldModel, loading, error };
}

export function useWorldModelBounds(id: string | null) {
  const [bounds, setBounds] = useState<{
    bounds?: [number, number, number, number] | null;
    center?: [number, number] | null;
    zoom: number;
    planet_scale_factor: number;
    earth_radius?: number | null;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setBounds(null);
      setLoading(false);
      setError(null);
      return;
    }

    async function loadBounds() {
      try {
        setLoading(true);
        setError(null);
        const boundsData = await getWorldModelBounds(id!); // id is guaranteed to be non-null here
        setBounds(boundsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load world model bounds');
        setBounds(null);
      } finally {
        setLoading(false);
      }
    }

    loadBounds();
  }, [id]);

  return { bounds, loading, error };
}