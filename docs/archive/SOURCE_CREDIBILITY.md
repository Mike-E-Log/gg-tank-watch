# Source Credibility Framework: GG Tank Watch

## Purpose

GG Tank Watch aggregates information from multiple sources. This document defines
how sources are evaluated for credibility and prioritized in the data pipeline.

## Evaluation Criteria (1-5 each)

| Criterion | 1 (Low) | 5 (High) |
|-----------|---------|----------|
| Authority | Blog, social media | Official agency, primary source |
| Editorial standards | No fact-checking | Professional editorial process |
| Track record | New/unverified | Decades of accurate reporting |
| Timeliness | Delayed rewrites | First to report verified facts |
| Community reach | Niche audience | Reaches affected population directly |

## Source Tiers

### Tier 1: Official Agencies (Score 20-25)

These agencies produce the information. They are the primary authority.

| Source | Score | Rationale |
|--------|-------|-----------|
| OCFA (Orange County Fire Authority) | 25 | Incident command authority |
| OC Sheriff | 24 | Evacuation enforcement authority |
| City of Garden Grove Emergency | 24 | Municipal emergency management |
| Cal OES / Governor's Office | 23 | State emergency coordination |
| US EPA Region 9 | 23 | Air quality monitoring authority |
| SCAQMD | 22 | Regional air quality authority |

### Tier 2: Established Primary News (Score 15-19)

Professional outlets with reporters on scene and editorial standards.

| Source | Score | Rationale |
|--------|-------|-----------|
| ABC7 Los Angeles (KABC) | 19 | Primary local TV, live updates blog |
| NBC Los Angeles (KNBC) | 19 | Primary local TV, live updates blog |
| KTLA | 18 | Detailed timeline coverage |
| CBS Los Angeles (KCBS) | 18 | DA investigation coverage |
| LA Times | 19 | Major regional paper, investigative |
| OC Register | 18 | Primary Orange County paper |
| Associated Press | 19 | Wire service, strict fact-checking |
| CNN | 17 | National, EPA Zeldin interview |
| Nguoi Viet Daily News | 18 | Largest Vietnamese-American daily (45+ years), professional editorial, headquartered in Westminster OC. Critical for reaching ~40% of affected population. |

### Tier 3: Reputable Secondary (Score 10-14)

Reliable outlets with less direct coverage of this incident.

| Source | Score | Rationale |
|--------|-------|-----------|
| Fox 11 Los Angeles | 14 | Local TV, less primary coverage |
| ABC News national | 14 | National desk, wire-fed |
| CBS News national | 14 | National desk |
| NPR | 15 | Two articles, trusted |
| Voice of OC | 13 | Nonprofit OC journalism |
| VnExpress International | 12 | Vietnamese community impact reporting |
| SBTN | 11 | Vietnamese TV network in OC |
| Vien Dong Daily News | 11 | Vietnamese-language daily |

### Excluded

Social media (Reddit, Twitter/X, Nextdoor), unverified blogs, forums, opinion sites.
Wikipedia is useful as a secondary cross-reference but not a primary source.

## Vietnamese-Language Media Inclusion

Garden Grove / Little Saigon is the largest Vietnamese community outside Vietnam.
Vietnamese-language sources are included because:

1. They reach residents who may not read English outlets
2. They carry unique community-impact information (private sheltering, community mutual aid, Buddhist temple openings)
3. Nguoi Viet Daily News meets Tier 2 editorial standards (professional newsroom since 1978)

## How This Is Applied

The `scripts/gather_facts.py` pipeline instructs Claude to:
1. Search Tier 1 sources first (official agencies)
2. Cross-check with Tier 2 sources (established news)
3. Include Tier 3 when they carry unique information
4. Never use excluded sources as primary evidence
