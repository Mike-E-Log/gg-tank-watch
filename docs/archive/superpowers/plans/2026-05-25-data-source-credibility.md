# Data Source Expansion + Credibility Framework — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the gather_facts.py pipeline to check 12+ high-credibility sources (including Vietnamese-language media) with a tiered credibility framework, ensuring the dashboard's news feed aggregates the most trustworthy and comprehensive coverage of the GG Tank incident.

**Architecture:** Add a `SOURCE_CREDIBILITY` constant documenting the tiered source hierarchy. Update the gatherer prompt to name these sources explicitly and instruct Claude to prioritize by credibility tier. Increase `WEB_SEARCH_MAX_USES` from 8 to 14 to cover more ground. No schema changes needed — `status.json` already accepts the output.

**Tech Stack:** Python 3, Anthropic API (web_search tool), pytest-style eval harness

---

### Credibility Framework

Sources are evaluated on 5 criteria, scored 1-5 each:

| Criterion | Description |
|-----------|-------------|
| **Authority** | Is this a primary/official source or a reporter? |
| **Editorial standards** | Professional fact-checking, corrections policy? |
| **Track record** | History of accurate emergency reporting? |
| **Timeliness** | How fast do they publish verified updates? |
| **Community reach** | Does this source reach the affected population? |

**Resulting tiers:**

- **Tier 1 (20-25 pts):** Official agencies producing the information. OCFA, OC Sheriff, ggcity.org/emergency, Cal OES/Governor, US EPA, SCAQMD.
- **Tier 2 (15-19 pts):** Established outlets with reporters on scene. ABC7, NBC LA, KTLA, CBS LA, LA Times, OC Register, AP, CNN. Also: Nguoi Viet Daily News (45+ year Vietnamese-American daily with professional editorial staff, headquartered in Westminster OC).
- **Tier 3 (10-14 pts):** Reputable secondary outlets. Fox 11 LA, ABC News national, CBS News national, NPR, Voice of OC, VnExpress International, SBTN.
- **Excluded:** Social media, forums, opinion sites, unverified blogs.

---

### Task 1: Add credibility tiers and expand prompt in gather_facts.py

**Files:**
- Modify: `scripts/gather_facts.py:26-80`

- [ ] **Step 1: Write the failing test**

Create a test that verifies the gather_facts module exposes the credibility tier data structure and the prompt includes Vietnamese sources.

