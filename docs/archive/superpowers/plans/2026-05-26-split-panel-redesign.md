# Split-Panel Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the "Split-panel" (Variant B) full dashboard redesign from the Claude Design prototype, updating `dashboard.html` to match the new visual language while preserving all existing JS functionality (data loading, geocoding, Leaflet map, i18n, theme toggle).

**Architecture:** Single-file update to `dashboard.html`. The design prototype uses React JSX for mockups, but the target is vanilla HTML/CSS/JS matching the project's existing stack. All changes are visual/structural — the data model (`status.json`, `config.json`, `timeline.json`) and JS business logic (geocoding, point-in-polygon, wind fetching) are preserved verbatim. The CSS variable namespace shifts from `--bg`/`--surface`/etc. to `--sa-*` (Sơn Mài Authority tokens), and the HTML structure is reorganized to support the Split-panel hero and unified tab system.

**Tech Stack:** Vanilla HTML/CSS/JS, Leaflet.js (existing), Google Fonts (existing: Plus Jakarta Sans, Be Vietnam Pro, IBM Plex Mono)

**Design source:** `/tmp/design-extract/gg-tank-watch/project/` — `tokens.css`, `topbar.jsx`, `variants.jsx`, `tabs.jsx`, `data.jsx`, `app.jsx`

---

### Task 1: Update CSS Custom Properties to Sơn Mài Authority Tokens

**Files:**
- Modify: `dashboard.html:17-72` (CSS variables block)

The design uses `--sa-*` prefixed tokens. We rename existing `--bg`/`--surface`/`--text`/etc. to match, and add new tokens (`--sa-celadon-2`, `--sa-celadon-3`, `--sa-gold-2`, `--sa-surface-2`, `--sa-border-2`, `--sa-shadow`). Every `var(--old)` reference throughout the CSS must be updated.

- [ ] **Step 1: Replace the light-theme CSS variable block**

Replace `:root, html.theme-light { ... }` with:

```css
:root, html.theme-light {
  --sa-bg:        #faf8f5;
  --sa-surface:   #ffffff;
  --sa-surface-2: #f3efe7;
  --sa-text:      #1a1612;
  --sa-text-2:    #5c5347;
  --sa-text-3:    #8a8279;
  --sa-celadon:   #0e6f5e;
  --sa-celadon-2: #d8eae5;
  --sa-celadon-3: rgba(14, 111, 94, 0.12);
  --sa-gold:      #9e7c29;
  --sa-gold-2:    #efe4c5;
  --sa-safe:      #059669;
  --sa-moderate:  #d97706;
  --sa-high:      #dc2626;
  --sa-critical:  #7f1d1d;
  --sa-high-soft: rgba(220, 38, 38, 0.10);
  --sa-border:    rgba(26, 22, 18, 0.08);
  --sa-border-2:  rgba(26, 22, 18, 0.16);
  --sa-shadow-sm: 0 1px 2px rgba(26, 22, 18, 0.05);
  --sa-shadow:    0 2px 12px rgba(26, 22, 18, 0.06), 0 1px 2px rgba(26, 22, 18, 0.04);
}
```

- [ ] **Step 2: Replace the dark-theme CSS variable block**

Replace `html.theme-dark { ... }` with:

```css
html.theme-dark {
  --sa-bg:        #121110;
  --sa-surface:   #1e1c19;
  --sa-surface-2: #28241e;
  --sa-text:      #f0ece6;
  --sa-text-2:    #a39a8e;
  --sa-text-3:    #6e665c;
  --sa-celadon:   #4ecdb4;
  --sa-celadon-2: #1f3a35;
  --sa-celadon-3: rgba(78, 205, 180, 0.14);
  --sa-gold:      #d4b05c;
  --sa-gold-2:    #3a2f17;
  --sa-safe:      #10b981;
  --sa-moderate:  #f59e0b;
  --sa-high:      #ef4444;
  --sa-critical:  #b91c1c;
  --sa-high-soft: rgba(239, 68, 68, 0.14);
  --sa-border:    rgba(240, 236, 230, 0.10);
  --sa-border-2:  rgba(240, 236, 230, 0.20);
  --sa-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --sa-shadow:    0 2px 14px rgba(0, 0, 0, 0.45), 0 1px 2px rgba(0, 0, 0, 0.3);
}
```

