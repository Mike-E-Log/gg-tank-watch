# Desktop/Tablet Content-Cap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** At ≥768px, cap the GG Tank Watch *content* to a comfortable centered reading width while the *map* stays full-bleed — fixing the full-bleed stretch (933px label→value gaps, 1388px news lines) without changing the settled mobile layout.

**Architecture:** CSS-only change to the single-file `dashboard.html`. Keep `.app` full-width at ≥768px (so `#maplibre-map` keeps filling the viewport, zero map risk), and instead cap the *content*: `max-width: var(--content-cap)` + `margin-inline:auto` on the scrolling panels (`.news-subpanel`, `#info-content`), and full-width bars with centered content via `padding-inline: max(<own-pad>, calc((100% - var(--content-cap)) / 2))` on `.topbar`, `.safety-strip`, `.tab-bar`. No markup change.

**Tech Stack:** Static HTML/CSS (single file), CSS custom properties, pytest-style eval harness (`eval/run_all.py`), service worker cache versioning (`sw.js`), native Claude-in-Chrome for the rendered-geometry gate.

---

## Mechanism decision (B, with reasoning)

Two options were considered:

- **(A) Re-cap whole `.app` at ~800 centered + break the map out to `100vw`.** Rejected: the map lives in a flex-grow slot under an `overflow:hidden`, `height:100dvh` column with an `.app-chrome` max-height clamp; a `width:100vw; margin-left:calc(50% - 50vw)` breakout interacts with that flex/clamp and risks the map's ResizeObserver re-fit. High risk on a settled, primary view.
- **(B) Keep `.app` full-width; cap only the content.** ✅ **Chosen.** The map panel is left untouched (zero map risk). Bars keep their full-width background + hairline border (looks finished, not floating) while their content centers into the same column as the panels. Pure CSS, no markup change, lowest blast radius. The one behavior change to verify: at ≥768px the three bars' inline padding becomes `max(own-pad, centering)`, so below the cap threshold they keep their own padding and above it they center — confirm each bar's existing padding is preserved as the floor.

**Content cap value:** `--content-cap: 800px` — reuses the existing mobile `.app { max-width: 800px }` value, so the content column reads at a consistent 800px on both mobile and desktop; only the map breaks wide on desktop.

## Acceptance criteria

At **≥768px** (verify at 768, 1024, 1280, 1440; light + dark):
1. `.news-subpanel` and `#info-content` render at **width ≤ 800px, horizontally centered** (`margin-inline:auto`).
2. The **map** (`#maplibre-map` / `.map-outer`) renders at the **full viewport width** (unchanged).
3. `.topbar`, `.safety-strip`, `.tab-bar` keep **full-width backgrounds/borders**, but their *content* sits within the centered ≤800 column.
4. **No horizontal page overflow** (`documentElement.scrollWidth === clientWidth`).
5. Info Summary label→value gap and News card width are bounded by the 800 column (no 933px gap, no 1388px line).

At **<768px** (360, 390): layout is **behaviorally identical** to current (mobile is settled — the new rules live only inside the `@media (min-width:768px)` block).

Deterministic floor: a static CSS causal-invariant test passes. Eyes-in-loop: rendered-geometry confirmed in real Chrome at all widths × themes.

## File structure

- **Modify:** `dashboard.html` — add `--content-cap` to the existing `:root` token block; add content-cap + bar-centering rules inside the existing `@media (min-width: 768px)` region.
- **Modify:** `sw.js` — bump `CACHE_NAME` `gg-tank-v69` → `gg-tank-v70`.
- **Create:** `eval/test_desktop_layout.py` — static CSS causal-invariant guard.
- **Update:** `eval/test_sw_cache_strategy.py` + `eval/test_sw_precache.py` — version pins v69 → v70.

---

## Task 1: Failing geometry-invariant guard (deterministic floor)

**Files:**
- Create: `eval/test_desktop_layout.py`

- [ ] **Step 1: Write the failing test**

