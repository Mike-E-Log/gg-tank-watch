"""Guards for Map-tab landing + reveal (user follow-up 2026-06-02):

1. A first-time visitor (no saved tab) must land on Map — the markup default-active panel
   is panel-map. (Returning-visitor restore is a separate, kept feature: test_tab_persist.)
2. Switching TO the Map tab must force a MapLibre repaint. Inactive panels are opacity:0
   (not display:none), so the GL canvas sits composited-but-invisible; revealing it via the
   0.15s opacity fade can show a stale compositing seam (a light-blue line) through the legend.
   _ggMap.resize() re-syncs the canvas (verified in lib/maplibre-gl.js: resize() re-runs
   _resizeCanvas + painter.resize + a render with no unchanged-size early-out).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_default_active_panel_is_map():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'<div class="tab-panel active" id="panel-([a-z]+)"', text)
    panel = m.group(1) if m else ""
    return {"passed": panel == "map", "details": f"default active panel={panel!r}"}


def test_switchtab_repaints_map_on_reveal():
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find("function switchTab(tabId)")
    j = text.find("window.switchTab = switchTab", i)
    body = text[i:j] if (i >= 0 and j > i) else ""
    gated_on_map = '"map"' in body
    repaints = "_ggMap.resize()" in body
    ok = bool(body) and gated_on_map and repaints
    return {"passed": ok,
            "details": f"body_found={bool(body)} gated_on_map={gated_on_map} repaints={repaints}"}
