"""Guard (T1, archive pivot): the topbar masthead frames the app as a frozen historical
archive — an ARCHIVE pill beside UNOFFICIAL, and the freshness slot bound to a fixed
archive label (archive.label) instead of the live "Last updated {age}" (updated.freshness)."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASH = REPO_ROOT / "dashboard.html"


def test_archive_pill_present():
    t = DASH.read_text(encoding="utf-8")
    has_pill = "archive-pill" in t or 'data-i18n="topbar.archive"' in t
    return {"passed": has_pill, "details": f"archive pill present={has_pill}"}


def test_freshness_label_is_archive_not_live():
    t = DASH.read_text(encoding="utf-8")
    has_key = '"archive.label"' in t
    bound = 'data-i18n="archive.label"' in t
    return {"passed": has_key and bound,
            "details": f"archive.label key={has_key} bound_in_topbar={bound}"}
