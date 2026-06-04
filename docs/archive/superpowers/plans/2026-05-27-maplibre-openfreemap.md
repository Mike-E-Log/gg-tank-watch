# MapLibre GL JS + OpenFreeMap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the static JPEG + SVG overlay map with MapLibre GL JS vector tiles from OpenFreeMap for smooth WebGL-accelerated pan/zoom at zero cost.

**Architecture:** Load MapLibre GL JS v4.7.1 (UMD bundle via unpkg CDN) and point it at OpenFreeMap's Liberty style. The map reads evacuation polygon, facility, and shelter coordinates from `config.json` at runtime and renders them as GeoJSON layers. The existing wind overlay, legend, and "Check your zone" button stay as CSS overlays on top of the map container. The static JPEG images become unnecessary and are removed from the service worker cache.

**Tech Stack:** MapLibre GL JS 4.7.1 (BSD-3), OpenFreeMap tiles (MIT, no API key), GeoJSON polygon/marker layers.

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `dashboard.html` | Modify | Add MapLibre CSS/JS in `<head>`, replace map CSS (lines 581-718), replace map HTML (lines 1549-1591), replace map JS (lines 2848-3006) |
| `vercel.json` | Modify | Add tile/font/sprite domains to CSP `connect-src`, `img-src`, `script-src`, `style-src` |
| `sw.js` | Modify | Bump cache version to v6, remove hires image from pre-cache list |

---

### Task 1: Update CSP in vercel.json

**Files:**
- Modify: `vercel.json:11` (Content-Security-Policy header value)

MapLibre needs to fetch vector tiles, fonts (glyphs), and sprites from OpenFreeMap and unpkg CDN. Without CSP updates, tile requests will be silently blocked.

- [ ] **Step 1: Update the CSP header**

Add these domains:
- `script-src`: add `https://unpkg.com` (MapLibre JS)
- `style-src`: add `https://unpkg.com` (MapLibre CSS)
- `connect-src`: add `https://tiles.openfreemap.org` (tiles + style JSON)
- `img-src`: add `https://tiles.openfreemap.org` (sprite images)

The full updated CSP value:

```
default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; font-src https://fonts.gstatic.com; img-src 'self' data: https://img.youtube.com https://api.microlink.io https://tiles.openfreemap.org blob:; connect-src 'self' https://api.weather.gov https://api.microlink.io https://tiles.openfreemap.org; frame-src https://www.youtube.com https://www.youtube-nocookie.com
```

- [ ] **Step 2: Verify the JSON is valid**

Run: `python -c "import json; json.load(open('vercel.json')); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add vercel.json
git commit -m "chore: add MapLibre + OpenFreeMap domains to CSP"
```

---

### Task 2: Update service worker cache

**Files:**
- Modify: `sw.js:1-8`

Remove the static map images from the pre-cache list (MapLibre handles its own tile caching) and bump the cache version so existing users get the new service worker.

- [ ] **Step 1: Update sw.js**

Change lines 1-8 from:
```javascript
var CACHE_NAME = "gg-tank-v5";
var STATIC_ASSETS = [
  "/",
  "/dashboard.html",
  "/config.json",
  "/manifest.json",
  "/images/zone-map.png",
  "/images/zone-map-hires.jpg"
];
```

To:
```javascript
var CACHE_NAME = "gg-tank-v6";
var STATIC_ASSETS = [
  "/",
  "/dashboard.html",
  "/config.json",
  "/manifest.json"
];
```

- [ ] **Step 2: Commit**

```bash
git add sw.js
git commit -m "chore: bump SW cache to v6, remove static map images"
```

---

### Task 3: Add MapLibre CSS and JS to dashboard.html head

**Files:**
- Modify: `dashboard.html:11` (after the Google Fonts link, before `<link rel="manifest">`)

- [ ] **Step 1: Add MapLibre assets**

After line 10 (the Google Fonts `<link>`) and before line 11 (`<link rel="manifest">`), insert:

```html
<link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
```

- [ ] **Step 2: Commit**

