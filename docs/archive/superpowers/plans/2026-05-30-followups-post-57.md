# GG Tank Watch — Post-#57 Follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clear the five deferred TODOs from the 2026-05-30 dashboard batch — resolved-state banner correctness, a config-fetch refactor, dead-Vietnamese-residue removal, a DISTRIBUTION.md post-mortem reframe, and two cosmetic fixes — each as its own PR, production merge gated on explicit "merge #N".

**Architecture:** Single-file static dashboard (`dashboard.html`), Python writer (`scripts/update_status.py`), pytest-style eval harness (`eval/`), Vercel static hosting, cache-first service worker (`sw.js`). The incident resolved 2026-05-28; the live site is now a resolved-state demonstration and an Anthropic-fellowship portfolio piece whose thesis is honesty / AI-transparency.

**Tech Stack:** Vanilla JS + MapLibre GL, Python 3 stdlib writer, Python eval harness (`eval/run_all.py`), service-worker cache.

---

## Decisions (locked 2026-05-30)

- **#3 breaking approach → writer-side clear + UI defensive guard** (cross-vendor judges: Claude+GPT+Gemini unanimous 9/9/9 vs 3/4/2, HIGH confidence). Rationale: the only option with automated coverage AND it makes `status.json` itself honest — on-thesis. Implemented as a single post-resolution invariant in `build_snapshot()` + new `test_t6` + a defensive `!resolved` UI guard.
- **#4 → single shared `configReady` promise** (eng-review). `loadConfig()` returns the parsed config; the map reuses it instead of a second cache-first fetch. Consequence (accepted): the map polygon no longer draws from SW cache offline — fine for a resolved demo; the rest of the page already behaves this way.
- **#5 → remove dead vi residue + `terms.html` honesty fix + a new eval guard** so English-only is enforced for the STRINGS dict, not just the LANGS array.
- **#6 → in-place historical post-mortem reframe** of `DISTRIBUTION.md` (its own sunset rule at line 166 is now triggered).
- **#7 → hero `center` + LICENSE reword** (cosmetic).

## Constraints (binding)

- **English-only / conduit-only.** No directives, no authority over-claim. Recovery/resolved copy is descriptive of observed state.
- **Eval verified by exit code:** `python eval/run_all.py --skip integration` → exit 0. **NEVER `--quiet`** (it suppresses `[FAIL]` lines). Baseline before this work: **49/49**. Target after #5: **50/50**.
- **SW `CACHE_NAME` bump is part of ANY `dashboard.html` / `config.json` change** — increment `gg-tank-vN` (currently `v10`) or returning users keep the old shell (silent fail). `status.json` is network-first.
- **Status-driven UI lives in `render()` / `updateInfoData()`**, config-driven UI in `renderResources()` / `loadConfig()`.
- **No new dependencies.** No JS test runtime → JS-display changes are verified by signed Edge headless (`./__qa_shots.ps1`); map tiles render blank in headless (expected, not a bug).
- **Production deploy gate:** branch → PR → merge to `main` auto-deploys to the live resident site. Merge ONLY on the founder's explicit "merge #N". `noindex` stays on.

## File Structure

| File | Responsibility | Touched by |
|---|---|---|
| `scripts/update_status.py` | Writer: build status.json, breaking detection | #3 (Task 1) |
| `eval/test_writer.py` | Behavioral writer tests (t1–t5 family) | #3 (Task 1) |
| `dashboard.html` | The whole UI: render(), banners, loadConfig, map, hero, vi residue | #2,#3,#4,#5,#7 (Tasks 1,2,3,5) |
| `eval/test_no_vietnamese_residue.py` | NEW static guard: no vi residue in dashboard.html | #5 (Task 3) |
| `terms.html` | Terms page (carries a stale "Vietnamese version being prepared") | #5 (Task 3) |
| `docs/DISTRIBUTION.md` | Distribution strategy doc (now historical) | #6 (Task 4) |
| `LICENSE` | License + disclaimer (names removed features) | #7 (Task 5) |
| `sw.js` | Service worker cache (`CACHE_NAME`) | every dashboard.html PR |

