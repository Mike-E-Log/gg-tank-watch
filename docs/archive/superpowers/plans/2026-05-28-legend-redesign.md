# Legend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace uniform 10px dots in the map legend with distinct shapes, increase size, and switch to a ColorBrewer Dark2 colorblind-safe palette — applying the same colors to all map layers and markers for visual consistency.

**Architecture:** Single-file edit (`dashboard.html`) touching CSS, HTML, inline styles, and JS map layer paint properties. The color mapping is: evac zone `#3b82f6` → `#D95F02` (burnt orange), shelter `#2563eb` → `#1B9E77` (dark teal), facility `#dc2626`/`#111` → `#444444` (dark gray). Legend icons change from identical dots to shape-matched icons (filled rectangle for evac zone, square with house glyph for shelter, circle for facility).

**Tech Stack:** HTML/CSS, MapLibre GL JS paint properties, inline styles

---

## Color map (reference for all tasks)

| Item | Old color | New color | Shape |
|------|-----------|-----------|-------|
| Evac zone | `#3b82f6` | `#D95F02` | Filled rectangle (horizontal bar) |
| Shelter | `#2563eb` | `#1B9E77` | Rounded square with 🏠 glyph |
| Facility | `#dc2626` / `#111` | `#444444` | Circle |

## Sites to update (complete inventory)

| Line(s) | What | Color change |
|----------|------|-------------|
| 32 | CSS var `--sa-high` | `#dc2626` → keep (used for severity, not facility) |
| 958 | `.shelter-marker` background | `#2563eb` → `#1B9E77` |
| 1010 | `.cr-cat-shelter` badge | `#dbeafe`/`#2563eb` → `#d1fae5`/`#1B9E77` |
| 1281 | `.info-shelter-icon` background | `#2563eb` → `#1B9E77` |
| 1512-1514 | Legend HTML (dots → shapes) | All three |
| 612-636 | Legend CSS (`.map-legend`, `.legend-dot`) | Reshape |
| 2800, 2802 | `_ggSwapMapStyle` evac fill/line | `#3b82f6` → `#D95F02` |
| 2840, 2844 | `map.on("load")` evac fill/line | `#3b82f6` → `#D95F02` |
| 2849 | Facility marker inline style | `#dc2626` → `#444444` |
| 2857 | Shelter marker inline style | `#2563eb` → `#1B9E77` |

---

### Task 1: Update legend CSS and HTML (shapes + sizes)

**Files:**
- Modify: `dashboard.html:612-636` (legend CSS)
- Modify: `dashboard.html:1512-1514` (legend HTML)

- [ ] **Step 1: Replace `.legend-dot` CSS with `.legend-icon` supporting distinct shapes**

Replace the existing legend CSS block (lines 612-636):

```css
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
```

With:

```css
    .map-legend {
      position: absolute;
      bottom: 8px;
      left: 8px;
      background: var(--sa-surface);
      border: 1px solid var(--sa-border);
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 12px;
      box-shadow: var(--sa-shadow);
      z-index: 2;
    }
    .legend-row {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 2px 0;
      color: var(--sa-text-2);
    }
    .legend-icon {
      flex-shrink: 0;
      border: 1px solid rgba(0,0,0,0.15);
    }
    .legend-icon-evac {
      width: 18px;
      height: 10px;
      border-radius: 2px;
      background: #D95F02;
      opacity: 0.7;
    }
    .legend-icon-shelter {
      width: 14px;
      height: 14px;
      border-radius: 3px;
      background: #1B9E77;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 9px;
      line-height: 1;
      color: #fff;
    }
    .legend-icon-facility {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: #444;
    }
```

- [ ] **Step 2: Replace legend HTML to use shaped icons**

Replace the legend HTML (lines 1511-1515):

```html
          <div class="map-legend">
            <div class="legend-row"><span class="legend-dot" style="background:#3b82f6"></span> Evac zone</div>
            <div class="legend-row"><span class="legend-dot" style="background:#2563eb;border-radius:2px"></span> Shelter</div>
            <div class="legend-row"><span class="legend-dot" style="background:#111"></span> Facility</div>
          </div>
```

With:

```html
          <div class="map-legend">
            <div class="legend-row"><span class="legend-icon legend-icon-evac"></span> Evac zone</div>
            <div class="legend-row"><span class="legend-icon legend-icon-shelter">&#127968;</span> Shelter</div>
            <div class="legend-row"><span class="legend-icon legend-icon-facility"></span> Facility</div>
          </div>
```

- [ ] **Step 3: Run eval suite**

```bash
python eval/run_all.py --skip integration
```

Expected: 42/42 pass.

- [ ] **Step 4: Commit**

