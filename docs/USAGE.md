# USAGE: viewing the dashboard

Operational guide for GG Tank Watch. For the project pitch / case study, see [`README.md`](../README.md).

> **This is a frozen historical archive.** The May 2026 Garden Grove tank emergency resolved on **May 26, 2026**, and the dashboard now shows a static snapshot from that date. It does **not** auto-refresh, wind direction is **not** live (the wind indicator was removed), and the refresh job (`scripts/refresh_local.py`) is **retired**; it exits with an `ARCHIVED` error if run. This guide covers (1) how to view the frozen archive today and (2) how the pipeline operated during the incident, kept for reference.

## View the live archive (hosted)

The frozen archive is hosted at **[ggtankwatch.org](https://ggtankwatch.org)**. Open it directly, nothing to install. It is intentionally `noindex` (not listed in search engines); the direct link works.

## View the frozen archive locally

1. **Double-click `scripts\start_dashboard.bat`** (or, from the repo root, run `python -m http.server 8000 -d public` and open `http://127.0.0.1:8000/dashboard.html`). A local server is required because browsers block `fetch()` on `file://` URLs; without it the page shows "Offline / file missing".
2. The page loads the **frozen snapshot** (`status.json`, as of the May 26, 2026 all-clear). There is no polling and nothing to refresh.
3. **Light / dark theme toggle** sits in the top-right; the preference is saved per browser.

To stop the local server, close the `cmd` window the `.bat` opened.

## What you see

- **Hero:** the resolved-incident summary and key facts (final evacuation status, residents) as of the all-clear.
- **Map:** the former evacuation zone ("Former evac area"), the GKN Aerospace facility, and former shelter locations. There is no wind indicator; it was removed (a single NOAA station was wrong often enough to be a hazard on a no-directives tool).
- **Official sources:** links to ggcity.org/emergency, OCFA, and other authoritative channels: officials first, the conduit principle.
- **News (Coverage Archive):** a date-anchored record of how the incident was reported, newest first (the **Official** filter shows the official statements on their own).
- **Info tab:** Summary · Officials · Resources · About, including the persistent AI-assistance disclosure.

## Running the eval suite

See [`eval/README.md`](eval/README.md). From the repo root:

```powershell
python eval/run_all.py --skip integration
```

It appends scores to `eval/scores.jsonl`, prints a scorecard, and the exit code reflects pass / fail. Don't pass `--quiet`; it suppresses the `[FAIL]` lines.

---

## Historical: how the pipeline ran during the incident

> Kept for reference. **None of this is active in the frozen archive**: the dashboard no longer polls, the wind fetch was removed, and `refresh_local.py` is retired. See [`docs/DATA_SYNC.md`](docs/DATA_SYNC.md) and [Architecture](README.md#architecture-the-retired-pipeline) for the full design.

During the May 21–26 emergency the dashboard polled `status.json` every 30 seconds, and a contributor ran the refresh job (`scripts/refresh_local.py`) on demand (roughly every 20–30 minutes) to re-gather facts and rewrite `status.json`. The map also showed a live wind reading from NOAA station KFUL, later removed for the reason above.

**Banners (historical behavior).** Each banner carried a `?` info icon with a full explanation.

- **🚨 URGENT** (pulsing red, audible beep): an act-now change: evac order toggled (expanded / lifted / reinstated), severity bumped, first injuries, or incident resolved.
- **📢 UPDATE** (amber, no beep): informational: a new official statement, or a notable resident-count shift.
- **⚠️ Data is stale**: the writer hadn't run in >30 min.
- **Offline / file missing**: the browser couldn't fetch `status.json`.

**The writer.** `scripts/update_status.py` (the control layer) read facts from stdin as JSON, diffed against the previous snapshot, and atomic-wrote `status.json`, enforcing the corroboration / provenance / freshness / date-sanity gates before any write (see [Safety architecture](README.md#safety-architecture--verification)). Running it now would overwrite the frozen snapshot, so it is left as historical reference only.

**Unattended operation.** During the incident the refresh path ran on a contributor's machine; a Windows Task Scheduler job was the unattended alternative. Both are retired with the archive.
