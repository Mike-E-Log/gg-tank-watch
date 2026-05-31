# Remove Map Wind Indicator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the map wind indicator from GG Tank Watch — the overlay, its CSS, all wind JS, the weather-API call, the wind i18n keys — and guard the removal with an eval so wind cannot silently creep back.

**Architecture:** Pure deletion in a single-file static dashboard. The wind overlay is `position:absolute` over the MapLibre map, so removing it cannot shift layout or break map init. A new structural eval (`test_wind_removed.py`) asserts absence of every wind token; it is RED while wind exists and GREEN after the deletion (TDD for a removal). The service-worker cache name is bumped so returning users get the new shell.

**Tech Stack:** Static HTML/CSS/vanilla JS (`dashboard.html`), service worker (`sw.js`), Python eval harness (`eval/`, functions returning `{"passed","details","metrics"}` with a module-level `CATEGORY`).

**Why removed (decision record):** The reading came from one NOAA station, KFUL (Fullerton Airport, ~5.7 mi from the GKN tank). Measured against the nearest reporting station to the site, it pointed ≥90° the wrong way ~34% of the time (39% in the light-wind regime shown) and the site was calm/no-direction 53% of the time. On a no-directives safety conduit, a resident could misread the arrow as "which way the danger is blowing." Residents are routed to officials (NWS/AirNow) for authoritative wind/air quality. Cross-vendor judges + a 7-day empirical NOAA comparison backed removal over relabeling.

**Decisions locked (plan-eng-review):** D1 — remove the now-orphaned helpers `fmtAbsTime` + `cardinalFromDeg` (used only by the wind display). D2 — guard lives in a new file `eval/test_wind_removed.py` (repo convention: one concern per eval). NOT touched: `config.json` (no `weather_station` key present), `eval/test_map_reload_regressions.py` (its assertions are wind-independent), `zone_status` everywhere.

---

### Task 1: Add the failing regression guard (RED)

**Files:**
- Create: `eval/test_wind_removed.py`

- [ ] **Step 1: Write the guard test**

```python
"""Regression guard: the map wind indicator was removed (2026-05-31).

The reading came from a single NOAA station (KFUL, Fullerton Airport, ~5.7 mi
from the GKN tank). Against the nearest reporting station to the site it
pointed >=90deg the wrong way ~34% of the time (39% in light winds) and the
site was calm/no-direction 53% of the time -- a spatially-unrepresentative
direction a resident could misread as "which way the danger is blowing" on a
no-directives safety conduit. Residents are routed to officials (NWS/AirNow)
for authoritative wind/air quality.

These guards fail the build if any wind UI, JS, weather-API call, or wind i18n
key creeps back into dashboard.html. Pure text guards; no JS runtime needed
(the harness has none).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Tokens that must no longer appear anywhere in dashboard.html after removal.
# All are wind-specific substrings -- none is contained in "downwind"
# (the zone_status value), so this cannot false-positive on resident-zone copy.
FORBIDDEN = (
    # overlay markup + CSS
    "map-wind-overlay", "map-wind", "wind-arrow", "wind-text-map", "wind-source",
    # JS state + functions (incl. orphaned helpers per D1)
    "fetchWind", "refreshWind", "scheduleWindRefresh", "updateWindDisplay",
    "cardinalFromDeg", "lastObservationTime", "WIND_BASE_MS", "WIND_MAX_MS",
    # weather API call + station config lookup
    "api.weather.gov", "weather_station",
    # i18n keys
    "wind.source", "wind.disclaimer", "wind.unavailable", "info.method.wind",
)


def test_no_wind_indicator_in_dashboard():
    """No wind UI/JS/API/i18n may reappear in dashboard.html (removed 2026-05-31)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "no wind-indicator artifacts in dashboard.html"
        if not survivors
        else "wind artifact(s) still present (should be removed): " + ", ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_map_aria_label_has_no_wind_claim():
    """The map aria-label must not advertise a wind-direction marker anymore."""
    text = DASHBOARD.read_text(encoding="utf-8")
    bad = "wind direction" in text.lower()
    return {
        "passed": not bad,
        "details": "no 'wind direction' claim in dashboard.html"
        if not bad
        else 'dashboard.html still says "wind direction" (stale aria-label?)',
        "metrics": {"wind_direction_mentions": int(bad)},
    }
```

