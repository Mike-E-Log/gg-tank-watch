# GG MMA Tank Dashboard

**A single-page situational-awareness dashboard built during the May 2026 Garden Grove methyl methacrylate tank emergency** — a real, ongoing chemical incident that evacuated ~50,000 residents in a 9-square-mile zone of Orange County, California. I was a downwind-adjacent resident; I built this for myself.

[![Status](https://img.shields.io/badge/status-shipped-success)](#)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Stack](https://img.shields.io/badge/stack-vanilla%20JS%20%2B%20Python%20stdlib-lightgrey)](#stack)
[![Eval](https://img.shields.io/badge/eval-pytest%20%2B%20LLM%20judge-orange)](eval/)

---

## What it does

| | |
|---|---|
| **Single glance** | Hero tells you whether you're inside the evacuation zone — green / red, 32px |
| **Live map** | Leaflet + OpenStreetMap. Evac polygon, three blast-radius circles, plume cone driven by live NOAA wind, fixed reference pins (color-coded by safety verdict), tank facility marker |
| **Safety checker** | Type any address or intersection ("Magnolia & Talbert") → geocoded via Nominatim → verdict (SAFE / ELEVATED / HIGH / CRITICAL) + pin dropped on the map |
| **Update banner** | URGENT (red, pulsing, beep) for act-now changes; UPDATE (amber, no beep) for informational. Click → scrolls sidebar to highlight the newest statement |
| **Statements sidebar** | Sticky, scrollable, newest-first, with `Newest` + `Recent` badges. Source links on each |
| **Auto-refresh** | Dashboard polls `status.json` every 30 s. Writer refreshes `status.json` every 30 min via a background loop. Wind refreshes every 5 min from NOAA's free API |
| **Theme** | Light default with dark toggle, saved per browser |

## Why I built it

The emergency was multi-day and evolving. The available signals — news live-blogs, the city's emergency page, OCFA tweets — were scattered. Reaching for my phone or refreshing news tabs felt like a tax I was paying every 20 minutes. I wanted one page that answered my actual question ("do I need to leave?") with everything else as supporting evidence I could glance at, not hunt for.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  /loop cron (every 30 min) → WebSearch (Claude tool)                │
│       ↓ extracts structured facts as JSON                           │
│       ↓ pipes to stdin                                              │
│  scripts/update_status.py  (Python stdlib only)                     │
│   • diffs against prev snapshot                                     │
│   • classifies change: URGENT (toggles) vs UPDATE (info)            │
│   • atomic-writes status.json with Windows OneDrive retry           │
│   • appends to breaking_events.jsonl + updates.log                  │
│       ↓                                                              │
│  status.json  ← atomic-renamed snapshot                             │
│       ↑                                                              │
│  dashboard.html  (vanilla JS, no build step)                        │
│   • polls status.json every 30 s                                    │
│   • renders hero / map / safety checker / sidebar / panels          │
│   • fetches wind from api.weather.gov every 5 min (KFUL)            │
│   • fetches map tiles from OpenStreetMap                            │
│   • geocodes via Nominatim on safety check                          │
│       ↑                                                              │
│  start_dashboard.bat  → python -m http.server + opens browser       │
└─────────────────────────────────────────────────────────────────────┘
```

**No backend, no database, no auth, no build step.** Two files of real code (Python writer + HTML/JS reader), JSON as the message bus, browser as the runtime. The whole thing is double-clickable.

## Stack

- **Frontend:** vanilla HTML/CSS/JS + [Leaflet](https://leafletjs.com/) (map) + [OpenStreetMap](https://www.openstreetmap.org/) (tiles, geocoding). No framework, no build step, ~30 KB of original code.
- **Writer:** Python 3 stdlib only. No external deps. Uses `urllib` for HTTP would have been, but the ntfy push pipeline was scratched (see DESIGN_LOG D-009).
- **Map data:**
  - Wind from NOAA's free `api.weather.gov` (station KFUL Fullerton Muni)
  - Geocoding from OpenStreetMap Nominatim
  - Blast-zone radii estimated from BLEVE scaling for the actual tank inventory (~7,000 gal MMA ≈ ~100 tonnes TNT-equivalent overpressure)
- **Trigger:** Claude Code's in-session `/loop` cron (every 30 min) does the WebSearch and pipes a structured facts JSON to the writer.
- **No deps beyond Python 3 stdlib + a CDN-loaded Leaflet.**

## How design decisions get made and tracked

Every meaningful design call is captured in [`DESIGN_LOG.md`](DESIGN_LOG.md) with structured fields:

- **What** was decided
- **Alternatives** considered (and why they lost)
- **Rationale** + which design principles applied
- **Rubric score** (correctness / maintainability / user-fit, 1–10)
- **Status** (active / superseded / reverted) — including links to superseding decisions when direction changed
- **Retrospective lesson**

The log was seeded retroactively from the project's first hour, then maintained going forward. It demonstrates the *thinking* behind the code, not just the code.

The most interesting reversal is **D-001 → D-009**: I went into the build push-first-dashboard-second based on the CEO subagent's strong reasoning (the user can't see a dashboard when asleep / away from screen). The user immediately reversed it: "scratch all mobile plans." Both decisions are logged with full reasoning. Lesson at the bottom of D-001.

## How data quality + behavior gets evaluated

[`eval/`](eval/) contains a pytest-style behavioral test suite + LLM-as-judge rubrics. Every change runs through it.

| Suite | What it checks |
|---|---|
| `test_writer.py` | 5-state behavioral sequence (baseline / no-diff / urgent-toggle / stable / resolved) + new-statement detection + residents-shift rate-limiting + schema validation |
| `test_safety.py` | Known-input → known-verdict for the safety checker. Includes plume-direction math, point-in-polygon, blast-zone-distance math |
| `test_geocoder.py` | Live Nominatim regression: `Magnolia & Talbert` → known coords (33.702, -117.972), `Trask & Harbor` → (33.766, -117.920), full street address → near facility |
| `test_schema.py` | JSON schema validation for `status.json` and `config.json` |
| `rubrics/design_quality.md` | LLM-as-judge prompt for evaluating any design decision against the 6 autoplan principles |
| `rubrics/data_quality.md` | LLM-as-judge prompt for evaluating writer fact extraction (precision, recall, hallucination check) |

Results append to `eval/scores.jsonl` so regressions are visible over time. Run with `python eval/run_all.py`.

## Process highlight: full autoplan review on day 1

Before writing a line of code I ran a full multi-phase plan review against the original SPEC: CEO (strategy + scope), Design (UI / interaction states / aesthetic), and Eng (architecture / atomic writes / error paths / test coverage / budget honesty). Codex CLI wasn't available locally so phases ran with Claude subagents only — degraded gracefully via the autoplan skill's documented fallback. Findings ended up reshaping the SPEC before I touched the implementation.

Reviewer outputs are folded into [`docs/SPEC.md`](docs/SPEC.md) and the design log. The most load-bearing findings:

- **CEO F1:** Original dashboard-first scope was solving the wrong problem ("seen when looking" vs "reaches me when not looking"). Triggered the push-first pivot.
- **Eng E1:** Per-site HTML scrapers would be broken within a day. Reframed extraction to "WebSearch (Claude side) + regex on snippets" — fragile parts on the model, deterministic parts in Python.
- **Eng E3:** Residents-count flapping between reports would false-fire breaking every tick. Added rate-limiting (now: residents shifts only fire once per 2 hours).
- **Design D1:** Hero was tank temperature; should be zone verdict. Tank temp isn't something the user can act on. Zone status is.

Each finding logged with status (Fixed / Deferred / Reverted) in the design log.

## Lessons (what I'd do differently)

- **Build the eval suite earlier.** I had the writer's behavior wrong twice (hysteresis logic) before I had tests. A 5-state behavioral sequence as a test file would have caught both within minutes.
- **Trust the reviewers' biggest finding even when it conflicts with the user's framing.** I built mobile push, the user said "scratch it," I deleted it cleanly — but if I'd surfaced the reviewer's full reasoning earlier maybe we'd have caught the disconnect sooner.
- **Don't pick a `--theme=dark` aesthetic without showing the user.** First version was NWS gov-emergency-calm dark. User said "too dark" within 30 seconds. Light/dark toggle should have been default from the start.
- **Atomic rename + OneDrive sync is a real failure mode on Windows.** The retry-with-backoff wrapper has caught at least one transient `PermissionError` in testing. Worth the 10 lines.
- **Hardcoded blast radii are defensible if you say where they came from.** I derived them from BLEVE scaling for the actual tank inventory + visually matched to the OC Register's published map. Called out clearly in `config.json.notes` and the dashboard legend.

## Running it yourself

See [`USAGE.md`](USAGE.md) for full operational docs. Quick version:

```powershell
git clone <this-repo>
cd gg-tank-dashboard
.\start_dashboard.bat
```

Then in another shell (or via your scheduler of choice), feed the writer some facts:

```powershell
'{"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": false, "status_headline": "Test"}' | python scripts\update_status.py
```

Refresh the browser to see the snapshot.

## Repository layout

```
gg-tank-dashboard/
├── README.md                       ← you are here
├── USAGE.md                        ← operational guide
├── CHANGELOG.md                    ← iteration log
├── DESIGN_LOG.md                   ← decisions + rubric scores
├── LICENSE                         ← MIT
├── .gitignore
├── start_dashboard.bat             ← launcher
├── dashboard.html                  ← the dashboard
├── config.json                     ← map coords, intervals, zone_status
├── go_bag.md                       ← printable evac checklist
├── BRIEF_2026-05-24.md             ← source-cited factual brief
├── PERSONAL_UPDATE_2026-05-24.md   ← personal status update drafts
├── scripts/
│   └── update_status.py            ← the writer
├── docs/
│   └── SPEC.md                     ← full SPEC + autoplan trail
└── eval/
    ├── README.md
    ├── run_all.py                  ← runs everything, appends scores.jsonl
    ├── test_writer.py
    ├── test_safety.py
    ├── test_geocoder.py
    ├── test_schema.py
    ├── scores.jsonl                ← append-only eval history
    ├── fixtures/
    └── rubrics/
        ├── design_quality.md       ← LLM-as-judge prompt
        └── data_quality.md
```

## License

MIT — see [LICENSE](LICENSE). Data + blast-zone estimates + plume visualization are informational only, NOT authoritative emergency guidance. For evacuation status refer to OCFA, ggcity.org/emergency, Genasys EVAC, Ready OC, AirNow.