```bash
git add dashboard.html
git commit -m "chore: add MapLibre GL JS v4.7.1 CDN assets"
```

---

### Task 4: Replace map CSS

**Files:**
- Modify: `dashboard.html:581-718` (the entire `/* ===== MAP PANEL ===== */` CSS section)

The old CSS handled the static image viewport, SVG overlay, and vanilla JS zoom. MapLibre manages its own canvas, so most of that CSS is unnecessary. Keep the overlay styles (wind, legend, actions, attribution).

- [ ] **Step 1: Replace the MAP PANEL CSS block**

Replace everything from `#panel-map {` through `.static-map-attribution a { color: var(--sa-text-3); }` with:

```css
/* ===== MAP PANEL ===== */
#panel-map { overflow: hidden; display: flex; flex-direction: column; }
.map-outer {
  position: relative;
  flex: 1;
  min-height: 0;
}
#maplibre-map {
  width: 100%;
  height: 100%;
}
.maplibregl-ctrl-bottom-left,
.maplibregl-ctrl-bottom-right { display: none; }
.map-wind {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--sa-surface);
  border: 1px solid var(--sa-border);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 11px;
  color: var(--sa-text-2);
  box-shadow: var(--sa-shadow);
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 2;
}
.map-legend {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: var(--sa-surface);
  border: 1px solid var(--sa-border);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 10px;
  box-shadow: var(--sa-shadow);
  z-index: 2;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 1px 0;
  color: var(--sa-text-2);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.1);
}
.static-map-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px 16px;
  text-align: center;
  background: linear-gradient(transparent, var(--sa-surface) 30%);
  z-index: 2;
}
.zone-check-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 24px;
  background: var(--sa-celadon);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  border-radius: 8px;
  text-decoration: none;
  width: 100%;
  max-width: 400px;
}
.zone-check-btn:hover { opacity: 0.9; }
.zone-check-note {
  font-size: 11px;
  color: var(--sa-text-3);
  margin: 8px 0 0;
  line-height: 1.4;
}
.zone-check-note a { color: var(--sa-celadon); }
.static-map-attribution {
  position: absolute;
  bottom: 2px;
  right: 4px;
  font-size: 9px;
  color: var(--sa-text-3);
  z-index: 2;
}
.static-map-attribution a { color: var(--sa-text-3); }
```

Key changes from old CSS:
- Removed `.map-viewport`, `.map-content`, `.map-content img`, `.map-overlay-svg`, `.map-zoom-hint` (all handled by MapLibre)
- Added `#maplibre-map` (the GL canvas container)
- Hidden MapLibre's built-in attribution controls (we have our own)
- All overlays (wind, legend, actions, attribution) kept as-is

- [ ] **Step 2: Commit**

```bash
git add dashboard.html
git commit -m "refactor: replace static map CSS with MapLibre container styles"
```

---

### Task 5: Replace map HTML

**Files:**
- Modify: `dashboard.html:1549-1591` (the `#panel-map` content)

Replace the static image + SVG overlay + zoom hint with a single MapLibre container div. Keep all overlays.

- [ ] **Step 1: Replace the panel-map content**

Replace everything from `<div class="tab-panel active" id="panel-map"...>` through its closing `</div>` (before `<div class="tab-panel" id="panel-news"`) with:

