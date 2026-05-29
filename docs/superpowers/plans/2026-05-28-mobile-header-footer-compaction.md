# Mobile Header / Footer Compaction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Verification note:** This is CSS/HTML in a single static file (`dashboard.html`). There is no unit-test surface for layout. The "test" for each task is the **signed Edge-headless screenshot matrix** (Smart App Control blocks gstack's `browse.exe` on this machine — see memory `sac-blocks-browse-edge-fallback`) plus the existing **eval harness** (`python eval/run_all.py --skip integration`). Verification is consolidated in Task 4 and run once after the three surgical edits land.

**Goal:** Fix three mobile-layout defects in `dashboard.html` — (1) misaligned separator dots / OCFA in the footer disclaimer, (2) the header+stats block crowding the map, (3) the Vietnamese language toggle pushing the light/dark toggle onto its own line — without dropping any information or any load-bearing legal/honesty element.

**Architecture:** Three surgical, mobile-scoped CSS changes plus one tiny HTML wrapper, all inside the existing single-file dashboard. No new dependencies, no JS logic changes (IDs preserved so existing `getElementById` handlers keep working). Desktop (≥600px / ≥768px per existing per-component breakpoints) is left untouched. Reclaimed vertical space flows automatically to the map, which is already `flex: 1` inside the `100dvh` `.app` column.

**Tech Stack:** Static HTML/CSS (single file), Python eval harness (`eval/`), signed Edge headless for visual verification, `python -m http.server` for a same-origin local host.

---

## File Structure

- **Modify:** `dashboard.html`
  - `.safety-strip-sources` rule (~line 357) — Task 2 (footer alignment)
  - `.safety-strip` + `.hero-status*` rules (~lines 327–348, 457–467) — Task 3 (compaction)
  - `.topbar`/`.unofficial-pill`/new `.topbar-controls` rules (~lines 147–253) + header markup (~lines 1493–1503) — Task 1 (control cluster)
- **Create (verification artifacts, not committed):** `docs/superpowers/plans/_shots/2026-05-28/*.png`
- **Unchanged:** all JavaScript, all i18n strings, `terms.html`, `eval/`.

Edit ordering is chosen so the height-sensitive change (Task 3, compaction) is verified last, after the header (Task 1) and footer (Task 2) have settled their own heights.

---

### Task 1: Issue #3 — pin language + theme controls so VI never splits them

**Root cause:** `.topbar` is `display:flex; flex-wrap:wrap` on mobile (`@media (max-width: 599px)`, line 214). In Vietnamese the pill text becomes `KHÔNG CHÍNH THỨC` (`.unofficial-pill { white-space: nowrap; flex: 0 0 auto }`, line 178/180 — cannot shrink) and the lang label becomes `Việt`. Pill + wordmark + lang button + theme button exceed phone width, so the last item (theme toggle) wraps to its own line.

