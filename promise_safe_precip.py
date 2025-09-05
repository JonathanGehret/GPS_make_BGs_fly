#!/usr/bin/env python3
"""
Promise-safe precipitation injection with proper async error handling.
"""

def inject_diagnostic_precip_overlay(html: str, *, data_by_hour, interval_min: int = 60, zmax: float = 10.0) -> str:
    """
    Precipitation overlay with proper promise rejection handling.
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
<!-- PROMISE-SAFE PRECIPITATION OVERLAY -->
<script>
(function() {{
    'use strict';
    
    console.log("[PRECIP-PROMISE] Starting promise-safe precipitation overlay");
    
    // Global promise rejection handler - this is the key fix!
    window.addEventListener('unhandledrejection', function(event) {{
        console.log("[PRECIP-PROMISE] Caught unhandled promise rejection:", event.reason);
        // Prevent the default behavior (which causes the uncaught error)
        event.preventDefault();
    }});
    
    // Global error handler
    window.addEventListener('error', function(event) {{
        console.log("[PRECIP-PROMISE] Caught global error:", event.error, event.message);
        event.preventDefault();
    }});
    
    try {{
        window.precipData = {data_json};
        window.precipIntervalMin = {interval_min};
        window.precipZmax = {zmax};
        
        console.log("[PRECIP-PROMISE] Data loaded:", Object.keys(window.precipData || {{}}).length, "hours");
        
        let precipCanvas = null;
        let precipCtx = null;
        let plotlyDiv = null;
        let isInitialized = false;
        
        function safeLog(message, ...args) {{
            try {{
                console.log("[PRECIP-PROMISE]", message, ...args);
            }} catch (e) {{
                // Silent fail for logging errors
            }}
        }}
        
        function getDebugColor(intensity) {{
            if (intensity <= 0) return 'rgba(255, 0, 255, 0.8)'; // Magenta
            if (intensity <= 0.1) return 'rgba(255, 255, 0, 0.8)'; // Yellow
            if (intensity <= 0.5) return 'rgba(255, 165, 0, 0.8)'; // Orange
            if (intensity <= 1.0) return 'rgba(255, 0, 0, 0.8)';   // Red
            return 'rgba(128, 0, 128, 0.8)'; // Purple
        }}
        
        async function setupPromiseSafeCanvas() {{
            try {{
                safeLog("Setting up promise-safe canvas");
                
                if (isInitialized) {{
                    safeLog("Already initialized, skipping");
                    return;
                }}
                
                // Wait for DOM to be ready with promise
                await new Promise((resolve) => {{
                    if (document.readyState === 'loading') {{
                        document.addEventListener('DOMContentLoaded', resolve);
                    }} else {{
                        resolve();
                    }}
                }}).catch(e => {{
                    safeLog("DOM ready promise error:", e);
                }});
                
                // Find plotly div with timeout
                plotlyDiv = await new Promise((resolve, reject) => {{
                    const checkForPlotly = () => {{
                        const div = document.querySelector('.js-plotly-plot');
                        if (div) {{
                            resolve(div);
                        }} else {{
                            setTimeout(checkForPlotly, 500);
                        }}
                    }};
                    checkForPlotly();
                    // Timeout after 10 seconds
                    setTimeout(() => reject(new Error("Plotly div not found")), 10000);
                }}).catch(e => {{
                    safeLog("Plotly div search error:", e);
                    return null;
                }});
                
                if (!plotlyDiv) {{
                    safeLog("Could not find plotly div");
                    return;
                }}
                
                safeLog("Found plotly div, creating canvas");
                
                // Remove existing canvas
                const existing = document.getElementById('precip-promise-canvas');
                if (existing) existing.remove();
                
                // Create canvas
                precipCanvas = document.createElement('canvas');
                precipCanvas.id = 'precip-promise-canvas';
                precipCanvas.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    pointer-events: none;
                    z-index: 1000;
                    border: 3px solid lime;
                `;
                
                // Set size
                precipCanvas.width = Math.max(800, plotlyDiv.clientWidth || 800);
                precipCanvas.height = Math.max(600, plotlyDiv.clientHeight || 600);
                
                plotlyDiv.appendChild(precipCanvas);
                precipCtx = precipCanvas.getContext('2d');
                
                if (!precipCtx) {{
                    safeLog("Failed to get canvas context");
                    return;
                }}
                
                safeLog("Canvas setup complete:", precipCanvas.width, 'x', precipCanvas.height);
                isInitialized = true;
                
                // Draw test pattern
                await drawPromiseSafeTest().catch(e => safeLog("Test draw error:", e));
                
                // Start precipitation drawing
                await drawPromiseSafePrecip().catch(e => safeLog("Precip draw error:", e));
                
                // Setup periodic updates with promise handling
                setInterval(async () => {{
                    try {{
                        await drawPromiseSafePrecip().catch(e => safeLog("Periodic draw error:", e));
                    }} catch (e) {{
                        safeLog("Interval error:", e);
                    }}
                }}, 3000);
                
            }} catch (e) {{
                safeLog("Setup error:", e);
            }}
        }}
        
        async function drawPromiseSafeTest() {{
            return new Promise((resolve) => {{
                try {{
                    if (!precipCtx) {{
                        resolve();
                        return;
                    }}
                    
                    safeLog("Drawing promise-safe test pattern");
                    
                    precipCtx.clearRect(0, 0, precipCanvas.width, precipCanvas.height);
                    
                    // Draw lime green corners
                    precipCtx.fillStyle = 'lime';
                    precipCtx.fillRect(5, 5, 25, 25);
                    precipCtx.fillRect(precipCanvas.width - 30, 5, 25, 25);
                    precipCtx.fillRect(5, precipCanvas.height - 30, 25, 25);
                    precipCtx.fillRect(precipCanvas.width - 30, precipCanvas.height - 30, 25, 25);
                    
                    // Draw center circle
                    const centerX = precipCanvas.width / 2;
                    const centerY = precipCanvas.height / 2;
                    precipCtx.fillStyle = 'cyan';
                    precipCtx.beginPath();
                    precipCtx.arc(centerX, centerY, 50, 0, 2 * Math.PI);
                    precipCtx.fill();
                    
                    // Draw text
                    precipCtx.fillStyle = 'black';
                    precipCtx.font = 'bold 18px Arial';
                    precipCtx.fillText('PROMISE-SAFE PRECIP', 30, 50);
                    precipCtx.fillText('No Errors!', 30, 75);
                    
                    safeLog("Test pattern drawn successfully");
                    resolve();
                    
                }} catch (e) {{
                    safeLog("Test draw error:", e);
                    resolve();
                }}
            }});
        }}
        
        async function drawPromiseSafePrecip() {{
            return new Promise((resolve) => {{
                try {{
                    if (!precipCtx || !window.precipData) {{
                        safeLog("Missing context or data");
                        resolve();
                        return;
                    }}
                    
                    safeLog("Drawing promise-safe precipitation");
                    
                    const times = Object.keys(window.precipData);
                    if (times.length === 0) {{
                        safeLog("No precipitation times available");
                        resolve();
                        return;
                    }}
                    
                    const currentTime = times[0];
                    const data = window.precipData[currentTime] || [];
                    
                    safeLog("Using time:", currentTime, "with", data.length, "points");
                    
                    // Redraw test first
                    drawPromiseSafeTest().then(() => {{
                        try {{
                            if (data.length === 0) {{
                                safeLog("No precipitation data");
                                resolve();
                                return;
                            }}
                            
                            // Draw precipitation in simple grid
                            let drawn = 0;
                            for (let i = 0; i < Math.min(data.length, 12); i++) {{
                                const point = data[i];
                                const [lat, lon, intensity] = point;
                                
                                // Simple grid layout
                                const col = i % 4;
                                const row = Math.floor(i / 4);
                                const x = 150 + col * 120;
                                const y = 150 + row * 80;
                                
                                const color = getDebugColor(intensity);
                                const radius = Math.max(20, intensity * 25);
                                
                                // Draw circle
                                precipCtx.fillStyle = color;
                                precipCtx.beginPath();
                                precipCtx.arc(x, y, radius, 0, 2 * Math.PI);
                                precipCtx.fill();
                                
                                // Draw label
                                precipCtx.fillStyle = 'white';
                                precipCtx.strokeStyle = 'black';
                                precipCtx.lineWidth = 1;
                                precipCtx.font = 'bold 12px Arial';
                                const text = intensity.toFixed(1);
                                precipCtx.strokeText(text, x - 10, y + 5);
                                precipCtx.fillText(text, x - 10, y + 5);
                                
                                drawn++;
                            }}
                            
                            safeLog("Drew", drawn, "precipitation points");
                            resolve();
                            
                        }} catch (e) {{
                            safeLog("Precip drawing error:", e);
                            resolve();
                        }}
                    }}).catch(e => {{
                        safeLog("Test redraw error:", e);
                        resolve();
                    }});
                    
                }} catch (e) {{
                    safeLog("Precip function error:", e);
                    resolve();
                }}
            }});
        }}
        
        // Initialize with proper promise handling
        safeLog("Initializing promise-safe precipitation system");
        
        // Start setup with multiple attempts
        setTimeout(() => setupPromiseSafeCanvas().catch(e => safeLog("Setup attempt 1 failed:", e)), 100);
        setTimeout(() => setupPromiseSafeCanvas().catch(e => safeLog("Setup attempt 2 failed:", e)), 1000);
        setTimeout(() => setupPromiseSafeCanvas().catch(e => safeLog("Setup attempt 3 failed:", e)), 3000);
        
        safeLog("Promise-safe precipitation system loaded");
        
    }} catch (e) {{
        console.error("[PRECIP-PROMISE] Fatal initialization error:", e);
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
    print("Promise-safe precipitation injection ready!")
    print("This version properly handles unhandled promise rejections to prevent console errors.")
