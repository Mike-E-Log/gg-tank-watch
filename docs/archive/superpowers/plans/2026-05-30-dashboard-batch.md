# Dashboard Improvement Batch — Execution Plan

- **Date:** 2026-05-30
- **Branch:** `feat/dashboard-batch-2026-05-30` (off `main` @ `820fb4b`)
- **Status:** PLAN — reviewed (plan-eng-review + codex outside voice). Awaiting build authorization. No batch code written.
- **Source:** 8-agent read-only investigation (`wf_6e0dd54d-542`); founder + eng-review + cross-model decisions locked 2026-05-30.

## Context

Single-file static dashboard (`dashboard.html`, 2861 lines), English-only, live at `gg-tank-watch.vercel.app`.
Information conduit: routes residents to officials, authors NO directives. The Garden Grove MMA tank incident
**resolved 2026-05-28** (`status.json`: `resolved_iso` set, `evacuation.lifted: true`, `residents: 0`, Day-10
recovery). Also an Anthropic-fellowship **portfolio piece** — the live site doubles as a demonstration.
Production deploy is gated: merge → auto-deploy to the live site, requires explicit "merge #N" authorization.

## Decisions (locked 2026-05-30)

**Founder:** #7 recovery-state hero · #6 relabel historical + banner · #5 one clean feed (kept live) · #2 wide Info with ~1200px cap.

**Eng review (minimal-diff):**
- #5 → **UI-layer only.** Writer already exact-URL-dedupes + re-derives `is_video` per URL (`test_videos_dedupe.py`). Ordering, base-URL live-blog collapse, graceful no-thumbnail video card → render layer. No `articles` array, no writer change, no schema migration.
- #6 → **keep + relabel, NO writer clear** (clearing contradicts "keep visible" + touches tested writer/provenance gate).
- #7 → **reuse existing fields** (no new status.json fields, no fragile headline parsing).
- **SW cache bump REQUIRED:** `sw.js CACHE_NAME` `gg-tank-v9` → `gg-tank-v10`.
- #3 → **neuter the AirNow writer call** + remove UI/i18n/print/doc refs; reuse existing `resolved` var (`dashboard.html:2589`).
- **New 49th eval:** static "no air-quality link in dashboard.html" safety guard.

**Cross-model (codex outside voice):**
- **#9 map reframe ADDED** — the default tab still renders active-evacuation framing.
- **Meta/share reframe ADDED to #6** — OG/Twitter/manifest still advertise active emergency.
- **Cleanup kept narrow** — vi: i18n residue + DISTRIBUTION.md overhaul deferred to TODOs.
- Folded refinements: dedupe-before-counts, fix "Newest" badge, drop computed day-count, hero shows headline prose (not discrete cells), neuter `fetch_air_quality()` call.

## Constraints (binding)

- Conduit only — no directives, no authority over-claim. Recovery copy is descriptive of observed state.
- English-only — do not re-add Vietnamese (`eval/test_english_only` enforces).
- Keep in the safety strip: "Informational only" disclosure + 911 + ggcity.org routing.
- Eval verified by exit code (`python eval/run_all.py --skip integration`), never `--quiet`. Target after batch: **49/49**.
- SW `CACHE_NAME` bump is part of any `dashboard.html`/`config.json` change.
- No new dependencies.

## Per-item specification

Line refs approximate (build step re-locates). Incident is resolved throughout.

### Item 8 — Doc rewords (mechanical) · `docs/DISTRIBUTION.md`, `docs/LANGUAGE_ACCESS.md`
- `DISTRIBUTION.md:~228`: "address checker removed" → in-app verification removed (2026-05-26); dashboard links out to ggcity.org/emergency's official checker; no user input collected.
- `LANGUAGE_ACCESS.md:~95`: present-tense "picker" → conditional ("would appear in the picker if a language's `ready` flag were flipped"); English-only by design.

### Item 3 — Remove AirNow + config.json title_vi · `dashboard.html`, `config.json`, `scripts/update_status.py`, `README.md`, `LICENSE`, `CHANGELOG.md`
- Remove AirNow: i18n key `~1668`, Resources link `~2448`, print view `~2500` (no orphaned key references). Reason: AirNow = particulates/ozone, not MMA vapor → false-reassurance.
- **Neuter the writer call:** guard/remove the `fetch_air_quality()` call in `build_snapshot()` (`update_status.py:~516`) so a future `AIRNOW_API_KEY` can't silently reintroduce it. Leave the function defined. `air_quality` stays `null`; `test_air_quality_shape_if_present` (conditional) stays green.
- Remove doc/legal refs: `README.md:~67,238`, `LICENSE:~26`, `CHANGELOG.md:~235` (annotate history entry).
- Remove dead `title_vi`: `config.json:~44,53,61` (render path uses `r.title` only).

