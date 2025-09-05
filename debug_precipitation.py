#!/usr/bin/env python3
"""
Debug precipitation overlay system by creating a simplified test
"""

import os
import json
from pathlib import Path


def create_debug_precip_html():
    """Create a minimal HTML file to test precipitation overlay independently"""
    
    # Create fake precipitation data that should definitely be visible
    fake_precip_data = {
        "intervalMin": 60,
        "zmax": 2.0,  # Very low threshold so any rain shows up
        "hours": {
            "2023-11-02T06:00:00+00:00": [
                [51.5074, -0.1278, 5.0],  # London center - heavy rain
                [51.5100, -0.1300, 8.0],  # North of London - very heavy
                [51.5050, -0.1250, 6.0],  # South of London - heavy
                [51.5074, -0.1200, 4.0],  # East of London - moderate
                [51.5074, -0.1350, 7.0],  # West of London - very heavy
            ],
            "2023-11-02T07:00:00+00:00": [
                [51.5074, -0.1278, 10.0], # London center - extreme rain
                [51.5120, -0.1320, 12.0], # Heavy everywhere
                [51.5030, -0.1230, 9.0],
                [51.5074, -0.1180, 8.0],
                [51.5074, -0.1380, 11.0],
            ]
        }
    }
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Precipitation Debug Test</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        #map {{ width: 100vw; height: 100vh; }}
        #controls {{ position: absolute; top: 10px; left: 10px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; }}
        .btn {{ margin: 5px; padding: 10px; cursor: pointer; border: 1px solid #ccc; background: #f0f0f0; }}
        .btn.active {{ background: #4CAF50; color: white; box-shadow: 0 0 10px rgba(76, 175, 80, 0.5); }}
        #precip-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; display: block; z-index: 5;
            border: 2px solid red; /* Debug border */
        }}
        #debug {{ position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; max-width: 300px; }}
    </style>
</head>
<body>
    <div id="controls">
        <div class="btn" id="precipBtn">☔ Toggle Precipitation</div>
        <div class="btn" id="debugBtn">🔍 Debug Info</div>
    </div>
    <div id="debug"></div>
    <div id="map"></div>

    <script>
        // Inject precipitation data
        window.__PRECIP = {json.dumps(fake_precip_data)};
        window._precipEnabled = true;
        
        const debugDiv = document.getElementById('debug');
        const precipBtn = document.getElementById('precipBtn');
        const debugBtn = document.getElementById('debugBtn');
        let showDebug = false;
        
        function log(msg) {{
            console.log('[DEBUG]', msg);
            if (showDebug) {{
                debugDiv.innerHTML += msg + '<br>';
                debugDiv.scrollTop = debugDiv.scrollHeight;
            }}
        }}
        
        // Create map
        const mapData = [{{
            type: 'scattermap',
            lat: [51.5074],
            lon: [-0.1278],
            mode: 'markers',
            marker: {{ size: 10, color: 'red' }},
            name: 'London Center'
        }}];
        
        const layout = {{
            map: {{
                style: 'open-street-map',
                center: {{ lat: 51.5074, lon: -0.1278 }},
                zoom: 11
            }},
            margin: {{ t: 0, b: 0, l: 0, r: 0 }}
        }};
        
        Plotly.newPlot('map', mapData, layout).then(() => {{
            log('Map created successfully');
            setupPrecipitationOverlay();
        }});
        
        function setupPrecipitationOverlay() {{
            const mapDiv = document.getElementById('map');
            const plotDiv = mapDiv.querySelector('.plotly-graph-div');
            if (!plotDiv) {{
                log('ERROR: Could not find plotly-graph-div');
                return;
            }}
            
            // Ensure relative positioning
            if (getComputedStyle(plotDiv).position === 'static') {{
                plotDiv.style.position = 'relative';
            }}
            
            // Create canvas
            let canvas = document.getElementById('precip-overlay');
            if (!canvas) {{
                canvas = document.createElement('canvas');
                canvas.id = 'precip-overlay';
                plotDiv.appendChild(canvas);
                log('Canvas created and added to plot div');
            }}
            
            // Size canvas
            const rect = plotDiv.getBoundingClientRect();
            canvas.width = Math.floor(rect.width);
            canvas.height = Math.floor(rect.height);
            canvas.style.width = rect.width + 'px';
            canvas.style.height = rect.height + 'px';
            
            log(`Canvas sized: ${{canvas.width}} x ${{canvas.height}}`);
            
            drawPrecipitation();
        }}
        
        function lon2x(lon, zoom) {{
            return (lon + 180) / 360 * Math.pow(2, zoom);
        }}
        
        function lat2y(lat, zoom) {{
            const rad = lat * Math.PI / 180;
            return (1 - Math.asinh(Math.tan(rad)) / Math.PI) / 2 * Math.pow(2, zoom);
        }}
        
        function drawPrecipitation() {{
            const canvas = document.getElementById('precip-overlay');
            if (!canvas) {{
                log('ERROR: Canvas not found');
                return;
            }}
            
            const ctx = canvas.getContext('2d');
            if (!ctx) {{
                log('ERROR: Could not get canvas context');
                return;
            }}
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (!window._precipEnabled) {{
                log('Precipitation disabled, clearing canvas');
                return;
            }}
            
            // Get current map state
            const mapDiv = document.getElementById('map');
            const gd = mapDiv.querySelector('.plotly-graph-div');
            const fullLayout = gd._fullLayout;
            const map = fullLayout.map;
            
            if (!map) {{
                log('ERROR: Could not get map layout');
                return;
            }}
            
            const center = map.center;
            const zoom = map.zoom;
            
            log(`Map center: ${{center.lat}}, ${{center.lon}}, zoom: ${{zoom}}`);
            
            // Get precipitation data for current hour
            const hourKey = "2023-11-02T06:00:00+00:00"; // Fixed for testing
            const precipData = window.__PRECIP.hours[hourKey];
            
            if (!precipData || precipData.length === 0) {{
                log(`No precipitation data for hour: ${{hourKey}}`);
                return;
            }}
            
            log(`Drawing ${{precipData.length}} precipitation points`);
            
            // Draw precipitation
            ctx.save();
            ctx.globalCompositeOperation = 'lighter';
            
            precipData.forEach((point, i) => {{
                const [lat, lon, intensity] = point;
                
                // Convert lat/lon to canvas coordinates
                const x = lon2x(lon, zoom);
                const y = lat2y(lat, zoom);
                const centerX = lon2x(center.lon, zoom);
                const centerY = lat2y(center.lat, zoom);
                
                const pixelX = (x - centerX) * 256 + canvas.width / 2;
                const pixelY = (y - centerY) * 256 + canvas.height / 2;
                
                // Calculate color and size based on intensity
                const normalizedIntensity = Math.min(1, intensity / window.__PRECIP.zmax);
                const radius = 30 + 40 * normalizedIntensity;
                const alpha = 0.3 + 0.6 * normalizedIntensity;
                
                // Create gradient
                const gradient = ctx.createRadialGradient(pixelX, pixelY, 0, pixelX, pixelY, radius);
                gradient.addColorStop(0, `rgba(0, 100, 255, ${{alpha}})`);
                gradient.addColorStop(1, 'rgba(0, 100, 255, 0)');
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(pixelX, pixelY, radius, 0, Math.PI * 2);
                ctx.fill();
                
                log(`Point ${{i}}: lat=${{lat}}, lon=${{lon}}, intensity=${{intensity}}, pixel=(${{Math.round(pixelX)}}, ${{Math.round(pixelY)}}), radius=${{Math.round(radius)}}`);
            }});
            
            ctx.restore();
            
            log('Precipitation drawing complete');
        }}
        
        // Event handlers
        precipBtn.addEventListener('click', () => {{
            window._precipEnabled = !window._precipEnabled;
            precipBtn.classList.toggle('active', window._precipEnabled);
            log(`Precipitation toggled: ${{window._precipEnabled ? 'ON' : 'OFF'}}`);
            drawPrecipitation();
        }});
        
        debugBtn.addEventListener('click', () => {{
            showDebug = !showDebug;
            debugDiv.style.display = showDebug ? 'block' : 'none';
            debugBtn.classList.toggle('active', showDebug);
            if (showDebug) {{
                debugDiv.innerHTML = 'Debug mode enabled<br>';
                log('Debug mode enabled');
            }}
        }});
        
        // Update on map changes
        const mapDiv = document.getElementById('map');
        const gd = mapDiv.querySelector('.plotly-graph-div');
        if (gd) {{
            gd.addEventListener('plotly_relayout', () => {{
                log('Map relayout detected');
                setTimeout(drawPrecipitation, 100);
            }});
        }}
        
        // Initial state
        precipBtn.classList.add('active');
        log('Debug precipitation test loaded');
    </script>
</body>
</html>"""
    
    debug_path = Path("debug_precipitation.html")
    debug_path.write_text(html_content)
    
    print(f"✅ Created debug precipitation test: {debug_path.absolute()}")
    print("🔍 Open this file in your browser to test precipitation overlay")
    print("📋 Features:")
    print("   • ☔ Toggle button to enable/disable precipitation")
    print("   • 🔍 Debug button to show detailed logs")
    print("   • Red border around canvas for visibility")
    print("   • Console logs for debugging")
    print("   • Fixed heavy rain data over London")
    
    return debug_path


if __name__ == "__main__":
    create_debug_precip_html()
