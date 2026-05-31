"""Guard for the map zoom-out floor.

The map's MapLibre `minZoom` floor is a uniform zoom 8 on every viewport, so a
desktop user can zoom out for regional context exactly as far as a phone user
can pinch out. (Earlier the floor was viewport-gated -- desktop z10, mobile z8 --
but that kept desktop from zooming out as far as mobile, which residents wanted.)

Pure text guard; no JS runtime needed (the harness has none).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_minzoom_floor_is_uniform_z8():
    """The map's minZoom must be a flat zoom 8 on all viewports -- not gated to a
    tighter desktop floor -- so desktop can zoom out as far as mobile."""
    norm = "".join(DASHBOARD.read_text(encoding="utf-8").split())
    uniform = "minZoom:8," in norm
    gated = "minZoom:window.innerWidth>=768?10:8" in norm
    desktop_floor = "minZoom:10," in norm
    passed = uniform and not gated and not desktop_floor
    return {
        "passed": passed,
        "details": "minZoom is a uniform z8 floor (desktop zooms out as far as mobile)"
        if passed
        else "expected a flat `minZoom: 8,` with no viewport gating and no static "
        "`minZoom: 10,`; desktop cannot zoom out as far as mobile",
        "metrics": {
            "uniform_z8": int(uniform),
            "viewport_gated": int(gated),
            "desktop_floor_present": int(desktop_floor),
        },
    }
