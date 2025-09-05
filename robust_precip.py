#!/usr/bin/env python3
"""
Ultra-robust precipitation injection with comprehensive error handling.
"""

def inject_diagnostic_precip_overlay(html: str, *, data_by_hour, interval_min: int = 60, zmax: float = 10.0) -> str:
    """
    Ultra-robust precipitation overlay with extensive error handling and logging.
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
<!-- ULTRA-ROBUST PRECIPITATION OVERLAY -->
<script>
(function() {{
    'use strict';
    
    // Global error handler
    window.addEventListener('error', function(e) {{
        console.error("[PRECIP-ROBUST] Global error:", e.error, e.message, e.filename, e.lineno);
    }});
    
    window.addEventListener('unhandledrejection', function(e) {{
        console.error("[PRECIP-ROBUST] Unhandled promise rejection:", e.reason);
    }});
    
    console.log("[PRECIP-ROBUST] Starting ultra-robust precipitation overlay");
    
    try {{
        window.precipData = {data_json};
        window.precipIntervalMin = {interval_min};
        window.precipZmax = {zmax};
        
        console.log("[PRECIP-ROBUST] Data loaded successfully:", Object.keys(window.precipData || {{}}).length, "hours");
        
        let precipCanvas = null;
        let precipCtx = null;
        let plotlyDiv = null;
        let isSetup = false;
        
        function safeLog(message, ...args) {{
            try {{
                console.log("[PRECIP-ROBUST]", message, ...args);
            }} catch (e) {{
                // Ignore logging errors
            }}
        }}
        
        function debugColorFor(intensity) {{
            try {{
                if (intensity <= 0) return 'rgba(255, 0, 255, 0.9)';
                if (intensity <= 0.1) return 'rgba(255, 255, 0, 0.9)';
                if (intensity <= 0.5) return 'rgba(255, 165, 0, 0.9)';
                if (intensity <= 1.0) return 'rgba(255, 0, 0, 0.9)';
                return 'rgba(128, 0, 128, 0.9)';
            }} catch (e) {{
                safeLog("Error in debugColorFor:", e);
                return 'rgba(255, 0, 0, 0.9)';
            }}
        }}
        
        function setupRobustCanvas() {{
            try {{
                safeLog("Setting up robust canvas...");
                
                if (isSetup) {{
                    safeLog("Canvas already setup, skipping");
                    return;
                }}
                
                plotlyDiv = document.querySelector('.js-plotly-plot');
                if (!plotlyDiv) {{
                    safeLog("No plotly div found, retrying in 1 second...");
                    setTimeout(setupRobustCanvas, 1000);
                    return;
                }}
                
                safeLog("Found plotly div, creating canvas");
                
                // Remove any existing canvas
                const existingCanvas = document.getElementById('precip-robust-canvas');
                if (existingCanvas) {{
                    existingCanvas.remove();
                }}
                
                precipCanvas = document.createElement('canvas');
                precipCanvas.id = 'precip-robust-canvas';
                precipCanvas.style.cssText = 'position:absolute;top:0;left:0;pointer-events:none;z-index:1000;border:2px solid magenta;';
                
                const rect = plotlyDiv.getBoundingClientRect();
                precipCanvas.width = Math.max(800, plotlyDiv.clientWidth || 800);
                precipCanvas.height = Math.max(600, plotlyDiv.clientHeight || 600);
                
                plotlyDiv.appendChild(precipCanvas);
                precipCtx = precipCanvas.getContext('2d');
                
                if (!precipCtx) {{
                    safeLog("ERROR: Could not get canvas context");
                    return;
                }}
                
                safeLog("Canvas created successfully:", precipCanvas.width, 'x', precipCanvas.height);
                
                isSetup = true;
                
                // Draw immediate test
                drawRobustTest();
                
                // Draw precipitation after a delay
                setTimeout(function() {{
                    try {{
                        drawRobustPrecip();
                    }} catch (e) {{
                        safeLog("Error drawing precipitation:", e);
                    }}
                }}, 2000);
                
                // Setup periodic updates
                setInterval(function() {{
                    try {{
                        drawRobustPrecip();
                    }} catch (e) {{
                        safeLog("Error in periodic update:", e);
                    }}
                }}, 5000);
                
            }} catch (e) {{
                safeLog("Error in setupRobustCanvas:", e);
                setTimeout(setupRobustCanvas, 2000);
            }}
        }}
        
        function drawRobustTest() {{
            try {{
                if (!precipCtx || !precipCanvas) return;
                
                safeLog("Drawing robust test pattern");
                
                precipCtx.clearRect(0, 0, precipCanvas.width, precipCanvas.height);
                
                // Draw magenta corners
                precipCtx.fillStyle = 'magenta';
                precipCtx.fillRect(0, 0, 20, 20);
                precipCtx.fillRect(precipCanvas.width - 20, 0, 20, 20);
                precipCtx.fillRect(0, precipCanvas.height - 20, 20, 20);
                precipCtx.fillRect(precipCanvas.width - 20, precipCanvas.height - 20, 20, 20);
                
                // Draw center circle
                const centerX = precipCanvas.width / 2;
                const centerY = precipCanvas.height / 2;
                precipCtx.fillStyle = 'lime';
                precipCtx.beginPath();
                precipCtx.arc(centerX, centerY, 40, 0, 2 * Math.PI);
                precipCtx.fill();
                
                // Draw text
                precipCtx.fillStyle = 'black';
                precipCtx.font = 'bold 16px Arial';
                precipCtx.fillText('ROBUST PRECIP TEST', 25, 45);
                precipCtx.fillText('Canvas Working!', 25, 65);
                
                safeLog("Test pattern drawn successfully");
                
            }} catch (e) {{
                safeLog("Error drawing test pattern:", e);
            }}
        }}
        
        function drawRobustPrecip() {{
            try {{
                if (!precipCtx || !window.precipData) {{
                    safeLog("Cannot draw precipitation - missing context or data");
                    return;
                }}
                
                safeLog("Drawing robust precipitation");
                
                // Get available times
                const availableTimes = Object.keys(window.precipData || {{}});
                if (availableTimes.length === 0) {{
                    safeLog("No precipitation times available");
                    return;
                }}
                
                // Use first available time for testing
                const currentTime = availableTimes[0];
                const data = window.precipData[currentTime] || [];
                
                safeLog("Using time:", currentTime, "with", data.length, "points");
                
                // Redraw test pattern
                drawRobustTest();
                
                if (data.length === 0) {{
                    safeLog("No precipitation data for selected time");
                    return;
                }}
                
                // Draw precipitation points with simple positioning
                let pointsDrawn = 0;
                for (let i = 0; i < Math.min(data.length, 10); i++) {{
                    try {{
                        const point = data[i];
                        const [lat, lon, intensity] = point;
                        
                        // Simple grid positioning for testing
                        const x = 100 + (i % 3) * 150;
                        const y = 100 + Math.floor(i / 3) * 100;
                        
                        const color = debugColorFor(intensity);
                        const radius = Math.max(25, intensity * 30);
                        
                        precipCtx.fillStyle = color;
                        precipCtx.beginPath();
                        precipCtx.arc(x, y, radius, 0, 2 * Math.PI);
                        precipCtx.fill();
                        
                        // Label
                        precipCtx.fillStyle = 'white';
                        precipCtx.strokeStyle = 'black';
                        precipCtx.lineWidth = 2;
                        precipCtx.font = 'bold 14px Arial';
                        const text = intensity.toFixed(1) + 'mm';
                        precipCtx.strokeText(text, x + radius + 5, y);
                        precipCtx.fillText(text, x + radius + 5, y);
                        
                        pointsDrawn++;
                        
                    }} catch (e) {{
                        safeLog("Error drawing point", i, ":", e);
                    }}
                }}
                
                safeLog("Drew", pointsDrawn, "precipitation test points");
                
            }} catch (e) {{
                safeLog("Error in drawRobustPrecip:", e);
            }}
        }}
        
        // Initialize with multiple fallbacks
        safeLog("Initializing robust precipitation system");
        
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', setupRobustCanvas);
        }} else {{
            setupRobustCanvas();
        }}
        
        // Also try after various delays
        setTimeout(setupRobustCanvas, 1000);
        setTimeout(setupRobustCanvas, 3000);
        setTimeout(setupRobustCanvas, 5000);
        
        safeLog("Robust precipitation system initialization complete");
        
    }} catch (e) {{
        console.error("[PRECIP-ROBUST] Fatal error in main block:", e);
    }}
}})();
</script>
"""
    
    # Inject before closing body tag
    if '</body>' in html:
        return html.replace('</body>', injection + '</body>')
    else:
        return html + injection

if __name__ == "__main__":
    print("Ultra-robust precipitation injection ready!")
    print("This version has comprehensive error handling and simple grid positioning for testing.")