**SW bump per PR:** before opening each dashboard.html-touching PR, read the current `CACHE_NAME` integer in `sw.js:1` and increment it (`v10`→`v11` for the first such PR merged, and so on). Task 4 (`DISTRIBUTION.md` only) and the LICENSE half of Task 5 do **not** need a bump; the hero-CSS half of Task 5 does.

---

## Task 1 — Group `fix/banners-resolved` (#3 writer-side + UI guard, #2 staleness)

**Files:**
- Modify: `scripts/update_status.py` (post-resolution breaking invariant, after line 494)
- Test: `eval/test_writer.py` (add `test_t6_post_resolution_statement_no_breaking`)
- Modify: `dashboard.html` (`render()`: hoist `resolved`, add `!resolved` guard ~2629; wire staleness banner ~2628)
- Modify: `sw.js` (`CACHE_NAME` bump)

### 1A — #3 writer-side clear (TDD)

- [ ] **Step 1: Write the failing test** — add to `eval/test_writer.py` after `test_t5` (line ~158):

```python
def test_t6_post_resolution_statement_no_breaking():
    """After the incident is ALREADY resolved (resolved_iso set on a prior tick),
    a routine new official statement must NOT re-arm breaking. The resolution
    TRANSITION (test_t5) still fires urgent; this guards every tick AFTER it,
    so status.json never carries breaking:true on a long-resolved incident."""
    _reset_sandbox()
    # Tick 1: baseline (not resolved)
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    # Tick 2: resolution transition (fires urgent — identical to test_t5)
    _tick({
        "evacuation_lifted": True,
        "incident_resolved_iso": "2026-05-24T12:00:00Z",
        "status_headline": "all clear",
        "sources_checked": [
            {"url": "https://ocfa.org/all-clear"},
            {"url": "https://latimes.com/all-clear"},
        ],
    })
    # Tick 3: incident ALREADY resolved + a brand-new official statement.
    exit_code, snap = _tick({
        "evacuation_lifted": True,
        "incident_resolved_iso": "2026-05-24T12:00:00Z",
        "status_headline": "recovery update",
        "sources_checked": [{"url": "https://ocfa.org/recovery"}],
        "official_statements": [
            {"agency": "OCFA", "time_iso": "2026-05-24T18:00:00Z",
             "text": "exclusion zone reduced to 150 ft", "source_url": "https://ocfa.org/recovery"}
        ],
    })
    return {
        "passed": exit_code == 0 and snap is not None and snap["breaking"] is False,
        "details": f"breaking={snap and snap.get('breaking')}, level={snap and snap.get('breaking_level')}, reason={snap and snap.get('breaking_reason')}",
        "metrics": {"breaking": snap and snap.get("breaking")},
    }
```

- [ ] **Step 2: Run it — expect FAIL.** Without the writer fix, tick 3's novel statement fires INFO breaking, so `breaking` is `True`.

Run: `python eval/run_all.py --skip integration`
Expected: `[FAIL] test_writer::test_t6_post_resolution_statement_no_breaking` (breaking=True), TOTAL 49/50.

- [ ] **Step 3: Implement the post-resolution invariant** in `scripts/update_status.py`. Insert **after line 494** (the end of the breaking decay `if/elif/else` block) and **before** the `# Compute timestamps` comment (line ~496):

```python
    # [#3 follow-up 2026-05-30] Post-resolution invariant: a resolved incident
    # carries NO live "breaking" state on any tick AFTER the resolution
    # transition. The transition tick itself (prev not resolved -> now resolved)
    # still fires urgent above (see detect_breaking + test_t5); this only clears
    # on subsequent ticks, so a routine recovery statement can't re-arm the
    # "UPDATE — N new official statement" banner and status.json stays honest.
    if incident.get("resolved_iso") and prev_incident.get("resolved_iso") and breaking:
        breaking, breaking_reason, breaking_since, breaking_level = False, None, None, None
```

