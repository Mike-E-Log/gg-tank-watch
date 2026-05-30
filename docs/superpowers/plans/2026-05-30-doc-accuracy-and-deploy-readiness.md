# Doc-Accuracy Cluster + Deploy-Readiness Consolidation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix reviewer-facing documentation inaccuracies (stale 47→48 eval count; DISTRIBUTION.md describing removed features) and replace the stale/contradictory idea-to-ship sentinel files with one accurate deploy-readiness source of truth — before the Anthropic Fellows submission.

**Architecture:** Pure documentation changes. No code, no logic, no tests authored. The "test" for each change is a verification grep (no stale string remains) plus the existing eval harness still passing 48/48. All work on a feature branch → PR → merge (never push `main`). Vietnamese copy is never authored or machine-translated (G1).

**Tech Stack:** Markdown docs; `git`; `python eval/run_all.py --skip integration` (verification only).

**Verified preconditions (2026-05-30):**
- Live eval count is **48/48** (`--skip integration`; 41 behavioral + 7 schema), exit 0. Confirmed by running it.
- All current-facing "47" references located: README.md (×3), CLAUDE.md (×1), cover-letter-draft.md (×1), evidence-summary.md (×1), safety-method-writeup.md (×2), submission-checklist.md (×2) = 6 files, 10 sites.
- DISTRIBUTION.md removed-feature drift: address checker (lines 91, 103, 104-VI, 107, 111, 181, 228) + blast-radius/plume map (line 180). Per memory `conduit-strategy`: address checker + severity removed 2026-05-26; tool is now a pure information conduit.
- Git tree clean except disposable `eval/scores.jsonl` append.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `README.md` | Modify | eval count 47→48 + scorecard block (behavioral 40→41) |
| `CLAUDE.md` (project) | Modify | "47-test" → "48-test" in safety table |
| `docs/fellowship/cover-letter-draft.md` | Modify | "47/47" → "48/48" |
| `docs/fellowship/evidence-summary.md` | Modify | "47-test" → "48-test" |
| `docs/fellowship/safety-method-writeup.md` | Modify | "47-test" → "48-test" (×2); ratify header as-is |
| `docs/fellowship/submission-checklist.md` | Modify | "47 tests"/"47/47" → 48; check eval box still accurate |
| `docs/DISTRIBUTION.md` | Modify | strip removed-feature drift (address checker, plume map) |
| `docs/DEPLOYMENT_READINESS.md` | Create | single deploy-readiness source of truth (Lane B + G1 gates) |
| `loop/DONE.md` | Create | terminal sentinel: build loop closed, points to readiness doc |
| `docs/sessions/2026-05-25-conduit-sprint-execution-plan.md` | Create (git mv) | archived EXECUTION_PLAN.md |
| `docs/sessions/2026-05-25-conduit-sprint-loop-state.md` | Create (git mv) | archived LOOP_STATE.md |
| `plan/EXECUTION_PLAN.md` | Delete (via git mv) | superseded |
| `loop/LOOP_STATE.md` | Delete (via git mv) | superseded |

---

### Task 0: Branch

- [ ] **Step 1: Verify clean state + branch off main**

Run:
```bash
cd "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-watch"
git branch --show-current   # expect: main
git checkout -b docs/accuracy-and-deploy-readiness
```
Expected: switched to new branch. (The `M eval/scores.jsonl` carries over harmlessly; do not stage it.)

---

### Task 1: Eval-count correction (47 → 48) across all current-facing docs

**Files:** `README.md`, `CLAUDE.md`, `docs/fellowship/{cover-letter-draft,evidence-summary,safety-method-writeup,submission-checklist}.md`

- [ ] **Step 1: README.md line 14** — in the recommended-path sentence:
  - OLD: `` (run `python eval/run_all.py --skip integration` — 47 tests, exits 0).``
  - NEW: `` (run `python eval/run_all.py --skip integration` — 48 tests, exits 0).``

