"""Guard (archive pivot, 2026-06-01): the live, viewport-dependent "Last updated {age}"
freshness label was REMOVED. It could hard-clip "(N ago)" on mobile — but more importantly
a frozen archive must not show a live, self-updating age. The freshness slot is now a fixed
historical-archive label (archive.label). This guards against regressing to the live label.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_no_live_age_freshness_label():
    text = DASHBOARD.read_text(encoding="utf-8")
    no_live = "(!_isDesktop && ageStr) ? ageStr" not in text and "relativeAge(" not in text
    archive = 'data-i18n="archive.label"' in text
    return {"passed": no_live and archive,
            "details": f"live-age-label removed={no_live}, archive label bound={archive}"}
