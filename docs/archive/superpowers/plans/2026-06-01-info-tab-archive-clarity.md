# Info tab — archive-clarity redesign

Status: PLAN (design-reviewed; decisions locked). Scope **B (targeted decard)**. Target: one PR — `dashboard.html` + inline STRINGS i18n + new eval guards; SW `CACHE_NAME` v42 → v43; DESIGN.md decision-log entry. **Depends on PR #92 merging first** (SW collides at v42 otherwise).

## Context

GG Tank Watch is a frozen historical archive of the resolved May 21–26, 2026 Garden Grove chemical-tank emergency. Information conduit: routes residents to officials, authors no directives (Section 230 / §552 line). English-only. `noindex` ON. This tidies the **Info tab** (Status / Resources / About) and aligns it to the existing **Map / News** visual system — no new design system.

## Primary purposes (yardstick, priority order)
1. **Route** to official authoritative sources (conduit, not authority); no single source is the only one.
2. **Amplify** official info honestly; author no directives.
3. **Transparent** about provenance + freshness — the whole app is FROZEN; must read as historical, not live.
4. **Do no harm / avoid over-trust** — English-only; "Watch" not "Safety".

## Design-system calibration (DESIGN.md)
Honor: Plus Jakarta Sans + IBM Plex Mono; celadon teal accent (`#0e6f5e`/`#4ecdb4`); gold accent (`#9e7c29`/`#d4b05c`) for the UNOFFICIAL pill + AI disclosure; 4px spacing; radius sm4/md6/lg8; lotus-petal divider; the `.resolved-note` celadon-left-border pill. DESIGN.md is partly pre-pivot/stale (Vietnamese type, "Check" tab, "What should I do?" hero) — out of scope; flag separately. The 2026-05-29 log chose "Status" + folded Sources under About → the rename below needs a new decision-log entry.

## Locked decisions (from the design review)
- **Scope = B (targeted decard):** reorder + collapse + copy/dedup AND strip card chrome on the collapsed historical resources (dense rows, no shadows). Bounded to the Resources historical block; does NOT touch Map/News or `.shelter-card` use elsewhere. (C — full structural `.info-section` refactor — deferred as a follow-up.)
- **Status disclaimer copy:** "Resolved {date} — all evacuations lifted. This is a historical snapshot, not live; current info: ggcity.org/emergency." Date derives from `status.json` `incident.resolved_iso` (Pacific); `ggcity.org/emergency` is a real link (= the in-context official link). Reuses `.resolved-note`. Differentiates from the topbar `archive.label` pill (pill = archive context; note = resolved status + routing).
- **Resources fold:** native `<details class="info-fold">`, summary "Historical resources," collapsed by default; contains the historical shelters + government/safety/community resources, de-carded to dense rows (no card shadows). Confirm school-closures location at implementation and apply the same historical framing.
- **Lotus divider:** keep one between the always-open Official Sources and the historical fold; bump dark-mode border contrast (verified at 390px in `/design-review`).
- **Row renames:** "Tank temperature" → "Final tank temperature"; "Residents in zone" → "Peak evacuation"; boundary → "Former boundary". "Crack observed" stays.

## Changes

### Status sub-tab → "What happened"
- Rename the subtab + section title to "What happened".
- Add the `.resolved-note` disclaimer (copy above) as the **first** element of the panel, before the kv-rows.
- Rename rows: Final tank temperature / Peak evacuation / Former boundary.

### Resources sub-tab (fix heavy scrolling + hard-rejection)
- **Reorder:** resolved note → **Official Sources** (ggcity.org/emergency, Genasys/Zonehaven, AlertOC + the "no single source" note) → one lotus divider → collapsed **Historical resources** `<details>`.
- **Decard** the historical shelters + gov/safety/community into dense rows inside the fold (strip `.shelter-card`/`.community-resource-card` shadows for this block).
- Cut the redundant shelters CTA card; de-jargon "source of truth" → "official".

### About sub-tab (dedup)
- Retitle the collapsed fold `info.sourcesH` "Sources & methodology" → **"Sources checked"** (it holds only the source LIST); keep the methodology narrative in the open section.
- Promote the AI disclosure (`disclosure.ai`) from 11px to **12px**, gold accent, above the pipeline text.
- Cut the dead unused string `info.about.conductlink`. Keep builder names + unofficial seal.

### Cross-cutting
- Split `info.method.disclaimer` into single-claim lines; **"In an emergency, call 911." on its own line**.
- Unify section-title styling across the three sub-tabs (within scope B — no full structural refactor).

## Test-first guards (RED → GREEN)
- `test_status_disclaimer_present` — Status panel renders the `.resolved-note` (historical marker + ggcity link).
- `test_official_before_shelters` — in Resources markup the Official Sources block precedes the historical fold. **Anchor on full markup tags** (e.g. `<details class="info-fold"`), not bare class names (class names hit the inline `<style>` first → false ordering — `eval-find-hits-css-before-html`).
- `test_disclaimer_911_own_line` — `info.method.disclaimer` renders "call 911" as its own clause/line.
- `test_about_fold_retitled` — `info.sourcesH` == "Sources checked"; `info.about.conductlink` absent; AI-disclosure font-size ≥ 12px.
- SW `CACHE_NAME` = v43 (+ the two existing SW guards bumped).

## Constraints from prior learnings
- **Disclaimer date DERIVES** from `incident.resolved_iso` (Pacific), never hardcode (`resolved-date-hardcoded-drift`).
- **Eval order-guards anchor on full markup tags**, not bare class names (`eval-find-hits-css-before-html`).
- **`/design-review` uses a `getBoundingClientRect` DOM probe** — Edge headless `--window-size=375` renders ~474px CSS (`edge-headless-375-actually-474`).

