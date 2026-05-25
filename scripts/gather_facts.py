"""Headless fact-gatherer for the GG MMA tank dashboard.

Calls the Anthropic Messages API with the web_search server tool to find the
CURRENT status of the incident, and prints a facts JSON object to stdout in the
exact schema scripts/update_status.py reads from stdin. Pipe them together:

    python scripts/gather_facts.py | python scripts/update_status.py

Runs headless in GitHub Actions (no interactive Claude session). The writer's
logic is untouched — this only replaces the human/WebSearch step that used to
feed it facts.

On failure it exits NON-ZERO and prints nothing to stdout, so the caller can
skip the writer and let status.json go visibly stale (the dashboard's staleness
banner is the safety signal) rather than stamping a fresh timestamp onto old
data.

Env:
  ANTHROPIC_API_KEY      required
  CLAUDE_MODEL           optional, default claude-sonnet-4-6
  WEB_SEARCH_TOOL_TYPE   optional, default web_search_20250305 (newer dated
                         versions e.g. web_search_20260209 can be swapped in)
  WEB_SEARCH_MAX_USES    optional, default 8
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
TOOL_TYPE = os.environ.get("WEB_SEARCH_TOOL_TYPE", "web_search_20250305")
MAX_USES = int(os.environ.get("WEB_SEARCH_MAX_USES", "8"))

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

Use web search to find the MOST RECENT verified status as of right now. Prioritize
official / authoritative sources: Orange County Fire Authority (OCFA), OC Sheriff,
ggcity.org/emergency, Cal OES, US EPA, SCAQMD, and established news outlets
(LA Times, OC Register, KTLA, ABC7). Cross-check before reporting a fact.

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


def extract_json(text: str) -> dict:
    t = text.strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found in model output")
    return json.loads(t[start:end + 1])


def main() -> int:
    try:
        import anthropic
    except ImportError:
        sys.stderr.write("anthropic SDK not installed (pip install anthropic)\n")
        return 2
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.stderr.write("ANTHROPIC_API_KEY not set\n")
        return 2

    client = anthropic.Anthropic()
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=8192,
            tools=[{
                "type": TOOL_TYPE,
                "name": "web_search",
                "max_uses": MAX_USES,
                "user_location": {
                    "type": "approximate", "country": "US", "region": "California",
                    "city": "Garden Grove", "timezone": "America/Los_Angeles",
                },
            }],
            messages=[{"role": "user", "content": PROMPT}],
        )
    except Exception as e:
        sys.stderr.write(f"Anthropic API call failed: {e}\n")
        return 1

    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    try:
        facts = extract_json(text)
    except (ValueError, json.JSONDecodeError) as e:
        sys.stderr.write(f"could not parse facts JSON: {e}\n---raw---\n{text[:2000]}\n")
        return 1

    # Backfill sources_checked from the web_search citations the model actually
    # used, so the git-commit audit trail always carries provenance even if the
    # model forgot to list them.
    if not facts.get("sources_checked"):
        seen, srcs = set(), []
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for b in resp.content:
            for c in (getattr(b, "citations", None) or []):
                url = getattr(c, "url", None)
                if url and url not in seen:
                    seen.add(url)
                    srcs.append({"url": url, "title": getattr(c, "title", "") or "", "fetched_iso": now})
        if srcs:
            facts["sources_checked"] = srcs

    json.dump(facts, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
