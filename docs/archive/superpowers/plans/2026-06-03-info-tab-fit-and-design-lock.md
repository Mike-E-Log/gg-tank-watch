# Info-Tab Fit + Design-Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **TDD loop (this repo):** the eval harness is text-grep + static-CSS-invariant; it does NOT run JS. So the loop is: write/flip the guard to the NEW state → run it, confirm FAIL on current HTML → make the `dashboard.html`/CSS/i18n edit → run, confirm PASS. The **rendered geometry check** (no vertical scroll at 320/375/390 × light/dark) is the real behavioral gate, batched in Task 5 via the native Chrome integration (`mcp__claude-in-chrome__*`) — `browse.exe` is SAC-blocked, raw `msedge.exe` is permission-denied.

**Goal:** Implement the four 2026-06-03 design-locked Info-tab targets from `docs/info-tab-acceptance-rubric.md` §1 — Summary mobile-fit (cut 2 rows, single-line 4 values), Officials as calm bordered cards (1A), Resources sections visibly delineated (2A), and the About AI-disclosure moved to the panel-closing bottom line — as one branch → PR → merge.

**Architecture:** Single-file static dashboard. All UI edits land in `dashboard.html` (the `STRINGS` i18n block + `renderInfoTab`/`updateInfoData` + the inline `<style>` CSS), plus `sw.js` (cache bump) and the `eval/` grep + CSS-invariant guards. No JS framework, no new deps.

**Tech Stack:** vanilla HTML/CSS/JS, Python pytest-style eval harness (`eval/run_all.py`), Vercel static host.

**Verify cmd (never `--quiet`):** full `python eval/run_all.py --skip integration` · single module `python eval/run_all.py --only <module_stem>`

**Render/eyes (Task 5):** native Claude Code + Chrome integration (`mcp__claude-in-chrome__*`); `python -m http.server 8137` in repo root; viewports 320/360/375/390 × 568; light + dark (seed `localStorage` `gg-theme`); `switchTab('info')` then `switchInfoSubtab(id)`.

---

### Task 0: Feature branch + SW cache bump (v66 → v67)

**Files:**
- Modify: `sw.js:1`
- Modify: `eval/test_sw_cache_strategy.py:10-13`
- Modify: `eval/test_sw_precache.py:13`

- [ ] **Step 1:** create the branch and verify it.

```bash
git switch -c feat/info-tab-fit-and-design-lock
git branch --show-current   # expect: feat/info-tab-fit-and-design-lock
```

- [ ] **Step 2 (flip guards first):** in `eval/test_sw_cache_strategy.py` rename `test_cache_bumped_v66` → `test_cache_bumped_v67` and change both `gg-tank-v66` strings to `gg-tank-v67`:

```python
def test_cache_bumped_v67():
    t = SW.read_text(encoding="utf-8")
    return {"passed": 'CACHE_NAME = "gg-tank-v67"' in t,
            "details": f"v67 present={'gg-tank-v67' in t}"}
```

In `eval/test_sw_precache.py:13` change the version string:

```python
    bumped = 'CACHE_NAME = "gg-tank-v67"' in text
```

- [ ] **Step 3:** run → expect FAIL (sw.js still v66).

```bash
python eval/run_all.py --only test_sw_cache_strategy --only test_sw_precache
```
Expected: both `test_cache_bumped_*` FAIL.

- [ ] **Step 4:** edit `sw.js:1`:

```js
var CACHE_NAME = "gg-tank-v67";
```

- [ ] **Step 5:** run → PASS, then commit.

```bash
python eval/run_all.py --only test_sw_cache_strategy --only test_sw_precache
git add sw.js eval/test_sw_cache_strategy.py eval/test_sw_precache.py
git commit -m "chore(sw): bump cache v66->v67 for info-tab fit + design-lock"
```

---

### Task 1: Summary mobile-fit — cut Tank + Crack rows, single-line 4 values

**Files:**
- Modify: `dashboard.html` STRINGS (`:1603`, `:1605`, `:1609`, `:1610-1611`, `:1615`), summary render (`:2098-2107`), `updateInfoData` crack fill (`:2166-2167`)
- Modify: `eval/test_info_archive_clarity.py::test_summary_archive_facts_present` (`:228-244`)
- Test (new): `eval/test_info_subtab_fit.py`

