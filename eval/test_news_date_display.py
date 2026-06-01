"""Guard: archive items render absolute dates (date+time when verified, date-only when
not), never relativeTime, so a resolved record doesn't drift to 'months ago' (2026-05-31)."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_archive_date_helpers_present():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": "function fmtAbsDateOnly" in text and "function fmtArchiveWhen" in text,
            "details": "absolute date-only + archive-when helpers present"}


def test_archive_when_branches_on_confidence():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = 'confidence === "verified"' in text
    return {"passed": ok, "details": "date display branches on published_iso_confidence"}


def test_renderer_uses_isarchive_for_date():
    """Wiring guard: the active renderer routes archive items (isArchive) through
    fmtArchiveWhen, not relativeTime — so a resolved record can't drift to 'months ago'
    even if the helpers exist but were never wired into buildFeedCardsHtml (adversarial
    review 2026-05-31)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = "it.isArchive ? fmtArchiveWhen(it)" in text
    return {"passed": ok, "details": "renderer branches archive items to fmtArchiveWhen"}