- [ ] **Step 3: Search-and-replace all `var(--old)` references**

Mapping (apply throughout the entire `<style>` block and inline styles):
- `var(--bg)` → `var(--sa-bg)`
- `var(--surface)` → `var(--sa-surface)`
- `var(--text)` → `var(--sa-text)`
- `var(--text-sec)` → `var(--sa-text-2)`
- `var(--text-muted)` → `var(--sa-text-3)`
- `var(--border)` → `var(--sa-border)` (the 1px-line border)
- `var(--shadow)` → `var(--sa-shadow)`
- `var(--accent)` → `var(--sa-celadon)`
- `var(--accent-light)` → `var(--sa-celadon-3)`
- `var(--gold)` → `var(--sa-gold)`
- `var(--gold-light)` → `var(--sa-gold-2)`
- `var(--safe)` → `var(--sa-safe)`
- `var(--moderate)` → `var(--sa-moderate)`
- `var(--high)` → `var(--sa-high)`
- `var(--critical)` → `var(--sa-critical)`
- `var(--safe-bg)` → `var(--sa-celadon-3)` (reuse)
- `var(--high-bg)` → `var(--sa-high-soft)`
- `var(--banner-update-bg)` → `var(--sa-gold-2)`
- `var(--banner-stale-bg)` → `var(--sa-surface-2)`
- `var(--banner-breaking-bg)` → `var(--sa-high-soft)`

Also remove `--safe-bg`, `--safe-border`, `--moderate-bg`, `--moderate-border`, `--high-bg`, `--high-border`, `--critical-bg`, `--critical-border`, `--banner-*-bg` variables since they map to the new tokens above.

- [ ] **Step 4: Add new utility classes**

After the `.mono` class, add:

```css
.sa-mono { font-family: 'IBM Plex Mono', ui-monospace, monospace; font-feature-settings: 'zero', 'cv11'; }
.sa-sev-low      { color: var(--sa-safe); }
.sa-sev-moderate { color: var(--sa-moderate); }
.sa-sev-high     { color: var(--sa-high); }
.sa-sev-critical { color: var(--sa-critical); }
.sa-sev-resolved { color: var(--sa-celadon); }
```

- [ ] **Step 5: Verify no broken `var(--*)` references remain**

Search the entire file for `var(--` and confirm every reference uses a `--sa-*` token that exists in the variable blocks. Fix any stragglers.

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "refactor(design): migrate CSS variables to Sơn Mài Authority --sa-* tokens"
```

---

### Task 2: Rebuild Topbar HTML + CSS

**Files:**
- Modify: `dashboard.html` — topbar CSS (~line 150-235) and topbar HTML (~line 1285-1298)

The new topbar matches the design: UNOFFICIAL pill with dot indicator, "GG Tank Watch" wordmark with colored "Tank", pulse-dot freshness indicator, flag-based language toggle button, and theme toggle with sun/moon SVG icons.

- [ ] **Step 1: Replace topbar CSS**

Replace the entire `/* ===== TOPBAR ===== */` CSS section with styles matching the design prototype's `Topbar` component. Key changes:
- UNOFFICIAL pill: gold background `--sa-gold-2`, gold border, gold text, IBM Plex Mono, 10.5px, dot indicator
- Wordmark: 16.5px, weight 800, "Tank" span colored `--sa-celadon`
- Freshness: pulse-dot animation, IBM Plex Mono
- Lang toggle: flag + label, border button style
- Theme toggle: SVG sun/moon, compact button

- [ ] **Step 2: Replace topbar HTML**

Replace the `<header class="topbar">...</header>` block with the Split-panel topbar structure. Keep `id` attributes for JS targeting (`unofficial-pill`, `updated-text`, `lang-toggle`, `lang-menu`, `theme-toggle`, `lang-picker`).

- [ ] **Step 3: Add pulse-dot keyframe animation**

```css
@keyframes sa-pulse {
  0%   { box-shadow: 0 0 0 0 currentColor; opacity: 1; }
  70%  { box-shadow: 0 0 0 6px transparent; opacity: 0.6; }
  100% { box-shadow: 0 0 0 0 transparent; opacity: 1; }
}
```

- [ ] **Step 4: Update topbar JS references**

Update `applyTheme()` and `renderLangPicker()` to work with the new HTML structure. The theme toggle now uses SVG icons inline (sun/moon from the design) instead of emoji/SVG constants.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): rebuild topbar with Sơn Mài Authority split-panel styling"
```

