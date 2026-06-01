"""Guard: archive items AND live official statements render absolute dates (date+time when
verified, date-only when not), never relativeTime, so a resolved record doesn't drift to
'months ago'; and no timestamp sits at midnight UTC, which renders a day early in Pacific
(2026-05-31)."""
import json
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"
STATUS = REPO_ROOT / "status.json"
ARCHIVE = REPO_ROOT / "data" / "news_archive.json"


def test_archive_date_helpers_present():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": "function fmtAbsDateOnly" in text and "function fmtArchiveWhen" in text,
            "details": "absolute date-only + archive-when helpers present"}


def test_archive_when_branches_on_confidence():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = 'confidence === "verified"' in text
    return {"passed": ok, "details": "date display branches on published_iso_confidence"}


def test_renderer_uses_absolute_for_archive_and_officials():
    """Wiring guard: the active renderer routes archive items (isArchive) AND live official
    statements (type === "official") through fmtArchiveWhen, not relativeTime — so neither a
    resolved record nor a status.json official can drift to a relative 'Fri 5:00 PM' label
    (user follow-up 2026-05-31; extends adversarial review 2026-05-31)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = '(it.isArchive || it.type === "official") ? fmtArchiveWhen(it)' in text
    return {"passed": ok,
            "details": "renderer branches archive + official items to fmtArchiveWhen"}


def test_live_officials_not_midnight_utc():
    """status.json official statements must not carry a midnight-UTC time_iso: T00:00:00Z is
    5pm the PREVIOUS day in Pacific, so the card shows the wrong date. Normalize to noon UTC."""
    d = json.loads(STATUS.read_text(encoding="utf-8"))
    bad = [s.get("time_iso") for s in d.get("official_statements", [])
           if (s.get("time_iso") or "").endswith("T00:00:00Z")]
    return {"passed": not bad,
            "details": "no midnight-UTC official time_iso" if not bad
            else f"midnight-UTC officials render a day early: {bad}"}


def test_archive_published_iso_not_midnight_utc():
    """Archive items must not carry a midnight-UTC published_iso for the same Pacific
    day-early reason (the resolved record is frozen — dates must read true)."""
    d = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    bad = sum(1 for it in d.get("items", [])
              if (it.get("published_iso") or "").endswith("T00:00:00Z"))
    return {"passed": bad == 0,
            "details": "no midnight-UTC published_iso" if bad == 0
            else f"{bad} archive items at midnight-UTC render a day early in Pacific"}