- [ ] **Step 2: Run the guard to verify it FAILS**

Run: `python eval/run_all.py --skip integration`
Expected: `test_no_wind_indicator_in_dashboard` and `test_map_aria_label_has_no_wind_claim` both `[FAIL]` — wind is still present. (Do NOT use `--quiet`; it hides `[FAIL]` lines.)

---

### Task 2: Delete the wind indicator from dashboard.html (GREEN)

**Files:**
- Modify: `dashboard.html` (multiple deletions below)

- [ ] **Step 1: Remove the `.wind-arrow-sm` CSS rule** (was ~:491-496)

Delete exactly:
```css
    .wind-arrow-sm {
      display: inline-block;
      width: 10px;
      height: 10px;
      transition: transform 0.4s ease;
    }

```

- [ ] **Step 2: Remove the `.map-wind` CSS block** (was ~:614-634)

Delete the six rules `.map-wind { ... }`, `.map-wind-reading`, `#wind-arrow-map`, `#wind-text-map`, `.wind-source` (from the line `.map-wind {` through the `.wind-source { ... }` line inclusive). Leave `.maplibregl-ctrl-group button { ... }` above and `.map-legend {` below untouched.

- [ ] **Step 3: Drop `.map-wind` from the print rule** (was ~:1383-1384)

Change:
```css
      .refresh-bar, .banners, .topbar-btn, .lang-picker,
      .map-wind, .map-legend, .skip-link { display: none !important; }
```
to:
```css
      .refresh-bar, .banners, .topbar-btn, .lang-picker,
      .map-legend, .skip-link { display: none !important; }
```

- [ ] **Step 4: Clean the map aria-label** (was :1493)

Change the `aria-label` end from `...with shelter locations and the current wind direction marked."` to `...with shelter locations marked."`. Full replacement target:
```html
          <div id="maplibre-map" role="img" aria-label="Map of the Garden Grove evacuation zone showing the approximate evacuation boundary around the GKN Aerospace facility, with shelter locations and the current wind direction marked."></div>
```
becomes:
```html
          <div id="maplibre-map" role="img" aria-label="Map of the Garden Grove evacuation zone showing the approximate evacuation boundary around the GKN Aerospace facility, with shelter locations marked."></div>
```

- [ ] **Step 5: Remove the wind overlay block** (was :1494-1500)

Delete exactly (the whole `#map-wind-overlay` div):
```html
          <div class="map-wind" id="map-wind-overlay" title="Weather data, not safety guidance">
            <div class="map-wind-reading">
              <svg class="wind-arrow-sm" id="wind-arrow-map" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1 L13 14 L8 11 L3 14 Z"/></svg>
              <span id="wind-text-map">--</span>
            </div>
            <span class="wind-source" data-i18n="wind.source">Wind — NOAA</span>
          </div>
```

- [ ] **Step 6: Remove the wind interval constants** (was :1565-1566)

Delete:
```js
var WIND_BASE_MS = 60000;
var WIND_MAX_MS = 480000;
```

- [ ] **Step 7: Remove the three wind i18n keys** (was :1576-1578)

Delete:
```js
  "wind.source": { en: "Wind — NOAA" },
  "wind.disclaimer": { en: "weather data, not safety guidance" },
  "wind.unavailable": { en: "Wind data unavailable" },
```

- [ ] **Step 8: Remove the `info.method.wind` i18n key** (was :1645)

Delete the single line:
```js
  "info.method.wind": { en: "<strong>Wind data:</strong> Live observations from NOAA station KFUL (Fullerton Municipal Airport), polled every 60 seconds." },
```

- [ ] **Step 9: Remove the wind JS state vars** (was :1808-1811)

Delete:
```js
var lastWind = null;
var windInterval = WIND_BASE_MS;
var windTimer = null;
var lastObservationTime = null;
```

- [ ] **Step 10: Remove the orphaned `fmtAbsTime` helper** (was :1883-1885, D1)