---

### Task 3: Replace Hero with Split-Panel Layout

**Files:**
- Modify: `dashboard.html` — hero CSS (~line 380-493) and hero HTML (~line 1302-1314)

The current hero is a centered block with severity chip + summary + address check input. The new Split-panel hero has two cards side-by-side:
- **Left card**: Severity word (large, colored), resident count, "in evacuation zone" label, colored top rule
- **Right card**: "What changed" header with day counter, 3 severity-specific bullets with dashed dividers

The address checker moves OUT of the hero into the Check tab (Task 6).

- [ ] **Step 1: Replace hero CSS**

Remove the old `.hero`, `.hero-severity`, `.hero-summary`, `.hero-check`, `.hero-verdict`, `.severity-chip` CSS blocks. Add new Split-panel hero CSS:

```css
.hero-split {
  display: flex;
  background: var(--sa-bg);
}
.hero-split-left {
  flex: 0 0 38%;
  padding: 22px 24px;
  background: var(--sa-surface);
  border-right: 1px solid var(--sa-border);
  border-top: 3px solid var(--sa-high); /* dynamic via JS */
  position: relative;
}
.hero-split-right {
  flex: 1 1 auto;
  padding: 22px 24px;
  min-width: 0;
}
/* Mobile: stack vertically */
@media (max-width: 767px) {
  .hero-split { flex-direction: column; }
  .hero-split-left {
    flex: 0 0 auto;
    padding: 18px 14px 14px;
    border-right: none;
    border-bottom: 1px solid var(--sa-border);
  }
  .hero-split-right { padding: 14px 14px 18px; }
}
```

- [ ] **Step 2: Replace hero HTML**

Remove `<section class="hero" id="hero">...</section>` including the address check form. Replace with Split-panel HTML structure with `id` attributes for JS data binding:
- `id="hero-severity-word"` — the large severity text
- `id="hero-severity-border"` — the left card (for dynamic border-top color)
- `id="hero-res-count"` — resident count
- `id="hero-bullets"` — the 3-bullet list

- [ ] **Step 3: Add hero rendering to `render()` function**

Update the `render(snap)` function to populate the Split-panel hero:
- Set severity word text + color class
- Set resident count from `snap.evacuation.residents`
- Set top-border color based on severity
- Generate 3 bullet items from severity-specific i18n strings (add new `STRINGS` entries)

- [ ] **Step 4: Add i18n strings for hero bullets**

Add new entries to `STRINGS`:

```javascript
"hero.bullet.high.1": { en: "BLEVE explosion threat eliminated", vi: "Loại bỏ nguy cơ nổ BLEVE" },
"hero.bullet.high.2": { en: "Evacuation zone reduced 50,000 → 16,000", vi: "Vùng sơ tán giảm 50.000 → 16.000" },
"hero.bullet.high.3": { en: "Tank temperature stabilizing · smaller blast risk remains", vi: "Nhiệt độ bồn ổn định · còn nguy cơ nổ nhỏ" },
// ... similarly for critical, moderate, low, resolved
"hero.whatchanged": { en: "What changed", vi: "Diễn biến" },
"hero.daysince": { en: "Day 5 · since Thu 3:40 PM", vi: "Ngày thứ 5 · từ 3:40 chiều thứ Năm" },
```

- [ ] **Step 5: Remove old stats strip**

