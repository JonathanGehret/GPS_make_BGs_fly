"""OSM (Plotly layout.map) precipitation heatmap injection.

Clean rewrite focused on reliability with Plotly's open-street-map backend.

Workflow:
1. Python builds hourly precipitation dict: ISO hour -> [[lat, lon, precip_mm], ...]
2. We inject a lightweight JS bundle that:
   - Waits for .plotly-graph-div and fullLayout.map to exist.
   - Creates a single absolutely-positioned <canvas> overlay.
   - On animation frame events (plotly_animated) parses frame name to UTC timestamp.
   - Selects current hour (floor) and (optionally) the next hour for interpolation.
   - Performs Web Mercator transform (lon/lat -> tile coords) relative to current center/zoom.
   - Draws blurred radial gradients whose alpha encodes intensity.
   - Supports toggle via existing updatemenu button containing '☔ Precip'; if absent adds a minimal floating button.
   - Handles relayout (pan/zoom), resize, fullscreen changes.

Design principles:
 - Purely additive: no mutation of existing Plotly traces.
 - No Mapbox class name dependencies.
 - Defensive error handling without swallowing console diagnostics.
 - Idempotent initialization (safe to call multiple times).

Future extension hooks are marked with // TODO comments.
"""

from __future__ import annotations

import json
from typing import Dict, List