```python
"""Guard: at desktop/tablet (>=768px) the CONTENT is capped to a comfortable, centered
reading width while the MAP stays full-bleed. Failure mode fixed here is the inverse of #108:
`@media (min-width:768px){ .app{ max-width:none } }` dropped the cap for EVERYTHING, so Info
rows ran 1200px wide with a 933px label->value gap and News cards ran 1388px. This asserts the
causal CSS invariant in source (deterministic, no browser); the rendered-geometry proof
(content<=cap, map==full viewport, no h-overflow) is the eyes-in-loop Chrome gate in the DoD."""
from pathlib import Path
import re

CATEGORY = "behavioral"
ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "dashboard.html"


def test_desktop_content_capped_map_full():
    text = DASHBOARD.read_text(encoding="utf-8")
    # 1. a single content-cap token is defined and reused
    cap_defined = re.search(r"--content-cap:\s*\d+px", text) is not None
    # 2. the scrolling panels are capped + centered with that token
    news_capped = re.search(r"\.news-subpanel\b[^{]*\{[^}]*max-width:\s*var\(--content-cap\)", text, re.S) is not None \
        or re.search(r"\.news-subpanel,\s*\n?\s*#info-content\s*\{[^}]*max-width:\s*var\(--content-cap\)", text, re.S) is not None
    info_capped = "#info-content" in text and "max-width: var(--content-cap)" in text
    centered = "margin-inline: auto" in text
    # 3. full-width bars center their content via the padding-inline max() trick
    bar_centering = "calc((100% - var(--content-cap)) / 2)" in text
    # 4. the cap is scoped to >=768px only (mobile untouched)
    scoped = re.search(r"@media\s*\(min-width:\s*768px\)", text) is not None
    # 5. the map is NOT given the content cap (stays full-bleed)
    map_not_capped = re.search(r"#maplibre-map[^{]*\{[^}]*max-width:\s*var\(--content-cap\)", text, re.S) is None \
        and re.search(r"\.map-outer[^{]*\{[^}]*max-width:\s*var\(--content-cap\)", text, re.S) is None
    ok = cap_defined and (news_capped or info_capped) and centered and bar_centering and scoped and map_not_capped
    return {"passed": ok,
            "details": "Desktop: content capped to var(--content-cap) centered; bars padding-inline-centered; map uncapped"
            if ok else f"cap_defined={cap_defined} news={news_capped} info={info_capped} "
                       f"centered={centered} bars={bar_centering} scoped={scoped} map_free={map_not_capped}"}
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `python eval/run_all.py --only test_desktop_layout`
Expected: `[FAIL] test_desktop_layout::test_desktop_content_capped_map_full` (cap_defined=False bars=False …). Scorecard authoritative; `RUNNER_EXIT` via `${PIPESTATUS[0]}`.

---

## Task 2: Implement the content cap (make the guard pass)

**Files:**
- Modify: `dashboard.html` — `:root` token block (add `--content-cap`) and the `@media (min-width: 768px)` region.

- [ ] **Step 1: Read the existing bar paddings** so each bar's own inline padding is preserved as the `max()` floor.

Run: confirm the current inline padding of `.topbar` (`padding: 10px 22px` at ≥768 — floor `22px`), `.safety-strip`, and `.tab-bar` (Grep their rules in `dashboard.html`). Use each bar's own horizontal padding as the first `max()` arg.

- [ ] **Step 2: Add the cap token** to the existing `:root` (where `--sa-*` tokens are defined):

```css
--content-cap: 800px;
```

- [ ] **Step 3: Add the desktop rules** inside the existing `@media (min-width: 768px)` block (keep `.app { max-width: none }` as-is so the map fills the viewport):

```css
@media (min-width: 768px) {
  /* ...existing rules (.app max-width:none, topbar/pills paddings) stay... */

  /* Cap the scrolling content to a comfortable reading column, centered.
     The MAP panel is deliberately NOT capped — it keeps the full viewport width. */
  .news-subpanel,
  #info-content {
    max-width: var(--content-cap);
    margin-inline: auto;
  }

  /* Full-width bars (bg + hairline border preserved), content centered into the
     same column via symmetric padding — no markup change. Each bar keeps its own
     horizontal padding as the floor below the cap threshold. */
  .topbar      { padding-inline: max(22px, calc((100% - var(--content-cap)) / 2)); }
  .safety-strip{ padding-inline: max(<safety-strip-own-x>, calc((100% - var(--content-cap)) / 2)); }
  .tab-bar     { padding-inline: max(<tab-bar-own-x>, calc((100% - var(--content-cap)) / 2)); }
}
```
(Replace `<safety-strip-own-x>` / `<tab-bar-own-x>` with the literal values read in Step 1. If a bar sets `padding: a b` shorthand, switch it to keep the vertical padding and use `padding-inline` for horizontal, or set `padding-inline` after the shorthand — verify no regression.)

- [ ] **Step 4: Run the guard to verify it PASSES**

Run: `python eval/run_all.py --only test_desktop_layout`
Expected: `[PASS] test_desktop_layout::test_desktop_content_capped_map_full`.

---

## Task 3: SW cache bump + version-pin guards

**Files:**
- Modify: `sw.js` (`CACHE_NAME` v69 → v70)
- Modify: `eval/test_sw_cache_strategy.py` (`test_cache_bumped_v69` → `_v70`, strings v69→v70)
- Modify: `eval/test_sw_precache.py` (v69 → v70)

- [ ] **Step 1:** `sw.js`: `var CACHE_NAME = "gg-tank-v70";`
- [ ] **Step 2:** `eval/test_sw_cache_strategy.py`: rename fn `test_cache_bumped_v70`, replace `gg-tank-v69`→`gg-tank-v70`, detail `v70`.
- [ ] **Step 3:** `eval/test_sw_precache.py`: `gg-tank-v69`→`gg-tank-v70`, detail `v70`.

---

## Task 4: Full eval green

- [ ] **Step 1:** Run: `python eval/run_all.py --skip integration 2>&1 | grep -E "\[FAIL\]|TOTAL|pass\)" ; echo "RUNNER_EXIT=${PIPESTATUS[0]}"`
Expected: `RUNNER_EXIT=0`, TOTAL all pass (new desktop test included), no `[FAIL]`.

---

## Task 5: Eyes-in-loop render-diff gate (binding — geometry, not strings)

Drive the connected Chrome (deployed page won't have the change; serve `python -m http.server` locally and navigate, OR — since localhost nav was denied earlier — inject the candidate CSS into the live page and resize). For each width **768, 1024, 1280, 1440** × **light + dark**, switch to Info, News, Map and assert by `getBoundingClientRect`/`scrollWidth`:

- [ ] `news-subpanel`/`#info-content` width ≤ 800 and centered (left margin ≈ right margin).
- [ ] Info Summary row label→value gap is small (no 933px gulf).
- [ ] `#maplibre-map` width === `window.innerWidth` (full-bleed) on the Map tab.
- [ ] `documentElement.scrollWidth === clientWidth` (no horizontal overflow).
- [ ] Bars (`.topbar`, `.safety-strip`, `.tab-bar`) span full width; their content sits in the centered column.
- [ ] Screenshot each anchor (1440 + 768), light + dark; eyeball calm/centered.
- [ ] Re-check **mobile 390** is visually unchanged (content fills, no new cap effect).

---

## Task 6: Ship

- [ ] Branch `feat/desktop-content-cap`; stage explicit paths (`dashboard.html sw.js eval/test_desktop_layout.py eval/test_sw_cache_strategy.py eval/test_sw_precache.py` — never `eval/scores.jsonl`).
- [ ] Conventional commit; push; `gh pr create` (problem/approach/test plan/risk/rollback + screenshots).
- [ ] On user approval: `gh pr merge --squash --delete-branch`; **verify on prod** (`curl` for `--content-cap` + `gg-tank-v70`; real-Chrome render at 1440 + 768).

---

## Self-review

- **Spec coverage:** target (content cap + map full) → Task 2; failing test first → Task 1; SW bump → Task 3; eval green → Task 4; rendered-geometry gate at all widths×themes → Task 5; ship+prod-verify → Task 6. ✓
- **Placeholders:** only `<safety-strip-own-x>` / `<tab-bar-own-x>`, intentionally read in Task 2 Step 1 (their literal current values) — not a TODO. ✓
- **Consistency:** `--content-cap` used identically in CSS (Task 2) and test (Task 1); `gg-tank-v70` consistent across `sw.js` + both guards (Task 3). ✓
