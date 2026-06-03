"""Guard: Info-tab 6-sub-tab redesign (2026-06-02).

The Info tab is a frozen historical archive, rebuilt into six individually-navigable,
horizontally-scrollable sub-tabs: Summary | Officials | Shelters | Schools | Recovery |
About. These guards lock the design-reviewed structure: all six sub-tabs wired with a
one-line descriptor each, the three official channels in the Officials panel, the
Recovery panel fed by community_resources, the sourced peak facts on Summary, the AI
disclosure kept in About (binding honesty principle), the old parallel-Resources CSS
retired, and no inline font-size in the Info render path.

Anchors on full markup tags / i18n key-value pairs, NOT bare class names (class names
also appear in the inline <style>; see learning eval-find-hits-css-before-html). Sub-tab
chrome is generated from one {id,label,descriptor} array, so the honest per-tab anchors
are the array ids and the i18n label/descriptor keys, not the dynamically-built onclick.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

SUBTABS = ["summary", "officials", "shelters", "schools", "recovery", "about"]


def test_six_subtabs_present():
    """All six sub-tabs are wired: each id in the TABS array, each label i18n key
    defined, and the tablist + onclick handler emitted."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing_id = [s for s in SUBTABS if f'id: "{s}"' not in text]
    missing_label = [s for s in SUBTABS if f'"info.subtab.{s}"' not in text]
    wired = "switchInfoSubtab(" in text and 'role="tablist"' in text
    ok = not missing_id and not missing_label and wired
    return {"passed": ok,
            "details": "6 sub-tabs in TABS array + label keys + tablist/onclick wired"
            if ok else f"missing_id={missing_id} missing_label={missing_label} wired={wired}"}


def test_each_panel_has_descriptor():
    """Each of the six panels leads with a one-line purpose descriptor (info.desc.*)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing = [s for s in SUBTABS if f'"info.desc.{s}"' not in text]
    ok = not missing
    return {"passed": ok, "details": "6 per-panel descriptors present (info.desc.*)"
            if ok else f"missing descriptor keys: {missing}"}


def test_officials_panel_has_three_links():
    """Officials panel routes residents to the 3 official channels (city, Zonehaven,
    Everbridge alerts) — the conduit's primary route-to-officials action."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = ('"info.official.city"' in text and '"info.official.zonehaven"' in text
          and '"info.official.alert"' in text
          and "ggcity.org/emergency" in text)
    return {"passed": ok, "details": "Officials panel renders the 3 official channels"
            if ok else "an official channel is missing"}


def test_recovery_panel_present():
    """Recovery is its own sub-tab, fed by config.community_resources (FEMA aid,
    DA tip line, price-gouging hotline) with its own descriptor."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = 'id: "recovery"' in text and '"info.desc.recovery"' in text
    return {"passed": ok, "details": "Recovery tab + descriptor present"
            if ok else "Recovery tab missing"}


def test_what_happened_shows_sourced_peak_facts():
    """The Summary panel surfaces the sourced peak facts (timeline.json: ~100F peak
    temp, ~50,000 evacuated across ~9 sq mi) as static archive copy, decoupled from the
    resolved snapshot's cleared current-state fields so updateInfoData can't overwrite
    them with a misleading 0/--."""
    text = DASHBOARD.read_text(encoding="utf-8")
    labels = ('"info.tankTemp": { en: "Peak tank temperature" }' in text
              and '"info.evacResidents": { en: "Peak evacuation" }' in text
              and '"info.evacBoundary": { en: "Evacuation zone (peak)" }' in text)
    values = ('"info.tankTempArchive": { en: "~100' in text
              and '"info.peakEvac": { en: "~50,000' in text
              and '"info.zonePeak": { en:' in text and "9 sq mi" in text)
    bound = ('t("info.peakEvac")' in text and 't("info.tankTempArchive")' in text
             and 't("info.zonePeak")' in text)
    # the cleared current-state bindings must stay gone so they can't overwrite the facts
    decoupled = 'id="info-residents-val"' not in text and 'id="info-boundary-val"' not in text
    ok = labels and values and bound and decoupled
    return {"passed": ok,
            "details": "Summary shows sourced peak temp/evac/zone (timeline.json), decoupled from cleared snap"
            if ok else f"labels={labels} values={values} bound={bound} decoupled={decoupled}"}


def test_about_disclosure_and_sources():
    """About keeps the binding AI disclosure (12px gold) + the 'Sources checked' fold;
    the methodology/who-made-it narrative moved to the README, and the old conduct link
    stays gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    sources_retitled = '"info.sourcesH": { en: "Sources checked" }' in text
    conduct_removed = '"info.about.conductlink"' not in text
    disclosure_class = 'class="info-ai-disclosure"' in text
    css_i = text.find(".info-ai-disclosure {")
    css_block = text[css_i:css_i + 240] if css_i != -1 else ""
    disclosure_styled = "12px" in css_block and "--sa-gold" in css_block
    ok = sources_retitled and conduct_removed and disclosure_class and disclosure_styled
    return {"passed": ok,
            "details": "About keeps 'Sources checked' + AI disclosure 12px gold"
            if ok else f"retitled={sources_retitled} conduct_removed={conduct_removed} cls={disclosure_class} styled={disclosure_styled}"}


def test_retired_classes_gone_markup_and_css():
    """The old parallel Resources system (separate from the unified .info-section
    primitives) is fully retired — markup AND CSS."""
    text = DASHBOARD.read_text(encoding="utf-8")
    retired = [".resources-section", ".community-resource-card", ".shelters-grid",
               ".official-link", 'class="resources-section"',
               'class="community-resource-card"']
    present = [r for r in retired if r in text]
    ok = not present
    return {"passed": ok, "details": "old parallel Resources classes retired (markup + CSS)"
            if ok else f"still present: {present}"}


def test_no_inline_font_size_in_info_panels():
    """No inline font-size in the Info render path (renderInfoTab through the helpers
    that precede renderPrintContent). renderPrintContent legitimately uses inline styles
    for print and is OUTSIDE this region."""
    text = DASHBOARD.read_text(encoding="utf-8")
    start = text.find("function renderInfoTab()")
    end = text.find("function renderPrintContent")
    region = text[start:end] if (start != -1 and end != -1 and end > start) else ""
    ok = bool(region) and ("font-size:" not in region) and ('style="font-size' not in region)
    return {"passed": ok,
            "details": "no inline font-size between renderInfoTab and renderPrintContent"
            if ok else "inline font-size found in Info render region"}


def test_dead_shelter_renderer_removed():
    """Regression guard (T1): the dead renderInfoShelters() + #info-shelter-list +
    orphaned .info-shelter-* CSS stay removed."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = ("function renderInfoShelters" not in text
          and 'id="info-shelter-list"' not in text
          and ".info-shelter-row" not in text)
    return {"passed": ok,
            "details": "renderInfoShelters + #info-shelter-list + .info-shelter-* removed"
            if ok else "dead shelter renderer still present"}
