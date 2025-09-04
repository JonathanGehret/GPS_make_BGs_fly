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
</style>
<script>
// Enhanced fullscreen functionality with better centering
document.addEventListener('DOMContentLoaded', function() {
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
