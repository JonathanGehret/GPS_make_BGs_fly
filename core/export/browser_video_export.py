from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

try:
  from playwright.sync_api import sync_playwright  # type: ignore
except Exception:  # defer import error until function call
  sync_playwright = None  # type: ignore


def _js_get_frame_names() -> str:
    """Return JS snippet to extract frame names from the Plotly graph div."""
    return (
        """
        () => {
          const gd = document.querySelector('.plotly-graph-div');
          if (!gd) return [];
          // Prefer slider step args as authoritative frame names
          const sliders = (gd._fullLayout && gd._fullLayout.sliders) || [];
          if (sliders.length && sliders[0].steps && sliders[0].steps.length) {
            const steps = sliders[0].steps;
            return steps.map(s => {
              if (Array.isArray(s.args) && s.args.length > 0 && Array.isArray(s.args[0])) return s.args[0][0];
              if (Array.isArray(s.args) && s.args.length > 0) return s.args[0];
              return (s.label || '').toString();
            });
          }
          // Fallback to internal frames list
          const frames = (gd._transitionData && gd._transitionData._frames) || [];
          if (frames.length) return frames.map(f => f.name || '');
          return [];
        }
        """
    )


def _js_animate_to_frame(_name: str) -> str:
    """Return JS snippet that animates to a given frame name and resolves after animation."""
    return (
        """
        async (frameName) => {
          const gd = document.querySelector('.plotly-graph-div');
          if (!gd) return false;
          return await new Promise(async (resolve) => {
            let done = false;
            function handler() {
              if (!done) { done = true; gd.removeEventListener('plotly_animated', handler); resolve(true); }
            }
            gd.addEventListener('plotly_animated', handler, { once: true });
            try {
              await window.Plotly.animate(gd, [frameName], {
                transition: { duration: 0 },
                frame: { duration: 0, redraw: true, mode: 'immediate' }
              });
              // safety fallback if event not fired
              setTimeout(() => { if (!done) { done = true; gd.removeEventListener('plotly_animated', handler); resolve(true); } }, 100);
            } catch (e) {
              resolve(false);
            }
          });
        }
        """
    )


def export_animation_video_browser(
  html_path: str,
  out_basename: str,
  *,
  fps: int = 30,
  width: int = 1280,
  height: int = 720,
  quality_crf: int = 20,
  headless: bool = True,
) -> str:
  """
  Render the already-generated interactive HTML in a real browser (Chromium/Chrome) and
  capture one screenshot per animation frame, then encode MP4 with ffmpeg.

  This preserves the actual web map tiles and visuals.
  Requires: pip install playwright, and a Chromium/Chrome available. We launch the system
  Chrome via channel='chrome' when available, else default Chromium.
  """
  if sync_playwright is None:
    raise RuntimeError(
      "Playwright is required for browser-based export. Install with 'pip install playwright' "
      "and run 'playwright install chromium' once."
    )

  html_file = Path(html_path)
  if not html_file.exists():
    raise FileNotFoundError(f"HTML not found: {html_path}")

  out_mp4 = str(Path(out_basename).with_suffix(".mp4"))
  tmpdir = Path(tempfile.mkdtemp(prefix="frames_browser_"))
  try:
    with sync_playwright() as p:
      # Try Chrome first to reuse system installation, else fall back to bundled Chromium
      try:
        browser = p.chromium.launch(channel="chrome", headless=headless)
      except Exception:
        browser = p.chromium.launch(headless=headless)

      page = browser.new_page(viewport={"width": width, "height": height, "deviceScaleFactor": 1})
      page.goto(html_file.as_uri(), wait_until="networkidle")
      # Give tiles a moment to settle
      page.wait_for_timeout(400)

  # (Radar overlay removed) No auto-toggle needed here.

      # Extract frame names from the figure
      frame_names: List[str] = page.evaluate(_js_get_frame_names())
      if not frame_names:
        # Single frame capture fallback
        page.locator(".plotly-graph-div").screenshot(path=str(tmpdir / f"{0:05d}.png"))
        browser.close()
      else:
        animate_fn = _js_animate_to_frame("")  # function text to be used via evaluate
        for i, name in enumerate(frame_names):
          # animate then screenshot
          page.evaluate(animate_fn, name)
          # small delay to ensure tiles/text have updated
          page.wait_for_timeout(30)
          page.locator(".plotly-graph-div").screenshot(path=str(tmpdir / f"{i:05d}.png"))
        browser.close()

    # Encode with ffmpeg
    cmd = [
      "ffmpeg",
      "-y",
      "-framerate",
      str(fps),
      "-i",
      str(tmpdir / "%05d.png"),
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      "-crf",
      str(quality_crf),
      out_mp4,
    ]
    subprocess.run(cmd, check=True)
    return out_mp4
  finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
