# P0 UX Fixes + PWA Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix critical mobile UX issues (touch targets, iOS auto-zoom, meta refresh) and add a PWA layer (service worker + manifest.json) for offline access and installability — without touching core dashboard logic.

**Architecture:** CSS-only fixes for touch targets and input sizing. Two new files (`manifest.json`, `sw.js`) for PWA. Three small additions to `dashboard.html`: manifest link, service worker registration script, and removal of the meta refresh tag. All changes are additive or CSS-only — zero risk to existing functionality.

**Tech Stack:** HTML/CSS, Service Worker API, Web App Manifest

---

### Task 1: Fix touch targets to meet 44px+ minimum

**Files:**
- Modify: `dashboard.html:157-173` (theme toggle CSS)
- Modify: `dashboard.html:481-503` (tab bar CSS)
- Modify: `dashboard.html:348-375` (hero check CSS)

- [ ] **Step 1: Identify all undersized touch targets**

Read `dashboard.html` and verify these elements are undersized:
- `.tab-btn` (line 487): `padding: 6px 0 4px` = ~32px height
- `#theme-toggle` (line 173): `padding: 3px 6px` = ~23px height
- `#lang-toggle` (line 925): uses `.theme-toggle` class = ~23px height
- `.hero-check button` (line 364): `padding: 8px 12px` = ~33px height
- `.safety-form button` (line 792): `padding: 10px 14px` = ~38px height

- [ ] **Step 2: Fix tab bar touch targets**

In `dashboard.html`, change the `.tab-btn` CSS (around line 487):

```css
    .tab-btn {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      padding: 10px 0 8px;
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 10px;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      transition: color 0.15s;
      border-top: 2px solid transparent;
      min-height: 48px;
    }
```

Key changes: `padding: 6px 0 4px` -> `padding: 10px 0 8px`, added `min-height: 48px`, `gap: 1px` -> `gap: 2px`.

- [ ] **Step 3: Fix theme toggle and language picker touch targets**

In `dashboard.html`, change the `#theme-toggle` CSS (around line 173) and add touch target rules:

```css
    #theme-toggle {
      padding: 3px 6px;
      min-width: 44px;
      min-height: 44px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    #lang-toggle {
      min-width: 44px;
      min-height: 44px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
```

- [ ] **Step 4: Fix hero check button touch target**

In `dashboard.html`, change `.hero-check button` CSS (around line 363):

```css
    .hero-check button {
      padding: 10px 16px;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 6px;
      font-weight: 700;
      font-size: 14px;
      font-family: inherit;
      cursor: pointer;
      white-space: nowrap;
      min-height: 44px;
    }
```

Key changes: `padding: 8px 12px` -> `padding: 10px 16px`, `font-size: 13px` -> `14px`, added `min-height: 44px`.

- [ ] **Step 5: Fix safety form button touch target**

In `dashboard.html`, change `.safety-form button` CSS (around line 791):

```css
    .safety-form button {
      padding: 12px 16px;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 6px;
      font-weight: 700;
      font-size: 14px;
      font-family: inherit;
      cursor: pointer;
      white-space: nowrap;
      min-height: 44px;
    }
```

- [ ] **Step 6: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass. The CSS changes don't affect any behavioral tests.

- [ ] **Step 7: Commit**

```bash
git add dashboard.html
git commit -m "fix(a11y): enlarge touch targets to 44px+ minimum for emergency mobile use"
```

---

### Task 2: Fix iOS auto-zoom and remove meta refresh

**Files:**
- Modify: `dashboard.html:7-8` (meta refresh removal)
- Modify: `dashboard.html:348-358` (hero check input)
- Modify: `dashboard.html:777-786` (safety form input)

- [ ] **Step 1: Remove the meta http-equiv refresh tag**

In `dashboard.html`, delete line 7:
```html
  <meta http-equiv="refresh" content="600">
```

The JS `setInterval(fetchStatus, REFRESH_MS)` already handles auto-refresh every 30 seconds. The meta tag forces a full page reload every 10 minutes, losing user state (active tab, checked address, scroll position).

- [ ] **Step 2: Fix hero check input font-size to prevent iOS auto-zoom**

In `dashboard.html`, change `.hero-check input` CSS (around line 348):

```css
    .hero-check input {
      flex: 1;
      padding: 10px 12px;
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 16px;
      font-family: inherit;
      min-width: 0;
    }
```

Key change: `font-size: 13px` -> `16px`, `padding: 8px 10px` -> `10px 12px`. iOS Safari auto-zooms on focus for inputs < 16px.

- [ ] **Step 3: Fix safety form input font-size**

In `dashboard.html`, change `.safety-form input` CSS (around line 777):

```css
    .safety-form input {
      flex: 1;
      padding: 10px 12px;
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 16px;
      font-family: inherit;
    }
```

Key change: `font-size: 15px` -> `16px`.

- [ ] **Step 4: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "fix(mobile): prevent iOS auto-zoom on inputs, remove meta refresh"
```

---

### Task 3: Add manifest.json for installability

**Files:**
- Create: `manifest.json`
- Modify: `dashboard.html:9` (add manifest link)

- [ ] **Step 1: Create manifest.json**

```json
{
  "name": "GG Tank Watch",
  "short_name": "GG Tank",
  "description": "Unofficial situational awareness for the Garden Grove chemical-tank emergency",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#faf8f5",
  "theme_color": "#0e6f5e",
  "orientation": "portrait",
  "icons": [
    {
      "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏭</text></svg>",
      "sizes": "any",
      "type": "image/svg+xml"
    }
  ]
}
```

Note: `background_color` and `theme_color` use the Sơn Mài Authority palette values. If Plan B hasn't shipped yet, use `#f8fafc` and `#1e40af` (current values) and update when the theme ships.