**Fix (judge-selected Candidate A, hardened):** (a) wrap the two control buttons in a non-splitting `.topbar-controls` cluster so they can never separate from each other; (b) on mobile only, let the pill text wrap to multiple lines (`white-space: normal`) so it yields width instead of forcing the controls off the row — the `KHÔNG CHÍNH THỨC` disclosure stays **fully visible and prominent**, just taller on the narrowest screens (this answers the dissenting judge's only objection).

**Files:**
- Modify markup: `dashboard.html:1498-1502`
- Modify/Add CSS: `dashboard.html` topbar block (`~147-253`)

- [ ] **Step 1: Wrap the two controls in a cluster (markup)**

Replace the lang-picker + theme-toggle block (lines 1498–1502):

```html
      <div class="lang-picker" id="lang-picker">
        <button class="topbar-btn" id="lang-toggle" onclick="toggleLangMenu()" aria-haspopup="true" aria-expanded="false" title="Language / Ng&#xF4;n ng&#x1EEF;">VI</button>
        <div class="lang-menu" id="lang-menu" role="menu"></div>
      </div>
      <button class="topbar-btn" id="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme" title="Toggle theme">&#x1F319;</button>
```

with the same elements wrapped in `.topbar-controls`:

```html
      <div class="topbar-controls">
        <div class="lang-picker" id="lang-picker">
          <button class="topbar-btn" id="lang-toggle" onclick="toggleLangMenu()" aria-haspopup="true" aria-expanded="false" title="Language / Ng&#xF4;n ng&#x1EEF;">VI</button>
          <div class="lang-menu" id="lang-menu" role="menu"></div>
        </div>
        <button class="topbar-btn" id="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme" title="Toggle theme">&#x1F319;</button>
      </div>
```

All four IDs (`lang-picker`, `lang-toggle`, `lang-menu`, `theme-toggle`) are preserved, so every `getElementById` call and the `.lang-menu` absolute positioning (anchored to `#lang-picker`, `position: relative`) keep working unchanged.

- [ ] **Step 2: Add the `.topbar-controls` cluster rule**

Insert immediately after the `.lang-picker { ... }` rule (line 254):

```css
    .topbar-controls { display: inline-flex; align-items: center; gap: 8px; flex: 0 0 auto; }
```

This makes the lang+theme pair a single, non-shrinking flex item — flex-wrap can move the *cluster* as a unit but can never split the theme toggle away from the lang toggle.

- [ ] **Step 3: Let the pill wrap on mobile so it yields width (keeps controls on row 1)**

Inside the existing `@media (max-width: 599px)` topbar block (lines 212–216), add a pill override so the long VI text wraps instead of forcing the cluster off the line:

```css
    @media (max-width: 599px) {
      /* mobile: freshness on its own full-width line so it never clips in the crowded topbar */
      .topbar { flex-wrap: wrap; }
      .topbar-freshness { order: 1; width: 100%; display: block; text-align: right; overflow: visible; }
      /* VI: let "KHÔNG CHÍNH THỨC" wrap to 2 lines (stays fully visible) instead of pushing the controls off the row */
      .unofficial-pill { white-space: normal; text-align: center; }
    }
```

English is unaffected — `UNOFFICIAL` is a single token and will not wrap.

- [ ] **Step 4: Verify (deferred to Task 4)** — VI mobile shows lang + theme side-by-side on one row; pill fully readable; EN mobile visually unchanged; desktop unchanged.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "fix(mobile): pin lang+theme controls so VI never splits the theme toggle"
```

---

### Task 2: Issue #1 — vertically center the footer source row

**Root cause:** `.safety-strip-sources` (line 357) is `display:flex; flex-wrap:wrap` with the default `align-items: stretch`. Its `<a>` children carry `min-height: 44px; display: inline-flex; align-items: center` (mobile tap targets, lines 368–375), so link text is centered in a 44px-tall box — but the separator `·` spans (`.safety-strip-sep`, line 380) and the bare `<span>OCFA</span>` (line 1541) have no height, so their glyphs sit at the **top** of the 44px flex line. Result: dots and OCFA float above the link baseline.

**Fix:** center the whole row on the cross axis so every child (links, dots, OCFA) shares one vertical center.

**Files:**
- Modify CSS: `dashboard.html:357-364`

- [ ] **Step 1: Add `align-items: center` to the sources row**

Replace (lines 357–364):

```css
    .safety-strip-sources {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 4px 8px;
      font-family: "IBM Plex Mono", monospace;
      font-size: 10.5px;
    }
```

with:

```css
    .safety-strip-sources {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 4px 8px;
      font-family: "IBM Plex Mono", monospace;
      font-size: 10.5px;
    }
```

- [ ] **Step 2: Verify (deferred to Task 4)** — dots and `OCFA` sit on the same vertical center as `ggcity.org/emergency`, `911`, `714-628-7085`. No element raised above the others.

- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "fix(mobile): vertically center footer disclaimer sources so dots/OCFA align"
```

---

### Task 3: Issue #2 — compact the hero stats + safety strip to give the map more height

**Root cause:** `.app` is a `100dvh` flex column; the map (`.map-outer { flex: 1 }`) gets whatever the chrome above it leaves. On mobile the stacked `.hero-status` (2×2 grid) + `.safety-strip` (disclaimer + 44px tap-target source links) consume ~170px. User direction: **maximum compaction while keeping every stat, the full disclaimer, the terms link, and all official-source links (incl. OCFA)**, and without dropping tap targets below 44px in this safety-critical app.

**Approach:** tighten padding / gaps / value font on the **mobile** rules only (the `<600px` defaults, matching each component's existing breakpoint). Keep the 2×2 stat grid (4 long labels do not fit legibly in one row at 320–360px), keep all legal copy, keep 44px tap targets. Reclaimed height flows to the `flex: 1` map automatically. Exact pixel values below are the starting point; Task 4 confirms the map gained meaningful height and that nothing clips — tune within these rules if a screenshot shows a problem.

**Files:**
- Modify CSS: `dashboard.html:327-334` (`.safety-strip` mobile padding/gap)
- Modify CSS: `dashboard.html:457, 458, 461` (`.hero-status` mobile padding, row gap, value font)

- [ ] **Step 1: Compact the hero stats (mobile defaults)**

Replace (line 457):

```css
    .hero-status { padding: 8px 16px; border-bottom: 1px solid var(--sa-border); }
```

with:

```css
    .hero-status { padding: 5px 16px; border-bottom: 1px solid var(--sa-border); }
```

Replace (line 458):

```css
    .hero-status-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 12px; }
```

with:

```css
    .hero-status-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px 12px; }
```

Replace (line 461):

```css
    .hero-status-value { font-size: 16px; font-weight: 700; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; color: var(--sa-text); }
```

with:

```css
    .hero-status-value { font-size: 15px; font-weight: 700; line-height: 1.15; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; color: var(--sa-text); }
```

The `@media (min-width: 600px)` overrides (lines 463–467) already reset `.hero-status` padding to `12px 16px` and value font to `18px`, so desktop/tablet is unaffected.

- [ ] **Step 2: Compact the safety strip (mobile defaults), keeping all copy + 44px taps**

Replace (lines 333–334) inside `.safety-strip`:

```css
      gap: 3px;
      padding: 8px 14px;
```

with:

```css
      gap: 2px;
      padding: 5px 14px;
```

The `@media (min-width: 600px)` override (lines 342–347) resets `gap: 6px; padding: 10px 22px`, so desktop is unaffected. The disclaimer sentence, terms link, and all four source links (`ggcity.org/emergency`, `911`, `714-628-7085`, `OCFA`) remain present and the source links keep `min-height: 44px`.

- [ ] **Step 3: Verify (deferred to Task 4)** — every stat label+value still visible; full disclaimer + terms + all 4 sources still present; source links still ≥44px tall; map is visibly taller than before; no clipping.

- [ ] **Step 4: Commit**

```bash
git add dashboard.html
git commit -m "fix(mobile): compact hero stats + safety strip to give the map more height"
```

---

### Task 4: Verification — Edge-headless screenshot matrix + eval harness

**Goal:** prove all three fixes work and nothing regressed, across both languages, both themes, and desktop. Uses signed Edge (SAC allows it) driven from a fresh profile that seeds `gg-lang` / `gg-theme` localStorage, against a same-origin local server.

**Files:**
- Create: `docs/superpowers/plans/_shots/2026-05-28/` (screenshots; not committed)

- [ ] **Step 1: Serve the site (same-origin, background)**

```bash
cd "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-dashboard"
python -m http.server 8765
```
(run in background; `file://` blocks the JSON/config fetches, so an http origin is required)

- [ ] **Step 2: For each matrix cell, seed localStorage then screenshot with the SAME fresh profile**

Matrix (state → device):
- mobile EN light — 375×812
- mobile EN dark — 375×812
- mobile VI light — 375×812
- mobile VI dark — 375×812
- mobile VI light **narrow** — 320×812 (confirms pill wraps cleanly AND controls stay together)
- desktop EN light — 1024×768 (regression guard)

Seed page (write once to a temp file, e.g. `$env:TEMP\seed.html`), served from the same origin or loaded then redirected — set both keys per cell:

```html
<script>localStorage.setItem('gg-lang','vi');localStorage.setItem('gg-theme','dark');location.replace('/dashboard.html');</script>
```

Screenshot command per cell (fresh `--user-data-dir` each run so edited CSS + seeded storage are not stale-cached):

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --enable-unsafe-swiftshader --hide-scrollbars --force-device-scale-factor=2 --user-data-dir="$env:TEMP\ggshot_<cell>" --window-size=375,812 --virtual-time-budget=9000 --screenshot="docs\superpowers\plans\_shots\2026-05-28\<cell>.png" "http://127.0.0.1:8765/dashboard.html" | Out-Null
```
(use `| Out-Null`, never `2>$null` on the native exe — PS 5.1 native-stderr footgun; see memory)

- [ ] **Step 3: Vision-check each screenshot** against its acceptance criteria:
  - #1: footer dots + OCFA vertically centered with the link row (all cells)
  - #2: map visibly larger than the pre-fix baseline; all 4 stats + full disclaimer + terms + 4 sources present and unclipped (mobile cells)
  - #3: lang + theme controls on ONE row in VI; `KHÔNG CHÍNH THỨC` fully visible; theme toggle never on its own line (VI cells, esp. 320px)
  - regression: desktop EN cell visually identical to pre-fix desktop; light/dark both correct

- [ ] **Step 4: Run the eval harness (must stay green)**

```bash
python eval/run_all.py --skip integration
```
Expected: exit code 0, no `[FAIL]` lines. (Never use `--quiet` — it suppresses `[FAIL]` lines; verify by exit code/scorecard — see memory `eval-runner-quiet-hides-fails`.)

- [ ] **Step 5: Stop the background server.**

---

## Self-Review

**1. Spec coverage:**
- Issue #1 (footer dots/OCFA) → Task 2 ✅
- Issue #2 (upper stack crowds map, max compaction, keep all info + legal) → Task 3 ✅ (keeps every stat, full disclaimer, terms, all 4 sources, 44px taps)
- Issue #3 (VI splits theme toggle) → Task 1 ✅ (cluster + pill-wrap, judge-selected + hardened)
- Verification across EN/VI × light/dark + desktop + eval → Task 4 ✅

**2. Placeholder scan:** No TBD/TODO/"handle edge cases". Every CSS change shows complete before/after. Pixel values in Task 3 are explicit starting values with a stated tune-during-verify allowance.

**3. Consistency:** New class `.topbar-controls` defined in Task 1 Step 2 and used in Task 1 Step 1 markup. IDs unchanged (`lang-picker`/`lang-toggle`/`lang-menu`/`theme-toggle`) so JS is untouched. All breakpoints match the file's existing per-component scoping (`max-width:599px` for topbar wrap; `min-width:600px` resets for hero/safety-strip).

**Risk / rollback:** Single-file, CSS-only + one wrapper div. Each task commits atomically; revert any single commit to roll back that fix independently. No data, deps, auth, or eval contract touched.
