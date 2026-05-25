# Changelog

All notable changes to the GG MMA Tank Dashboard. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) loosely; dates in `YYYY-MM-DD`.

## [v0.5] — 2026-05-24 (portfolio cut)

### Added
- Top-level `README.md` rewritten as a portfolio pitch (case study, screenshots, architecture, what I'd change).
- `DESIGN_LOG.md` — structured log of every design decision (D-001 … D-NNN) with rubric scoring, alternatives considered, status (active/superseded), and retrospective notes.
- `eval/` directory with pytest-style behavioral suite:
  - `test_writer.py` — 5-state sequence (baseline / no-diff / urgent-toggle / stable / resolved) + new-statement + residents-shift + schema validation
  - `test_safety.py` — known-input → known-verdict coverage for the safety checker
  - `test_geocoder.py` — live Nominatim regression for Magnolia & Talbert, Trask & Harbor, full street address
  - `test_schema.py` — JSON schema validation for `status.json` + `config.json`
  - `run_all.py` — runs everything, appends to `eval/scores.jsonl`, prints scorecard
  - `rubrics/design_quality.md` — LLM-as-judge prompt for evaluating individual design decisions
  - `rubrics/data_quality.md` — LLM-as-judge prompt for evaluating writer fact extraction
- `USAGE.md` — operational guide (was the previous `README.md`)
- `LICENSE` (MIT)
- `.gitignore` (excludes runtime artifacts)

### Changed
- Original user-facing `README.md` moved to `USAGE.md`. Top-level `README.md` now serves a different audience (portfolio visitors).

## [v0.4] — 2026-05-24 (UPDATE banner + sidebar + statement card polish)

### Added
- Two fixed reference pins on the map (Trask & Harbor, Magnolia & Ellis) — auto-recolored by current safety verdict.
- Sticky right-sidebar for official statements (collapses to bottom-of-page below 1000px viewport).
- "Newest" red badge on the most recent statement + "Recent" amber badge on statements <2 hours old.
- UPDATE/URGENT banner is now clickable — scrolls sidebar list to top + flashes the newest statement.
- Section headers ("MAP", "CHECK AN ADDRESS", "INCIDENT DETAILS") to give the page a clearer flow.

### Changed
- Statement card layout: date+time is now the 14px bold dominant line; agency on its own line below.
- Statement sort: newest-first (was insertion order).
- BREAKING split into URGENT (red, pulsing, beep — for act-now changes) and UPDATE (amber, no beep — for info-level changes like new statements).
- Hero reduced from 72px → clamp(20px, 3.2vw, 32px) and severity chip merged into the hero (was a separate row).
- Evac polygon extended west to ~Knott Ave to include Stanton + W Cypress portions per news reports.

## [v0.3] — 2026-05-24 (map + safety checker + light theme)

### Added
- Leaflet map with OpenStreetMap tiles (no API key).
- 3 blast-zone circles (0.11 / 0.31 / 0.93 mi — derived from BLEVE scaling for ~7,000 gal MMA + visual match to OC Register published map).
- Live plume cone driven by NOAA `api.weather.gov` wind data (station KFUL, refreshed every 5 min, cached in localStorage).
- Safety checker: geocodes any address/intersection via Nominatim, computes verdict (CRITICAL / HIGH / ELEVATED / SAFE), drops a colored pin on the map.
- Light/dark theme toggle, light default. Preference saved per browser.
- `start_dashboard.bat` launcher — starts `python -m http.server` and opens the browser (fixes Chrome's `file://` fetch block).

### Changed
- Facility coordinates corrected to 33.7858, -118.0050 (12122 Western Ave per news reports — was a guess at 33.7748, -117.9978).
- Blast zone radii recalibrated: was 0.25/0.5/1.0 mi (generic); now matches BLEVE scaling for the actual tank inventory.

## [v0.2] — 2026-05-24 (desktop-only pivot)

### Removed
- ntfy push pipeline (POST on breaking, writer-down alert, ASCII-safe header helper).
- `urllib.request` / `urllib.error` imports (writer is now stdlib-only beyond optional deps).
- `apps-checklist.md` (Ready OC / Genasys EVAC / AirNow / ntfy install guide).
- All phone / mobile / OneDrive-web-on-phone references.

### Rationale
- User direction: "scratch all mobile plans, I just want a single live desktop dashboard app."
- Architectural note: the writer is still necessary because the browser can't pull news directly. Cloud routine remains as redundant text-delta producer (does not write status.json).

## [v0.1] — 2026-05-24 (v0 build)

### Added
- `update_status.py` writer: WebSearch+regex fact extraction (driven by /loop), structural-diff breaking detection with TOGGLES-fire-immediately + residents-shift-rate-limited rules, atomic write with retry on Windows OneDrive file-locks.
- `dashboard.html` v0: 4 panels (Hero with zone verdict / Tank / Evacuation / Schools closed / Sources collapsed / Statements collapsed) with NWS gov-emergency-calm aesthetic.
- `config.json`: zone_status, refresh intervals, incident metadata.
- `go_bag.md`: standalone printable evacuation checklist.
- Hooked into existing in-session `/loop` job (every 30 min) and cloud routine (hourly redundancy).

### Decisions captured at this point (see DESIGN_LOG.md for full context)
- D-001 push-first vs dashboard-first (later reversed per D-009)
- D-002 OneDrive path vs `%LOCALAPPDATA%` (kept OneDrive)
- D-003 WebSearch+regex vs per-site scrapers (chose WebSearch+regex)
- D-004 Hysteresis design (initially 2-tick, then killed in v0.1.1 because the candidate-fires-twice rule was wrong for toggle events)
- D-005 Severity rules (hardcoded `SEVERITY_RULES` dict)
- D-006 Cloud routine writing to status.json (rejected — Linux sandbox can't reach OneDrive)
- D-007 Map vs no map (initially deferred, then added in v0.3 per user request)

## [v0] — 2026-05-24 (SPEC + autoplan review)

### Added
- `docs/SPEC.md` — full SPEC capturing problem statement, premises, architecture, data model, error model, scope.
- `BRIEF_2026-05-24.md` — source-cited factual brief on the incident (10+ news sources triangulated).
- `PERSONAL_UPDATE_2026-05-24.md` — drafts for personal status updates to family / manager.
- Autoplan review: CEO + Design + Eng phases run via Claude subagents (Codex unavailable on this machine — degraded gracefully).
- Premise gate + final approval gate with 5 taste decisions surfaced for the user.

### Decisions captured
- D-008 Pivot from dashboard-first to push-first (CEO findings F1, F2, F11 triggered user challenge → user accepted pivot)

## [v0 prelude] — 2026-05-24 (research)

### Added
- `BRIEF_2026-05-24.md` produced via `/deep-research` — triangulated across ABC7, NBC LA, CBS LA, KTLA, CNN, PBS, Wikipedia, EPA, CDPH.
- Recurring update infrastructure: `/loop` cron (every 30 min in-session) + cloud routine `trig_017YEJ4zkKeeXswyXPWz3yFw` (hourly via claude.ai).