### Item 5 — News curation (UI-layer only) · `dashboard.html`
- **Dedupe in feed-build, before filter counts** (`~2079-2089`): collapse same-base-URL ABC7 live-blog `/entry/` fragments to one (keep newest); avoids inflated chip counts.
- **Ordering:** official-first then recency in the sort (`~2613-2621`).
- **Fix the "Newest" badge** (`~2114-2124`, currently `idx===0`): mark the newest-by-time item, not idx 0, so official-first sort doesn't mislabel it.
- **Graceful video card:** NBC explainer (`is_video:true`, no `youtube_id`/thumbnail) must not render as a broken thumbnail-less video tile — fall back to a non-thumbnail card.
- No writer/data/schema change. `test_videos_dedupe.py` stays green.

### Item 6 — Resolved lifecycle + demo + meta/share · `dashboard.html`, `manifest.json`
- Resolved banner in `renderResources()` (`~2403-2457`) keyed on existing `resolved` var: "Shelters and school closures below are historical — incident resolved May 28; see ggcity.org/emergency for current info." Relabel shelters/schools as historical (muted style cue).
- **Demo framing:** About/footer note "incident resolved — live demonstration of the system" (conduit-safe).
- **Meta/share reframe:** OG + Twitter description (`dashboard.html:~7,11-20,2837`) + `manifest.json` (`~4`) → resolved-incident / live-demo, not active emergency.
- No writer change; shelters are static `config.json` → UI-label only.

### Item 7 — Recovery hero (reuse existing fields) · `dashboard.html`
- Hero markup `~1453-1472`, `renderHeroStatus()` `~2507-2531`. In resolved state, replace evac metric cells (residents 0, blank tank temp, blank "Day") with a compact recovery summary built from existing data: `evacuation.lifted` → "All evacuations lifted", and **un-hide the existing `news-situation` block** (`~1522`, suppressed at `~2626` when resolved) to surface `status_headline` (the founder-authored "Day 10 recovery: exclusion zone reduced to 150 ft…" prose). Add a support-resources link.
- **No computed day-counter** (timezone/advance-after-resolved undefined), **no discrete "150 ft" cells** (would require hardcoding/new fields), no new status.json fields.
- Visual treatment is the founder's design call; data source is the existing headline.

### Item 2 — Desktop Info full width · `dashboard.html`
- Remove `@media(min-width:768px){.info-subpanel.active{max-width:760px}}` (`~1072-1074`); add `max-width:~1200px; margin:auto` for readability.
- Responsive grids: `.shelters-grid`/`.resources-grid` reflow; make `.info-schools-grid` (`~1298-1302`) responsive 2→3→4 cols; optionally Status as 2×2.

### Item 9 — Map resolved-state reframe (NEW) · `dashboard.html`, possibly `config.json`
- Default tab is the map (`~1535`); it still renders active-evacuation framing (`~1496-1514`): evac-zone legend, "Check Address" CTA, wind overlay.
- Relabel the evac polygon/legend as "former evacuation area — lifted May 27" (the polygon already carries an "approximate / not authoritative" note in `config.json:24`); reconcile the "Check Address" CTA for resolved state; soften active-emergency cues. Keep routing to ggcity.org. Conduit-safe, descriptive.
- Default-tab change (map → hero/Info) is a design option for the founder; not assumed here.

### Item 4 — Mobile safety strip shorter · `dashboard.html` (phase 4)
- Markup `~1475-1487`, CSS `356-420`. Collapse 4-5 wrapped rows (~80px) → ~2 tight rows (~40px): merge the two flex rows, compress copy, tighten gap/line-height/font; drop redundant `(714)` city phone. Keep (binding): "Informational only" disclosure + 911 + ggcity routing.