```python
# In eval/test_gather_facts.py, add:

def test_prompt_includes_vietnamese_sources():
    """Gatherer prompt must name Vietnamese-language sources for community coverage."""
    from gather_facts import PROMPT
    vi_sources = ["Nguoi Viet", "nguoi-viet.com"]
    found = any(s.lower() in PROMPT.lower() for s in vi_sources)
    return {
        "passed": found,
        "details": f"Vietnamese source mentioned in prompt: {found}",
    }


def test_prompt_includes_credibility_guidance():
    """Gatherer prompt must instruct model to prioritize official/Tier-1 sources."""
    from gather_facts import PROMPT
    has_tier = "tier" in PROMPT.lower() or "prioritize official" in PROMPT.lower() or "official sources first" in PROMPT.lower()
    return {
        "passed": has_tier,
        "details": f"Credibility guidance in prompt: {has_tier}",
    }


def test_max_uses_sufficient_for_expanded_sources():
    """WEB_SEARCH_MAX_USES must be >= 12 to cover expanded source list."""
    from gather_facts import MAX_USES
    return {
        "passed": MAX_USES >= 12,
        "details": f"MAX_USES={MAX_USES} (need >= 12)",
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python eval/run_all.py --skip integration 2>&1 | findstr /I "gather_facts"`
Expected: 3 new tests FAIL (prompt doesn't mention Vietnamese sources, no credibility guidance, MAX_USES is 8)

- [ ] **Step 3: Update gather_facts.py with expanded sources and credibility framework**

Replace the constants and prompt in `scripts/gather_facts.py`:

```python
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
TOOL_TYPE = os.environ.get("WEB_SEARCH_TOOL_TYPE", "web_search_20250305")
MAX_USES = int(os.environ.get("WEB_SEARCH_MAX_USES", "14"))

# Source credibility tiers for documentation and prompt construction.
# Tier 1: official agencies (primary information producers)
# Tier 2: established outlets with on-scene reporters + Nguoi Viet Daily News
# Tier 3: reputable secondary outlets
SOURCE_TIERS = {
    "tier_1_official": [
        "OCFA (ocfa.org)",
        "OC Sheriff (ocsheriff.gov)",
        "City of Garden Grove (ggcity.org/emergency)",
        "Cal OES / Governor's Office (gov.ca.gov)",
        "US EPA Region 9 (epa.gov)",
        "SCAQMD (aqmd.gov)",
    ],
    "tier_2_primary_news": [
        "ABC7 Los Angeles / KABC (abc7.com)",
        "NBC Los Angeles / KNBC (nbclosangeles.com)",
        "KTLA (ktla.com)",
        "CBS Los Angeles / KCBS (cbsnews.com/losangeles)",
        "LA Times (latimes.com)",
        "OC Register (ocregister.com)",
        "Associated Press (apnews.com)",
        "CNN (cnn.com)",
        "Nguoi Viet Daily News (nguoi-viet.com) — largest Vietnamese-American daily",
    ],
    "tier_3_secondary": [
        "Fox 11 Los Angeles (foxla.com)",
        "ABC News national (abcnews.com)",
        "CBS News national (cbsnews.com)",
        "NPR (npr.org)",
        "Voice of OC (voiceofoc.org)",
        "VnExpress International (e.vnexpress.net)",
        "SBTN (sbtn.tv) — Vietnamese TV network",
    ],
}

SCHEMA_HINT = """{
  "status_headline": "<one concise sentence on the current situation>",
  "tank_temp_f": <number or null>,
  "tank_crack_observed": <true / false / null>,
  "evacuation_residents": <integer or null>,
  "evacuation_area_sq_mi": <number or null>,
  "evacuation_boundary_text": "<streets bounding the zone, or null>",
  "evacuation_lifted": <true / false>,
  "evacuation_expanded": <true / false>,
  "injuries": <integer>,
  "incident_resolved_iso": <ISO 8601 string or null>,
  "schools_closed": ["<district or school>", "..."],
  "official_statements": [
    {"agency": "<e.g. OCFA>", "time_iso": "<ISO 8601>", "text": "<verbatim or close paraphrase>", "source_url": "<url>"}
  ],
  "sources_checked": [
    {"url": "<url>", "title": "<page title>", "fetched_iso": "<ISO 8601>"}
  ]
}"""

PROMPT = f"""You are the data updater for a community emergency dashboard tracking the Garden
Grove, California methyl methacrylate (MMA) storage-tank incident at GKN Aerospace,
12122 Western Ave (began 2026-05-21; ~50,000 residents evacuated).

Use web search to find the MOST RECENT verified status as of right now.

SOURCE PRIORITY (search official sources first, then work down):
  Tier 1 — Official agencies (these ARE the information, highest credibility):
    OCFA (ocfa.org), OC Sheriff (ocsheriff.gov), ggcity.org/emergency,
    Cal OES / Governor (gov.ca.gov, caloes.ca.gov), US EPA, SCAQMD (aqmd.gov)
  Tier 2 — Established news with reporters on scene:
    ABC7/KABC, NBC LA/KNBC, KTLA, CBS LA/KCBS, LA Times, OC Register,
    AP (apnews.com), CNN,
    Nguoi Viet Daily News (nguoi-viet.com) — largest Vietnamese-American daily
  Tier 3 — Reputable secondary outlets:
    Fox 11 LA, ABC News national, CBS News national, NPR, Voice of OC,
    VnExpress International (e.vnexpress.net), SBTN (sbtn.tv)

Cross-check facts across tiers before reporting. Prefer Tier 1 statements verbatim.
Include Vietnamese-language sources when they carry unique community information
not available in English outlets.

Rules:
- Report ONLY facts you found in a source during this search. If you cannot
  confirm a field, set it to null (keep injuries 0 and evacuation_lifted /
  evacuation_expanded false unless a source says otherwise). DO NOT guess or
  carry over prior assumptions.
- Every official_statement and every sources_checked entry MUST use a real URL
  you actually retrieved this search. Never fabricate a URL, agency, quote, or date.
- All times in ISO 8601 UTC (e.g. 2026-05-24T17:00:00Z).

After searching, output ONLY a single JSON object (no prose, no markdown fences)
matching exactly this shape:

{SCHEMA_HINT}
"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python eval/run_all.py --skip integration`
Expected: All tests PASS including the 3 new ones. Exit code 0.

- [ ] **Step 5: Run full eval to verify no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: 45+ tests pass, exit code 0. Check scorecard for any FAIL lines.

- [ ] **Step 6: Commit**

```bash
git add scripts/gather_facts.py eval/test_gather_facts.py
git commit -m "feat(data): expand source coverage with credibility tiers + Vietnamese media"
```

---

### Task 2: Add credibility documentation

**Files:**
- Create: `docs/SOURCE_CREDIBILITY.md`

- [ ] **Step 1: Write the credibility framework documentation**

```markdown
# Source Credibility Framework — GG Tank Watch

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

### Tier 1 — Official Agencies (Score 20-25)

These agencies produce the information. They are the primary authority.

| Source | Score | Rationale |
|--------|-------|-----------|
| OCFA (Orange County Fire Authority) | 25 | Incident command authority |
| OC Sheriff | 24 | Evacuation enforcement authority |
| City of Garden Grove Emergency | 24 | Municipal emergency management |
| Cal OES / Governor's Office | 23 | State emergency coordination |
| US EPA Region 9 | 23 | Air quality monitoring authority |
| SCAQMD | 22 | Regional air quality authority |

### Tier 2 — Established Primary News (Score 15-19)

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

### Tier 3 — Reputable Secondary (Score 10-14)

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
```

- [ ] **Step 2: Commit**

```bash
git add docs/SOURCE_CREDIBILITY.md
git commit -m "docs: add source credibility framework for data pipeline"
```
