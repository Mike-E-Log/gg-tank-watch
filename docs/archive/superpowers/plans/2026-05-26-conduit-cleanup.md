# Conduit Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the address checker and computed severity from dashboard.html, making the dashboard a pure information conduit (no functional output that creates negligent-undertaking liability).

**Architecture:** Four surgical passes on dashboard.html (remove Check HTML, refactor hero, remove checker JS, update CSP), plus eval test cleanup and doc updates. The dashboard drops from 3750 to ~3400 lines. Tabs go from Map/News/Check/Info to Map/News/Info.

**Tech Stack:** Single-file HTML, Python eval harness, Vercel static hosting.

---

## File Map

| File | Changes |
|------|---------|
| `dashboard.html` | Remove Check tab HTML + hero-check-inline + Check tab button; refactor hero from severity label to factual status; remove ~250 lines of address-checker JS (geocodeAddress through checkTabUseLocation); remove severity computation vars; update renderHeroSplit; remove Nominatim references |
| `vercel.json` | Remove `nominatim.openstreetmap.org` from CSP connect-src |
| `eval/test_safety.py` | Remove 4 math tests (haversine, polygon, distance, facility). Keep 2 conduit tests |
| `config.json` | Remove `geocode_bias` and `geocode_viewbox` if present |

---

### Task 1: Remove Check tab HTML and hero address checker

**Files:**
- Modify: `dashboard.html`

This task removes the Check tab panel, the hero inline address checker, and the Check button from the tab bar. No JS changes yet.

- [ ] **Step 1: Remove the hero inline address checker block (lines 1902-1911)**

Delete the entire `<div class="hero-check-inline">` block. Find and remove:

```html
    <div class="hero-check-inline">
      <form onsubmit="event.preventDefault(); checkTabAddress(document.getElementById('hero-inline-input').value.trim());">
        <label class="hero-check-label" data-i18n="check.prompt">Check your address</label>
        <div class="hero-check-row">
          <input id="hero-inline-input" type="text" placeholder="e.g. Magnolia &amp; Talbert" data-i18n-placeholder="check.placeholder" autocomplete="off">
          <button type="submit" data-i18n="check.btn">Check</button>
        </div>
      </form>
      <div class="hero-check-verdict" id="hero-inline-verdict" role="status" aria-live="polite"></div>
    </div>
```

- [ ] **Step 2: Remove the Check tab panel (lines 1958-1984)**

Delete the entire `<div class="tab-panel" id="panel-check">` block:

```html
      <div class="tab-panel" id="panel-check" role="tabpanel" aria-labelledby="tab-check">
        <div class="check-layout">
          ...entire check layout...
        </div>
      </div>
```

- [ ] **Step 3: Remove the Check button from the tab bar (lines 2000-2003)**

Delete this button from the `<nav class="tab-bar">`:

```html
      <button class="tab-btn" role="tab" id="tab-check" aria-selected="false" aria-controls="panel-check" data-tab="check" onclick="switchTab('check')">
        <svg class="tab-btn-icon-svg" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <span class="tab-btn-label" data-i18n="tab.check">Check</span>
      </button>
```

- [ ] **Step 4: Remove Check-related CSS classes**

