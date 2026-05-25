# Data sync — how `status.json` stays fresh

The dashboard polls `status.json` (incident facts) every ~30s. Something has to
keep that file current. There are two paths; **only the local one is active right now.**

## Active: local refresh on subscription credits

`scripts/refresh_local.py`, run on a contributor's machine that's left on.

- Gathers current facts via `claude -p` with the **OAuth subscription**
  (`ANTHROPIC_API_KEY` unset) + the WebSearch tool — so it bills **subscription
  credits, $0 metered**.
- Runs the existing writer (`scripts/update_status.py`) and commits the refreshed
  `status.json` (`[skip ci]`), which Vercel auto-deploys.
- Model defaults to `sonnet` (cheaper on the shared subscription quota); override
  with `CLAUDE_MODEL`.

Run once:

```bash
python scripts/refresh_local.py            # gather -> write -> commit -> push
python scripts/refresh_local.py --dry-run  # gather -> write status.json only (no git)
```

Keep it running every ~20 min (under the dashboard's 30-min staleness threshold)
while the machine is on. Pick one:

**Windows Task Scheduler (survives terminal close):**
```powershell
$py = (Get-Command python).Source
schtasks /Create /TN "gg-tank-refresh" /SC MINUTE /MO 20 /F `
  /TR "cmd /c cd /d C:\Users\redacted\Desktop\Projects\gg-tank-dashboard && `"$py`" scripts\refresh_local.py"
# remove later:  schtasks /Delete /TN "gg-tank-refresh" /F
```

**Simple loop (dies when the terminal closes):**
```powershell
while ($true) { python scripts\refresh_local.py; Start-Sleep -Seconds 1200 }
```

Trade-off accepted for now: this depends on a machine being on. If it sleeps or
the loop stops, `status.json` simply ages and the dashboard's staleness banner
fires (it never shows fresh-stamped stale data — the gatherer writes nothing on
failure).

## Dormant: metered cloud cron (the "no machine required" path, for later)

`.github/workflows/update-status.yml` does the same thing on GitHub's hosted
runners every 20 min — **no machine required** — but a headless runner can't use
the OAuth subscription, so it bills a **metered `ANTHROPIC_API_KEY`** (~$200-330/mo
at 20-min cadence). The `schedule:` trigger is commented out; `workflow_dispatch`
still works for a manual run.

**To switch to this later:** uncomment the `schedule:` block in that workflow.
The `ANTHROPIC_API_KEY` repo secret is already set, so that's the only change.
Stop the local Task Scheduler job at the same time so the two don't both push.

## Before distribution

Whichever path is active, the writer is not yet hardened per
[`DATA_QUALITY.md`](DATA_QUALITY.md) (corroboration gate, URL-integrity are
prompt-level only). Harden before distributing — see
`distribution-gating-constraints` in project memory.
