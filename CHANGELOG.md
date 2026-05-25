# Changelog

All notable changes to GG Tank Watch. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) loosely; dates in `YYYY-MM-DD`.

## [v0.8] — 2026-05-25 (dashboard redesign — PR-B)

### Changed
- **Rebrand to "GG Tank Watch"** across the topbar, page titles, and terms page.
- **Hero is now a neutral status line** — removed the "What should I do?" framing and the "STAY PUT"/"LEAVE NOW" directive (liability: we issue no directives and imply no safety, per LEGAL R1/R2). Shows a labeled "Incident severity: HIGH" and a clamped situation summary; per-address verdicts stay in the Check tab. Reclaims map real-estate.
- **News is one unified reverse-chronological feed** — official statements, articles, and videos merged and tagged by type (Official / Article / Video), replacing the confusing statements-vs-Coverage split.
- **Info tab reorganized** by resident need: Incident status (tank + evacuation) → Where to go (shelters) → Closures (schools) → collapsible Sources & methodology → collapsible About.
- **Topbar toggles**: "VI"/"EN" → "Viet"/"Eng"; Light/Dark text → sun/moon icons.

### Added
- **UPDATE banner is dismissible** — clicking it marks the latest statement as seen (localStorage); it stays gone until a newer statement arrives.
- **Geocode result caching** (localStorage, 7-day TTL) to satisfy the OSM Nominatim caching policy.

### Notes
- New user-facing strings are English-only with EN fallback under VI until Anna verifies (G1 gate). Final hero/severity wording remains attorney-review-gated per `docs/LEGAL.md`. The takeover modal's "LEAVE NOW" directive is flagged for a separate liability decision in `docs/REDESIGN_PUNCHLIST.md`. A pre-existing em-dash mojibake in `status.json` `boundary_text` (Info → Evacuation → Boundary) is a data-pipeline issue for the DATA_QUALITY lane, not this PR.

## [v0.7] — 2026-05-25 (trust/safety on-page — PR-A)

Pre-distribution trust and liability hardening from `docs/LEGAL.md` (minimum-bar checklist) and `docs/DISTRIBUTION.md` §5. The dashboard now sells its own unofficial, informational-only posture on first glance and points to the city as the source of truth on every screen.

### Added
- **Persistent "UNOFFICIAL" pill** in the topbar next to the title — never dismissable, with a "volunteer-made, not an official government source" tooltip.
- **Persistent safety strip** below the hero, visible across all tabs (Map/News/Check/Info): "Informational only — not official. In an emergency, call 911." plus a first-class official-source block (ggcity.org/emergency · 911 · 714-628-7085 · OCFA) and a link to the full terms.
- **"Who made this" block** at the top of the Info tab: built-by-volunteers line, full non-affiliation notice, no-data-collection statement, and a link to the terms page.
- **New `terms.html`** — standalone Terms & disclaimer page carrying the draft ToU (not-official/not-affiliated, informational-only, no-warranty, verify-official-sources, §1668-aware liability limit, third-party content, report-an-error, privacy, changes), an on-page banner, official sources, and OSM/Leaflet attribution.

### Changed
- **Address-check verdict wording audit** (highest-risk per LEGAL R1/R2, DISTRIBUTION §3): the "outside all zones" verdict no longer says "LIKELY SAFE" / "CÓ KHẢ NĂNG AN TOÀN" (dropped the banned safety promise) — now "OUTSIDE MAPPED ZONES" / "NGOÀI CÁC VÙNG TRÊN BẢN ĐỒ". "inside official evac zone" → "inside the city's evacuation zone" (keeps attribution to the authority, drops the "official" adjective).
- **Check-result disclaimer** strengthened to "Estimate only — not official. Verify at ggcity.org/emergency; in an emergency, call 911."

### Notes
- New user-facing strings are English-only and fall back to English under VI until Anna verifies them (G1 translation gate). The minimal VI redactions in changed verdict strings also need Anna's sign-off. Final wording remains attorney-review-gated per `docs/LEGAL.md` (🔴).

## [v0.6] — 2026-05-25 (post-portfolio iteration)

