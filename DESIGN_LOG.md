# Design Log

Structured log of every meaningful design decision made on the GG MMA Tank Dashboard. Seeded retroactively from project start; maintained going forward.

## How to read this

Each decision has:
- **Date** — when made
- **Status** — `Active` · `Superseded` (with link) · `Reverted` · `Deferred`
- **Context** — what triggered the decision
- **Decision** — what we did
- **Alternatives** — what we considered and why each lost
- **Principles applied** — the 6 autoplan principles (P1 completeness, P2 boil lakes, P3 pragmatic, P4 DRY, P5 explicit, P6 bias to action)
- **Rubric score** — retrospective grading on three axes, 1–10:
  - **Correctness:** does it solve the actual problem?
  - **Maintainability:** would another engineer understand + extend it?
  - **User-fit:** did Nancy (the actual user) accept it?
- **Lesson** — what to remember next time

## Decision summary table

| ID | Date | Title | Status | Score (avg) |
|---|---|---|---|---|
| D-001 | 2026-05-24 | Push-first vs dashboard-first | Superseded → [D-009](#d-009) | 6.0 |
| D-002 | 2026-05-24 | Runtime path: OneDrive vs %LOCALAPPDATA% | Active | 8.0 |
| D-003 | 2026-05-24 | Fact extraction: WebSearch+regex vs site scrapers | Active | 9.0 |
| D-004 | 2026-05-24 | Breaking detection hysteresis (2-tick) | Reverted → [D-016](#d-016) | 4.0 |
| D-005 | 2026-05-24 | Severity derivation: SEVERITY_RULES dict | Active | 8.3 |
| D-006 | 2026-05-24 | Cloud routine writing status.json | Rejected | 9.0 |
| D-007 | 2026-05-24 | Map: deferred to v1 (initially) | Superseded → [D-011](#d-011) | 5.0 |
| D-008 | 2026-05-24 | CEO pivot: push-first | Reverted → [D-009](#d-009) | 7.0 |
| D-009 | 2026-05-24 | User reversal: scratch all mobile | Active | 9.3 |
| D-010 | 2026-05-24 | Light theme default + dark toggle | Active | 9.0 |
| D-011 | 2026-05-24 | Map library: Leaflet | Active | 9.3 |
| D-012 | 2026-05-24 | Hero size: shrink 72px → 32px | Active | 9.0 |
| D-013 | 2026-05-24 | Evac polygon: extend west to ~Knott Ave | Active | 7.7 |
| D-014 | 2026-05-24 | Blast radii: BLEVE-scaled, not generic | Active | 8.3 |
| D-015 | 2026-05-24 | Official statements: sticky right sidebar | Active | 9.0 |
| D-016 | 2026-05-24 | URGENT vs UPDATE banner classification | Active | 9.3 |
| D-017 | 2026-05-24 | Banner clickable → scroll + highlight | Active | 8.7 |
| D-018 | 2026-05-24 | Newest + Recent badges on statements | Active | 9.0 |
| D-019 | 2026-05-24 | Fixed reference pins on map | Active | 8.7 |
| D-020 | 2026-05-24 | Geocoder bias: Garden Grove → Orange County | Active | 9.0 |
| D-021 | 2026-05-24 | Section headers for visual flow | Active | 8.0 |
| D-022 | 2026-05-24 | Safety checker placement: below map | Active | 8.0 |
| D-023 | 2026-05-24 | Statement card design: bold meta + relative time | Active | 9.0 |
| D-024 | 2026-05-24 | Portfolio framing: eval suite + design log | Active | TBD |
| D-025 | 2026-05-25 | Evac shelters: aggregate + link (hybrid) | Active | 9.0 |
| D-026 | 2026-05-25 | News panel: generalize to videos + articles, Microlink OG fetch | Active | 8.7 |
| D-027 | 2026-05-25 | Writer fix: partial facts must not recompute severity | Active | 9.3 |
| D-028 | 2026-05-25 | PR workflow: feature branches + GitHub PRs for non-trivial changes | Active | TBD |
| D-029 | 2026-05-25 | Hero address check: move safety checker into always-visible hero | Active | 8.7 |

---

## D-001: Push-first vs dashboard-first

- **Date:** 2026-05-24
- **Status:** Superseded by [D-009](#d-009) within 90 minutes of accepting it.
- **Context:** Initial SPEC framed this as a "live dashboard" Nancy would glance at. CEO subagent challenged hard: the real failure mode isn't "I want to look but can't" — it's "I'm asleep / showering / driving when the evac expands and don't see it."
- **Decision:** Build push notifications (ntfy.sh) as the **primary** alert path; dashboard becomes secondary.
- **Alternatives:**
  - **Dashboard-first (rejected):** fails the asleep/away-from-screen scenario.
  - **Phone apps only (rejected):** user explicitly wanted custom code.
  - **Hybrid (chosen):** ntfy push for breaking + dashboard for glance.
- **Principles applied:** P1 completeness, P5 explicit, P6 bias to action.
- **Rubric:**
  - Correctness: 8 (sound at the time)
  - Maintainability: 7
  - User-fit: 3 (user reversed within 90 min)
- **Lesson:** A strong CEO-level argument is necessary but not sufficient — the user has context the reviewer doesn't. Build for revert (the ntfy pipeline was cleanly removable when D-009 fired).

## D-002: Runtime path: OneDrive vs %LOCALAPPDATA%

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** Eng review flagged Windows + OneDrive + atomic rename as a real `PermissionError` risk (sync client + Defender hold file handles briefly).
- **Decision:** Keep runtime files (`status.json`, `updates.log`, `breaking_events.jsonl`) inside the OneDrive-synced project folder; add a 5-attempt exponential-backoff retry on `os.replace()` / append.
- **Alternatives:**
  - **Move runtime to `%LOCALAPPDATA%\gg-dashboard\` (rejected):** would kill the cross-device view (which was a v0 premise at that point — later moot per D-009).
  - **Disable OneDrive sync for the folder (rejected):** invasive; affects user's overall OneDrive setup.
- **Principles applied:** P3 pragmatic, P5 explicit.
- **Rubric:** Correctness 9 · Maintainability 8 · User-fit 7.
- **Lesson:** "Atomic rename is atomic" is true at the OS layer but false at the OneDrive layer. Retry-with-backoff is the cheap fix; ~10 lines of code, zero user-visible cost.

## D-003: Fact extraction: WebSearch+regex vs per-site scrapers

- **Date:** 2026-05-24
- **Status:** Active. **Most load-bearing decision in the codebase.**
- **Context:** Eng review (E1) flagged the original SPEC's "one extractor per source" as the biggest handwave — per-site HTML scrapers would be broken within a day by news-site changes.
- **Decision:** The `/loop` cron does WebSearch (Claude's tool) and pipes a structured facts JSON to `update_status.py` via stdin. The script never touches the open web; it's pure JSON → diff → snapshot → log.
- **Alternatives:**
  - **Per-site HTML scrapers (rejected):** fragile, days of work, dies on the next news-site redesign.
  - **News API (rejected):** all the good ones need paid keys.
  - **WebSearch in the Python script via Anthropic API (rejected):** requires API key + cost.
  - **WebSearch in /loop, parse in Python (chosen):** fragile-things-on-the-model, deterministic-things-in-Python.
- **Principles applied:** P3 pragmatic, P5 explicit.
- **Rubric:** Correctness 10 · Maintainability 9 · User-fit 8.
- **Lesson:** Where you draw the boundary between "AI does the messy part" and "code does the deterministic part" is the single most important architecture call in an LLM-augmented system. Get this wrong and you're either building a brittle scraper or a black box.

## D-004: Breaking detection hysteresis (2-tick)

- **Date:** 2026-05-24
- **Status:** Reverted within 2 hours. See [D-016](#d-016).
- **Context:** Eng review (E3) flagged that residents-count flapping between reports (45k ↔ 50k) would false-fire breaking every tick. Recommendation: 2-tick hysteresis — require the candidate to fire on two consecutive ticks before flipping.
- **Decision (then):** Implemented `pending_breaking_since_iso` field; first detection sets pending, second consecutive detection 30 min later flips breaking.
- **Why reverted:** Behavioral test showed the implementation was wrong — a real evacuation expansion generates a *toggle event* on tick N (false→true) and equilibrium thereafter. The detector saw no NEW toggle on tick N+1 because the value was already `true`. Pending was reset, breaking never flipped. **Cry-wolf prevention turned into miss-the-real-event.**
- **Replaced with:** Toggle events fire immediately (lifted/expanded/severity-bumped/resolved/injuries/new-statement). Only the residents-shift rule gets a rate-limit (once per 2 hours). See D-016.
- **Principles applied:** P1 completeness (over-applied — the toggle case wasn't a count case).
- **Rubric:** Correctness 3 · Maintainability 5 · User-fit 4.
- **Lesson:** **Test the design before shipping it.** The 5-state behavioral sequence (baseline / no-diff / toggle / stable / resolved) caught this in minutes. Without it the bug would have shipped and the next real expansion would have been silently missed.

## D-005: Severity derivation: SEVERITY_RULES dict

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** Eng review (E4) — severity is not in news source data; needs derivation from observed facts.
- **Decision:** Hardcoded `SEVERITY_RULES` dict in `update_status.py`, first-match-wins ordering: critical (tank failed / explosion / injuries) → high (>1000 evacuated, not lifted) → moderate (>0 evacuated) → low (resolved or lifted).
- **Alternatives:**
  - **LLM call to classify (rejected):** overkill, brittle, latency, cost.
  - **Configurable rules in JSON (deferred):** P5 explicit — code is where this logic should live for one user.
- **Principles applied:** P5 explicit, P3 pragmatic.
- **Rubric:** Correctness 9 · Maintainability 8 · User-fit 8.
- **Lesson:** Heuristic classification rules in code (with a clear first-match-wins order) beat both LLM calls and configurable-rules-as-data for a single-user tool.

## D-006: Cloud routine writing status.json

- **Date:** 2026-05-24
- **Status:** Rejected.
- **Context:** Original SPEC envisioned the hourly cloud routine as a redundant writer of `status.json`.
- **Decision:** Cloud routine produces text deltas in its own log and does NOT write `status.json`. Local `/loop` is the sole writer.
- **Why:** The cloud routine runs in a Linux sandbox with no access to Nancy's OneDrive folder. Architecturally impossible.
- **Alternatives:**
  - **Push from cloud to a public endpoint (rejected):** infrastructure for one user.
  - **Cloud writes to a git repo, local pulls (rejected):** churn, complexity.
- **Principles applied:** P5 explicit.
- **Rubric:** Correctness 10 · Maintainability 9 · User-fit 8.
- **Lesson:** Sometimes the right call is "this redundancy isn't actually possible; document why and move on."

## D-007: Map: deferred to v1 (initially)

- **Date:** 2026-05-24
- **Status:** Superseded by D-011 (a few hours later, per user direction).
- **Context:** Original v0 SPEC explicitly cut the map ("static SVG") as out-of-scope.
- **Decision (then):** Skip map for v0. Link to ggcity.org/emergency instead.
- **Why superseded:** User added "I want a map showing a live wind flow direction, evacuation area, with the explosion blast zone, with the chemical plume zone" as an explicit feature request right after seeing the no-map version.
- **Rubric:** Correctness 7 (was right for the original v0 scope) · Maintainability 5 · User-fit 3.
- **Lesson:** Defer-to-v1 decisions are honest scope-cuts but get reverted fast if the user sees the cut feature as core. Better to ask before deferring something user-visible.

## D-008: CEO pivot to push-first

- **Date:** 2026-05-24
- **Status:** Reverted by D-009 within 90 min.
- **Context:** CEO subagent's F1 / F2 / F11 findings (see `docs/SPEC.md`) triggered a User Challenge — both my analysis and the subagent agreed the user's stated direction ("live dashboard") should change to "push-first, dashboard-secondary."
- **Decision:** Presented the User Challenge at the premise gate; user accepted the pivot.
- **Why reverted:** User changed their mind 90 min later after seeing the implementation: "scratch all mobile plans." See D-009.
- **Rubric:** Correctness 8 (CEO reasoning was sound) · Maintainability 7 · User-fit 6.
- **Lesson:** A "user accepts the pivot" answer at the premise gate isn't durable — users discover what they actually want by interacting with the artifact. Build for revert.

## D-009: User reversal: scratch all mobile

- **Date:** 2026-05-24
- **Status:** Active. **The most important UX decision in the project.**
- **Context:** User direct message: "Scratch all mobile plans. I just want a single live desktop dashboard app."
- **Decision:** Removed the entire mobile/push pipeline (`apps-checklist.md`, ntfy POST code, `urllib` imports, `ntfy_topic`/`ntfy_server` config fields, all phone references in README/SPEC).
- **Alternatives:** None — direct user instruction.
- **Principles applied:** User direction is the highest priority signal.
- **Rubric:** Correctness 10 · Maintainability 9 · User-fit 9.
- **Lesson:** When a user reverses a decision a reviewer talked them into, take it at face value and revert cleanly. The mobile pipeline came out in ~10 minutes because D-001 was built for revert (clean separation of concerns).

## D-010: Light theme default + dark toggle

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** Original aesthetic was NWS gov-emergency-calm (dark only). User: "I want it to look brighter it's too dark."
- **Decision:** Light theme with neutral background `#f5f5f7`, white surfaces, slate text. Dark theme kept as a toggle (top-right), preference saved in `localStorage`. Light is default.
- **Alternatives:**
  - **Lighten the dark palette in place (rejected):** halfway measure.
  - **System-prefers-color-scheme (rejected):** user explicitly asked for "brighter," not "follow OS."
- **Principles applied:** P5 explicit (named the aesthetic), P3 pragmatic.
- **Rubric:** Correctness 9 · Maintainability 9 · User-fit 9.
- **Lesson:** Don't pick a single aesthetic without showing the user. The default-to-light + saved-toggle pattern is the right answer for any tool that runs in a browser tab the user keeps open.

## D-011: Map library: Leaflet

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** Need a live map. Three real options.
- **Decision:** [Leaflet](https://leafletjs.com/) + OpenStreetMap tiles + Nominatim geocoding. CDN-loaded from unpkg.
- **Alternatives:**
  - **Mapbox GL JS (rejected):** needs API key, paid tier, more polished but overkill.
  - **Google Maps (rejected):** API key + credit card, less open.
  - **Static SVG (rejected):** doesn't support live wind / safety pins / interactivity.
- **Principles applied:** P3 pragmatic, P4 DRY.
- **Rubric:** Correctness 10 · Maintainability 9 · User-fit 9.
- **Lesson:** For "live map, no API key, vanilla JS" Leaflet is unambiguously the right tool. Don't reach for Mapbox/Google unless you need 3D / vector tiles / proprietary data.

## D-012: Hero size: shrink 72px → 32px

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "resize this to be smaller, it's too big." Hero was `clamp(36px, 7vw, 72px)` which dominated the viewport.
- **Decision:** Hero `clamp(20px, 3.2vw, 32px)`. Padding tightened. Severity chip + status headline merged into the hero (was a separate row).
- **Principles applied:** P3 pragmatic.
- **Rubric:** Correctness 9 · Maintainability 10 · User-fit 8.
- **Lesson:** "Make the hero huge" is conventional UX advice but Nancy's screen real estate matters — the map + sidebar are the dominant artifacts, the hero just needs to be unmistakable.

## D-013: Evac polygon: extend west to ~Knott Ave

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "evacuation zone looks like it's missing a big area on the left." Original polygon was the four-street rectangle (Trask / Ball / Valley View / Dale) which excluded the Stanton + W Cypress portions news reports listed as included.
- **Decision:** Extended west edge from -118.0167 to -118.0420 (~Knott Ave area).
- **Alternatives:**
  - **Pull authoritative GeoJSON from ggcity.org (deferred):** they don't publish one in machine-readable form.
  - **Hand-trace the actual irregular polygon from the OC Register map (deferred):** would need ~20 vertices for accuracy.
- **Principles applied:** P3 pragmatic.
- **Rubric:** Correctness 7 (still approximate) · Maintainability 8 · User-fit 8.
- **Lesson:** When the authoritative shape isn't available, document the approximation honestly (`config.json.notes`) and ship.

## D-014: Blast radii: BLEVE-scaled, not generic

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User shared the OC Register's published blast-zone map. Original v0 radii were generic (0.25 / 0.5 / 1.0 mi).
- **Decision:** Recalibrated to **0.11 / 0.31 / 0.93 mi** derived from BLEVE / overpressure scaling for ~7,000 gal MMA ≈ ~100 tonnes TNT-equivalent. Labels updated to OCFA categories: "20 PSI overpressure" / "Moderate damage" / "Lightweight injury."
- **Alternatives:**
  - **Read exact radii off the OC Register image (couldn't):** numbers not legible in the photo.
  - **Use OCFA's published numbers (couldn't find machine-readable):** not published.
  - **BLEVE chemistry (chosen):** defensible methodology, visually matches the OC Register map.
- **Principles applied:** P1 completeness, P5 explicit (methodology in config.json notes).
- **Rubric:** Correctness 8 (defensible) · Maintainability 8 · User-fit 9.
- **Lesson:** When the authoritative numbers aren't public, derive from first principles, match against visual scale of any published artifact, and document the methodology in the config file itself so future-you knows where the numbers came from.

## D-015: Official statements: sticky right sidebar

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "I want the official statements to be scrollable on the side, rather than at the bottom." Statements were a collapsed details-element at the bottom of the page; required clicking + scrolling.
- **Decision:** Two-column grid layout: main content (left, flexible width) + sticky scrollable sidebar (right, 340px). Below 1000px viewport, sidebar stacks below.
- **Alternatives:**
  - **Statements as the hero (rejected):** user's hero is the zone verdict.
  - **Statements as a floating panel (rejected):** floaters compete with the map.
  - **Sidebar (chosen):** always-visible, doesn't compete, scrolls independently.
- **Principles applied:** P3 pragmatic, P5 explicit.
- **Rubric:** Correctness 9 · Maintainability 9 · User-fit 9.
- **Lesson:** Sidebar with `position: sticky` + independent scroll is the right pattern for "always-visible secondary information" on a wide-screen dashboard.

## D-016: URGENT vs UPDATE banner classification

- **Date:** 2026-05-24
- **Status:** Active. Replaces D-004.
- **Context:** User: "What does 'breaking news' mean?" Single BREAKING banner cried wolf for every change including new statements.
- **Decision:** Detector returns `(fires, reason, level)`. `level` ∈ `{urgent, info}`. URGENT (act-now changes: toggles + severity + injuries + resolved) → pulsing red + tab-title flash + beep. UPDATE (info changes: new statement + residents-shift) → steady amber + no beep. `breaking_level` field added to `status.json` schema.
- **Alternatives:**
  - **Single banner, suppress new-statement triggers (rejected):** loses information.
  - **Three levels (rejected):** more categories = more cognitive overhead.
- **Principles applied:** P5 explicit (named the levels clearly), P1 completeness.
- **Rubric:** Correctness 10 · Maintainability 9 · User-fit 9.
- **Lesson:** Don't use "BREAKING" as a single bucket. Classify by what action the user should take. Two levels (act vs note) is usually the right number.

## D-017: Banner clickable → scroll + highlight

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "What does it mean when there's an update and how do I see or find them?" The UPDATE banner didn't tell her *where* to look or *what* changed.
- **Decision:** Banner becomes clickable (cursor:pointer + `→ See statements` affordance on hover). Click scrolls the sidebar's internal list to top + applies a 2.5-sec yellow flash to the newest statement card. On narrow screens, scrolls the page to the sidebar first.
- **Alternatives:**
  - **Inline statement preview in banner (rejected):** breaks the consistent banner shape.
  - **Auto-expand statements on UPDATE only (rejected):** they're already visible in the sidebar; this is more about "where to look."
- **Principles applied:** P5 explicit (affordance is visible), P3 pragmatic.
- **Rubric:** Correctness 9 · Maintainability 8 · User-fit 9.
- **Lesson:** A banner that announces "something changed" without showing what changed is a useless banner. Either inline the change or make the banner a navigation affordance.

## D-018: Newest + Recent badges on statement cards

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "Make the date and time on the official statements bolder and easier to see. I want to make sure I'm able to see the most recent updates instantly."
- **Decision:**
  - Date+time bumped to 14px bold, dominant on each card.
  - Newest card: red `Newest` badge + red left-border + faint gradient.
  - Statements <2 hours old: amber `Recent` badge.
  - All cards show absolute date+time + `(N min ago)` relative time.
- **Alternatives:**
  - **Sort + style only the top card (rejected):** loses the "is this still fresh?" signal for the next-to-top.
  - **Time-bucket headers (rejected):** more visual structure than the user wants.
- **Principles applied:** P1 completeness, P5 explicit.
- **Rubric:** Correctness 9 · Maintainability 9 · User-fit 9.
- **Lesson:** "What's newest" needs visual signals at three layers: card-level (badge), list-level (sort), and time-level (relative timestamp). Any single signal is ambiguous.

## D-019: Fixed reference pins on map

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "I'd like some fixed points on the map. Trask and Harbor, Magnolia and Ellis."
- **Decision:** New `config.json.map.fixed_points` array. Rendered as circle markers with persistent tooltips. **Color-coded by current safety verdict** (green/amber/red/dark-red) so the user sees at-a-glance whether a landmark is safe right now. Auto-recolored every 5 min when wind updates.
- **Alternatives:**
  - **Static blue markers (rejected):** misses the safety angle.
  - **A side list with safety verdicts (rejected):** map is the visual; verdicts belong in context.
- **Principles applied:** P1 completeness, P5 explicit.
- **Rubric:** Correctness 9 · Maintainability 8 · User-fit 9.
- **Lesson:** When the user asks for a pin, give them a pin that *says something*. Safety-colored beats static every time for an emergency-monitoring tool.

## D-020: Geocoder bias: Garden Grove → Orange County

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** First geocoder bias was "Garden Grove, CA" which failed for "Magnolia & Talbert" (the example user gave) because Magnolia & Talbert is in Fountain Valley, not Garden Grove.
- **Decision:** Widened bias to "Orange County, CA" + added a viewbox-bounded fallback (-118.10, 33.85, -117.85, 33.65) for tough intersections. Two attempts: free-text with bias appended, then viewbox-bounded.
- **Alternatives:**
  - **Dedicated intersection geocoder (rejected):** none of the free ones are reliable.
  - **Compute intersection from two street geometries (rejected):** complex.
- **Principles applied:** P1 completeness, P3 pragmatic.
- **Rubric:** Correctness 9 · Maintainability 9 · User-fit 9.
- **Lesson:** Geocoder bias is a balance — too narrow misses, too wide pulls in wrong-region matches. Two-attempt strategy (free-text bias → viewbox fallback) covers most cases.

## D-021: Section headers for visual flow

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "The dashboard is hard to follow and make sense of." Too many distinct visual blocks competing for attention with no grouping.
- **Decision:** Added 4 section headers (`MAP · WIND · BLAST ZONES · PLUME`, `CHECK AN ADDRESS OR INTERSECTION`, `INCIDENT DETAILS`, `SOURCES`) styled as 11px uppercase tracked dim text with a 1px bottom border.
- **Alternatives:**
  - **Card-based grouping (rejected):** more chrome.
  - **Tabs (rejected):** hides information that should be visible.
- **Principles applied:** P5 explicit, P3 pragmatic.
- **Rubric:** Correctness 8 · Maintainability 9 · User-fit 7.
- **Lesson:** Section headers are cheap, semantic, and improve scan-ability without adding visual weight. Use them on any multi-section dashboard.

## D-022: Safety checker placement: below map

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** Originally placed between hero and map. Broke the visual flow (user looks at hero verdict → expects map next → got a form first).
- **Decision:** Moved safety checker BELOW the map. Natural flow: look at the map, see something, want to check a specific address.
- **Principles applied:** P3 pragmatic.
- **Rubric:** Correctness 8 · Maintainability 9 · User-fit 7.
- **Lesson:** Form placement matters. Put the form near what the user would interact with right after seeing it, not where it interrupts the visual narrative.

## D-023: Statement card design: bold meta + relative time

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** See D-018.
- **Decision:** Statement card structure (top to bottom):
  1. Datetime line: 14px bold + badge + `(N min ago)` relative time
  2. Agency line: 12px semibold
  3. Body text: 13px regular
  4. Source link: 11px small
- **Principles applied:** P5 explicit, P1 completeness.
- **Rubric:** Correctness 9 · Maintainability 9 · User-fit 9.
- **Lesson:** When the user can't tell what's newest at a glance, the fix is hierarchy — make the freshness signal the largest element on the card.

## D-024: Portfolio framing: eval suite + design log

- **Date:** 2026-05-24
- **Status:** Active.
- **Context:** User: "I'm planning to put this as a github portfolio piece. I would like all of our design, so far and moving forward, to be logged and evaluated. Use AI Eval techniques to ensure the elite analytics engineer data-quality."
- **Decision:**
  - Top-level `README.md` rewritten as a portfolio pitch (case study, architecture, lessons).
  - Operational guide moved to `USAGE.md`.
  - This `DESIGN_LOG.md` seeded retroactively + maintained going forward.
  - `eval/` directory with pytest-style behavioral tests (writer 5-state sequence, safety-compute known-input/output, geocoder live regression, JSON schema validation) + LLM-as-judge rubric files. `eval/run_all.py` produces `eval/scores.jsonl` append-only history.
  - GitHub Actions workflow runs evals on every push.
  - MIT LICENSE + .gitignore (excludes runtime artifacts).
- **Principles applied:** P1 completeness, P5 explicit.
- **Rubric:** TBD (this decision is too new to retroactively score).
- **Lesson:** TBD. Note for future-self: the highest-leverage element of "portfolio quality" is showing the *thinking* (design log + eval suite + lessons) — not just the artifact.

## D-025: Evacuation shelters — aggregate + link (hybrid)

- **Date:** 2026-05-25
- **Status:** Active.
- **Context:** User asked to include the evacuation shelter list from `ggcity.org/emergency`. Tradeoff: scrape and display vs. just link out.
- **Decision:** Hybrid. Pull 9 known shelter locations into `config.json.map.shelters` (geocoded via Nominatim, each with name, city, address, lat/lon, optional notes like "RV evacuees only"). Pin each on the map with a blue square 🏠 marker. Render a panel below the safety-checker with cards: name + address + "Directions ↗" link (opens Google Maps with destination pre-filled). Prominent CTA banner at top: "🛏️ Live list at ggcity.org/emergency — the city is the source of truth; the list below is a snapshot."
- **Alternatives:**
  - **Just link out (rejected):** loses map context (visual relationship between home, evac zone, nearest shelter) and the one-click directions.
  - **Live-scrape ggcity.org every tick (rejected):** city's HTML structure isn't documented; would break on the first redesign; also overkill for a list that changes a few times per week.
  - **Hybrid with prominent source-of-truth disclaimer (chosen):** map context + directions + offline-tolerant + clear about authoritativeness.
- **Principles applied:** P1 completeness, P5 explicit, P3 pragmatic.
- **Rubric:** Correctness 9 · Maintainability 9 · User-fit 9.
- **Lesson:** Aggregate-or-link is a false dichotomy on emergency tools. Aggregate for the workflow value (map context, directions); link prominently so users know where to verify. The CTA banner makes the relationship between snapshot + source explicit.

## D-026: News panel — generalize to videos + articles, Microlink OG fetch

- **Date:** 2026-05-25
- **Status:** Active.
- **Context:** User asked to add YouTube videos with thumbnails for major changes, then added news article URLs (ABC7 entries). Initial implementation forced everything through a video-shaped card with a play overlay — articles looked like broken videos.
- **Decision:**
  - Single `videos` field on `status.json` holds both types. `youtube_id` auto-derives `https://img.youtube.com/vi/{id}/hqdefault.jpg` thumbnail. `is_video: true` flag for non-YouTube videos. Otherwise treated as article.
  - Conditional render: play-button overlay only when video; article footer tag `📰 article`, video tag `▶ video`. Typed placeholder background (play-icon vs document-icon) when no thumbnail.
  - **Client-side Microlink fetch** (`api.microlink.io`, free tier, no API key) for article OG images. Cached 24 hours in `localStorage`. Failures cached in-memory to avoid retry storms.
- **Alternatives:**
  - **Separate `videos` and `news_articles` arrays (rejected):** schema bloat, two render paths.
  - **Server-side OG fetch in the writer (rejected):** the writer is intentionally stdlib + offline. Adding HTTP calls would broaden the failure surface.
  - **Hardcode thumbnails per article (rejected initially, then reverted to it for ABC7 entries, then dropped):** the abcotvs CDN appears to block hotlinking. Microlink proxies through their servers, sidestepping the issue.
- **Principles applied:** P5 explicit, P3 pragmatic, P1 completeness.
- **Rubric:** Correctness 9 · Maintainability 8 · User-fit 9.
- **Lesson:** Where the deterministic-vs-fragile boundary sits matters (cf. D-003). Server-side scraping in Python = brittle. Client-side OG via a hosted service = fragile but the failure mode is graceful (placeholder) and the cache amortizes the cost. Use third-party services as the "fragile path" with deterministic fallbacks.

## D-027: Writer fix — partial facts must not recompute severity

- **Date:** 2026-05-25
- **Status:** Active.
- **Context:** Operational `cat data/news_seed.json | python scripts/update_status.py` (only `videos` in the facts) silently downgraded severity to "low" because `derive_severity()` saw `residents=0`, `lifted=None`, and walked off the bottom of the rules table. The next real tick went "low → high" and fired URGENT — a false positive caused entirely by the seeding workflow.
- **Decision:** Severity is only re-derived when this tick provides one of `(evacuation_residents, evacuation_lifted, incident_resolved_iso, injuries, tank_failed, explosion_confirmed)`. Otherwise carry forward from prev snapshot. New `test_partial_facts_dont_downgrade_severity` in `eval/test_writer.py` reproduces the bug and locks the fix in.
- **Alternatives:**
  - **Require facts to always include severity-relevant fields (rejected):** breaks the partial-update use case (e.g., adding only videos).
  - **Compute severity from prev + facts merged (rejected as overkill):** would work but increases coupling; the gate-on-fields approach is simpler and explicit.
- **Principles applied:** P5 explicit, P4 DRY (don't compute when not asked).
- **Rubric:** Correctness 10 · Maintainability 9 · User-fit 9.
- **Lesson:** Derivation functions need to know what they're being asked to derive FROM. Passing them an empty/partial dict and getting back a default is a classic silent-failure bug. Gate on field presence; the writer should treat "missing input" as "keep prev," not "set to default."

## D-028: PR workflow for non-trivial changes

- **Date:** 2026-05-25
- **Status:** Active.
- **Context:** First 8 commits landed directly on `main` while iterating live during an active emergency. That was the right velocity for the build phase. Now that the repo is a portfolio piece, the workflow should look like a real engineering team's.
- **Decision:** Going forward, non-trivial changes (>3 files, new dependency, schema change, doc updates spanning multiple files) land via feature branch + GitHub PR + merge. Trivial direct-to-main is still OK for one-line fixes during active incident response.
- **Alternatives:**
  - **Always PR (rejected):** during the build phase, the PR overhead per change was wrong — 30-sec edits being PR'd would have killed momentum and added noise.
  - **Never PR (rejected):** this is a portfolio piece now; the PR-merge history is part of the artifact.
- **Principles applied:** P3 pragmatic (right tool per phase), P5 explicit.
- **Rubric:** TBD — too new to score retrospectively.
- **Lesson:** Process maturity isn't a single switch. Build phase ≠ portfolio phase ≠ team phase. Pick the lightest workflow that meets the current phase's quality bar.

## D-029: Hero address check — move safety checker into always-visible hero

- **Date:** 2026-05-25
- **Status:** Active.
- **Context:** Three converging lenses identified the same friction point. The address-safety checker — the most personal feature ("am I safe?") — was buried in the Check tab, requiring users to discover and navigate to it. During the conduit-strategy rework, office-hours analysis confirmed the problem from safety, marketing, and builder perspectives simultaneously.
- **Decision:** Move the address-check widget into the always-visible hero section so it's the first interactive element a user encounters. Keep the Check tab as an expanded detail view (full zone explanation, methodology notes, source links). Tabbed architecture preserved for secondary content.
- **Alternatives:**
  - **A) Keep tabs as-is (rejected):** hides the most personal feature behind navigation. A frightened, limited-English-speaking elder shouldn't need to discover a tab to learn if their home is safe.
  - **B) Single scroll page removing all tabs (rejected):** scroll fatigue on mobile; overwhelming for the billboard-test audience. Loses the technical sophistication signal for the portfolio.
  - **C) Hybrid with collapsible sections (rejected):** collapsibles have their own discoverability problem — users don't know what's inside until they click. Same failure mode as tabs, just repackaged.
  - **D) Keep tabs + hero check (chosen):** smallest change that addresses the core safety concern. Answers the user's primary question ("am I safe?") with zero navigation friction while preserving the tabbed architecture for secondary information depth.
- **Principles applied:** P1 completeness (primary user need answered without navigation), P5 explicit (the answer is visible, not hidden), P3 pragmatic (minimal structural change).
- **Rubric:**
  - Correctness: 9 (directly solves the "hidden primary feature" problem)
  - Maintainability: 8 (hero section grows slightly; tab remains as detail view — clean separation)
  - User-fit: 9 (conduit mission = answer with minimum friction; three independent lenses converged)
- **Lesson:** When safety, marketing, and builder instincts all point at the same answer, the decision is load-bearing — not a coincidence. The "coolest version answers before you ask" framing is the same thing as "conduit with minimum friction" and "billboard test for a frightened elder." Convergence across lenses = high-confidence signal.

---

## Decision template (for future entries)

Copy this block, fill it in, add a row to the summary table.

```markdown
## D-NNN: <one-line title>

- **Date:** YYYY-MM-DD
- **Status:** Active | Superseded → [D-XXX](#d-xxx) | Reverted → [D-XXX](#d-xxx) | Deferred | Rejected
- **Context:** what triggered the decision
- **Decision:** what we did
- **Alternatives:**
  - **Option A (rejected):** why
  - **Option B (rejected):** why
  - **Option C (chosen):** why
- **Principles applied:** P1 completeness, P2 boil lakes, P3 pragmatic, P4 DRY, P5 explicit, P6 bias to action
- **Rubric:**
  - Correctness: N (does it solve the actual problem?)
  - Maintainability: N (would another engineer understand + extend it?)
  - User-fit: N (did the user accept it?)
- **Lesson:** what to remember next time
```
