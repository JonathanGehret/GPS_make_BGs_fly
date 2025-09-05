#!/usr/bin/env python3
"""
Create a diagnostic version of precipitation injection to debug issues
"""

import json


def create_diagnostic_precip_injection():
    """Create a more robust precipitation injection with extensive debugging"""
    
    template = '''
<style>
#precip-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; display: none; z-index: 5;
  border: 3px solid lime; /* VERY visible debug border */
}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
  console.log('[PRECIP-DEBUG] Starting precipitation overlay initialization');
  
  window.__PRECIP = __PRECIP_JSON__;
  window._precipEnabled = true;
  
  console.log('[PRECIP-DEBUG] Injected data:', window.__PRECIP);
  console.log('[PRECIP-DEBUG] Available hours:', Object.keys((window.__PRECIP && window.__PRECIP.hours) || {}));

  function ensureCanvas() {
    console.log('[PRECIP-DEBUG] ensureCanvas called');
    const gd = document.querySelector('.plotly-graph-div');
    if (!gd) {
      console.error('[PRECIP-DEBUG] No .plotly-graph-div found!');
      return null;
    }
    console.log('[PRECIP-DEBUG] Found plotly-graph-div:', gd);
    
    if (getComputedStyle(gd).position === 'static') {
      gd.style.position = 'relative';
      console.log('[PRECIP-DEBUG] Set plotly-graph-div to relative positioning');
    }
    
    let c = document.getElementById('precip-overlay');
    if (!c) { 
      c = document.createElement('canvas'); 
      c.id = 'precip-overlay'; 
      gd.appendChild(c); 
      console.log('[PRECIP-DEBUG] Created new canvas element');
    }
    
    const r = gd.getBoundingClientRect();
    c.width = Math.floor(r.width); 
    c.height = Math.floor(r.height);
    console.log('[PRECIP-DEBUG] Canvas sized to:', c.width, 'x', c.height);
    
    // Make canvas VERY visible for debugging
    c.style.display = 'block';
    c.style.border = '3px solid lime';
    c.style.backgroundColor = 'rgba(255, 0, 0, 0.1)'; // Slight red tint
    
    return c;
  }

  function lon2x(lon, z) { return (lon + 180) / 360 * Math.pow(2, z); }
  function lat2y(lat, z) { const rad = lat * Math.PI/180; return (1 - Math.asinh(Math.tan(rad)) / Math.PI) / 2 * Math.pow(2, z); }

  function quantizeToInterval(date, minutes) {
    const d = new Date(date);
    const ms = minutes * 60 * 1000;
    return new Date(Math.floor(d.getTime() / ms) * ms);
  }

  function toHourKeyUTC(date) {
    const d = new Date(date);
    d.setUTCMinutes(0,0,0);
    return d.toISOString().slice(0,13) + ':00:00+00:00';
  }

  function drawHeatmapForTime(dt) {
    console.log('[PRECIP-DEBUG] drawHeatmapForTime called with:', dt);
    
    const c = ensureCanvas(); 
    if (!c) {
      console.error('[PRECIP-DEBUG] Could not create canvas');
      return;
    }
    
    const ctx = c.getContext('2d'); 
    if (!ctx) {
      console.error('[PRECIP-DEBUG] Could not get canvas context');
      return;
    }

    const gd = document.querySelector('.plotly-graph-div');
    const fl = gd && gd._fullLayout;
    const map = fl && (fl.map || fl.mapbox);
    
    if (!map) {
      console.error('[PRECIP-DEBUG] No map layout found. gd:', !!gd, 'fl:', !!fl, 'map:', !!map);
      return;
    }

    let center = map.center || {lon:0, lat:0};
    if (center && center.lat === undefined && Array.isArray(center)) { 
      center = {lat: center[1], lon: center[0]}; 
    }
    const zoom = Math.max(0, Math.min(10, Math.round((typeof map.zoom === 'number' ? map.zoom : (parseFloat(map.zoom) || 6)) )));

    console.log('[PRECIP-DEBUG] Map state - center:', center, 'zoom:', zoom);

    const intervalMin = (window.__PRECIP && window.__PRECIP.intervalMin) || 60;
    const zmax = (window.__PRECIP && window.__PRECIP.zmax) || 10.0;
    const q = quantizeToInterval(dt, intervalMin);
    const hourKey = toHourKeyUTC(q);
    const frame = window.__PRECIP && window.__PRECIP.hours && window.__PRECIP.hours[hourKey];

    console.log('[PRECIP-DEBUG] Looking for hour key:', hourKey);
    console.log('[PRECIP-DEBUG] Available keys:', Object.keys((window.__PRECIP && window.__PRECIP.hours) || {}));
    console.log('[PRECIP-DEBUG] Frame data:', frame);

    ctx.clearRect(0,0,c.width,c.height);
    
    if (!window._precipEnabled) {
      console.log('[PRECIP-DEBUG] Precipitation disabled');
      return;
    }
    
    if (!frame || !frame.length) { 
      console.warn('[PRECIP-DEBUG] No data for hour', hourKey);
      // Draw a test pattern to verify canvas is working
      ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
      ctx.fillRect(10, 10, 100, 100);
      ctx.fillStyle = 'white';
      ctx.font = '16px Arial';
      ctx.fillText('NO PRECIP DATA', 20, 50);
      ctx.fillText(hourKey, 20, 70);
      return;
    }

    console.log('[PRECIP-DEBUG] Drawing', frame.length, 'precipitation points');

    const xC = lon2x(center.lon, zoom); 
    const yC = lat2y(center.lat, zoom);
    const pxTile = 256;

    // Draw test background first
    ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
    ctx.fillRect(0, 0, c.width, c.height);

    // Draw precipitation heatmap
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.filter = 'blur(24px)';
    
    for (let i = 0; i < frame.length; i++) {
      const lat = frame[i][0], lon = frame[i][1], val = frame[i][2];
      const x = lon2x(lon, zoom), y = lat2y(lat, zoom);
      const px = (x - xC) * pxTile + c.width/2;
      const py = (y - yC) * pxTile + c.height/2;
      const t = Math.max(0, Math.min(1, val / (zmax || 1)));
      const rad = 40 + 80 * t;
      
      console.log('[PRECIP-DEBUG] Point', i, '- lat:', lat, 'lon:', lon, 'val:', val, 'px:', Math.round(px), 'py:', Math.round(py), 'rad:', Math.round(rad));
      
      const grad = ctx.createRadialGradient(px, py, 0, px, py, rad);
      const a = 0.5 + 0.5 * t; // High opacity for visibility
      grad.addColorStop(0.0, `rgba(0, 150, 255, ${a})`);
      grad.addColorStop(0.7, `rgba(0, 100, 200, ${a * 0.3})`);
      grad.addColorStop(1.0, 'rgba(0, 100, 200, 0)');
      
      ctx.fillStyle = grad;
      ctx.beginPath(); 
      ctx.arc(px, py, rad, 0, Math.PI*2); 
      ctx.fill();
    }
    ctx.restore();

    console.log('[PRECIP-DEBUG] Heatmap drawing complete');
  }

  function bindPrecipToggle() {
    console.log('[PRECIP-DEBUG] Binding precipitation toggle');
    const btns = document.querySelectorAll('.updatemenu-button');
    console.log('[PRECIP-DEBUG] Found', btns.length, 'updatemenu buttons');
    
    let foundButton = false;
    btns.forEach((b, i) => {
      console.log('[PRECIP-DEBUG] Button', i, 'text:', b.textContent);
      if (b.textContent && (b.textContent.includes('☔ Precip') || b.textContent.includes('Precip'))) {
        foundButton = true;
        console.log('[PRECIP-DEBUG] Binding to precipitation button:', b.textContent);
        
        const oldHandler = b.onclick;
        b.onclick = (e) => {
          console.log('[PRECIP-DEBUG] Precipitation button clicked!');
          e.preventDefault(); 
          e.stopPropagation();
          
          if (oldHandler) oldHandler.call(b, e);
          
          window._precipEnabled = !window._precipEnabled;
          console.log('[PRECIP-DEBUG] Precipitation toggled to:', window._precipEnabled);
          
          const c = ensureCanvas(); 
          if (c) {
            c.style.display = window._precipEnabled ? 'block' : 'none';
            console.log('[PRECIP-DEBUG] Canvas display set to:', c.style.display);
          }
          
          // Use current time for testing
          const testTime = new Date('2023-11-02T06:30:00Z');
          console.log('[PRECIP-DEBUG] Drawing for test time:', testTime);
          drawHeatmapForTime(testTime);
        };
      }
    });
    
    if (!foundButton) {
      console.warn('[PRECIP-DEBUG] No precipitation button found! Available buttons:', 
        Array.from(btns).map(b => b.textContent));
    }
  }

  // Initial setup
  console.log('[PRECIP-DEBUG] Setting up precipitation overlay');
  bindPrecipToggle();
  
  // Create canvas immediately for testing
  const testCanvas = ensureCanvas();
  if (testCanvas) {
    console.log('[PRECIP-DEBUG] Test canvas created successfully');
    
    // Draw immediately with test time
    setTimeout(() => {
      console.log('[PRECIP-DEBUG] Drawing initial test precipitation');
      drawHeatmapForTime(new Date('2023-11-02T06:30:00Z'));
    }, 1000);
  }

  // Enhanced observer
  const ob = new MutationObserver(() => { 
    console.log('[PRECIP-DEBUG] DOM mutation detected, rebinding');
    bindPrecipToggle();
  });
  ob.observe(document.body, {childList:true, subtree:true});
  
  // Additional retry
  setTimeout(() => {
    console.log('[PRECIP-DEBUG] Delayed rebind attempt');
    bindPrecipToggle();
  }, 2000);
  
  console.log('[PRECIP-DEBUG] Precipitation overlay initialization complete');
});
</script>
'''
    
    return template