The design does not have the compact stats strip (wind/temp/AQI/evac/countdown). Remove the `.stats-strip` HTML and CSS. The wind display now only shows on the map overlay.

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): replace hero with split-panel layout + remove stats strip"
```

---

### Task 4: Update Safety Strip + Update Banner

**Files:**
- Modify: `dashboard.html` — safety strip CSS (~line 284-306) and HTML (~line 1316-1326), banner CSS/JS

- [ ] **Step 1: Update safety strip CSS**

Match the design: `--sa-surface-2` background, two-row mobile layout (message + sources on separate lines), IBM Plex Mono for source links, "Full terms" link right-aligned.

- [ ] **Step 2: Update safety strip HTML**

Restructure to match design's `SafetyStrip` component. Keep the same links and text.

- [ ] **Step 3: Update banner system for UPDATE banner**

The design shows an update banner with a `[NEW]` pill, message text, and dismiss button. Update `setBanners()` to match this visual style using `--sa-celadon-3` background (normal) or `--sa-high-soft` (urgent).

- [ ] **Step 4: Remove AI disclosure strip**

The design does not show the AI disclosure as a separate strip. It can be incorporated into the Info tab's "About" section instead.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): update safety strip and banner to match split-panel design"
```

---

### Task 5: Restructure Tab System (Map / News / Check / Info)

**Files:**
- Modify: `dashboard.html` — tab CSS, tab HTML, tab JS functions

The tabs rename from `Map / Updates / Resources / About` to `Map / News / Check / Info`. Mobile tabs move to bottom with glyph icons (M/N/C/I). Desktop tabs stay at top with text labels.

- [ ] **Step 1: Update tab CSS**

Update `.tab-bar` and `.tab-btn` styles to match design:
- Mobile: bottom bar with stacked glyph + label
- Desktop: top bar with underline indicator, `--sa-celadon` active color
- Glyph squares: 16×16, IBM Plex Mono, colored background when active

- [ ] **Step 2: Update tab HTML**

Rename tab IDs and labels:
- `tab-map` / `panel-map` → keep as-is
- `tab-updates` / `panel-updates` → `tab-news` / `panel-news`
- `tab-resources` / `panel-resources` → `tab-check` / `panel-check`
- `tab-about` / `panel-about` → `tab-info` / `panel-info`

Add glyph spans: M, N, C, I.

- [ ] **Step 3: Update i18n strings for tab labels**

```javascript
"tab.map":   { en: "Map",   vi: "Bản đồ" },
"tab.news":  { en: "News",  vi: "Tin tức" },
"tab.check": { en: "Check", vi: "Kiểm tra" },
"tab.info":  { en: "Info",  vi: "Thông tin" },
```

- [ ] **Step 4: Update `switchTab()` and `switchSidebarTab()` JS**

Update panel ID references from `updates`→`news`, `resources`→`check`, `about`→`info`. Update banner onclick targets.

- [ ] **Step 5: Restructure desktop layout**

