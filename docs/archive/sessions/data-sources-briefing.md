# Data Sources & Incident Timeline — Compile the full timeline and audit news aggregation completeness (deep session)

You are running the **data-sources** workstream. 2 other workstreams run concurrently ("mobile-ux-audit" on `docs/sessions/mobile-ux-assessment.md`, "viet-design" on `docs/sessions/viet-design-report.md`). You do NOT touch their files. You own your report only.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `status.json` — current incident data (official statements, sources checked, videos, schools closed)
4. `scripts/gather_facts.py` — the data gathering pipeline (uses Anthropic API + web_search tool to find current status)
5. `dashboard.html` — read the News tab rendering section to understand how data is displayed (READ-ONLY)

## Primary goal

Two deliverables:
1. **Full incident timeline** from Day 1 (May 21, 2026) through today (May 25, 2026) — every major official statement, news development, and key event, with sources and timestamps
2. **Data source completeness audit** — identify ALL major data sources covering this incident and assess which ones we're missing in our aggregation

The user explicitly wants: "the major/official information from the beginning so we have the full timeline."

## File ownership

**You OWN (exclusive write access):**
```
docs/sessions/data-source-audit.md
```

**DO NOT TOUCH:**
```
docs/sessions/mobile-ux-assessment.md     → mobile-ux-audit
docs/sessions/viet-design-report.md       → viet-design
dashboard.html                             → READ-ONLY
status.json                                → READ-ONLY
scripts/gather_facts.py                    → READ-ONLY
.orchestra/orchestration.json              → Orchestrator ONLY
```

## The work

### Phase 1 — Compile the full incident timeline

Use WebSearch extensively to build a comprehensive, chronological timeline of the GG Tank incident. The incident started on May 21, 2026 (Wednesday evening) when a methyl methacrylate (MMA) storage tank at GKN Aerospace, 12122 Western Ave, Garden Grove, CA began leaking.

For each event, capture:
- **Timestamp** (ISO 8601 UTC)
- **Event description** (factual, one sentence)
- **Source** (agency or outlet + URL)
- **Category**: one of [initial_response, evacuation, tank_status, official_statement, government_action, school_closure, air_quality, community_impact, media_coverage]

Key events to research and document (search for each):
- Initial leak discovery and first responder arrival (May 21 evening)
- First evacuation orders (when, how many, what area)
- Evacuation zone expansions (each expansion with new boundaries)
- OCFA press conferences and official statements (every one)
- OC Sheriff statements and coordination
- Garden Grove city emergency declarations
- Governor Newsom's state of emergency declaration
- Federal emergency declaration request
- EPA and SCAQMD air quality monitoring deployments
- Tank temperature readings over time (the tank was heating)
- BLEVE threat assessment timeline
- Crack discovery in the tank (major development)
- BLEVE threat elimination announcement
- School district closures (which districts, which schools, when)
- Shelter openings and locations
- National media coverage milestones (when did NYT, CNN, national outlets pick up the story?)
- Community response and volunteer efforts
- Vietnamese-language community information efforts
- Any injuries or health reports
- Timeline of hazmat/technical response (cooling operations, pressure relief)

### Phase 2 — Audit current data sources

Review `status.json` and `scripts/gather_facts.py` to understand what sources we currently check:
- Current `sources_checked` in status.json
- Sources the gather_facts prompt tells Claude to prioritize
- What's in the `official_statements` array
- What's in the `videos` array

### Phase 3 — Identify missing sources

Use WebSearch to find ALL outlets and agencies covering this incident. Categorize:

**Official/Government sources:**
- OCFA (Orange County Fire Authority) — ocfa.org
- OC Sheriff — ocsheriff.gov
- Garden Grove city — ggcity.org/emergency
- Cal OES (Governor's Office of Emergency Services)
- US EPA Region 9
- SCAQMD (South Coast Air Quality Management District)
- CDC/ATSDR (Agency for Toxic Substances)
- OSHA
- OC Health Care Agency
- Orange County Board of Supervisors
- Congressional representatives (local)

**Major news outlets:**
- Local: ABC7 (KABC), NBC Los Angeles (KNBC), KTLA, KCBS/KCAL, FOX 11 (KTTV), LA Times, OC Register, Daily Pilot, Voice of OC
- National: ABC News, NBC News, CBS News, CNN, Fox News, AP, Reuters, NYT, Washington Post, TIME
- Vietnamese-language: Nguoi Viet Daily News, Viet Bao, VietnamNet, other Vietnamese-American media in Orange County

**Specialized:**
- Weather/environment: NOAA, NWS, AirNow.gov
- Emergency management: FEMA, ReadyOC.org
- School districts: GGUSD, Westminster SD, Magnolia SD, Savanna SD, OCDE
- Social media: Reddit (r/orangecounty, r/gardengroveca), Twitter/X official accounts, Nextdoor
- Wikipedia article on the incident

**Data feeds:**
- AirNow API (air quality index)
- NOAA weather observations
- USGS (any seismic concerns?)

### Phase 4 — Write comprehensive report

Write `docs/sessions/data-source-audit.md` with:

```markdown
# Data Sources & Incident Timeline — GG Tank Watch

## Executive Summary
[2-3 sentences: timeline completeness + source gaps identified]

## Complete Incident Timeline

### Day 1 — Wednesday, May 21, 2026
[Events with timestamps, sources, categories]

### Day 2 — Thursday, May 22, 2026
[Events]

### Day 3 — Friday, May 23, 2026
[Events]

### Day 4 — Saturday, May 24, 2026
[Events]

### Day 5 — Sunday, May 25, 2026 (today)
[Events]

## Current Data Sources (what we have)
[From status.json and gather_facts.py]

## Source Coverage Audit

### Official Sources
| Source | Currently Tracked | Gap | Priority |
|--------|------------------|-----|----------|

### News Outlets
| Source | Currently Tracked | Gap | Priority |

### Vietnamese-Language Media
| Source | Currently Tracked | Gap | Priority |

### Data Feeds / APIs
| Source | Currently Tracked | Gap | Priority |

## Recommendations
### High-Priority Source Additions
### Medium-Priority Source Additions
### Nice-to-Have Sources

## Integration Notes
[How new sources could be added to the gather_facts.py pipeline]
[Format compatibility with current status.json schema]
```

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- DO NOT modify status.json, gather_facts.py, or dashboard.html — this is a research stream
- Every timeline event MUST have a source URL. Do not fabricate events, quotes, or timestamps.
- Cross-reference multiple sources for key facts (evacuation numbers, tank readings, official statements)
- Vietnamese-language media sources are especially important given the community demographics
- Use ISO 8601 UTC timestamps consistently
- Flag uncertainty explicitly — if a timestamp is approximate, mark it as such

## What "done" looks like

- `docs/sessions/data-source-audit.md` written with all sections complete
- Chronological timeline from May 21-25 with sourced events
- Complete source coverage audit table
- Prioritized recommendations for source additions
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Mobile UX evaluation → mobile-ux-audit workstream
- Vietnamese cultural design → viet-design workstream
- Code implementation — this stream produces research only
- Actually modifying the data pipeline — recommendations only