### Item 1 — Mobile map reload (verify on real device) · `dashboard.html`, `sw.js`
- Root cause: MapLibre canvas constructed synchronously (`~2747`) before flex layout settles; `.map-outer` (`613-617`) `flex:1;min-height:0` → 0-height under cache-first reload; ResizeObserver fires only on change; `pageshow` too late.
- Layered fix: (a) explicit `min-height` on `.map-outer`; (b) gate init behind `requestAnimationFrame` until `#map-outer.offsetHeight>0`; (c) post-`load` `map.resize()`. Apply (a) first; add (b) if needed.
- **SW cache bump v9→v10** (this is where it lands; also required for items 2-9 to reach cached users).
- **Founder verifies on a real mobile device** — headless cannot reproduce the cache-first reload race.

## Build sequencing

```
Phase 1  Docs + cleanup        #8, #3            no behavior change → eval 49/49 (add AirNow guard here)
Phase 2  News UI               #5                UI-only; test_videos_dedupe stays green; Edge-headless feed check
Phase 3  Resolved framing      #6, #7, #9, #2    biggest visual diff; Edge-headless QA via __qa_harness.html
Phase 4  Mobile + SW           #4, #1 + sw bump  Edge-headless + FOUNDER real-mobile verification
Phase 5  Gate                  eval 49/49 + node --check + visual QA → PR → founder "merge #N"
```

## Verification

- `python eval/run_all.py --skip integration` → exit 0, **49/49** (48 existing + new AirNow guard). Never `--quiet`.
- `node --check` on extracted dashboard JS (or browser console clean).
- Signed Edge headless (`--headless=new --screenshot --enable-unsafe-swiftshader`) vs `python -m http.server`, via the `__qa_harness.html` iframe pattern (tab/sub-tab nav + scroll).
- Static headless CANNOT confirm `position:sticky` scroll-pin or the map reload race → founder real-device check for #1.

## NOT in scope (deferred, with rationale)

- **vi: i18n residue** in `dashboard.html` — dead behind `ready:false`, not user-surfaced; full removal is a separate cleanup → TODO.
- **DISTRIBUTION.md resolved-state overhaul** — broad doc rewrite (bilingual/LEP/Vietnamese-media sections) beyond the 2 scoped rewords → TODO.
- **Staleness banner wiring** (`now > stale_after_iso`) — pre-existing, unverified, low-risk post-resolution → TODO (verify first).
- **`breaking:true` persistence** post-resolution — data-state, resolves on a writer run → TODO.
- **Dual config-fetch cache paths** (`~2677` cache-busted vs `~2764` cache-first) — architectural inconsistency, cache bump handles this instance → TODO.
- **SW stale-while-revalidate for HTML** — bump-only chosen; SWR is a separate improvement → TODO.
- **Default-tab change** (map→hero) — design decision, not assumed.

## What already exists (reuse, don't rebuild)

- Writer exact-URL dedupe + URL-based `is_video` re-derivation (`update_status.py`, proven by `test_videos_dedupe.py`).
- `resolved` detection (`dashboard.html:2589`); `news-situation` block already renders `status_headline` (just suppressed when resolved); `setCell` already hides null hero cells.
- 48-test eval harness: schema required-fields, resolved/lifted corroboration gate (`test_provenance`), English-only, video dedupe, static dashboard.html grep tests (`test_safety`, `test_provenance`).
- Evac polygon already carries a "not authoritative / confirm at ggcity" note (`config.json:24`).

## Failure modes (new/changed codepaths)

| Codepath | Realistic prod failure | Test? | Error handling? | Silent? |
|---|---|---|---|---|
| #1 map init (rAF gate) | `offsetHeight` never >0 (tab display:none) → init never fires, blank map | No (real-device) | Add a max-retry/fallback resize | Would be silent → **add fallback** |
| #5 base-URL dedupe | Over-collapse distinct stories sharing a base URL | UI (manual QA) | Conservative base-URL match (path prefix to `/entry/`) | Visible (missing item) |
| #5 Newest badge | Mislabel after official-first sort | Manual QA | Compute newest-by-time explicitly | Visible |
| #6 resolved banner | `resolved` true but copy hardcodes a date that drifts | AirNow guard unrelated | Derive date from `resolved_iso` | Visible |
| #7 hero un-hide | `status_headline` empty → empty hero | Existing setCell hide | Hide block when headline empty | Handled |
| #9 map relabel | Legend relabel misses a string → mixed active/resolved cues | Manual QA | Single source for the label | Visible |
| SW v10 | Forgot bump → changes don't reach cached users | Ship checklist | — | **Silent → checklist gate** |