The current desktop layout is map-left + sidebar-right with sub-tabs. The new design uses the same tab system on both desktop and mobile (full-width tabs at top on desktop). Remove the `desktop-body` / `desktop-sidebar` / `sidebar-tabs` structure and use a single unified tab system. The map tab takes full width on desktop. Other tabs use the full viewport width with appropriate padding.

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): restructure tabs to Map/News/Check/Info with glyph icons"
```

---

### Task 6: Build Check Tab Content

**Files:**
- Modify: `dashboard.html` — add Check tab HTML + CSS, wire up geocoder

The address checker moves from the hero into its own dedicated tab. The design shows: input field + Check button, "Use my location" affordance, recent-checks list, verdict card with severity-colored left border, distance from tank, and legal note.

- [ ] **Step 1: Add Check tab CSS**

Styles for: input group with integrated Check button, "Use my location" dashed-border button, recent-check list items with verdict dots, verdict card with colored left border, distance display.

- [ ] **Step 2: Add Check tab HTML**

Two-column layout on desktop (input+recents left, verdict right), stacked on mobile.

- [ ] **Step 3: Wire geocoder to Check tab**

Move `heroCheckSafety()` logic to a new `checkAddress()` function that:
- Gets input value from the Check tab input
- Calls existing `geocodeAddress()` + `computeSafety()`
- Renders verdict card in the Check tab
- Updates map pin (existing `renderSafetyResult()` logic)
- Saves to `localStorage` for recent-checks list

- [ ] **Step 4: Add recent-checks rendering**

On page load, read recent checks from `localStorage` and render them as clickable list items. Clicking re-runs the check.

- [ ] **Step 5: Add i18n strings for Check tab**

```javascript
"check.prompt": { en: "Check an address or intersection", vi: "Kiểm tra địa chỉ hoặc giao lộ" },
"check.sub": { en: "Pins your address on the map and gives an unofficial verdict.", vi: "Ghim địa chỉ của bạn trên bản đồ và đưa ra phán đoán không chính thức." },
"check.placeholder": { en: "e.g. Magnolia & Talbert", vi: "ví dụ: Magnolia & Talbert" },
"check.useLocation": { en: "Use my location", vi: "Dùng vị trí của tôi" },
"check.btn": { en: "Check", vi: "Kiểm tra" },
"check.lastChecked": { en: "Last checked", vi: "Kiểm tra gần nhất" },
"check.recent": { en: "Recent", vi: "Gần đây" },
"check.fromTank": { en: "from tank", vi: "từ bồn" },
"check.viewOnMap": { en: "View on map", vi: "Xem trên bản đồ" },
```

- [ ] **Step 6: Add verdict label strings**

```javascript
"verdict.inside": { en: "INSIDE OFFICIAL EVAC ZONE", vi: "TRONG VÙNG SƠ TÁN CHÍNH THỨC" },
"verdict.blast20": { en: "BLAST RING — 20 PSI OVERPRESSURE", vi: "VÒNG NỔ — ÁP SUẤT 20 PSI" },
"verdict.blastMod": { en: "BLAST RING — MODERATE DAMAGE", vi: "VÒNG NỔ — THIỆT HẠI VỪA" },
"verdict.outside": { en: "OUTSIDE MAPPED ZONES", vi: "NGOÀI CÁC VÙNG TRÊN BẢN ĐỒ" },
"verdict.note": { en: "Estimate only — not official. Verify at ggcity.org/emergency; in an emergency, call 911.", vi: "Chỉ là ước tính — không chính thức. Kiểm tra tại ggcity.org/emergency; khẩn cấp gọi 911." },
```

- [ ] **Step 7: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): build Check tab with address checker + verdict cards"
```

---

### Task 7: Update News Tab Content

**Files:**
- Modify: `dashboard.html` — News tab HTML + CSS + JS (formerly "Updates")

The News tab adds: current-situation summary block at top, filter chips (All / Official / Articles / Videos with counts), feed cards with mono badges and newest/recent pills.

- [ ] **Step 1: Update feed card CSS**

Match design: rounded cards with border, severity-colored left border for newest, mono badges (`OFFICIAL` celadon, `ARTICLE` text-2, `VIDEO` gold), `Newest`/`Recent` pills.

- [ ] **Step 2: Add filter chips to News tab HTML**

Filter chips: All (count), Official (count), Articles (count), Videos (count). Celadon background when active, pill shape.

- [ ] **Step 3: Wire filter chip logic**

Add `filterNews(kind)` function that filters `FEED_ITEMS` by type and re-renders. Preserve the existing `buildFeedHtml()` function but update its output format to match the design's card layout.

- [ ] **Step 4: Update i18n strings for News**