The kept 7-fact narrative (after cutting Tank + Crack): Substance · Facility · Peak tank temperature · Peak evacuation · Evacuation zone · Incident window · Outcome. Keep the `info.tankCrack`/`info.tankCrackY`/`info.tankTempV` keys (read by `test_info_disclosures::test_tank_facts_past_tense`); only `info.fact.tank`/`info.fact.tankV` are orphaned by the cut and get removed.

- [ ] **Step 1 (new static guards):** append to `eval/test_info_subtab_fit.py` (pytest `assert` style, matching that file):

```python
def test_summary_fits_seven_rows():
    """Summary must be <=7 kv-rows so it fits a 568px-tall mobile panel with no vertical
    scroll (rubric 2026-06-03: 9 rows measured 486px@375 / 541px@320, over the ~342px panel).
    Tank + Crack observed are cut; the kept set is the 7-fact narrative. The real one-line/
    no-scroll proof is the rendered geometry probe in the acceptance rubric DoD."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find("var summary =")
    j = text.find("var officials", i)
    region = text[i:j] if (i >= 0 and j > i) else ""
    assert region, "summary render block not found"
    n = region.count('class="info-kv-row"')
    assert 0 < n <= 7, f"Summary should be 1..7 kv-rows, found {n}"
    assert 't("info.fact.tankV")' not in region, "Tank row should be cut"
    assert 'id="info-crack-val"' not in region, "Crack observed row should be cut"


def test_summary_values_shortened_for_single_line():
    """The 4 values that wrapped to 2-3 lines at <=320px are shortened to single-line forms
    (rubric 2026-06-03): Facility 'GKN Aerospace'; Peak tank temperature '~100F (gauge max)'
    (trailing ', then stabilized' dropped); Evacuation zone '~9 sq mi, 6 cities'; Outcome
    'No injuries; 0 displaced'."""
    text = DASHBOARD.read_text(encoding="utf-8")
    assert '{ en: "GKN Aerospace" }' in text, "facilityV not shortened"
    assert '{ en: "~9 sq mi, 6 cities" }' in text, "zonePeak not shortened"
    assert '{ en: "No injuries; 0 displaced" }' in text, "outcomeV not shortened"
    assert ", then stabilized" not in text, "tankTempArchive tail not trimmed"
```

- [ ] **Step 2 (update the superseded guard):** in `eval/test_info_archive_clarity.py::test_summary_archive_facts_present` drop `tank` from both key lists (the Summary now carries the kept narrative facts, not Tank):

```python
    val_keys = ["info.fact.substanceV", "info.fact.facilityV",
                "info.fact.windowV", "info.fact.outcomeV"]
    label_keys = ["info.fact.substance", "info.fact.facility",
                  "info.fact.window", "info.fact.outcome"]
```

- [ ] **Step 3:** run → expect FAIL (current HTML has 9 rows incl. Tank + Crack; values not shortened).

```bash
python eval/run_all.py --only test_info_subtab_fit --only test_info_archive_clarity
```
Expected: `test_summary_fits_seven_rows`, `test_summary_values_shortened_for_single_line` FAIL.

- [ ] **Step 4a (shorten i18n values):** four edits in `dashboard.html` STRINGS.

`:1609` —
```js
  "info.fact.facilityV":  { en: "GKN Aerospace" },
```
`:1603` (trim trailing clause; do not retype the degree glyph — match `(gauge max), then stabilized" }` → `(gauge max)" }`):
```js
  "info.tankTempArchive": { en: "~100°F (gauge max)" },
```
`:1605` —
```js
  "info.zonePeak": { en: "~9 sq mi, 6 cities" },
```
`:1615` —
```js
  "info.fact.outcomeV":   { en: "No injuries; 0 displaced" },
```

- [ ] **Step 4b (remove orphaned Tank keys):** delete `dashboard.html:1610-1611`:
```js
  "info.fact.tank":       { en: "Tank" },
  "info.fact.tankV":      { en: "34,000-gallon storage tank" },
```

