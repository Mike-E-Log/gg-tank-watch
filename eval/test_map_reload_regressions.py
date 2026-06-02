"""Regression guards from the 2026-05-31 Firefox-mobile blank-map investigation.

Two bugs, both confirmed in a live Firefox-mobile console on reload:

1. sw.js wrapped EVERY cross-origin request in
   `event.respondWith(fetch(event.request))`. On Firefox the re-dispatched
   cross-origin fetch rejects ("CORS request did not succeed" / NetworkError),
   so the OpenFreeMap map style + glyph tiles never loaded and the map blanked
   on reload (the service worker only controls the page AFTER the first load,
   which is why a fresh load worked and a reload did not). The fix is to NOT
   intercept cross-origin requests — let the browser fetch them natively.

2. dashboard.html still carried `recolorFixedPoints()`, dead code from the
   pre-MapLibre Leaflet map that references a `fixedPointMarkers` global which
   no longer exists. It threw `ReferenceError: fixedPointMarkers is not defined`
   on every load inside refreshWind(), so scheduleWindRefresh() never ran and
   the wind indicator stopped auto-refreshing.

Pure text guards; no JS / service-worker runtime needed (the harness has none).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
SW = REPO_ROOT / "sw.js"
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_sw_does_not_intercept_cross_origin():
    """The service worker must not re-dispatch cross-origin requests through
    respondWith(fetch(event.request)); that blanked the map on Firefox reload."""
    norm = "".join(SW.read_text(encoding="utf-8").split())
    bad = "event.respondWith(fetch(event.request))" in norm
    return {
        "passed": not bad,
        "details": "cross-origin requests fall through to native browser fetch"
        if not bad
        else "sw.js still wraps cross-origin requests in respondWith(fetch(event.request)) "
        "(rejects on Firefox -> map blanks on reload)",
        "metrics": {"blanket_intercept": int(bad)},
    }


def test_legend_promoted_to_own_compositing_layer():
    """2026-06-02 investigation: on reload the GPU compositor intermittently composites a slice
    of the MapLibre WebGL canvas (light-blue water, lower-left) ABOVE the opaque legend, drawing
    a light-blue line through it. The legend is z-index:2 but a plain painted element, while the
    canvas is its own composited layer — mixing the two lets the canvas win on some reload-timing
    layer churn. Promoting the legend to its own compositing layer (transform: translateZ(0))
    makes the compositor order it above the canvas deterministically. Guards that promotion stays."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find(".map-legend {")
    j = text.find("}", i) if i >= 0 else -1
    rule = text[i:j] if (i >= 0 and j > i) else ""
    promoted = "translateZ(0)" in rule or "will-change: transform" in rule
    return {"passed": bool(rule) and promoted,
            "details": f"rule_found={bool(rule)} layer_promoted={promoted}"}


def test_tab_panel_keeps_persistent_stacking_context():
    """2026-06-02 (deepened root cause, adversarially vetted): the light-blue line is the MapLibre
    WebGL canvas compositing over the legend. The real cause is that .tab-panel's stacking context
    DISSOLVES at opacity:1 -- per CSS spec opacity<1 creates a stacking context but opacity:1 does
    not, so at the end of the 0.15s reveal (and on reload) the compositor re-resolves canvas-vs-
    legend z-order against a non-context parent and the water slice flickers above the legend.
    isolation:isolate forces .tab-panel to ALWAYS be a stacking context, keeping the legend
    (z-index:2) above the canvas in every opacity state. This is why the legend-only translateZ
    (PR #101) and the resize() (PR #100) could not fix it -- neither stabilizes the PARENT context."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.tab-panel\s*\{[^}]*inset:\s*0[^}]*\}", text)
    rule = m.group(0) if m else ""
    isolated = "isolation: isolate" in rule
    return {"passed": bool(rule) and isolated,
            "details": f"main_tab_panel_rule_found={bool(rule)} isolation_isolate={isolated}"}


def test_no_orphaned_leaflet_marker_code():
    """dashboard.html must not reference the removed Leaflet `fixedPointMarkers`
    global or its `recolorFixedPoints` helper -- they throw ReferenceError and
    halt the wind auto-refresh."""
    text = DASHBOARD.read_text(encoding="utf-8")
    found = [s for s in ("fixedPointMarkers", "recolorFixedPoints") if s in text]
    return {
        "passed": not found,
        "details": "no orphaned Leaflet marker references"
        if not found
        else "orphaned Leaflet symbols still present: " + ", ".join(found),
        "metrics": {"orphaned_refs": len(found)},
    }