## Implementation Tasks
- [ ] **T1 (P1)** Status — rename "What happened"; add derived `.resolved-note` first; rename rows Final/Peak/Former. Files: dashboard.html. Verify: `test_status_disclaimer_present` + render.
- [ ] **T2 (P1)** Resources — reorder Official-first; collapsed `<details class="info-fold">` "Historical resources" with de-carded dense rows; cut CTA; de-jargon. Files: dashboard.html. Verify: `test_official_before_shelters` + /design-review.
- [ ] **T3 (P1)** Disclaimer — split to single-claim lines; "In an emergency, call 911." own line. Files: dashboard.html. Verify: `test_disclaimer_911_own_line`.
- [ ] **T4 (P2)** About — retitle fold "Sources checked"; AI disclosure 12px gold above pipeline; cut `info.about.conductlink`. Files: dashboard.html. Verify: `test_about_fold_retitled`.
- [ ] **T5 (P2)** Visual — unify section-title styling; lotus divider dark-contrast bump. Files: dashboard.html CSS. Verify: /design-review light+dark.
- [ ] **T6 (P1)** SW — bump `CACHE_NAME` v42→v43 + the two SW guards; DESIGN.md decision-log entry. Files: sw.js, eval/test_sw_*, DESIGN.md. Verify: eval 153+/all green.
- [ ] **T7 (P2)** QA — `/design-review` Edge-headless, 6 viewports light+dark, DOM probe at ~474px; confirm fold collapsed-by-default + no-JS. Verify: visual.

## Implementation sequence
1. PR #92 merges → `git fetch` + ff main → branch `feat/info-tab-archive-clarity`.
2. Test-first: add the guards (RED) → implement dashboard.html + i18n (GREEN).
3. SW bump + guards + DESIGN.md decision-log entry.
4. `/design-review` (Edge-headless) — 6 viewports, light + dark.
5. One PR → hand the user the `! gh pr merge`.

## Outside-voices litmus scorecard (APP UI)
| Check | Codex (gpt-5.5) | Claude subagent | Consensus |
|---|---|---|---|
| Brand unmistakable first screen | YES | — | YES |
| One strong visual anchor | NO | implied NO | NO |
| Scannable by headlines only | NO | NO | NO (confirmed) |
| Each section has one job | NO | NO | NO (confirmed) |
| Cards actually necessary | NO | NO | NO (confirmed) |
| Motion improves hierarchy | NO | — | NO |
| Premium w/o decorative shadows | NO | — | NO |
| Hard rejections | #1 card-grid-first, #7 stacked-cards | (same, implied) | addressed by scope B |

## NOT in scope (deferred, with rationale)
- **C — full structural `.info-section` refactor** of all three sub-panels: higher Map/News parity but largest regression surface on a live frozen-prod app; revisit as a follow-up.
- **DESIGN.md staleness** (Vietnamese type, "Check" tab, "What should I do?" hero): real, but a separate doc-accuracy task, not this Info-tab PR.
- **Loading/error skeletons** for the fold: data is static/precached in a frozen archive; existing empty fallbacks ("No shelters available") suffice.

## What already exists (reuse, don't reinvent)
`.resolved-note` pill (date-derived) · `.info-fold` `<details>` pattern · `.info-section` / `.info-section-title` · `.shelter-card` weight reference · `.official-link` style · the `news-archive-note` as the disclaimer-copy reference · lotus-divider.

## QA findings (Edge-headless visual QA — light + dark, ~390px)
- **Verified:** "What happened" tab; Status historical disclaimer (date-derived + ggcity link), differentiated from the topbar archive pill; Official-sources-first Resources + collapsed de-carded "Historical resources" fold (dense rows, no shadows); About AI disclosure 12px gold; disclaimer "In an emergency, call 911." on its own bold line; "Sources checked" fold; `conductlink` gone. Dark mode legible throughout. eval 157/157; node --check clean.
- **Caught + fixed:** the planned row renames (Final tank temperature / Peak evacuation / Former boundary) were **reverted** — the frozen `status.json` clears those fields (`temp_f` null, `residents` 0, `boundary_text` null), so "Peak evacuation: 0" was a false claim. Historical framing is carried by the tab + disclaimer instead.
- **Follow-up (out of scope — needs authoritative numbers + pipeline work):** the "What happened" panel still shows empty/0 rows; recording the real peak evacuation (~50,000), final tank temp, and former boundary into the archive data would make the panel genuinely informative.
- Lotus divider is faint in dark (decorative Son Mai accent; section labels carry the structure) — acceptable, no change.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | issues resolved | score 7.5→9/10; 1 scope decision (B); ~6 decisions locked |
| Outside voices | Codex + Claude subagent | Cross-model | 1 | clean (converged) | 2 hard-rejections (card-grid-first) → fixed by scope B; 5 litmus NO confirmed |

- **CROSS-MODEL:** Codex (gpt-5.5) and the blind Claude subagent converged on the same core issues (Status reads live; official links buried; card-grid-first; dense run-ons; About dedup) and both elevated the plan to a targeted decard.
- **UNRESOLVED:** 0 (all decisions locked; final-plan approval pending; implementation gated on #92 merge).
- **VERDICT:** DESIGN CLEARED — plan is implementable and unambiguous. Eng review not separately required (copy/layout within existing system, test-first guards specified).
