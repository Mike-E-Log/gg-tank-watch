"""Guard: the topbar freshness dateline can't hard-clip "(N ago)" on mobile (2026-06-01).

On narrow viewports "Last updated 5/31, 6:09 PM (12 min ago)" overflowed `.topbar-freshness`
(white-space:nowrap; overflow:hidden) and the tail was cut. Fix: on mobile show the relative
age ALONE ("Last updated 12 min ago") and keep the absolute clock in the existing tooltip.
Anchored on the live wiring so a revert to the unconditional clock+age label fails this.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_freshness_label_is_viewport_aware():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": "_isDesktop" in text and "window.innerWidth >= 768" in text,
            "details": "freshness label branches on viewport width (_isDesktop)"}


def test_freshness_mobile_is_age_only():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = "(!_isDesktop && ageStr) ? ageStr" in text
    return {"passed": ok,
            "details": "mobile freshness label = relative age only (no absolute clock to clip)"
            if ok else "mobile age-only branch missing -> clock+age can clip on narrow screens"}