Critical-gap watch: **#1 rAF-gate silent-fail** (no test + would be silent) → mitigate with a bounded retry + fallback resize. **SW bump omission** (silent) → enforced by the ship checklist.

## Worktree parallelization

| Phase | Modules | Depends on |
|---|---|---|
| P1 docs+cleanup | docs/, README/LICENSE/CHANGELOG, config.json, update_status.py | — |
| P2 news UI | dashboard.html (News render) | — |
| P3 resolved framing | dashboard.html (hero/info/map), manifest.json | — |
| P4 mobile+SW | dashboard.html (safety strip, map init), sw.js | P3 (same file) |

P2, P3, P4 all touch `dashboard.html` → **same lane, sequential** (one file, merge-conflict risk). P1 is mostly disjoint (docs/python/config) and could run in a parallel worktree, but the batch is small enough that **sequential single-branch implementation is simplest** — no real parallelization win.

## Implementation Tasks

- [ ] **T1 (P1)** — docs — reword DISTRIBUTION.md:228 + LANGUAGE_ACCESS.md:95 · Verify: `git diff`
- [ ] **T2 (P1)** — dashboard/config/python — remove AirNow (UI+i18n+print+docs) + neuter writer call + remove config title_vi · Verify: eval 48/48 + grep no airnow
- [ ] **T3 (P1)** — eval — add `test_no_air_quality_link` (49th) · Verify: eval 49/49
- [ ] **T4 (P2)** — dashboard — news dedupe-before-counts + official-first sort + Newest-badge fix + graceful video card · Verify: test_videos_dedupe green + Edge feed check
- [ ] **T5 (P3)** — dashboard/manifest — resolved banner + historical relabel + demo note + OG/Twitter/manifest reframe · Verify: Edge-headless + meta grep
- [ ] **T6 (P3)** — dashboard — recovery hero (reuse fields, un-hide news-situation, no day-count) · Verify: Edge-headless resolved state
- [ ] **T7 (P3)** — dashboard — map resolved reframe (legend/CTA/polygon label) · Verify: Edge-headless map (swiftshader)
- [ ] **T8 (P3)** — dashboard — desktop Info full width (~1200px cap) + responsive grids · Verify: Edge-headless desktop viewport
- [ ] **T9 (P4)** — dashboard — mobile safety strip ≥50% shorter (keep disclosure+911+ggcity) · Verify: Edge-headless 390px
- [ ] **T10 (P4)** — dashboard/sw — map reload layered fix + bump CACHE_NAME v9→v10 · Verify: **real mobile device** (founder)

## TODOs (captured 2026-05-30, deferred)

1. vi: i18n residue removal in dashboard.html (dead behind ready:false).
2. DISTRIBUTION.md resolved-state / English-only overhaul.
3. Staleness banner: verify + wire `now > stale_after_iso` in render (safety signal).
4. Clear/suppress `breaking:true` in resolved state.
5. Reconcile dual config-fetch cache paths (`~2677` vs `~2764`); consider SWR for HTML.

## Rollback / Risks

- Feature branch; `main` untouched until merge. Each phase = independent commit → revert per phase.
- Map fix needs per-breakpoint tuning; real-device verification is the gate.
- Recovery copy stays descriptive (conduit) — no "do X".
- SW bump omission is the one silent failure mode → ship-checklist gate.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | not run (optional) |
| Codex Review | `/codex review` | Independent 2nd opinion | 1 | ISSUES | 14 findings: 3 → scope, 5 → TODO, rest folded |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR | 6 issues resolved, 1 critical gap mitigated |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | not run (optional; UI-heavy) |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | n/a |

- **CODEX:** caught the active-evac map (→ new item 9), share/meta + manifest staleness (→ folded into #6), the AirNow writer-call still firing (→ neutered in #3), news dedupe-before-counts + "Newest" badge (→ folded into #5), and drop-the-day-count (→ folded into #7).
- **CROSS-MODEL:** eng review + codex agree the data layer stays minimal (UI-only #5, no writer schools-clear); codex extended coverage to surfaces the section review didn't reach.
- **UNRESOLVED:** 0.
- **VERDICT:** ENG CLEARED — ready to implement. 9 items, 49-test target, 5 TODOs captured. Production merge gated on explicit "merge #N".