```html
<div class="tab-panel active" id="panel-map" role="tabpanel" aria-labelledby="tab-map">
  <div class="map-outer" id="map-outer">
    <div id="maplibre-map" role="img" aria-label="Map of the Garden Grove evacuation zone showing the approximate evacuation boundary around the GKN Aerospace facility, with shelter locations marked."></div>
    <div class="map-wind" id="map-wind-overlay">
      <svg class="wind-arrow-sm" id="wind-arrow-map" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1 L13 14 L8 11 L3 14 Z"/></svg>
      <span id="wind-text-map">--</span>
    </div>
    <div class="map-legend">
      <div class="legend-row"><span class="legend-dot" style="background:#3b82f6"></span> Evac zone</div>
      <div class="legend-row"><span class="legend-dot" style="background:#2563eb;border-radius:2px"></span> Shelter</div>
      <div class="legend-row"><span class="legend-dot" style="background:#111"></span> Facility</div>
    </div>
    <div class="static-map-actions">
      <a href="https://community.zonehaven.com/?lat=33.7858&lng=-118.005&z=12" target="_blank" rel="noopener" class="zone-check-btn" data-i18n="map.check_zone">Check your zone (official tool)</a>
      <p class="zone-check-note" data-i18n-html="map.zone_note">Boundaries are approximate. Verify your evacuation status at <a href="https://ggcity.org/emergency" target="_blank" rel="noopener">ggcity.org/emergency</a>.</p>
    </div>
    <div class="static-map-attribution">&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a></div>
  </div>
</div>
```

Key changes:
- Removed: `map-viewport`, `map-content`, `#map-img`, `#map-svg` (entire SVG overlay), `map-zoom-hint`
- Added: `#maplibre-map` div with `role="img"` and `aria-label` for accessibility
- Updated attribution: removed CARTO, kept OpenStreetMap (required by ODbL)
- All overlays (wind, legend, actions) unchanged

- [ ] **Step 2: Commit**

```bash
git add dashboard.html
git commit -m "refactor: replace static map HTML with MapLibre container"
```

---

### Task 6: Replace map JS with MapLibre initialization

**Files:**
- Modify: `dashboard.html:2848-3006` (the entire `/* ============ ZOOMABLE MAP ============ */` block)

This is the core task. Replace the vanilla pinch-zoom JS with MapLibre initialization that reads coordinates from `config.json` and adds GeoJSON layers.

- [ ] **Step 1: Replace the ZOOMABLE MAP JS block**

Replace everything from `/* ============ ZOOMABLE MAP ============ */` through the closing `})();` with:

```javascript
/* ============ MAPLIBRE MAP ============ */
(function() {
  if (typeof maplibregl === "undefined") return;

  var mapEl = document.getElementById("maplibre-map");
  if (!mapEl) return;

  var map = new maplibregl.Map({
    container: "maplibre-map",
    style: "https://tiles.openfreemap.org/styles/liberty",
    center: [-118.0088, 33.7930],
    zoom: 12.5,
    minZoom: 10,
    maxZoom: 17,
    attributionControl: false
  });

  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");

  map.on("load", function() {
    fetch("/config.json").then(function(r) { return r.json(); }).then(function(cfg) {
      var poly = cfg.map.evac_polygon;
      var coords = poly.map(function(p) { return [p[1], p[0]]; });
      coords.push(coords[0]);

      map.addSource("evac-zone", {
        type: "geojson",
        data: { type: "Feature", geometry: { type: "Polygon", coordinates: [coords] } }
      });
      map.addLayer({
        id: "evac-fill", type: "fill", source: "evac-zone",
        paint: { "fill-color": "#3b82f6", "fill-opacity": 0.15 }
      });
      map.addLayer({
        id: "evac-line", type: "line", source: "evac-zone",
        paint: { "line-color": "#3b82f6", "line-width": 2.5 }
      });

      var fac = cfg.map.facility;
      var facEl = document.createElement("div");
      facEl.style.cssText = "width:14px;height:14px;background:#dc2626;border:2px solid #111;border-radius:50%;";
      new maplibregl.Marker({ element: facEl })
        .setLngLat([fac.lon, fac.lat])
        .setPopup(new maplibregl.Popup({ offset: 12, closeButton: false }).setHTML("<strong>" + fac.label + "</strong>"))
        .addTo(map);

      cfg.map.shelters.forEach(function(s) {
        var el = document.createElement("div");
        el.style.cssText = "width:12px;height:12px;background:#2563eb;border:2px solid #fff;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.3);";
        new maplibregl.Marker({ element: el })
          .setLngLat([s.lon, s.lat])
          .setPopup(new maplibregl.Popup({ offset: 10, closeButton: false }).setHTML("<strong>" + s.name + "</strong><br>" + s.city + (s.notes ? " &middot; " + s.notes : "")))
          .addTo(map);
      });

      map.fitBounds([
        [Math.min.apply(null, coords.map(function(c){return c[0]})) - 0.005,
         Math.min.apply(null, coords.map(function(c){return c[1]})) - 0.005],
        [Math.max.apply(null, coords.map(function(c){return c[0]})) + 0.005,
         Math.max.apply(null, coords.map(function(c){return c[1]})) + 0.005]
      ], { padding: 40, maxZoom: 14 });
    });
  });
})();
```

