# Header Masthead (Option B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harmonize the dashboard topbar into a masthead so the UNOFFICIAL pill, the "GG Tank Watch" wordmark, and the "Last updated…" dateline sit on one clean left axis at every width, with the share/theme controls pinned top-right.

**Architecture:** Move `.topbar-freshness` inside `.topbar-lead`, below a new `.topbar-lead-row` wrapper (pill + wordmark). Make `.topbar-lead` a flex column. At narrow widths the topbar stays a single non-wrapping flex row `[lead column | controls]`, so controls can never wrap to a second line — this **removes** the old flex-wrap trick (`.topbar-lead{flex:1 1 0}` + `.topbar-wordmark{flex:0 0 100%}` + right-aligned `order:1` freshness) whose only reason was an EN/VI width-jump that no longer exists (English-only). The now-orphaned `.topbar-spacer` is deleted.

**Tech Stack:** Single-file static `dashboard.html` (inline CSS), Python `test_*` eval guards (`eval/run_all.py` auto-discovers), `sw.js` cache-first service worker.

**Constraints (binding):** UNOFFICIAL pill stays prominent; theme toggle keeps `min-width: 44px` (a11y); English-only; preserve ids `#updated-text` / `#freshness-label` and the `"updated.freshness"` i18n string (JS + `test_freshness_ui.py` depend on them); CSS-first minimal diff.

---

## File Structure

- `dashboard.html` — header markup (`~1404-1417`) + topbar CSS (`~162-278`). The whole change except the two below.
- `eval/test_topbar_masthead.py` — **new** string-level regression guard (matches `test_wind_removed.py` / `test_freshness_ui.py` convention).
- `sw.js:1` — bump `CACHE_NAME` `gg-tank-v19` → `gg-tank-v20` so returning users get the new shell.

---

## Task 1: Regression guard (RED first)

**Files:**
- Test: `eval/test_topbar_masthead.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Regression guard: the topbar is a left-axis masthead (2026-05-31).

The UNOFFICIAL pill, wordmark, and "Last updated..." dateline share one left
axis (pill -> wordmark -> dateline), with share/theme controls pinned top-right.
This replaced the old layout where the freshness line was right-aligned on its
own row (the orphan the user flagged) and a flex-wrap trick kept controls pinned.
Pure text guards; no JS runtime needed (the harness has none).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Tokens that MUST be present after the masthead refactor.
REQUIRED = (
    "topbar--masthead",                              # masthead refactor marker
    "topbar-lead-row",                               # pill+wordmark wrapper
    "unofficial-pill",                               # pill kept (load-bearing trust signal)
    ">UNOFFICIAL<",                                  # pill text kept
    "min-width: 44px",                               # theme-toggle touch target kept
    'id="updated-text"',                             # freshness id kept (JS binds here)
    '"updated.freshness": { en: "Last updated',      # honest label kept
)

# Tokens that must NO LONGER appear (the orphan layout + the dead spacer).
FORBIDDEN = (
    "text-align: right; overflow: visible",          # old right-aligned mobile freshness rule
    "topbar-spacer",                                 # orphaned element removed
)


def test_masthead_tokens_present():
    """All masthead structure + preserved load-bearing tokens are present."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing = [tok for tok in REQUIRED if tok not in text]
    return {
        "passed": not missing,
        "details": "masthead structure + kept tokens present"
        if not missing
        else "required token(s) missing: " + " | ".join(missing),
        "metrics": {"missing": len(missing)},
    }


def test_orphan_freshness_layout_removed():
    """The right-aligned freshness orphan rule and the dead spacer are gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "orphan freshness layout + spacer removed"
        if not survivors
        else "forbidden token(s) still present: " + " | ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_dateline_is_inside_lead_before_controls():
    """Source order proves the dateline is part of the left identity cluster:
    lead-row (pill+wordmark) -> freshness dateline -> controls."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i_leadrow = text.find("topbar-lead-row")
    i_fresh = text.find('id="updated-text"')
    i_controls = text.find("topbar-controls")
    ok = -1 < i_leadrow < i_fresh < i_controls
    return {
        "passed": ok,
        "details": "order: lead-row < dateline < controls"
        if ok
        else f"bad source order leadrow={i_leadrow} fresh={i_fresh} controls={i_controls}",
        "metrics": {"leadrow": i_leadrow, "fresh": i_fresh, "controls": i_controls},
    }
```

