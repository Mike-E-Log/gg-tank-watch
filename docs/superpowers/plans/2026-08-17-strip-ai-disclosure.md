# Persistent Strip AI-Disclosure Implementation Plan

> **STATUS: DEFERRED (operator ruling 2026-08-17).** Ships only after the Claude Corps decision arrives (expected by Sep 1, 2026). The work is complete and green (213/213) on local branch `readme-clarity-and-strip`; do not push it before then. Default wording at ship time: the scoped clause "Summaries AI-assisted, human-checked" (matches About's summaries-only claim), operator may override. This deferral is a review-window optics choice, not a freeze-rule requirement: the ratified freeze scope (2026-08-05, session 73075a20) binds incident content only and keeps repo/UI changes open.

> **For agentic workers:** REQUIRED SUB-SKILL: per project CLAUDE.md this plan executes INLINE in the main session (no subagent-driven development). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the short AI-disclosure clause to the dashboard's always-visible safety strip (operator option 1), with the census, service-worker, and doc surfaces updated so the suite is green by exit code.

**Architecture:** Text-guard TDD against `public/dashboard.html` (the repo's pure-stdlib eval harness reads the file; no JS runtime). One new behavioral test moves the census 212→213 (default) / 214→215 (full), so every machine-guarded and prose count copy updates in the same change. Service-worker cache bumps v92→v93 so cached clients pick up the new shell.

**Tech Stack:** stdlib Python eval harness (`eval/run_all.py`), single-file dashboard, Vercel static hosting.

## Global Constraints

- Verify ONLY by unpiped `python eval/run_all.py --skip integration` + exit code (never `--quiet`).
- No em dashes in new prose; publication voice.
- G1: the new i18n key ships English-only; listed in `ENGLISH_ONLY_KEYS`.
- Remote surfaces keep floor wording ("more than 200") — never pin the live count outside this repo.
- Final clause wording + 4-row mobile acceptance = operator ruling (audit NEEDS-USER items) before merge.

---

### Task 1: Failing guard + strip implementation — DONE

**Files:** Modify: `eval/test_safety_strip_route.py` (new `test_safety_strip_discloses_ai_assistance`), `public/dashboard.html` (strip span + `"safety.strip.ai"` i18n key), `eval/test_language_access.py` (`ENGLISH_ONLY_KEYS` + `"safety.strip.ai"`).

- [x] **Step 1:** Guard written; verified FAIL (`markup=False order=False en=''`, exit 1).
- [x] **Step 2:** Markup + i18n implemented; module now passes.

### Task 2: Census sweep 212→213 / 214→215 / 204→205 / ~194→~195

**Files:** Modify: `README.md:12,66,131,134,137,140,142,178,235,361,386,396,422`, `CLAUDE.md:16`, `docs/CONTRIBUTING.md:35`, `docs/AI_CONTROL_ARCHITECTURE.md:165`, `docs/safety-method/evidence-summary.md:12`, `docs/safety-method/safety-method-writeup.md:5,62`.

- [ ] **Step 1:** Apply exact replacements (each site: `212`→`213`; also `204/204`→`205/205` at README.md:134; `**214**`→`**215**` at README.md:140; `~194 tests in the 212-test suite`→`~195 tests in the 213-test suite` at AI_CONTROL_ARCHITECTURE.md:165; badge `eval-212%20tests`→`eval-213%20tests` at README.md:12). Historical files (`docs/archive/*`, `docs/CHANGELOG.md`) stay untouched.
- [ ] **Step 2:** Run `python eval/run_all.py --only test_readme_archive_count; echo EXIT=$?` → expect PASS, EXIT=0.

### Task 3: Service-worker bump v92→v93 + pin tests

**Files:** Modify: `public/sw.js:1` (`gg-tank-v92`→`gg-tank-v93`), `eval/test_sw_cache_strategy.py` (rename `test_cache_bumped_v92`→`test_cache_bumped_v93`, expected string v93), `eval/test_sw_precache.py` (v92 pin→v93).

- [ ] **Step 1:** Update both pin tests first (renames keep the census at 213), run `python eval/run_all.py --only test_sw_cache_strategy --only test_sw_precache; echo EXIT=$?` → expect FAIL (sw.js still v92).
- [ ] **Step 2:** Bump `public/sw.js` CACHE_NAME to `gg-tank-v93`; re-run the two modules → PASS.

### Task 4: Full-suite green + render check

- [ ] **Step 1:** `python eval/run_all.py --skip integration; echo EXIT=$?` → expect `TOTAL 213/213`, EXIT=0.
- [ ] **Step 2:** Headless-Edge render of the working-tree dashboard at 390px: measure `.safety-strip-info` height; report rows to the operator (audit measured 35px = 2 lines below 480px).

### Task 5: Operator ruling → final wording → commit

- [ ] **Step 1:** Operator picks: clause scope ("Summaries AI-assisted, human-checked" vs unscoped) and 4-row mobile acceptance vs shorter clause.
- [ ] **Step 2:** Apply the picked wording to `public/dashboard.html` (i18n en value + no-JS fallback span, both in sync); re-run `test_safety_strip_route` module → PASS; re-measure at 390px.
- [ ] **Step 3:** Commit (branch `readme-clarity-and-strip`); PR; merge on operator approval.