(`incident` and `prev_incident` are both already in scope: `incident` is the snapshot's incident object, `prev_incident` is set at line 391.)

- [ ] **Step 4: Run tests — expect PASS, t5 still green.**

Run: `python eval/run_all.py --skip integration`
Expected: `[PASS] test_writer::test_t6_...`, `[PASS] test_writer::test_t5_incident_resolved_fires_urgent`, TOTAL **50/50**, exit 0.

### 1B — #2 staleness banner + #3 UI defensive guard (in `render()`)

> No automated test possible (Python harness can't exec dashboard.html JS). Verify visually in Step 8.

- [ ] **Step 5: Confirm the staleness infra exists** before wiring. Read `dashboard.html` around `:345` (`.banner-stale` CSS), `:1688-1689` (`banner.stale.title` / `banner.stale.msg`), `:1979` (`setBanners` handles `kind:"stale"`). If `banner.stale.msg` does not interpolate `{n}`, adjust the message arg in Step 6 to a no-arg string.

- [ ] **Step 6: Hoist `resolved`, add the `!resolved` guard, and wire the staleness banner.** In `dashboard.html render()`:

(a) Move the `resolved` computation up. Insert immediately before `var banners = [];` (line ~2627):

```javascript
  var now = new Date();
  var resolved = !!(snap.incident && snap.incident.resolved_iso);
```

(b) At the existing `var resolved = ...` line (~2665) remove the `var ` so it is no longer redeclared:

```javascript
  // was: var resolved = !!(snap.incident && snap.incident.resolved_iso);
  // now the value is already set above; keep the `if (resolved) { ... legend ... }` block using it.
```

(c) Add the staleness push right after the offline push (after line 2628), before `if (snap.breaking)`:

```javascript
  var staleAfter = snap.stale_after_iso ? new Date(snap.stale_after_iso) : null;
  if (staleAfter && now > staleAfter) {
    var dataAsOf = snap.data_as_of_iso ? new Date(snap.data_as_of_iso) : null;
    var minsAgo = dataAsOf ? Math.floor((now - dataAsOf) / 60000) : "?";
    banners.push({kind:"stale", title: t("banner.stale.title"), message: t("banner.stale.msg", {n: minsAgo})});
  }
```

(d) Change the breaking guard at line 2629 from `if (snap.breaking) {` to:

```javascript
  if (snap.breaking && !resolved) {
```

- [ ] **Step 7: Bump the service worker cache.** In `sw.js:1`, increment `CACHE_NAME` to the next integer (`gg-tank-v10` → `gg-tank-v11`).

- [ ] **Step 8: Verify.** Eval (`python eval/run_all.py --skip integration` → 50/50). JS sanity: `node --check` on the extracted `<script>` (or load locally + clean console). Visual: run `./__qa_shots.ps1` (signed Edge headless via `__qa_harness.html`) against `python -m http.server`; (i) confirm NO "UPDATE — 1 new official statement" banner on the resolved live data; (ii) temporarily edit a local `status.json` copy so `stale_after_iso` is in the past, reload, confirm the `⚠️ Stale` banner appears.

- [ ] **Step 9: Commit + PR (do NOT merge — await "merge #N").**

```bash
git checkout -b fix/banners-resolved
git add scripts/update_status.py eval/test_writer.py dashboard.html sw.js
git commit -m "fix(resolved): suppress post-resolution breaking + wire staleness banner"
git push -u origin fix/banners-resolved
gh pr create --title "fix: post-resolution breaking suppression + staleness banner" --body "<problem/approach/test plan/risk/rollback>"
```

---

## Task 2 — Group `refactor/config-fetch` (#4 single shared promise)

**Files:**
- Modify: `dashboard.html` (`loadConfig()` returns cfg; kickoff exposes `configReady`; map reuses it)
- Modify: `sw.js` (`CACHE_NAME` bump)

> No automated test (JS). Verify via Edge-headless map check.

- [ ] **Step 1: `loadConfig()` returns the parsed config.** In `dashboard.html` (~2754-2766) add a `return configCache;` so the promise resolves with the config:

```javascript
async function loadConfig() {
  try {
    var resp = await fetch("config.json?t=" + Date.now(), {cache:"no-store"});
    if (!resp.ok) throw new Error("config.json HTTP " + resp.status);
    configCache = await resp.json();
    renderInfoTab();
    renderResources();
    renderInfoShelters();
    refreshWind();
    return configCache;
  } catch (e) {
    console.warn("config load failed:", e);
    return null;   // configReady resolves to null; map skips drawing rather than throwing
  }
}
```

- [ ] **Step 2: Expose a single `configReady` promise at kickoff** (~2784):

```javascript
applyLang();
var configReady = loadConfig();
configReady.then(function() { fetchStatus(); });
setInterval(fetchStatus, REFRESH_MS);
```

- [ ] **Step 3: Map reuses `configReady` instead of its own fetch.** In the `map.on("load", ...)` handler (~2843-2844) replace the standalone fetch:

```javascript
  map.on("load", function() {
    configReady.then(function(cfg) {
      if (!cfg) return;   // config failed to load; leave the base map without overlays
      var poly = cfg.map.evac_polygon;
      // ... rest of the existing body unchanged (coords, addSource, addLayer, facility marker, shelters) ...
    });
  });
```

The only change is `fetch("/config.json").then(function(r){return r.json();}).then(function(cfg){` → `configReady.then(function(cfg){ if (!cfg) return;`. Everything inside the callback stays. (`configReady` is declared at kickoff, in scope for the map IIFE.)

- [ ] **Step 4: Bump `sw.js` `CACHE_NAME`** to the next integer.

- [ ] **Step 5: Verify.** Eval 50/50 (unchanged — JS only). `node --check`. Edge-headless: confirm the map still draws the evac polygon + facility/shelter markers (tiles blank in headless = expected; the polygon/markers are GeoJSON and DO render). Real-device/Vercel-preview map confirmation is the founder's check.

- [ ] **Step 6: Commit + PR (await "merge #N").**

```bash
git checkout -b refactor/config-fetch
git add dashboard.html sw.js
git commit -m "refactor(config): single shared configReady promise (drop duplicate map fetch)"
git push -u origin refactor/config-fetch && gh pr create --title "refactor: unify config fetch into one shared promise" --body "..."
```

---

## Task 3 — Group `chore/remove-vi-residue` (#5 + eval guard)

**Files:**
- Create: `eval/test_no_vietnamese_residue.py`
- Modify: `dashboard.html` (delete vi CSS / strings / comments)
- Modify: `terms.html` (delete `.vi-note` + the "Vietnamese version being prepared" placeholder)
- Modify: `sw.js` (`CACHE_NAME` bump — dashboard.html changed)

### 3A — Eval guard first (TDD: guard fails on current residue, passes after removal)

- [ ] **Step 1: Write the guard.** Create `eval/test_no_vietnamese_residue.py`:

```python
"""Static guard: dashboard.html ships English-only.

The LANGS array is already English-only (test_language_access::test_english_only),
but unverified Vietnamese STRINGS values and lang=vi CSS lingered behind a dead
ready:false gate. English-only is the project's safety posture (G1) — enforce it
for the STRINGS dict and CSS too, not just the language picker. Pure-text grep;
no JS execution needed.
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Diacritic set that only appears in Vietnamese copy here (kept narrow to avoid
# false positives on legitimate accented English/place names).
VI_DIACRITICS = "ạảấầẩậắằẳẵặẹẻẽếềểễệịỉọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹđ"


def test_no_vietnamese_residue():
    text = DASHBOARD.read_text(encoding="utf-8")
    lower = text.lower()
    bad_lines = []
    for i, line in enumerate(text.splitlines(), 1):
        ll = line.lower()
        # 1) a `vi:` key in the STRINGS dict (the dead translation values)
        if "vi:" in ll and ("'" in line or '"' in line):
            bad_lines.append((i, "vi: key", line.strip()[:80]))
        # 2) lang="vi" CSS / attribute selectors
        elif 'lang="vi"' in ll or "lang='vi'" in ll:
            bad_lines.append((i, 'lang=vi', line.strip()[:80]))
        # 3) Vietnamese diacritics (catches stray copy + held-VI comments)
        elif any(ch in line for ch in VI_DIACRITICS):
            bad_lines.append((i, "vi diacritics", line.strip()[:80]))
    return {
        "passed": len(bad_lines) == 0,
        "details": "no Vietnamese residue" if not bad_lines
                   else f"{len(bad_lines)} residue line(s): " + "; ".join(f"L{n}({why})" for n, why, _ in bad_lines[:8]),
        "metrics": {"residue_lines": len(bad_lines)},
    }
```

- [ ] **Step 2: Run it — expect FAIL** listing the current residue lines.

Run: `python eval/run_all.py --skip integration`
Expected: `[FAIL] test_no_vietnamese_residue::test_no_vietnamese_residue` (N residue lines), TOTAL 49/50.

### 3B — Remove the residue

- [ ] **Step 3: Delete the vi residue in `dashboard.html`.** Read each region first (line numbers drift), then delete:
  - `:91-101` — the `/* ===== VIETNAMESE TYPOGRAPHY ===== */` comment + `html[lang="vi"]` font/wordmark CSS rules (delete the whole block).
  - `:1644, 1649, 1662, 1663, 1672` — the `vi: '...'` value in each of these `STRINGS` entries (delete only the `vi:` line, keep `en:`; ensure the preceding `en:` line keeps/loses its trailing comma so the object literal stays valid).
  - `:1695-1718` — the held-VI strategy comment blocks + inline `G1:` pending-Nancy comments.
  - `:1755-1759` — the held-vi gate docstring comment.

  Verify after deletion that no remaining live code references a removed `vi` value (none does — `t()` reads `.en`).

- [ ] **Step 4: Delete the `terms.html` residue (honesty fix).**
  - `:40` — the `.vi-note { ... }` CSS rule.
  - `:69` — `<p class="vi-note" lang="vi">Bản tiếng Việt đang được chuẩn bị. (A Vietnamese version is being prepared.)</p>` — delete the whole element. (It promises a Vietnamese version that English-only-by-design will never ship — removing it is the honesty fix, not just cleanup.)

- [ ] **Step 5: Run tests — expect PASS.**

Run: `python eval/run_all.py --skip integration`
Expected: `[PASS] test_no_vietnamese_residue`, `[PASS] test_english_only`, `[PASS] test_new_strings_english_only`, TOTAL **50/50**, exit 0.

- [ ] **Step 6: `node --check`** the dashboard `<script>` (ensures the STRINGS object literal is still valid after deleting `vi:` lines). Bump `sw.js` `CACHE_NAME`.

- [ ] **Step 7: Commit + PR (await "merge #N").**

```bash
git checkout -b chore/remove-vi-residue
git add dashboard.html terms.html eval/test_no_vietnamese_residue.py sw.js
git commit -m "chore(i18n): remove dead Vietnamese residue + add English-only guard"
git push -u origin chore/remove-vi-residue && gh pr create --title "chore: remove dead vi residue + English-only eval guard (50/50)" --body "..."
```

---

## Task 4 — Group `docs/distribution-postmortem` (#6)

**Files:** Modify `docs/DISTRIBUTION.md` only. No code, no eval, no SW bump.

- [ ] **Step 1: Read `docs/DISTRIBUTION.md` in full** (line numbers below are approximate from investigation).

- [ ] **Step 2: Add a post-mortem header** at the top (after the title), stating: incident resolved 2026-05-28; the app shipped **English-only** on 2026-05-30 (fluent Vietnamese verification was never obtained — unverified safety copy is a liability in a life-safety tool, so the conservative choice was English + routing LEP residents to officials); distribution **never advanced past Phase 0** (family testing); this document is retained as a historical / post-mortem reference. Cite the sunset rule (line 166) as now in effect.

- [ ] **Step 3: Reframe the active-distribution sections as "planned, never deployed."** Wrap Sections 2–4 (channels / messaging / phased rollout, ~lines 50-165) under a callout: *"Planned strategy (never deployed) — for reference only."* Reframe posture point #4 (~23-24, "Bilingual, VI as first-class") to: original strategy was bilingual, but the product shipped English-only; LEP residents are routed to ggcity.org/emergency (which publishes verified Vietnamese). Reframe Ring C (~37-46) and the example blurbs (~100-112) to drop present-tense bilingual claims (or mark them "planned").

- [ ] **Step 4: Keep Section 5 (trust / anti-misinformation)** intact and label it as generalizable principles for future incident tools (it is not bilingual-dependent and remains valid).

- [ ] **Step 5: Mark the doc's own stale open-questions** (~223-230) as resolved where the resolution/English-only decision answers them.

- [ ] **Step 6: Verify** with `git diff docs/DISTRIBUTION.md` — confirm no remaining present-tense "we are distributing / Vietnamese is first-class" claims; the doc reads as historical + English-only.

- [ ] **Step 7: Commit + PR (await "merge #N").**

```bash
git checkout -b docs/distribution-postmortem
git add docs/DISTRIBUTION.md
git commit -m "docs(distribution): reframe as historical post-mortem (resolved + English-only)"
git push -u origin docs/distribution-postmortem && gh pr create --title "docs: DISTRIBUTION.md historical post-mortem reframe" --body "..."
```

---

## Task 5 — Group `fix/hero-and-license` (#7A hero, #7B LICENSE)

**Files:** Modify `dashboard.html` (hero CSS), `LICENSE`, `sw.js` (bump — dashboard.html changed).

- [ ] **Step 1: Center the resolved hero cells.** In `dashboard.html` find the `.hero-status-row` desktop rule (~497, `justify-content: space-between;`) and change to `justify-content: center;`. (Resolved state injects exactly 2 cells, ~2575-2583; `space-between` pins them to opposite edges. `center` clusters them with the existing 16px gap. The 4-cell active layout is no longer reachable on a resolved incident; `center` is also fine for it.)

- [ ] **Step 2: Reword the LICENSE disclaimer.** In `LICENSE` (~23-26), replace the sentence naming removed features:

```
This dashboard's data and status summaries are informational only — NOT
authoritative emergency guidance. Refer to official sources (Orange County Fire
Authority, ggcity.org/emergency, Genasys EVAC, Ready OC) for evacuation information.
```

(removes "blast-zone estimates, and plume visualization" — both removed in the conduit-only scope.)

- [ ] **Step 3: Bump `sw.js` `CACHE_NAME`** (dashboard.html changed; LICENSE is not cached).

- [ ] **Step 4: Verify.** Eval 50/50 (unchanged). Edge-headless desktop viewport: confirm the 2 resolved hero cells are centered, not edge-pinned. `git diff LICENSE`.

- [ ] **Step 5: Commit + PR (await "merge #N").**

```bash
git checkout -b fix/hero-and-license
git add dashboard.html LICENSE sw.js
git commit -m "fix(ui): center resolved hero cells + LICENSE conduit-scope reword"
git push -u origin fix/hero-and-license && gh pr create --title "fix: center resolved hero + LICENSE feature-scope reword" --body "..."
```

---

## Build sequencing

```
Order   Branch                       Files                                              Eval     SW bump
1       fix/banners-resolved         update_status.py, test_writer.py, dashboard, sw.js  50/50    v10→v11
2       refactor/config-fetch        dashboard.html, sw.js                               50/50    →v12
3       chore/remove-vi-residue      dashboard.html, terms.html, NEW eval test, sw.js    50/50    →v13
4       docs/distribution-postmortem docs/DISTRIBUTION.md                                (n/a)    none
5       fix/hero-and-license         dashboard.html, LICENSE, sw.js                      50/50    →v14
```

All dashboard.html-touching branches are **sequential** (same file → merge-conflict risk; re-base each on `main` after the prior merge). #4 is disjoint but the merge gate makes sequential simplest. Each PR is independently revertable.

## Verification (every code PR)

- `python eval/run_all.py --skip integration` → exit 0, **50/50** after #5 (49/50 mid-#3 and mid-#5 before the impl step — that's the TDD red). Never `--quiet`.
- `node --check` on the extracted dashboard JS (Tasks 1, 2, 3, 5).
- Signed Edge headless via `./__qa_shots.ps1` for the visual checks above (map tiles blank in headless = expected).
- Founder real-device / Vercel-preview confirmation for the map (Task 2) and any sticky/scroll behavior.

## NOT in scope (deferred)

- **Writer-side SWR for HTML** — bump-only chosen; SWR is a separate improvement.
- **A JS test runtime** — would be a new dependency; JS-display changes verified by Edge headless instead.
- **Default-tab change (map→hero)** — founder design decision, not assumed.
- **The #57 batch plan-doc stale status line** ("PLAN — awaiting build" though it shipped) — cosmetic doc-accuracy, separate from these TODOs.

## What already exists (reuse, don't rebuild)

- Staleness banner: `.banner-stale` CSS (`:345`), `banner.stale.{title,msg}` i18n (`:1688-9`), `setBanners` handles `kind:"stale"` (`:1979`). Only the `render()` comparison was missing.
- Writer prev-state diffing (`prev_incident`, `prev_breaking*`) — powers t1–t5 and extends cleanly to the t6 invariant.
- `configCache` global (`:2827`) + `resolved` var (`:2665`) — reused, not re-derived.
- Eval static-grep pattern (`test_no_air_quality_link`, `test_safety`) — modeled for the vi guard.
- DISTRIBUTION.md already contains its own sunset rule (line 166) — the reframe activates it, doesn't invent it.

## Failure modes

| Codepath | Realistic failure | Test? | Handling | Silent? |
|---|---|---|---|---|
| #3 writer invariant | clears a genuine post-resolution urgent | `test_t6` + `test_t5` retained | only clears AFTER the transition tick | visible |
| #2 staleness | perpetual banner if refresh cron stops | manual | honest-by-design (data IS stale) | visible |
| #4 shared promise | config fetch fails → polygon not drawn | manual (Edge) | `if (!cfg) return;` + loadConfig try/catch | handled (no throw) |
| #5 vi removal | break the STRINGS object literal | `node --check` + eval | pure dead-code deletion | caught by node --check |
| SW bump omission | changes don't reach cached users | this checklist | per-PR bump step | **silent → checklist gate** |

No critical gaps (each has a test or explicit handling). The one historically-silent mode (SW bump omission) is gated by the per-PR checklist step.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | not run (small follow-ups) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR | 1 issue (#3 approach), 0 critical gaps |
| Outside Voice | cross-vendor-judges | Independent multi-model scrutiny | 1 | CLEAR | #3 → A unanimous 9/9/9 vs 3/4/2, HIGH |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | not run (optional) |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | n/a |

- **CROSS-MODEL:** Claude + GPT + Gemini unanimously picked the writer-side+UI-guard approach for #3 (data honesty + testability + on-thesis), reversing the initial UI-only lean.
- **UNRESOLVED:** 0.
- **VERDICT:** ENG CLEARED — ready to implement. 5 PR groups, eval target 50/50, production merge gated on explicit "merge #N".
