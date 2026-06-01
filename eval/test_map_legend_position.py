"""Regression guard: the map legend sits in the map corner, not lifted to clear
a bottom action-button band.

The location-checker ("Check Address") CTA that the legend used to dodge was
removed in the archive pivot (#86). Its old `bottom: 72px` CTA-clearance offset
then floated the legend high in the now-short archive map (owner flagged it
2026-06-01). This guard fails if the legend re-acquires a large bottom offset --
i.e. someone reintroduces a bottom CTA without also moving the legend. Pure text
guard; no JS runtime (the harness has none).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

MAX_CORNER_INSET_PX = 24  # a corner inset; the dead CTA-clearance offset was 72px


def test_legend_at_corner_not_cta_clearance():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.map-legend\s*\{([^}]*)\}", text)
    body = m.group(1) if m else ""
    bm = re.search(r"bottom:\s*([0-9.]+)px", body)
    bottom = float(bm.group(1)) if bm else -1.0
    ok = m is not None and bm is not None and bottom <= MAX_CORNER_INSET_PX
    return {
        "passed": ok,
        "details": f".map-legend bottom={bottom}px (<= {MAX_CORNER_INSET_PX}px corner inset)"
        if ok
        else f".map-legend bottom={bottom}px exceeds {MAX_CORNER_INSET_PX}px corner inset "
        f"(stale CTA-clearance offset?) or .map-legend rule/value missing",
        "metrics": {"bottom_px": bottom},
    }
