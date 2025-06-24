# Enhanced demo endpoint with debugging capabilities

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/demo/basemap-debug/{basemap_id}", response_class=HTMLResponse)
async def demo_basemap_debug(basemap_id: str):
    """Enhanced demo page with extensive debugging for custom basemaps."""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mundi Basemap Debug - {basemap_id}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet">
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        .info-panel {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 400px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        .debug-log {{
            background: #f0f0f0;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 300px;
            overflow-y: auto;
        }}
        .coordinate-display {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 14px;
            z-index: 1000;
        }}
        .status {{ 
            padding: 5px 10px; 
            border-radius: 4px; 
            margin: 5px 0;
            font-weight: bold;
        }}
        .status.success {{ background: #4CAF50; color: white; }}
        .status.error {{ background: #f44336; color: white; }}
        .status.loading {{ background: #2196F3; color: white; }}
        button {{
            background: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }}
        button:hover {{ background: #1976D2; }}
        .grid-toggle {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <h3>🔍 Basemap Debug Tool</h3>
        <p><strong>Basemap ID:</strong> <code>{basemap_id}</code></p>
        <div id="status-display"></div>
        
        <div>
            <button onclick="loadBasemapInfo()">Load Basemap Info</button>
            <button onclick="testDataEndpoint()">Test Data Endpoint</button>
            <button onclick="reloadMap()">Reload Map</button>
            <button onclick="clearLog()">Clear Log</button>
        </div>
        
        <div id="basemap-info"></div>
        
        <h4>Debug Log:</h4>
        <div id="debug-log" class="debug-log"></div>
    </div>
    
    <div class="grid-toggle">
        <button onclick="toggleGrid()">Toggle Grid</button>
        <button onclick="toggleWorldModel()">Toggle World Model</button>
    </div>
    
    <div id="coordinate-display" class="coordinate-display">
        <div>Mouse: <span id="mouse-coords">Move mouse over map</span></div>
        <div>Center: <span id="center-coords">-</span></div>
        <div>Zoom: <span id="zoom-level">-</span></div>
        <div>Bounds: <span id="bounds-coords">-</span></div>
    </div>
    
    <div id="map"></div>

    <script>
        let map;
        let debugLog = [];
        let gridVisible = false;
        let worldModelApplied = false;
        
        // Logging function
        function log(message, data = null) {{
            const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
            const logEntry = `[${{timestamp}}] ${{message}}`;
            debugLog.push(logEntry);
            if (data) {{
                debugLog.push(JSON.stringify(data, null, 2));
            }}
            console.log(message, data || '');
            updateDebugLog();
        }}
        
        function updateDebugLog() {{
            const logElement = document.getElementById('debug-log');
            logElement.textContent = debugLog.slice(-50).join('\\n');
            logElement.scrollTop = logElement.scrollHeight;
        }}
        
        function clearLog() {{
            debugLog = [];
            updateDebugLog();
        }}
        
        function setStatus(message, type = 'loading') {{
            document.getElementById('status-display').innerHTML = 
                `<div class="status ${{type}}">${{message}}</div>`;
        }}
        
        // Test data endpoint
        async function testDataEndpoint() {{
            try {{
                setStatus('Testing data endpoint...', 'loading');
                log('Testing /api/basemaps/{basemap_id}/data endpoint');
                
                const response = await fetch(`/api/basemaps/{basemap_id}/data`);
                log(`Data endpoint response status: ${{response.status}}`);
                
                if (response.ok) {{
                    const data = await response.json();
                    log('Data endpoint successful', {{
                        type: data.type,
                        features: data.features ? data.features.length : 'N/A'
                    }});
                    setStatus('Data endpoint working!', 'success');
                }} else {{
                    const error = await response.text();
                    log('Data endpoint error', error);
                    setStatus(`Data endpoint error: ${{response.status}}`, 'error');
                }}
            }} catch (error) {{
                log('Data endpoint exception', error.message);
                setStatus('Data endpoint failed', 'error');
            }}
        }}
        
        async function loadBasemapInfo() {{
            try {{
                setStatus('Loading basemap info...', 'loading');
                log('Fetching basemap info from /api/basemaps/{basemap_id}');
                
                const response = await fetch(`/api/basemaps/{basemap_id}`);
                const basemap = await response.json();
                
                log('Basemap info received', basemap);
                
                document.getElementById('basemap-info').innerHTML = `
                    <hr>
                    <h4>${{basemap.name}}</h4>
                    <p><strong>Type:</strong> ${{basemap.tile_format}}</p>
                    <p><strong>URL Template:</strong> <code>${{basemap.tile_url_template}}</code></p>
                    <p><strong>Zoom Range:</strong> ${{basemap.min_zoom}}-${{basemap.max_zoom}}</p>
                    <p><strong>Attribution:</strong> ${{basemap.attribution}}</p>
                    <p><strong>Bounds:</strong> ${{JSON.stringify(basemap.bounds)}}</p>
                    <p><strong>Center:</strong> ${{JSON.stringify(basemap.center)}}</p>
                    <p><strong>World Model:</strong> ${{basemap.world_model_id || 'None'}}</p>
                    <details>
                        <summary>Full JSON</summary>
                        <pre style="font-size: 10px;">${{JSON.stringify(basemap, null, 2)}}</pre>
                    </details>
                `;
                setStatus('Basemap info loaded', 'success');
            }} catch (error) {{
                log('Error loading basemap info', error.message);
                setStatus('Failed to load basemap info', 'error');
                document.getElementById('basemap-info').innerHTML = 
                    '<p style="color: red;">Error: ' + error.message + '</p>';
            }}
        }}
        
        function updateCoordinateDisplay() {{
            if (!map) return;
            
            const center = map.getCenter();
            const zoom = map.getZoom();
            const bounds = map.getBounds();
            
            document.getElementById('center-coords').textContent = 
                `[${{center.lng.toFixed(4)}}, ${{center.lat.toFixed(4)}}]`;
            document.getElementById('zoom-level').textContent = zoom.toFixed(2);
            document.getElementById('bounds-coords').textContent = 
                `SW: [${{bounds.getSouthWest().lng.toFixed(2)}}, ${{bounds.getSouthWest().lat.toFixed(2)}}] ` +
                `NE: [${{bounds.getNorthEast().lng.toFixed(2)}}, ${{bounds.getNorthEast().lat.toFixed(2)}}]`;
        }}
        
        function toggleGrid() {{
            if (!map || !map.isStyleLoaded()) return;
            
            gridVisible = !gridVisible;
            
            if (gridVisible) {{
                // Add grid source and layer
                if (!map.getSource('grid')) {{
                    map.addSource('grid', {{
                        type: 'geojson',
                        data: createGridGeoJSON()
                    }});
                }}
                
                if (!map.getLayer('grid-lines')) {{
                    map.addLayer({{
                        id: 'grid-lines',
                        type: 'line',
                        source: 'grid',
                        paint: {{
                            'line-color': '#000',
                            'line-width': 1,
                            'line-opacity': 0.3
                        }}
                    }});
                }}
                
                if (!map.getLayer('grid-labels')) {{
                    map.addLayer({{
                        id: 'grid-labels',
                        type: 'symbol',
                        source: 'grid',
                        filter: ['==', '$type', 'Point'],
                        layout: {{
                            'text-field': ['get', 'label'],
                            'text-size': 10,
                            'text-anchor': 'bottom-left',
                            'text-offset': [0.5, -0.5]
                        }},
                        paint: {{
                            'text-color': '#000',
                            'text-halo-color': '#fff',
                            'text-halo-width': 2
                        }}
                    }});
                }}
            }} else {{
                if (map.getLayer('grid-lines')) map.removeLayer('grid-lines');
                if (map.getLayer('grid-labels')) map.removeLayer('grid-labels');
            }}
        }}
        
        function createGridGeoJSON() {{
            const features = [];
            const step = 50; // Grid step size
            
            // Create grid lines and labels
            for (let lng = -180; lng <= 180; lng += step) {{
                // Vertical lines
                features.push({{
                    type: 'Feature',
                    geometry: {{
                        type: 'LineString',
                        coordinates: [[lng, -90], [lng, 90]]
                    }}
                }});
                
                // Labels for longitude
                features.push({{
                    type: 'Feature',
                    geometry: {{
                        type: 'Point',
                        coordinates: [lng, 0]
                    }},
                    properties: {{
                        label: `${{lng}}°`
                    }}
                }});
            }}
            
            for (let lat = -90; lat <= 90; lat += step) {{
                // Horizontal lines
                features.push({{
                    type: 'Feature',
                    geometry: {{
                        type: 'LineString',
                        coordinates: [[-180, lat], [180, lat]]
                    }}
                }});
                
                // Labels for latitude
                if (lat !== 0) {{ // Skip 0 to avoid overlap
                    features.push({{
                        type: 'Feature',
                        geometry: {{
                            type: 'Point',
                            coordinates: [0, lat]
                        }},
                        properties: {{
                            label: `${{lat}}°`
                        }}
                    }});
                }}
            }}
            
            return {{
                type: 'FeatureCollection',
                features: features
            }};
        }}
        
        function toggleWorldModel() {{
            // This would apply/remove world model transformation
            worldModelApplied = !worldModelApplied;
            log(`World model transformation: ${{worldModelApplied ? 'ON' : 'OFF'}}`);
            // In a real implementation, this would reload the map with transformation
        }}
        
        async function initMap() {{
            try {{
                setStatus('Initializing map...', 'loading');
                log('Starting map initialization');
                
                // First, try to get the style
                log('Fetching basemap style from /api/basemaps/{basemap_id}/style');
                const response = await fetch('/api/basemaps/{basemap_id}/style');
                
                if (!response.ok) {{
                    throw new Error(`Style endpoint returned ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const style = await response.json();
                log('Style loaded successfully', {{
                    version: style.version,
                    name: style.name,
                    sources: Object.keys(style.sources),
                    layers: style.layers.map(l => `${{l.id}} (${{l.type}})`)
                }});
                
                // Initialize map
                log('Creating MapLibre map instance');
                map = new maplibregl.Map({{
                    container: 'map',
                    style: style,
                    center: style.center || [0, 0],
                    zoom: style.zoom || 2,
                    renderWorldCopies: false // Important for fantasy worlds
                }});
                
                // Add navigation controls
                map.addControl(new maplibregl.NavigationControl());
                
                // Map event handlers
                map.on('load', function() {{
                    log('Map loaded successfully');
                    setStatus('Map loaded!', 'success');
                    loadBasemapInfo();
                    updateCoordinateDisplay();
                    
                    // Log map state
                    log('Map state after load', {{
                        center: map.getCenter(),
                        zoom: map.getZoom(),
                        bearing: map.getBearing(),
                        pitch: map.getPitch(),
                        bounds: map.getBounds()
                    }});
                }});
                
                map.on('error', function(e) {{
                    log('Map error', {{
                        error: e.error,
                        message: e.error?.message || 'Unknown error',
                        sourceId: e.sourceId,
                        layerId: e.layerId
                    }});
                    setStatus('Map error occurred', 'error');
                }});
                
                map.on('move', updateCoordinateDisplay);
                
                map.on('mousemove', function(e) {{
                    document.getElementById('mouse-coords').textContent = 
                        `[${{e.lngLat.lng.toFixed(4)}}, ${{e.lngLat.lat.toFixed(4)}}]`;
                }});
                
                // Log source and layer events
                map.on('sourcedata', function(e) {{
                    if (e.isSourceLoaded) {{
                        log(`Source loaded: ${{e.sourceId}}`);
                    }}
                }});
                
            }} catch (error) {{
                log('Failed to initialize map', {{
                    error: error.message,
                    stack: error.stack
                }});
                setStatus('Failed to initialize map', 'error');
                
                document.getElementById('map').innerHTML = `
                    <div style="padding: 20px; text-align: center; background: #ffebee;">
                        <h3 style="color: #c62828;">Error Loading Map</h3>
                        <p>${{error.message}}</p>
                        <details style="text-align: left; max-width: 600px; margin: 20px auto;">
                            <summary>Error Details</summary>
                            <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">
${{error.stack || error}}
                            </pre>
                        </details>
                    </div>
                `;
            }}
        }}
        
        function reloadMap() {{
            log('Reloading map...');
            debugLog = [];
            if (map) {{
                map.remove();
                map = null;
            }}
            document.getElementById('map').innerHTML = '';
            initMap();
        }}
        
        // Initialize map when page loads
        window.addEventListener('load', function() {{
            log('Page loaded, initializing map');
            initMap();
        }});
        
        // Also log any uncaught errors
        window.addEventListener('error', function(e) {{
            log('Uncaught error', {{
                message: e.message,
                filename: e.filename,
                line: e.lineno,
                column: e.colno
            }});
        }});
    </script>
</body>
</html>
"""
    
    return html_content