Delete (leave `fmtRelTime` above and `fmtAbsDateTime` below intact):
```js
function fmtAbsTime(iso) {
  return iso ? new Date(iso).toLocaleTimeString(currentLocale(), TIME_OPTS) : "—";
}
```

- [ ] **Step 11: Remove `updateWindDisplay` + `cardinalFromDeg` and their stale `MAP` section divider** (was :1977-2011, D1)

Delete from the divider comment through the end of `cardinalFromDeg` (the divider now heads nothing; the real MapLibre init lives elsewhere):
```js
/* ============ MAP (static image — no tile server dependency) ============ */

function updateWindDisplay(wind) {
  if (!wind) return;
  var heading = (wind.directionDeg + 180) % 360;
  ["wind-arrow", "wind-arrow-map"].forEach(function(id) {
    var el = $(id);
    if (el) {
      // F4: hide the directional arrow when there is no real observation (default fallback).
      el.style.visibility = wind.fallback ? "hidden" : "visible";
      el.style.transform = "rotate(" + heading + "deg)";
    }
  });
  var windCompact = cardinalFromDeg(wind.directionDeg) + "→" + cardinalFromDeg(heading) + " " + Math.round(wind.speedMph) + "mph";
  var el = $("wind-compact");
  if (el) el.textContent = windCompact;
  ["wind-text-map"].forEach(function(id) {
    var mapEl = $(id);
    if (mapEl) {
      if (wind.fallback) {
        // F4: the hardcoded default (NOAA fetch failed, no cached observation) must
        // never read as a live measurement. Show an explicit unavailable state.
        mapEl.textContent = t("wind.unavailable");
      } else {
        var obs = wind.observedAt ? " (obs " + fmtAbsTime(wind.observedAt) + ")" : "";
        mapEl.textContent = windCompact + obs;
      }
    }
  });
}

function cardinalFromDeg(deg) {
  var dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"];
  return dirs[Math.round(((deg % 360) / 22.5)) % 16];
}
```
Leave the `/* ============ SAFETY CHECK ============ */` divider that follows.

- [ ] **Step 12: Remove the `info.method.wind` render line** (was :2247)

Delete:
```js
  html += '<p>' + t("info.method.wind") + '</p>';
```

- [ ] **Step 13: Remove the entire WIND JS section** (was :2384-2425)

Delete from the `WIND` divider through the end of `refreshWind` (the divider + `fetchWind` + `scheduleWindRefresh` + `refreshWind`):
```js
/* ============ WIND ============ */
async function fetchWind(stationId) {
  try {
    var url = "https://api.weather.gov/stations/" + stationId + "/observations/latest";
    var resp = await fetch(url, {headers: {"User-Agent": "GG-Dashboard/1.0 (emergency-awareness)"}});
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    var data = await resp.json();
    var props = data.properties || {};
    var dirDeg = props.windDirection && props.windDirection.value;
    var spdKmh = props.windSpeed && props.windSpeed.value;
    if (dirDeg === null || dirDeg === undefined) throw new Error("no wind direction");
    var observedAt = props.timestamp;
    lastObservationTime = observedAt;
    var wind = {
      directionDeg: dirDeg,
      speedMph: spdKmh != null ? spdKmh * 0.621371 : 5,
      observedAt: observedAt,
      station: stationId
    };
    localStorage.setItem("gg-wind", JSON.stringify({wind: wind, fetchedAt: Date.now()}));
    windInterval = WIND_BASE_MS;
    return wind;
  } catch (e) {
    console.warn("wind fetch failed:", e);
    windInterval = Math.min(windInterval * 2, WIND_MAX_MS);
    var cached = JSON.parse(localStorage.getItem("gg-wind") || "null");
    return cached ? cached.wind : { directionDeg: 270, speedMph: 5, observedAt: null, station: stationId, fallback: true };
  }
}

function scheduleWindRefresh() {
  if (windTimer) clearTimeout(windTimer);
  windTimer = setTimeout(refreshWind, windInterval);
}

async function refreshWind() {
  if (!configCache) return;
  var stationId = (configCache.map && configCache.map.weather_station) || "KFUL";
  lastWind = await fetchWind(stationId);
  updateWindDisplay(lastWind);
  scheduleWindRefresh();
}
```
Leave the `/* ============ RESOURCES TAB ============ */` divider that follows.

