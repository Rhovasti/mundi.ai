# Demo endpoint to show custom basemap in action

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/demo/basemap/{basemap_id}", response_class=HTMLResponse)
async def demo_basemap(basemap_id: str):
    """Demo page showing a custom basemap in action."""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mundi Custom Basemap Demo</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet">
    <style>
        body {{ margin: 0; padding: 0; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        .info-panel {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 300px;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <h3>🗺️ Custom Basemap Demo</h3>
        <p><strong>Basemap ID:</strong> {basemap_id}</p>
        <p>This map loads your custom basemap using the Mundi custom basemap API.</p>
        <button onclick="loadBasemapInfo()">Show Basemap Info</button>
        <div id="basemap-info"></div>
    </div>
    <div id="map"></div>

    <script>
        let map;
        
        async function loadBasemapInfo() {{
            try {{
                const response = await fetch(`/api/basemaps/{basemap_id}`);
                const basemap = await response.json();
                document.getElementById('basemap-info').innerHTML = `
                    <hr>
                    <h4>${{basemap.name}}</h4>
                    <p><strong>Format:</strong> ${{basemap.tile_format}}</p>
                    <p><strong>Zoom Range:</strong> ${{basemap.min_zoom}}-${{basemap.max_zoom}}</p>
                    <p><strong>Attribution:</strong> ${{basemap.attribution}}</p>
                `;
            }} catch (error) {{
                document.getElementById('basemap-info').innerHTML = 
                    '<p style="color: red;">Error loading basemap info: ' + error.message + '</p>';
            }}
        }}
        
        async function initMap() {{
            try {{
                console.log('Loading basemap style for {basemap_id}...');
                const response = await fetch('/api/basemaps/{basemap_id}/style');
                
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const style = await response.json();
                console.log('Loaded style:', style);
                
                map = new maplibregl.Map({{
                    container: 'map',
                    style: style,
                    center: style.center || [0, 0],
                    zoom: style.zoom || 2
                }});
                
                map.on('load', function() {{
                    console.log('Map loaded successfully with custom basemap!');
                    loadBasemapInfo();
                }});
                
                map.on('error', function(e) {{
                    console.error('Map error:', e);
                }});
                
            }} catch (error) {{
                console.error('Failed to load basemap:', error);
                document.getElementById('map').innerHTML = `
                    <div style="padding: 20px; text-align: center;">
                        <h3>Error Loading Basemap</h3>
                        <p>${{error.message}}</p>
                        <p>Basemap ID: {basemap_id}</p>
                    </div>
                `;
            }}
        }}
        
        // Initialize map when page loads
        initMap();
    </script>
</body>
</html>
"""
    
    return html_content