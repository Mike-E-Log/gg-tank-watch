# Legal & Liability Research — distribution-readiness (deep session)

You are running the **Legal** workstream. One other workstream runs concurrently (Marketing on `docs/DISTRIBUTION.md`). You do NOT touch its files. You own legal research only.

## Project context (self-contained)

`gg-tank-dashboard` is an **unofficial, volunteer-built, free** single-page web dashboard for the **Garden Grove, California methyl-methacrylate (MMA) chemical-tank incident** at GKN Aerospace, 12122 Western Ave (began 2026-05-21; ~50,000 residents evacuated). It is a static HTML + vanilla-JS page deployed on Vercel (org: `ggtankwatch`), currently `noindex` and **not yet distributed**. It shows: a Leaflet map with evac zone + blast/plume estimates; a "check your address" safety tool (OpenStreetMap Nominatim geocoding + client-side risk math); aggregated news headlines, videos (YouTube embeds), and official agency statements pulled from a `status.json` feed. Two volunteers run it: Mike and Nancy (who is producing a Vietnamese translation). The team's standing posture: highest-quality info, **deliberate** distribution, **never promise safety**, always point to official sources (ggcity.org/emergency, OCFA). They deliberately avoid the words "official", "safe", and the Vietnamese "an toàn".

**The trigger for this research:** they want to distribute it to a vulnerable, largely Vietnamese ("Little Saigon") community — starting with Nancy's parents, potentially wider. Before that, they need to understand the legal/liability landscape and how to mitigate it.

## Read first
1. `~/.claude/CLAUDE.md` (global engineering contract)
2. This briefing

## Primary goal
Produce `docs/LEGAL.md`: a well-sourced map of the legal/liability risks of publicly distributing this tool, plus **concrete, actionable mitigations** (framing, disclaimers, a draft Terms-of-Use / disclaimer) the team can implement — clearly marked as research, not legal advice.

## The work — use the /deep-research skill
Invoke `/deep-research` and investigate, with citations, for a free unofficial emergency-information web tool operated by private volunteers in California:

1. **Liability for inaccurate or stale safety information** — negligence / duty of care; whether publishing safety info creates an assumed duty; how disclaimers and "informational only" framing affect this.
2. **Volunteer / Good Samaritan protections** — California Good Samaritan statutes and the federal Volunteer Protection Act (1997): do they extend to *information* tools, or only hands-on aid? What are the limits (gross negligence, recklessness)?
3. **Why avoiding "official" / "safe" matters legally** — misrepresentation, false association with a government/emergency authority, assumed-duty escalation. Validate the team's instinct with legal basis.
4. **Disclaimers & Terms of Use** — recommended language and enforceability of limitation-of-liability / "no warranty" / "verify with official sources" clauses for a free public tool. Provide a usable DRAFT.
5. **Content aggregation** — republishing news headlines + official statements: copyright/fair-use boundaries (headline + link + short quote vs. full reproduction); defamation exposure from aggregating others' reporting; safe-harbor considerations.
6. **Third-party service terms** — OpenStreetMap/Nominatim usage policy (rate limits, attribution, bulk-use rules), Leaflet license, YouTube embed ToS, Microlink ToS — compliance obligations for a public deployment.
7. **Accessibility** — ADA Title III / Section 508 / WCAG exposure for a public-facing civic tool, and what minimal compliance looks like.
8. **Privacy (conditional)** — IF a messaging/reunification feature is later added: CCPA/CPRA, and minors (COPPA) implications. Flag as forward-looking.
9. **Branding / domains** — using a name like "ggtankwatch" / avoiding implication of official status; basic trademark hygiene.

## What "done" looks like
- `docs/LEGAL.md` exists containing: (a) a **prominent top banner**: "This is research, NOT legal advice — consult a licensed California attorney before public distribution."; (b) findings per topic with citations/links; (c) a **risk matrix** (each risk: likelihood × severity × mitigation); (d) a concrete **DRAFT disclaimer / Terms-of-Use** block ready to adapt; (e) a short "minimum bar before distributing" checklist.
- `.orchestra/legal/status.json` set to `{ "phase": "complete", "progress": 100, ... }`
- `.orchestra/legal/log.md` has a final findings summary.

## Hard constraints (NON-NEGOTIABLE)
- This is RESEARCH, not legal advice — say so explicitly and repeatedly; recommend a real attorney for anything load-bearing.
- Cite real sources you actually retrieved. Never fabricate a statute, case, or URL.
- Self-execute everything; do not ask the user to paste commands.
- DO NOT touch any file except `docs/LEGAL.md` and `.orchestra/legal/*`. In particular do NOT edit `docs/DISTRIBUTION.md` (Marketing's), `dashboard.html`, `config.json`, `status.json`, or `.orchestra/STATE.json` (orchestrator only).
- Do NOT run `git commit` or `git push` — the orchestrator commits your output.

## Out of scope
- Distribution channels / marketing messaging → Marketing workstream.
- Actually implementing disclaimers in the UI → future dashboard work (Nancy's/Mike's lane). You only DRAFT the language.

## Open questions to flag, NOT resolve
- Whether the team should register a formal entity (nonprofit/LLC) before distributing — surface considerations, don't decide.
- Whether to add an explicit "report an error" channel as a liability mitigation.

---

## Wiki Write Protocol
Maintain two files in `.orchestra/legal/` throughout:

**status.json** — update at every phase transition:
```json
{ "phase": "<current phase>", "progress": 0, "blockers": [], "last_action": "<one line>", "files_touched": ["docs/LEGAL.md"], "timestamp": "<ISO8601 UTC>" }
```
**log.md** — append after each significant action (`## HH:MM — <phase>` + bullets). Write a final summary entry when done.
