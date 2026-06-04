# Sơn Mài Authority Theme — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the "Sơn Mài Authority" Vietnamese cultural design system to the dashboard — warm lacquerware-inspired surfaces, celadon teal accent, Be Vietnam Pro font for Vietnamese body text, and subtle cultural motifs (lotus divider, wave texture, celadon card borders). Severity colors remain completely unchanged.

**Architecture:** Swap CSS custom property values in both light and dark themes. Add Be Vietnam Pro to the Google Fonts load. Add language-aware CSS for Vietnamese body text. Add three CSS classes for cultural motifs. Update DESIGN.md. All changes are CSS + one font link — zero JavaScript changes.

**Tech Stack:** CSS custom properties, Google Fonts CDN, HTML `lang` attribute

---

### Task 1: Update CSS custom properties for Sơn Mài palette

**Files:**
- Modify: `dashboard.html:14-65` (CSS custom properties for light and dark themes)

- [ ] **Step 1: Replace light theme CSS custom properties**

In `dashboard.html`, replace the `:root, html.theme-light` block (lines 14-39):

```css
    :root, html.theme-light {
      --bg: #faf8f5;
      --surface: #ffffff;
      --text: #1a1612;
      --text-sec: #5c5347;
      --text-muted: #8a8279;
      --border: #e5e0d8;
      --shadow: 0 1px 2px rgba(26,22,18,0.06);
      --accent: #0e6f5e;
      --accent-light: #e0f2ee;
      --gold: #9e7c29;
      --gold-light: #f7f0e0;
      --safe: #059669;
      --safe-bg: #ecfdf5;
      --safe-border: #a7f3d0;
      --moderate: #d97706;
      --moderate-bg: #fffbeb;
      --moderate-border: #fde68a;
      --high: #dc2626;
      --high-bg: #fef2f2;
      --high-border: #fecaca;
      --critical: #7f1d1d;
      --critical-bg: #fef2f2;
      --critical-border: #fecaca;
      --banner-breaking-bg: #fef2f2;
      --banner-update-bg: #fdf6e8;
      --banner-stale-bg: #f3f0eb;
    }
```

Key changes from current:
- `--bg`: `#f8fafc` (cool slate) -> `#faf8f5` (warm ivory)
- `--text`: `#0f172a` -> `#1a1612` (warm near-black)
- `--text-sec`: `#475569` -> `#5c5347` (warm gray)
- `--text-muted`: `#94a3b8` -> `#8a8279` (warm stone)
- `--border`: `#e2e8f0` -> `#e5e0d8` (warm sand)
- `--accent`: `#1e40af` (deep blue) -> `#0e6f5e` (deep celadon teal)
- `--accent-light`: `#dbeafe` -> `#e0f2ee` (celadon mist)
- Added: `--gold`, `--gold-light`
- `--banner-update-bg`: `#fffbeb` -> `#fdf6e8` (warmer)
- `--banner-stale-bg`: `#f1f5f9` -> `#f3f0eb` (warmer)
- Severity colors: UNCHANGED

- [ ] **Step 2: Replace dark theme CSS custom properties**

In `dashboard.html`, replace the `html.theme-dark` block (lines 40-65):

```css
    html.theme-dark {
      --bg: #121110;
      --surface: #1e1c19;
      --text: #f0ece6;
      --text-sec: #a39a8e;
      --text-muted: #6e665c;
      --border: #302c27;
      --shadow: 0 1px 3px rgba(0,0,0,0.5);
      --accent: #4ecdb4;
      --accent-light: rgba(78,205,180,0.12);
      --gold: #d4b05c;
      --gold-light: rgba(212,176,92,0.1);
      --safe: #34d399;
      --safe-bg: rgba(52,211,153,0.12);
      --safe-border: rgba(52,211,153,0.3);
      --moderate: #fbbf24;
      --moderate-bg: rgba(251,191,36,0.1);
      --moderate-border: rgba(251,191,36,0.3);
      --high: #f87171;
      --high-bg: rgba(248,113,113,0.12);
      --high-border: rgba(248,113,113,0.3);
      --critical: #fca5a5;
      --critical-bg: rgba(252,165,165,0.12);
      --critical-border: rgba(252,165,165,0.3);
      --banner-breaking-bg: rgba(248,113,113,0.15);
      --banner-update-bg: rgba(212,176,92,0.08);
      --banner-stale-bg: rgba(110,102,92,0.12);
    }
```

Key changes from current dark:
- `--bg`: `#0f172a` -> `#121110` (warm charcoal)
- `--surface`: `#1e293b` -> `#1e1c19` (lacquer dark)
- `--text`: `#f1f5f9` -> `#f0ece6` (warm off-white)
- `--text-sec`: `#94a3b8` -> `#a39a8e` (warm gray)
- `--text-muted`: `#64748b` -> `#6e665c` (warm stone)
- `--border`: `#334155` -> `#302c27` (warm border)
- `--accent`: `#3b82f6` -> `#4ecdb4` (light celadon)
- `--accent-light`: blue -> celadon tint
- Added: `--gold`, `--gold-light`
- Dark severity: UNCHANGED

- [ ] **Step 3: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass. Custom property swaps don't affect behavioral tests.

- [ ] **Step 4: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): apply Son Mai Authority color palette (warm ivory + celadon teal)"
```

---

### Task 2: Add Be Vietnam Pro font and Vietnamese typography CSS

**Files:**
- Modify: `dashboard.html:11` (Google Fonts link)
- Modify: `dashboard.html` (add CSS after line 77, before app shell)

- [ ] **Step 1: Update Google Fonts link to include Be Vietnam Pro**

In `dashboard.html`, replace line 11:

```html
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

This adds `Be+Vietnam+Pro:wght@400;500;600;700` to the existing font load.

- [ ] **Step 2: Add Vietnamese typography CSS**

In `dashboard.html`, after the `.mono` rule (around line 77), add:

```css
    /* ===== VIETNAMESE TYPOGRAPHY ===== */
    html[lang="vi"] {
      font-family: "Be Vietnam Pro", "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
      line-height: 1.5;
    }
    html[lang="vi"] .topbar-title,
    html[lang="vi"] .hero-severity-label {
      font-family: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
    }
    html[lang="vi"] .topbar-title {
      letter-spacing: 0.3px;
    }
```

- [ ] **Step 3: Update the language switcher JS to set the html lang attribute**

Find the `setLang` function in the `<script>` section. It likely already sets `document.documentElement.lang`. Verify this by reading the function. If it does not set `lang`, add this line at the top of the function:

```javascript
document.documentElement.lang = code;
```

This is needed for the `html[lang="vi"]` CSS selector to activate.

- [ ] **Step 4: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "feat(i18n): add Be Vietnam Pro font with language-aware typography switching"
```

---

### Task 3: Add cultural visual elements (lotus, wave, celadon borders)

**Files:**
- Modify: `dashboard.html` (add CSS before the desktop media query, around line 900)

- [ ] **Step 1: Add lotus divider CSS**

In `dashboard.html`, before the `@media (min-width: 768px)` block (around line 902), add:

```css
    /* ===== SON MAI CULTURAL ELEMENTS ===== */
    .lotus-divider {
      display: flex;
      justify-content: center;
      padding: 8px 0;
    }
    .lotus-divider::before {
      content: '';
      display: block;
      width: 24px;
      height: 12px;
      border: 1.5px solid var(--border);
      border-radius: 50% 50% 0 0;
      border-bottom: none;
    }
```

- [ ] **Step 2: Add wave background texture CSS**

```css
    .app::before {
      content: '';
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: -1;
      background: repeating-linear-gradient(
        180deg,
        transparent 0px,
        transparent 40px,
        var(--border) 40px,
        transparent 41px
      );
      opacity: 0.04;
    }
    .app.severity-high::before,
    .app.severity-critical::before {
      opacity: 0;
    }