- [ ] **Step 2: Add manifest link to dashboard.html**

In `dashboard.html`, after the Google Fonts `<link>` (around line 11), add:

```html
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0e6f5e">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
```

- [ ] **Step 3: Commit**

```bash
git add manifest.json dashboard.html
git commit -m "feat(pwa): add web app manifest for Add-to-Homescreen installability"
```

---

### Task 4: Add service worker for offline access

**Files:**
- Create: `sw.js`
- Modify: `dashboard.html` (add registration script before closing `</body>`)

- [ ] **Step 1: Create sw.js**

```javascript
var CACHE_NAME = "gg-tank-v1";
var STATIC_ASSETS = [
  "/",
  "/dashboard.html",
  "/config.json",
  "/manifest.json"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (names) {
      return Promise.all(
        names
          .filter(function (name) { return name !== CACHE_NAME; })
          .map(function (name) { return caches.delete(name); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function (event) {
  var url = new URL(event.request.url);

  // Network-first for status.json (always try fresh data)
  if (url.pathname.endsWith("/status.json")) {
    event.respondWith(
      fetch(event.request)
        .then(function (response) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(event.request, clone);
          });
          return response;
        })
        .catch(function () {
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache-first for static assets
  if (event.request.method === "GET" && url.origin === self.location.origin) {
    event.respondWith(
      caches.match(event.request).then(function (cached) {
        if (cached) { return cached; }
        return fetch(event.request).then(function (response) {
          if (response.ok) {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function (cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Pass through external requests (Nominatim, NOAA, tiles, fonts)
  event.respondWith(fetch(event.request));
});
```

- [ ] **Step 2: Register the service worker in dashboard.html**

Add before the closing `</body>` tag in `dashboard.html`:

```html
  <script>
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(function () {});
    }
  </script>
```

- [ ] **Step 3: Add sw.js to vercel.json headers (allow caching)**

Read `vercel.json` and verify the existing headers config. The service worker needs to be served from the root. Vercel serves static files from root by default, so `sw.js` at the project root will be accessible at `/sw.js`. No vercel.json changes needed unless there's a restrictive content-type header.

- [ ] **Step 4: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass. The service worker is a separate file and doesn't affect the dashboard's DOM structure.

- [ ] **Step 5: Commit**

```bash
git add sw.js dashboard.html
git commit -m "feat(pwa): add service worker for offline access to cached dashboard state"
```

---

### Task 5: Add ARIA tab pattern for accessibility

**Files:**
- Modify: `dashboard.html` (tab bar HTML, around lines 1108-1123)
- Modify: `dashboard.html` (tab panel HTML)
- Modify: `dashboard.html` (switchTab JS function)

- [ ] **Step 1: Update tab bar HTML with ARIA roles**

Find the tab bar section in the HTML (around line 1108) and update:

```html
    <nav class="tab-bar" role="tablist" aria-label="Dashboard sections">
      <button class="tab-btn active" role="tab" id="tab-map" aria-selected="true" aria-controls="panel-map" onclick="switchTab('map')" data-tab="map">
        <span class="tab-btn-icon">🗺️</span>
        <span class="tab-btn-label" data-i18n="tab.map">Map</span>
      </button>
      <button class="tab-btn" role="tab" id="tab-news" aria-selected="false" aria-controls="panel-news" onclick="switchTab('news')" data-tab="news">
        <span class="tab-btn-icon">📰</span>
        <span class="tab-btn-label" data-i18n="tab.news">News</span>
      </button>
      <button class="tab-btn" role="tab" id="tab-check" aria-selected="false" aria-controls="panel-check" onclick="switchTab('check')" data-tab="check">
        <span class="tab-btn-icon">🔍</span>
        <span class="tab-btn-label" data-i18n="tab.check">Check</span>
      </button>
      <button class="tab-btn" role="tab" id="tab-info" aria-selected="false" aria-controls="panel-info" onclick="switchTab('info')" data-tab="info">
        <span class="tab-btn-icon">ℹ️</span>
        <span class="tab-btn-label" data-i18n="tab.info">Info</span>
      </button>
    </nav>
```

- [ ] **Step 2: Update tab panel HTML with ARIA roles**

Find each tab panel div and add `role="tabpanel"` and `aria-labelledby`:

```html
    <div class="tab-panel active" id="panel-map" role="tabpanel" aria-labelledby="tab-map">
    ...
    <div class="tab-panel" id="panel-news" role="tabpanel" aria-labelledby="tab-news">
    ...
    <div class="tab-panel" id="panel-check" role="tabpanel" aria-labelledby="tab-check">
    ...
    <div class="tab-panel" id="panel-info" role="tabpanel" aria-labelledby="tab-info">
```

- [ ] **Step 3: Update switchTab JS function to manage aria-selected**

Find the `switchTab` function in the `<script>` section and update it to toggle `aria-selected`:

```javascript
function switchTab(id) {
  document.querySelectorAll('.tab-panel').forEach(function(p) {
    p.classList.remove('active');
  });
  document.querySelectorAll('.tab-btn').forEach(function(b) {
    b.classList.remove('active');
    b.setAttribute('aria-selected', 'false');
  });
  var panel = document.getElementById('panel-' + id);
  var tab = document.getElementById('tab-' + id);
  if (panel) panel.classList.add('active');
  if (tab) {
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
  }
  if (id === 'map' && typeof map !== 'undefined') {
    setTimeout(function() { map.invalidateSize(); }, 150);
  }
}
```

- [ ] **Step 4: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "fix(a11y): add ARIA tab pattern for screen reader navigation"
```
