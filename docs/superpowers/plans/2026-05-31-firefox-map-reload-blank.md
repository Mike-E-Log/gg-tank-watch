# Firefox-Mobile Blank-Map-on-Reload Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the live MapLibre map from rendering blank after a reload on mobile Firefox, and remove a co-occurring `ReferenceError` that silently halts the wind auto-refresh.

**Architecture:** Single-file static dashboard (`dashboard.html`) + cache-first service worker (`sw.js`), Vercel static hosting, Python pytest-style eval harness (no JS runtime). Root cause was confirmed from a live Firefox-mobile console, then fixed test-first against the eval harness with static-source guards (the only automated coverage available for SW/JS in this repo).

**Tech Stack:** Vanilla JS + MapLibre GL JS 4.7.1 (self-hosted) + OpenFreeMap vector tiles, service-worker cache, Python 3 stdlib eval harness (`eval/run_all.py`).

**Status:** Tasks 1–2 implemented + committed (`a1b07ab` on branch `fix/firefox-map-reload-blank`), eval **53/53**. Task 3 (push + on-device verify) pending. Task 4 is a contingency, only if Task 3 shows residual blanking.

---

## Root cause (confirmed, not inferred)

Live Firefox-mobile console on reload:

```
Failed to load 'https://tiles.openfreemap.org/fonts/Noto Sans Regular/0-255.pbf'.
A ServiceWorker passed a promise to FetchEvent.respondWith() that rejected with
'TypeError: NetworkError when attempting to fetch resource.'.   sw.js:74:9
Cross-Origin Request Blocked ... (Reason: CORS request did not succeed). Status code: (null).
Uncaught (in promise) ReferenceError: fixedPointMarkers is not defined
    recolorFixedPoints  .../:2429   refreshWind  .../:2424   loadConfig  .../:2756
```

- **Primary:** `sw.js:74` wrapped every cross-origin request in `event.respondWith(fetch(event.request))`. The SW only controls the page *after* the first load, so a fresh load worked but a reload routed OpenFreeMap's style/tile/glyph fetches through the SW; Firefox rejects that re-dispatched cross-origin fetch (CORS NetworkError) with no native fallback → blank map.
- **Secondary:** `recolorFixedPoints()` is dead code from the pre-MapLibre Leaflet map; it references a removed `fixedPointMarkers` global and throws every load in `refreshWind()` before `scheduleWindRefresh()` runs → wind indicator stops auto-refreshing.
- **Ruled out:** the self-hosted `maplibre-gl.js` loaded fine (only a benign `.map` source-map 404), and WebGL was actively rendering (`WebGL warning:` lines, not errors) → not a corrupt-lib (H1) or WebGL-context (H3) failure.

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `sw.js` | Service-worker cache + fetch routing | Stop intercepting cross-origin; bump `CACHE_NAME` |
| `dashboard.html` | The whole UI incl. `refreshWind()` / map init | Remove orphaned `recolorFixedPoints()` (call + def) |
| `eval/test_map_reload_regressions.py` | NEW static guards locking both fixes | Create |

---

## Task 1: Service-worker cross-origin fix (DONE — `a1b07ab`)

**Files:**
- Modify: `sw.js:1` (`CACHE_NAME`), `sw.js:73-74` (cross-origin handler)
- Test: `eval/test_map_reload_regressions.py` (`test_sw_does_not_intercept_cross_origin`)

- [x] **Step 1: Write the failing guard** in `eval/test_map_reload_regressions.py`:

```python
def test_sw_does_not_intercept_cross_origin():
    norm = "".join(SW.read_text(encoding="utf-8").split())
    bad = "event.respondWith(fetch(event.request))" in norm
    return {
        "passed": not bad,
        "details": "cross-origin requests fall through to native browser fetch"
        if not bad else
        "sw.js still wraps cross-origin requests in respondWith(fetch(event.request)) "
        "(rejects on Firefox -> map blanks on reload)",
        "metrics": {"blanket_intercept": int(bad)},
    }
```

- [x] **Step 2: Run it — verify RED**

Run: `python eval/run_all.py --only test_map_reload_regressions --skip integration`
Expected: `[FAIL] ... test_sw_does_not_intercept_cross_origin` (blanket intercept present).

