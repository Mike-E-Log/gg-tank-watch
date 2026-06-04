# Portfolio Polish — Architecture Diagram + Eval Visibility + Perf Docs (deep session)

You are running the **Portfolio** workstream. 3 other workstreams run concurrently ("research" on research docs; "data-pipeline" on `config.json, timeline.json, scripts/, eval/`; "dashboard" is QUEUED). You do NOT touch their files.

## Read first, in this order

1. `CLAUDE.md` (project — especially the "Portfolio Framing" and "Anthropic Safety Principles" sections)
2. `~/.claude/CLAUDE.md` (global)
3. `.orchestra/CONTRACTS.md` — READ ONLY
4. `docs/AI_CONTROL_ARCHITECTURE.md` — the control architecture doc (you'll enhance this)
5. `docs/FAILURE_ANALYSIS.md` — the red-team report
6. `docs/fellowship/evidence-summary.md` — how principles map to evidence
7. `docs/fellowship/submission-checklist.md` — what's done, what's pending
8. `README.md` — current README
9. `docs/WCAG_NOTES.md` — accessibility gap list

## Primary goal

Make the portfolio evidence immediately visible and impressive to reviewers (Anthropic Fellows Program, general employers). The safety architecture should be scannable in 30 seconds, not buried in prose.

## File ownership

**You OWN (exclusive write access):**
```
README.md
docs/AI_CONTROL_ARCHITECTURE.md
docs/WCAG_NOTES.md
```

**DO NOT TOUCH:**
```
dashboard.html                    → dashboard (queued)
config.json, timeline.json        → data-pipeline
scripts/, eval/                   → data-pipeline
docs/sessions/*-research*.md      → research
docs/fellowship/*                 → READ ONLY (already final)
.orchestra/CONTRACTS.md           → Orchestrator ONLY
.orchestra/orchestration.json     → Orchestrator ONLY
```

## The work

### Phase 1 — Architecture diagram

Add a visual architecture diagram to `docs/AI_CONTROL_ARCHITECTURE.md`. Use ASCII/text-based diagram (Mermaid syntax in a fenced code block) showing:

```
gather_facts.py (LLM + web search)
    │
    ▼
update_status.py ← CONTROL LAYER
    │               ├── P0-1: Corroboration gate
    │               ├── P0-2: Source/URL integrity
    │               ├── P0-3: Freshness honesty
    │               └── P1-1: Date sanity
    ▼
status.json → dashboard.html
                ├── Staleness banner
                ├── Source attribution
                └── AI disclosure
```

The diagram should make the control-layer architecture immediately scannable. Show:
- Data flow direction
- Where the LLM's authority ends (the chokepoint)
- What each control prevents
- The asymmetric gating principle visually

### Phase 2 — Eval visibility in README

Update `README.md` to make the eval harness more visible:

1. Add a "Safety Architecture" section near the top with the diagram (or a link to it)
2. Add a quick-start for running the eval: `python eval/run_all.py --skip integration`
3. Show what the eval output looks like (test count, categories, pass/fail)
4. Link to `docs/AI_CONTROL_ARCHITECTURE.md` and `docs/FAILURE_ANALYSIS.md`

Don't rewrite the entire README — add to the "For Anthropic reviewers" section that already exists. Make it so a reviewer can understand the safety story in 30 seconds.

### Phase 3 — Performance documentation

Add a brief performance section to README.md:
- First paint: ~500ms on 3G (measured from current single-file HTML)
- No framework overhead (zero JS dependencies)
- PWA with service worker for offline resilience
- Single HTTP request for initial load

This is a legitimate engineering achievement that the README should highlight. A single-file HTML app that beats most React apps on first paint, serving a safety-critical audience with poor connectivity.

### Phase 4 — Update WCAG_NOTES.md

Update the "Planned improvements" section to reflect that the dashboard stream will address the known gaps (focus styles, main landmark, skip-nav, form labels). Mark them as "in progress" rather than "planned."

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- Treat `.orchestra/CONTRACTS.md` as authoritative; READ it, never write it
- Don't modify `docs/fellowship/*` — those are final
- Don't overwrite existing README content — ADD to it
- Diagrams must be text-based (Mermaid or ASCII) — no external image files
- All claims must be verifiable (don't claim test counts without checking)

## What "done" looks like

- `docs/AI_CONTROL_ARCHITECTURE.md` has a scannable visual diagram
- `README.md` has enhanced safety/eval/performance sections
- `docs/WCAG_NOTES.md` updated with "in progress" status
- All existing content preserved (additions, not rewrites)
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Dashboard HTML/CSS/JS changes → dashboard stream
- Data pipeline files → data-pipeline stream
- Research → research stream
- Fellowship application materials → already final, READ ONLY

## On completion

1. Mark your task `completed` via `TaskUpdate`
2. `SendMessage` the orchestrator lead with: files modified, what was added
3. The orchestrator reads your transcripts for full visibility — no journal needed