Search for and remove these CSS rule blocks (they'll be in the `<style>` section near the top):
- `.check-layout` and all `.check-*` classes (check-left, check-right, check-header, check-subtitle, check-input-group, check-input, check-submit-btn, check-location-btn, check-location-dot, check-recent-header, check-recent-list, check-recent-item, check-recent-dot, check-recent-addr, check-recent-time, check-verdict-card, check-verdict-header, check-verdict-addr, check-verdict-label, check-verdict-distance, check-verdict-miles, check-verdict-unit, check-verdict-note, check-view-map-btn, check-empty-state)
- `.hero-check-inline` and related classes (hero-check-label, hero-check-row, hero-check-verdict)

Use grep to find them: `grep -n "\.check-\|\.hero-check" dashboard.html | head -50`

- [ ] **Step 5: Verify the page still has 3 tabs (Map, News, Info)**

Run: `grep -c "tab-btn" dashboard.html`
Expected: 3 tab buttons remain (map, news, info).

Run: `grep -c "panel-check\|hero-check-inline\|check-tab-form" dashboard.html`
Expected: 0 (all check HTML removed).

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "refactor(conduit): remove address checker UI (Check tab + hero checker)"
```

---

### Task 2: Refactor hero to factual status board

**Files:**
- Modify: `dashboard.html`

Replace the severity-label hero with a factual status board showing data from status.json.

- [ ] **Step 1: Replace the hero HTML**

Find the `<section class="hero-split" id="hero">` block (starts around line 1876, ends with `</section>` around line 1900). Replace it with a factual status board:

```html
    <section class="hero-status" id="hero">
      <div class="hero-status-row">
        <div class="hero-status-item">
          <span class="hero-status-label" data-i18n="hero.status.evacuation">Evacuation</span>
          <span class="hero-status-value" id="hero-evac-status">--</span>
        </div>
        <div class="hero-status-item">
          <span class="hero-status-label" data-i18n="hero.status.residents">Residents affected</span>
          <span class="hero-status-value" id="hero-res-count">--</span>
        </div>
        <div class="hero-status-item">
          <span class="hero-status-label" data-i18n="hero.status.tankTemp">Tank temp</span>
          <span class="hero-status-value" id="hero-tank-temp">--</span>
        </div>
        <div class="hero-status-item">
          <span class="hero-status-label" data-i18n="hero.status.day">Day</span>
          <span class="hero-status-value" id="hero-day-counter">--</span>
        </div>
      </div>
    </section>
```

- [ ] **Step 2: Add CSS for the new hero**

Remove the old hero-split CSS classes (hero-split, hero-split-left, hero-split-right, hero-split-left-header, hero-split-right-header, hero-severity-word, hero-res-row, hero-res-count, hero-res-label, hero-bullet, hero-bullet-dash, hero-bullet-text, hero-day-counter) and add:

```css
    .hero-status { padding: 12px 16px; border-bottom: 1px solid var(--sa-border); }
    .hero-status-row { display: flex; gap: 16px; flex-wrap: wrap; justify-content: space-between; }
    .hero-status-item { display: flex; flex-direction: column; gap: 2px; min-width: 80px; }
    .hero-status-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--sa-text-3); font-family: "IBM Plex Mono", monospace; }
    .hero-status-value { font-size: 18px; font-weight: 700; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; color: var(--sa-text); }
```

- [ ] **Step 3: Add i18n strings for the new hero labels**

Add to the STRINGS object:

```javascript
  "hero.status.evacuation": { en: "Evacuation", vi: "Sơ tán", es: "Evacuación" },
  "hero.status.residents": { en: "Residents affected", vi: "Cư dân bị ảnh hưởng", es: "Residentes afectados" },
  "hero.status.tankTemp": { en: "Tank temp", vi: "Nhiệt độ bồn", es: "Temp. tanque" },
  "hero.status.day": { en: "Day", vi: "Ngày", es: "Día" },
```

- [ ] **Step 4: Rewrite `renderHeroSplit` to populate factual data**

Replace the entire `renderHeroSplit` function (and the SEVERITY_WORDS, SEVERITY_RES_COUNTS, SEV_COLOR_VARS constants above it) with a simpler `renderHeroStatus` function:

```javascript
function renderHeroStatus(snap) {
  var evac = (snap && snap.evacuation) || {};
  var tank = (snap && snap.tank) || {};
  var incident = (snap && snap.incident) || {};

  var evacStatus = $("hero-evac-status");
  if (evacStatus) {
    if (evac.lifted) {
      evacStatus.textContent = t("hero.status.lifted") || "Lifted";
    } else {
      evacStatus.textContent = t("hero.status.active") || "Active";
    }
  }

  var count = $("hero-res-count");
  if (count) count.textContent = evac.residents != null ? fmtNumber(evac.residents) : "--";

  var temp = $("hero-tank-temp");
  if (temp) temp.textContent = tank.temp_f != null ? tank.temp_f + "°F" : "--";

  var dayCounter = $("hero-day-counter");
  if (dayCounter) dayCounter.textContent = incident.day_count || "--";
}
```

Also add the i18n strings for evacuation status:

```javascript
  "hero.status.active": { en: "Active", vi: "Đang diễn ra", es: "Activa" },
  "hero.status.lifted": { en: "Lifted", vi: "Đã dỡ bỏ", es: "Levantada" },
