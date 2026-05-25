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
