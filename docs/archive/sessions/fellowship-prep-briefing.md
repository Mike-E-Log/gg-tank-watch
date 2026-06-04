# Workstream Briefing: Fellowship Application Prep

## Identity
- **Stream name:** fellowship-prep
- **Type:** Deep (start immediately)
- **Orchestrator:** lead session

## Context

GG Tank Watch is an Anthropic Fellows Program portfolio piece. The thesis: responsible AI and helpful AI are the same lane. The project serves ~50,000 evacuated residents during a real chemical emergency by amplifying official information, and every design choice demonstrates an Anthropic safety principle in production.

The /center-reorient diagnostic from the previous session was clear: the fellowship application is the highest-leverage action, and more engineering without submitting is build-theatre.

Application URL: https://job-boards.greenhouse.io/anthropic/jobs/5023394008

## File Ownership (exclusive write access)

- `docs/fellowship/` directory (all files within)

## Read-Only References (do NOT modify)

- `CLAUDE.md` -- contains the portfolio framing, safety principles table, and project thesis
- `docs/AI_CONTROL_ARCHITECTURE.md` -- maps safety properties to eval tests (P0-1/P0-2/P0-3 to F1/F2/F4)
- `docs/FAILURE_ANALYSIS.md` -- red-teams all 12 failure modes
- `docs/PRIOR_ART.md` -- conduit vs authority pattern, prior art landscape
- `docs/CODE_OF_CONDUCT.md` -- 8 editorial principles defining conduit posture
- `docs/LANGUAGE_ACCESS.md` -- G1 native-verification framework
- `eval/` directory -- 45-test behavioral eval harness

## Do-Not-Touch

- Everything outside `docs/fellowship/`

## The Work

### Phase 1: Cover Letter Draft
Create `docs/fellowship/cover-letter-draft.md`:
- One page maximum
- Opening: connect scalable oversight + AI control (Anthropic's stated research priorities) to this project as a worked example
- Body: three concrete evidence points drawn from the portfolio docs:
  1. Scalable oversight applied to a consumer-facing AI system (eval harness with 45 behavioral tests catching drift from safety contract)
  2. AI control in deployment (system cannot exceed its authority, enforced by code structure + eval, not prompting alone)
  3. Empirical safety thinking (every safety property has a test that fails before the property is violated)
- Closing: why this matters -- responsible AI deployment is not theoretical, it's engineering discipline
- Tone: direct, evidence-based, no corporate filler. Show, don't claim.
- Reference specific files/tests by name so a reviewer can verify

### Phase 2: Submission Checklist
Create `docs/fellowship/submission-checklist.md`:
- Application URL and any known deadlines (rolling, May/July 2026 cohorts)
- Required materials and where each lives in this repo
- Evidence map: which doc demonstrates which Anthropic safety principle
- Reviewer entry points: "Start here" pointers (CLAUDE.md -> AI_CONTROL_ARCHITECTURE.md -> eval/)
- Pre-submission verification items (repo is public/accessible, noindex doesn't block Greenhouse reviewers, README is adequate)

### Phase 3: Evidence Summary
Create `docs/fellowship/evidence-summary.md`:
- A one-page matrix mapping each Anthropic safety principle to its implementation + evidence in this repo
- Columns: Principle | Implementation | Evidence File | Key Test
- Cover: Honesty/AI transparency, Avoiding harm, Human oversight, Scalable oversight, Responsible deployment, Alignment tax = zero
- This is the "cheat sheet" a reviewer would want

## Done Criteria

- [ ] `docs/fellowship/cover-letter-draft.md` -- one page, evidence-based, references specific files
- [ ] `docs/fellowship/submission-checklist.md` -- complete with evidence map and reviewer entry points
- [ ] `docs/fellowship/evidence-summary.md` -- principle-to-evidence matrix
- [ ] All files committed with: `docs: add fellowship application prep materials`

## On Completion

Mark your task as `completed` and SendMessage to the lead with a one-line summary of what you produced.
