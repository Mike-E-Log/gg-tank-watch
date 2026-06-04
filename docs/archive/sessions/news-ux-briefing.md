# News / History / Alerts UX Spec — distribution-readiness (deep session)

You are running the **News-UX** workstream. Other workstreams run concurrently (Legal → `docs/LEGAL.md`, Data-Quality → `docs/DATA_QUALITY.md`). You do NOT touch their files. You own ONE deliverable: `docs/NEWS_UX_SPEC.md` — a **specification**, not code.

## Project context (self-contained)

`gg-tank-dashboard` is an **unofficial, volunteer-built, free** single-page web dashboard for the **Garden Grove, California methyl-methacrylate (MMA) chemical-tank incident** at GKN Aerospace, 12122 Western Ave (began 2026-05-21; ~50,000 residents evacuated, heart of Little Saigon — large Vietnamese-speaking population). It is a single static page (`dashboard.html`, vanilla JS + Leaflet, no build step) on Vercel (currently `noindex`, not yet distributed). It polls `status.json` (live incident facts written by a data-sync pipeline) and `config.json` (map/geocoder config). It shows: a live map (evac polygon + facility), an address "what should I do?" safety check, a **news/video panel**, and official agency statements.

This workstream exists because the **news/alerts/history experience needs design attention** before distribution. The dashboard currently renders a news panel (articles + videos with conditional play overlay, client-side OG-image thumbnails via Microlink) and surfaces breaking-event detection (the writer maintains `breaking_events.jsonl` + an ntfy.sh hook). But there is **no designed spec** for: how breaking alerts surface to a frightened user, how news is prioritized/deduped/dated, and how a user reviews the **history** of how the incident evolved.

## Read first (READ-ONLY — do not edit any of these)
1. `~/.claude/CLAUDE.md` (global)
2. This briefing
3. `dashboard.html` — study the existing news panel render path, status polling, and how statements/news are currently shown. **READ ONLY. This file is owned by another contributor (Nancy) and is off-limits to you.**
4. `docs/SPEC.md` — product intent
5. `docs/DISTRIBUTION.md` — audience (displaced families, elderly Vietnamese speakers); your UX must serve them
6. `config.json` if present — feature flags / news config
7. The `status.json` schema as consumed by `dashboard.html` and produced by the writer (`scripts/update_status.py`) — read both to learn the exact fields available (statements, sources, severity, breaking flags, timestamps).

## Primary goal
Produce `docs/NEWS_UX_SPEC.md`: an implementation-ready UX spec for the news, alerts, and history experience — something Nancy can build into `dashboard.html` later without re-deciding the design.

## The work — cover at minimum
1. **Alerts (breaking events).** How a newly-detected breaking event surfaces to a user who may be scared and on a phone: visual treatment, placement, dismissal, dedupe, "what changed since I last looked." Respect the brand guardrails (unofficial; never promise safety / "an toàn"; always point to official sources). Define the states (no-alert / new-alert / acknowledged) and the data fields each needs from `status.json` / `breaking_events.jsonl`.
2. **News panel.** Prioritization & ordering (recency vs. source authority vs. relevance), source-credibility cues, dedupe across outlets, date/time display (relative + absolute, timezone), the article-vs-video distinction, graceful states (loading, no-news, thumbnail-fetch-failed). Bilingual EN/VI considerations (label placeholders for Nancy's VI, never invent VI strings).
3. **History / timeline.** How a user reviews the incident's evolution — a timeline of status changes & breaking events over time. Specify the data source (does the pipeline already persist history? if not, specify the minimal append-only record the writer would need to emit — as a *recommendation* to the Data-Quality stream, flagged, not implemented). Define the view: granularity, what each entry shows, how it ties to the map/severity.
4. **Provenance & trust.** Every news/alert item must show where it came from and when — anti-misinformation cues, "last updated" freshness indicator, stale-data treatment (the pipeline intentionally lets `status.json` go visibly stale rather than fresh-stamp on failure — design for that).
5. **Accessibility & mobile.** Large text, color-not-only severity, screen-reader order, one-handed phone use, low-bandwidth (shelter wifi) behavior.
6. **Component inventory + acceptance criteria.** A concrete list of UI components/states with acceptance criteria, so the spec is buildable and testable.

## What "done" looks like
- `docs/NEWS_UX_SPEC.md` exists with: alerts spec, news-panel spec, history/timeline spec, provenance/trust rules, a11y/mobile rules, a component+state inventory with acceptance criteria, and a short "open questions for the user" list.
- ASCII wireframes or clear structural sketches where layout matters (you cannot produce images — describe structure precisely).
- `.orchestra/news-ux/status.json` = `{ "phase": "complete", "progress": 100, ... }`
- `.orchestra/news-ux/log.md` has a final summary.

## Hard constraints (NON-NEGOTIABLE)
- **DO NOT edit `dashboard.html`** — it is Nancy's serial lane; you only SPEC changes to it.
- DO NOT touch any file except `docs/NEWS_UX_SPEC.md` and `.orchestra/news-ux/*`. Do NOT edit `docs/LEGAL.md`, `docs/DISTRIBUTION.md`, `docs/DATA_QUALITY.md`, `scripts/`, `eval/`, or `.orchestra/STATE.json`.
- Respect the brand guardrails: unofficial, never promise safety, always defer to official sources, never invent Vietnamese strings (use `[VI: ...]` placeholders for Nancy).
- This audience is vulnerable and in an active emergency — design nothing that exploits urgency or could amplify panic/misinformation.
- Do NOT invent news sources, URLs, or dates. If you need example content, label it clearly as illustrative.
- Work autonomously — do NOT block waiting for user input. If you use a design skill, auto-proceed with its recommended path; do not stall on interactive prompts.
- Self-execute; do not ask the user to paste commands.
- Do NOT run `git commit` or `git push` — the orchestrator commits your output.

## Out of scope
- Implementing the UI (that's later dashboard.html work, Nancy's lane). You only SPEC.
- Data-pipeline changes — if history requires new persisted data, RECOMMEND it (flagged), do not implement; the Data-Quality stream owns the pipeline design.

## Open questions to flag, NOT resolve
- Whether history requires a new pipeline output (coordinate via your spec's recommendation; orchestrator routes to Data-Quality).
- Whether to surface a "subscribe to alerts" (push/SMS) path given the no-local-machine, static-site architecture.

---

## Wiki Write Protocol
Maintain two files in `.orchestra/news-ux/` throughout:

**status.json** — update at every phase transition:
```json
{ "phase": "<current phase>", "progress": 0, "blockers": [], "last_action": "<one line>", "files_touched": ["docs/NEWS_UX_SPEC.md"], "timestamp": "<ISO8601 UTC>" }
```
**log.md** — append after each significant action (`## HH:MM — <phase>` + bullets). Write a final summary entry when done.
