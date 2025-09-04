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
                        // Enter fullscreen
                        document.documentElement.requestFullscreen().then(() => {
                            // Add fullscreen class for styling
                            document.body.classList.add('fullscreen-mode');

                            // Trigger Plotly resize with slight delay
                            setTimeout(() => {
                                const plotDiv = document.querySelector('.plotly-graph-div');
                                if (plotDiv && window.Plotly) {
                                    window.Plotly.Plots.resize(plotDiv);
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
        if (!document.fullscreenElement) {
            // Remove fullscreen class when exiting fullscreen
            document.body.classList.remove('fullscreen-mode');
        }
        // Trigger resize on both enter and exit
        setTimeout(() => {
            if (plotDiv && window.Plotly) {
                window.Plotly.Plots.resize(plotDiv);
            }
        }, 100);
    });

    // Also handle window resize within fullscreen
    window.addEventListener('resize', function() {
        const plotDiv = document.querySelector('.plotly-graph-div');
        if (plotDiv && window.Plotly) {
            window.Plotly.Plots.resize(plotDiv);
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
});
</script>
"""

    return html_string.replace('</body>', fullscreen_assets + '</body>')
