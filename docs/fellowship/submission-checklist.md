# Submission Checklist — Anthropic Fellows Program

## Application details

- **URL:** https://job-boards.greenhouse.io/anthropic/jobs/5023394008
- **Cohorts:** Rolling admissions, May/July 2026 cohorts
- **Portfolio repo:** github.com/ggtankwatch/gg-tank-dashboard

## Required materials

| Material | Location | Status |
|----------|----------|--------|
| Cover letter | `docs/fellowship/cover-letter-draft.md` | Final (463 words) |
| Evidence summary | `docs/fellowship/evidence-summary.md` | Final |
| Portfolio repo (this repo) | Root of repository | Active |

## Evidence map — which doc demonstrates which principle

| Anthropic Safety Principle | Primary evidence | Supporting evidence |
|----------------------------|-----------------|---------------------|
| **Honesty / AI transparency** | `docs/CODE_OF_CONDUCT.md` (principle 6) | `dashboard.html` disclosure string, `STRINGS.disclosure` |
| **Avoiding harm** | `docs/PRIOR_ART.md` (conduit vs. authority) | `docs/CODE_OF_CONDUCT.md` (principle 2: no directives) |
| **Human oversight** | `docs/CODE_OF_CONDUCT.md` (principle 6) | Pipeline design: human reviews AI summaries pre-publish |
| **Scalable oversight** | `docs/AI_CONTROL_ARCHITECTURE.md` | `eval/` harness (47 tests), `docs/FAILURE_ANALYSIS.md` |
| **Responsible deployment** | `CLAUDE.md` (attorney review gates, noindex) | `docs/LANGUAGE_ACCESS.md` + `eval/test_language_access.py` (G1 gate; VI held pending fluent verification) |
| **Alignment tax = zero** | `docs/PRIOR_ART.md` (section: "Why Option B is correct") | `docs/AI_CONTROL_ARCHITECTURE.md` (closing section) |

## Reviewer entry points

A reviewer evaluating the portfolio should follow this path:

1. **Start:** `CLAUDE.md` — portfolio framing, safety principles table, project thesis
2. **Architecture:** `docs/AI_CONTROL_ARCHITECTURE.md` — how the control layer works, maps safety properties to eval tests (P0-1/P0-2/P0-3 → F1/F2/F4)
3. **Red team:** `docs/FAILURE_ANALYSIS.md` — 12 failure modes, coverage verdicts, honest gaps
4. **Prior art:** `docs/PRIOR_ART.md` — conduit vs. authority pattern, landscape comparison
5. **Tests:** `eval/` — run `python eval/run_all.py --skip integration` to see the harness
6. **Live dashboard:** `dashboard.html` — the actual product residents use

## Pre-submission verification

- [ ] **Repo accessibility.** Verify the repo is public or the application includes access instructions
- [ ] **noindex does not block Greenhouse reviewers.** `noindex` is on `dashboard.html` meta tag and `vercel.json` — this blocks search engines, not direct URL access. Reviewers can still view the deployed site via direct link. Confirm the Vercel deployment URL is included in the application
- [x] **README is adequate.** "For Anthropic reviewers" signpost section added with direct links to CLAUDE.md, AI_CONTROL_ARCHITECTURE, FAILURE_ANALYSIS, PRIOR_ART, and eval/ (2026-05-25)
- [x] **Eval harness runs clean.** `python eval/run_all.py --skip integration` exits 0. Verified 47/47 pass (2026-05-29; was 45/45 on 2026-05-25, +2 for the G1 language-access gate)
- [x] **Cover letter is final.** 463 words, all file references verified to exist (2026-05-25)
- [x] **No secrets in repo.** Grepped for `sk-`, `ANTHROPIC_API_KEY=`, `ghp_`, `gho_` — no secrets in tracked files (2026-05-25)
- [ ] **Attorney review status.** Note current status of Lane B3 (attorney review) in application if asked about deployment timeline
- [ ] **Application form completed.** All required fields filled on Greenhouse form