- [ ] **Step 2: README.md scorecard block (lines 35, 38, 41)**:
  - Line 35 OLD: `Expected output (47 tests, all green):` → NEW: `Expected output (48 tests, all green):`
  - Line 38 OLD: `  behavioral       40/40   (100.0% pass)` → NEW: `  behavioral       41/41   (100.0% pass)`
  - Line 41 OLD: `  TOTAL            47/47   (100.0% pass)` → NEW: `  TOTAL            48/48   (100.0% pass)`

- [ ] **Step 3: CLAUDE.md line 16** — Scalable-oversight row:
  - OLD: `| **Scalable oversight** | 47-test eval harness monitors`
  - NEW: `| **Scalable oversight** | 48-test eval harness monitors`

- [ ] **Step 4: cover-letter-draft.md line 5**:
  - OLD: ``**Run the harness:** `python eval/run_all.py --skip integration` (47/47, exits 0).``
  - NEW: ``**Run the harness:** `python eval/run_all.py --skip integration` (48/48, exits 0).``

- [ ] **Step 5: evidence-summary.md line 12**:
  - OLD: `| **Scalable oversight** | 47-test eval harness monitors behavioral properties`
  - NEW: `| **Scalable oversight** | 48-test eval harness monitors behavioral properties`
  - (Leave the "17 control-specific tests" count untouched — that is a different, correct subset count.)

- [ ] **Step 6: safety-method-writeup.md** — two sites:
  - Line 5 (TL;DR) OLD: `A 47-test eval harness, with control-specific tests` → NEW: `A 48-test eval harness, with control-specific tests`
  - Line 62 OLD: `So the controls come with a 47-test eval harness (confirm the current count` → NEW: `So the controls come with a 48-test eval harness (confirm the current count`
  - (Keep the line-62 "confirm the current count with `eval/run_all.py` before any external use" caveat — it is good practice.)
  - **Header (line 3) is RATIFIED AS-IS** — no edit. The agent-inserted "Status (2026-05-29 decision): kept private" block is accurate (repo is private; it is a fellowship asset) and self-flags re-decision if the repo goes public. The user ratified it by choosing this action. NOTE for later: if the repo is made public for submission, this header must be updated then.

- [ ] **Step 7: submission-checklist.md** — two sites:
  - Line 24 OLD: `` | **Scalable oversight** | `docs/AI_CONTROL_ARCHITECTURE.md` | `eval/` harness (47 tests), `` → NEW: `` ... `eval/` harness (48 tests), ``
  - Line 44 OLD: `- [x] **Eval harness runs clean.** ... Verified 47/47 pass (2026-05-29; was 45/45 on 2026-05-25, +2 for the G1 language-access gate)`
  - NEW: `- [x] **Eval harness runs clean.** ... Verified 48/48 pass (2026-05-30; was 47/47 on 2026-05-29, 45/45 on 2026-05-25)`

- [ ] **Step 8: Verify no stale current-facing "47" eval refs remain**

Run:
```bash
grep -rn "47" README.md CLAUDE.md docs/fellowship/ | grep -iE "47[ -]test|47/47|47 test" || echo "CLEAN — no stale 47 eval refs"
```
Expected: `CLEAN — no stale 47 eval refs`

- [ ] **Step 9: Confirm eval still 48/48 (sanity — no code touched, but verify the claim)**

Run: `python eval/run_all.py --skip integration | tail -4`
Expected: `TOTAL            48/48   (100.0% pass)`

- [ ] **Step 10: Commit**

```bash
git add README.md CLAUDE.md docs/fellowship/cover-letter-draft.md docs/fellowship/evidence-summary.md docs/fellowship/safety-method-writeup.md docs/fellowship/submission-checklist.md
git commit -m "docs: correct eval count 47->48 across reviewer-facing docs"
```

---

### Task 2: Strip removed-feature drift from DISTRIBUTION.md

**File:** `docs/DISTRIBUTION.md`. The tool removed its address checker + severity/blast-radius/plume map on 2026-05-26 (conduit pivot); the doc still markets them.

