# Changelog

All notable changes to GG Tank Watch. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) loosely; dates in `YYYY-MM-DD`.

> **Frozen archive.** This changelog covers v0 → v0.28 (May–June 2026). The incident resolved May 26, 2026; the dashboard is now a frozen historical archive and no longer updates.

## [v0.28] — 2026-06-03 (About "Why this was made" + prominent Accessibility link + full Resources titles)

User-directed Info-tab update. Acceptance rubric amended first (the fixed target), then test-first.
Eval **194/194**; signed-Edge (Playwright msedge channel) vision-verified at 320/360/375/390/430px,
light + dark, with `getBoundingClientRect` geometry probes across the About and Resources sub-tabs.

### Added
- **About → "Why this was made"** section: a short, resident-first note placed under the binding AI
  disclosure (which stays the first line). Conduit-true — it states the app gathered scattered
  official updates into one place and routed back to the officials in charge, authoring no directives.
  Overrides the earlier "methodology / who-made-it narrative lives in the README, not in-app" posture.

### Changed
- **Accessibility link → prominent, centered, tappable button** (`.info-a11y-btn`): bordered celadon
  pill, ≥44px tap target, centered below the Sources fold, with a monochrome universal-access glyph —
  was a quiet 11px footer link. More apparent and more accessible (user 2026-06-03).
- **Resources section titles name each section in full:** SHELTERS / SCHOOL CLOSURES / RECOVERY AID
  (the `info.subtab.schools` / `info.subtab.recovery` values were lengthened from "Schools"/"Recovery";
  render single-line down to 320px).
- service-worker `CACHE_NAME` bumped `v65 → v66`.

## [v0.27] — 2026-06-03 (Info data freeze + refresh-proof Official tags + typography pass)

Follow-up to v0.26. Re-freezes the archive data (an upstream cloud auto-refresh had been
re-stamping timestamps and accumulating post-all-clear events), makes the Sources "Official"
tags immune to that refresh, and a typography-consistency pass per user feedback. Eval
**191/191**; signed-Edge vision-verified (light + dark, 320–768px) with `getComputedStyle`
font probes across all four sub-tabs.

### Changed
- **Official tags are now URL-derived** (`isOfficialSourceUrl()` → `ggcity.org` / `ocgov.com`),
  not a `status.json` `official` flag — the data-refresh regenerated `status.json` and stripped
  the flag, so the tags vanished; deriving from the (preserved) source URL is refresh-proof.
- **Typography harmonized across the four sub-tabs** (user 2026-06-03): About primary content
  (`.info-ai-disclosure` + `.source-item`) → **13px** to match the other panels' rows (were 12px
  outliers); the Officials channel name → dark `--sa-text` (was the muted key color, read lighter
  than the shelter names); group/section titles (`.info-section-title` for Shelters/Schools/
  Recovery **and** the About `.info-sources-toggle`) → **11px/700/caps/`--sa-text-2`** so a
  heading stands out above its 13px items.
