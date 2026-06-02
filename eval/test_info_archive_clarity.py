"""Guard: Info-tab archive-clarity redesign (2026-06-01, scope B).

The Info tab is a frozen historical archive. These guards lock the design-reviewed plan:
a historical disclaimer on the default "What happened" (Status) panel, Official Sources
routed BEFORE the collapsed historical-resources fold, the emergency 911 line surfaced as
its own line, and the About methodology/sources dedup. Order assertions anchor on full
markup tags, not bare class names (class names also appear in the inline <style>; see
learning eval-find-hits-css-before-html).
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_status_panel_has_historical_disclaimer():
    text = DASHBOARD.read_text(encoding="utf-8")
    i_status = text.find('id="info-subpanel-status"')
    i_note = text.find('id="status-resolved-note"')
    i_resources = text.find('id="info-subpanel-resources"')
    in_status_panel = -1 < i_status < i_note < i_resources
    has_string = '"info.resolved.status":' in text
    ok = in_status_panel and has_string
    return {"passed": ok,
            "details": "status-resolved-note inside the Status panel + info.resolved.status string"
            if ok else f"in_panel={in_status_panel} string={has_string}"}


def test_official_sources_before_historical_fold():
    text = DASHBOARD.read_text(encoding="utf-8")
    i_official = text.find('data-i18n="info.group.official"')
    i_fold = text.find('class="info-fold"')
    ok = -1 < i_official < i_fold
    return {"passed": ok,
            "details": "Official Sources render precedes the historical <details class=info-fold>"
            if ok else f"official={i_official} fold={i_fold}"}


def test_emergency_line_surfaced():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = "In an emergency, call 911.</strong>" in text
    return {"passed": ok,
            "details": "emergency 911 line surfaced as its own bold line"
            if ok else "911 not surfaced as its own <strong> line"}


def test_what_happened_shows_sourced_peak_facts():
    """The 'What happened' panel surfaces the sourced peak facts (timeline.json: ~100F peak
    temp, ~50,000 evacuated across ~9 sq mi) instead of the resolved snapshot's cleared
    0/-- fields. Labels are Peak/zone (honest now that real values exist); values are static
    so updateInfoData can't overwrite them with the cleared current-state snap."""
    text = DASHBOARD.read_text(encoding="utf-8")
    labels = ('"info.tankTemp": { en: "Peak tank temperature" }' in text
              and '"info.evacResidents": { en: "Peak evacuation" }' in text
              and '"info.evacBoundary": { en: "Evacuation zone (peak)" }' in text)
    values = ('"info.tankTempArchive": { en: "~100' in text
              and '"info.peakEvac": { en: "~50,000' in text
              and '"info.zonePeak": { en:' in text and "9 sq mi" in text)
    bound = ('t("info.peakEvac")' in text and 't("info.tankTempArchive")' in text
             and 't("info.zonePeak")' in text)
    # the cleared current-state bindings must be gone so they can't overwrite the static facts
    decoupled = 'id="info-residents-val"' not in text and 'id="info-boundary-val"' not in text
    ok = labels and values and bound and decoupled
    return {"passed": ok,
            "details": "What-happened shows sourced peak temp/evac/zone (timeline.json), decoupled from cleared snap"
            if ok else f"labels={labels} values={values} bound={bound} decoupled={decoupled}"}


def test_about_dedup_and_disclosure():
    text = DASHBOARD.read_text(encoding="utf-8")
    sources_retitled = '"info.sourcesH": { en: "Sources checked" }' in text
    conduct_removed = '"info.about.conductlink"' not in text
    disclosure_class = 'class="info-ai-disclosure"' in text
    css_i = text.find(".info-ai-disclosure {")
    css_block = text[css_i:css_i + 240] if css_i != -1 else ""
    disclosure_styled = "12px" in css_block and "--sa-gold" in css_block
    ok = sources_retitled and conduct_removed and disclosure_class and disclosure_styled
    return {"passed": ok,
            "details": "fold='Sources checked', conductlink gone, AI disclosure 12px gold"
            if ok else f"retitled={sources_retitled} conduct_removed={conduct_removed} cls={disclosure_class} styled={disclosure_styled}"}
