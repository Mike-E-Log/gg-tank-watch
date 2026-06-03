"""Guard: Info-tab archive structure + visual clarity (2026-06-02).

The Info tab is a frozen historical archive, presented as four single-row sub-tabs:
Summary | Officials | Resources | About. The six-panel build (2026-06-02, PR #108)
was consolidated to four so the bar fits one row at 375px without horizontal scroll
(max signal / min noise): Shelters, Schools, and Recovery merged into one Resources
panel as sections, while Officials stays pure (the 3 official channels) to keep the
conduit's route-to-officials action prominent. These guards lock that structure plus
the two visual-refinement fixes — the single-row sub-tab bar (scrollable-bar deviation
reversed) and the distinct descriptor band on every panel.

Anchors on full markup tags / i18n key-value pairs, NOT bare class names (class names
also appear in the inline <style>; see learning eval-find-hits-css-before-html). Sub-tab
chrome is generated from one {id,label,descriptor} array, so the honest per-tab anchors
are the array ids and the i18n label/descriptor keys, not the dynamically-built onclick.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

SUBTABS = ["summary", "officials", "resources", "about"]
MERGED = ["shelters", "schools", "recovery"]  # now sections inside Resources, not tabs


def test_four_subtabs_present():
    """The four sub-tabs are wired (each id in the TABS array, each label i18n key
    defined, tablist + onclick emitted) and the old standalone Shelters/Schools/Recovery
    tabs are gone — merged into Resources."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing_id = [s for s in SUBTABS if f'id: "{s}"' not in text]
    missing_label = [s for s in SUBTABS if f'"info.subtab.{s}"' not in text]
    wired = "switchInfoSubtab(" in text and 'role="tablist"' in text
    merged = all(f'id: "{s}"' not in text for s in MERGED)
    ok = not missing_id and not missing_label and wired and merged
    return {"passed": ok,
            "details": "4 sub-tabs (Summary|Officials|Resources|About); Shelters/Schools/Recovery merged"
            if ok else f"missing_id={missing_id} missing_label={missing_label} wired={wired} merged={merged}"}


def test_each_panel_has_descriptor():
    """Each of the four panels leads with a one-line purpose descriptor (info.desc.*)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing = [s for s in SUBTABS if f'"info.desc.{s}"' not in text]
    ok = not missing
    return {"passed": ok, "details": "4 per-panel descriptors present (info.desc.*)"
            if ok else f"missing descriptor keys: {missing}"}


def test_descriptor_is_distinct_block():
    """Visual refinement #2: the per-panel descriptor (.info-desc) reads as a distinct
    inset band (mirrors .resolved-note) — left border + tinted background + radius — not
    flat body copy."""
    text = DASHBOARD.read_text(encoding="utf-8")
    di = text.find(".info-desc {")
    block = text[di:di + 280] if di != -1 else ""
    ok = bool(block) and "border-left" in block and "background:" in block and "border-radius" in block
    return {"passed": ok,
            "details": ".info-desc styled as distinct inset band (border-left + background + radius)"
            if ok else "descriptor still flat — needs border-left + background + border-radius"}


def test_subtabs_single_row_no_hscroll():
    """Visual refinement #1: the sub-tab bar fits on one row without horizontal scroll —
    the scrollable-bar deviation (overflow-x:auto / flex-wrap:nowrap / scroll-snap) is
    reversed, and each tab flexes to fill the row equally (flex:1 1)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    bi = text.find(".info-subtabs {")
    bar = text[bi:bi + 280] if bi != -1 else ""
    ti = text.find(".info-subtab {")
    tab = text[ti:ti + 320] if ti != -1 else ""
    bar_ok = (bool(bar) and "overflow-x: auto" not in bar
              and "flex-wrap: nowrap" not in bar and "scroll-snap-type" not in bar)
    tab_ok = bool(tab) and "flex: 1 1" in tab
    ok = bar_ok and tab_ok
    return {"passed": ok,
            "details": "sub-tab bar single-row (no overflow-x scroll; tabs flex:1 1)"
            if ok else f"bar_ok={bar_ok} tab_ok={tab_ok}"}