- [x] **Step 3: Implement** — replace `sw.js:73-74`:

```javascript
  // Cross-origin requests (OpenFreeMap map style/tiles/glyphs/sprites, NOAA wind,
  // fonts): do NOT intercept. Falling through without event.respondWith() lets the
  // browser fetch them natively. Wrapping them in respondWith(fetch(event.request))
  // made the service worker the failure point: Firefox rejects the re-dispatched
  // cross-origin fetch ("CORS request did not succeed" / NetworkError), so the map
  // style + glyph tiles never loaded and the map blanked on reload — but only on
  // reload, because the SW does not control the page until after the first load.
});
```

And bump the cache at `sw.js:1`: `var CACHE_NAME = "gg-tank-v14";` → `"gg-tank-v15";`

- [x] **Step 4: Run it — verify GREEN.** `[PASS] test_sw_does_not_intercept_cross_origin`.

---

## Task 2: Remove orphaned Leaflet `recolorFixedPoints` (DONE — `a1b07ab`)

**Files:**
- Modify: `dashboard.html:2424` (call), `dashboard.html:2428-2438` (dead function)
- Test: `eval/test_map_reload_regressions.py` (`test_no_orphaned_leaflet_marker_code`)

- [x] **Step 1: Write the failing guard:**

```python
def test_no_orphaned_leaflet_marker_code():
    text = DASHBOARD.read_text(encoding="utf-8")
    found = [s for s in ("fixedPointMarkers", "recolorFixedPoints") if s in text]
    return {
        "passed": not found,
        "details": "no orphaned Leaflet marker references" if not found
        else "orphaned Leaflet symbols still present: " + ", ".join(found),
        "metrics": {"orphaned_refs": len(found)},
    }
```

- [x] **Step 2: Run it — verify RED.** `[FAIL] ... orphaned Leaflet symbols still present: fixedPointMarkers, recolorFixedPoints`.

- [x] **Step 3: Implement** — delete the call line in `refreshWind()`:

```javascript
  updateWindDisplay(lastWind);
  scheduleWindRefresh();   // recolorFixedPoints() removed
}
```

and delete the entire `function recolorFixedPoints() { ... }` block (it used Leaflet `m.setStyle`/`m.setTooltipContent`/`m.__fp`, none of which exist on MapLibre markers). Leave `cardinalFromDeg` (used by the wind display) and `pointInPolygon` (separate pre-existing dead code from the removed address-checker — a future `chore:` sweep, not this fix).

- [x] **Step 4: Run full suite — verify GREEN, no regression.**

Run: `python eval/run_all.py --skip integration`
Expected: `TOTAL 53/53`, exit 0. Plus `node --check sw.js` and an inline-`<script>` parse check both clean.

- [x] **Step 5: Commit (staging explicit paths only):**

```bash
git add sw.js dashboard.html eval/test_map_reload_regressions.py
git commit -m "fix(map): stop SW intercepting cross-origin tiles (Firefox blank-map-on-reload)"
```

---

## Task 3: Push, open PR, on-device verify (PENDING — required)

> This is the real verification step: the bug is Firefox-mobile-specific and cannot be reproduced from the Windows/Chromium dev box, so the founder confirms on an actual device via the Vercel preview. Production merge stays gated on explicit "merge".

- [ ] **Step 1: Push the branch**

Run: `git push -u origin fix/firefox-map-reload-blank`

- [ ] **Step 2: Open the PR (do NOT merge — await explicit "merge")**

```bash
gh pr create --title "fix: Firefox-mobile blank map on reload (SW cross-origin) + dead wind-recolor ref" \
  --body "<problem / approach / test plan / risk / rollback — see template below>"
```

PR body:
- **Problem:** On mobile Firefox the map is blank after reload (fine on first load). Confirmed cause: `sw.js:74` re-dispatched cross-origin OpenFreeMap fetches through `respondWith(fetch(event.request))`, which Firefox rejects (CORS NetworkError) once the SW controls the page on reload. Plus a `recolorFixedPoints` `ReferenceError` halting wind auto-refresh.
- **Approach:** Let cross-origin requests fall through to native browser fetch; bump SW cache v14→v15; remove the orphaned Leaflet `recolorFixedPoints`.
- **Test plan:** `eval/run_all.py --skip integration` → 53/53; two new static guards (`test_map_reload_regressions.py`); `node --check`; **founder reload on Firefox mobile via the preview URL — map must render and persist across reloads.**
- **Risk:** Low. SW no longer wraps external requests (it never cached them anyway). Cache bump forces a clean shell. Dashboard change is a pure dead-code deletion.
- **Rollback:** Revert the PR; the next SW cache bump (or v15→v16) propagates the rollback to cached users.