- **About copy/layout:** the AI disclosure reads "Summaries in this **archive**…" (was "on this
  page"); the Sources caption shortened to one line; the **Accessibility** link moved to the
  bottom of About (a quiet footer link, below the Sources fold, instead of under the disclosure).
- service-worker `CACHE_NAME` bumped `v64 → v65`.

### Removed / Frozen (data)
- **`timeline.json`:** removed **25 post-all-clear events** (May 28 → Jun 3) that the upstream
  auto-refresh had accumulated — the archive is May 21–26 (boundary `2026-05-27T02:30:00Z`), so
  the timeline is back to its 67 in-window events. (`timeline.json` is a static source for the
  Summary peak facts, not fetched at runtime — zero UI impact.)
- **`status.json`:** froze `last_updated_iso` / `next_check_at_iso` / per-source `fetched_iso` to
  the all-clear so the frozen archive stops presenting a live "last updated" time (the dashboard
  already ignores `last_updated_iso` for display); restored the 9-source provenance set; dropped
  the now-unused per-source `official` flag.

## [v0.26] — 2026-06-03 (Info sub-tab polish — Officials descriptions, About cleanup, ghost lines)

User-directed polish across the four Info sub-tabs. Acceptance rubric amended first as the
fixed target; test-first (guards red → green); eval green (**191/191**); vision-verified in
signed Edge (light + dark, 320/360/375/390/430/768px) with `getBoundingClientRect` geometry
probes on every rubric §0 hard constraint; cross-checked by a 4-lens adversarial review
(safety/transparency, eval-honesty, copy accuracy, rubric/surgical — all pass, zero
blocker/major).

### Added
- **Officials:** a one-line `.info-row-desc` description under each of the 3 official channels
  (what the city page / Zonehaven lookup / AlertOC sign-up is for), replacing the removed
  generic "No single source…" note.
- **About → Sources:** the fold is **open by default**, opens with a one-line caption stating
  what the list is (the provenance trail the pipeline checked), and tags the official
  City/County sources with an **"Official"** label (`status.json` flags 2 sources `official`).
- **Eval guards** (`eval/test_info_archive_clarity.py`): `test_officials_note_removed_and_descriptions_present`,
  `test_resources_descriptor_one_line`, `test_sources_caption_open_and_official_labels`,
  `test_no_ghost_lines_background`.

### Changed
- **About:** the binding AI-assistance disclosure renders at body near-black `--sa-text` (12px),
  in line with the other sub-tabs — the gold accent was dropped (text + first-line placement
  carry the binding-honesty property, not the color).
- **About:** removed the duplicate "Current life-safety info…" routing line (`disclosure.aiRoute`)
  — concrete 911/ggcity routing is carried persistently by the safety strip on every tab; the
  routing-concreteness guard was re-pointed to the strip.
- **About:** dropped the Terms link (still in the persistent strip), kept Accessibility (its only
  in-app entry point).
- **Resources:** descriptor band shortened to one line.
- **Removed the `.sa-wave-bg` "lined-paper" ghost lines** (the `repeating-linear-gradient` that
  painted a faint horizontal line every ~22px on every Info sub-tab); the intentional `1px solid`
  item separators stay.
- service-worker `CACHE_NAME` bumped `v63 → v64`.

## [v0.25] — 2026-06-02 (Info sub-tab fit guard)

Deterministic regression guard for the #108 failure class — the Info sub-tab bar must be
structurally incapable of one-row overflow. No browser, no new dependency; runs in the
existing text-only eval suite by asserting the causal layout invariant rather than pixels.

### Added
- **`eval/test_info_subtab_fit.py`** — asserts the invariant that guarantees the sub-tab bar
  fits one row: `.info-subtabs` carries no `overflow-x`/`scroll-snap`/`flex-wrap` anti-pattern
  (the #108 scrollable-bar that clipped "Recovery"/hid "About" at 375px), `.info-subtab` is
  `flex:1 1 0` + `min-width:0`, and the bar stays ≤4 tabs.

### Changed
- **`.info-subtab` hardened with `min-width: 0`** so equal-width flex is overflow-proof for any
  label length (no visual change to the current four short labels).
- service-worker `CACHE_NAME` bumped `v60 → v61`.

## [v0.24] — 2026-06-02 (Info tab polish batch — typography, spacing, content, honesty)

Follow-up polish on the consolidated 4-sub-tab Info tab (PR #109). Eleven live-observed
items (A–K) went through a full `/autoplan` review (4 independent voices + Codex): A–J
shipped, **K cut**. Eval green (**179/179**); vision-verified in signed Edge (light+dark, 320/375/768).

### Changed
- **Unified the Summary type scale** — dropped the 11px `.info-fine` downscale on the evacuation-zone value so every Summary key/value reads at 13px (B).
- **Gave Officials rows breathing room** — `.info-row` vertical padding `3px → 9px` with a hairline separator between rows (`:last-child` none) so they read as a list, not a cramped stack (D/E).
- **Restructured shelter rows** into a dedicated `.shelter-row` flex layout — name + city in a text column, "Directions ↗" pinned top-right — so a long shelter name wraps without dragging the action out of alignment (F).
- **Matched the News filter-chip bar height to the Info sub-tab bar** (both 52px; chip-bar bottom padding aligned) so toggling Info ↔ News no longer jumps the bar (A).
- **Shortened the About descriptor** to drop the orphaned "it." ("…and the sources behind it." → "…and its sources.") (G), and **added the horizontal gutter** to the About panel body so the disclosure/terms/sources are inset, not edge-to-edge (H).
- **Split the AI-assistance disclosure into two lines** — the compiled-with-AI/checked-by-a-person note, then the life-safety routing line reframed from an imperative to "Current life-safety info: ggcity.org/emergency or 911" (I).
- service-worker `CACHE_NAME` bumped `v59 → v60`.

### Added
- **Five sourced archive facts to the Summary** — Substance (Methyl methacrylate / MMA), Facility (GKN Aerospace, Garden Grove), Tank (34,000-gallon), Incident window (May 21–26, 2026), Outcome (no injuries, 0 displaced) — as static archive copy in narrative order, decoupled from the cleared resolved snapshot; neutral labels, no authority chrome (C).

### Removed
- **The per-source "checked {date}" suffix** from the About sources fold, and **retitled the fold "Sources checked" → "Sources"** (J, archive honesty): the per-source `fetched_iso` re-stamps on every refresh, so a post-resolution date on a frozen May-26 archive read like ongoing monitoring. The `fetched_iso` data contract stays in `status.json`; only the misleading UI surfacing was removed. Also dropped the now-orphaned `info.sources.checked` i18n key and `.source-time` CSS.

### Cut
- **Mobile pull-to-refresh (K)** — on a frozen archive a refresh re-fetches identical data and would imply live updates, contradicting the archive framing (`REFRESH_MS=null`, cache-first `status.json`, archived pipeline). Flagged unanimously by the review (4 voices + Codex) as a safety-contract risk and cut.

### Tests
- Added grep guards for A/B/C/D-E/F/G/H/I in `test_info_archive_clarity.py`; rewrote the J guards to assert the per-source date is GONE (`test_sources_checked_date_omitted`, the relaxed `test_feed_renders_source_attribution`, the retitled-fold `test_about_disclosure_and_sources`) while keeping the `fetched_iso` data-shape + anti-fabrication guards intact; updated `test_routing_jargon` to find the life-safety routing across the split disclosure; bumped the two SW tripwire tests `v59 → v60`.

## [v0.23] — 2026-06-02 (Info tab → 6 scrollable sub-tabs)

### Changed
- **Rebuilt the Info tab into 6 individually-navigable, horizontally-scrollable sub-tabs** — **Summary · Officials · Shelters · Schools · Recovery · About** — on the unified `.info-section` primitives, so Info reads as one system with the design-complete Map/News tabs. The sub-tab chrome + per-panel one-line descriptors (`.info-desc`) are generated from a single `{id,label,descriptor}` array. The bar is horizontally scrollable (`overflow-x:auto` + scroll-snap + a right-edge fade peek) — a conscious deviation from the equal-width reference chrome, chosen so all six sections stay individually findable. The AI-assistance disclosure stays in the About tab (binding honesty); the methodology / who-made-it narrative moved to the README.
- **Officials channels re-expressed as unified `.info-row` links** (the standalone `.official-link` card chrome retired), keeping the "Official" label and route-to-officials framing.
- service-worker `CACHE_NAME` bumped `v57 → v58` so cached residents re-fetch the new shell.

### Removed
- **Dead `renderInfoShelters()`** (its `#info-shelter-list` was never emitted, so it always early-returned) + its orphaned `.info-shelter-*` CSS, and the parallel Resources system (`renderResources` and the `.resources-section` / `.community-resource-card` / `.shelters-grid` / `.official-link` markup + CSS, plus the `.info-fold` / `.info-historical` styles) — Shelters and Recovery now render from config via `renderInfoConfigData`.
- **Ad-hoc inline `font-size`** across the Info render path, replaced by `.info-fine` (11px) / `.info-desc` (12px) / `.info-who-body` (12px); guarded by `test_no_inline_font_size_in_info_panels`.

### Tests
- Consolidated the Info behavioral contract into `test_info_archive_clarity.py` (6 sub-tabs present, per-panel descriptors, Officials 3 links, Recovery panel, sourced peak facts, About disclosure, retired-classes-gone markup+CSS, no-inline-font-size, dead-shelter-removed) and realigned the `test_info_disclosures` / `test_one_banner` About guards to the lean 6-tab About. Eval green.

## [v0.22] — 2026-06-02 (dotless-`i` root cause: a ligature, not size)

### Fixed
- **The dotless lowercase `i` was an `fi`/`ffi` OpenType ligature, not a rasterizer/size issue — the v0.21 diagnosis was wrong.** The tell: only the `i` *inside* the `ffi` cluster of "official" lost its dot (the standalone `i` was fine), and the v0.21 13px bump didn't help — ligature substitution is size-invariant and identical across Blink. Disabled common ligatures site-wide on `html, body` (`font-variant-ligatures: none`; brand typeface unchanged) so every `i` keeps its dot anywhere on the site, and **reverted the misdiagnosed v0.21 13px bump** on `.safety-strip-info`. Verified by rendering on Blink locally (Edge headless): "official" now shows separated f's and dotted `i`s, deterministic across Chrome/Edge/Android Chrome. New guard `test_no_dotless_ligatures` replaces the wrong `test_safety_strip_disclaimer_legible_size`; eval stays green (**163/163**).
- service-worker `CACHE_NAME` bumped `v56 → v57`.

## [v0.21] — 2026-06-02 (disclaimer copy + i-legibility + tab-design-status doc)

### Changed
- **Dropped the trailing period from the persistent safety-strip disclaimer** — "Informational only — not official**.**" → "Informational only — not official". The line reads as a label that flows into the "· Terms" link, so the hard stop looked like a stray double-stop. Fixed in both the rendered i18n `en` value and the no-JS fallback `<span>`. Guarded by the new `test_safety_strip_disclaimer_has_no_trailing_period` (eval **161 → 162**, all green).
- **Fixed the dotless lowercase `i` in the safety-strip disclaimer on Android Chrome.** At the inherited 11.5px-bold size, Plus Jakarta Sans's lowercase-`i` tittle dropped out of Android Chrome's rasterizer, so "official" read dotless (confirmed on a real device). Lifted `.safety-strip-info` to an explicit `font-size: 13px` (brand typeface unchanged); guarded by `test_safety_strip_disclaimer_legible_size`. Pending on-device verification.
- service-worker `CACHE_NAME` bumped `v55 → v56` so cached residents re-fetch the updated shell.

### Docs
- **`DESIGN.md` — tab design status.** Recorded that the **Map and News tabs are design-complete** (their patterns are the reference the rest of the app aligns to — don't restyle them without being asked) and that the **Info tab is the sole remaining tab**: its work is to adopt the Map/News visual language, reorganize its content into clearer individually-navigable sub-tabs, and use the documented type scale consistently (no ad-hoc inline `font-size` overrides). The exact sub-tab set is a pending design decision, not yet executed.

## [v0.20] — 2026-06-01 (frozen-archive honesty sweep)

### Changed
- **Policy metadata reframed to the frozen state.** `data/news_archive.json` `policy` drops the forward-posture `collection_going_forward: "officials-only"` (read as ongoing collection) for `collection_ended: "2026-05-27T02:30:00Z"`; the note now says collection ended at the all-clear with nothing added after — official statements included — which matches the data (all 92 items are dated ≤ May 26). `test_collection_policy_documented` now rejects forward-posture framing instead of merely requiring the `officials-only` string.
- **Stale forward-posture prose cleaned.** `CODE_OF_CONDUCT.md` (Vietnamese "currently held — awaiting verification" → removed 2026-05-30, English-only by design), `LANGUAGE_ACCESS.md` ("maintained for every future incident update" → "for the life of an incident", no future-incident assumption), and the distribution-plan doc (Open Question 3 "Nancy to confirm" → Phase 0 concluded at the May 26 all-clear).
- service-worker `CACHE_NAME` bumped `v40 → v41`.

### Removed
- **Dead present-tense hero strings.** The unused `hero.lead` / `hero.summary.default` i18n keys ("Active chemical-tank emergency…", "…Follow official orders") — never rendered, live-emergency framing inconsistent with the frozen archive. Guarded by the new `test_no_active_emergency_copy`.

## [v0.19] — 2026-05-31 (mobile map zoom-out range)

### Changed
- **Mobile map zooms out further.** On phones (viewport < 768px) the MapLibre `minZoom` floor drops from 10 to 8, so residents can pinch out to see the evacuation zone in its regional (Orange County) context; desktop keeps the tighter zoom-10 floor. Reuses the existing `window.innerWidth >= 768` viewport split. Adds one eval guard (`test_map_mobile_zoom`); the suite stays green.
- service-worker `CACHE_NAME` bumped `v15 → v16` so cached users receive the updated dashboard shell.

## [v0.18] — 2026-05-30 (English-only safety reframe + UX overhaul)

### Changed — English-only by design (G1, most conservative form)
- **Removed all Vietnamese + the language toggle.** The app ships English only: the toggle UI, the `vi` `LANGS` entry, the in-product Vietnamese sign-post, all 145 `vi:` STRINGS values, and the VN flag are gone. Safety decision — we never author or surface a translation we can't reliably verify (an unofficial mistranslation of an evacuation instruction can get someone killed); limited-English residents are routed to officials, who publish their own verified Vietnamese / Spanish / Korean per-update. Supersedes the v0.16 "held pending verification" posture.
- **Eval reframed.** Deleted `test_vietnamese_held_with_official_fallback`; added `test_english_only`, which fails the build if any non-English language appears in `LANGS` (eval stays **48/48**). Reframed README / CLAUDE / cover-letter / evidence-summary / submission-checklist / `LANGUAGE_ACCESS.md` to the English-only narrative.

### Changed — Map / News / Info UX
- **Top half compacted.** The hero hides empty status cells; the safety strip is a tighter 2-line block with labeled routing ("Emergency 911 · Official ggcity.org/emergency · City info (714) 628-7085"), dropping the unlabeled "OCFA". The disclosure + official routing are preserved (binding).
- **Wind overlay shrunk to ≤¼** its prior footprint; the "weather data, not safety guidance" note moves to a tooltip.
- **Timeline removed.** The News tab is a single sourced feed (official statements + articles + videos) with its filter chips; the Updates | Timeline sub-tab bar is gone.
- **Info → Resources** merges the former duplicate "nearest shelters" + "Evacuation shelters" into one shelter list, with School closures after it.
- **Info → Status** is a centered ~760px column on desktop (no longer stranded across the full width).
- **Info sub-tabs stick** to the top while scrolling.

### Changed — docs / process
- **Eval count corrected** to 48 across reviewer-facing docs (was stated as 47).
- **the distribution-plan doc** no longer markets removed features (address checker, blast-radius/plume map).
- **`docs/DEPLOYMENT_READINESS.md`** is the single source of truth for launch state, replacing the stale `plan/EXECUTION_PLAN.md` + `loop/LOOP_STATE.md` sentinels.
- service-worker `CACHE_NAME` bumped `v8 → v9`.

## [v0.17] — 2026-05-29 (design-complete gate + hosting fix)

### Design-complete gate (Map + News + Info + Timeline + tablet)

**Added** — wind overlay labels its source ("Wind — NOAA") plus a "weather data, not safety guidance" micro-label, with an honest "Wind data unavailable" fallback instead of presenting a default as a live reading (D1); English-only Vietnamese sign-post in Info → About routing Vietnamese-seekers to the city's official Vietnamese updates, `vi` held `ready:false` (D2); News video items render as 16:9 thumbnail cards with a play affordance; Info **Status | Resources | About** sub-tabs (reusing the News sub-tab pattern); Timeline curated to critical/major event categories by default with a "show full timeline" archive toggle (nothing deleted); a new eval G1 guard (`test_new_strings_english_only`) that fails the build if any new v0.17 i18n key carries an unverified Vietnamese value (eval **47 → 48**).

**Fixed** — map renders on a service-worker cache-first mobile reload: `_ggMap` is assigned at construction with a `ResizeObserver` on `#map-outer` + `pageshow`/`orientationchange` handlers (B2); the hero + safety strip are clamped to `max(168px, 33dvh)` so the map keeps the majority of a short viewport and the persistent disclosure is never clipped (L1); the tab-bar moves to the bottom on desktop (≥600px) (L2) and the hero gets its roomier 4-across row from 600px to fix the 600–767 tablet seam (T12); the Share button shows an `aria-live` "Copied to clipboard" toast on clipboard fallback (B1); the legend evac swatch has a visible border matching the map color (V1).

**Changed** — service-worker `CACHE_NAME` bumped `v7 → v8` so cached residents re-fetch the updated dashboard.

### Fixed
- **Live site was ~22h stale.** Vercel's free Hobby plan silently refuses to deploy a private repo owned by a GitHub *org*, so every `refresh_local.py` push since ~02:42Z never deployed — residents saw ~22h-old emergency data (the staleness banner correctly fired, so it was degraded-but-honest). Migrated the repo to a personal account (`Mike-E-Log/gg-tank-watch`), where Hobby deploys private repos free; auto-deploy on push is restored. Interim live URL is `gg-tank-watch.vercel.app` (resident-facing `gardengrovetankwatch.org` follows at launch).

### Changed
- **Repointed canonical / Open Graph / Twitter URLs** + the cover-letter "Live:" link to `gg-tank-watch.vercel.app`; repo ref → `Mike-E-Log/gg-tank-watch`.
- **`refresh_local.py` `trigger_deploy()`** — optionally POSTs `$VERCEL_DEPLOY_HOOK_URL` after each push as defense-in-depth against a silent auto-deploy stall (no-op until the hook env var is set; mirrors `ping_healthcheck`).

## [v0.16] — 2026-05-29 (Vietnamese held pending fluent verification — G1 honesty)

### Changed
- **Vietnamese held (`vi.ready=false`).** The ~134 AI-drafted Vietnamese strings were never verified by a fluent native speaker (the prior reviewer is not fluent and checked only a few), so they no longer ship as safety copy. `t()` falls back to verified English automatically. This corrects a real honesty gap — the site had been serving unverified Vietnamese life-safety copy. Re-enable only after a fluent native speaker + certified translation verify it (the gate below enforces this).
- **Interim "Tiếng Việt ↗" affordance.** With the toggle hidden, the language menu offers an outbound "Tiếng Việt ↗" link to the official Vietnamese emergency page (ggcity.org/emergency), routing Vietnamese-seeking residents to verified *human* Vietnamese instead of stranding them in English ("withhold-and-amplify").
- **Honesty corrections across docs.** Qualified/removed false "native-verified" / "Nancy has verified" claims in CODE_OF_CONDUCT, PRIOR_ART, LANGUAGE_ACCESS, and the i18n briefing (kept with a correction note as the audit trail). The truthful forward-looking "English fallback until verified" rules are unchanged.

### Added
- **G1 language-access gate (`eval/test_language_access.py`, +2 tests → 47 total).** A build-failing guard: any non-English language flipped to `ready:true` without fluent-native verification fails the eval — turning the G1 policy into an enforced control. The falsifier recommended by the 2026-05-29 research (`docs/research/2026-05-29-vi-anthropic-lens-research.md`).

## [v0.15] — 2026-05-29 (resident shareability)

### Added
- **Shareable link previews** — sharing the dashboard URL (iMessage, WhatsApp, Nextdoor, Facebook) now renders a rich card (title, description, and a "GG Tank Watch" preview image) instead of a bare link. Open Graph + Twitter Card tags drive it, and the card keeps the honest "unofficial — verify with ggcity.org/emergency" framing. Social crawlers render the card even though the site stays `noindex`, so resident-to-resident sharing — the main way it spreads during the emergency — now carries context.
- **One-tap Share button** — a Share control in the top-right header opens the native share sheet on mobile (Web Share API) and copies the link on desktop as a fallback. No new dependencies.

## [v0.14] — 2026-05-28 (banner messages translated)

### Fixed
- **English banner text in Vietnamese mode** — the alert banner at the top (e.g. "1 new official statement(s)") stayed in English even when the page was set to Vietnamese; only the pill label was translated. All eight banner messages the pipeline can emit (new statements, evacuation lifted/reinstated/expanded, severity change, first injuries, residents-count change, incident resolved) now render in the active language. Vietnamese shows "1 thông cáo chính thức mới". English is unchanged. The dismiss behavior is unaffected (the English text stays the banner's internal identity), and switching language re-translates any banner already on screen.
- **Mangled Vietnamese pill** — the banner category pill showed "CP NHT" in Vietnamese (the emoji-stripping step also ate the diacritics from "CẬP NHẬT"). It now reads "CẬP NHẬT" / "KHẨN CẤP" correctly.

> Note (G1): the Vietnamese for the five urgent banner reasons is AI-drafted and **not** native-verified — the reviewer (Nancy) is not a fluent Vietnamese speaker, so the G1 bar was never met (corrected in v0.16, 2026-05-29). Each is flagged inline and held under automatic English fallback. These banners are dormant unless the incident escalates.

## [v0.13] — 2026-05-28 (mobile wordmark row fix)

### Fixed
- **Vietnamese wordmark jump** — on mobile the "GG Tank Watch" wordmark used to sit beside the UNOFFICIAL badge in English but drop below it in Vietnamese (the wider "KHÔNG CHÍNH THỨC" badge pushed it to a second row), so switching language visibly shifted the title. The wordmark now always sits on its own line just below the badge on mobile, identical in both languages — no more jump. The desktop header is unchanged.

## [v0.12] — 2026-05-28 (mobile header + banner dismiss fixes)

### Fixed
- **Vietnamese header controls** — the language and light/dark buttons no longer drop to a second row at the far left in Vietnamese. They stay pinned top-right (as in English); the long "KHÔNG CHÍNH THỨC" badge and wordmark wrap below instead. English and desktop layouts are unchanged.
- **Dismissed notification reappearing** — closing the × on a top banner now sticks. Previously the urgent banner had no memory of being dismissed and a routine data refresh would bring it (and the info banner) right back. A dismissed banner now stays closed until the underlying situation actually changes; a genuine escalation still re-alerts.

## [v0.11] — 2026-05-28 (mobile layout polish)

### Fixed
- **Footer disclaimer alignment** — on mobile the separator dots and the "OCFA" label floated above the official-source links (`ggcity.org/emergency · 911 · 714-628-7085 · OCFA`). The whole row now shares one vertical centerline.
- **Vietnamese header wrap** — in Vietnamese the light/dark toggle dropped onto its own line. The language and theme controls are now a single cluster that never splits, and the "KHÔNG CHÍNH THỨC" unofficial badge stays fully visible.

### Changed
- **More map on small screens** — the stats grid and disclaimer strip are tighter on mobile, giving the map noticeably more height (~30–65px reclaimed) without dropping any stat, the disclaimer sentence, the terms link, or any official-source link. Desktop layout is unchanged.

## [v0.10] — 2026-05-25 (data-quality hardening + freshness UI)

### Added
- **Date-sanity validation** — the writer now drops a malformed or future-dated `incident_resolved_iso` before it can drive a false "all-clear". A hallucinated or mis-parsed resolve time can no longer flip the incident to "resolved".

### Fixed
- **Mojibake at the source** — the writer reads its facts from stdin as explicit UTF-8, and the local refresh pipeline forces UTF-8 on its subprocess boundaries, so em-dashes and degree signs can no longer be double-encoded (`â€"`, `Â°`) on a non-UTF-8 (Windows cp1252) locale. This closes the root cause noted in v0.9; the client-side repair stays as a backstop.
- **Inconsistent clock format** — the topbar time was 12-hour in English but 24-hour in Vietnamese (the same instant showing as "12:59 AM" vs "0:59"). Time now renders 12-hour across all languages.

### Changed
- **Clearer stale indicator** — when data is stale the topbar shows a single "⚠ Stale · last updated {time}" instead of the confusing doubled "⚠ ⟳ ~20 min · {time}". The "~20 min" refresh cadence no longer shows when nothing is actually refreshing.

## [v0.9] — 2026-05-25 (post-redesign polish + liability)

### Changed
- **Removed the takeover "LEAVE NOW" modal** — the last on-screen directive. We issue no directives (LEGAL R1/R2); the urgent-breaking alert beep is kept. The full-screen flashing modal is gone.
- **Hero shows a short lead** ("Active chemical-tank emergency in Garden Grove"); the full situation summary moved to a **"Current situation"** block at the top of News (it was truncating in the hero).
- **Stale banner removed** — staleness now shows in the topbar freshness text ("~20 min · last X", turns red with ⚠ when stale), preserving the G3 staleness signal without a separate banner.
- **Language toggle is now a flag** (🇻🇳 Viet / 🇺🇸 Eng) and the theme toggle uses clearer custom sun/moon icons (the emoji sun was too faint and rendered as letters on some platforms).
- **Check** label and hint now make clear that checking an address pins it on the map.
- **Credit** updated to "Mike and Nancy".

### Added
- **Road closures** section in the Info tab (defers to ggcity.org/emergency; we hold no authoritative road-closure feed).

### Fixed
- **Mojibake in feed data** — em-dashes and degree signs (`â€"`, `Â°`) now render correctly ("—", "100°F") via a client-side repair. Root cause is the refresh pipeline emitting double-encoded UTF-8; that fix belongs in the DATA_QUALITY lane.
- Meta description no longer carries the old "What should I do?" framing or the old brand name.

## [v0.8] — 2026-05-25 (dashboard redesign — PR-B)

### Changed
- **Rebrand to "GG Tank Watch"** across the topbar, page titles, and terms page.
- **Hero is now a neutral status line** — removed the "What should I do?" framing and the "STAY PUT"/"LEAVE NOW" directive (liability: we issue no directives and imply no safety, per LEGAL R1/R2). Shows a labeled "Incident severity: HIGH" and a clamped situation summary; per-address verdicts stay in the Check tab. Reclaims map real-estate.
- **News is one unified reverse-chronological feed** — official statements, articles, and videos merged and tagged by type (Official / Article / Video), replacing the confusing statements-vs-Coverage split.
- **Info tab reorganized** by resident need: Incident status (tank + evacuation) → Where to go (shelters) → Closures (schools) → collapsible Sources & methodology → collapsible About.
- **Topbar toggles**: "VI"/"EN" → "Viet"/"Eng"; Light/Dark text → sun/moon icons.

### Added
- **UPDATE banner is dismissible** — clicking it marks the latest statement as seen (localStorage); it stays gone until a newer statement arrives.
- **Geocode result caching** (localStorage, 7-day TTL) to satisfy the OSM Nominatim caching policy.

### Notes
- New user-facing strings are English-only with EN fallback under VI until Nancy verifies (G1 gate). Final hero/severity wording remains attorney-review-gated per `docs/LEGAL.md`. The takeover modal's "LEAVE NOW" directive is flagged for a separate liability decision in an internal punch-list. A pre-existing em-dash mojibake in `status.json` `boundary_text` (Info → Evacuation → Boundary) is a data-pipeline issue for the DATA_QUALITY lane, not this PR.

## [v0.7] — 2026-05-25 (trust/safety on-page — PR-A)

Pre-distribution trust and liability hardening from `docs/LEGAL.md` (minimum-bar checklist) and the distribution-plan doc. The dashboard now sells its own unofficial, informational-only posture on first glance and points to the city as the source of truth on every screen.

### Added
- **Persistent "UNOFFICIAL" pill** in the topbar next to the title — never dismissable, with a "volunteer-made, not an official government source" tooltip.
- **Persistent safety strip** below the hero, visible across all tabs (Map/News/Check/Info): "Informational only — not official. In an emergency, call 911." plus a first-class official-source block (ggcity.org/emergency · 911 · 714-628-7085 · OCFA) and a link to the full terms.
- **"Who made this" block** at the top of the Info tab: built-by-volunteers line, full non-affiliation notice, no-data-collection statement, and a link to the terms page.
- **New `terms.html`** — standalone Terms & disclaimer page carrying the draft ToU (not-official/not-affiliated, informational-only, no-warranty, verify-official-sources, §1668-aware liability limit, third-party content, report-an-error, privacy, changes), an on-page banner, official sources, and OSM/Leaflet attribution.

### Changed
- **Address-check verdict wording audit** (highest-risk per LEGAL R1/R2, the distribution-plan doc): the "outside all zones" verdict no longer says "LIKELY SAFE" / "CÓ KHẢ NĂNG AN TOÀN" (dropped the banned safety promise) — now "OUTSIDE MAPPED ZONES" / "NGOÀI CÁC VÙNG TRÊN BẢN ĐỒ". "inside official evac zone" → "inside the city's evacuation zone" (keeps attribution to the authority, drops the "official" adjective).
- **Check-result disclaimer** strengthened to "Estimate only — not official. Verify at ggcity.org/emergency; in an emergency, call 911."

### Notes
- New user-facing strings are English-only and fall back to English under VI until Nancy verifies them (G1 translation gate). The minimal VI redactions in changed verdict strings also need Nancy's sign-off. Final wording remains attorney-review-gated per `docs/LEGAL.md` (🔴).

## [v0.6] — 2026-05-25 (post-release iteration)

### Added
- **Evacuation shelters panel + map markers** (D-025). 9 hand-curated shelters geocoded via Nominatim: Garden Grove Sports & Rec, Cypress Community Center, Savanna HS (Anaheim), Mile Square Park (Fountain Valley), Los Amigos HS (Fountain Valley), Ocean View HS (Huntington Beach), Golden West College, JFK HS (La Palma), OC Fair & Event Center (Costa Mesa — RV evacuees only). Each rendered as a blue square marker on the map; panel below safety-checker shows name, city, address, RV-only chip, and a "Directions ↗" link that opens Google Maps with the destination pre-filled. Prominent CTA at top: "Live list at ggcity.org/emergency" since the city stays the source of truth.
- **News videos panel** generalized to **"Major news updates"** — supports both YouTube videos (`youtube_id` auto-derives `https://img.youtube.com/vi/{id}/hqdefault.jpg` thumbnail) and news article entries (no play overlay, document-icon placeholder when no thumbnail). 11 entries curated covering ABC7 LA, NBC LA, KTLA, ABC News, News18. Selection criteria: recency, coverage depth, format mix.
- **Client-side OG image fetcher** for article thumbnails (Microlink API, free tier, no key). Articles without a hardcoded `thumbnail_url` get their preview image fetched + cached in localStorage for 24 hours. Falls back gracefully to the typed placeholder if Microlink fails or rate-limits.
- **Statement backfill** (D-023 follow-up). Full incident timeline now: OCFA initial alert (Thu 5/21), Covey "tank will fail" press conference (Fri 5/22), drone temp rise 77→90°F (Sat 5/23), OC DA tipline launch + X-Law class action lawsuit (Sat evening), OCFA recon crack discovery (Sun 5/24), Chinsio-Kwong toxicity briefing, McGovern positive-intel update, gauge-pegged-at-100°F note, Costa Mesa fairgrounds opens for RV shelter. 12 statements in sidebar.
- **Two fixed reference pins on map**: Trask & Harbor + Magnolia & Ellis, color-coded by current safety verdict (auto-recolored on wind updates).
- **Safety checker**: geocodes any OC address/intersection via Nominatim, computes verdict (CRITICAL / HIGH / ELEVATED / SAFE), drops pin on map. New `D-019` and `D-020` in design log.
- **Statement card polish**: 14px bold date+time as the dominant line, agency on its own line, `Newest` red badge + red left-border on the most recent, `Recent` amber badge on statements <2 hours old, relative time `(N min ago)` on every card.
- **Sticky right sidebar** for statements (collapses to bottom-of-page below 1000px viewport). URGENT/UPDATE banner is now clickable — scrolls sidebar list to top + flashes the newest statement.
- **Light/dark theme toggle** in top-right, light is default, preference saved per-browser.

### Changed
- **Hero**: 72px clamp → `clamp(20px, 3.2vw, 32px)`. Severity chip merged into the hero (was a separate row).
- **Evac polygon**: extended west to ~Knott Ave to include Stanton + W Cypress portions per news reports.
- **Blast radii**: recalibrated from generic 0.25/0.5/1.0 mi → BLEVE-scaled 0.11/0.31/0.93 mi (matching OCFA labels: 20 PSI overpressure / Moderate damage / Lightweight injury). Methodology documented in `config.json.notes`.
- **Facility coordinates**: corrected to 33.7858, -118.0050 (12122 Western Ave per news reports — was a guess at 33.7748, -117.9978).
- **BREAKING banner classification**: split into URGENT (red, pulsing, beep, for act-now changes) and UPDATE (amber, no beep, for info-level like new statements). `breaking_level: urgent | info` field added to `status.json`. See D-016.
- **Map fitBounds**: now includes `fixed_points` and `shelters` so the southern/northern markers stay in viewport on initial load.
- **Geocoder bias**: Garden Grove → Orange County (with viewbox fallback) so generic intersections like "Magnolia & Talbert" find the OC location instead of out-of-state matches. D-020.
- **Section headers** added between page regions (`MAP`, `CHECK AN ADDRESS`, `EVACUATION SHELTERS`, `MAJOR NEWS UPDATES`, `INCIDENT DETAILS`, `SOURCES`) for visual hierarchy.

### Fixed
- **Writer bug**: piping partial facts (e.g., `cat data/news_seed.json | python scripts/update_status.py` which only contains `videos`) silently downgraded severity to "low" because `derive_severity()` walked off the rules table on missing fields. Next real tick fired a false URGENT "Severity bumped: low → high". Fix: only re-derive severity when this tick provides one of the severity-relevant fields (`evacuation_residents`, `evacuation_lifted`, `incident_resolved_iso`, `injuries`, `tank_failed`, `explosion_confirmed`). Otherwise carry prev. New `test_partial_facts_dont_downgrade_severity` locks the fix in. Eval went from 23/23 → 24/24.
- **fitBounds** missed `fixed_points` so Magnolia & Ellis (the southern green pin) was cut below the viewport.
- **Hardcoded ABC7 article thumbnails** weren't loading (likely CDN hotlink restrictions) — removed; replaced by Microlink OG fetch.

### Repo
- Initial push to a private repository.
- 8 commits on `main` before this PR. GH Actions workflow runs eval suite on every push.

## [v0.5] — 2026-05-24 (public-release cut)

### Added
- Top-level `README.md` rewritten as a case study (architecture, what I'd change).
- `DESIGN_LOG.md` — structured log of every design decision (D-001 … D-NNN) with rubric scoring, alternatives considered, status (active/superseded), and retrospective notes.
- `eval/` directory with pytest-style behavioral suite:
  - `test_writer.py` — 5-state sequence (baseline / no-diff / urgent-toggle / stable / resolved) + new-statement + residents-shift + schema validation
  - `test_safety.py` — known-input → known-verdict coverage for the safety checker
  - `test_geocoder.py` — live Nominatim regression for Magnolia & Talbert, Trask & Harbor, full street address
  - `test_schema.py` — JSON schema validation for `status.json` + `config.json`
  - `run_all.py` — runs everything, appends to `eval/scores.jsonl`, prints scorecard
  - `rubrics/design_quality.md` — LLM-as-judge prompt for evaluating individual design decisions
  - `rubrics/data_quality.md` — LLM-as-judge prompt for evaluating writer fact extraction
- `USAGE.md` — operational guide (was the previous `README.md`)
- `LICENSE` (MIT)
- `.gitignore` (excludes runtime artifacts)

### Changed
- Original user-facing `README.md` moved to `USAGE.md`. Top-level `README.md` now serves a different audience (public readers).

## [v0.4] — 2026-05-24 (UPDATE banner + sidebar + statement card polish)

### Added
- Two fixed reference pins on the map (Trask & Harbor, Magnolia & Ellis) — auto-recolored by current safety verdict.
- Sticky right-sidebar for official statements (collapses to bottom-of-page below 1000px viewport).
- "Newest" red badge on the most recent statement + "Recent" amber badge on statements <2 hours old.
- UPDATE/URGENT banner is now clickable — scrolls sidebar list to top + flashes the newest statement.
- Section headers ("MAP", "CHECK AN ADDRESS", "INCIDENT DETAILS") to give the page a clearer flow.

### Changed
- Statement card layout: date+time is now the 14px bold dominant line; agency on its own line below.
- Statement sort: newest-first (was insertion order).
- BREAKING split into URGENT (red, pulsing, beep — for act-now changes) and UPDATE (amber, no beep — for info-level changes like new statements).
- Hero reduced from 72px → clamp(20px, 3.2vw, 32px) and severity chip merged into the hero (was a separate row).
- Evac polygon extended west to ~Knott Ave to include Stanton + W Cypress portions per news reports.

## [v0.3] — 2026-05-24 (map + safety checker + light theme)

### Added
- Leaflet map with OpenStreetMap tiles (no API key).
- 3 blast-zone circles (0.11 / 0.31 / 0.93 mi — derived from BLEVE scaling for ~7,000 gal MMA + visual match to OC Register published map).
- Live plume cone driven by NOAA `api.weather.gov` wind data (station KFUL, refreshed every 5 min, cached in localStorage).
- Safety checker: geocodes any address/intersection via Nominatim, computes verdict (CRITICAL / HIGH / ELEVATED / SAFE), drops a colored pin on the map.
- Light/dark theme toggle, light default. Preference saved per browser.
- `start_dashboard.bat` launcher — starts `python -m http.server` and opens the browser (fixes Chrome's `file://` fetch block).

### Changed
- Facility coordinates corrected to 33.7858, -118.0050 (12122 Western Ave per news reports — was a guess at 33.7748, -117.9978).
- Blast zone radii recalibrated: was 0.25/0.5/1.0 mi (generic); now matches BLEVE scaling for the actual tank inventory.

## [v0.2] — 2026-05-24 (desktop-only pivot)

### Removed
- ntfy push pipeline (POST on breaking, writer-down alert, ASCII-safe header helper).
- `urllib.request` / `urllib.error` imports (writer is now stdlib-only beyond optional deps).
- `apps-checklist.md` (Ready OC / Genasys EVAC / AirNow / ntfy install guide).
- All phone / mobile / OneDrive-web-on-phone references.

### Rationale
- User direction: "scratch all mobile plans, I just want a single live desktop dashboard app."
- Architectural note: the writer is still necessary because the browser can't pull news directly. Cloud routine remains as redundant text-delta producer (does not write status.json).

## [v0.1] — 2026-05-24 (v0 build)

### Added
- `update_status.py` writer: WebSearch+regex fact extraction (driven by /loop), structural-diff breaking detection with TOGGLES-fire-immediately + residents-shift-rate-limited rules, atomic write with retry on Windows OneDrive file-locks.
- `dashboard.html` v0: 4 panels (Hero with zone verdict / Tank / Evacuation / Schools closed / Sources collapsed / Statements collapsed) with NWS gov-emergency-calm aesthetic.
- `config.json`: zone_status, refresh intervals, incident metadata.
- `go_bag.md`: standalone printable evacuation checklist.
- Hooked into existing in-session `/loop` job (every 30 min) and cloud routine (hourly redundancy).

### Decisions captured at this point (see DESIGN_LOG.md for full context)
- D-001 push-first vs dashboard-first (later reversed per D-009)
- D-002 OneDrive path vs `%LOCALAPPDATA%` (kept OneDrive)
- D-003 WebSearch+regex vs per-site scrapers (chose WebSearch+regex)
- D-004 Hysteresis design (initially 2-tick, then killed in v0.1.1 because the candidate-fires-twice rule was wrong for toggle events)
- D-005 Severity rules (hardcoded `SEVERITY_RULES` dict)
- D-006 Cloud routine writing to status.json (rejected — Linux sandbox can't reach OneDrive)
- D-007 Map vs no map (initially deferred, then added in v0.3 per user request)

## [v0] — 2026-05-24 (SPEC + autoplan review)

### Added
- `docs/SPEC.md` — full SPEC capturing problem statement, premises, architecture, data model, error model, scope.
- `BRIEF_2026-05-24.md` — source-cited factual brief on the incident (10+ news sources triangulated).
- `PERSONAL_UPDATE_2026-05-24.md` — drafts for personal status updates to family / manager.
- Autoplan review: CEO + Design + Eng phases run via Claude subagents (Codex unavailable on this machine — degraded gracefully).
- Premise gate + final approval gate with 5 taste decisions surfaced for the user.

### Decisions captured
- D-008 Pivot from dashboard-first to push-first (CEO findings F1, F2, F11 triggered user challenge → user accepted pivot)

## [v0 prelude] — 2026-05-24 (research)

### Added
- `BRIEF_2026-05-24.md` produced via `/deep-research` — triangulated across ABC7, NBC LA, CBS LA, KTLA, CNN, PBS, Wikipedia, EPA, CDPH.
- Recurring update infrastructure: `/loop` cron (every 30 min in-session) + cloud routine `trig_017YEJ4zkKeeXswyXPWz3yFw` (hourly via claude.ai).
