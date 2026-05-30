# Dashboard UX Overhaul + English-Only Reframe — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline, sequential — `dashboard.html` is one file; no parallel editors). Steps use checkbox (`- [ ]`).

**Goal:** Free vertical space on the Map top half, shrink the wind widget, remove the language toggle and ALL Vietnamese content (English-only safety choice), simplify the News tab to a single sourced feed (remove Timeline), fix the Info → Resources order, fix the Info → Status desktop layout, make multi-tab sub-tab bars sticky, and reframe eval + reviewer-facing docs to the English-only + G1 story.

**Architecture:** Single-file edits to `dashboard.html` + `sw.js` + `eval/test_language_access.py` + reviewer-facing docs. No new deps. Conduit safety constraints are binding (see below). Build sequentially; keep eval green; visual-verify via signed Edge headless (SAC blocks `browse.exe`).

**Tech stack:** vanilla JS/CSS in `dashboard.html`; Python eval; MapLibre; Vercel static.

## Binding constraints (do NOT violate)
- The **"unofficial / not official / in an emergency call 911"** disclosure and the **official routing** (ggcity.org/emergency + 911) stay persistent and visible — conduit safety, eval-tested. Compact/relabel only; never remove.
- **English-only is the safety posture:** never ship machine/AI-translated safety copy. The eval must still *enforce* that (T9).
- `noindex` stays ON. No new deps. Branch → PR → merge; never push `main`.

## Three sub-decisions to confirm at plan sign-off
- **D-a (VI strings):** (a1, recommended) strip all **145** `vi:` props from STRINGS for a truly VI-free source — larger, mechanical diff; or (a2) remove only the toggle + sign-post + `vi` LANG and leave the 145 `vi:` values as dead data — smaller/safer, but source still contains VI.
- **D-b (Resources):** (b1, recommended) **merge** the redundant "Where to go · nearest shelters" and "Evacuation shelters" into one shelter section (they render the same shelters); or (b2) just **reorder** — move "School closures" below both shelter sections so they're adjacent, as literally asked.
- **D-c (eval):** (c1, recommended) **replace** `test_vietnamese_held_with_official_fallback` with `test_english_only` (asserts no non-English language exists) — keeps the count at **48** and encodes the new invariant; or (c2) just delete it (count → 47, re-churns the docs we just fixed).

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `dashboard.html` | Modify | all UI/UX + VI removal (T1–T8) |
| `eval/test_language_access.py` | Modify | reframe G1 guard to English-only (T9) |
| `README.md`, `docs/fellowship/{cover-letter-draft,evidence-summary}.md`, `CLAUDE.md`, `docs/LANGUAGE_ACCESS.md`, `docs/fellowship/submission-checklist.md` | Modify | English-only + G1 reframe (T10) |
| `sw.js`, `CHANGELOG.md` | Modify | cache bump + changelog (T11) |
| `~/.claude/projects/.../memory/vi-held-pending-verification.md` + `MEMORY.md` | Modify | supersede with English-only decision (T10) |

---

### T0 — Branch off main

- [ ] `git branch --show-current` → if not `main`, `git checkout main` first. Then `git checkout -b feat/dashboard-english-only-ux`. (Independent of the `docs/accuracy-and-deploy-readiness` branch; `dashboard.html` is untouched by that branch, so no conflict.)

---

### T1 — Remove language toggle + ALL Vietnamese (English-only)

**File:** `dashboard.html`.

- [ ] **Remove the language picker DOM** (`:1627-1630`): delete the `<div class="lang-picker">…</div>` block (the `lang-toggle` button + `lang-menu`). Leave `share-btn` and `theme-toggle`.
- [ ] **LANGS → English only** (`:1961-1964`): replace the array with a single entry:
  ```js
  var LANGS = [
    { code: "en", label: "English", flag: FLAG_US, locale: "en-US", ready: true }
  ];
  ```