def inject_precip_osm_heatmap(html: str, *, data_by_hour: Dict[str, List[List[float]]], zmax: float = 10.0, interval_min: int = 60) -> str:
  """Inject the OSM precipitation heatmap overlay into the produced HTML string."""
  payload = json.dumps({
    "hours": data_by_hour,
    "zmax": zmax,
    "intervalMin": interval_min,
    "version": 1,
  })

  script = """
<style>
canvas#precip-heatmap-layer {
  position:absolute; inset:0; width:100%; height:100%; pointer-events:none; display:none; z-index:7;
}
.precip-toggle-btn {
  position:absolute; top:6px; left:6px; background:rgba(20,20,30,0.65); color:#fff; font:12px/1.2 sans-serif; padding:4px 8px; border-radius:4px; cursor:pointer; z-index:20;
  backdrop-filter: blur(4px); border:1px solid rgba(255,255,255,0.25);
}
.precip-toggle-btn.active { box-shadow:0 0 6px 2px rgba(70,150,255,0.9), 0 0 0 1px rgba(255,255,255,0.4); background:rgba(30,60,120,0.75); }
</style>
<script>
(function() {
  'use strict';
  const PAYLOAD = __PRECIP_OSM_PAYLOAD__;
  const HOURS = Object.keys(PAYLOAD.hours).sort();
  if (!window.__PRECIP_OSM__) window.__PRECIP_OSM__ = {};
  window.__PRECIP_OSM__.data = PAYLOAD;
  window.__PRECIP_OSM__.enabled = true;

  function log(...a) { try { console.log('[PRECIP-OSM]', ...a); } catch(_) {} }
  function warn(...a) { try { console.warn('[PRECIP-OSM]', ...a); } catch(_) {} }

  function ensureGraphDiv() { return document.querySelector('.plotly-graph-div'); }
  function ensureCanvas() {
    const gd = ensureGraphDiv(); if (!gd) return null;
    if (getComputedStyle(gd).position === 'static') gd.style.position='relative';
    let c = document.getElementById('precip-heatmap-layer');
    if (!c) { c = document.createElement('canvas'); c.id='precip-heatmap-layer'; gd.appendChild(c); }
    const r = gd.getBoundingClientRect();
    if (c.width !== Math.floor(r.width) || c.height !== Math.floor(r.height)) { c.width=Math.floor(r.width); c.height=Math.floor(r.height); }
    return c;
  }

  // Web Mercator helpers (tile coordinate space) //
  function lon2x(lon,z) { return (lon + 180) / 360 * Math.pow(2,z); }
  function lat2y(lat,z) { const rad = lat * Math.PI/180; return (1 - Math.asinh(Math.tan(rad))/Math.PI)/2 * Math.pow(2,z); }

  function parseFrameName(name) {
    // Expected format: dd.mm.YYYY HH:MM:SS
    const m = name && name.match(/(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})/);
    if (!m) return null;
    return new Date(Date.UTC(+m[3], +m[2]-1, +m[1], +m[4], +m[5], +m[6]));
  }

  function hourKeyUTC(d) { const dt = new Date(d); dt.setUTCMinutes(0,0,0); return dt.toISOString().slice(0,13)+':00:00+00:00'; }

  // Fallback: match by hour prefix ignoring timezone formatting differences
  function resolveHourKey(dt) {
    const hourPrefix = dt.toISOString().slice(0,13); // YYYY-MM-DDTHH
    for (const h of HOURS) { if (h.startsWith(hourPrefix)) return h; }
    // Try without trailing timezone if present
    for (const h of HOURS) { if (h.replace('Z','').startsWith(hourPrefix)) return h; }
    return HOURS[0];
  }

  function getLayoutMap() {
    const gd = ensureGraphDiv(); if (!gd) return null;
    const fl = gd._fullLayout; if (!fl) return null;
    if (fl.map) return fl.map;
    if (fl.mapbox) return fl.mapbox; // fallback
    return null;
  }

  function currentFrameDate() {
    const gd = ensureGraphDiv(); if (!gd) return new Date();
    try {
      const t = gd._transitionData && gd._transitionData._frame && gd._transitionData._frame.name;
      if (t) { const d = parseFrameName(t); if (d) return d; }
    } catch(_) {}
    return new Date();
  }

  function interpValue(a,b,t) { return a + (b-a)*t; }

  function unifyPoints(hourA, hourB) {
    // Build map of point id -> {lat,lon,a,b}
    const da = PAYLOAD.hours[hourA] || []; const db = PAYLOAD.hours[hourB] || [];
    const map = new Map();
    for (let i=0;i<da.length;i++) { const p=da[i]; map.set(p[0].toFixed(4)+','+p[1].toFixed(4), {lat:p[0], lon:p[1], a:p[2], b:0}); }
    for (let j=0;j<db.length;j++) { const p=db[j]; const k=p[0].toFixed(4)+','+p[1].toFixed(4); const e = map.get(k); if (e) e.b=p[2]; else map.set(k, {lat:p[0], lon:p[1], a:0, b:p[2]}); }
    return [...map.values()];
  }

  function draw() {
    const c = ensureCanvas(); if (!c) return; const ctx=c.getContext('2d'); if (!ctx) return;
    c.style.display = window.__PRECIP_OSM__.enabled ? 'block':'none';
    ctx.clearRect(0,0,c.width,c.height);
    if (!window.__PRECIP_OSM__.enabled) return;
    const map = getLayoutMap(); if (!map) return;
    const center = map.center || {lat:0, lon:0}; const zoom = Math.max(0, Math.min(20, (map.zoom||5)));
    const frameDate = currentFrameDate();
    let baseHour = hourKeyUTC(frameDate);
    if (!PAYLOAD.hours[baseHour]) {
      const fallback = resolveHourKey(frameDate);
      if (fallback !== baseHour) { log('Hour key mismatch. Wanted', baseHour, 'using fallback', fallback); }
      baseHour = fallback;
    }
    // Find next hour key for interpolation
    const idx = HOURS.indexOf(baseHour);
    const nextHour = idx>=0 && idx < HOURS.length-1 ? HOURS[idx+1] : baseHour;
    const deltaMs = 60*60*1000; // hour
    const tFrac = nextHour === baseHour ? 0 : Math.min(1, (frameDate - new Date(baseHour)) / deltaMs);
    const points = unifyPoints(baseHour, nextHour);
    const zmax = PAYLOAD.zmax || 10.0;
    const pxTile=256; const cx=lon2x(center.lon, zoom); const cy=lat2y(center.lat, zoom);
    ctx.save(); ctx.globalCompositeOperation='lighter'; ctx.filter='blur(18px)';
    let drawn = 0;
    // approximate meters per pixel at current latitude/zoom (Web Mercator)
    const metersPerPixel = 156543.03392 * Math.cos(center.lat * Math.PI/180) / Math.pow(2, zoom);
    // target physical radius range (meters)
    const minRadiusM = 2500; // 2.5 km light precip footprint
    const maxRadiusM = 8000; // 8 km heavy precip footprint
    for (let i=0;i<points.length;i++) {
      const p=points[i]; const val=interpValue(p.a, p.b, tFrac);
      if (val<=0) continue;
      const x = (lon2x(p.lon,zoom)-cx)*pxTile + c.width/2;
      const y = (lat2y(p.lat,zoom)-cy)*pxTile + c.height/2;
      const t = Math.max(0, Math.min(1, val/(zmax||1)));
      const radiusMeters = minRadiusM + (maxRadiusM - minRadiusM)*t; // intensity → physical footprint
      const radius = Math.max(6, radiusMeters / metersPerPixel); // convert to pixels
      const g = ctx.createRadialGradient(x,y,0,x,y,radius);
      const alpha = 0.12 + 0.45*t; // moderate transparency
      // color ramp: light cyan → saturated blue
      const innerR = Math.round(30 + 40*t);
      const innerG = Math.round(140 + 40*t);
      const innerB = Math.round(255 - 40*t);
      g.addColorStop(0, 'rgba('+innerR+','+innerG+','+innerB+',' + alpha.toFixed(3) + ')');
      g.addColorStop(0.6, 'rgba('+innerR+','+innerG+','+innerB+',' + (alpha*0.5).toFixed(3) + ')');
      g.addColorStop(1, 'rgba('+innerR+','+innerG+','+innerB+',0)');
      ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,radius,0,Math.PI*2); ctx.fill();
      drawn++;
    }
    if (!drawn) {
      ctx.save(); ctx.fillStyle='rgba(255,255,255,0.85)'; ctx.font='14px sans-serif'; ctx.fillText('No precip points drawn ('+baseHour+')', 12, 22); ctx.restore();
    }
    log('Draw frame', frameDate.toISOString(), 'baseHour', baseHour, 'next', nextHour, 'points', points.length, 'drawn', drawn, 'tFrac', tFrac.toFixed(2));
    ctx.restore();
  }

  function toggleEnabled() { window.__PRECIP_OSM__.enabled = !window.__PRECIP_OSM__.enabled; updateToggleUI(); draw(); }

  function findExistingButton() {
    const btns = document.querySelectorAll('.updatemenu-button');
    for (const b of btns) { if (b.textContent && b.textContent.includes('☔')) return b; }
    return null;
  }

  function createFallbackButton() {
    const gd = ensureGraphDiv(); if (!gd) return null;
    let btn = document.getElementById('precip-fallback-btn');
    if (!btn) {
      btn = document.createElement('div'); btn.id='precip-fallback-btn'; btn.className='precip-toggle-btn';
      btn.textContent='☔ Precip'; gd.appendChild(btn);
      btn.addEventListener('click', (e)=>{ e.stopPropagation(); toggleEnabled(); });
    }
    return btn;
  }

  function updateToggleUI() {
    const btn = findExistingButton() || createFallbackButton(); if (!btn) return;
    if (window.__PRECIP_OSM__.enabled) btn.classList.add('active'); else btn.classList.remove('active');
  }

  function bindEvents() {
    const gd = ensureGraphDiv(); if (!gd) return;
    if (gd.__precipBound) return; gd.__precipBound = true;
    gd.addEventListener('plotly_animated', ()=> draw());
    gd.addEventListener('plotly_relayout', ()=> draw());
    window.addEventListener('resize', ()=> draw());
    document.addEventListener('fullscreenchange', ()=> draw());
  window.addEventListener('keydown', (e)=> { if (e.key==='p' || e.key==='P') { toggleEnabled(); } });
    // Mutation observer to catch late creation of controls
    const mo = new MutationObserver(()=> updateToggleUI());
    mo.observe(gd, {childList:true, subtree:true});
    updateToggleUI();
  }

  function initWhenReady(attempt=0) {
    const gd = ensureGraphDiv(); const map = getLayoutMap();
    if (!gd || !map) {
      if (attempt < 40) return void setTimeout(()=> initWhenReady(attempt+1), 100);
      return warn('Failed to initialize (graph/map not found)');
    }
    ensureCanvas(); bindEvents(); draw(); log('Initialized. Hours:', HOURS.length);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initWhenReady); else initWhenReady();
})();
</script>
"""
  script = script.replace('__PRECIP_OSM_PAYLOAD__', payload)
  return html.replace('</body>', script + '</body>')


__all__ = ["inject_precip_osm_heatmap"]