### Added
- **Evacuation shelters panel + map markers** (D-025). 9 hand-curated shelters geocoded via Nominatim: Garden Grove Sports & Rec, Cypress Community Center, Savanna HS (Anaheim), Mile Square Park (Fountain Valley), Los Amigos HS (Fountain Valley), Ocean View HS (Huntington Beach), Golden West College, JFK HS (La Palma), OC Fair & Event Center (Costa Mesa — RV evacuees only). Each rendered as a blue square marker on the map; panel below safety-checker shows name, city, address, RV-only chip, and a "Directions ↗" link that opens Google Maps with the destination pre-filled. Prominent CTA at top: "Live list at ggcity.org/emergency" since the city stays the source of truth.
- **News videos panel** generalized to **"Major news updates"** — supports both YouTube videos (`youtube_id` auto-derives `https://img.youtube.com/vi/{id}/hqdefault.jpg` thumbnail) and news article entries (no play overlay, document-icon placeholder when no thumbnail). 11 entries curated covering ABC7 LA, NBC LA, KTLA, ABC News, News18. Selection criteria: recency, coverage depth, format mix.
- **Client-side OG image fetcher** for article thumbnails (Microlink API, free tier, no key). Articles without a hardcoded `thumbnail_url` get their preview image fetched + cached in localStorage for 24 hours. Falls back gracefully to the typed placeholder if Microlink fails or rate-limits.
- **Statement backfill** (D-023 follow-up). Full incident timeline now: OCFA initial alert (Thu 5/21), Covey "tank will fail" press conference (Fri 5/22), drone temp rise 77→90°F (Sat 5/23), OC DA tipline launch + X-Law class action lawsuit (Sat evening), OCFA recon crack discovery (Sun 5/24), Chinsio-Kwong toxicity briefing, McGovern positive-intel update, gauge-pegged-at-100°F note, Costa Mesa fairgrounds opens for RV shelter. 12 statements in sidebar.
- **Two fixed reference pins on map**: Trask & Harbor + Magnolia & Ellis, color-coded by current safety verdict (auto-recolored on wind updates).
- **Safety checker**: geocodes any OC address/intersection via Nominatim, computes verdict (CRITICAL / HIGH / ELEVATED / SAFE), drops pin on map. New `D-019` and `D-020` in design log.
- **Statement card polish**: 14px bold date+time as the dominant line, agency on its own line, `Newest` red badge + red left-border on the most recent, `Recent` amber badge on statements <2 hours old, relative time `(N min ago)` on every card.
- **Sticky right sidebar** for statements (collapses to bottom-of-page below 1000px viewport). URGENT/UPDATE banner is now clickable — scrolls sidebar list to top + flashes the newest statement.
- **Light/dark theme toggle** in top-right, light is default, preference saved per-browser.

### Changed
- **Hero**: 72px clamp → `clamp(20px, 3.2vw, 32px)`. Severity chip merged into the hero (was a separate row).
- **Evac polygon**: extended west to ~Knott Ave to include Stanton + W Cypress portions per news reports.
- **Blast radii**: recalibrated from generic 0.25/0.5/1.0 mi → BLEVE-scaled 0.11/0.31/0.93 mi (matching OCFA labels: 20 PSI overpressure / Moderate damage / Lightweight injury). Methodology documented in `config.json.notes`.
- **Facility coordinates**: corrected to 33.7858, -118.0050 (12122 Western Ave per news reports — was a guess at 33.7748, -117.9978).
- **BREAKING banner classification**: split into URGENT (red, pulsing, beep, for act-now changes) and UPDATE (amber, no beep, for info-level like new statements). `breaking_level: urgent | info` field added to `status.json`. See D-016.
- **Map fitBounds**: now includes `fixed_points` and `shelters` so the southern/northern markers stay in viewport on initial load.
- **Geocoder bias**: Garden Grove → Orange County (with viewbox fallback) so generic intersections like "Magnolia & Talbert" find the OC location instead of out-of-state matches. D-020.
- **Section headers** added between page regions (`MAP`, `CHECK AN ADDRESS`, `EVACUATION SHELTERS`, `MAJOR NEWS UPDATES`, `INCIDENT DETAILS`, `SOURCES`) for visual hierarchy.

### Fixed
- **Writer bug**: piping partial facts (e.g., `cat data/news_seed.json | python scripts/update_status.py` which only contains `videos`) silently downgraded severity to "low" because `derive_severity()` walked off the rules table on missing fields. Next real tick fired a false URGENT "Severity bumped: low → high". Fix: only re-derive severity when this tick provides one of the severity-relevant fields (`evacuation_residents`, `evacuation_lifted`, `incident_resolved_iso`, `injuries`, `tank_failed`, `explosion_confirmed`). Otherwise carry prev. New `test_partial_facts_dont_downgrade_severity` locks the fix in. Eval went from 23/23 → 24/24.
- **fitBounds** missed `fixed_points` so Magnolia & Ellis (the southern green pin) was cut below the viewport.
- **Hardcoded ABC7 article thumbnails** weren't loading (likely CDN hotlink restrictions) — removed; replaced by Microlink OG fetch.

### Repo
- Initial push to **github.com/AnnaThyme/gg-tank-dashboard** (private).
- 8 commits on `main` before this PR. GH Actions workflow runs eval suite on every push.

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
