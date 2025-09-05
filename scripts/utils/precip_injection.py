from __future__ import annotations

import json
from typing import Dict, List


def inject_precip_overlay(html: str, *, data_by_hour: Dict[str, List[List[float]]], interval_min: int = 60, zmax: float = 10.0) -> str:
    """
    Injects a precipitation heatmap overlay (canvas) into the HTML.

    data_by_hour: mapping ISO hour string -> list of [lat, lon, precip_mm]
    interval_min: quantization of frames (10/15/30/60)
    zmax: max scale for intensity
    """
    payload = json.dumps({
        "intervalMin": interval_min,
        "zmax": zmax,
        "hours": data_by_hour,
    })

    TEMPLATE = """
<style>
#precip-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; display: none; z-index: 5;
}
/* Control glow is centralized in html_injection; no duplicated styles here */
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
  window.__PRECIP = __PRECIP_JSON__;
  // Enable by default when injected
  window._precipEnabled = true;

  function ensureCanvas() {
    const gd = document.querySelector('.plotly-graph-div');
    if (!gd) return null;
    if (getComputedStyle(gd).position === 'static') gd.style.position = 'relative';
    let c = document.getElementById('precip-overlay');
    if (!c) { c = document.createElement('canvas'); c.id = 'precip-overlay'; gd.appendChild(c); }
    const r = gd.getBoundingClientRect();
    c.width = Math.floor(r.width); c.height = Math.floor(r.height);
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

  function colorFor(v, vmax) {
    // Simple blue scale; return rgba with alpha by intensity
    const t = Math.max(0, Math.min(1, v / (vmax || 1)));
    const a = 0.25 + 0.65 * t; // stronger opacity at higher precip
    return 'rgba(30, 100, 200, ' + a.toFixed(3) + ')';
  }

  async function drawHeatmapForTime(dt) {
    const c = ensureCanvas(); if (!c) return;
    const ctx = c.getContext('2d'); if (!ctx) return;
    const gd = document.querySelector('.plotly-graph-div');
    const map = gd && gd._fullLayout && gd._fullLayout.map; if (!map) return;
    const center = map.center || {lon:0, lat:0}; const zoom = Math.max(0, Math.min(10, Math.round(map.zoom || 6)));

    const intervalMin = (window.__PRECIP && window.__PRECIP.intervalMin) || 60;
    const zmax = (window.__PRECIP && window.__PRECIP.zmax) || 10.0;
    const q = quantizeToInterval(dt, intervalMin);
    const hourKey = toHourKeyUTC(q);
    const frame = window.__PRECIP && window.__PRECIP.hours && window.__PRECIP.hours[hourKey];

    ctx.clearRect(0,0,c.width,c.height);
    if (!window._precipEnabled || !frame || !frame.length) return;

    const xC = lon2x(center.lon, zoom); const yC = lat2y(center.lat, zoom);
    const pxTile = 256; // pixel per tile (approx)

    // Draw blurry blue spots per point
    ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.filter = 'blur(16px)';
    for (let i=0;i<frame.length;i++) {
      const lat = frame[i][0], lon = frame[i][1], val = frame[i][2];
      const x = lon2x(lon, zoom), y = lat2y(lat, zoom);
      const px = (x - xC) * pxTile + c.width/2;
      const py = (y - yC) * pxTile + c.height/2;
  const t = Math.max(0, Math.min(1, val / (zmax || 1)));
  const rad = 30 + 60 * t;
      const grad = ctx.createRadialGradient(px, py, 0, px, py, rad);
      const col = colorFor(val, zmax);
      grad.addColorStop(0.0, col);
      grad.addColorStop(1.0, 'rgba(30, 100, 200, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath(); ctx.arc(px, py, rad, 0, Math.PI*2); ctx.fill();
    }
    ctx.restore();
  }

  function updatePrecipButtonState() {
    // Prefer centralized control API when available
    try {
      if (window.__CONTROL && window.__CONTROL.setControlActive) {
        window.__CONTROL.setControlActive('☔ Precip', !!window._precipEnabled);
        return;
      }
    } catch(_){}
    // Fallback: toggle classes on matching updatemenu button
    const btns = document.querySelectorAll('.updatemenu-button');
    btns.forEach(b => {
      if (b.textContent && b.textContent.includes('☔ Precip')) {
        if (window._precipEnabled) {
          b.classList.add('precip-active');
          b.classList.add('control-active');
        } else {
          b.classList.remove('precip-active');
          b.classList.remove('control-active');
        }
      }
    });
  }
  // local fallback helper for control-active toggles if no centralized API
  function localSetControlActive(label, on) {
    const btns = document.querySelectorAll('.updatemenu-button');
    btns.forEach(b => {
      if (b.textContent && b.textContent.includes(label)) {
        if (on) b.classList.add('control-active'); else b.classList.remove('control-active');
      }
    });
  }

  function bindPrecipToggle() {
    const btns = document.querySelectorAll('.updatemenu-button');
    btns.forEach(b => {
      if (b.textContent && b.textContent.includes('☔ Precip')) {
        b.onclick = (e) => {
          e.preventDefault(); e.stopPropagation();
          window._precipEnabled = !window._precipEnabled;
          const c = ensureCanvas(); if (c) c.style.display = window._precipEnabled ? 'block' : 'none';
          updatePrecipButtonState();
          const gd = document.querySelector('.plotly-graph-div');
          let dt = new Date();
          try {
            const t = gd._transitionData && gd._transitionData._frame && gd._transitionData._frame.name;
            if (t) {
              const m = t.match(/(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})/);
              if (m) dt = new Date(m[3] + '-' + m[2] + '-' + m[1] + 'T' + m[4] + ':' + m[5] + ':' + m[6] + 'Z');
            }
          } catch(_){}
          drawHeatmapForTime(dt);
        };
      }
    });
  }

  function bindFrameAndRelayout() {
    const gd = document.querySelector('.plotly-graph-div'); if (!gd) return;
    gd.addEventListener('plotly_animated', function() {
      // Animation frame event — treat as "playing"
      try { if (window.__CONTROL && window.__CONTROL.setControlActive) { window.__CONTROL.setControlActive('▶️ Play', true); window.__CONTROL.setControlActive('⏸️ Pause', false); } else { localSetControlActive('▶️ Play', true); localSetControlActive('⏸️ Pause', false); } } catch(_){}
      if (!window._precipEnabled) return;
      try {
        const t = gd._transitionData && gd._transitionData._frame && gd._transitionData._frame.name;
        if (t) {
          const m = t.match(/(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})/);
          if (m) drawHeatmapForTime(m[3] + '-' + m[2] + '-' + m[1] + 'T' + m[4] + ':' + m[5] + ':' + m[6] + 'Z');
        }
      } catch(_){}
    });
    gd.addEventListener('plotly_relayout', function(evt) {
      // Layout change — consider this a manual interaction (paused)
      try { if (window.__CONTROL && window.__CONTROL.setControlActive) { window.__CONTROL.setControlActive('⏸️ Pause', true); window.__CONTROL.setControlActive('▶️ Play', false); } else { localSetControlActive('⏸️ Pause', true); localSetControlActive('▶️ Play', false); } } catch(_){}
      if (window._precipEnabled) drawHeatmapForTime(new Date());
      // Check recenter condition when center/zoom changes
      try { if (window.__CONTROL && window.__CONTROL.checkRecenterState) window.__CONTROL.checkRecenterState(); else {/* no-op */} } catch(_){}}
    });
    window.addEventListener('resize', function() { if (window._precipEnabled) drawHeatmapForTime(new Date()); checkRecenterState(); });

    // Fullscreen change -> update fullscreen button state
    document.addEventListener('fullscreenchange', function() {
      const isFs = !!document.fullscreenElement;
      try { if (window.__CONTROL && window.__CONTROL.setControlActive) window.__CONTROL.setControlActive('⛶ Fullscreen', isFs); else localSetControlActive('⛶ Fullscreen', isFs); } catch(_){}
    });
  }

  // Initial bind and observer for dynamic UI
  bindPrecipToggle();
  bindFrameAndRelayout();
  // Prefer the centralized control binder when available (injected by html_injection).
  try {
    if (window.__CONTROL && window.__CONTROL.bindControlInterceptors) {
      window.__CONTROL.bindControlInterceptors();
    } else if (typeof bindControlInterceptors === 'function') {
      // defensive: call local binder only if present
      bindControlInterceptors();
    }
  } catch (_){ }
  // Show initial frame (use current quantized time if available, else first hour)
  try {
    const c = ensureCanvas(); if (c) c.style.display = 'block';
    const intervalMin = (window.__PRECIP && window.__PRECIP.intervalMin) || 60;
    const nowQ = quantizeToInterval(new Date(), intervalMin);
    drawHeatmapForTime(nowQ);
    updatePrecipButtonState();
    // Also update other control visual states
    // Update control visuals using centralized API when available, else fallback to local toggles
    try {
      if (window.__CONTROL && window.__CONTROL.setControlActive) {
        window.__CONTROL.setControlActive('⏸️ Pause', false);
        window.__CONTROL.setControlActive('▶️ Play', false);
        window.__CONTROL.setControlActive('⛶ Fullscreen', !!document.fullscreenElement);
        if (window.__CONTROL.checkRecenterState) window.__CONTROL.checkRecenterState();
      } else {
        localSetControlActive('⏸️ Pause', false);
        localSetControlActive('▶️ Play', false);
        localSetControlActive('⛶ Fullscreen', !!document.fullscreenElement);
        // no centralized recenter checker available here
      }
    } catch (_){ }
    if (!window._precipEnabled) {
      const keys = Object.keys((window.__PRECIP && window.__PRECIP.hours) || {});
      if (keys && keys.length) { drawHeatmapForTime(new Date(keys[0])); }
    }
  } catch(_){}
  const ob = new MutationObserver(() => { bindPrecipToggle(); updatePrecipButtonState(); });
  ob.observe(document.body, {childList:true, subtree:true});
});
</script>
"""
    assets = TEMPLATE.replace('__PRECIP_JSON__', payload)
    return html.replace('</body>', assets + '</body>')