```

- [ ] **Step 5: Update all call sites from `renderHeroSplit(sev, snap)` to `renderHeroStatus(snap)`**

There are two call sites. Find each and update:

1. In `applyLang()` (~line 2267-2268):
   Change: `var sev = (lastSnap.incident && lastSnap.incident.severity) || "low"; renderHeroSplit(sev, lastSnap);`
   To: `renderHeroStatus(lastSnap);`

2. In `render(snap)` (~line 3603-3604):
   Change: `var sev = (snap.incident && snap.incident.severity) || "low"; renderHeroSplit(sev, snap);`
   To: `renderHeroStatus(snap);`

- [ ] **Step 6: Remove the HERO_BULLETS constant**

Search for `var HERO_BULLETS = {` and remove the entire object (it's a large multi-line object containing severity-keyed bullet text). It's no longer used.

- [ ] **Step 7: Remove severity-related CSS**

Remove CSS classes: `.sa-sev-low`, `.sa-sev-moderate`, `.sa-sev-high`, `.sa-sev-critical`, `.sa-sev-resolved` and related color definitions that only served the severity label.

- [ ] **Step 8: Verify**

Run: `grep -c "SEVERITY_WORDS\|SEVERITY_RES_COUNTS\|SEV_COLOR_VARS\|renderHeroSplit\|HERO_BULLETS" dashboard.html`
Expected: 0

Run: `grep -c "renderHeroStatus" dashboard.html`
Expected: 3 (definition + 2 call sites)

- [ ] **Step 9: Commit**

```bash
git add dashboard.html
git commit -m "refactor(conduit): replace severity hero with factual status board"
```

---

### Task 3: Remove address-checker JS and Nominatim

**Files:**
- Modify: `dashboard.html`
- Modify: `vercel.json`

- [ ] **Step 1: Remove address-checker JS functions**

Remove these functions and their supporting code (roughly lines 2638-2888):
- `geocodeAddress` (and the nested `nominatim` function)
- `computeSafety`
- `renderSafetyResult`
- `translateErrorMessage`
- `getCheckHistory`, `saveCheckHistory`
- `verdictFromResult`, `renderCheckVerdict`, `renderCheckRecent`
- `checkTabAddress`
- `rerunCheck`
- `checkTabUseLocation`

Also remove `restoreHeroInlineCheck` (near line 3713) and its call in the kickoff section (line 3737: `restoreHeroInlineCheck();`).

Also remove the `heroCheckSafety` and `restoreHeroCheck` functions (near line 2700).

Keep the `/* ============ NEWS FILTER ============ */` section and everything after it intact.

Also remove the `translateSafetyResult` function if it exists (search for it).

Also remove the `safetyPin` and `safetyPinBuffer` variable declarations (search for `var safetyPin`).

Also remove the `geocodeCacheGet` and `geocodeCacheSet` functions if they exist.

- [ ] **Step 2: Remove address-checker i18n strings**

Remove from the STRINGS object all keys starting with:
- `check.*` (check.prompt, check.sub, check.placeholder, check.btn, check.loading, check.error, check.lastChecked, check.fromTank, check.viewOnMap, check.useLocation, check.recent)
- `hero.check.*` (hero.check.label, hero.check.placeholder, hero.check.button)
- `hero.verdict.*` (hero.verdict.inside, hero.verdict.outside, hero.verdict.loading, hero.verdict.error)
- `verdict.*` (verdict.inside, verdict.outside, verdict.blast20, verdict.blastMod, verdict.note)
- `tab.check`

Keep: `hero.status.*` strings (added in Task 2).

- [ ] **Step 3: Remove address checker references from render() and other functions**

Search for any remaining references to `checkTabAddress`, `computeSafety`, `geocodeAddress`, `renderSafetyResult`, `renderCheckRecent`, `safetyPin`, `safetyPinBuffer` in the rest of the file and clean them up. Common locations:

- The `render()` function may call `renderCheckRecent()` -- remove that call.
- The desktop layout code may reference address checker elements -- remove those references.

- [ ] **Step 4: Remove Nominatim from CSP in vercel.json**

In `vercel.json`, update the CSP connect-src directive to remove `https://nominatim.openstreetmap.org`:

Change:
```
connect-src 'self' https://nominatim.openstreetmap.org https://api.weather.gov https://api.microlink.io
```
To:
```
connect-src 'self' https://api.weather.gov https://api.microlink.io
```

- [ ] **Step 5: Verify clean removal**

Run: `grep -c "nominatim\|geocodeAddress\|computeSafety\|checkTabAddress\|renderSafetyResult\|safetyPin" dashboard.html`
Expected: 0

Run: `grep -c "nominatim" vercel.json`
Expected: 0

Run: `python -m json.tool vercel.json`
Expected: valid JSON

- [ ] **Step 6: Commit**

```bash
git add dashboard.html vercel.json
git commit -m "refactor(conduit): remove address checker JS, Nominatim dependency, and CSP entry"
```

---

### Task 4: Update eval tests, config, and docs

**Files:**
- Modify: `eval/test_safety.py`
- Modify: `config.json` (if geocode_bias/geocode_viewbox exist)

- [ ] **Step 1: Remove 4 math tests from test_safety.py**

Remove these functions and all supporting code (haversine, bearing, point-in-polygon, compute_safety):
- `test_facility_itself_is_near_zero_distance`
- `test_inside_evac_polygon_detected`
- `test_outside_evac_polygon_detected`
- `test_haversine_known_distance`

Also remove the helper functions that only these tests use:
- `_haversine_mi`
- `_bearing_deg`
- `_point_in_polygon`
- `compute_safety`
- `_load_config`

Keep these two tests (they verify conduit principles against dashboard.html):
- `test_no_authored_hazard_verdict`
- `test_checker_routes_to_official`

The kept tests open `dashboard.html` directly and grep for banned strings / required URLs. They don't depend on any of the removed helper functions.

The resulting `test_safety.py` should be ~20 lines:

```python
"""Conduit-principle tests for dashboard.html.

Verifies the dashboard does not contain authored hazard verdicts
and routes users to official sources.
"""

CATEGORY = "behavioral"


def test_no_authored_hazard_verdict():
    html = open("dashboard.html", encoding="utf-8").read()
    banned = ["within injury radius or plume", "blast_zones_mi", "layers.plume", "ELEVATED — within injury radius"]
    found = [b for b in banned if b in html]
    assert not found, f"authored-hazard remnants still present: {found}"


def test_checker_routes_to_official():
    html = open("dashboard.html", encoding="utf-8").read()
    assert "ggcity.org/emergency" in html, "dashboard must route to official source"
```

- [ ] **Step 2: Remove geocode config from config.json (if present)**

Check if `config.json` contains `geocode_bias` or `geocode_viewbox` keys under the `map` object. If so, remove them. These were only used by the address checker.

Run: `grep "geocode" config.json`

If matches found, remove those keys.

- [ ] **Step 3: Run the eval suite**

Run: `python eval/run_all.py --skip integration`
Expected: 42/42 pass (100%). The 4 removed math tests reduce the count from 46 to 42.

- [ ] **Step 4: Commit**

```bash
git add eval/test_safety.py config.json
git commit -m "refactor(eval): remove address-checker math tests, keep conduit-principle tests"
```

---

## NOT in scope

- Removing the map visualization (the Leaflet map stays -- it shows the evacuation polygon from official sources, not a computed verdict)
- Removing the wind overlay (factual data from NOAA weather.gov)
- Removing the timeline (factual events from verified sources)
- Updating LEGAL.md or DISTRIBUTION.md (follow-up: these docs reference the address checker but are reference material, not live code)
- Removing the evacuation polygon from config.json (still used by the map)

## What already exists

- The factual data (tank temp, resident count, evacuation status, day count) is already in `status.json` and already rendered in the topbar/info sections. The hero refactor surfaces it more prominently.
- The safety strip, UNOFFICIAL pill, and terms.html already establish the conduit posture. This cleanup removes the features that contradicted it.