```

- [ ] **Step 3: Add celadon card border and gold accent CSS**

```css
    .feed-item {
      border-top: 2px solid transparent;
      border-image: linear-gradient(90deg, var(--accent), transparent) 1;
    }
    .unofficial-pill {
      background: var(--gold);
    }
    .ai-disclosure {
      color: var(--gold);
    }
```

Note: The `.feed-item` override adds a gradient top border. The `.unofficial-pill` already has `background: var(--text-sec)` at line 134 — this override changes it to `var(--gold)`. The `.ai-disclosure` already has `color: var(--text-muted)` at line 279 — this override changes it to `var(--gold)`.

Place these overrides AFTER the original rules so they take precedence, or use the same specificity and place them later in the cascade.

- [ ] **Step 4: Add severity class to app element in JS**

Find where the severity is set in the `<script>` section (likely in the `renderStatus` or `updateUI` function). Add logic to set the severity class on the `.app` element:

```javascript
var appEl = document.querySelector('.app');
appEl.className = 'app';
if (severity === 'high') appEl.classList.add('severity-high');
if (severity === 'critical') appEl.classList.add('severity-critical');
```

This enables the wave pattern suppression during high/critical severity states.

- [ ] **Step 5: Add lotus dividers to the Info tab HTML**

Find the Info tab panel in the HTML. Add `<div class="lotus-divider"></div>` between major info sections. For example, between the incident details and the shelters section, and between shelters and the methodology section. Add 2-3 dividers in the Info panel where information density is lower.

- [ ] **Step 6: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add dashboard.html
git commit -m "feat(design): add Son Mai cultural elements (lotus dividers, wave texture, celadon borders)"
```

---

### Task 4: Update DESIGN.md with new theme

**Files:**
- Modify: `DESIGN.md`

- [ ] **Step 1: Update DESIGN.md to reflect the Sơn Mài Authority theme**

Replace the relevant sections of `DESIGN.md`:

