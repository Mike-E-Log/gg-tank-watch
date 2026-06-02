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
    # i18n values use either double or single quotes (e.g. roads.defer / shelters.cta embed
    # double-quoted <a href="..."> so they are single-quoted). Match the opening quote and
    # capture up to its matching close.
    m = re.search(r'"' + re.escape(key) + r'":\s*\{\s*en:\s*(["\'])(.*?)\1', text)
    return m.group(2) if m else ""


def test_resolved_note_concise_routes_and_discloses():
    """The Resources resolved-note must be CONCISE (<=180 chars), show the resolution date
    ({date}), mark the shelters/schools below as historical, route to officials, and avoid
    authority-claiming language. Minimization requirement made testable via the length cap."""
    val = _en_string("info.resolved.banner")
    concise = 0 < len(val) <= 180
    shows_date = "{date}" in val
    historical = "historical" in val.lower()
    no_overclaim = not any(b in val.lower() for b in FORBIDDEN)
    no_live_demo = "live demonstration" not in val.lower()
    # One-banner pivot (2026-06-01): routing (911/ggcity) lives once in the consolidated
    # banner's own route line (guarded by test_one_banner), so the resolved line no longer
    # repeats it. This guard now checks the resolved line is concise, dated, and historical.
    ok = concise and shows_date and historical and no_overclaim and no_live_demo
    return {"passed": ok,
            "details": f"len={len(val)} concise={concise} date={shows_date} historical={historical} "
                       f"no_overclaim={no_overclaim} no_live_demo={no_live_demo}"}


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
        # official routing dropped from About — now carried once by the consolidated banner
        "terms_link": "info.about.termslink" in region,
    }
    ok = all(checks.values())
    return {"passed": ok, "details": str(checks)}


def test_method_pipeline_past_tense():
    """T10: the data-pipeline description reads in PAST tense (the incident is resolved and
    polling has been frozen since Batch 1). 'was updated' / 'was cross-referenced', not present."""
    val = _en_string("info.method.pipeline")
    low = val.lower()
    past = "was updated" in low or "was cross-referenced" in low
    not_present = "status updated every" not in low
    return {"passed": past and not_present,
            "details": f"past_tense={past} no_present_tense={not_present}"}


def test_sources_checked_uses_absolute_date():
    """T10 (deferred fix): the 'sources checked' age renders an ABSOLUTE date (fmtAbsDateOnly),
    not a drifting relativeTime 'N days ago' — a frozen archive must not age its own provenance."""
    text = DASHBOARD.read_text(encoding="utf-8")
    uses_abs = "fmtAbsDateOnly(s.fetched_iso)" in text
    no_relative = "relativeTime(s.fetched_iso)" not in text
    return {"passed": uses_abs and no_relative,
            "details": f"uses_fmtAbsDateOnly={uses_abs} no_relativeTime={no_relative}"}


def test_tank_facts_past_tense():
    """T10: tank-state labels read past tense (the crack relieved pressure / temp stabilized
    DURING the resolved incident), not as an ongoing process."""
    crack = _en_string("info.tankCrackY").lower()
    temp = _en_string("info.tankTempV").lower()
    ok = ("relieved" in crack and "relieving" not in crack
          and "stabilized" in temp and "stabilizing" not in temp)
    return {"passed": ok, "details": f"crack={crack!r} temp={temp!r}"}


def test_shelters_cta_no_live_framing():
    """T10: the shelters CTA still routes to officials but must NOT call the list 'Live' — it is
    a historical snapshot from the resolved incident."""
    val = _en_string("info.shelters.cta")
    routes = "ggcity.org/emergency" in val
    no_live = "live list" not in val.lower()
    return {"passed": routes and no_live, "details": f"routes={routes} no_live_list={no_live}"}


def test_info_routing_strings_past_tense():
    """T10: the remaining Info routing strings drop active-emergency present tense
    (liveList 'Live list' -> records; roads.defer 'are closed' -> 'were closed')."""
    live_list = _en_string("info.liveList").lower()
    roads = _en_string("info.roads.defer").lower()
    ok = "live list" not in live_list and "are closed" not in roads
    return {"passed": ok,
            "details": f"liveList_has_'live list'={'live list' in live_list} roads_has_'are closed'={'are closed' in roads}"}
