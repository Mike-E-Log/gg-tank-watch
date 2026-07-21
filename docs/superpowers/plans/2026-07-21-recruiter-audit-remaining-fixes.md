# Recruiter-Audit Remaining Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task in the MAIN session thread (operator CLAUDE.md forbids subagent-driven development). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the three remaining fixes from the 2026-07-21 recruiter-presentation audit: product screenshot above the README fold, one canonical test-count story (211, with the 198-snapshot and 213-full-census explained), and a live-site → GitHub-repo link.

**Architecture:** Docs-only edits to `README.md` plus one minimal About-panel addition to the single-file dashboard (`public/dashboard.html`, i18n key + render line + CSS), guarded red-first by extending an existing eval test so the 211 census is preserved, with the repo's standard service-worker cache bump (v89→v90) so returning visitors receive the new HTML.

**Tech Stack:** Vanilla JS single-file dashboard, Python-stdlib eval harness (`eval/run_all.py`), service worker precache, Vercel static hosting (deploy = push to main, operator-gated).

## Global Constraints

- Repo CLAUDE.md: G1 English-only safety copy; no directives; no new deps; `noindex` permanent; branch → PR → merge, never push `main` directly.
- Verify with `python eval/run_all.py --skip integration` non-quiet (never `--quiet`), exit 0, TOTAL 211/211.
- Census must stay **211** (203 behavioral + 8 schema): the README badge, ~11 in-repo mentions, repo CLAUDE.md, and the external Mike-E-Log profile README all pin 211 — no new test functions/files.
- AI disclosure (`disclosure.ai`) keeps the About panel-closing position (user decision 2026-06-03).
- Commit on branch `presentation/recruiter-audit-remaining` only; push/PR/deploy needs operator approval.
- Audit 2026-07-21: PROCEED WITH TRIPWIRES — gate every commit on the non-quiet suite being green; never commit while `sw.js` and its v90 guards disagree.

---

### Task 1: README — product screenshot above the fold [EXECUTED]

**Files:**
- Modify: `README.md` (intro block, lines ~20–28)

**Interfaces:**
- Consumes: existing `docs/assets/preview-desktop.png` (Desktop title baked in, #57).
- Produces: first-screenful product shot; TL;DR paragraph moves directly below the image.

- [x] **Step 1: Move the desktop preview block above the TL;DR paragraph** — the `<p align="center">…preview-desktop.png…</p>` block now sits between the disclaimer blockquote and the TL;DR paragraph (order: title → bullets → badges → disclaimer → **image** → TL;DR → mobile grid → byline).
- [x] **Step 2: Verify by rendering** — GitHub markdown API render + github-markdown-css served locally, Playwright (msedge) screenshots at 1280×800. Before: fold ends mid-TL;DR, no product visible. After: dashboard masthead + map clearly inside the first viewport.

### Task 2: README — one canonical test-count story [EXECUTED]

**Files:**
- Modify: `README.md` ("Run the tests yourself" section + the `gg-tank-watch-method` bullet)

- [x] **Step 1: Add the 213 note** after the expected-output block:
  `(The full census is **213**: the 2 extra tests are live geocoder regressions that call OpenStreetMap's Nominatim service over the network, so they stay opt-in — drop `--skip integration` to run them.)`
  Verified: `eval/test_geocoder.py` is the only `CATEGORY = "integration"` module and holds exactly 2 test functions (211 + 2 = 213).
- [x] **Step 2: Add the 198-snapshot note** to the method-repo bullet: eval-summary.json is "a snapshot sealed at an earlier commit — **198/198** as of that commit; the suite here has since grown to the 211 above." Verified against the method repo's `eval-summary.json` meta block (total 198 = 191 behavioral + 7 schema, source_commit d81f7d9).

### Task 3: Dashboard — About-panel source-code link, red-first [EXECUTED except sw.js]

**Files:**
- Modify: `eval/test_info_disclosures.py` (extend `test_about_panel_lean_keeps_disclosure_and_a11y` — two new checks: `source_code_link_in_about` = `"info.about.sourcecode" in region`, `source_repo_url_present` = `"github.com/Mike-E-Log/gg-tank-watch" in text`)
- Modify: `public/dashboard.html` (i18n key `info.about.sourcecode`; About render line between the Accessibility pill and the AI disclosure; `.info-sourcecode` CSS = 13px legible, mirroring `.info-ai-disclosure`)
- Modify: `public/sw.js:1` (CACHE_NAME v89→v90) + `eval/test_sw_precache.py` + `eval/test_sw_cache_strategy.py` (guards → v90) + `README.md` cache ref (precedent: #58/bea96d3)

- [x] **Step 1: RED** — extended the About guard; `python eval/run_all.py --only test_info_disclosures` → `[FAIL] … source_code_link_in_about: False, source_repo_url_present: False`, exit 1.
- [x] **Step 2: Implement the link** — i18n string (`en:`-only, descriptive, `target="_blank" rel="noopener"` matching `info.roads.defer`) + render line + CSS.
- [x] **Step 3: Flip the SW guards + README ref to v90** (test files + README line edited).
- [ ] **Step 4: Land the 1-line source edit** — `public/sw.js:1` → `var CACHE_NAME = "gg-tank-v90";` (the only file still pinning v89; without it the tree is red 208/211).

### Task 4: Verify green, visual check, commit (no push)

- [ ] **Step 1: GREEN (targeted)** — Run: `python eval/run_all.py --only test_info_disclosures` → all 7 pass, exit 0.
- [ ] **Step 2: GREEN (full, non-quiet, unpiped)** — Run: `python eval/run_all.py --skip integration` → `TOTAL 211/211 (100.0% pass)`, exit 0.
- [ ] **Step 3: Visual check** — serve `public/` (`python -m http.server <port> -d public`), open the Info → About tab, screenshot (Playwright msedge fallback if the Browser pane screenshot channel is still broken): source-code line renders at 13px between the Accessibility pill and the AI disclosure, light + dark.
- [ ] **Step 4: Commit fix 1** — `git add README.md` is NOT possible per-hunk here; commit order instead: (a) this plan file, (b) fix 3 (dashboard + sw + guards + README cache ref + README count notes + screenshot move — see Step 5 note).
- [ ] **Step 5: Commits** — three logical commits on the branch, each message stating the decision (repo convention), `eval/scores.jsonl` left uncommitted (pre-existing dirty state + local run appends):
  1. `docs(plan): land the 2026-07-21 recruiter-audit remaining-fixes plan`
  2. `docs(readme): product shot above the fold + one canonical test-count story (211; 198 = sealed method-repo snapshot; 213 = +2 opt-in Nominatim tests)`
  3. `feat(dashboard): About links the public repo (info.about.sourcecode) + SW v90 — red-first via the About guard`
- [ ] **Step 6: Stop** — no push, no PR; hand back to operator for approval.

## Self-Review

Spec coverage: fix 1 → Task 1; fix 2 → Task 2; fix 3 → Task 3 + 4. Placeholders: none. Type consistency: i18n key `info.about.sourcecode` and CSS class `.info-sourcecode` used identically across Task 3 and the executed edits. Commit split in Task 4 keeps README edits (fixes 1+2) separate from the dashboard change (fix 3); the README v90 cache ref rides with the fix-3 commit since it describes the SW state.