- [ ] **Step 2: Run test to verify it FAILS**

Run: `python eval/run_all.py --only test_topbar_masthead`
Expected: FAIL — `topbar--masthead`/`topbar-lead-row` missing (REQUIRED) and `text-align: right; overflow: visible` + `topbar-spacer` still present (FORBIDDEN).

---

## Task 2: Masthead HTML + CSS (GREEN)

**Files:**
- Modify: `dashboard.html:1404-1417` (header markup), `dashboard.html:162-278` (topbar CSS)

- [ ] **Step 3: Replace the header markup** (`dashboard.html:1404-1417`)

```html
    <header class="topbar topbar--masthead">
      <div class="topbar-lead">
        <div class="topbar-lead-row">
          <span class="unofficial-pill" id="unofficial-pill" data-i18n="topbar.unofficial" data-i18n-title="topbar.unofficial.title" title="Volunteer-made — not an official government source">UNOFFICIAL</span>
          <span class="topbar-wordmark">GG <span class="topbar-wordmark-tank">Tank</span> Watch</span>
        </div>
        <span class="topbar-freshness" id="updated-text"><span id="freshness-label" data-i18n="updated.loading">loading...</span></span>
      </div>
      <div class="topbar-controls">
        <button id="share-btn" class="topbar-btn" type="button" aria-label="Share this page" title="Share">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
        </button>
        <button class="topbar-btn" id="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme" title="Toggle theme">&#x1F319;</button>
      </div>
    </header>
```
Changes vs current: header gains `topbar--masthead`; `<span class="topbar-spacer"></span>` deleted; pill+wordmark wrapped in `.topbar-lead-row`; `.topbar-freshness` moved inside `.topbar-lead` after the row. All ids/attrs/svg/onclick unchanged.

- [ ] **Step 4: Replace the topbar layout CSS** (`dashboard.html:162-249`, i.e. `.topbar` through the old `@media (max-width:599px)` block and the `@media (min-width:768px) .topbar-freshness` rule). Replace those rules with:

```css
    /* ===== TOPBAR (masthead) ===== */
    .topbar {
      position: relative;
      display: flex;
      align-items: flex-start;      /* masthead: top-align lead column + controls */
      gap: 8px;
      padding: 10px 14px;
      background: var(--sa-surface);
      border-bottom: 1px solid var(--sa-border);
      flex-shrink: 0;
      min-height: 56px;
      font-size: 13px;
    }
    @media (min-width: 600px) { .topbar { order: -1; } }
    @media (min-width: 768px) { .topbar { gap: 14px; padding: 10px 22px; } }
    /* lead = left identity column: [pill + wordmark] over [dateline] */
    .topbar-lead {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 3px;
      min-width: 0;
      flex: 1 1 auto;
    }
    .topbar-lead-row {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .unofficial-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 6px;
      border-radius: 4px;
      background: var(--sa-gold-2);
      border: 1px solid var(--sa-gold);
      color: var(--sa-gold);
      font-family: "IBM Plex Mono", monospace;
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.08em;
      white-space: nowrap;
      cursor: help;
      flex: 0 0 auto;
    }
    @media (min-width: 768px) { .unofficial-pill { padding: 4px 8px; } }
    .topbar-wordmark {
      font-weight: 800;
      font-size: 15px;
      letter-spacing: -0.01em;
      color: var(--sa-text);
      white-space: nowrap;
      flex: 0 0 auto;
    }
    @media (min-width: 768px) { .topbar-wordmark { font-size: 16.5px; } }
    .topbar-wordmark-tank { color: var(--sa-celadon); }
    /* freshness = left-aligned dateline under the wordmark, all widths */
    .topbar-freshness {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-width: 0;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      font-family: "IBM Plex Mono", monospace;
      font-size: 10.5px;
      color: var(--sa-text-2);
      white-space: nowrap;
    }
    @media (min-width: 768px) { .topbar-freshness { font-size: 11.5px; } }
    @media (max-width: 599px) {
      /* narrow: wordmark drops to its own line below the pill */
      .topbar-lead-row { flex-wrap: wrap; gap: 4px 8px; }
      .topbar-lead-row .topbar-wordmark { flex: 0 0 100%; }
    }
```
Deleted in this replace: `.topbar-spacer { flex: 1 1 auto; }` (line 213) and its comment; `.topbar-lead { display: contents; }` (line 215); the entire old `@media (max-width: 599px)` block (lines 229-246) including `text-align: right`, `order:1`, the `flex:1 1 0` trick, `flex:0 0 100%`, and `.unofficial-pill { white-space: normal }`. Leave `.topbar-btn`, `#theme-toggle`, and `.topbar-controls` rules (lines 250-278) unchanged.

