# Research — Premium Emergency Dashboard UI/UX + Design Decisions (deep session)

You are running the **Research** workstream. 3 other workstreams run concurrently ("data-pipeline" on `config.json, timeline.json, scripts/, eval/`; "portfolio" on `README.md, docs/`; "dashboard" is QUEUED and will consume your findings). You do NOT touch their files.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `.orchestra/CONTRACTS.md` — cross-cutting contracts. READ ONLY.
4. `docs/sessions/data-source-audit.md` — the incident timeline and source data
5. `docs/sessions/mobile-ux-assessment.md` — prior mobile UX research
6. `docs/sessions/viet-design-report.md` — Son Mai Authority design direction
7. `DESIGN.md` — current design system
8. `dashboard.html` — current implementation (skim structure, CSS, JS)

## Primary goal

Produce research-backed design direction for transforming GG Tank Watch into a premium, no-scroll desktop dashboard (1920x1080) and premium mobile experience that maximizes community help for ~50,000 evacuated residents during a chemical emergency. This project is also an Anthropic Fellows Program portfolio piece.

## File ownership

**You OWN (exclusive write access):**
```
docs/sessions/ux-research-findings.md (new — your primary deliverable)
```

**DO NOT TOUCH:**
```
config.json, timeline.json, scripts/, eval/  → data-pipeline
dashboard.html                               → dashboard (queued)
README.md, docs/AI_CONTROL_ARCHITECTURE.md   → portfolio
.orchestra/CONTRACTS.md                      → Orchestrator ONLY
.orchestra/orchestration.json                → Orchestrator ONLY
```

## The work

### Phase 1 — Deep research on premium emergency dashboard UI/UX

Use WebSearch and WebFetch to research:

1. **Emergency dashboard design patterns** — How do the best emergency information systems present data? Look at: FEMA.gov incident pages, CDC dashboard patterns, Japan's NHK disaster broadcasts (known for excellent information design), Australia's emergency.vic.gov.au, UK Met Office severe weather displays. What makes them trustworthy AND usable under stress?

2. **No-scroll dashboard layouts** — How do operations dashboards (Grafana, Datadog, Bloomberg Terminal, flight status boards, hospital patient tracking) organize dense information in a fixed viewport? What patterns work for 1920x1080?

3. **Premium UI/UX in safety-critical contexts** — What makes a UI feel "expensive" and trustworthy in a high-stakes context? Research Apple Health emergency cards, airline safety apps, financial trading terminals. The aesthetic must convey authority and care, not just prettiness.

4. **Mobile emergency UX** — How do the best emergency apps handle the same information on mobile? Tokyo's earthquake early warning system, Israel's Home Front Command app, FEMA app. What's the mobile-specific premium feel?

5. **Information architecture for emergency dashboards** — How should Map/Updates/Resources/About be arranged? Simultaneous panels vs. tabs? What does research say about cognitive load during emergencies?

6. **Cultural sensitivity in emergency design for Vietnamese communities** — Any research on emergency communication design for Vietnamese diaspora? Cultural considerations for trustworthiness signals?

### Phase 2 — Cross-vendor judges on two design decisions

Evaluate these two decisions and recommend the best option with reasoning:

**Decision 1: Check section scope**
The dashboard has a hero address checker (always visible at top) AND a separate Check tab with the same functionality. Options:
- A) Remove the Check tab only (hero stays, reduce from 4 tabs to 3)
- B) Remove both check UIs (no address lookup at all)
- C) Keep both

Consider: The hero checker is the primary user action ("am I in the zone?"). The Check tab duplicates it. Removing it simplifies the tab bar and makes room for Resources + About tabs. BUT — does removing it reduce accessibility for users who discover the app through the tab bar?

**Decision 2: Eval test handling for removed map points**
Two map points (Magnolia & Ellis, Trask & Harbor) are being removed from config.json. They're also referenced in 4 eval tests. Options:
- A) Remove both config entries AND their eval tests (clean removal)
- B) Remove config entries but keep eval tests (regression coverage)
- C) Remove config entries, replace eval tests with different intersections

Consider: The eval tests verify geocoder accuracy for those specific intersections. If the intersections are removed from the map, the tests still verify geocoder functionality at those coordinates. But the tests would be testing intersections the dashboard no longer displays.

### Phase 3 — Synthesize findings

Write `docs/sessions/ux-research-findings.md` with:

1. **Desktop layout recommendation** — panels vs. tabs vs. hybrid, with evidence
2. **Design aesthetic recommendation** — which style (Apple-clean, news-authority, data-dashboard, or hybrid) best serves a bilingual emergency dashboard, with evidence
3. **Incident status placement** — always-visible strip vs. tab, with evidence
4. **Mobile layout recommendation** — how to handle the same content on mobile
5. **Premium UI/UX patterns** — specific techniques (typography, spacing, animation, micro-interactions) that make it feel expensive without adding cognitive load
6. **Cross-vendor judges verdicts** — recommended decisions on check section + eval tests
7. **Community-help information architecture** — how Resources tab should be organized for maximum findability under stress

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- DO NOT write to shared docs directly
- Treat `.orchestra/CONTRACTS.md` as authoritative; READ it, never write it
- Son Mai Authority theme (celadon/ivory/Be Vietnam Pro) is the foundation — enhance, don't replace
- Conduit pattern — no directives in any example copy
- Safety constraints from CLAUDE.md are binding

## What "done" looks like

- `docs/sessions/ux-research-findings.md` written with all 7 sections above
- Each recommendation backed by at least 2 external references
- Verdicts on both cross-vendor-judges decisions with reasoning
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Implementing any changes to dashboard.html → dashboard stream
- Creating timeline.json → data-pipeline stream
- Editing README or docs → portfolio stream
- Shared doc updates → Orchestrator

## On completion

1. Mark your task `completed` via `TaskUpdate`
2. `SendMessage` the orchestrator lead a one-line summary of what you accomplished
3. The orchestrator reads your transcripts for full visibility — no journal needed
