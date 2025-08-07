import React, { useState, useEffect } from 'react';
import { Plus, Globe, Trash2, Edit2, Eye, EyeOff, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { toast } from 'sonner';

interface BasemapConfig {
  url?: string;
  tileSize?: number;
  attribution?: string;
  layers?: string;
  styles?: string;
  format?: string;
  version?: string;
  crs?: string;
  style?: any;
}

interface CustomBasemap {
  id: string;
  name: string;
  description?: string;
  type: string;
  config: BasemapConfig;
  thumbnail_url?: string;
  owner_uuid: string;
  project_id?: string;
  is_public: boolean;
  is_default: boolean;
  attribution?: string;
  min_zoom: number;
  max_zoom: number;
  created_at: string;
  updated_at: string;
}

interface PresetBasemap {
  id: string;
  name: string;
  description: string;
  type: string;
  thumbnail: string;
  config: BasemapConfig;
}

interface BasemapManagerProps {
  projectId?: string;
  onBasemapSelect?: (basemapId: string) => void;
  currentBasemap?: string;
}

export default function BasemapManager({ projectId, onBasemapSelect, currentBasemap }: BasemapManagerProps) {
  const [customBasemaps, setCustomBasemaps] = useState<CustomBasemap[]>([]);
  const [presetBasemaps, setPresetBasemaps] = useState<PresetBasemap[]>([]);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingBasemap, setEditingBasemap] = useState<CustomBasemap | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'xyz',
    url: '',
    attribution: '',
    tileSize: 256,
    min_zoom: 0,
    max_zoom: 22,
    is_public: false,
    // WMS specific
    layers: '',
    styles: '',
    format: 'image/png',
    version: '1.3.0',
    crs: 'EPSG:3857',
  });

  useEffect(() => {
    fetchCustomBasemaps();
    fetchPresetBasemaps();
  }, [projectId]);

  const fetchCustomBasemaps = async () => {
    try {
      const url = new URL('/api/basemaps/custom', window.location.origin);
      if (projectId) {
        url.searchParams.set('project_id', projectId);
      }
      const response = await fetch(url.toString());
      if (response.ok) {
        const data = await response.json();
        setCustomBasemaps(data);
      }
    } catch (error) {
      console.error('Failed to fetch custom basemaps:', error);
    }
  };

  const fetchPresetBasemaps = async () => {
    try {
      const response = await fetch('/api/basemaps/presets');
      if (response.ok) {
        const data = await response.json();
        setPresetBasemaps(data);
      }
    } catch (error) {
      console.error('Failed to fetch preset basemaps:', error);
    }
  };

  const handleAddBasemap = async () => {
    setLoading(true);
    try {
      const config: BasemapConfig = {
        url: formData.url,
        tileSize: formData.tileSize,
        attribution: formData.attribution,
      };

      if (formData.type === 'wms' || formData.type === 'wmts') {
        config.layers = formData.layers;
        config.styles = formData.styles;
        config.format = formData.format;
        config.version = formData.version;
        config.crs = formData.crs;
      }

      const response = await fetch('/api/basemaps/custom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description,
          type: formData.type,
          config,
          project_id: projectId,
          is_public: formData.is_public,
          attribution: formData.attribution,
          min_zoom: formData.min_zoom,
          max_zoom: formData.max_zoom,
        }),
      });

      if (response.ok) {
        toast.success('Basemap added successfully');
        setIsAddDialogOpen(false);
        resetForm();
        fetchCustomBasemaps();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to add basemap');
      }
    } catch (error) {
      toast.error('Failed to add basemap');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBasemap = async () => {
    if (!editingBasemap) return;
    
    setLoading(true);
    try {
      const config: BasemapConfig = {
        url: formData.url,
        tileSize: formData.tileSize,
        attribution: formData.attribution,
      };

      if (formData.type === 'wms' || formData.type === 'wmts') {
        config.layers = formData.layers;
        config.styles = formData.styles;
        config.format = formData.format;
        config.version = formData.version;
        config.crs = formData.crs;
      }

      const response = await fetch(`/api/basemaps/custom/${editingBasemap.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description,
          config,
          is_public: formData.is_public,
          attribution: formData.attribution,
          min_zoom: formData.min_zoom,
          max_zoom: formData.max_zoom,
        }),
      });

      if (response.ok) {
        toast.success('Basemap updated successfully');
        setIsEditDialogOpen(false);
        setEditingBasemap(null);
        resetForm();
        fetchCustomBasemaps();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to update basemap');
      }
    } catch (error) {
      toast.error('Failed to update basemap');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBasemap = async (basemapId: string) => {
    if (!confirm('Are you sure you want to delete this basemap?')) return;

    try {
      const response = await fetch(`/api/basemaps/custom/${basemapId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Basemap deleted successfully');
        fetchCustomBasemaps();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to delete basemap');
      }
    } catch (error) {
      toast.error('Failed to delete basemap');
    }
  };

  const handleEditBasemap = (basemap: CustomBasemap) => {
    setEditingBasemap(basemap);
    setFormData({
      name: basemap.name,
      description: basemap.description || '',
      type: basemap.type,
      url: basemap.config.url || '',
      attribution: basemap.attribution || '',
      tileSize: basemap.config.tileSize || 256,
      min_zoom: basemap.min_zoom,
      max_zoom: basemap.max_zoom,
      is_public: basemap.is_public,
      layers: basemap.config.layers || '',
      styles: basemap.config.styles || '',
      format: basemap.config.format || 'image/png',
      version: basemap.config.version || '1.3.0',
      crs: basemap.config.crs || 'EPSG:3857',
    });
    setIsEditDialogOpen(true);
  };

  const handlePresetSelect = (preset: PresetBasemap) => {
    setFormData({
      name: preset.name,
      description: preset.description,
      type: preset.type,
      url: preset.config.url || '',
      attribution: preset.config.attribution || '',
      tileSize: preset.config.tileSize || 256,
      min_zoom: 0,
      max_zoom: preset.config.maxZoom || 22,
      is_public: false,
      layers: '',
      styles: '',
      format: 'image/png',
      version: '1.3.0',
      crs: 'EPSG:3857',
    });
    setIsAddDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      type: 'xyz',
      url: '',
      attribution: '',
      tileSize: 256,
      min_zoom: 0,
      max_zoom: 22,
      is_public: false,
      layers: '',
      styles: '',
      format: 'image/png',
      version: '1.3.0',
      crs: 'EPSG:3857',
    });
  };

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Basemap Manager</h2>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Basemap
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add Custom Basemap</DialogTitle>
              <DialogDescription>
                Configure a new basemap from a tile server or select from presets.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right">
                  Name
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="col-span-3"
                  placeholder="My Custom Basemap"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="description" className="text-right">
                  Description
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="col-span-3"
                  placeholder="Optional description"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="type" className="text-right">
                  Type
                </Label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="col-span-3 h-10 px-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="xyz">XYZ Tiles</option>
                  <option value="wms">WMS</option>
                  <option value="wmts">WMTS</option>
                  <option value="style_json">MapLibre Style JSON</option>
                </select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="url" className="text-right">
                  URL Template
                </Label>
                <Input
                  id="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="col-span-3"
                  placeholder="https://tile.example.com/{z}/{x}/{y}.png"
                />
              </div>
              {(formData.type === 'wms' || formData.type === 'wmts') && (
                <>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="layers" className="text-right">
                      Layers
                    </Label>
                    <Input
                      id="layers"
                      value={formData.layers}
                      onChange={(e) => setFormData({ ...formData, layers: e.target.value })}
                      className="col-span-3"
                      placeholder="layer1,layer2"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="format" className="text-right">
                      Format
                    </Label>
                    <Input
                      id="format"
                      value={formData.format}
                      onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                      className="col-span-3"
                      placeholder="image/png"
                    />
                  </div>
                </>
              )}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="attribution" className="text-right">
                  Attribution
                </Label>
                <Input
                  id="attribution"
                  value={formData.attribution}
                  onChange={(e) => setFormData({ ...formData, attribution: e.target.value })}
                  className="col-span-3"
                  placeholder="© Data Provider"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="min_zoom" className="text-right">
                  Zoom Range
                </Label>
                <div className="col-span-3 flex gap-2 items-center">
                  <Input
                    id="min_zoom"
                    type="number"
                    value={formData.min_zoom}
                    onChange={(e) => setFormData({ ...formData, min_zoom: parseInt(e.target.value) })}
                    className="w-20"
                    min="0"
                    max="22"
                  />
                  <span>to</span>
                  <Input
                    id="max_zoom"
                    type="number"
                    value={formData.max_zoom}
                    onChange={(e) => setFormData({ ...formData, max_zoom: parseInt(e.target.value) })}
                    className="w-20"
                    min="0"
                    max="22"
                  />
                </div>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="is_public" className="text-right">
                  Public
                </Label>
                <div className="col-span-3">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={formData.is_public}
                    onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-600">Allow others to use this basemap</span>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddBasemap} disabled={loading || !formData.name || !formData.url}>
                {loading ? 'Adding...' : 'Add Basemap'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Preset Basemaps */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Preset Basemaps</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {presetBasemaps.map((preset) => (
            <Card
              key={preset.id}
              className={`cursor-pointer hover:shadow-lg transition-shadow ${
                currentBasemap === preset.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => onBasemapSelect?.(preset.id)}
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{preset.name}</span>
                  {currentBasemap === preset.id && <Check className="h-5 w-5 text-green-500" />}
                </CardTitle>
                <CardDescription>{preset.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePresetSelect(preset);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Use as Template
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Custom Basemaps */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Custom Basemaps</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {customBasemaps.map((basemap) => (
            <Card
              key={basemap.id}
              className={`cursor-pointer hover:shadow-lg transition-shadow ${
                currentBasemap === basemap.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => onBasemapSelect?.(basemap.id)}
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{basemap.name}</span>
                  <div className="flex items-center gap-2">
                    {basemap.is_public ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                    {currentBasemap === basemap.id && <Check className="h-5 w-5 text-green-500" />}
                  </div>
                </CardTitle>
                <CardDescription>{basemap.description || basemap.type.toUpperCase()}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    Zoom: {basemap.min_zoom}-{basemap.max_zoom}
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditBasemap(basemap);
                      }}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteBasemap(basemap.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Basemap</DialogTitle>
            <DialogDescription>
              Update the configuration for this basemap.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-name" className="text-right">
                Name
              </Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-description" className="text-right">
                Description
              </Label>
              <Textarea
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-url" className="text-right">
                URL Template
              </Label>
              <Input
                id="edit-url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-attribution" className="text-right">
                Attribution
              </Label>
              <Input
                id="edit-attribution"
                value={formData.attribution}
                onChange={(e) => setFormData({ ...formData, attribution: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-is_public" className="text-right">
                Public
              </Label>
              <div className="col-span-3">
                <input
                  type="checkbox"
                  id="edit-is_public"
                  checked={formData.is_public}
                  onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm text-gray-600">Allow others to use this basemap</span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateBasemap} disabled={loading || !formData.name}>
              {loading ? 'Updating...' : 'Update Basemap'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}