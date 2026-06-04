# GG Tank Watch — Map Page Mobile Cleanup Plan

> Produced by the `mobile-map-cleanup` workflow (5 audit lenses → adversarial verify → synthesis). Source-grounded; live browser verification was BLOCKED by a Windows Application Control policy at authoring time.

## Goal
Fix the mobile (iPhone-class 360–414px) Map tab — the default/active surface for ~50,000 evacuees, most on phones — so the on-map legend is no longer buried by the full-width "Check Address" button, Vietnamese users get a translated legend, zoom controls are tappable, and attribution is both legible and license-correct. Single-file edits to `dashboard.html`, smallest diff, conduit-only (route to officials, author no directives), G1-respecting (no machine-translated safety copy).

## Architecture
- **All map CSS is BASE (mobile) CSS** (`dashboard.html:570–683`). Every `@media` in the file is `min-width` (600/768 = tablet+), `prefers-reduced-motion`, or `print` — zero `max-width`/`max-height`/`orientation` queries. Mobile defects live in base CSS; fixes ARE base-CSS changes; no media query is added.
- **Bottom band of `.map-outer`** stacks three absolutely-positioned overlays at the bottom edge: `.map-legend` (bottom-left), `.static-map-actions`→`.zone-check-btn` (full-width, `bottom:0`), `.static-map-attribution` (bottom-right). Button band ~68px tall (10+48+10). Fix = lift legend `bottom` above the band; leave button at `bottom:0` (safety CTA stays prominent).
- **i18n engine** applies `el.textContent = t(key)` on every `[data-i18n]`. `textContent` replaces all child nodes — so `data-i18n` MUST go on a dedicated text `<span>` sibling of `.legend-icon`, never on `.legend-row` (would delete the icon + emoji). `t()` returns the raw key id for a missing string, so a `data-i18n` pointing at a non-existent `legend.facility` would render "legend.facility" — hence Facility stays hardcoded English.
- **Safe-area:** `viewport-fit=cover`; `env(safe-area-inset-*)` used once, on `.tab-bar`. The tab-bar sits below the map and absorbs the home-indicator inset; the map's `bottom:0` button is the tab-bar's top edge, NOT the screen edge — so NO safe-area term is added to map overlays.
- **Eval reality:** `python eval/run_all.py --skip integration` (45 tests) is Python/data-contract only. It does NOT exercise CSS/markup/layout. Run after every task to prove no data regression; it CANNOT catch a mobile layout bug.
- **Visual verification BLOCKED** by Windows AppControl on the browser tool. Each task lists what to eyeball at 375px once unblocked.

## Out of scope (deferred / rejected — do NOT bundle)
- prefers-reduced-motion for the MapLibre camera/zoom (needs net-new JS; defer to a motion pass).
- target=_blank "opens in new tab" cue (AAA; adds G1 VI debt; rejected).
- z-index reshuffle (after Task 2 there's no residual overlap; earns nothing).
- Landscape `@media (max-height:480px)` legend rule (would be first max-height query; gate on in-browser confirmation).
- Safe-area insets on map overlays (tab-bar already handles it; would re-break the collision).

---

## Task 1 — (SAFEST, no render change) Add wind indicator to map aria-label; KEEP "GKN Aerospace"
`dashboard.html:1547`. config.json confirms the facility IS "GKN Aerospace" — keep it. Add wind mention.
- Commit: `fix(a11y): name wind indicator in map aria-label`

## Task 2 — (LOAD-BEARING) Lift legend above the button band
`dashboard.html:599–602`: `.map-legend bottom: 8px` → `bottom: 72px` (clears ~68px band + gap). One property; no media query.
- Commit: `fix(map): lift mobile legend above the action button band`

## Task 3 — (i18n/G1) Wire existing VI legend strings; leave Facility English, flag for Nancy
`dashboard.html:1552–1556`. `data-i18n` on a text `<span>` sibling of `.legend-icon` (wrapping `.legend-row` would textContent-wipe the icon). Wire `legend.evac`/`legend.shelter` only. Facility stays English + G1 comment.
- G1 flag (PR body): `legend.facility` needs native-speaker VI from Nancy.
- Commit: `fix(i18n): wire existing VI legend strings; flag legend.facility for review`

## Task 4 — (optional, ship with 3) Defensive line-height on VI button
`dashboard.html:667–668`: add `line-height: 1.25;` for clean 2-line VI wrap. No `white-space:nowrap`.
- Commit: `style(map): add line-height for 2-line VI Check-Address wrap`

## Task 5 — (TOUCH) Enlarge zoom buttons to 40px
`dashboard.html:581–582`: add `.maplibregl-ctrl-group button { width: 40px; height: 40px; }`.
- Commit: `fix(map): enlarge zoom controls to 40px for mobile touch targets`

## Task 6 — (A11Y) Group/decorative semantics on legend
Post-Task-3 markup: `.map-legend` gets `role="group" aria-label="Map legend"` (English-only, G1-flagged); icon spans get `aria-hidden="true"`.
- Commit: `fix(a11y): add group + decorative semantics to map legend`

## Task 7 — (A11Y/LICENSE) Attribution surface chip (apply now) + OpenFreeMap credit (GATED)
`dashboard.html:675–683`: add `background: var(--sa-surface); padding: 1px 4px; border-radius: 3px;` to `.static-map-attribution` (contrast chip — apply now). The OpenFreeMap credit-string change (`:1560`) is GATED on verifying exact license wording — hold and flag.
- Commit: `fix(map): add attribution surface chip`

## Task 8 — (RESPONSIVE) fitBounds asymmetric padding
`dashboard.html:2907`: `{ padding: 20, maxZoom: 11 }` → `{ padding: { top: 40, bottom: 80, left: 20, right: 20 }, maxZoom: 11 }`.
- Commit: `fix(map): reserve overlay space in fitBounds padding`

## Task 9 — (DARK MODE, VERIFICATION-GATED — DEFER) Lighten facility marker
`dashboard.html:2887` + `:645`: `#444` → `#6b6b6b` on BOTH. DO NOT apply while visual verification is blocked. Deferred to post-unblock visual pass.

## Sequencing & git hygiene
Safest-first: 1 → 2 → 3(+4) → 5 → 6 → 7a → 8 → (9 deferred). Stage explicit paths (`git add dashboard.html`), never `-A`. Branch → PR → merge. PR body carries G1 flags (legend.facility VI + "Map legend" group-label VI, both pending Nancy) and the note that visual verification was BLOCKED by AppControl — the per-task eyeball checklist is the post-merge QA gate.
