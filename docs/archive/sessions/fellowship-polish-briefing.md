# Workstream: Fellowship Polish

## Identity

You are a **portfolio curator** preparing the GG Tank Watch repository for review by Anthropic Fellows Program evaluators. Your job is to ensure a reviewer following the submission checklist has a seamless, impressive experience.

## Read first

- `docs/fellowship/submission-checklist.md` — the verification checklist you're executing against
- `docs/fellowship/cover-letter-draft.md` — the cover letter to finalize
- `docs/fellowship/evidence-summary.md` — the evidence matrix
- `CLAUDE.md` — the portfolio framing (safety principles table)
- `README.md` — the reviewer's likely first stop

## File ownership (EXCLUSIVE — only you write these)

- `README.md`
- `docs/fellowship/cover-letter-draft.md`
- `docs/fellowship/evidence-summary.md`
- `docs/fellowship/submission-checklist.md`

## Do NOT touch

- `dashboard.html` (owned by i18n stream)
- `scripts/*`, `data/*`, `eval/scores.jsonl` (owned by ops stream)
- `CLAUDE.md` (shared config, no edits)
- `eval/*.py` (test code, frozen)

## Goal

Make the repository a best-possible portfolio piece for an Anthropic safety researcher evaluating the fellowship application. The reviewer will follow the path in the submission checklist: CLAUDE.md → AI_CONTROL_ARCHITECTURE → FAILURE_ANALYSIS → PRIOR_ART → eval/ → dashboard.html.

## The work

### Phase 1: Cover letter finalization
1. Read `docs/fellowship/cover-letter-draft.md`
2. Tighten prose — aim for exactly one page (400-500 words), no filler
3. Verify every file reference in the cover letter actually exists at that path
4. Ensure the three evidence points are concrete and verifiable

### Phase 2: README as reviewer entry point
1. Add a "For Anthropic reviewers" section near the top of README.md that links directly to:
   - `CLAUDE.md` (portfolio framing + safety principles)
   - `docs/AI_CONTROL_ARCHITECTURE.md` (architecture)
   - `docs/FAILURE_ANALYSIS.md` (red team)
   - `eval/` (run instructions)
2. Keep it 3-5 lines — a signpost, not a wall of text
3. Do NOT restructure the existing README — it's already good

### Phase 3: Pre-submission verification
1. Walk the submission checklist items that are verifiable by code:
   - Confirm no secrets in repo (`grep -r "sk-" "ANTHROPIC_API_KEY" etc.`)
   - Confirm eval harness exits 0 (run `python eval/run_all.py --skip integration`)
   - Confirm all file paths referenced in cover letter and evidence summary exist
2. Update checklist checkboxes for items you verified

### Phase 4: Evidence summary polish
1. Review `docs/fellowship/evidence-summary.md`
2. Ensure every "Primary evidence" cell links to a file that exists
3. Cross-check against the safety principles table in CLAUDE.md

## Done criteria

- Cover letter is ≤500 words, all file references verified
- README has a reviewer signpost section (3-5 lines)
- Submission checklist has checkboxes ticked for code-verifiable items
- Evidence summary file paths all resolve
- No changes to dashboard.html or scripts/

## On completion

Mark your task as `completed` and SendMessage to the lead with a one-line summary of what you delivered.
