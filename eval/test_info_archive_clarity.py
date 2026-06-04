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
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"
STATUS = REPO_ROOT / "status.json"

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
    """About keeps the binding AI disclosure + a static Sources section, titled 'Sources'
    (J, archive honesty 2026-06-02). The disclosure now renders at body near-black --sa-text
    (NOT gold — user 2026-06-02: bring it in line with the other sub-tabs' body text); the
    binding-honesty property holds via the text + the persistent safety strip, and the disclosure
    renders at the panel-closing bottom line of About (moved there 2026-06-03), not the first line.
    The Sources section is static (always visible — the lone collapsible fold was removed
    2026-06-03) with a one-line caption stating what the list is (info.sources.caption). The
    methodology narrative stays in the README; the conduct link stays gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    sources_section = '"info.sourcesH": { en: "Sources" }' in text
    sources_caption = '"info.sources.caption"' in text
    conduct_removed = '"info.about.conductlink"' not in text
    disclosure_class = 'class="info-ai-disclosure"' in text
    css_i = text.find(".info-ai-disclosure {")
    css_block = text[css_i:css_i + 240] if css_i != -1 else ""
    # body near-black, no gold accent
    disclosure_styled = "13px" in css_block and "var(--sa-text)" in css_block and "--sa-gold" not in css_block
    ok = (sources_section and sources_caption and conduct_removed
          and disclosure_class and disclosure_styled)
    return {"passed": ok,
            "details": "About: 'Sources' section + caption + AI disclosure 12px body --sa-text (not gold)"
            if ok else (f"section_titled={sources_section} caption={sources_caption} "
                        f"conduct_removed={conduct_removed} cls={disclosure_class} styled={disclosure_styled}")}


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
    val_keys = ["info.fact.substanceV", "info.fact.facilityV",
                "info.fact.windowV", "info.fact.outcomeV"]
    label_keys = ["info.fact.substance", "info.fact.facility",
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


def test_disclosure_single_line_body_color():
    """The AI disclosure is ONE line — compiled-with-AI/checked-by-a-person — in
    .info-ai-disclosure at body near-black --sa-text (user 2026-06-02). The second
    'Current life-safety info…' routing line (disclosure.aiRoute) was REMOVED as a duplicate
    of the persistent safety strip (which carries 911 + ggcity.org/emergency on every tab;
    re-guarded by test_routing_jargon::test_ai_disclosure_routes_concretely). The disclosure
    must not become an imperative ('Always confirm…')."""
    text = DASHBOARD.read_text(encoding="utf-8")
    has_ai = '"disclosure.ai"' in text
    airoute_gone = '"disclosure.aiRoute"' not in text and "disclosure.aiRoute" not in text
    line1 = 'info-ai-disclosure">\' + t("disclosure.ai")' in text
    no_imperative = "Always confirm life-safety" not in text
    ci = text.find(".info-ai-disclosure {")
    css = text[ci:ci + 200] if ci != -1 else ""
    styled = "13px" in css and "var(--sa-text)" in css and "--sa-gold" not in css
    ok = has_ai and airoute_gone and line1 and no_imperative and styled
    return {"passed": ok,
            "details": "AI disclosure: single body-color line; duplicate routing line removed"
            if ok else (f"has_ai={has_ai} airoute_gone={airoute_gone} line1={line1} "
                        f"no_imperative={no_imperative} styled={styled}")}


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


def test_officials_note_removed_and_descriptions_present():
    """Officials (user 2026-06-02): the generic 'No single source should be your only one…'
    note (info.official.note) is REMOVED — boilerplate that didn't fit a frozen, resolved
    archive — and each of the 3 official channels now carries a one-line description of what
    it is for (info.official.cityDesc / zonehavenDesc / alertDesc), rendered in a
    .info-row-desc sub-line (a CLASS, so the no-inline-font-size guard still holds)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    note_removed = "info.official.note" not in text
    desc_keys = all(k in text for k in (
        '"info.official.cityDesc"', '"info.official.zonehavenDesc"', '"info.official.alertDesc"'))
    sub_line_class = ".info-row-desc" in text and "info-row-desc" in text
    ok = note_removed and desc_keys and sub_line_class
    return {"passed": ok,
            "details": "Officials: note removed + 3 per-link descriptions in .info-row-desc"
            if ok else f"note_removed={note_removed} desc_keys={desc_keys} sub_line_class={sub_line_class}"}


