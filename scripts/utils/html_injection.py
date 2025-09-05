"""
HTML post-processing utilities for Plotly exports.

Currently includes:
- inject_fullscreen: Adds CSS/JS to enable a custom fullscreen button that
  toggles the entire page into fullscreen while properly resizing Plotly.
"""

from __future__ import annotations


def inject_fullscreen(html_string: str) -> str:
    """
    Injects CSS and JavaScript before </body> to support a custom
    "⛶ Fullscreen" updatemenus button in Plotly figures.

    The script:
    - Styles windowed mode to be centered with padding.
    - Applies a fullscreen-mode class in fullscreen for near-full viewport fit.
    - Binds the updatemenus button labeled "⛶ Fullscreen" to the Fullscreen API.
    - Resizes the Plotly graph on enter/exit and window resize.
    - Uses a MutationObserver to rebind handlers after Plotly DOM updates.

    Args:
        html_string: HTML document produced by fig.to_html(...)

    Returns:
        Modified HTML string with fullscreen support.
    """
    fullscreen_assets = """
<style>
/* Improve centering for windowed mode */
body {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
    box-sizing: border-box;
}

/* Plot container visuals */
.plotly-graph-div {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-radius: 8px;
    background: white;
    max-width: 100%;
}

/* Fullscreen mode styles */
body.fullscreen-mode {
    padding: 0;
    background-color: white;
    align-items: center;
    justify-content: center;
}

body.fullscreen-mode .plotly-graph-div {
    box-shadow: none;
    border-radius: 0;
    width: 98vw !important;
    height: 95vh !important;
}
/* Radar overlay canvas sits above the map background but below Plotly traces */
#radar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none; /* passthrough */
    display: none; /* hidden by default */
}
</style>
<script>
// Enhanced fullscreen functionality with better centering
document.addEventListener('DOMContentLoaded', function() {
    // Create a radar canvas overlay inside the Plotly container once ready
    function ensureRadarCanvas() {
        const gd = document.querySelector('.plotly-graph-div');
        if (!gd) return null;
        // Position host relatively
        if (getComputedStyle(gd).position === 'static') {
            gd.style.position = 'relative';
        }
        let canvas = document.getElementById('radar-overlay');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'radar-overlay';
            canvas.style.zIndex = '0';
            gd.appendChild(canvas);
        }
        // Match canvas size to graph div
        const rect = gd.getBoundingClientRect();
        canvas.width = Math.floor(rect.width);
        canvas.height = Math.floor(rect.height);
        return canvas;
    }

    // Simple RainViewer v2 tile loader
    // Docs: https://www.rainviewer.com/api.html (public free tiles)
    // Note: For production, consider API terms and caching
    async function drawRadarForTimestamp(dt) {
        const canvas = ensureRadarCanvas();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        const gd = document.querySelector('.plotly-graph-div');
        if (!gd || !gd._fullLayout) return;
        const map = gd._fullLayout.map;
        if (!map) return;
        const zoom = Math.max(0, Math.min(10, Math.round(map.zoom || 6))); // limit zoom range for radar

        // Convert plotly map extents to lon/lat bbox
        const center = map.center || {lon: 0, lat: 0};
        const W = canvas.width, H = canvas.height;
        // Approximate visible span using zoom (rough heuristic for WebMercator)
        const spanLon = 360 / Math.pow(2, zoom + 1);
        const spanLat = 170 / Math.pow(2, zoom + 1);
        const bbox = {
            west: center.lon - spanLon,
            east: center.lon + spanLon,
            south: center.lat - spanLat,
            north: center.lat + spanLat,
        };

        // Determine RainViewer radar time frame (rounded to 10 min)
        const t = new Date(dt);
        if (isNaN(t.getTime())) return;
        t.setUTCMinutes(Math.floor(t.getUTCMinutes() / 10) * 10, 0, 0);
        const ts = Math.floor(t.getTime() / 1000);

        // Fetch available radar frames list once and cache
        if (!window._rvCache) window._rvCache = {};
        if (!window._rvCache.frames) {
            try {
                const meta = await fetch('https://api.rainviewer.com/public/weather-maps.json').then(r => r.json());
                window._rvCache.frames = (meta && meta.radar && meta.radar.past ? meta.radar.past : []).concat(meta && meta.radar && meta.radar.now ? [meta.radar.now] : []);
            } catch (e) {
                return;
            }
        }
        const frames = window._rvCache.frames || [];
        // Find closest frame <= ts
        let frame = null;
        for (let i = frames.length - 1; i >= 0; i--) {
            if (frames[i].time <= ts) { frame = frames[i]; break; }
        }
        if (!frame) frame = frames[0] || null;
        if (!frame) return;

        // Clear canvas
        ctx.clearRect(0, 0, W, H);
        if (!window._radarEnabled) return;

        // Compose tile URLs for current zoom; draw basic grid covering canvas
        const tileSize = 256;
        const scale = window.devicePixelRatio || 1;
        const baseUrl = `https://tilecache.rainviewer.com/v2/radar/${frame.path}/${zoom}/{x}/{y}/2/1_1.png`;

        // Project lon/lat to WebMercator tile coordinates
        function lon2x(lon, z) { return (lon + 180) / 360 * Math.pow(2, z); }
        function lat2y(lat, z) {
            const rad = lat * Math.PI / 180;
            return (1 - Math.asinh(Math.tan(rad)) / Math.PI) / 2 * Math.pow(2, z);
        }
        const xCenter = lon2x(center.lon, zoom);
        const yCenter = lat2y(center.lat, zoom);

        // Determine how many tiles to cover canvas
        const pxPerTile = tileSize; // assume 1:1
        const tilesAcross = Math.ceil(W / pxPerTile) + 2;
        const tilesDown = Math.ceil(H / pxPerTile) + 2;
        const startX = Math.floor(xCenter - tilesAcross / 2);
        const startY = Math.floor(yCenter - tilesDown / 2);

        canvas.style.display = window._radarEnabled ? 'block' : 'none';
        ctx.globalAlpha = 0.6;
        const promises = [];
        for (let dx = 0; dx < tilesAcross; dx++) {
            for (let dy = 0; dy < tilesDown; dy++) {
                const tx = startX + dx;
                const ty = startY + dy;
                const url = baseUrl.replace('{x}', tx).replace('{y}', ty);
                const img = new Image();
                img.crossOrigin = 'anonymous';
                const px = (tx - xCenter) * pxPerTile + W / 2;
                const py = (ty - yCenter) * pxPerTile + H / 2;
                promises.push(new Promise(resolve => {
                    img.onload = () => { try { ctx.drawImage(img, Math.round(px), Math.round(py)); } catch(_){} resolve(); };
                    img.onerror = () => resolve();
                }));
                img.src = url;
            }
        }
        await Promise.all(promises);
    }

    // Toggle handler wired to the "☔ Radar" button
    function bindRadarToggle() {
        const gd = document.querySelector('.plotly-graph-div');
        if (!gd) return;
        const buttons = document.querySelectorAll('.updatemenu-button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('☔ Radar')) {
                btn.onclick = (e) => {
                    e.preventDefault(); e.stopPropagation();
                    window._radarEnabled = !window._radarEnabled;
                    const canvas = ensureRadarCanvas();
                    if (canvas) canvas.style.display = window._radarEnabled ? 'block' : 'none';
                    // Redraw for current frame time
                    const t = (gd._transitionData && gd._transitionData._frame && gd._transitionData._frame.name) || null;
                    if (t) drawRadarForTimestamp(t.replace(/\./g,'/').replace(/ (\d{2}):(\d{2}):(\d{2})/, ' $1:$2:$3'));
                };
            }
        });
    }

    // Update radar on animation frame changes
    function bindAnimationEvents() {
        const gd = document.querySelector('.plotly-graph-div');
        if (!gd) return;
        gd.addEventListener('plotly_animated', function() {
            try {
                const t = gd._transitionData && gd._transitionData._frame && gd._transitionData._frame.name;
                if (t && window._radarEnabled) {
                    // Convert dd.mm.yyyy HH:MM:SS to ISO-like for Date parsing
                    const m = t.match(/(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})/);
                    if (m) {
                        const iso = `${m[3]}-${m[2]}-${m[1]}T${m[4]}:${m[5]}:${m[6]}Z`;
                        drawRadarForTimestamp(iso);
                    }
                }
            } catch(_){}
        });
        gd.addEventListener('plotly_relayout', function() {
            // Redraw on pan/zoom to keep alignment
            try {
                const t = gd._transitionData && gd._transitionData._frame && gd._transitionData._frame.name;
                if (window._radarEnabled) {
                    const nowIso = new Date().toISOString();
                    // Use current frame if available, else now
                    if (t) {
                        const m = t.match(/(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})/);
                        if (m) {
                            const iso = `${m[3]}-${m[2]}-${m[1]}T${m[4]}:${m[5]}:${m[6]}Z`;
                            drawRadarForTimestamp(iso); return;
                        }
                    }
                    drawRadarForTimestamp(nowIso);
                }
            } catch(_){}
        });
        window.addEventListener('resize', () => { if (window._radarEnabled) drawRadarForTimestamp(new Date().toISOString()); });
    }
    // Find all buttons and add fullscreen functionality
    function addFullscreenHandler() {
        const buttons = document.querySelectorAll('.updatemenu-button');
        buttons.forEach(button => {
            if (button.textContent.includes('⛶ Fullscreen')) {
                button.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    if (!document.fullscreenElement) {
                        // Capture current (windowed) size and margins BEFORE entering fullscreen
                        const plotDiv = document.querySelector('.plotly-graph-div');
                        if (plotDiv) {
                            const rect = plotDiv.getBoundingClientRect();
                            plotDiv.dataset.initialWidth = String(Math.floor(rect.width));
                            plotDiv.dataset.initialHeight = String(Math.floor(rect.height));
                            try {
                                if (plotDiv.layout && plotDiv.layout.margin) {
                                    plotDiv.dataset.initialMargin = JSON.stringify(plotDiv.layout.margin);
                                }
                            } catch (err) {
                                // Safe-guard if accessing layout fails
                                delete plotDiv.dataset.initialMargin;
                            }
                        }
                        // Enter fullscreen
                        document.documentElement.requestFullscreen().then(() => {
                            // Add fullscreen class for styling
                            document.body.classList.add('fullscreen-mode');

                            // After entering fullscreen, relayout to fill viewport
                            setTimeout(() => {
                                const plotDiv = document.querySelector('.plotly-graph-div');
                                if (plotDiv && window.Plotly) {
                                    window.Plotly.relayout(plotDiv, {
                                        width: Math.floor(window.innerWidth * 0.98),
                                        height: Math.floor(window.innerHeight * 0.95),
                                        margin: {l: 30, r: 30, t: 80, b: 130}
                                    });
                                }
                            }, 100);
                        }).catch(err => {
                            console.log('Fullscreen failed:', err);
                        });
                    } else {
                        // Exit fullscreen
                        document.exitFullscreen();
                    }
                };
            }
        });
    }

    // Add handlers initially and after any DOM updates
    addFullscreenHandler();
    bindRadarToggle();
    bindAnimationEvents();

    // Listen for fullscreen changes
    document.addEventListener('fullscreenchange', function() {
        const plotDiv = document.querySelector('.plotly-graph-div');
        // On exit fullscreen
        if (!document.fullscreenElement) {
            // Restore windowed mode styles and centering
            document.body.classList.remove('fullscreen-mode');
            document.body.style.margin = '';
            document.body.style.padding = '';
            document.body.style.width = '';
            document.body.style.height = '';
            document.body.style.overflow = '';
            document.documentElement.style.margin = '';
            document.documentElement.style.padding = '';

            setTimeout(() => {
                if (plotDiv && window.Plotly) {
                    const initW = plotDiv.dataset.initialWidth ? parseInt(plotDiv.dataset.initialWidth) : null;
                    const initH = plotDiv.dataset.initialHeight ? parseInt(plotDiv.dataset.initialHeight) : null;
                    let relayoutProps = {};
                    if (initW && initH) {
                        relayoutProps = { width: initW, height: initH };
                    }
                    // Restore initial margins if we captured them
                    if (plotDiv.dataset.initialMargin) {
                        try {
                            const m = JSON.parse(plotDiv.dataset.initialMargin);
                            relayoutProps['margin'] = m;
                        } catch (err) {
                            // Ignore parse errors
                        }
                    }
                    if (Object.keys(relayoutProps).length > 0) {
                        window.Plotly.relayout(plotDiv, relayoutProps);
                    }
                    window.Plotly.Plots.resize(plotDiv);
                }
            }, 100);
        } else {
            // On entering fullscreen, ensure a relayout to viewport size
            setTimeout(() => {
                if (plotDiv && window.Plotly) {
                    window.Plotly.relayout(plotDiv, {
                        width: Math.floor(window.innerWidth * 0.98),
                        height: Math.floor(window.innerHeight * 0.95)
                    });
                }
            }, 100);
        }
    });

    // Also handle window resize within fullscreen
    window.addEventListener('resize', function() {
        const plotDiv = document.querySelector('.plotly-graph-div');
        if (plotDiv && window.Plotly) {
            if (document.fullscreenElement) {
                window.Plotly.relayout(plotDiv, {
                    width: Math.floor(window.innerWidth * 0.98),
                    height: Math.floor(window.innerHeight * 0.95)
                });
            } else {
                window.Plotly.Plots.resize(plotDiv);
            }
        }
    });

    // Re-add handlers after Plotly updates (for dynamic buttons)
    const observer = new MutationObserver(function(mutations) {
        for (const mutation of mutations) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                addFullscreenHandler();
                bindRadarToggle();
                break;
            }
        }
    });
    observer.observe(document.body, {childList: true, subtree: true});

    // Ensure slider stays in sync with animation even after manual drag
    function enableSliderSync() {
        const gd = document.querySelector('.plotly-graph-div');
        if (!gd || !window.Plotly) return;

        function getFrameNames() {
            try {
                const fl = gd._fullLayout;
                if (fl && fl.sliders && fl.sliders.length && fl.sliders[0].steps) {
                    return fl.sliders[0].steps.map(s => Array.isArray(s.args[0]) ? s.args[0][0] : s.args[0]);
                }
            } catch (_) {}
            return [];
        }

        function startSyncLoop() {
            if (gd._sliderSyncTimer) clearInterval(gd._sliderSyncTimer);
            gd._sliderSyncTimer = setInterval(() => {
                try {
                    const t = gd._transitionData;
                    let name = null;
                    if (t && t._frame && t._frame.name) name = t._frame.name;
                    else if (t && t._frames && t._frameIndex != null) {
                        const fi = t._frameIndex;
                        if (t._frames[fi]) name = t._frames[fi].name || null;
                    }
                    if (!name) return;
                    const names = getFrameNames();
                    const idx = names.indexOf(name);
                    if (idx >= 0) {
                        window.Plotly.relayout(gd, {'sliders[0].active': idx});
                    }
                    if (t && t._animating === false) {
                        clearInterval(gd._sliderSyncTimer);
                        gd._sliderSyncTimer = null;
                    }
                } catch (_) {}
            }, 80);
        }

        // Start sync when animation starts
        function stopSync() {
            if (gd._sliderSyncTimer) { clearInterval(gd._sliderSyncTimer); gd._sliderSyncTimer = null; }
        }

        // Also listen to animation events (best-effort)
        if (gd.on) {
            gd.on('plotly_animationstart', startSyncLoop);
            gd.on('plotly_animationinterrupted', stopSync);
            gd.on('plotly_animated', stopSync);
        }

        // As a fallback, watch Play clicks without overriding handlers
        document.addEventListener('click', function(ev) {
            const el = ev.target.closest('.updatemenu-button');
            if (el && el.textContent && el.textContent.includes('▶️ Play')) {
                setTimeout(startSyncLoop, 50);
            }
        }, true);
    }

    // Enable sync now and after DOM changes
    enableSliderSync();
    const syncObserver = new MutationObserver(function(muts) {
        for (const m of muts) {
            if (m.addedNodes && m.addedNodes.length > 0) { enableSliderSync(); break; }
        }
    });
    syncObserver.observe(document.body, {childList: true, subtree: true});
});
</script>
"""

    return html_string.replace('</body>', fullscreen_assets + '</body>')
