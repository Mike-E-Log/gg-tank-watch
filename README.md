# GG Tank Watch

**A single-page situational-awareness dashboard built during the May 2026 Garden Grove methyl methacrylate tank emergency** — a real, ongoing chemical incident that evacuated ~50,000 residents in a 9-square-mile zone of Orange County, California. I was a downwind-adjacent resident; I built this for myself.

[![Status](https://img.shields.io/badge/status-shipped-success)](#)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Stack](https://img.shields.io/badge/stack-vanilla%20JS%20%2B%20Python%20stdlib-lightgrey)](#stack)
[![Eval](https://img.shields.io/badge/eval-pytest%20%2B%20LLM%20judge-orange)](eval/)

---

## For Anthropic reviewers

This repo is a portfolio piece for the Fellows Program. Recommended path: [`CLAUDE.md`](CLAUDE.md) (safety principles table) → [`docs/AI_CONTROL_ARCHITECTURE.md`](docs/AI_CONTROL_ARCHITECTURE.md) (control layer + test mapping) → [`docs/FAILURE_ANALYSIS.md`](docs/FAILURE_ANALYSIS.md) (12-mode red team) → [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) (conduit pattern) → [`eval/`](eval/) (run `python eval/run_all.py --skip integration` — 45 tests, exits 0).

### Safety architecture (30-second scan)

The LLM's output passes through a single chokepoint before reaching `status.json`. The control layer enforces four structural properties — no prompting required:

| Control | What it prevents | Asymmetry |
|---------|-----------------|-----------|
| **P0-1 Corroboration gate** | A single hallucinated `evacuation_lifted: true` fires an all-clear | Danger downgrades need ≥2 sources + ≥1 official. Upgrades fire on 1. |
| **P0-2 Provenance check** | Fabricated source URL or unattributed quote reaches the dashboard | Statement dropped unless its URL was actually fetched this run |
| **P0-3 Freshness honesty** | Empty-facts run stamps a fresh timestamp on stale data | `data_as_of_iso` advances only on source-backed facts; staleness banner keys off data age, not write age |
| **P1-1 Date sanity** | Future-dated or malformed `incident_resolved_iso` flips incident to resolved | Future/malformed timestamps are nulled before snapshot write |

Full diagram and test mapping: [`docs/AI_CONTROL_ARCHITECTURE.md`](docs/AI_CONTROL_ARCHITECTURE.md)

### Eval quick-start

```bash
python eval/run_all.py --skip integration
```

Expected output (45 tests, all green):

```
  behavioral       38/38   (100.0% pass)
  schema            7/7    (100.0% pass)
----------------------------------------------------------------
  TOTAL            45/45   (100.0% pass)
```

Test categories: 5-state behavioral sequence (writer state machine) · corroboration gate · provenance · freshness · date sanity · severity derivation · gatherer failure contract · encoding integrity · schema validation. Results append to `eval/scores.jsonl` for regression tracking.

Red-team report (12 failure modes, guarded/unguarded verdict per mode): [`docs/FAILURE_ANALYSIS.md`](docs/FAILURE_ANALYSIS.md)

### Performance

| Metric | Value | How |
|--------|-------|-----|
| First paint | No framework, no build step | The whole UI ships in one ~126 KB HTML file; `status.json` is fetched client-side after paint |
| Third-party CDN in the critical path | 0 | MapLibre GL is self-hosted in `/lib` (~800 KB) and service-worker cached, so the map can't vanish when a CDN changes |
| Offline resilience | PWA + service worker | Caches the last-known state and the map library; the staleness banner fires when data is old |
| Map | MapLibre GL + OpenFreeMap | Vector tiles, light/dark styles; the map library loads when the Map tab is opened |

A single HTML file with no framework and no build step, serving a safety-critical audience on mobile data. Self-hosting the map library is a deliberate reliability choice: an earlier CDN-loaded build disappeared on refresh, so the library now ships with the app and is cached by the service worker. Tiles come from OpenFreeMap and degrade gracefully.

---

## What it does

| | |
|---|---|
| **Single glance** | Hero status board: the current-situation lead plus the key facts — evacuation status, residents affected, last verified update — without scrolling |
| **Live map** | MapLibre GL + OpenFreeMap vector tiles (light / dark). The evacuation-zone boundary, the GKN Aerospace facility marker, shelter locations, and live NOAA wind direction |
| **Official sources** | Routes to the authoritative channels — ggcity.org/emergency, OCFA, Genasys EVAC, OC Alert, EPA AirNow — with the reminder that no single source should be your only one |
| **Update banner** | URGENT (red, pulsing, beep) for act-now changes; UPDATE (amber, no beep) for informational. Click → scrolls sidebar to highlight the newest statement |
| **Statements sidebar** | Sticky, scrollable, newest-first, with `Newest` + `Recent` badges. Source links on each |
| **Auto-refresh** | Dashboard polls `status.json` every 30 s. A contributor runs the refresh job on demand — roughly every 20–30 min during the active incident — to re-gather facts and rewrite `status.json` (see [Data sync](#data-sync--how-statusjson-stays-fresh)). Wind refreshes every 5 min from NOAA's free API |
| **Theme** | Light default with dark toggle, saved per browser |

## Why I built it

The emergency was multi-day and evolving. The available signals — news live-blogs, the city's emergency page, OCFA tweets — were scattered. Reaching for my phone or refreshing news tabs felt like a tax I was paying every 20 minutes. I wanted one page that answered my actual question ("do I need to leave?") with everything else as supporting evidence I could glance at, not hunt for.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  refresh job (on demand) → claude -p WebSearch (subscription)       │
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
│   • renders hero / map / sidebar / panels                           │
│   • fetches wind from api.weather.gov every 5 min (KFUL)            │
│   • fetches map tiles from OpenFreeMap                              │
││       ↑                                                              │
│  start_dashboard.bat  → python -m http.server + opens browser       │
└─────────────────────────────────────────────────────────────────────┘
```

**No backend, no database, no auth, no build step.** Two files of real code (Python writer + HTML/JS reader), JSON as the message bus, browser as the runtime. The whole thing is double-clickable.

## Data sync — how `status.json` stays fresh

`status.json` is the only thing that changes after deploy, so keeping it current is the one real ops problem. I built two interchangeable paths and deliberately run the cheaper one:

| Path | Where it runs | Billing | Status |
|---|---|---|---|
| `scripts/refresh_local.py` | a contributor's machine, left on | **subscription credits, $0 metered** — calls `claude -p` on the OAuth subscription with `ANTHROPIC_API_KEY` unset | **active** |
| `.github/workflows/update-status.yml` | GitHub-hosted runner, no machine needed | **metered `ANTHROPIC_API_KEY`** (~$200–330/mo at a 20-min cadence) | **dormant** — `schedule:` commented out |

Both share one gatherer: `refresh_local.py` imports `PROMPT` + `extract_json` from `gather_facts.py`, so the two paths stay in lockstep and only the model call differs (subscription CLI vs. metered SDK). Each run gathers facts via WebSearch, writes `status.json`, commits it with `[skip ci]`, and pushes — Vercel auto-deploys the new snapshot.

**The tradeoff is the point.** A headless cloud runner can't use the OAuth subscription, only a metered key, so "no machine required" costs real money while "$0 metered" needs a machine that's on. For a single-incident dashboard that isn't cleared for wide distribution yet, the right call is to keep the cloud cron wired-but-dormant (the secret's already set; uncommenting one line flips it on) and refresh locally on subscription credits. Full writeup in [`docs/DATA_SYNC.md`](docs/DATA_SYNC.md).

**The failure mode is honest by design.** If a gather fails, the writer writes nothing: `status.json` keeps its old timestamp and the dashboard's staleness banner fires. It never stamps a fresh time onto stale data.

## Stack

- **Frontend:** vanilla HTML/CSS/JS + [MapLibre GL](https://maplibre.org/) (self-hosted in `/lib`) + [OpenFreeMap](https://openfreemap.org/) vector tiles. No framework, no build step; the app ships as one ~126 KB HTML file.
- **Writer:** Python 3 stdlib only. No external deps. Uses `urllib` for HTTP would have been, but the ntfy push pipeline was scratched (see DESIGN_LOG D-009).
- **Map data:**
  - Wind from NOAA's free `api.weather.gov` (station KFUL Fullerton Muni)
  - Vector tiles from OpenFreeMap (light / dark styles)
  - Evacuation-zone polygon, the GKN Aerospace facility, and shelter locations from `config.json`
- **Trigger:** `scripts/refresh_local.py` (run on demand, roughly every 20–30 min during the active incident) gathers facts via `claude -p` WebSearch on the subscription and pipes structured JSON to the writer. See [Data sync](#data-sync--how-statusjson-stays-fresh) for the dual-path design.
- **No deps beyond Python 3 stdlib + a self-hosted MapLibre GL build.**

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
| `test_safety.py` | Conduit-principle guards: asserts the dashboard contains no authored hazard verdicts (no `blast_zones_mi`, no plume layer, no injury-radius copy) and routes users to an official source |
| `test_geocoder.py` | Legacy integration test for the pre-conduit address geocoder (Nominatim). Skipped by default (`--skip integration`); retained as regression history |
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
- **A hardcoded estimate is defensible if you say where it came from.** Early versions rendered blast-radius circles derived from BLEVE scaling for the tank inventory, with the basis spelled out in `config.json.notes`. The circles were later removed in the conduit pivot (the dashboard authors no hazard verdicts), but the principle holds.

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
│   ├── refresh_local.py            ← subscription-billed refresh (active path)
│   ├── gather_facts.py             ← metered SDK gatherer (cloud path)
│   └── update_status.py            ← the writer
├── docs/
│   ├── SPEC.md                     ← full SPEC + autoplan trail
│   └── DATA_SYNC.md                ← dual-path data-sync design + cost tradeoff
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

MIT — see [LICENSE](LICENSE). Data is informational only, NOT authoritative emergency guidance. For evacuation status refer to OCFA, ggcity.org/emergency, Genasys EVAC, Ready OC, AirNow.