def inject_diagnostic_precip_overlay(html: str, *, data_by_hour: dict, interval_min: int = 60, zmax: float = 10.0) -> str:
    """Inject diagnostic precipitation overlay"""
    payload = json.dumps({
        "intervalMin": interval_min,
        "zmax": zmax,
        "hours": data_by_hour,
    })
    
    template = create_diagnostic_precip_injection()
    assets = template.replace('__PRECIP_JSON__', payload)
    return html.replace('</body>', assets + '</body>')


if __name__ == "__main__":
    print("✅ Created diagnostic precipitation injection")
    print("📋 This version includes:")
    print("   • Extensive console logging")
    print("   • Visible canvas borders")
    print("   • Test pattern when no data")
    print("   • Button detection diagnostics")
    print("   • Immediate test drawing")
    
    # Save the diagnostic function to a file for import
    with open('diagnostic_precip_injection.py', 'w') as f:
        f.write('import json\n\n')
        f.write(f'def inject_diagnostic_precip_overlay(html: str, *, data_by_hour: dict, interval_min: int = 60, zmax: float = 10.0) -> str:\n')
        f.write(f'    """Inject diagnostic precipitation overlay"""\n')
        f.write(f'    payload = json.dumps({{"intervalMin": interval_min, "zmax": zmax, "hours": data_by_hour}})\n')
        f.write(f'    template = """{create_diagnostic_precip_injection()}"""\n')
        f.write(f'    assets = template.replace("__PRECIP_JSON__", payload)\n')
        f.write(f'    return html.replace("</body>", assets + "</body>")\n')
    
    print("💾 Saved diagnostic_precip_injection.py for import")