- [ ] **Step 14: Remove the `refreshWind()` call in loadConfig** (was :2743)

Delete the single line (leave `renderInfoShelters();` above and `return configCache;` below):
```js
    refreshWind();
```

- [ ] **Step 15: Run the guard to verify it now PASSES**

Run: `python eval/run_all.py --skip integration`
Expected: `test_no_wind_indicator_in_dashboard` and `test_map_aria_label_has_no_wind_claim` both `[PASS]`.

---

### Task 3: Drop the dead wind keys from the English-only test

**Files:**
- Modify: `eval/test_language_access.py:79-82`

- [ ] **Step 1: Remove the 3 wind keys from `ENGLISH_ONLY_KEYS`**

Change:
```python
ENGLISH_ONLY_KEYS = {
    "share.copied", "wind.source", "wind.disclaimer", "wind.unavailable",
    "info.subtab.status", "info.subtab.resources", "info.subtab.about",
}
```
to:
```python
ENGLISH_ONLY_KEYS = {
    "share.copied",
    "info.subtab.status", "info.subtab.resources", "info.subtab.about",
}
```
(The keys no longer exist; `test_new_strings_english_only` would skip them anyway, but listing dead keys is stale — and they are the very keys this change removes, so this is in-scope orphan cleanup, not unrelated dead code.)

- [ ] **Step 2: Run the language-access suite to verify still green**

Run: `python eval/run_all.py --skip integration`
Expected: `test_english_only`, `test_no_unverified_language_ships`, `test_new_strings_english_only` all `[PASS]`.

---

### Task 4: Bump the service-worker cache

**Files:**
- Modify: `sw.js:1`

- [ ] **Step 1: Bump CACHE_NAME** (learning `sw-cache-bump-required`: cache-first shell; without a bump, returning users keep the old wind-bearing HTML)

Change:
```js
var CACHE_NAME = "gg-tank-v16";
```
to:
```js
var CACHE_NAME = "gg-tank-v17";
```

---

### Task 5: Full verification + commit

- [ ] **Step 1: Run the full eval suite**

Run: `python eval/run_all.py --skip integration`
Expected: exit code 0, scorecard all green, zero `[FAIL]` lines (verify by reading output, not `--quiet`).

- [ ] **Step 2: Visual sanity check (optional but recommended)**

Serve locally and confirm the map renders with no wind overlay (top-right corner clear), legend intact, no console errors. Per learning `edge-headless-375-actually-474`, use a `getBoundingClientRect` DOM probe rather than eyeballed crops if checking element positions.

- [ ] **Step 3: Commit (stage explicit paths only — never `git add -A`)**

```bash
git add dashboard.html sw.js eval/test_wind_removed.py eval/test_language_access.py docs/superpowers/plans/2026-05-31-remove-map-wind-indicator.md
git commit -m "feat(map): remove wind indicator (unrepresentative single-station reading)"
```

---

## NOT in scope
- `config.json` — no `weather_station` key present; the removed code fell back to the literal `"KFUL"`. Nothing to edit.
- `eval/test_map_reload_regressions.py` assertions — they guard Leaflet/SW orphans, wind-independent. Its docstring mentions `refreshWind()` as the 2026-05-31 symptom (now stale prose); left as history per §3 (P3).
- `zone_status: "outside_downwind"` — resident-zone field, unrelated to wind. Untouched everywhere.
- On-site wind sensor / plume model — the whole point is to route to officials.
- Purging the stale `gg-wind` localStorage key on old clients — self-limiting orphan data; YAGNI.

## What already exists
- The wind feature itself is the removal target (no reuse).
- The structural string-guard eval pattern in `test_map_reload_regressions.py` is the template reused for `test_wind_removed.py` (not rebuilt).

## Failure modes
- The only failure mode in the removed code was `fetchWind` network failure (handled today by a fallback arrow). Deleting the code deletes the failure mode. No new silent-failure paths introduced. No critical gaps.

## Parallelization
Sequential implementation, no parallelization opportunity — all edits center on `dashboard.html` and the evals depend on the removal being defined.