- [ ] **Step 1: Line 91 (what-it-does bullet)**
  - OLD: `- **What it does**, plainly: a quick view of the current situation + an address check, updated regularly.`
  - NEW: `- **What it does**, plainly: a quick, bilingual view of the current situation that always routes people to the city's official page and hotline, updated regularly.`

- [ ] **Step 2: Line 103 (Phase 0 EN blurb)**
  - OLD: `I made a simple web page that shows the current status of the Garden Grove chemical-tank situation and lets you check an address. It's **not official**`
  - NEW: `I made a simple web page that shows the current status of the Garden Grove chemical-tank situation at a glance and always links the city's official page. It's **not official**`

- [ ] **Step 3: Line 104 (Phase 0 VI placeholder)** — remove the stale machine-translated VI (it references the removed address check; G1 forbids shipping MT VI). Match the empty-placeholder style of lines 108/112:
  - OLD (the entire VI blockquote): `> **VI (placeholder — Nancy to verify):** *[Tôi đã làm một trang web đơn giản ... Ba/Mẹ có muốn con chỉ cách dùng không?]*`
  - NEW: `> **VI (placeholder — Nancy to verify):** *[…]*`

- [ ] **Step 4: Line 107 (Phase 1 EN blurb)**
  - OLD: `a glanceable, bilingual view of the Garden Grove tank situation and an address checker. It always points people to the city's official page and hotline`
  - NEW: `a glanceable, bilingual view of the Garden Grove tank situation. It always points people to the city's official page and hotline`

- [ ] **Step 5: Line 111 (Phase 2 EN blurb)**
  - OLD: `**Garden Grove tank situation — quick status & address check (unofficial, free, EN/Tiếng Việt).** A volunteer-made page summarizing the current situation and letting you check an address. **For official orders and updates, always use ggcity.org/emergency · 714-628-7085.** Updates ~every 30 min.`
  - NEW: `**Garden Grove tank situation — quick status (unofficial, free, EN/Tiếng Việt).** A volunteer-made page summarizing the current situation that always routes you to officials. **For official orders and updates, always use ggcity.org/emergency · 714-628-7085.** Updates ~every 30 min.`

- [ ] **Step 6: Line 180 (estimates-labeled bullet)** — the blast-radius/plume map was removed; the map now shows official evacuation zones:
  - OLD: `- **Estimates labeled as estimates:** the blast-radius/plume map already carries "not authoritative" notes — keep that language loud; never let a visual estimate read as official fact.`
  - NEW: `- **Map reads as unofficial:** the map shows official evacuation zones, not the tool's own predictions — never let any visual read as an official order or an authoritative hazard estimate. Keep the "unofficial" framing loud on every map view.`

- [ ] **Step 7: Line 181 (no-data-collection bullet)** — drop the address-checker parenthetical:
  - OLD: `- **No data collection / no login / no ads** — and *say so*. "Free, no sign-up, we don't collect your data" removes the scam suspicion. (Confirm the address checker doesn't transmit/store entered addresses; if it does, disclose — coordinate with Legal.)`
  - NEW: `- **No data collection / no login / no ads** — and *say so*. "Free, no sign-up, we don't collect your data" removes the scam suspicion. The tool takes no user input and stores nothing — keep it that way.`

- [ ] **Step 8: Line 228 (open question 4)** — resolve the now-moot question without renumbering:
  - OLD: `4. **Does the address checker store/transmit entered addresses?** If yes, privacy disclosure needed (coordinate with Legal) before any wider distribution.`
  - NEW: `4. **Data input / privacy:** *Resolved — the conduit takes no user input (the address checker was removed 2026-05-26), so there is nothing entered to store or transmit and no privacy disclosure is required.*`

- [ ] **Step 9: Verify no removed-feature drift remains**

