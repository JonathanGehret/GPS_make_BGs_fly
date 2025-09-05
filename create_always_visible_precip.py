#!/usr/bin/env python3
"""
Create a precipitation injection that's always visible for debugging.
This version will render precipitation regardless of button state and use bright colors.
"""

def create_always_visible_precip_injection():
    return """
<!-- ALWAYS VISIBLE PRECIPITATION DEBUG OVERLAY -->
<script>
(function() {
    console.log("[PRECIP-ALWAYS] Always visible precipitation debugging enabled");
    
    let precipCanvas = null;
    let precipCtx = null;
    let mapContainer = null;
    
    // Bright, visible colors for debugging
    function debugColorFor(intensity) {
        if (intensity <= 0) return 'rgba(255, 0, 255, 0.8)'; // Bright magenta for zero
        if (intensity <= 0.1) return 'rgba(255, 255, 0, 0.8)'; // Bright yellow
        if (intensity <= 0.5) return 'rgba(255, 165, 0, 0.8)'; // Orange
        if (intensity <= 1.0) return 'rgba(255, 0, 0, 0.8)';   // Red
        return 'rgba(128, 0, 128, 0.8)'; // Purple for heavy rain
    }
    
    function setupAlwaysVisibleCanvas() {
        const plotlyDiv = document.querySelector('.js-plotly-plot');
        if (!plotlyDiv) {
            console.log("[PRECIP-ALWAYS] No plotly div found, retrying...");
            setTimeout(setupAlwaysVisibleCanvas, 500);
            return;
        }
        
        mapContainer = plotlyDiv.querySelector('.mapboxgl-map');
        if (!mapContainer) {
            console.log("[PRECIP-ALWAYS] No mapbox container found, retrying...");
            setTimeout(setupAlwaysVisibleCanvas, 500);
            return;
        }
        
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
        if (window.precipData) {
            console.log("[PRECIP-ALWAYS] Drawing precipitation data");
            drawAlwaysVisiblePrecip();
        } else {
            console.log("[PRECIP-ALWAYS] No precipitation data available yet");
        }
        
        // Update on resize
        window.addEventListener('resize', () => {
            precipCanvas.width = mapContainer.clientWidth;
            precipCanvas.height = mapContainer.clientHeight;
            drawTestPattern();
            if (window.precipData) drawAlwaysVisiblePrecip();
        });
    }
    
    function drawTestPattern() {
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
        precipCtx.fillText('PRECIP DEBUG CANVAS', 30, 50);
    }
    
    function drawAlwaysVisiblePrecip() {
        if (!precipCtx || !window.precipData) return;
        
        console.log("[PRECIP-ALWAYS] Drawing precipitation overlay");
        
        // Get current time from Plotly
        let currentTime = null;
        try {
            const plotlyDiv = document.querySelector('.js-plotly-plot');
            if (plotlyDiv && plotlyDiv._fullLayout && plotlyDiv._fullLayout.sliders) {
                const slider = plotlyDiv._fullLayout.sliders[0];
                if (slider && slider.active !== undefined) {
                    const step = slider.steps[slider.active];
                    currentTime = step.label;
                }
            }
        } catch (e) {
            console.log("[PRECIP-ALWAYS] Could not get current time:", e);
        }
        
        // If no current time, use first available
        if (!currentTime) {
            const keys = Object.keys(window.precipData);
            currentTime = keys.length > 0 ? keys[0] : null;
        }
        
        if (!currentTime) {
            console.log("[PRECIP-ALWAYS] No time available for precipitation");
            return;
        }
        
        console.log("[PRECIP-ALWAYS] Drawing for time:", currentTime);
        
        const data = window.precipData[currentTime] || [];
        console.log("[PRECIP-ALWAYS] Data points:", data.length);
        
        if (data.length === 0) {
            console.log("[PRECIP-ALWAYS] No precipitation data for time:", currentTime);
            return;
        }
        
        // Clear previous precipitation (but keep test pattern)
        precipCtx.save();
        precipCtx.globalCompositeOperation = 'source-over';
        
        // Get map bounds
        const plotlyDiv = document.querySelector('.js-plotly-plot');
        const layout = plotlyDiv._fullLayout;
        const mapbox = layout.mapbox;
        
        if (!mapbox) {
            console.log("[PRECIP-ALWAYS] No mapbox layout found");
            return;
        }
        
        // Draw each precipitation point
        data.forEach((point, index) => {
            const [lat, lon, intensity] = point;
            
            // Convert lat/lon to screen coordinates (simplified)
            // This is a rough approximation - in real implementation you'd use proper projection
            const centerLat = mapbox.center ? mapbox.center.lat : 51.5074;
            const centerLon = mapbox.center ? mapbox.center.lon : -0.1278;
            const zoom = mapbox.zoom || 10;
            
            const scale = Math.pow(2, zoom) * 256;
            const x = precipCanvas.width / 2 + (lon - centerLon) * scale * Math.cos(centerLat * Math.PI / 180);
            const y = precipCanvas.height / 2 - (lat - centerLat) * scale;
            
            // Make sure the point is visible on screen
            if (x >= 0 && x <= precipCanvas.width && y >= 0 && y <= precipCanvas.height) {
                const color = debugColorFor(intensity);
                const radius = Math.max(20, intensity * 30); // Large, visible radius
                
                // Draw with glow effect
                const gradient = precipCtx.createRadialGradient(x, y, 0, x, y, radius);
                gradient.addColorStop(0, color);
                gradient.addColorStop(1, 'rgba(0,0,0,0)');
                
                precipCtx.fillStyle = gradient;
                precipCtx.beginPath();
                precipCtx.arc(x, y, radius, 0, 2 * Math.PI);
                precipCtx.fill();
                
                // Add text label
                precipCtx.fillStyle = 'white';
                precipCtx.font = '12px Arial';
                precipCtx.fillText(intensity.toFixed(2), x + radius + 5, y);
                
                if (index < 5) {
                    console.log(`[PRECIP-ALWAYS] Point ${index}: lat=${lat}, lon=${lon}, intensity=${intensity}, screen=(${x.toFixed(0)}, ${y.toFixed(0)}), radius=${radius}`);
                }
            }
        });
        
        precipCtx.restore();
        
        console.log("[PRECIP-ALWAYS] Finished drawing precipitation");
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupAlwaysVisibleCanvas);
    } else {
        setupAlwaysVisibleCanvas();
    }
    
    // Also update when precipitation data changes
    window.updateAlwaysVisiblePrecip = drawAlwaysVisiblePrecip;
    
    console.log("[PRECIP-ALWAYS] Always visible precipitation debug system initialized");
})();
</script>
"""

if __name__ == "__main__":
    print("Always visible precipitation injection created!")
    print("\nThis injection will:")
    print("- Always render precipitation regardless of button state")
    print("- Use bright, highly visible colors")
    print("- Draw corner markers and center circle for canvas verification")
    print("- Show precipitation intensity values as text labels")
    print("- Use high z-index to ensure visibility")
    print("- Log detailed information to console")
