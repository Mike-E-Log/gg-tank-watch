"""Guard: the News tab carries a persistent archive-note banner ABOVE the feed (2026-05-31).

Resolved-state demonstration: the News tab is a historical Coverage Archive, not a live
feed. The note routes to officials and never claims authority. Anchored on the real markup
tag — class names also appear in the inline <style>, so a bare-name find() would measure CSS
order, not DOM order (see eval-find-hits-css-before-html).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_archive_note_present_and_localized():
    text = DASHBOARD.read_text(encoding="utf-8")
    has_markup = '<div class="news-archive-note"' in text
    has_i18n = '"news.archive.note": { en:' in text
    return {"passed": has_markup and has_i18n,
            "details": "archive-note markup + en string present"
            if (has_markup and has_i18n) else f"markup={has_markup} i18n={has_i18n}"}


def test_archive_note_before_feed():
    text = DASHBOARD.read_text(encoding="utf-8")
    i_note = text.find('<div class="news-archive-note"')
    i_feed = text.find('<div id="news-feed">')
    ok = -1 < i_note < i_feed
    return {"passed": ok,
            "details": "order: archive-note < news-feed" if ok
            else f"bad order note={i_note} feed={i_feed}",
            "metrics": {"note": i_note, "feed": i_feed}}


def test_archive_note_routes_official_no_authority_chrome():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"news\.archive\.note":\s*\{\s*en:\s*"([^"]*)"', text)
    val = (m.group(1) if m else "")
    routes = "ggcity.org/emergency" in val or "911" in val
    forbidden = any(bad in val.lower() for bad in ["verified", "official source", "government"])
    return {"passed": bool(val) and routes and not forbidden,
            "details": f"routes={routes} forbidden_terms_present={forbidden} len={len(val)}"}


def test_archive_note_discloses_snapshot():
    """Honesty: the banner must disclose the archive is a curated snapshot/selection, not a
    complete or live record (it covers only part of the May 2026 incident window)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"news\.archive\.note":\s*\{\s*en:\s*"([^"]*)"', text)
    val = (m.group(1) if m else "").lower()
    discloses = "snapshot" in val and "not a complete" in val
    return {"passed": discloses,
            "details": "banner discloses snapshot + non-completeness" if discloses
            else f"banner over-implies completeness: snapshot={'snapshot' in val} not_complete={'not a complete' in val}"}
