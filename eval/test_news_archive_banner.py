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
    not_complete = "not complete" in val or "not a complete" in val
    discloses = "snapshot" in val and not_complete
    return {"passed": discloses,
            "details": "banner discloses snapshot + non-completeness" if discloses
            else f"banner over-implies completeness: snapshot={'snapshot' in val} not_complete={not_complete}"}


def test_archive_note_frozen_no_ongoing_collection():
    """Fully-historical pivot (2026-06-01): the archive is a FROZEN record of the May 21-26
    emergency. The banner must state the collection window AND frame it as a frozen, not-live
    record — but must NOT imply collection continues after the window. The old copy's
    'After evacuation lifted: official statements only' clause both (a) used 'official statements
    only' jargon and (b) created a 21-26-vs-ongoing contradiction (the window says collection
    stopped on the 26th; the clause says officials kept arriving). New contract: state the
    window, frame it as frozen/not-live, drop the cutoff/ongoing-collection clause and its
    jargon. 'all-clear' stays forbidden (user follow-up 2026-06-01: simplify, drop jargon)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"news\.archive\.note":\s*\{\s*en:\s*"([^"]*)"', text)
    val = (m.group(1) if m else "").lower()
    states_window = ("21–26" in val or "21-26" in val) and "2026" in val
    frozen_framing = "frozen" in val or "not live" in val
    no_ongoing_jargon = "official statements only" not in val
    no_cutoff_contradiction = "after evacuation lifted" not in val and "going forward" not in val
    forbids_jargon = "all-clear" not in val
    ok = states_window and frozen_framing and no_ongoing_jargon and no_cutoff_contradiction and forbids_jargon
    return {"passed": ok,
            "details": "banner: May 21-26 window + frozen/not-live framing, no ongoing-collection clause" if ok
            else (f"window={states_window} frozen={frozen_framing} no_jargon={no_ongoing_jargon} "
                  f"no_contradiction={no_cutoff_contradiction} no_allclear={forbids_jargon}")}


def test_archive_note_structured_header_and_bullets():
    """Layout (user follow-up 2026-06-01): the archive note is organized into a labeled header
    + bulleted lines, not one run-on block of back-to-back sentences. Rendered as HTML via
    data-i18n-html so the structure survives localization; guards against silently collapsing
    back to a single paragraph."""
    text = DASHBOARD.read_text(encoding="utf-8")
    renders_html = 'data-i18n-html="news.archive.note"' in text
    m = re.search(r'"news\.archive\.note":\s*\{\s*en:\s*"([^"]*)"', text)
    val = m.group(1) if m else ""
    has_bullets = val.count("<li>") >= 2
    has_header = "archive-note-h" in val
    ok = renders_html and has_bullets and has_header
    return {"passed": ok,
            "details": "archive note = labeled header + bulleted lines (data-i18n-html)" if ok
            else f"renders_html={renders_html} bullets={val.count('<li>')} header={has_header}"}
