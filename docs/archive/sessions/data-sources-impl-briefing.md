# Data Sources Implementation — Expand gather_facts.py with credibility-tiered sources (deep session)

You are running the **data-sources-impl** workstream. 1 other workstream runs concurrently ("ux-pwa-impl" on `dashboard.html`/`manifest.json`/`sw.js`). A third ("son-mai-impl") is queued after ux-pwa-impl. You do NOT touch their files.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `docs/superpowers/plans/2026-05-25-data-source-credibility.md` — **YOUR IMPLEMENTATION PLAN. Follow it task by task.**
4. `scripts/gather_facts.py` — the file you will modify
5. `eval/test_gather_facts.py` — the test file you will modify

## Primary goal

Implement the data source credibility framework: expand `gather_facts.py` with tiered source priorities (including Vietnamese-language media), increase `WEB_SEARCH_MAX_USES` to 14, and write the `docs/SOURCE_CREDIBILITY.md` documentation.

## File ownership

**You OWN (exclusive write access):**
```
scripts/gather_facts.py
eval/test_gather_facts.py
docs/SOURCE_CREDIBILITY.md
```

**DO NOT TOUCH:**
```
dashboard.html                → ux-pwa-impl
manifest.json                 → ux-pwa-impl
sw.js                         → ux-pwa-impl
DESIGN.md                     → son-mai-impl (queued)
scripts/update_status.py      → READ-ONLY
.orchestra/orchestration.json → Orchestrator ONLY
```

## The work

Follow `docs/superpowers/plans/2026-05-25-data-source-credibility.md` exactly, task by task:

### Task 1: Add credibility tiers and expand prompt in gather_facts.py
- Add 3 new tests to `eval/test_gather_facts.py`
- Run tests to verify they fail
- Update `gather_facts.py`: change MAX_USES to 14, add SOURCE_TIERS dict, replace PROMPT with expanded version including Vietnamese sources and credibility guidance
- Run tests to verify they pass
- Run full eval: `python eval/run_all.py --skip integration`
- Commit

### Task 2: Add credibility documentation
- Write `docs/SOURCE_CREDIBILITY.md` with the full framework
- Commit

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- Run `python eval/run_all.py --skip integration` after changes and verify exit code 0
- Follow the plan's exact code blocks — don't improvise different implementations
- Every commit must use explicit file paths in `git add` (never `git add -A` or `git add .`)

## What "done" looks like

- `scripts/gather_facts.py` updated with SOURCE_TIERS, expanded PROMPT, MAX_USES=14
- `eval/test_gather_facts.py` has 3 new passing tests
- `docs/SOURCE_CREDIBILITY.md` written
- All eval tests pass (45+ tests, exit code 0)
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage
