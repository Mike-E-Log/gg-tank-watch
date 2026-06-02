"""Guard: the persistent global safety strip is the single, LABELED home for the route to
officials (2026-06-02).

The route was consolidated OUT of the News archive note into the strip (which renders on every
tab and stays pinned above the feed on scroll — the app is a fixed-viewport shell where only the
tab content scrolls). A 'Current info:' label was added so a cold visitor knows what 911 / the
city URL are for. This guard relocates the routes-to-officials safety property: it must hold at
the strip even though it no longer lives in the archive note (see
test_news_archive_banner::test_archive_note_route_consolidated_to_strip).

Anchored on the full markup of the safety-strip-sources block — bare class names also match the
inline <style>, so a whole-file find() would measure CSS order, not DOM order.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def _sources_block(text):
    m = re.search(r'<div class="safety-strip-sources">(.*?)</div>', text, re.S)
    return m.group(1) if m else ""


def test_safety_strip_routes_to_officials():
    """The strip must carry the actual route — a tel:911 link and the ggcity.org/emergency link —
    so a user on any tab (the News archive included) can reach officials with the note's own route
    gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _sources_block(text)
    tel = '<a href="tel:911">911</a>' in block
    city = 'href="https://ggcity.org/emergency"' in block and ">ggcity.org/emergency</a>" in block
    ok = bool(block) and tel and city
    return {"passed": ok,
            "details": "strip routes to officials: tel:911 + ggcity link" if ok
            else f"tel={tel} city={city} block_found={bool(block)}"}


def test_safety_strip_route_is_labeled():
    """The route row must be LABELED so a cold visitor knows what the links are for (the unlabeled
    '911 · ggcity · Terms' row was ambiguous). Guards the label markup + a non-empty en string."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _sources_block(text)
    has_label_markup = 'data-i18n="safety.strip.route"' in block
    m = re.search(r'"safety\.strip\.route":\s*\{\s*en:\s*"([^"]*)"', text)
    label = (m.group(1) if m else "").strip()
    ok = bool(block) and has_label_markup and bool(label)
    return {"passed": ok,
            "details": f"route row labeled: '{label}'" if ok
            else f"label_markup={has_label_markup} label='{label}'"}


def test_safety_strip_terms_outside_route_label():
    """Honesty: the legal 'Terms' link must NOT sit inside the labeled 'Current info:' route row —
    the label would scope it and imply Terms is current official guidance. Terms belongs with the
    'Informational only - not official' disclaimer (legal grouped with legal). Guards that the
    Terms link lives OUTSIDE the safety-strip-sources block."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _sources_block(text)
    terms_in_route_row = "terms.html" in block or "safety.strip.terms" in block
    ok = bool(block) and not terms_in_route_row
    return {"passed": ok,
            "details": "Terms link sits outside the labeled route row" if ok
            else "Terms link is inside the Current-info route row (ambiguous label scope)"}