Key decisions:
- Reads coordinates from `config.json` at runtime (not hardcoded pixel coordinates)
- All 9 shelters get markers (not just the 5 that were in the SVG viewport)
- `fitBounds` auto-centers on the evacuation zone with padding
- `attributionControl: false` since we have our own attribution element
- Navigation control (zoom +/-) added top-left
- Facility marker: red with black border (matching the legend)
- Shelter markers: blue with white border (matching the legend)
- Popups with shelter name, city, and notes (tappable on mobile)
- Graceful fallback: if `maplibregl` is undefined (CDN fails), the IIFE exits silently

- [ ] **Step 2: Verify the eval suite still passes**

Run: `python eval/run_all.py --skip integration`
Expected: 42/42 pass (no behavioral tests touch the map JS)

- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "feat: replace static map with MapLibre GL JS + OpenFreeMap"
```

---

### Task 7: Update print CSS

**Files:**
- Modify: `dashboard.html` (the `@media print` block, around line 1444)

The print CSS hides `.map-wind`, `.map-legend`, `.map-zoom-hint`. Remove `.map-zoom-hint` (no longer exists). The rest stays.

- [ ] **Step 1: Update the print media query**

Find the line:
```css
.map-wind, .map-legend, .map-zoom-hint, .skip-link { display: none !important; }
```

Replace with:
```css
.map-wind, .map-legend, .skip-link { display: none !important; }
```

- [ ] **Step 2: Commit**

```bash
git add dashboard.html
git commit -m "chore: remove map-zoom-hint from print CSS"
```

---

### Task 8: Visual verification

- [ ] **Step 1: Start local server and test**

Run: `python -m http.server 8080`

Open `http://localhost:8080/dashboard.html` in browse tool at 390x844 (mobile) and 1280x720 (desktop).

Verify:
1. Vector map loads with street names visible
2. Blue evacuation zone polygon visible
3. Red facility marker with popup on click
4. Blue shelter markers (all 9) with popups
5. Wind overlay visible top-right
6. Legend visible bottom-left
7. "Check your zone" button visible bottom-center
8. No vertical scroll on Map tab
9. Smooth pinch-zoom (simulated via scroll-wheel)
10. No console errors
11. Tab switching (Map -> News -> Map) preserves map state

- [ ] **Step 2: Run eval suite**

Run: `python eval/run_all.py --skip integration`
Expected: 42/42 pass

- [ ] **Step 3: Test dark mode**

Toggle dark mode. Verify overlays (wind, legend, button) use dark theme colors. The map tiles stay light (expected -- vector tiles don't respond to CSS vars).

---

### Task 9: Ship

- [ ] **Step 1: Create branch, squash commits, push, create PR, merge**

Use `/ship` skill.

---

## Self-Review Checklist

1. **Spec coverage:** CSP update (Task 1), SW cache (Task 2), CDN assets (Task 3), CSS (Task 4), HTML (Task 5), JS (Task 6), print CSS (Task 7), verification (Task 8), ship (Task 9). All requirements covered.
2. **Placeholder scan:** No TBDs, no "add appropriate handling", all code blocks complete.
3. **Type consistency:** `maplibregl.Map`, `maplibregl.Marker`, `maplibregl.Popup`, `maplibregl.NavigationControl` used consistently. `config.json` field names match: `cfg.map.evac_polygon`, `cfg.map.facility`, `cfg.map.shelters` with `.lat`, `.lon`, `.name`, `.city`, `.notes`.