def test_resources_descriptor_one_line():
    """Resources (user 2026-06-02): the .info-desc descriptor copy is shortened to fit ONE line
    at 375px (the old 'Evacuation shelters, school closures, and recovery aid from the emergency.'
    wrapped to two). Coarse text backstop (<=50 chars); the real one-line check is the rendered
    screenshot per the acceptance rubric §0."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"info\.desc\.resources":\s*\{\s*en:\s*"([^"]*)"', text)
    val = m.group(1) if m else ""
    ok = 0 < len(val) <= 50
    return {"passed": ok, "details": f"resources descriptor len={len(val)} (<=50) val={val!r}"}


def test_sources_caption_static_and_official_labels():
    """Sources is a STATIC, always-visible section (user 2026-06-03: it was the only collapsible
    element on an otherwise-static site, and provenance should stay visible on a transparency-first
    archive — so the <details>/<summary> fold was removed). The 'Sources' heading reuses the
    .about-why-title group-title treatment (matching the 'Why this was made' heading in the same
    panel); a one-line caption (info.sources.caption) states what the list is; official City/County
    sources are tagged 'Official' (info.sources.official).

    Official-ness is DERIVED FROM THE SOURCE URL host (ggcity.org / ocgov.com) via
    isOfficialSourceUrl() — NOT a status.json `official` flag. The data-refresh pipeline
    regenerates status.json and strips an explicit flag (it did, 2026-06-03: the tags vanished
    after an auto-refresh), but it PRESERVES the source URLs, so URL-derived tagging is
    refresh-proof. The eval counts official sources by URL host (>=2) and asserts the render no
    longer depends on the volatile s.official flag. The tag uses a class (.source-official) so
    the no-inline-font-size guard still holds."""
    text = DASHBOARD.read_text(encoding="utf-8")
    caption_key = '"info.sources.caption"' in text
    # no collapsible fold anywhere; the Sources heading is a static .about-why-title
    sources_static = "<details" not in text and "info-sources-toggle" not in text
    sources_heading = 't("info.sourcesH")' in text
    tag_key = '"info.sources.official"' in text
    derives_from_url = "isOfficialSourceUrl" in text and ".source-official" in text
    # must not key the tag off the refresh-stripped data flag. Match the precise render ternary
    # `s.official ?` (NOT the substring "s.official", which also occurs in the i18n key
    # "info.sources.official").
    no_volatile_flag = "s.official ?" not in text and "s.official?" not in text

    def _official_url(u):
        u = (u or "").lower()
        return "ggcity.org" in u or "ocgov.com" in u

    d = json.loads(STATUS.read_text(encoding="utf-8"))
    n_official = sum(1 for s in d.get("sources_checked", []) if _official_url(s.get("url")))
    ok = (caption_key and sources_static and sources_heading and tag_key and derives_from_url
          and no_volatile_flag and n_official >= 2)
    return {"passed": ok,
            "details": "Sources: static (no fold) + caption + URL-derived Official labels (>=2 official-host sources)"
            if ok else (f"caption={caption_key} static={sources_static} heading={sources_heading} "
                        f"tag_key={tag_key} derives_from_url={derives_from_url} "
                        f"no_volatile_flag={no_volatile_flag} n_official={n_official}")}


def test_no_ghost_lines_background():
    """User 2026-06-02: the .sa-wave-bg decorative background painted a faint horizontal line
    every ~22px (a repeating-linear-gradient 'lined-paper' effect) that read as noisy, erroneous
    ghost lines across every Info sub-tab. That repeating gradient is REMOVED; the only horizontal
    lines kept are the intentional 1px solid item separators (.info-row / .info-kv-row /
    .info-section hairlines). The soft top radial glow may remain."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ci = text.find(".sa-wave-bg {")
    block = text[ci:ci + 320] if ci != -1 else ""
    ghost_gone = bool(block) and "repeating-linear-gradient" not in block
    separators_kept = "1px solid var(--sa-border)" in text
    return {"passed": ghost_gone and separators_kept,
            "details": f"ghost_repeating_gradient_gone={ghost_gone} solid_separators_kept={separators_kept}"}


def test_resources_section_titles_full_labels():
    """User 2026-06-03: the Resources section titles name each section in full —
    SHELTERS / SCHOOL CLOSURES / RECOVERY AID (uppercased by .info-section-title). The
    info.subtab.schools/recovery values were lengthened from "Schools"/"Recovery"; "Shelters"
    was already full. The titles reuse these keys (test_resources_panel_merges_three guards the
    t() calls stay) — this guards the displayed VALUES."""
    text = DASHBOARD.read_text(encoding="utf-8")
    shelters = '"info.subtab.shelters": { en: "Shelters" }' in text
    schools = '"info.subtab.schools": { en: "School closures" }' in text
    recovery = '"info.subtab.recovery": { en: "Recovery aid" }' in text
    ok = shelters and schools and recovery
    return {"passed": ok,
            "details": "Resources titles: Shelters / School closures / Recovery aid"
            if ok else f"shelters={shelters} schools={schools} recovery={recovery}"}


def test_about_why_section_present():
    """User 2026-06-03: About order is Why -> Sources -> Accessibility -> AI disclosure
    (panel-closing line). The binding AI disclosure MOVED from the first line to the very bottom
    (the persistent safety strip carries the always-on honesty; the disclosure stays present +
    legible at 13px, position demoted not size). 'Why this was made' is a .about-why-title heading
    + a short resident-first paragraph; conduit-true (routes to officials, authors no directive).
    New keys (info.about.whyH/why) so the retired info.about.title/body + info.method.* keys stay
    gone (test_about_panel_lean_keeps_disclosure_and_a11y)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    keys = '"info.about.whyH"' in text and '"info.about.why"' in text
    i = text.find("var about =")
    j = text.find("var bodies =", i) if i >= 0 else -1
    region = text[i:j] if (i >= 0 and j > i) else ""
    bound = ('t("info.about.whyH")' in region and 't("info.about.why")' in region
             and 'class="about-why-title"' in region)
    p_why = region.find('t("info.about.whyH")')
    p_src = region.find('t("info.sourcesH")')
    p_a11y = region.find('class="info-a11y-btn"')
    p_disc = region.find('t("disclosure.ai")')
    ordered = -1 < p_why < p_src < p_a11y < p_disc
    m = re.search(r'"info\.about\.why":\s*\{\s*en:\s*"([^"]*)"', text)
    why_body = (m.group(1) if m else "").lower()
    conduit = "officials" in why_body
    ok = keys and bound and ordered and conduit
    return {"passed": ok,
            "details": "About order Why->Sources->Accessibility->disclosure (disclosure last)"
            if ok else f"keys={keys} bound={bound} ordered={ordered} conduit={conduit}"}


def test_about_why_is_bulleted():
    """User 2026-06-03: the 'Why this was made' narrative is a scannable bulleted list, not one
    back-to-back-sentences paragraph. The four sentences become four <li> items (words/punctuation
    unchanged) wrapped in a styled <ul class="about-why-list"> (not a <p>). The load-bearing conduit
    clause ('pointed back to the officials in charge -- it never replaced them or told anyone what to
    do') stays whole inside a single bullet so the Section 230 / no-directive framing is not split.
    .about-why-list carries a bounded padding-left so the list cannot overflow the 320px panel
    (causal-layout guard, matching test_info_subtab_fit's 'assert the property, not the pixels')."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"info\.about\.why":\s*\{\s*en:\s*"([^"]*)"', text)
    why_val = m.group(1) if m else ""
    li_open = why_val.count("<li>")
    four_bullets = li_open == 4 and why_val.count("</li>") == 4
    conduit_whole = "officials in charge &mdash; it never replaced them or told anyone what to do.</li>" in why_val
    i = text.find("var about =")
    j = text.find("var bodies =", i) if i >= 0 else -1
    region = text[i:j] if (i >= 0 and j > i) else ""
    ul_wrapped = '\'<ul class="about-why-list">\' + t("info.about.why") + \'</ul>\'' in region
    no_p_wrap = '\'<p>\' + t("info.about.why")' not in region
    ci = text.find(".about-why-list {")
    css = text[ci:ci + 200] if ci != -1 else ""
    css_ok = bool(css) and "padding-left" in css
    ok = four_bullets and conduit_whole and ul_wrapped and no_p_wrap and css_ok
    return {"passed": ok,
            "details": "About 'Why' renders as a 4-item <ul class=about-why-list>, conduit clause intact"
            if ok else f"four_bullets={four_bullets} conduit_whole={conduit_whole} "
                       f"ul_wrapped={ul_wrapped} no_p_wrap={no_p_wrap} css_ok={css_ok}"}


def test_about_a11y_link_prominent_centered():
    """User 2026-06-03: the Accessibility link is prominent + centered + tappable, not the quiet
    11px footer link. .info-about-footlink centers it (text-align: center); the link itself
    (.info-a11y-btn) is a bordered pill with a >=44px tap target. The markup drops the .info-fine
    downscale (so it is no longer 11px) and the inline color (styling moved to the class)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    fi = text.find(".info-about-footlink {")
    foot = text[fi:fi + 160] if fi != -1 else ""
    centered = bool(foot) and "text-align: center" in foot
    bi = text.find(".info-a11y-btn {")
    btn = text[bi:bi + 360] if bi != -1 else ""
    btn_ok = bool(btn) and "border" in btn and "min-height: 44px" in btn
    i = text.find("var about =")
    j = text.find("var bodies =", i) if i >= 0 else -1
    region = text[i:j] if (i >= 0 and j > i) else ""
    markup_ok = 'class="info-a11y-btn"' in region
    not_fine = 'info-fine info-about-footlink' not in region and 'info-about-footlink info-fine' not in region
    ok = centered and btn_ok and markup_ok and not_fine
    return {"passed": ok,
            "details": "Accessibility link centered (.info-about-footlink) + bordered >=44px tap (.info-a11y-btn)"
            if ok else f"centered={centered} btn_ok={btn_ok} markup_ok={markup_ok} not_fine={not_fine}"}


def test_officials_render_as_cards():
    """Officials 1A (2026-06-03): the 3 channels render as calm bordered cards — --sa-surface
    fill + a FULL --sa-border hairline (not a colored left border) + radius + ~14px padding +
    >=44px tap target — so routing-to-officials is the panel's visual focus. The channel name
    reads 15px/600. This is Officials-scoped and does NOT reintroduce the Resources card grid
    cross-model review hard-rejected."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ci = text.find(".info-official-row {")
    css = text[ci:ci + 340] if ci != -1 else ""
    carded = (bool(css) and "background: var(--sa-surface)" in css
              and "border: 1px solid var(--sa-border)" in css
              and "border-radius" in css and "min-height: 44px" in css)
    no_left_accent = "border-left: 3px solid var(--sa-celadon)" not in css
    ki = text.find(".info-official-row .k {")
    kcss = text[ki:ki + 140] if ki != -1 else ""
    name_15 = bool(kcss) and "font-size: 15px" in kcss and "font-weight: 600" in kcss
    ok = carded and no_left_accent and name_15
    return {"passed": ok,
            "details": "Officials channels render as bordered cards (15px/600 name, >=44px tap)"
            if ok else f"carded={carded} no_left_accent={no_left_accent} name_15={name_15}"}


def test_resources_sections_delineated():
    """Resources 2A (2026-06-03): the three sections are visibly delineated — each
    .info-section-title carries a FULL-WIDTH top hairline (--sa-border, no horizontal margin
    inset) + generous top space, so Shelters / School closures / Recovery aid read as three
    distinct blocks, not one undifferentiated list. Reuses the --sa-border token (no card grid)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ti = text.find(".info-section-title {")
    css = text[ti:ti + 260] if ti != -1 else ""
    ruled = bool(css) and "border-top: 1px solid var(--sa-border)" in css
    full_width = bool(css) and "margin: 0;" in css and "padding: 16px 14px 6px" in css
    ok = ruled and full_width
    return {"passed": ok,
            "details": "Resources section titles ruled full-width with top space (3 distinct blocks)"
            if ok else f"ruled={ruled} full_width={full_width}"}
