#!/usr/bin/env python3
"""
Always visible precipitation injection for debugging.
"""

def inject_diagnostic_precip_overlay(html: str, *, data_by_hour, interval_min: int = 60, zmax: float = 10.0) -> str:
    """
    Inject always visible precipitation overlay - this version renders precipitation 
    regardless of button state using bright, highly visible colors.
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
<!-- ALWAYS VISIBLE PRECIPITATION DEBUG OVERLAY -->
<script>
window.precipData = {data_json};
window.precipIntervalMin = {interval_min};
window.precipZmax = {zmax};

console.log("[PRECIP-ALWAYS] Precipitation data loaded:", Object.keys(window.precipData).length, "hours");
for (const [hour, data] of Object.entries(window.precipData)) {{
    console.log("[PRECIP-ALWAYS] Hour", hour, "has", data.length, "points");
}}

(function() {{
    console.log("[PRECIP-ALWAYS] Always visible precipitation debugging enabled");
    
    let precipCanvas = null;
    let precipCtx = null;
    let mapContainer = null;
    
    // Bright, visible colors for debugging
    function debugColorFor(intensity) {{
        if (intensity <= 0) return 'rgba(255, 0, 255, 0.8)'; // Bright magenta for zero
        if (intensity <= 0.1) return 'rgba(255, 255, 0, 0.8)'; // Bright yellow
        if (intensity <= 0.5) return 'rgba(255, 165, 0, 0.8)'; // Orange
        if (intensity <= 1.0) return 'rgba(255, 0, 0, 0.8)';   // Red
        return 'rgba(128, 0, 128, 0.8)'; // Purple for heavy rain
    }}
    
    function setupAlwaysVisibleCanvas() {{
        const plotlyDiv = document.querySelector('.js-plotly-plot');
        if (!plotlyDiv) {{
            console.log("[PRECIP-ALWAYS] No plotly div found, retrying...");
            setTimeout(setupAlwaysVisibleCanvas, 500);
            return;
        }}
        
        mapContainer = plotlyDiv.querySelector('.mapboxgl-map');
        if (!mapContainer) {{
            console.log("[PRECIP-ALWAYS] No mapbox container found, retrying...");
            setTimeout(setupAlwaysVisibleCanvas, 500);
            return;
        }}
        
        console.log("[PRECIP-ALWAYS] Setting up always visible canvas");
        
        // Create precipitation canvas
        precipCanvas = document.createElement('canvas');
        precipCanvas.id = 'precip-debug-canvas';
        precipCanvas.style.position = 'absolute';
        precipCanvas.style.top = '0';
        precipCanvas.style.left = '0';
        precipCanvas.style.pointerEvents = 'none';
        precipCanvas.style.zIndex = '1000'; // Very high z-index
        precipCanvas.style.border = '3px solid lime'; // Bright green border for visibility
        precipCanvas.width = mapContainer.clientWidth;
        precipCanvas.height = mapContainer.clientHeight;
        
        mapContainer.appendChild(precipCanvas);
        precipCtx = precipCanvas.getContext('2d');
        
        console.log("[PRECIP-ALWAYS] Canvas created:", precipCanvas.width, 'x', precipCanvas.height);
        
        // Draw a test pattern immediately
        drawTestPattern();
        
        // Draw precipitation data if available
        setTimeout(() => {{
            console.log("[PRECIP-ALWAYS] Drawing initial precipitation");
            drawAlwaysVisiblePrecip();
        }}, 1000);
        
        // Update on resize
        window.addEventListener('resize', () => {{
            precipCanvas.width = mapContainer.clientWidth;
            precipCanvas.height = mapContainer.clientHeight;
            drawTestPattern();
            drawAlwaysVisiblePrecip();
        }});
        
        // Update when animation changes
        setInterval(drawAlwaysVisiblePrecip, 2000); // Update every 2 seconds
    }}
    
    function drawTestPattern() {{
        if (!precipCtx) return;
        
        console.log("[PRECIP-ALWAYS] Drawing test pattern");
        
        // Clear canvas
        precipCtx.clearRect(0, 0, precipCanvas.width, precipCanvas.height);
        
        // Draw corner markers
        precipCtx.fillStyle = 'red';
        precipCtx.fillRect(0, 0, 20, 20); // Top-left
        precipCtx.fillRect(precipCanvas.width - 20, 0, 20, 20); // Top-right
        precipCtx.fillRect(0, precipCanvas.height - 20, 20, 20); // Bottom-left
        precipCtx.fillRect(precipCanvas.width - 20, precipCanvas.height - 20, 20, 20); // Bottom-right
        
        // Draw center marker
        const centerX = precipCanvas.width / 2;
        const centerY = precipCanvas.height / 2;
        precipCtx.fillStyle = 'lime';
        precipCtx.beginPath();
        precipCtx.arc(centerX, centerY, 50, 0, 2 * Math.PI);
        precipCtx.fill();
        
        // Draw text
        precipCtx.fillStyle = 'black';
        precipCtx.font = '16px Arial';
        precipCtx.fillText('ALWAYS VISIBLE PRECIP', 30, 50);
    }}
    
    function drawAlwaysVisiblePrecip() {{
        if (!precipCtx || !window.precipData) return;
        
        console.log("[PRECIP-ALWAYS] Drawing precipitation overlay");
        
        // Get current time from Plotly
        let currentTime = null;
        try {{
            const plotlyDiv = document.querySelector('.js-plotly-plot');
            if (plotlyDiv && plotlyDiv._fullLayout && plotlyDiv._fullLayout.sliders) {{
                const slider = plotlyDiv._fullLayout.sliders[0];
                if (slider && slider.active !== undefined) {{
                    const step = slider.steps[slider.active];
                    currentTime = step.label;
                }}
            }}
        }} catch (e) {{
            console.log("[PRECIP-ALWAYS] Could not get current time:", e);
        }}
        
        // If no current time, use first available
        if (!currentTime) {{
            const keys = Object.keys(window.precipData);
            currentTime = keys.length > 0 ? keys[0] : null;
        }}
        
        if (!currentTime) {{
            console.log("[PRECIP-ALWAYS] No time available for precipitation");
            return;
        }}
        
        console.log("[PRECIP-ALWAYS] Drawing for time:", currentTime);
        
        const data = window.precipData[currentTime] || [];
        console.log("[PRECIP-ALWAYS] Data points:", data.length);
        
        if (data.length === 0) {{
            console.log("[PRECIP-ALWAYS] No precipitation data for time:", currentTime);
            return;
        }}
        
        // Redraw test pattern first
        drawTestPattern();
        
        // Get map bounds
        const plotlyDiv = document.querySelector('.js-plotly-plot');
        const layout = plotlyDiv._fullLayout;
        const mapbox = layout.mapbox;
        
        if (!mapbox) {{
            console.log("[PRECIP-ALWAYS] No mapbox layout found");
            return;
        }}
        
        // Draw each precipitation point
        data.forEach((point, index) => {{
            const [lat, lon, intensity] = point;
            
            // Convert lat/lon to screen coordinates (simplified)
            const centerLat = mapbox.center ? mapbox.center.lat : 51.5074;
            const centerLon = mapbox.center ? mapbox.center.lon : -0.1278;
            const zoom = mapbox.zoom || 10;
            
            const scale = Math.pow(2, zoom - 8) * 40000; // Adjusted scale
            const x = precipCanvas.width / 2 + (lon - centerLon) * scale * Math.cos(centerLat * Math.PI / 180);
            const y = precipCanvas.height / 2 - (lat - centerLat) * scale;
            
            // Draw all points, even if off-screen, but mark them
            const color = debugColorFor(intensity);
            const radius = Math.max(30, intensity * 50); // Large, visible radius
            
            // Draw with glow effect
            const gradient = precipCtx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, color);
            gradient.addColorStop(1, 'rgba(0,0,0,0.2)');
            
            precipCtx.fillStyle = gradient;
            precipCtx.beginPath();
            precipCtx.arc(x, y, radius, 0, 2 * Math.PI);
            precipCtx.fill();
            
            // Add text label
            precipCtx.fillStyle = 'white';
            precipCtx.font = 'bold 14px Arial';
            precipCtx.strokeStyle = 'black';
            precipCtx.lineWidth = 2;
            precipCtx.strokeText(intensity.toFixed(2), x + radius + 5, y);
            precipCtx.fillText(intensity.toFixed(2), x + radius + 5, y);
            
            if (index < 3) {{
                console.log(`[PRECIP-ALWAYS] Point ${{index}}: lat=${{lat}}, lon=${{lon}}, intensity=${{intensity}}, screen=(${{x.toFixed(0)}}, ${{y.toFixed(0)}}), radius=${{radius}}`);
            }}
        }});
        
        console.log("[PRECIP-ALWAYS] Finished drawing precipitation");
    }}
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', setupAlwaysVisibleCanvas);
    }} else {{
        setupAlwaysVisibleCanvas();
    }}
    
    console.log("[PRECIP-ALWAYS] Always visible precipitation debug system initialized");
}})();
</script>
"""
    
    # Find where to inject (before </body> or at the end)
    if '</body>' in html:
        return html.replace('</body>', injection + '</body>')
    else:
        return html + injection

if __name__ == "__main__":
    print("Always visible precipitation injection module ready!")
