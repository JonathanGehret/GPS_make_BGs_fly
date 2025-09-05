#!/usr/bin/env python3
"""
Fixed precipitation injection that works with OpenStreetMap/Plotly maps instead of Mapbox.
"""

def inject_diagnostic_precip_overlay(html: str, *, data_by_hour, interval_min: int = 60, zmax: float = 10.0) -> str:
    """
    Fixed precipitation overlay for OpenStreetMap-based Plotly visualizations.
    """
    
    # Convert data_by_hour to the format expected by JavaScript
    data_by_hour_js = {}
    for hour_dt, df in data_by_hour.items():
        hour_str = hour_dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        if not df.empty:
            # Convert to list of [lat, lon, intensity] arrays
            points = []
            for _, row in df.iterrows():
                points.append([float(row['lat']), float(row['lon']), float(row['precip_mm'])])
            data_by_hour_js[hour_str] = points
        else:
            data_by_hour_js[hour_str] = []
    
    import json
    data_json = json.dumps(data_by_hour_js)
    
    injection = f"""
<!-- FIXED OPENSTREETMAP PRECIPITATION OVERLAY -->
<script>
window.precipData = {data_json};
window.precipIntervalMin = {interval_min};
window.precipZmax = {zmax};

console.log("[PRECIP-FIXED] Precipitation data loaded for OpenStreetMap:", Object.keys(window.precipData).length, "hours");
for (const [hour, data] of Object.entries(window.precipData)) {{
    console.log("[PRECIP-FIXED] Hour", hour, "has", data.length, "points");
}}

(function() {{
    console.log("[PRECIP-FIXED] Fixed OpenStreetMap precipitation overlay starting");
    
    let precipCanvas = null;
    let precipCtx = null;
    let plotlyDiv = null;
    
    // Bright, visible colors for debugging
    function debugColorFor(intensity) {{
        if (intensity <= 0) return 'rgba(255, 0, 255, 0.9)'; // Bright magenta for zero
        if (intensity <= 0.1) return 'rgba(255, 255, 0, 0.9)'; // Bright yellow
        if (intensity <= 0.5) return 'rgba(255, 165, 0, 0.9)'; // Orange
        if (intensity <= 1.0) return 'rgba(255, 0, 0, 0.9)';   // Red
        return 'rgba(128, 0, 128, 0.9)'; // Purple for heavy rain
    }}
    
    function setupFixedCanvas() {{
        plotlyDiv = document.querySelector('.js-plotly-plot');
        if (!plotlyDiv) {{
            console.log("[PRECIP-FIXED] No plotly div found, retrying...");
            setTimeout(setupFixedCanvas, 500);
            return;
        }}
        
        console.log("[PRECIP-FIXED] Found plotly div, setting up canvas overlay");
        
        // Create precipitation canvas directly on the plotly div
        precipCanvas = document.createElement('canvas');
        precipCanvas.id = 'precip-fixed-canvas';
        precipCanvas.style.position = 'absolute';
        precipCanvas.style.top = '0';
        precipCanvas.style.left = '0';
        precipCanvas.style.pointerEvents = 'none';
        precipCanvas.style.zIndex = '1000';
        precipCanvas.style.border = '2px solid cyan'; // Cyan border for visibility
        
        // Size to match the plotly div
        const rect = plotlyDiv.getBoundingClientRect();
        precipCanvas.width = plotlyDiv.clientWidth;
        precipCanvas.height = plotlyDiv.clientHeight;
        
        plotlyDiv.appendChild(precipCanvas);
        precipCtx = precipCanvas.getContext('2d');
        
        console.log("[PRECIP-FIXED] Canvas created:", precipCanvas.width, 'x', precipCanvas.height);
        
        // Draw test pattern to confirm canvas works
        drawTestPattern();
        
        // Draw precipitation data
        setTimeout(() => {{
            console.log("[PRECIP-FIXED] Drawing initial precipitation");
            drawFixedPrecip();
        }}, 1000);
        
        // Update on resize
        window.addEventListener('resize', () => {{
            precipCanvas.width = plotlyDiv.clientWidth;
            precipCanvas.height = plotlyDiv.clientHeight;
            drawTestPattern();
            drawFixedPrecip();
        }});
        
        // Update when animation changes (multiple methods)
        setInterval(drawFixedPrecip, 3000); // Update every 3 seconds
        
        // Also listen for plotly events
        if (plotlyDiv.on) {{
            plotlyDiv.on('plotly_animated', drawFixedPrecip);
            plotlyDiv.on('plotly_sliderchange', drawFixedPrecip);
        }}
    }}
    
    function drawTestPattern() {{
        if (!precipCtx) return;
        
        console.log("[PRECIP-FIXED] Drawing test pattern");
        
        // Clear canvas
        precipCtx.clearRect(0, 0, precipCanvas.width, precipCanvas.height);
        
        // Draw corner markers (smaller than before)
        precipCtx.fillStyle = 'cyan';
        precipCtx.fillRect(5, 5, 15, 15); // Top-left
        precipCtx.fillRect(precipCanvas.width - 20, 5, 15, 15); // Top-right
        precipCtx.fillRect(5, precipCanvas.height - 20, 15, 15); // Bottom-left
        precipCtx.fillRect(precipCanvas.width - 20, precipCanvas.height - 20, 15, 15); // Bottom-right
        
        // Draw center marker
        const centerX = precipCanvas.width / 2;
        const centerY = precipCanvas.height / 2;
        precipCtx.fillStyle = 'lime';
        precipCtx.beginPath();
        precipCtx.arc(centerX, centerY, 30, 0, 2 * Math.PI);
        precipCtx.fill();
        
        // Draw text
        precipCtx.fillStyle = 'black';
        precipCtx.font = 'bold 14px Arial';
        precipCtx.fillText('FIXED OSM PRECIP', 25, 35);
    }}
    
    function drawFixedPrecip() {{
        if (!precipCtx || !window.precipData || !plotlyDiv) return;
        
        console.log("[PRECIP-FIXED] Drawing precipitation for OpenStreetMap");
        
        // Get current time from Plotly slider
        let currentTime = null;
        try {{
            if (plotlyDiv._fullLayout && plotlyDiv._fullLayout.sliders) {{
                const slider = plotlyDiv._fullLayout.sliders[0];
                if (slider && slider.active !== undefined && slider.steps) {{
                    const step = slider.steps[slider.active];
                    currentTime = step.label;
                }}
            }}
        }} catch (e) {{
            console.log("[PRECIP-FIXED] Could not get current time from slider:", e);
        }}
        
        // If no current time, use first available
        if (!currentTime) {{
            const keys = Object.keys(window.precipData);
            currentTime = keys.length > 0 ? keys[0] : null;
            console.log("[PRECIP-FIXED] Using first available time:", currentTime);
        }}
        
        if (!currentTime) {{
            console.log("[PRECIP-FIXED] No time available for precipitation");
            return;
        }}
        
        console.log("[PRECIP-FIXED] Drawing for time:", currentTime);
        
        const data = window.precipData[currentTime] || [];
        console.log("[PRECIP-FIXED] Data points:", data.length);
        
        if (data.length === 0) {{
            console.log("[PRECIP-FIXED] No precipitation data for time:", currentTime);
            return;
        }}
        
        // Redraw test pattern first
        drawTestPattern();
        
        // Get map layout - for OpenStreetMap, it's under layout.map not layout.mapbox
        const layout = plotlyDiv._fullLayout;
        let map = null;
        
        if (layout.map) {{
            map = layout.map;
            console.log("[PRECIP-FIXED] Using layout.map (OpenStreetMap)");
        }} else if (layout.mapbox) {{
            map = layout.mapbox;
            console.log("[PRECIP-FIXED] Using layout.mapbox (fallback)");
        }} else {{
            console.log("[PRECIP-FIXED] No map layout found, using defaults");
        }}
        
        // Get map parameters
        let centerLat = 51.5074;
        let centerLon = -0.1278;
        let zoom = 10;
        
        if (map && map.center) {{
            centerLat = map.center.lat || centerLat;
            centerLon = map.center.lon || centerLon;
        }}
        if (map && map.zoom !== undefined) {{
            zoom = map.zoom;
        }}
        
        console.log("[PRECIP-FIXED] Map center:", centerLat, centerLon, "zoom:", zoom);
        
        // Draw each precipitation point
        let pointsDrawn = 0;
        data.forEach((point, index) => {{
            const [lat, lon, intensity] = point;
            
            // Convert lat/lon to screen coordinates using proper projection for OpenStreetMap
            const scale = Math.pow(2, zoom) * 256 / (2 * Math.PI);
            const latRad = lat * Math.PI / 180;
            const centerLatRad = centerLat * Math.PI / 180;
            
            // Web Mercator projection (used by OpenStreetMap)
            const x = precipCanvas.width / 2 + (lon - centerLon) * scale * Math.cos(centerLatRad);
            const y = precipCanvas.height / 2 - (Math.log(Math.tan(Math.PI/4 + latRad/2)) - Math.log(Math.tan(Math.PI/4 + centerLatRad/2))) * scale;
            
            // Draw if on screen or nearby
            if (x >= -100 && x <= precipCanvas.width + 100 && y >= -100 && y <= precipCanvas.height + 100) {{
                const color = debugColorFor(intensity);
                const radius = Math.max(20, intensity * 40); // Large, visible radius
                
                // Draw with glow effect
                const gradient = precipCtx.createRadialGradient(x, y, 0, x, y, radius);
                gradient.addColorStop(0, color);
                gradient.addColorStop(1, 'rgba(0,0,0,0.1)');
                
                precipCtx.fillStyle = gradient;
                precipCtx.beginPath();
                precipCtx.arc(x, y, radius, 0, 2 * Math.PI);
                precipCtx.fill();
                
                // Add text label with background
                precipCtx.fillStyle = 'white';
                precipCtx.strokeStyle = 'black';
                precipCtx.lineWidth = 2;
                precipCtx.font = 'bold 12px Arial';
                const text = intensity.toFixed(1);
                precipCtx.strokeText(text, x + radius + 5, y);
                precipCtx.fillText(text, x + radius + 5, y);
                
                pointsDrawn++;
                
                if (index < 3) {{
                    console.log(`[PRECIP-FIXED] Point ${{index}}: lat=${{lat}}, lon=${{lon}}, intensity=${{intensity}}, screen=(${{x.toFixed(0)}}, ${{y.toFixed(0)}})`);
                }}
            }}
        }});
        
        console.log("[PRECIP-FIXED] Drew", pointsDrawn, "precipitation points on screen");
    }}
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', setupFixedCanvas);
    }} else {{
        setupFixedCanvas();
    }}
    
    console.log("[PRECIP-FIXED] Fixed OpenStreetMap precipitation system initialized");
}})();
</script>
"""
    
    # Inject before closing body tag
    if '</body>' in html:
        return html.replace('</body>', injection + '</body>')
    else:
        return html + injection

if __name__ == "__main__":
    print("Fixed OpenStreetMap precipitation injection ready!")
    print("This version works with Plotly's OpenStreetMap style instead of Mapbox.")
