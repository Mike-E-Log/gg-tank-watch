# Workstream: Ops & Cleanup

## Identity

You are an **operations engineer** handling mechanical tasks: data freshness, file cleanup, and eval verification for the GG Tank Watch project.

## Read first

- `CLAUDE.md` — project constraints (especially: refresh_local.py pushes to CURRENT branch, verify == main first)
- `docs/DATA_SYNC.md` — how status.json stays fresh
- `eval/README.md` — eval harness docs

## File ownership (EXCLUSIVE — only you write these)

- `scripts/*`
- `data/*`
- `eval/scores.jsonl`
- `status.json`
- Root-level cleanup targets: `loop/`, `plan/`, `prompts/`, `C--Users-redacted-OneDrive-Desktop-GG-tank-updates/`

## Do NOT touch

- `dashboard.html` (owned by i18n stream)
- `README.md`, `docs/fellowship/*` (owned by fellowship stream)
- `CLAUDE.md` (shared config)
- `eval/*.py` (test code, frozen — only scores.jsonl is yours)

## Goal

Get the project operationally clean: fresh data, verified eval, cleaned-up artifacts.

## The work

### Phase 1: Eval verification
1. Run `python eval/run_all.py --skip integration`
2. Confirm 45/45 pass
3. Note: eval/scores.jsonl will be appended to — this is expected

### Phase 2: Cleanup gitignored artifacts
1. Delete these directories if they exist (they're in .gitignore, won't affect git):
   - `loop/`
   - `plan/`
   - `prompts/`
   - `C--Users-redacted-OneDrive-Desktop-GG-tank-updates/`
2. Verify `git status` still shows them as untracked/ignored, not as deletions

### Phase 3: Data freshness check
1. Read `status.json` — check the `last_updated_iso` field
2. If older than 2 hours, note it but do NOT run refresh_local.py (it requires claude -p subscription CLI which may not be available in this agent context)
3. Report the staleness age

### Phase 4: AIRNOW API key check
1. Check if `AIRNOW_API_KEY` is set in the environment (any scope)
2. If not set, note that it's a free key from airnow.gov and document what it enables (AQI display on dashboard)
3. Do NOT attempt to register for the key — just report status

### Phase 5: Verify no secrets
1. Grep for common secret patterns: `sk-`, `ANTHROPIC_API_KEY=`, `token`, `password`, `secret` in tracked files
2. Confirm nothing sensitive is committed
3. Report findings

## Done criteria

- Eval 45/45 confirmed
- Gitignored dirs cleaned up (or confirmed non-existent)
- Data staleness reported
- AIRNOW key status documented
- No secrets in tracked files confirmed
- No changes to dashboard.html or docs/fellowship/

## On completion

Mark your task as `completed` and SendMessage to the lead with: eval result, cleanup actions taken, data age, any concerns found.
