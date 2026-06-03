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
- **Map tab:** MapLibre GL JS v4.7.1 (WebGL, UMD bundle) rendering OpenFreeMap vector tiles (Liberty style). GeoJSON evacuation polygon from config.json, 9 shelter markers with tappable popups. GPU-accelerated pan/zoom. No API key, no rate limits, $0 at any traffic level.
- **Desktop (>768px):** Same structure, wider content
- **Border radius:** sm:4px, md:6px, lg:8px

## Motion
- **Approach:** Minimal-functional
- **Animations:** Breaking banner pulse (1.5s), tab switch (150ms opacity), refresh countdown bar (linear 30s)
- **Easing:** ease-out entrances, ease-in exits
- **Reduced motion:** Respected via prefers-reduced-motion

## Core UX Principle
The hero shows severity status and situation bullets — never directives.
- Information conduit: amplify official information, route to authorities
- Never tell users to evacuate, stay, or take specific action
- Severity word + "What changed" bullets give situational awareness
- Map tab links to Zonehaven's official zone checker for evacuation status
- All information defers to official channels for authoritative orders

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
| 2026-05-26 | Conduit cleanup: address checker + severity removed | Pure information conduit — no functional output that could imply authority. Section 230 safe harbor. |
| 2026-05-27 | MapLibre GL JS v4.7.1 + OpenFreeMap vector tiles | GPU-accelerated WebGL map replacing static JPEG + SVG overlay. $0, no API key, no rate limits. UMD bundle for single-file dashboard. |
| 2026-05-27 | OpenFreeMap over Mapbox/Google/Protomaps | Zero cost at any traffic, no registration, survived 100K req/sec stress test. CARTO tiles (previous) went enterprise-only. |
| 2026-05-27 | Dark mode map tiles | OpenFreeMap dark style swapped on theme toggle. Evacuation polygon + markers persist across style changes. |
| 2026-05-29 | v0.17 = full-scope design-complete (Map+News+Info+Timeline+tablet), NOT Map-only | Founder: the design-complete gate must address ALL observations, concerns, and instructions. |
| 2026-05-29 | L1 chrome clamp-with-pixel-floor | Cap chrome to ~1/3 viewport but guarantee the persistent disclosure is never clipped on short screens. |
| 2026-05-29 | V1 legend-only border fix (map #D95F02 unchanged) | Real defect is the faint legend swatch border, not the perimeter color. |
| 2026-05-29 | D1 wind "Wind — NOAA" + "(weather data, not safety guidance)" | Source-attributed fact; micro-label prevents misreading wind as shelter guidance. Wind never ranks/recolors shelters. |
| 2026-05-29 | D2 'Tiếng Việt' sign-post, vi.ready=false (standing posture) | Reviewer reachable but NOT scheduled → withhold-and-amplify is the durable design, not a temporary patch. G1. |
| 2026-05-29 | Info sub-tabs: Status \| Resources \| About | "Get Help" over-claims (conduit routes to help, doesn't provide it); "Sources" folded under About to remove the Resources/Sources label clash. |
| 2026-05-29 | Timeline: curate + archive toggle | Keep the data; default-show ~critical/major milestones, archive toggle for forensic depth. Fits the during-incident thesis without dropping history. |
| 2026-05-29 | Tablet: comprehensive responsive (600–767 + 768–1023) | All-concerns scope + portfolio stakes warrant proper tablet handling, not a deferral. |
| 2026-05-29 | News dedupe deferred | Dedupe code is proven in tests but effectively a no-op on the static seed; defer to a post-incident video-sourcing strategy. |
| 2026-06-01 | Info tab archive-clarity (scope B) | "Status"→"What happened"; Status gets its own derived historical disclaimer; Resources leads with Official Sources, then a collapsed de-carded "Historical resources" fold (shelters + community as dense rows, no card chrome); About fold retitled "Sources checked"; AI disclosure promoted to 12px gold; disclaimer split with "In an emergency, call 911." on its own line. Cross-model review (Codex gpt-5.5 + blind Claude subagent) hard-rejected the card-grid-first Resources panel. Full structural `.info-section` refactor (scope C) deferred. |
| 2026-06-02 | Map + News design-complete; Info is the remaining alignment work | Map/News patterns are the reference the rest of the app aligns to; the Info tab must adopt that visual language, gain clearer individually-navigable sub-tabs, and use the documented type scale consistently. Exact sub-tab set is a pending design decision. (Also: dropped the trailing period from the safety-strip disclaimer — it reads as a label flowing into "· Terms".) |
| 2026-06-02 | Info tab → 6 scrollable sub-tabs (Summary \| Officials \| Shelters \| Schools \| Recovery \| About) | Rebuilt Info onto the unified `.info-section` primitives so it reads as one system with Map/News. Each panel leads with a one-line descriptor (`.info-desc`); the sub-tab chrome is generated from one `{id,label,descriptor}` array. The sub-tab bar is horizontally **scrollable** (`overflow-x:auto` + scroll-snap + a right-edge fade peek) — a conscious deviation from the equal-width reference chrome, chosen for granularity: six individually-findable sections beat three squished equal-width tabs. Tab-focus + `aria-selected` kept; arrow-key roving deliberately not added (would diverge from the app's other tabs). AI disclosure stays in the About tab (binding honesty); methodology/who-made-it narrative moved to the README. Dead `renderInfoShelters` and the parallel `.resources-*`/`.community-resource-card`/`.shelters-grid`/`.official-link` markup+CSS retired; inline `font-size` killed via `.info-fine`/`.info-desc`/`.info-who-body`. |

## v0.17 Design-Complete Gate (2026-05-29)

The founder's binding "design-complete" bar, made finite so it can be reached (not a receding feeling). v0.17 is **all-concerns**, not Map-only. Done = every item below passes, verified, and recorded here.

**Build order (foundation-first):** B2 → L1 → L2 → V1 → B1 → D1 → D2 → News video cards → Info sub-tabs → Timeline curate → tablet → eval + visual verify + cache bump + docs.

**Gate items (17):**
1. **B2** — map renders (not blank) on cached mobile reload @ 375x812/375x667; `_ggMap` assigned at construction; `ResizeObserver` on `.map-outer`; `pageshow`/`orientationchange` fire `resize()`.
2. **L1** — chrome clamps to `max(Npx, 33dvh)`; persistent disclosure never clipped at any mobile/tablet height; map is the flex residue.
3. **L2** — tab-bar at bottom on desktop (`order:1` @ ≥600px); top on mobile.
4. **V1** — `.legend-icon-evac` border opaque/visible; map `#D95F02` paint sites unchanged.
5. **B1** — Share: clipboard fallback + `role=status aria-live=polite` toast (`share.copied`, English fallback per G1).
6. **D1** — wind shows "Wind — NOAA" + "(weather data, not safety guidance)"; no directional verbs; never ranks/recolors shelters.
7. **D2** — 'Tiếng Việt' sign-post routes to official VI; `vi.ready=false`; no machine-translated copy; `test_vietnamese_held_with_official_fallback` passes.
8. **News video cards** — thumbnail + duration badge + play affordance; 16:9; YouTube CDN thumbnail; no CSP violation.
9. **News dedupe** — decision documented (deferred; no-op in practice).
10. **Info sub-tabs** — Status | Resources | About (Resources = shelters + schools + community resources; About = who-made-this + sources/methods).
11. **Timeline** — curate + archive toggle (default critical/major; archive for the rest); no orphaned refs.
12. **Tablet** — comprehensive 600–767 + 768–1023 media handling; renders clean at the full viewport matrix.
13. **Eval** — `python eval/run_all.py --skip integration` → 48/48 by scorecard (never `--quiet`); the +1 over v0.16 is the new `test_new_strings_english_only` G1 guard (new i18n keys must be English-only until fluent-native verification).
14. **Visual verify** — Edge-headless at 375x812, 375x667, 700x900, 768x1024, 1024x768, 1280x720, light + dark; no clipping/reflow.
15. **Cache** — `CACHE_NAME` v7→v8 on deploy (dashboard.html changes); reason in CHANGELOG.
16. **Docs + rename refs** — CHANGELOG + this gate; constraints audit (conduit/G1/honesty/noindex); update README/USAGE/docs/DATA_SYNC current-facing `gg-tank-dashboard`→`gg-tank-watch` refs (leave historical records).
17. **Submission-ready** — all of the above merged + deployed; Fellows application can submit.

**Milestone ladder (safety net, not a scope cut — the gate is M3):** M1 Map-foundation (B2+L1+L2+V1+B1) · M2 +D1+D2+video cards · **M3 = full all-concerns (the gate).**

**Binding constraints:** conduit (no authored directives) · G1 (no MT safety copy; vi held) · persistent honesty disclosure · `noindex` ON (vercel.json header). **Verified non-issues:** noindex meta tag, Info "buried disclaimer", `.vercel/project.json` staleness (gitignored).

## Tab Design Status — Map, News & Info design-complete (Info: 2026-06-02)

**Map, News, and Info are now design-complete.** Their patterns are the reference the rest of the app aligns to — do not restyle them without being asked. Info was brought up to that bar on 2026-06-02: four single-row sub-tabs on the unified `.info-section` primitives.

### Reference patterns (carry these into Info)
- **Type scale (single source of truth):** body Plus Jakarta Sans 14px / line-height 1.4; data & numbers in IBM Plex Mono (`.mono` / `.sa-mono`, tabular-nums); headings, section titles, and 11–12px labels per the Typography block above. No per-element inline `font-size` overrides.
- **Sub-navigation chrome:** the underline-accent sub-tab bar (`.info-subtabs` / `.info-subtab`) — celadon `border-bottom` on `.active`, sticky to the top of the scroll area, 44px min touch target — is the established sub-tab pattern (it reused the original News sub-tab styling). Info's 4-tab bar uses the **equal-width single-row** variant (`flex:1 1 0`, centered labels) — all four tabs fit 320–375px+ with no horizontal scroll. News renders a single sourced feed with filter chips in the same celadon-accent family.
- **Surfaces & color:** `--sa-surface` cards on the `--sa-bg` page, `--sa-border` hairlines, celadon (`--sa-celadon`) for active/interactive accents; gold is reserved for the UNOFFICIAL pill and the AI disclosure.
- **Spacing:** 4px base unit, compact density.

### Info tab — design-complete (2026-06-02)
Info was first rebuilt into 6 sub-tabs (PR #108), then consolidated to **4 single-row sub-tabs** — **Summary | Officials | Resources | About** (`renderInfoTab` in `dashboard.html`) — on the unified `.info-section` primitives, so it reads as one system with Map/News. Shelters, Schools, and Recovery are merged into the Resources panel as labeled sections (`.info-section-title`) so the bar fits one row (max signal / min noise), while Officials stays a pure route-to-officials tab. What shipped:
1. **Aligned to Map/News** — same type scale, spacing, surface/border treatment, and celadon accents; all panels use `.info-section`/`.info-row`/`.info-kv-row` primitives.
2. **Individually-navigable sub-tabs** — Summary (peak facts), Officials (official channels), Resources (shelters / school closures / recovery aid), and About, each led by a distinct `.info-desc` descriptor band; the chrome is generated from one `{id,label,descriptor}` array.
3. **Type-scale consistency** — the ad-hoc inline `style="font-size:…"` overrides are gone, replaced by `.info-fine` (11px) / `.info-desc` (12.5px) / `.info-who-body` (12px); guarded by `test_no_inline_font_size_in_info_panels`.

**2026-06-02 refinement:** the earlier scrollable 6-tab bar (content-width + `overflow-x:auto` + scroll-snap + edge fade) clipped "Recovery" and hid "About" at 375px, so it was reversed — consolidated to 4 equal-width tabs that fit one row with no scroll, and the per-panel `.info-desc` descriptor was restyled into a distinct inset band (3px celadon left border + `--sa-surface` tint + radius, mirroring `.resolved-note`). Tab-focus + `aria-selected` are kept; arrow-key roving is deliberately not added (would diverge from the app's other tabs). Guarded by `test_subtabs_single_row_no_hscroll` + `test_descriptor_is_distinct_block`.

**Status:** DONE — eval green (171/171), signed-Edge verified light + dark @320–375px. Map/News remain the off-limits reference patterns.

> **Lowercase-`i` legibility — root-caused 2026-06-02.** The dotless `i` in "official" was the `fi`/`ffi` OpenType ligature dropping the i's tittle — only the `i` inside the `ffi` cluster was affected, and it's size-invariant (the initial 13px guess was wrong and was reverted). Fixed globally with `font-variant-ligatures: none` on `html, body` (brand typeface unchanged), guarded by `test_no_dotless_ligatures`. Verified locally on Blink (Edge headless) and deterministic across Chrome/Edge/Android Chrome.
