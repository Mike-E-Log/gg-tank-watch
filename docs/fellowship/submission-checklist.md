# Submission Checklist — Anthropic Fellows Program

## Application details

- **URL:** https://job-boards.greenhouse.io/anthropic/jobs/5023394008
- **Cohorts:** Rolling admissions, May/July 2026 cohorts
- **Portfolio repo:** github.com/ggtankwatch/gg-tank-dashboard

## Required materials

| Material | Location | Status |
|----------|----------|--------|
| Cover letter | `docs/fellowship/cover-letter-draft.md` | Draft |
| Evidence summary | `docs/fellowship/evidence-summary.md` | Draft |
| Portfolio repo (this repo) | Root of repository | Active |

## Evidence map — which doc demonstrates which principle

| Anthropic Safety Principle | Primary evidence | Supporting evidence |
|----------------------------|-----------------|---------------------|
| **Honesty / AI transparency** | `docs/CODE_OF_CONDUCT.md` (principle 6) | `dashboard.html` disclosure string, `STRINGS.disclosure` |
| **Avoiding harm** | `docs/PRIOR_ART.md` (conduit vs. authority) | `docs/CODE_OF_CONDUCT.md` (principle 2: no directives) |
| **Human oversight** | `docs/CODE_OF_CONDUCT.md` (principle 6) | Pipeline design: human reviews AI summaries pre-publish |
| **Scalable oversight** | `docs/AI_CONTROL_ARCHITECTURE.md` | `eval/` harness (45 tests), `docs/FAILURE_ANALYSIS.md` |
| **Responsible deployment** | `CLAUDE.md` (attorney review gates, noindex) | `docs/LANGUAGE_ACCESS.md` (G1 native-verification) |
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
- [ ] **README is adequate.** README should orient a reviewer: what this is, why it exists, how to verify the eval harness, link to the architecture docs
- [ ] **Eval harness runs clean.** `python eval/run_all.py --skip integration` exits 0. Run before submission
- [ ] **Cover letter is final.** Review `docs/fellowship/cover-letter-draft.md` for tone, length (one page), and accuracy of file references
- [ ] **No secrets in repo.** No API keys, tokens, or credentials committed
- [ ] **Attorney review status.** Note current status of Lane B3 (attorney review) in application if asked about deployment timeline
- [ ] **Application form completed.** All required fields filled on Greenhouse form