def test_officials_panel_has_three_links():
    """Officials panel routes residents to the 3 official channels (city, Zonehaven,
    Everbridge alerts) — the conduit's primary route-to-officials action; kept pure."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = ('"info.official.city"' in text and '"info.official.zonehaven"' in text
          and '"info.official.alert"' in text
          and "ggcity.org/emergency" in text)
    return {"passed": ok, "details": "Officials panel renders the 3 official channels"
            if ok else "an official channel is missing"}


def test_resources_panel_merges_three():
    """Resources is one sub-tab merging the three logistics lists — Shelters
    (config.map.shelters), Schools (snap.schools_closed), and Recovery
    (config.community_resources) — as sections. The fill-targets stay (ids unchanged so
    updateInfoData/renderInfoConfigData keep working) and the section headings reuse the
    Shelters/Schools/Recovery labels."""
    text = DASHBOARD.read_text(encoding="utf-8")
    tab = ('id: "resources"' in text and '"info.subtab.resources"' in text
           and '"info.desc.resources"' in text)
    targets = ('id="info-shelters-list"' in text and 'id="info-schools-grid"' in text
               and 'id="info-recovery-list"' in text)
    headings = ('t("info.subtab.shelters")' in text and 't("info.subtab.schools")' in text
                and 't("info.subtab.recovery")' in text)
    ok = tab and targets and headings
    return {"passed": ok,
            "details": "Resources tab merges Shelters+Schools+Recovery as sections (fill-targets intact)"
            if ok else f"tab={tab} targets={targets} headings={headings}"}


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
    """About keeps the binding AI disclosure (12px gold) + the sources fold; the fold is now
    titled 'Sources' (J, archive honesty 2026-06-02 — 'Sources checked' gestured at a freshness
    claim once the per-source dates were dropped). The methodology/who-made-it narrative moved to
    the README, and the old conduct link stays gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    sources_fold = '"info.sourcesH": { en: "Sources" }' in text
    conduct_removed = '"info.about.conductlink"' not in text
    disclosure_class = 'class="info-ai-disclosure"' in text
    css_i = text.find(".info-ai-disclosure {")
    css_block = text[css_i:css_i + 240] if css_i != -1 else ""
    disclosure_styled = "12px" in css_block and "--sa-gold" in css_block
    ok = sources_fold and conduct_removed and disclosure_class and disclosure_styled
    return {"passed": ok,
            "details": "About keeps 'Sources' fold + AI disclosure 12px gold"
            if ok else f"fold_titled={sources_fold} conduct_removed={conduct_removed} cls={disclosure_class} styled={disclosure_styled}"}


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


