"""Guard: ONE consolidated banner across all tabs; every tab is pure content below it.

User directive (2026-06-01): collapse the hero-status strip + safety strip into a SINGLE
persistent banner (disclaimer + resolved/all-clear + route to officials), and remove every
per-tab/per-subtab note — the Map historical caption, the News archive-note, and the Info
Status/Resources resolved-notes — plus the About panel's redundant disclaimer + official-
routing prose. The persistent AI-assistance disclosure stays in the About sub-tab (its single
allowed in-content home). This deliberately reverses the per-tab-note design (#93 + the
2026-06-02 map/news captions); the obsolete per-note guards are removed in favor of these.

Anchors on full markup tags / ids — class names also appear in the inline <style>, so a
bare-name find() would measure CSS order, not DOM order (see eval-find-hits-css-before-html).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_single_banner_replaces_hero_status():
    """The one banner is the persistent safety strip; the separate hero-status strip is gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    has_banner = 'class="safety-strip"' in text
    no_hero_section = 'class="hero-status"' not in text and 'id="hero"' not in text
    ok = has_banner and no_hero_section
    return {"passed": ok,
            "details": "safety-strip banner present + hero-status section removed"
            if ok else f"banner={has_banner} hero_status_removed={no_hero_section}"}


def test_no_per_tab_notes_anywhere():
    """No per-tab or per-subtab disclosure note survives: not the Map caption, the News
    archive-note, nor the Info Status/Resources resolved-notes."""
    text = DASHBOARD.read_text(encoding="utf-8")
    checks = {
        "no_status_note": 'id="status-resolved-note"' not in text,
        "no_resources_note": 'id="resources-resolved-note"' not in text,
        "no_map_note": "map-historical-note" not in text and 'data-i18n="map.historical"' not in text,
        "no_news_note": "news-archive-note" not in text,
    }
    ok = all(checks.values())
    return {"passed": ok, "details": str(checks)}


def test_banner_carries_disclaimer_resolved_and_route():
    """The one banner discloses informational-only, carries the resolved/all-clear line
    (JS-filled from info.resolved.banner so the date derives in Pacific), and routes to
    officials (911 + ggcity)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    discloses = 'data-i18n="safety.strip.info"' in text
    has_resolved_slot = 'id="banner-resolved"' in text
    routes = "tel:911" in text and "ggcity.org/emergency" in text
    ok = discloses and has_resolved_slot and routes
    return {"passed": ok,
            "details": f"discloses={discloses} resolved_slot={has_resolved_slot} routes={routes}"}


def test_about_drops_disclaimer_and_official_routing_keeps_ai():
    """The About sub-tab no longer repeats the global disclaimer paragraph or the official-
    routing prose (both now carried once by the banner), but KEEPS the persistent AI-assistance
    disclosure (its single allowed in-content home)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    # 6-tab redesign (2026-06-02): panel ids are built dynamically, so anchor on the
    # renderInfoTab `var about =` block instead of the removed literal id / "// end about
    # panel" marker.
    i = text.find("var about =")
    j = text.find("var bodies =", i) if i >= 0 else -1
    region = text[i:j] if (i >= 0 and j > i) else ""
    no_disclaimer = "info.method.disclaimer" not in region
    no_official_routing = "info.about.official" not in region
    keeps_ai = "disclosure.ai" in region
    ok = bool(region) and no_disclaimer and no_official_routing and keeps_ai
    return {"passed": ok,
            "details": f"no_disclaimer={no_disclaimer} no_official={no_official_routing} keeps_ai={keeps_ai}"}