- [ ] **Step 4c (cut the 2 summary rows):** in the `var summary =` block remove the Tank row (`:2101`) and the Crack row (`:2102`). The block becomes:
```js
  var summary =
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.fact.substance") + '</span><span class="info-kv-val">' + t("info.fact.substanceV") + '</span></div>' +
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.fact.facility") + '</span><span class="info-kv-val">' + t("info.fact.facilityV") + '</span></div>' +
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.tankTemp") + '</span><span class="info-kv-val">' + t("info.tankTempArchive") + '</span></div>' +
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.evacResidents") + '</span><span class="info-kv-val">' + t("info.peakEvac") + '</span></div>' +
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.evacBoundary") + '</span><span class="info-kv-val">' + t("info.zonePeak") + '</span></div>' +
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.fact.window") + '</span><span class="info-kv-val">' + t("info.fact.windowV") + '</span></div>' +
    '<div class="info-kv-row"><span class="info-kv-key">' + t("info.fact.outcome") + '</span><span class="info-kv-val">' + t("info.fact.outcomeV") + '</span></div>';
```

- [ ] **Step 4d (remove the now-dead crack fill):** delete `dashboard.html:2166-2167` (the `#info-crack-val` lookup + fill), leaving `updateInfoData` starting straight into Schools after `var tank = snap.tank || {};`. Remove the orphaned `var tank` line too **only if** nothing else in `updateInfoData` reads `tank` (grep first: `grep -n "tank\." dashboard.html` within the function) — current body uses `tank.crack_observed` only, so `var tank = snap.tank || {};` becomes orphaned and should be removed.

```js
function updateInfoData(snap) {
  // Schools
  var schoolsGrid = $("info-schools-grid");
  ...
```

- [ ] **Step 5:** run the affected modules → PASS, and confirm no collateral break:

```bash
python eval/run_all.py --only test_info_subtab_fit --only test_info_archive_clarity --only test_info_disclosures
```
Expected: `test_summary_fits_seven_rows`, `test_summary_values_shortened_for_single_line`, `test_summary_archive_facts_present`, `test_what_happened_shows_sourced_peak_facts`, `test_summary_zone_value_full_scale`, `test_tank_facts_past_tense` all PASS.

- [ ] **Step 6:** commit.

```bash
git add dashboard.html eval/test_info_subtab_fit.py eval/test_info_archive_clarity.py
git commit -m "feat(info): trim Summary to 7 single-line rows for mobile fit"
```

---

### Task 2: Officials → calm bordered cards (1A)

**Files:**
- Modify: `dashboard.html` `.info-official-row` + `.info-official-row .k` CSS (`:847`, `:853`)
- Test: `eval/test_info_archive_clarity.py` (new func)

Restyle the existing `.info-official-row` (markup unchanged) from a bottom-bordered flex row into a card: `--sa-surface` fill + full `--sa-border` hairline (NOT a colored left border — celadon-left is reserved for `.info-desc`) + radius + ~14px padding + ≥44px tap target; channel name 15px/600.

- [ ] **Step 1 (guard):** append to `eval/test_info_archive_clarity.py` (dict style):

```python
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
```

- [ ] **Step 2:** run → expect FAIL.

```bash
python eval/run_all.py --only test_info_archive_clarity
```
Expected: `test_officials_render_as_cards` FAIL.

- [ ] **Step 3:** edit `dashboard.html`. Replace `.info-official-row` (`:847`) and `.info-official-row .k` (`:853`):

```css
    /* Officials 1A (2026-06-03): each of the 3 channels is a calm bordered card — --sa-surface
       fill + a FULL --sa-border hairline (NOT a colored left border; celadon-left is reserved for
       .info-desc) + radius + 14px padding + >=44px tap target — so routing-to-officials is the
       panel's visual focus. Overrides .info-row's bottom-border/0-side padding via the full border
       + padding here. */
    .info-official-row {
      flex-direction: column;
      align-items: stretch;
      gap: 4px;
      background: var(--sa-surface);
      border: 1px solid var(--sa-border);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 10px;
      min-height: 44px;
    }
    .info-official-row:last-child { margin-bottom: 0; }
    .info-row-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
    /* keep the "Official ↗" cue intact; let a long channel name wrap instead (shelter-row pattern). */
    .info-row-top .v { white-space: nowrap; flex: 0 0 auto; }
    /* Official channel NAME is the card's primary content (the link): 15px/600 at the dark value
       color (user 2026-06-03). */
    .info-official-row .k { color: var(--sa-text); font-size: 15px; font-weight: 600; }
```

(Leave the existing `.info-row-top` and `.info-row-desc` rules as-is if untouched above; the block above re-states `.info-row-top` only to preserve adjacency — if duplicating causes a double rule, edit in place instead of re-adding.)