```bash
git add dashboard.html
git commit -m "fix: redesign map legend with distinct shapes and colorblind-safe palette

Legend icons now use distinct shapes matching map markers:
- Evac zone: horizontal bar (burnt orange #D95F02)
- Shelter: rounded square with house glyph (teal #1B9E77)
- Facility: circle (gray #444)

Based on FGDC emergency symbology and ColorBrewer Dark2 palette.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Update map layer colors (evac zone polygon)

**Files:**
- Modify: `dashboard.html:2800,2802` (`_ggSwapMapStyle` evac colors)
- Modify: `dashboard.html:2840,2844` (`map.on("load")` evac colors)

- [ ] **Step 1: Update `_ggSwapMapStyle` evac zone colors**

At line 2800, change:
```js
paint: { "fill-color": "#3b82f6", "fill-opacity": 0.15 }
```
To:
```js
paint: { "fill-color": "#D95F02", "fill-opacity": 0.13 }
```

At line 2802, change:
```js
paint: { "line-color": "#3b82f6", "line-width": 2.5 }
```
To:
```js
paint: { "line-color": "#D95F02", "line-width": 2.5 }
```

- [ ] **Step 2: Update `map.on("load")` evac zone colors**

At line 2840, change:
```js
paint: { "fill-color": "#3b82f6", "fill-opacity": 0.15 }
```
To:
```js
paint: { "fill-color": "#D95F02", "fill-opacity": 0.13 }
```

At line 2844, change:
```js
paint: { "line-color": "#3b82f6", "line-width": 2.5 }
```
To:
```js
paint: { "line-color": "#D95F02", "line-width": 2.5 }
```

Note: opacity lowered slightly from 0.15 to 0.13 because orange is perceptually brighter than blue at the same opacity — this keeps the fill subtle.

- [ ] **Step 3: Run eval suite**

```bash
python eval/run_all.py --skip integration
```

Expected: 42/42 pass.

- [ ] **Step 4: Commit**

```bash
git add dashboard.html
git commit -m "fix: update evac zone polygon to burnt orange (#D95F02)

Matches new legend color. Opacity reduced 0.15 → 0.13 to compensate
for orange being perceptually brighter than blue.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Update shelter marker colors (map + UI)

**Files:**
- Modify: `dashboard.html:958` (`.shelter-marker` CSS)
- Modify: `dashboard.html:1010` (`.cr-cat-shelter` badge CSS)
- Modify: `dashboard.html:1281` (`.info-shelter-icon` CSS)
- Modify: `dashboard.html:2857` (shelter map marker inline style)

- [ ] **Step 1: Update `.shelter-marker` CSS**

At line 958, change:
```css
      width: 22px; height: 22px; background: #2563eb; border: 2px solid white;
```
To:
```css
      width: 22px; height: 22px; background: #1B9E77; border: 2px solid white;
```

- [ ] **Step 2: Update `.cr-cat-shelter` badge CSS**

At line 1010, change:
```css
    .cr-cat-shelter { background: #dbeafe; color: #2563eb; }
```
To:
```css
    .cr-cat-shelter { background: #d1fae5; color: #1B9E77; }
```

- [ ] **Step 3: Update `.info-shelter-icon` CSS**

At line 1281, change:
```css
      background: #2563eb;
```
To:
```css
      background: #1B9E77;
```

- [ ] **Step 4: Update shelter map marker inline style**

At line 2857, change:
```js
        el.style.cssText = "width:12px;height:12px;background:#2563eb;border:2px solid #fff;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.3);";
```
To:
```js
        el.style.cssText = "width:14px;height:14px;background:#1B9E77;border:2px solid #fff;border-radius:3px;box-shadow:0 1px 3px rgba(0,0,0,0.3);";
```

Note: also changed `border-radius:50%` → `3px` (circle → rounded square to match legend shape) and `12px` → `14px` (slightly larger for visibility).

- [ ] **Step 5: Run eval suite**

```bash
python eval/run_all.py --skip integration
```

Expected: 42/42 pass.

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "fix: update shelter markers and badges to teal (#1B9E77)

Shelter markers, info panel icons, and community resource badges now
use ColorBrewer Dark2 teal. Map markers changed from circles to
rounded squares to match legend shape.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Update facility marker color

**Files:**
- Modify: `dashboard.html:2849` (facility map marker inline style)

- [ ] **Step 1: Update facility marker inline style**

At line 2849, change:
```js
      facEl.style.cssText = "width:14px;height:14px;background:#dc2626;border:2px solid #111;border-radius:50%;";
```
To:
```js
      facEl.style.cssText = "width:16px;height:16px;background:#444;border:2px solid #fff;border-radius:50%;";
```

Note: `#dc2626` (red) → `#444` (dark gray), border color `#111` → `#fff` for visibility on dark tiles, size `14px` → `16px` for slightly better visibility.

- [ ] **Step 2: Run eval suite**

```bash
python eval/run_all.py --skip integration
```

Expected: 42/42 pass.

- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "fix: update facility marker to neutral gray (#444)

Facility marker now uses neutral gray instead of red, with white
border for dark-tile visibility. Does not compete visually with
safety-critical evac zone and shelter markers.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Post-implementation verification

After all 4 tasks, run final verification:

```bash
python eval/run_all.py --skip integration
git log --oneline -5
```

Expected: 42/42 pass, 4 new commits.

Visual check (cannot do from CLI — note for manual testing):
- Map legend shows three distinct shapes at larger sizes
- Evac zone polygon is burnt orange (subtle fill, solid stroke)
- Shelter markers are teal rounded squares
- Facility marker is gray circle
- All items visually distinct on both Liberty (light) and Dark tile sets
- Legend colors match their corresponding map markers
