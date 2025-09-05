#!/usr/bin/env python3
"""
Create a very simple precipitation test that just adds a visible canvas overlay.
"""

def inject_diagnostic_precip_overlay(html: str, *, data_by_hour, interval_min: int = 60, zmax: float = 10.0) -> str:
    """
    Ultra-simple precipitation test - just add a visible canvas with test pattern.
    """
    
    injection = """
<!-- SIMPLE PRECIPITATION TEST -->
<script>
console.log("=== SIMPLE PRECIP TEST STARTING ===");

function setupSimpleTest() {
    console.log("Setting up simple precipitation test...");
    
    // Wait for Plotly to be ready
    if (typeof Plotly === 'undefined') {
        console.log("Plotly not ready, retrying...");
        setTimeout(setupSimpleTest, 1000);
        return;
    }
    
    // Find the plotly container
    const plotlyDiv = document.querySelector('.js-plotly-plot');
    if (!plotlyDiv) {
        console.log("No plotly div found, retrying...");
        setTimeout(setupSimpleTest, 1000);
        return;
    }
    
    console.log("Found plotly div:", plotlyDiv);
    
    // Create a simple overlay div instead of canvas
    const overlay = document.createElement('div');
    overlay.id = 'simple-precip-test';
    overlay.style.position = 'absolute';
    overlay.style.top = '50px';
    overlay.style.left = '50px';
    overlay.style.width = '200px';
    overlay.style.height = '100px';
    overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.8)';
    overlay.style.color = 'white';
    overlay.style.padding = '10px';
    overlay.style.border = '3px solid lime';
    overlay.style.zIndex = '9999';
    overlay.style.fontSize = '14px';
    overlay.style.fontWeight = 'bold';
    overlay.innerHTML = 'PRECIPITATION TEST<br>Canvas Overlay Working!<br>Z-Index: 9999';
    
    // Add to plotly div
    plotlyDiv.appendChild(overlay);
    
    console.log("Simple test overlay added successfully!");
    
    // Also try to add to map container if it exists
    setTimeout(() => {
        const mapContainer = plotlyDiv.querySelector('.mapboxgl-map, .mapboxgl-canvas-container, .mapboxgl-canvas');
        if (mapContainer) {
            console.log("Found map container:", mapContainer);
            
            const mapOverlay = overlay.cloneNode(true);
            mapOverlay.id = 'simple-precip-test-map';
            mapOverlay.style.top = '100px';
            mapOverlay.innerHTML = 'MAP OVERLAY TEST<br>Direct to Map!<br>Working!';
            mapContainer.appendChild(mapOverlay);
            
            console.log("Map overlay added too!");
        } else {
            console.log("No map container found");
        }
    }, 2000);
}

// Start immediately and retry if needed
setupSimpleTest();

console.log("=== SIMPLE PRECIP TEST SCRIPT LOADED ===");
</script>
"""
    
    # Inject before closing body tag
    if '</body>' in html:
        return html.replace('</body>', injection + '</body>')
    else:
        return html + injection

if __name__ == "__main__":
    print("Simple precipitation test injection ready!")
    print("This will add a bright red test overlay to verify canvas positioning works.")
