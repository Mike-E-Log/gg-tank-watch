"""Guards for the Info-tab disclosures (Resources resolved-note) — user follow-up 2026-05-31:
keep them minimal but still routing to officials and disclosing the historical/resolved state,
without over-claiming authority."""
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"
STATUS = REPO_ROOT / "public" / "status.json"

FORBIDDEN = ["official source", "verified", "government"]


def _en_string(key):
    text = DASHBOARD.read_text(encoding="utf-8")
    # i18n values use either double or single quotes (e.g. roads.defer / shelters.cta embed
    # double-quoted <a href="..."> so they are single-quoted). Match the opening quote and
    # capture up to its matching close.
    m = re.search(r'"' + re.escape(key) + r'":\s*\{\s*en:\s*(["\'])(.*?)\1', text)
    return m.group(2) if m else ""


def test_resolved_note_concise_routes_and_discloses():
    """The resolved banner line must be CONCISE (<=180 chars), show the resolution date
    ({date}), and avoid authority-claiming language. The historical/archive framing is carried
    PERSISTENTLY by the topbar masthead (archive.label + ARCHIVE pill, on every tab; guarded by
    test_topbar_archive_pill / test_freshness_ui), so the resolved line no longer repeats it —
    "Historical archive." was removed from the banner (user follow-up 2026-06-02). Routing
    (911/ggcity) lives once in the consolidated banner's own route line (test_one_banner).
    Minimization requirement made testable via the length cap."""
    val = _en_string("info.resolved.banner")
    concise = 0 < len(val) <= 180
    shows_date = "{date}" in val
    # No longer repeats the archive framing the topbar already carries on every tab...
    no_redundant_archive = "historical archive" not in val.lower()
    # ...but that framing must still be disclosed somewhere persistent — the topbar label.
    historical_in_topbar = "historical archive" in _en_string("archive.label").lower()
    no_overclaim = not any(b in val.lower() for b in FORBIDDEN)
    no_live_demo = "live demonstration" not in val.lower()
    ok = (concise and shows_date and no_redundant_archive and historical_in_topbar
          and no_overclaim and no_live_demo)
    return {"passed": ok,
            "details": f"len={len(val)} concise={concise} date={shows_date} "
                       f"no_redundant_archive={no_redundant_archive} historical_in_topbar={historical_in_topbar} "
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


def test_about_panel_lean_keeps_disclosure_and_a11y():
    """About surfaces the binding AI-assistance disclosure + a short "Why this was made" section
    (info.about.whyH/why, added in-app 2026-06-03 per user) + an Accessibility link + the Sources
    fold. The earlier METHODOLOGY narrative (the step-by-step pipeline) stays in the README — the
    legacy in-app keys info.about.title/body + info.method.title/pipeline must stay gone; the new
    Why section deliberately uses DISTINCT keys (info.about.why*) so those retired keys do not
    return. Anchors on the renderInfoTab `var about =` block, since panel ids are built dynamically.

    The Terms link was DROPPED from About 2026-06-02 (user): it duplicated the persistent
    safety strip's Terms link (safety.strip.terms), which carries it on every tab — so Terms
    stays reachable site-wide, just not twice. The Accessibility link is KEPT because the strip
    has no Accessibility link, so About is its only entry point.

    The past-tense integrity of the migrated pipeline text is re-guarded on the README
    (eval/test_readme_archive_count.py::test_readme_methodology_past_tense)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find("var about =")
    j = text.find("var bodies =", i) if i >= 0 else -1
    region = text[i:j] if (i >= 0 and j > i) else ""
    checks = {
        "ai_disclosure_surfaced": "disclosure.ai" in region,
        "why_section": "info.about.whyH" in region and "info.about.why" in region,
        "a11y_link": "info.about.a11ylink" in region,
        "terms_dropped_from_about": "info.about.termslink" not in region,
        "terms_reachable_in_strip": "safety.strip.terms" in text,
        "sources_fold": "info.sourcesH" in region,
        "legacy_about_narrative_out": "info.about.title" not in text and "info.about.body" not in text,
        "methodology_moved_out": "info.method.title" not in text and "info.method.pipeline" not in text,
    }
    ok = bool(region) and all(checks.values())
    return {"passed": ok, "details": str(checks)}


def test_sources_checked_date_omitted():
    """J (archive honesty, 2026-06-02): the per-source 'checked {date}' suffix is REMOVED from
    the sources fold. fetched_iso re-stamps on every refresh, so a post-resolution date (e.g.
    Jun 3) on a May-26 frozen archive reads like ongoing monitoring. The list shows title/URL
    only; fetched_iso stays IN status.json (data-shape guard test_provenance.py::
    test_sources_checked_have_fetched_time) but is no longer surfaced as a freshness date.
    Supersedes the old T10 'render an absolute date' guard — the honest archive answer is no date."""
    text = DASHBOARD.read_text(encoding="utf-8")
    date_gone = "fmtAbsDateOnly(s.fetched_iso)" not in text
    no_relative = "relativeTime(s.fetched_iso)" not in text
    return {"passed": date_gone and no_relative,
            "details": f"per_source_date_removed={date_gone} no_relativeTime={no_relative}"}


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
