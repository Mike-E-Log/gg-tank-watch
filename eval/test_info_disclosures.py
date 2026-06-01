"""Guards for the Info-tab disclosures (Resources resolved-note) — user follow-up 2026-05-31:
keep them minimal but still routing to officials and disclosing the historical/resolved state,
without over-claiming authority."""
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"
STATUS = REPO_ROOT / "status.json"

FORBIDDEN = ["official source", "verified", "government"]


def _en_string(key):
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"' + re.escape(key) + r'":\s*\{\s*en:\s*"([^"]*)"', text)
    return m.group(1) if m else ""


def test_resolved_note_concise_routes_and_discloses():
    """The Resources resolved-note must be CONCISE (<=180 chars), show the resolution date
    ({date}), mark the shelters/schools below as historical, route to officials, and avoid
    authority-claiming language. Minimization requirement made testable via the length cap."""
    val = _en_string("info.resolved.banner")
    concise = 0 < len(val) <= 180
    shows_date = "{date}" in val
    historical = "historical" in val.lower()
    routes = "ggcity.org/emergency" in val
    no_overclaim = not any(b in val.lower() for b in FORBIDDEN)
    ok = concise and shows_date and historical and routes and no_overclaim
    return {"passed": ok,
            "details": f"len={len(val)} concise={concise} date={shows_date} historical={historical} "
                       f"routes={routes} no_overclaim={no_overclaim}"}


def test_situation_headline_concise_and_resolved():
    """Archive pivot: status.json incident.status_headline is a MINIMAL resolved line —
    concise (<=220), conveys the resolved/lifted state, and carries NO post-26th editorial
    synthesis (cleanup/lawsuits/investigation/monitoring/removal). The 'Current situation'
    box is being removed; the field stays honest and frozen."""
    d = json.loads(STATUS.read_text(encoding="utf-8"))
    h = (d.get("incident", {}).get("status_headline") or "")
    low = h.lower()
    concise = 0 < len(h) <= 220
    conveys_resolved = "resolved" in low or "lifted" in low
    no_editorial = not any(w in low for w in ["cleanup", "lawsuit", "investigation", "monitoring", "removal"])
    ok = concise and conveys_resolved and no_editorial
    return {"passed": ok,
            "details": f"len={len(h)} concise={concise} resolved={conveys_resolved} no_editorial={no_editorial}"}


def test_about_panel_organized_into_sections():
    """The Info > About panel must be organized into consistent info-section blocks (like the
    Status/Resources panels) and SURFACE the responsible-AI methodology + official routing +
    conduct code, rather than burying methodology in a collapsed <details>. Guards that the
    reorg uses the structured About/method strings (user follow-up 2026-05-31)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find('id="info-subpanel-about"')
    j = text.find("// end about panel", i) if i >= 0 else -1
    region = text[i:j] if (i >= 0 and j > i) else ""
    checks = {
        "who_section": "info.about.title" in region,
        "methodology_section": "info.method.title" in region,
        "ai_disclosure_surfaced": "disclosure.ai" in region,
        "official_routing": "info.about.official" in region,
        "terms_link": "info.about.termslink" in region,
    }
    ok = all(checks.values())
    return {"passed": ok, "details": str(checks)}