```markdown
# Design System -- GG MMA Tank Dashboard

## Product Context
- **What this is:** Real-time emergency situational awareness dashboard for the Garden Grove MMA tank crisis
- **Who it's for:** Panicking residents on phones during an active chemical/explosion emergency
- **Space/industry:** Emergency management, public safety
- **Project type:** Mobile-first dashboard / public utility

## Aesthetic Direction
- **Direction:** Sơn Mài Authority (Vietnamese lacquerware-inspired institutional calm)
- **Decoration level:** Minimal — warm surfaces and celadon accents do the work, cultural motifs appear only in low-density areas
- **Mood:** A trusted community resource telling you exactly what to do. Warm, culturally grounded, institutional. Made by and for the Vietnamese-American community of Little Saigon.
- **Memorable thing:** "I looked at this for 2 seconds and knew exactly what I needed to do — and it felt like it was made for our community."

## Typography
- **Display/Hero:** Plus Jakarta Sans 800 — geometric, warm, authoritative at large sizes
- **Body (English):** Plus Jakarta Sans 400/500/600 — consistent identity, excellent mobile readability
- **Body (Vietnamese):** Be Vietnam Pro 400/500/600/700 — purpose-built Vietnamese diacritical rendering
- **Data/Numbers:** IBM Plex Mono 500/600 — tabular alignment for temps, distances, timestamps
- **Loading:** Google Fonts CDN (3 families)
- **Scale:** Action (clamp 28-40px) / Headline (18-22px) / Body (14-16px) / Label (11-12px) / Data (13-14px mono)

## Color
- **Approach:** Culturally warm — lacquerware ivory surfaces, celadon teal accents from Ly dynasty ceramics
- **Surfaces (light):** Background #faf8f5 (warm ivory) / Surface #ffffff
- **Surfaces (dark):** Background #121110 (warm charcoal) / Surface #1e1c19 (lacquer dark)
- **Text (light):** Primary #1a1612 / Secondary #5c5347 / Muted #8a8279
- **Text (dark):** Primary #f0ece6 / Secondary #a39a8e / Muted #6e665c
- **Authority accent:** #0e6f5e (deep celadon teal, light) / #4ecdb4 (light celadon, dark)
- **Gold accent:** #9e7c29 (light) / #d4b05c (dark) — used for UNOFFICIAL pill and AI disclosure
- **Severity (UNCHANGED):**
  - Safe: #059669 (emerald)
  - Moderate: #d97706 (amber)
  - High: #dc2626 (red)
  - Critical: #7f1d1d (dark red)
- **Dark mode:** Warm charcoal base, celadon brightened for contrast

## Cultural Elements
- **Lotus petal divider:** Minimal line-art petal silhouette as section divider in Info tab
- **Wave background:** 4% opacity repeating pattern on page background; suppressed during high/critical severity
- **Celadon card borders:** Gradient accent-to-transparent top border on news feed items
- **Gold pill accent:** UNOFFICIAL badge and AI disclosure use gold for institutional authority

## Spacing
- **Base unit:** 4px
- **Density:** Compact — phones need information density
- **Scale:** 2xs(2px) xs(4px) sm(8px) md(12px) lg(16px) xl(24px) 2xl(32px)

## Layout
- **Approach:** Mobile-first command card
- **Structure:** Flex column, 100dvh, no outer scroll
  - Header (36px) + conditional banner
  - Hero action zone (~100px): "WHAT SHOULD I DO?" + action + instruction
  - Stats strip (32px): wind, tank temp, evac count, refresh countdown
  - Tabbed content (flex: 1, internal scroll only)
  - Bottom tab bar (48px+ with safe-area-inset-bottom)
- **Tabs:** Map | News | Check | Info
- **Desktop (>768px):** Same structure, wider content
- **Border radius:** sm:4px, md:6px, lg:8px

## Motion
- **Approach:** Minimal-functional
- **Animations:** Breaking banner pulse (1.5s), tab switch (150ms opacity), refresh countdown bar (linear 30s)
- **Easing:** ease-out entrances, ease-in exits
- **Reduced motion:** Respected via prefers-reduced-motion

## Core UX Principle
The hero answers "What should I do?" not "What zone am I in?"
- outside/outside_downwind: "STAY PUT. Close windows. Monitor for updates."
- inside: "LEAVE NOW. Evacuate per OCFA guidance."
- resolved: "ALL CLEAR. Evacuation lifted."
- unknown: "CHECK YOUR STATUS. Use safety checker or ggcity.org/emergency."

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-24 | Calm Authority aesthetic | Mobile-first emergency dashboard needs institutional trust + outdoor phone readability |
| 2026-05-24 | "What should I do?" hero | More actionable than status-only. Users need action, not data. |
| 2026-05-24 | 100dvh no-scroll command card | Panicking users should never need to scroll. Tab navigation for detail. |
| 2026-05-24 | Breaking news + videos in same tab | User requirement: these belong together. Single "News" tab. |
| 2026-05-24 | 60s adaptive wind polling | NOAA updates every ~10-20 min. 60s base catches updates fast. Exponential backoff prevents errors. |
| 2026-05-24 | Plus Jakarta Sans | Geometric, warm, authoritative. Not overused. Excellent mobile legibility. |
| 2026-05-25 | Son Mai Authority theme | Lacquerware-inspired warmth for Vietnamese-American community. Celadon teal replaces blue for cultural resonance. |
| 2026-05-25 | Be Vietnam Pro for vi body | Purpose-built Vietnamese diacritical rendering. Plus Jakarta Sans remains brand typeface. |
| 2026-05-25 | Always-on cultural theme | Community IS Vietnamese-American. Theme honors identity regardless of language selection. |
| 2026-05-25 | Severity colors unchanged | Safety-critical signals. Cultural theme works around them, never over them. |
```

- [ ] **Step 2: Run eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add DESIGN.md
git commit -m "docs: update DESIGN.md with Son Mai Authority theme system"
```