- [ ] **Remove the picker/menu machinery:** `renderLangPicker` (`:2024-2055`), `openLangMenu`/`closeLangMenu`/`outsideLangClick` (`:2056-2073`), `toggleLangMenu`, `setLang` (grep them). Keep `t()`, `detectLang()` (now always returns "en"), `currentLocale()`, `langByCode()`. In `applyLang()` (`:2013`) remove the `renderLangPicker();` call.
- [ ] **Remove the Vietnamese sign-post** render in the About panel (`:2517-2521`, the `<aside class="vi-signpost">…`) and its CSS (`.vi-signpost` `:318,325-327`).
- [ ] **Remove `#lang-toggle` / `.lang-picker` / `.lang-menu` CSS** (`:289`+ block).
- [ ] **Remove `signpost.vi.body` / `signpost.vi.cta` strings** (`:1789-1790`) and the `FLAG_VN` constant (grep).
- [ ] **renderResources VI branch** (`:2855`): delete the `titleVi` line and its use (`+ titleVi +` at `:2863`) — drop the `r.title_vi` rendering.
- [ ] **D-a (VI strings):** per sign-off — (a1) strip all 145 `vi:` props from STRINGS [grep `vi:\s*"` to enumerate; remove the `, vi: "…"` segment from each entry, preserving `en`]; (a2) leave them as dead data.
- [ ] **Verify:** load page — no language button renders; nothing Vietnamese displays; `grep -c 'vi:' dashboard.html` is 0 (if a1). Eval after T9.

---

### T2 — Remove the Timeline (News sub-tab)

**File:** `dashboard.html`.

- [ ] **Remove the News sub-tab bar** (`:1709-1712`, `<div class="news-subtabs">…Updates/Timeline…</div>`) — News renders the feed directly with no sub-tab bar.
- [ ] **Remove the Timeline sub-panel** (`:1718`+ `news-subpanel-timeline` and its inner markup: filter chips container, `timeline-feed`, `timeline-count`, archive toggle).
- [ ] **Remove `switchNewsSubtab`** (`:2338`+) — no longer needed (single view). Update the Updates panel to be always-visible.
- [ ] **Remove timeline JS** (`:2713-2831`): `CATEGORY_LABELS`, `DAY_LABELS`, `TIMELINE_MAJOR`, `timelineShowAll`, `toggleTimelineArchive`, `toggleFilter`, `renderFilterChips`, `renderTimelineEvents`, `renderTimeline`, `loadTimeline`, plus `timelineData`/`activeFilters` globals (grep).
- [ ] **Remove the `loadTimeline();` call** (`:3134`).
- [ ] **Remove timeline CSS** (`.timeline-*`, `.filter-chip`, `.filter-divider`, `.news-subtabs`, `.news-subtab` — `:889`+, `:1201-1228`).
- [ ] **Remove timeline i18n strings** (`timeline.*`, `news.subtab.timeline`, `news.subtab.updates` — `:1780-1781`).
- [ ] **`timeline.json`:** leave the file (now unused; harmless) — note it in CHANGELOG as orphaned data.
- [ ] **Verify:** News tab shows only the feed; no Timeline tab; no console errors (timeline refs gone).

---

### T3 — News = single sourced feed

**File:** `dashboard.html`. The feed (official statements + videos→video/article, `:3032-3044`) already renders via `buildFeedCardsHtml` + filter chips. With T2 done, it's the only News view.

- [ ] Confirm the Updates sub-panel is the default/only News content (remove `active`-class gating tied to the removed sub-tabs).
- [ ] **(Optional, confirm in build)** verify the video/article typing (`:3037`) is correct for the live `status.json` (11 entries → 5 video + 6 article); if news links are mis-typed, note as a `gather_facts`/data follow-up (out of scope for this UI plan).
- [ ] **Verify:** All / Official / Articles / Videos chips work; counts honest; newest-first.

---

### T4 — Compact the top half (topbar + hero + safety strip)

**File:** `dashboard.html`.