def test_news_chipbar_matches_subtab_bar():
    """A: the News filter-chip bar uses the same vertical padding as the Info sub-tab bar
    (8px 12px 0) so toggling Info<->News does not jump the bar height."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ci = text.find(".news-filter-chips {")
    block = text[ci:ci + 220] if ci != -1 else ""
    ok = bool(block) and "padding: 8px 12px 0" in block
    return {"passed": ok,
            "details": "news chip-bar padding matches sub-tab bar (8px 12px 0)"
            if ok else "news chip-bar padding still differs from .info-subtabs"}


def test_summary_zone_value_full_scale():
    """B: the Summary zone value reads at the same 13px as its sibling kv-values — the 11px
    .info-fine downscale is dropped so the Summary type scale is uniform."""
    text = DASHBOARD.read_text(encoding="utf-8")
    has_fine = 'info-fine">\' + t("info.zonePeak")' in text
    bound_plain = 'info-kv-val">\' + t("info.zonePeak")' in text
    ok = (not has_fine) and bound_plain
    return {"passed": ok,
            "details": "zone value at full 13px scale (info-fine dropped)"
            if ok else f"has_fine={has_fine} bound_plain={bound_plain}"}


def test_info_row_has_breathing_room():
    """D/E: the unified .info-row (Officials + Shelters) has list breathing room — ~9px
    vertical padding and a hairline separator (last-child none) — not the old 3px cramp."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ri = text.find(".info-row {")
    block = text[ri:ri + 220] if ri != -1 else ""
    padded = bool(block) and ("padding: 9px 0" in block or "padding: 10px 0" in block)
    bordered = "border-bottom: 1px solid var(--sa-border)" in block
    last_none = ".info-row:last-child { border-bottom: none; }" in text
    ok = padded and bordered and last_none
    return {"passed": ok,
            "details": "info-row ~9px padding + hairline + last-child none"
            if ok else f"padded={padded} bordered={bordered} last_none={last_none}"}


def test_summary_archive_facts_present():
    """C: the Summary surfaces five sourced archive facts (substance/facility/tank/window/
    outcome) as STATIC copy — neutral labels, NO 'verified' authority chrome, and decoupled
    from the cleared resolved snapshot (no live id binding)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    val_keys = ["info.fact.substanceV", "info.fact.facilityV", "info.fact.tankV",
                "info.fact.windowV", "info.fact.outcomeV"]
    label_keys = ["info.fact.substance", "info.fact.facility", "info.fact.tank",
                  "info.fact.window", "info.fact.outcome"]
    missing = [k for k in (val_keys + label_keys) if f'"{k}"' not in text]
    bound = all(f't("{k}")' in text for k in val_keys)
    no_live_id = ('id="info-substance-val"' not in text
                  and 'id="info-facility-val"' not in text)
    ok = not missing and bound and no_live_id
    return {"passed": ok,
            "details": "Summary shows 5 sourced static archive facts (neutral labels, decoupled)"
            if ok else f"missing_keys={missing} bound={bound} no_live_id={no_live_id}"}


def test_shelter_row_dedicated_layout():
    """F: shelter rows use a dedicated flex layout (.shelter-row) with name+city in a flex
    text column and 'Directions' pinned top (align-items: flex-start), so a long shelter name
    wraps without pushing the action out of alignment. Google Maps directions href preserved."""
    text = DASHBOARD.read_text(encoding="utf-8")
    si = text.find(".shelter-row {")
    css = text[si:si + 260] if si != -1 else ""
    css_ok = bool(css) and "display: flex" in css and "align-items: flex-start" in css
    markup_ok = ('class="shelter-row"' in text and 'class="shelter-name"' in text
                 and 'class="shelter-go"' in text)
    href_ok = "maps/dir/?api=1&destination=" in text
    ok = css_ok and markup_ok and href_ok
    return {"passed": ok,
            "details": "shelter rows use dedicated flex layout (text column + pinned action)"
            if ok else f"css_ok={css_ok} markup_ok={markup_ok} href_ok={href_ok}"}


def test_about_desc_no_orphan():
    """G: the About descriptor is shortened so 'it.' no longer orphans onto its own line."""
    text = DASHBOARD.read_text(encoding="utf-8")
    new_ok = '"info.desc.about": { en: "How this archive was made, and its sources." }' in text
    old_gone = "and the sources behind it." not in text
    ok = new_ok and old_gone
    return {"passed": ok, "details": "About descriptor shortened (no orphan)"
            if ok else f"new_present={new_ok} old_gone={old_gone}"}


def test_about_body_has_gutter():
    """H: the About body (disclosure + terms + sources fold) is wrapped in a gutter container
    (.about-body, padding 0 14px) so its text aligns with the inset descriptor band rather than
    running to the panel edges."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ci = text.find(".about-body {")
    css = text[ci:ci + 120] if ci != -1 else ""
    css_ok = bool(css) and "padding: 0 14px" in css
    markup_ok = 'class="about-body"' in text
    ok = css_ok and markup_ok
    return {"passed": ok, "details": "About body wrapped in .about-body gutter (0 14px)"
            if ok else f"css_ok={css_ok} markup_ok={markup_ok}"}


def test_disclosure_split_two_lines():
    """I: the AI disclosure renders as two lines — (1) compiled-with-AI/checked-by-a-person,
    (2) routing copy to officials/911 (NOT an 'Always confirm' imperative) — both in
    .info-ai-disclosure (12px gold preserved)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    two_keys = '"disclosure.ai"' in text and '"disclosure.aiRoute"' in text
    line1 = 'info-ai-disclosure">\' + t("disclosure.ai")' in text
    line2 = 'info-ai-disclosure">\' + t("disclosure.aiRoute")' in text
    no_imperative = "Always confirm life-safety" not in text
    ci = text.find(".info-ai-disclosure {")
    css = text[ci:ci + 200] if ci != -1 else ""
    styled = "12px" in css and "--sa-gold" in css
    ok = two_keys and line1 and line2 and no_imperative and styled
    return {"passed": ok,
            "details": "AI disclosure split into two gold lines; routing copy not imperative"
            if ok else f"two_keys={two_keys} line1={line1} line2={line2} no_imperative={no_imperative} styled={styled}"}


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
