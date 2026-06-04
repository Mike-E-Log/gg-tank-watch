# Workstream Briefing: Dashboard Engineering

## Identity
- **Stream name:** dashboard-eng
- **Type:** Deep (start immediately)
- **Orchestrator:** lead session

## Context

GG Tank Watch is an emergency information dashboard served as a single static HTML file (`dashboard.html`) deployed to Vercel. The project has a design system documented in `DESIGN.md` (aesthetic: "Calm Authority / Refined Utilitarian", mobile-first, emergency context). There are variant HTML files (a.html, d.html, p.html) that appear to be experimental dashboard versions that need resolution. The eval harness is 45/45 green and must stay that way.

## File Ownership (exclusive write access)

- `dashboard.html`
- `DESIGN.md`
- `render_safety_briefing.py`
- `safety-briefing-philosophy.md`
- `safety-briefing.png`
- `a.html`, `d.html`, `p.html`
- `eval/` directory

## Do-Not-Touch

- `docs/` (all files -- owned by other streams)
- `scripts/` (data pipeline -- no changes needed)
- `CLAUDE.md`
- `.gitignore`
- `data/` directory

## The Work

### Phase 1: Assess Variant Files
- Read `a.html`, `d.html`, `p.html` and compare against `dashboard.html`
- Determine: are these older drafts, experimental variants, or generated artifacts?
- Decision: delete if they're stale duplicates, or extract any useful improvements into dashboard.html first
- If deleting, commit: `chore: remove stale dashboard variant files`

### Phase 2: Design System Application
- Read `DESIGN.md` for the design system specification
- Read `dashboard.html` current state
- Apply design system improvements to dashboard.html:
  - Typography (font stack, sizes, weights per DESIGN.md)
  - Color palette (thermal-atmospheric register if specified)
  - Spacing and layout consistency
  - Mobile responsiveness refinements
- Keep changes conservative -- this is a live emergency dashboard, not a redesign
- Maintain all existing functionality (map, stats, alerts, official sources panel, AI disclosure)

### Phase 3: Safety Briefing Assessment
- Read `render_safety_briefing.py` and `safety-briefing-philosophy.md`
- Assess whether the safety briefing visualization is ready for integration or still experimental
- If ready: integrate into the dashboard or document how it connects
- If experimental: document current state and what's needed to ship it
- Do NOT break existing dashboard functionality for an experimental feature

### Phase 4: Eval Verification
- Run `python eval/run_all.py --skip integration` and verify 45/45 pass
- If any design changes broke tests, fix the tests or revert the changes
- If there are obvious gaps in eval coverage related to new features, add tests
- Do NOT use `--quiet` flag (it suppresses [FAIL] lines)

### Phase 5: Commit
- Stage only your owned files explicitly (never `git add -A`)
- Separate commits for logical units:
  - `chore: remove stale dashboard variant files` (if applicable)
  - `feat(ui): apply design system to dashboard` (if design changes made)
  - Any other logical commits
- Verify eval passes after each commit

## Constraints

- **No new dependencies** without approval
- **No directives** -- never tell anyone to evacuate or take action (conduit posture)
- **Eval must stay 45/45 green** at every commit
- **Conservative changes** -- this serves real evacuated residents

## Done Criteria

- [ ] Variant files (a.html, d.html, p.html) resolved (deleted or consolidated)
- [ ] Design system improvements applied to dashboard.html (if DESIGN.md specifies actionable changes)
- [ ] Safety briefing status documented or integrated
- [ ] Eval: 45/45 green after all changes
- [ ] All changes committed with conventional commit messages

## On Completion

Mark your task as `completed` and SendMessage to the lead with a one-line summary of what you shipped and the eval score.