- [ ] **Hero — hide empty cells:** in `renderHeroStatus` (grep it) set each `.hero-status-item` to `hidden` when its value is empty/`"--"`/null, so a resolved incident shows only populated fields (e.g. Evacuation + Residents), not 4 cells with 2 blanks. Verify Tank temp / Day disappear when `--`.
- [ ] **Safety strip — relabel + compact** (`:1660-1673`): keep the disclosure line. Replace the unlabeled routing row with labeled, compact items and **drop the bare "OCFA"**:
  ```html
  <div class="safety-strip-sources">
    <span class="safety-strip-lbl">Emergency:</span> <a href="tel:911">911</a>
    <span class="safety-strip-sep">·</span>
    <span class="safety-strip-lbl">Official updates:</span> <a href="https://ggcity.org/emergency" target="_blank" rel="noopener">ggcity.org/emergency</a>
    <span class="safety-strip-sep">·</span>
    <span class="safety-strip-lbl">City info line:</span> <a href="tel:+17146287085">(714) 628-7085</a>
  </div>
  ```
  Move "OCFA" → Info → About → official sources (labeled "Orange County Fire Authority" with a link), via `renderResources` official-links (`:2877`).
- [ ] **Tighten CSS:** reduce `.hero-status` and `.safety-strip` vertical padding (`:518,387`); keep `.app-chrome` clamp (`:156`).
- [ ] **Verify (binding):** disclosure + 911 + ggcity still visible; top half visibly shorter; map gets the freed space.

---

### T5 — Wind widget ≤ ¼ size

**File:** `dashboard.html`, `.map-wind` (`:656-677`) + overlay markup (`:1686-1692`).

- [ ] CSS: `width: 160px → 92px`, `padding: 6px 10px → 3px 6px`, `font-size: 11px → 9px`; `.wind-source 10px → 8px`.
- [ ] Move the "(weather data, not safety guidance)" disclaimer out of the visible box into the overlay's `title`/`aria-label` (keeps the honesty cue without the bulk); shrink `#wind-arrow-map`.
- [ ] **Verify:** Edge-headless screenshot — wind overlay ≤ ¼ of its current bounding area; still legible; NOAA source + non-safety note present (in title).

---

### T6 — Info → Resources order (per D-b)

**File:** `dashboard.html`.
- [ ] **(b1, recommended) Merge:** drop the separate "Where to go · nearest shelters" block (`:2488-2492`, `info-shelter-list`) since `renderResources` already renders the same shelters as "Evacuation shelters" (`:2837-2839` + `renderResourceShelters`). Keep one shelter section; move "School closures" (`:2494-2496`) to sit after it.
- [ ] **(b2, fallback) Reorder only:** move the "School closures" block (`:2494-2496`) to *after* `resources-content` (`:2499`), so "Where to go" and "Evacuation shelters" become adjacent.
- [ ] **Verify:** shelter content is contiguous; School closures no longer splits it; no empty/duplicate sections.

---

### T7 — Info → Status desktop layout

**File:** `dashboard.html`, info panel CSS (`.info-subpanel` `:1239`, `.info-kv-row` `:1430`, desktop `@media` `:1556`).
- [ ] Add a desktop constraint so the 4-row status list doesn't strand a huge void:
  ```css
  @media (min-width: 768px) {
    .info-subpanel { max-width: 760px; margin-left: auto; margin-right: auto; }
  }
  ```
  (Tune the value at build via visual check; goal: status content fills a sensible column, not the full ultrawide.)
- [ ] **Verify:** desktop Status sub-tab no longer feels sparse; mobile unchanged.

---

### T8 — Sticky sub-tabs (when >1 sub-tab)

