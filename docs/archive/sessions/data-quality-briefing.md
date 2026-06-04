# Data-Pipeline Quality Spec — distribution-readiness (deep session)

You are running the **Data-Quality** workstream. Other workstreams run concurrently (Legal → `docs/LEGAL.md`, Marketing → `docs/DISTRIBUTION.md`, News-UX → `docs/NEWS_UX_SPEC.md`). You do NOT touch their files. You own ONE deliverable: `docs/DATA_QUALITY.md` — a **hardening + eval-test design spec**, not code.

## Project context (self-contained)

`gg-tank-dashboard` is an **unofficial, volunteer-built, free** single-page dashboard for the **Garden Grove, CA methyl-methacrylate chemical-tank incident** (GKN Aerospace, 12122 Western Ave; began 2026-05-21; ~50,000 evacuated). It is a static page on Vercel that polls `status.json` — the live incident facts. Those facts are produced by a **cloud data-sync pipeline** (decided via cross-vendor judging, runs with zero dependence on any volunteer's computer):

```
GitHub Actions cron (*/20)
  → scripts/gather_facts.py   (calls Anthropic Messages API web_search server tool;
                               emits a facts JSON to stdout; exits non-zero + prints
                               NOTHING on failure, so status.json goes visibly STALE
                               rather than being fresh-stamped with garbage)
  → scripts/update_status.py  (reads facts on stdin; writes status.json with
                               severity hysteresis + breaking-event detection;
                               appends breaking_events.jsonl; ntfy.sh breaking hook)
  → commits status.json [skip ci] → Vercel auto-deploys
```

**Branch note (IMPORTANT):** You are on branch `docs/distribution-readiness`. On THIS branch, `scripts/` contains only `update_status.py`. `scripts/gather_facts.py` and the workflow live on branch `feat/data-sync`. To read them WITHOUT switching branches, use:
```
git show feat/data-sync:scripts/gather_facts.py
git show feat/data-sync:.github/workflows/update-status.yml
git show feat/data-sync:.gitignore
```
This is why you produce a **spec**, not code edits: the pipeline code lives on a different branch and will be hardened there later. Do not switch branches; do not edit the scripts.

## Read first (READ-ONLY)
1. `~/.claude/CLAUDE.md` (global)
2. This briefing
3. `scripts/update_status.py` (present on this branch) — the writer: severity hysteresis, breaking detection, the exact `status.json` schema it emits, the stdin facts schema it expects.
4. `git show feat/data-sync:scripts/gather_facts.py` — the gatherer: web_search call, `extract_json()`, citation→sources backfill, failure behavior.
5. `eval/` — existing tests: `test_geocoder.py`, `test_safety.py`, `test_schema.py`, `test_writer.py`, `run_all.py`, `fixtures/`, `rubrics/`. Study what's already covered so your test design EXTENDS rather than duplicates.
6. `docs/SPEC.md` — product intent and the data contract.

## Primary goal
Produce `docs/DATA_QUALITY.md`: a prioritized hardening plan for the gather→writer pipeline PLUS an eval-test design that raises confidence the live data is accurate, fresh, and never silently wrong. Implementation lands later on `feat/data-sync`; you design what to build and how to test it.

## The work — cover at minimum
1. **Failure-mode map.** Enumerate how the pipeline can produce bad/misleading `status.json`: hallucinated facts, fabricated sources/URLs/dates, stale-but-fresh-stamped data, severity miscompute (esp. the known partial-facts bug — partial facts must NOT recompute severity from zeros, see commit history), web_search returning nothing, citation parse failures, schema drift, cron silently not running, commit/deploy failures. For each: likelihood, user-visible harm, current mitigation (if any), gap.
2. **Hardening recommendations**, prioritized (P0 safety-critical → P2 nice-to-have). Concrete and minimal — match the existing vanilla-Python-stdlib + small-diff style. Examples to evaluate (accept/reject with reasoning, don't just list): source-allowlist or credibility scoring; URL/date sanity validation; a freshness SLA + stale banner contract with the frontend; severity-change guardrails; web_search result-count floor; structured logging for the Actions run; a dead-man's-switch if the cron stops committing.
3. **Eval-test design.** Specify NEW tests (and fixtures) to add under `eval/`, extending the existing harness. For each: what it asserts, the fixture it needs, pass/fail criteria. Cover: no-fabrication checks, freshness/staleness handling, severity hysteresis + the partial-facts-zero bug as a regression test, schema conformance, citation/source integrity, graceful failure (non-zero exit prints nothing). Distinguish deterministic unit tests from any LLM-output evals (and how to keep the latter cheap/stable).
4. **Data-freshness contract.** Define the precise freshness signal the frontend should trust (timestamp field, max-age, what "stale" means) so News-UX's stale treatment and this pipeline agree. (Flag this as a cross-stream handshake; the orchestrator routes it.)
5. **CI integration.** How the eval suite should gate the data-sync workflow / a PR merging `feat/data-sync` → `main` — what must be green before the paid cron is allowed to write production.

## What "done" looks like
- `docs/DATA_QUALITY.md` exists with: failure-mode map (table), prioritized hardening plan (P0–P2 with rationale), eval-test design (named tests + fixtures + assertions), the freshness contract, and CI gating recommendation, plus an "open questions for the user" list.
- `.orchestra/data-quality/status.json` = `{ "phase": "complete", "progress": 100, ... }`
- `.orchestra/data-quality/log.md` has a final summary.

## Hard constraints (NON-NEGOTIABLE)
- **DO NOT edit code.** No changes to `scripts/`, `eval/`, `.github/`, or any pipeline file. You design; implementation is later, on `feat/data-sync`.
- Do NOT switch branches. Read other-branch files via `git show feat/data-sync:<path>`.
- DO NOT touch any file except `docs/DATA_QUALITY.md` and `.orchestra/data-quality/*`. Do NOT edit `docs/LEGAL.md`, `docs/DISTRIBUTION.md`, `docs/NEWS_UX_SPEC.md`, or `.orchestra/STATE.json`.
- Archive/data integrity is paramount: your anti-fabrication tests must be designed so they would actually CATCH invented sources/URLs/dates — that is the single highest-value safety property here.
- Match the project's minimal, dependency-light style (vanilla Python stdlib; no new deps without flagging them as an open question).
- Work autonomously — do NOT block on user input.
- Self-execute; do not ask the user to paste commands.
- Do NOT run `git commit` or `git push` — the orchestrator commits your output.

## Out of scope
- Implementing fixes or tests (later, on `feat/data-sync`). You SPEC them.
- Frontend rendering of freshness → News-UX stream (you define the contract; they consume it).

## Open questions to flag, NOT resolve
- Whether to add any new dependency (e.g., a source-reputation list) vs. staying stdlib-only.
- The exact cron cadence vs. API cost tradeoff at relaunch.

---

## Wiki Write Protocol
Maintain two files in `.orchestra/data-quality/` throughout:

**status.json** — update at every phase transition:
```json
{ "phase": "<current phase>", "progress": 0, "blockers": [], "last_action": "<one line>", "files_touched": ["docs/DATA_QUALITY.md"], "timestamp": "<ISO8601 UTC>" }
```
**log.md** — append after each significant action (`## HH:MM — <phase>` + bullets). Write a final summary entry when done.