- [ ] **Step 4:** run → PASS; confirm `test_officials_panel_has_three_links` + `test_officials_note_removed_and_descriptions_present` still green.

```bash
python eval/run_all.py --only test_info_archive_clarity
```

- [ ] **Step 5:** commit.

```bash
git add dashboard.html eval/test_info_archive_clarity.py
git commit -m "feat(info): render Officials channels as calm bordered cards (1A)"
```

---

### Task 3: Resources sections visibly delineated (2A)

**Files:**
- Modify: `dashboard.html` `.info-section-title` CSS (`:817-824`)
- Test: `eval/test_info_archive_clarity.py` (new func)

Give each `.info-section-title` (Resources-only in markup) a full-width top hairline + generous top space so Shelters / School closures / Recovery aid read as three distinct blocks. Full-width = drop the horizontal margin and move the gutter into horizontal padding so the border-top spans the panel width.

- [ ] **Step 1 (guard):** append to `eval/test_info_archive_clarity.py`:

```python
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
```

- [ ] **Step 2:** run → expect FAIL.

```bash
python eval/run_all.py --only test_info_archive_clarity
```
Expected: `test_resources_sections_delineated` FAIL.

- [ ] **Step 3:** edit `dashboard.html` `.info-section-title` (`:817-824`):

```css
    .info-section-title {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: var(--sa-text-2);
      margin: 0;
      padding: 16px 14px 6px;
      border-top: 1px solid var(--sa-border);
    }
```

- [ ] **Step 4:** run → PASS; confirm `test_resources_panel_merges_three` + `test_resources_section_titles_full_labels` still green.

```bash
python eval/run_all.py --only test_info_archive_clarity
```

- [ ] **Step 5:** commit.

```bash
git add dashboard.html eval/test_info_archive_clarity.py
git commit -m "feat(info): delineate Resources sections with full-width rules (2A)"
```

---

### Task 4: About — move AI disclosure to the panel-closing bottom line

**Files:**
- Modify: `dashboard.html` `var about =` render (`:2141-2150`), `.info-ai-disclosure` CSS + comment (`:825-834`)
- Modify: `eval/test_info_archive_clarity.py::test_about_why_section_present` (`:419-443`), docstring of `test_about_disclosure_and_sources` (`:137-159`)

The binding honesty stays present + legible at 13px; only its POSITION moves from first line to last (the persistent safety strip carries the always-on honesty). New canonical About order: descriptor (from `panel()`) → Why → Sources fold → Accessibility link → AI disclosure.

- [ ] **Step 1 (flip the regression guard — TDD entry point):** rewrite `eval/test_info_archive_clarity.py::test_about_why_section_present` to assert the new canonical order Why → Sources → Accessibility → disclosure-last:

```python
def test_about_why_section_present():
    """User 2026-06-03: About order is Why -> Sources -> Accessibility -> AI disclosure
    (panel-closing line). The binding AI disclosure MOVED from the first line to the very bottom
    (the persistent safety strip carries the always-on honesty; the disclosure stays present +
    legible at 13px, position demoted not size). 'Why this was made' is a .about-why-title heading
    + a short resident-first paragraph; conduit-true (routes to officials, authors no directive)."""
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
```

- [ ] **Step 2:** run → expect FAIL (current HTML renders disclosure first).

```bash
python eval/run_all.py --only test_info_archive_clarity
```
Expected: `test_about_why_section_present` FAIL (`ordered=False`).

- [ ] **Step 3a (reorder render):** rewrite `dashboard.html` `var about =` (`:2141-2150`) so the disclosure is last:

```js
  // About — resident-first "Why this was made" + Sources fold + a prominent centered Accessibility
  // link, then the binding AI disclosure as the panel-closing line (user 2026-06-03: moved from the
  // first line to the bottom; the persistent safety strip carries the always-on honesty, so the
  // disclosure stays present + legible at 13px, position demoted not size). Methodology stays in README.
  var about =
    '<div class="about-body">' +
    '<div class="about-why-title">' + t("info.about.whyH") + '</div>' +
    '<p>' + t("info.about.why") + '</p>' +
    '<details open><summary class="info-sources-toggle">' + t("info.sourcesH") + '</summary>' +
    '<p class="info-fine info-sources-caption">' + t("info.sources.caption") + '</p>' +
    '<div id="info-source-list" class="info-fine" style="padding:0 0 12px"></div></details>' +
    '<p class="info-about-footlink"><a class="info-a11y-btn" href="accessibility.html"><span class="info-a11y-ico" aria-hidden="true">&#9855;&#65038;</span>' + t("info.about.a11ylink") + '</a></p>' +
    '<p class="info-ai-disclosure">' + t("disclosure.ai") + '</p>' +
    '</div>';
```

