"""Guard for the mobile map zoom-out range.

Mobile viewports get a lower MapLibre `minZoom` floor than desktop so residents
on a phone can pinch out far enough to see the evacuation zone in its regional
context. Desktop keeps the tighter floor (it has the screen room to stay close).

The split reuses the codebase's existing viewport convention
(`window.innerWidth >= 768`, see dashboard.html updateInfoData()): desktop floor
zoom 10, mobile floor zoom 8.

Pure text guard; no JS runtime needed (the harness has none).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_mobile_minzoom_floor_is_lower_than_desktop():
    """The map's minZoom must be viewport-gated: zoom 8 on mobile (< 768px),
    zoom 10 on desktop -- so mobile can zoom out further than desktop."""
    norm = "".join(DASHBOARD.read_text(encoding="utf-8").split())
    gated = "minZoom:window.innerWidth>=768?10:8" in norm
    static_floor = "minZoom:10," in norm
    passed = gated and not static_floor
    return {
        "passed": passed,
        "details": "minZoom is viewport-gated (mobile floor z8, desktop floor z10)"
        if passed
        else "expected `minZoom: window.innerWidth >= 768 ? 10 : 8` and no static "
        "`minZoom: 10,`; mobile cannot zoom out further than desktop",
        "metrics": {"viewport_gated": int(gated), "static_floor_present": int(static_floor)},
    }
