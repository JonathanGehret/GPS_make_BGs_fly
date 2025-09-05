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

/* Updatemenu active glow (centralized) */
.updatemenu-button.control-active {
    /* Stronger golden glow for visibility */
    box-shadow: 0 0 0 4px rgba(255, 210, 90, 0.20), 0 0 28px 8px rgba(255, 200, 60, 0.90) !important;
    border-color: rgba(255, 200, 60, 0.98) !important;
}
/* SVG-aware styling: Plotly often renders updatemenu buttons as SVG <g>/<rect>/<text> elements.
   box-shadow doesn't apply to SVG elements, so add stroke + drop-shadow to make the glow visible. */
.updatemenu-button.control-active rect,
.updatemenu-button.control-active .updatemenu-item-rect,
.updatemenu-button.control-active .updatemenu-dropdown-button,
.updatemenu-button.control-active .dropdown-button-rect {
    /* SVG-aware golden stroke + drop-shadow for visible glow */
    stroke: rgba(255, 200, 60, 0.98);
    stroke-width: 2.5px;
    fill-opacity: 0.98;
    filter: drop-shadow(0 0 14px rgba(255,200,60,0.95));
}

/* Precip-specific active style for SVG buttons */
.updatemenu-button.precip-active rect,
.updatemenu-button.precip-active .updatemenu-item-rect,
.updatemenu-button.precip-active .updatemenu-dropdown-button {
    /* Make Precip button match the golden highlight for extra visibility */
    stroke: rgba(255, 185, 55, 0.98);
    stroke-width: 2.5px;
    filter: drop-shadow(0 0 14px rgba(255,185,55,0.9));
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
</style>
<script>
// Enhanced fullscreen functionality with better centering
document.addEventListener('DOMContentLoaded', function() {
    // (Removed legacy Radar overlay injection)
    // Centralized control-state helpers (button glow / play/pause/fullscreen/recenter)
    // Exposes a small API on window.__CONTROL for other injected scripts to call.
    (function(){
        if (window.__CONTROL) return; // already injected
        window.__CONTROL = {
            // Robust label matching: normalize emoji/variation selectors and read SVG <text> children
            setControlActive: function(label, on) {
                try {
                    function normalize(s) {
                        if (!s) return '';
                        // strip variation selectors (U+FE0E/U+FE0F) and collapse whitespace
                        return s.replace(/\uFE0E|\uFE0F/g, '').replace(/\s+/g, ' ').trim();
                    }
                    function getLabelFromButton(b) {
                        // Prefer explicit textContent, then search for SVG text nodes
                        let txt = (b.textContent || '') + '';
                        if (!txt || txt.trim().length === 0) {
                            const t = b.querySelector && (b.querySelector('text') || b.querySelector('tspan'));
                            if (t) txt = t.textContent || '';
                        }
                        return normalize(txt);
                    }
                    const want = normalize(label);
                    const btns = document.querySelectorAll('.updatemenu-button');
                    btns.forEach(b => {
                        try {
                            const txt = getLabelFromButton(b);
                            if (txt && txt.indexOf(want) !== -1) {
                                if (on) b.classList.add('control-active'); else b.classList.remove('control-active');
                            }
                        } catch(_){}
                    });
                } catch(_){ }
            },
            findMapAndStoreOriginal: function() {
                try {
                    const gd = document.querySelector('.plotly-graph-div'); if (!gd) return null;
                    const map = gd._fullLayout && gd._fullLayout.map; if (!map) return null;
                    if (!window.__ORIG_MAP) {
                        window.__ORIG_MAP = { lat: map.center.lat, lon: map.center.lon, zoom: map.zoom };
                    }
                    return map;
                } catch(_) { return null; }
            },
            checkRecenterState: function() {
                try {
                    const gd = document.querySelector('.plotly-graph-div'); if (!gd) return;
                    const map = gd._fullLayout && gd._fullLayout.map; if (!map || !window.__ORIG_MAP) return;
                    const tol = 1e-6;
                    const same = Math.abs((map.center.lat || 0) - (window.__ORIG_MAP.lat || 0)) < tol &&
                                 Math.abs((map.center.lon || 0) - (window.__ORIG_MAP.lon || 0)) < tol &&
                                 Math.abs((map.zoom || 0) - (window.__ORIG_MAP.zoom || 0)) < 1e-3;
                    this.setControlActive('🎯 Recenter', same);
                } catch(_){}
            },
            bindControlInterceptors: function() {
                try {
                    function normalize(s) { return (s||'').replace(/\uFE0E|\uFE0F/g,'').replace(/\s+/g,' ').trim(); }
                    function getLabelFromButton(b) {
                        let txt = (b.textContent || '') + '';
                        if (!txt || txt.trim().length === 0) {
                            const t = b.querySelector && (b.querySelector('text') || b.querySelector('tspan'));
                            if (t) txt = t.textContent || '';
                        }
                        return normalize(txt);
                    }
                    const btns = document.querySelectorAll('.updatemenu-button');
                    btns.forEach(b => {
                        // don't capture textContent at bind-time (Plotly may render later) — read on click
                        b.addEventListener('click', function(e) {
                            try {
                                const textNow = getLabelFromButton(b);
                                if (textNow.indexOf(normalize('▶️ Play')) !== -1) {
                                    window.__CONTROL.setControlActive('▶️ Play', true);
                                    window.__CONTROL.setControlActive('⏸️ Pause', false);
                                } else if (textNow.indexOf(normalize('⏸️ Pause')) !== -1) {
                                    window.__CONTROL.setControlActive('⏸️ Pause', true);
                                    window.__CONTROL.setControlActive('▶️ Play', false);
                                } else if (textNow.indexOf(normalize('⛶ Fullscreen')) !== -1) {
                                    const willBe = !document.fullscreenElement;
                                    window.__CONTROL.setControlActive('⛶ Fullscreen', willBe);
                                } else if (textNow.indexOf(normalize('🎯 Recenter')) !== -1) {
                                    window.__CONTROL.setControlActive('🎯 Recenter', true);
                                    setTimeout(()=>{ window.__CONTROL.checkRecenterState(); }, 250);
                                }
                            } catch(_){ }
                        }, true);
                    });
                } catch(_){ }
            }
        };

        // Hook into plotly and document events to update visual state
        try {
            const gd = document.querySelector('.plotly-graph-div');
            if (gd) {
                gd.addEventListener('plotly_animated', function() {
                    window.__CONTROL.setControlActive('▶️ Play', true);
                    window.__CONTROL.setControlActive('⏸️ Pause', false);
                });
                gd.addEventListener('plotly_relayout', function() {
                    window.__CONTROL.setControlActive('⏸️ Pause', true);
                    window.__CONTROL.setControlActive('▶️ Play', false);
                    try { if (window.__CONTROL) window.__CONTROL.checkRecenterState(); } catch(_){}
                });
            }
        } catch(_){}

        document.addEventListener('fullscreenchange', function() {
            const isFs = !!document.fullscreenElement;
            window.__CONTROL.setControlActive('⛶ Fullscreen', isFs);
        });

        // Observe DOM changes to rebind handlers
        const ctrlObserver = new MutationObserver(function(muts) {
            for (const m of muts) {
                if (m.addedNodes && m.addedNodes.length>0) { window.__CONTROL.bindControlInterceptors(); break; }
            }
        });
        ctrlObserver.observe(document.body, {childList:true, subtree:true});

    // Initial bind
    window.__CONTROL.bindControlInterceptors();
    window.__CONTROL.findMapAndStoreOriginal();
    window.__CONTROL.checkRecenterState();
    })();
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
