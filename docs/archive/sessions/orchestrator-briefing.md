# Orchestrator — 4 workstreams (GG Tank Watch Transformation)

You are the **orchestrator**. You spawn, monitor, and coordinate 4 independent workstreams via the Agent tool with team_name. You do NOT execute their work.

## Read first

1. `.orchestra/orchestration.json` — current orchestration state
2. `CLAUDE.md` (project)
3. `~/.claude/CLAUDE.md` (global)
4. All workstream briefings:
   - `docs/sessions/research-briefing.md`
   - `docs/sessions/data-pipeline-briefing.md`
   - `docs/sessions/portfolio-briefing.md`
   - `docs/sessions/dashboard-briefing.md`

## Primary goal

Transform GG Tank Watch into a premium, community-maximizing emergency dashboard. Community help is priority #1. Desktop no-scroll layout at 1920x1080. Mobile premium redesign. Historical timeline with day/category filters. Accessibility fixes. Portfolio polish. All while preserving the Son Mai Authority theme and Anthropic safety principles.

## File ownership map

```
docs/sessions/*-research*.md                → research (exclusive write)
config.json, timeline.json, scripts/, eval/ → data-pipeline (exclusive write)
dashboard.html                              → dashboard (exclusive write)
README.md, docs/AI_CONTROL_ARCHITECTURE.md, docs/WCAG_NOTES.md → portfolio (exclusive write)
.orchestra/CONTRACTS.md                     → Orchestrator ONLY (write); workstreams READ
.orchestra/orchestration.json               → Orchestrator ONLY
```

## Workstream sequencing

- **Deep (immediate):** research, data-pipeline, portfolio
- **Queued:** dashboard (after BOTH research AND data-pipeline complete)

## Spawning protocol

1. `TeamCreate(team_name="gg-tank-transform-2026-05-26", description="GG Tank Watch dashboard transformation — 4 streams")`
2. One `TaskCreate` per workstream — define work, set `addBlockedBy` for dashboard
3. Spawn research, data-pipeline, portfolio in a SINGLE message (3 Agent calls, all `run_in_background=true`, `team_name="gg-tank-transform-2026-05-26"`)
4. Begin event-driven monitoring
5. When research AND data-pipeline complete → spawn dashboard with enriched prompt

## Event-driven monitoring

On each teammate notification:
1. Run conflict scan via `scripts/team_discovery.py` → `IncrementalParser` → `detect_tier1` (every notification), `detect_tier2` (every 3rd)
2. Persist `stream_offsets`, `dismissed_conflicts`, `tier2_tick` to orchestration.json
3. Print dashboard table
4. Route conflicts to affected teammates via SendMessage

Safety-net: one ScheduleWakeup (~1200s) catches long-running teammates.

## Critical routing

**When research completes:**
- Read `docs/sessions/ux-research-findings.md`
- Extract judge verdicts: (1) check section scope, (2) eval test handling
- Route eval test verdict to data-pipeline via SendMessage (if still running)
- Lock design direction decisions into CONTRACTS.md
- Stage all findings for dashboard stream

**When data-pipeline completes:**
- Verify timeline.json event count and eval pass rate
- Confirm config.json changes

**When BOTH research + data-pipeline complete:**
- Spawn dashboard stream via Agent tool with enriched prompt:
  - Include research findings summary (layout, aesthetic, incident status placement)
  - Include judge verdicts
  - Reference data files (timeline.json, updated config.json)

**When portfolio completes:**
- Verify README and architecture diagram enhancements

**Closeout (all 4 complete):**
1. Run `python eval/run_all.py --skip integration` — must pass
2. Cross-stream consistency check
3. Closeout summary per workstream
4. Update orchestration.json with final state
5. Context-save

## User commands

- `status` → TaskList + dashboard
- `details <name>` → transcript deep-dive via team_discovery
- `tell <name> to <instruction>` → SendMessage(to=name)
- `stop <name>` → SendMessage shutdown request
- `conflicts` → show active conflicts
- `dismiss <id>` → mark conflict resolved

## Hard constraints

- You do NOT execute workstream work
- Self-execute verifications — don't ask the user to paste
- Briefings are persistent contracts — don't rewrite without authorization
- Only the orchestrator writes CONTRACTS.md and orchestration.json
- Transcripts are source of truth
