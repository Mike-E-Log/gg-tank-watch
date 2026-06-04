# Distribution / Marketing Strategy — distribution-readiness (deep session)

You are running the **Marketing** workstream. One other workstream runs concurrently (Legal on `docs/LEGAL.md`). You do NOT touch its files. You own distribution strategy only.

## Project context (self-contained)

`gg-tank-dashboard` is an **unofficial, volunteer-built, free** single-page web dashboard for the **Garden Grove, California methyl-methacrylate (MMA) chemical-tank incident** at GKN Aerospace, 12122 Western Ave (began 2026-05-21; ~50,000 residents evacuated). Garden Grove is the heart of **Little Saigon** — a large share of the affected population is Vietnamese-speaking. It is a static web page on Vercel (currently `noindex`, **not yet distributed**), showing a live map (evac zone + blast/plume estimates), an address-based "what should I do?" safety check, aggregated news/video, and official agency statements. Two volunteers run it: Mike (***REDACTED***) and Nancy (producing the Vietnamese translation). A Vietnamese-language doorway domain `ggkhancap.org` ("GG khẩn cấp" = GG Emergency) and canonical `ggtankwatch.org` were scoped (not yet bought).

**The trigger for this work:** they want to distribute it responsibly — starting with **Nancy's parents**, potentially to the wider Vietnamese and broader affected community.

## Read first
1. `~/.claude/CLAUDE.md` (global)
2. This briefing

## Non-negotiable guardrails (the brand's posture — bake these into every recommendation)
- **Unofficial.** Never present it as an official or government source. Always direct people to official sources (ggcity.org/emergency, OCFA) as the authority.
- **Never promise safety.** No "safe" / "an toàn" reassurance language. Use guarded, situational framing ("watch", "current status", "what we know").
- **Quality over reach.** The team will NOT push for broad distribution until readiness gates are met (verified Vietnamese translation, legal review, reliable data freshness). Your plan must be **phased** and tied to those gates.
- **Bilingual.** English + Vietnamese, with the Vietnamese community as a first-class audience, not an afterthought.
- A **legal review is in progress in parallel** (`docs/LEGAL.md`); assume distribution messaging must respect whatever disclaimers/framing it recommends.

## Primary goal
Produce `docs/DISTRIBUTION.md`: a responsible, phased distribution/GTM strategy for reaching Nancy's parents → the Little Saigon community → potentially wider, without overpromising.

## The work — use the /chief-marketing-officer skill
Invoke `/chief-marketing-officer` to diagnose and produce a strategy. Cover at minimum:
1. **Stage + audience diagnosis** — who exactly (displaced parents, elderly Vietnamese speakers, families split across shelters), their information needs, trust dynamics, and where they already look for info.
2. **Channels for Little Saigon** — Vietnamese community orgs, churches/temples, schools & PTAs, Zalo, Facebook community groups, Vietnamese-language local media (e.g., Người Việt, Việt Báo, SBTN), trusted community figures. Word-of-mouth via the parent network.
3. **Messaging guidelines** — how to describe the tool truthfully and compellingly under the guardrails above (unofficial, no safety promise, points to official sources). Provide example bilingual blurbs (EN + a placeholder for VI, to be verified by Nancy).
4. **Phased rollout** — concrete phases (e.g., private link to family/trusted testers → community-leader soft launch → wider) each **gated** on readiness criteria (verified VI, legal sign-off, data-freshness live, accessibility pass).
5. **Trust & anti-misinformation** — how to build credibility and avoid being perceived as rumor/misinformation in a high-stakes emergency; provenance/transparency cues to surface.
6. **Metrics** — what success looks like at each phase without growth-hacking a safety tool.
7. **Risks** — reputational/safety risks of distribution and how to mitigate.

## What "done" looks like
- `docs/DISTRIBUTION.md` exists with: stage/audience diagnosis, channel plan, messaging guidelines + example blurbs, a **phased rollout tied to explicit readiness gates**, metrics, risks, and open questions for the user.
- `.orchestra/marketing/status.json` set to `{ "phase": "complete", "progress": 100, ... }`
- `.orchestra/marketing/log.md` has a final summary.

## Hard constraints (NON-NEGOTIABLE)
- Respect every guardrail above — if a tactic conflicts with "unofficial / no safety promise / quality-first", drop it.
- This audience is vulnerable and in an active emergency — recommend nothing manipulative, urgency-exploiting, or that could spread panic/misinformation.
- Cite sources for any channel/audience claims you can; flag assumptions clearly.
- Self-execute; do not ask the user to paste commands.
- DO NOT touch any file except `docs/DISTRIBUTION.md` and `.orchestra/marketing/*`. Do NOT edit `docs/LEGAL.md` (Legal's), `dashboard.html`, or `.orchestra/STATE.json` (orchestrator only).
- Do NOT run `git commit` or `git push` — the orchestrator commits your output.

## Out of scope
- Legal/liability analysis → Legal workstream (you may reference its existence, not write it).
- Implementing UI copy → future dashboard work. You only RECOMMEND messaging.

## Open questions to flag, NOT resolve
- Whether/when to buy the domains (`ggtankwatch.org`, `ggkhancap.org`) — surface the distribution implications, don't decide.
- Whether to coordinate with any official body before community distribution.

---

## Wiki Write Protocol
Maintain two files in `.orchestra/marketing/` throughout:

**status.json** — update at every phase transition:
```json
{ "phase": "<current phase>", "progress": 0, "blockers": [], "last_action": "<one line>", "files_touched": ["docs/DISTRIBUTION.md"], "timestamp": "<ISO8601 UTC>" }
```
**log.md** — append after each significant action (`## HH:MM — <phase>` + bullets). Write a final summary entry when done.
