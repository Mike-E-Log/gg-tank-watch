# USAGE — running the dashboard

Operational guide for GG Tank Watch. If you want the project pitch / case study instead, see [`README.md`](README.md).

## TL;DR — what to do right now

1. **Double-click `start_dashboard.bat`.** Starts a local web server on port 8765 AND opens the dashboard in your default browser. Required because Chrome blocks `fetch()` on `file://` URLs — without the server you get "Offline / file missing" forever.
2. **The page auto-refreshes every 30 seconds.** Leave the tab open; you never have to F5.
3. **The map shows the evacuation zone, the GKN Aerospace facility, shelter locations, and live wind direction.** Wind pulled from NOAA station KFUL every 5 min.
4. **Light/dark theme toggle** in the top-right. Defaults to light; preference saved per browser.
5. **A contributor runs the refresh job (`refresh_local.py`) on demand** — roughly every 20–30 min during the active incident — to rewrite `status.json`. When no one is refreshing, the staleness banner fires. See "Long-haul operation" below and [Data sync](README.md#data-sync--how-statusjson-stays-fresh).

To stop the dashboard: close the `cmd` window that the `.bat` opened.

## What you see

- **Hero:** the current-situation summary, the incident severity, and key facts (evacuation status, residents) — the answer to "what's going on," at the top.
- **Map** with the evacuation zone, the GKN Aerospace facility, shelter locations, and live wind direction.
- **Official sources:** routes to ggcity.org/emergency, OCFA, and other authoritative channels — no single source should be your only one.
- **Incident details panels:** tank temp, evac numbers, schools closed.
- **Right sidebar (sticky):** official statements, newest first, with `Newest` / `Recent` badges.
- **Sources** (collapsed): URLs the data came from this tick.
- **Footer:** official-source links (ggcity.org/emergency · 911 · 714-628-7085 · OCFA), the disclaimer, and the Terms link.

## Banners

Each banner has a `?` info icon — hover for the full explanation.

- **🚨 URGENT** (pulsing red, audible beep) — an act-now change. Triggers: evac order toggled (expanded / lifted / reinstated), severity bumped, first injuries reported, or incident officially resolved. Tab title also flashes.
- **📢 UPDATE** (amber, no beep, no pulse) — informational change. Triggers: new official statement was published, or resident count shifted noticeably. Click the banner to jump to the highlighted newest statement in the sidebar.
- **⚠️ Data is stale** — writer hasn't run in >30 min. Likely cause: the refresh job hasn't run.
- **Offline / file missing** — browser couldn't fetch `status.json`. See troubleshooting.

All breaking banners auto-clear 30 min after firing.

## What each file does

| File | Purpose |
|---|---|
| **`start_dashboard.bat`** | **Launcher.** Double-click. Runs `python -m http.server 8765` + opens browser. |
| `dashboard.html` | The dashboard. Light/dark theme, live map, sticky statements sidebar. |
| `status.json` | Current snapshot. Atomic-written by the writer; read by the dashboard. Excluded from git. |
| `config.json` | `zone_status`, refresh intervals, incident metadata, map coords (facility, evac polygon, shelters, weather station). |
| `scripts/update_status.py` | The writer. Reads facts via stdin (JSON), diffs against prev snapshot, atomic-writes `status.json`. |
| `breaking_events.jsonl` | Append-only log of every breaking event. Incident timeline. Excluded from git. |
| `updates.log` | Append-only writer activity log. Debugging + uptime. Excluded from git. |
| `go_bag.md` | Pre-pack evacuation checklist. Print and tape to door. |
| `BRIEF_2026-05-24.md` | Source-cited factual brief on the incident. |
| `PERSONAL_UPDATE_2026-05-24.md` | Drafts for personal status updates to family / manager. |
| `docs/SPEC.md` | Full SPEC + autoplan review trail (CEO/Design/Eng phases). |
| `DESIGN_LOG.md` | Structured log of every design decision with rubric scoring. |
| `CHANGELOG.md` | Iteration-by-iteration changes. |
| `eval/` | Behavioral + schema test suite. |

## Manual run (force an update right now)

```powershell
cd gg-tank-dashboard   # the repo root
'{"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": false, "status_headline": "Manual refresh"}' | python scripts\update_status.py
```

Missing fields keep their previous values.

Check the output:
```powershell
type status.json | findstr last_updated_iso
type updates.log | Select-Object -Last 5
```

## Pin as a Chrome app (standalone window)

1. Open the dashboard in Chrome
2. ⋮ menu → **Cast, save, and share** → **Install page as app**
3. Pick a name like "GG Tank Dashboard"
4. Chrome creates a standalone-window app with its own taskbar icon.

## Long-haul operation (after Claude Code session ends)

The active refresh path (`refresh_local.py` — see [Data sync](README.md#data-sync--how-statusjson-stays-fresh)) runs on a contributor's machine on demand. For unattended long-haul use, set up Windows Task Scheduler:

1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily, every 30 minutes
3. Action: Start a program
   - Program: `python`
   - Arguments: `"<your-clone-path>\gg-tank-dashboard\scripts\update_status.py"`
   - Start in: `<your-clone-path>\gg-tank-dashboard`
4. **But:** without WebSearch (only the `refresh_local.py` path has it), the script needs facts piped to stdin. Either:
   - Curate `facts.json` once a day with what you've read in news, then schedule:
     ```powershell
     Get-Content C:\path\to\facts.json | python scripts\update_status.py
     ```
   - Or accept that the dashboard shows the last successful tick's data until you re-run manually.

## Troubleshooting

**Dashboard says "Initializing…" forever.** First writer run hasn't happened yet (run the manual command above), OR you opened `dashboard.html` directly instead of via `start_dashboard.bat` — Chrome blocks `fetch()` on `file://`. Use the .bat.

**Dashboard says "Offline / file missing".** Same root cause — use `start_dashboard.bat`.

**Map gray / doesn't appear.** Vector tiles load from OpenFreeMap — needs internet. The MapLibre library itself is self-hosted and service-worker-cached, so it survives offline once cached. NOAA wind also needs internet.

**Wind shows fallback (W, 5 mph).** NOAA API unreachable or station KFUL had no current observation. Falls back to cached localStorage value, then to a SoCal prevailing-wind default. Retries every 5 min.

**Staleness banner is showing.** Writer hasn't run in >30 min. Check that the refresh job is running.

**False UPDATE fired on a new statement.** Expected behavior — any genuinely new statement (hash not seen before) fires an info-level UPDATE. To suppress without changing logic: edit `status.json`, set `"breaking": false` and `"breaking_reason": null`, save, refresh.

**The writer crashed (no `updates.log` entry on last tick).** Check `updates.log` for traceback. Likely: OneDrive file lock (resolves on next tick), Python syntax error from manual edit, or disk full. The dashboard's staleness banner is the only signal.

## Running the eval suite

See [`eval/README.md`](eval/README.md). TL;DR:

```powershell
# from the repo root
python eval/run_all.py
```

Appends scores to `eval/scores.jsonl`. Prints a scorecard. Exit code reflects overall pass/fail.