- [ ] **Step 3b (CSS separation + comment):** update `.info-ai-disclosure` (`:825-834`) so the now-bottom line is set off from the a11y pill above it (keep 13px / `--sa-text` / no gold — guarded by `test_about_disclosure_and_sources` + `test_disclosure_single_line_body_color`):

```css
    /* Responsible-AI disclosure: the panel-closing line of About (moved from the first line
       2026-06-03 — the persistent safety strip carries the always-on honesty). Stays at body
       near-black --sa-text, 13px, legible (position demoted, size not); the gold accent was
       dropped 2026-06-02. */
    .info-ai-disclosure {
      font-size: 13px;
      color: var(--sa-text);
      line-height: 1.45;
      margin-top: 16px;
    }
```

- [ ] **Step 3c (de-stale the sibling docstring):** in `eval/test_info_archive_clarity.py::test_about_disclosure_and_sources` (`:137-159`) the assertions are unchanged, but the docstring claim "binding-honesty property holds via the text + first-line placement" is now false. Replace that clause with "via the text + persistent safety strip; the disclosure renders at the panel-closing bottom line (2026-06-03)." (Docstring only — do not touch the asserts.)

- [ ] **Step 4:** run → PASS; confirm the four About guards all green: `test_about_why_section_present`, `test_about_disclosure_and_sources`, `test_about_a11y_link_prominent_centered`, and `test_disclosure_single_line_body_color` (in `test_info_disclosures`).

```bash
python eval/run_all.py --only test_info_archive_clarity --only test_info_disclosures
```

- [ ] **Step 5:** commit.

```bash
git add dashboard.html eval/test_info_archive_clarity.py
git commit -m "feat(info): move AI disclosure to the panel-closing line of About"
```

---

### Task 5: Full eval + eyes-in-the-loop render verification (the real gate)

**Files:** none (verification); fallback edits to `dashboard.html` + `eval/test_info_subtab_fit.py` only if 320px still clips.

- [ ] **Step 1:** full suite, no `--quiet`:

```bash
python eval/run_all.py --skip integration
```
Expected: 0 `[FAIL]` lines; total ≥ prior count + 4 new tests (`test_summary_fits_seven_rows`, `test_summary_values_shortened_for_single_line`, `test_officials_render_as_cards`, `test_resources_sections_delineated`).

- [ ] **Step 2 (serve + render):** start the static server and drive the native Chrome integration:

```bash
python -m http.server 8137   # run in repo root (background)
```
Navigate to `http://127.0.0.1:8137/dashboard.html`. For each viewport in {320, 360, 375, 390} × 568 and each theme in {light, dark} (seed dark via `localStorage.setItem('gg-theme','dark')` then reload), run `switchTab('info')` then visit each sub-tab.

- [ ] **Step 3 (geometry probe — Summary no vertical scroll):** with Summary active, in `mcp__claude-in-chrome__javascript_tool` evaluate:

```js
(function () {
  switchTab('info'); switchInfoSubtab('summary');
  var over = document.body.scrollHeight - window.innerHeight;
  var rows = document.querySelectorAll('#info-subpanel-summary .info-kv-row').length;
  return JSON.stringify({ w: window.innerWidth, h: window.innerHeight, rows: rows, overflowPx: over });
})()
```
Acceptance: `rows === 7` and `overflowPx <= 0` (no vertical page scroll) at **every** width, both themes. Also confirm each shortened value renders on **one line** (the four single-lined values do not wrap) — visual check + optionally a `Range`-based glyph-width probe per the rubric.

- [ ] **Step 4 (ranked fallback if 320 still clips):** if `overflowPx > 0` at 320 only, apply the rubric's ranked fallback **in this order, re-measuring after each**: (1) drop the **Peak tank temperature** row; (2) then drop **Incident window**. Each drop: lower the `<=7` bound in `test_summary_fits_seven_rows` to match, remove the row from `var summary =`, re-run the module, re-probe. `log` what was dropped (no silent cap). Commit any fallback as `fix(info): drop <row> so Summary fits 320px (ranked fallback)`.