- [ ] **Step 3: Founder verifies on Firefox mobile**

Open the Vercel preview URL on the phone → load → reload 2–3× → confirm the map tiles render every time, and the Firefox console shows **no** `sw.js` respondWith rejections and **no** `fixedPointMarkers` ReferenceError.

- [ ] **Step 4: Merge on explicit "merge #N"** (auto-deploys `main` to the live site; `noindex` stays on).

---

## Task 4: WebGL context-loss hardening (CONTINGENCY — only if Task 3 still blanks)

> Do NOT implement preemptively. The console proved WebGL was rendering, so H3 is not the active cause. MapLibre GL 4.x already handles `webglcontextlost`/`restored` internally; adding our own handlers risks conflicting for zero confirmed benefit. Implement ONLY if, after Task 3, the map still intermittently blanks on reload/bfcache-restore on the founder's device.

**Files:** Modify `dashboard.html` inside the map IIFE, after `_ggMap = map;` (~`:2842`). Test: extend `eval/test_map_reload_regressions.py`.

- [ ] **Step 1: Reproduce + capture** the residual blank with a console error naming a lost/again-needed GL context (e.g. `webglcontextlost`). If no such error appears, STOP — the residual blank is a different bug; re-run `/investigate`.

- [ ] **Step 2: Write the failing guard** (asserts the handler is wired):

```python
def test_map_handles_webgl_context_loss():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = "webglcontextlost" in text and "webglcontextrestored" in text
    return {"passed": ok,
            "details": "GL context-loss handlers wired" if ok
            else "no webglcontextlost/restored handling in dashboard.html",
            "metrics": {"has_ctx_handlers": int(ok)}}
```

- [ ] **Step 3: Run it — verify RED.** `[FAIL] test_map_handles_webgl_context_loss`.

- [ ] **Step 4: Implement** — after `_ggMap = map;`:

```javascript
  var _glCanvas = map.getCanvas();
  _glCanvas.addEventListener("webglcontextlost", function (e) {
    e.preventDefault();            // permit restoration instead of permanent loss
  });
  _glCanvas.addEventListener("webglcontextrestored", function () {
    map.resize();                  // re-sync canvas dims
    map.triggerRepaint();          // force MapLibre to redraw on the restored context
  });
```

- [ ] **Step 5: Run suite — verify GREEN** (`python eval/run_all.py --skip integration` → all pass) + `node --check` inline scripts. Bump `sw.js` `CACHE_NAME` again (dashboard.html changed). Commit, push to the same branch, re-verify on device.

---

## Verification (every code task)

- `python eval/run_all.py --skip integration` → exit 0 (NEVER `--quiet`; it hides `[FAIL]`).
- `node --check sw.js` + inline-`<script>` parse check on `dashboard.html`.
- Founder real-device Firefox-mobile reload via the Vercel preview (the only place the Firefox/SW interaction is observable).

## Self-review

- **Spec coverage:** primary (SW blank) → Task 1; secondary (wind ReferenceError) → Task 2; on-device confirmation → Task 3; speculative WebGL → Task 4 (gated). No gaps.
- **Placeholders:** none — every code/command step shows actual content.
- **Type/name consistency:** guard names (`test_sw_does_not_intercept_cross_origin`, `test_no_orphaned_leaflet_marker_code`), `CACHE_NAME` string, and `recolorFixedPoints`/`fixedPointMarkers` symbols match across tasks and the committed code.

## Out of scope (deferred)

- Sweeping the remaining dead "SAFETY CHECK" helpers (`haversineMi`, `bearingDeg`, `pointInPolygon`) from the removed address-checker — a separate `chore:` per the repo's dead-code-sweep convention (`820fb4b`).
- `favicon.ico` 404 (cosmetic) and the `maplibre-gl.js.map` source-map 404 (benign devtools-only).
