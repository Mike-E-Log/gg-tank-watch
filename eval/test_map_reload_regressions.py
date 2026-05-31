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