**File:** `dashboard.html`, `.info-subtabs` (`:1230`). After T2, only **Info** has multiple sub-tabs (News has none).
- [ ] Make `.info-subtabs` stick to the top of its scroll container while scrolling:
  ```css
  .info-subtabs { position: sticky; top: 0; z-index: 3; }
  ```
  (Confirm the correct sticky context = the tab-panel scroll container; adjust `top` if there's an overlapping header.)
- [ ] **Verify:** scrolling the Info tab keeps Status|Resources|About pinned; News (no sub-tabs) unaffected.

---

### T9 — Eval reframe to English-only G1 guard (per D-c)

**File:** `eval/test_language_access.py`.
- [ ] **Delete** `test_vietnamese_held_with_official_fallback` (`:62-71`) — obsolete once `vi` is gone.
- [ ] **(c1, recommended) Add** `test_english_only`:
  ```python
  def test_english_only():
      """Safety choice: the app ships English only — no non-English (unverifiable) language surface."""
      html = DASHBOARD.read_text(encoding="utf-8")
      langs = _parse_langs(html)
      codes = [c for c, _ in langs]
      assert codes == ["en"], (
          "app must be English-only (non-English safety copy is not shipped without "
          "reliable human translation): found languages " + ", ".join(codes)
      )
      return {"passed": True, "details": "languages=" + ",".join(codes), "metrics": {"languages": len(codes)}}
  ```
- [ ] **Keep** `test_no_unverified_language_ships` (still valid; now trivially English-only).
- [ ] **Update** `ENGLISH_ONLY_KEYS` (`:78-83`): remove `signpost.vi.body`, `signpost.vi.cta`, `timeline.showAll`, `timeline.showMajor` (those keys are deleted in T1/T2). Keep `share.copied`, `wind.*`, `info.subtab.*`.
- [ ] **Update the module docstring** to state the English-only safety posture (no `vi`/hold language).
- [ ] **Verify:** `python eval/run_all.py --skip integration` → **48/48** (41 behavioral + 7 schema), exit 0. NEVER `--quiet`.

---

### T10 — Reviewer-facing docs + memory reframe

- [ ] **README.md:** any "bilingual / Tiếng Việt" claim → "English-only"; reframe the human-oversight/G1 line to "we don't ship safety copy in a language we can't reliably verify; the app is English-only and routes to officials, who provide their own multilingual access."
- [ ] **cover-letter-draft.md `:5`:** "bilingual English / Tiếng Việt" → "English (routes to officials for other languages)".
- [ ] **evidence-summary.md / CLAUDE.md / docs/LANGUAGE_ACCESS.md / submission-checklist.md:** change every "Vietnamese held pending verification" framing to the English-only safety choice; keep G1 as a *strengthened* enforced control (T9 test). `docs/DEPLOYMENT_READINESS.md` is already done.
- [ ] **Memory:** rewrite `memory/vi-held-pending-verification.md` (and its `MEMORY.md` line) to record the 2026-05-30 decision: VI removed, English-only, G1 satisfied by no-translation-surface. Update `g1-translation-posture.md` similarly.
- [ ] **Verify:** `grep -rin "tiếng việt\|vietnamese\|bilingual\|vi.ready" README.md CLAUDE.md docs/` returns only intentional historical mentions (e.g., CHANGELOG, archived session docs).

---

### T11 — Cache bump + changelog

- [ ] `sw.js`: `CACHE_NAME` `gg-tank-v8` → `gg-tank-v9`.
- [ ] `CHANGELOG.md`: new entry — English-only (VI removed), Timeline removed, top-half/wind/Resources/Status/sticky-subtab changes, eval reframed (still 48/48), orphaned `timeline.json` noted.

---

### T12 — Verify + gated push/PR

- [ ] `python eval/run_all.py --skip integration` → 48/48, exit 0.
- [ ] Edge-headless 6-viewport (375×812, 375×667, 768×1024, 1024×768, 1280×720, 414×896) light + dark: confirm — no language button; compact top half with disclosure+routing visible; wind ≤¼; News single feed; Info Resources order; Info Status desktop fill; sticky Info sub-tabs.
- [ ] `git status --short` (do NOT stage `eval/scores.jsonl`); stage explicit paths; commit per task group.
- [ ] **PUSH GATE (consent):** present diff; on OK, `git push -u origin feat/dashboard-english-only-ux` + PR (problem/approach/test plan/risk/rollback). Merge via PR only.

---

## Self-Review
1. **Coverage:** all 8 original items + top-half compaction (12/13) + VI removal mapped to T1–T11. ✓
2. **Placeholders:** logic edits (T1/T2/T9) carry exact anchors + code; sizing edits (T4/T5/T7) carry concrete targets + visual-verify (legitimate for design). The 145 `vi:` strip and `renderHeroStatus` edit name the exact function/grep; build performs the literal edit. ✓
3. **Safety:** disclosure + official routing preserved (T4 binding); English-only enforced by eval (T9), not just removed. ✓
4. **Consistency:** eval stays 48/48 (c1), so the README "48" from the prior branch stays correct — no count re-churn. ✓
5. **Decisions surfaced:** D-a, D-b, D-c flagged for sign-off, with recommendations. ✓