Run:
```bash
grep -inE "address.checker|check an address|address check|blast.radius|plume.(map|cone)|lets you check" docs/DISTRIBUTION.md || echo "CLEAN — no removed-feature drift"
```
Expected: `CLEAN — no removed-feature drift` (line 96's "exact plume concentrations" in the *never-claim* list is intentional and uses neither pattern — confirm it is NOT matched; if matched, it is the allowed "things-we-can't-claim" list and should stay.)

- [ ] **Step 10: Commit**

```bash
git add docs/DISTRIBUTION.md
git commit -m "docs(distribution): remove address-checker + plume-map drift (conduit pivot)"
```

**Out of scope (flag, do not fix here):** DISTRIBUTION.md still names "Nancy" as the VI verifier in several places; per memory `vi-held-pending-verification` Nancy is not fluent. That is a separate drift thread — left untouched to keep this change surgical.

---

### Task 3: Replace stale sentinel files with one deploy-readiness source of truth

**Files:** Create `docs/DEPLOYMENT_READINESS.md` + `loop/DONE.md`; archive `plan/EXECUTION_PLAN.md` + `loop/LOOP_STATE.md` into `docs/sessions/`.

- [ ] **Step 1: Create `docs/DEPLOYMENT_READINESS.md`** with this content:

```markdown
# Deployment Readiness — GG Tank Watch

**Single source of truth for launch state.** Supersedes `plan/EXECUTION_PLAN.md` and
`loop/LOOP_STATE.md` (archived 2026-05-30 under `docs/sessions/`), which were frozen at
the 2026-05-25 conduit sprint and contradicted each other.

**Status (2026-05-30): PRE-LAUNCH.** Code is design-complete and live; public go-live is
blocked by the Lane B human gates below. `noindex` stays ON until attorney review clears.

## Shipped (code complete)

- Conduit tasks T1–T3, T5–T7 (official-zone router, provenance, AI disclosure, official-
  sources panel, Code of Conduct, AirNow AQI). T4 (Vietnamese) intentionally held — see
  Language gate.
- v0.15 resident shareability (#49), v0.16 Vietnamese hold (#51), v0.17 design-complete
  (Map + News + Info + Timeline + tablet) (#54).
- Eval harness **48/48** (`python eval/run_all.py --skip integration`, exit 0).
- Live at https://gg-tank-watch.vercel.app — auto-deploy active (PR #52 moved hosting to a
  personal account; the prior org/Hobby stale-data block is resolved). Honest staleness
  banner intact.

## Lane B — launch gate (blocks public go-live; not code)

- [ ] **Attorney review** (the `noindex` gate, "B3" in CLAUDE.md) — incl. naming /
  impersonation posture (any `.org` domain, non-government disclosure). Source research:
  `docs/LEGAL.md`. Removing `noindex` requires this to clear.
- [ ] **Entity formation** — appropriate legal entity for liability shielding.
- [ ] **Insurance** — liability coverage.

## Language gate (G1 — gates `vi.ready = true`, not launch)

- [ ] Schedule (not just "reach") a fluent native Vietnamese reviewer.
- [ ] Decide the in-product VI sign-post label: keep `Tiếng Việt`, adopt a verbatim
  official phrase from ggcity.org/hazmat-incident, or fund a certified translation
  (~$100–400 for the short set).
- [ ] Confirm the OC County `_VIE.pdf` is genuine human VI (not machine-translated).
- Until then: `vi.ready = false`, English fallback, eval gate enforces it.

## Deferred (Phase 2, not blocking)

- Custom domain (`gardengrovetankwatch.org` / `ggtankwatch.org`) + final URL repoint.
- Approach B: curated "official Vietnamese sources" panel (Approach A sign-post is shipped).
```

- [ ] **Step 2: Create `loop/DONE.md`** with this content:

```markdown
# Loop DONE — conduit sprint + design-complete

status: DONE
closed_iso: 2026-05-30
supersedes: loop/LOOP_STATE.md (archived to docs/sessions/)

The idea-to-ship build loop is closed. All code tasks are complete and live
(conduit T1–T3, T5–T7; v0.15–v0.17; eval 48/48). T4 (Vietnamese) is held by design.

Remaining work is NOT code — it is the Lane B human launch gate (attorney review,
entity, insurance) and the G1 language gate. Track those in the single source of truth:
**`docs/DEPLOYMENT_READINESS.md`**. Do not re-open this loop for them.
```

- [ ] **Step 3: Archive the two stale sentinel files (preserve history via `git mv`)**

```bash
git mv plan/EXECUTION_PLAN.md docs/sessions/2026-05-25-conduit-sprint-execution-plan.md
git mv loop/LOOP_STATE.md docs/sessions/2026-05-25-conduit-sprint-loop-state.md
```

- [ ] **Step 4: Prepend a "superseded" banner to each archived file** (so a future reader is not misled). Add as the new first line of each:
  - `2026-05-25-conduit-sprint-execution-plan.md`: prepend `> **ARCHIVED 2026-05-30 — superseded by docs/DEPLOYMENT_READINESS.md.** Historical record of the 2026-05-25 conduit sprint; do not treat as current.\n\n`
  - `2026-05-25-conduit-sprint-loop-state.md`: prepend the same banner.

- [ ] **Step 5: Verify the loop/plan dirs are clean and DONE sentinel exists**

```bash
ls loop/ plan/ 2>&1            # expect: loop/ has DONE.md; plan/ gone or empty
ls docs/sessions/2026-05-25-conduit-sprint-*.md   # expect: both archived files
```

- [ ] **Step 6: Commit**

```bash
git add docs/DEPLOYMENT_READINESS.md loop/DONE.md docs/sessions/2026-05-25-conduit-sprint-execution-plan.md docs/sessions/2026-05-25-conduit-sprint-loop-state.md
git rm --cached plan/EXECUTION_PLAN.md loop/LOOP_STATE.md 2>/dev/null || true
git status --short            # confirm only intended files staged; do NOT stage eval/scores.jsonl
git commit -m "docs: close build loop + add single deploy-readiness source of truth"
```

---

### Task 4: Final verification + push gate

- [ ] **Step 1: Full verification sweep**

```bash
grep -rn "47" README.md CLAUDE.md docs/fellowship/ | grep -iE "47[ -]test|47/47" || echo "OK: no stale 47"
grep -inE "address.checker|check an address|lets you check|blast.radius" docs/DISTRIBUTION.md || echo "OK: no drift"
python eval/run_all.py --skip integration | tail -2
git status --short
git log --oneline -4
```
Expected: both `OK:` lines print; eval `48/48`; only the 3 new commits + the disposable `M eval/scores.jsonl` unstaged.

- [ ] **Step 2: PUSH GATE (consent required — outward-facing).** Do NOT push or open a PR automatically. Present the diff summary to the user and ask whether to `git push -u origin docs/accuracy-and-deploy-readiness` + open a PR (problem / approach / test plan / risk / rollback). Merge to `main` only via PR per CLAUDE.md.

---

## Self-Review

1. **Spec coverage:** (a) eval 47→48 — Task 1 covers all 6 files / 10 sites + verification. (b) DISTRIBUTION.md drift — Task 2 covers all 8 address-checker/plume sites + verification. (c) writeup header — Task 1 Step 6 ratifies as-is (explicit decision). (b/process) stale sentinels — Task 3 archives both + creates DEPLOYMENT_READINESS.md + loop/DONE.md. ✓
2. **Placeholder scan:** every edit step has exact OLD/NEW text or full file content; no TBD/TODO. ✓
3. **Consistency:** all counts go to **48** (matches the verified live `--skip integration` total); README sub-counts updated to 41/41 + 7/7 = 48. New docs reference `docs/DEPLOYMENT_READINESS.md` by the same path everywhere. ✓
4. **G1 safety:** no Vietnamese authored or machine-translated; the one VI edit (DISTRIBUTION line 104) *removes* stale MT, leaving an empty placeholder. ✓
5. **Surgical:** Nancy-as-VI-verifier drift explicitly left out of scope and flagged. ✓