```javascript
"news.filter.all": { en: "All", vi: "Tất cả" },
"news.filter.official": { en: "Official", vi: "Chính thức" },
"news.filter.articles": { en: "Articles", vi: "Báo chí" },
"news.filter.videos": { en: "Videos", vi: "Video" },
"news.badge.official": { en: "OFFICIAL", vi: "CHÍNH THỨC" },
"news.badge.article": { en: "ARTICLE", vi: "BÁO CHÍ" },
"news.badge.video": { en: "VIDEO", vi: "VIDEO" },
```

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): update News tab with filter chips and card layout"
```

---

### Task 8: Build Info Tab Content

**Files:**
- Modify: `dashboard.html` — Info tab HTML + CSS (formerly "About")

The Info tab shows: incident status key-value rows, nearest shelters list, school closures grid, "Who made this" section with gold seal, sources section (collapsed).

- [ ] **Step 1: Add Info tab CSS**

Section headers with uppercase labels + horizontal rule, KV rows with dashed bottom borders, shelter rows with blue square indicators + directions links, school grid, gold informational seal.

- [ ] **Step 2: Build Info tab HTML structure**

Two-column on desktop, single-column on mobile:
- Left column: Incident status KVs, Shelters
- Right column: School closures, Who made this, Sources

- [ ] **Step 3: Wire incident data rendering**

Update `updateAboutData(snap)` (or create new `renderInfoTab(snap)`) to populate:
- Tank crack: Yes/No
- Tank temperature: value from `snap.tank.temp_f`
- Residents in zone: from `snap.evacuation.residents`
- Boundary: from `snap.evacuation.boundary_text`

- [ ] **Step 4: Wire shelter list rendering**

Render top 5 shelters from `configCache.map.shelters` with name, city, distance, directions link. Reuse existing shelter data.

- [ ] **Step 5: Wire school closures**

Render `snap.schools_closed` as a 2-column grid of compact cards.

- [ ] **Step 6: Add "Who made this" section**

Static content with gold informational seal badge. Include the AI disclosure text that was removed from the strip in Task 4.

- [ ] **Step 7: Add i18n strings for Info tab**

```javascript
"info.tankCrack": { en: "Crack observed", vi: "Có vết nứt" },
"info.tankCrackY": { en: "Yes — relieving pressure", vi: "Có — đang giải áp" },
"info.tankTemp": { en: "Tank temperature", vi: "Nhiệt độ bồn" },
"info.tankTempV": { en: "Stabilizing", vi: "Đang ổn định" },
"info.evacResidents": { en: "Residents in zone", vi: "Cư dân trong vùng" },
"info.evacBoundary": { en: "Boundary", vi: "Ranh giới" },
"info.whereToGo": { en: "Where to go · nearest shelters", vi: "Nơi đến · trú ẩn gần nhất" },
"info.allShelters": { en: "All 9 shelters", vi: "Toàn bộ 9 nơi" },
"info.directions": { en: "Directions ↗", vi: "Chỉ đường ↗" },
"info.schoolsClosed": { en: "School closures", vi: "Trường đóng cửa" },
"info.whoMade": { en: "Who made this", vi: "Ai làm trang này" },
"info.unofficial.seal": { en: "INFORMATIONAL · UNOFFICIAL", vi: "THAM KHẢO · KHÔNG CHÍNH THỨC" },
```

- [ ] **Step 8: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): build Info tab with status KVs, shelters, schools, about"
```

---

### Task 9: Responsive Layout + Desktop/Mobile Unification

**Files:**
- Modify: `dashboard.html` — desktop layout CSS + HTML

The current dashboard has separate desktop (map-left + sidebar) and mobile (tab-bar bottom) layouts. The new design unifies them: same tab structure on both, with tabs at top on desktop and bottom on mobile.

- [ ] **Step 1: Remove old desktop-body layout**

Remove the `<div class="desktop-body">...</div>` HTML block and its CSS (`.desktop-body`, `.desktop-map-panel`, `.desktop-sidebar`, `.sidebar-tabs`, `.sidebar-tab-btn`, `.sidebar-content`, `.sidebar-panel`).

- [ ] **Step 2: Add responsive tab positioning CSS**

```css
/* Mobile: tabs at bottom */
@media (max-width: 767px) {
  .tab-nav { order: 99; }
  .tab-nav .tab-btn { flex-direction: column; }
}
/* Desktop: tabs at top, below hero */
@media (min-width: 768px) {
  .tab-nav { order: 0; border-bottom: 1px solid var(--sa-border); }
}
```

- [ ] **Step 3: Update map initialization**

Since there's now only one map container (not separate mobile/desktop), simplify `initMap()` to always target `id="map"`. Remove the desktop map duplicate.

- [ ] **Step 4: Update `checkDesktop()` and resize handling**

Simplify — no longer need separate desktop/mobile panel switching. The tab system handles everything.

- [ ] **Step 5: Ensure print styles still work**