- [ ] **Step 5: Run the regression test — verify it PASSES**

Run: `python eval/run_all.py --only test_topbar_masthead`
Expected: PASS (3/3).

- [ ] **Step 6: Run the full eval suite — verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: all behavioral guards pass, including `test_freshness_ui` (label string untouched) and `test_map_reload_regressions`. Do NOT use `--quiet` (it hides `[FAIL]` lines).

---

## Task 3: Service-worker cache bump

**Files:**
- Modify: `sw.js:1`

- [ ] **Step 7: Bump CACHE_NAME**

```javascript
var CACHE_NAME = "gg-tank-v20";
```
(was `gg-tank-v19`). Required so returning users get the new shell — `sw.js` is cache-first on `dashboard.html`.

---

## Task 4: Visual verify + commit

- [ ] **Step 8: Visual verify** — render `dashboard.html` via Edge headless (browse.exe is SAC-blocked) at narrow (≤599) and desktop (≥768), light + dark; confirm pill→wordmark→dateline on one left axis, controls pinned top-right, no clipping of the long "Last updated…" string, theme toggle ≥44px. (Use the same Edge headless invocation already used for the preview.)

- [ ] **Step 9: Branch + commit** (project rule: never push main directly)

```bash
git checkout -b feat/header-masthead
git add dashboard.html eval/test_topbar_masthead.py sw.js
git commit -m "feat(topbar): masthead layout — pill/wordmark/dateline on one left axis"
```
Then open a PR (do not merge to main directly). Stage explicit paths only.

---

## Failure modes

| Codepath | Failure | Covered? |
|---|---|---|
| Narrow controls pinning | controls wrap to row 2 | Non-wrapping row prevents it; visual-verify Step 8 confirms |
| Long freshness string | clips/overflows | `max-width:100%` + `text-overflow:ellipsis`; Step 8 confirms |
| Returning user cache | old shell served | `sw.js` CACHE_NAME bump (Task 3) |
| Label honesty | `"updated.freshness"` string lost | preserved; `test_freshness_ui` stays green (Step 6) |

## NOT in scope
- Pill/dateline typography swap (Option C, off-mono) — deferred; brand change, not layout.
- Desktop-only or narrow-only variants (Option A) — superseded by user's Option B choice.
- Any non-English copy — out by G1.

## What already exists (reused, not rebuilt)
- The topbar renders in place — this refactors its layout only.
- `test_freshness_ui.py` already guards label honesty (`"updated.freshness"`, `relativeAge`, `data_as_of_iso`, `.banner-stale`) — untouched and stays green.
- `eval/run_all.py` auto-discovers `test_*.py` — the new guard needs no registration.

## Parallelization
Sequential implementation, no parallelization opportunity (single file is the bulk of the change).