- [ ] **Step 5 (the other three panels — visual confirm):**
  - **Officials:** 3 calm bordered cards (surface fill + full hairline, NOT colored-left), name 15px/600, `Official ↗` celadon cue, one-line desc, tappable ≥44px; cards fill the panel so routing is the focus. No double border under the group reads as a stray line.
  - **Resources:** three sections read as distinct blocks (full-width rule + top space above each title); descriptor band still one line at 375px; no card grid.
  - **About:** order top→bottom = descriptor → Why → Sources (open) → centered Accessibility pill → AI disclosure as the closing line (13px, legible, separated from the pill).
  - **Info↔News toggle:** no sub-tab-bar height jump (A guard).

- [ ] **Step 6:** if any visual regression → fix + re-run Step 1 + re-probe. Do **not** claim done on green grep alone (the rubric exists because text-only went green while #108 clipped at 375px).

---

### Task 6: Ship

**Files:** `CHANGELOG.md` (+ any VERSION bump the `/ship` flow performs).

- [ ] **Step 1:** `git status --short` — confirm only intended paths staged across the task commits; `eval/scores.jsonl` may show `M` (regenerable append-log; leave it).
- [ ] **Step 2:** run `/ship` (or `/land-and-deploy`): CHANGELOG entry, final diff review, push `feat/info-tab-fit-and-design-lock`, open PR (problem / approach / test plan incl. the geometry probe results / risk / rollback; UI screenshots at 320/375/390 light+dark). **noindex stays ON** (Lane B3 not cleared). Never push `main`.
- [ ] **Step 3 (post-merge):** after merge, verify on `gg-tank-watch.vercel.app` (HTTP 200) and that the SW serves `gg-tank-v67`. Sync local main carefully (`git fetch` first; the `eval/scores.jsonl` `M` may need a stash/restore before `--ff-only`).
- [ ] **Step 4:** stage the rubric. `docs/info-tab-acceptance-rubric.md` (the locked target, currently uncommitted) ships in this PR as the design-of-record for these four changes — `git add docs/info-tab-acceptance-rubric.md` in the same branch before the PR.

---

## Self-Review

**1. Spec coverage (rubric §1 four changes):**
- Summary fit (cut 2, single-line 4, ranked fallback) → Task 1 + Task 5 Steps 3-4. ✓
- Officials calm bordered cards (1A) → Task 2. ✓
- Resources sections delineated (2A) → Task 3. ✓
- About disclosure → panel-closing line → Task 4. ✓
- SW cache bump (any HTML change) → Task 0. ✓
- Geometry/eyes gate (not text-only) → Task 5. ✓

**2. Placeholder scan:** every code step shows exact i18n/CSS/JS/assertion content and exact file lines; no TBD/"handle edge cases"/"similar to". ✓

**3. Affected-guard ledger (no silent breakage):**
- `test_summary_archive_facts_present` — updated (drop tank) in Task 1 Step 2. ✓
- `test_about_why_section_present` — flipped to disclosure-last in Task 4 Step 1 (the TDD entry point). ✓
- `test_about_disclosure_and_sources` — docstring de-staled, asserts unchanged (Task 4 Step 3c). ✓
- `test_tank_facts_past_tense` — reads `info.tankCrackY`/`info.tankTempV` **values**; those keys are kept → stays green (verified Task 1 Step 5). ✓
- `test_what_happened_shows_sourced_peak_facts` — `~100`/`9 sq mi` substrings + `tankTempArchive`/`zonePeak`/`peakEvac` bindings survive the shortening → stays green. ✓
- `test_disclosure_single_line_body_color`, `test_about_a11y_link_prominent_centered`, `test_officials_panel_has_three_links`, `test_resources_panel_merges_three`, `test_no_inline_font_size_in_info_panels` — markup/classes preserved; CSS-only restyles → stay green. ✓

**4. Type/name consistency:** selector/class/key names (`.info-official-row`, `.info-section-title`, `.info-ai-disclosure`, `info.fact.*`, `disclosure.ai`, `gg-tank-v67`) used identically across tasks and guards. Removed only the orphaned `info.fact.tank`/`info.fact.tankV` (kept `info.tankCrack`/`info.tankCrackY`/`info.tankTempV` per rubric). ✓
