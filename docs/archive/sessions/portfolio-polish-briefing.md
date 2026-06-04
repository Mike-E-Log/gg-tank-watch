# Workstream Briefing: Portfolio Polish & Repo Hygiene

## Identity
- **Stream name:** portfolio-polish
- **Type:** Deep (start immediately)
- **Orchestrator:** lead session

## Context

GG Tank Watch is an emergency information dashboard for ~50,000 evacuated residents near a chemical tank incident in Garden Grove, CA. It is also an Anthropic Fellows Program portfolio piece demonstrating responsible AI deployment in a safety-critical domain.

The project has shipped 6 PRs (T2-T7), eval is 45/45 green, and HEAD is at `47dc107` on main. The repo needs portfolio-quality documentation and cleanup of untracked orchestration artifacts from previous build sessions.

## File Ownership (exclusive write access)

- `docs/CONTRIBUTING.md` (new file)
- `docs/WCAG_NOTES.md` (new file)
- `.gitignore` (modifications only)

## Cleanup Targets (delete/organize)

- `loop/` directory (untracked build-loop state from previous session)
- `plan/` directory (untracked execution plan artifacts)
- `prompts/` directory (untracked prompt artifacts)
- `C--Users-redacted-OneDrive-Desktop-GG-tank-updates/` (stale path artifact)

## Do-Not-Touch

- `dashboard.html`, `eval/`, `scripts/` (owned by dashboard-eng)
- `CLAUDE.md`, `DESIGN.md` (owned by dashboard-eng or root)
- `a.html`, `d.html`, `p.html` (owned by dashboard-eng)
- `render_safety_briefing.py`, `safety-briefing*` (owned by dashboard-eng)
- `docs/fellowship/` (owned by fellowship-prep)
- Any existing files in `docs/` (read-only reference)

## The Work

### Phase 1: CONTRIBUTING.md
Create a portfolio-quality CONTRIBUTING.md that:
- Explains the conduit posture (amplify official information, no directives)
- References the Code of Conduct at docs/CODE_OF_CONDUCT.md
- Covers the eval harness requirement (45/45 must pass before merge)
- Describes the branch workflow (branch -> PR -> merge, never push main directly)
- Notes the G1 constraint (no machine-translated safety copy)
- Mentions the data pipeline architecture briefly
- Keep it concise -- this is a portfolio piece, not a sprawling contributor guide

### Phase 2: WCAG Accessibility Notes
Create docs/WCAG_NOTES.md documenting:
- Current accessibility status of dashboard.html (color contrast, semantic HTML, ARIA)
- Known gaps and planned improvements
- How the emergency-context design choices (high contrast, large text, simple layout) naturally align with WCAG
- This is for portfolio completeness, not a full audit

### Phase 3: Repo Hygiene
- Delete untracked orchestration artifacts: `loop/`, `plan/`, `prompts/`
- Delete or investigate `C--Users-redacted-OneDrive-Desktop-GG-tank-updates/`
- Update `.gitignore` to prevent these from accumulating again (add `loop/`, `plan/`, `prompts/`)
- Do NOT delete any tracked files
- Do NOT modify `eval/scores.jsonl` (it's modified but that's expected)

### Phase 4: Commit
- Stage only your owned files explicitly (never `git add -A`)
- Use conventional commit format: `docs: add CONTRIBUTING.md and WCAG accessibility notes`
- Separate commit for cleanup: `chore: clean untracked orchestration artifacts`

## Done Criteria

- [ ] `docs/CONTRIBUTING.md` exists and is committed
- [ ] `docs/WCAG_NOTES.md` exists and is committed
- [ ] `loop/`, `plan/`, `prompts/` deleted
- [ ] `.gitignore` updated to exclude orchestration dirs
- [ ] No other files modified

## On Completion

Mark your task as `completed` and SendMessage to the lead with a one-line summary of what you shipped.
