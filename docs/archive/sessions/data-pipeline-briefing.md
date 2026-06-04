# Data Pipeline — Timeline + Community Resources + Map Cleanup (deep session)

You are running the **Data Pipeline** workstream. 3 other workstreams run concurrently ("research" on `docs/sessions/*-research*.md`; "portfolio" on `README.md, docs/`; "dashboard" is QUEUED and will consume your data files). You do NOT touch their files.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `.orchestra/CONTRACTS.md` — cross-cutting contracts including timeline.json schema and community_resources schema. READ ONLY. **Build to these schemas exactly.**
4. `docs/sessions/data-source-audit.md` — the 40+ event timeline source data
5. `config.json` — current config (map points, shelters, etc.)
6. `eval/test_geocoder.py` — tests referencing Magnolia & Ellis, Trask & Harbor
7. `eval/test_safety.py` — tests referencing the same intersections

## Primary goal

Create the data files the dashboard stream needs: `timeline.json` (40+ historical events), updated `config.json` (community resources added, 2 map points removed), and eval test updates.

## File ownership

**You OWN (exclusive write access):**
```
config.json
timeline.json (new)
scripts/
eval/
```

**DO NOT TOUCH:**
```
dashboard.html                               → dashboard (queued)
README.md, docs/AI_CONTROL_ARCHITECTURE.md   → portfolio
docs/sessions/*-research*.md                 → research
.orchestra/CONTRACTS.md                      → Orchestrator ONLY
.orchestra/orchestration.json                → Orchestrator ONLY
```

## The work

### Phase 1 — Create timeline.json

Read `docs/sessions/data-source-audit.md` and extract all events into `timeline.json` following the schema in `.orchestra/CONTRACTS.md` exactly.

For each event:
- Generate a stable `id` (format: `evt-YYYYMMDD-NNN`)
- Convert timestamps to both UTC and local (PDT = UTC-7)
- Assign `day` (1-5) based on date
- Write a concise `title` (one line, max 80 chars)
- Keep `description` from the audit doc (may be longer)
- Verify every `source_url` is a real URL from the audit doc (conduit pattern — no fabricated sources)
- Assign `category` from the fixed set in CONTRACTS.md

Validate:
- Every `source_url` appears in the audit document
- Every `category` is from the approved set
- Timestamps are valid ISO 8601
- No duplicate IDs
- Events are sorted by timestamp ascending

### Phase 2 — Update config.json

1. **Remove map points:** Delete `Magnolia & Ellis` and `Trask & Harbor` from `nearby_intersections` in config.json.

2. **Add community resources:** Add a `community_resources` array to config.json following the schema in CONTRACTS.md. Include at minimum:
   - FEMA Individual Assistance (DisasterAssistance.gov, 1-800-621-3362)
   - OC DA anonymous tip line (714-347-8714)
   - CA AG price gouging hotline (1-800-952-5225)
   - Verify all phone numbers and URLs are real

### Phase 3 — Update eval tests

The orchestrator will route the research stream's verdict on eval test handling. Until then:

**Default action (if no verdict arrives):** Remove the 4 tests that reference the removed intersections:
- `eval/test_geocoder.py`: `test_magnolia_ellis`, `test_trask_harbor` (keep `test_magnolia_talbert` — that intersection is not being removed)
- `eval/test_safety.py`: `test_trask_harbor_distance`, `test_magnolia_ellis_distance`

After removing tests, run `python eval/run_all.py --skip integration` and verify all remaining tests pass.

### Phase 4 — Verify

Run the eval harness: `python eval/run_all.py --skip integration`
- Must exit 0
- Report the test count (should be 48 - removed tests)

Validate timeline.json:
```python
import json
with open('timeline.json') as f:
    data = json.load(f)
print(f"Events: {len(data['events'])}")
print(f"Categories: {set(e['category'] for e in data['events'])}")
print(f"Days: {sorted(set(e['day'] for e in data['events']))}")
```

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- Treat `.orchestra/CONTRACTS.md` as authoritative for schemas; READ it, never write it
- Every source URL in timeline.json must come from docs/sessions/data-source-audit.md — no fabricated sources (conduit pattern, P0-2 provenance integrity)
- Vietnamese text in community_resources uses real Vietnamese (title_vi fields) — but these are NOT safety-critical copy, so machine translation is acceptable for resource titles (they're proper nouns and short labels, not safety directives)
- All phone numbers and URLs must be verified real

## What "done" looks like

- `timeline.json` created with 40+ events matching CONTRACTS.md schema
- `config.json` updated: 2 map points removed, community_resources added
- Eval tests updated (2-4 tests removed depending on verdict)
- `python eval/run_all.py --skip integration` exits 0
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Rendering timeline in dashboard.html → dashboard stream
- Desktop/mobile layout → dashboard stream
- README/docs updates → portfolio stream
- Research/design direction → research stream
- Shared doc updates → Orchestrator

## On completion

1. Mark your task `completed` via `TaskUpdate`
2. `SendMessage` the orchestrator lead with: event count, tests passing/total, files modified
3. The orchestrator reads your transcripts for full visibility — no journal needed