Update print CSS selectors to match new class names.

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "refactor(design): unify desktop/mobile layout into single tab system"
```

---

### Task 10: Final Polish + Verification

**Files:**
- Modify: `dashboard.html`

- [ ] **Step 1: Add wave-background pattern**

From the design's `.sa-wave-bg` class — subtle celadon horizontal lines at 4% opacity, suppressed at high/critical severity.

- [ ] **Step 2: Verify Leaflet map dark-theme overrides**

Ensure `.leaflet-control-attribution`, `.leaflet-control-zoom`, and tooltip styles use `--sa-*` tokens.

- [ ] **Step 3: Verify all i18n strings are wired**

Run through every `data-i18n` attribute and every `t()` call to confirm all new strings exist in `STRINGS`.

- [ ] **Step 4: Test theme toggle**

Verify light↔dark switching updates all new tokens correctly.

- [ ] **Step 5: Test language toggle**

Verify EN↔VI switching translates all new UI elements (hero bullets, tab labels, check labels, info KVs).

- [ ] **Step 6: Run eval suite**

```bash
cd eval && python run_all.py --skip integration
```

Verify all behavioral tests still pass — especially safety-related ones (no directives, source provenance).

- [ ] **Step 7: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): complete split-panel redesign with polish and verification"
```

## Implementation Tasks

Synthesized from design review findings. Each task derives from a specific finding above.

- [ ] **T1 (P1, human: ~2h / CC: ~15min)** — hero — Restore inline address checker below split-panel hero
  - Surfaced by: Pass 1 D2 — address checker buried in 3rd tab; primary user action inaccessible
  - Files: `dashboard.html`
  - Verify: Address input visible on page load without tapping any tab

- [ ] **T2 (P1, human: ~30min / CC: ~5min)** — info-tab — Restore community resources DOM container in Info tab
  - Surfaced by: Pass 1 D3 — community resources (FEMA, DA tip line, price gouging) dropped during redesign
  - Files: `dashboard.html`
  - Verify: Community resources render in Info tab from `config.json` data

- [ ] **T3 (P2, human: ~30min / CC: ~5min)** — hero — Replace `--` placeholders with skeleton shimmer bars
  - Surfaced by: Pass 2 D4 — placeholder dashes look broken on slow connections
  - Files: `dashboard.html`
  - Verify: Shimmer bars show during loading; replaced with real data when status.json loads

- [ ] **T4 (P2, human: ~15min / CC: ~3min)** — docs — Update DESIGN.md Core UX Principle to conduit framing
  - Surfaced by: Pass 5 D5 — DESIGN.md specifies directives that violate binding constraint
  - Files: `DESIGN.md`
  - Verify: No directive language ("STAY PUT", "LEAVE NOW") in DESIGN.md hero spec

- [ ] **T5 (P2, human: ~1h / CC: ~10min)** — layout — Remove max-width cap for Map tab on desktop
  - Surfaced by: Pass 6 D6 — 800px cap wastes desktop viewport for the map
  - Files: `dashboard.html`
  - Verify: Map tab fills viewport on 1920px+ screens; other tabs keep max-width

- [ ] **T6 (P2, human: ~1h / CC: ~10min)** — tabs — Replace letter glyphs with standard SVG icons
  - Surfaced by: Pass 7 D7 — letter glyphs (M/N/C/I) require learning; Nielsen heuristic #6
  - Files: `dashboard.html`
  - Verify: Map pin, newspaper, magnifying glass, info circle icons in mobile tab bar

- [ ] **T7 (P3, human: ~15min / CC: ~3min)** — a11y — Darken `--sa-text-3` to meet WCAG AA 4.5:1 contrast
  - Surfaced by: Pass 6 — `#8a8279` on `#faf8f5` is ~3.4:1, below WCAG AA
  - Files: `dashboard.html`
  - Verify: `--sa-text-3` contrast ratio against `--sa-bg` >= 4.5:1

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | -- | -- |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | -- | -- |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR (PLAN) | 2 issues, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | ISSUES_OPEN (FULL) | score: 5/10 -> 7/10, 6 decisions made |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | -- | -- |

- **UNRESOLVED:** 0 decisions unresolved across both reviews
- **ENG FINDINGS:** (1) Wire hero checker to shared `checkTabAddress()` instead of resurrecting dead `heroCheckSafety()`. (2) Dead `renderAbout()` function should be removed (content now in `renderInfoTab()`).
- **VERDICT:** DESIGN + ENG CLEARED. 7 implementation tasks ready to execute (2 P1, 4 P2, 1 P3). T1 updated: hero checker uses shared `checkTabAddress()` path.
